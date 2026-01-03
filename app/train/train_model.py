import yfinance as yf
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# Descargar datos históricos del IBEX
data = yf.download("^IBEX", period="5y", interval="1d")

# Crear indicadores
data['SMA_5'] = data['Close'].rolling(5).mean()
data['SMA_20'] = data['Close'].rolling(20).mean()
data['Target'] = (data['Close'].shift(-1) > data['Close']).astype(int)

# Preparar dataset
df = data[['SMA_5', 'SMA_20', 'Target']].dropna()
X = df[['SMA_5', 'SMA_20']]
y = df['Target']

# Entrenar modelo
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# Guardar modelo
joblib.dump(model, "ibex_model.pkl")
print("Modelo guardado como ibex_model.pkl")

