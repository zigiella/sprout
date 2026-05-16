<!-- Versión castellana · English version: README.md -->

🇪🇸 **Castellano** · 🇬🇧 **[English](README.md)**

---

# Sprout

> **Optimización hídrica Local-first AI para parcelas que la red olvida.**
> *Abierto · local · seguro · explicable.*

> **Sprout es una red de decisión acotada por seguridad para el agua bajo ausencia.**

[Ver el vídeo de 3 minutos](https://www.youtube.com/watch?v=D9ETS4EPnxI) · [Probar la demo pública de contratos](https://sprout.zigiella.com) · [Leer el writeup](writeup/draft.md) · [Guía de entrega](SUBMISSION.md)

---

## En 30 segundos

Sprout es una arquitectura local-first de IA para riego en parcelas remotas o con conectividad débil — lugares donde el campo, la persona y la red rara vez coinciden en el tiempo.

La demo usa macetas, una Jetson, un ESP32, un móvil Android, un portátil, una bomba 12V y lecturas reales de humedad de suelo. El patrón representa algo mayor: pequeñas granjas, huertos comunitarios, parcelas rurales y tierra periférica donde las decisiones de agua no pueden esperar a la nube o a la próxima visita humana.

Sprout distribuye inteligencia entre tres nodos Gemma 4 y una capa física de veto:

- **Rhizome** vive en la parcela. Corre **Gemma 4 E2B** sobre Jetson vía `llama.cpp`, lee el estado local y decide si regar, diferir, saltar o bloquear.
- **Pollen** vive en el móvil Android del agricultor. Corre **Gemma 4 E4B** vía **LiteRT-LM**, convierte visitas y voz en objetos `MissionPatch` con caducidad, y transporta contexto entre parcelas desconectadas.
- **Meristem** vive en el portátil casero del agricultor. Corre **Gemma 4 E4B** vía `llama.cpp`, evalúa bundles y refina objetos `PolicyPacket` duraderos para la siguiente ventana.
- **ESP32-S3** posee la seguridad física. Corre firmware ESP-IDF propio y puede vetar comandos antes de que nada toque el agua.

**El LLM puede proponer. La capa física puede decir que no.**

---

## Por qué Sprout

El riego es un problema de tiempos tanto como un problema de agua. Una parcela puede secarse mientras el agricultor está fuera. Un pronóstico local puede cambiar mientras la red no está. Una observación humana puede importar más que un sensor, pero solo cuando alguien visita.

Sprout reduce la latencia entre la evidencia local y la acción local.

En lugar de asumir conectividad permanente, Sprout usa tres escalas de tiempo:

| Capa | Escala de tiempo | Pregunta |
|---|---:|---|
| **Rhizome** | minutos | ¿Qué debería hacer esta parcela ahora? |
| **Pollen** | TTL de visita | ¿Qué intención humana y qué contexto deben entrar en la parcela? |
| **Meristem** | días | ¿Qué política debería gobernar la próxima ventana? |
| **ESP32** | instante físico | ¿Es esta orden suficientemente segura para ejecutarse? |

---

## Arquitectura

```text
             Pollen · Android · Gemma 4 E4B · LiteRT-LM
          voz de visita → MissionPatch · WeatherDigest · FieldVisit
                                │
                                ▼
        Rhizome · Jetson · Gemma 4 E2B · llama.cpp
           telemetría local → acción candidata → DecisionReceipt
                                │
                                ▼
              ESP32-S3 · firmware ESP-IDF · veto físico
                    bomba · relé · sensor humedad · tanque/caudal
                                ▲
                                │
        Meristem · portátil casero · Gemma 4 E4B · llama.cpp
               bundles → evaluator/tools → PolicyPacket
```

### Invariantes

1. **La capa física prevalece.** Ningún LLM puede saltarse el ESP32.
2. **Toda inteligencia tiene jurisdicción.** Rhizome arbitra, Pollen media, Meristem refina.
3. **Todo criterio caduca.** Los objetos `MissionPatch`, `WeatherDigest` y `PolicyPacket` llevan TTL o ventana de validez.
4. **La lógica determinista decide; Gemma 4 escribe el rationale y ayuda a formular criterio.**
5. **El rechazo es una feature.** Cuando el sistema está inseguro, viejo o no es seguro, rechaza con motivo legible.

---

## Qué es real vs simulado

Sprout es un MVP de hackathon con fronteras explícitas.

### Caminos validados

- Bucle de decisión local de Rhizome sobre Jetson con Gemma 4 E2B vía `llama.cpp`.
- App Android de Pollen con flavors `demo` y `device`; la ruta `device` usa LiteRT-LM y Gemma 4 E4B.
- Ruta de voz de Pollen graba audio `.wav` y alimenta el contenido de audio al backend LiteRT-LM device.
- Evaluator local de Meristem y ruta de tool calling de Gemma 4 E4B.
- Firmware ESP32-S3 con protocolo serial, heartbeat, chequeos de seguridad, `WATER` en `DRY_RUN`, y prueba supervisada de hardware vía `PUMP_PULSE` en `TEST_ONLY`.
- Camino físico de banco con relé, bomba 12V, lectura de humedad de suelo y pulsos supervisados.

### Fronteras deliberadamente conservadoras

- `WATER` autónomo permanece conservador en `DRY_RUN` mientras se cierra la semántica de producción.
- La actuación física se demuestra mediante `PUMP_PULSE <ms>` supervisado como `TEST_ONLY`.
- La demo del navegador es un simulador determinista de contratos. La ejecución real de Gemma 4 ocurre en las rutas Android, Jetson y portátil documentadas en este repo.

Esta distinción es intencional. Sprout valora fronteras de seguridad honestas sobre teatro de demo.

---

## Cómo se usa Gemma 4

Sprout usa Gemma 4 de formas concretas y específicas por nodo:

### Rhizome — Gemma 4 E2B sobre Jetson

- Runtime: `llama.cpp`.
- Rol: rationale local y soporte de arbitración para una decisión ya acotada por gates deterministas.
- Restricción: Gemma 4 no autoriza agua.

### Pollen — Gemma 4 E4B sobre Android

- Runtime: Google AI Edge LiteRT-LM.
- Rol: entrada de audio multimodal, compilación de misión en lenguaje natural, refusal/retry para instrucciones poco claras.
- Output: objetos `MissionPatch` con caducidad validados antes de aplicación.

### Meristem — Gemma 4 E4B sobre portátil casero

- Runtime: `llama.cpp`.
- Rol: revisión de política asistida por tool calling y explicación.
- Output: objetos `PolicyPacket` duraderos para la siguiente ventana.

### Trabajo de configuración

Probamos configuraciones de prompt y runtime antes de congelar la ruta de demo: tamaño de contexto, presupuesto de output, comportamiento de thinking y estabilidad de salida estructurada. Un hallazgo útil fue que la latencia a menudo seguía a lo que el modelo escribía, no solo a lo que leía. Presupuestos de output más cortos mejoraron la usabilidad cuando el contrato se mantuvo estable.

Las notas completas de evaluación, los experimentos de runtime por nodo y las fuentes consultadas viven en [`research/`](research/) — incluyendo el comportamiento de la ventana de contexto de Gemma 4 en Ollama, el profiling sobre Jetson Orin Nano Super, la migración a LiteRT-LM en Pixel 10 Pro y la estrategia de localización de idioma para Pollen.

---

## Demo en vivo

La demo web pública es un **simulador determinista de contratos**:

- inspecciona decisiones de Rhizome;
- compila MissionPatches estilo Pollen;
- evalúa cambios de política estilo Meristem;
- ve TTLs, receipts y caminos de rechazo.

No pretende ejecutar Gemma 4 en el navegador. Existe para que cualquiera pueda experimentar la arquitectura sin hardware, descarga de modelo, APIs de nube ni login.

Las rutas reales de Gemma 4 local están documentadas en:

- `code/pollen/` — Android + LiteRT-LM;
- `code/rhizome/` — Jetson + `llama.cpp`;
- `code/meristem_node/` — portátil + `llama.cpp`;
- `hardware/firmware_esp32/` — coprocesador de seguridad físico.

---

## Reproducir en local

### Meristem, sin hardware

```bash
cd code/meristem_node
make run
make test
```

### Pollen Android, flavor demo

```bash
cd code/pollen
./gradlew assembleDemoDebug
./gradlew testDemoDebugUnitTest
```

El flavor demo usa inferencia mock determinista, así que funciona sin un archivo de modelo de 3 GB. Instala en cualquier Android 12+ (físico o emulador) con `adb install app/build/outputs/apk/demo/debug/pollen-demo.apk`.

### Pollen flavor device con Gemma 4 E4B

```bash
cd code/pollen
./gradlew assembleDeviceRelease
adb push gemma-4-E4B-it.litertlm /data/local/tmp/gemma-4-E4B-it.litertlm
```

Después abre Pollen en Android y selecciona la ruta del modelo local.

### Rhizome sobre Jetson

```bash
cd code/rhizome/jetson
./run_runtime.sh safe-cpu
./start_adapter.sh
./smoke_adapter.sh
```

### Firmware ESP32

```bash
cd hardware/firmware_esp32
idf.py set-target esp32s3
idf.py build
idf.py -p /dev/ttyACM0 flash monitor
```

Mira el README de cada componente para setup completo.

---

## Mapa del repo

| Path | Propósito |
|---|---|
| `SUBMISSION.md` | Camino rápido para evaluación: enlaces, evidencia, qué es real vs contrato |
| `writeup/` | Writeup del proyecto y notas de apoyo |
| `landing-demo/` | Demo pública determinista de contratos |
| `code/rhizome/` | Nodo de parcela Jetson, bucle de decisión local, fachada de sync |
| `code/pollen/` | Nodo móvil Android, ruta LiteRT-LM, voz → MissionPatch |
| `code/meristem_node/` | Cerebro lento portátil, evaluator, compositor de política |
| `hardware/firmware_esp32/` | Firmware del coprocesador de seguridad ESP32 |
| `docs/` | Arquitectura, specs, contratos de datos y reglas de seguridad |
| `bitacora/` | Diario de desarrollo en castellano y registro de decisiones |
| `research/` | Notas de evaluación, trabajo de configuración de modelo y fuentes |
| `video/` | Scripts del vídeo y notas de producción |

---

## Equipo

**zigiella** — desarrolladora humana en solitario, trabajando con un equipo coordinado de agentes de IA especializados. Cada agente tiene un rol definido, una identidad escrita, y autoría git versionada.

### Personas

| Rol | Persona |
|---|---|
| Product owner · hardware · cámara · voz humana | **Bea** |
| Cámara | **Ferran** |
| Caja Rhizome en el muro · lector del diario | **El padre de Bea** |

### Agentes IA

| Rol | Identidad |
|---|---|
| Tech lead · coordinación · constitución | **Cambium** |
| Dirección creativa · guion | **Corola** |
| Dirección de arte · cartelas · diagramas | **Venation** |
| Montaje · Remotion · CapCut · ElevenLabs | **Bract** |
| Nodo Pollen · Android · LiteRT-LM · Gemma 4 E4B | **Floema** |
| Firmware ESP32 · hard limits · capa de seguridad | **Xilema** |
| Nodo Meristem · tuning · `llama.cpp` · Gemma 4 E4B | **Meristem** |
| Nodo Rhizome · Jetson · `llama.cpp` · Gemma 4 E2B | **Endodermis** |

La metodología — repo-first, bitácoras escritas como contratos vinculantes, autoría git con identidad inline, mensajes de inicio de día con plantilla `Interrelaciones` explícita — está documentada en [`CONTRIBUTING.md`](CONTRIBUTING.md) y discutida en el [writeup](writeup/draft.md).

**Ubicaciones:** Castellar de n'Hug, Cataluña, España · Barcelona, Cataluña, España.

---

## Nota sobre idioma

Sprout se ha construido por un equipo que trabaja en castellano. **Las puertas públicas (este README, el [writeup](writeup/draft.md), la [guía de entrega](SUBMISSION.md), la [demo en vivo](https://sprout.zigiella.com), READMEs de nodos)** son English-first o bilingües. **Los artefactos internos (bitácoras, specs que evolucionan rápido, handoffs día a día, definiciones de rol de los agentes)** se mantienen en castellano por diseño — son evidencia del proceso de trabajo, no la interfaz pública.

Esto refleja la propia tesis del producto: **la inteligencia local debe encontrarse con las personas en el idioma y contexto donde el trabajo ocurre de verdad**. Los contratos y código de Sprout son inspeccionables sin necesidad de castellano; el diario de desarrollo preserva el castellano en el que el sistema fue realmente construido.

Si lees código o docs de nivel superior, el inglés te lleva a todas partes. Si quieres leer el proceso vivo, las bitácoras en castellano viven en `bitacora/`.

---

## Estado

Sprout es un MVP, no un controlador de riego de producción. Demuestra la arquitectura central:

- razonamiento Gemma 4 local por jurisdicción;
- nodo móvil Android con ruta LiteRT-LM;
- nodo edge con `llama.cpp`;
- cerebro lento de portátil con refinamiento de política;
- veto físico ESP32;
- receipts firmados, TTLs y caminos de rechazo.

El trabajo futuro incluye semánticas de `WATER` de producción con medición de caudal, riego multi-zona, alimentación solar, estaciones meteo locales, evidencia de visión y ajuste de lenguaje para vocabularios agrícolas locales.

---

## Licencia y atribución

Apache 2.0. Ver [`LICENSE`](LICENSE).

Créditos completos de modelos, runtimes, dependencias open source, assets de producción y marcas: [`CREDITS.md`](CREDITS.md).

Sprout usa modelos Gemma 4 de Google. Gemma is a trademark of Google LLC. Este proyecto no está afiliado ni respaldado por Google.
