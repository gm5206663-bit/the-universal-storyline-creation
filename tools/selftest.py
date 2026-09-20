#!/usr/bin/env python3
"""Negative tests for the Control Centre toolchain.

Usage:  python3 tools/selftest.py

Every rejection rule in validate.py gets two cases: one that MUST be rejected,
and a minimal valid counterpart that MUST pass. A rule that fires on the valid
case is a false positive; a rule that stays silent on the bad case is a hole.
Both are caught here.

This exists because of a specific past failure: tools/verify.py in the Universal
Kit once reported fifteen failures against a proven 33,100-word serial, and every
one of them was a false positive. A gate nobody has tested is a guess.

Exit 0 if every rule behaves, 1 otherwise.
"""
import json, os, sys, tempfile, shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import validate as V

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PASS = 0
FAIL = 0
NOTES = []


def check(name, contrib, should_pass, expect_substring=None, filename='t.json'):
    """Write a contribution to a temp file, validate it, assert the outcome.

    should_pass=True  -> validator must report no errors
    should_pass=False -> validator must report at least one error, and if
                         expect_substring is given, one error must contain it
    """
    global PASS, FAIL
    tmp = tempfile.mkdtemp(prefix='cc_selftest_')
    path = os.path.join(tmp, filename)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            if isinstance(contrib, str):
                f.write(contrib)
            else:
                json.dump(contrib, f, ensure_ascii=False)
        r = V.validate(path)

        if should_pass:
            if r.ok:
                PASS += 1
                print(f"  ok    {name}")
            else:
                FAIL += 1
                print(f"  FAIL  {name} — expected PASS but got errors:")
                for e in r.errors:
                    print(f"          - {e}")
        else:
            if r.ok:
                FAIL += 1
                print(f"  FAIL  {name} — expected rejection but validator passed it")
            elif expect_substring and not any(expect_substring in e for e in r.errors):
                FAIL += 1
                print(f"  FAIL  {name} — rejected, but not for the expected reason")
                print(f"          wanted substring: {expect_substring!r}")
                for e in r.errors:
                    print(f"          got: {e[:110]}")
            else:
                PASS += 1
                print(f"  ok    {name}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# A minimal valid firewall, reused as the "must pass" baseline.
VALID_FW = {
    "kind": "firewall",
    "project": "blue_silver",
    "who": "Test Person",
    "state": "KNOWN",
    "topic": "A test topic",
    "belief": "They believe a testable thing.",
    "earliest_change": "A later on-page event supported by evidence.",
    "rule": "They may not act on what they do not know.",
    "provenance": {"agent": "selftest", "date": "2026-09-18"},
}


def section(title):
    print(f"\n{title}")
    print("-" * len(title))


def main():
    global PASS, FAIL

    print("CONTROL CENTRE SELFTEST")
    print("negative tests for validate.py — every rule gets a bad case and a good case")

    # ---------------- baseline ----------------
    section("Baseline")
    check("minimal valid firewall passes", VALID_FW, True)
    check("valid firewall without provenance passes (provenance is optional)",
          {k: v for k, v in VALID_FW.items() if k != 'provenance'}, True)
    check("array of two valid contributions passes",
          [VALID_FW, dict(VALID_FW, who="Second Person")], True)

    # ---------------- parse-level ----------------
    section("Parse level")
    check("malformed JSON is rejected", "{not json at all", False, "not valid JSON")
    check("empty array is rejected", [], False, "empty contribution")
    check("non-object contribution is rejected", ["just a string"], False,
          "must be a JSON object")

    # ---------------- gate 1: unreadable script ----------------
    section("Gate 1 - unreadable script")
    check("CJK in a string is rejected",
          dict(VALID_FW, belief="They believe \u84dd\u94f6 things."), False,
          "unreadable script")
    check("kana is rejected",
          dict(VALID_FW, belief="They believe \u3053\u308c things."), False,
          "unreadable script")
    check("hangul is rejected",
          dict(VALID_FW, belief="They believe \ud55c\uad6d things."), False,
          "unreadable script")
    # the false-positive guard: em dashes and box drawing must NOT trip gate 1
    check("em dash and en dash are allowed (not a blanket non-ASCII ban)",
          dict(VALID_FW, belief="They believe this \u2014 and that \u2013 not the other."), True)
    check("box-drawing characters are allowed",
          dict(VALID_FW, belief="Tree: \u251c\u2500\u2500 \u2514\u2500\u2500 branch."), True)
    check("bullet marker is allowed",
          dict(VALID_FW, belief="The \u25c6 marker stays out of prose."), True)

    # ---------------- gate 2: literal backslash-n ----------------
    section("Gate 2 - literal backslash-n (decoded values only)")
    # The regression this section exists for: JSON cannot hold a raw newline in a
    # string literal, so the two-character escape is the NORMAL on-disk form.
    # Scanning raw bytes flagged every legitimate multi-line value.
    check("a real newline inside a JSON string is allowed",
          {"kind": "note", "text": "line one\nline two"}, True)
    check("a multi-line belief with several newlines is allowed",
          dict(VALID_FW, belief="First line.\nSecond line.\nThird line."), True)
    check("a literal backslash-n surviving into the VALUE is rejected",
          {"kind": "note", "text": "line one\\nline two"}, False, "backslash-n")
    check("a literal backslash-n nested deep in the structure is rejected",
          {"kind": "firewall", "who": "X", "state": "KNOWN", "topic": "t",
           "earliest_change": "later, with evidence", "rule": "r",
           "provenance": {"agent": "a\\nb", "date": "2026-09-18"}}, False, "backslash-n")

    # ---------------- gate 1 escape blind spot ----------------
    section("Gate 1 - CJK hidden behind a unicode escape")
    # json.dump with ensure_ascii=True writes CJK as \uXXXX, which a raw-bytes
    # scan cannot see. Decoded-value scanning catches it either way.
    raw_escaped = json.dumps(dict(VALID_FW, belief="They believe \u84dd\u94f6 things."),
                             ensure_ascii=True)
    check("CJK written as a \\u escape is still rejected", raw_escaped, False,
          "unreadable script")
    check("CJK written directly is rejected",
          dict(VALID_FW, belief="They believe \u84dd\u94f6 things."), False,
          "unreadable script")

    # ---------------- filename law ----------------
    section("Filename law")
    check("filename with a space is rejected", VALID_FW, False,
          "filename law", filename="bad name.json")
    check("filename with CJK is rejected", VALID_FW, False,
          "filename law", filename="\u84dd.json")
    check("underscore/dot/hyphen filename is allowed", VALID_FW, True,
          filename="good_name-1.2.json")

    # ---------------- envelope ----------------
    section("Envelope")
    check("missing kind is rejected",
          {k: v for k, v in VALID_FW.items() if k != 'kind'}, False, "missing 'kind'")
    check("unknown kind is rejected", dict(VALID_FW, kind="prophecy"), False,
          "unknown kind")
    for kind in ['project', 'firewall', 'anchor', 'canon', 'lock',
                 'decision', 'correction', 'note']:
        check(f"kind '{kind}' is recognised as a valid kind name",
              {"kind": kind}, False, "missing required field")

    # ---------------- required fields ----------------
    section("Required fields, per kind")
    required = {
        'firewall': ['who', 'state', 'topic', 'earliest_change', 'rule'],
        'project': ['id', 'name', 'path', 'status', 'live_edge'],
        'anchor': ['anchor', 'year'],
        'canon': ['claim', 'confidence'],
        'lock': ['lock', 'value'],
        'decision': ['decision', 'reason'],
        'correction': ['was', 'now', 'reason'],
        'note': ['text'],
    }
    for kind, fields in required.items():
        for field in fields:
            base = dict(VALID_FW)
            base['kind'] = kind
            # supply every required field with a filler, then remove one
            for f in fields:
                base[f] = f"filler_{f}"
            base.pop(field)
            check(f"{kind}: missing '{field}' is rejected", base, False,
                  f"missing required field {field!r}")

    # ---------------- reserved fields ----------------
    section("Reserved fields")
    for res in ['authority_order', 'seven_gates', 'gate_scope_warning', '_comment']:
        check(f"reserved field '{res}' is rejected",
              dict(VALID_FW, **{res: "x"}), False, "reserved")

    # ---------------- firewall states ----------------
    section("Firewall states")
    valid_states = ["KNOWN", "KNOWN PARTLY", "SUSPICION", "DISBELIEF",
                    "UNKNOWN", "FALSE BELIEF", "HIDDEN"]
    for st in valid_states:
        check(f"state '{st}' is accepted", dict(VALID_FW, state=st), True)
    for st in ["MAYBE", "known", "Known", "PROBABLY KNOWN", "HIDDEN FROM READER"]:
        check(f"state {st!r} is rejected", dict(VALID_FW, state=st), False,
              "not a defined firewall state")
    # An empty string is caught by the required-field check, not the state check.
    # That is correct behaviour - an empty state IS a missing field - so assert
    # the reason it actually fails rather than the reason I first guessed.
    check("empty state is rejected as a missing field",
          dict(VALID_FW, state=""), False, "missing required field 'state'")
    check("short earliest_change warns but still passes",
          dict(VALID_FW, earliest_change="soon"), True)

    # ---------------- canon confidence ----------------
    section("Canon confidence tags")
    for conf in ['fan', 'design', 'user ruling', 'on page', 'reported']:
        check(f"confidence '{conf}' needs no sources",
              {"kind": "canon", "claim": "A test claim.", "confidence": conf}, True)
    check("confidence 'canon' with sources passes",
          {"kind": "canon", "claim": "A test claim.", "confidence": "canon",
           "sources": "three secondary sources agree"}, True)
    check("confidence 'canon' without sources is rejected",
          {"kind": "canon", "claim": "A test claim.", "confidence": "canon"}, False,
          "without naming sources")
    check("undefined confidence tag is rejected",
          {"kind": "canon", "claim": "A test claim.", "confidence": "probably"}, False,
          "not a defined tag")

    # ---------------- project rules ----------------
    section("Project rules")
    VALID_PROJ = {"kind": "project", "id": "test_serial", "name": "Test Serial",
                  "path": "test_serial/", "status": "active",
                  "live_edge": "Chapter 1"}
    check("valid project passes", VALID_PROJ, True)
    for st in ['live', 'active', 'gate-pass', 'portable', 'reference',
               'template', 'external', 'paused', 'superseded']:
        check(f"status '{st}' is accepted", dict(VALID_PROJ, status=st), True)
    check("undefined project status is rejected",
          dict(VALID_PROJ, status="wonderful"), False, "not defined")
    check("project id with uppercase is rejected",
          dict(VALID_PROJ, id="TestSerial"), False, "lowercase ascii")
    check("project id with a hyphen is rejected",
          dict(VALID_PROJ, id="test-serial"), False, "lowercase ascii")
    check("project id with underscores is accepted",
          dict(VALID_PROJ, id="test_serial_v2"), True)

    # ---------------- correction rule ----------------
    section("Correction rule")
    check("correction with was == now is rejected",
          {"kind": "correction", "was": "7,000 years", "now": "7,000 years",
           "reason": "No actual change."}, False, "changes nothing")
    check("correction with a real change passes",
          {"kind": "correction", "was": "7,000 years", "now": "9,000 years",
           "reason": "Recounted from the continuity ledger."}, True)

    # ---------------- duplicates ----------------
    section("Duplicate detection")
    check("two identical contributions in one file are rejected",
          [VALID_FW, dict(VALID_FW)], False, "duplicate")
    check("two contributions differing in a required field pass",
          [VALID_FW, dict(VALID_FW, who="Someone Else")], True)

    # ---------------- warnings (must NOT be errors) ----------------
    section("Warnings must not block ingestion")
    check("unrecognised field warns but passes",
          dict(VALID_FW, colour="blue"), True)
    check("decision without authorized_by warns but passes",
          {"kind": "decision", "decision": "A decision.", "reason": "Because."}, True)

    # ---------------- the self-referential trap ----------------
    section("Self-referential trap (the recurring failure)")
    # A file whose text DESCRIBES the gates must not trip them.
    check("a note describing the placeholder gate is not itself flagged",
          {"kind": "note",
           "text": "No placeholder text left in a shipped file, and no TODO or FIXME remains."},
          True)
    check("a note naming the firewall states is not itself flagged",
          {"kind": "note",
           "text": "Valid states are KNOWN, UNKNOWN, SUSPICION, DISBELIEF, "
                   "FALSE BELIEF, HIDDEN and KNOWN PARTLY."}, True)
    check("a note reporting a zero count is not itself flagged",
          {"kind": "note", "text": "Audit result: TODO/FIXME/TBD = 0 failures."}, True)

    # ---------------- summary ----------------
    total = PASS + FAIL
    print(f"\n{'=' * 62}")
    print(f"  {PASS}/{total} checks passed")
    if FAIL:
        print(f"  {FAIL} FAILED — a rule is either too loose or too strict")
        print("  Do not ship a change to validate.py while this is red.")
    else:
        print("  every rejection rule fires on its bad case and stays")
        print("  silent on its good case")
    print(f"{'=' * 62}")
    return 1 if FAIL else 0


if __name__ == '__main__':
    sys.exit(main())
