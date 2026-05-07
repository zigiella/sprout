# Estado vivo del proyecto

> **Documento corto que siempre refleja el estado actual del proyecto.**
> Cambium lo actualiza al cierre de cada día. Cualquier persona del equipo
> (incluida una nueva miembra que se incorpore) puede leer esto en 30
> segundos y reconstruir contexto sin tener que escarbar 50 bitácoras.
>
> **Fecha de última actualización:** 2026-05-07 (cierre del día 22)
> **Día del proyecto:** 22 de 30. Quedan 8 días.

---

## Tesis del proyecto en una línea

Sprout reduce la latencia de decisión de riego en parcelas aisladas — donde el campo, la persona y la red no coinciden en el tiempo — distribuyendo la decisión entre tres nodos con jurisdicciones distintas y un coprocesador físico que veta.

> *"Lo físico manda, Rhizome arbitra, Pollen media, Meristem afina."* (Xilema, día 13)

> *"Cuando la red no llega, el criterio sí."* (Bea, día 16) ≈ *"When the network is absent, local criteria still irrigate."* (Venation, día 16, sin coordinación previa)

> *"Yo somos todas nosotras. Por eso firmo como zigiella."* (Bea, día 17) — frase para writeup §5.

> *"Hoy el sistema dejó de ser piezas sueltas. Jetson piensa, ESP32 veta, Rhizome empieza a tener cuerpo físico real."* (Xilema, día 18) — frase ancla del cierre del día.

> *"En sistemas físicos, el perfil rápido no gana hasta que conserva contrato. El perfil seguro manda."* (Endodermis, día 18) — frase para writeup §5.

> *"Un esquema no es solo dónde va cada cable; también es una frontera de autorización."* (Xilema, día 19) — frase para writeup §5.

> *"En demo física, un pass silencioso vale menos que un fail trazable."* (Endodermis, día 19) — frase para writeup §5.

> *"El slow brain doméstico no compite con cloud. Compite con el agricultor que abre Excel y mira cuatro columnas."* (Meristem, día 19) — frase clave para writeup §6.

> *"Decisión narrativa precede a producción mecánica."* (Venation, día 19) — frase para writeup §5.

> *"Repo-first es repo-first."* (Corola, día 19) — regla operativa formalizada.

> *"Imagine this pot is a whole plot."* (Bract, día 19) — convención maceta-parcela para cartela del video.

> *"Un sensor físico no puede parecer dos. UI, contrato y narrativa tienen que decir lo mismo."* (Endodermis, día 20) — frase para writeup §5 sobre coherencia narrativa-técnica.

> *"Menos piezas, mejor demo, menos humo literal y metafórico."* (Xilema, día 20) — frase sobre alcance MVP físico (recorte a 1-línea), va al writeup §6.

> *"Material flexible vence material apretado. Animar 20s completo + recortar en post es siempre más barato que reanimar."* (Bea, día 20) — principio operativo de producción audiovisual, va al writeup §5.

> *"Tu trabajo se mantiene aunque las decisiones cambien."* (Corola, día 20) — apunte cultural sobre aceptación sin defensividad de revocaciones, va al writeup §5.

> *"En sistemas físicos, la pregunta correcta de un coordinador puede liberar dominios completos a un especialista, no solo capas."* (apunte cultural día 20 — Bea→Meristem→Venation reframing) — va al writeup §5.

> *"Una bomba probada vale más que un esquema perfecto sin probar."* (Xilema, día 21) — frase para writeup §5.

> *"Piezas que no gritan y aun así hacen que el sistema empiece a parecer real."* (Endodermis, día 21) — frase para writeup §5 como cierre del bloque "MVP qué proyectamos vs qué hacemos".

> *"HTML estructural bien pensado al inicio = ampliación indolora."* (Meristem, día 21) — apunte arquitectural sobre UI.

> *"El flujo lote HTML → batch render → CapCut se cerró en menos de una hora desde que llegó el ZIP."* (Bract, día 21) — frase sobre velocidad de integración audiovisual.

> *"Cuando vea descarte en lote entregado, preguntar antes de pedir ajuste — la decisión puede haberse cerrado lateralmente sin pasar por mí."* (Corola, día 21) — apunte cultural sobre coordinación lateral.

> *"A estas alturas, saber no forzar también es progreso."* (Xilema, día 22) — frase para writeup §5 sobre disciplina técnica.

> *"Hoy evitamos un drift antes de que Floema lo hardcodeara."* (Xilema, día 22) — frase para writeup §5 sobre la distinción `FirmwareHardLimits` vs `PolicyGuardrails` como precisión diagnóstica.

**Día 22 técnico**: PR #118 (Xilema) cierra distinción cristalina entre los 4 valores **firmware enforcement actual ESP32 v0** (`tank_minimum_pct=20`, `max WATER=30s`, `heartbeat_timeout=5000ms`, `ALERT_LATCHED` hasta `RESET_ALERT`) y los 2 valores **guardrails de política razonables** (180s max event + 60s entre eventos + 600s/día) que NO son enforcement actual del firmware. Drift evitado antes de hardcoding en Mini-Evaluator. Patrón cultural para writeup §5.

**Día 22 video**: Bea + Bract grabaron material informal pre-rodaje principal. *"Regulinchi"* (Bea) — exactamente la información que ahorra horas en rodaje real. Bract arranca primera versión del montaje día 23.

**Día 22 writeup**: §5 reescrita técnica + §9 sin sombra + §10 nuevo enfoque (Meristem más inteligente + sensores y complejidad parcela + multiagentes Jetson + GPU/audio/deuda) tras feedback Bea. Material proceso guardado en `CAJON/articulo_como_trabajamos_borrador.md` para artículo aparte post-hackathon.

> *"La tesis del proyecto es local-first. Si en la demo usamos API hosteada, estamos demostrando lo contrario de lo que defendemos."* (Cambium, reformulación tras pregunta Bea día 21) — patrón de coherencia narrativa.

**Feature beta voz → política día 21**: implementación operativa en local. Floema cerró Mini-Evaluator + RhizomeNetworkClient + VoiceBetaPanel UI con captura real de micrófono. Endo cerró endpoint `POST /policy` + `GET /policy/active` en fachada Rhizome `:13010` con smoke Jetson real OK. **Pendiente día 22**: Xilema confirma lista canónica hard limits firmware (consulta cherry-pick mergeada día 21) + smoke E2E Pollen → Jetson real con Endo.

**Decisión Bea día 21 sobre landing demo (mocks vs API)**: quedarnos con mocks deterministas como **coherente con la tesis local-first** — la demo se prueba sin red porque el sistema real tampoco depende de red. Reformulación de disclaimers en `landing-demo/` para reflejar coherencia. Cero infra externa, código mock público y transparente en `js/api.js`.

**MVP físico día 21**: bomba 12V validada con fuente directa (Xilema + Bea). Alcance recortado a 1-línea mantiene firmeza (sin electroválvulas, sin A/B físico, semántica `WATER A` visible en UI). Relé COM+NO (no NC) — bomba apagada por defecto. Próximo paso día 22: relé controlado + bomba vía relé sin ESP32.

**Tagline final confirmada (bookend del video, inicio + cierre):** *"When network is absent — and the human is far — local criteria still irrigate."*

**Guion v1.8 firmado día 20** (Corola + Bea, PR #96 mergeado). Diferencias respecto a v1.7: E8 sobrevive, **E9 Opción B 20s firme** (cadencia v1.6 con cierre largo, modulación Cambium 3-beats queda plan B post-edición), F6 va en E9b (no E9), timing en montaje (post-edición decide compresión final).

**Feature beta voz → política inmediata (día 20-22 implementación)**: spec Mini-Evaluator de Meristem firme (PR #92, 624 líneas + 12 casos test). Reparto: Floema (~13h, Mini-Evaluator Kotlin + structured output Gemma 4 E4B + cliente HTTP + UI BETA + tests E2E), Endo (~3h, endpoint POST /policy en :13010). Conservador por defecto: si confianza no suficiente, no aplica. **Tres capas de defensa**: schema validation Pollen + Mini-Evaluator local + ESP32 último filtro físico.

**Guion v1.7 cerrado día 19** (Corola, commits `55fcac2` + `3ee6d0a`, mergeado a main como PR #59 / `6cfce71`): 12 escenas + cartela apertura E0 + E3b + E9b. VO inglés master. 7 frases fuertes (incluida F6 nueva *"Tomorrow, it will learn"* + Extra E3b *"Meristem composes the policy"*). Microcorte 0.5s tierra agrietada en E1. Cenital E9 a 10s con animación Venation. Microcartela Gemma trademark al cierre.

---

## Equipo (9 miembras activas)

| Nombre | Rol | Frente | Estado |
|--------|-----|--------|--------|
| **Bea** | Product owner | Decisiones, narrativa, escritos al jurado, cara del vídeo. Sprout escala 1 plantado en terraza día 18. Schematics #73 día 19 → montaje Fase A día 20 | Activa |
| **Cambium** | Tech lead | Coordinación, bitácoras, writeup, moderación, research, cadena de merges día 19 (13 PRs) | Activa |
| **Xilema** | Dueña Rhizome físico + ESP32 | Firmware ESP-IDF, USB-CDC, sensores. **PR #73 mergeado día 19**: schematics oficiales + frontera de autorización + DRY_RUN para actuadores | Activa |
| **Floema** | Dueña Pollen + dueña live demo | Nodo móvil Android Gemma 4 E4B + LiteRT-LM | **Activa, día 19 enorme**: pixel-perfect UI Venation + Variante D WebSocket + voz multimodal Gemma 4 E4B nativa (jubilado SpeechRecognizer) + validación Pollen↔Jetson real |
| **Meristem** | Dueña Meristem-nodo + tuning | Cerebro lento + Plan IA por fases (PR #77) + WebSocket Variante D (PR #81) | Activa, **5 PRs día 19 mergeados (#63 LLM, #77 bitácoras, #78 followups, #81 WS, #82 cierre, #79 aclaración)** |
| **Corola** | Dueña vídeo | Guion v1.7 cerrado día 19 + 4 PRs procesados + corrección operativa repo-first | **Activa, día 19 extraordinario** — directora creativa identidad establecida (días 11, 13, 16, 19) |
| **Endodermis** | Apoyo a Xilema en frente Jetson | Bring-up Jetson + perfiles + fachada Rhizome→Pollen | Activa, **PRs #83 + #84 día 19**: helper estricto + fachada `:13010` validada por Floema. Hallazgo RH02 regression en safe-cpu desde main pendiente diagnóstico |
| **Bract** | Montadora de vídeo | Montaje CapCut, plantilla dossier-escena, 3 pipelines validadas | Activa, **PR #72 mergeado día 19**: 9 dossiers E1-E9 + convención maceta-parcela formalizada |
| **Venation** | Directora de arte | Sistema visual del proyecto + cenital E09 | Activa, **3 PRs día 19 mergeados (#74, #75, #76) + PR #85 abierto** (cenital cadencia pregunta a Corola) |

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

## Estado por frente — día 22 cierre

### Rhizome físico (Xilema + Endo)

- **Firmware ESP32-S3**: 5 reglas no negociables + SAFETY_DOWNGRADE.
- **BME280 estable** desde día 18. Telemetría `bme280_valid=true` confirmada.
- **Jetson día 19 (Endo, PRs #83 + #84)**:
  - **Helper estricto de batería** que falla si encuentra `envelope_valid=false`, error HTTP o `status_match` roto.
  - **Fachada Rhizome→Pollen** en `http://192.168.1.60:13010/` con `/status`, `/snapshot/latest`, `/receipts`, `/explain/decision/{id}`. **Validada por Floema con Pollen real**. El último cuello operativo del MVP cayó día 19.
  - **Hallazgo RH02 regression**: `safe-cpu` desde main falla `critical` 2/2 (RH02 JSON casi completo pero inválido). Pendiente diagnóstico Endo+Meristem día 20 sin tunear en caliente.
- **Schematics oficiales día 19 (Xilema, PR #73)**: `hardware/wiring_diagrams/day19_mounting_schematics.md`. Capa por capa (alimentación, masas, BME280, sensores analógicos, caudalímetro, actuadores, agua). Distinción contrato real (USB Jetson↔ESP32 + BME280) vs pinout candidato pendiente firmware (humedad, nivel, caudal, bomba, válvulas). **NO conectar 12V/actuadores hasta cableado protegido revisado**.
- **Sprout escala 1 corriendo en terraza Bea**: jardineras + sustrato + garrafa-depósito + sensores. Bea continúa montaje Fase A día 20 con apoyo Xilema según schematics #73.
- **GPU runtime/quality split**: `safe-cpu` default contractual; `gpu-experimental` con `--fit off --no-op-offload` carga 36/36 capas pero quality NO todavía (RD04 + ahora RH02). Pendiente post-hackathon.

### Pollen (Floema)

- **F0-F5 cerradas + verificación día 19**: `apply now` bloque 1 sigue cerrado.
- **Día 19 enorme**:
  - **Pixel-perfect UI con Venation**: `VisitarRhizomeScreen` finalizada con estética Venation + checklist interactivo colapsable + historial scrolleable + bilingüe ES/EN migrado a `strings.xml` + `strings-es.xml`.
  - **Decisión arquitectura E2E: Variante D (WebSockets)**: Pollen como cliente WS recibe comandos desde UI Meristem. Esquiva inestabilidad servidor móvil + latencia cero. Acordado con Meristem (PR #81).
  - **Voz Multimodal con Gemma 4 E4B nativa**: gracias a *Gemmita* prototype de Bea, jubilado SpeechRecognizer Android. Pollen graba `.wav` 16kHz e inyecta directo al modelo via `Content.AudioFile(...)`. Implementado en ambos flavors. Hallazgo SIGSEGV: `audioBackend = Backend.CPU()` faltante. **Material para writeup §4 (Gemma 4)** como uso real de capacidades multimodales.
  - **Validación Pollen↔Jetson real**: probada contra fachada Endo `:13010` y confirmado OK.
- **Pendiente día 20**: implementar `MeristemSocketClient` WS en Pollen (Variante D). Coordinas con Meristem que implementa servidor.
- **Live demo**: Plan A activo con flavors `device`/`demo` (mock para Appetize sin OOM). Plan B (endpoint público Meristem) en cola — no urge con flavors en place. Plazo draft día 22, pulido día 28.
- **Apuntes para writeup §5**: *"el backend C++ se corrompe silenciosamente al procesar el mel-spectrogram"* (frase Floema día 19) + *"las dependencias nativas hiper-pesadas pueden ser un lastre no solo operativo, sino también para enseñar el producto"* (frase Floema día 18).

### Meristem-nodo (Meristem)

- **Día 16 cerrado**: LLM E4B integrado con tool calling end-to-end + multi-Rhizome simulado v0 funcional.
- **Día 19 — 5 PRs mergeados a main**:
  - **PR #63 (cuerpo del trabajo)**: integración LLM Gemma 4 E4B + tool calling + 2-Rhizome MVP support. 1535 inserciones.
  - **PR #77 — Plan IA por fases** (bitácora estratégica): 7 fases progresivas + 6 principios arquitectónicos transversales. **Material directo para writeup §3, §5, §6**. Frase clave: *"el slow brain doméstico no compite con cloud. Compite con el agricultor que abre Excel y mira cuatro columnas."*
  - **PR #78 — followups técnicos**: RD04 + tool calling demo + UI spec dashboard + mini-experimento contexto.
  - **PR #81 — Aceptación Variante D (WebSocket)** + protocolo de mensajes detallado para Floema.
  - **PR #82 — cierre día 19** + PR #79 aclaración modelo Pollen-Floema (preserva trazabilidad decisión Variante D).
- **Patrón validado empíricamente día 18-19** por la deriva GPU RD04 de Endo: lógica determinista decide, LLM solo escribe rationale.
- **Pendientes día 20**:
  - Implementar servidor WS Variante D (coordina con Floema cliente WS).
  - Generar UI Meristem real para E3b (composing) y E9b (processing/storing) — material para video.
  - Coordinar con Endo diagnóstico RH02 regression sin tunear en caliente.
  - `decisions_by_rule` en `/health` si tiempo.
  - Mensaje pendiente Xilema (validación dominio prompt + 5 bundles + nomenclatura `SAFETY_DOWNGRADE` ↔ `HARD_LIMIT_DOMAIN`).

### Tuning Rhizome

- **Rhizome v0.5 al 100%** validado en Jetson real (Endo día 17, 18/18 status_match en CPU-only).
- **Día 18**: GPU full pasa 12/12 envelope + 11/12 status_match (RD04 deriva).
- **Día 19**: helper estricto detecta **RH02 regression también en `safe-cpu` desde main** (2/2 falla). Algo cambió tras los merges del día 18-19. Pendiente bisección Endo+Meristem día 20 sin tunear en caliente.

### Vídeo (Corola + Bract + Venation)

- **Guion v1.7 cerrado día 19** (Corola, PR #59 mergeado a main). 12 escenas + cartela apertura E0 + E3b Meristem prepara + E9b Meristem recibe. VO inglés master. 7 frases fuertes (incluida F6 *"Meristem stores and processes. Tomorrow, it will learn."* + Extra E3b *"Meristem composes the policy."*). Microcorte 0.5s tierra agrietada en E1 como bisagra emocional. Cenital E9 a 10s con animación Venation. Microcartela Gemma trademark al cierre.
- **Bract día 19 (PR #72 mergeado)**: plantilla `dossier-escena.md` + 9 dossiers E1-E9 + convención maceta-parcela formalizada (*"Imagine this pot is a whole plot."*). Tres pipelines validadas: análisis VL con dossier por escena, Remotion → ProRes/H.264 → CapCut, SVG Venation → Remotion → MP4.
- **Venation día 19 — 3 PRs mergeados + 1 abierto**:
  - **PR #74**: auditoría branding "no pisa Gemma" — confirma sistema visual no usa elementos Gemma (color, tipografía, mark).
  - **PR #75**: mini-lote overlays E01 + E02 + Z99 (4 PNG transparentes 1280×720) en `video/wip/overlays/`.
  - **PR #76**: paquete jsx-reference para Floema en `handoff/floema/2026-05-04/` (HTML compilado + 6 .jsx).
  - **PR #85 abierto** (sin merge): pregunta a Corola por cadencia 5 cartelas en 20s + modo Pollen B1 cascada vs B2 saltos + aclaración tagline bookend NO va dentro del cenital. Bract desistió de animar Remotion → Venation pivota a HTML+PNG, Bract codifica MP4 con ffmpeg.
- **Corola día 19 — 4 PRs procesados**:
  - **PR #80**: cherry-pick respuesta a Venation 4 preguntas pendientes.
  - **Procesó paquete Venation v2 completo (14 archivos) en 3 PRs gatekeep**: branding-audit + overlays mini-lote + jsx-reference para Floema.
  - **Corrección operativa repo-first**: Floema sin commit → Slack/mail → repo-first formalizado como regla del equipo.
- **Apuntes culturales día 19** (todos para writeup §5): *"Repo-first es repo-first."* (Corola), *"Imagine this pot is a whole plot."* (Bract), *"Decisión narrativa precede a producción mecánica."* (Venation), reconocimiento profesional cruzado entre frentes (Floema↔Meristem variantes, Bract↔Venation pivote sin escándalo).
- **Herramienta Bract `video-tools/`**: **NO entra al repo** (decisión Bea día 19, foco narrativo Gemma 4). Apunte cultural §5: tooling complementario que se mantuvo fuera del repo por foco narrativo.

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
- **Material confirmado para §5 Buenas prácticas** (acumulado hasta día 19):
  - Thinking mode aplicado por nodo.
  - Definición de parámetros prompts + config modelos + benchmark.
  - Cómo trabajamos: bitácoras como contrato, formato síncrono por turnos contra repo, regla *"5 días para escribirla, 1 día para que las nuevas la tengan"*, contratos JSON como interfaz dura, frase **"Yo somos todas nosotras. Por eso firmo como zigiella."**, disciplina §9.2 aplicada por todo el equipo.
  - Convergencias (Bea↔Venation conceptual, Bract↔Venation operativa).
  - Aceptación profesional sin pelea (Corola → Venation, Meristem → Floema Variante D día 19).
  - **Frase Endo día 18**: *"En sistemas físicos, el perfil rápido no gana hasta que conserva contrato. El perfil seguro manda."*
  - **Frase Xilema día 18**: *"Hoy el sistema dejó de ser piezas sueltas."*
  - **Frase Xilema día 19**: *"Un esquema no es solo dónde va cada cable; también es una frontera de autorización."*
  - **Frase Endo día 19**: *"En demo física, un pass silencioso vale menos que un fail trazable."*
  - **Frase Venation día 19**: *"Decisión narrativa precede a producción mecánica. Mejor preguntar cadencia que animar 480 frames y rehacerlos."*
  - **Frase Corola día 19**: *"Repo-first es repo-first."* (regla operativa formalizada).
  - **Frase Bract día 19**: *"Imagine this pot is a whole plot."* (convención maceta-parcela).
  - **Frase Floema día 19**: *"el backend C++ se corrompe silenciosamente al procesar el mel-spectrogram"* (diagnóstico fino multimodal).
  - **Disciplina epistémica `OBSERVADO / INFERIDO / DECLARADO`** de Bract.
  - Diagnóstico Xilema BME280: distinción síntoma vs causa raíz (cobre, pinout, puerto fantasma, ruta frágil).
  - Aprendizaje operativo: antes de sospechar de hardware, verificar permisos OS (caso Jetson↔ESP32 dialout día 18).
  - **Día 19 — equipo opera lateralmente sin cuello de botella**: 17 PRs abiertos en un día + 13 mergeados al cierre. Patrón validado empíricamente. Material para writeup §5.
- **Material para §6 MVP — qué proyectamos vs qué hacemos**:
  - Multi-Rhizome simulado v0 ya funcional (Meristem día 16).
  - signal.seed (#C5F26B) cross-escena.
  - Live demo Plan A activo: APK demo flavor + Appetize.io + transcripts (Floema día 18-19). Plan B (endpoint público Meristem) en cola — no urge.
  - **Sprout escala 1 corriendo en terraza Bea** — proyecto ya funcionando a escala doméstica, no solo proyectado.
  - **GPU runtime PASS / quality NO** como evidencia empírica del patrón Safety & Trust (Endo días 18-19).
  - **Plan IA Meristem por fases (PR #77 día 19)**: 7 fases progresivas + 6 principios transversales. Frase clave Meristem para apertura del §6: *"el slow brain doméstico no compite con cloud. Compite con el agricultor que abre Excel y mira cuatro columnas."*
  - **Voz multimodal Gemma 4 E4B nativa** (Floema día 19): uso real de capacidades multimodales sin SpeechRecognizer Android. Diferenciador concreto vs ganador 2025 (Gemma 3n + ML Kit).
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
| **Special LiteRT** | $10k | Pollen usa LiteRT-LM en E4B on-device + **voz multimodal Gemma 4 E4B nativa día 19** (diferenciador concreto vs Gemma Vision 2025) | **Alta + diferenciada** | ✅ Sí (verificar si solo 1 Special) |
| **Special Cactus** | $10k | Local-first mobile que routes between models | Verificar si framework específico | ✅ Sí |
| **Impact Global Resilience** | $10k | Encaje literal: offline, edge-based, climate mitigation | Alta — solo si NO Main | ❌ |
| **Impact Safety & Trust** | $10k | Lógica determinista + decisions_by_rule + ESP32 veto + GPU RD04 deriva sin romper sistema | Alta — solo si NO Main | ❌ |
| **Impact Digital Equity** | $10k | Operator_note literal castellano + UX bilingüe | Media — solo si NO Main | ❌ |

---

## Decisiones operativas pendientes

| # | Decisión | Dueña | Plazo |
|---|----------|-------|-------|
| 1 | ~~Mergear PRs #68/#69/#70~~ — cerrado día 18 + #63/#72/#73/#74/#75/#76/#77/#78/#79/#80/#81/#82/#83/#84 cerrados día 19 (13 merges en cadena) | — | — |
| 2 | Cactus framework verificación — *"solo si da tiempo"* (Bea día 19) | Bea + Floema/Meristem/Xilema | Si tiempo |
| 3 | ~~`video-tools/` al repo~~ — cerrado: NO entra (Bea día 19, foco narrativo Gemma 4) | — | — |
| 4 | Frases fuertes revisión consolidada — propuesta en `CAJON/cambios_guion_para_corola_dia19.md`, sesión los tres día 20 | Cambium + Bea + Corola | Sesión día 20 |
| 5 | Reorganizar writeup índice nuevo + arrancar §4 Gemma 4 | Bea + Cambium | Sesión conjunta día 20+ |
| 6 | Atribución *"Gemma is a trademark of Google LLC."* en 5 sitios | Cambium (cuando OK Bea) | Pre-deadline |
| 7 | ~~Verificar branding Venation no pisa Gemma~~ — cerrado día 19 (PR #74 mergeado) | — | — |
| 8 | Stash `[corola]` con update estado_vivo de día 16: descartar o aplicar | Bea + Cambium | Sesión conjunta |
| 9 | ~~Merge `feat/corola-guion-v1`~~ — cerrado día 19 (guion v1.7 en main) | — | — |
| 11 | Endpoint público Meristem (Cloud Run / Fly.io) — Plan B con flavors `demo` Mock ya en place | Floema + Meristem | Si tiempo |
| 12 | Verificar coste Appetize.io versión gratuita al subir APK demo real | Floema | Día 20+ |
| 15 | ~~Pasar a Floema material `.jsx`~~ — cerrado día 19 (PR #76 mergeado, paquete jsx-reference en `handoff/floema/`) | — | — |
| 13 | Meteo dentro/fuera del MVP (depende Froggit) | Bea + Xilema | Si tiempo |
| 14 | Slack MCP — solo Corola | Bea | Post-hackathon |
| **16** | **PR #85 Venation cenital cadencia** — decisión Corola sobre 3 preguntas (cadencia 5 cartelas / B1 vs B2 Pollen / aclaración bookend) | Corola gatekeep | Día 20 |
| **17** | **¿Mata E8 caducidad o no?** Opción B (sin E8) vs Opción C (con E8 + cenital corto) | Bea + Corola en sesión los tres | Día 20 |
| **18** | **Cadencia cartela final E9** — variante Corola v1.7 vs modulación Cambium *"Federated. Autonomous."* | Corola en sesión los tres | Día 20 |
| **19** | **Frase 6 dónde va** — VO E9 (cenital) o VO E9b (Bea tecleando) | Corola en sesión los tres | Día 20 |
| **20** | **RH02 regression en safe-cpu desde main** — bisección controlada, no tunear caliente | Endo + Meristem coordinan | Día 20 |
| **21** | **Variante D WS implementación** — servidor (Meristem) + cliente (Floema) | Meristem + Floema | Día 20-21 |
| **22** | **UI Meristem real para E3b + E9b** | Meristem genera, Corola integra | Día 20-21 |

---

## Pendientes activos día 23

### Bea
- **Montaje Fase A** según schematics #73 con apoyo Xilema (BME280, USB, depósito, tubos, bomba/caudal/válvulas físicamente sin energizar, borneras y etiquetas)
- **NO conectar 12V/actuadores** hasta cableado protegido revisado
- **Sesión conjunta los tres** (tú + Cambium + Corola) para cerrar 4 abiertos del guion v1.7 (matar E8 sí/no, cadencia cartela final E9, frase 6 dónde va, opciones B/C timing)
- **Sesión conjunta tú + Cambium** para writeup índice + §4 Gemma 4 + decisión sobre stash `[corola]` día 16
- Voto sobre PR #85 (cenital cadencia Venation) si quieres decidir directo
- Voz humana real E5 castellano: confirmar quién graba (probable Bea, días 24-25)

### Xilema
- **Soporte presencial a Bea en montaje Fase A**
- **NO conectar 12V/actuadores** hasta cableado protegido revisado
- Próximo PR firmware: fijar pinout real humedad/nivel/caudal/actuadores + probar GPIOs sin carga + transición controlada desde DRY_RUN
- Convertir secuencia ping Jetson↔ESP32 en escenario reproducible (runner controlado)
- Mensaje pendiente Meristem (validación dominio prompt + 5 bundles + nomenclatura `SAFETY_DOWNGRADE` ↔ `HARD_LIMIT_DOMAIN`)

### Endodermis
- **Pull limpio main + verificar adapter `:12000` + fachada `:13010` siguen vivos**
- **Investigar RH02 regression** en safe-cpu desde main (2/2 falla critical) — coordinar con Meristem, no tunear caliente
- GPU offload pendiente RD04/RH02 — post-hackathon
- Coordinar primer flujo Jetson↔ESP32 bajo liderazgo Xilema cuando ella avance firmware actuadores

### Floema
- **Implementar `MeristemSocketClient` WS Variante D** — coordina con Meristem (ella implementa servidor)
- **Empaquetar release APK demo flavor** + congelar cambios pre-Hackathon. Plazo draft live demo día 22, pulido día 28
- **Verificar coste Appetize.io versión gratuita** al subir APK demo real
- Pasar capturas alta fidelidad de `VisitarRhizomeScreen` bilingüe a Venation para validación copy
- Si Bract pide screencast Pollen procesando voz humana real para draft CapCut: app demo flavor cubre

### Meristem
- **Implementar servidor WS Variante D** — coordina con Floema (ella implementa cliente). Bidireccional desde primera hora
- **Generar UI Meristem real** para E3b (composing — `PolicyComposer`) y E9b (processing/storing post-`/visit`) — material para video, coordinar con Corola/Venation
- **Coordinar con Endo diagnóstico RH02** sin tunear en caliente
- `decisions_by_rule` en `/health` si tiempo sobra
- Mensaje pendiente Xilema (validación dominio prompt + 5 bundles + nomenclatura)
- Mini-experimento contexto (3 bundles × 4 num_ctx) si tiempo

### Corola
- **Sesión conjunta los tres** (tú + Bea + Cambium) para refinar v1.7
- **Generar `copies_bilingual.md` v0.2** con copies actualizados v1.7
- **Producir `montage_brief.md`** para Bract con detalle plano-por-plano + copies CapCut sobre v1.7
- **Decidir PR #85 Venation** sobre cadencia cenital
- Coordinación Bract sobre formatos exportar y plazo draft inicial CapCut sobre v1.7
- Coordinación Meristem para UI Meristem en E3b y E9b
- Posible regeneración 2 PNG Venation (E01 lower-thirds + Z99 cierre con texto definitivo)
- B-roll tierra agrietada microcorte E1 — confirmar producible o descartar

### Bract
- **Esperar `montage_brief.md` v1.7 + `copies_bilingual.md` v0.2** de Corola
- **Tras llegar v1.7**: regenerar draft CapCut con cartelas EN literales en posición exacta + capa de texto separada
- Esperar respuesta Venation sobre tipografía Manrope + IBM Plex Mono
- Cuando Bea pase material rodado real: doble análisis con dossier + sin
- Capturas Jetson E2-E3-E7 — coordinar con Endo cuando hueco mutuo

### Venation
- **Esperar decisión Corola PR #85** sobre cadencia cenital — bloqueo principal
- **Tras decisión Corola**: animar cenital E09 (HTML autocontenido + 480 PNG transparentes) en `handoff/bract/2026-05-04-cenital-anim/`
- **Regenerar Z99 cierre** con texto definitivo confirmado v1.7
- Posible regeneración E01 lower-thirds tras sesión estratégica
- Esperar UI Meristem real para integrar al sistema visual de E3b + E9b

### Cambium
- **Sesión conjunta tú + Bea** para writeup índice + §4 Gemma 4 + decisión stash `[corola]`
- **Sesión conjunta los tres** (tú + Bea + Corola) para cerrar 4 abiertos guion v1.7
- Update `docs/40_pitch_video.md` v3 con cambios v1.7 cuando Corola dé OK (sesión)
- Trademark statement Gemma en 5 sitios cuando Bea OK
- Commit PDF naming guidelines a `docs/external/` cuando Bea OK
- README ganador EN-primero cuando writeup avance
- Mergeo PR #85 Venation tras Corola gatekeep

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
