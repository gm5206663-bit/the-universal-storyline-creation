#!/usr/bin/env python3
"""Extract real project state from the workspace into state/*.json.

Run from the repo root's control_centre/ directory. Every number written here is
measured from disk, never typed by hand. Re-run any time the workspace changes.

If the fiction workspace is not present alongside control_centre/ - which is the
normal case for an agent who has been handed the Control Centre on its own - this
script leaves the committed state/workspace.json untouched and exits 0. The
measurements are already stored in state/, so the bootstrap and the site still
build. Nothing downstream depends on re-deriving them.
"""
import json, os, re, subprocess, hashlib, datetime, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WS   = os.path.dirname(ROOT)
STATE = os.path.join(ROOT, 'state')

# The directories that must exist for measurement to mean anything. If the first
# one is missing we are almost certainly looking at a bare Control Centre handoff
# rather than the full workspace.
REQUIRED_DIRS = ['blue_silver', 'SOUL_LAND_UNIVERSAL_KIT']


def workspace_present():
    return all(os.path.isdir(os.path.join(WS, d)) for d in REQUIRED_DIRS)

def is_binary(p):
    try:
        with open(p, 'rb') as f: head = f.read(4096)
    except Exception: return True
    if b'\0' in head: return True
    return head[:4] in (b'PK\x03\x04', b'\x89PNG', b'\xff\xd8\xff', b'GIF8', b'%PDF', b'\x1f\x8b')

def walk_files(d):
    for r, ds, fs in os.walk(d):
        ds[:] = [x for x in ds if x != '__pycache__']
        for f in fs:
            yield os.path.join(r, f)

def measure(path):
    files = list(walk_files(path))
    words = 0
    binaries = []
    for p in files:
        if p.endswith(('.md', '.txt')):
            if is_binary(p):
                binaries.append(os.path.relpath(p, WS))
            else:
                try: words += len(open(p, encoding='utf-8', errors='replace').read().split())
                except Exception: pass
    return {'files': len(files), 'words': words, 'mislabeled_binaries': sorted(binaries)}


# ---------- cold-start guard ----------
# An agent handed the Control Centre on its own will not have the fiction
# workspace beside it. Without this check the script dies with a
# FileNotFoundError partway through, and `make all` fails at the first command -
# which is exactly the moment a handoff has to work.
#
# The committed state/workspace.json already holds the measurements, so there is
# nothing to re-derive. Leave it alone and let the rest of the pipeline run.
if not workspace_present():
    missing = [d for d in REQUIRED_DIRS if not os.path.isdir(os.path.join(WS, d))]
    print("  workspace not present alongside control_centre/ "
          f"(missing: {', '.join(missing)})")
    kept = os.path.join(STATE, 'workspace.json')
    if os.path.exists(kept):
        with open(kept, encoding='utf-8') as f:
            prev = json.load(f)
        t = prev.get('totals', {})
        print(f"  keeping the committed measurements: "
              f"{t.get('projects', 0)} projects, {t.get('files', 0)} files, "
              f"{t.get('words', 0):,} words, measured {prev.get('generated', '?')}")
        print("  nothing re-measured. Run this again beside the real workspace to refresh.")
    else:
        print("  no committed measurements to fall back on - state/workspace.json absent")
    sys.exit(0)


# ---------- projects ----------
PROJECTS = [
    ('blue_silver',              'Blue Silver',      'Book One complete — 15 rebuilt chapters', 'gate-pass'),
    ('sl4_fire_phoenix',         'SL4 Fire Phoenix', 'After Chapter 31 — The Ticket Owed to Fire', 'live'),
    ('SOUL_LAND_UNIVERSAL_KIT',  'Universal Kit',    '11 laws + 13 templates + verify tooling', 'portable'),
    ('SOUL_LAND_NEW',            'Soul Land New',    'Tian Yu — 6 chapters, pre-Chapter-11', 'active'),
    ('reference/sl3_lin_hao',    'SL3 Lin Hao',      'Reference archive — craft only, never canon', 'reference'),
    ('soul_land_starter',        'Starter Pack',     'Blank-project bootstrap skeleton', 'template'),
]
projects = []
tot_f = tot_w = 0
for path, name, edge, status in PROJECTS:
    m = measure(os.path.join(WS, path))
    tot_f += m['files']; tot_w += m['words']
    projects.append({'id': path.replace('/', '_'), 'name': name, 'path': path,
                     'files': m['files'], 'words': m['words'], 'live_edge': edge,
                     'status': status, 'mislabeled_binaries': m['mislabeled_binaries']})

# ---------- blue silver chapters ----------
bs = []
cdir = os.path.join(WS, 'blue_silver/chapters_rebuilt')
for fn in sorted(os.listdir(cdir)):
    if not fn.startswith('Chapter_') or not fn.endswith('.md'): continue
    p = os.path.join(cdir, fn)
    txt = open(p, encoding='utf-8').read()
    m = re.search(r'years\s+(\d+)\s*[\u2013-]\s*(\d+)', txt)
    bs.append({'file': fn, 'title': re.sub(r'^Chapter_\d+_|\.md$', '', fn).replace('_', ' '),
               'n': int(re.search(r'Chapter_(\d+)', fn).group(1)),
               'words': len(txt.split()),
               'year_start': int(m.group(1)) if m else None,
               'year_end': int(m.group(2)) if m else None,
               'sha256': hashlib.sha256(txt.encode()).hexdigest()[:16]})

# ---------- kit laws ----------
laws = []
kdir = os.path.join(WS, 'SOUL_LAND_UNIVERSAL_KIT')
for fn in sorted(os.listdir(kdir)):
    if re.match(r'^\d\d_[A-Z_]+\.md$', fn):
        txt = open(os.path.join(kdir, fn), encoding='utf-8').read()
        laws.append({'file': fn, 'n': int(fn[:2]), 'words': len(txt.split()),
                     'title': txt.split('\n')[0].lstrip('# ').strip()})
templates = sorted(f for f in os.listdir(os.path.join(kdir, 'templates')) if f.endswith('.md'))

# ---------- sl4 chapters ----------
sl4dir = os.path.join(WS, 'sl4_fire_phoenix/soul_land_4_fire_phoenix/chapters')
sl4 = [f for f in sorted(os.listdir(sl4dir)) if re.match(r'^Chapter_\d+\.md$', f)]

state = {
    'generated': datetime.date.today().isoformat(),
    # Relative, not absolute. An absolute path here is true only on the machine
    # that measured it, so every clone elsewhere rewrites this line on its first
    # `make` and shows a dirty tree for a change nobody actually made.
    'workspace': os.path.relpath(WS, ROOT),
    'totals': {'projects': len(projects), 'files': tot_f, 'words': tot_w,
               'blue_silver_chapters': len(bs), 'sl4_chapters': len(sl4),
               'kit_laws': len(laws), 'kit_templates': len(templates)},
    'projects': projects,
    'blue_silver_chapters': bs,
    'kit_laws': laws,
    'kit_templates': templates,
    'sl4_chapters': sl4,
}
os.makedirs(STATE, exist_ok=True)
out = os.path.join(STATE, 'workspace.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)
print(f"  wrote {os.path.relpath(out, ROOT)}")
print(f"  projects {len(projects)} | files {tot_f} | words {tot_w:,}")
print(f"  blue_silver chapters {len(bs)} | sl4 chapters {len(sl4)}")
print(f"  kit laws {len(laws)} | templates {len(templates)}")
