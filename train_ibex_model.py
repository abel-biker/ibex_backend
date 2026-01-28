"""
Script para entrenar modelo ML con datos históricos del IBEX 35.
Ejecutar: python train_ibex_model.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.predictor import MLPredictor
from app.data_providers.market_data import get_daily_data
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

print("=" * 60)
print("🤖 ENTRENAMIENTO DE MODELO ML PARA IBEX 35")
print("=" * 60)

# 1. Descargar datos históricos
print("\n📥 Descargando datos históricos del IBEX (5 años)...")
try:
    data_raw = get_daily_data("^IBEX", interval="1d", period="5y")
    if not data_raw or len(data_raw) < 500:
        print("❌ Datos insuficientes. Intentando con menor período...")
        data_raw = get_daily_data("^IBEX", interval="1d", period="2y")
    
    df = pd.DataFrame(data_raw)
    print(f"✅ Descargados {len(df)} días de datos históricos")
except Exception as e:
    print(f"❌ Error descargando datos: {e}")
    sys.exit(1)

# 2. Calcular indicadores técnicos
print("\n📊 Calculando indicadores técnicos...")
try:
    from app.services.ensemble import calculate_rsi, calculate_macd, calculate_bollinger_bands
    
    # Medias móviles
    df["sma_20"] = df["close"].rolling(window=20).mean()
    df["sma_50"] = df["close"].rolling(window=50).mean()
    
    # RSI
    df["rsi"] = calculate_rsi(df["close"])
    
    # MACD
    macd_vals = calculate_macd(df["close"])
    df["macd"] = macd_vals[0]
    df["macd_signal"] = macd_vals[1]
    
    # Bandas de Bollinger
    bb_vals = calculate_bollinger_bands(df["close"])
    df["bb_upper"] = bb_vals[0]
    df["bb_middle"] = bb_vals[1]
    df["bb_lower"] = bb_vals[2]
    
    print("✅ Indicadores calculados")
except Exception as e:
    print(f"❌ Error calculando indicadores: {e}")
    sys.exit(1)

# 3. Crear target (1 si sube en 15 días, 0 si baja)
print("\n🎯 Creando variable objetivo (predicción a 15 días)...")
days_ahead = 15
df["future_return"] = df["close"].shift(-days_ahead) / df["close"] - 1
df["target"] = (df["future_return"] > 0).astype(int)

# Limpiar NaN
df_clean = df.dropna()
print(f"✅ Datos limpios: {len(df_clean)} muestras")

# Distribución de clases
positive_pct = (df_clean["target"] == 1).sum() / len(df_clean) * 100
print(f"   - Subidas: {positive_pct:.1f}%")
print(f"   - Bajadas: {100-positive_pct:.1f}%")

# 4. Preparar features
print("\n🔧 Preparando features...")
feature_cols = ['rsi', 'macd', 'macd_signal', 'sma_20', 'sma_50',
                'bb_upper', 'bb_middle', 'bb_lower', 'volume', 'close']

X = df_clean[feature_cols].values
y = df_clean["target"].values

print(f"✅ Features preparadas: {X.shape}")

# 5. Split train/test (sin shuffle para series temporales)
print("\n✂️ Dividiendo datos train/test (80/20)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, shuffle=False
)

print(f"   - Train: {len(X_train)} muestras")
print(f"   - Test: {len(X_test)} muestras")

# 6. Entrenar modelo
print("\n🔄 Entrenando modelo XGBoost...")
print("   (Esto puede tardar 1-2 minutos...)")

try:
    predictor = MLPredictor()
    predictor.train(X_train, y_train, X_test, y_test)
    print("✅ Modelo entrenado exitosamente")
except Exception as e:
    print(f"❌ Error entrenando modelo: {e}")
    sys.exit(1)

# 7. Guardar modelo
print("\n💾 Guardando modelo...")
model_path = "data/models/ibex_xgboost.pkl"
try:
    predictor.save_model(model_path)
except Exception as e:
    print(f"❌ Error guardando modelo: {e}")
    sys.exit(1)

# 8. Feature importance
print("\n📊 Importancia de Features:")
print("-" * 40)
try:
    importance = predictor.get_feature_importance()
    for i, (feature, imp) in enumerate(importance.items(), 1):
        bar = "█" * int(imp * 50)
        print(f"{i}. {feature:12} {bar} {imp:.4f}")
except Exception as e:
    print(f"⚠️ No se pudo calcular feature importance: {e}")

# 9. Resumen final
print("\n" + "=" * 60)
print("✅ ENTRENAMIENTO COMPLETADO")
print("=" * 60)
print(f"📁 Modelo guardado en: {model_path}")
print(f"📊 Datos de entrenamiento: {len(X_train)} muestras")
print(f"🎯 Horizonte de predicción: {days_ahead} días")
print("\n🚀 Próximos pasos:")
print("   1. Reiniciar servidor: python -m uvicorn app.main:app --reload")
print("   2. Probar endpoint: GET /api/v1/stock/SAN.MC/score?use_ai=true")
print("   3. Ver status: GET /api/v1/admin/ml/model-status")
print("\n💡 El modelo ahora predice tendencias en lugar de reaccionar al pasado")
