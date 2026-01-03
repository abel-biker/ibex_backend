import os
import requests
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()

API_KEY = os.getenv("TWELVE_DATA_API_KEY")

if not API_KEY:
    print("❌ No se encontró TWELVE_DATA_API_KEY en el .env")
    exit()

print("🔑 API KEY cargada correctamente:", API_KEY)

# Petición de prueba
url = "https://api.twelvedata.com/time_series"
params = {
    "symbol": "AAPL",
    "interval": "1day",
    "apikey": API_KEY,
    "outputsize": 5
}

response = requests.get(url, params=params).json()

print("\n📡 Respuesta de Twelve Data:")
print(response)
