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
