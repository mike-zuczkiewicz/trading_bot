# Trading Bot — Development Plan

## Phase Status

### Completed
- ✅ Phase 1: Infrastructure (Alpaca connected, VPS provisioned, bot scaffold)
- ✅ Phase 2: Reboot-proof (systemd, .env, SSH from Windows)
- ✅ Security hardening (UFW, Fail2ban, non-root user, root SSH disabled)
- ✅ Bot migrated into git (2026-05-17) — VPS deploys via `sudo git -C /root/trading_bot pull && sudo systemctl restart trading-bot.service`

### Pending
- [ ] Mac SSH as mike
- [ ] Phase 3: CAN SLIM bot + email alerts
- [ ] Phase 3.1: Market-regime filter (SPY 200-SMA gate)
- [ ] Phase 3.2: Institutional-sponsorship signal
- [ ] Phase 4: Signal layers
- [ ] Phase 5: Svelte web app
  - [ ] Configure Font Awesome Pro v7.2.0 kit
- [ ] Phase 6: Telegram bot
- [ ] Phase 7: Live trading — gated on paper-validation criteria below

### Phase 7 entry criteria (all must be true, evaluated over ≥4 weeks live-paper)
- Closed trade count: ≥ 30 (for statistical signal)
- Win rate: ≥ 45%
- Average winner / average loser: ≥ 2.0
- Max peak-to-trough drawdown: ≤ 15%
- Annualised Sharpe (252-day basis): ≥ 1.0
- No single underlying responsible for > 25% of total loss
- Audit log: zero unexplained parameter changes (see CLAUDE.md §Audit Trail)

---

## Strategy Parameters

### CAN SLIM Screener
- Universe: S&P 500 (503 stocks)
- Scan times: Market open, midday, close (Berlin: 15:30, 18:45, 22:00)
- Mode: Signals only (no auto-execution yet)
- Earnings data: Morningstar MCP + Financial Modeling Prep (free tier)

### Entry
- Cup-with-handle breakout above handle high
- Volume surge: 1.4–1.5x 50-day average on breakout

### Exit Rules
- -5% from entry: sell 50%
- -8% from entry: sell all

### Position Sizing
- Risk per trade: 1.5% of portfolio (worst case — single gap-down through both exit levels)
- Formula: (Portfolio × 0.015) / 0.08
- At $100k: ~$18,750 per position
- Max concurrent positions: 5 (5 × $18,750 = $93,750 ≤ cash balance, no margin use)
- Reserve: capacity to add to winners
- Expected realised risk per trade with staged exit (50% sold at -5%, remainder at -8%): ~1.22% of portfolio
- Worst-case (rule-of-thumb 1.5%) only applies when both stops fail to trigger separately, e.g. an overnight gap-down. Treat the 1.5% as the planning ceiling, 1.22% as the typical outcome.

### Cup-with-Handle Parameters
- Cup duration: 7–65 weeks
- Cup depth: 12–33%
- Right side within 1–2% of left side high
- Handle: 5–15% pullback, low volume, upper half of cup
- Buy point: close above handle high + 40%+ volume surge

---

## Signal Layers
1. CAN SLIM screener — current coverage: C+A (earnings), L (RS), S (volume), N partial (52-week high)
   - Gap: I (institutional sponsorship) and M (market direction) not yet implemented
   - Planned in Phase 3.1: market-regime filter (SPY > 200-day SMA → buys enabled; SPY < 200-day SMA → screener returns watchlist only, no entries). This is the highest-priority addition since unfiltered CAN SLIM has historically blown up in bear markets.
   - Planned in Phase 3.2: institutional-sponsorship signal via Alpaca news feed + 13F-freshness flag
2. Cup-with-handle entry trigger
3. Trump Truth Social / X posts via Alpaca news feed
4. Congressional trades via Capitol Trades (Trump focus)
5. Morningstar MCP for fundamental earnings data

---

## Claude's Role
- Advisory and monitoring only
- Queries Alpaca via MCP on demand
- Limited autonomous parameter adjustment within the envelope below. All other parameter changes require explicit human approval.
- Full audit trail of all parameter changes (see CLAUDE.md §Audit Trail)
- Never executes trades directly

### Autonomous-adjustment envelope
Claude may add up to **+$5,000** to an existing position when ALL of the following are true:
- Position is currently ≥ +3% above entry
- 5-day average volume > 50-day average volume (continued institutional interest)
- Last daily close above the 21-day SMA
- No scheduled earnings within next 5 trading days
- Resulting total notional ≤ max-concurrent cap × per-position size
- Action is logged to audit trail with all five values that satisfied the rule

---

## Web App (Phase 5)
- Framework: SvelteKit
- Match watchbill project conventions: `/github/watchbill`
- Read watchbill repo before scaffolding
- Hosted on same VPS (Nginx)
- Build locally, deploy static dist/ to VPS
- Features: live charts, portfolio, signal feed, bot control panel, audit log

---

## Alerts
- Email: okipapa@me.com (Phase 3)
- Telegram: account created, username pending (Phase 6)
