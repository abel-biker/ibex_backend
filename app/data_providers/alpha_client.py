import os
import requests
from dotenv import load_dotenv

# Cargar el archivo .env desde la raíz del proyecto
load_dotenv(dotenv_path="C:/Users/Abel/Desktop/Proyecto API/ibex_backend/.env")

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"

def get_daily_data(symbol: str):
    if not API_KEY:
        raise RuntimeError("No se encontró ALPHA_VANTAGE_API_KEY en las variables de entorno")

    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": "compact",
        "apikey": API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if "Error Message" in data:
        raise ValueError(f"Error de Alpha Vantage: {data['Error Message']}")

    if "Time Series (Daily)" not in data:
        raise ValueError(f"Respuesta inesperada de Alpha Vantage: {data}")

    series = data["Time Series (Daily)"]
    precios = []

    for fecha, valores in series.items():
        precios.append({
            "fecha": fecha,
            "open": float(valores["1. open"]),
            "high": float(valores["2. high"]),
            "low": float(valores["3. low"]),
            "close": float(valores["4. close"]),
            "volume": float(valores["6. volume"])
        })

    precios.sort(key=lambda x: x["fecha"])
    return precios
