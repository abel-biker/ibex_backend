# 📈 IBEX 35 Trading System - Danelfin Style + Expert Advisors

**Versión:** 2.2.1 (Hotfix - Enero 2026)  
**Estado:** ✅ Estable en Railway

Sistema completo de análisis y trading automático para el IBEX 35, inspirado en **Danelfin** con **Expert Advisors** tipo MetaTrader 4/5. Optimizado para Android.

## 🚨 Última Actualización (v2.2.1)

**Hotfix crítico aplicado:** Scheduler de alertas deshabilitado temporalmente para resolver bloqueos en Railway. Las alertas ahora se verifican manualmente vía endpoint:

```bash
POST /api/v1/admin/check-alerts-now
```

Ver [CHANGELOG_v2.2.1.md](CHANGELOG_v2.2.1.md) para detalles completos.

---

## 🎯 Características Principales

### 1. **Sistema de Scoring Danelfin (0-10)**
- Rating automático de 0 a 10 para cada acción del IBEX 35
- Análisis combinado:
  - **Técnico (40%)**: RSI, MACD, Medias móviles, Bandas de Bollinger
  - **Momentum (30%)**: Tendencias de precio, volumen relativo
  - **Sentiment (30%)**: Posición vs máximos/mínimos, volatilidad

### 2. **Expert Advisors (EAs) Configurables**
5 estrategias de trading automático:
- **RSI EA**: Basado en sobreventa/sobrecompra
- **MACD EA**: Cruces de MACD
- **MA Crossover EA**: Golden Cross / Death Cross
- **Bollinger EA**: Bandas de Bollinger
- **Ensemble EA**: Combinación inteligente de todas (recomendado)

Cada EA incluye:
- Gestión de riesgo (stop loss, take profit, trailing stop)
- Backtesting con métricas detalladas
- Señales en tiempo real

### 3. **API REST Optimizada para Móvil**
Endpoints lightweight diseñados para apps Android con respuestas rápidas y datos comprimidos.

### 4. **35 Empresas del IBEX 35**
Base de datos completa con sectores y pesos de capitalización.

---

## 🚀 Instalación y Configuración

### Requisitos
- Python 3.8+
- pip
- Virtualenv (recomendado)

### Setup Rápido

```powershell
# 1. Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar servidor
python -m uvicorn app.main:app --reload

# 4. Acceder a la API
# http://localhost:8000
# Documentación interactiva: http://localhost:8000/docs
```

---

## 📱 API Endpoints para Android

### 1. Ranking IBEX 35 con Scores
```http
GET /api/v1/ibex35/ranking?limit=35&sector=Financiero&min_score=7.0
```

**Respuesta:**
```json
{
  "total": 8,
  "sector_filter": "Financiero",
  "min_score_filter": 7.0,
  "timestamp": "2026-01-03 10:30:00",
  "ranking": [
    {
      "symbol": "SAN.MC",
      "name": "Banco Santander",
      "sector": "Financiero",
      "score": 8.5,
      "rating": "STRONG BUY",
      "confidence": "HIGH",
      "price": 4.25,
      "change_pct": 2.4,
      "technical_score": 8.2,
      "momentum_score": 8.9,
      "sentiment_score": 8.4
    }
  ]
}
```

### 2. Score Detallado de una Acción
```http
GET /api/v1/stock/SAN.MC/score
```

**Respuesta:**
```json
{
  "symbol": "SAN.MC",
  "name": "Banco Santander",
  "sector": "Financiero",
  "timestamp": "2026-01-03 10:30:00",
  "price": 4.25,
  "score": 8.5,
  "rating": "STRONG BUY",
  "confidence": "HIGH",
  "sub_scores": {
    "technical": 8.2,
    "momentum": 8.9,
    "sentiment": 8.4
  },
  "signals": [
    "RSI en sobreventa (28.5) - Oportunidad de compra",
    "MACD cruzó al alza - Señal alcista",
    "⭐ Score excelente (8.5/10) - Fuerte potencial alcista"
  ],
  "indicators": {
    "rsi": 28.5,
    "macd": 0.0234,
    "macd_signal": 0.0189,
    "sma_20": 4.15,
    "sma_50": 3.98
  }
}
```

### 3. Señales de Expert Advisors
```http
GET /api/v1/stock/SAN.MC/signals?strategy=ensemble
```

**Estrategias disponibles:**
- `rsi` - RSI oversold/overbought
- `macd` - MACD crossovers
- `ma_crossover` - Golden/Death Cross
- `bollinger` - Bollinger Bands
- `ensemble` - Combinación de todas (recomendado)

**Respuesta:**
```json
{
  "symbol": "SAN.MC",
  "name": "Banco Santander",
  "strategy": "ensemble",
  "timestamp": "2026-01-03 10:30:00",
  "signal": "BUY",
  "confidence": 0.82,
  "reason": "Consenso alcista: RSI en sobreventa; MACD cruzó al alza",
  "current_price": 4.25,
  "stop_loss": 4.12,
  "take_profit": 4.51,
  "risk_reward": 2.0
}
```

### 4. Backtest de Estrategia
```http
GET /api/v1/stock/SAN.MC/backtest?strategy=ensemble&initial_capital=10000
```

**Respuesta:**
```json
{
  "symbol": "SAN.MC",
  "name": "Banco Santander",
  "strategy": "ensemble",
  "timestamp": "2026-01-03 10:30:00",
  "initial_capital": 10000,
  "final_equity": 12450.50,
  "metrics": {
    "total_trades": 42,
    "winning_trades": 28,
    "losing_trades": 14,
    "win_rate": 66.67,
    "total_return": 2450.50,
    "total_return_pct": 24.51,
    "max_drawdown": 8.5,
    "sharpe_ratio": 1.85,
    "avg_win": 150.25,
    "avg_loss": 75.50,
    "profit_factor": 1.99
  },
  "recent_trades": [...]
}
```

### 5. Watchlist de Oportunidades
```http
GET /api/v1/watchlist?min_score=7.0
```

Retorna todas las acciones del IBEX 35 con score >= 7.0 (oportunidades de compra).

### 6. Sectores del IBEX 35
```http
GET /api/v1/sectors
```

---

## 🎓 Guía de Uso para Android

### Flujo Típico de la App

1. **Pantalla Inicio**: Mostrar ranking IBEX 35
   ```
   GET /api/v1/ibex35/ranking?limit=10
   ```

2. **Detalle de Acción**: Al hacer tap en una empresa
   ```
   GET /api/v1/stock/{symbol}/score
   GET /api/v1/stock/{symbol}/signals?strategy=ensemble
   ```

3. **Watchlist**: Filtrar oportunidades
   ```
   GET /api/v1/watchlist?min_score=7.0
   ```

4. **Backtesting**: Validar estrategia antes de invertir
   ```
   GET /api/v1/stock/{symbol}/backtest?strategy=ensemble
   ```

### Recomendaciones para Android

1. **Cache**: Cachear rankings por 5-15 minutos
2. **Refresh**: Pull-to-refresh para actualizar datos
3. **Notificaciones**: Usar watchlist para alertas push
4. **Offline**: Guardar último ranking en SQLite local
5. **Gráficos**: Usar bibliotecas como MPAndroidChart

---

## 🔧 Configuración de Expert Advisors

Los EAs se pueden configurar con parámetros personalizados:

```python
from app.ea.expert_advisors import EAConfig, Ensemble_EA

config = EAConfig(
    name="Mi Estrategia",
    description="Estrategia conservadora",
    
    # Indicadores
    rsi_period=14,
    rsi_oversold=30,
    rsi_overbought=70,
    
    # Gestión de riesgo
    risk_per_trade=2.0,  # 2% del capital por operación
    max_open_trades=3,   # Máximo 3 posiciones abiertas
    stop_loss_pct=3.0,   # Stop loss al 3%
    take_profit_pct=6.0, # Take profit al 6%
    trailing_stop_pct=2.0,  # Trailing stop al 2%
    
    # Filtros
    min_score=7.0,       # Solo operar con score >= 7
    volume_filter=True,
    trend_filter=True
)

ea = Ensemble_EA(config)
```

---

## 📊 Métricas del Scoring Danelfin

### Escala de Rating
- **9.0-10.0**: STRONG BUY ⭐⭐⭐⭐⭐
- **7.5-8.9**: BUY ⭐⭐⭐⭐
- **6.0-7.4**: HOLD ⭐⭐⭐
- **4.5-5.9**: NEUTRAL ⭐⭐
- **3.0-4.4**: SELL ⭐
- **0.0-2.9**: STRONG SELL 🚫

### Componentes del Score

#### Análisis Técnico (40%)
- RSI: Sobreventa = +puntos, Sobrecompra = -puntos
- MACD: Cruces alcistas = +puntos
- Medias móviles: Golden Cross = +puntos
- Bollinger Bands: Posición en las bandas

#### Momentum (30%)
- Rendimiento 5 días y 20 días
- Volumen relativo (confirmación de movimientos)
- Tendencia de máximos y mínimos

#### Sentiment (30%)
- Distancia a máximos/mínimos de 52 semanas
- Volatilidad (menor = mejor)
- Racha de días positivos/negativos

---

## 🧪 Testing y Validación

### Ejecutar Tests
```powershell
# Unit tests
pytest tests/

# Test de una acción específica
python -c "
from app.data_providers.market_data import get_daily_data
from app.scoring.danelfin_score import calculate_danelfin_score
import pandas as pd

data = get_daily_data('SAN.MC')
df = pd.DataFrame(data)
score = calculate_danelfin_score(df)
print(score)
"
```

### Backtest Manual
```python
from app.ea.expert_advisors import Ensemble_EA, EAConfig
import pandas as pd

# Cargar datos
data = get_daily_data('SAN.MC')
df = pd.DataFrame(data)

# Crear EA
config = EAConfig(name="Test Strategy")
ea = Ensemble_EA(config)

# Backtest
results = ea.backtest(df, initial_capital=10000)
print(f"Return: {results['total_return_pct']:.2f}%")
print(f"Win Rate: {results['win_rate']:.2f}%")
print(f"Sharpe: {results['sharpe_ratio']:.2f}")
```

---

## 🌐 Despliegue en Producción

### Opción 1: Docker (Recomendado)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```powershell
docker build -t ibex35-api .
docker run -p 8000:8000 ibex35-api
```

### Opción 2: Cloud (Railway, Render, Heroku)
1. Conectar repositorio Git
2. Configurar `Procfile`:
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
3. Deploy automático

### Opción 3: VPS
```bash
# Instalar Nginx como reverse proxy
sudo apt install nginx

# Configurar systemd service
sudo nano /etc/systemd/system/ibex35-api.service

# Contenido:
[Unit]
Description=IBEX 35 Trading API
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/ibex35
ExecStart=/var/www/ibex35/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 🔐 Seguridad y Rate Limiting

Para producción, añadir:

```python
# app/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/v1/ibex35/ranking")
@limiter.limit("10/minute")  # Máximo 10 requests por minuto
def get_ranking(...):
    ...
```

---

## 📈 Roadmap Futuro

- [ ] Sistema de alertas push para Android
- [ ] Base de datos SQLite para cache y persistencia
- [ ] WebSocket para datos en tiempo real
- [ ] Análisis fundamental (P/E, ROE, deuda, etc.)
- [ ] Integración con brokers (Interactive Brokers, XTB)
- [ ] Modo paper trading
- [ ] Portfolio tracker con performance
- [ ] Machine Learning para predicción de precios

---

## 🤝 Contribuciones

Para contribuir:
1. Fork el repositorio
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -m 'Add nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

---

## 📞 Soporte

- Documentación API interactiva: `http://localhost:8000/docs`
- Issues: GitHub Issues
- Email: support@ibex35trading.com

---

## 📄 Licencia

MIT License - Libre para uso comercial y personal

---

## ⚠️ Disclaimer

Este software es solo para fines educativos e informativos. Las señales de trading y scores **no constituyen asesoramiento financiero**. El trading conlleva riesgo de pérdida de capital. Siempre realice su propia investigación y consulte con un asesor financiero profesional antes de invertir.

---

**Desarrollado con ❤️ para traders del IBEX 35**
