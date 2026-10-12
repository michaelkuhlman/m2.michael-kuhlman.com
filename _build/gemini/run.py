#!/usr/bin/env python3
"""Generate every shot in shots.py with ~/bin/gemini-image (Michael's Gemini). Resumable: skips ids whose raw
file exists. Order: all main (_1) shots, then editorial banners, then secondary gallery shots.
Usage: run.py [--only id1,id2] [--redo]   Raw output: ~/m2-gemini-raw/<id>.jpeg"""
import importlib, json, os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shots as shotmod

RAW = os.path.expanduser('~/m2-gemini-raw')
os.makedirs(RAW, exist_ok=True)
args = sys.argv[1:]
only = set(args[args.index('--only') + 1].split(',')) if '--only' in args else None
redo = '--redo' in args

def rank(s):
    i = s['id']
    if not i.startswith('TS-'): return 1
    return 0 if i.endswith('_1') else 2

log = open(os.path.join(RAW, 'run.log'), 'a')
tried = set()
while True:  # re-read shots.py before every image so edits apply to a running batch
    importlib.reload(shotmod)
    todo = [s for s in sorted(shotmod.shots(), key=rank) if s['id'] not in tried
            and (not only or s['id'] in only) and (redo or not os.path.exists(os.path.join(RAW, s['id'] + '.jpeg')))]
    if not todo:
        break
    s = todo[0]; tried.add(s['id'])
    out = os.path.join(RAW, s['id'] + '.jpeg')
    for attempt in (1, 2):
        cmd = ['/home/kai/bin/gemini-image', s['prompt'], '--aspect', s['aspect'], '--out', RAW, '--name', s['id']]
        if s['ref']: cmd += ['--ref', os.path.abspath(s['ref'])]
        t = time.time()
        p = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=1800)
        msg = f"{time.strftime('%H:%M:%S')} {s['id']} try{attempt} exit={p.returncode} {time.time()-t:.0f}s"
        print(msg, flush=True); log.write(msg + '\n'); log.flush()
        saved = [l[6:].strip() for l in p.stdout.splitlines() if l.startswith('SAVED ')]
        if p.returncode == 0 and saved:
            os.replace(saved[0], out)
            for f in saved[1:]: os.remove(f)
            for f in os.listdir(RAW):
                if f.endswith('.web.jpg'): os.remove(os.path.join(RAW, f))
            break
        if p.returncode in (3, 4, 5):
            print(p.stdout[-800:], p.stderr[-800:]); sys.exit(p.returncode)
        log.write((p.stdout + p.stderr)[-1500:] + '\n')
print('DONE', flush=True)
