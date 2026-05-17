# trading_bot

Automated trading bot using Alpaca paper/live account, CAN SLIM strategy with cup-with-handle entry pattern.
Hosted on DigitalOcean (Frankfurt). Includes a SvelteKit frontend for monitoring and control.

## Layout
- `bot/` — Python trading bot (CAN SLIM + cup-with-handle); deployed to the VPS via `git pull`
- `trading-bot/` — SvelteKit web app (frontend for monitoring + control)
- `.claude/` — project context, strategy plan, and behavioural rules

## Frontend (`trading-bot/`)

Stack: SvelteKit 2 + Svelte 5 (runes mode), strict TypeScript, Prettier + ESLint.

### Developing

```sh
cd trading-bot
npm install
npm run dev
# or open the app in a new browser tab
npm run dev -- --open
```

### Building

```sh
npm run build
```

Preview the production build with `npm run preview`.

> To deploy, you may need to install an [adapter](https://svelte.dev/docs/kit/adapters) for your target environment.

### Scaffolded with

```sh
npx sv@0.15.3 create --template minimal --types ts --add prettier eslint mcp="ide:claude-code+setup:remote" --install npm trading-bot
```

## Bot (`bot/`)

Python trading bot. Source lives here; deployed to `/root/trading_bot/bot/` on the production droplet via `git pull`. See [bot/README.md](bot/README.md) for the deploy workflow and the one-time migration runbook (the bot was previously scp-only at `/root/trading-bot/`). Strategy parameters and phase roadmap live in [.claude/PLAN.md](.claude/PLAN.md); infrastructure details in [.claude/CLAUDE.md](.claude/CLAUDE.md).

## Status

Paper trading only — `TRADING_ENABLED=False`. Live trading is gated on Phase 7 validation criteria in [.claude/PLAN.md](.claude/PLAN.md).

## Licence

MIT — see [LICENSE](LICENSE).
