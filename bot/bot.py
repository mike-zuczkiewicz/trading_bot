#!/usr/bin/env python3
# =============================================================================
# ALPACA TRADING BOT
# Two loops:
#   screener_loop  — runs at Berlin 15:30 / 18:45 / 22:00, updates signal dict
#   trading_loop   — polls every POLL_INTERVAL_SEC, pauses while screener runs
# Does not trade until config.TRADING_ENABLED = True
# =============================================================================

import logging
import os
import threading
import time
from datetime import datetime, date
from pathlib import Path
from zoneinfo import ZoneInfo

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, StockLatestQuoteRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

import config
from strategy import generate_signal

# --- Logging -----------------------------------------------------------------

logging.basicConfig(
    level    = getattr(logging, config.LOG_LEVEL),
    format   = "%(asctime)s [%(levelname)s] %(message)s",
    handlers = [
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler(),
    ]
)
log = logging.getLogger(__name__)

# --- Alpaca clients ----------------------------------------------------------

API_KEY    = os.environ.get("ALPACA_API_KEY")
API_SECRET = os.environ.get("ALPACA_SECRET_KEY")

if not API_KEY or not API_SECRET:
    raise EnvironmentError("ALPACA_API_KEY and ALPACA_SECRET_KEY must be set.")

trading_client = TradingClient(API_KEY, API_SECRET, paper=config.PAPER_TRADING)
data_client    = StockHistoricalDataClient(API_KEY, API_SECRET)

# --- Shared state (screener → trading loop) ----------------------------------
#
# screener_running: set while screener is active; trading loop skips each cycle
#   where it is set. Cleared in a finally block so it always resets even on error.
#
# screener_signals: written exclusively by screener_loop (only while
#   screener_running is set); read by trading_loop (only while screener_running
#   is clear). No additional lock needed.

screener_running = threading.Event()
screener_signals: dict[str, str] = {}   # {symbol: "buy" | "sell"}
stop_event       = threading.Event()

# --- Timeframe map -----------------------------------------------------------

TIMEFRAME_MAP = {
    "1Min":  TimeFrame(1,  TimeFrameUnit.Minute),
    "5Min":  TimeFrame(5,  TimeFrameUnit.Minute),
    "15Min": TimeFrame(15, TimeFrameUnit.Minute),
    "1Hour": TimeFrame(1,  TimeFrameUnit.Hour),
    "1Day":  TimeFrame(1,  TimeFrameUnit.Day),
}

# --- Helpers -----------------------------------------------------------------

def stop_file_exists() -> bool:
    return Path(config.STOP_FILE).exists()


def get_account():
    return trading_client.get_account()


def get_positions() -> dict:
    return {p.symbol: p for p in trading_client.get_all_positions()}


def get_bars(symbol: str):
    tf  = TIMEFRAME_MAP.get(config.BAR_TIMEFRAME, TimeFrame(1, TimeFrameUnit.Day))
    req = StockBarsRequest(
        symbol_or_symbols = symbol,
        timeframe          = tf,
        limit              = config.LOOKBACK_BARS,
    )
    bars = data_client.get_stock_bars(req).df
    if hasattr(bars.index, "levels"):
        bars = bars.loc[symbol]
    return bars


def daily_loss_exceeded(account) -> bool:
    equity     = float(account.equity)
    last_eq    = float(account.last_equity)
    daily_loss = last_eq - equity
    if daily_loss >= config.MAX_DAILY_LOSS_USD:
        log.warning(f"Daily loss ${daily_loss:.2f} exceeds limit ${config.MAX_DAILY_LOSS_USD}. Halting.")
        return True
    return False


def place_order(symbol: str, side: OrderSide, notional: float):
    if config.ORDER_TYPE == "market":
        req = MarketOrderRequest(
            symbol        = symbol,
            notional      = round(notional, 2),
            side          = side,
            time_in_force = TimeInForce.DAY,
        )
    else:
        quote = data_client.get_stock_latest_quote(
            StockLatestQuoteRequest(symbol_or_symbols=symbol)
        )[symbol]
        mid   = (quote.ask_price + quote.bid_price) / 2
        limit = mid * (1 + config.LIMIT_SLIPPAGE_PCT) if side == OrderSide.BUY \
                else mid * (1 - config.LIMIT_SLIPPAGE_PCT)
        req = LimitOrderRequest(
            symbol        = symbol,
            notional      = round(notional, 2),
            limit_price   = round(limit, 2),
            side          = side,
            time_in_force = TimeInForce.DAY,
        )
    order = trading_client.submit_order(req)
    log.info(f"Order submitted: {side.value.upper()} {symbol} ${notional:.2f} | id={order.id}")
    return order


# --- Screener ----------------------------------------------------------------

def _due_slot(last_run: dict[tuple, date]) -> tuple | None:
    """Return the (H, M) slot that is due right now but not yet run today."""
    now   = datetime.now(ZoneInfo(config.SCREENER_TZ))
    today = now.date()
    hm    = (now.hour, now.minute)
    for slot in config.SCREENER_TIMES_HM:
        if hm == slot and last_run.get(slot) != today:
            return slot
    return None


def _run_screener(universe: list[str]) -> dict[str, str]:
    """Screen every symbol and return signals. Called inside screener_loop."""
    signals = {}
    for symbol in universe:
        try:
            bars   = get_bars(symbol)
            signal = generate_signal(symbol, bars)
            if signal:
                signals[symbol] = signal
        except Exception as e:
            log.warning(f"Screener: {symbol} error — {e}")
    log.info(f"Screener: {len(signals)} signals from {len(universe)} symbols")
    return signals


def screener_loop() -> None:
    """Thread: fires the screener at each scheduled Berlin time slot."""
    last_run: dict[tuple, date] = {}
    log.info(f"Screener thread started. Slots: {config.SCREENER_TIMES_HM} ({config.SCREENER_TZ})")

    while not stop_event.is_set():
        slot = _due_slot(last_run)
        if slot:
            log.info(f"Screener: starting run for slot {slot[0]:02d}:{slot[1]:02d}")
            screener_running.set()
            try:
                new_signals = _run_screener(config.WATCHLIST)
                screener_signals.clear()
                screener_signals.update(new_signals)
                last_run[slot] = datetime.now(ZoneInfo(config.SCREENER_TZ)).date()
            except Exception as e:
                log.error(f"Screener: run failed — {e}")
            finally:
                screener_running.clear()
                log.info("Screener: complete. Trading loop resuming.")

        stop_event.wait(timeout=30)


# --- Trading loop ------------------------------------------------------------

def trading_loop() -> None:
    """Thread: runs a trading cycle every POLL_INTERVAL_SEC."""
    log.info(f"Trading thread started. Poll interval: {config.POLL_INTERVAL_SEC}s")

    while not stop_event.is_set():

        if stop_file_exists():
            log.info("STOP file detected. Halting.")
            stop_event.set()
            break

        if screener_running.is_set():
            log.info("Screener running — trading cycle paused.")
            stop_event.wait(timeout=config.POLL_INTERVAL_SEC)
            continue

        try:
            account = get_account()
        except Exception as e:
            log.error(f"Failed to fetch account: {e}")
            stop_event.wait(timeout=config.POLL_INTERVAL_SEC)
            continue

        if daily_loss_exceeded(account):
            stop_event.set()
            break

        positions = get_positions()

        # --- Stop-loss exits (Phase 3 — not yet implemented) -----------------
        # Will run here before buy logic each cycle.

        # --- Act on screener signals -----------------------------------------
        for symbol, signal in list(screener_signals.items()):
            in_position = symbol in positions

            if signal == "buy" and not in_position:
                if len(positions) >= config.MAX_OPEN_POSITIONS:
                    log.info(f"{symbol}: max positions reached, skipping.")
                    continue
                if config.TRADING_ENABLED:
                    place_order(symbol, OrderSide.BUY, config.MAX_POSITION_VALUE)
                else:
                    log.info(f"[DRY RUN] Would BUY {symbol} ${config.MAX_POSITION_VALUE}")

            elif signal == "sell" and in_position:
                pos_value = float(positions[symbol].market_value)
                if config.TRADING_ENABLED:
                    place_order(symbol, OrderSide.SELL, pos_value)
                else:
                    log.info(f"[DRY RUN] Would SELL {symbol} ${pos_value:.2f}")

        log.info(f"Trading cycle complete. Sleeping {config.POLL_INTERVAL_SEC}s.")
        stop_event.wait(timeout=config.POLL_INTERVAL_SEC)


# --- Entry point -------------------------------------------------------------

def run() -> None:
    log.info("=" * 60)
    log.info("Alpaca Trading Bot starting")
    log.info(f"TRADING_ENABLED  : {config.TRADING_ENABLED}")
    log.info(f"PAPER_TRADING    : {config.PAPER_TRADING}")
    log.info(f"WATCHLIST        : {config.WATCHLIST}")
    log.info(f"SCREENER_TIMES   : {config.SCREENER_TIMES_HM} ({config.SCREENER_TZ})")
    log.info(f"POLL_INTERVAL    : {config.POLL_INTERVAL_SEC}s")
    log.info("=" * 60)

    t_screener = threading.Thread(target=screener_loop, name="screener", daemon=True)
    t_trading  = threading.Thread(target=trading_loop,  name="trading",  daemon=True)

    t_screener.start()
    t_trading.start()

    try:
        while not stop_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("KeyboardInterrupt — stopping.")
        stop_event.set()

    t_screener.join(timeout=60)
    t_trading.join(timeout=60)
    log.info("Bot stopped.")


if __name__ == "__main__":
    run()
