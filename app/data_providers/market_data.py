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


def get_daily_data(symbol: str):
    norm_symbol = normalize_symbol(symbol)
    try:
        data = get_daily_data_yahoo(norm_symbol)
        if data:
            return data
    except Exception as e:
        print("Yahoo Finance falló:", e)

    # Fallback a TwelveData
    try:
        return get_daily_data_twelvedata(norm_symbol)
    except Exception as e:
        print("TwelveData falló:", e)
        return []
