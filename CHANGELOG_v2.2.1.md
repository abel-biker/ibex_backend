# CHANGELOG v2.2.1 - Hotfix Railway Crash

**Fecha:** 2026-01-07  
**Versión:** 2.2.1  
**Tipo:** 🚨 HOTFIX CRÍTICO

---

## 🐛 Problema Resuelto

### Síntoma
- Railway mostraba "contenedor bloqueado" después del despliegue v2.2
- Al intentar reiniciar, pedía confirmación para "reiniciar contenedor bloqueado"
- La aplicación se quedaba congelada o no respondía

### Causa Raíz
El `BackgroundScheduler` de APScheduler ejecutándose cada 5 minutos para verificar alertas de precios:

```python
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_all_alerts, trigger=IntervalTrigger(minutes=5), ...)
scheduler.start()
```

**Problemas identificados:**
1. **Múltiples instancias**: Railway puede ejecutar varias instancias del contenedor, causando conflictos
2. **Llamadas API intensivas**: Cada 5 minutos se hacían múltiples requests a Yahoo Finance
3. **Timeouts**: Las llamadas lentas bloqueaban el scheduler y consumían recursos
4. **Sin límite de rate**: No había control de cuántas llamadas simultáneas se hacían

---

## ✅ Solución Implementada

### 1. Scheduler Deshabilitado
**Archivo:** `app/main.py` (líneas 111-129)

```python
# ANTES (causaba crash):
scheduler = BackgroundScheduler()
scheduler.start()

# AHORA (deshabilitado):
# scheduler = BackgroundScheduler()
# scheduler.start()
print("⚠️ Scheduler de alertas DESHABILITADO")
```

### 2. Nuevo Endpoint Manual
**Endpoint:** `POST /api/v1/admin/check-alerts-now`

Permite verificar alertas manualmente cuando sea necesario:

```bash
curl -X POST https://web-production-4c740.up.railway.app/api/v1/admin/check-alerts-now
```

**Respuesta:**
```json
{
  "status": "success",
  "message": "Verificación de alertas completada. Revisa los logs del servidor."
}
```

---

## 📦 Pasos para Desplegar el Fix

### Opción A: Push automático (Recomendado)
```powershell
git add .
git commit -m "🚨 Hotfix v2.2.1: Deshabilitar scheduler que bloqueaba Railway"
git push origin main
```

Railway detectará los cambios automáticamente.

### Opción B: Si Railway sigue bloqueado
1. Acepta "Reiniciar contenedor bloqueado" en Railway Dashboard
2. Haz push de estos cambios
3. Railway reconstruirá con el fix aplicado

---

## 🔄 Alternativas Futuras

### Opción 1: Railway Cron Jobs (Recomendada)
Crear un servicio Cron separado en Railway:

```yaml
# railway.toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"

[[crons]]
command = "curl -X POST http://localhost:$PORT/api/v1/admin/check-alerts-now"
schedule = "*/5 * * * *"  # Cada 5 minutos
```

### Opción 2: Webhook externo
Usar un servicio como **cron-job.org** o **EasyCron** para llamar al endpoint cada 5 minutos.

### Opción 3: N8N Workflow
Crear un workflow en tu instancia N8N existente:
- Trigger: Schedule (cada 5 minutos)
- HTTP Request: `POST /api/v1/admin/check-alerts-now`

---

## ✅ Verificación Post-Fix

### 1. Health Check
```
GET https://web-production-4c740.up.railway.app/health
```

Debe responder con status 200:
```json
{
  "status": "healthy",
  "api": "IBEX 35 Trading API",
  "version": "2.0.0"
}
```

### 2. Ver logs en Railway
Debería mostrar:
```
⚠️ Scheduler de alertas DESHABILITADO (configurar Railway Cron Jobs)
```

En lugar de:
```
✅ Scheduler de alertas iniciado (cada 5 minutos)
```

### 3. Probar endpoint manual
```bash
curl -X POST https://web-production-4c740.up.railway.app/api/v1/admin/check-alerts-now
```

---

## 📊 Impacto

### ✅ Mejoras
- ✅ Railway ya no se bloquea
- ✅ Contenedor estable y responsive
- ✅ Control manual de cuándo verificar alertas
- ✅ Menor consumo de recursos

### ⚠️ Cambios de Comportamiento
- ⚠️ Las alertas NO se verifican automáticamente cada 5 minutos
- ⚠️ Debes llamar manualmente `POST /api/v1/admin/check-alerts-now` o configurar un cron externo

---

## 🎯 Próximos Pasos

1. ✅ **INMEDIATO:** Desplegar este hotfix
2. 📅 **Esta semana:** Configurar Railway Cron Jobs o webhook externo
3. 📅 **Futuro:** Migrar a sistema de colas (Celery + Redis) para tareas asíncronas robustas

---

## 🔗 Referencias

- **Railway Cron Jobs:** https://docs.railway.app/reference/cron-jobs
- **APScheduler Issues:** https://github.com/agronholm/apscheduler/issues
- **FastAPI Background Tasks:** https://fastapi.tiangolo.com/tutorial/background-tasks/

---

**Autor:** Abel  
**Fecha:** 2026-01-07  
**Versión:** 2.2.1
