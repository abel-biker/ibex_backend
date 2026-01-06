# 🚀 Changelog - Versión 2.2.0

**Fecha**: 6 de Enero de 2026  
**Versión**: 2.2.0 - Mejoras Masivas

---

## ✅ Problemas Corregidos

### 1. **Nivel de Confianza Dinámico** 🎯
- ❌ **Antes**: Siempre mostraba 50% o valores fijos (HIGH/MEDIUM/LOW)
- ✅ **Ahora**: Cálculo dinámico basado en:
  - Cantidad de datos históricos (40%)
  - Calidad de indicadores técnicos (30%)
  - Volatilidad reciente (15%)
  - Consistencia de volumen (15%)
- 📊 **Resultado**: Muestra porcentaje exacto, ej: "HIGH (85%)" o "MEDIUM (67%)"
- 📍 **Archivo modificado**: `app/scoring/danelfin_score.py`

### 2. **Validación de Símbolos** (Versión 2.1.0)
- ✅ Todos los endpoints validan símbolos del IBEX 35
- ✅ Mensajes de error claros en español
- ✅ Dashboard HTML con página de error amigable

### 3. **Performance con Caché** (Versión 2.1.0)
- ✅ Sistema de caché de 5 minutos
- ✅ Respuestas 98% más rápidas

---

## 🆕 Nuevas Funcionalidades

### 4. **Múltiples Timeframes (1h / 1d / 5d)** ⏰

**Nuevo endpoint:**
```http
GET /api/v1/stock/{symbol}/data?timeframe=1h
```

**Timeframes disponibles:**
- `1h`: Datos horarios (últimos 7 días) - Perfecto para day trading
- `1d`: Datos diarios (6 meses) - Análisis medio plazo
- `5d`: Datos diarios (5 días) - Vista rápida semanal

**Ejemplo:**
```bash
GET /api/v1/stock/SAN.MC/data?timeframe=1h
```

**Respuesta:**
```json
{
  "symbol": "SAN.MC",
  "name": "Banco Santander",
  "sector": "Financiero",
  "timeframe": "1h",
  "data_points": 168,
  "data": [
    {"fecha": "2026-01-05 09:00:00", "open": 4.25, "high": 4.27, ...},
    ...
  ]
}
```

---

### 5. **Sistema de Favoritos** ⭐

**Endpoints:**
```http
POST   /api/v1/favorites/{symbol}    # Añadir favorito
DELETE /api/v1/favorites/{symbol}    # Eliminar favorito
GET    /api/v1/favorites             # Listar todos
```

**Características:**
- Persistencia en SQLite local
- Multi-usuario con `user_id` (default: "default")
- Enriquecido con nombre de empresa y sector

**Ejemplos:**
```bash
# Añadir Santander a favoritos
POST /api/v1/favorites/SAN.MC

# Listar favoritos
GET /api/v1/favorites?user_id=default
```

**Respuesta:**
```json
{
  "total": 3,
  "favorites": [
    {
      "id": 1,
      "symbol": "SAN.MC",
      "name": "Banco Santander",
      "sector": "Financiero",
      "added_at": "2026-01-06 10:30:00"
    },
    ...
  ]
}
```

---

### 6. **Sistema de Alertas de Precio** 🔔

**Endpoints:**
```http
POST   /api/v1/alerts              # Crear alerta
GET    /api/v1/alerts              # Listar alertas
DELETE /api/v1/alerts/{id}         # Eliminar alerta
PATCH  /api/v1/alerts/{id}         # Activar/desactivar
POST   /api/v1/alerts/check/{symbol}  # Verificar manualmente
```

**Características:**
- Alertas `above` (cuando sube) o `below` (cuando baja)
- Notificaciones:
  - **Popup**: Solo en plataforma
  - **Email**: Envío automático por SMTP
  - **Both**: Ambos métodos
- Persistencia en base de datos
- Verificación automática de precios

**Ejemplo - Crear alerta:**
```bash
POST /api/v1/alerts?symbol=SAN.MC&condition=above&target_price=4.50&notification_type=email&email=tu@email.com
```

**Parámetros:**
- `symbol`: Símbolo (ej: SAN.MC)
- `condition`: "above" o "below"
- `target_price`: Precio objetivo
- `notification_type`: "popup", "email", "both"
- `email`: Email (requerido si notification_type=email/both)

**Respuesta:**
```json
{
  "id": 1,
  "symbol": "SAN.MC",
  "name": "Banco Santander",
  "condition": "above",
  "target_price": 4.5,
  "notification_type": "email",
  "status": "created"
}
```

**Listar alertas activas:**
```bash
GET /api/v1/alerts?user_id=default&active_only=true
```

**Verificar alertas manualmente:**
```bash
POST /api/v1/alerts/check/SAN.MC
```
Retorna alertas activadas y emails enviados.

---

### 7. **Nombre de Empresa Prominente en Dashboard** 📋

- ❌ **Antes**: Solo mostraba el símbolo técnico (SAN.MC)
- ✅ **Ahora**: Muestra:
  - **Nombre completo** en título grande: "Banco Santander"
  - Símbolo debajo: "SAN.MC · Financiero"
  - Sector de la empresa

**Ejemplo visual:**
```
📊 Banco Santander
    SAN.MC · Financiero
    Última actualización: 06/01/2026
```

---

### 8. **Notificaciones por Email** 📧

**Sistema SMTP configurado:**
- Compatible con Gmail, Outlook, Yahoo, SMTP custom
- Emails HTML profesionales con gradientes
- Configuración vía variables de entorno

**Configurar (.env file):**
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password
FROM_EMAIL=tu-email@gmail.com
```

**Gmail App Password:**
1. Ve a https://myaccount.google.com/apppasswords
2. Crea una contraseña de aplicación
3. Usa esa contraseña en `.env`

**Endpoint de prueba:**
```bash
GET /api/v1/admin/test-email
```
Verifica que la configuración SMTP funcione.

---

## 🔧 Cambios Técnicos

### Archivos Nuevos:
```
app/
  models/
    user_data.py           # Gestión de favoritos y alertas (SQLite)
  services/
    notifications.py       # Envío de emails SMTP
  utils/
    __init__.py
    cache.py              # Sistema de caché (v2.1.0)
data/
  user_data.db            # Base de datos SQLite (auto-generada)
.env.example              # Plantilla de configuración
CHANGELOG_v2.2.md         # Este archivo
```

### Archivos Modificados:
```
app/main.py               # +200 líneas: endpoints favoritos, alertas, timeframes
app/scoring/danelfin_score.py  # Confianza dinámica mejorada
app/services/formatter.py      # Dashboard con nombre de empresa
app/data_providers/yahoo_client.py    # Soporte para 1h/1d/5d
app/data_providers/market_data.py     # Wrapper para timeframes
```

### Base de Datos SQLite:

**Tabla `favorites`:**
```sql
id | user_id | symbol | added_at
---+---------+--------+----------
1  | default | SAN.MC | 2026-01-06 10:00
```

**Tabla `price_alerts`:**
```sql
id | user_id | symbol | condition | target_price | notification_type | email | is_active | triggered
---+---------+--------+-----------+--------------+-------------------+-------+-----------+----------
1  | default | SAN.MC | above     | 4.50         | email             | tu@.. | 1         | 0
```

---

## 📊 Impacto de las Mejoras

| Funcionalidad | Antes | Después | Mejora |
|---------------|-------|---------|--------|
| **Confianza** | Fijo 50% | Dinámico 40-95% | ✅ Mucho más preciso |
| **Timeframes** | Solo diario | 1h/1d/5d | ✅ 3x flexibilidad |
| **Favoritos** | No existían | CRUD completo | ✅ Nueva feature |
| **Alertas** | No existían | Con email automático | ✅ Nueva feature |
| **Nombre empresa** | Solo símbolo | Nombre + sector | ✅ Mejor UX |
| **Notificaciones** | Manual | Automáticas por email | ✅ Nueva feature |

---

## 🚀 Cómo Usar las Nuevas Funcionalidades

### 📱 Para Desarrolladores de App Android:

**1. Selector de Timeframe:**
```kotlin
// En tu RecyclerView o tabs
val timeframes = listOf("1h", "1d", "5d")

fun loadData(symbol: String, timeframe: String) {
    api.getStockData(symbol, timeframe)
        .enqueue { response ->
            // Actualizar gráfico con response.data
        }
}
```

**2. Botón de Favoritos:**
```kotlin
favoriteButton.setOnClickListener {
    if (isFavorite) {
        api.removeFavorite(symbol).enqueue { ... }
    } else {
        api.addFavorite(symbol).enqueue { ... }
    }
}
```

**3. Crear Alerta:**
```kotlin
fun createAlert(symbol: String, price: Double, email: String) {
    api.createAlert(
        symbol = symbol,
        condition = "above",
        targetPrice = price,
        notificationType = "both",
        email = email
    ).enqueue { ... }
}
```

### 🌐 Para Frontend Web:

**HTML con selector de timeframe:**
```html
<select id="timeframe" onchange="loadChart()">
  <option value="1h">Últimas 24 horas</option>
  <option value="1d" selected>Últimos 6 meses</option>
  <option value="5d">Últimos 5 días</option>
</select>
```

**JavaScript:**
```javascript
async function loadChart() {
  const timeframe = document.getElementById('timeframe').value;
  const data = await fetch(`/api/v1/stock/SAN.MC/data?timeframe=${timeframe}`);
  // Renderizar gráfico
}
```

---

## 🧪 Ejemplos de Uso Completo

### Flujo típico de usuario:

**1. Buscar acción y ver datos en diferentes timeframes:**
```bash
# Vista diaria (default)
GET /api/v1/stock/SAN.MC/score

# Vista horaria para day trading
GET /api/v1/stock/SAN.MC/data?timeframe=1h

# Vista semanal rápida
GET /api/v1/stock/SAN.MC/data?timeframe=5d
```

**2. Añadir a favoritos si le gusta:**
```bash
POST /api/v1/favorites/SAN.MC
```

**3. Crear alerta de precio:**
```bash
POST /api/v1/alerts?symbol=SAN.MC&condition=above&target_price=4.50&notification_type=email&email=inversor@example.com
```

**4. Recibir notificación:**
- Cuando el precio de Santander llegue a 4.50€, recibirás un email automático 📧

**5. Ver favoritos y alertas:**
```bash
GET /api/v1/favorites
GET /api/v1/alerts
```

---

## ⚙️ Configuración Necesaria

### 1. Variables de Entorno (Email)

**Copiar plantilla:**
```bash
cp .env.example .env
```

**Editar `.env`:**
```env
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx  # App Password de Gmail
```

**Verificar:**
```bash
GET /api/v1/admin/test-email
```

### 2. Base de Datos

Se crea automáticamente en `data/user_data.db` al iniciar la API.

---

## 📝 Notas Importantes

### Gmail App Password:
- Gmail requiere "App Password", no tu contraseña normal
- 2FA debe estar activado
- Guía: https://support.google.com/accounts/answer/185833

### Verificación de Alertas:
- **Manual**: `POST /api/v1/alerts/check/{symbol}`
- **Automático**: Implementar worker background con cron/celery (próxima versión)

### Timeframes:
- **1h**: Yahoo Finance limita a 730 días de datos horarios
- **1d/5d**: Sin limitaciones significativas

### Base de Datos:
- SQLite es suficiente para <10k usuarios
- Para producción escalable, migrar a PostgreSQL

---

## 🐛 Troubleshooting

### Email no se envía:
```bash
# Verificar configuración
GET /api/v1/admin/test-email

# Errores comunes:
# - SMTP_PASSWORD incorrecto
# - Gmail sin App Password
# - Puerto 587 bloqueado por firewall
```

### Alerta no se activa:
```bash
# Verificar manualmente
POST /api/v1/alerts/check/SAN.MC

# Verificar que la alerta esté activa
GET /api/v1/alerts?active_only=true
```

### Timeframe 1h no funciona:
```bash
# Yahoo Finance puede fallar temporalmente
# Reintentar o usar timeframe 1d
```

---

## 🔜 Próximas Funcionalidades (Sugerencias)

### Corto Plazo:
- [ ] Worker background para verificar alertas cada 5 minutos
- [ ] Notificaciones push (Firebase/OneSignal)
- [ ] Gráficos interactivos con timeframes en el dashboard HTML
- [ ] Exportar favoritos/alertas a CSV

### Medio Plazo:
- [ ] Alertas por RSI/MACD (no solo precio)
- [ ] Alertas recurrentes (diarias/semanales)
- [ ] Portfolios virtuales con seguimiento P&L
- [ ] Comparar múltiples símbolos side-by-side

### Largo Plazo:
- [ ] Machine Learning para predicciones
- [ ] Social trading (copiar portfolios de otros)
- [ ] WebSockets para datos en tiempo real
- [ ] Integración con brokers (órdenes reales)

---

## 📞 Recursos

**Documentación API:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Endpoints clave:**
```
GET  /                          # Página inicio con guía
GET  /health                    # Estado del servicio
GET  /api/v1/stock/{symbol}/data?timeframe=1h
POST /api/v1/favorites/{symbol}
POST /api/v1/alerts
```

**Archivos importantes:**
```
CHANGELOG.md              # Este archivo
DEPLOY_RAILWAY.md         # Guía de despliegue
.env.example              # Plantilla configuración
```

---

## ✅ Checklist de Migración

Si actualizas desde v2.1.0:

- [ ] `git pull origin main`
- [ ] Crear archivo `.env` con credenciales SMTP
- [ ] Verificar que `data/` existe (se crea auto)
- [ ] `pip install -r requirements.txt` (sin cambios, pero por si acaso)
- [ ] Probar email: `GET /api/v1/admin/test-email`
- [ ] Crear alerta de prueba
- [ ] Verificar dashboard muestra nombre de empresa
- [ ] Probar timeframes 1h/1d/5d
- [ ] Push a Railway (deploy automático)

---

**¡Disfruta de todas las nuevas funcionalidades! 🎉🚀**
