from app.data_providers.yahoo_client import get_daily_data_yahoo
from app.data_providers.twelvedata_client import get_daily_data_twelvedata


# Alias seguros para símbolos frecuentes
ALIAS = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
}


def normalize_symbol(symbol: str) -> str:
    """Normaliza símbolos comunes sin romper los que ya funcionan.
    Reglas mínimas y reversibles:
    - Usa alias BTC/ETH → BTC-USD/ETH-USD.
    - Si no trae sufijo y es corto (IBEX), añade .MC.
    - Si ya trae '-' o '.', no se toca.
    """
    if not symbol:
        return symbol
    s = symbol.strip()
    upper = s.upper()

    if upper in ALIAS:
        return ALIAS[upper]

    if "." in s or "-" in s:
        return s

    # Heurística ligera para IBEX
    if len(upper) <= 5 and upper.isalnum():
        return f"{upper}.MC"

    return s


def get_daily_data(symbol: str, interval: str = "1d", period: str = "5y"):
    """
    Obtiene datos de mercado con soporte para múltiples intervalos.
    
    Args:
        symbol: Símbolo del activo
        interval: "1h" (horario), "1d" (diario), "5d" usa "1d"
        period: Período de histórico ("1d", "5d", "1mo", "3mo", "1y", "5y")
    
    Returns:
        Lista de diccionarios con datos OHLCV
    """
    norm_symbol = normalize_symbol(symbol)
    
    # Mapeo de timeframes para usuarios a Yahoo Finance
    if interval == "5d":
        interval = "1d"
        period = "5d"
    
    try:
        data = get_daily_data_yahoo(norm_symbol, interval=interval, period=period)
        if data:
            return data
    except Exception as e:
        print(f"Yahoo Finance falló para {norm_symbol} ({interval}/{period}):", e)

    # Fallback a TwelveData (solo para datos diarios)
    if interval == "1d":
        try:
            return get_daily_data_twelvedata(norm_symbol)
        except Exception as e:
            print("TwelveData falló:", e)
    
    return None
