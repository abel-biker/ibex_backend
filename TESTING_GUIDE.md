# 🧪 Guía Rápida de Pruebas - v2.2.0

## 📋 Checklist de Pruebas

### 1. Verificar que el servidor arranca sin errores

```powershell
# Activar entorno
.\.venv\Scripts\Activate.ps1

# Ejecutar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Debe mostrar:**
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

### 2. ✅ Probar Nivel de Confianza Dinámico

```bash
# Ver score de Santander
http://localhost:8000/api/v1/stock/SAN.MC/score
```

**Buscar en respuesta:**
```json
{
  "confidence": "HIGH (85%)"  // ← Ya no es fijo 50%!
}
```

---

### 3. ⏰ Probar Timeframes (1h / 1d / 5d)

```bash
# Vista horaria (últimos 7 días)
http://localhost:8000/api/v1/stock/SAN.MC/data?timeframe=1h

# Vista diaria (6 meses)
http://localhost:8000/api/v1/stock/SAN.MC/data?timeframe=1d

# Vista 5 días
http://localhost:8000/api/v1/stock/SAN.MC/data?timeframe=5d
```

**Verificar:**
- `timeframe` en respuesta coincide con el solicitado
- `data_points` varía: ~168 para 1h (7 días * 24h), pocos para 5d
- Campo `fecha` tiene formato diferente:
  - 1h: "2026-01-06 14:00:00"
  - 1d: "2026-01-06"

---

### 4. 📊 Dashboard con Nombre de Empresa

```bash
http://localhost:8000/dashboard/SAN.MC
```

**Debe mostrar en el título:**
```
📊 Banco Santander
    SAN.MC · Financiero
    Última actualización: 06/01/2026
```

Prueba con otros:
- http://localhost:8000/dashboard/BBVA.MC → "BBVA"
- http://localhost:8000/dashboard/ITX.MC → "Inditex"

---

### 5. ⭐ Sistema de Favoritos

**Añadir favorito:**
```bash
curl -X POST "http://localhost:8000/api/v1/favorites/SAN.MC"
```

**Respuesta:**
```json
{
  "status": "added",
  "symbol": "SAN.MC",
  "name": "Banco Santander",
  "sector": "Financiero",
  "id": 1
}
```

**Añadir más:**
```bash
curl -X POST "http://localhost:8000/api/v1/favorites/BBVA.MC"
curl -X POST "http://localhost:8000/api/v1/favorites/ITX.MC"
```

**Listar favoritos:**
```bash
http://localhost:8000/api/v1/favorites
```

**Debe mostrar:**
```json
{
  "total": 3,
  "favorites": [
    {"id": 3, "symbol": "ITX.MC", "name": "Inditex", ...},
    {"id": 2, "symbol": "BBVA.MC", "name": "BBVA", ...},
    {"id": 1, "symbol": "SAN.MC", "name": "Banco Santander", ...}
  ]
}
```

**Eliminar favorito:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/favorites/BBVA.MC"
```

---

### 6. 🔔 Sistema de Alertas (Sin Email primero)

**Crear alerta con notificación "popup" (no requiere email):**
```bash
curl -X POST "http://localhost:8000/api/v1/alerts?symbol=SAN.MC&condition=above&target_price=4.50&notification_type=popup"
```

**Respuesta:**
```json
{
  "id": 1,
  "symbol": "SAN.MC",
  "name": "Banco Santander",
  "condition": "above",
  "target_price": 4.5,
  "notification_type": "popup",
  "status": "created"
}
```

**Listar alertas:**
```bash
http://localhost:8000/api/v1/alerts
```

**Verificar alerta manualmente:**
```bash
curl -X POST "http://localhost:8000/api/v1/alerts/check/SAN.MC"
```

**Debe retornar:**
```json
{
  "symbol": "SAN.MC",
  "current_price": 4.23,  // Precio actual
  "alerts_triggered": 0,   // 0 si no se activó, 1 si sí
  "triggered_alerts": [],
  "notifications_sent": []
}
```

---

### 7. 📧 Configurar y Probar Email (Opcional)

**7.1 Crear archivo `.env`:**
```bash
cp .env.example .env
```

**7.2 Editar `.env` con tus credenciales:**

**Para Gmail:**
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx
FROM_EMAIL=tu-email@gmail.com
```

**Obtener Gmail App Password:**
1. Ve a https://myaccount.google.com/apppasswords
2. Selecciona "Mail" y "Other (Custom name)"
3. Copia la contraseña de 16 caracteres
4. Pégala en `SMTP_PASSWORD` (sin espacios)

**7.3 Reiniciar servidor:**
```powershell
# Ctrl+C para detener
# Volver a ejecutar
uvicorn app.main:app --reload
```

**7.4 Probar configuración:**
```bash
http://localhost:8000/api/v1/admin/test-email
```

**Debe retornar:**
```json
{
  "status": "ok",
  "message": "Conexión SMTP exitosa a smtp.gmail.com:587",
  "smtp_user": "tu-email@gmail.com"
}
```

**7.5 Crear alerta con email:**
```bash
curl -X POST "http://localhost:8000/api/v1/alerts?symbol=SAN.MC&condition=below&target_price=4.20&notification_type=email&email=tu-email@gmail.com"
```

**7.6 Simular activación:**
```bash
# Si el precio actual es < 4.20, la alerta se activará
curl -X POST "http://localhost:8000/api/v1/alerts/check/SAN.MC"
```

**Verificar en tu bandeja de entrada** 📧

---

### 8. 🏠 Página de Inicio

```bash
http://localhost:8000/
```

**Debe mostrar:**
- Lista de 35 símbolos del IBEX clickables
- Enlaces a documentación
- Ejemplos de endpoints
- Estado del servicio

---

## 🐛 Errores Comunes

### Error: ModuleNotFoundError: No module named 'app.models'
```powershell
# Verificar que existe __init__.py
ls app/models/__init__.py

# Si no existe, crear:
echo "" > app/models/__init__.py
```

### Error: sqlite3.OperationalError
```powershell
# Crear directorio data/
mkdir data
```
La base de datos se creará automáticamente.

### Error: SMTPAuthenticationError
```
# Gmail requiere App Password, no tu contraseña normal
# Verifica:
1. 2FA activado en tu cuenta Google
2. App Password generado correctamente
3. Sin espacios en SMTP_PASSWORD
```

### Timeframe 1h retorna poco o nada
```
Yahoo Finance puede limitar datos horarios antiguos.
Es normal, solo retorna últimos 7 días.
```

---

## 📊 Comparación Antes/Después

### Confianza:
```bash
# ANTES
GET /api/v1/stock/SAN.MC/score
# → "confidence": "MEDIUM"  (siempre igual)

# AHORA
GET /api/v1/stock/SAN.MC/score
# → "confidence": "HIGH (87%)"  (dinámico y preciso)
```

### Dashboard:
```bash
# ANTES
http://localhost:8000/dashboard/SAN.MC
# Título: "📊 SAN.MC"

# AHORA
http://localhost:8000/dashboard/SAN.MC
# Título: "📊 Banco Santander
#         SAN.MC · Financiero"
```

### Funcionalidades nuevas:
```bash
# ANTES: No existían
# AHORA:
- /api/v1/favorites
- /api/v1/alerts
- /api/v1/stock/{symbol}/data?timeframe=1h
```

---

## ✅ Checklist Final

Antes de hacer commit:

- [ ] Servidor arranca sin errores
- [ ] Confianza muestra porcentaje (ej: 85%)
- [ ] Timeframe 1h retorna datos con timestamp de hora
- [ ] Dashboard muestra "Banco Santander", no solo "SAN.MC"
- [ ] Favoritos: añadir/listar/eliminar funciona
- [ ] Alertas: crear/listar funciona (sin email)
- [ ] (Opcional) Email configurado y alerta enviada
- [ ] Página inicio (/) muestra HTML con símbolos
- [ ] Base de datos `data/user_data.db` creada

---

## 🚀 Deploy a Railway

Cuando todo funcione localmente:

```powershell
git add .
git commit -m "🎉 v2.2.0: Confianza dinámica, timeframes, favoritos, alertas con email"
git push origin main
```

Railway desplegará automáticamente en ~3 minutos.

**Verificar en Railway:**
```bash
# Cambiar localhost por tu URL
https://web-production-4c740.up.railway.app/health
https://web-production-4c740.up.railway.app/api/v1/stock/SAN.MC/score
```

---

## 📱 Próximos Pasos: App Android

Con estas mejoras, tu app Android puede tener:

1. **Selector de timeframe**: Tabs "1H / 1D / 5D"
2. **Botón estrella**: Añadir/quitar favoritos
3. **Pestaña Favoritos**: RecyclerView de favoritos
4. **Diálogo de alerta**: Input precio + email
5. **Notificaciones push**: Cuando se activa alerta

¿Quieres que te cree el proyecto Android completo con UI lista para usar? 🚀
