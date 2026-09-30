from html import escape
import json

def compare_profiles(before, after):
    a={c['name']:c for c in before['columns']}; b={c['name']:c for c in after['columns']}
    added=sorted(set(b)-set(a)); removed=sorted(set(a)-set(b)); changed=[]
    for name in sorted(set(a)&set(b)):
        x,y=a[name],b[name]; item={'column':name}
        if x['kind']!=y['kind']: item['kind']={'before':x['kind'],'after':y['kind']}
        md=round(y['missing_percent']-x['missing_percent'],2)
        if md: item['missing_percent_delta']=md
        dd=y['distinct_nonempty']-x['distinct_nonempty']
        if dd: item['distinct_nonempty_delta']=dd
        if len(item)>1: changed.append(item)
    return {'before':before['source_name'],'after':after['source_name'],'added_columns':added,'removed_columns':removed,'changed_columns':changed,'row_delta':after['rows']-before['rows'],'duplicate_row_delta':after['duplicate_rows_after_first']-before['duplicate_rows_after_first']}

def render_html(report):
    e=lambda x:escape(str(x),quote=True)
    rows=''.join('<tr><td>'+e(x['column'])+'</td><td>'+e(json.dumps({k:v for k,v in x.items() if k!='column'},ensure_ascii=False))+'</td></tr>' for x in report['changed_columns']) or '<tr><td colspan="2">No common-column metric changes.</td></tr>'
    return '<!doctype html><meta charset="utf-8"><title>CSV comparison</title><style>body{font-family:system-ui;max-width:960px;margin:40px auto;padding:0 20px}table{border-collapse:collapse;width:100%}td,th{padding:10px;border-bottom:1px solid #ddd;text-align:left}</style>'+f"<h1>CSV schema / quality comparison</h1><p><b>{e(report['before'])}</b> → <b>{e(report['after'])}</b></p><p>Added: {e(', '.join(report['added_columns']) or 'none')}<br>Removed: {e(', '.join(report['removed_columns']) or 'none')}<br>Row delta: {report['row_delta']}</p><table><tr><th>Column</th><th>Observed change</th></tr>{rows}</table>"
