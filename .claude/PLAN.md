# Trading Bot — Development Plan

## Phase Status

### Completed
- ✅ Phase 1: Infrastructure (Alpaca connected, VPS provisioned, bot scaffold)
- ✅ Phase 2: Reboot-proof (systemd, .env, SSH from Mac+Windows)
- ✅ Security hardening (UFW, Fail2ban, non-root user, root SSH disabled)

### Pending
- [ ] Mac SSH as mike
- [ ] Phase 3: CAN SLIM bot + email alerts
- [ ] Phase 4: Signal layers
- [ ] Phase 5: Svelte web app
  - [ ] Configure Font Awesome Pro v7.2.0 kit
- [ ] Phase 6: Telegram bot
- [ ] Phase 7: Live trading (after 4–6 weeks paper validation)

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
- Risk per trade: 1.5% of portfolio
- Formula: (Portfolio × 0.015) / 0.08
- At $100k: ~$18,750 per position
- Max concurrent positions: 5–6
- Reserve: capacity to add to winners

### Cup-with-Handle Parameters
- Cup duration: 7–65 weeks
- Cup depth: 12–33%
- Right side within 1–2% of left side high
- Handle: 5–15% pullback, low volume, upper half of cup
- Buy point: close above handle high + 40%+ volume surge

---

## Signal Layers
1. CAN SLIM screener (earnings, RS, volume, 52-week high)
2. Cup-with-handle entry trigger
3. Trump Truth Social / X posts via Alpaca news feed
4. Congressional trades via Capitol Trades (Trump focus)
5. Morningstar MCP for fundamental earnings data

---

## Claude's Role
- Advisory and monitoring only
- Queries Alpaca via MCP on demand
- Limited autonomous parameter adjustment within defined envelope (e.g. +$5K on strong candidates)
- Full audit trail of all parameter changes
- Never executes trades directly

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
