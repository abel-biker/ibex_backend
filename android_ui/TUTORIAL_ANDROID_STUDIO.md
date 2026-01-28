# 🚀 Guía Completa: Crear App Android desde Cero

## 📋 Requisitos Previos

1. **Android Studio** instalado (última versión)
   - Descarga: https://developer.android.com/studio
   - Asegúrate de instalar el SDK de Android

2. **Dispositivo para probar:**
   - Emulador Android (incluido en Android Studio)
   - O tu móvil Android conectado por USB con modo desarrollador

---

## 🎯 PASO 1: Crear Nuevo Proyecto

### 1.1 Abrir Android Studio
- Abre Android Studio
- Click en **"New Project"**

### 1.2 Seleccionar Template
- Selecciona **"Empty Views Activity"** (no Compose)
- Click en **"Next"**

### 1.3 Configurar Proyecto
```
Name: IBEX 35 Trading
Package name: com.example.ibex35trading
Save location: Donde quieras (ej: C:\AndroidProjects\IBEX35Trading)
Language: Kotlin
Minimum SDK: API 24 (Android 7.0)
Build configuration language: Gradle (Kotlin DSL) o Groovy (da igual)
```
- Click en **"Finish"**
- Espera a que Gradle sincronice (puede tardar 2-3 minutos)

---

## 🎯 PASO 2: Configurar Dependencias

### 2.1 Abrir `build.gradle` (Module: app)
- En el panel izquierdo, navega a: `Gradle Scripts > build.gradle (Module :app)`
- **Borra todo** el contenido
- **Copia y pega** el contenido de tu archivo: `android_ui/build.gradle`

### 2.2 Añadir repositorio para MPAndroidChart
- Abre `settings.gradle` (Project Settings)
- Encuentra la sección `dependencyResolutionManagement`
- Añade dentro de `repositories`:

```gradle
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
        maven { url 'https://jitpack.io' }  // ← Añade esta línea
    }
}
```

### 2.3 Sincronizar Gradle
- Click en el botón **"Sync Now"** que aparece arriba
- O: `File > Sync Project with Gradle Files`
- Espera a que descargue todas las dependencias (puede tardar 5 minutos la primera vez)

---

## 🎯 PASO 3: Añadir Permisos

### 3.1 Abrir AndroidManifest.xml
- Navega a: `app > manifests > AndroidManifest.xml`

### 3.2 Añadir permisos ANTES de `<application>`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <!-- Añade estas 2 líneas -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <application
        android:allowBackup="true"
        ...
```

---

## 🎯 PASO 4: Activar View Binding

### 4.1 Verificar en `build.gradle` (Module: app)
Asegúrate de que existe (ya debería estar si copiaste el archivo):

```gradle
android {
    ...
    buildFeatures {
        viewBinding true
    }
}
```

---

## 🎯 PASO 5: Copiar Archivos API

### 5.1 Crear paquete `api`
- Click derecho en `app > java > com.example.ibex35trading`
- `New > Package`
- Nombre: `api`
- Click OK

### 5.2 Copiar archivo API
- Click derecho en el paquete `api` recién creado
- `New > Kotlin Class/File`
- Selecciona **"File"**
- Nombre: `IBEX35ApiClient`
- Click OK

- **Abre** tu archivo `android_example.kt` (en tu carpeta del backend)
- **Copia TODO** el contenido
- **Pégalo** en `IBEX35ApiClient.kt` que acabas de crear

**IMPORTANTE:** Cambia la primera línea del paquete:
```kotlin
// Cambiar de:
package com.example.ibex35trading.api

// A:
package com.example.ibex35trading.api
```
(Ya debería estar correcto)

---

## 🎯 PASO 6: Crear Layouts XML

### 6.1 Layout Principal (activity_main.xml)

**Opción A - Reemplazar archivo existente:**
- Navega a: `app > res > layout > activity_main.xml`
- **Borra todo** el contenido
- **Copia y pega** el contenido de `android_ui/activity_main.xml`

**Opción B - Crear desde cero:**
- Click derecho en `res > layout`
- `New > Layout Resource File`
- Nombre: `activity_main`
- Root element: `androidx.coordinatorlayout.widget.CoordinatorLayout`
- Click OK
- Luego copia el contenido

### 6.2 Item de Stock (item_stock.xml)
- Click derecho en `res > layout`
- `New > Layout Resource File`
- Nombre: `item_stock`
- Root element: `com.google.android.material.card.MaterialCardView`
- Click OK
- **Copia y pega** el contenido de `android_ui/item_stock.xml`

### 6.3 Detalle de Stock (activity_stock_detail.xml)
- Click derecho en `res > layout`
- `New > Layout Resource File`
- Nombre: `activity_stock_detail`
- Root element: `androidx.core.widget.NestedScrollView`
- Click OK
- **Copia y pega** el contenido de `android_ui/activity_stock_detail.xml`

---

## 🎯 PASO 7: Crear Drawables (Iconos)

### 7.1 Crear carpeta si no existe
- `res > drawable` ya debería existir

### 7.2 Crear ic_refresh.xml
- Click derecho en `res > drawable`
- `New > Vector Asset`
- En "Clip Art", busca "refresh"
- Selecciona el icono de refresh
- Name: `ic_refresh`
- Color: Blanco (#FFFFFF)
- Click Next > Finish

### 7.3 Crear ic_star_outline.xml
- Click derecho en `res > drawable`
- `New > Vector Asset`
- Busca "star_border"
- Name: `ic_star_outline`
- Color: Amarillo (#FFB300)
- Click Next > Finish

### 7.4 Crear ic_star_filled.xml
- Click derecho en `res > drawable`
- `New > Vector Asset`
- Busca "star" (estrella rellena)
- Name: `ic_star_filled`
- Color: Amarillo (#FFB300)
- Click Next > Finish

### 7.5 Crear ic_notifications.xml
- Busca "notifications"
- Name: `ic_notifications`
- Click Next > Finish

### 7.6 Crear ic_chart.xml
- Busca "show_chart"
- Name: `ic_chart`
- Click Next > Finish

### 7.7 Crear background_reason.xml
- Click derecho en `res > drawable`
- `New > Drawable Resource File`
- Nombre: `background_reason`
- Click OK
- **Pega este contenido:**

```xml
<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android">
    <solid android:color="#F5F5F5" />
    <corners android:radius="8dp" />
    <stroke android:color="#E0E0E0" android:width="1dp" />
</shape>
```

---

## 🎯 PASO 8: Copiar Código Kotlin

### 8.1 MainActivity.kt
- Ya existe `MainActivity.kt` en `app > java > com.example.ibex35trading`
- **Borra todo** su contenido
- **Copia y pega** el contenido de `android_ui/MainActivity.kt`

### 8.2 Crear paquete adapters
- Click derecho en `com.example.ibex35trading`
- `New > Package`
- Nombre: `adapters`

### 8.3 Crear StocksAdapter.kt
- Click derecho en `adapters`
- `New > Kotlin Class/File`
- Nombre: `StocksAdapter`
- **Copia y pega** el contenido de `android_ui/StocksAdapter.kt`

### 8.4 Crear StockDetailActivity.kt
- Click derecho en `com.example.ibex35trading` (paquete principal)
- `New > Kotlin Class/File`
- Nombre: `StockDetailActivity`
- **Copia y pega** el contenido de `android_ui/StockDetailActivity.kt`

---

## 🎯 PASO 9: Actualizar AndroidManifest.xml

Añade la nueva Activity:

```xml
<application
    android:allowBackup="true"
    ...
    android:theme="@style/Theme.IBEX35Trading">
    
    <activity
        android:name=".MainActivity"
        android:exported="true">
        <intent-filter>
            <action android:name="android.intent.action.MAIN" />
            <category android:name="android.intent.category.LAUNCHER" />
        </intent-filter>
    </activity>
    
    <!-- Añade esto -->
    <activity
        android:name=".StockDetailActivity"
        android:parentActivityName=".MainActivity" />
    
</application>
```

---

## 🎯 PASO 10: Configurar URL de la API

### 10.1 Abrir IBEX35ApiClient.kt
- Navega a: `app > java > com.example.ibex35trading > api > IBEX35ApiClient.kt`

### 10.2 Cambiar BASE_URL según tu entorno

**Para usar servidor local (desarrollo):**
```kotlin
object IBEX35ApiClient {
    // Si usas EMULADOR:
    private const val BASE_URL = "http://10.0.2.2:8000"
    
    // Si usas DISPOSITIVO FÍSICO (obtén tu IP con 'ipconfig'):
    // private const val BASE_URL = "http://192.168.1.X:8000"
    
    // Para producción (cuando Railway esté listo):
    // private const val BASE_URL = "https://web-production-4c740.up.railway.app"
```

---

## 🎯 PASO 11: Resolver Errores de Compilación

### 11.1 Actualizar modelos de datos

En `IBEX35ApiClient.kt`, busca `data class StockRanking` y añade estos campos opcionales:

```kotlin
data class StockRanking(
    val symbol: String,
    val name: String,
    val sector: String,
    val score: Float,
    val rating: String,
    val confidence: String,
    val price: Float,
    val change_pct: Float,
    val technical_score: Float,
    val momentum_score: Float,
    val sentiment_score: Float,
    // Añade estos campos para IA:
    val signal: String? = null,
    val ml_probability: Float? = null,
    val reason: String? = null,
    val methodology: String? = null
)
```

### 11.2 Build > Clean Project
- Menu: `Build > Clean Project`
- Espera
- Menu: `Build > Rebuild Project`

---

## 🎯 PASO 12: Probar la App

### 12.1 Asegúrate de que tu backend local esté corriendo:

**En PowerShell (carpeta del backend):**
```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

Verifica que funciona:
```powershell
Invoke-RestMethod http://localhost:8000/health
```

### 12.2 Ejecutar la app

**Opción A - Emulador:**
1. Click en el botón **Run** (triángulo verde) arriba a la derecha
2. Selecciona **"Create New Virtual Device"** si no tienes uno
3. Elige un dispositivo (ej: Pixel 5)
4. Descarga una imagen del sistema (ej: Android 14)
5. Click Finish
6. Click Run de nuevo
7. Espera a que arranque el emulador (1-2 minutos primera vez)

**Opción B - Dispositivo físico:**
1. Habilita "Opciones de desarrollo" en tu móvil:
   - Ajustes > Acerca del teléfono
   - Toca 7 veces en "Número de compilación"
2. Ajustes > Opciones de desarrollo > USB debugging (activar)
3. Conecta móvil por USB
4. Acepta "Permitir depuración USB" en el móvil
5. En Android Studio, selecciona tu dispositivo en la lista
6. Click Run

### 12.3 Verificar funcionamiento
- Deberías ver el ranking del IBEX 35
- Click en una empresa para ver el detalle
- Verás las predicciones AI si tu backend local está corriendo

---

## 🐛 Solución de Problemas Comunes

### Error: "Unable to resolve host"
**Causa:** La app no puede conectar con el backend
**Solución:**
1. Verifica que el backend esté corriendo: `http://localhost:8000/health`
2. Si usas emulador, usa `http://10.0.2.2:8000`
3. Si usas dispositivo físico, usa tu IP local (no localhost)

### Error: "Unresolved reference"
**Causa:** Falta sincronizar Gradle
**Solución:**
1. `File > Invalidate Caches > Invalidate and Restart`
2. `Build > Clean Project`
3. `Build > Rebuild Project`

### La app crashea al abrir
**Causa:** Probablemente error en el layout o falta un drawable
**Solución:**
1. Abre Logcat (panel inferior)
2. Busca el error en rojo
3. Si dice "Resource not found", crea el drawable faltante

### El backend responde 404
**Causa:** La URL está mal o el endpoint no existe
**Solución:**
1. Prueba en navegador: `http://localhost:8000/docs`
2. Verifica que uses `/api/v1/` en las rutas

---

## 🎉 ¡Listo!

Ahora tienes:
✅ App Android funcionando
✅ Conectada a tu backend con IA
✅ UI profesional con Material Design
✅ 4 componentes AI visualizados

## 📱 Próximos Pasos

1. **Probar todas las funciones**
2. **Cuando Railway esté listo**, cambia BASE_URL a producción
3. **Añadir gráficos** (MPAndroidChart ya está instalado)
4. **Implementar cache** con Room Database
5. **Publicar en Play Store**

---

## 🆘 ¿Necesitas Ayuda?

Si te atascas en algún paso, dime:
- ¿En qué paso estás?
- ¿Qué error ves exactamente?
- Captura de pantalla si es posible

¡Estoy aquí para ayudarte! 🚀
