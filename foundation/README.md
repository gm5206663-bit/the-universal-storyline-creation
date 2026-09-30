# THE UNIVERSAL FOUNDATION LAYER — foundation docset v6.0

**Built 2026-09-30. Home: the Control Centre. Provenance: measured from
`pokemon-adaptation` (freshest Stage 0 docset), `soul-land-2-the-grey-wolf`
(mature system serial), and the method repo's `templates/SERIAL_FOUNDATION_TEMPLATE.md`
(which this layer supersedes as the portable standard — the old template stays
untouched in its repo, add-only).**

Citations: guide edition **v2.1**, law revision **v5.4**, 31 entries of record
(F0–F26 + P12 + 7 structural). See `how-to-write-fanfiction/VERSION_OF_RECORD.md`.

---

## What this is

Every serial you write gets its own `foundation/` directory. This layer says
exactly which files that directory holds, gives you a template for each one, and
ships a gate that fails the build when the docset is incomplete, unfilled, or
disciplined-broken. Three parts:

| Part | What it is | Run it |
|---|---|---|
| `STAGE_0.md` | The rulings-first lifecycle: open → rule → docset → gate → close → record | read it |
| `templates/` | One template per foundation file — copy into a serial, fill, never paraphrase a ruling | copy + fill |
| `../tools/foundation_gate.py` | The machine check over the whole docset | `python3 tools/foundation_gate.py <serial>` |

**The rule this layer exists to enforce:** *rulings first, prose second, always
zero chapters until ruled* (Foundation-Stage law). A foundation is not a mood —
it is either complete and gate-clean, or the serial is not ready to write.

---

## Core — every serial, every fandom

Required by the gate. Nineteen files:

| File | What it holds | Template |
|---|---|---|
| `FOUNDATION.md` | Base of base: serial identity, lessons, locks, world rules | `templates/FOUNDATION_TEMPLATE.md` |
| `RULINGS_LOG.md` | Every author ruling, verbatim, dated, numbered | `templates/RULINGS_LOG_TEMPLATE.md` |
| `OPEN_RULINGS.md` | The Stage 0 lane table — decisions only the author can make | `templates/OPEN_RULINGS_TEMPLATE.md` |
| `HANDOFF.md` | Cold start for any future agent: truth now, authority order, read order | `templates/HANDOFF_TEMPLATE.md` |
| `RAILS.md` | This serial's own laws, k-numbered, each with a check | `templates/RAILS_TEMPLATE.md` |
| `STATUS.md` | The single current-truth source. Live edge, locks, bans | `templates/STATUS_TEMPLATE.md` |
| `CANON_GROUND.md` | Every canon claim with its source and confidence tag | `templates/CANON_GROUND_TEMPLATE.md` |
| `CANON_ACCESS.md` | How canon ore enters: the spine, the anchors, the receipt rule | `templates/CANON_ACCESS_TEMPLATE.md` |
| `POWER_LAW.md` | How power works in this serial — no System vocabulary unless the pack says so | `templates/POWER_LAW_TEMPLATE.md` |
| `TIMELINE.md` | Canon spine receipted + our road | `templates/TIMELINE_TEMPLATE.md` |
| `CHARACTERS.md` | The cast: canon and ours | `templates/CHARACTERS_TEMPLATE.md` |
| `RELATIONSHIPS.md` | Knowledge firewalls — who knows what, and since when | `templates/RELATIONSHIPS_TEMPLATE.md` |
| `STORY_ARCS.md` | Arc plan | `templates/STORY_ARCS_TEMPLATE.md` |
| `CODEX.md` | File map + decision log | `templates/CODEX_TEMPLATE.md` |
| `SERIAL_LOG.md` | Work journal — dated, append-only | `templates/SERIAL_LOG_TEMPLATE.md` |
| `GLOSSARY.md` | World terms | `templates/GLOSSARY_TEMPLATE.md` |
| `PLACES.md` | The map | `templates/PLACES_TEMPLATE.md` |
| `PANELS.md` | Panel grammar + ledger. Zero panels is a legal grammar — write that down | `templates/PANELS_TEMPLATE.md` |
| `SKILLS_CANON.md` | What the OC can do, in the franchise's own terms | `templates/SKILLS_CANON_TEMPLATE.md` |

## Packs — declared, never guessed

A pack is **both files or neither**. The gate auto-detects a pack from the
presence of either file and fails if only one survived.

| Pack | Files | For serials that… | Templates |
|---|---|---|---|
| `system` | `SYSTEM_SPEC.md`, `METERS.md` | have a cheat/system on page (Grey Wolf did; Pokémon explicitly does not) | `templates/SYSTEM_SPEC_TEMPLATE.md`, `templates/METERS_TEMPLATE.md` |
| `world` | `ECONOMY.md` | have money worth a ledger | `templates/ECONOMY_TEMPLATE.md` |

**Serial-specific extensions are legal and never gated** — one local module file
per serial is the pattern (`ADAPTATION_TALENT_BAGON.md`), plus dated receipts
like `CANON_STUDY_*.md` and rebuild/audit records. The gate requires files; it
never rejects extras.

---

## How to use it

```
1. cp foundation/templates/<X>_TEMPLATE.md  <serial>/foundation/<X>.md
2. Fill. Author rulings go in verbatim or they are not rulings.
3. python3 tools/foundation_gate.py <serial>/          # must PASS
4. Stage 0 close rule: zero chapters until the gate is green and every
   OPEN_RULINGS line is ruled. See STAGE_0.md.
```

### The gate

```
python3 tools/foundation_gate.py path/to/serial            # auto packs
python3 tools/foundation_gate.py path/to/serial --strict   # warnings fail too
python3 tools/foundation_gate.py --selftest                # prove the checks can fail
```

Exit 0 means clean. A check that cannot fail on a bad input is not a check —
`--selftest` injects a defect for every rule, and it runs first, same as the
Control Centre selftest law.

### What it checks

- the nineteen core files exist and are filled (no `{{placeholders}}` or
  template examples left — those FAIL; bare `TBD`/`FIXME` WARNs for eyes-on
  and only fails under `--strict`, because prose may be quoting the ban);
- pack pairs are complete — half a system is not a system;
- `RULINGS_LOG.md` declares verbatim discipline and carries ruling entries
  (both house formats accepted: `### R1 …` with blockquotes, and the
  `| F0 | date | verbatim |` table);
- `STATUS.md` carries a live edge;
- `HANDOFF.md` carries a read order;
- Stage 0 state versus chapters on disk: locked foundation + chapters = FAIL;
- stale foundation-docset tags (`v5.x`) surface as warnings — retag when touched,
  per `VERSION_OF_RECORD.md`.

---

## Dry run

`DRY_RUN_2026-09-30.md` holds the honest findings from running this gate
against `pokemon-adaptation` and `soul-land-2-the-grey-wolf` on the day it was
built. Read it before you trust it.

## Boundaries

- This layer governs **foundation files only**. Chapter prose is gated by the
  serial's own tools (`style_gate.py` and friends). Two gates, two jobs.
- Author word outranks this layer, and so does a serial's own RAILS.
- Never weaken a gate to pass it. Fix the docset, not the check.
- Filing this layer into `state/` (so the site shows it) is an author decision —
  a `decision` or `note` contribution through `intake/drop/`, per PROTOCOL.md.
