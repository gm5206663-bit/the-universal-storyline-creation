# CONTROL CENTRE

Navigation and state reference for every Soul Land serial, plus the portable
authoring law that governs them. Built so a fresh agent — or a human
collaborator — can reach correct state in one read, without being told anything
twice and without inventing anything missing.

**This is a system, not a document.** The site and the transfer bootstrap are
generated from `state/`. You do not edit them; you change the state.

---

## Thirty seconds

```
make            # selftest -> measure -> bootstrap -> build
make serve      # the above, then serve the site on :8080
```

Open `index.html`. That is the whole Control Centre.

It is also **live on GitHub Pages** (published 2026-09-23):
https://gm5206663-bit.github.io/the-universal-storyline-creation/

To hand it to another agent, give them `TRANSFER_BOOTSTRAP.txt`. It is the same
state as plain text and needs no access to this directory.

---

## The layout

```
index.html              GENERATED — the site. Never hand-edit.
TRANSFER_BOOTSTRAP.txt  GENERATED — plain-text handoff. Never hand-edit.
README.md               this file
PROTOCOL.md             the contribution contract. Read before filing anything.
Makefile                the commands

state/                  the data. This is what actually persists.
  workspace.json        measured from disk by tools/extract_state.py
  canon.json            canon spine, rank ladder, ring ages, user rulings
  laws.json             twelve locks, seven gates, pipeline, firewall states
  firewalls.json        the knowledge firewall registry
  log.json              every growth event, append-only
  contributions.json    contributed records (appears on first ingest)
  projects/             one file per project

intake/
  drop/                 FILE CONTRIBUTIONS HERE
  accepted/             merged, with provenance
  rejected/             failed validation, with a report saying why

tools/
  selftest.py           102 negative tests over the validator
  extract_state.py      measure the workspace -> state/workspace.json
  schema.py             what a contribution may be
  validate.py           reject bad input
  ingest.py             merge validated input into state/
  bootstrap.py          state/ -> TRANSFER_BOOTSTRAP.txt
  build.py              state/ -> index.html
```

---

## How it grows

Any agent, on any platform, files a JSON contribution into `intake/drop/`:

```
make ingest
```

That validates it, merges it into `state/`, records it in `state/log.json` with
the filing agent's name and timestamp, and regenerates the site and the
bootstrap.

Eight kinds of contribution: `project`, `firewall`, `anchor`, `canon`, `lock`,
`decision`, `correction`, `note`. Required fields and examples are in
[PROTOCOL.md](PROTOCOL.md).

Contributions are **append-only**. Nothing silently overwrites existing state. A
correction is recorded as a correction, keeping the old value visible next to
the new one with the reason. A state layer where anything can be quietly
replaced is a state layer nobody can trust.

---

## Commands

| Command | What it does |
|---|---|
| `make` | selftest, measure, bootstrap, build |
| `make test` | run the 102 negative tests alone |
| `make measure` | re-measure the workspace into `state/workspace.json` |
| `make bootstrap` | regenerate `TRANSFER_BOOTSTRAP.txt` |
| `make build` | regenerate `index.html` |
| `make check` | validate everything waiting in `intake/drop/` |
| `make ingest` | validate + merge everything in `intake/drop/`, then rebuild |
| `make serve` | `make`, then serve on port 8080 |
| `make clean` | remove `__pycache__` |

`make` runs the selftest first and stops if it is red. A red selftest means a
validation rule is either too loose or too strict, and nothing downstream can be
trusted.

---

## Cold start

If you have been given this directory alone, without the fiction workspace
beside it, `make` still works. `extract_state.py` detects the missing workspace,
keeps the committed measurements in `state/workspace.json`, tells you what it is
retaining and when it was measured, and continues. The site and the bootstrap
build from `state/` either way.

Run `make measure` again beside the real workspace to refresh the counts.

---

## What this cannot do

- It cannot verify a claim is true. It checks that a claim is well-formed and
  that its confidence is disclosed honestly — nothing more.
- It cannot stop an agent ignoring the state. It can only make the state easy to
  read and hard to lose.
- It does not replace the source files. `state/workspace.json` records counts;
  the prose still lives in the project directories.

---

## The rule underneath all of it

**Author knowledge is never character knowledge.**

Every knowledge firewall carries an `earliest_change` field. Without it, the
next agent will helpfully let a character find something out early because the
plot needs it. That field is the whole defence, and the validator warns when it
is too thin to do its job.

Corrections come before new content. If a lock, a firewall or a canon receipt
turns out to be wrong, file the correction and re-run the gates *before* writing
the next chapter.
