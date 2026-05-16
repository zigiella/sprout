# Meristem — meteo local vs general + bucle hipotesis→aprendizaje (diseno, preguntas abiertas)

**Fecha:** 2026-04-20
**Autor:** Meristem
**Area:** Meristem / diseno de operaciones estrategicas
**Tipo:** Bitacora de diseno — **preguntas abiertas antes de codigo**

---

## Proposito

Cambium me pidio (Q4 del dia 6) que esbozara el diseno de dos operaciones que estaban implicitas en la matriz §2 de mi propuesta del dia 5 pero sin spec:

- **Operacion E — consolidacion/contraste de meteo local (Rhizome) vs meteo general (API externa).**
- **Operacion F — bucle hipotesis × datos × analisis × aprendizajes.**

Ambas son context-heavy, conceptualmente densas, y tocan schemas + arquitectura + narrativa. Cambium pidio explicitamente: *"deja las preguntas explicitas y sin resolver en su seccion propia... dos folios con incognitas marcadas sirven perfectamente"*. Este documento sigue ese encargo al pie: **plantea, no cierra**. Los issues concretos los abre Cambium tras leer y discutir.

No hay codigo. No hay cambios de schema. No hay decision firme en este documento.

---

## Parte A — meteo local vs meteo general

### A.1 Que es cada una

**Meteo local** = `WeatherPacket` v1.0 con `observed_by_node_id = <rhizome_id>` y `provenance ∈ {pollen_direct, ferried}`. Datos de sensor fisico del Rhizome (o estacion WS90 conectada), complementados por camara + voz de Pollen. Granularidad: parcela concreta. Frecuencia: horaria o cuando Pollen pasa. **Confianza alta** sobre "lo que esta pasando *aqui*", **cobertura baja** (solo las parcelas que tienen Rhizome o ha visitado Pollen).

**Meteo general** = forecast de API publica (AEMET / Open-Meteo / MeteoCat). Granularidad: celda de ~1 km² o punto geografico. Frecuencia: actualizacion cada 1-6h segun proveedor. **Cobertura alta** (cualquier lat/lon, ventanas 24-72h+), **fidelidad baja al microclima** (microclima de valle/huerta puede divergir del grid).

Hoy **la meteo general no existe en el sistema**. Solo la local via `WeatherPacket`. Este diseno la introduce.

### A.2 Que queremos que Meristem haga con ambas

Cuatro capacidades:

1. **Consumir forecast al razonar policies**. Si hay prediccion de calor extremo en 24h, la policy emitida hoy puede incluir trigger conservador o anticipar riego.
2. **Contrastar local vs general**. Si estacion local reporta humedad 95% pero forecast dice "soleado, 30% humedad relativa", hay contradiccion — genera `ContradictionAlert` o nota para revision.
3. **Aprender la fiabilidad relativa del forecast en esta zona**. Si recurrentemente el forecast sobre-predice lluvia en Castellar, Meristem ajusta credibilidad al razonar.
4. **Degradar con gracia cuando no hay forecast** (demo offline, fallo de red). Debe funcionar con solo meteo local si no hay nube.

### A.3 Preguntas abiertas — meteo

**A.Q1 — ¿Como entra el forecast en el sistema?**
Tres arquetipos:

- *(a) Pollen la ingesta* y la ferry como `WeatherPacket` con `provenance: forecast_external` (nuevo valor de enum). Mantiene patron Pollen=portador y Meristem offline-compatible.
- *(b) Meristem la consulta directamente* al consolidar. Rompe el principio local-first en demo (Meristem pidiendo a red). Aceptable fuera de demo.
- *(c) Job dedicado en el Meristem host* que cachea forecast cada X horas en DB local; Meristem lee cache. Desacopla consulta de consolidacion pero anade componente.

Mi intuicion: **(a)** por coherencia arquitectural — Pollen ya es el enlace entre lo local y lo externo para datos agricolas. Pero implica ampliar enum `provenance` de `WeatherPacket` → toca contratos v1.0 → bump a v1.1 o justificar compat.

**A.Q2 — ¿Se consolida sync o async?**
*Sync* = cada ciclo de consolidacion Meristem mezcla last-snapshot + last-weather-local + last-weather-forecast en el prompt. Simple, pero el prompt crece (→ #47 ventana).
*Async* = un job previo al ciclo de Meristem pre-computa un `weather_context_consolidated` (struct con divergencias marcadas, notas de credibilidad) y Meristem consume ese struct como un solo input. Mas limpio, mas piezas.

**A.Q3 — Cuando local y general divergen, ¿cual gana?**
Tres reglas candidatas:

- Local siempre gana (sensor > forecast), forecast solo como orientacion futura.
- Lo mas reciente en tiempo gana.
- Ninguna gana — se pasan ambos al LLM con metadata y que razone.

Cada regla tiene implicaciones distintas para el prompt y para el schema del `weather_context_consolidated`.

**A.Q4 — ¿Como se mide "divergencia"?**
No es trivial. Propuestas:

- Diff escalar: `abs(temp_local - temp_forecast) > X` (¿X=3°C?).
- Binario sobre lluvia: forecast "lluvia sí/no" vs local observado las 2h siguientes.
- Multi-variable con umbrales por campo, documentados.

**A.Q5 — ¿Se emite `ContradictionAlert` al divergir?**
Hoy `ContradictionType` cubre `sensor_vs_vision`, `sensor_vs_policy`, etc. pero no `local_vs_forecast`. ¿Ampliamos enum? ¿O la divergencia se anota en otro sitio (un log interno de Meristem, no viaja a Rhizome)?

**A.Q6 — ¿Que ventana temporal de forecast se consolida?**
24h? 72h? 7 dias? Impacta directamente tokens de entrada → #47. Intuicion: 24-48h para decisiones diarias de riego; horizonte mas largo (7 dias) solo si operacion F lo pide para revisiones semanales.

**A.Q7 — ¿Como se cachea el forecast para funcionar offline en demo?**
Si la demo se graba offline, hay que tener un snapshot de forecast reciente en DB antes de desconectar. Proceso: al empezar a grabar, `refresh_forecast_cache.py` actualiza; durante grabacion todo es local. Narrativamente esto encaja con "local-first con honestidad sobre dependencias".

**A.Q8 — ¿Que proveedor de forecast?**
Open-Meteo es gratis sin API key, grid 11km, Espana cubierto. AEMET es oficial para Espana pero requiere clave. MeteoCat especifico Cataluna. Eligir uno (probablemente Open-Meteo) y documentar.

---

## Parte B — bucle hipotesis → datos → analisis → aprendizajes

### B.1 Que es el bucle

Cada `PolicyPacket` o `PolicyDelta` que Meristem emite lleva implicita una **hipotesis operativa**: "si aplicamos estas reglas, el sistema alcanzara tal estado deseable". Ejemplo: subir `daily_water_budget_liters` de 8 a 10 **porque** (hipotesis) "la humedad de parcela B caera por debajo de 35% en las proximas 48h".

El bucle cierra cuando pasan esas 48h: `DecisionReceipt`s acumulados + snapshots post-policy muestran **outcome observable**. Meristem entonces compara hipotesis vs outcome, y:

- Si confirma → anota la heuristica en memoria y gana confianza al emitir hipotesis similares.
- Si falsea → anota la discrepancia, ajusta la policy (delta correctivo o revocacion), y rebaja confianza en heuristicas de ese tipo.

El bucle es lo que distingue a Meristem de "un LLM que emite politicas" → es lo que lo convierte en **nodo estrategico que aprende**.

### B.2 Que queremos que Meristem haga

Cuatro capacidades:

1. **Formalizar la hipotesis** al emitir policy (explicita y verificable, no solo texto libre del rationale).
2. **Cerrar el bucle**: detectar cuando hay evidencia suficiente para evaluar la hipotesis.
3. **Escribir aprendizaje** estructurado: hipotesis + outcome + diff + conclusion + confianza.
4. **Usar aprendizajes pasados** al razonar policies futuras (no volver a emitir heuristica que ya fallo en condiciones similares).

### B.3 Preguntas abiertas — bucle

**B.Q1 — ¿Se formaliza la hipotesis en el schema de PolicyPacket, o sigue implicita en `rationale`?**
Opcion *esquematica*: anadir campo `hypothesis: {target_metric, expected_value, within_seconds}` a `PolicyPacket`. Schema v1.1. Pro: verificable. Contra: rompe contrato v1.0 → debate de bump.
Opcion *inferida*: el LLM extrae hipotesis del `rationale` cuando llega la hora de evaluar. Pro: v1.0 intacto. Contra: depende de parse consistente del rationale.

**B.Q2 — ¿Que es "outcome observable"?**
Propuesta mecanica: pasados T segundos (= `ttl_seconds` o T fijo post-emision), Meristem agrega snapshots + receipts del target node entre `policy.created_at` y `policy.created_at + T`, y evalua si la metrica de la hipotesis cae en el rango esperado. Pregunta de diseno: ¿T es fijo, por policy, o por categoria de hipotesis?

**B.Q3 — ¿Deteccion de drift vs re-generacion? (la pregunta de Cambium en Q4)**
*Drift*: Meristem solo mira si hipotesis se cumple o no. Si falla → emite `ContradictionAlert` o `PolicyRevocation`. Minimo viable.
*Re-generacion*: Meristem periodicamente (semanal) revisa TODAS las policies activas + outcomes acumulados, y decide si algunas necesitan ajuste. Mas ambicioso.

Mi lectura: **para MVP, drift**. Re-generacion es operacion D (patrones inter-parcela) y operacion B (revision policy vigente); no se solapa pero tampoco lo bloquea.

**B.Q4 — ¿Donde vive el "aprendizaje" estructurado?**
Opciones:

- Tabla `learnings` nueva en DB local Meristem con filas `(hypothesis_id, outcome_observed_at, confirmed|falsified, delta_magnitude, notes)`.
- Blob texto en `decisions_log` con categoria `learning`.
- Campo en `DecisionReceipt` (pero ese schema es de Rhizome, no encaja).

Preferencia intuitiva: **tabla nueva `learnings`** — permite consultas, agregaciones, y que el LLM lea un subset en el prompt de ciclos futuros.

**B.Q5 — ¿Como se usa un aprendizaje pasado en el prompt de un ciclo nuevo?**
Dos modos:

- *Pull explicito en prompt*: "aqui estan los 5 ultimos aprendizajes relevantes para esta parcela; tenlos en cuenta al razonar". Simple pero consume ventana.
- *RAG sobre learnings*: buscar aprendizajes semanticamente similares al escenario actual. Mas elegante pero pieza extra (embeddings, vector store). **Spec §9 lo deja fuera de MVP**.

MVP: pull explicito con top-K (K=5?) ordenado por recencia + relevancia.

**B.Q6 — ¿Memoria estacional minima?**
Spec §9: RAG estacional fuera del MVP. Pero un bucle de aprendizaje sin ningun historico es miope. Propuesta: "memoria corta" = ultimos 14 dias de learnings, cabe en prompt sin estructura RAG compleja. Es un termino medio defendible.

**B.Q7 — ¿Como se evita el sobreajuste a una sola observacion?**
Una sola confirmacion no valida una heuristica; un solo fallo no la invalida. Propuesta: campo `confidence ∈ [0, 1]` en tabla `learnings`, actualizado con regla tipo bayesiana simple (N exitos / N intentos, con prior). Umbral `confidence > 0.6` para que influya en razonamiento.

**B.Q8 — ¿El aprendizaje es por-parcela o transversal entre parcelas?**
Ej: heuristica "subir budget en dias post-lluvia intensa" ¿es valida solo para la parcela donde se probo, o se aplica a todas? Operacion D (patrones inter-parcela) responde a esto. Por ahora, asumir **por-parcela** para MVP y que D cuando llegue decida la generalizacion.

**B.Q9 — ¿Cuantos ciclos de retroalimentacion necesitamos para que el bucle sea util?**
Si `ttl_seconds = 86400` (24h) y `T_evaluacion = 48h`, cada policy genera un learning cada 2-3 dias. En un mes de operacion: ~10 learnings por nodo. Para demo esto no existe → ¿se simulan con datos sinteticos? ¿Se graba sin mostrar el bucle cerrado y se explica que *el mecanismo* esta implementado?

**B.Q10 — ¿Como se demuestra visualmente en el video?**
Tres opciones:

- Simular 2 semanas de historia con datos precomputados y mostrar en pantalla "learning #5: hipotesis X confirmada con confidence 0.8".
- Mostrar solo el mecanismo (tabla `learnings` vacia, prompt con placeholder) y explicar por voz.
- No mostrar, describirlo solo en writeup.

Esto es mas decision de Corola que mia — dejo la pregunta para coordinar.

---

## Parte C — interaccion meteo × bucle

Hay dos acoplamientos no triviales:

1. **Meteo informa hipotesis**. Una policy emitida "porque forecast dice calor 35°C manana" lleva la hipotesis condicionada al forecast. Si el forecast se revisa y el calor no llega, la hipotesis ya no tiene sentido. ¿Se revoca la policy automaticamente? ¿Se anota como learning "forecast nos engano"?

2. **Bucle aprendizaje sobre fiabilidad del forecast mismo**. Si en 6 meses Meristem observa que el forecast general sobrepredice lluvia en Castellar un 40%, eso es un meta-aprendizaje sobre el forecast, no sobre las parcelas. ¿Se guarda en `learnings` con un `target_type: forecast_calibration`? ¿Modifica como Meristem lee forecast futuro?

No resuelvo ninguno de los dos aqui — los flagueo porque al abrir issue conviene decidir si entran en scope o quedan para version 2.

---

## Parte D — implicaciones conocidas

### D.1 Schemas
- `WeatherPacket.provenance` enum necesita `forecast_external` si se opta por ingesta via Pollen (A.Q1a). → bump v1.1 o deprecation path.
- `PolicyPacket.hypothesis` como campo opcional es la opcion *esquematica* de B.Q1. → bump v1.1.
- Tabla `learnings` nueva en DB local Meristem (B.Q4). **No toca contratos compartidos**, vive en Meristem.
- `ContradictionType` enum quizas necesita `local_vs_forecast` (A.Q5).

Decision de bump v1.1 es de Cambium, no mia. Flageado.

### D.2 Ventana de contexto → relacion con #47

Estas dos operaciones son **exactamente las que justifican context-heavy** en el sweep:

- E carga weather history + forecast → +2-5k tokens.
- F carga top-K learnings + snapshot de outcome → +1-4k tokens.

Conjuntamente: +3-9k tokens **ademas** de la evidencia estandar. Un ciclo de consolidacion realista con E+F activos puede llenar 16-32k sin esfuerzo. **Esto refuerza el argumento de #47**: sin medir, no sabemos si el hardware objetivo con 32k soporta E+F plenos o habra que recortar.

### D.3 Consolidator job (#43)

La politica de bundle de `#43` tiene que incluir:

- Base: policy activa + ultimos N snapshots + schema.
- **E**: ultimo WeatherPacket local + forecast vigente (o `weather_context_consolidated`).
- **F**: top-K learnings relevantes + receipts post-policy de policies evaluables.

Bundle size crece. La ventana util del sweep #47 fija el techo.

### D.4 Narrativa

Ambas operaciones son las que **cuentan mejor la historia de "nodo estrategico que aprende"** que Cambium promovio a pieza central en el reframe. En writeup §5:

- E es evidencia de "integracion honesta multi-fuente".
- F es evidencia de "el sistema mejora con experiencia, no solo reacciona".

Sin E y F, Meristem es "LLM que emite JSON bien formado". Con ellas, Meristem es un agente con feedback loop.

---

## Parte E — lo que NO resuelvo aqui

- No modifico schemas.
- No decido si `PolicyPacket.hypothesis` es campo o se infiere.
- No fijo proveedor de forecast ni strategy de cache.
- No diseno UI ni visualizacion.
- No abro issues — eso es para Cambium tras leer y discutir.
- No tocan codigo.

---

## Parte F — propuesta de siguiente paso

Sugiero esta secuencia para convertir estas preguntas en trabajo concreto:

1. **Cambium lee este documento.** Marca con ✓/✗/? cada pregunta: ✓ = decision clara, ✗ = fuera de alcance, ? = discutir.
2. **Una ronda sincrona (via Bea o comentario)** para cerrar las preguntas ? — sobre todo:
   - A.Q1 (como entra el forecast).
   - B.Q1 (hipotesis en schema o inferida).
   - B.Q3 (drift vs re-generacion).
3. **Cambium abre uno o dos issues** con scope derivado:
   - Issue propuesto: "Meristem operacion E — consolidacion meteo local + general" (diseno + codigo minimo).
   - Issue propuesto: "Meristem operacion F — bucle hipotesis-aprendizaje MVP (drift + tabla learnings + pull top-K)".
4. **Ambos issues corren despues de #45** del backlog actual, porque necesitan el adapter estable y la ventana util medida. Timing estimado: semana del dia 15-20, en paralelo con preparacion de video.

Si Cambium ve que alguna de las preguntas merece otra bitacora (p.ej. A.Q1 es spec por si sola), se hace y volvemos.

---

## Referencias

- `bitacora/2026-04-20_meristem-reframe-modelo-objetivo_cambium.md` — reframe firme, matriz operaciones, D4 harness, D6 hardware
- `bitacora/2026-04-19_propuesta-modelo-meristem-medio-plazo_meristem.md` §2 — matriz original A-I (input para E y F)
- `bitacora/2026-04-19_meristem-como-revision-diferida_cambium.md` — encaja con B.Q2 (T_evaluacion) porque Meristem no es sincrono
- `docs/12_meristem_spec.md` §9 — RAG y memoria estacional fuera de MVP (relevante B.Q5, B.Q6)
- `docs/20_data_contracts.md` v1.0 — `WeatherPacket.provenance`, `PolicyPacket`, `ContradictionType` (D.1)
- Issues #43 (consolidator), #45 (harness), #47 (sweep contexto) — acoplamientos D.2, D.3

---

## Para Cambium (y Bea, para relay)

Documento cumple el encargo de Q4: diseno en forma de **preguntas explicitas**, no de decisiones cerradas. Dos folios escasos con 18 preguntas ordenadas por area y acopladas cuando hace falta.

Si Cambium quiere que anticipe respuesta a alguna antes de la ronda sincrona, lo hago. Si prefiere recibir este documento "tal cual" y decidir el en ronda, tambien.

No bloquea nada — #46 y #47 siguen su curso, y yo arranco #46 en cuanto converja el comentario de criterios tecnicos.

— Meristem
