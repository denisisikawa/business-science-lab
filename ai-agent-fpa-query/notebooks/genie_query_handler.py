"""Scoped finance query demo and opt-in, unverified live Genie adapter.

Default local mode uses fixed query templates and synthetic SQLite data.
No arbitrary generated SQL is executed locally.
"""
import argparse
import csv
from datetime import datetime, timezone, date
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import time
import unicodedata
from urllib.parse import urlparse, quote

REPORT_DIR = Path(__file__).resolve().parents[2] / "reports"
CATEGORIES = ("SOFTWARE", "HARDWARE", "CLOUD", "CONSULTING")
SQL = {
    "total": "SELECT SUM(amount_cents) AS amount_cents FROM costs WHERE month = ?",
    "category": "SELECT category, SUM(amount_cents) AS amount_cents FROM costs WHERE month = ? GROUP BY category ORDER BY category"
}

class GenieError(RuntimeError):
    pass

def normalize_question(question):
    if not isinstance(question, str) or not question.strip() or len(question) > 500:
        raise ValueError("Question must contain 1–500 characters")
    return " ".join(unicodedata.normalize("NFKD", question.casefold()).encode("ascii", "ignore").decode().split()).rstrip("?.")

def parse_question(question):
    normalized = normalize_question(question)
    patterns = {
        "total": r"(?:what was the |show |qual (?:foi |e )?o )?(?:total (?:it )?cost(?: for| in)?|custo total(?: de ti)?(?: em| de)?) (\d{4}-\d{2})",
        "category": r"(?:show |mostre )?(?:costs? by category(?: for| in)?|custos por categoria(?: em| de)?) (\d{4}-\d{2})"
    }
    for intent, pattern in patterns.items():
        match = re.fullmatch(pattern, normalized)
        if match:
            month = match.group(1)
            try:
                date.fromisoformat(month + "-01")
            except ValueError:
                return {"status": "invalid_period"}
            return {"status": "supported", "intent": intent, "month": month}
    if not re.search(r"\d{4}-\d{2}", normalized) and any(w in normalized for w in ("cost", "custo")):
        return {"status": "needs_clarification"}
    return {"status": "unsupported"}

def synthetic_rows():
    rows = []
    for index in range(12):
        year, month = divmod(2024 * 12 + 5 + index, 12)
        for category_index, category in enumerate(CATEGORIES):
            # Exact integer cents; June 2024 through May 2025.
            rows.append({"month": f"{year:04d}-{month+1:02d}", "category": category,
                         "amount_cents": 10_000_000 + category_index * 1_000_000 + index * 200_000})
    return rows

def local_query(question):
    request = parse_question(question)
    base = {"mode": "local", "data_scope": "synthetic", "question": question,
            "verified": False, "status": request["status"], "answer": None,
            "sql_query": None, "sources": [], "rows": []}
    if request["status"] != "supported":
        return base
    records = synthetic_rows()
    fingerprint = hashlib.sha256(json.dumps(records, sort_keys=True).encode()).hexdigest()
    with sqlite3.connect(":memory:") as connection:
        connection.execute("CREATE TABLE costs(month TEXT, category TEXT, amount_cents INTEGER, PRIMARY KEY(month,category))")
        connection.executemany("INSERT INTO costs VALUES(:month,:category,:amount_cents)", records)
        connection.execute("PRAGMA query_only = ON")
        connection.row_factory = sqlite3.Row
        results = [dict(r) for r in connection.execute(SQL[request["intent"]], (request["month"],))]
    if not results or results[0]["amount_cents"] is None:
        return {**base, "status": "no_data", "period": request["month"], "dataset_sha256": fingerprint}
    return {**base, "status": "completed", "verified": True, "period": request["month"],
            "answer": "Calculated from the synthetic local dataset; amounts are BRL cents.",
            "sql_query": SQL[request["intent"]], "parameters": [request["month"]],
            "sources": ["synthetic.costs"], "rows": results, "dataset_sha256": fingerprint}

def _identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", value):
        raise GenieError("Invalid Genie resource identifier")
    return quote(value, safe="")

def ask_genie(question, space_id=None, *, mode="local", session=None,
              host=None, token=None, max_polls=30, timeout=15, poll_interval=1):
    request = parse_question(question)
    if mode == "local":
        return local_query(question)
    if mode != "genie":
        raise ValueError("mode must be local or genie")
    if request["status"] != "supported":
        return {"mode": "genie", "status": request["status"], "verified": False,
                "answer": None, "rows": [], "sources": []}
    import requests
    host, token = host or os.getenv("DATABRICKS_HOST"), token or os.getenv("DATABRICKS_TOKEN")
    space_id = space_id or os.getenv("GENIE_SPACE_ID")
    parsed = urlparse(host or "")
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
            or parsed.path not in ("", "/") or parsed.query or parsed.fragment):
        raise GenieError("Configure an HTTPS Databricks workspace origin")
    if not token or not space_id:
        raise GenieError("Live mode requires DATABRICKS_TOKEN and GENIE_SPACE_ID; no synthetic fallback")
    if not isinstance(max_polls, int) or not 1 <= max_polls <= 60 or not 0 < timeout <= 60 or not 0 <= poll_interval <= 5:
        raise ValueError("Invalid request timeout or polling limits")
    client = session or requests.Session()
    root = host.rstrip("/") + "/api/2.0/genie/spaces/" + _identifier(space_id)
    def call(method, url, **kwargs):
        try:
            response = client.request(method, url, headers={"Authorization": "Bearer " + token},
                                      timeout=timeout, allow_redirects=False, **kwargs)
            if not 200 <= response.status_code < 300:
                raise GenieError(f"Genie HTTP {response.status_code}; response body withheld")
            payload = response.json()
            if not isinstance(payload, dict):
                raise GenieError("Unexpected Genie response shape")
            return payload
        except (requests.RequestException, ValueError) as error:
            raise GenieError("Genie request failed or returned invalid JSON") from None
    started = call("POST", root + "/start-conversation", json={"content": question})
    message = started.get("message") or {}
    if not isinstance(message, dict):
        raise GenieError("Invalid initial message")
    conversation = _identifier(started.get("conversation_id") or message.get("conversation_id"))
    message_id = _identifier(started.get("message_id") or message.get("message_id") or message.get("id"))
    url = root + "/conversations/" + conversation + "/messages/" + message_id
    for _ in range(max_polls):
        message = call("GET", url)
        status = message.get("status")
        if status in ("FAILED", "CANCELLED", "QUERY_RESULT_EXPIRED"):
            raise GenieError("Genie message ended with status " + status)
        if status == "COMPLETED":
            attachments = message.get("attachments", [])
            if not isinstance(attachments, list):
                raise GenieError("Invalid attachment list")
            texts, queries, results = [], [], []
            for attachment in attachments:
                if not isinstance(attachment, dict):
                    raise GenieError("Invalid attachment")
                text, query = attachment.get("text") or {}, attachment.get("query") or {}
                if not isinstance(text, dict) or not isinstance(query, dict):
                    raise GenieError("Invalid attachment shape")
                if text.get("content"):
                    texts.append(text["content"])
                if query.get("query"):
                    queries.append(query["query"])
                    attachment_id = _identifier(attachment.get("attachment_id"))
                    results.append(call("GET", url + "/attachments/" + attachment_id + "/query-result"))
            return {"mode": "genie", "status": "completed_unverified", "verified": False,
                    "answer": "\n".join(texts) or None, "sql_query": queries,
                    "provider_results": results, "sources": ["configured_genie_space"],
                    "conversation_id": conversation, "message_id": message_id}
        if poll_interval:
            time.sleep(poll_interval)
    raise GenieError("Genie polling limit reached; no synthetic fallback")

def log_query(question, result, analyst="local_user", path=None):
    """JSON Lines: metadata only by default, excluding prompts, SQL and answers."""
    path = Path(path) if path else REPORT_DIR / "genie_query_audit.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {"timestamp": datetime.now(timezone.utc).isoformat(), "analyst": analyst,
             "question_sha256": hashlib.sha256(question.encode()).hexdigest(),
             "mode": result["mode"], "status": result["status"],
             "verified": result.get("verified", False),
             "dataset_sha256": result.get("dataset_sha256")}
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(entry, ensure_ascii=False) + "\n")

def generate_sample_report(output_dir=None):
    output = Path(output_dir) if output_dir else REPORT_DIR
    output.mkdir(parents=True, exist_ok=True)
    path = output / "genie_sample_report.csv"
    rows = synthetic_rows()
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["month", "category", "amount_cents"])
        writer.writeheader()
        writer.writerows(rows)
    return rows

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["local", "genie"], default="local")
    parser.add_argument("--question", default="total IT cost for 2025-05")
    parser.add_argument("--output-dir", type=Path, default=REPORT_DIR)
    args = parser.parse_args(argv)
    try:
        result = ask_genie(args.question, mode=args.mode)
    except GenieError as error:
        result = {"mode": args.mode, "status": "error", "verified": False}
        log_query(args.question, result, path=args.output_dir / "genie_query_audit.jsonl")
        parser.exit(1, str(error) + "\n")
    log_query(args.question, result, path=args.output_dir / "genie_query_audit.jsonl")
    if args.mode == "local":
        generate_sample_report(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
