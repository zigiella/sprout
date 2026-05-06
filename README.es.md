<!-- Versión castellana del README · English version: README.md -->

🇪🇸 **Castellano** · 🇬🇧 **[English](README.md)**

---

# Sprout

> **Decisiones de riego con AI Local-first.**
> *Seguro · explicable · open-source.*

> *"Cuando la red no llega y nadie está cerca, el criterio sigue regando."*

📜 **Lee el [writeup técnico](writeup/draft.md)** — la prueba de ingeniería detrás del sistema
🏗️ **Reprodúcelo en local** — ver [sección de setup](#reproduce-en-local) abajo

---

## En 30 segundos

Sprout es una **arquitectura local-first de IA para decisiones de riego en parcelas remotas** — lugares donde el campo, la persona y la red rara vez coinciden en el tiempo.

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
2. Ningún `PolicyPacket` de Meristem puede reducir los hard limits del firmware. Solo recomendar comportamiento más conservador.

**Patrón clave (validado empíricamente)**: la lógica determinista decide; el LLM solo escribe el rationale. Cuando el offload a GPU causó deriva semántica en el caso de test RD04 (output: `need_clarification` en lugar de `ok`), el sistema no se rompió — el Evaluator determinista mantuvo el contrato mientras el LLM seguía escribiendo prosa segura-pero-fuera-de-contrato. **Esta es la prueba empírica de la tesis Safety & Trust.**

---

## Cómo se usa Gemma 4

- **Audio multimodal nativo** — Pollen alimenta `.wav` 16kHz directamente a Gemma 4 E4B vía LiteRT-LM, **sin pipeline STT separado**. Reemplazó al `SpeechRecognizer` de Android tras inestabilidad extensa. Código: `code/pollen/.../PollenVoiceInfra.kt`.
- **Tool calling** — Meristem usa Gemma 4 E4B con tool calling nativo para `compose_policy(...)` y validación de bundles. Mini-batería 5/5 PASS. Código: `code/meristem_node/...`.
- **Routing entre tres nodos** — tres instancias de Gemma 4 (E2B + E4B + E4B), tres jurisdicciones, ningún roundtrip a la nube. Cada nodo guarda el tipo de contexto del que su capa es responsable.
- **Perfil `safe-cpu` contractual** — Rhizome corre Gemma 4 E2B-it Q4_K_S en CPU del Jetson (validado 18/18 en batería de tests). El offload GPU funciona (36/36 capas) pero la calidad aún no es contractual.

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

---

## Estado del proyecto

- **MVP**: los cuatro nodos operativos. Cadena Pollen ↔ Rhizome real validada. Veto físico ESP32 confirmado en placa real. Integración LLM Meristem con tool calling cerrada.
- **Arquitectura**: invariantes estables. Routing entre tres nodos con lógica determinista + LLMs Gemma 4 como autores del rationale.

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
