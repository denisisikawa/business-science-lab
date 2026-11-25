from html.parser import HTMLParser
from pathlib import Path
import re
import tempfile
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parent.parent
page = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")

class Reader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.fragments = []
        self.translations = 0
        self.outgoing = []
        self.cards = 0
        self.local_files = []
    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "details":
            assert "open" not in attributes, "Disclosures must start closed"
        for key in ("href", "src"):
            target = attributes.get(key, "")
            parsed = urlsplit(target)
            if target and not parsed.scheme and not parsed.netloc and parsed.path:
                self.local_files.append(unquote(parsed.path))
        if "id" in attributes:
            self.ids.append(attributes["id"])
        if attributes.get("href", "").startswith("#"):
            self.fragments.append(attributes["href"][1:])
        if "data-en" in attributes or "data-pt" in attributes:
            assert "data-en" in attributes and "data-pt" in attributes, "Missing a locale counterpart"
            assert attributes["data-en"] and attributes["data-pt"], "Empty translation"
            self.translations += 1
        if "class" in attributes and tag == "details" and "project-accordion" in attributes["class"].split():
            self.cards += 1
        if attributes.get("href", "").startswith("http"):
            self.outgoing.append(attributes["href"])

reader = Reader()
reader.feed(page)
assert len(reader.ids) == len(set(reader.ids)), "Duplicate IDs"
assert all(x in reader.ids for x in reader.fragments), "Broken in-page navigation link"
assert reader.cards == 8, "Expected eight expandable projects"
assert reader.translations >= 90, "Locale coverage decreased"
assert "prefers-reduced-motion:reduce" in page, "Reduced-motion support missing"
assert 'name="viewport"' in page, "Viewport missing"
assert "aria-expanded" in page, "Accessible menu missing"
assert (ROOT / "docs" / "favicon.svg").is_file(), "Favicon missing"
allowed_hosts = {"github.com", "www.linkedin.com", "fonts.googleapis.com", "fonts.gstatic.com", "denisisikawa.github.io"}
assert all(urlsplit(x).hostname in allowed_hosts for x in reader.outgoing), "Unexpected external link"
assert all((ROOT / "docs" / x).is_file() or (ROOT / "docs" / x / "index.html").is_file() for x in reader.local_files), "Missing local resource"
scripts = re.findall(r"<script(?:\s[^>]*)?>([\s\S]*?)</script>", page)
assert scripts, "No embedded script"
(Path(tempfile.gettempdir()) / "denis-portfolio-check.js").write_text(scripts[-1], encoding="utf-8")
print(f"Portfolio HTML valid: {reader.cards} closed cards, {reader.translations} translated elements, {len(reader.fragments)} internal anchors, {len(reader.local_files)} local resources.")
