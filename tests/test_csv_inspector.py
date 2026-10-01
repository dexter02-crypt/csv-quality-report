from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest
import csv_inspector
from csv_inspector.core import numeric_value, profile_csv, render_html, save_report
ROOT=Path(__file__).resolve().parents[1]
class CsvTests(unittest.TestCase):
    def test_package_version_matches_release(self):
        self.assertEqual(csv_inspector.__version__, "1.1.0")

    def make_report(self,text,**kwargs):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'test.csv'; path.write_text(text,encoding='utf-8')
            return profile_csv(path,**kwargs)

    def test_sample_expected_metrics(self):
        report=profile_csv(ROOT/'examples/orders.csv')
        self.assertEqual((report['rows'],report['column_count'],report['missing_cells'],report['duplicate_rows_after_first']),(12,6,4,1))

    def test_numeric_summary_and_zero(self):
        col=self.make_report('n\n0\n2\n4\n')['columns'][0]
        self.assertEqual(col['kind'],'numeric')
        self.assertEqual(col['missing'],0)
        self.assertEqual(col['numeric_summary'],{'min':'0','max':'4','mean':'2'})

    def test_missing_is_only_empty(self):
        report=self.make_report('a,b\nNA,\nnull,False\n0, \n')
        self.assertEqual(report['missing_cells'],2)
        self.assertEqual(report['columns'][0]['missing'],0)

    def test_whitespace_and_duplicate_semantics(self):
        report=self.make_report(' a ,b\n x, 1\nx,1\nx,1\n')
        self.assertEqual(report['columns'][0]['name'],'a')
        self.assertEqual(report['duplicate_rows_after_first'],2)

    def test_header_only_is_valid(self):
        report=self.make_report('a,b\n')
        self.assertEqual(report['rows'],0)
        self.assertTrue(all(col['kind']=='empty' for col in report['columns']))

    def test_blank_records_skipped(self):
        report=self.make_report('a,b\n\n1,2\n\n')
        self.assertEqual(report['rows'],1)
        self.assertEqual(report['blank_records_skipped'],2)

    def test_utf8_bom_and_unicode(self):
        report=self.make_report('\ufeffcity\nजयपुर\n')
        self.assertEqual(report['columns'][0]['top_values'][0]['value'],'जयपुर')

    def test_quoted_comma_and_newline(self):
        report=self.make_report('a,b\n"one,two","line\nline"\n')
        self.assertEqual(report['rows'],1)
        self.assertEqual(report['columns'][0]['top_values'][0]['value'],'one,two')

    def test_alternate_delimiter(self):
        report=self.make_report('a;b\n1;2\n',delimiter=';')
        self.assertEqual(report['column_count'],2)

    def test_invalid_headers(self):
        for text in ('','\n','a,a\n1,2\n','a, \n1,2\n'):
            with self.subTest(text=text), self.assertRaises(ValueError): self.make_report(text)

    def test_ragged_and_malformed(self):
        for text in ('a,b\n1\n','a,b\n1,2,3\n','a\n"unterminated\n'):
            with self.subTest(text=text), self.assertRaises(ValueError): self.make_report(text)

    def test_input_limits(self):
        for kwargs in ({'max_rows':1},{'max_columns':1},{'max_bytes':2}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.make_report('a,b\n1,2\n3,4\n',**kwargs)

    def test_invalid_delimiter(self):
        for delimiter in ('','||','\n','"'):
            with self.subTest(delimiter=delimiter), self.assertRaises(ValueError):
                self.make_report('a\n1\n',delimiter=delimiter)

    def test_nonfinite_and_expression_are_not_numbers(self):
        for value in ('nan','Infinity','-inf','1/0','1e99999','0e99999'):
            self.assertIsNone(numeric_value(value))
        self.assertEqual(self.make_report('x\nnan\n1\n')['columns'][0]['kind'],'text/mixed')

    def test_html_escapes_cells_and_column_names(self):
        report=self.make_report('<script>alert(1)</script>\n<img src=x onerror=alert(1)>\n')
        html=render_html(report)
        self.assertNotIn('<script>',html)
        self.assertNotIn('<img ',html)
        self.assertIn('&lt;script&gt;',html)
        self.assertIn('default-src',html)

    def test_output_round_trip_and_no_overwrite(self):
        report=self.make_report('a\n1\n')
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'report'
            html,path=save_report(report,target)
            self.assertEqual(json.loads(path.read_text()),report)
            self.assertTrue(html.read_text().startswith('<!doctype html>'))
            with self.assertRaises(FileExistsError): save_report(report,target)

    def test_input_unchanged_and_cli(self):
        source=ROOT/'examples/orders.csv'; before=source.read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            result=subprocess.run([sys.executable,'-m','csv_inspector',str(source),'--output-dir',str(Path(tmp)/'out')],cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('Missing cells: 4',result.stdout)
            self.assertEqual(source.read_bytes(),before)

    def test_bad_encoding_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'bad.csv'; source.write_bytes(b'col\n\xff\n')
            with self.assertRaisesRegex(ValueError,'UTF-8'): profile_csv(source)
