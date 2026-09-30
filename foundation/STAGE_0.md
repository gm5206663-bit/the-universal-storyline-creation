# STAGE_0.md — the rulings-first lifecycle

**The Foundation-Stage law, verbatim from the record:**
*rulings first, prose second, always zero chapters until ruled.*

Stage 0 is the foundation stage of a serial. It opens when a serial is born and
closes when — and only when — every ruling the author has opened is answered,
the docset is filled, and the gate is green. Nothing in Stage 0 is prose.
Sentences you enjoy writing belong in Stage 1.

---

## Why it exists

Foundations die in one predictable order: an agent gets eager, writes chapter 1
before the premise is ruled, and by chapter 30 the unanswered question has
become a rewrite of everything. The Seed of Creation precedent is the receipt:
four pending rulings, zero chapters written — **that was correct behaviour, not
a failure to start.** Zero chapters is cheap. Thirty wrong chapters are not.

Stage 0 converts every author-only decision into a numbered, verbatim, dated
receipt *before* prose exists to depend on it.

---

## The six steps, in order

```
OPEN -> RULE -> RECONCILE -> DOCSET -> GATE -> CLOSE -> RECORD
```

1. **OPEN.** File `foundation/OPEN_RULINGS.md` with the Stage 0 lane table:
   one row per decision, a recommended default, and the reason it matters.
   Decisions only the author can make. Agents recommend; the author rules.
   Answering "defaults" takes every recommendation — that is a legal ruling.

2. **RULE.** Every answer lands in `foundation/RULINGS_LOG.md` **verbatim** —
   the author's exact words, numbered (R1, R2, …), dated. Never paraphrased
   into something better. This is AGENTS.md rule 4 and it is not stylistic
   advice: a paraphrased ruling is an agent's invention wearing the author's
   coat.

3. **RECONCILE.** Rulings collide — they are made at different times about
   different worries. A collision becomes **new rulings, never a silent fix**.
   The receipt: R2 and R3 collided in the Pokémon serial (anime start vs a
   Hoenn species in 1997 Kanto) and produced R13 and R14 rather than an
   undocumented fudge. When a new ruling overrides old material, the old
   material keeps standing with a dated strike receipt beside it (see
   `_archive/2026-09-30_system_framework_struck/` — struck on the author's
   word, archived, never deleted). An author word overrides a document; it does
   not erase it.

4. **DOCSET.** Fill every core file from `templates/` (see README). Pack files
   if the serial declares them. Canon claims enter `CANON_GROUND.md` with
   source + confidence — never from memory. Missing canon is identified as
   missing, not invented.

5. **GATE.** `python3 tools/foundation_gate.py <serial>/` must PASS. The gate
   is built **before** it is needed: a serial with no gate has no Stage 1, per
   the Pokémon k17 lesson — *the gate does not exist yet; build it before
   chapter 1.* A gate that has never caught anything is decoration.

6. **CLOSE + RECORD.** Mark Stage 0 closed in `STATUS.md` and `HANDOFF.md`
   (drafting unlocked), then file the state where the system can see it: a
   `decision` or `note` contribution into `intake/drop/`, per PROTOCOL.md.
   Append the closure to `SERIAL_LOG.md`. Only now does chapter 1 become a
   legal act — still subject to the serial's chapter gate before shipping.

---

## What Stage 0 is not

- **Not drafting.** Zero chapters. The gate fails on locked-stage chapters on
  disk — that check exists because eagerness is predictable.
- **Not canon invention.** Stage 0 *discovers* canon (receipts in
  `CANON_GROUND.md`). If a source scene is missing, the docset says it is
  missing.
- **Not an agent decision.** Every lane-table row is the author's. A default
  offered is not a default taken.
- **Not fandom-mixing.** A new fandom gets a new repository — the separation
  walls hold (`qian-xunji-adaptation`, `pokemon-adaptation` precedents). Stage
  0 inherits *method* from other serials; it never inherits their canon.

---

## Stage 0 and the twelve locks

The Control Centre's twelve locks are set before drafting chapter one. Stage 0
is where their inputs are produced:

| Lock | Produced by |
|---|---|
| ERA | OPEN_RULINGS (which series, which years) |
| PROTAGONIST | OPEN_RULINGS + FOUNDATION (who — and what they are NOT) |
| CANON ENTRY | CANON_ACCESS + CANON_GROUND |
| SPINE | OPEN_RULINGS — the lock with three blanks; unfilled = no story yet |
| POWER CEILING | POWER_LAW (+ SYSTEM_SPEC if the pack is declared) |
| IDENTITY | OPEN_RULINGS |
| ABSOLUTES | RAILS + FOUNDATION bans |
| CANON IMMUNITY | CANON_GROUND + TIMELINE |
| MEASUREMENT | STATUS + PANELS (how it shows on the page) |
| VOICE | RAILS |
| CADENCE | RAILS (when audits run) |
| HANDOFF | HANDOFF.md itself |

---

## The Stage 0 checklist

- [ ] New repository for the fandom (separation walls hold)
- [ ] `OPEN_RULINGS.md` lane table filed, drafting locked, zero chapters
- [ ] Every R-entry answered verbatim in `RULINGS_LOG.md`, dated
- [ ] Collisions routed to new rulings; strikes archived with dated receipts
- [ ] All nineteen core files filled; packs declared both-or-neither
- [ ] Canon claims receipted in `CANON_GROUND.md`
- [ ] Chapter gate (`tools/`) built and self-tested before chapter 1
- [ ] `foundation_gate.py` PASS
- [ ] Stage 0 marked closed in `STATUS.md` + `HANDOFF.md`
- [ ] Closure recorded: `SERIAL_LOG.md` + Control Centre contribution
