import yfinance as yf
import pandas as pd

def get_daily_data_yahoo(symbol: str, interval: str = "1d", period: str = "5y"):
    """
    Descarga datos históricos de Yahoo Finance con diferentes intervalos.
    
    Args:
        symbol: Símbolo del ticker (ej: SAN.MC)
        interval: Intervalo de tiempo - "1h", "1d", "1wk", "1mo"
        period: Período de datos - "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"
    
    Nota: Yahoo Finance limita datos intradiarios (1h) a los últimos 730 días
    """
    try:
        ticker = yf.Ticker(symbol)
        
        # Ajustar período según intervalo para evitar errores de Yahoo
        if interval == "1h":
            # Yahoo solo permite 730 días de datos horarios
            if period in ["5y", "2y"]:
                period = "730d"
        
        df = ticker.history(period=period, interval=interval)
    except Exception as e:
        raise ValueError(f"Error descargando de Yahoo Finance: {e}")

    if df.empty:
        raise ValueError(f"No se pudieron obtener datos de Yahoo Finance para {symbol}")

    # Resetear index para tener la fecha como columna
    df = df.reset_index()
    
    # DEBUG: Ver qué columnas devuelve Yahoo
    print(f"🔍 DEBUG yahoo_client - Columnas: {df.columns.tolist()}")
    print(f"🔍 DEBUG yahoo_client - interval={interval}, shape={df.shape}")
    if not df.empty:
        print(f"🔍 DEBUG yahoo_client - Primera fila index: {df.index[0]}, valor: {df.iloc[0]}")
    
    # Determinar nombre de columna de fecha (depende del intervalo)
    date_col = "Datetime" if interval in ["1m", "5m", "15m", "30m", "1h", "90m"] else "Date"
    
    precios = []
    for _, row in df.iterrows():
        timestamp = pd.Timestamp(row[date_col])
        
        # Formato de fecha según intervalo
        if interval in ["1m", "5m", "15m", "30m", "1h", "90m"]:
            fecha_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        else:
            fecha_str = timestamp.strftime("%Y-%m-%d")
        
        precios.append({
            "fecha": fecha_str,
            "open": float(row["Open"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "close": float(row["Close"]),
            "volume": int(row["Volume"])
        })

    return precios

