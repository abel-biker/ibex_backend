# 📱 Guía para Desarrolladores Frontend/Mobile

**Versión API:** 2.3.1  
**Base URL Producción:** `https://web-production-4c740.up.railway.app`  
**Documentación Interactiva:** `/docs`

---

## 🔐 Sistema de Identificación (Sin Login)

La API usa **identificación anónima basada en localStorage** para personalizar favoritos e historial sin requerir login.

### ¿Cómo funciona?

1. **Primera visita:** Se genera un UUID único: `user_1736284530_abc123xyz`
2. **Se guarda en localStorage:** Persiste entre sesiones del navegador
3. **Cada request incluye el user_id:** Los datos son personales por navegador
4. **Si borran localStorage/cookies:** Se genera un nuevo ID (se pierden favoritos, comportamiento esperado)

### Implementación JavaScript

```javascript
// Generar o recuperar User ID único
function getUserId() {
  let userId = localStorage.getItem('ibex_user_id');
  if (!userId) {
    userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('ibex_user_id', userId);
    console.log('✨ Nuevo usuario creado:', userId);
  }
  return userId;
}

const USER_ID = getUserId();

// Usar en todas las llamadas
fetch(`/api/v1/favorites?user_id=${USER_ID}`)
```

### Implementación Kotlin (Android)

```kotlin
object UserManager {
    private const val PREFS_NAME = "ibex_prefs"
    private const val KEY_USER_ID = "user_id"
    
    fun getUserId(context: Context): String {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        var userId = prefs.getString(KEY_USER_ID, null)
        
        if (userId == null) {
            userId = "user_${System.currentTimeMillis()}_${UUID.randomUUID().toString().take(9)}"
            prefs.edit().putString(KEY_USER_ID, userId).apply()
            Log.d("UserManager", "✨ Nuevo usuario: $userId")
        }
        
        return userId
    }
}

// Usar en toda la app
val userId = UserManager.getUserId(context)
```

---

## 🚀 Quick Start

### Configuración Base

```javascript
// JavaScript/TypeScript
const API_BASE = 'https://web-production-4c740.up.railway.app';

// Obtener o generar User ID
function getUserId() {
  let userId = localStorage.getItem('ibex_user_id');
  if (!userId) {
    userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('ibex_user_id', userId);
  }
  return userId;
}

const USER_ID = getUserId();

async function apiGet(endpoint) {
  const response = await fetch(`${API_BASE}${endpoint}`);
  return response.json();
}

async function apiPost(endpoint, body = {}) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  return response.json();
}
```

```kotlin
// Kotlin (Android)
object ApiClient {
    private const val BASE_URL = "https://web-production-4c740.up.railway.app"
    
    private fun getUserId(context: Context): String {
        return UserManager.getUserId(context)
    }
    
    suspend fun getFavorites(context: Context): FavoritesResponse {
        val userId = getUserId(context)
        return ktorClient.get("$BASE_URL/api/v1/favorites?user_id=$userId")
    }
}
```

---

## ⭐ Favoritos (Máximo 10)

### Añadir a Favoritos

```http
POST /api/v1/favorites/{symbol}?user_id=default
```

**Ejemplo:**
```javascript
async function addFavorite(symbol) {
  const response = await apiPost(`/api/v1/favorites/${symbol}?user_id=${USER_ID}`);
  
  if (response.status === 'added') {
    console.log(`✅ ${symbol} añadido a favoritos`);
  } else if (response.status === 'already_exists') {
    console.log(`ℹ️ ${symbol} ya está en favoritos`);
  }
  
  return response;
}

// Uso
await addFavorite('SAN.MC');
```

**Respuesta:**
```json
{
  "status": "added",
  "symbol": "SAN.MC",
  "id": 5,
  "name": "Banco Santander",
  "sector": "Bancario"
}
```

**Límite de 10:** Si ya hay 10 favoritos, se elimina automáticamente el más antiguo.

---

### Ver Todos los Favoritos

```http
GET /api/v1/favorites?user_id=default
```

**Ejemplo:**
```javascript
async function getFavorites() {
  const data = await apiGet(`/api/v1/favorites?user_id=${USER_ID}`);
  
  console.log(`Tienes ${data.total} favoritos`);
  
  data.favorites.forEach(fav => {
    console.log(`⭐ ${fav.symbol} - ${fav.name}`);
  });
  
  return data.favorites;
}
```

**Respuesta:**
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
    }
  ]
}
```

---

### Eliminar Favorito

```http
DELETE /api/v1/favorites/{symbol}?user_id=default
```

**Ejemplo:**
```javascript
async function removeFavorite(symbol) {
  const response = await fetch(
    `${API_BASE}/api/v1/favorites/${symbol}?user_id=${USER_ID}`,
    { method: 'DELETE' }
  );
  
  const data = await response.json();
  
  if (data.status === 'removed') {
    console.log(`🗑️ ${symbol} eliminado de favoritos`);
  }
  
  return data;
}
```

**Respuesta:**
```json
{
  "status": "removed",
  "symbol": "SAN.MC"
}
```

---

## 📜 Historial de Búsquedas (Últimos 10 Únicos)

### Ver Historial

```http
GET /api/v1/history?user_id=default
```

**Ejemplo:**
```javascript
async function getHistory() {
  const data = await apiGet(`/api/v1/history?user_id=${USER_ID}`);
  
  console.log(`Historial de ${data.total} símbolos`);
  
  data.history.forEach(item => {
    console.log(`📜 ${item.symbol} - Última búsqueda: ${item.last_searched}`);
  });
  
  return data.history;
}
```

**Respuesta:**
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
    }
  ]
}
```

**⚡ Automático:** El historial se añade automáticamente cuando consultas:
- `GET /dashboard/{symbol}`
- `GET /api/v1/stock/{symbol}/score`

No necesitas llamar manualmente ningún endpoint para añadir al historial.

---

### Limpiar Historial

```http
DELETE /api/v1/history?user_id=default
```

**Ejemplo:**
```javascript
async function clearHistory() {
  const response = await fetch(
    `${API_BASE}/api/v1/history?user_id=${USER_ID}`,
    { method: 'DELETE' }
  );
  
  const data = await response.json();
  console.log(`🗑️ ${data.deleted_count} registros eliminados`);
  
  return data;
}
```

**Respuesta:**
```json
{
  "status": "cleared",
  "deleted_count": 8
}
```

---

## 🎨 Implementación UI Recomendada

### Campo de Búsqueda con Sugerencias

```javascript
// Componente de Búsqueda (React/Vue/Angular)
async function loadSearchSuggestions() {
  const [favorites, history] = await Promise.all([
    getFavorites(),
    getHistory()
  ]);
  
  return {
    favorites: favorites.map(f => ({
      ...f,
      type: 'favorite',
      icon: '⭐'
    })),
    history: history.map(h => ({
      ...h,
      type: 'history',
      icon: '📜'
    }))
  };
}

// Renderizar sugerencias
function renderSuggestions(suggestions) {
  return `
    <div class="search-suggestions">
      ${suggestions.favorites.length > 0 ? `
        <div class="section">
          <h3>⭐ Favoritos</h3>
          ${suggestions.favorites.map(fav => `
            <div class="suggestion-item" data-symbol="${fav.symbol}">
              <span class="symbol">${fav.symbol}</span>
              <span class="name">${fav.name}</span>
            </div>
          `).join('')}
        </div>
      ` : ''}
      
      ${suggestions.history.length > 0 ? `
        <div class="section">
          <h3>📜 Historial Reciente</h3>
          ${suggestions.history.map(item => `
            <div class="suggestion-item" data-symbol="${item.symbol}">
              <span class="symbol">${item.symbol}</span>
              <span class="name">${item.name}</span>
            </div>
          `).join('')}
        </div>
      ` : ''}
    </div>
  `;
}
```

---

### Botón de Favorito en Detalle de Acción

```javascript
// Componente de botón estrella
class FavoriteButton {
  constructor(symbol) {
    this.symbol = symbol;
    this.isFavorite = false;
  }
  
  async init() {
    // Verificar si ya está en favoritos
    const favorites = await getFavorites();
    this.isFavorite = favorites.some(f => f.symbol === this.symbol);
    this.render();
  }
  
  async toggle() {
    if (this.isFavorite) {
      await removeFavorite(this.symbol);
      this.isFavorite = false;
    } else {
      await addFavorite(this.symbol);
      this.isFavorite = true;
    }
    this.render();
  }
  
  render() {
    const icon = this.isFavorite ? '⭐' : '☆';
    const text = this.isFavorite ? 'En favoritos' : 'Añadir a favoritos';
    return `<button onclick="toggleFavorite()">${icon} ${text}</button>`;
  }
}
```

---

### Pantalla de Favoritos

```kotlin
// Android Jetpack Compose
@Composable
fun FavoritesScreen() {
    val favorites by remember { mutableStateOf(listOf<Favorite>()) }
    
    LaunchedEffect(Unit) {
        favorites = apiClient.getFavorites().favorites
    }
    
    LazyColumn {
        items(favorites) { favorite ->
            FavoriteItem(
                symbol = favorite.symbol,
                name = favorite.name,
                sector = favorite.sector,
                onRemove = { 
                    apiClient.removeFavorite(favorite.symbol)
                    favorites = favorites.filter { it.id != favorite.id }
                }
            )
        }
    }
}
```

---

## 🔄 Flujo Completo de Usuario

### Ejemplo: Búsqueda y Consulta de Acción

```javascript
// 1. Usuario abre el buscador
async function onSearchFocused() {
  const suggestions = await loadSearchSuggestions();
  displaySuggestions(suggestions);
}

// 2. Usuario selecciona un símbolo (ej: "SAN.MC")
async function onSymbolSelected(symbol) {
  // El historial se añade automáticamente al consultar el score
  const score = await apiGet(`/api/v1/stock/${symbol}/score`);
  
  // Mostrar detalle de la acción
  displayStockDetails(score);
}

// 3. Usuario añade a favoritos
async function onAddToFavorites(symbol) {
  await addFavorite(symbol);
  showToast('✅ Añadido a favoritos');
}

// 4. Usuario navega a "Mis Favoritos"
async function onFavoritesScreen() {
  const favorites = await getFavorites();
  displayFavoritesList(favorites);
}
```

---

## 📊 Otros Endpoints Útiles

### Ranking IBEX 35
```http
GET /api/v1/ibex35/ranking?limit=35
```

### Score de una Acción
```http
GET /api/v1/stock/{symbol}/score
```

### Señales de Trading
```http
GET /api/v1/stock/{symbol}/signals?strategy=ensemble
```

### Dashboard HTML Completo
```http
GET /dashboard/{symbol}
```

---

## 🎯 Best Practices

### 1. **Gestión de Usuarios**
```javascript
// Generar ID único por usuario
const USER_ID = localStorage.getItem('user_id') || generateUserId();
localStorage.setItem('user_id', USER_ID);

function generateUserId() {
  return `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}
```

### 2. **Caché Local**
```javascript
// Cachear favoritos para offline
async function getFavoritesCached() {
  try {
    const favorites = await getFavorites();
    localStorage.setItem('favorites_cache', JSON.stringify(favorites));
    return favorites;
  } catch (error) {
    // Si hay error de red, usar caché
    return JSON.parse(localStorage.getItem('favorites_cache') || '[]');
  }
}
```

### 3. **Límite de Favoritos**
```javascript
// Mostrar mensaje cuando se alcance el límite
async function addFavoriteWithFeedback(symbol) {
  const currentFavorites = await getFavorites();
  
  if (currentFavorites.length >= 10) {
    showWarning('⚠️ Límite de 10 favoritos. Se eliminará el más antiguo.');
  }
  
  await addFavorite(symbol);
}
```

### 4. **Manejo de Errores**
```javascript
async function safeFetch(url) {
  try {
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    showError('No se pudo conectar con el servidor');
    return null;
  }
}
```

---

## 🔗 Enlaces Útiles

- **Documentación Interactiva:** https://web-production-4c740.up.railway.app/docs
- **Health Check:** https://web-production-4c740.up.railway.app/health
- **GitHub Repository:** https://github.com/abel-biker/ibex_backend

---

## 📝 Notas Importantes

1. **Persistencia:** Los favoritos e historial se guardan en SQLite y sobreviven a reinicios del servidor.

2. **User ID:** Usa `?user_id=default` o genera un ID único por usuario. Esto permite tener favoritos separados por usuario.

3. **Límites:**
   - Favoritos: 10 máximo (auto-elimina el más antiguo)
   - Historial: 10 símbolos únicos (mantiene los más recientes)

4. **Historial Automático:** No necesitas llamar ningún endpoint para añadir al historial. Se hace automáticamente en:
   - `/dashboard/{symbol}`
   - `/api/v1/stock/{symbol}/score`

5. **Offline:** Ambas funcionalidades usan SQLite local en el servidor, pero puedes implementar caché local en tu app para modo offline.

---

**¿Preguntas o sugerencias?** Abre un issue en GitHub o contacta al equipo de desarrollo.
