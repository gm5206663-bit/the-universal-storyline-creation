# METERS_TEMPLATE.md — SYSTEM PACK (optional, both files or neither)

**Foundation docset v6.0 · pack `system`.**
Every meter with its own pace law. A meter without a pace law is a number that
lies about how fast the story moves. Companion to `SYSTEM_SPEC.md`; no system
serial never creates this file (Pokémon's meter table was struck with the
system — receipt in `_archive/`).

---

```
# METERS.md — the meters of {{SERIAL_NAME}}

| Meter | What feeds it | Pace law | Ceiling / trigger |
|---|---|---|---|
| {{meter}} | {{what counts as progress}} | {{honest yield — when it moves and how fast}} | {{what happens at the top}} |

## Rules

- Everything that grows feeds every open meter — nothing grows for free.
- 100% (or the serial's cap) is an **evolution/fusion trigger, never a resting
  terminal** — F14 as this serial's law states it.
- Exact figures live here and in panels/STATUS — never in chapter prose
  (F22 / panel law).
- Cross-check: `SYSTEM_SPEC.md` grants == this file's movement. Mismatch fails
  the drift guard.
```
