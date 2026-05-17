import pandas as pd


def generate_signal(symbol: str, bars: pd.DataFrame) -> str | None:
    if len(bars) < 2:
        return None

    close  = bars["close"]
    sma    = close.mean()
    latest = close.iloc[-1]

    if latest > sma:
        return "buy"
    else:
        return "sell"

    return None
