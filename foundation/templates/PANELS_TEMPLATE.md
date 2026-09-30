# PANELS_TEMPLATE.md — panel grammar + ledger

**Foundation docset v6.0 · core · universal.**
Panels are the bracketed stat/rank lines (`[Level 30 · Great Soul Master]`).
This file declares **whether this serial has them at all**, the grammar if it
does, and the ledger of every line ever printed — full only on an update/gain
beat, zero lines allowed otherwise (F22).

**Zero panels is a legal grammar.** Write that down explicitly — "no panels,
ever" is a rule the gate can check; silence is not.

---

```
# PANELS.md — panel grammar of {{SERIAL_NAME}}

## Declaration

**{{HAS_PANELS: yes}}** or **{{NO PANELS — banned outright (kNN)}}**
If banned: a panel would be a lie in the narrative voice — {{why}}. STATUS.md
counts; prose shows; neither waits on the other.

## Grammar (if yes)

- Shape: {{exact panel line format}}
- When full details print: **only on update or gain beats** (F22)
- When nothing prints: **every other beat — 0 lines** (F22)
- Where the truth lives between prints: `STATUS.md`, `SKILLS_CANON.md`

## The ledger

Every panel line ever printed, in ship order — kept IN SYNC with STATUS by
`{{check_panels.py or equivalent}}`.

| Ch | Line printed | STATUS match | Checked |
|---|---|---|---|

## Rules

- Frozen meters fail the build (drift guard): panel vs STATUS mismatch = gate
  red. Fix the panel or fix STATUS — never the checker.
```
