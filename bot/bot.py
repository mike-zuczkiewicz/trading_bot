#!/usr/bin/env python3
# =============================================================================
# ALPACA TRADING BOT — SCAFFOLD
# Does not trade until config.TRADING_ENABLED = True
# =============================================================================

import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
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
    positions = trading_client.get_all_positions()
    return {p.symbol: p for p in positions}


def get_bars(symbol: str):
    from alpaca.data.requests import StockBarsRequest
    from datetime import timedelta

    tf  = TIMEFRAME_MAP.get(config.BAR_TIMEFRAME, TimeFrame(1, TimeFrameUnit.Day))
    req = StockBarsRequest(
        symbol_or_symbols = symbol,
        timeframe          = tf,
        limit              = config.LOOKBACK_BARS,
    )
    bars = data_client.get_stock_bars(req).df
    if hasattr(bars.index, "levels"):          # multi-index (symbol, timestamp)
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
    """Place an order. Only called when TRADING_ENABLED = True."""
    if config.ORDER_TYPE == "market":
        req = MarketOrderRequest(
            symbol      = symbol,
            notional    = round(notional, 2),
            side        = side,
            time_in_force = TimeInForce.DAY,
        )
    else:
        # Limit order: fetch latest quote for price reference
        from alpaca.data.requests import StockLatestQuoteRequest
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


# --- Main loop ---------------------------------------------------------------

def run():
    log.info("=" * 60)
    log.info("Alpaca Trading Bot starting")
    log.info(f"TRADING_ENABLED : {config.TRADING_ENABLED}")
    log.info(f"PAPER_TRADING   : {config.PAPER_TRADING}")
    log.info(f"WATCHLIST       : {config.WATCHLIST}")
    log.info("=" * 60)

    while True:

        # --- Stop file check -------------------------------------------------
        if stop_file_exists():
            log.info(f"STOP file detected. Halting.")
            break

        # --- Account / daily loss check --------------------------------------
        try:
            account = get_account()
        except Exception as e:
            log.error(f"Failed to fetch account: {e}")
            time.sleep(config.POLL_INTERVAL_SEC)
            continue

        if daily_loss_exceeded(account):
            break

        positions = get_positions()

        # --- Scan watchlist --------------------------------------------------
        for symbol in config.WATCHLIST:

            try:
                bars   = get_bars(symbol)
                signal = generate_signal(symbol, bars)
            except Exception as e:
                log.warning(f"{symbol}: data/signal error — {e}")
                continue

            log.info(f"{symbol}: signal={signal}")

            if signal is None:
                continue

            in_position = symbol in positions

            # --- BUY logic ---------------------------------------------------
            if signal == "buy" and not in_position:
                if len(positions) >= config.MAX_OPEN_POSITIONS:
                    log.info(f"{symbol}: max positions reached, skipping.")
                    continue
                if config.TRADING_ENABLED:
                    place_order(symbol, OrderSide.BUY, config.MAX_POSITION_VALUE)
                else:
                    log.info(f"[DRY RUN] Would BUY {symbol} ${config.MAX_POSITION_VALUE}")

            # --- SELL logic --------------------------------------------------
            elif signal == "sell" and in_position:
                pos_value = float(positions[symbol].market_value)
                if config.TRADING_ENABLED:
                    place_order(symbol, OrderSide.SELL, pos_value)
                else:
                    log.info(f"[DRY RUN] Would SELL {symbol} ${pos_value:.2f}")

        log.info(f"Scan complete. Sleeping {config.POLL_INTERVAL_SEC}s.")
        time.sleep(config.POLL_INTERVAL_SEC)

    log.info("Bot stopped.")


# --- Entry point -------------------------------------------------------------

if __name__ == "__main__":
    run()
