# CHANGELOG v2.3.0 - Feature: Favoritos e Historial

**Fecha:** 2026-01-07  
**Versión:** 2.3.0  
**Tipo:** ✨ FEATURE RELEASE

---

## 🎉 Nuevas Funcionalidades

### ⭐ Sistema de Favoritos

Guarda tus acciones favoritas para acceso rápido.

**Características:**
- Máximo **10 favoritos** por usuario
- Auto-gestiona el límite: elimina el más antiguo si añades un 11º
- Persistencia en SQLite (sobrevive a reinicios)
- Enriquecido con nombre de empresa y sector

**Endpoints:**
```bash
POST   /api/v1/favorites/{symbol}      # Añadir favorito
GET    /api/v1/favorites              # Ver todos
DELETE /api/v1/favorites/{symbol}      # Eliminar
```

**Ejemplo de uso:**
```bash
# Añadir Santander a favoritos
curl -X POST https://web-production-4c740.up.railway.app/api/v1/favorites/SAN.MC

# Ver mis favoritos
curl https://web-production-4c740.up.railway.app/api/v1/favorites
```

---

### 📜 Historial de Búsquedas

Mantiene un registro de los últimos símbolos consultados.

**Características:**
- Últimos **10 símbolos únicos** consultados
- Se añade **automáticamente** al visitar dashboard o consultar scores
- Muestra la última fecha de consulta por símbolo
- No duplica símbolos repetidos (solo actualiza fecha)

**Endpoints:**
```bash
GET    /api/v1/history     # Ver historial
DELETE /api/v1/history     # Limpiar todo
```

**Auto-tracking en:**
- `GET /dashboard/{symbol}`
- `GET /api/v1/stock/{symbol}/score`

---

## 🛠️ Cambios Técnicos

### Base de Datos
**Nueva tabla:** `search_history`
```sql
CREATE TABLE search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT 'default',
    symbol TEXT NOT NULL,
    searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Índices añadidos:**
```sql
CREATE INDEX idx_history_user ON search_history(user_id);
```

### Funciones Nuevas (user_data.py)
- `add_to_history(symbol, user_id)` - Añade símbolo al historial
- `get_search_history(user_id)` - Obtiene últimos 10 símbolos únicos
- `clear_search_history(user_id)` - Limpia historial completo

### Mejoras en Favoritos
- `add_favorite()` ahora gestiona automáticamente el límite de 10
- Elimina el favorito más antiguo si se supera el límite

---

## 📱 Impacto en Frontend/Mobile

### Nuevas Capacidades

1. **Campo de búsqueda inteligente:**
   ```javascript
   // Mostrar favoritos + historial al abrir buscador
   const [favorites, history] = await Promise.all([
     api.get('/api/v1/favorites'),
     api.get('/api/v1/history')
   ]);
   ```

2. **Botón de estrella en cada acción:**
   ```javascript
   // Toggle favorito
   await api.post(`/api/v1/favorites/${symbol}`);
   // o
   await api.delete(`/api/v1/favorites/${symbol}`);
   ```

3. **Pantalla de favoritos:**
   ```javascript
   // Listar todos los favoritos con detalles
   const { favorites } = await api.get('/api/v1/favorites');
   ```

### Experiencia de Usuario

**Antes (v2.2):**
```
Usuario busca "SAN.MC" → Escribe todo manualmente cada vez
```

**Ahora (v2.3):**
```
Usuario abre buscador → Ve favoritos ⭐ + historial 📜
↓
Tap en "SAN.MC" → Acceso instantáneo
↓
Puede añadir a favoritos con un botón
```

---

## 📊 Ejemplos de Respuestas

### GET /api/v1/favorites
```json
{
  "total": 3,
  "favorites": [
    {
      "id": 5,
      "symbol": "SAN.MC",
      "added_at": "2026-01-07 15:30:00",
      "name": "Banco Santander",
      "sector": "Bancario"
    },
    {
      "id": 4,
      "symbol": "BBVA.MC",
      "added_at": "2026-01-07 14:20:00",
      "name": "BBVA",
      "sector": "Bancario"
    },
    {
      "id": 2,
      "symbol": "TEF.MC",
      "added_at": "2026-01-07 10:15:00",
      "name": "Telefónica",
      "sector": "Telecomunicaciones"
    }
  ]
}
```

### GET /api/v1/history
```json
{
  "total": 5,
  "history": [
    {
      "symbol": "BBVA.MC",
      "last_searched": "2026-01-07 15:45:32",
      "name": "BBVA",
      "sector": "Bancario"
    },
    {
      "symbol": "TEF.MC",
      "last_searched": "2026-01-07 15:40:15",
      "name": "Telefónica",
      "sector": "Telecomunicaciones"
    },
    {
      "symbol": "ITX.MC",
      "last_searched": "2026-01-07 15:35:00",
      "name": "Inditex",
      "sector": "Textil"
    }
  ]
}
```

---

## 🔧 Migración y Compatibilidad

### Base de Datos Existente
La tabla `search_history` se crea automáticamente en el primer uso gracias a:
```python
def init_db():
    # Crea tabla si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_history (...)
    """)
```

**No requiere migración manual** - compatible con bases de datos existentes.

### APIs Anteriores
Todos los endpoints anteriores **siguen funcionando igual**. Esta es una release aditiva, sin breaking changes.

---

## 📝 Documentación Actualizada

- **README.md**: Sección de favoritos e historial en endpoints principales
- **FRONTEND_GUIDE.md**: Guía completa con ejemplos de código JS/Kotlin
- **Swagger UI**: Documentación interactiva actualizada en `/docs`

---

## 🎯 Próximos Pasos

### Mejoras Planificadas (v2.4)

1. **Sincronización multi-dispositivo:**
   - Usar `user_id` único por usuario
   - Sincronizar favoritos entre móvil y web

2. **Ordenar favoritos:**
   - Drag & drop para reordenar
   - Endpoint PATCH para cambiar orden

3. **Exportar/Importar:**
   - Exportar favoritos a JSON
   - Importar desde archivo

4. **Estadísticas de historial:**
   - Símbolos más consultados
   - Tendencias de búsqueda

---

## 🐛 Bugs Conocidos

Ninguno reportado hasta el momento.

---

## 🔗 Enlaces

- **Producción:** https://web-production-4c740.up.railway.app
- **Docs interactivas:** https://web-production-4c740.up.railway.app/docs
- **GitHub:** https://github.com/abel-biker/ibex_backend

---

**Autor:** Abel  
**Fecha:** 2026-01-07  
**Versión:** 2.3.0
