import argparse,json
from pathlib import Path
from csv_inspector.core import profile_csv
from csv_inspector.compare import compare_profiles,render_html

def main():
    a=argparse.ArgumentParser(); a.add_argument('before',type=Path); a.add_argument('after',type=Path); a.add_argument('--output-dir',type=Path,required=True); a.add_argument('--delimiter',default=','); x=a.parse_args()
    try:
        r=compare_profiles(profile_csv(x.before,delimiter=x.delimiter),profile_csv(x.after,delimiter=x.delimiter)); x.output_dir.mkdir(parents=True,exist_ok=False); (x.output_dir/'comparison.json').write_text(json.dumps(r,indent=2)+'\n'); (x.output_dir/'comparison.html').write_text(render_html(r)); print(json.dumps(r,indent=2))
    except (ValueError,OSError) as e: print('Error:',e); raise SystemExit(2)
if __name__=='__main__': main()
