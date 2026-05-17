# trading_bot

Automated trading bot using Alpaca paper/live account, CAN SLIM strategy with cup-with-handle entry pattern.
Hosted on DigitalOcean (Frankfurt). Includes a SvelteKit frontend for monitoring and control.

## Layout
- `trading-bot/` — SvelteKit web app (this repo's main tracked code)
- `/root/trading-bot/` on the VPS — Python bot (separate; see `.claude/CLAUDE.md`)
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

## Bot (VPS)

Lives outside this repo at `/root/trading-bot/` on the production droplet. See [.claude/CLAUDE.md](.claude/CLAUDE.md) for infrastructure, deployment, and strategy details. Status and pending phases tracked in [.claude/PLAN.md](.claude/PLAN.md).

## Status

Paper trading only — `TRADING_ENABLED=False`. Live trading is gated on Phase 7 validation criteria in [.claude/PLAN.md](.claude/PLAN.md).

## Licence

MIT — see [LICENSE](LICENSE).
