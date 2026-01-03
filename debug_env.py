from dotenv import load_dotenv
import os

print("Cargando .env...")
ok = load_dotenv(dotenv_path="C:/Users/Abel/Desktop/Proyecto API/ibex_backend/.env")
print("load_dotenv devolvió:", ok)

print("API KEY =", os.getenv("ALPHA_VANTAGE_API_KEY"))
