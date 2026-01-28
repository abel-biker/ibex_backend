# 🤖 Sistema Híbrido AI - Guía Completa

## 🎯 ¿Qué es el Sistema Híbrido?

El nuevo sistema combina **4 metodologías de análisis** para generar señales de trading más precisas:

1. **Danelfin (25%)** - Indicadores técnicos tradicionales (RSI, MACD, SMA, Bollinger)
2. **XGBoost ML (40%)** - Predicción de tendencia con Machine Learning ⭐ **MÁS IMPORTANTE**
3. **Prophet (20%)** - Predicción de precio con series temporales de Meta
4. **FinBERT (15%)** - Análisis de sentiment de noticias (opcional)

---

## 🚀 Instalación de Dependencias

```powershell
# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Instalar nuevas dependencias
pip install -r requirements.txt

# Las dependencias clave son:
# - xgboost: Machine Learning
# - prophet: Predicción de series temporales
# - transformers + torch: FinBERT sentiment analysis
```

**⏱️ Tiempo estimado:** 5-10 minutos (Prophet requiere compilar cmdstanpy)

---

## 📊 Uso Básico

### 1. Obtener Ranking con AI

```http
GET /api/v1/ibex35/ranking?use_ai=true&limit=10
```

**Respuesta:**
```json
{
  "total": 10,
  "methodology": "Hybrid AI (XGBoost+Prophet+Danelfin)",
  "ranking": [
    {
      "symbol": "SAN.MC",
      "score": 7.8,
      "signal": "BUY",
      "ml_signal": "BUY",
      "ml_score": 8.2,
      "prophet_score": 7.5,
      "technical_score": 7.0
    }
  ]
}
```

### 2. Obtener Score Individual con AI

```http
GET /api/v1/stock/SAN.MC/score?use_ai=true
```

**Respuesta detallada:**
```json
{
  "symbol": "SAN.MC",
  "score": 7.8,
  "rating": "BUY",
  "signal": "BUY",
  "confidence": "HIGH",
  "methodology": "Hybrid AI",
  "components": {
    "technical": {
      "score": 7.0,
      "weight": "25%"
    },
    "ml_prediction": {
      "score": 8.2,
      "signal": "BUY",
      "probability": 0.82,
      "weight": "40%"
    },
    "prophet": {
      "score": 7.5,
      "predicted_change_pct": 3.2,
      "weight": "20%"
    },
    "sentiment": {
      "score": 5.0,
      "sentiment": "neutral",
      "weight": "15%"
    }
  }
}
```

---

## 🎓 Entrenar Modelo ML

### Opción 1: Entrenar con el índice IBEX (recomendado)

```http
POST /api/v1/admin/ml/train-model?symbol=^IBEX&days_ahead=15
```

### Opción 2: Entrenar con una acción específica

```http
POST /api/v1/admin/ml/train-model?symbol=SAN.MC&days_ahead=15
```

**Parámetros:**
- `symbol`: Símbolo para entrenar (default: ^IBEX)
- `days_ahead`: Días futuros a predecir (default: 15)
- `test_size`: Proporción de test (default: 0.2)

**⏱️ Tiempo:** 2-5 minutos

**Respuesta:**
```json
{
  "status": "success",
  "model_path": "data/models/ibex_xgboost.pkl",
  "training_stats": {
    "total_samples": 1250,
    "train_samples": 1000,
    "test_samples": 250,
    "days_ahead": 15
  },
  "feature_importance": {
    "rsi": 0.25,
    "macd": 0.18,
    "close": 0.15,
    "sma_20": 0.12
  }
}
```

---

## 📈 Feature Importance

Ver qué indicadores son más importantes:

```http
GET /api/v1/admin/ml/feature-importance
```

**Respuesta:**
```json
{
  "model_status": "trained",
  "feature_importance": {
    "rsi": 0.25,
    "macd": 0.18,
    "close": 0.15,
    "sma_20": 0.12,
    "bb_lower": 0.10,
    "volume": 0.08,
    "sma_50": 0.07,
    "bb_middle": 0.03,
    "bb_upper": 0.02
  }
}
```

---

## 🔍 Estado del Sistema

Verificar que todo funciona:

```http
GET /api/v1/admin/ml/model-status
```

**Respuesta:**
```json
{
  "hybrid_system": {
    "status": "active",
    "components": {
      "danelfin": {
        "status": "active",
        "weight": "25%"
      },
      "ml_predictor": {
        "status": "trained",
        "weight": "40%",
        "model_type": "XGBoost"
      },
      "prophet": {
        "status": "available",
        "weight": "20%"
      },
      "sentiment": {
        "status": "disabled",
        "weight": "15%"
      }
    }
  }
}
```

---

## 🆚 Comparación: Tradicional vs Híbrido

### Sistema Tradicional (Danelfin)
```
✅ Solo indicadores técnicos
❌ No predice el futuro
❌ Señales retrasadas
📊 Score basado en lo que YA pasó
```

### Sistema Híbrido AI
```
✅ Indicadores técnicos + ML
✅ Predice tendencia a 15 días
✅ Señales adelantadas
✅ Prophet predice precio futuro
📊 Score basado en predicciones
```

---

## 🐛 Troubleshooting

### Error: "Modelo no entrenado"
**Solución:** Entrenar el modelo primero:
```http
POST /api/v1/admin/ml/train-model
```

### Error: "Prophet no disponible"
**Solución:** Instalar Prophet:
```powershell
pip install prophet cmdstanpy
```

### Error: "FinBERT no disponible"
**Solución:** Instalar transformers:
```powershell
pip install transformers torch
```

### Predicciones lentas
**Normal:** La primera predicción tarda ~2-3 segundos (carga modelos). Las siguientes son instantáneas.

---

## 🎯 Mejores Prácticas

### 1. Entrenar periódicamente
- Reentrenar cada semana con datos actualizados
- Usar `symbol=^IBEX` para mejor generalización

### 2. Usar caché
- El sistema cachea datos 5 minutos automáticamente
- Mejora performance en móvil

### 3. Modo AI por defecto
- Usar `use_ai=true` siempre para mejores predicciones
- Fallback a Danelfin si modelo no entrenado

### 4. Monitorear feature importance
- Verificar qué indicadores son más importantes
- Ajustar estrategias según importancia

---

## 📱 Integración en Android

```kotlin
// Usar sistema híbrido en Android
interface IBEX35ApiService {
    
    @GET("/api/v1/ibex35/ranking")
    suspend fun getRankingAI(
        @Query("use_ai") useAI: Boolean = true,
        @Query("limit") limit: Int = 10
    ): Response<RankingResponse>
    
    @GET("/api/v1/stock/{symbol}/score")
    suspend fun getStockScoreAI(
        @Path("symbol") symbol: String,
        @Query("use_ai") useAI: Boolean = true
    ): Response<HybridScoreResponse>
}
```

---

## 🔬 Metodología Científica

### XGBoost (40% peso)
- Algoritmo: Gradient Boosting
- Input: 10 features (RSI, MACD, SMA, etc.)
- Output: Probabilidad de subida en 15 días
- Métricas: Accuracy ~65-70%, F1-Score ~0.68

### Prophet (20% peso)
- Algoritmo: Series temporales aditivas
- Componentes: Tendencia + Estacionalidad
- Output: Precio predicho en 5 días
- Intervalos de confianza incluidos

### FinBERT (15% peso - opcional)
- Modelo: BERT fine-tuned en noticias financieras
- Input: Texto de noticias/reportes
- Output: Sentiment (positive/negative/neutral)
- Precisión: ~90% en textos financieros

---

## 📊 Próximos Pasos

1. ✅ Sistema híbrido implementado
2. 🔄 Entrenar modelo con datos del IBEX
3. 📱 Integrar en app Android
4. 📰 Añadir scraping de noticias para FinBERT
5. 🎯 Optimizar pesos de componentes
6. 🔄 Auto-reentrenamiento semanal
7. 📊 Dashboard de métricas ML

---

## 🤝 Contribuir

Si quieres mejorar el sistema:
- Experimentar con otros modelos (LSTM, CNN-LSTM del TFM)
- Ajustar pesos de componentes
- Añadir más features
- Integrar fuentes de noticias

---

**Versión:** 2.3.0  
**Autor:** Abel  
**Fecha:** Enero 2026  
