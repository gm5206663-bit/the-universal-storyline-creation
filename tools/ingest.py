#!/usr/bin/env python3
"""Merge a validated contribution into the state layer.

Usage:  python3 tools/ingest.py intake/drop/<file>.json
        python3 tools/ingest.py --all

Nothing is ingested unless it passes validation first. On success the file moves
to intake/accepted/ and an entry is appended to state/log.json, so every growth
event is traceable to who filed it and when.

This is append-only by design. A contribution can ADD a firewall, an anchor, a
decision or a correction. It cannot silently overwrite existing state - a
correction is recorded as a correction, which keeps the old value visible and
shows why it changed.
"""
import json, os, sys, shutil, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schema import KINDS
import validate as V

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, 'state')
LOG = os.path.join(STATE, 'log.json')

# Git does not track empty directories, so a fresh clone or an unpacked bundle
# can arrive without the intake tree even though .gitkeep files are committed -
# and any packaging step that drops empty directories will lose them outright.
# Recreate them here rather than failing, because the grow loop is the entire
# reason this system exists.
for _d in ('drop', 'accepted', 'rejected'):
    os.makedirs(os.path.join(ROOT, 'intake', _d), exist_ok=True)


def load(p, default):
    if not os.path.exists(p):
        return default
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def save(p, data):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def collection_path(kind):
    """Where each kind of contribution lands."""
    if kind == 'project':   return os.path.join(STATE, 'projects_registry.json')
    if kind == 'firewall':  return os.path.join(STATE, 'firewalls.json'), 'registry'
    if kind == 'canon':     return os.path.join(STATE, 'canon_contributions.json')
    return os.path.join(STATE, 'contributions.json')


def append_record(kind, item, log):
    """Append one contribution, returning the id assigned."""
    if kind == 'firewall':
        path, key = collection_path(kind)
        data = load(path, {'registry': []})
        existing = data.get(key, [])
        nxt = max([e.get('id', 0) for e in existing], default=0) + 1
        item = dict(item)
        item['id'] = nxt
        item.setdefault('project', 'unassigned')
        existing.append(item)
        data[key] = existing
        save(path, data)
        return f"firewall#{nxt}"

    if kind == 'project':
        path = collection_path(kind)
        data = load(path, {'projects': []})
        if any(p.get('id') == item.get('id') for p in data['projects']):
            raise ValueError(f"project id {item['id']!r} already exists — "
                             f"file a 'correction' instead of a duplicate 'project'")
        data['projects'].append(item)
        save(path, data)
        return f"project:{item['id']}"

    path = collection_path(kind)
    data = load(path, {'records': []})
    records = data['records']
    nxt = max([r.get('seq', 0) for r in records], default=0) + 1
    item = dict(item)
    item['seq'] = nxt
    # keep the kind on the record: build.py renders a Kind column from it, and
    # a generic record file needs to say what each record is
    item['kind'] = kind
    records.append(item)
    save(path, data)
    return f"{kind}#{nxt}"


def ingest(path):
    r = V.validate(path)
    if not r.ok:
        print(f"  REJECTED {os.path.basename(path)} — {len(r.errors)} error(s)")
        for e in r.errors:
            print(f"      - {e}")
        dest = os.path.join(ROOT, 'intake', 'rejected', os.path.basename(path))
        shutil.move(path, dest)
        rep = dest[:-5] + '.report.txt'
        with open(rep, 'w', encoding='utf-8') as f:
            f.write(r.render() + "\n")
        print(f"      moved to intake/rejected/, report at {os.path.basename(rep)}")
        return False

    raw = json.load(open(path, encoding='utf-8'))
    contributions = raw if isinstance(raw, list) else [raw]

    log = load(LOG, {'events': []})
    now = datetime.datetime.now().isoformat(timespec='seconds')
    ids = []

    for c in contributions:
        kind = c['kind']
        body = {k: v for k, v in c.items() if k != 'kind'}
        try:
            ids.append(append_record(kind, body, log))
        except ValueError as e:
            print(f"  REJECTED {os.path.basename(path)} — {e}")
            dest = os.path.join(ROOT, 'intake', 'rejected', os.path.basename(path))
            shutil.move(path, dest)
            return False

    prov = contributions[0].get('provenance', {}) if isinstance(contributions[0], dict) else {}
    log['events'].append({
        'when': now,
        'file': os.path.basename(path),
        'agent': prov.get('agent', 'unknown'),
        'ids': ids,
        'count': len(ids),
    })
    save(LOG, log)

    dest = os.path.join(ROOT, 'intake', 'accepted', os.path.basename(path))
    shutil.move(path, dest)
    print(f"  ACCEPTED {os.path.basename(path)} — {len(ids)} record(s): {', '.join(ids)}")
    print(f"      filed by: {prov.get('agent','unknown')} | moved to intake/accepted/")
    return True


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    if args[0] == '--all':
        d = os.path.join(ROOT, 'intake', 'drop')
        files = sorted(os.path.join(d, f) for f in os.listdir(d)
                       if f.endswith('.json')) if os.path.isdir(d) else []
    else:
        files = args
    if not files:
        print("  intake/drop/ is empty — nothing to ingest")
        return 0
    ok = sum(1 for f in files if ingest(f))
    print(f"\n  {ok}/{len(files)} ingested. Rebuild the site: python3 tools/build.py")
    return 0


if __name__ == '__main__':
    sys.exit(main())
