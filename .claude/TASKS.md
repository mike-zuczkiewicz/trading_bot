# Trading Bot — Next Coding Tasks

Concrete, actionable work items for the active phase. Tasks here are the unit of "do this next."

Sister files:
- `PHASES.md` — the phase list (sets context for which tasks are in scope right now)
- `PLAN.md` — strategy parameters, signal-layer priorities, Phase 7 gate criteria

**Active phase:** Phase 3 — CAN SLIM bot + email alerts. Phase 3.1 (regime filter) is the prerequisite that ships first.

**Parking lot:** ratcheting trailing-stop variant — see [PLAN.md §Open Design Questions](PLAN.md). Discuss / backtest before scheduling.

---

## Phase 3.1 — Market-regime filter (SPY 200-SMA) — START HERE

Without this, the bot can't safely run CAN SLIM in bear markets. Smallest possible scope to ship.

- [ ] Add a `bot/regime.py` module exposing `is_buy_regime() -> bool`. Fetch SPY daily bars via the existing Alpaca data client; compare last close to its 200-day SMA.
- [ ] Cache one SPY-bars fetch per scan loop in `bot.py` (not per symbol).
- [ ] Wire `is_buy_regime()` into `bot.py`'s scan loop between the watchlist scan and the per-symbol BUY branch. When `False`: log `Regime: bearish — buys disabled` and skip BUY actions. SELL/exit logic stays active.
- [ ] Add `SPY_REGIME_LOOKBACK_DAYS = 200` to `bot/config.py`.
- [ ] Unit test: mock SPY bars above vs below the 200-SMA; assert `True`/`False`.

---

## Phase 3 — CAN SLIM screener + cup-with-handle entry

Replaces the momentum stub in `bot/strategy.py`. Build incrementally — each sub-task should produce log-visible behavior before moving on.

### Universe
- [ ] Replace `WATCHLIST` in `config.py` with a loader for the S&P 500 constituent list. Cache to a gitignored JSON under `bot/` (e.g. `sp500_cache.json`); refresh weekly.
- [ ] Update `bot.py`'s scan loop to iterate the loaded universe.

### Screener (CAN SLIM — see `PLAN.md` §Signal Layers for full source list)
- [ ] **C + A — Earnings:** integrate `yfinance` for quarterly EPS and revenue growth (primary, free, no account); Financial Modeling Prep free tier as fallback. Threshold: ≥25% YoY EPS growth, ≥25% revenue growth. Morningstar Investor MCP used by Claude for advisory validation — not in the automated bot loop (see `PLAN.md` §Morningstar Access).
- [ ] **L — Relative strength:** compute 12-month RS rank vs S&P 500; keep top 20%.
- [ ] **S — Volume:** ≥1.4× the 50-day average on the breakout bar.
- [ ] **N — 52-week high:** current close within 15% of 52-week high.

### Cup-with-handle detector
Parameters in `PLAN.md` §Cup-with-Handle Parameters.
- [ ] Detect cup base: 7–65 weeks duration, 12–33% depth, right side within 1–2% of left high.
- [ ] Detect handle: 5–15% pullback, low volume, upper half of cup.
- [ ] Buy trigger: close above handle high + 40%+ volume surge on the breakout bar.

### Position sizing — align with `PLAN.md` §Position Sizing
- [ ] `config.py`: set `MAX_POSITION_VALUE = 18750`, `MAX_OPEN_POSITIONS = 5`.
- [ ] Confirm sizing math in `bot.py` matches `(equity × 0.015) / 0.08` — formula needs to be in code, not hardcoded.

### Staged exit logic
The bot currently has **no** per-position stop-loss. This is the biggest gap.
- [ ] Track entry price per position (read from Alpaca position objects; persist locally if needed for restarts).
- [ ] At −5% from entry: sell 50% of the position.
- [ ] At −8% from entry: sell remaining 50%.
- [ ] Wire into the scan loop (runs before BUY logic each cycle).
- [ ] `config.py`: add `STOP_LOSS_STAGE_1_PCT = 0.05`, `STOP_LOSS_STAGE_2_PCT = 0.08`, `STAGE_1_SELL_FRACTION = 0.5`.

### Audit log writer
Schema and policy in `CLAUDE.md` §Audit Trail. Currently aspirational; not implemented.
- [ ] Implement `bot/audit.py` with `log_event(actor, change_type, target, old_value, new_value, reason, envelope_rule_satisfied=None)`. JSONL append to `/root/trading_bot/bot/audit.log`.
- [ ] Call from `bot.py` on: parameter updates, position adds, manual overrides, envelope actions.
- [ ] Weekly rotation to `audit-YYYY-WW.log.gz` (cron, or in-Python check on first scan after Monday 00:00 UTC).

### Email alerts
- [ ] Add SMTP env vars to `.env.example`: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`. Recipient is `okipapa@me.com` per `PLAN.md` §Alerts.
- [ ] Send on: BUY signal, SELL signal, daily-loss halt, STOP-file detected, regime flip (Phase 3.1), audit-log write error.

### Scan-time gating
Current code polls every `POLL_INTERVAL_SEC` (60s). PLAN.md wants three scheduled scans per day. Schedule constants `SCREENER_TIMES_HM` and `SCREENER_TZ` already exist in [bot/config.py](../bot/config.py); what's missing is the `bot.py` refactor that uses them.
- [ ] Refactor [bot/bot.py](../bot/bot.py) to the two-thread architecture in [scan-loop.html](scan-loop.html): screener thread fires at the scheduled Berlin windows and writes to a `screener_signals` dict; trading thread runs every 60s, pauses while screener is running, and reads signals from the shared dict.

---

## Phase 3.2 — Institutional sponsorship (after Phase 3 ships)

- [ ] Alpaca news-feed integration: pull recent headlines for each candidate, score for institutional-buying mentions.
- [ ] 13F-freshness flag: if a candidate appears in a 13F filing within the last 90 days, raise its score.
- [ ] Combine into a composite "I" score; threshold to gate or raise conviction (decide which after looking at noise during paper-validation).

---

## Cross-cutting (not phase-gated)

- [ ] **Move bot from `User=root` to `User=mike`** in the systemd unit. Do this after Phase 5 (web app) ships and the production layout is finalized, per `CLAUDE.md`.
- [ ] **Font Awesome Pro v7.2.0 kit:** configure before Phase 5 starts.

---

## Done

Move tasks here as they ship, with date + commit SHA. Pruned periodically.

- 2026-05-17: bot migrated into git, deploy workflow switched to `git -C /root/trading_bot pull && systemctl restart` — commits `bf910ea`..`444e6d6`.
- 2026-05-17: post-audit cleanup of unused `config.py` keys (`FRACTIONAL_SHARES`, `STOP_LOSS_PCT`, etc. removed) and STOP-latency wording — `444e6d6`.
- 2026-05-19: Mac SSH as `mike` confirmed working (key already authorized) — no commit, environment-only.
