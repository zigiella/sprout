# Estado vivo del proyecto

> **Documento corto que siempre refleja el estado actual del proyecto.**
> Cambium lo actualiza al cierre de cada día. Cualquier persona del equipo
> (incluida una nueva miembra que se incorpore) puede leer esto en 30
> segundos y reconstruir contexto sin tener que escarbar 50 bitácoras.
>
> **Fecha de última actualización:** 2026-05-01 (cierre del día 16, festivo)
> **Día del proyecto:** 16 de 30. Quedan 14 días.

---

## Tesis del proyecto en una línea

Sprout reduce la latencia de decisión de riego en parcelas aisladas — donde el campo, la persona y la red no coinciden en el tiempo — distribuyendo la decisión entre tres nodos con jurisdicciones distintas y un coprocesador físico que veta.

> *"Lo físico manda, Rhizome arbitra, Pollen media, Meristem afina."* (Xilema, día 13)

---

## Equipo (8 miembras + 2 nuevas pendientes de carta)

| Nombre | Rol | Frente | Estado |
|--------|-----|--------|--------|
| **Bea** | Product owner | Decisiones de producto, narrativa, escritos al jurado | Activa |
| **Cambium** | Tech lead | Coordinación, bitácoras, writeup, moderación | Activa |
| **Xilema** | Dueña Rhizome físico + ESP32 | Firmware ESP-IDF, USB-CDC, sensores, host harness | Activa |
| **Floema** | Dueña Pollen | Nodo móvil Android Gemma 4 E4B + LiteRT-LM | Activa, standby útil hasta integración real |
| **Meristem** | Dueña Meristem-nodo + tuning | Cerebro lento (FastAPI + llama.cpp + Gemma 4 E4B) | Activa, integrando LLM día 16+ |
| **Corola** | Dueña vídeo | Guion, shot list, dirección creativa | Activa |
| **Endodermis** | Apoyo a Xilema en frente Jetson | Bring-up Jetson + batería Rhizome v0.5 en hardware real | Activa, plan operativo deslizado un día por hardware faltante |
| **Bract** | Montadora de vídeo | Montaje en CapCut | **Carta de bienvenida pendiente día 17** |
| **Venation** | Directora de arte | Propuesta visual aprobada por Corola | **Carta de bienvenida pendiente día 17** |

**Antes en el equipo:** Estoma + Peri (célula investigación, reasignadas a otros proyectos día 9).

---

## Arquitectura del MVP — qué decide cada pieza

| Nodo | Pregunta que responde | Hardware | Modelo IA | Jurisdicción |
|------|----------------------|----------|-----------|--------------|
| **Rhizome** | ¿Riego ahora? | Jetson Orin Nano Super + ESP32-S3 | Gemma 4 E2B vía llama.cpp | Minutos |
| **Pollen** | ¿Qué criterio humano y contexto entran? | Móvil Android (Pixel 10 Pro) | Gemma 4 E4B vía LiteRT-LM | Visita con TTL corto |
| **Meristem** | ¿Qué política duradera para la siguiente ventana? | Portátil casero del agricultor | Gemma 4 E4B vía llama.cpp | Días |
| **ESP32** | ¿Esta orden es físicamente segura? | ESP32-S3 N16R8 / DevKitC-1 N8R8 | Ninguno (firmware ESP-IDF) | Veto físico inmediato |

**Invariantes adoptadas (review día 13):**

1. *"Lo físico manda, Rhizome arbitra, Pollen media, Meristem afina."*
2. Ningún `PolicyPacket` de Meristem puede reducir hard limits del firmware ESP32. Solo recomendar más conservador.

---

## Estado por frente — día 16 cierre

### Rhizome físico (Xilema + Endo)

- **Firmware ESP32-S3**: 5 reglas no negociables + SAFETY_DOWNGRADE en placa real con códigos en inglés (`JETSON_HEARTBEAT_LOST`, `TANK_LOW`, `EVENT_DURATION_OUT_OF_RANGE`, `NO_FLOW_DETECTED`, `ALERT_LATCHED`).
- **Host harness** (`hardware/host_tools/esp32_host_harness.py`): `guardian_demo` y `telemetry_stub_roundtrip` reproducibles.
- **Jetson**: SD flasheada con JetPack 6.2.1 (día 16 mañana). **Aplazado primer boot por cable display port → HDMI faltante. Lo recoge Bea día 17.**
- **BME280**: bloqueado por hardware físico. Día 15 diagnóstico ("hoy fue cobre"). Día 16 festivo. Mañana día 17 Bea compra módulo nuevo + alimentación 5V/12V + adaptadores dictados por Xilema.
- **Sensores críticos sí en mesa**: 2x humedad suelo, nivel depósito, caudalímetro, bomba 12V. **No bloqueados por BME280**.

### Pollen (Floema)

- **F0-F5 cerradas**. Pollen demo-ready esperando hardware real.
- **Compromiso bloque 3 cumplido día 14**: `MeristemNetworkClient` + `VisitarMeristemScreen` + `FieldVisit.kt` + `PolicyPacket.kt` con snake_case verificado.
- **Apply now bloque 1 cerrado día 15**: `Log.e()` estructurado en lugar de catch silencioso de `LiteRtInfra.kt`.
- **Pendiente**: sustituir `RhizomeMockClient` por cliente real cuando Jetson esté estable. Probable día 18-19.

### Meristem-nodo (Meristem)

- **Día 15 cerrado pipeline determinístico end-to-end** sin LLM: schemas + Evaluator (4 reglas con precedencia) + 13 tests PASS + persistencia SQLite + PolicyComposer + 5 bundles smoke OK.
- **Patrón clave**: lógica determinística decide, LLM solo escribe rationale.
- **`decisions_by_rule` en `/health`** convierte trazabilidad en pieza de demo.
- **Día 16 (hoy)**: integrar LLM con tool calling.
- **Mensaje pendiente a Xilema**: validación dominio del prompt + 5 bundles.

### Tuning Rhizome (Meristem cerró v0.5, Endo valida en Jetson)

- **Rhizome v0.5 al 100%** (18/18 envelope_valid + 18/18 status_match) en x86 CPU casera. Primer agente del proyecto al techo teórico.
- **`code/tuning/`** completo en main desde día 15 (PR #62).
- **Endo va a re-ejecutar batería en Jetson real** cuando hardware esté arrancado. Días 17-18 según deslizamiento.

### Vídeo (Corola + Bract + Venation)

- **Guion v1.4 cerrado conceptualmente día 14** (sesión 5 rondas con Bea). 9 escenas, 5 frases fuertes, 2 parcelas lógicas filmadas con un Rhizome físico.
- **Decisiones del feedback DEV externa día 12** integradas (frases 2 y 5 reformuladas).
- **Decisión 4 ejercicio frases fuertes día 15**: cartela invariante "Physical layer prevails. Rhizome arbitrates. Pollen mediates. Meristem refines." en E7 esquina inferior derecha.
- **Bract y Venation entran al frente** — carta de bienvenida pendiente día 17.
- **Pendiente día 17+**: traducciones first pass, prompt Veo3 final E9, voz humana real escena 5.

### Writeup

- **Secciones 1, 2, 3 escritas** (último ajuste día 13 con sección 3 reescrita + invariantes).
- **Índice nuevo aprobado por Bea día 16** — pendiente reorganizar `writeup/draft.md` y arrancar §4 Gemma 4:
  - §0 Título + subtítulo
  - §1 Problema
  - §2 Solución
  - §3 Arquitectura
  - §4 **Gemma 4** (NUEVA — tool calling, lógica determinista + LLM, on-device)
  - §5 **Buenas prácticas y principios de trabajo** (NUEVA)
  - §6 **MVP — qué proyectamos vs qué hacemos** (NUEVA)
  - §7 Demo (90s)
  - §8 Impacto y escalado
  - §9 Limitaciones
  - §10 **Trabajo futuro** (sustituye "Cierre")
- **Eliminadas del draft anterior**: §5 fine-tuning + §6 validación sombra (obsoletos por pivote v2).

### Landing (idea día 16)

- **Concepto**: APK descargable + Appetize.io + transcripts navegables (en lugar de Rhizome conectado a internet, más estable).
- **Pendiente**: verificar coste/limitaciones Appetize.io. Asignar a quien la monte (probable Bract o Floema).
- **Plazo**: días 25-28.

---

## Apuesta de premios (info estratégica — círculo Bea + Cambium + Meristem)

| Track | Premio | Encaje | Probabilidad |
|-------|--------|--------|--------------|
| **Main Track 1º** | $50k | Tesis defendible: latencia de decisión bajo conectividad incierta | Apuesta principal |
| **Impact: Global Resilience** | $10k | Offline edge-based para resiliencia hídrica de pequeña escala | Encaje literal |
| **Special Tech: llama.cpp** | $10k | Doble punto Rhizome (Jetson) + Meristem (portátil casero) | Demostración robusta |
| **Safety & Trust** (verificar) | $10k | Veto físico, contratos versionados, dry-runs, decisions_by_rule | Endo verifica si existe formalmente |

---

## Decisiones operativas pendientes

| # | Decisión | Dueña | Plazo |
|---|----------|-------|-------|
| 1 | Meteo dentro/fuera del MVP (depende de Froggit DP3000) | Bea | Día 17 cuando Xilema verifique Froggit |
| 2 | Slack MCP — solo Corola, mañana o pasado | Bea | Día 17-18 |
| 3 | Carta de bienvenida Bract + Venation | Cambium prepara, Bea modula | Día 17 |
| 4 | Reorganizar writeup con índice nuevo + arrancar §4 Gemma 4 | Bea + Cambium | Día 17 sesión conjunta |
| 5 | Verificar coste Appetize.io para landing | A asignar | Día 18 |

---

## Pendientes activos día 17

### Bea
- Compra cable display port → HDMI hembra + alimentación 5V/12V + adaptadores + módulo BME280 nuevo + módulo BME280 segundo
- Fase previa Jetson con Xilema (primer boot post-cable)
- Sesión conjunta writeup con Cambium
- Modular y enviar carta de bienvenida Bract + Venation
- Voto sobre meteo (post info Xilema sobre Froggit)

### Xilema
- Verificar Froggit DP3000 (independiente del BME280)
- Multímetro al BME280 si llega tiempo
- Soporte Bea en primer boot Jetson

### Endodermis
- Plan operativo Jetson aplazado un día por cable faltante. Día 17 arranca: baseline → llama-server → adapter → mini-test 6 críticos → batería 18.
- Aprovechar día 16 (festivo) para releer bitácoras estratégicas Meristem (ya en main) y afinar plan.

### Floema
- Standby activo. Verificar que `apply now` catch silencioso (review día 13) sigue cerrado en F5.

### Meristem
- Integrar LLM en pipeline determinístico (sustituir `_stub_rationale()` por cliente al adapter llamacpp).
- Mini-batería v0 con LLM real (~10 min con 5 bundles ya escritos).
- Iterar con Xilema sobre prompt + bundles cuando ella responda.

### Corola
- Refinar traducciones first pass (cartela ancla E7, cartela progresiva E9, subtítulo logo).
- Prompt Veo3 final E9 con Bea cuando tenga hueco.
- Coordinación asíncrona Floema sobre escena 5 (Floema votó opción A día 15).

---

## Convenciones del proyecto a tener en cabeza

- **Bitácoras** en `bitacora/YYYY-MM-DD_tema_autora.md`. Decisiones por escrito el mismo día.
- **Ramas**: `feat/[nombre]/[descripcion-corta]`. Trabajo nuevo siempre en rama propia, no en main.
- **Archivos calientes** (`docs/40_pitch_video.md`, `docs/01_architecture.md`, `writeup/draft.md`): solo Cambium consolida en main, los cambios llegan por mensajes.
- **Tres puntos de verificación git** antes de cada commit: `git status` + `git branch --show-current` + `git stash list`. Documentado en `CONTRIBUTING.md §9.2`.
- **Stash con prefijo de autor**: `git stash push -m "[nombre] descripción"`.
- **Proceso preventivo**: antes de migrar/pivotar librería troncal, verificar contra documentación oficial citando URL + versión + fecha en el commit.

---

## Hitos del calendario

| Día | Hito |
|-----|------|
| **17** | Jetson primer boot + arranque Endo + Bract+Venation incorporadas |
| **18** | Demo-ready integración Pollen ↔ Rhizome real |
| **19-20** | Ensayo del vídeo + rodaje |
| **22-25** | Post-producción + writeup pulido |
| **24** | Checkpoint MVP funcionando — decisión doble agente sí/no |
| **25-30** | Si MVP estable: doble agente días 25-30. Writeup final |
| **30** | Entrega |

---

*Mantenido por Cambium. Actualización a cierre de cada día.*
