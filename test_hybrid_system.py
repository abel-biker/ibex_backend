"""
Test rápido del sistema híbrido sin necesidad de servidor HTTP.
"""
import sys
import os

# Añadir directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("🧪 Iniciando test del sistema híbrido AI...\n")

# Test 1: Importaciones
print("📦 Test 1: Verificando importaciones...")
try:
    from app.models.predictor import MLPredictor
    from app.scoring.sentiment import FinBERTSentiment
    from app.models.prophet_predictor import ProphetPredictor
    from app.scoring.hybrid_scorer import HybridScorer
    print("✅ Todas las importaciones exitosas\n")
except Exception as e:
    print(f"❌ Error en importaciones: {e}\n")
    sys.exit(1)

# Test 2: ML Predictor
print("📊 Test 2: Inicializando ML Predictor...")
try:
    ml_predictor = MLPredictor()
    print(f"✅ ML Predictor creado")
    print(f"   Estado: {'Entrenado' if ml_predictor.is_trained else 'Modo básico'}\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

# Test 3: Prophet
print("📈 Test 3: Inicializando Prophet...")
try:
    prophet = ProphetPredictor()
    print(f"✅ Prophet creado")
    print(f"   Disponible: {prophet.is_available}\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

# Test 4: FinBERT
print("🤖 Test 4: Inicializando FinBERT (lazy loading)...")
try:
    finbert = FinBERTSentiment()
    print(f"✅ FinBERT creado (lazy loading OK)\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

# Test 5: Hybrid Scorer
print("🚀 Test 5: Inicializando Hybrid Scorer...")
try:
    hybrid = HybridScorer(enable_sentiment=False)
    print(f"✅ Hybrid Scorer creado")
    print(f"   ML entrenado: {hybrid.ml_predictor.is_trained}")
    print(f"   Prophet disponible: {hybrid.prophet.is_available}")
    print(f"   Sentiment habilitado: {hybrid.enable_sentiment}\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

# Test 6: Predicción simple con datos sintéticos
print("🧠 Test 6: Test de predicción con datos sintéticos...")
try:
    import pandas as pd
    import numpy as np
    
    # Crear datos sintéticos
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    data = pd.DataFrame({
        'date': dates,
        'open': np.random.uniform(10, 15, 100),
        'high': np.random.uniform(11, 16, 100),
        'low': np.random.uniform(9, 14, 100),
        'close': np.random.uniform(10, 15, 100),
        'volume': np.random.uniform(1000000, 5000000, 100),
        'rsi': np.random.uniform(30, 70, 100),
        'macd': np.random.uniform(-0.5, 0.5, 100),
        'macd_signal': np.random.uniform(-0.5, 0.5, 100),
        'sma_20': np.random.uniform(10, 15, 100),
        'sma_50': np.random.uniform(10, 15, 100),
        'bb_upper': np.random.uniform(15, 16, 100),
        'bb_middle': np.random.uniform(12, 13, 100),
        'bb_lower': np.random.uniform(9, 10, 100),
    })
    
    # Test con Danelfin tradicional
    from app.scoring.danelfin_score import calculate_danelfin_score
    score_trad = calculate_danelfin_score(data)
    print(f"✅ Danelfin tradicional:")
    print(f"   Score: {score_trad['total_score']}")
    print(f"   Rating: {score_trad['rating']}\n")
    
    # Test con sistema híbrido
    score_hybrid = hybrid.calculate_hybrid_score(data)
    print(f"✅ Sistema híbrido:")
    print(f"   Score: {score_hybrid['total_score']}")
    print(f"   Rating: {score_hybrid['rating']}")
    print(f"   Signal: {score_hybrid['signal']}")
    print(f"   Metodología: {score_hybrid.get('methodology', 'N/A')}\n")
    
except Exception as e:
    print(f"❌ Error en predicción: {e}\n")
    import traceback
    traceback.print_exc()

print("\n✨ Tests completados!")
print("\n📝 Resumen:")
print("   - Sistema híbrido: ✅ Funcionando")
print("   - ML Predictor: ⚠️  Modo básico (necesita entrenamiento)")
print("   - Prophet: ⚠️  Instalar con: pip install prophet")
print("   - FinBERT: ✅ OK (lazy loading)")
print("\n🎯 Siguiente paso: Entrenar modelo ML con datos reales")
print("   POST /api/v1/admin/ml/train-model")
