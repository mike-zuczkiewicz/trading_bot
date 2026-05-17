# =============================================================================
# TRADING BOT CONFIGURATION
# Edit parameters here. Bot will not trade until TRADING_ENABLED = True.
# =============================================================================

# --- MASTER SWITCH -----------------------------------------------------------
TRADING_ENABLED = False          # Set True only when ready to trade

# --- ACCOUNT -----------------------------------------------------------------
PAPER_TRADING   = True           # True = paper account, False = live (careful)

# --- UNIVERSE ----------------------------------------------------------------
WATCHLIST = [                    # Symbols to monitor and trade
    "SPY",
    "QQQ",
    "AAPL",
]

# --- POSITION SIZING ---------------------------------------------------------
MAX_POSITION_VALUE   = 5000      # Max USD per position
MAX_OPEN_POSITIONS   = 3         # Max concurrent positions

# --- RISK MANAGEMENT ---------------------------------------------------------
MAX_DAILY_LOSS_USD   = 500       # Bot halts if daily loss exceeds this

# --- STRATEGY ----------------------------------------------------------------
LOOKBACK_BARS        = 20          # Number of bars for signal calculation
BAR_TIMEFRAME        = "1Min"      # 1Min, 5Min, 15Min, 1Hour, 1Day

# --- ORDER EXECUTION ---------------------------------------------------------
ORDER_TYPE           = "market"    # market | limit
LIMIT_SLIPPAGE_PCT   = 0.001       # For limit orders: offset from mid-price

# --- CONTROL -----------------------------------------------------------------
STOP_FILE            = "STOP"      # Bot halts if this file exists in run dir
POLL_INTERVAL_SEC    = 60          # Seconds between market scans

# --- LOGGING -----------------------------------------------------------------
LOG_FILE             = "bot.log"
LOG_LEVEL            = "INFO"      # DEBUG | INFO | WARNING | ERROR
