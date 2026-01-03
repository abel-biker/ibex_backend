import pandas as pd

def sma(data: pd.DataFrame, period: int) -> pd.Series:
    """
    Calcula la media móvil simple (SMA).
    """
    if "Close" not in data.columns:
        raise ValueError("El DataFrame debe contener la columna 'Close'.")

    return data["Close"].rolling(window=period).mean()


def rsi(data: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calcula el RSI (Relative Strength Index).
    """
    if "Close" not in data.columns:
        raise ValueError("El DataFrame debe contener la columna 'Close'.")

    delta = data["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))
    return rsi

