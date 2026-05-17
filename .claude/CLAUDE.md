# Trading Bot — Project Context for Claude

> **Session start:** Read `.claude/MEMORY.md` first, then `.claude/PLAN.md`, then continue with this file.

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
- Windows key: `C:\Users\mikez\.ssh\id_ed25519`
- Mac key: `~/.ssh/id_ed25519`
- Mac SSH as mike: pending setup
- Windows SSH config: `C:\Users\mikez\.ssh\config`

### Security
- UFW firewall: ports 22, 80, 443
- Fail2ban: enabled
- .env permissions: 600
- Bot currently runs as root — move to mike after web app build

### Bot Files (VPS only — not in Git)
- Location: `/root/trading-bot/`
- Files: `bot.py`, `config.py`, `strategy.py`, `venv/`
- Environment: `/root/trading-bot/.env`
- Systemd service: `trading-bot.service` (enabled, auto-restart)
- Log: `/root/trading-bot/bot.log`
- **Not tracked in Git — deployed directly to VPS via scp**

### Git Repo (SvelteKit frontend only)
- Local path: `C:\Users\mikez\iCloudDrive\DEV\trading_bot\`
- Contains SvelteKit frontend only
- Python bot files are NOT in this repo

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

## Hard Limits (Never Change)
- Claude never executes trades directly
- Bot never exceeds preset parameters without code change
- Claude autonomous adjustments stay within defined outer envelope
- Kill switch: STOP file in bot directory halts bot immediately
