import yfinance as yf
import pandas as pd

def get_daily_data_yahoo(symbol: str):
    """Descarga 5 años de datos históricos de Yahoo Finance"""
    try:
        # Usar Ticker().history() en vez de yf.download() para evitar MultiIndex
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="5y", interval="1d")
    except Exception as e:
        raise ValueError(f"Error descargando de Yahoo Finance: {e}")

    if df.empty:
        raise ValueError(f"No se pudieron obtener datos de Yahoo Finance para {symbol}")

    # Resetear index para tener la fecha como columna
    df = df.reset_index()
    
    precios = []
    for _, row in df.iterrows():
        precios.append({
            "fecha": pd.Timestamp(row["Date"]).strftime("%Y-%m-%d"),
            "open": float(row["Open"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "close": float(row["Close"]),
            "volume": int(row["Volume"])
        })

    return precios
