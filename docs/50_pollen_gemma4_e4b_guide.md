# Guía técnica de desarrollo v2

## Gemma 4 E4B + LiteRT-LM en Pixel 10 Pro

Versión: 2026-04-22  
Audiencia: programadora Android que va a desarrollar conmigo  
Formato: Kotlin + Android + LiteRT-LM  
Estado: documento operativo para arrancar implementación  
Nota: esta versión corrige un error de nomenclatura de una versión anterior. El modelo objetivo es **Gemma 4 E4B**, no A4B.

---

## 1. Objetivo del documento

Este documento convierte la investigación previa en una guía de ejecución. No busca vender una demo, sino reducir ambigüedad técnica para una implementación real de una app Android que ejecute **Gemma 4 E4B** mediante **LiteRT-LM** en un **Pixel 10 Pro**.

La base del proyecto se apoya en cuatro hechos:

1. **Gemma 4 E4B existe oficialmente** como variante edge de la familia Gemma 4, con **4.5B parámetros efectivos**, alrededor de **8B contando embeddings**, soporte multimodal y **contexto de hasta 128K tokens**.
2. **LiteRT-LM** es el runtime oficial abierto de Google AI Edge para LLMs on-device con **CPU, GPU, NPU, multimodalidad y tool use**.
3. **Pixel 10 Pro** sale con **Tensor G5**, **16 GB de RAM** y **Android 16**.
4. **E4B ya funciona en tu Pixel 10 Pro dentro de AI Edge Gallery**, que según la documentación oficial corre enteramente sobre **LiteRT-LM**.

Eso permite una conclusión muy importante:

> El proyecto no tiene que demostrar si la plataforma es viable. Tiene que replicar fuera de Edge Gallery la ruta que ya está funcionando en tu dispositivo, con instrumentación, control de backend y una arquitectura mantenible.

---

## 2. Resumen ejecutivo

### Lo que asumimos como verdadero

- El dispositivo objetivo primario es **Pixel 10 Pro**.
- El sistema operativo objetivo es **Android 16**.
- El runtime obligatorio es **LiteRT-LM**.
- El modelo objetivo funcional es **Gemma 4 E4B**.
- Existe una validación práctica positiva en **AI Edge Gallery** con tu propio teléfono.

### Lo que no asumimos

- No asumimos que el backend **GPU** sea estable en Pixel 10 Pro.
- No asumimos que el artefacto **E4B** que ves en Gallery coincida byte a byte con el paquete público de LiteRT Community, aunque sí existe una ruta pública clara para E4B en formato `.litertlm`.
- No asumimos que 128K tokens sean utilizables en móvil como presupuesto de contexto realista.
- No asumimos que la **NPU** de Pixel esté lista para nuestro caso con LiteRT-LM.

### Decisiones de producto para el MVP

- **CPU como baseline obligatoria**.
- **GPU solo detrás de feature flag**.
- **Texto primero**.
- **Imagen después**, cuando esté cerrada la estabilidad base.
- **Sin dependencia de red para inferencia**.
- **Persistencia local y observabilidad desde el primer sprint**.

---

## 3. Estado técnico relevante

### 3.1 Modelo: Gemma 4 E4B

Según la ficha técnica oficial:

- variante: **edge**
- parámetros efectivos: **4.5B**
- tamaño aproximado total: **8B contando embeddings**
- contexto máximo teórico: **128K**
- modalidades: **texto, imagen y audio**
- orientado a ejecución on-device y edge

La implicación práctica es clara: no es un modelo “pequeño” en sentido trivial, pero sí está diseñado para caber en hardware móvil moderno. Aun así, hay que planificar con cuidado **latencia, inicialización, temperatura, memoria y degradación**.

### 3.2 Runtime: LiteRT-LM

La API Android oficial de LiteRT-LM gira en torno a estas piezas:

- `Engine`
- `EngineConfig`
- `Conversation`
- `ConversationConfig`
- `SamplerConfig`
- `Backend`

Google documenta que `engine.initialize()` puede tardar varios segundos y recomienda ejecutarlo en un hilo de fondo. También documenta requisitos concretos en Android para GPU, incluyendo `libvndksupport.so` y `libOpenCL.so` dentro del `AndroidManifest.xml`.

### 3.3 App de referencia: Google AI Edge Gallery

La documentación oficial de LiteRT-LM afirma que **AI Edge Gallery** es una app experimental que muestra capacidades GenAI on-device ejecutadas enteramente offline con LiteRT-LM.

Esto importa mucho, porque tu evidencia local no es anecdótica: si E4B funciona allí en tu Pixel 10 Pro, entonces la combinación **Pixel 10 Pro + LiteRT-LM** ya está probada en el mundo real al menos para una ruta concreta.

### 3.4 Pixel 10 Pro como plataforma

Google publica para Pixel 10 Pro:

- **16 GB RAM**
- **Google Tensor G5**
- **Android 16**

Eso sitúa al dispositivo en la categoría correcta para inferencia seria on-device, pero no elimina problemas del software intermedio.

### 3.5 Riesgo específico de GPU en Pixel 10 / Tensor G5

Hay dos señales públicas relevantes:

1. En **AI Edge Gallery**, un issue reporta que en **Pixel 10 Pro con Android 16** el modelo funciona en **CPU**, pero al cambiar a **GPU** la app se congela y crashea.
2. En **LiteRT-LM**, otro issue describe que el backend GPU en **Tensor G5** puede identificar erróneamente la GPU como **PowerVR** al consultar `GL_RENDERER` sin contexto EGL actual, desactivando preparación de pesos en GPU y degradando la inicialización.

Traducción operativa:

- GPU no se prohíbe.
- GPU no se convierte en base del proyecto.
- Toda inicialización debe tener **fallback a CPU**.
- Todo experimento GPU debe dejar rastro en logs y métricas.

### 3.6 NPU en Pixel

No la tomamos como pilar del MVP. La documentación general de LiteRT-LM contempla NPU, pero para Pixel el estado público sigue sin ser lo bastante sólido como para diseñar sobre ello.

### 3.7 Disponibilidad pública del artefacto E4B

A fecha de este documento:

- sí existe una ruta pública clara para **E4B** en formato `.litertlm`
- tu validación en Gallery demuestra que **E4B** ya corre en tu Pixel 10 Pro
- aun así, conviene tratar el artefacto exacto que ya funciona en tu teléfono como referencia de proyecto, porque no sabemos si Gallery usa exactamente el mismo empaquetado, backend o configuración que tu futura app

Conclusión técnica:

> E4B sí es reproducible públicamente en LiteRT-LM, pero el artefacto exacto que ya funciona en tu Pixel debe inventariarse y preservarse como referencia de proyecto.

---

## 4. Objetivo funcional del MVP

Construir una app Android nativa que:

- cargue Gemma 4 E4B con LiteRT-LM
- funcione de forma estable en Pixel 10 Pro
- soporte chat de texto
- permita streaming de salida
- gestione historial local
- mida tiempos y errores
- permita backend configurable por flags internas
- opere completamente offline en inferencia

### Fuera de alcance del MVP

- tool use de producción
- RAG complejo
- audio
- sincronización cloud
- multiusuario
- persistencia multinodo
- soporte generalizado a todo Android
- promesas comerciales de benchmark

---

## 5. Estrategia de implementación

### Fase 0. Captura de la realidad que ya funciona

Antes de programar nada serio, hay que documentar exactamente el E4B que ya corre en Edge Gallery.

Checklist obligatorio:

- versión exacta de AI Edge Gallery
- nombre exacto del modelo mostrado en UI
- tamaño del archivo
- origen del modelo: descarga integrada, importación manual u otro
- si la prueba funcional fue con CPU o GPU
- si se probó texto, imagen o ambos
- hash SHA-256 del artefacto si es accesible
- fecha de validación

Sin esto, el proyecto puede acabar intentando reconstruir una realidad que ya tenías resuelta, pero de forma ciega.

### Fase 1. Baseline estable

Objetivo: una app de chat local con backend **CPU**.

### Fase 2. Instrumentación y calidad

Objetivo: TTFT, duración de inicialización, tokens por segundo aproximados, errores de carga, memoria y temperatura.

### Fase 3. Imagen

Objetivo: habilitar inputs de imagen solo si el artefacto E4B y la integración Kotlin/Android demuestran estabilidad suficiente.

### Fase 4. GPU experimental

Objetivo: probar GPU en Tensor G5 solo detrás de feature flag y con telemetría detallada.

---

## 6. Arquitectura propuesta

### 6.1 Capas

#### Capa de UI

Responsable de:

- pantalla de chat
- captura de prompts
- streaming de respuesta
- visor de estado del backend
- importación de imagen en fase 2
- pantalla de diagnóstico

#### Capa de aplicación

Responsable de:

- coordinación de casos de uso
- orquestación del ciclo de inferencia
- gestión de sesiones
- routing entre UI y runtime

#### Capa de runtime LLM

Responsable de:

- crear `Engine`
- inicializar `Conversation`
- enviar prompts
- cerrar recursos
- exponer errores estandarizados

#### Capa de infraestructura local

Responsable de:

- almacenamiento del modelo
- cache de runtime
- persistencia de sesiones
- logs locales
- preferencias y feature flags

#### Capa de observabilidad

Responsable de:

- TTFT
- tokens generados
- duración total
- errores por backend
- número de retries
- temperatura observada
- versión de modelo

---

## 7. Estructura del repositorio Android

```text
app/
  build.gradle.kts
  src/main/
    AndroidManifest.xml
    java/com/tuempresa/gemma/
      GemmaApp.kt
      MainActivity.kt
      di/
        AppContainer.kt
      config/
        FeatureFlags.kt
        ModelRegistry.kt
      data/
        model/
          ChatMessageEntity.kt
          SessionEntity.kt
          ModelArtifact.kt
        prefs/
          SettingsStore.kt
        repository/
          ChatRepository.kt
          ModelRepository.kt
      domain/
        model/
          ChatMessage.kt
          GenerationChunk.kt
          GenerationMetrics.kt
          BackendMode.kt
          ModelStatus.kt
        usecase/
          InitializeModelUseCase.kt
          SendPromptUseCase.kt
          ResetConversationUseCase.kt
          ImportImageUseCase.kt
      llm/
        LiteRtEngineFactory.kt
        LiteRtSessionManager.kt
        LiteRtChatService.kt
        LiteRtPromptBuilder.kt
        LiteRtErrorMapper.kt
        LiteRtBackendPolicy.kt
        LiteRtMetricsCollector.kt
      ui/
        chat/
          ChatScreen.kt
          ChatViewModel.kt
          ChatUiState.kt
        settings/
          SettingsScreen.kt
          SettingsViewModel.kt
        diagnostics/
          DiagnosticsScreen.kt
          DiagnosticsViewModel.kt
      util/
        Logger.kt
        HashUtils.kt
        FileUtils.kt
        TimeUtils.kt
    res/
      values/
      xml/
      drawable/
  src/test/
  src/androidTest/
```

Notas:

- Si se usa Compose, la capa `ui/` debe ser exclusivamente declarativa.
- Toda referencia a LiteRT-LM debe quedar encapsulada en `llm/`.
- El resto de la app no debería depender directamente de clases del runtime.

---

## 8. Gradle y dependencias

### build.gradle.kts del módulo app

```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.tuempresa.gemma"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.tuempresa.gemma"
        minSdk = 31
        targetSdk = 36
        versionCode = 1
        versionName = "0.1.0"
    }

    buildFeatures {
        compose = true
    }
}

dependencies {
    implementation("com.google.ai.edge.litertlm:litertlm-android:latest.release")

    implementation("androidx.core:core-ktx:1.17.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.9.3")
    implementation("androidx.activity:activity-compose:1.10.1")
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
}
```

Notas:

- fijar versión exacta cuando se estabilice el proyecto
- no vivir eternamente con `latest.release`
- bloquear versión del runtime en CI cuando el baseline pase QA

---

## 9. AndroidManifest mínimo

```xml
<manifest ...>
    <application
        android:name=".GemmaApp"
        ...>

        <uses-native-library
            android:name="libvndksupport.so"
            android:required="false" />

        <uses-native-library
            android:name="libOpenCL.so"
            android:required="false" />

    </application>
</manifest>
```

Notas:

- estas bibliotecas son necesarias para la ruta GPU documentada por LiteRT-LM
- aunque el MVP use CPU, conviene dejar listo el manifiesto para experimentos controlados

---

## 10. Estrategia de modelo y archivos

### 10.1 Política de artefactos

No hay que esconder esta realidad: el modelo es un activo grande y delicado.

Nuestra política debería ser:

- nunca asumir nombre ni empaquetado sin verificarlo
- guardar hash SHA-256
- guardar tamaño exacto
- versionar metadatos del modelo aunque el archivo no viva en git
- separar claramente `model artifact`, `cache runtime` y `user data`

### 10.2 Dónde guardar el modelo

Preferencia:

- almacenamiento privado de la app o ruta controlada accesible por el runtime
- no meter el modelo dentro del APK
- contemplar importación local y validación por hash

### 10.3 Registry del modelo

`ModelRegistry.kt`

```kotlin
package com.tuempresa.gemma.config

data class ModelDescriptor(
    val id: String,
    val displayName: String,
    val localPath: String,
    val sha256: String?,
    val supportsVision: Boolean,
    val recommendedBackend: String,
)

object ModelRegistry {
    fun activeModel(): ModelDescriptor = ModelDescriptor(
        id = "gemma4_a4b_pixel10",
        displayName = "Gemma 4 E4B",
        localPath = "/data/user/0/com.tuempresa.gemma/files/models/gemma4-a4b/model.litertlm",
        sha256 = null,
        supportsVision = true,
        recommendedBackend = "CPU"
    )
}
```

Notas:

- el `localPath` es ilustrativo
- el hash no puede quedarse en `null` cuando el proyecto pase a fase real

---

## 11. Política de backend

### 11.1 Reglas

- backend por defecto: **CPU**
- GPU: solo activable por flag interna
- NPU: fuera del MVP
- si `engine.initialize()` falla con GPU, fallback automático a CPU
- si primer decode falla con GPU, registrar incidente y volver a CPU
- no reintentar GPU en bucle infinito

### 11.2 Enum de backend

```kotlin
package com.tuempresa.gemma.domain.model

enum class BackendMode {
    CPU,
    GPU,
    NPU
}
```

### 11.3 Feature flags

```kotlin
package com.tuempresa.gemma.config

data class FeatureFlags(
    val enableGpuExperimental: Boolean = false,
    val enableVisionInput: Boolean = false,
    val enableVerboseLlmLogs: Boolean = true,
)
```

### 11.4 Política de fallback

```kotlin
package com.tuempresa.gemma.llm

import com.tuempresa.gemma.domain.model.BackendMode

class LiteRtBackendPolicy {
    fun orderedBackends(preferred: BackendMode): List<BackendMode> {
        return when (preferred) {
            BackendMode.CPU -> listOf(BackendMode.CPU)
            BackendMode.GPU -> listOf(BackendMode.GPU, BackendMode.CPU)
            BackendMode.NPU -> listOf(BackendMode.NPU, BackendMode.CPU)
        }
    }
}
```

---

## 12. Inicialización de LiteRT-LM

### 12.1 Factory de Engine

```kotlin
package com.tuempresa.gemma.llm

import android.content.Context
import com.google.ai.edge.litertlm.Backend
import com.google.ai.edge.litertlm.Engine
import com.google.ai.edge.litertlm.EngineConfig
import com.tuempresa.gemma.domain.model.BackendMode

class LiteRtEngineFactory(
    private val context: Context,
) {
    fun create(modelPath: String, backendMode: BackendMode): Engine {
        val backend = when (backendMode) {
            BackendMode.CPU -> Backend.CPU()
            BackendMode.GPU -> Backend.GPU()
            BackendMode.NPU -> Backend.NPU(
                nativeLibraryDir = context.applicationInfo.nativeLibraryDir
            )
        }

        val config = EngineConfig(
            modelPath = modelPath,
            backend = backend,
            cacheDir = context.cacheDir.path
        )

        return Engine(config)
    }
}
```

Notas:

- si se activa visión, revisar si la API o el artefacto requieren `visionBackend`
- la configuración exacta dependerá del formato del modelo E4B que ya estás usando

### 12.2 Session manager

```kotlin
package com.tuempresa.gemma.llm

import com.google.ai.edge.litertlm.Engine
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

class LiteRtSessionManager(
    private val engineFactory: LiteRtEngineFactory,
    private val backendPolicy: LiteRtBackendPolicy,
) {
    private val mutex = Mutex()
    private var engine: Engine? = null

    suspend fun initialize(modelPath: String, preferredBackend: com.tuempresa.gemma.domain.model.BackendMode): Engine {
        return mutex.withLock {
            engine?.close()
            var lastError: Throwable? = null

            for (candidate in backendPolicy.orderedBackends(preferredBackend)) {
                try {
                    val newEngine = engineFactory.create(modelPath, candidate)
                    newEngine.initialize()
                    engine = newEngine
                    return@withLock newEngine
                } catch (t: Throwable) {
                    lastError = t
                }
            }

            throw IllegalStateException("No se pudo inicializar LiteRT-LM", lastError)
        }
    }

    fun currentEngine(): Engine? = engine

    fun close() {
        engine?.close()
        engine = null
    }
}
```

Notas:

- el `Mutex` evita carreras de inicialización
- el `Engine` debe tener un único dueño de ciclo de vida claro

---

## 13. Servicio de chat

```kotlin
package com.tuempresa.gemma.llm

import com.google.ai.edge.litertlm.Contents
import com.google.ai.edge.litertlm.Message
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

class LiteRtChatService(
    private val sessionManager: LiteRtSessionManager,
) {
    fun sendPrompt(userText: String): Flow<String> = flow {
        val engine = requireNotNull(sessionManager.currentEngine()) {
            "Engine no inicializado"
        }

        engine.createConversation().use { conversation ->
            val prompt = Message.user(userText)
            conversation.sendMessageAsync(prompt).collect { chunk ->
                emit(chunk)
            }
        }
    }
}
```

Notas:

- esta versión es minimalista
- en producción conviene persistir una conversación viva o reconstruir contexto de forma controlada
- no regalar el contexto al infinito; el móvil paga cada exceso

---

## 14. Capa de dominio y métricas

### 14.1 Modelos de dominio

```kotlin
package com.tuempresa.gemma.domain.model

data class ChatMessage(
    val id: String,
    val role: String,
    val text: String,
    val createdAtMillis: Long,
)

data class GenerationMetrics(
    val backendMode: BackendMode,
    val initializeMillis: Long,
    val ttftMillis: Long,
    val totalMillis: Long,
    val outputChars: Int,
    val temperatureCelsius: Float?,
)
```

### 14.2 Collector de métricas

```kotlin
package com.tuempresa.gemma.llm

import android.os.SystemClock
import com.tuempresa.gemma.domain.model.BackendMode
import com.tuempresa.gemma.domain.model.GenerationMetrics

class LiteRtMetricsCollector {
    fun build(
        backendMode: BackendMode,
        initializeStart: Long,
        initializeEnd: Long,
        firstTokenAt: Long,
        completedAt: Long,
        output: String,
        temperatureCelsius: Float? = null,
    ): GenerationMetrics {
        return GenerationMetrics(
            backendMode = backendMode,
            initializeMillis = initializeEnd - initializeStart,
            ttftMillis = firstTokenAt - initializeEnd,
            totalMillis = completedAt - initializeEnd,
            outputChars = output.length,
            temperatureCelsius = temperatureCelsius,
        )
    }

    fun now(): Long = SystemClock.elapsedRealtime()
}
```

Notas:

- si quieres tokens exactos, hay que ver qué expone el runtime o estimarlos de otro modo
- TTFT y duración total ya son datos muy útiles para decisiones reales

---

## 15. ViewModel de chat

```kotlin
package com.tuempresa.gemma.ui.chat

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.tuempresa.gemma.llm.LiteRtChatService
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class ChatUiState(
    val prompt: String = "",
    val isLoading: Boolean = false,
    val output: String = "",
    val error: String? = null,
)

class ChatViewModel(
    private val chatService: LiteRtChatService,
) : ViewModel() {
    private val _uiState = MutableStateFlow(ChatUiState())
    val uiState: StateFlow<ChatUiState> = _uiState

    fun onPromptChanged(value: String) {
        _uiState.update { it.copy(prompt = value) }
    }

    fun send() {
        val prompt = _uiState.value.prompt.trim()
        if (prompt.isEmpty()) return

        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, output = "", error = null) }
            runCatching {
                chatService.sendPrompt(prompt).collect { chunk ->
                    _uiState.update { state ->
                        state.copy(output = state.output + chunk)
                    }
                }
            }.onFailure { t ->
                _uiState.update { it.copy(error = t.message) }
            }
            _uiState.update { it.copy(isLoading = false) }
        }
    }
}
```

---

## 16. UI mínima con Compose

```kotlin
@Composable
fun ChatScreen(
    uiState: ChatUiState,
    onPromptChanged: (String) -> Unit,
    onSend: () -> Unit,
) {
    Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
        OutlinedTextField(
            value = uiState.prompt,
            onValueChange = onPromptChanged,
            modifier = Modifier.fillMaxWidth(),
            label = { Text("Prompt") }
        )

        Spacer(Modifier.height(12.dp))

        Button(
            onClick = onSend,
            enabled = !uiState.isLoading,
        ) {
            Text(if (uiState.isLoading) "Generando..." else "Enviar")
        }

        Spacer(Modifier.height(16.dp))

        if (uiState.error != null) {
            Text(text = "Error: ${uiState.error}")
        }

        SelectionContainer {
            Text(text = uiState.output)
        }
    }
}
```

---

## 17. Gestión del ciclo de vida

### Reglas

- inicializar el motor fuera del hilo principal
- evitar reinicializar el modelo por cada prompt
- cerrar `Engine` y `Conversation` explícitamente
- serializar acceso al runtime cuando proceda
- separar claramente inicialización de inferencia

### Recomendación

- `Application` o un contenedor singleton puede mantener servicios, pero el `Engine` no debe quedar inmortal sin motivo
- usar un `SessionManager` con ownership claro

---

## 18. Estrategia de conversación y contexto

No hay que caer en la fantasía de “el modelo soporta 128K, así que se lo damos todo”.

### Política recomendada

- ventana conversacional corta para el MVP
- resumen de historial si la sesión crece
- truncado por presupuesto configurable
- logs de prompts solo en builds internas

### Lo que conviene evitar

- reinyectar historial completo en cada turno sin control
- adjuntar imágenes a cada interacción por defecto
- sesiones eternas que mezclen UX y ensayo térmico

---

## 19. Visión e imagen

Gemma 4 E4B soporta texto + imagen según el model card oficial. Eso lo vuelve muy interesante para una segunda fase.

### Requisitos antes de activarlo

- confirmar que el artefacto E4B concreto que tienes soporta visión bajo LiteRT-LM en Android
- confirmar firma de API concreta para enviar imagen en Kotlin
- validar memoria y temperatura con inputs visuales

### Política de fase 2

- una imagen por prompt al principio
- redimensionado controlado
- compresión razonable
- límites explícitos de peso y resolución

### Casos de uso sensatos

- pregunta sobre una única foto
- OCR ligero
- comprensión de interfaz
- resumen de documento fotografiado

---

## 20. Observabilidad y diagnóstico

### Pantalla interna de diagnóstico

La app debe tener una pantalla no comercial que muestre:

- versión app
- versión runtime LiteRT-LM
- modelo activo
- hash del modelo
- backend activo
- tiempo de initialize
- TTFT último prompt
- duración total última respuesta
- si hubo fallback de GPU a CPU
- contador de errores por backend

### Logging

- logs verbosos solo en builds internas
- capturar excepción original completa
- separar errores de modelo, errores de backend y errores de UI

### Temperatura

No hace falta una telemetría paranoica desde el día uno, pero sí conviene registrar:

- temperatura aproximada si está disponible
- batería
- si hubo thermal throttling observable en pruebas largas

---

## 21. Plan de QA técnico

### 21.1 Smoke tests

- arranque de app
- inicialización de modelo
- prompt corto de una línea
- prompt medio de varias frases
- cancelación de generación
- reinicio de conversación

### 21.2 Pruebas de estabilidad

- 20 prompts seguidos en CPU
- sesiones largas de 10-15 minutos
- app al background y foreground
- bloqueo/desbloqueo de pantalla
- rotación si la UI no está bloqueada

### 21.3 Pruebas GPU experimentales

- inicialización en GPU
- prompt corto en GPU
- prompt medio en GPU
- captura de crash o freeze
- verificación de fallback a CPU

### 21.4 Pruebas de visión

- una imagen pequeña
- una captura de pantalla
- una foto con texto
- imagen demasiado grande con manejo de error limpio

---

## 22. Riesgos del proyecto

### Riesgo 1. El artefacto E4B que ya funciona en Gallery no coincide exactamente con el de la app propia

Mitigación:

- inventariar lo que ya funciona
- no cambiar de artefacto sin validación A/B

### Riesgo 2. GPU en Tensor G5 sigue inestable

Mitigación:

- CPU baseline
- GPU con feature flag
- fallback automático

### Riesgo 3. Latencia de inicialización demasiado alta

Mitigación:

- prewarm controlado
- caché de runtime
- inicialización diferida al entrar en chat o al abrir app según tests

### Riesgo 4. Sobrecalentamiento o consumo excesivo

Mitigación:

- sesiones de prueba controladas
- límites de contexto
- desactivar visión si dispara la temperatura

### Riesgo 5. El equipo mezcla investigación con producto

Mitigación:

- dos carriles: `stable` y `experimental`
- métricas comparables
- no esconder bugs bajo UX bonita

---

## 23. Plan de trabajo recomendado

### Sprint 0

- inventario del modelo E4B validado en Edge Gallery
- captura de hashes y metadatos
- decisión de ruta de almacenamiento

### Sprint 1

- app mínima
- inicialización LiteRT-LM en CPU
- chat de texto con streaming
- persistencia local básica

### Sprint 2

- pantalla de diagnóstico
- métricas y logging
- reset de conversación
- importación controlada de modelo

### Sprint 3

- GPU experimental detrás de flag
- fallback automático
- suite de pruebas comparativas CPU vs GPU

### Sprint 4

- imagen si la ruta E4B real la soporta de forma estable en Kotlin
- redimensionado y límites
- pruebas térmicas y de memoria

---

## 24. Preguntas técnicas que la programadora debe resolver al inicio

1. ¿Cuál es exactamente el archivo E4B que ya funciona en tu Edge Gallery?
2. ¿Está disponible fuera de la app o solo queda encapsulado dentro de su flujo?
3. ¿La ruta actual funcional usa CPU o GPU?
4. ¿Qué firma exacta de API requiere visión para ese artefacto con LiteRT-LM Kotlin?
5. ¿Cuál es el tiempo real de `engine.initialize()` en Pixel 10 Pro?
6. ¿Cuál es el TTFT medio en prompts cortos y medianos?
7. ¿Qué tamaño máximo de contexto es cómodo antes de degradación térmica o de UX?

---

## 25. Criterios de éxito

### Éxito mínimo

- app abre
- modelo carga
- chat de texto funciona offline
- backend CPU estable
- logs diagnósticos útiles

### Éxito bueno

- TTFT aceptable
- historial local correcto
- pantalla de diagnóstico usable
- GPU experimental integrada con fallback limpio

### Éxito ambicioso

- imagen operativa
- GPU estable en algunos recorridos
- sesiones consistentes sin degradación fuerte

---

## 26. Recomendación final de arquitectura

La arquitectura correcta no es la más aparatosa. Es la que acepta el estado real del stack.

### Recomendación

- app Android nativa
- LiteRT-LM encapsulado en una capa interna
- Gemma 4 E4B como artefacto controlado y versionado por metadatos
- CPU como contrato estable
- GPU como experimento reversible
- visión como segunda iteración
- diagnóstico integrado desde el día uno

En otras palabras:

> No construir como si todo estuviera resuelto porque una demo funciona. Construir como si la demo fuera una pista valiosa, pero todavía parcial.

---

## 27. Referencias técnicas

### Fuentes primarias

1. Gemma 4 model card  
   https://ai.google.dev/gemma/docs/core/model_card_4

2. LiteRT-LM overview  
   https://ai.google.dev/edge/litert-lm/overview

3. LiteRT-LM Android  
   https://ai.google.dev/edge/litert-lm/android

4. Pixel 10 Pro specs  
   https://store.google.com/es/product/pixel_10_pro_specs?hl=es

5. LiteRT-LM issue sobre Tensor G5 / GPU misidentification  
   https://github.com/google-ai-edge/LiteRT-LM/issues/1681

6. AI Edge Gallery issue en Pixel 10 Pro con GPU  
   https://github.com/google-ai-edge/gallery/issues/309

### Fuentes internas de proyecto a crear

- ficha del artefacto E4B validado localmente
- hash SHA-256 del modelo
- tabla de benchmarks internos CPU/GPU
- registro de fallos por backend
- matriz de compatibilidad por versión de app

