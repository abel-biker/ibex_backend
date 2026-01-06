# 🚀 Guía de Despliegue en Railway

## Actualizar tu app en Railway

### Opción 1: Desde GitHub (Recomendada)

Si tu proyecto está conectado a GitHub, Railway detecta cambios automáticamente:

```powershell
# 1. Commitear cambios
git add .
git commit -m "✨ Mejoras v2.1.0: Caché, validaciones, mejor UX"
git push origin main

# 2. Railway despliega automáticamente en ~2-3 minutos
```

### Opción 2: Railway CLI

```powershell
# Instalar Railway CLI (solo primera vez)
npm install -g @railway/cli

# Login
railway login

# Desplegar
railway up
```

---

## ✅ Verificación Post-Despliegue

### 1. Verificar salud del servicio
```
https://web-production-4c740.up.railway.app/health
```
Debe responder:
```json
{
  "status": "healthy",
  "api": "IBEX 35 Trading API",
  "version": "2.0.0",
  "timestamp": "2026-01-06 ...",
  "total_symbols": 35
}
```

### 2. Probar página de inicio
```
https://web-production-4c740.up.railway.app/
```
Debe mostrar HTML con lista de símbolos.

### 3. Probar endpoint corregido
**ANTES fallaba:**
```
https://web-production-4c740.up.railway.app/dashboard/BTC
```
**AHORA debe mostrar:** Página HTML de error con lista de símbolos válidos.

**Prueba con símbolo válido:**
```
https://web-production-4c740.up.railway.app/dashboard/SAN.MC?limit=30
```

### 4. Verificar caché funciona
```bash
# Primera carga (lenta)
curl -w "\nTiempo: %{time_total}s\n" \
  https://web-production-4c740.up.railway.app/api/v1/ibex35/ranking?limit=5

# Segunda carga (rápida - debe ser <1s)
curl -w "\nTiempo: %{time_total}s\n" \
  https://web-production-4c740.up.railway.app/api/v1/ibex35/ranking?limit=5
```

---

## 🔧 Configuración Railway

### Variables de Entorno (Opcional)

Si quieres añadir configuración adicional:

**En Railway Dashboard → Variables:**
```bash
PYTHONUNBUFFERED=1
PORT=8000
```

### Procfile Existente
Tu `Procfile` actual debería funcionar:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Si no existe o da problemas, créalo con:
```
web: uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

---

## 📊 Monitoreo

### Logs en tiempo real
```powershell
# Con Railway CLI
railway logs

# O ver en dashboard:
# https://railway.app/project/<tu-proyecto>/deployments
```

### Métricas clave a observar:

1. **Tiempo de respuesta `/ranking`**:
   - Primera carga: 2-5s (normal)
   - Cargas siguientes: <1s (caché)
   
2. **Errores**:
   - Debe ser 0 en `/dashboard/BTC` (ahora es 404 controlado)
   - Logs claros para debugging

3. **Uso de memoria**:
   - Caché usa ~50-100MB (aceptable)
   - Si crece mucho, limpiar con `/api/v1/admin/cache/clear`

---

## 🐛 Troubleshooting

### Problema: "ModuleNotFoundError: No module named 'app.utils'"

**Solución**: Asegúrate que Railway detecta `app/utils/__init__.py`
```powershell
# Verificar archivos
git ls-files app/utils/

# Debe mostrar:
# app/utils/__init__.py
# app/utils/cache.py
```

### Problema: Caché no funciona

**Diagnóstico**:
```bash
# Ver stats
curl https://web-production-4c740.up.railway.app/api/v1/admin/cache/stats

# Limpiar caché
curl -X POST https://web-production-4c740.up.railway.app/api/v1/admin/cache/clear
```

### Problema: Errores 500 después de despliegue

**Revisar logs**:
```powershell
railway logs --tail 100
```

**Causas comunes**:
- Dependencia faltante en `requirements.txt`
- Puerto incorrecto (debe usar `$PORT` de Railway)
- Imports incorrectos

---

## 🔄 Rollback (Si algo sale mal)

### En Railway Dashboard:
1. Ve a **Deployments**
2. Encuentra el deploy anterior que funcionaba
3. Click en **"..."** → **"Redeploy"**

### Desde CLI:
```powershell
# Ver deployments
railway deployments

# Rollback al anterior
railway rollback
```

---

## 📱 Integración con App Android

### Actualizar URL base en tu app:

**En tu `android_example.kt` o donde definas Retrofit:**

```kotlin
private const val BASE_URL = "https://web-production-4c740.up.railway.app/"

val retrofit = Retrofit.Builder()
    .baseUrl(BASE_URL)
    .addConverterFactory(GsonConverterFactory.create())
    .build()
```

### Endpoints listos para usar:

```kotlin
// Ranking
GET /api/v1/ibex35/ranking?limit=10

// Score individual
GET /api/v1/stock/SAN.MC/score

// Señales de trading
GET /api/v1/stock/BBVA.MC/signals?strategy=ensemble

// Backtest
GET /api/v1/stock/ITX.MC/backtest?strategy=ensemble
```

---

## 🎯 Checklist Final

Antes de considerar el deploy exitoso:

- [ ] `/health` responde "healthy"
- [ ] `/` muestra HTML con lista de símbolos
- [ ] `/dashboard/BTC` muestra error amigable (no 500)
- [ ] `/dashboard/SAN.MC` muestra gráficos correctamente
- [ ] `/api/v1/ibex35/ranking?limit=5` es rápido en 2ª carga
- [ ] `/api/v1/admin/cache/stats` responde
- [ ] Logs no muestran errores críticos
- [ ] Documentación en `/docs` funciona

---

## 🆘 Soporte Adicional

Si encuentras problemas:

1. **Revisa logs primero**: `railway logs`
2. **Prueba localmente**: `uvicorn app.main:app --reload`
3. **Limpia caché**: `POST /api/v1/admin/cache/clear`
4. **Rollback si es crítico**: Ver sección arriba

---

## 🚀 Siguientes Mejoras

Una vez estable en Railway:

1. **Dominio personalizado**: `trading.tudominio.com`
2. **SSL/HTTPS**: Railway lo provee gratis
3. **Rate limiting**: Prevenir spam
4. **Autenticación**: API keys para control de acceso
5. **Redis**: Para caché distribuido si escalas

---

**¡Listo para desplegar! 🎉**
