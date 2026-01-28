# 📱 IBEX 35 Trading - UI Android

Interfaz de usuario completa para la app Android del sistema de trading IBEX 35 con **Sistema Híbrido AI v2.3.0**.

## 📁 Archivos Incluidos

### Layouts XML
- **activity_main.xml** - Pantalla principal con ranking de empresas
  - AppBar con búsqueda
  - Chips de filtros por sector
  - RecyclerView de acciones
  - FAB para refrescar
  - Info del Sistema AI

- **item_stock.xml** - Card para cada empresa en el ranking
  - Nombre, símbolo, sector
  - Precio y cambio porcentual
  - Puntuación AI (0-10)
  - Señal ML (BUY/SELL/HOLD) con probabilidad
  - Nivel de confianza
  - Razón de la predicción
  - Icono de favorito

- **activity_stock_detail.xml** - Detalle completo de una acción
  - Header con precio destacado
  - Card de predicción AI
  - Desglose de 4 componentes AI:
    - 🤖 XGBoost ML (40%)
    - 📈 Prophet (20%)
    - 🔧 Danelfin (25%)
    - 📰 FinBERT (15%)
  - Indicadores técnicos (RSI, MACD, SMA)
  - Botones de acción (alertas, gráfico)

### Código Kotlin
- **MainActivity.kt** - Activity principal
  - Carga ranking del IBEX 35
  - Filtros por sector
  - Pull-to-refresh
  - Navegación a detalle

- **StockDetailActivity.kt** - Detalle de acción
  - Muestra todos los datos de IA
  - Componentes desglosados
  - Indicadores técnicos
  - Gestión de favoritos

- **StocksAdapter.kt** - Adapter del RecyclerView
  - Bind de datos de API
  - Colores dinámicos según score
  - Click handlers

- **android_example.kt** - Cliente API (ya existente)
  - Retrofit configurado
  - Modelos de datos actualizados para IA
  - Repository pattern

### Configuración
- **build.gradle** - Dependencias necesarias
  - Material Design 3
  - Retrofit + OkHttp
  - Coroutines
  - ViewBinding
  - RecyclerView
  - (Opcional) MPAndroidChart

## 🚀 Cómo Integrar en tu Proyecto

### 1. Copia los archivos

```
YourProject/
  app/
    src/
      main/
        java/com/example/ibex35trading/
          MainActivity.kt              ← Copia aquí
          StockDetailActivity.kt       ← Copia aquí
          adapters/
            StocksAdapter.kt           ← Copia aquí
          api/
            android_example.kt         ← Ya tienes este
        res/
          layout/
            activity_main.xml          ← Copia aquí
            item_stock.xml             ← Copia aquí
            activity_stock_detail.xml  ← Copia aquí
```

### 2. Actualiza `build.gradle`

Añade las dependencias del archivo `build.gradle` proporcionado.

### 3. Configura la URL de la API

En `android_example.kt` línea 169:

```kotlin
private const val BASE_URL = "https://web-production-4c740.up.railway.app"
```

**Para desarrollo local:**
```kotlin
private const val BASE_URL = "http://10.0.2.2:8000"  // Emulador
// o
private const val BASE_URL = "http://TU_IP_LOCAL:8000"  // Dispositivo físico
```

### 4. Añade permisos en `AndroidManifest.xml`

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

### 5. Añade las Activities en `AndroidManifest.xml`

```xml
<application ...>
    <activity
        android:name=".MainActivity"
        android:exported="true">
        <intent-filter>
            <action android:name="android.intent.action.MAIN" />
            <category android:name="android.intent.category.LAUNCHER" />
        </intent-filter>
    </activity>
    
    <activity
        android:name=".StockDetailActivity"
        android:parentActivityName=".MainActivity" />
</application>
```

### 6. Crea los drawables faltantes

**res/drawable/ic_refresh.xml:**
```xml
<vector android:height="24dp" android:tint="#FFFFFF"
    android:viewportHeight="24" android:viewportWidth="24"
    android:width="24dp" xmlns:android="http://schemas.android.com/apk/res/android">
    <path android:fillColor="@android:color/white" 
        android:pathData="M17.65,6.35C16.2,4.9 14.21,4 12,4c-4.42,0 -7.99,3.58 -7.99,8s3.57,8 7.99,8c3.73,0 6.84,-2.55 7.73,-6h-2.08c-0.82,2.33 -3.04,4 -5.65,4 -3.31,0 -6,-2.69 -6,-6s2.69,-6 6,-6c1.66,0 3.14,0.69 4.22,1.78L13,11h7V4l-2.35,2.35z"/>
</vector>
```

**res/drawable/ic_star_outline.xml:**
```xml
<vector android:height="24dp" android:tint="#FFB300"
    android:viewportHeight="24" android:viewportWidth="24"
    android:width="24dp" xmlns:android="http://schemas.android.com/apk/res/android">
    <path android:fillColor="@android:color/white" 
        android:pathData="M22,9.24l-7.19,-0.62L12,2 9.19,8.63 2,9.24l5.46,4.73L5.82,21 12,17.27 18.18,21l-1.63,-7.03L22,9.24zM12,15.4l-3.76,2.27 1,-4.28 -3.32,-2.88 4.38,-0.38L12,6.1l1.71,4.04 4.38,0.38 -3.32,2.88 1,4.28L12,15.4z"/>
</vector>
```

**res/drawable/ic_star_filled.xml:**
```xml
<vector android:height="24dp" android:tint="#FFB300"
    android:viewportHeight="24" android:viewportWidth="24"
    android:width="24dp" xmlns:android="http://schemas.android.com/apk/res/android">
    <path android:fillColor="@android:color/white" 
        android:pathData="M12,17.27L18.18,21l-1.64,-7.03L22,9.24l-7.19,-0.61L12,2 9.19,8.63 2,9.24l5.46,4.73L5.82,21z"/>
</vector>
```

**res/drawable/background_reason.xml:**
```xml
<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <solid android:color="#F5F5F5" />
    <corners android:radius="8dp" />
    <stroke android:color="#E0E0E0" android:width="1dp" />
</shape>
```

## 🎨 Colores del Score

Los scores se colorean automáticamente:

- **8.0 - 10.0**: 🟢 Verde fuerte (#4CAF50) - STRONG BUY
- **6.5 - 7.9**: 🟢 Verde claro (#8BC34A) - BUY
- **5.0 - 6.4**: 🟠 Naranja (#FF9800) - MODERATE BUY/HOLD
- **3.5 - 4.9**: 🟠 Naranja oscuro (#FF5722) - MODERATE SELL
- **0.0 - 3.4**: 🔴 Rojo (#F44336) - SELL

## 📊 Características de la UI

✅ **Material Design 3** - Diseño moderno y profesional  
✅ **Responsive** - Adaptado a diferentes tamaños de pantalla  
✅ **Dark Mode Ready** - Usa colores del tema del sistema  
✅ **Animaciones** - Transiciones suaves  
✅ **View Binding** - Sin `findViewById()`  
✅ **Coroutines** - Llamadas asíncronas eficientes  
✅ **DiffUtil** - Actualizaciones optimizadas del RecyclerView  

## 🧪 Prueba Rápida

### En Emulador:
```kotlin
// MainActivity.kt línea 169 de android_example.kt
private const val BASE_URL = "http://10.0.2.2:8000"
```

Asegúrate de que tu servidor local esté corriendo:
```powershell
uvicorn app.main:app --reload --port 8000
```

### En Dispositivo Físico:
```kotlin
// Obtén tu IP local con: ipconfig (Windows) o ifconfig (Mac/Linux)
private const val BASE_URL = "http://192.168.1.X:8000"
```

## 📝 Próximos Pasos

1. **Implementar gráficos** - Usar MPAndroidChart para mostrar histórico
2. **Sistema de alertas** - Notificaciones push cuando cambien condiciones
3. **Cache local** - Room Database para modo offline
4. **Modo oscuro** - Tema dark completo
5. **Widgets** - Widget de home screen con top 5 acciones
6. **Filtros avanzados** - Por score mínimo, por cambio porcentual, etc.

## 🐛 Troubleshooting

**Error "Unable to resolve host":**
- Verifica permisos de Internet en Manifest
- Comprueba que el servidor esté corriendo
- Usa IP correcta para emulador/dispositivo

**Crash al cargar datos:**
- Revisa logs con Logcat
- Verifica que la API esté respondiendo con `/health`
- Comprueba que los modelos de datos coincidan con la respuesta JSON

**Imágenes no se muestran:**
- Crea los drawables faltantes (ic_refresh, ic_star_outline, etc.)
- O descarga Material Icons de Google

## 📚 Documentación Adicional

- [API Endpoints](../README.md#-api-endpoints)
- [Sistema Híbrido AI](../HYBRID_AI_GUIDE.md)
- [Guía de Implementación](../IMPLEMENTACION_COMPLETA.md)

---

**¿Necesitas ayuda?** Revisa los logs de Logcat o consulta la documentación de la API.
