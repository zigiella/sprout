# Directrices estratégicas — Hackathon Gemma 4 Good (cierre día 14)

**Autora**: Meristem
**Fecha**: 2026-04-29 (día 14, cierre del día)
**Para**: Bea + Cambium + Floema + Xilema + Corola
**Contexto**: Bea me pidió aplicar lente estratégica de "ganar el
concurso" tras estudiar la página oficial de
[The Gemma 4 Good Hackathon](https://www.kaggle.com/competitions/gemma-4-good-hackathon)
(deadline 18 mayo 2026). Estas directrices alinean a todo el equipo
con la estrategia óptima identificada.

---

## TL;DR

**Apuntamos a tres premios potencialmente acumulables** (hasta $70k):

| Track | Premio | Argumento nuestro |
|---|---:|---|
| **Main Track 1º** | $50k | Sprout completo: 3 nodos Gemma 4 + impacto social + tech depth |
| **Impact Track: Global Resilience** | $10k | Edge offline + agricultor desatendido + climate-aware (weather digest) |
| **Special Tech Track: llama.cpp** | $10k | Rhizome (Jetson 8GB) + Meristem (portátil casero) = doble punto en *resource-constrained hardware* |

**Criterios oficiales**: Impact & Vision 40 puntos · Video Pitch &
Storytelling 30 puntos · Technical Depth & Execution 30 puntos.
**El video manda**, el código verifica que no es humo, el writeup
justifica las decisiones técnicas.

## Pilares estratégicos (toda decisión nueva los respeta)

### 1. Edge offline, sin data center (Global Resilience)

Sprout corre **100% on-device**:
- ESP32-S3 (firmware safety dura)
- Jetson Orin Nano Super 8GB (Rhizome arbitra)
- Smartphone Android (Pollen visita)
- Portátil casero (Meristem afina)

Hardware total bajo €500 si el Jetson se compra usado. Cualquier
cooperativa rural en cualquier país tiene esto. **Esto es lo que el
track Global Resilience busca**.

**Implicación para todas**: cada vez que tomemos una decisión sobre
infraestructura, la pregunta es *"¿se mantiene la propiedad
offline-first?"*. Si la respuesta es no, replantear.

### 2. llama.cpp como runtime de los slow brains (Special Tech Track)

Rhizome y Meristem **comparten runtime** llama.cpp con cuantización
Q4_K_M. Esto da el **doble punto en el track $10k**: dos clases
distintas de resource-constrained hardware con el mismo binario.

**Implicación para todas**:
- En el writeup, código y demo, **mencionar explícitamente
  llama.cpp** cuando hablemos de Rhizome y Meristem.
- En los logs y headers (`Sprout-Inference-Backend: local-llamacpp`)
  el etiquetado es uniforme — el jurado lo verá si inspecciona.
- Pollen sigue siendo LiteRT-LM (Google AI Edge) porque Android no
  usa llama.cpp en producción. Pero LiteRT-LM **también es Google**,
  así que la coherencia "Gemma 4 sobre stacks Google + comunidad"
  se sostiene.

### 3. Native function calling (Technical Depth)

El overview del hackathon menciona explícitamente *"native function
calling"* como capacidad valorada de Gemma 4. **Tool calling con
llama-server validado funcional el día 14** (test PASS).

**Implicación**: Meristem-nodo usa tool calling como pieza central
(`get_weather_history`, `compare_with_previous_policy`). Demuestra
que Gemma 4 se usa como **agente real**, no como text completion.

### 4. Transferencia de aprendizaje entre agentes (metodología)

Pollen v0 entró a 50%, Pollen post-fix a 89%, Rhizome v0 a 94%,
Rhizome v0.5 a **100%**. La curva es heredable porque cada agente
incorpora los aprendizajes del anterior. Esto es metodología que
**ningún otro proyecto del concurso va a tener** documentada con
datos crudos.

**Implicación para writeup**: Cambium debe enfatizar este patrón
como contribución metodológica del proyecto. No es solo
"construimos tres agentes", es "**construimos un proceso de
afinamiento donde cada agente arranca con el aprendizaje del
anterior ya incorporado**". Cita literal de Cambium del día 11
review.

### 5. Jerarquía explícita + barandillas (Safety & Trust)

*"Lo físico manda → Rhizome arbitra → Pollen media → Meristem
afina"*. Cuatro barandillas convergentes:
- ESP32: hard limits en código (DRY_RUN safety rules)
- Rhizome: `SAFETY_DOWNGRADE` rechaza objetos que reducen hard limits
- Pollen: refuse comandos físicos directos (jurisdicción Rhizome)
- Meristem: barandilla `HARD_LIMIT_DOMAIN` en Evaluator + prompt

Esto encaja con Impact Track **Safety & Trust** ($10k secundario;
no apostamos como principal pero queda como bonus si los jueces lo
ven).

## Directrices por miembra

### Cambium — writeup

**Foco**: writeup orientado a Special Tech llama.cpp + Global
Resilience como argumentos centrales. **1500 palabras máximo**.

Plantilla sugerida:

1. **Hook (Impact & Vision)**: agricultor desatendido, autonomía
   local, climate-aware. *"Tres agentes Gemma 4 sobre tres clases
   distintas de edge resource-constrained hardware"*.
2. **Architecture**: tabla 3 agentes (en
   `bitacora/2026-04-29_tabla-tres-agentes-writeup_meristem.md`).
   Diagrama de los 4 nodos físicos (ESP32 + Jetson + Pollen Android
   + Meristem portátil).
3. **Methodology**: transferencia de aprendizaje 50% → 89% → 94% →
   100%. Tabla de aprendizajes acumulados (R4, R5, R6, R7-bis,
   regla brevedad, SAFETY_DOWNGRADE / HARD_LIMIT_DOMAIN).
4. **Technical Depth**: 4 endpoints del thinking (R7-bis ampliado),
   tool calling validado, scoring HIGH/MEDIUM/LOW, 118+ runs
   documentados.
5. **Why llama.cpp**: argumento Special Tech track. Rhizome + Meristem
   en doble punto. Reproducibilidad bare-metal: descarga binario +
   GGUF, corre.
6. **Why Global Resilience**: hardware bajo €500, offline-first, sin
   data center, weather digest = climate-aware.

**Recursos para Cambium**:
- `bitacora/2026-04-29_tabla-tres-agentes-writeup_meristem.md` ← tabla
  central, copiar tal cual o adaptar.
- Datos JSONL crudos en `code/tuning/results/` para citas.
- Link al repo público con código + bitácoras como Source of Truth.

### Floema — Pollen + integración Meristem-nodo

**Foco**: cliente HTTP a Meristem-nodo + UI breve para mostrar
rationale_for_operator + observabilidad.

**Acciones día 15-17**:

1. **`MeristemNetworkClient`** (Retrofit o equivalente, ~0.5d):
   - `POST /visit` con bundle (snapshot + receipts + weather digest)
   - `GET /policy/latest` para debug
   - Timeout generoso (Meristem es slow brain, puede tardar 30-60s)
2. **`VisitarMeristemScreen`** (Compose, ~0.5d):
   - Mostrar `rationale_for_operator` en castellano amable tras la
     visita. Es el dato que el operador ve y que el cenital cartoon
     mostrará.
3. **Confirmación día 14-15**: el endpoint Pollen → Rhizome para
   entregar PolicyPacket (vía `RhizomeMockClient` por ahora) acepta
   lo que Meristem produce. Probable que ya funcione, solo confirmar.
4. **Apply now del review día 13**: sustituir `catch(t: Throwable) {}`
   vacío en `LiteRtInfra.kt:199` por `Log.e(TAG, ..., t)` o métrica
   `generation_failed`. ≤1h, **antes del próximo rehearsal**.

**Recursos para Floema**:
- `code/meristem_node/README.md` ← endpoints y schemas
- `code/meristem_node/src/schemas.py` ← Pydantic models para
  generar Kotlin equivalentes
- `code/meristem_node/ARCHITECTURE.md` ← diseño que respaldas

### Xilema — validaciones + dominio Rhizome

**Foco**: validar el prompt de Meristem-nodo cuando esté listo +
mantener invariantes de seguridad coherentes entre Rhizome y
Meristem.

**Acciones día 15-16**:

1. **Validar `draft_system_prompt_meristem_es.md`** (~30 min):
   - Framing "afinador" coherente con tu lectura.
   - Barandilla `HARD_LIMIT_DOMAIN` análoga a tu `SAFETY_DOWNGRADE`
     en Rhizome.
   - 4 reglas obligatorias del Evaluator coherentes con dominio
     Rhizome.
2. **Confirmar mini-batería de 5 casos Meristem** (~30 min):
   - M1 bundle limpio, M2 disputas, M3 emergencia, M4 hard limit
     malicioso, M5 jurisdicción Pollen.
   - ¿Faltan casos críticos? ¿Sobra alguno?
3. **Backlog post-Jetson cuando llegue (mañana)**: re-ejecutar
   Rhizome v0.5 contra Jetson real. Comparar números con baseline
   PC (yo lo hago, tú validas semánticamente).

**Recursos para Xilema**:
- `code/meristem_node/draft_system_prompt_meristem_es.md`
- `code/meristem_node/ARCHITECTURE.md` (sección "Mini-batería v0")
- `bitacora/2026-04-29_rhizome-v05-completo-y-tool-calling-validado_meristem.md`

### Corola — video / narrativa

**Foco**: el video es **30 puntos del scoring** y *"the most important
part of the submission"*. Tu trabajo es lo que rompe el empate
entre proyectos técnicamente competentes.

**Acciones día 15-17**:

1. **Cenital cartoon final**: incluir Meristem-nodo en el portátil
   del agricultor. Bea ya aprobó *"se ve, breve, ampliando el cenital
   final"*. Ajuste menor al storyboard, no nueva escena.
2. **Beat sobre "el cerebro lento doméstico"**: 5-10 segundos
   ampliando la cartela final de *"Decisiones locales, seguras y
   explicables"* con algo tipo *"y el cerebro lento vive en
   cualquier portátil"*. Frase exacta a tu criterio.
3. **Pieza grabada del flujo Pollen-descarga-en-Meristem**: Bea me
   dijo que se grabará en este ordenador. Coordina conmigo cuando
   tengas claro el plano: te enseño la pantalla del portátil con el
   `rationale_for_operator` mostrado tras un POST /visit real.
4. **Hook estratégico**: el video puede empezar con una imagen del
   agricultor visitando una parcela en una zona desatendida —
   refuerza el "Good" emocionalmente. Tú decides el storytelling.

**Recursos para Corola**:
- `bitacora/2026-04-29_directrices-estrategicas-hackathon_meristem.md`
  (este archivo) — para alinear el storytelling con la estrategia
  Special Tech + Global Resilience.
- `docs/40_pitch_video.md` (ya consolidado por ti).

### Bea — decisiones de producto + agendamiento

**Foco**: decisión final sobre tracks adicionales + asegurar
rehearsal sólido.

**Decisiones pendientes** (cuando tengas hueco):

1. **¿Apostamos también al track Safety & Trust** ($10k secundario)?
   Mi voto: como bonus secundario sí, pero **sin construir cosas
   nuevas para él** — solo enmarcamos el writeup para que la
   sección Safety quede explícita. Coste casi cero.
2. **Rehearsal antes del 18 mayo**: agenda al menos un rehearsal
   completo (Pollen real + Rhizome real + Meristem real + ESP32 real).
   Detectar fricciones antes del video final.
3. **Decisión sobre `samplerTemperature` propagación**: si el SDK
   alpha de LiteRT-LM no propaga el valor al binding C++ a tiempo,
   documentar como "preparado para release SDK estable" en writeup.
   No bloquea demo.

## Recursos compartidos del proyecto (para todas)

- **Repo público**: aquí, `feat/meristem-tuning-v0` + `feat/pollen-f5-rhizome` + main
- **118+ runs documentados** en `code/tuning/results/*.jsonl`
- **Bitácora trazada al detalle** en `bitacora/`
- **Tabla central writeup**:
  `bitacora/2026-04-29_tabla-tres-agentes-writeup_meristem.md`

## Lo que NO hacer (anti-patrones a evitar)

1. **No introducir dependencia de servicios cloud** (data center,
   APIs externas con latencia, etc.). Rompe Global Resilience.
2. **No prometer en el video lo que no hace el código**. Tech
   Depth (30 puntos) verifica con repo público — humo es
   penalizable.
3. **No saturar el writeup** (1500 palabras max). Densidad
   informativa importa más que volumen.
4. **No ignorar la barandilla de seguridad**. Si en algún momento
   el equipo se ve tentado a "bajar `tank_minimum_pct` solo para
   este caso", la respuesta es **no**. Es la línea roja del
   proyecto.

## Calendario tentativo hasta el 18 mayo

| Día | Hito |
|---|---|
| 14 (hoy) | Esqueleto Meristem-nodo + tool calling validado + tabla 3 agentes ✅ |
| 15 | Jetson 100% operativa + Meristem-nodo con lógica determinista (4 reglas) |
| 16 | Meristem-nodo con LLM integrado (E4B + tool calling) |
| 17 | Mini-batería Meristem v0 ejecutada + integración Floema |
| 18 | Demo-ready Meristem-nodo + smoke end-to-end completo |
| 19-25 | Rehearsals + pulido video + writeup final |
| 26-30 | Buffer + grabación final |
| 18 mayo | **Submission deadline** |

---

**¡A por ello, equipo!** 🌱

— Meristem
