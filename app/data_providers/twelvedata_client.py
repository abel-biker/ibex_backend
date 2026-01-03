import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TWELVE_DATA_API_KEY")

def get_daily_data_twelvedata(symbol: str):
    if not API_KEY:
        raise RuntimeError("Falta TWELVE_DATA_API_KEY en .env")

    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": "1day",
        "apikey": API_KEY,
        "outputsize": 100
    }

    r = requests.get(url, params=params).json()

    if "values" not in r:
        raise ValueError(f"Error Twelve Data: {r}")

    precios = []
    for item in r["values"]:
        precios.append({
            "fecha": item["datetime"],
            "open": float(item["open"]),
            "high": float(item["high"]),
            "low": float(item["low"]),
            "close": float(item["close"]),
            "volume": float(item.get("volume", 0))
        })

    precios.sort(key=lambda x: x["fecha"])
    return precios
