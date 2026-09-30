# CANON_ACCESS_TEMPLATE.md — how canon ore enters

**Foundation docset v6.0 · core · universal.**
The recipe: which canon is the spine, which is only ore, and how material
passes from source to receipt. Ported from the Miraculous V1–V6 recipe and the
Pokémon port of it.

---

```
# CANON_ACCESS.md — how canon ore enters {{SERIAL_NAME}}

## The spine vs the anchors

- **Spine (load-bearing):** {{one declared source — the one whose beats the
  serial follows in order}}
- **Anchors (citable, never load-bearing):** {{list — games, novels, manhua,
  wikis, official sources}}
- **Ore rule:** every canon is admissible as *ore*; only the spine is
  load-bearing for *beats*. Without this split, one chapter can be
  contradicted by four different sources at once — the exact failure the
  Ledger-Canon Law exists to prevent.

## The V1–V6 recipe (keep the numbers)

| Step | What happens | Done for this serial |
|---|---|---|
| V1 | Inventory the spine's units (episodes/chapters) | {{...}} |
| V2 | Extract per-unit receipts into `canon_extract/` | {{...}} |
| V3 | Index them (`canon_extract/INDEX.txt`) | {{...}} |
| V4 | Map units to the serial's planned beats | {{...}} |
| V5 | Declare the spine (one) + anchors (many) | done — see above |
| V6 | Gate: narration overlap checked before ship | {{gate/tool name}} |

## What never enters

- Rejected drafts and non-canon fan wikis as load-bearing sources.
- Author/agent knowledge as character knowledge (see `RELATIONSHIPS.md`).
- Anything absent from `CANON_GROUND.md` — access without a receipt is not access.
```

## Rules

- The spine is declared **once**; changing it is an author ruling with a
  correction entry, not an edit.
- Extraction is mechanical where possible (`canon_extract/` as plain text) so
  the chapter gate can quote-check narration against it.
