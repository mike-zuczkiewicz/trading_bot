# Trading Bot — Project Context for Claude

> **Session start (read in this order):**
> 1. `.claude/MEMORY.md` — behavioural rules and persistent context
> 2. `.claude/PHASES.md` — where the project is on the roadmap
> 3. `.claude/TASKS.md` — concrete next coding tasks
> 4. `.claude/PLAN.md` — strategy parameters, signal layers, Phase 7 gate, Claude's autonomy envelope
> 5. This file (`CLAUDE.md`) — infrastructure, conventions, hard limits
>
> The three middle files (`PHASES`, `TASKS`, `PLAN`) are connected views of the same plan — keep them in sync per the rule in `MEMORY.md` §Documentation Maintenance.

## Project Overview
Automated trading bot using Alpaca paper/live account, CAN SLIM strategy with cup-with-handle entry pattern, hosted on DigitalOcean VPS. Claude interacts via Alpaca MCP server for monitoring and advisory analysis.

---

## Infrastructure

### DigitalOcean VPS
- IP: 167.172.107.21
- OS: Ubuntu 24.04 LTS
- Size: 1 vCPU, 1GB RAM, $6/mo
- Datacenter: Frankfurt (FRA1)
- User: `mike` (sudo)
- Root SSH login: disabled

### SSH Access
- Windows key: `C:\Users\mikez\.ssh\id_ed25519` (authorized for `mike` on the VPS)
- Mac key: `~/.ssh/id_ed25519`
- Mac SSH as mike: working — `~/.ssh/id_ed25519` already authorized for `mike@167.172.107.21` (verified 2026-05-19)
- Windows SSH config: `C:\Users\mikez\.ssh\config` defines `Host vps` → `ssh vps` and `scp vps:...` work without arguments
- Sudo on the VPS: `mike` is in the sudo group but **needs a password** for sudo commands (no NOPASSWD rules in place). Any runbook with `sudo` on the VPS has to be pasted by Mike — Claude can't drive sudo over SSH.

### Security
- UFW firewall: ports 22, 80, 443
- Fail2ban: enabled
- .env permissions: 600
- Bot currently runs as root — move to mike after web app build

### Bot (in this repo at `bot/`)
- Source: `bot/bot.py`, `bot/config.py`, `bot/strategy.py` — version-controlled
- Dependencies: `bot/requirements.txt`
- Environment: `bot/.env` (gitignored; copy from `bot/.env.example`). Required vars: `ALPACA_API_KEY`, `ALPACA_SECRET_KEY` (note: `SECRET_KEY`, not `API_SECRET`).
- VPS location: `/root/trading_bot/bot/` (cloned via git, not scp). Migrated 2026-05-17.
- Systemd service: `trading-bot.service` (enabled, auto-restart); `WorkingDirectory=/root/trading_bot/bot`, `User=root` (move to `mike` after web app build).
- Log: `/root/trading_bot/bot/bot.log` on the VPS (gitignored)
- Current strategy state: scaffold only — `strategy.py` is a momentum stub, `config.py` has placeholder params that **do not match** the CAN SLIM values in `PLAN.md` §Strategy Parameters. Phase 3 work will replace both.
- Deploy: `sudo git -C /root/trading_bot pull && sudo systemctl restart trading-bot.service` on the VPS. `git -C <path>` is required because `mike` can't `cd` into `/root/` even with sudo. The historical migration runbook is retained in `bot/README.md` for reference only.

### Git Repo (monorepo: frontend + bot)
- Local path: `d:\DEV\trading_bot\` (Windows). On Mac, path will differ — see whatever the session's working directory reports.
- Remote: `https://github.com/mike-zuczkiewicz/trading_bot.git` (**public** — anonymous clone works; required for the VPS to pull without auth setup)
- Layout:
  - `trading-bot/` — SvelteKit web app (scaffold only)
  - `bot/` — Python trading bot (migrated into git 2026-05-17; was VPS-only before)
  - `.claude/` — project context, plan, behavioural rules

---

## Alpaca Account
- Type: Paper trading
- Balance: $100,000
- Buying power: $200,000 (2x margin)
- Options level: 3
- TRADING_ENABLED: False (dry-run mode)
- PAPER_TRADING: True

---

## Coding Conventions
- Python for bot backend
- Svelte for frontend (match watchbill style)
- Read watchbill repo before any frontend work

### Stack
- SvelteKit + TypeScript
- Package manager: npm
- Add-ons: prettier, eslint, mcp
- Strict TypeScript mode
- Font Awesome Pro v7.2.0 for icons and styling
- Match watchbill project conventions before writing any component

### Watchbill Conventions (replicate exactly)
- **State**: `data.svelte.ts` — single file owns all global `$state()` exports (bot state, positions, orders, UI state). No store subscriptions, no context API, no prop-drilling for global state. Components import directly and mutate in place.
- **Types**: `types.d.ts` with interfaces: `BotState`, `Position`, `Order`, `UserPrefs`
- **Routes**: Minimal — `+layout.ts` for auth/init, `+page.ts` for data loading
- **Services**: Curried fetch layer per API (Alpaca, news, etc.), environment-switched
- **Styling**: CSS variables for colors/spacing in `app.css`, scoped `<style>` per component
- **Components**: Domain folders — `trading/`, `portfolio/`, `controls/`, `components/`
- **Exports**: Barrel file at `src/lib/index.ts`
- **Permissions**: `userLevel` in `appState`, checked at render time with `$derived()`

### Svelte MCP Tools

When working on Svelte/SvelteKit code, use these tools in order:

1. **`list-sections`** — Call FIRST to discover all available documentation sections. Always use this at the start of any Svelte/SvelteKit task.
2. **`get-documentation`** — Fetch ALL sections relevant to the task (analyze `use_cases` field to decide).
3. **`svelte-autofixer`** — Run on ALL Svelte code before delivering it. Keep calling until no issues or suggestions are returned.
4. **`playground-link`** — Only call after user confirms they want a link. Never call if code was written to project files.

### Prettier (all JS/TS/Svelte files)
- useTabs: true
- singleQuote: true
- semi: false
- tabWidth: 2
- trailingComma: es5
- printWidth: 100
- plugins: prettier-plugin-svelte (with svelte parser override for *.svelte)
- Config file: `trading-bot/.prettierrc`
- Always format before committing

---

## Audit Trail (where parameter changes are logged)
- Location: `/root/trading_bot/bot/audit.log` on the VPS (append-only). Not yet implemented — Phase 3 work; this path is the target for when it lands.
- Format: JSON Lines (one JSON object per line), schema:
  ```
  {
    "timestamp": "<ISO-8601 with TZ>",
    "actor": "claude" | "mike" | "system",
    "change_type": "param_update" | "position_add" | "manual_override" | "envelope_action",
    "target": "<param name or position symbol>",
    "old_value": <any>,
    "new_value": <any>,
    "reason": "<free-text>",
    "envelope_rule_satisfied": <object | null>
  }
  ```
- Rotation: weekly to `audit-YYYY-WW.log.gz`
- Retention: 1 year minimum
- Read access: Claude, Mike. Write access: bot process only.

---

## Hard Limits (Never Change)
- Claude never executes trades directly
- Bot never exceeds preset parameters without code change
- Claude autonomous adjustments stay within defined outer envelope
- Kill switch: creating a `STOP` file in the bot's `WorkingDirectory` (`/root/trading_bot/bot/` on the VPS) halts the bot at the next scan-loop iteration — worst-case latency is one `POLL_INTERVAL_SEC` (default 60s), not instant
