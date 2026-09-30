# CODEX_TEMPLATE.md — file map + decision log

**Foundation docset v6.0 · core · universal.**
Two jobs: say what every file in the serial is, and hold the decision log's
pointers (the rulings themselves live in `RULINGS_LOG.md` — the codex does not
duplicate them; a fact maintained in two places will be wrong in one of them).

---

```
# CODEX.md — the map of {{SERIAL_NAME}}

## Files

| Path | What it is | Authority rank |
|---|---|---|
| `foundation/RULINGS_LOG.md` | author rulings, verbatim | top |
| `foundation/RAILS.md` | k-laws of this serial | high |
| `foundation/STATUS.md` | single current-truth | high |
| `chapters/` | shipped prose | — |
| `tools/` | the gates | — |
| {{...}} | {{...}} | |

## Decision log (pointers only)

| Date | Decision | Where the record lives |
|---|---|---|
| {{YYYY-MM-DD}} | {{one line}} | `RULINGS_LOG.md` R{{n}} / {{receipt path}} |

## Rules

- New file → this table, same turn. Orphan files rot.
- The codex never restates a ruling — it points at it.
```
