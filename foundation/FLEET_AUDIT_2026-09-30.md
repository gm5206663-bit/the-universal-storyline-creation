# FLEET_AUDIT_2026-09-30.md — every serial docset, measured

Command: `python3 tools/foundation_gate.py <serial>` — docset v6.0, gate as of
2026-09-30 (18/18 selftest). Clones: full shallow, except Fire Phoenix and
kit serials (blobless sparse: foundation only — their *chapter counts on disk
in this audit are artifacts*, not truth).

## The table

| Serial | Result | Err | Warn | Notable findings |
|---|---|---|---|---|
| `pokemon-adaptation` | **PASS** | 0 | 0 | The standard. Stage 0 closed, packs none. |
| `soul-land-2-the-grey-wolf` | **PASS** | 0 | 0 | **Adopted this day** — 5 files created from its own record (row 29 of its SERIAL_LOG). Packs system+world complete. |
| `soul_land_system_cheat` (kit) | FAIL | 7 | 0 | Closest. Missing HANDOFF, RAILS, STATUS, CANON_ACCESS, POWER_LAW, SKILLS_CANON; RULINGS_LOG entries in a format the gate does not recognize. Design-stage serial — the cheapest next adopt. |
| `qian-xunji-adaptation` | FAIL | 15 | 0 | **Real inconsistency:** `SYSTEM_SPEC.md` present, `METERS.md` absent — half a system pack. RULINGS_LOG has no verbatim declaration. |
| `kit/soul_land_devouring_dragon` | FAIL | 16 | 1 | WARN: `TBD` in SERIAL_LOG — but the line reads "was TBD — s15 verified it": a resolved receipt, eyes-on not verdict. |
| `kit/soul_land_holy_spirit` | FAIL | 17 | 1 | WARN: "working title TBD" in FOUNDATION — genuinely unfilled (foundation-phase serial). |
| `kit/soul_land_2_new` (Golden Lion) | FAIL | 17 | 0 | LIVE serial (8 chapters, live agent — do not touch without author's word). Missing 17 of 19 modern core files. |
| `lan_shen` | FAIL | 18 | 0 | 2 chapters on disk; missing 18 of 19 (has only FOUNDATION-class material). |
| `mcu_eternal_fanfic` | FAIL | 18 | 0 | PAUSED by user order — adoption waits on unpause. |
| `soul_land_4_fire_phoenix` (private) | FAIL | 18 | 0 | Live edge ch52 (not audited on disk — sparse). Biggest serial, oldest docset shape. |
| `stark_heir` | FAIL | 19 | 0 | Missing all 19 — but its gates/HANDOFF live at repo root pattern, not `foundation/`. |
| `kit/SOUL_LAND_NEW` | FAIL | 19 | 0 | |
| `kit/dragon_prince_yuan_native_oc_fanfiction` | FAIL | 19 | 0 | |
| `kit/Soul_Land_2_Project` (Unraveled Tide) | FAIL | 18 | 0 | PAUSED at 24 chapters — revival queued. |
| `kit/soul_land_3_fanfiction` (Qing Ling) | FAIL | 18 | 0 | Foundation phase — the right time to adopt. |
| `kit/soul_land_3_new` | FAIL | 16 | 0 | |
| `kit/soul_land_new` · `kit/soul_land_starter` | FAIL | 16 each | 1 each | WARNs are their own ban sentences mentioning FIXME — correctly WARN, not FAIL, after today's rule fix. |

Not audited: `_archive/`, `SL_ARCHIVE/`, `soul-land-projects` (archived),
`soul-library` / `storyos-site` (publishing, not serial docsets),
`gm5206663-bit` (profile), `how-to-write-fanfiction` (method templates are
not a serial docset).

## Receipts from this audit

1. **The gate caught a false positive in itself.** Bare `TBD`/`FIXME` matched
   prose that *bans* those words ("No TODO/FIXME residue"). Rule corrected the
   same day: `{{...}}` and `EXAMPLE — DELETE` = FAIL (unambiguous scaffolding);
   bare `TBD`/`FIXME` = WARN with eyes-on wording; `--strict` escalates.
   Selftest grew with it: **18/18**.
2. **Grey Wolf adoption proven non-inventive:** all five files cite only its
   own record (STATUS §0, CANON_GROUND spine, README working laws,
   style_gate.py constants, SERIAL_LOG strike row 28). No new F-numbers
   (k08 cites the strike, not a fictional F27 — checked).
3. **Qian Xunji's half-system is real** — SYSTEM_SPEC without METERS fails by
   design. Either the meters are missing or the system is not what it claims;
   that ruling is the author's, not the gate's.
4. Chapter counts for sparse clones are marked artifacts; chapter gates were
   not run — this audit is foundation-layer scope only.

## Adoption path (per serial, the Grey Wolf method)

Read the serial's own README/STATUS/rulings → create the missing files as
restatements with receipts, never as new law → update CODEX + SERIAL_LOG same
turn → gate green → commit. Author order needed per serial (live serials:
explicit word, per AGENTS.md boundaries).
