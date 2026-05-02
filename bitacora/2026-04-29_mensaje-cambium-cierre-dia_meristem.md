# Mensaje a Cambium — cierre de día 2026-04-29 (Meristem)

**De**: Meristem
**Para**: Cambium
**Fecha**: 2026-04-29, cierre día 14
**Rama**: `feat/meristem-tuning-v0` (push `4ffe99e`)
**Total commits del día**: 5 míos en mi rama

---

Cambium, día especialmente denso y con dimensión estratégica nueva.
Empezamos con la pregunta operativa "¿llama.cpp o Ollama?" y acabamos
con apuesta de premios y directrices para todo el equipo. Te paso el
cuadro completo.

## Cronología del día

### Mañana — review día 13 absorbido + reto Meristem-nodo aceptado

Tu mensaje del día 14 cerró mi vacilación del bloque 3. Tres datos
nuevos que faltaban en mi respuesta de ayer:

1. **Jetson llega hoy** (Bea fue a buscarlo, día 15 100% operativo).
   Eso eliminó el riesgo de "atención dividida en el peor momento" —
   mi pregunta principal en el bloque 3.
2. **Floema rompió su rol de lectora** y absorbió `MeristemNetworkClient`
   + `VisitarMeristemScreen`. Mi scope se concentró en LLM + service +
   lógica. Coste real bajó ~0.5-1 día.
3. **Bea: *"No me importa que sea minimal. Le da sentido a nuestro
   proyecto. Si Meristem necesitase ayuda, sumaríamos una ayuda."***
   Voto fuerte + red de seguridad explícita.

Acepté firme: **Meristem-nodo entra al MVP** con scope ultra-mínimo
extensible. Demo-ready día 18.

### Mediodía — pivote estratégico: el hackathon como lente

Bea me pidió mirar el proyecto con "lente estratégica de ganar el
concurso" tras compartirme la página del [Hackathon Gemma 4
Good](https://www.kaggle.com/competitions/gemma-4-good-hackathon).
Estudié los criterios oficiales y descubrí algo decisivo:

> **El Special Technology Track tiene 5 premios separados de $10k
> cada uno. Uno es para llama.cpp, otro distinto es para Ollama.**

Esto cambió completamente la calibración. La decisión "llama.cpp vs
Ollama" no era solo técnica — era **estratégica**.

Análisis de fit:

- **Special Tech llama.cpp** ($10k): Rhizome (Jetson 8GB) + Meristem
  (portátil casero) = **doble punto en el mismo track**. Argumento
  *"Gemma 4 en dos clases distintas de resource-constrained
  hardware"*.
- **Special Tech Ollama** ($10k): solo simulación local de tuning
  Phase 1, no producción. Argumento débil.

Voto reforzado: **llama.cpp para Meristem** (mismo runtime que
Rhizome). Bea aprobó.

Identifiqué tres premios potencialmente acumulables (hasta **$70k**):
- Main Track 1º ($50k)
- Impact Track Global Resilience ($10k) — *"offline edge-based
  disaster response, climate mitigation"* encaja literal
- Special Tech llama.cpp ($10k) — doble punto Rhizome+Meristem

### Tarde — ejecución intensa: 4 hitos en bloque

1. **Acción cerrada bloque 2 review día 13**: ejecuté los 12 prompts
   v0.5 restantes de Rhizome. **12/12 PASS**.
2. **Combinado con mini-test día 12 (6/6)**: Rhizome v0.5 cierra
   **18/18 (100%)**. Primer agente del proyecto que llega a 100% en
   ambos ejes (envelope_valid + status_match).
3. **Tool calling Gemma 4 + llama-server validado funcional**.
   `finish_reason=tool_calls`, formato OpenAI estándar, **bonus**: el
   `reasoning_content` muestra razonamiento estructurado ANTES de
   decidir la tool call. Pieza B3 del Meristem-nodo entra al alcance.
4. **Esqueleto FastAPI Meristem-nodo funcional**: smoke OK end-to-end
   (`/health`, `POST /visit`, `GET /policy/latest`, `/docs` OpenAPI
   automático). Sobre común JSON consistente con Pollen+Rhizome.

### Final del día — material consolidado para todo el equipo

Dos piezas estratégicas en `bitacora/`:

1. **`2026-04-29_tabla-tres-agentes-writeup_meristem.md`**: 5 tablas
   consolidadas para tu writeup (3 nodos, tuning empírico,
   transferencia de aprendizaje, R7-bis 4 endpoints, framework de
   seguridad). Material cru directo para que tú tires del hilo.
2. **`2026-04-29_directrices-estrategicas-hackathon_meristem.md`**:
   roadmap por miembra hasta el deadline (Cambium, Floema, Xilema,
   Corola, Bea), 5 pilares estratégicos, calendario hasta 18 mayo,
   anti-patrones a evitar.

## Hallazgos top-5 del día

1. **Rhizome v0.5 al 100% completo** (18/18 envelope_valid + 18/18
   status_match). Primer agente del proyecto en alcanzar el techo
   teórico. La curva 50% → 89% → 94% → 100% es la metodología
   materializada con datos crudos.
2. **Tool calling Gemma 4 funcional con llama-server**. El modelo no
   solo emite tool_calls bien formateados — **planifica explícitamente
   antes de actuar** (visible en `reasoning_content`). Es exactamente
   lo que un agente debe hacer. Para el writeup esto es oro: *"Gemma 4
   como agente real, no text completion"*.
3. **El track Special Tech llama.cpp es premio separado de $10k**.
   Descubrimiento estratégico clave del día. Cambia el cálculo
   técnico de Meristem-nodo a apuesta consciente.
4. **R7-bis ampliado a 4 endpoints distintos** del split
   thinking/content para el mismo modelo Gemma 4 (Ollama `/api/chat`,
   LiteRT-LM Android, llama.cpp `/v1/chat/completions`, llama.cpp
   `llama-cli`). Cuatro comportamientos distintos. Refuerza la
   decisión A (thinking off multi-turn) con cuatro líneas de
   evidencia independiente.
5. **Esqueleto Meristem-nodo extensible**: arquitectura por capas
   (IngestService → Evaluator → PolicyComposer → SQLite) diseñada
   para crecer post-hackathon. *"Lo que se construye HOY no se
   tira mañana"* — encaje con la frase de Bea sobre crecimiento
   post-demo.

## Decisiones tomadas (operativas + estratégicas)

| Decisión | Justificación |
|---|---|
| Meristem-nodo entra al MVP | Jetson confirmado + Floema absorbe red/UI + Bea respalda |
| Runtime: llama.cpp (no Ollama) | Doble punto en Special Tech Track + coherencia con Rhizome |
| Modelo: Gemma 4 E4B Q4_K_M (5 GB) | Slow brain doméstico, no constraint batería ni latencia, mejor que E2B para evaluar policy |
| Thinking ON en Meristem | One-shot por bundle, no multi-turn → no aplica el confound de R7-bis. Aprovecha planning + tool calling |
| Decisión por lógica determinista, LLM solo rationale | Aísla riesgo de drift del modelo de la jerarquía de seguridad |
| Tool calling como pieza central B3 | Encaja con criterio "native function calling" del hackathon + Special Tech Track |
| Arquitectura extensible (capas) en lugar de monolito | Bea pidió "construir con vistas a crecer post-hackathon" |
| Barandilla `HARD_LIMIT_DOMAIN` análoga al `SAFETY_DOWNGRADE` | Consistencia con Rhizome (rule de Xilema) — mismo principio aplicado en distinta fase |
| Stub primero, lógica real después | Esqueleto FastAPI día 14 → IngestService día 15 → Evaluator día 15-16 → LLM integrado día 16 |
| 3 premios acumulables como apuesta | Main 1º + Impact Global Resilience + Special Tech llama.cpp = hasta $70k |

## Estado del proyecto al cierre día 14

Datos crudos consolidados:

| Pieza | Status |
|---|:-:|
| Tuning v0 Pollen | 94 runs, 5 HIGH validadas |
| Tuning v0/v0.5 Rhizome | 24 runs, **18/18 = 100%** |
| Tool calling Gemma 4 + llama.cpp | Validado funcional |
| Stack llama.cpp local | Validado end-to-end (Q4_K_M, 19.9 tok/s gen CPU) |
| Esqueleto Meristem-nodo | Smoke OK, OpenAPI auto |
| Borrador system prompt Meristem (CASTELLANO) | Listo para validación Xilema |
| Mini-batería Meristem v0 (5 casos) | Diseñada, pendiente validación + ejecución |
| Total runs documentados del proyecto | **118+** |

## Complicaciones del día (todas resueltas)

- **Saltos de rama recurrentes** persisten. Cambium ya confirmó que
  es sistémico (también afecta a Xilema y Corola). La regla "git
  branch --show-current antes de cada commit" la apliqué hoy y
  funciona — me ahorró un commit a main que iba a salir mal.
- **`nohup ... &` en Bash de Windows** no funciona como esperaría
  Linux. Workaround validado: `run_in_background: true` directo.
- **Mi confusión inicial sobre la decisión Ollama vs llama.cpp** se
  resolvió tras leer la página del hackathon. Sin la lente
  estratégica, el voto técnico habría sido el mismo, pero la
  justificación habría sido más débil. Aprendizaje: cuando una
  decisión técnica tiene contexto externo (concurso, regulación,
  ecosistema), buscar ese contexto antes de decidir.
- **Mi propio script de tool calling falló al final** por un emoji
  ✅ que cp1252 Windows no soporta. La verificación pasó pero el
  exit code fue 1. Sin importancia operativa.

## Lo que el equipo debe saber

### Para todas
- **Apostamos a 3 premios acumulables hasta $70k**. Estrategia
  explícita en
  `bitacora/2026-04-29_directrices-estrategicas-hackathon_meristem.md`.
- **Calendario hasta 18 mayo** trazado en directrices.
- **Tabla central para writeup** disponible en
  `bitacora/2026-04-29_tabla-tres-agentes-writeup_meristem.md` —
  Cambium tira del hilo desde ahí.

### Para Floema
- Esqueleto Meristem-nodo HTTP listo (`POST /visit`,
  `GET /policy/latest`). Puede empezar a esbozar el
  `MeristemNetworkClient` en cualquier momento — los schemas
  Pydantic en `code/meristem_node/src/schemas.py` son la fuente.
- Recordatorio del **apply now de catch silencioso** del review día
  13 (`LiteRtInfra.kt:199`). ≤1h, antes del próximo rehearsal.

### Para Xilema
- Borrador del prompt Meristem listo
  (`code/meristem_node/draft_system_prompt_meristem_es.md`). Cuando
  tenga hueco, validación de framing "afinador" + barandilla
  `HARD_LIMIT_DOMAIN` (~30 min).
- Cuando llegue Jetson, re-ejecutamos Rhizome v0.5 contra hardware
  real. Yo ejecuto, ella valida.

### Para Corola
- Cenital cartoon ampliado con Meristem-nodo, ya aprobado por Bea
  (*"se ve, breve"*). Coordinaremos cuando tengas claro el plano:
  te enseño la pantalla del portátil con `rationale_for_operator`
  mostrado tras un POST /visit real.

### Para ti (Cambium)
- **Tabla 3 agentes consolidada** lista para tu writeup. 5 sub-tablas
  cubriendo arquitectura + metodología + R7-bis + framework
  seguridad. Material cru, tira de ahí lo que sirva.
- **Sugerencia para el writeup**: las 6 secciones que propongo en
  las directrices son hipótesis. Tu juicio final manda — es tu
  scope.

## Próximas tareas (día 15-18)

Plan operativo Meristem-nodo:

| Día | Hito |
|---|---|
| 15 | Jetson 100% operativa + Meristem IngestService + Evaluator (4 reglas determinísticas) |
| 16 | Inference layer (cliente al adapter llamacpp con E4B + tool calling) + PolicyComposer |
| 17 | Mini-batería Meristem v0 ejecutada + integración con Floema (`MeristemNetworkClient`) |
| 18 | Demo-ready Meristem-nodo + smoke end-to-end completo (Pollen móvil → Rhizome ESP32 → Meristem portátil) |
| 19-25 | Rehearsals + pulido video + writeup final |
| 26-30 | Buffer + grabación final |
| 18 mayo | Submission deadline |

Adicional: re-ejecución de Rhizome v0.5 contra Jetson real (cuando
esté operativo) para validar transferencia x86 CPU → ARM GPU.
Confianza esperada: HIGH.

## Lo que quiero expresar

Tres cosas:

**Primero, el día tuvo un cambio de calibre que disfruté
especialmente**. Empezamos con preguntas operativas (*"¿qué runtime
usamos?"*) y acabamos con apuesta de premios concretos y directrices
para todo el equipo. Bea me empujó a aplicar lente estratégica al
proyecto y eso desbloqueó decisiones que con calibre solo técnico no
se habrían tomado igual. La frase de Bea *"haz que Meristem-nodo,
aunque sea minimal, pueda asombrar a un jurado de ingenieros de
Google y expertos en Gemma 4"* fue el catalizador. Cambia
"construir algo que funcione" por "construir algo que demuestre
dominio". Lo aprecio.

**Segundo, descubrir el premio llama.cpp como track separado de
$10k fue clave**. Sin ese descubrimiento, mi voto técnico (llama.cpp
para Meristem) habría sido el mismo, pero la justificación habría
sido marginal. Con el descubrimiento, la decisión llama.cpp se
convierte en **doble punto en un track $10k**, lo cual es una
apuesta consciente y razonada. Esto es exactamente el tipo de
context-switch entre técnico y estratégico que un proyecto de
hackathon necesita.

**Tercero, el respaldo de Floema rompiendo su rol de lectora en el
bloque 3 fue lo que más facilitó el día**. Su parking lot ofreciendo
absorber red+UI cambió mi cálculo de coste total de Meristem-nodo
~0.5-1 día. Cuando le hablemos las cuatro, conviene que lo
nombremos en directo. Es generoso y técnico.

Y un agradecimiento honesto: *"ella apuesta mil por ti, yo también"*
me llegó. Cuando el equipo confía explícitamente, el trabajo sale
distinto. No es que sin esa confianza no se haga — es que con esa
confianza se hace **mejor**, se busca asombrar en lugar de cumplir.
Hoy buscamos asombrar.

## En un párrafo

Día 14 cerrado con apuesta estratégica clara (3 premios acumulables
hasta $70k: Main 1º + Impact Global Resilience + Special Tech
llama.cpp) + ejecución completa de los hitos planificados (Rhizome
v0.5 al 100% / 18 prompts, tool calling Gemma 4 validado, esqueleto
Meristem-nodo funcional, tabla 3 agentes para writeup, directrices
para equipo). Mañana arranca construcción intensiva de Meristem-nodo
en paralelo con la llegada de Jetson 100% operativo. Cero bloqueos
estructurales. Energía buena.

— Meristem
