# CONTROL CENTRE — CONTRIBUTION PROTOCOL

This system grows by contribution. Anyone — you, or any agent, on any platform —
can add to it. This document is the contract. Read it before filing anything.

---

## The shape of the system

```
control_centre/
├── index.html              GENERATED — never hand-edit
├── TRANSFER_BOOTSTRAP.txt  GENERATED — never hand-edit
├── PROTOCOL.md             this file
├── state/                  the data. hand-curated + contributions
│   ├── workspace.json      measured from disk by tools/extract_state.py
│   ├── canon.json          canon spine, rank ladder, ring ages, user rulings
│   ├── laws.json           twelve locks, seven gates, pipeline, firewall states
│   ├── firewalls.json      the knowledge firewall registry
│   ├── log.json            every growth event, append-only
│   ├── contributions.json  contributed records (created on first ingest)
│   ├── canon_contributions.json   contributed canon claims
│   ├── projects_registry.json     contributed projects
│   └── projects/           one file per project
├── intake/
│   ├── drop/               FILE YOUR CONTRIBUTION HERE
│   ├── accepted/           merged, with provenance
│   └── rejected/           failed validation, with a report saying why
└── tools/
    ├── extract_state.py    measure the workspace -> state/workspace.json
    ├── schema.py           what a contribution may be
    ├── validate.py         reject bad input
    ├── ingest.py           merge validated input into state/
    ├── bootstrap.py        state/ -> TRANSFER_BOOTSTRAP.txt
    └── build.py            state/ -> index.html
```

**The two generated files are artifacts.** If you edit them by hand, the next
build overwrites your edit. Edit `state/`, or file a contribution.

---

## How to contribute

### 1. Write the contribution

A JSON file into `intake/drop/`. Filename must be ASCII-safe: letters, digits,
underscores, dots, hyphens.

One object, or an array of objects:

```json
{
  "kind": "firewall",
  "project": "blue_silver",
  "who": "Berrit Ohn",
  "state": "KNOWN PARTLY",
  "topic": "The valley's contents",
  "belief": "She knows the seal exists and what it protects, but not that the grass is sentient.",
  "earliest_change": "A direct encounter with Home after the seal is filed.",
  "rule": "Her paperwork protects the valley without her knowing what lives in it.",
  "provenance": {"agent": "your-agent-name", "date": "2026-09-18"}
}
```

Always include `provenance.agent`. It is how the growth log attributes the
change, and it is how a future agent knows who to ask.

### 2. Validate

```
python3 tools/validate.py intake/drop/your_file.json
```

Reads the file, writes a report beside it. Exit 0 means it will ingest.

### 3. Ingest

```
python3 tools/ingest.py intake/drop/your_file.json
```

Re-validates, merges into `state/`, appends to `state/log.json`, moves the file
to `intake/accepted/`. A failure moves it to `intake/rejected/` with the report.

### 4. Rebuild

```
python3 tools/bootstrap.py && python3 tools/build.py
```

Or just `make` from this directory.

---

## The eight kinds

| kind | required | what it is for |
|---|---|---|
| `project` | id, name, path, status, live_edge | Register a new project |
| `firewall` | who, state, topic, earliest_change, rule | Add a knowledge firewall |
| `anchor` | anchor, year | Add a fixed timeline anchor |
| `canon` | claim, confidence | Assert a canon claim |
| `lock` | lock, value | Record one of the twelve locks |
| `decision` | decision, reason | Record an authorised decision |
| `correction` | was, now, reason | Correct a value, keeping the old one visible |
| `note` | text | A free-form note tagged to a project |

---

## What gets rejected

- An unknown `kind`, or a required field missing.
- A firewall `state` outside the seven defined states. **Adding a new state is a
  law change and needs the user, not an agent.**
- A `confidence: "canon"` claim with no `sources`. Either cite them or downgrade
  the tag to `reported`.
- CJK, kana or hangul anywhere in the file (gate 1).
- A literal backslash-n sequence (gate 2).
- A reserved field: `authority_order`, `seven_gates`, `gate_scope_warning`,
  `_comment`. These change the shape of the system.
- A duplicate of another contribution in the same file.
- A `project` id that already exists. File a `correction` instead.

Rejection is not deletion. The file moves to `intake/rejected/` with a report
naming every problem, so nothing is lost and the fix is obvious.

---

## The rules that matter most

**Append-only.** A contribution adds. It never silently replaces. A correction
is recorded as a correction — the old value stays visible next to the new one,
with the reason. A state layer where anything can be quietly overwritten is a
state layer nobody can trust.

**Author knowledge is not character knowledge.** Every firewall needs
`earliest_change`. Without it, the next agent will helpfully let the character
find out early because the plot needs it. That field is the whole defence.

**Disclose your confidence.** `[canon]` means multiple independent secondary
sources agree — and you must name them. If you cannot, the tag is `reported`.
A system that cannot tell you which of its own facts are soft is not a control
centre.

**Corrections before new content.** If a lock, firewall or canon receipt is
wrong, file the correction and re-run the gates before writing the next chapter.

---

## Growing a new project into this system

1. File a `project` contribution.
2. File its `lock` contributions — all twelve. Lock 4 must be a filled sentence:
   *"______ wants ______ from my protagonist, and will ______ to get it."*
3. File its `firewall` contributions — one per character who knows anything.
4. File its `anchor` contributions for every fixed date.
5. Rebuild.

That is the minimum for a project to be safely handable. A project with locks
but no firewalls will leak. A project with firewalls but no locks will drift.

---

## What this system cannot do

- It cannot verify a claim is true. It can only check that the claim is
  well-formed and that its confidence is disclosed honestly.
- It cannot stop an agent ignoring the state. It can only make the state easy to
  read and hard to lose.
- It does not replace the source files. `state/workspace.json` records counts;
  the prose still lives in the project directories.
