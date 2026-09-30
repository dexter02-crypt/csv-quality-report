"""Bounded CSV profiling with escaped, offline HTML output. Standard library only."""
from __future__ import annotations
from collections import Counter
import csv
from decimal import Decimal, InvalidOperation, localcontext
from html import escape
import json
from pathlib import Path


def numeric_value(value: str) -> Decimal | None:
    """Infer plain finite decimals; never evaluate expressions or locale-formatted money."""
    if not value or len(value) > 128:
        return None
    try:
        number = Decimal(value)
    except InvalidOperation:
        return None
    if not number.is_finite() or abs(number.adjusted()) > 100:
        return None
    return number


def profile_csv(path: Path, *, delimiter: str = ',', max_rows: int = 100_000,
                max_columns: int = 200, max_bytes: int = 20 * 1024 * 1024) -> dict:
    path = Path(path)
    if len(delimiter) != 1 or delimiter in '\r\n\x00"':
        raise ValueError('Delimiter must be one character other than a newline, NUL, or quote.')
    if min(max_rows, max_columns, max_bytes) < 1:
        raise ValueError('All input limits must be positive.')
    if not path.is_file():
        raise ValueError('CSV input is missing or is not a regular file.')
    # Read max+1 rather than trusting a size check if a local file grows mid-read.
    with path.open('rb') as handle:
        raw = handle.read(max_bytes + 1)
    if len(raw) > max_bytes:
        raise ValueError(f'CSV exceeds the {max_bytes}-byte input limit.')
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError as exc:
        raise ValueError('CSV must be UTF-8 encoded (a UTF-8 BOM is allowed).') from exc
    if '\x00' in text:
        raise ValueError('NUL characters are not accepted in CSV input.')
    # newline="" preserves embedded newlines for Python's CSV parser.
    from io import StringIO
    rows = csv.reader(StringIO(text, newline=''), delimiter=delimiter, strict=True)
    try:
        header = next(rows, None)
        if not header:
            raise ValueError('CSV must contain a header row.')
        header = [value.strip() for value in header]
        if len(header) > max_columns:
            raise ValueError(f'CSV exceeds the {max_columns}-column limit.')
        if not all(header) or len(set(header)) != len(header):
            raise ValueError('Column names must be nonempty and unique after whitespace trimming.')
        counts = [Counter() for _ in header]
        missing = [0] * len(header)
        seen_rows: set[tuple[str, ...]] = set()
        duplicates = row_count = blank_rows = 0
        for row in rows:
            if not row:
                blank_rows += 1
                continue
            row_count += 1
            if row_count > max_rows:
                raise ValueError(f'CSV exceeds the {max_rows}-row limit.')
            if len(row) != len(header):
                raise ValueError(f'CSV record ending on line {rows.line_num} has {len(row)} fields; expected {len(header)}.')
            values = tuple(value.strip() for value in row)
            duplicates += values in seen_rows
            seen_rows.add(values)
            for index, value in enumerate(values):
                if value == '':
                    missing[index] += 1
                else:
                    counts[index][value] += 1
    except csv.Error as exc:
        raise ValueError(f'Invalid CSV: {exc}') from exc
    columns = []
    for name, values, empty in zip(header, counts, missing):
        numeric = {value: numeric_value(value) for value in values}
        numeric_count = sum(values[value] for value, number in numeric.items() if number is not None)
        present = row_count - empty
        kind = 'empty' if present == 0 else ('numeric' if numeric_count == present else 'text/mixed')
        stats = None
        if kind == 'numeric':
            numbers = [n for n in numeric.values() if n is not None]
            with localcontext() as context:
                context.prec = 34
                total = sum((numeric[value] * count for value, count in values.items()), Decimal(0))
                stats = {'min': str(min(numbers)), 'max': str(max(numbers)), 'mean': format(total / present, '.8g')}
        columns.append({'name': name, 'kind': kind, 'missing': empty,
                        'missing_percent': round(empty / row_count * 100, 2) if row_count else 0.0,
                        'distinct_nonempty': len(values), 'numeric_values': numeric_count,
                        'top_values': [{'value': value, 'count': count} for value, count in values.most_common(3)],
                        'numeric_summary': stats})
    return {'source_name': path.name, 'rows': row_count, 'column_count': len(header),
            'missing_cells': sum(missing), 'duplicate_rows_after_first': duplicates,
            'blank_records_skipped': blank_rows, 'columns': columns,
            'notes': ['Whitespace around fields is stripped for all statistics and duplicate checks.',
                      'Only empty/whitespace-only fields are missing; NA, null, zero, and False are not missing.',
                      'Numeric types are suggestions, not schemas; identifiers with leading zeros may look numeric.',
                      'Numeric means use Decimal precision 34 and are rounded to 8 significant digits.',
                      'Reports include column names and top values. Treat reports as potentially sensitive.']}

CSS = """
:root{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#172739;background:#f1f5f8}
*{box-sizing:border-box}body{margin:0}main{max-width:1180px;margin:auto;padding:42px 28px}
.eyebrow{font-size:12px;letter-spacing:.16em;text-transform:uppercase;font-weight:700;color:#426779}
h1{font-size:42px;letter-spacing:-.04em;margin:8px 0 12px}h2{font-size:22px;margin:32px 0 14px}
p{line-height:1.65}.muted{color:#526674}.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:30px 0}
.card{background:white;border:1px solid #dce5e9;border-radius:14px;padding:20px}.card strong{display:block;font-size:32px;margin-top:8px}
.card span{font-size:13px;color:#526674}.table-wrap{overflow-x:auto;border:1px solid #dce5e9;border-radius:14px;background:white}
table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:16px 14px;border-bottom:1px solid #e8eef1;vertical-align:top;font-size:14px}
th{font-size:11px;text-transform:uppercase;letter-spacing:.06em;background:#e8eff3}tr:last-child td{border-bottom:0}
.name{font-weight:700;overflow-wrap:anywhere;max-width:230px}.tag{display:inline-block;padding:4px 8px;border-radius:6px;background:#e9f2f5;font-size:12px;white-space:nowrap}
.warning{color:#925c0f}.small{font-size:12px;line-height:1.7;max-width:260px;overflow-wrap:anywhere}
progress{display:block;width:110px;height:8px;margin-top:8px;accent-color:#d09b3c}.notes{padding:20px 26px;background:#e5edf1;border-radius:14px}
.notes li{margin:8px 0;line-height:1.6}footer{margin-top:28px;font-size:12px;color:#526674}
@media(max-width:700px){main{padding:24px 16px}h1{font-size:30px}.cards{grid-template-columns:repeat(2,1fr)}th,td{padding:12px 10px}}
"""

def render_html(report: dict) -> str:
    e = lambda value: escape(str(value), quote=True)
    cards = ''.join(f'<section class="card"><span>{label}</span><strong>{e(report[key])}</strong></section>'
                    for key, label in [('rows','Data rows'),('column_count','Columns'),
                                       ('missing_cells','Missing cells'),('duplicate_rows_after_first','Duplicate rows after first')])
    body = []
    for column in report['columns']:
        top = '<br>'.join(f'{e(item["value"])} <span class="muted">× {e(item["count"])}</span>' for item in column['top_values']) or '—'
        stats = column['numeric_summary']
        summary = '<br>'.join(f'{e(key.title())}: {e(value)}' for key,value in stats.items()) if stats else '—'
        body.append(f"""<tr><td class="name">{e(column['name'])}</td><td><span class="tag">{e(column['kind'])}</span></td>
<td>{e(column['missing'])} <span class="muted">({e(column['missing_percent'])}%)</span><progress max="100" value="{e(column['missing_percent'])}"></progress></td>
<td>{e(column['distinct_nonempty'])}</td><td class="small">{top}</td><td class="small">{summary}</td></tr>""")
    notes = ''.join(f'<li>{e(note)}</li>' for note in report['notes'])
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>CSV Quality Report · {e(report['source_name'])}</title><style>{CSS}</style></head><body><main>
<div class="eyebrow">Small tools / Data quality</div><h1>Know your CSV before you use it.</h1>
<p class="muted">Local analysis of <strong>{e(report['source_name'])}</strong>. No cloud uploads. No external scripts.</p>
<div class="cards">{cards}</div><h2>Column-by-column profile</h2><div class="table-wrap"><table>
<thead><tr><th scope="col">Column</th><th scope="col">Suggested type</th><th scope="col">Missing</th><th scope="col">Distinct</th><th scope="col">Most frequent values</th><th scope="col">Numeric summary</th></tr></thead>
<tbody>{''.join(body)}</tbody></table></div><h2>How to read this report</h2><div class="notes"><ul>{notes}</ul>
<p>Blank records skipped: {e(report['blank_records_skipped'])}. This tool reports observations; it does not clean or change your CSV.</p></div>
<footer>CSV Quality Report · Python standard library · Prepared for Shikhar Singh</footer></main></body></html>"""


def save_report(report: dict, directory: Path) -> tuple[Path, Path]:
    directory = Path(directory)
    # Render first, then create a NEW output directory; never replace prior work.
    html = render_html(report)
    payload = json.dumps(report, indent=2, ensure_ascii=True, allow_nan=False) + '\n'
    directory.mkdir(parents=True, exist_ok=False)
    html_path, json_path = directory/'report.html', directory/'report.json'
    with html_path.open('x', encoding='utf-8') as handle:
        handle.write(html)
    with json_path.open('x', encoding='utf-8') as handle:
        handle.write(payload)
    return html_path, json_path
