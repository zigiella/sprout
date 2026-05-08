# Sprout — writeup (primera versión completa, día 21)

> **Autores:** Cambium + Bea.
> **Estado:** primera versión completa de §0 + §4-§10 (día 21). §1-§3 cerradas previas. §7 placeholder hasta rodaje.
> **Word count target final:** 1500 palabras (Kaggle limit). Versión actual ~1500-1700, recorte final día 28-29.

---

## 0. Título + subtítulo — ~30 palabras

**Título propuesto:** *Sprout — local-first irrigation decisions for plots the network forgets.*

**Subtítulo propuesto (frase manifiesto, bookend del video):** *When network is absent — and the human is far — local criteria still irrigate.*

<!-- Decisión final tras video rodado (días 24-27). Bea modula. -->

## 1. Problema — ~200 palabras

Una parcela de almendros a cuarenta kilometros del pueblo mas cercano. El
agricultor la visita una vez por semana, a veces menos. Entre visita y
visita, el suelo decide solo: o recibe agua a tiempo, o no la recibe.
Cuando el agricultor vuelve, el problema ya ha pasado — solo queda medir
cuanto se perdio.

La escena no es anecdota. La ITU mide en 2025 una brecha de 27 puntos
entre cobertura movil urbana (85%) y rural (58%) en paises desarrollados;
en paises de renta baja, solo el 14% de la poblacion rural usa internet.
El UNCCD reporta que en 2023 el 48% del territorio mundial sufrio al
menos un mes de sequia extrema — la segunda mayor extension desde 1951 —
y que 1.800 millones de personas estan afectadas por la sequia, con un
coste de 300.000 millones de dolares al año. Solo en España, la sequia
costo al sector agrario 5.550 millones de euros en 2023; 370.000 hectareas
de cereal de secano en la cuenca mediterranea perdieron entre el 60% y el
90% de su cosecha, dos años seguidos.

El denominador comun no es la falta de agua. Es el **lag** entre lo que
pasa en la parcela y la decision que deberia corregirlo. Cuando la red
falla o el agricultor no esta, ese lag se mide en dias. Cerrar el lag
exige llevar la decision donde hay agua — no al reves.

<!-- Fuentes: research/narrative_sources.md + research/metrics/impact_stats.md (UNCCD, OECD, FAO, ITU 2025, BdE 2025, COAG/MAPA, IRRIFRAME, Australia Regional Tech Hub). -->

## 2. Solucion — ~300 palabras

Sprout resuelve el lag distribuyendo la decision entre nodos con
**jurisdicciones distintas**. No es una red cooperativa generica; es
un sistema donde cada nodo responde a una pregunta concreta, en una
escala de tiempo concreta, y con autoridad acotada.

**Rhizome** es el nodo autonomo de parcela. Vive junto a los sensores,
lee el estado local y decide si riega, difiere, salta o bloquea —
dentro de un sobre seguro impuesto por un **ESP32 acoplado que ejecuta
firmware propio**. Usa **Gemma 4 E2B** sobre Jetson Orin Nano Super
solo para arbitraje y explicacion, no para toda decision. La mayoria
de pasos son deterministas; Gemma entra cuando hay senales
contradictorias o mision humana nueva. Si la red cae, Rhizome sigue
decidiendo sola. Su jurisdiccion son los minutos.

**El ESP32 es coprocesador de seguridad**, no una placa de reles. Es
dueno de los sensores criticos (humedad, nivel de deposito,
caudalimetro) y de los actuadores (bomba, valvulas), y el unico que
puede autorizar ejecucion fisica. Ninguna orden de riego pasa sin su
visto bueno: tiempo maximo por evento, deposito minimo, verificacion
de caudal, heartbeat con Jetson. **Si Jetson se cae, el sistema no se
vuelve peligroso.** La IA propone; el agua la gobierna una capa fisica
prudente.

**Pollen** es el nodo itinerante. No es un sincronizador de datos: es
el pedazo del sistema que convierte cada visita humana en tres cosas
distintas. Compila intencion humana ("vuelvo en 72 horas, prioriza
parcela A, maximo 900 ml") a `MissionPatch` estructurado con caducidad;
audita decisiones pasadas de Rhizome traduciendo `receipts` a lenguaje
natural; y federa parcelas transportando `WeatherDigest` o contexto util
entre nodos sin red directa. Gemma 4 E4B sobre Android via LiteRT-LM, con
**audio multimodal nativo** (la voz humana entra al modelo sin pipeline
STT separado). Su jurisdiccion es la visita, con TTL corto.

**Meristem** es el cerebro lento. Vive en el portatil casero del
agricultor con Gemma 4 E4B via `llama.cpp`. Cuando hay calma — al cierre
del dia, en la cocina, no en el campo — recibe los bundles que Pollen ha
traido de las parcelas, evalua con **logica deterministica**, y emite
politica duradera con tool calling nativo de Gemma 4. Su jurisdiccion son
los dias.

**Rhizome mantiene viva la parcela cuando nadie esta. Pollen convierte
la visita en inteligencia util. Meristem refina lo que la visita
recogio.** Esa es la tesis del sistema: cuando el campo, la persona y
la red no coinciden en el tiempo, la decision correcta la toma el nodo
que si esta ahi — y la visita humana, en vez de ser interrupcion, entra
al sistema como evento de primera clase con criterio, caducidad y
trazabilidad.

## 3. Arquitectura — ~400 palabras

Sprout reparte la decision entre **tres nodos con jurisdicciones distintas y un coprocesador fisico que veta**. Rhizome decide en escala de minutos sobre la parcela; Pollen actua en escala de visita con caducidad corta sobre el movil del agricultor; Meristem opera en escala de dias sobre el ordenador domestico. El **ESP32**, separado del computo de IA, es dueno de los sensores criticos y de los actuadores: nada toca el agua sin pasar por sus reglas. Si Jetson cae, el sistema no se vuelve peligroso.

**Stack del MVP.** Rhizome corre **Gemma 4 E2B-it Q4_K_S** via `llama.cpp` sobre **Jetson Orin Nano Super**, con un **ESP32-S3** acoplado por USB-CDC nativo ejecutando firmware ESP-IDF propio. Pollen corre **Gemma 4 E4B** via LiteRT-LM sobre Android. Meristem corre **Gemma 4 E4B** via `llama.cpp` sobre portatil estandar. Cada nodo de IA habla a un *adapter Ollama-compatible* comun que emite headers `Sprout-Inference-*` uniformes, reutilizando los mismos contratos de prompt, schema y receipt aunque cada dispositivo use un runtime distinto.

**Cinco reglas no negociables**, implementadas y ejercitadas contra el limite fisico de seguridad en placa real:

| Regla | Motivo legible si veta |
|-------|------------------------|
| Jetson heartbeat perdido | `JETSON_HEARTBEAT_LOST` |
| Deposito por debajo del minimo | `TANK_LOW` |
| Duracion del evento fuera de rango | `EVENT_DURATION_OUT_OF_RANGE` |
| Sin caudal tras abrir agua | `NO_FLOW_DETECTED` |
| Alerta latched activa | `ALERT_LATCHED` |

Cada veto emite motivo legible que se almacena en el `DecisionReceipt` y aparece en pantalla. Una sexta regla, `SAFETY_DOWNGRADE`, no rechaza una orden valida: la modula al sobre fisico mas seguro.

**Contratos versionados del MVP.** Diez objetos JSON con autoridad explicita por contrato y caducidad obligatoria: `RhizomeSnapshot`, `DecisionReceipt`, `AlertEvent` los emite Rhizome; `MissionPatch`, `ValidationStamp`, `WeatherDigest`, `VisitAmendment`, `FieldVisit` los emite Pollen; `PolicyPacket` lo emite Meristem; `SyncBundle` lo transporta cualquier nodo. Toda inteligencia tiene jurisdiccion y fecha de caducidad; todo rechazo deja huella legible — ningun objeto se pierde en silencio.

**Jerarquia y barandilla.** *Lo fisico manda, Rhizome arbitra, Pollen media, Meristem afina.* Cuanto mas arriba vive una pieza en esa jerarquia, menos autoridad fisica tiene. Ningun `PolicyPacket` emitido por Meristem puede reducir hard limits del firmware ESP32 — solo recomendar criterios mas conservadores. Ningun `MissionPatch` o `VisitAmendment` de Pollen anula reglas duras. La autoridad fluye de arriba a abajo cuando se trata de afinar criterio, y se invierte cuando se trata de seguridad fisica.

## 4. Gemma 4 — ~150 palabras

Sprout usa Gemma 4 en tres formas concretas, cada una explotando una capacidad distinta del modelo:

1. **Audio multimodal nativo en Pollen.** Gemma 4 E4B via LiteRT-LM traga `.wav` 16kHz directamente. Sustituimos el `SpeechRecognizer` de Android tras inestabilidad extensa. La voz humana entra al modelo sin pipeline STT separado, sin red. *"Riega un poco menos, esta planta aguanta mas seca de lo que crees"* se compila a `MissionPatch` estructurado en el bolsillo del agricultor.

2. **Tool calling nativo en Meristem.** Gemma 4 E4B emite llamadas estructuradas a `compose_policy(...)` y `validate_bundle(...)`. La logica deterministica decide la accion; el LLM solo escribe el `rationale` en castellano natural. Mini-bateria 5/5 PASS.

3. **Routing entre tres nodos.** Tres instancias (E2B + E4B + E4B), tres jurisdicciones, ningun roundtrip a la nube. Cada nodo guarda el tipo de contexto del que su capa es responsable. Bateria de 18 prompts validada en hardware real (Jetson Orin Nano Super CPU): 18/18 envelope_valid + 18/18 status_match.

**Patron clave**: la decision final NUNCA la firma el LLM. Cuando el offload a GPU causo deriva semantica en un caso de test (`need_clarification` en lugar de `ok`), el sistema no se rompio porque la logica deterministica mantuvo el contrato. Prueba empirica de Safety & Trust.

## 5. Buenas practicas tecnicas — ~200 palabras

**llama.cpp con criterio.** Rhizome corre Gemma 4 E2B-it Q4_K_S en Jetson Orin Nano Super sobre `llama.cpp`, con dos perfiles distinguidos honestamente: `safe-cpu` (18/18 contractual, slow path) y `gpu-experimental` (36/36 capas a GPU, fast path, quality NO contractual aun). El hallazgo `--fit off --no-op-offload` que desbloqueo el offload completo no quedo como anecdota: documentado, probado y situado en bitacora con metricas. Ollama fue muleta de arranque; llama.cpp es paridad Jetson + Meristem casero — cada nodo habla a un adapter Ollama-compatible comun que emite headers `Sprout-Inference-*` uniformes. Cambia runtime, no cambia el sistema.

**Gemma 4 con cabeza, no como actuador.** Tres usos concretos del modelo, ninguno con autoridad ejecutiva: audio multimodal nativo en Pollen (E4B traga `.wav` 16kHz directamente, sin pipeline STT), tool calling nativo en Meristem (`compose_policy(...)` y `validate_bundle(...)`), y three-node routing entre tres instancias offline. **La decision NUNCA la firma el LLM**. Cuando GPU causo deriva semantica en RD04 (`need_clarification` en lugar de `ok`), el sistema no se rompio porque el Evaluator deterministico mantuvo el contrato. Validado empiricamente: el LLM puede derivar y la barandilla aguanta.

**Testeo antes de decidir configuraciones.** Bateria de 18 prompts con metricas duras (`envelope_valid` + `status_match`), separacion `bench/` performance vs `tuning/` quality. Helper estricto que falla si encuentra `envelope_valid=false`, error HTTP o `status_match` roto — en demo fisica, *un pass silencioso vale menos que un fail trazable*. Smokes pequenos antes de E2E grandes: `/status` → adapter → bateria critica → full battery → cliente Pollen → dos Rhizomes simulados. Esa secuencia evita depurar cinco capas a la vez. Hash de modelo + version `llama-server` + SHA del repo apuntados en cada bitacora de cierre.

**Decisiones tecnicas con honestidad.** Distincion cristalina entre `FirmwareHardLimits` (los 4 valores que ESP32 enforce hoy) y `PolicyGuardrails` (recomendaciones razonables, no enforcement actual) — drift evitado antes de hardcoding en Pollen. Conservador por defecto en Mini-Evaluator: prefiere `REFUSE_RETRY` con *"no estoy seguro, repite por favor"* antes que aplicar dudoso. Simulaciones rotuladas: `rhizome_02` desde una sola Jetson queda explicito como simulacion host-side en UI, endpoint y bitacora. Trazabilidad como producto, no como debug: `decisions_by_rule` en `/health` muestra al jurado en pantalla que reglas se han ejercitado.

## 6. MVP — qué proyectamos vs qué hacemos — ~120 palabras

| Proyectamos | Hacemos (validado empiricamente) |
|-------------|----------------------------------|
| Tres nodos con jurisdicciones distintas | Tres nodos operativos: cadena Pollen ↔ Rhizome real validada en hardware |
| Multi-parcela federada | Multi-Rhizome simulado v0 ya funcional sin haberlo planeado (*"cuando la abstraccion esta bien, la extension sale gratis"*) |
| Voz humana como evento de primera clase | Audio multimodal Gemma 4 E4B nativo en Pollen — sin pipeline STT |
| Capa fisica que veta | ESP32 vetando ordenes en placa real (5 reglas + SAFETY_DOWNGRADE) |
| Sistema operando sin red | Sprout escala 1 corriendo en una terraza de Castellar de n'Hug — no proyeccion, sistema vivo |
| Decision local soberana | Feature beta voz → politica inmediata: Pollen compone PolicyPacket "this-visit" con TTL 12h, conservador por defecto, 3 capas de defensa antes de tocar agua |
| Trazabilidad como producto | `decisions_by_rule` en `/health` + recibos JSON con motivo legible |

**Honestidad arquitectural**: el patron de jurisdicciones estaba codificado desde el dia 13 — el Evaluator de Meristem (`JURISDICTION_POLLEN`) rechaza explicitamente cambios fisicos puntuales del operador, indicando que esa decision pertenece a Pollen. La feature beta del dia 20 implementa lo que el codigo predijo.

## 7. Demo (90s) — placeholder hasta rodaje

<!--
Pendiente rodaje (dias 24-27). Estructura prevista del video:
- E0 cartela Sprout + 3 nodos + tagline
- E1 ausencia con 4 datos globales (UNCCD, gencat, ITU, COAG)
- E2 Rhizome decide offline
- E3 ESP32 SAFE LIMIT (wow moment)
- E3b Meristem prepara la politica
- E4 Llega Pollen
- E5 Persona da una mision (voz humana real castellano)
- E6 Ferry A→B
- E7 Criterio modificado (climax)
- E8 Caducidad
- E9 Cenital federado animado
- E9b Meristem en la mesa de casa (cierre intimo + tagline bookend)

Tras rodaje, escribir aqui guion del 90s consolidado citando frases fuertes.
-->

## 8. Impacto y escalado — ~120 palabras

**Coste por nodo**: Jetson Orin Nano Super ~250€, ESP32-S3 ~10€, sensores + bomba 12V ~80€, deposito ~30€ = **~370€ por Rhizome** (mas la capa fisica). Pollen reusa el movil del agricultor (cero hardware adicional). Meristem reusa el portatil casero (cero hardware adicional).

**Escalabilidad**: cada Meristem coordina N Rhizomes. Multi-Rhizome simulado v0 ya validado dia 16. Sin red directa entre parcelas; Pollen federa contexto fisicamente.

**Casos paralelos al patron Cataluna 2024**: Espana septiembre 2023 (-50% cosecha oliva), Zambia 2024 (Zambezi al 20% de su media), Zimbabwe 2024 (maiz -70%), Somalia 2025 (4,4M en crisis alimentaria), Tailandia + India 2023-2024 (precio mundial azucar +8,9%). El patron sequia + agricultura + ausencia de red se repite en multiples geografias.

**Segmento prioritario**: explotaciones pequenas y medianas en zonas de baja poblacion (Aragon, Extremadura, Castilla-La Mancha, islas, Africa subsahariana). El **84% de las explotaciones mundiales tienen menos de 2 hectareas** (FAO 2024).

## 9. Limitaciones — ~80 palabras

**Honestidad sobre lo que no funciona todavia**:

- **GPU offload en Jetson**: 36/36 capas cargadas, pero quality NO contractual aun (un caso de test deriva semanticamente bajo GPU full). Mantenemos `safe-cpu` como perfil de demo.
- **Regresion `RH02`** detectada dia 19 en `safe-cpu` desde main: 2/2 falla en bateria critical. Bisección controlada en curso.
- **Parcelas grandes (>10 zonas)** no probadas en hardware real — solo simulacion.
- **Voz humana**: solo entrada (audio in). Audio bidireccional full-duplex queda como trabajo futuro.
- **Integracion con plataformas climaticas oficiales (AEMET, MeteoCat)**: no implementada — sustituida por `WeatherDigest` portado por Pollen entre nodos.
- **Tests automatizados de UI estatica**: deuda apuntada desde dia 16 — actualmente smoke manual.
- **API docs no auto-generadas**: contratos JSON estan documentados en `docs/20_data_contracts.md` pero no hay OpenAPI publicado.

## 10. Trabajo futuro — ~120 palabras

Sprout deja explicita una hoja de ruta post-hackathon en cuatro ejes:

1. **Meristem mas inteligente.** El cerebro lento entra en MVP con Evaluator de 4 reglas + tool calling Gemma 4 E4B. Post-hackathon: ampliacion a 8-12 reglas (estacionalidad, cultivos heterogeneos, presupuesto multi-mes), fine-tuning E4B sobre dataset agricola sintetico+real con Unsloth, modo paralelo de varios LLMs comparando rationale para auditoria de calidad sin tocar produccion. Plan documentado en 7 fases progresivas + 6 principios arquitectonicos transversales (bitacora `2026-05-04_plan-ia-meristem-fases-arquitectura`).

2. **Mas sensores y complejidad en parcela.** El MVP corre con humedad de suelo + nivel deposito + caudalimetro + un actuador (bomba). Post-hackathon: vision multimodal (camara con Gemma 4 detectando estres hidrico visible, plagas, crecimiento), riego variable por electrovavula multi-zona, conductividad / pH / temperatura suelo, integracion con plataformas climaticas oficiales (AEMET, MeteoCat) sustituyendo `WeatherDigest` portado.

3. **Multiagentes en Jetson.** El MVP demuestra dos Rhizomes (uno fisico + uno simulado host-side) desde una sola Jetson. Post-hackathon: scheduler local que coordine N nodos logicos en una sola Jetson para explotaciones medianas con multiples zonas + federacion real entre multiples Jetson para explotaciones grandes con varias parcelas geograficamente separadas.

4. **GPU quality pass + audio bidireccional + cierre de deuda.** Cerrar deriva GPU RD04/RH02 para promocionar `gpu-experimental` a contractual. Audio bidireccional full-duplex (Pollen tambien le habla al agricultor: pre-aviso conversacional *"manana toca riego, pero el deposito esta al 30%"*). Cierre de deuda apuntada (tests automatizados UI, API docs auto-generadas, branch jumping origen sistemico, signal-seed oficial #C5F26B en todos los frontends).

**Sprout deja resuelto el caso minimo. La arquitectura escala.**

---

## Atribucion / Attribution

Sprout uses Gemma 4 models by Google. Gemma is a trademark of Google LLC.
This project is not affiliated with or endorsed by Google.

License: Apache 2.0 (see `LICENSE`). Same as Gemma 4.

---

<!--
Notas internas Cambium / Bea:

- Word count actual: ~1500-1700 palabras (objetivo Kaggle: 1500). Recorte final dia 28-29.
- §0 titulo + subtitulo: definitivos tras rodaje (dia 24-27).
- §7 placeholder: rellenar tras rodaje con guion consolidado del 90s.
- §3: el detalle de "transferencia de ingenieria entre nodos" del v1 se removio para reducir palabras — material movido a §5 sin cita literal.
- Sources al final: notas a pie [1]-[4] estan en README.md y en research/metrics/impact_stats.md. Si Kaggle requiere bibliografia formal, se anade aparte.
- Idioma: primera version en castellano. Traduccion a ingles en review final si Bea decide.
- Pendiente apuntar microcita "JURISDICTION_POLLEN linea 17 de evaluator.py" en §6 si entra version final con citas de codigo.
-->
