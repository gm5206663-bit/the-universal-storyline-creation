#!/usr/bin/env python3
"""Validate a contribution against the schema before it can enter the state layer.

Usage:  python3 tools/validate.py intake/drop/<file>.json
        python3 tools/validate.py --all

Exits 0 if valid, 1 if not. A rejected file stays in intake/drop/ and a report is
written next to it so the filing agent can see exactly what to fix.

The rules here are deliberately strict. A state layer that accepts anything
becomes a pile of notes, and then no agent can trust it.
"""
import json, os, re, sys, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schema import (KINDS, FIREWALL_STATES, CONFIDENCE_LEVELS,
                    PROJECT_STATUSES, RESERVED_FIELDS)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CJK = re.compile(r'[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]')
FILENAME = re.compile(r'^[A-Za-z0-9_.\-]+$')


def iter_strings(obj):
    """Yield every string inside a decoded JSON structure, at any depth.

    Gates 1 and 2 run over these rather than over the raw file bytes, because
    the raw bytes of a JSON file legitimately contain escape sequences that
    stand for something else once decoded.
    """
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from iter_strings(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from iter_strings(v)


class Report:
    def __init__(self, path):
        self.path = path
        self.errors = []
        self.warnings = []

    def err(self, msg):  self.errors.append(msg)
    def warn(self, msg): self.warnings.append(msg)

    @property
    def ok(self): return not self.errors

    def render(self):
        name = os.path.basename(self.path)
        out = [f"VALIDATION REPORT — {name}",
               f"checked: {datetime.datetime.now().isoformat(timespec='seconds')}",
               f"result:  {'PASS' if self.ok else 'FAIL'}", ""]
        if self.errors:
            out.append(f"ERRORS ({len(self.errors)}) — must fix before this can be ingested:")
            out += [f"  - {e}" for e in self.errors] + [""]
        if self.warnings:
            out.append(f"WARNINGS ({len(self.warnings)}) — allowed, but look at these:")
            out += [f"  - {w}" for w in self.warnings] + [""]
        if self.ok and not self.warnings:
            out.append("No issues. Run: python3 tools/ingest.py " + self.path)
        return "\n".join(out)


def validate(path):
    r = Report(path)

    # ---- the file must parse ----
    try:
        raw = open(path, encoding='utf-8').read()
    except Exception as e:
        r.err(f"cannot read file: {e}")
        return r

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        r.err(f"not valid JSON: {e}")
        return r

    # ---- gates 1 and 2 scan DECODED values, not raw bytes ----
    #
    # JSON has no way to put a raw newline inside a string literal: it must be
    # written as the two-character escape. So scanning the raw file for that
    # escape flags every legitimate multi-line value, which is the check
    # matching the normal form of its own container format.
    #
    # The same applies to gate 1 in reverse: CJK written as a \u escape is
    # invisible to a raw-bytes scan but present in the decoded value.
    #
    # Both gates therefore run over decoded strings, which is what actually
    # ships downstream into state/ and onto the page.
    for s in iter_strings(data):
        m = CJK.search(s)
        if m:
            r.err(f"unreadable script {m.group()!r} in a decoded value "
                  f"(gate 1 — CJK/kana/hangul never ships)")
            break
    for s in iter_strings(data):
        if '\\n' in s:
            r.err("literal backslash-n sequence in a decoded value "
                  "(gate 2 — use a real newline)")
            break

    # ---- filename law ----
    if not FILENAME.match(os.path.basename(path)):
        r.err("filename breaks the filename law: ASCII letters, digits, "
              "underscores, dots and hyphens only")

    # ---- envelope ----
    contributions = data if isinstance(data, list) else [data]
    if not contributions:
        r.err("empty contribution")
        return r

    seen_keys = set()
    for i, c in enumerate(contributions):
        tag = f"[{i}]" if isinstance(data, list) else ""
        if not isinstance(c, dict):
            r.err(f"{tag} contribution must be a JSON object")
            continue

        kind = c.get('kind')
        if not kind:
            r.err(f"{tag} missing 'kind'")
            continue
        if kind not in KINDS:
            r.err(f"{tag} unknown kind {kind!r} — must be one of: "
                  f"{', '.join(sorted(KINDS))}")
            continue

        spec = KINDS[kind]

        for f in spec['required']:
            if f not in c or c[f] in (None, "", []):
                r.err(f"{tag} kind={kind} missing required field {f!r}")

        allowed = set(spec['required']) | set(spec['optional']) | {'kind', 'id', 'provenance'}
        unknown = set(c) - allowed
        if unknown:
            r.warn(f"{tag} kind={kind} has unrecognised fields {sorted(unknown)} "
                   f"— they will be stored but nothing reads them")

        for f in RESERVED_FIELDS:
            if f in c:
                r.err(f"{tag} {f!r} is reserved — it changes the shape of the "
                      f"system and needs the user, not a contribution")

        # ---- kind-specific rules ----
        if kind == 'firewall':
            st = c.get('state')
            if st and st not in FIREWALL_STATES:
                r.err(f"{tag} state {st!r} is not a defined firewall state. "
                      f"Adding a new state is a law change and needs the user. "
                      f"Defined: {', '.join(FIREWALL_STATES)}")
            # the field that prevents regressions
            ec = c.get('earliest_change', '')
            if ec and len(str(ec)) < 12:
                r.warn(f"{tag} earliest_change is very short — this field is what "
                       f"stops the next agent letting the character find out early")

        elif kind == 'canon':
            conf = c.get('confidence')
            if conf and conf not in CONFIDENCE_LEVELS:
                r.err(f"{tag} confidence {conf!r} is not a defined tag. "
                      f"Defined: {', '.join(CONFIDENCE_LEVELS)}")
            if conf == 'canon' and not c.get('sources'):
                r.err(f"{tag} claiming [canon] without naming sources. "
                      f"Either cite the sources or downgrade the tag.")

        elif kind == 'project':
            st = c.get('status')
            if st and st not in PROJECT_STATUSES:
                r.err(f"{tag} status {st!r} not defined. "
                      f"Defined: {', '.join(PROJECT_STATUSES)}")
            pid = c.get('id')
            if pid and not re.match(r'^[a-z0-9_]+$', pid):
                r.err(f"{tag} project id {pid!r} must be lowercase ascii and underscores")
            p = c.get('path')
            if p and not FILENAME.match(p.replace('/', '_')):
                r.warn(f"{tag} project path is not upload-safe")

        elif kind == 'correction':
            if str(c.get('was', '')).strip() == str(c.get('now', '')).strip():
                r.err(f"{tag} a correction where 'was' equals 'now' changes nothing")

        elif kind == 'decision':
            if not c.get('authorized_by'):
                r.warn(f"{tag} decision has no authorized_by — record who authorised "
                       f"it or the next agent cannot tell a ruling from a guess")

        # ---- duplicate detection ----
        key = (kind, json.dumps({k: v for k, v in sorted(c.items())
                                 if k in spec['required']}, sort_keys=True,
                                ensure_ascii=False))
        if key in seen_keys:
            r.err(f"{tag} duplicate of an earlier contribution in the same file")
        seen_keys.add(key)

    return r


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2

    if args[0] == '--all':
        d = os.path.join(ROOT, 'intake', 'drop')
        files = sorted(os.path.join(d, f) for f in os.listdir(d)
                       if f.endswith('.json')) if os.path.isdir(d) else []
        if not files:
            print("  intake/drop/ is empty — nothing to validate")
            return 0
    else:
        files = args

    failed = 0
    for f in files:
        r = validate(f)
        print(r.render())
        print()
        out = f[:-5] + '.report.txt' if f.endswith('.json') else f + '.report.txt'
        with open(out, 'w', encoding='utf-8') as fh:
            fh.write(r.render() + "\n")
        if not r.ok:
            failed += 1

    print(f"  {len(files)} file(s) checked, {failed} failed")
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
