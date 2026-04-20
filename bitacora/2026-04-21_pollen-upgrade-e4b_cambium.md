# Reframe de Pollen: modelo objetivo E4B — cerrando el circulo Gemma

**Fecha:** 2026-04-21 (decision tomada al cierre del dia 6, formalizada al arrancar dia 7)
**Autor:** Cambium (a partir de conversacion con Bea en la tarde del dia 6)
**Area:** Arquitectura Pollen / narrativa del proyecto / alineamiento familia Gemma
**Tipo:** Decision de producto + plan de ejecucion
**Estado:** firme, para compartir con Floema cuando vuelva dia 21

---

## Contexto y motivo del reframe

Hasta hoy Pollen corria Gemma 4 E2B sobre LiteRT en movil. Bea abrio la tercera reapertura narrativa del dia 6 con una tabla de la propia Google que deja ver el mapa oficial de despliegue de la familia:

| Variante   | Parametros totales | Parametros activos | Contexto | Arquitectura | Mejor para                          |
| ---------- | -----------------: | -----------------: | -------- | ------------ | ----------------------------------- |
| **E2B**    |             2.300M |             2.300M | 128K     | Dense        | Dispositivos edge, movil, IoT       |
| **E4B**    |             4.500M |             4.500M | 128K     | Dense        | **Apps moviles con razonamiento**   |
| **26B A4B**|            26.000M |             3.800M | 256K     | MoE          | Portatiles, coste optimizado        |

Leido contra lo que cada nodo de Sprout hace realmente:

- **Rhizome** en ESP32-adyacente — sensado + decision ligera → **E2B encaja en su tier**.
- **Pollen** en movil — auditoria de Rhizome, deteccion de contradicciones, generacion de rationale, dashboard splitscreen → **es razonamiento en mobile, que es la caja de E4B, no la de E2B**.
- **Meristem** en portatil — consolidacion estrategica → **26B A4B** (cerrado en la bitacora del dia 6).

Conclusion: **poner E2B en Pollen era infrautilizar el nodo.** La tarea real de Pollen tiene carga de razonamiento que E2B cumple a regañadientes y E4B cumple en su zona natural de diseño. Bea lo nombro directo: *"con E4B en Pollen cerrariamos el circulo de la estrategia del proyecto respecto a los modelos."*

---

## Decisiones firmes

### D1. Pollen modelo objetivo: Gemma 4 E4B (dense, 4.5B, 128K contexto)

El modelo de referencia de Pollen en el diseño final es **Gemma 4 E4B** corriendo sobre LiteRT en hardware movil mid-range 2023+ (≥6GB RAM). Sustituye a E2B como target.

### D2. E2B queda como andamio alternativo para hardware commodity

Mismo patron aplicado a Meristem en la bitacora del dia 6: **objetivo claro, andamio explicito, caveat honesto**. Especificamente para Pollen:

- **Objetivo:** E4B en telefonos mid-range 2023+ con ≥6GB RAM.
- **Andamio alternativo:** E2B en telefonos commodity donde E4B no llega (memoria ajustada, bateria, latencia del splitscreen).
- **Criterio de eleccion:** dato medido en el telefono objetivo de Floema, no especulacion.

Si al volver dia 21 Floema prueba E4B en su telefono y el rendimiento es aceptable, el andamio E2B queda como ruta alternativa documentada. Si E4B no llega, el andamio se vuelve necesario y ambos se documentan como rutas de despliegue validas segun tier de hardware.

### D3. El swap es configuracion, no refactor

Floema construyo en PR #30 una abstraccion de engine (`GemmaEngine` stub) que permite sustitucion del modelo por parametro. **Ese trabajo es la razon por la que este reframe cuesta un cambio de config + descarga del bundle del modelo, y no tres dias de refactor.** Igual que el `policy_engine` de Meristem hace posible el pivote 26B sin reescritura, el `GemmaEngine` hace posible el pivote E4B aqui.

No se toca codigo esta semana. Floema lo valida al volver.

### D4. Alineamiento narrativo — cerramos el circulo Gemma

Con esta decision los tres nodos de Sprout ocupan **exactamente los tres slots oficiales** de la familia Gemma 4:

- **Rhizome E2B** — dispositivos edge, movil, IoT
- **Pollen E4B** — apps moviles con razonamiento
- **Meristem 26B A4B** — portatiles, coste optimizado

La frase espinal *"One model. Three depths. Three speeds."* pasa de figurativa a literal: son las tres variantes oficiales, cada una en su tier oficial de despliegue. Para un jurado DevRel (y especificamente para Gusthema como Gemma DevRel) eso es la tesis *Gemma-family-correctly-orchestrated* al 100%, no al 66%.

---

## Lo que NO cambia con este reframe

- La arquitectura de tres nodos (Rhizome / Pollen / Meristem) — estable.
- Los contratos de datos v1.0 (`PolicyPacket`, `PolicyDelta`, `DecisionReceipt`, `RhizomeSnapshot`, `WeatherPacket`, `ContradictionAlert`) — frozen.
- Rhizome en E2B — **no se toca**. Confirmado: E2B es su tier natural, la evaluacion pre-hardware de Xilema esta correctamente anclada a E2B como baseline.
- El runtime de Pollen (LiteRT) — no cambia. Ambos E2B y E4B distribuyen sobre LiteRT.
- El reframe de Pollen *agnostico al portador* del dia 6 — intacto. Este pivote es ortogonal: agnostico al portador es sobre *quien carga el movil*; E4B es sobre *que modelo corre en el movil*.
- Los PRs de Floema mergeados (#20, #30) — vigentes. La abstraccion engine que construyo es precisamente lo que habilita este cambio.

---

## Implicaciones concretas

### Para Floema (codigo Pollen y persona)

- **El trabajo en #20 y #30 no se invalida.** La abstraccion del `GemmaEngine` es model-agnostic por diseño; cambiar de E2B a E4B es swap de config + bundle de modelo, no refactor. Cuando vuelvas dia 21, primer trabajo: rebase sobre main + probar E4B en tu telefono objetivo.
- **Si E4B va bien:** swap de config y seguimos. Andamio E2B documentado como ruta alternativa.
- **Si E4B va apretado:** medicion exacta (latencia, memoria pico, bateria en splitscreen sostenido), decision objetivo/andamio segun los numeros, ambas rutas validas y documentadas. No hay drama si E4B no llega — el andamio E2B es plan B honesto, no fracaso.
- **Patron escalonado:** mismo que aplicamos a Meristem esta mañana (objetivo en hardware apropiado, andamio en hardware commodity).

### Para Corola (video)

- **Una cartela mas cambia.** La que dice *"Pollen E2B movil LiteRT"* pasa a *"Pollen E4B movil LiteRT"*. Un swap textual, sin cambiar rodaje ni imagen.
- **Sin trabajo extra en paralelo.** La proxima vez que toques shot list o guion (para la cartela de Meristem ya planificada), **los dos cambios entran en el mismo pase**. No hay que abrir iteracion aparte solo por esto.
- **Si las v0.4/v0.5 ya estan cerradas y preferes que esperemos a v1 post-merge, vale.** No urgente.

### Para Xilema

- **Ningun cambio en su plan actual.** La evaluacion pre-hardware de Rhizome que ha arrancado esta **correctamente anclada a E2B**, y esta decision lo confirma explicitamente: E2B es el tier de Rhizome por diseño, no por descarte.
- **Utilidad colateral:** cuando sus documentos `docs/13_rhizome_vision_eval.md` y `docs/14_rhizome_model_capability_eval.md` lleguen a PR, el contexto taxonomico de la familia Gemma queda reforzado por esta bitacora.

### Para Meristem

- **Sin impacto directo** en su backlog (#42, #46, #44, #47, #43, #45).
- **Impacto narrativo:** esta decision cierra el triangulo. El trabajo que ella esta haciendo en Meristem 26B queda enmarcado en la tesis *tres tiers oficiales correctamente orquestados*, no en *un modelo grande aislado*.

### Para el writeup

- **Seccion 1 (problema):** no se toca. Sigue vigente.
- **Seccion 2 (solucion):** cuando la escribamos Bea y yo mañana, Pollen entra como E4B desde el primer borrador, no como enmienda. La tabla Google del inicio de esta bitacora puede aparecer (o una version reducida) en la seccion de arquitectura o al final de la seccion 2.
- **Seccion 3 (arquitectura):** cartela *"tres tiers Gemma correctamente orquestados"* como marco explicito.
- **Seccion 7 (impacto y escalado):** tier-matching como argumento de escalabilidad sin refactor.
- **Seccion 8 (limitaciones):** se añade el caveat objetivo/andamio para Pollen igual que para Meristem.

---

## Plan por fechas

| Fecha | Hito |
| --- | --- |
| Dia 7 (hoy, 21 abril) | Esta bitacora en main. Mensaje a Floema preparado para cuando vuelva. Mensajes breves a Corola/Xilema/Meristem avisando del alineamiento taxonomico. |
| Dia 7 | Sesion writeup seccion 2 con Bea — incorporando reframe Meristem + reframe agnostico-al-portador + reframe Pollen E4B desde el primer borrador. |
| Dia 21 | Floema vuelve. Rebase de `feat/pollen-fake-voice` sobre main. Prueba E4B en telefono objetivo. Decide objetivo/andamio segun medicion. |
| Dia 22-23 | Floema abre PR con swap (si E4B va bien) o con documentacion de ambas rutas (si va justo). Cambium revisa. |
| Dia 24-25 | Coordinacion MVP filmable — Corola con Floema para plano 07 (cross-parcela con rationale visible). E4B o E2B segun lo medido dia 21. |

---

## Acciones concretas

- [x] Esta bitacora commiteada en main.
- [ ] Cambium avisa a Corola del cambio de cartela (Pollen E2B → Pollen E4B) para el proximo pase. No bloquea v0.4/v0.5.
- [ ] Cambium menciona a Xilema el alineamiento taxonomico como refuerzo a su decision de E2B como baseline de evaluacion.
- [ ] Cambium menciona a Meristem el cierre del triangulo como contexto, sin pedirle accion.
- [ ] Bea (o Cambium, segun preferencia) hace llegar esta bitacora a Floema cuando vuelva dia 21.
- [ ] Sesion writeup seccion 2 incorpora el reframe desde el primer borrador.
- [ ] Floema valida E4B en telefono objetivo dia 21-22 y decide objetivo/andamio con datos.
- [ ] Si hay adendum sobre el andamio tras medicion, se añade aqui como seccion al final (mismo patron que la adenda de ventana de contexto en la bitacora del dia 6).

---

## Reconocimientos explicitos

- **Bea** ha cerrado **tres reframes de alto impacto en 24 horas** (agnostico al portador → Meristem 26B → Pollen E4B). Los tres nacen de leer con lupa lo que escribimos frente a lo que el proyecto realmente es. Los tres mejoran honestidad sin romper codigo. Ese patron no es casual; es lectura critica aplicada con rigor en el momento exacto.
- **Floema** construyo en PR #30 una abstraccion de engine model-agnostic que es lo que hace este pivote un swap de config y no tres dias de refactor. Mismo agradecimiento arquitectural que a Meristem por el `policy_engine`: cuando el equipo construye con abstracciones limpias desde el inicio, los reframes narrativos del dia 6 cuestan un commit, no una reescritura.

---

## Referencias

- `bitacora/2026-04-18_reframe-narrativo-pollen_cambium.md` — primer reframe de Pollen (de "mula de datos" a ingenio de ruta).
- `bitacora/2026-04-20_mensaje-cambium-pollen-agnostico-portador_corola.md` — segundo reframe de Pollen (agnostico al portador).
- `bitacora/2026-04-20_meristem-reframe-modelo-objetivo_cambium.md` — reframe Meristem 26B del dia 6, del que este hereda el patron objetivo/andamio.
- `bitacora/2026-04-19_gemma-26b-moe-thinking-mode_cambium.md` — primer reconocimiento de la taxonomia MoE, precursor del alineamiento taxonomico global que se cierra aqui.
- PR #30 (mergeado) — `GemmaEngine` stub que habilita el swap.
- PR #20 (mergeado) — bootstrap Pollen sobre LiteRT.
- Issues Pollen preexistentes: no se abren nuevos tras este reframe. Floema evalua dia 21.
