import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from csv_inspector.compare import compare_profiles

ROOT = Path(__file__).resolve().parents[1]

class Tests(unittest.TestCase):
    def report(self,name,cols,rows=10,dups=0): return {'source_name':name,'rows':rows,'duplicate_rows_after_first':dups,'columns':cols}
    def col(self,n,k='text/mixed',m=0,d=3): return {'name':n,'kind':k,'missing_percent':m,'distinct_nonempty':d}
    def test_add_remove(self):
        r=compare_profiles(self.report('a',[self.col('x')]),self.report('b',[self.col('y')]))
        self.assertEqual(r['added_columns'],['y']); self.assertEqual(r['removed_columns'],['x'])
    def test_kind(self):
        r=compare_profiles(self.report('a',[self.col('x')]),self.report('b',[self.col('x','numeric')]))
        self.assertIn('kind',r['changed_columns'][0])
    def test_missing_delta(self):
        r=compare_profiles(self.report('a',[self.col('x',m=10)]),self.report('b',[self.col('x',m=25)]))
        self.assertEqual(r['changed_columns'][0]['missing_percent_delta'],15)
    def test_rows(self): self.assertEqual(compare_profiles(self.report('a',[],10),self.report('b',[],13))['row_delta'],3)

    def test_compare_cli_writes_outputs_and_preserves_inputs(self):
        before = ROOT / "examples" / "orders.csv"
        after = ROOT / "examples" / "orders-next.csv"
        before_bytes = before.read_bytes()
        after_bytes = after.read_bytes()

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "comparison"
            result = subprocess.run(
                [
                    sys.executable,
                    "compare_csv.py",
                    str(before),
                    str(after),
                    "--output-dir",
                    str(output)
                ],
                cwd=ROOT,
                capture_output=True,
                text=True
            )

            self.assertEqual(result.returncode, 0, result.stderr)

            payload = json.loads(
                (output / "comparison.json").read_text(encoding="utf-8")
            )
            self.assertEqual(payload["before"], "orders.csv")
            self.assertEqual(payload["after"], "orders-next.csv")
            html = (output / "comparison.html").read_text(encoding="utf-8")
            self.assertTrue(
                html.startswith("<" + chr(33) + "doctype html>")
            )

            self.assertEqual(before.read_bytes(), before_bytes)
            self.assertEqual(after.read_bytes(), after_bytes)
