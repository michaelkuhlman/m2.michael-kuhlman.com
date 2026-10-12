# Median table of a directory of Lighthouse JSON reports named <page>-<form>-<n>.json (used by lighthouse.sh).
import json,sys,glob,statistics as st,os
d=sys.argv[1]; rows={}
for f in sorted(glob.glob(d+'/*.json')):
    b=os.path.basename(f)[:-5]; page,form,n=b.rsplit('-',2)
    j=json.load(open(f)); a=j['audits']
    try:
        r=dict(perf=j['categories']['performance']['score']*100, fcp=a['first-contentful-paint']['numericValue'],
           lcp=a['largest-contentful-paint']['numericValue'], tbt=a['total-blocking-time']['numericValue'],
           cls=a['cumulative-layout-shift']['numericValue'], si=a['speed-index']['numericValue'],
           bytes=a['total-byte-weight']['numericValue'])
    except Exception as e: continue
    rows.setdefault((page,form),[]).append(r)
print(f"{'page':5} {'form':8} {'perf':>5} {'FCP':>6} {'LCP':>6} {'TBT':>5} {'CLS':>6} {'SI':>6} {'KB':>6}  runs")
for (p,f),rs in sorted(rows.items()):
    m=lambda k: st.median([r[k] for r in rs])
    print(f"{p:5} {f:8} {m('perf'):5.0f} {m('fcp')/1000:6.2f} {m('lcp')/1000:6.2f} {m('tbt'):5.0f} {m('cls'):6.3f} {m('si')/1000:6.2f} {m('bytes')/1024:6.0f}  {[int(r['perf']) for r in rs]}")
