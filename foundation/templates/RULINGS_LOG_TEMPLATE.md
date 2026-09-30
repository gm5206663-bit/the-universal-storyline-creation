# RULINGS_LOG_TEMPLATE.md — every ruling, verbatim

**Foundation docset v6.0 · core · universal.**

The author's words are law; they are kept verbatim and never paraphrased
(AGENTS.md rule 4). If you do not have the exact words, you do not have a
ruling — go ask.

Both house formats are legal; the gate accepts either:

## Format A — numbered sections (modern, preferred)

```
# RULINGS_LOG.md — every ruling verbatim from the author

**Authority order:** author word > RAILS / FOUNDATION > STATUS > codex > kit >
README > everything else. Nothing in this file is paraphrased into something
better.

---

## Ruled {{YYYY-MM-DD}} — {{one line of context}}

### R1 — {{the question, as asked}}

> **Author's word, verbatim:** "{{the exact words}}"

**Recorded as:** {{installation — what the words lock in, plainly}}

**Reconciliation with {{overridden doc/law}}, which the author's word
overrides but does not erase:** {{how the old material still stands, with its
strike receipt if struck}}.
```

## Format B — the ledger table (mature-serial format)

```
| # | Date | The author's word (verbatim) | The ruling installed |
|---|---|---|---|
| R1 | {{YYYY-MM-DD}} | "{{exact words}}" | {{what it locks in}} |
```

## Rules

- Numbering: R1, R2, … in asking order. Never renumber — numbers are receipts.
- A collision between two rulings becomes **new rulings**, not a silent fix.
- A strike is recorded as a correction (old value visible next to new), never
  a deletion. Struck *documents* go to `_archive/{{YYYY-MM-DD}}_{{slug}}/`
  with a receipt.
- Open questions do not live here — they live in `OPEN_RULINGS.md`.
