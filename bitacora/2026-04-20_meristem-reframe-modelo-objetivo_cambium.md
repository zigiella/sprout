# Reframe de Meristem: modelo objetivo 26B, estrategia de demo, harness comparativo

**Fecha:** 2026-04-20
**Autor:** Cambium (a partir de conversacion con Bea la manana del dia 6)
**Area:** Arquitectura Meristem / narrativa del proyecto / plan de validacion
**Tipo:** Decision de producto + plan de ejecucion
**Estado:** firme, para compartir con Meristem (persona) y despues con Corola

---

## Contexto y motivo del reframe

Dos bitacoras previas dejaron a Meristem con un diseno a medias:

- `2026-04-19_meristem-como-revision-diferida_cambium.md` establecio que Meristem es revision diferida, no sincrona, con E4B local como modelo.
- `2026-04-19_gemma-26b-moe-thinking-mode_cambium.md` introdujo que 26B (MoE, ~4B activos, 6-7x mas rapido que 31B dense) es la opcion clara para el modelo **sombra**.

En esa segunda bitacora dejé el 26B como "sombra opcional para auditar acuerdo" y E4B como "Meristem de produccion". Bea lo reabrio esta manana con un argumento que yo no habia verbalizado con la crudeza suficiente y que comparto entero: **presentar E4B como Meristem de produccion es deshonesto si creemos que el diseno real exige 26B+**. Meristem consolida evidencia, detecta contradicciones y emite `PolicyDelta` con rationale — es tarea de razonamiento estrategico, no de filtrado edge. Un jurado tecnico (en particular Gusthema como Gemma DevRel) va a mirar la cartela y si ve "E4B Ollama" en el nodo estrategico va a leer "modelo equivocado para el nodo equivocado". Eso resta, no suma.

Este documento formaliza el pivote y cierra todas las ramificaciones (codigo, narrativa, demo, hardware, presupuesto).

---

## Decisiones firmes

### D1. El modelo objetivo de Meristem es Gemma 26B MoE

Meristem se disena para correr **Gemma 26B MoE local** sobre hardware apropiado (Mac Studio / MacBook Pro M1+ Max 64GB / PC con RTX 3090 24GB clase). E4B queda reposicionado como **andamio de integracion**, no como modelo objetivo.

La diferencia de framing es sutil pero definitiva:
- Antes: "Meristem = E4B local. 26B sombra opcional para auditoria."
- Ahora: "Meristem = 26B en hardware objetivo. E4B local como andamio que demuestra que la integracion extremo-a-extremo funciona sobre hardware commodity mientras escalamos el modelo."

### D2. La demo se filma con Meristem ejecutando inferencia remota presentada como local, con caveat explicito

No tenemos hardware objetivo. Para este hackathon:

- La inferencia de Meristem corre contra **Gemini API (Gemma 26B)** durante desarrollo y rodaje.
- El codepath de Meristem **no sabe que la inferencia es remota**: habla contra un endpoint `localhost:11434` que es Ollama-compatible. Detras, un proxy thin reenvia a Gemini API.
- En hardware objetivo con Gemma 26B nativo, **una variable de entorno elimina el proxy** y la inferencia es 100% local. El codepath es bit-a-bit el mismo.
- En el video y en el writeup **declaramos esto sin asterisco enterrado**: una cartela de dos lineas visible, con el texto exacto acordado abajo.

Esto **no es mentir en la demo**. Es demostrar un patron migratorio cloud-to-edge con el adaptador explicito. Es lo que los jurados Gemma-DevRel quieren ver: apps que se mueven entre nube y local por configuracion, no apps casadas con un runtime concreto.

**Texto de cartela acordado (borrador para Corola):**

> "Inferencia de Meristem via proxy local hacia Gemma 26B en la nube. En hardware objetivo (MacBook Pro M1+ Max 64GB o equivalente) el mismo codepath ejecuta 100% local. Demo simulada por restriccion de hardware del hackathon."

### D3. El proxy Ollama-Gemini es pieza arquitectural, no parche

Se disena, se documenta y se lista en el writeup como componente de primer nivel. Nombre provisional: **`meristem_inference_adapter`**. Responsabilidades:

- Exponer `localhost:11434` con la API Ollama (`/api/chat`, `/api/generate`).
- Reenviar a Gemini API cuando el flag `INFERENCE_BACKEND=cloud`; pasar a Ollama real cuando `INFERENCE_BACKEND=local`.
- Tracking de coste por decision (tokens entrada + tokens salida × precio Gemini API) registrado en `decisions_log`.
- Respetar los parametros que Meristem encontro relevantes: `/api/chat` con `format=<schema>` para que thinking mode no se suprima (ver bitacora `2026-04-19_thinking-mode-e4b-latencia_meristem.md`).
- Mismo contrato de `eval_count`, `prompt_eval_count`, `eval_duration`, `prompt_eval_duration` que Ollama — para que la metrica existente siga midiendo.

### D4. El harness comparativo cross-modelo se convierte en pieza central del writeup

El sombra deja de ser "validation audit opcional" y pasa a ser **el eje de la seccion 5 del writeup** ("Validacion local vs sombra" → renombrada a "Validacion cross-modelo"). Ejecuta:

| Modelo                | Runtime            | Rol                                    |
| --------------------- | ------------------ | -------------------------------------- |
| Gemma 4B (E4B)        | Ollama local       | Andamio — lower bound de calidad       |
| Gemma 26B MoE         | Gemini API / local | Candidato objetivo A                   |
| Gemma 31B dense       | Gemini API         | Candidato objetivo B (comparacion)     |
| Claude Sonnet 4.6     | Anthropic API      | Referencia externa de calibracion      |

**Claude Sonnet se usa como referencia, no como techo.** Uso: verificar que la tarea esta bien formulada (si Claude no detecta los mismos fallos que nuestras metricas automaticas, nuestras metricas estan mal). No es "cuanto nos acercamos al mejor"; es "nuestros detectores de calidad son defendibles".

GPT-5.4, GPT-OSS 120B y similares **fuera** del harness. Si un jurado pregunta en Q&A, respondemos que la comparacion con frontera cerrada no era el objetivo, la comparacion dentro de familia Gemma si.

**Eje de tareas** que el harness evalua (ampliado tras el feedback de Bea, que cubre gaps que yo no habia codificado):

1. Emitir `PolicyDelta` con rationale coherente sobre evidencia dada.
2. Detectar contradicciones entre evidencias.
3. **Consolidacion o contraste de meteo local (Rhizome) vs meteo general (API externa).** Gap identificado por Bea — estaba implicito, no estaba en el spec.
4. **Bucle hipotesis → evidencia → analisis → aprendizaje.** Gap identificado por Bea — la retroalimentacion temporal (¿propone hoy lo contrario de lo que propuso anteayer? ¿por que?) no estaba codificada.
5. Sanity check contra reglas §30 del firmware.
6. Consistencia temporal cross-ciclo.

**Ejes de metrica:**
- Acuerdo con 31B (baseline de razonamiento interno familia).
- Acuerdo con Sonnet (referencia externa).
- Latencia efectiva (tokens/s de salida).
- Coste por decision (€ para cloud; amortizacion hardware para local).
- Precision/recall de contradicciones sobre set etiquetado.

No se llenan las 4×6×5 celdas. El diseno del harness permite correr cualquier celda que interese.

### D5. Presupuesto Gemini API aprobado: techo €150

Cubre:
- 3-4 ejecuciones completas del harness sobre set de 80-120 escenarios etiquetados.
- Inferencia Meristem en vivo durante ensayos + rodaje + demo.
- Experimentos del A/B de thinking mode (#44) sobre 26B.
- Colchon.

Cambium reporta gasto semanal a Bea. Alerta a €120 de gasto acumulado.

### D6. Hardware objetivo — decision diferida a dia 18-20

**No se compra hardware hoy.** El proxy Gemini API cubre el 80% de la demo sin coste de capital. El 20% restante — un plano de camara que muestre inferencia nativa offline — se evalua tras primer ensayo completo del video en dia 18-20.

Si en ese ensayo los planos funcionan con proxy + cartela, **no compramos**. Si hay uno o dos planos que pierden fuerza sin inferencia nativa, **Bea compra MacBook Pro M1 Max 64GB reacondicionada (~€1.900)**. ETA reacondicionado 3-7 dias → llega a tiempo para rodaje final dias 25-27.

**Por que MBP M1 Max 64GB y no otras opciones evaluadas (tabla de Bea):**

- `Samsung + eGPU RTX 3090 (€1.200)`: cadena de riesgo alta por eGPU sobre portatil no-Mac (drivers, Thunderbolt, compatibilidades). Ahorro de €700 no compensa 2-4 dias potenciales de debugging de setup cuando quedan <30 dias de proyecto.
- `Torre 7900X + RTX 3090 (€1.900)`: solida pero estacionaria. Equipo distribuido; un portatil lo rotamos entre quien lo necesite. Una torre vive en una mesa. Ademas, 24GB VRAM deja poco margen para ventana de contexto amplia.
- `MBP M1 Max 64GB reacond (~€1.900)`: **elegida**. Mismo precio que la torre, portable, 64GB unified memory permite 26B MoE con holgura y tambien 31B a Q4 si quisieramos comparar nativo. Ventana 256k por heuristica Ollama — diferencia arquitectural frente a 32k de las otras opciones (consolidar vs chunkear). Ollama/Metal maduro. M1 Max es silicio 2021 pero tokens/s en 26B MoE (~15-20 t/s salida estimados) es suficiente para Meristem deferido.
- `MBP M3 Max 64GB reacond (€3.750-4.100)`: doble velocidad, doble precio. Meristem no es latency-bound; retorno marginal no justifica coste.
- `Mac Studio M3 Ultra 96GB (€4.849)`: sobredimensionado 3x para 26B MoE.

**Verificaciones antes de comprar (si se decide en dia 18-20):** bateria ≥85%, <400 ciclos, garantia ≥12 meses, ETA de envio compatible con dia 25 como fecha limite.

### D7. E4B no desaparece — es el andamio explicito

E4B sigue en Meristem **local como entorno de desarrollo, rehearsal rapido y lower bound del harness**. Ubicacion narrativa:

- En el video: aparece como "andamio de integracion commodity" en la seccion de arquitectura del Meristem.
- En el writeup seccion 3 (arquitectura): documentado como path de ejecucion alternativo que demuestra que el sistema es portable a hardware menor si aceptas la perdida de calidad cognitiva.
- En el harness: es la fila "lower bound" de la tabla comparativa.

Con esto E4B gana presencia honesta. Deja de ser "el modelo de Meristem" (mentira) y pasa a ser "el modelo del andamio" (verdad con valor propio).

---

## Lo que NO cambia con este reframe

- Arquitectura de tres nodos (Rhizome / Pollen / Meristem).
- Contratos de datos v1.0 (`PolicyPacket`, `PolicyDelta`, `DecisionReceipt`, `RhizomeSnapshot`, `WeatherPacket`, `ContradictionAlert`) — frozen, intactos.
- Rhizome en E2B edge — no se toca.
- Pollen en E2B movil LiteRT — no se toca.
- Reglas §30 del firmware — intactas.
- Narrativa local-first — se mantiene con la honestidad sobre el limite economico del hackathon, no se sustituye por narrativa cloud.

---

## Implicaciones concretas

### Para Meristem (codigo y persona)

**El trabajo en #37 no se invalida. Al contrario: es lo que hace este pivote posible sin reescribir nada.** El `policy_engine` que Meristem construyo es model-agnostic por diseno. Cambiar de E4B a 26B es configuracion, no arquitectura. Si el engine hubiera estado acoplado al modelo concreto, este pivote nos costaria tres dias; con la abstraccion que existe, nos cuesta un PR.

El hallazgo de `/api/chat` vs `/api/generate` **gana peso**, no lo pierde: thinking mode importa *mas* en 26B que en 4B, porque el coste marginal de latencia sobre un modelo que ya razona 10-20s es proporcionalmente menor que sobre uno que razona 2s. La bitacora de Meristem del dia 5 queda como documento arquitectural vigente, no como nota historica.

**Orden de issues actualizado:**

| Issue | Estado tras reframe | Nota |
| --- | --- | --- |
| #42 quick-win `/api/chat` + thinking mode | Sin cambios | Aplica a cualquier modelo Ollama-compatible (4B local o 26B via proxy) |
| **NUEVO: `meristem_inference_adapter`** (proxy Ollama-Gemini) | Precede a #43 | 1 dia estimado. Se abre hoy |
| #43 consolidator job | Sin cambios | Model-agnostic |
| #44 thinking mode A/B | Prioridad 26B; 4B como control | Inversion de prioridad |
| #45 sombra (harness comparativo) | **Promovido a pieza central** del writeup | Incluye D4 completo |
| **NUEVO: meteo local vs general + bucle aprendizaje** | Nuevo issue de diseno | Gap identificado por Bea. Diseno antes de codigo |

Orden de ejecucion propuesto: #42 → proxy adapter → #43 → #44 → #45 → meteo/aprendizaje.

### Para Corola (video)

- La cartela "E4B MVP / 26B objetivo" **cambia** a la version de dos lineas de D2 (borrador). Probablemente requiere dos cartelas seriadas en vez de una; Corola encuentra la cadencia.
- El shot list v1 (futuro, no el v0 actual) incorpora el cambio. **No bloquea el merge de #40 y #41.** El v0 mergea hoy; el cambio entra en v1 como iteracion natural.
- Un plano adicional de oportunidad: mostrar **el proxy adapter en codigo** o el flag `INFERENCE_BACKEND` alternando entre `local` y `cloud` en un split-screen. Refuerza la tesis "mismo codepath, distinto runtime". Opcional, decide Corola.

### Para Xilema

Sin impacto directo. El firmware ESP32 (PR #39), el harness E2E (#36 mergeado), el analisis baseline (#32/#34 pendientes de review) siguen vigentes exactamente como estan.

### Para Floema

Sin impacto directo. Vuelve dia 21 con su rebase de `feat/pollen-fake-voice`. El mock cross-parcela que construira sigue siendo la misma pieza.

### Para el writeup

- **Seccion 1 (problema)** — no se toca. La cerre ayer y sigue vigente.
- **Seccion 2 (solucion)** — se escribe la proxima sesion con Bea incorporando el reframe. El modelo objetivo de Meristem es 26B; la demo corre via proxy; E4B es andamio.
- **Seccion 3 (arquitectura)** — el `meristem_inference_adapter` entra como componente listado.
- **Seccion 5 (validacion)** — se reescribe entera siguiendo D4. Pasa a ser la seccion estrella tecnica.
- **Seccion 7 (impacto y escalado)** — incorpora la linea "hardware objetivo Mac Studio / MBP M1+ Max / RTX 3090 clase" con precio de referencia (~€1.900-2.500).
- **Seccion 8 (limitaciones)** — menciona explicitamente el limite economico del hackathon como por que la demo corre via nube.

---

## Plan por fechas

| Fecha | Hito |
| --- | --- |
| Dia 6 (hoy) | Esta bitacora en main. Mensaje a Meristem. Mensaje a Corola. Issue del proxy adapter abierto. |
| Dia 6-7 | Sesion writeup seccion 2 con Bea (incorporando reframe) |
| Dia 7-10 | Meristem: #42 → proxy adapter → #43 |
| Dia 10-15 | Harness comparativo #45 ejecutado sobre 80-120 escenarios etiquetados. Datos brutos para seccion 5 writeup |
| Dia 15-18 | A/B thinking mode #44. Meteo + bucle aprendizaje (diseno + codigo minimo si tiempo) |
| Dia 18-20 | **Decision hardware** tras primer ensayo video completo |
| Dia 20-25 | Rodaje video con o sin hardware nuevo. Ensayos. |
| Dia 25-29 | Recorte writeup, edicion video, entrega |

---

## Acciones concretas

- [x] Esta bitacora commiteada en main.
- [ ] Cambium abre issue de `meristem_inference_adapter` hoy. Asignado a Meristem.
- [ ] Cambium abre issue "Meristem: meteo local vs meteo general + bucle hipotesis→aprendizaje" hoy como diseno. Asignado a Meristem.
- [ ] Bea habla con Meristem (persona) compartiendo esta bitacora.
- [ ] Cambium escribe mensaje a Corola (despues de Meristem) anunciando cambio de cartela y sin bloquear merges de hoy.
- [ ] Cambium actualiza `docs/12_meristem_spec.md` con modelo objetivo 26B y presencia del adapter (commit aparte, esta semana).
- [ ] Cambium lleva contabilidad semanal de gasto Gemini API. Alerta a Bea a €120 acumulados.
- [ ] Bea verifica en dia 18-20 si hay que comprar MBP M1 Max 64GB.

---

## Reconocimientos explicitos

- **Bea** forzo este reframe con el argumento correcto en el momento correcto. El dia 6 es tarde, pero no es demasiado tarde — el dia 15 si lo habria sido. El impulso vino de ella; este documento solo lo formaliza.
- **Meristem (persona)** construyo el `policy_engine` en #37 con abstraccion model-agnostic, lo que es la razon ingenieril por la que este pivote no es un rollback. Tambien es su hallazgo de `/api/chat` vs `/api/generate` lo que hace que thinking mode sea una palanca real, no un detalle.

## Referencias

- `bitacora/2026-04-19_gemma-26b-moe-thinking-mode_cambium.md` — origen de la decision 26B como modelo serio, que aqui se promueve de sombra a objetivo.
- `bitacora/2026-04-19_meristem-como-revision-diferida_cambium.md` — marco temporal: Meristem es asincrono, lo que permite aceptar latencia extra de thinking mode o de proxy cloud.
- `bitacora/2026-04-19_thinking-mode-e4b-latencia_meristem.md` — hallazgo `/api/chat` vs `/api/generate`, vigente y ganando peso con este reframe.
- PR #37 (mergeado dia 5) — `policy_engine` model-agnostic que habilita el pivote.
- Issues: #42, #43, #44, #45 (preexistentes tras reframe) + **#46 adapter Ollama-Gemini** y **#47 context window sweep** abiertos en el dia 6.

---

## Adenda (dia 6, tarde): eje de ventana de contexto como estructural

Tras la ronda Q1-Q4 sobre el diseno del adapter #46, Meristem (persona) identifico que la ventana de contexto efectiva es un eje **estructural independiente** del thinking budget, no parametro de tuning. Razones:

1. Thinking budget y contexto consumen el mismo pool de tokens — medirlos juntos emborrona senal.
2. Afecta operaciones asimetricamente: las context-heavy (D patrones inter-parcela, E meteo local vs general, F bucle hipotesis→aprendizaje, I contradicciones temporales) se limitan por ventana util, no solo se ralentizan.
3. Informa D6 (decision hardware dia 18-20): si 32k basta → RTX 3090 24GB viable con ahorro ~€700 vs MBP M1 Max. Medir con dato, no con spec de catalogo. Ademas hay riesgo `lost-in-the-middle`: aceptar 128k no implica usarlos bien.

**Decision:** issue gemelo dedicado — **#47 `meristem_context_window_sweep`** — priorizado para correr **despues** de #44 (thinking A/B) y **antes** del dia 18. Cadena de dependencias:

```
adapter #46 → #42 → #44 → #47 sweep → #45 harness completo → decision hardware D6
                                   ↓
                                  #43 consolidator consume ventana util del knee
```

Presupuesto €15-25 dentro del techo €150.

**Procedencia explicita:** este eje nace del callout de Meristem al procesar las respuestas Q1-Q5 del reframe. No estaba en el cuerpo original de esta bitacora. La trazabilidad queda registrada para que el proximo lector del repo entienda de donde sale la pieza.
