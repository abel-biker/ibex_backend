# 🚀 Guía de Inicio Rápido - IBEX 35 Trading System

## Paso 1: Activar Entorno Virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

Si aparece error de permisos:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Paso 2: Instalar Dependencias (solo primera vez)

Las dependencias ya están instaladas. Si necesitas reinstalarlas:
```powershell
pip install -r requirements.txt
```

## Paso 3: Iniciar Servidor

```powershell
python -m uvicorn app.main:app --reload
```

✅ El servidor estará disponible en: **http://localhost:8000**

## Paso 4: Pruebas Rápidas

### Opción A: Navegador (Más Fácil)

1. Abre en tu navegador: http://localhost:8000/docs
2. Verás la documentación interactiva de Swagger
3. Prueba los endpoints haciendo clic en "Try it out"

### Endpoints Recomendados para Probar:

- **GET** `/` - Estado de la API
- **GET** `/api/v1/ibex35/ranking?limit=10` - Top 10 IBEX 35
- **GET** `/api/v1/stock/SAN.MC/score` - Score de Santander
- **GET** `/api/v1/stock/SAN.MC/signals` - Señales de trading
- **GET** `/api/v1/watchlist?min_score=7.0` - Oportunidades de compra

### Opción B: Script de Prueba

Ejecuta el script de test incluido:
```powershell
python test_system.py
```

Esto analizará Banco Santander (SAN.MC) con:
- Score Danelfin completo
- Señales de Expert Advisors
- Backtest de la estrategia Ensemble

### Opción C: curl (Terminal)

```powershell
# Ranking top 5
curl http://localhost:8000/api/v1/ibex35/ranking?limit=5

# Score de Santander
curl http://localhost:8000/api/v1/stock/SAN.MC/score

# Señales de trading
curl http://localhost:8000/api/v1/stock/SAN.MC/signals?strategy=ensemble
```

### Opción D: Python Directo

```python
import requests

# Ranking
response = requests.get("http://localhost:8000/api/v1/ibex35/ranking?limit=5")
print(response.json())

# Score individual
response = requests.get("http://localhost:8000/api/v1/stock/SAN.MC/score")
print(response.json())
```

## 📊 Empresas del IBEX 35 Disponibles

### Top por Capitalización (High Weight):
- `SAN.MC` - Banco Santander
- `BBVA.MC` - BBVA
- `IBE.MC` - Iberdrola
- `ITX.MC` - Inditex
- `TEF.MC` - Telefónica
- `REP.MC` - Repsol
- `FER.MC` - Ferrovial
- `ACS.MC` - ACS

### Más Símbolos:
Ver archivo `app/data_providers/ibex35_symbols.py` para la lista completa de 35 empresas.

## 🔥 Ejemplos de Uso Avanzados

### 1. Ranking por Sector
```http
GET /api/v1/ibex35/ranking?sector=Financiero&limit=10
```

Sectores disponibles:
- Financiero
- Energía
- Telecomunicaciones
- Construcción
- Retail
- Farmacéutico
- etc.

### 2. Watchlist Personalizada
```http
GET /api/v1/watchlist?min_score=7.5
```

Retorna solo acciones con score >= 7.5 (oportunidades fuertes)

### 3. Comparar Estrategias
```http
# RSI
GET /api/v1/stock/SAN.MC/signals?strategy=rsi

# MACD
GET /api/v1/stock/SAN.MC/signals?strategy=macd

# Ensemble (recomendado)
GET /api/v1/stock/SAN.MC/signals?strategy=ensemble
```

### 4. Backtest con Capital Personalizado
```http
GET /api/v1/stock/SAN.MC/backtest?strategy=ensemble&initial_capital=50000
```

## 🐛 Solución de Problemas

### Error: "No module named 'app'"
- Asegúrate de estar en el directorio raíz: `cd "C:\Proyecto Abel\Proyecto API\ibex_backend"`
- Verifica que exista el archivo `app/__init__.py`

### Error: "Symbol not in IBEX 35"
- Usa símbolos con sufijo `.MC` (Madrid): `SAN.MC`, `BBVA.MC`, etc.
- Ver lista completa en `app/data_providers/ibex35_symbols.py`

### Error: "No data available"
- Yahoo Finance puede estar temporalmente caído
- Algunos símbolos pueden tener restricciones de datos
- Prueba con otro símbolo: `SAN.MC`, `BBVA.MC`, `IBE.MC`

### Puerto 8000 en Uso
```powershell
# Usar otro puerto
python -m uvicorn app.main:app --reload --port 8080
```

### Lentitud en Primera Petición
- Es normal, Yahoo Finance tarda en responder la primera vez
- Posteriores peticiones son más rápidas

## 📱 Integración con Android

Ver archivo `android_example.kt` para código completo de integración.

### Setup Rápido Android:

1. Agregar Retrofit en `build.gradle`:
```gradle
implementation 'com.squareup.retrofit2:retrofit:2.9.0'
implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
```

2. Cambiar base URL en el cliente:
```kotlin
private const val BASE_URL = "http://TU_IP:8000/"
```

3. Usar desde ViewModel:
```kotlin
viewModelScope.launch {
    val result = repository.getRanking(limit = 10)
    // Actualizar UI
}
```

## 🎯 Próximos Pasos

1. ✅ **Prueba la API** con Swagger Docs: http://localhost:8000/docs
2. ✅ **Ejecuta el test**: `python test_system.py`
3. ✅ **Explora diferentes estrategias** (rsi, macd, bollinger, ensemble)
4. ✅ **Analiza tu acción favorita** del IBEX 35
5. ✅ **Integra con tu app Android** usando el código de ejemplo

## 📚 Documentación Completa

- README.md - Documentación completa del sistema
- android_example.kt - Código Kotlin para Android
- test_system.py - Script de prueba con ejemplos

## ✨ Features Destacadas

- ⭐ **Scoring Danelfin** 0-10 con análisis técnico, momentum y sentiment
- 🤖 **5 Expert Advisors** configurables con backtesting
- 📱 **API optimizada** para móviles Android
- 📊 **35 empresas** del IBEX 35
- 🔄 **Actualizaciones** en tiempo real de Yahoo Finance
- 📈 **Backtesting** completo con métricas profesionales

---

**¿Problemas? Consulta README.md para más detalles**
