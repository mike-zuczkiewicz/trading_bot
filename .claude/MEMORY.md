# Trading Bot — Things to Remember

## Time & Location
- Always use **Berlin time (CET/CEST)** for all time references and scheduling
- UTC+1 (CET) in winter, UTC+2 (CEST) in summer
- US market open = 15:30 Berlin, close = 22:00 Berlin
- Mike is in Wiesbaden, Germany (SOFA status, US citizen)

---

## Behavioral Rules
- **Do not act on vague or ambiguous requirements** — ask for clarification before implementing
- **Analysis-only prompts must not produce unsolicited code changes**
- **All bot parameter changes must be logged** with reasoning and timestamp
- **Never execute trades directly** — Claude's role is advisory and monitoring only
- Autonomous parameter adjustments must stay within the predefined outer envelope

---

## Documentation Maintenance
- **Keep `.claude/PHASES.md`, `.claude/TASKS.md`, and `.claude/PLAN.md` in sync.** These three files are connected views of the same plan: PHASES = where on the roadmap, TASKS = what to code next, PLAN = strategy/policy/parameters. Whenever any of the following happens, update all affected files in the same turn:
  - A task on `TASKS.md` is shipped (move it under §Done with date + commit SHA, remove its underlying `[ ]` items)
  - A phase boundary is crossed (start of a new phase, or completion of the active one)
  - A parameter in `PLAN.md` changes (cup-with-handle params, position sizing, Phase 7 gate, autonomy envelope, etc.)
  - A new phase is added or scope of an existing phase materially changes
- **Cross-reference, don't duplicate.** PLAN.md should not repeat the phase list — point at PHASES.md. TASKS.md should not repeat strategy parameters — point at PLAN.md.
- **At the start of each coding session,** re-read all three. If the files contradict the actual code or `PLAN.md` parameters don't match `config.py`, surface the drift to the user before starting new work.
