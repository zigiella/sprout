# Estado vivo del proyecto

> **Documento corto que siempre refleja el estado actual del proyecto.**
> Cambium lo actualiza al cierre de cada día. Cualquier persona del equipo
> (incluida una nueva miembra que se incorpore) puede leer esto en 30
> segundos y reconstruir contexto sin tener que escarbar 50 bitácoras.
>
> **Fecha de última actualización:** 2026-05-02 (cierre del día 17)
> **Día del proyecto:** 17 de 30. Quedan 13 días.

---

## Tesis del proyecto en una línea

Sprout reduce la latencia de decisión de riego en parcelas aisladas — donde el campo, la persona y la red no coinciden en el tiempo — distribuyendo la decisión entre tres nodos con jurisdicciones distintas y un coprocesador físico que veta.

> *"Lo físico manda, Rhizome arbitra, Pollen media, Meristem afina."* (Xilema, día 13)

> *"Cuando la red no llega, el criterio sí."* (Bea, día 16) ≈ *"When the network is absent, local criteria still irrigate."* (Venation, día 16, sin coordinación previa)

> *"Yo somos todas nosotras. Por eso firmo como zigiella."* (Bea, día 17) — frase para writeup §5.

---

## Equipo (9 miembras activas)

| Nombre | Rol | Frente | Estado |
|--------|-----|--------|--------|
| **Bea** | Product owner | Decisiones de producto, narrativa, escritos al jurado, cara del vídeo | Activa |
| **Cambium** | Tech lead | Coordinación, bitácoras, writeup, moderación | Activa |
| **Xilema** | Dueña Rhizome físico + ESP32 | Firmware ESP-IDF, USB-CDC, sensores, host harness | Activa |
| **Floema** | Dueña Pollen + dueña live demo | Nodo móvil Android Gemma 4 E4B + LiteRT-LM. APK + Appetize.io + transcripts | Activa, F5+Rhizome en `feat/pollen-f5-rhizome` |
| **Meristem** | Dueña Meristem-nodo + tuning | Cerebro lento (FastAPI + llama.cpp + Gemma 4 E4B) | Activa, LLM integrado día 16 + multi-Rhizome v0 |
| **Corola** | Dueña vídeo | Guion, shot list, dirección creativa | Activa, script + shot list v1.6 en `feat/corola-guion-v1` (pendiente merge) |
| **Endodermis** | Apoyo a Xilema en frente Jetson | Bring-up Jetson + batería Rhizome v0.5 en hardware real | Activa, **Rhizome v0.5 al 100% en Jetson real** día 17 (CPU-only) |
| **Bract** | Montadora de vídeo | Montaje en CapCut, doble export ES/EN-dub | Activa día 17, PR #65 (DRAFT) con 9 incoherencias detectadas |
| **Venation** | Directora de arte | Sistema visual del proyecto, design pack | Activa día 17, PR #66 mergeado a main, signal.seed blindado como regla |

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

**Patrón Meristem confirmado día 16:** *"lógica determinística decide, LLM solo escribe rationale"* — con LLM real integrado y validado en 5/5 bundles (cierre día 16). Multi-Rhizome simulado v0 funcional sin haberlo planeado.

---

## Estado por frente — día 17 cierre

### Rhizome físico (Xilema + Endo)

- **Firmware ESP32-S3**: 5 reglas no negociables + SAFETY_DOWNGRADE en placa real con códigos en inglés (`JETSON_HEARTBEAT_LOST`, `TANK_LOW`, `EVENT_DURATION_OUT_OF_RANGE`, `NO_FLOW_DETECTED`, `ALERT_LATCHED`).
- **Host harness** (`hardware/host_tools/esp32_host_harness.py`): `guardian_demo` y `telemetry_stub_roundtrip` reproducibles.
- **Jetson día 17 cierre**: cable display port → HDMI hembra resuelto en Diotronic muy temprano. Fase previa Jetson cerrada por Bea + Xilema. **Endodermis cerró batería 18/18 PASS en Jetson real con Rhizome v0.5 vía llama.cpp + adapter llamacpp**:
  - Mini-test crítico frío: 6/6
  - Repetición caliente: 6/6
  - Batería completa combinada: 18/18
  - Sin OOM, sin truncamiento, sin fences
  - **Riesgo apuntado**: GPU offload falla por asignación CUDA/NvMap. Runtime estable actual = CPU-only. No bloqueante para demo. Pendiente técnica para post-hackathon.
  - No tocó firmware ni frontera física. Workspace local limpio en main; contenedores Jetson vivos para verificación.
- **BME280**: aún bloqueado físicamente. Día 17 Bea compró módulos nuevos en Diotronic. **Mañana día 18 Xilema desbloquea con módulos nuevos + alimentación + adaptadores**.
- **Sensores críticos sí en mesa**: 2x humedad suelo, nivel depósito, caudalímetro, bomba 12V. **No bloqueados por BME280**.

### Pollen (Floema)

- **F0-F5 cerradas**. Pollen demo-ready esperando integración real con Rhizome.
- **Compromiso bloque 3 cumplido día 14**: `MeristemNetworkClient` + `VisitarMeristemScreen` + `FieldVisit.kt` + `PolicyPacket.kt` con snake_case verificado.
- **Apply now bloque 1 cerrado día 15**: `Log.e()` estructurado en `LiteRtInfra.kt:199` en lugar de catch silencioso.
- **Día 16-17**: trabajo en `feat/pollen-f5-rhizome` (digest día 16 en `2026-05-01_digest-dia16_floema.md`). Standby útil mantenido.
- **Pendiente día 18+**: sustituir `RhizomeMockClient` por cliente real apuntando a IP del Jetson (Jetson ya estable según cierre Endo). **Floema y Endo lo hacen juntas**.
- **Floema dueña live demo**: APK descargable + Appetize.io + transcripts navegables. Plazo draft día 22, pulido día 28. Decisión pendiente Bea: ¿endpoint público Meristem (Cloud Run / Fly.io) para que el APK pueda llamar fuera de rodaje?

### Meristem-nodo (Meristem)

- **Día 15 cerró pipeline determinístico end-to-end** sin LLM: schemas + Evaluator (4 reglas con precedencia) + 13 tests PASS + persistencia SQLite + PolicyComposer + 5 bundles smoke OK.
- **Día 16 cerró**: **LLM E4B integrado con tool calling end-to-end**. Mini-batería 5/5 PASS. Calidad rationale mejor de lo esperado. Rama `feat/meristem-node-llm-integration` lista para PR.
- **Bonus día 16 no planeado**: **multi-Rhizome simulado v0 funcional**. Cuando la abstracción está bien, la extensión sale gratis. Para writeup §6.
- **`decisions_by_rule` en `/health`** convierte trazabilidad en pieza de demo. Pendiente día 18 si tiempo.
- **Mensaje pendiente a Xilema**: validación dominio del prompt + 5 bundles. Sin urgencia mientras Xilema esté en BME280 día 18.
- **Verificación Cactus framework** con Bea + Floema + Xilema (decisión Bea día 18).

### Tuning Rhizome (Meristem cerró v0.5 x86, Endo validó en Jetson real)

- **Rhizome v0.5 al 100%** (18/18 envelope_valid + 18/18 status_match) en x86 CPU casera (Meristem día 15).
- **`code/tuning/`** completo en main desde día 15 (PR #62).
- **Día 17**: Endo re-ejecutó batería completa en Jetson Orin Nano Super real (CPU-only). 18/18. Reproducción 1:1 de la línea base x86 sobre hardware constrained.

### Vídeo (Corola + Bract + Venation)

- **Guion v1.4 cerrado conceptualmente día 14**. 9 escenas, 5 frases fuertes, 2 parcelas lógicas.
- **Día 17 cerrado**:
  - **PR #66 (Venation) mergeado a main**: onboarding + handoff video con inventario E2-E9 de assets disponibles + cenital E9 ya animado + signal.seed blindado como regla.
  - **PR #65 (Bract) en DRAFT**: 9 incoherencias detectadas + asset spec a Venation + onboarding bitácora. Pendiente actualización con decisiones cerradas + renombrar borrador→mensaje + Ready for review + merge Cambium.
  - **`feat/corola-guion-v1` pendiente de merge a main**: script + shot list **v1.6** con sistema visual Venation aplicado + respuestas a Venation y Bract.
- **Tres decisiones cerradas Bea día 17**:
  - **Climax narrativo (incoherencia #2 Bract)**: criterio modificado E7. Transferencia cruzada A→B baja a tensión visual.
  - **Cenital editorial (incoherencia #3 Bract)**: uno solo en E9. Veo3 fuera. Animación Venation adoptada.
  - **Meristem en MVP del vídeo (incoherencia #5 Bract)**: sí entra. Yo actualizo `pitch_video.md` en sesión conjunta con Bea (pendiente día 18).
- **Pivote pequeño del guion día 17**: abrir con **ausencia** (red que no llega, móvil sin señal, decisión que no espera), después solución y los 3 nodos, después zoom Rhizome. **Bea aparece a partir de E5** (`operator_note`) como cara de la decisión humana, no narradora del problema.
- **Tagline maestra confirmada**: *"When the network is absent, local criteria still irrigate."* — convergencia conceptual Bea + Venation. Va al cierre del video.
- **Wow moment dirigido**: ESP32 SAFE LIMIT en E3 (`candidate_action.seconds=30 → final_action.seconds=12`).
- **Convergencia operativa Bract ↔ Venation sin coordinación previa**: ambas hablan el mismo lenguaje técnico de assets/formatos/plazos. Material para writeup §5.

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
- **Material confirmado para §5 Buenas prácticas**:
  - Thinking mode aplicado por nodo (Pollen sin, Meristem con, Rhizome a definir por Endo).
  - Definición de parámetros prompts + config modelos + benchmark (batería 18 prompts, criterios envelope_valid + status_match, patrón "lógica determinista decide, LLM solo escribe rationale").
  - Cómo trabajamos (4-5 bullets cortos): bitácoras como contrato, formato síncrono por turnos contra repo, regla *"5 días para escribirla, 1 día para que las nuevas la tengan"*, contratos JSON como interfaz dura, frase **"Yo somos todas nosotras. Por eso firmo como zigiella."**
  - Convergencia conceptual Bea↔Venation y operativa Bract↔Venation (ejemplos de tesis legible sin explicación).
  - Aceptación profesional sin pelea Corola → Venation (*"lo arregla con un copy mejor que el mío"*).
- **Material confirmado para §6 MVP — qué proyectamos vs qué hacemos**:
  - Multi-Rhizome simulado v0 ya funcional (no estaba planeado para día 16).
  - signal.seed (#C5F26B) como pista visual única "inteligencia activa" cross-escena.
  - Live demo con APK + Appetize.io + transcripts (no Rhizome en internet).
- **Material confirmado para §10 Trabajo futuro**:
  - Sumar visión (cámara + análisis visual con Gemma 4 multimodal).
  - Hablar con la parcela (audio in/out, voz natural full-duplex).
  - Escalabilidad multi-parcela / multi-Rhizome real (v0 simulado ya hay).

### Estrategia hackathon (revelación día 17)

- **El video pesa 70 puntos de 100** en la evaluación (40 Impact & Vision *as demonstrated in your video* + 30 Video Pitch). Writeup + repo solo verifican que la tecnología es real (30 pts Technical Depth).
- **Combinaciones de premios**:
  - Main + Special Tech: explícitamente combinable.
  - Main + Impact: NO mencionado → asumir excluyente.
  - Best case realista: Main 1st ($50k) + Special llama.cpp ($10k) = **$60k**.
- **Patrón ganador 2025 (Gemma Vision) que coincide con Sprout**: singular focus + on-device + offline + privacy + real functional tech + multi-modelo con routing. Le copiamos el playbook sin saberlo.
- **Lo que falta del playbook**: persona real con cara y nombre en el video. Decisión Bea día 17: ella sale en el video, no obsesión por agricultor real. Plan: pivote guion con "ausencia" para abrir, Bea entra en E5.

### Naming Gemma 4 (verificado día 17)

- **Repo cumple**: nombres "Gemma 4 E2B" / "Gemma 4 E4B" consistentes en 161 ocurrencias.
- **Falta**: añadir statement *"Gemma is a trademark of Google LLC."* en 5 sitios (README, writeup, video, landing live demo, APK Pollen).
- **Verificar**: branding Venation no pisa elementos Gemma (color signal.seed verde-lima probablemente seguro, pero confirmación pendiente con Venation vía bitácora).
- PDF naming guidelines descargado en local; pendiente commit a `docs/external/` cuando OK Bea.

### Landing (idea día 16)

- **Concepto**: APK descargable (GitHub Releases) + Appetize.io + transcripts navegables. Floema dueña.
- **Pendiente**: verificar coste/limitaciones Appetize.io. Decisión Bea sobre endpoint público Meristem para cadena hands-on real.
- **Plazo**: draft día 22, pulido día 28.

### README del repo (rehacer día 18+)

- Estructura ganadora propuesta: hero + watch demo + try yourself + 30s pitch + architecture + Gemma 4 use + reproduce + team (zigiella) + license + atribución Gemma trademark.
- Inglés primero, español en archivo aparte (`README.es.md`).
- Cambium arranca cuando writeup esté avanzado (cita §5 sobre cómo trabajamos).

---

## Apuesta de premios (revisada con datos del reglamento día 17)

| Track | Premio | Encaje real Sprout | Probabilidad | Combinable con Main |
|-------|--------|---------------------|--------------|---------------------|
| **Main 1st** | $50k | Tesis defendible + tecnología real + offline-first + privacy (mismo playbook que Gemma Vision 2025) | Apuesta principal | — |
| **Special llama.cpp** | $10k | Doble punto Rhizome (Jetson) + Meristem (portátil casero) en hardware constrained | Alta | ✅ Sí |
| **Special LiteRT** | $10k | Pollen usa LiteRT-LM en E4B on-device | Alta | ✅ Sí (verificar si solo 1 Special) |
| **Special Cactus** | $10k | Local-first mobile que routes between models — Pollen literal | Verificar si es framework específico | ✅ Sí |
| **Impact Global Resilience** | $10k | Encaje literal: offline, edge-based, climate mitigation | Alta — solo si NO Main | ❌ |
| **Impact Safety & Trust** | $10k | Lógica determinista + decisions_by_rule + ESP32 veto | Alta — solo si NO Main | ❌ |
| **Impact Digital Equity** | $10k | Operator_note literal castellano + UX bilingüe | Media — solo si NO Main | ❌ |

---

## Decisiones operativas pendientes

| # | Decisión | Dueña | Plazo |
|---|----------|-------|-------|
| 1 | Meteo dentro/fuera del MVP (depende de Froggit DP3000) | Bea + Xilema | Día 18 |
| 2 | Slack MCP — solo Corola, mañana o pasado | Bea | Día 18-19 |
| 3 | Reorganizar writeup con índice nuevo + arrancar §4 Gemma 4 | Bea + Cambium | Día 18 sesión conjunta |
| 4 | Endpoint público Meristem (Cloud Run / Fly.io) sí o no para live demo | Bea | Día 18 |
| 5 | Cactus framework verificación + decisión usar | Bea + Floema/Meristem/Xilema | Día 18 |
| 6 | Atribución *"Gemma is a trademark of Google LLC."* en 5 sitios | Cambium (cuando OK Bea) | Pre-deadline |
| 7 | Verificar branding Venation no pisa Gemma | Venation (vía bitácora) | Pre-rodaje |
| 8 | Stash `[corola]` con update estado_vivo de día 16: descartar o aplicar diff vs versión actual | Bea + Cambium | Sesión conjunta día 18 |
| 9 | Merge `feat/corola-guion-v1` (script + shot list v1.6) a main | Cambium | Cuando Corola dé OK final |
| 10 | Verificar coste Appetize.io | Floema | Día 18 |

---

## Pendientes activos día 18

### Bea
- Macetas pimientos + tomates por la mañana (compradas día 17)
- BME280 con Xilema (módulos nuevos en mano)
- Coordinación arte-video-creatividad (continúa con Corola, Bract, Venation)
- Sesión conjunta writeup con Cambium (índice nuevo + §4 Gemma 4 + decisión sobre stash `[corola]`)
- Voto sobre meteo (post info Xilema sobre Froggit)
- Voto sobre Slack MCP
- Voto sobre endpoint público Meristem
- Voto sobre Cactus

### Xilema
- BME280 desbloqueado con módulos nuevos + alimentación 5V/12V + adaptadores
- Multímetro al BME280 roto (si llega tiempo)
- Verificar Froggit DP3000 (independiente del BME280) — input para voto Bea sobre meteo
- Soporte mensaje pendiente Meristem (validación dominio + 5 bundles) cuando hueco

### Endodermis
- Rhizome v0.5 corriendo en Jetson real (mantenimiento + monitoreo)
- Soporte Floema cuando empiece integración real Pollen ↔ Rhizome (sustituir mock por cliente real)
- GPU offload pendiente (CUDA/NvMap) — apuntada para post-hackathon, no urge día 18
- Apuesta multi-agente día 24: si MVP funciona, lidera doble agente días 25-30

### Floema
- Integración real Pollen ↔ Rhizome (sustituir `RhizomeMockClient` por cliente real apuntando a IP Jetson) — juntas con Endo
- Live demo dueña: arrancar APK + Appetize.io + transcripts. Verificar coste Appetize.io.
- Cactus verificación con Bea + Meristem + Xilema
- Cuando Meristem confirme LLM en producción: smoke real Pollen → Meristem
- Coordinación con Venation sobre tokens visuales del design pack aplicables a Pollen (Floema decide qué entra y cuándo)

### Meristem
- PR `feat/meristem-node-llm-integration` listo para mergear (verificar tres puntos antes de empujar)
- Soporte a Endodermis (ya cerró batería; ahora mantenimiento + integración Pollen)
- `decisions_by_rule` en `/health` si tiempo
- Iterar con Xilema sobre prompt + 5 bundles cuando ella responda
- Cactus verificación con Bea + Floema + Xilema
- Cerrar nomenclatura `SAFETY_DOWNGRADE` ↔ `HARD_LIMIT_DOMAIN` con Xilema

### Corola
- Merge `feat/corola-guion-v1` a main cuando dé OK final (script + shot list v1.6)
- Continuar coordinación lateral con Bract y Venation (las respuestas a sus handoffs ya están en su rama)
- Decisión sobre `signal.seed` cross-escena (Venation propone aplicación sistemática)
- Refinar traducciones first pass — cartela ancla E7, cartela progresiva E9, subtítulo logo
- Voz humana real escena 5 — pendiente confirmar (probable Bea, días 24-25)

### Bract
- Actualizar borradores `borrador-mensaje-corola-incoherencias_bract.md` y `borrador-mensaje-venation-assets_bract.md` con decisiones cerradas Bea (#2 climax E7, #3 cenital uno solo Veo3 fuera, #5 Meristem dentro)
- Renombrar `borrador-mensaje-*` → `mensaje-*` en commit aparte
- Convertir PR #65 a Ready for review
- Cambium mergea
- Esperar respuesta Floema sobre estabilidad UI Pollen (capturas E4-E5-E7)
- Esperar respuesta Xilema sobre disponibilidad capturas Jetson (E2-E3-E7)

### Venation
- Esperar respuesta Corola al handoff (en bitácora aparte cuando Corola tenga hueco)
- Esperar respuesta Bract al asset spec (cuando ella dispare mensaje desde PR #65 mergeado)
- Verificar branding propio no pisa Gemma (color, tipografía, mark) — bitácora corta confirmando
- Si configuró `git config --local user.name`, verificar y limpiar con `git config --local --unset` para mantener `.git/config` neutro

### Cambium
- Sesión conjunta writeup con Bea (índice + §4 Gemma 4 + stash `[corola]`)
- Update `pitch_video.md` con Meristem en MVP
- Mergeo PR #65 Bract cuando convierta a Ready
- Mergeo `feat/corola-guion-v1` cuando Corola dé OK
- Trademark statement Gemma en 5 sitios cuando Bea OK
- Commit PDF naming guidelines a `docs/external/` cuando Bea OK

---

## Convenciones del proyecto a tener en cabeza

- **Bitácoras** en `bitacora/YYYY-MM-DD_tema_autora.md`. Decisiones por escrito el mismo día.
- **Ramas**: `feat/[nombre]/[descripcion-corta]`. Trabajo nuevo siempre en rama propia, no en main.
- **Archivos calientes** (`docs/40_pitch_video.md`, `docs/01_architecture.md`, `writeup/draft.md`): solo Cambium consolida en main, los cambios llegan por mensajes.
- **Tres puntos de verificación git** antes de cada commit: `git status` + `git branch --show-current` + `git stash list`. Documentado en `CONTRIBUTING.md §9.2`.
- **Stash con prefijo de autor**: `git stash push -m "[nombre] descripción"`.
- **Una operación atómica por sesión** en máquina compartida.
- **Identidad git inline** (`git -c user.name=... -c user.email=...`) para no modificar `.git/config` del clone compartido.
- **Proceso preventivo**: antes de migrar/pivotar librería troncal, verificar contra documentación oficial citando URL + versión + fecha en el commit.

---

## Hitos del calendario

| Día | Hito |
|-----|------|
| **18 (mañana)** | BME280 desbloqueado + integración real Pollen↔Rhizome + sesión writeup conjunta + macetas Bea |
| **19-20** | Ensayo del vídeo + rodaje (con guion pivoteado: ausencia → solución → zoom Rhizome) |
| **22-25** | Post-producción + writeup pulido + live demo draft (Floema) |
| **24** | Checkpoint MVP funcionando — decisión doble agente sí/no |
| **25-30** | Si MVP estable: doble agente días 25-30 lidera Endodermis. Writeup final. README ganador |
| **28** | Live demo pulida (APK + Appetize.io + transcripts) |
| **30 (15 mayo)** | Fin del plan interno del proyecto |
| **18 mayo 23:59 UTC** | Deadline hackathon Kaggle. **3 días de margen sobre plan interno**. |

---

*Mantenido por Cambium. Actualización a cierre de cada día.*
