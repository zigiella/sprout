# Sprout — writeup (día 27)

> **Autores:** Cambium + Bea.
> **Estado:** pasada día 27 con material del día 26 integrado — recuperación F4 (*"Every intelligence has jurisdiction. And expiry."*) explícita en §3 tras retirada de E8 Caducidad del video; aprendizajes culturales Corola día 26 + ACK `TEST_ONLY` Endo día 26 + Xilema calibración suelo en §5 y §6; honestidad arquitectural sobre bucle físico cerrado pero ejecución reportada como prueba. §7 Demo eliminada — la landing demo es autoexplicativa.
> **Word count target final:** 1500 palabras (Kaggle limit). Versión actual ~2200-2400, recorte final día 28-29.

---

## 0. Título + subtítulo — ~30 palabras

**Título propuesto:** *Sprout — local-first water optimization for plots the network forgets.*

**Subtítulo propuesto (frase manifiesto, bookend cierre del video):** *When network is absent — and the human is far — local criteria still irrigate.*

<!-- Eco hídrico abre/cierra del video: la pregunta inicial superpuesta sobre el plano de Castellar — *"When network is absent — and the human is far — what irrigates the field?"* — se responde en el bookend cierre — *"…local criteria still irrigate."* El verbo `irrigate` abre y cierra el arco narrativo. Decisión Bea día 24 sobre inicio firme (Opción A: 3 cartelas superpuestas sobre el plano abierto de Castellar, sin fullscreen sobre negro; cartela bisagra "Imagine this pot is a whole plot." conservada y reubicada a 0:11-0:14, sincronizada con el dolly-in al macetero PLOT_01). Decisión final del título tras video rodado (días 26-27). Bea modula. -->

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

**Jurisdiccion natural de cada nodo.** *Rhizome entiende la parcela. Pollen entiende la visita.* Rhizome arbitra agua porque vive donde el agua se decide — junto al sensor, junto al actuador, junto al ESP32 que veta. Pollen media porque vive donde la persona habla — en el bolsillo de quien visita, con micrófono, con voz, con idioma. Entre ambas, Sprout no solo automatiza riego: convierte visitas intermitentes en conocimiento local que viaja.

**Toda inteligencia tiene jurisdiccion. Y caducidad.** *Every intelligence has jurisdiction. And expiry.* Es el cuarto invariante del sistema. Cada `MissionPatch` que Pollen entrega lleva TTL corto — la voluntad del agricultor caduca con la visita, no se queda viva indefinidamente. Cada `PolicyPacket` que Meristem emite lleva fecha de validez. Cada `WeatherDigest` portado caduca antes de envejecer. Cuando un objeto expirado intenta aplicarse, el sistema lo rechaza con motivo legible (`EXPIRED → REJECTED`) y deja huella en el `DecisionReceipt`. **Ningun criterio se queda silenciosamente vigente despues de su ventana**. Esta regla es lo que evita la falla mas comun de sistemas autonomos: aceptar ordenes viejas como si fueran nuevas. La inteligencia tiene autoridad acotada en tiempo y en alcance, no autoridad indefinida.

## 4. Gemma 4 — ~250 palabras

Sprout usa Gemma 4 en cinco formas concretas, cada una explotando una capacidad distinta del modelo y conectada a una decision arquitectural especifica:

1. **Audio multimodal nativo en Pollen.** Gemma 4 E4B via LiteRT-LM traga `.wav` 16kHz directamente. La voz humana entra al modelo sin pipeline STT separado, sin red. *"Riega un poco menos, esta planta aguanta mas seca de lo que crees"* se compila a `MissionPatch` estructurado en el bolsillo del agricultor.

2. **Tool calling nativo en Meristem.** Gemma 4 E4B emite llamadas estructuradas a `compose_policy(...)` y `validate_bundle(...)`. La logica deterministica decide la accion; el LLM solo escribe el `rationale` en castellano natural. Mini-bateria 5/5 PASS.

3. **Routing entre tres nodos.** Tres instancias (E2B + E4B + E4B), tres jurisdicciones, ningun roundtrip a la nube. Cada nodo guarda el tipo de contexto del que su capa es responsable. Bateria de 18 prompts validada en hardware real (Jetson Orin Nano Super CPU): 18/18 envelope_valid + 18/18 status_match.

4. **Narrador bilingue en Rhizome.** Endpoints `GET /summary/since?locale=es|en` y `GET /explain/decision/<id>?locale=es|en` ya operativos. Gemma 4 E2B mejora el `rationale_short` sobre una decision **ya cerrada** por la logica deterministica — no cambia accion, no autoriza agua, no inventa facts. El sistema habla dos idiomas en produccion, no en post-hackathon.

5. **Localizacion via Approach C** (estandar oficial del proyecto, `research/07_llm_localization_strategy.md`). Los nodos edge (Rhizome, ESP32) piensan en Ingles Tecnico estable; Pollen + Gemma 4 E4B local traduce al idioma de la UI antes de pintar. Beneficios: agnosticidad hardware (sin re-flashear nodos por idioma), preparacion para lenguas minoritarias (Pular, Wolof, Swahili, Quechua, Catalan, Euskera) sin replicar explicaciones en N idiomas en almacenamiento central.

**Patron clave**: la decision final NUNCA la firma el LLM. Cuando el offload a GPU causo deriva semantica en un caso de test (`need_clarification` en lugar de `ok`), el sistema no se rompio porque la logica deterministica mantuvo el contrato. Prueba empirica de Safety & Trust.

## 5. Buenas practicas tecnicas — ~200 palabras

**llama.cpp con criterio.** Rhizome corre Gemma 4 E2B-it Q4_K_S en Jetson Orin Nano Super sobre `llama.cpp`, con dos perfiles distinguidos honestamente: `safe-cpu` (18/18 contractual, slow path) y `gpu-experimental` (36/36 capas a GPU, fast path, quality NO contractual aun). El hallazgo `--fit off --no-op-offload` que desbloqueo el offload completo no quedo como anecdota: documentado, probado y situado en bitacora con metricas. Ollama fue muleta de arranque; llama.cpp es paridad Jetson + Meristem casero — cada nodo habla a un adapter Ollama-compatible comun que emite headers `Sprout-Inference-*` uniformes. Cambia runtime, no cambia el sistema.

**Gemma 4 con cabeza, no como actuador.** Tres usos concretos del modelo, ninguno con autoridad ejecutiva: audio multimodal nativo en Pollen (E4B traga `.wav` 16kHz directamente, sin pipeline STT), tool calling nativo en Meristem (`compose_policy(...)` y `validate_bundle(...)`), y three-node routing entre tres instancias offline. **La decision NUNCA la firma el LLM**. Cuando GPU causo deriva semantica en RD04 (`need_clarification` en lugar de `ok`), el sistema no se rompio porque el Evaluator deterministico mantuvo el contrato. Validado empiricamente: el LLM puede derivar y la barandilla aguanta.

**Testeo antes de decidir configuraciones.** Bateria de 18 prompts con metricas duras (`envelope_valid` + `status_match`), separacion `bench/` performance vs `tuning/` quality. Helper estricto que falla si encuentra `envelope_valid=false`, error HTTP o `status_match` roto — en demo fisica, *un pass silencioso vale menos que un fail trazable*. Smokes pequenos antes de E2E grandes: `/status` → adapter → bateria critica → full battery → cliente Pollen → dos Rhizomes simulados. Esa secuencia evita depurar cinco capas a la vez. Hash de modelo + version `llama-server` + SHA del repo apuntados en cada bitacora de cierre.

**Decisiones tecnicas con honestidad.** Distincion cristalina entre `FirmwareHardLimits` (los 4 valores que ESP32 enforce hoy) y `PolicyGuardrails` (recomendaciones razonables, no enforcement actual) — drift evitado antes de hardcoding en Pollen. Conservador por defecto en Mini-Evaluator: prefiere `REFUSE_RETRY` con *"no estoy seguro, repite por favor"* antes que aplicar dudoso. Simulaciones rotuladas: `rhizome_02` desde una sola Jetson queda explicito como simulacion host-side en UI, endpoint y bitacora. Trazabilidad como producto, no como debug: `decisions_by_rule` en `/health` muestra al jurado en pantalla que reglas se han ejercitado.

**Hallazgo `num_predict`: la latencia escala con lo que el LLM ESCRIBE, no con lo que LEE.** Bateria experimental con `num_ctx` y `num_predict` independientes mostro que reducir `num_predict` de 1024 a 256 baja la latencia un **53%** sin degradar la utilidad para el operador (regla de brevedad 240 chars). El budget extra se gastaba en *thinking*, no en output util. Demo en directo viable a ~1.5 min/bundle en lugar de ~3 min. Lo contraintuitivo del hallazgo es exactamente lo que justifica testear configuraciones antes de fijarlas.

**Chat read-only por construccion.** Endpoint `POST /chat` de Meristem expone Gemma 4 conversacional al operador, pero **formalmente desacoplado del control plane**: test explicito verifica que el chat NO puede modificar `bundles`, `policies` ni firmware. Cero superficie de prompt injection sobre hardware. La mayoria de chats LLM modifican estado; aqui esta arquitecturalmente prohibido y verificado.

**Validar antes de portar.** Cuando el modulo rele de 12V/1ch no respondia limpio con alimentacion estandar 5V, antes de improvisar adaptaciones el equipo abrio un sketch Arduino minimo para entender el comportamiento real del componente. El sketch revelo que ese rele concreto trabaja estable alimentado desde 3V3, no desde 5V (zona ambigua de saturacion del transistor de la placa). Portado a ESP-IDF con esa configuracion, quedo estable. Caso de oficio: cuando el comportamiento no cuadra con la datasheet, **se valida con el componente mas pequeño posible** antes de seguir.

**Medir antes de celebrar — y no atribuirse lo que el ACK no nombra.** La disciplina cultural mas fuerte del proyecto se materializo el dia 25 en el banco de potencia (Xilema: pausa ante bomba que se mueve raro hasta tener multimetro; calibracion de umbrales `SOIL_WET_BELOW_RAW=1300` / `SOIL_DRY_ABOVE_RAW=2200` antes de permitir riego autonomo) y el dia 26 en el bucle real (Endo: Steward decide cada 5 min sobre ESP32 real, manda `PUMP_PULSE` 20s, pero como el ACK del firmware reporta `execution=TEST_ONLY`, el sistema **no se atribuye el riego como ejecutado** — `executed=false`, `blocked_reason=ESP32_TEST_ONLY` en cada `DecisionReceipt`). **La palabra es la que esta pendiente, no el agua**. La barandilla cultural opera mucho antes que la electronica deje de tener ambiguedades.

**Decisiones de calidad pueden retirar decisiones narrativas previas.** Cuando la ejecucion tecnica no soporta la intencion original — caso voz humana E5 del video: la intencion declarada dia 18 era *"voz humana real autentica como excepcion narrativa"*, pero la grabacion en castellano de Bea no soportaba el resto del master master narrado con voz pro ElevenLabs — el equipo retira la decision narrativa cerrada y la sustituye consciente. **No es traicion al pasado; es ejecucion adulta del presente**. Patron registrado en bitacora `2026-05-11_consolidacion-dia-26-v1.8.7_corola`.

## 6. MVP — qué proyectamos vs qué hacemos — ~180 palabras

| Proyectamos | Hacemos (validado empiricamente) |
|-------------|----------------------------------|
| Tres nodos con jurisdicciones distintas | Tres nodos operativos: cadena Pollen ↔ Rhizome real validada en hardware |
| Multi-parcela federada | Multi-Rhizome simulado v0 ya funcional sin haberlo planeado (*"cuando la abstraccion esta bien, la extension sale gratis"*) |
| Voz humana como evento de primera clase | Audio multimodal Gemma 4 E4B nativo en Pollen — sin pipeline STT. Validado contra microfono real con `REFUSE_RETRY` operando sobre frases sin sentido agricola |
| Capa fisica que veta | ESP32 vetando ordenes en placa real (5 reglas + SAFETY_DOWNGRADE) |
| Sistema operando sin red | Sprout escala 1 corriendo en una terraza de Castellar de n'Hug — no proyeccion, sistema vivo |
| Decision local soberana | Feature beta voz → politica inmediata: Pollen compone PolicyPacket "this-visit" con TTL 12h, conservador por defecto, 3 capas de defensa antes de tocar agua |
| Riego real desde decision software | **Bucle fisico cerrado: ESP32 → rele → bomba 12V → agua → sensor capacitivo. Humedad raw bajo de 2278 a 1289 tras pulso. Evidencia empirica.** Comando autonomo sigue en `DRY_RUN`; pulso real solo bajo `TEST_ONLY` supervisado |
| Autonomia minima Rhizome | **Steward v0 operativo**: heartbeat + telemetria + gates deterministas + cooldown + receipts persistentes. Persistencia rotada disenada para meses (`retention_days=120`, `max_total_bytes=64 MiB`), no para demo |
| Pollen↔Meristem sincronizado | **Conectividad E2E REST real** en produccion: `GET /health` automatico + `POST /visit` con `RhizomeSnapshot`+`DecisionReceipts` + `GET /policy/by-target/{id}`. Consola de logs en vivo en UI |
| Sistema bilingue | `?locale=es|en` operativo en endpoints Rhizome (`/summary/since`, `/explain/decision/<id>`). Approach C declarado estandar oficial |
| Una sola inteligencia decide por nodo | **ShadowSkeptic deterministic_shadow_skeptic_v0** activo: segundo agente local con jurisdiccion explicita, `affects_decision=false`, recoge datos sin autoridad efectiva. Primera version de doble agente auditor en produccion |
| UI Meristem accesible solo desde el portatil | **UI accesible desde toda la LAN** (mDNS `meristem.local:13000`), validada con click real de Bea desde 192.168.1.36 con `trace_id` correlado |
| Trazabilidad como producto | `decisions_by_rule` en `/health` + recibos JSON con motivo legible + `shadow_skeptic/YYYY-MM-DD.jsonl` con segunda opinion |
| Sistema operando autonomamente en piloto real (no demo) | **Dia 26: Steward queda corriendo en Jetson sobre ESP32 real, decision cada 5 min, cooldown 5 min, pulso `PUMP_PULSE` 20s (Bea observo que la bomba necesita cebarse), guardia programada para detener a las 22:02:54.** Trazabilidad de honestidad: ACK del firmware reporta `execution=TEST_ONLY` en cada pulso; el sistema registra `executed=false` + `blocked_reason=ESP32_TEST_ONLY` y NO se atribuye riego fisico hasta precisar la semantica del firmware. |
| Calibracion provisional del sensor de suelo | Dia 26 (Xilema): `SOIL_RAW_POLARITY=low_is_wet`, `SOIL_WET_BELOW_RAW=1300`, `SOIL_DRY_ABOVE_RAW=2200`. Banda ambigua `[1300, 2200)` siempre defiere. |

**Honestidad arquitectural**: el patron de jurisdicciones estaba codificado desde el dia 13 — el Evaluator de Meristem (`JURISDICTION_POLLEN`) rechaza explicitamente cambios fisicos puntuales del operador, indicando que esa decision pertenece a Pollen. La feature beta del dia 20 implementa lo que el codigo predijo. La pieza dia 25 (Steward v0 con ShadowSkeptic) materializa una intuicion arquitectural que llevaba semanas en bitacoras sin codigo.

**Honestidad operacional**: el sistema operando autonomamente en bucle real dia 26 es la diferencia entre **prototipo** (funciona cuando le miras) y **piloto** (funciona cuando no le miras). Pero la disciplina cultural del equipo va mas alla del bucle: cuando el ACK del firmware reporta `TEST_ONLY` aunque la bomba se mueva, el sistema NO se atribuye el riego — espera a precisar la palabra antes de promocionarla. *"La palabra es la que esta pendiente, no el agua."*

## 7. Impacto y escalado — ~120 palabras

**Coste por nodo**: Jetson Orin Nano Super ~250€, ESP32-S3 ~10€, sensores + bomba 12V ~80€, deposito ~30€ = **~370€ por Rhizome** (mas la capa fisica). Pollen reusa el movil del agricultor (cero hardware adicional). Meristem reusa el portatil casero (cero hardware adicional).

**Escalabilidad**: cada Meristem coordina N Rhizomes. Multi-Rhizome simulado v0 ya validado dia 16. Sin red directa entre parcelas; Pollen federa contexto fisicamente.

**Casos paralelos al patron Cataluna 2024**: Espana septiembre 2023 (-50% cosecha oliva), Zambia 2024 (Zambezi al 20% de su media), Zimbabwe 2024 (maiz -70%), Somalia 2025 (4,4M en crisis alimentaria), Tailandia + India 2023-2024 (precio mundial azucar +8,9%). El patron sequia + agricultura + ausencia de red se repite en multiples geografias.

**Segmento prioritario**: explotaciones pequenas y medianas en zonas de baja poblacion (Aragon, Extremadura, Castilla-La Mancha, islas, Africa subsahariana). El **84% de las explotaciones mundiales tienen menos de 2 hectareas** (FAO 2024).

## 8. Limitaciones — ~80 palabras

**Honestidad sobre lo que no funciona todavia**:

- **GPU offload en Jetson**: 36/36 capas cargadas, pero quality NO contractual aun (un caso de test deriva semanticamente bajo GPU full). Mantenemos `safe-cpu` como perfil de demo.
- **Regresion `RH02`** detectada dia 19 en `safe-cpu` desde main: 2/2 falla en bateria critical. Bisección controlada en curso.
- **Parcelas grandes (>10 zonas)** no probadas en hardware real — solo simulacion.
- **Voz humana**: solo entrada (audio in). Audio bidireccional full-duplex queda como trabajo futuro.
- **Integracion con plataformas climaticas oficiales (AEMET, MeteoCat)**: no implementada — sustituida por `WeatherDigest` portado por Pollen entre nodos.
- **Tests automatizados de UI estatica**: deuda apuntada desde dia 16 — actualmente smoke manual.
- **API docs no auto-generadas**: contratos JSON estan documentados en `docs/20_data_contracts.md` pero no hay OpenAPI publicado.

## 9. Trabajo futuro — ~180 palabras

Sprout deja explicita una hoja de ruta post-hackathon en cinco ejes, dos de ellos cristalizados el dia 25:

1. **ShadowSkeptic LLM — auditoria agencial interna.** El doble agente determinista activo hoy (`deterministic_shadow_skeptic_v0`, `affects_decision=false`) recoge en `shadow_skeptic/YYYY-MM-DD.jsonl` cada disension contra la decision principal sin poder vetarla. Post-hackathon: si los registros muestran que la segunda voz tiene razon una fraccion suficiente del tiempo, promocionarla a una version Gemma 4 con autoridad limitada — un agente local cuya jurisdiccion es **cuestionar al primer agente**, no decidir. Patron de doble agente con jurisdiccion no autoritativa como ruta a agentes locales que se auditan entre si.

2. **Idiomas minoritarios via Approach C.** Approach C ya separa razonamiento (Ingles Tecnico estable en edge) de superficie (idioma usuario via Gemma 4 E4B local en Pollen). Post-hackathon: fine-tuning de Gemma 4 E4B sobre corpus agricolas en Pular, Wolof, Swahili, Bambara, Quechua, Aimara, Catalan, Euskera. Cada fine-tuning desbloquea un mercado donde el 84% de las explotaciones (FAO: <2 ha) opera sin acceso a interfaces en sus idiomas. Sin tocar hardware ni replicar explicaciones en N idiomas en almacenamiento central.

3. **Meristem mas inteligente.** El cerebro lento entra en MVP con Evaluator de 4 reglas + tool calling Gemma 4 E4B. Post-hackathon: ampliacion a 8-12 reglas (estacionalidad, cultivos heterogeneos, presupuesto multi-mes), fine-tuning E4B sobre dataset agricola sintetico+real con Unsloth, modo paralelo de varios LLMs comparando rationale para auditoria de calidad. Plan documentado en 7 fases.

4. **Mas sensores y complejidad en parcela.** El MVP corre con humedad + nivel deposito + caudalimetro + un actuador. Post-hackathon: vision multimodal (camara con Gemma 4 detectando estres hidrico visible, plagas, crecimiento), riego variable multi-zona, conductividad / pH / temperatura suelo, integracion con plataformas climaticas oficiales (AEMET, MeteoCat) sustituyendo `WeatherDigest` portado. Alimentacion solar de Rhizome (Jetson MAXN_SUPER + PV + LiFePO4).

5. **Multiagentes en Jetson + audio bidireccional + cierre de deuda.** Scheduler local coordinando N nodos logicos en una sola Jetson; federacion real entre multiples Jetson; audio bidireccional full-duplex (Pollen tambien habla al agricultor); cerrar deriva GPU RD04/RH02 para promocionar `gpu-experimental` a contractual; cierre de deuda apuntada (UI tests, OpenAPI, signal-seed `#C5F26B` consistente).

**Sprout deja resuelto el caso minimo. La arquitectura escala.**

---

## Atribucion / Attribution

Sprout uses Gemma 4 models by Google. Gemma is a trademark of Google LLC.
This project is not affiliated with or endorsed by Google.

License: Apache 2.0 (see `LICENSE`). Same as Gemma 4.

---

<!--
Notas internas Cambium / Bea:

- Word count actual: ~2200-2400 palabras tras pasada dia 27 (objetivo Kaggle: 1500). Recorte final dia 28-29.
- §0 titulo + subtitulo: definitivos tras rodaje (dia 26-27, voz pro DbwW cerrada).
- §7 eliminado dia 24 — la landing demo es autoexplicativa.

Material dia 25 integrado dia 26 (PR feat/cambium/writeup-integracion-dia25, mergeado):

- §3: cita Endo "Rhizome entiende la parcela. Pollen entiende la visita. / Rhizome cuida el agua. Pollen cuida la conversacion."
- §4: pasamos de 3 a 5 formas de uso de Gemma 4 — anadidas (4) narrador bilingue Rhizome y (5) Approach C localizacion.
- §5: anadidos hallazgo `num_predict` 53%, chat read-only por construccion, validar-antes-de-portar (sketch Arduino 3V3 vs 5V).
- §6: 6 filas nuevas (riego fisico real, Steward v0 persistencia meses, E2E REST, bilingue, ShadowSkeptic, UI LAN).
- §9: 5 ejes (ShadowSkeptic LLM, idiomas minoritarios, Meristem+, sensores+, multiagentes+audio bidireccional).

Material dia 26 integrado dia 27 (PR feat/cambium/writeup-readme-pasada-dia27, este):

- §3: recuperacion F4 explicita — *"Toda inteligencia tiene jurisdiccion. Y caducidad."* / *"Every intelligence has jurisdiction. And expiry."* Origen: Corola dia 26 (E8 Caducidad retirado del video por compresion, F4 va al writeup como invariante).
- §5: dos parrafos nuevos. (1) "Medir antes de celebrar — y no atribuirse lo que el ACK no nombra" — extension cultural del patron a Endo dia 26 (Steward registra `executed=false` aunque la bomba se mueva, porque ACK reporta TEST_ONLY). (2) "Decisiones de calidad pueden retirar decisiones narrativas previas" — caso voz humana E5 retirada conscientemente por Bea / Corola dia 26.
- §6: 2 filas nuevas. (1) Sistema operando autonomamente en piloto real (Steward bucle dia 26, guardia 22:02:54, ACK TEST_ONLY como pieza de honestidad). (2) Calibracion provisional del sensor de suelo (Xilema dia 26: umbrales 1300 / 2200).
- §6 cierre: nuevo parrafo "Honestidad operacional" sobre prototipo vs piloto.

Pendiente para recorte dia 28-29:
- Comprimir §6 tabla a 8-10 filas mas representativas (hoy 15).
- Reducir §5 a 4 parrafos densos (hoy 9).
- Comprimir §9 a 4 ejes con el quinto fusionado.
- Sources al final: notas a pie [1]-[4] estan en README.md y en research/metrics/impact_stats.md. Si Kaggle requiere bibliografia formal, se anade aparte.
- Idioma: primera version en castellano. Traduccion a ingles en review final si Bea decide.

Pendiente coordinacion con frontes:
- Si Xilema precisa la semantica de `TEST_ONLY` dia 27, actualizar §6 fila correspondiente (probable: combinacion falta caudalimetro + nomenclatura provisional).
- Si Meristem cierra demo en vivo con Floema + Endo dia 27, §6 puede pasar fila E2E REST de "real en local" a "demostrada end-to-end con bundle fisico".
-->
