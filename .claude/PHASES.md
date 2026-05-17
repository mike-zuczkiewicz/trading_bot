# Trading Bot — Phases

Authoritative phase list. One paragraph per phase describing what it accomplishes and why it exists.

Sister files:
- `TASKS.md` — concrete coding tasks for the active phase
- `PLAN.md` — strategy parameters, signal layer priorities, Phase 7 gate criteria, Claude's autonomy envelope

---

## Completed

### Phase 1 — Infrastructure
Provisioned the DigitalOcean droplet (Frankfurt, 1vCPU/1GB), connected the Alpaca paper account, scaffolded the bot directory layout, validated SDK auth end-to-end. Established the runtime location on the VPS.

### Phase 2 — Reboot-proof
Moved the bot under `systemd` with auto-restart and `EnvironmentFile=`-style `.env` loading. SSH key auth from Mike's Windows machine. Bot survives a host reboot without manual intervention.

### Security hardening
UFW firewall (ports 22/80/443 only), Fail2ban, `.env` at mode 600, root SSH login disabled. `mike` is a sudo user but sudo requires a password (no NOPASSWD rules).

### Bot migrated into git (2026-05-17)
Source moved from scp-only `/root/trading-bot/` (hyphen) to a version-controlled `bot/` folder. VPS deploys via `sudo git -C /root/trading_bot pull && sudo systemctl restart trading-bot.service`. The repo is public so the VPS can clone anonymously.

---

## Pending

### Phase 3 — CAN SLIM bot + email alerts
Replace the momentum stub in `strategy.py` with the real CAN SLIM screener and cup-with-handle entry trigger. Add email alerts on signal/exit. First phase where the bot produces trading signals worth acting on (still paper, still dry-run by `TRADING_ENABLED=False`).

### Phase 3.1 — Market-regime filter (SPY 200-SMA gate)
**Highest-priority Phase-3 add — ships first.** When SPY closes below its 200-day SMA, the screener returns watchlist only and emits no buy entries. Unfiltered CAN SLIM has historically blown up in bear markets, so this guard exists before any meaningful paper-validation period starts.

### Phase 3.2 — Institutional-sponsorship signal
Use the Alpaca news feed plus 13F-freshness flagging to close the "I" gap in CAN SLIM coverage. Soft signal (raises conviction), not a hard gate.

### Phase 4 — Signal layers
Supplementary feeds beyond CAN SLIM/cup-with-handle: Trump Truth Social / X posts via the Alpaca news feed, congressional trades via Capitol Trades (Trump focus), Morningstar MCP for fundamentals.

### Phase 5 — Svelte web app
SvelteKit frontend in `trading-bot/`. Live charts, portfolio view, signal feed, bot control panel, audit log. Matches watchbill project conventions exactly. Hosted on the same VPS via Nginx.

### Phase 6 — Telegram bot
Telegram channel for alerts and bot commands (status checks, kill switch, parameter queries).

### Phase 7 — Live trading
Flip `TRADING_ENABLED=True`, `PAPER_TRADING=False`. **Gated on the entry criteria in `PLAN.md` §Phase 7 entry criteria** — ≥30 closed trades, ≥45% win rate, ≥2.0 avg-winner/avg-loser, ≤15% max DD, ≥1.0 Sharpe, no single underlying responsible for >25% of total loss, zero unexplained parameter changes in the audit log, evaluated over ≥4 weeks of paper-trading.
