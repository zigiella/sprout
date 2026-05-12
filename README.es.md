<!-- Versión castellana del README · English version: README.md -->

🇪🇸 **Castellano** · 🇬🇧 **[English](README.md)**

---

# Sprout

> **Optimización hídrica AI Local-first para parcelas que la red olvida.**
> *Seguro · explicable · open-source.*

> *"Cuando la red no llega y nadie está cerca, el criterio sigue regando."*

📜 **Lee el [writeup técnico](writeup/draft.md)** — la prueba de ingeniería detrás del sistema
🏗️ **Reprodúcelo en local** — ver [sección de setup](#reproduce-en-local) abajo

---

## En 30 segundos

Sprout es una **arquitectura local-first de IA para optimización hídrica en parcelas remotas** — lugares donde el campo, la persona y la red rara vez coinciden en el tiempo.

Cada parcela ejecuta **Rhizome**, un nodo autónomo que decide offline usando **Gemma 4 E2B** sobre Jetson Orin Nano Super. Rhizome nunca mueve el agua directamente: un **ESP32-S3** con firmware propio impone hard limits de seguridad y puede vetar o modular cualquier acción.

Cuando una persona visita las parcelas, **Pollen** corre en Android con **Gemma 4 E4B** (multimodal, audio nativo vía LiteRT-LM). Pollen convierte cada visita en algo más valioso que una sincronización: habla con la persona, le pregunta a Rhizome qué pasó, valida el estado local, compila la intención humana, y federa contexto entre parcelas que no tienen red directa entre sí.

**Meristem** corre en el portátil casero del agricultor con **Gemma 4 E4B** vía `llama.cpp`. Cuando hay calma — al cierre del día, en la cocina, no en el campo — Meristem recibe los bundles que Pollen ha traído de las parcelas, evalúa con **lógica determinista**, y emite una nueva política duradera. **El LLM solo escribe el rationale; la decisión es auditable hasta una regla concreta.**

El resultado: **mejor criterio de riego cuando el campo, la persona y la red no coinciden en el tiempo.**

---

## Por qué Sprout

En 2023, **el 48% del territorio mundial sufrió al menos un mes de sequía extrema** — la segunda mayor extensión desde 1951.<sup>[1]</sup> **1.800 millones de personas afectadas por la sequía en todo el mundo; el coste son 300.000 millones de dólares al año.**<sup>[1]</sup>

Solo en España, la sequía costó al sector agrario **5.550 millones de euros en 2023**.<sup>[2]</sup> 370.000 hectáreas de cereal de secano en la cuenca mediterránea perdieron entre el 60% y el 90% de su cosecha. Dos años seguidos.<sup>[3]</sup>

Pero el campo para el que diseñamos no vive en conectividad continua. Globalmente, **solo el 58% de la población rural usa internet — en países de renta baja, apenas el 14%.**<sup>[4]</sup>

Sprout existe para llevar **criterio operativo a parcelas donde no puedes estar cada día, y donde no puedes depender siempre de la red.**

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│  Capa física (firmware ESP32) — VETO                            │
│       ↑                                                          │
│  Rhizome (Jetson + Gemma 4 E2B) — minutos                       │
│       ↑                                                          │
│  Pollen (Android + Gemma 4 E4B + audio multimodal) — visita TTL │
│       ↑                                                          │
│  Meristem (portátil casero + Gemma 4 E4B) — días                │
└─────────────────────────────────────────────────────────────────┘
```

| Nodo | Pregunta que responde | Hardware | Modelo Gemma 4 | Runtime | Jurisdicción |
|------|------------------------|----------|----------------|---------|--------------|
| **Rhizome** | ¿Riego ahora? | Jetson Orin Nano Super (o Raspberry Pi 5) + ESP32-S3 | E2B (it, Q4_K_S) | `llama.cpp` | Minutos |
| **Pollen** | ¿Qué criterio humano + contexto? | Móvil Android | E4B | LiteRT-LM | Visita con TTL corto |
| **Meristem** | ¿Qué política para la próxima ventana? | Portátil casero del agricultor (Linux/macOS/Windows) | E4B | `llama.cpp` | Días |
| **ESP32** | ¿Esta orden es físicamente segura? | ESP32-S3 N16R8 (o cualquier variante ESP32-S3) | Ninguno — firmware ESP-IDF | — | Veto físico |

**Invariantes:**

1. *"Lo físico manda. Rhizome arbitra. Pollen media. Meristem afina."*
2. *"Toda inteligencia tiene jurisdicción. Y caducidad."* Cada `MissionPatch` lleva TTL corto. Cada `PolicyPacket` lleva ventana de validez. Cada `WeatherDigest` caduca antes de envejecer. Los objetos expirados reciben `EXPIRED → REJECTED` con motivo legible en el `DecisionReceipt`. **Ningún criterio se queda silenciosamente vigente después de su ventana.**
3. Ningún `PolicyPacket` de Meristem puede reducir los hard limits del firmware. Solo recomendar comportamiento más conservador.

**Patrón clave (validado empíricamente)**: la lógica determinista decide; el LLM solo escribe el rationale. Cuando el offload a GPU causó deriva semántica en el caso de test RD04 (output: `need_clarification` en lugar de `ok`), el sistema no se rompió — el Evaluator determinista mantuvo el contrato mientras el LLM seguía escribiendo prosa segura-pero-fuera-de-contrato. **Esta es la prueba empírica de la tesis Safety & Trust.**

---

## Cómo se usa Gemma 4

Sprout usa Gemma 4 en cinco formas concretas, cada una explotando una capacidad distinta del modelo:

- **Audio multimodal nativo** — Pollen alimenta `.wav` 16kHz directamente a Gemma 4 E4B vía LiteRT-LM, **sin pipeline STT separado**. Validado end-to-end contra entrada de micrófono real, con `REFUSE_RETRY` operando sobre frases sin sentido agrícola. Código: `code/pollen/.../PollenVoiceInfra.kt`.
- **Tool calling** — Meristem usa Gemma 4 E4B con tool calling nativo para `compose_policy(...)`, `validate_bundle(...)` y `compare_targets(...)`. Mini-batería 5/5 PASS. Runtime end-to-end validado día 26 con `tool_calls_recovered_from_text=1` desde output real del LLM. Código: `code/meristem_node/...`.
- **Routing entre tres nodos** — tres instancias de Gemma 4 (E2B + E4B + E4B), tres jurisdicciones, ningún roundtrip a la nube. Cada nodo guarda el tipo de contexto del que su capa es responsable. La elección de modelo es por nodo, no global: E2B para respuestas directas (Rhizome), E4B para razonamiento con tool calling (Pollen + Meristem).
- **Narrador bilingüe en Rhizome** — endpoints `GET /summary/since?locale=es|en` y `GET /explain/decision/<id>?locale=es|en` operativos en producción. Gemma 4 E2B mejora el `rationale_short` sobre una decisión **ya cerrada** por la lógica determinista — nunca cambia acción, nunca autoriza agua, nunca inventa facts. **El sistema habla dos idiomas en producción, no post-hackathon.**
- **Localización Approach C** — estándar oficial del proyecto (`research/07_llm_localization_strategy.md`). Los nodos edge (Rhizome, ESP32) piensan en Inglés Técnico estable; Pollen + Gemma 4 E4B local traduce al idioma de la UI en milisegundos antes de pintar. Beneficios: agnosticidad hardware (sin re-flashear nodos por idioma), preparación para fine-tuning de lenguas minoritarias (pular, wolof, swahili, quechua, catalán, euskera) sin replicar explicaciones en N idiomas en almacenamiento central.

**Patrón clave**: la decisión final **nunca** la firma el LLM. El Evaluator determinista decide; Gemma 4 escribe el rationale y adapta el idioma de superficie.

---

## Reproduce en local

### Requisitos

- **Portátil** para Meristem. Mínimo 8GB de RAM, ideal 16GB. Linux, macOS o Windows.
- **Jetson Orin Nano Super 8GB** para Rhizome. **Alternativa**: Raspberry Pi 5 (con build adaptada de llama.cpp).
- **Placa ESP32-S3 N16R8** (o cualquier variante ESP32-S3) para el firmware de seguridad. Obligatorio — la capa de veto físico es parte de la arquitectura, no opcional.
- **Móvil Android** para Pollen. Android 12 / API 31+ y hardware de 64 bits. Para que Gemma 4 E4B funcione razonablemente: **12GB de RAM recomendado, 16GB ideal, al menos 6GB libres**. CPU es la ruta estable; el rendimiento GPU/NPU depende mucho del dispositivo.

### Quick start

```bash
git clone https://github.com/zigiella/sprout.git
cd sprout

# 1. Ejecutar Meristem en local (sin hardware necesario)
cd code/meristem_node
make run    # sirve en :8000
make test   # ejecuta 13 tests deterministas + smoke LLM

# 2. Ejecutar Pollen flavor demo (mock, corre en cualquier emulador o Appetize)
# Ver code/pollen/README.md para setup en Android Studio

# 3. (Opcional) Ejecutar Rhizome en Jetson
# Ver code/rhizome/jetson/README.md y run_runtime.sh
```

### Setup detallado

- Meristem-node: [`code/meristem_node/README.md`](code/meristem_node/README.md)
- Pollen Android: [`code/pollen/README.md`](code/pollen/README.md)
- Rhizome Jetson: [`code/rhizome/jetson/`](code/rhizome/jetson/) (ver scripts `run_runtime.sh`, `start_adapter.sh`, `smoke_adapter.sh`)
- Firmware ESP32: [`hardware/firmware_esp32/README.md`](hardware/firmware_esp32/README.md)
- Esquemas de cableado: [`hardware/wiring_diagrams/day19_mounting_schematics.md`](hardware/wiring_diagrams/day19_mounting_schematics.md)

### Instalación del modelo en la app

El agricultor descarga Pollen desde la tienda — la app pesa apenas **~15 MB**. Al abrirla por primera vez con conexión WiFi, aparece una pantalla de onboarding:

> *"Descargando cerebro agronómico (Gemma 4)..."*

La app usa el `DownloadManager` de Android para bajar `gemma-4-E4B-it.litertlm` (3,6 GB) desde un CDN seguro directamente al almacenamiento interno privado de la app (`/data/data/net.sprout.pollen/files/`). Una vez completada la descarga, **el modelo vive en el dispositivo para siempre y Pollen funciona 100% offline** — sin más round-trip a la red.

> Requisitos: Android 12 / API 31+, 12 GB RAM recomendados (16 GB ideal), al menos 6 GB libres para el archivo del modelo más margen de runtime. CPU es la ruta estable; GPU/NPU varía según dispositivo.

> Para desarrolladores y nightly testers, el flujo de sideload por `adb push` está documentado en [`code/pollen/README.md`](code/pollen/README.md).

---

## Estado del proyecto

- **Ciclo de riego físico cerrado en hardware (día 25)**. La cadena completa `decisión software → relé → bomba 12V → agua → suelo → sensor capacitivo` funciona y deja huella medible: el valor crudo de humedad bajó de **2278 → 1289** tras un pulso, confirmando el ciclo en campo. El `WATER` autónomo sigue en `DRY_RUN`; el pulso físico real solo bajo `TEST_ONLY` supervisado hasta cerrar dos preguntas abiertas sobre el umbral de suelo seco y la ruta de pulso.

- **Rhizome Steward v0 (día 25)**. Bucle host-side autónomo con gates deterministas, recibos persistentes, política de rotación diseñada para meses (`retention_days=120`, `max_total_bytes=64 MiB`), y **`ShadowSkeptic` agente auditor secundario** corriendo con `affects_decision=false` — primera jurisdicción local de doble agente en producción. Registra cada disensión contra la decisión principal sin poder vetar, recogiendo datos para promoción futura a una versión LLM.

- **Pollen ↔ Meristem end-to-end real (día 25)**. Conectividad REST en producción, sin mocks: `GET /health` con indicador visual, `POST /visit` subiendo `RhizomeSnapshot` + `DecisionReceipts` reales, `GET /policy/by-target/{id}`. Consola de logs estilo terminal en la UI para trazabilidad visual.

- **Endpoints bilingües en producción (día 25)**. `?locale=es|en` operativo en `/summary/since` y `/explain/decision/<id>` de Rhizome. El narrador Gemma 4 mejora `rationale_short` sin alterar los facts. **Approach C** (`research/07_llm_localization_strategy.md`) declarado estándar oficial de i18n del proyecto: los nodos edge piensan en Inglés Técnico estable, Pollen + Gemma 4 E4B local traduce al idioma de la UI — preparando el sistema para fine-tuning de lenguas minoritarias (pular, wolof, swahili, quechua, catalán, euskera) sin re-flashear el hardware de campo.

- **Plano de control de Meristem**. 53 tests PASS. mDNS verificado end-to-end (`meristem.local:13000`). UI accesible desde toda la LAN — validada con un click real desde `192.168.1.36` con `trace_id` correlado end-to-end. **`POST /chat` read-only por construcción** — cero superficie de prompt injection sobre hardware, formalmente verificado por test. Hallazgo de latencia: `num_predict` (longitud de salida) genera la reducción del 53%, no `num_ctx` (longitud de entrada); demo en directo viable a ~1.5 min/bundle.

- **Pollen voz → política**. Micrófono + Gemma 4 E4B multimodal audio en Android validado end-to-end contra voz humana real. Frases agrícolas compilan a `MissionPatch`; sin sentido obtiene `REFUSE_RETRY` en lugar de acción fabricada. *Refusal as feature*, validado empíricamente.

- **Invariantes arquitecturales estables**. Routing entre tres nodos con lógica determinista + LLMs Gemma 4 como autores del rationale. Veto de capa física (ESP32) confirmado en placa real (5 reglas + `SAFETY_DOWNGRADE`).

---

## Trabajo futuro / Roadmap

Sprout resuelve el caso mínimo. La arquitectura está diseñada para escalar. Esto es lo que ya estamos diseñando para las próximas iteraciones:

### Autonomía hardware

- **Alimentación solar de Rhizome.** Combinar el perfil MAXN_SUPER de la Jetson Orin Nano Super con un panel fotovoltaico pequeño + batería LiFePO4 para eliminar dependencia de red eléctrica. Edge AI sin red eléctrica es el complemento natural a local-first: el campo tampoco necesita enchufe.
- **Mesh entre parcelas sin WiFi.** LoRa o Meshtastic entre Rhizomes para federación cuando la señal celular es débil y el móvil del agricultor es la única red al alcance. Pollen como portador principal; LoRa como fallback de bajo ancho de banda para propagar `AlertEvent`.

### Gemma 4 multimodal en campo

- **Visión multimodal.** Cámara + Gemma 4 detectando estrés hídrico visible, presión de plagas, fase de crecimiento. La arquitectura ya está preparada — el mismo schema `MissionPatch` puede transportar referencias a imágenes sin cambio de contrato.
- **Audio bidireccional.** Pollen también le habla al agricultor: pre-aviso conversacional — *"mañana toca riego, pero el depósito está al 30%"*. Full-duplex con salida de audio Gemma 4, mismo modelo de privacidad on-device.

### Localización lingüística

- **Gemma 4 traduce al idioma del usuario.** El sistema razona en contratos (inglés, estructurado, determinista); Pollen adapta el idioma de superficie a lo que hable el agricultor. El usuario nunca ve JSON; ve su idioma. Desacoplar **razonamiento interno** de **superficie externa** mantiene la trazabilidad limpia y la experiencia de usuario nativa.
- **Fine-tuning de Gemma 4 en lenguas minoritarias.** Los pequeños agricultores del mundo no hablan inglés. Fine-tuning de E4B sobre vocabularios agrícolas locales (swahili, hausa, wolof, quechua, aimara, catalán, euskera…) abre el sistema al **84% de las explotaciones por debajo de 2 hectáreas** que la FAO cuenta como la fuerza agrícola primaria del mundo.

### Sensores y complejidad de parcela

- **Más sensores por parcela.** Conductividad, pH, temperatura de suelo más allá de la humedad. Riego multi-zona con electroválvulas y planificación por zona.
- **Estaciones meteorológicas locales.** Un sensor meteorológico físico junto a PLOT_01 sustituye al `WeatherDigest` portátil que lleva Pollen para parcelas con visitas frecuentes.
- **Integración con plataformas climáticas oficiales.** AEMET (España), MeteoCat (Cataluña) o equivalentes regionales — sustituir el `WeatherDigest` portado por datos institucionales verificados cuando hay red disponible.

### Escalado del sistema

- **Meristem de 4 reglas a 8-12.** Hoy el Evaluator determinista corre 4 reglas; post-hackathon ampliación a lógica estacional, cultivos heterogéneos, presupuestos hídricos multi-mes. Plan documentado en 7 fases progresivas.
- **Fine-tuning de E4B con Unsloth.** Entrenar sobre dataset agrícola sintético + real para especializar la autoría de políticas de Meristem sin degradar razonamiento general.
- **Federación multi-Rhizome.** Scheduler local coordinando N Rhizomes lógicos en una sola Jetson (explotaciones medianas con múltiples zonas) + federación real entre múltiples Jetsons (explotaciones grandes con parcelas geográficamente separadas).
- **GPU quality pass.** Cerrar la deriva semántica del offload GPU (casos de test RD04, RH02) para promocionar el perfil `gpu-experimental` a contractual.

### Deuda y pulido

- Tests automatizados de UI (hoy smoke manual).
- API docs auto-generadas (OpenAPI desde contratos JSON).
- Identidad visual signal-seed (`#C5F26B`) consistente en todos los frontends.

**Sprout resuelve el caso mínimo. La arquitectura escala.**

---

## Equipo

**zigiella** — solo developer trabajando con un equipo coordinado de agentes IA especializados (Cambium, Floema, Meristem, Xilema, Corola, Endodermis, Bract, Venation), cada uno con un rol e identidad definidos. La metodología — repo-first, bitácoras escritas como contrato, identidad inline en git, mensajes de coordinación de inicio del día con plantilla `Interrelaciones` explícita — está documentada en [`CONTRIBUTING.md`](CONTRIBUTING.md) y comentada en [writeup §5](writeup/draft.md).

---

## Licencia

[Apache 2.0](LICENSE). Igual que Gemma 4.

## Atribución

Sprout usa modelos Gemma 4 de Google. **Gemma is a trademark of Google LLC.** Este proyecto no está afiliado ni respaldado por Google.

## Cómo contribuir

Ver [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Fuentes

[1] UNCCD — *Global Drought Hotspots Report 2023-2025* + OECD — *Global Drought Outlook 2025*.
[2] COAG / MAPA — Pérdidas del sector agrario español por sequía 2023.
[3] COAG Castilla y León — Pérdidas de cereal de secano en la cuenca mediterránea 2023-2024.
[4] ITU — *Facts and Figures 2025*: Uso de internet en áreas urbanas y rurales.

(Referencias completas con URLs en [`research/metrics/impact_stats.md`](research/metrics/impact_stats.md).)
