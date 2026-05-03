# Estado vivo del proyecto

> **Documento corto que siempre refleja el estado actual del proyecto.**
> Cambium lo actualiza al cierre de cada día. Cualquier persona del equipo
> (incluida una nueva miembra que se incorpore) puede leer esto en 30
> segundos y reconstruir contexto sin tener que escarbar 50 bitácoras.
>
> **Fecha de última actualización:** 2026-05-03 (cierre del día 18)
> **Día del proyecto:** 18 de 30. Quedan 12 días.

---

## Tesis del proyecto en una línea

Sprout reduce la latencia de decisión de riego en parcelas aisladas — donde el campo, la persona y la red no coinciden en el tiempo — distribuyendo la decisión entre tres nodos con jurisdicciones distintas y un coprocesador físico que veta.

> *"Lo físico manda, Rhizome arbitra, Pollen media, Meristem afina."* (Xilema, día 13)

> *"Cuando la red no llega, el criterio sí."* (Bea, día 16) ≈ *"When the network is absent, local criteria still irrigate."* (Venation, día 16, sin coordinación previa)

> *"Yo somos todas nosotras. Por eso firmo como zigiella."* (Bea, día 17) — frase para writeup §5.

> *"Hoy el sistema dejó de ser piezas sueltas. Jetson piensa, ESP32 veta, Rhizome empieza a tener cuerpo físico real."* (Xilema, día 18) — frase ancla del cierre del día.

> *"En sistemas físicos, el perfil rápido no gana hasta que conserva contrato. El perfil seguro manda."* (Endodermis, día 18) — frase para writeup §5.

**Tagline final confirmada (bookend del video, inicio + cierre):** *"When network is absent — and the human is far — local criteria still irrigate."*

---

## Equipo (9 miembras activas)

| Nombre | Rol | Frente | Estado |
|--------|-----|--------|--------|
| **Bea** | Product owner | Decisiones, narrativa, escritos al jurado, cara del vídeo. Sprout escala 1 plantado en terraza día 18 | Activa |
| **Cambium** | Tech lead | Coordinación, bitácoras, writeup, moderación, research, vuelta del video | Activa |
| **Xilema** | Dueña Rhizome físico + ESP32 | Firmware ESP-IDF, USB-CDC, sensores. **BME280 estabilizado día 18 + primer ping Jetson↔ESP32** | Activa |
| **Floema** | Dueña Pollen + dueña live demo | Nodo móvil Android Gemma 4 E4B + LiteRT-LM. APK + Appetize.io + transcripts | Activa, F5+Rhizome (bitácora día 18 pendiente de localizar en repo) |
| **Meristem** | Dueña Meristem-nodo + tuning | Cerebro lento (FastAPI + llama.cpp + Gemma 4 E4B) | Activa, sin actualización día 18, PR LLM listo para mergear |
| **Corola** | Dueña vídeo | Guion, shot list, dirección creativa | Activa, script + shot list v1.6 en `feat/corola-guion-v1` (pendiente merge) |
| **Endodermis** | Apoyo a Xilema en frente Jetson | Bring-up Jetson + batería Rhizome v0.5 + perfiles GPU/CPU | Activa, **GPU runtime PASS día 18 (quality pendiente RD04)** |
| **Bract** | Montadora de vídeo | Montaje en CapCut, herramienta `video-tools/` para análisis VL | Activa, **PR #65 Ready for review** |
| **Venation** | Directora de arte | Sistema visual del proyecto, design pack | Activa, signal.seed blindado como regla, sin actualización día 18 |

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

**Patrón Meristem confirmado día 16, validado empíricamente día 18:** *"lógica determinística decide, LLM solo escribe rationale"* — la deriva GPU RD04 día 18 (LLM responde `need_clarification` en lugar de `ok`) es prueba de que el patrón funciona: el LLM puede derivar, el sistema no se rompe porque la decisión la firma la lógica determinista.

---

## Estado por frente — día 18 cierre

### Rhizome físico (Xilema + Endo)

- **Firmware ESP32-S3**: 5 reglas no negociables + SAFETY_DOWNGRADE.
- **BME280 estabilizado día 18 (PR #68)**: lectura física validada con `I2C_SCAN 0x76`, `chip_id=0x60`, `BME280_REPORT ... ESP_OK`, telemetría `bme280_valid=true`. Después de seis días de bloqueo físico. Diagnóstico final Xilema: *"combinación de cobre, pinout, puerto fantasma y ruta ESP-IDF/Bosch demasiado frágil para este módulo"*.
- **Jetson día 18**: GPU runtime PASS confirmado por Endo con `--fit off --no-op-offload`. 36/36 capas a GPU. Smoke ~1152ms vs 2277ms CPU-only. **Quality PASS NO todavía** — RD04 deriva semántica (need_clarification en lugar de ok) en GPU full. Mitigaciones probadas (temp=0, parcial -ngl 12, cache off) NO resuelven RD04. Apuntado para post-hackathon.
- **Primer ping Jetson↔ESP32 día 18 (PR #70)**: secuencia completa documentada (`STATUS`, `HOST_HEARTBEAT`, `TELEMETRY`, rechazo `WATER A 12` con `TANK_LOW`, `ALERT_LATCHED`, vuelta a `SAFE_IDLE` con `RESET_ALERT`). Bloqueo era solo permisos `dialout` en Jetson, no hardware.
- **Perfiles Jetson reproducibles (PR #69)**: `safe-cpu` (default demo contractual, 18/18) + `gpu-experimental` (apuntado, no promocionado hasta RD04 cerrado). Scripts en `code/rhizome/jetson/` (`run_runtime.sh`, `start_adapter.sh`, `smoke_adapter.sh`, `collect_baseline.sh`, `run_battery.sh`).
- **Sprout escala 1 corriendo en terraza Bea (Castellar de n'Hug) día 18**: jardineras metálicas + sacos textiles plantados (tomate, fresa, pimientos, aromáticas) + garrafa-depósito (no riego humano) + sensores conectados al ESP32. **No es metáfora — es el sistema funcionando a escala doméstica**. Coincidencia visual: el verde de los sacos textiles ≈ `signal.seed` (#C5F26B).
- **Sensores críticos en mesa**: 2x humedad suelo, nivel depósito, caudalímetro, bomba 12V (no conectada todavía — actuadores solo cuando cableado protegido revisado).

### Pollen (Floema)

- **F0-F5 cerradas día 16-17**. Pollen demo-ready esperando integración real con Rhizome.
- **Día 18**: bitácora `2026-05-03_cierre-dia-18-floema-a-cambium.md` mencionada por Bea pero no localizada en remoto. Apunte parcial (vía Bract): refactorización `MainActivity.kt`, `HomeScreen.kt`, `VisitarMeristemScreen.kt`, `ChatFeature.kt` durante día 17. Estado real día 18 pendiente confirmar.
- **Pendiente día 19**: sustituir `RhizomeMockClient` por cliente real apuntando a IP Jetson (juntas con Endo). **Esto desbloquea cierre del MVP**.
- **Floema dueña live demo**: APK descargable + Appetize.io + transcripts. Plazo draft día 22, pulido día 28. Bea OK al endpoint público Meristem (Cloud Run / Fly.io) — *"el coste lo podemos asumir"*.

### Meristem-nodo (Meristem)

- **Día 16 cerrado**: LLM E4B integrado con tool calling end-to-end + multi-Rhizome simulado v0 funcional.
- **Día 17-18 sin novedades activas en su frente**.
- **Patrón validado empíricamente día 18** por la deriva GPU RD04 de Endo: lógica determinista decide, LLM solo escribe rationale. Para writeup §5 + §6.
- **Pendiente**: PR `feat/meristem-node-llm-integration` listo para mergear cuando confirme rama limpia.
- **Cactus framework verificación** pendiente (Bea + Floema + Meristem + Xilema).
- **Cerrar nomenclatura `SAFETY_DOWNGRADE` ↔ `HARD_LIMIT_DOMAIN`** con Xilema en próximos días.

### Tuning Rhizome

- **Rhizome v0.5 al 100%** validado en Jetson real (Endo día 17, 18/18 status_match en CPU-only).
- **Día 18**: GPU full pasa 12/12 envelope + 11/12 status_match (RD04 deriva). Apuntado RD04/RH02 como "GPU quality pending".

### Vídeo (Corola + Bract + Venation)

- **Guion v1.4 cerrado día 14**. Script + shot list **v1.6 en `feat/corola-guion-v1`** (pendiente merge cuando Corola dé OK final).
- **PR #65 (Bract) Ready for review día 18**: 3 correcciones aplicadas + mensaje a Venation reescrito (4/4 preguntas respondidas con su handoff) + renombrado borradores → mensajes con `git mv`.
- **PR #66 (Venation) mergeado día 17**: handoff video con inventario E2-E9 + cenital E9 animado + signal.seed blindado.
- **Decisiones cerradas Bea día 17**: climax E7, cenital uno solo, Veo3 fuera, Meristem en MVP.
- **Vuelta del video cerrada Bea + Cambium día 18**:
  - Estructura **9-10 escenas** (no 3 actos), shot list v1.6 reagrupado.
  - **Cartela Sprout + lema + 3 nodos al inicio (~5 seg)** antes de la ausencia.
  - **E1 ausencia con 4 datos globales**: UNCCD 48% territorio mundial, UNCCD 1.8B + $300B, gencat -80% riego Cataluña 2024, ITU 58% rural mundial. Cataluña ejemplo del patrón global.
  - **Climax E7** criterio modificado, **wow moment ESP32 SAFE LIMIT en E3** dirigido.
  - **E9 cenital animado Venation** + **E9b nueva**: Bea tecleando portátil casero con Meristem en pantalla + cutaway a macetas reales (Sprout escala 1).
  - **VO en inglés** master + dub ES aparte. Voz cruda Bea castellano en E5 (`operator_note`) respetada.
  - **Tagline bookend** confirmada: inicio + cierre.
  - **Frases fuertes pendientes revisión** (Cambium las prepara día 19).
- **Herramienta Bract `video-tools/`** (fuera del repo): comparativa Qwen 3.6 Plus vs Gemini 2.5 Pro vs **Gemini 3.1 Pro Preview** sobre `videomacetas.mp4`. Default elegido: Gemini 3.1 Pro Preview (43% menos coste, lee audio real, honesto sobre dirección de arte). Disciplina epistémica `OBSERVADO / INFERIDO / DECLARADO` en prompt v2. Apunte cultural para writeup §5.

### Writeup

- **Secciones 1, 2, 3 escritas**.
- **Índice nuevo aprobado por Bea día 16**:
  - §0 Título + subtítulo
  - §1 Problema
  - §2 Solución
  - §3 Arquitectura
  - §4 **Gemma 4** (NUEVA)
  - §5 **Buenas prácticas y principios de trabajo** (NUEVA)
  - §6 **MVP — qué proyectamos vs qué hacemos** (NUEVA)
  - §7 Demo (90s)
  - §8 Impacto y escalado
  - §9 Limitaciones
  - §10 **Trabajo futuro**
- **Material confirmado para §5 Buenas prácticas** (acumulado hasta día 18):
  - Thinking mode aplicado por nodo.
  - Definición de parámetros prompts + config modelos + benchmark.
  - Cómo trabajamos: bitácoras como contrato, formato síncrono por turnos contra repo, regla *"5 días para escribirla, 1 día para que las nuevas la tengan"*, contratos JSON como interfaz dura, frase **"Yo somos todas nosotras. Por eso firmo como zigiella."**, disciplina §9.2 aplicada por todo el equipo.
  - Convergencias (Bea↔Venation conceptual, Bract↔Venation operativa).
  - Aceptación profesional sin pelea (Corola → Venation).
  - **Frase Endo día 18**: *"En sistemas físicos, el perfil rápido no gana hasta que conserva contrato. El perfil seguro manda."*
  - **Frase Xilema día 18**: *"Hoy el sistema dejó de ser piezas sueltas."*
  - **Disciplina epistémica `OBSERVADO / INFERIDO / DECLARADO`** de Bract.
  - Diagnóstico Xilema BME280: distinción síntoma vs causa raíz (cobre, pinout, puerto fantasma, ruta frágil).
  - Aprendizaje operativo: antes de sospechar de hardware, verificar permisos OS (caso Jetson↔ESP32 dialout).
- **Material para §6 MVP — qué proyectamos vs qué hacemos**:
  - Multi-Rhizome simulado v0 ya funcional.
  - signal.seed (#C5F26B) cross-escena.
  - Live demo: APK + Appetize.io + transcripts + endpoint público Meristem.
  - **Sprout escala 1 corriendo en terraza Bea** — proyecto ya funcionando a escala doméstica, no solo proyectado.
  - **GPU runtime PASS / quality NO** como evidencia empírica del patrón Safety & Trust.
- **Material para §10 Trabajo futuro**:
  - Sumar visión (cámara + análisis multimodal Gemma 4).
  - Hablar con la parcela (audio in/out, voz natural full-duplex).
  - Escalabilidad multi-parcela / multi-Rhizome real.
  - **GPU quality pass** (cerrar RD04/RH02).

### Estrategia hackathon (revisada día 18 con research nuevo)

- **El video pesa 70 puntos de 100**: Impact & Vision (40) + Video Pitch (30). Writeup + repo verifican (30).
- **Combinaciones premios**: Main + Special Tech combinable explícito. Main + Impact NO mencionado → asumir excluyente.
- **Best case realista**: Main 1st ($50k) + Special llama.cpp ($10k) = **$60k**.
- **Patrón ganador 2025 (Gemma Vision)** que coincide con Sprout: singular focus + on-device + offline + privacy + real functional + multi-modelo con routing.
- **Research global cerrado día 18 (PR #67 mergeado)**: 4 stats globales + 2 locales + 1 precedente + 1 bloque casos paralelos. Opener video con datos UNCCD + OECD + FAO + ITU + gencat + COAG/MAPA + WSU.

### Naming Gemma 4

- **Repo cumple**: nombres consistentes en 161 ocurrencias.
- **Falta**: añadir statement *"Gemma is a trademark of Google LLC."* en 5 sitios (README, writeup, video, landing live demo, APK Pollen).
- **Verificar**: branding Venation no pisa elementos Gemma.
- **PDF guidelines** descargado en local; pendiente commit a `docs/external/`.

### Landing (frente apuntado, sin arrancar todavía)

- **Concepto**: APK descargable (GitHub Releases) + Appetize.io versión gratuita (suficiente según Floema) + transcripts navegables + animaciones abstractas (Venation, "1 hora cada una") + endpoint público Meristem (Cloud Run / Fly.io, OK Bea).
- **Equipo doble**: Venation (planteamiento + frontend) + Floema (montaje + APK + Appetize.io). Bea + Cambium estrategia narrativa + textos.
- **Plazo**: draft día 22, pulido día 28.

### README ganador (pendiente, cuando arranquemos sesión conjunta Bea + Cambium)

- Estructura: hero + watch demo + try yourself + 30s pitch + architecture + Gemma 4 use + reproduce + team (zigiella) + license + atribución Gemma trademark.
- **Inglés primero**, español en archivo aparte (`README.es.md`).

---

## Apuesta de premios (revisada día 18)

| Track | Premio | Encaje | Probabilidad | Combinable con Main |
|-------|--------|--------|--------------|---------------------|
| **Main 1st** | $50k | Tesis defendible + tecnología real + offline-first + privacy | Apuesta principal | — |
| **Special llama.cpp** | $10k | Doble punto Rhizome (Jetson) + Meristem (portátil casero) | Alta | ✅ Sí |
| **Special LiteRT** | $10k | Pollen usa LiteRT-LM en E4B on-device | Alta | ✅ Sí (verificar si solo 1 Special) |
| **Special Cactus** | $10k | Local-first mobile que routes between models | Verificar si framework específico | ✅ Sí |
| **Impact Global Resilience** | $10k | Encaje literal: offline, edge-based, climate mitigation | Alta — solo si NO Main | ❌ |
| **Impact Safety & Trust** | $10k | Lógica determinista + decisions_by_rule + ESP32 veto + GPU RD04 deriva sin romper sistema | Alta — solo si NO Main | ❌ |
| **Impact Digital Equity** | $10k | Operator_note literal castellano + UX bilingüe | Media — solo si NO Main | ❌ |

---

## Decisiones operativas pendientes

| # | Decisión | Dueña | Plazo |
|---|----------|-------|-------|
| 1 | Mergear PRs #68 (BME280), #69 (Jetson profiles), #70 (ping) | Cambium | Día 19 |
| 2 | Cactus framework verificación + decisión usar | Bea + Floema/Meristem/Xilema | Día 19-20 |
| 3 | `video-tools/` al repo (sin key) sí o no | Bea | Día 19 |
| 4 | Frases fuertes revisión | Cambium prepara, Bea modula | Día 19 |
| 5 | Reorganizar writeup índice nuevo + arrancar §4 Gemma 4 | Bea + Cambium | Sesión conjunta día 19+ |
| 6 | Atribución *"Gemma is a trademark of Google LLC."* en 5 sitios | Cambium (cuando OK Bea) | Pre-deadline |
| 7 | Verificar branding Venation no pisa Gemma | Venation (vía bitácora) | Pre-rodaje |
| 8 | Stash `[corola]` con update estado_vivo de día 16: descartar o aplicar | Bea + Cambium | Sesión conjunta |
| 9 | Merge `feat/corola-guion-v1` (script + shot list v1.6) | Cambium | Cuando Corola dé OK |
| 10 | Localizar bitácora Floema día 18 | Bea pasa link | Día 19 |
| 11 | Endpoint público Meristem (Cloud Run / Fly.io) — arrancar | Floema + Meristem | Días 25-28 |
| 12 | Verificar coste Appetize.io versión gratuita | Floema | Día 19 |
| 13 | Meteo dentro/fuera del MVP (depende Froggit) | Bea + Xilema | Día 19+ |
| 14 | Slack MCP — solo Corola | Bea | Día 19+ |

---

## Pendientes activos día 19

### Bea
- BME280 ya cerrado físicamente. Plantel ya plantado.
- Sesión conjunta writeup con Cambium (índice + §4 Gemma 4 + decisión sobre stash `[corola]`)
- Frases fuertes revisión con Cambium
- Voto sobre PRs #68/#69/#70
- Voto sobre Cactus, `video-tools/` al repo, branding Venation
- **NO conectar bomba/12V hasta cableado protegido revisado**

### Xilema
- Tras merge #68 por Cambium: reflashear ESP32 desde main (eliminar `fw=25a904f-dirty`), repetir BME280 smoke + ping Jetson↔ESP32 con SHA limpio.
- Convertir secuencia ping en escenario reproducible / runner controlado
- Soporte a Endo si retoma scripts Jetson
- Verificar Froggit DP3000 (input para voto Bea sobre meteo)

### Endodermis
- Esperar merge #69 por Cambium. Tras merge: pull limpio, configurar autoría inline `Endodermis <endodermis@sprout.local>`, repetir scripts Jetson, documentar.
- Soporte a Floema cuando arranque integración real Pollen ↔ Rhizome
- GPU offload pendiente RD04/RH02 — no urge, post-hackathon
- Coordinar primer flujo Jetson↔ESP32 bajo liderazgo Xilema

### Floema
- **Integración real Pollen ↔ Rhizome** (sustituir `RhizomeMockClient` por cliente real apuntando a IP Jetson) — juntas con Endo. **Hoy desbloquea cierre del MVP.**
- Capturas Pollen UI E4-E5-E7 para Bract cuando UI estable
- Verificar coste Appetize.io versión gratuita
- Cactus verificación con Bea + Meristem + Xilema
- Live demo dueña: arrancar APK + Appetize.io + transcripts
- **Pasar bitácora día 18** (no localizada en repo)

### Meristem
- PR `feat/meristem-node-llm-integration` listo para mergear (verificar tres puntos)
- Soporte a Endo si itera RD04 con LLM
- `decisions_by_rule` en `/health` si tiempo
- Cactus verificación
- Cerrar nomenclatura con Xilema

### Corola
- Merge `feat/corola-guion-v1` cuando dé OK final
- Responder a Bract (PR #65) sobre 6 incoherencias creativas pendientes (#1, #4, #6, #7, #8, #9)
- Responder a Venation handoff en bitácora aparte (4 preguntas: validación paquete, voz humana E5, traducciones first pass, cartela final E9)
- Decisión `signal.seed` cross-escena
- Refinar traducciones first pass
- Voz humana real escena 5 — confirmar quién la graba

### Bract
- Esperar merge PR #65 por Cambium
- Tras respuesta Corola: regenerar draft CapCut con cartelas EN literales
- Tras respuesta Venation: cerrar tipografía Manrope + IBM Plex Mono vs monospace
- Cuando Bea pase más material rodado: doble análisis (con dossier + sin)
- Posible plantilla `dossier-escena.md` por escena E1-E9
- Capturas Jetson E2-E3-E7 — coordinación directa con Endo cuando hueco

### Venation
- Esperar respuesta Corola al handoff
- Esperar respuesta Bract (vía PR #65 mergeado)
- Verificar branding propio no pisa Gemma — bitácora corta
- Si configuró `git config --local`, limpiar con `--unset`

### Cambium
- **Mergear PRs #68 → #69 → #70** (orden recomendado por Endo+Xilema)
- Sesión conjunta writeup con Bea (índice + §4 Gemma 4 + decisión sobre stash `[corola]`)
- Frases fuertes revisión
- Update `pitch_video.md` con Meristem en MVP (decisión Bea día 17)
- Mergeo PR #65 Bract
- Mergeo `feat/corola-guion-v1` cuando Corola OK
- Mergeo `feat/meristem-node-llm-integration` cuando Meristem confirme
- Trademark statement Gemma en 5 sitios cuando Bea OK
- Commit PDF naming guidelines a `docs/external/` cuando Bea OK
- Apuntar plantilla `dossier-escena.md` para Bract cuando arranque

---

## Convenciones del proyecto a tener en cabeza

- **Bitácoras** en `bitacora/YYYY-MM-DD_tema_autora.md`. Decisiones por escrito el mismo día.
- **Ramas**: `feat/[nombre]/[descripcion-corta]`. Trabajo nuevo siempre en rama propia, no en main.
- **Archivos calientes** (`docs/40_pitch_video.md`, `docs/01_architecture.md`, `writeup/draft.md`): solo Cambium consolida en main, los cambios llegan por mensajes.
- **Tres puntos de verificación git** antes de cada commit: `git status` + `git branch --show-current` + `git stash list`. Documentado en `CONTRIBUTING.md §9.2`.
- **Stash con prefijo de autor**: `git stash push -m "[nombre] descripción"`.
- **Una operación atómica por sesión** en máquina compartida.
- **Identidad git inline** (`git -c user.name=... -c user.email=...`) para no modificar `.git/config` del clone compartido.
- **Comunicación Venation ↔ resto**: paquetes formales solo a Corola para commit (no Cambium por defecto). Bea ↔ Venation directa para mensajes rápidos.

---

## Hitos del calendario

| Día | Hito |
|-----|------|
| **19 (mañana, sábado)** | Merge PRs Jetson + integración Pollen ↔ Rhizome real + sesión writeup conjunta + frases fuertes revisión |
| **19-20** | Rodaje del vídeo (con guion v1.6 + cartela Sprout inicial + apertura ausencia + 3 cerebros + ESP32 + criterio + cenital + E9b) |
| **22-25** | Post-producción + writeup pulido + live demo draft (Floema + Venation) |
| **24** | Checkpoint MVP funcionando — decisión doble agente sí/no |
| **25-30** | Si MVP estable: doble agente días 25-30 lidera Endodermis. Writeup final. README ganador |
| **28** | Live demo pulida (APK + Appetize.io + transcripts) |
| **30 (15 mayo)** | Fin del plan interno del proyecto |
| **18 mayo 23:59 UTC** | Deadline hackathon Kaggle. **3 días de margen sobre plan interno**. |

---

*Mantenido por Cambium. Actualización a cierre de cada día.*
