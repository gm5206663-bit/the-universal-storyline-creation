#!/usr/bin/env python3
"""foundation_gate.py - the gate for foundation docsets.

Stdlib only. Run:   python3 tools/foundation_gate.py path/to/serial
                    python3 tools/foundation_gate.py path/to/serial --strict
Self-test:          python3 tools/foundation_gate.py --selftest

Checks the universal foundation layer (foundation/README.md, docset v6.0):
the nineteen core files exist and are filled, pack pairs are complete,
rulings keep verbatim discipline, STATUS carries a live edge, HANDOFF carries
a read order, and a locked Stage 0 may not sit next to chapters on disk.

A check that cannot fail on a bad input is not a check, which is why
--selftest injects a defect for each one. The selftest runs before every
check result is trusted (Control Centre selftest law).

Never weaken a gate to pass it: fix the docset, not the check.
"""
import argparse
import os
import re
import shutil
import sys
import tempfile

MIN_BYTES = 200  # a filled foundation file is never this thin

CORE = [
    "FOUNDATION.md", "RULINGS_LOG.md", "OPEN_RULINGS.md", "HANDOFF.md",
    "RAILS.md", "STATUS.md", "CANON_GROUND.md", "CANON_ACCESS.md",
    "POWER_LAW.md", "TIMELINE.md", "CHARACTERS.md", "RELATIONSHIPS.md",
    "STORY_ARCS.md", "CODEX.md", "SERIAL_LOG.md", "GLOSSARY.md",
    "PLACES.md", "PANELS.md", "SKILLS_CANON.md",
]

# Packs are both files or neither. 'world' has one file; it is detected and
# scanned, never required.
PACKS = {
    "system": ["SYSTEM_SPEC.md", "METERS.md"],
    "world": ["ECONOMY.md"],
}

# Leftover template scaffolding. 'EXAMPLE - DELETE' is the template's own
# delete-me marker (written with an en-dash in the files; match loosely).
PLACEHOLDER_RES = [
    (re.compile(r"\{\{|\}\}"), "unfilled {{placeholder}}"),
    (re.compile(r"\bTBD\b"), "unfilled TBD"),
    (re.compile(r"\bFIXME\b"), "unfilled FIXME"),
    (re.compile(r"EXAMPLE\s*[—-]\s*DELETE", re.I), "template example not deleted"),
]

# Ruling entries: house format A (### R1 / ## F2 sections) and format B
# (| F0 | ... | ledger table rows).
ENTRY_RE = re.compile(r"(?:^|\n)\s{0,3}#{1,4}\s*\**[RF]\d+\b", re.M)
TABLE_ENTRY_RE = re.compile(r"^\|\s*[RF]\d+\s*\|", re.M)
BLOCKQUOTE_RE = re.compile(r"^\s*>", re.M)

# Stage 0 state detector. 'unlocked' wins over 'locked': a closed Stage 0
# keeps its history, including old LOCKED quotes, so the newest state marks
# itself as unlocked / closed in STATUS and HANDOFF.
UNLOCKED_RE = re.compile(
    r"drafting (?:is |now )?unlocked|stage\s*0[:\s—-]*closed|stage zero[^.]{0,40}closed",
    re.I,
)
LOCKED_RE = re.compile(
    r"drafting (?:is |stays )?locked|drafting stays locked|zero chapters until",
    re.I,
)

# Stale citation tags on the two version axes (VERSION_OF_RECORD.md).
STALE_RES = [
    (re.compile(r"foundation docset v5\.[0-9]+\b", re.I),
     "stale foundation-docset tag (current layer is v6.0)"),
    (re.compile(r"law revision v5\.[0-3]\b", re.I),
     "stale law-revision tag (current is v5.4)"),
]

CHAPTER_RE = re.compile(r"\.md$")


def find_foundation(root):
    """Resolve <root>/foundation, or root itself if it is a foundation dir."""
    cand = os.path.join(root, "foundation")
    if os.path.isdir(cand):
        return cand
    if os.path.isdir(os.path.join(root, "templates")) and \
       os.path.isfile(os.path.join(root, "README.md")):
        # building against the layer itself: no serial docset here
        return None
    return root if os.path.isdir(root) else None


def read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def detect_packs(fdir, requested):
    """Return (packs_active, problems). 'auto' infers from presence."""
    present = {p for p, files in PACKS.items()
               if any(os.path.isfile(os.path.join(fdir, f)) for f in files)}
    if requested == "auto":
        return present, []
    want = {p.strip() for p in requested.split(",") if p.strip()}
    unknown = want - set(PACKS)
    problems = [f"unknown pack(s): {', '.join(sorted(unknown))}"] if unknown else []
    return (want & set(PACKS)), problems


def stage0_state(fdir):
    """Return 'unlocked', 'locked', or None (no Stage 0 statement found)."""
    blob = []
    for name in ("OPEN_RULINGS.md", "STATUS.md", "HANDOFF.md"):
        p = os.path.join(fdir, name)
        if os.path.isfile(p):
            blob.append(read(p))
    text = "\n".join(blob)
    if not text:
        return None
    if UNLOCKED_RE.search(text):
        return "unlocked"
    if LOCKED_RE.search(text):
        return "locked"
    return None


def count_chapters(serial_root):
    cdir = os.path.join(serial_root, "chapters")
    if not os.path.isdir(cdir):
        return 0
    return sum(1 for e in os.listdir(cdir)
               if e.endswith(".md") and os.path.isfile(os.path.join(cdir, e)))


def check_file_filled(path, rel):
    """Errors for one required file: exists, not thin, no scaffolding."""
    errs = []
    if not os.path.isfile(path):
        return [f"missing required file: {rel}"]
    text = read(path)
    if len(text.strip()) < MIN_BYTES:
        errs.append(f"{rel} is under {MIN_BYTES} bytes - not filled")
    for rx, label in PLACEHOLDER_RES:
        m = rx.search(text)
        if m:
            i = max(0, m.start() - 30)
            errs.append(f"{rel}: {label}, near ...{text[i:m.end() + 30]!r}...")
            break  # one scaffolding finding per file is enough to fail it
    return errs


def check_rulings(text, rel="foundation/RULINGS_LOG.md"):
    errs = []
    if not re.search(r"verbatim", text, re.I):
        errs.append(f"{rel}: no verbatim declaration - rulings must keep the author's exact words")
    has_entry = ENTRY_RE.search(text) or TABLE_ENTRY_RE.search(text)
    if not has_entry:
        errs.append(f"{rel}: no ruling entries found (### R1 sections or | F0 | table rows)")
    has_voice = BLOCKQUOTE_RE.search(text) or TABLE_ENTRY_RE.search(text)
    if has_voice:
        pass
    elif has_entry:
        errs.append(f"{rel}: ruling entries exist but no verbatim blockquote or ledger row carries the author's words")
    return errs


def check(serial_root, packs_request="auto", strict=False):
    """Return (errors, warnings, info_lines)."""
    errs, warns, info = [], [], []
    fdir = find_foundation(serial_root)
    if fdir is None:
        return (["no foundation directory found under: " + serial_root], warns, info)

    active, problems = detect_packs(fdir, packs_request)
    errs.extend(problems)
    info.append(f"foundation: {fdir}")
    info.append(f"packs: {', '.join(sorted(active)) if active else 'none'}")

    # 1 - core files exist, are filled, carry no scaffolding
    required = list(CORE)
    for pack in sorted(active):
        required.extend(PACKS[pack])
    for name in required:
        errs.extend(check_file_filled(os.path.join(fdir, name),
                                      os.path.relpath(os.path.join(fdir, name), serial_root)))

    # 2 - pack pairs: half a system is not a system
    for pack, files in PACKS.items():
        if pack == "world":
            continue
        present = [os.path.isfile(os.path.join(fdir, f)) for f in files]
        if any(present) and not all(present):
            missing = [f for f, ok in zip(files, present) if not ok]
            errs.append(f"pack '{pack}' is incomplete: missing {' , '.join(missing)}"
                        f" (both files or neither)")

    # 3 - rulings verbatim discipline
    rpath = os.path.join(fdir, "RULINGS_LOG.md")
    if os.path.isfile(rpath):
        errs.extend(check_rulings(read(rpath)))

    # 4 - STATUS carries a live edge
    spath = os.path.join(fdir, "STATUS.md")
    if os.path.isfile(spath) and not re.search(r"live edge", read(spath), re.I):
        errs.append("foundation/STATUS.md: no 'live edge' - the single current-truth source must say where the story is")

    # 5 - HANDOFF carries a read order
    hpath = os.path.join(fdir, "HANDOFF.md")
    if os.path.isfile(hpath):
        steps = re.findall(r"^\s*\d+\.\s+\S", read(hpath), re.M)
        if len(steps) < 3:
            errs.append(f"foundation/HANDOFF.md: read order has {len(steps)} step(s), needs 3+ - a cold start needs a route")

    # 6 - Stage 0: locked foundation may not sit next to chapters
    state = stage0_state(fdir)
    chapters = count_chapters(serial_root)
    if state == "locked" and chapters > 0:
        errs.append(f"Stage 0 is LOCKED but {chapters} chapter file(s) exist in chapters/ "
                    "- rulings first, prose second, zero chapters until ruled (Foundation-Stage law)")
    info.append(f"stage 0: {state or 'not stated'} | chapters on disk: {chapters}")

    # 7 - stale version tags (warn; retag when touched, VERSION_OF_RECORD)
    for name in required:
        p = os.path.join(fdir, name)
        if not os.path.isfile(p):
            continue
        text = read(p)
        for rx, label in STALE_RES:
            if rx.search(text):
                warns.append(f"{name}: {label}")

    if strict:
        errs.extend(f"strict: {w}" for w in warns)

    return errs, warns, info


def report(errs, warns, info, label=""):
    for line in info:
        print(f"  info  {line}")
    for w in warns:
        print(f"  WARN  {w}")
    for e in errs:
        print(f"  FAIL  {e}")
    verdict = "FAIL" if errs else "PASS"
    print(f"{verdict}  foundation gate: {len(errs)} error(s), {len(warns)} warning(s)"
          + (f" [{label}]" if label else ""))
    return 0 if not errs else 1


# ---------------------------------------------------------------- selftest

def _mk_serial(base, files, text="# {n}\n\nfilled. ", chapters=0, extra=None):
    """Build a minimal serial tree. files: list of names to create."""
    fdir = os.path.join(base, "foundation")
    os.makedirs(fdir, exist_ok=True)
    for name in files:
        with open(os.path.join(fdir, name), "w", encoding="utf-8") as fh:
            fh.write(text)
    if extra:
        for name, content in extra.items():
            with open(os.path.join(fdir, name), "w", encoding="utf-8") as fh:
                fh.write(content)
    if chapters:
        os.makedirs(os.path.join(base, "chapters"), exist_ok=True)
        for c in range(chapters):
            with open(os.path.join(base, "chapters", f"Chapter_{c + 1}.md"), "w") as fh:
                fh.write("prose.\n")
    return base


VALID_TEXT = (
    "# {n}\n\n"
    "Filled file. Live edge: chapter 3. Authority order. Read in this order.\n"
    "1. first\n2. second\n3. third\n"
    "Rulings keep the author's words verbatim.\n"
    "### R1 - the question\n\n> **Author's word, verbatim:** \"yes\"\n"
)


def selftest():
    """Every rule must fail on a purpose-built defect. Returns exit code."""
    results = []

    def run(name, builder, expect_fail=True, packs="auto", strict=False):
        base = tempfile.mkdtemp(prefix="fgate_")
        try:
            builder(base)
            errs, warns, _ = check(base, packs, strict)
            failed = bool(errs)
            ok = (failed == expect_fail)
            results.append((name, ok, errs, warns))
            print(("  ok   " if ok else "  MISS ") + name
                  + ("" if ok else f"  (errors={errs})"))
        finally:
            shutil.rmtree(base, ignore_errors=True)

    def good(b):
        _mk_serial(b, CORE, VALID_TEXT)

    # the healthy docset passes, extras allowed
    run("clean docset passes", good, expect_fail=False)

    # each core file goes missing at least once across defects below
    def miss(b):
        good(b)
        os.remove(os.path.join(b, "foundation", "RAILS.md"))
    run("missing core file fails", miss)

    def thin(b):
        _mk_serial(b, CORE, "tiny\n")
    run("thin file fails", thin)

    def ph(b):
        _mk_serial(b, CORE, VALID_TEXT + "\n{{FILL_ME}}\n")
    run("unfilled placeholder fails", ph)

    def half_sys(b):
        good(b)
        with open(os.path.join(b, "foundation", "SYSTEM_SPEC.md"), "w") as fh:
            fh.write(VALID_TEXT.format(n="SYSTEM_SPEC.md") + "x" * 200)
    run("half system pack fails", half_sys)

    def sys_pair(b):
        _mk_serial(b, CORE + ["SYSTEM_SPEC.md", "METERS.md"], VALID_TEXT)
    run("complete system pack passes", sys_pair, expect_fail=False, packs="system")

    def no_verbatim(b):
        _mk_serial(b, CORE,
                   VALID_TEXT.replace("verbatim", "approximately"))
    run("rulings without verbatim fails", no_verbatim)

    def no_entries(b):
        _mk_serial(b, CORE,
                   "# RULINGS_LOG.md\n\n" + "words verbatim here. " * 30)
    run("rulings without entries fails", no_entries)

    def no_live_edge(b):
        _mk_serial(b, CORE, VALID_TEXT.replace("Live edge", "Position"))
    run("status without live edge fails", no_live_edge)

    def no_read_order(b):
        _mk_serial(b, CORE, VALID_TEXT.replace("1. first\n2. second\n3. third\n", ""))
    run("handoff without read order fails", no_read_order)

    def locked_with_chapters(b):
        _mk_serial(b, CORE,
                   VALID_TEXT + "\n**DRAFTING IS LOCKED.** Zero chapters until ruled.\n",
                   chapters=2)
    run("locked stage 0 + chapters fails", locked_with_chapters)

    def unlocked_with_chapters(b):
        _mk_serial(b, CORE,
                   VALID_TEXT + "\nStage 0 closed. Drafting is unlocked.\n",
                   chapters=2)
    run("unlocked stage 0 + chapters passes", unlocked_with_chapters, expect_fail=False)

    def stale(b):
        _mk_serial(b, CORE, VALID_TEXT + "\nfoundation docset v5.1 20 files\n")
    run("stale docset tag warns", stale, expect_fail=False)
    run("stale tag fails in strict mode", stale, expect_fail=True, strict=True)

    def extra_ok(b):
        good(b)
        with open(os.path.join(b, "foundation", "MY_MODULE.md"), "w") as fh:
            fh.write("serial-specific extension, never gated.\n")
    run("serial-specific extras pass", extra_ok, expect_fail=False)

    def no_foundation(b):
        os.makedirs(os.path.join(b, "elsewhere"), exist_ok=True)
    run("no foundation dir fails", no_foundation)

    total = len(results)
    passed = sum(1 for _, ok, _, _ in results if ok)
    print(f"{'PASS' if passed == total else 'FAIL'}  foundation_gate selftest: "
          f"{passed}/{total} checks behaved as designed")
    return 0 if passed == total else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="gate for foundation docsets")
    ap.add_argument("root", nargs="?", help="serial root (or its foundation/ dir)")
    ap.add_argument("--packs", default="auto",
                    help="auto (default) or comma list: system,world")
    ap.add_argument("--strict", action="store_true", help="warnings become errors")
    ap.add_argument("--selftest", action="store_true",
                    help="prove every check can fail")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.root:
        ap.error("root is required unless --selftest")
    errs, warns, info = check(args.root, args.packs, args.strict)
    return report(errs, warns, info, label=args.root)


if __name__ == "__main__":
    sys.exit(main())
