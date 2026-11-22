"""Small, dependency-free reference for the financial ingestion contract.

SQLite is a local acceptance-test backend, not an emulation of Delta Lake.
"""
import hashlib
import json
import re
import sqlite3
from collections import defaultdict
from datetime import date, datetime, timezone
from decimal import Decimal

FIELDS = ('source_system', 'transaction_id', 'updated_at', 'month', 'cost_center',
          'category', 'vendor', 'currency', 'amount')
CATEGORIES = {'SOFTWARE', 'HARDWARE', 'CLOUD', 'CONSULTING'}
PAYLOAD = ('month', 'cost_center', 'category', 'vendor', 'currency', 'amount')


def normalize(row):
    errors, result = [], {}
    for key in FIELDS:
        value = row.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append('missing_' + key)
        else:
            result[key] = value.strip()
    for key in ('source_system', 'cost_center', 'category', 'currency'):
        if key in result:
            result[key] = result[key].upper()
    if result.get('category') not in CATEGORIES:
        errors.append('invalid_category')
    if result.get('currency') != 'BRL':
        errors.append('unsupported_currency')
    try:
        parsed = date.fromisoformat(result['month'])
        if not re.fullmatch(r'\d{4}-\d{2}-01', result['month']) or parsed.day != 1:
            raise ValueError()
    except (KeyError, ValueError):
        errors.append('invalid_month')
    try:
        raw = result['updated_at']
        stamp = datetime.fromisoformat(raw.replace('Z', '+00:00'))
        if stamp.tzinfo is None:
            raise ValueError()
        result['updated_at'] = stamp.astimezone(timezone.utc).isoformat(timespec='microseconds')
    except (KeyError, ValueError):
        errors.append('invalid_updated_at')
    amount = None
    try:
        raw = result['amount']
        if not re.fullmatch(r'[+-]?\d{1,16}(?:\.\d{1,2})?', raw):
            raise ValueError()
        amount = Decimal(raw).quantize(Decimal('.01'))
        result['amount'] = format(amount, '.2f')
    except (KeyError, ValueError):
        errors.append('invalid_amount')
    if errors:
        return None, sorted(set(errors)), amount
    result['row_hash'] = hashlib.sha256(json.dumps(
        {k: result[k] for k in PAYLOAD}, sort_keys=True).encode()).hexdigest()
    return result, [], amount


def transform_records(records):
    accepted, rejected, duplicate, superseded = [], [], [], []
    groups = defaultdict(list)
    known_total, unknown_amounts = 0, 0
    for index, raw in enumerate(records):
        row, errors, amount = normalize(raw)
        cents = int(amount * 100) if amount is not None else None
        if cents is None:
            unknown_amounts += 1
        else:
            known_total += cents
        envelope = {'row': row, 'raw': raw, 'source_row': index + 1, 'cents': cents}
        if errors:
            rejected.append({**envelope, 'reasons': errors})
        else:
            groups[(row['source_system'], row['transaction_id'])].append(envelope)
    for group in groups.values():
        versions = defaultdict(set)
        for entry in group:
            versions[entry['row']['updated_at']].add(entry['row']['row_hash'])
        if any(len(hashes) > 1 for hashes in versions.values()):
            rejected.extend({**e, 'reasons': ['conflicting_version']} for e in group)
            continue
        group.sort(key=lambda e: (-datetime.fromisoformat(e['row']['updated_at']).timestamp(), e['source_row']))
        winner = group[0]
        accepted.append(winner)
        for entry in group[1:]:
            (duplicate if entry['row']['updated_at'] == winner['row']['updated_at'] else superseded).append(entry)
    buckets = {'accepted': accepted, 'rejected': rejected, 'duplicates': duplicate, 'superseded': superseded}
    report = {'input_rows': len(records), 'unknown_amount_rows': unknown_amounts,
              'known_input_cents': known_total,
              **{name + '_rows': len(rows) for name, rows in buckets.items()},
              **{name + '_cents': sum(e['cents'] or 0 for e in rows) for name, rows in buckets.items()}}
    assert sum(len(rows) for rows in buckets.values()) == len(records)
    assert sum(report[name + '_cents'] for name in buckets) == known_total
    return {**buckets, 'report': report}


def run_local_batch(database, records, batch_id):
    """Commit raw input, dispositions and current facts in one SQLite transaction."""
    if not isinstance(batch_id, str) or not batch_id.strip():
        raise ValueError('batch_id is required')
    fingerprint = hashlib.sha256(json.dumps(records, sort_keys=True).encode()).hexdigest()
    result = transform_records(records)
    with sqlite3.connect(database) as connection:
        connection.execute('CREATE TABLE IF NOT EXISTS batches (id TEXT PRIMARY KEY, fingerprint TEXT, report TEXT)')
        connection.execute('CREATE TABLE IF NOT EXISTS bronze (batch_id TEXT, source_row INTEGER, raw TEXT, disposition TEXT, reasons TEXT, PRIMARY KEY(batch_id,source_row))')
        connection.execute('CREATE TABLE IF NOT EXISTS silver (source_system TEXT, transaction_id TEXT, updated_at TEXT, row_hash TEXT, amount_cents INTEGER, record TEXT, batch_id TEXT, source_row INTEGER, PRIMARY KEY(source_system,transaction_id))')
        connection.execute('BEGIN IMMEDIATE')
        existing = connection.execute('SELECT fingerprint, report FROM batches WHERE id=?', (batch_id,)).fetchone()
        if existing:
            if existing[0] != fingerprint:
                raise ValueError('batch_id already used with different input')
            return {**json.loads(existing[1]), 'replayed': True}
        for disposition in ('accepted', 'rejected', 'duplicates', 'superseded'):
            for entry in result[disposition]:
                connection.execute('INSERT INTO bronze VALUES(?,?,?,?,?)',
                    (batch_id, entry['source_row'], json.dumps(entry['raw'], sort_keys=True), disposition, json.dumps(entry.get('reasons', []))))
        stale = 0
        for entry in result['accepted']:
            row = entry['row']
            key = (row['source_system'], row['transaction_id'])
            old = connection.execute('SELECT updated_at,row_hash FROM silver WHERE source_system=? AND transaction_id=?', key).fetchone()
            if old:
                if old[0] == row['updated_at'] and old[1] != row['row_hash']:
                    raise ValueError('Conflicting version against persisted silver')
                if old[0] >= row['updated_at']:
                    stale += 1
                    continue
            connection.execute('INSERT OR REPLACE INTO silver VALUES(?,?,?,?,?,?,?,?)',
                (*key, row['updated_at'], row['row_hash'], entry['cents'], json.dumps(row, sort_keys=True), batch_id, entry['source_row']))
        report = {**result['report'], 'stale_or_unchanged_rows': stale, 'replayed': False}
        connection.execute('INSERT INTO batches VALUES(?,?,?)', (batch_id, fingerprint, json.dumps(report)))
    return report
