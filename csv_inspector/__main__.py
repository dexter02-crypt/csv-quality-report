import argparse
from pathlib import Path
import sys
from .core import profile_csv, save_report

def main(argv=None):
    parser = argparse.ArgumentParser(description='Make a local HTML/JSON quality report for a UTF-8 CSV.')
    parser.add_argument('input', type=Path)
    parser.add_argument('--output-dir', type=Path, required=True, help='A NEW directory for report.html and report.json.')
    parser.add_argument('--delimiter', default=',', help='One character, e.g. ";".')
    parser.add_argument('--max-rows', type=int, default=100000)
    args = parser.parse_args(argv)
    try:
        report=profile_csv(args.input,delimiter=args.delimiter,max_rows=args.max_rows)
        html_path,json_path=save_report(report,args.output_dir)
        print(f"Rows: {report['rows']} | Columns: {report['column_count']} | Missing cells: {report['missing_cells']} | Duplicate rows after first: {report['duplicate_rows_after_first']}")
        print(f'HTML: {html_path}\nJSON: {json_path}')
    except (ValueError,OSError) as exc:
        print(f'Error: {exc}',file=sys.stderr)
        return 2
    return 0

if __name__=='__main__':
    raise SystemExit(main())
