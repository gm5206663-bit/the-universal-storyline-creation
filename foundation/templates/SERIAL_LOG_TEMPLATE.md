# SERIAL_LOG_TEMPLATE.md — the work journal

**Foundation docset v6.0 · core · universal.**
Append-only. Every session that changes the serial leaves a dated line. A
decision not written down will regress — this is where "later" gets refused.

---

```
# SERIAL_LOG.md — {{SERIAL_NAME}}

Newest at the bottom. Never edit an old line — append a correction instead.

## {{YYYY-MM-DD}}

- {{what happened — ruling filed, gate built, chapter shipped, strike archived}}
- {{receipt: file paths, gate results, contribution ids}}
```

## Rules

- One section per day, entries in order.
- Ship events name the gate result (`style_gate PASS`, `run_all 4 steps PASS`).
- Strike/archive events name the receipt path (`_archive/{{YYYY-MM-DD}}_{{slug}}/`).
- State changes here mirror the same turn: STATUS, HANDOFF, Control Centre.
