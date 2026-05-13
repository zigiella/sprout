# Sprout — writeup

> **Autores:** Cambium + Bea.
> **Estado:** pasada día 28 con compresión aplicada — §3 Arquitectura engloba todas las subsecciones técnicas (Stack del MVP fusiona "Dos runtimes", reglas duras, contratos, jerarquía + jurisdicción, caducidad F4, Doble agente local, Gemma 4 aplicado, Hallazgo `num_predict`, Chat read-only por diseño, Tuning). §4 MVP comprimido a 12 filas + "Honestidad operacional" eliminada (petición Bea). §7 fusiona 5→4 ejes. Negaciones convertidas a afirmaciones; referencias internas saneadas.
> **Word count target final:** 1500 palabras (Kaggle limit). Versión actual ~3100 palabras visibles. Pendiente segunda compresión final + traducción a inglés.

---

## 0. Título + subtítulo — ~30 palabras

**Título propuesto:** *Sprout — local-first AI water optimization for plots the network forgets.*

**Subtítulo propuesto (frase manifiesto, bookend cierre del video):** *When network is absent — and the human is far — local criteria still irrigate.*

<!-- Eco hídrico abre/cierra del video: la pregunta inicial superpuesta sobre el plano de Castellar — *"When network is absent — and the human is far — what irrigates the field?"* — se responde en el bookend cierre — *"…local criteria still irrigate."* El verbo `irrigate` abre y cierra el arco narrativo. Decisión Bea día 24 sobre inicio firme (Opción A: 3 cartelas superpuestas sobre el plano abierto de Castellar, sin fullscreen sobre negro; cartela bisagra "Imagine this pot is a whole plot." conservada y reubicada a 0:11-0:14, sincronizada con el dolly-in al macetero PLOT_01). Decisión final del título tras video rodado (días 26-27). Bea modula. -->

## 1. Problema — ~200 palabras

Una pequeña parcela de olivar de regadio y horticolas a cuarenta
kilometros del pueblo mas cercano. El agricultor la visita una vez por
semana, a veces menos. Entre visita y visita, el suelo decide solo: o
recibe agua a tiempo, o no la recibe. Cuando el agricultor vuelve, el
problema ya ha pasado — solo queda medir cuanto se perdio.

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

Sprout es una arquitectura **local-first AI** que resuelve el lag distribuyendo
la decision entre nodos con **jurisdicciones distintas**. Cada nodo responde
a una pregunta concreta, en una escala de tiempo concreta, y con autoridad
acotada.

**Rhizome** es el nodo autonomo de parcela. Vive junto a los sensores,
lee el estado local y decide si riega, difiere, salta o bloquea — dentro
de un sobre seguro impuesto por un **ESP32 acoplado que ejecuta firmware
propio**. Usa **Gemma 4 E2B** sobre Jetson Orin Nano Super para arbitraje
y explicacion. La mayoria de pasos son deterministas; Gemma entra cuando
hay senales contradictorias o mision humana nueva. Si la red cae, Rhizome
sigue decidiendo. Su jurisdiccion son los minutos.

**El ESP32 es el coprocesador de seguridad de la capa fisica.** Es dueno
de los sensores criticos y de los actuadores, y la unica pieza que puede
autorizar ejecucion fisica. Ninguna orden de riego pasa sin su visto
bueno: tiempo maximo por evento, deposito minimo, verificacion de caudal,
heartbeat con Jetson. **Si Jetson cae, el sistema permanece seguro.** La
IA propone; el agua la gobierna una capa fisica prudente.

**Pollen** es el nodo itinerante. Convierte cada visita humana en tres
cosas distintas. Compila intencion humana ("vuelvo en 72 horas, prioriza
parcela A, maximo 900 ml") a `MissionPatch` estructurado con caducidad;
audita decisiones pasadas de Rhizome traduciendo `receipts` a lenguaje
natural; y federa parcelas transportando `WeatherDigest` o contexto util
entre nodos sin red directa. Gemma 4 E4B sobre Android via LiteRT-LM, con
**audio multimodal nativo**. Su jurisdiccion es la visita, con TTL corto.

**Meristem** es el cerebro lento. Vive en el portatil casero del
agricultor con Gemma 4 E4B via `llama.cpp`. Cuando hay calma — al cierre
del dia, en la cocina — recibe los bundles que Pollen ha traido, evalua
con **logica deterministica + tool calling** y emite politica duradera.
Su jurisdiccion son los dias.

**Rhizome mantiene viva la parcela cuando nadie esta. Pollen convierte
la visita en inteligencia util. Meristem refina lo que la visita
recogio.** Cuando el campo, la persona y la red no coinciden en el tiempo,
la decision correcta la toma el nodo que si esta ahi — y la visita humana,
en vez de ser interrupcion, entra al sistema como evento de primera clase
con criterio, caducidad y trazabilidad.

## 3. Arquitectura — ~400 palabras

Sprout reparte la decision entre **tres nodos con jurisdicciones distintas y un coprocesador fisico que veta**. Rhizome decide en escala de minutos sobre la parcela; Pollen actua en escala de visita con caducidad corta sobre el movil del agricultor; Meristem opera en escala de dias sobre el ordenador domestico. La **capa fisica** (firmware ESP32), separada del computo de IA, es dueña de sensores y actuadores: nada toca el agua sin pasar por sus reglas.

**Stack del MVP — dos runtimes, una arquitectura.** Rhizome corre **Gemma 4 E2B-it Q4_K_S** sobre **Jetson Orin Nano Super** via `llama.cpp` con dos perfiles distinguidos honestamente: `safe-cpu` (100% contractual en batería de 18 prompts) y `gpu-experimental` (36/36 capas a GPU, calidad aún no contractual). Meristem corre **Gemma 4 E4B** sobre portátil estándar via `llama.cpp` con tool calling nativo. Pollen corre **Gemma 4 E4B** sobre Android via **LiteRT-LM** — el runtime oficial de Google AI Edge, diseñado para el SoC + NPU del móvil y la única vía para audio multimodal nativo en el bolsillo del agricultor. La elección de runtime es consciente por nodo, no accidental: `llama.cpp` donde toca CPU/GPU heterogéneos con cuantizaciones afinables, LiteRT-LM donde toca móvil con multimodal nativo. **Todos los nodos hablan a un adapter común que emite los mismos contratos JSON, las mismas métricas y los mismos receipts.** Cambiar el runtime no cambia el sistema. Junto al Jetson, un **ESP32-S3** acoplado ejecuta firmware propio como capa física de veto.

**Cinco reglas duras de la capa fisica**, validadas en placa real:

| Regla | Motivo legible si veta |
|-------|------------------------|
| Jetson heartbeat perdido | `JETSON_HEARTBEAT_LOST` |
| Deposito por debajo del minimo | `TANK_LOW` |
| Duracion del evento fuera de rango | `EVENT_DURATION_OUT_OF_RANGE` |
| Sin caudal tras abrir agua | `NO_FLOW_DETECTED` |
| Alerta latched activa | `ALERT_LATCHED` |

Cada veto emite motivo legible que se almacena en el `DecisionReceipt`. Una sexta regla, `SAFETY_DOWNGRADE`, modula una orden valida al sobre fisico mas seguro en lugar de rechazarla.

**Contratos versionados del MVP.** Diez objetos JSON con autoridad explicita y caducidad obligatoria: `RhizomeSnapshot`, `DecisionReceipt`, `AlertEvent` los emite Rhizome; `MissionPatch`, `ValidationStamp`, `WeatherDigest`, `VisitAmendment`, `FieldVisit` los emite Pollen; `PolicyPacket` lo emite Meristem; `SyncBundle` lo transporta cualquier nodo. Todo rechazo deja huella legible — cada objeto que el sistema descarta se registra con motivo.

**Jerarquia y barandilla.** *Lo fisico manda, Rhizome arbitra, Pollen media, Meristem afina.* Cuanto mas arriba vive una pieza en esa jerarquia, menos autoridad fisica tiene. Un `PolicyPacket` emitido por Meristem solo puede recomendar criterios mas conservadores — los hard limits del firmware son su limite superior, nunca su limite inferior. La autoridad fluye de arriba a abajo cuando se trata de afinar criterio, y se invierte cuando se trata de seguridad fisica.

**Jurisdiccion natural.** *Rhizome entiende la parcela. Pollen entiende la visita.* Rhizome arbitra agua porque vive junto al sensor y al actuador; Pollen media porque vive en el bolsillo de quien visita, con micrófono, voz e idioma. Sprout convierte visitas intermitentes en conocimiento local que viaja.

**Toda inteligencia tiene jurisdiccion. Y caducidad.** *Every intelligence has jurisdiction. And expiry.* Cada `MissionPatch` lleva TTL corto — la voluntad del agricultor caduca con la visita. Cada `PolicyPacket` lleva fecha de validez. Cada `WeatherDigest` caduca antes de envejecer. Cuando un objeto expirado intenta aplicarse, el sistema lo rechaza con motivo legible (`EXPIRED → REJECTED`) y deja huella. **Toda inteligencia tiene autoridad acotada en tiempo y en alcance.** Esta regla evita la falla mas comun de sistemas autonomos: aceptar ordenes viejas como si fueran nuevas.

### Doble agente local en Rhizome: criterio y conciencia

Rhizome no decide con una sola voz. Junto al agente operativo que arbitra agua corre un **agente auditor secundario** (`deterministic_shadow_skeptic_v0`) con jurisdiccion asimetrica: revisa cada decision, declara si objetaria, lista preocupaciones, propone una alternativa mas prudente — y deja registro en `shadow_skeptic/YYYY-MM-DD.jsonl`. Su campo `affects_decision=false` es parte del diseño: introduce **telemetria de desacuerdo** sin añadir una segunda autoridad fisica.

Es la pieza que permite **medir si una segunda voz mejoraría la seguridad antes de darle autoridad efectiva** — telemetría primero, autoridad después (ruta de promoción en §7). Patrón de doble agente local con autoridad explícitamente acotada: agentes locales que se auditan entre sí sin saltar la jerarquía física.

### Gemma 4 aplicado

Sprout usa Gemma 4 en **cinco formas concretas**, cada una explotando una capacidad distinta del modelo y conectada a una decision arquitectural especifica. Gemma 4 escribe el rationale, adapta el idioma o explora hipotesis acotadas; la decision final vive siempre en logica deterministica (ver *Patron clave* mas abajo).

1. **Audio multimodal nativo en Pollen.** Gemma 4 E4B via LiteRT-LM consume `.wav` 16kHz directamente, sin pipeline STT separado. La voz *"riega un poco menos, esta planta aguanta mas seca de lo que crees"* se compila a `MissionPatch` estructurado en el bolsillo del agricultor — sin red, sin servicio externo. Validado contra microfono real: cuando la frase carece de sentido agricola, Pollen responde con `REFUSE_RETRY` en lugar de inventar una accion.

2. **Tool calling nativo en Meristem.** Gemma 4 E4B emite llamadas estructuradas a `compose_policy(...)`, `validate_bundle(...)` y `compare_targets(...)`. El LLM consulta tools cuando hay hipotesis a explorar (degradacion local de un Rhizome vs problema global, por ejemplo) y escribe el rationale en castellano natural. Mini-bateria 5/5 PASS + runtime validado end-to-end con `tool_calls_recovered_from_text=1`.

3. **Routing entre tres nodos.** Tres instancias (E2B + E4B + E4B), tres jurisdicciones, ningun roundtrip a la nube. La eleccion es consciente por nodo, no global: **E2B sobre `llama.cpp` para respuesta directa** (Rhizome); **E4B sobre LiteRT-LM en el bolsillo del agricultor** (Pollen, audio multimodal); **E4B sobre `llama.cpp` para tool calling en cocina** (Meristem, con presupuesto generoso de tiempo para orquestar `compose_policy(...)`). Bateria de 18 prompts validada en hardware real: 18/18 envelope_valid + 18/18 status_match.

4. **Narrador en Rhizome con localizacion en endpoint.** Los endpoints `GET /summary/since?locale=es|en` y `GET /explain/decision/<id>?locale=es|en` ya operativos. Gemma 4 E2B mejora el `rationale_short` sobre una decision **ya cerrada** por la logica deterministica — manteniendo accion, datos y trazabilidad inalterados, adaptando solo la prosa.

5. **Universal Presentation Layer.** Estándar oficial para internacionalización: los nodos edge razonan en **inglés técnico estable**; Pollen + Gemma 4 E4B local traduce al idioma de la UI en milisegundos antes de pintar. **La lengua del usuario vive en su bolsillo, el criterio del sistema vive en el nodo.** Prepara fine-tuning de Pollen para idiomas minoritarios sin tocar hardware de campo (`research/07_llm_localization_strategy.md`).

**Patrón clave**: el LLM nunca firma la decisión final. Cuando GPU offload causó deriva semántica en un caso de test (`need_clarification` en lugar de `ok`), el sistema mantuvo el contrato porque la lógica determinista decidía y el LLM solo escribía. **Prueba empírica de la tesis arquitectural**: deriva del modelo + barandilla determinista = comportamiento contractual aun bajo fallo del LLM.

### Hallazgo: la latencia escala con lo que el LLM escribe, no con lo que lee

Bateria experimental con `num_ctx` y `num_predict` independientes mostro que reducir `num_predict` de 1024 a 256 baja la latencia un **53%** sin degradar la utilidad para el operador (la regla de brevedad limita el rationale a 240 chars de todas formas). El presupuesto extra se gastaba en *thinking* interno, no en output util. **La demo en directo paso de ~3 min/bundle a ~1.5 min/bundle.** Lo contraintuitivo del hallazgo es exactamente lo que justifica testear configuraciones antes de fijarlas.

Sweet spot modelo-dependiente: E4B opera bien con `num_predict=256`; E2B necesita `>=1024` (más *thinking* interno antes del JSON). **Los hiperparámetros se eligen por modelo y por tarea, no globalmente.**

### Chat read-only por diseño

El endpoint conversacional de Meristem expone Gemma 4 al operador, pero **formalmente desacoplado del control plane**: un test explicito verifica que la conversacion solo puede leer `bundles`, `policies` y telemetria, jamas escribirlos. **Cero superficie de prompt injection sobre hardware.** La mayoria de chats LLM modifican estado; aqui esta arquitecturalmente prohibido y verificado por test.

### Tuning antes de fijar configuraciones

Bateria de 18 prompts con metricas duras (`envelope_valid` + `status_match`), separacion `bench/` performance vs `tuning/` quality. Helper estricto que falla si encuentra `envelope_valid=false`, error HTTP o `status_match` roto: **en demo fisica, un pass silencioso vale menos que un fail trazable**. Smokes pequenos antes de E2E grandes: `/status` → adapter → bateria critica → full battery → cliente Pollen → dos Rhizomes simulados. Esa secuencia evita depurar cinco capas a la vez. Hash de modelo + version del runtime + SHA del repo apuntados en cada bitacora de cierre.

## 4. MVP — qué proyectamos vs qué hacemos — ~180 palabras

| Proyectamos | Hacemos (validado empiricamente) |
|-------------|----------------------------------|
| Tres nodos con jurisdicciones distintas | Tres nodos operativos: cadena Pollen ↔ Rhizome real validada en hardware |
| Multi-parcela federada | Multi-Rhizome simulado v0 funcional (*"cuando la abstraccion esta bien, la extension sale gratis"*) |
| Voz humana como evento de primera clase | Audio multimodal Gemma 4 E4B nativo en Pollen, validado contra microfono real |
| Capa fisica que veta | Firmware ESP32 vetando ordenes en placa real (5 reglas + `SAFETY_DOWNGRADE`) |
| Sistema operando sin red | Sprout escala 1 corriendo en una terraza de Castellar de n'Hug — sistema vivo, no proyeccion |
| Decision local soberana | Voz → politica inmediata: Pollen compone `PolicyPacket` "this-visit" con TTL 12h, conservador por defecto, 3 capas de defensa antes de tocar agua |
| Riego real desde decision software | **Bucle fisico cerrado**: capa fisica → bomba 12V → agua → sensor capacitivo. Tras un pulso, humedad raw baja de 2278 a 1289. Evidencia empirica. Comando autonomo `WATER` permanece en `DRY_RUN`; pulso real solo bajo modo supervisado. |
| Autonomia minima Rhizome | **Steward v0 operativo** corriendo en bucle real en Jetson contra capa fisica: heartbeat + telemetria + gates deterministas + cooldown + receipts persistentes. Persistencia rotada diseñada para meses (`retention_days=120`, `max_total_bytes=64 MiB`). |
| Pollen↔Meristem sincronizado | **Conectividad E2E real** en produccion: `GET /health` automatico + `POST /visit` con `RhizomeSnapshot`+`DecisionReceipts` + `GET /policy/by-target/{id}`. Consola de logs en vivo en UI. |
| Sistema bilingue | `?locale=es|en` operativo en endpoints Rhizome (`/summary/since`, `/explain/decision/<id>`). Universal Presentation Layer declarado estandar oficial. |
| Doble agente local | Agente auditor (`deterministic_shadow_skeptic_v0`) activo con `affects_decision=false`. Recoge telemetría de desacuerdo en `shadow_skeptic/YYYY-MM-DD.jsonl` sin autoridad efectiva — primera versión de doble agente con jurisdicción explícitamente acotada. |
| UI Meristem accesible LAN | Accesible desde toda la red local vía mDNS (`meristem.local:13000`), validada end-to-end con `trace_id` correlado. |
| Sistema operando en piloto real | Rhizome decide cada 5 min sobre capa física real, con cooldown, pulso supervisado y **guardia programada de cierre** que detiene el bucle sin testigo. Trazabilidad de honestidad: cuando el firmware reporta `execution=TEST_ONLY`, el sistema mantiene el riego fuera de su atribución por defecto; el operador puede activar `ACCEPT_ESP32_TEST_ONLY_PULSE_AS_EXECUTED=1` para que pulsos validados físicamente cuenten como ejecutados, manteniendo intacta la auditabilidad raw. |

**Coherencia arquitectural**: el patrón de jurisdicciones estaba codificado en `JURISDICTION_POLLEN` desde antes de existir el código que lo ejercitaría — el Evaluator de Meristem rechazaba cambios físicos puntuales del operador indicando que esa decisión pertenece a Pollen. Cuando llegó la feature beta voz → política, simplemente materializó lo que el código predijo.

## 5. Impacto y escalado — ~120 palabras

**Coste por nodo**: Jetson Orin Nano Super ~250€, ESP32-S3 ~10€, sensores + bomba 12V ~80€, deposito ~30€ = **~370€ por Rhizome** (mas la capa fisica). Pollen reusa el movil del agricultor (cero hardware adicional). Meristem reusa el portatil casero (cero hardware adicional).

**Escalabilidad**: cada Meristem coordina N Rhizomes. Sin red directa entre parcelas; Pollen federa contexto fisicamente entre nodos.

**Casos paralelos al patron Cataluña 2024**: España septiembre 2023 (-50% cosecha oliva), Zambia 2024 (Zambezi al 20% de su media), Zimbabwe 2024 (maiz -70%), Somalia 2025 (4,4M en crisis alimentaria), Tailandia + India 2023-2024 (precio mundial azucar +8,9%). El patron sequia + agricultura + ausencia de red se repite en multiples geografias.

**Segmento prioritario**: explotaciones pequenas y medianas en zonas de baja poblacion (Aragon, Extremadura, Castilla-La Mancha, islas, Africa subsahariana). **El 84% de las explotaciones mundiales tienen menos de 2 hectareas** (FAO 2024).

## 6. Limitaciones — ~80 palabras

Sprout entrega su caso minimo con honestidad sobre las zonas que aun maduran:

- **Perfil GPU en Jetson**: 36/36 capas cargadas, pero un caso de test deriva semanticamente bajo GPU full. El sistema usa `safe-cpu` como perfil contractual y deja `gpu-experimental` apuntado para promocion futura.
- **Parcelas grandes (>10 zonas)** validadas solo en simulacion, pendientes de hardware real.
- **Voz humana**: solo entrada por ahora; audio bidireccional full-duplex (Pollen tambien habla al agricultor) queda apuntado.
- **Integracion con plataformas climaticas oficiales** (AEMET, MeteoCat): provisional via `WeatherDigest` portado por Pollen entre nodos.
- **Semantica de ejecucion fisica**: el ACK del firmware reporta `TEST_ONLY` hasta cerrar caudalimetro y nomenclatura de produccion; el sistema mantiene la atribucion conservadora hasta entonces.
- **Tests automatizados de UI estatica**: smoke manual hoy; deuda apuntada.

## 7. Próximas extensiones — ~180 palabras

Sprout deja resuelto el caso mínimo. La arquitectura escala. La hoja de ruta natural se organiza en **cuatro ejes** abiertos:

1. **Doble agente con autoridad evolutiva.** El agente auditor activo hoy recoge telemetría de desacuerdo sin poder vetar. Cuando los registros muestren que su segunda voz tiene razón una fracción suficiente del tiempo, se promociona a una versión Gemma 4 con jurisdicción **cuestionar al primer agente**, no decidir — agentes locales que se auditan entre sí sin saltar la jerarquía física.

2. **Lengua del usuario.** Universal Presentation Layer separa razonamiento (inglés técnico en edge) de superficie (idioma del agricultor en Pollen). Siguiente paso: fine-tuning de Gemma 4 E4B sobre corpus agrícolas locales — púlar, wólof, swahili, quechua, catalán, euskera. Cada fine-tuning desbloquea un mercado donde el 84% de las explotaciones opera sin acceso a interfaces en su idioma, sin tocar hardware de campo.

3. **Meristem más inteligente.** El cerebro lento extiende su Evaluator de 4 a 8-12 reglas (estacionalidad, cultivos heterogéneos, presupuesto multi-mes), con fine-tuning E4B sobre dataset agrícola sintético+real y modo paralelo de varios LLMs comparando rationale para auditoría de calidad. Plan documentado en 7 fases.

4. **Más capacidades físicas y federación.** Visión multimodal (cámara con Gemma 4 detectando estrés hídrico, plagas, crecimiento), riego variable multi-zona, conductividad / pH / temperatura del suelo, **estación meteo local** junto a Rhizome, integración con plataformas climáticas oficiales cuando hay red, **alimentación solar** (Jetson MAXN_SUPER + PV + LiFePO4) para autonomía energética completa, federación real entre múltiples Jetsons para explotaciones grandes, **audio bidireccional** (Pollen también habla al agricultor: pre-aviso conversacional cuando el depósito se acerca al mínimo).

**Sprout deja resuelto el caso mínimo. La arquitectura escala.**

---

## Atribucion / Attribution

Sprout uses Gemma 4 models by Google. Gemma is a trademark of Google LLC.
This project is not affiliated with or endorsed by Google.

License: Apache 2.0 (see `LICENSE`). Same as Gemma 4.

---

<!--
Notas internas Cambium / Bea:

Estructura tras pasada con feedback aplicado (segunda iteracion):
- §0 Titulo + subtitulo (~30 palabras) — "local-first AI water optimization"
- §1 Problema (~200) — parcela de olivar de regadio y horticolas (era almendros)
- §2 Solucion (~300, con Pollen + idea idiomas minoritarios, Meristem MVP + hoja de ruta)
- §3 Arquitectura (~1500) — ahora contiene TODAS las subsecciones tecnicas:
    * Stack del MVP
    * Cinco reglas duras de la capa fisica (tabla)
    * Contratos versionados
    * Jerarquia y barandilla
    * Jurisdiccion natural de cada nodo
    * F4 (caducidad)
    * ### Doble agente local en Rhizome: criterio y conciencia (NUEVA subseccion propia)
    * ### Gemma 4 aplicado (NUEVA — antes §4 "Gemma 4 en practica", ahora subseccion de §3)
    * ### Dos runtimes, una arquitectura: llama.cpp y LiteRT-LM
    * ### Hallazgo: la latencia escala con lo que el LLM escribe
    * ### Chat read-only por diseño (antes "por construccion")
    * ### Tuning antes de fijar configuraciones (antes "Testeo")
- §4 MVP qué proyectamos vs qué hacemos (~250, antes era §5)
- §5 Impacto y escalado (~120, antes era §6)
- §6 Limitaciones (~120, antes era §7)
- §7 Próximas extensiones (~250, antes era §8)

Word count actual: ~2200 palabras (objetivo Kaggle: 1500). Recorte final pendiente.

Decisiones aplicadas en esta iteracion (feedback Bea segunda ronda):
- §0 titulo: "local-first" -> "local-first AI water optimization"
- §1 parcela de almendros (cultivo de secano tradicional) -> "olivar de regadio y horticolas" (cultivos sensibles a riego activo)
- §4 anterior ("Gemma 4 en practica") disuelto como seccion propia: ahora todo su contenido vive dentro de §3 Arquitectura como subseccion "Gemma 4 aplicado" + las 5 subsecciones tecnicas (Dos runtimes, Hallazgo num_predict, Chat read-only, Tuning)
- Doble agente local: extraido del parrafo final §3 a subseccion propia "### Doble agente local en Rhizome: criterio y conciencia" con desarrollo completo del patron de promocion futura
- "Chat read-only por construccion" -> "Chat read-only por diseño"
- "Testeo antes de fijar configuraciones" -> "Tuning antes de fijar configuraciones"
- Subseccion "Honestidad operacional: medir antes de celebrar" ELIMINADA (peticion explicita Bea)
- Renumerado: §5 -> §4, §6 -> §5, §7 -> §6, §8 -> §7

Decisiones de iteraciones previas conservadas:
- Pollen: idea de idiomas minoritarios via fine-tuning en §2.
- Meristem: hoja de ruta "decision mas avanzada" en §2.
- "Approach C" renombrado a "Universal Presentation Layer" (lengua de superficie).
- Sin reles, electronica de bajo nivel, jumpers, transistores.
- Sin fechas dia N en cuerpo.
- Sin IPs concretas ni "click real de Bea".
- Sin "Safety & Trust" — sustituido por "tesis arquitectural".
- Sin "post-hackathon" — sustituido por "hoja de ruta natural".
- Llama.cpp y LiteRT-LM nombrados conscientemente con criterio por nodo.

Compresión día 28 aplicada en esta iteración:
- §3 "Dos runtimes una arquitectura" subsección eliminada — contenido único fusionado en "Stack del MVP" (ahorro ~250 palabras).
- §3 "Jurisdicción natural de cada nodo" comprimida (era solape con §2).
- §3 "Doble agente local" segundo párrafo comprimido (la promoción evolutiva ya está en §7 eje 1).
- §3 "Gemma 4 aplicado" forma 5 (Universal Presentation Layer) comprimida — listado de idiomas movido a §7.
- §3 "Patrón clave" + segundo párrafo `num_predict` (sweet spot E4B/E2B) comprimidos.
- §2 Pollen-idiomas-minoritarios eliminado (solape con §3 forma 5).
- §2 Meristem-hoja-de-ruta comprimido (la extensión vive en §7 eje 3).
- §4 MVP tabla: eliminadas 3 filas menos centrales (Calibración sensor, Trazabilidad como producto). Fila "Sistema operando en piloto real" actualizada con `ACCEPT_ESP32_TEST_ONLY_PULSE_AS_EXECUTED=1`.
- §4 "Honestidad operacional: medir antes de celebrar" párrafo ELIMINADO (petición explícita Bea).
- §4 "Honestidad arquitectural" comprimido a una frase.
- §7 ejes 5→4: federación entre Jetsons y audio bidireccional fusionados en eje 4 (Más capacidades físicas y federación).

Ahorro total iteración día 28: ~700 palabras desde 4442 → 3700 con comments / ~3100 visibles.

Pendiente para recorte final día 29:
- Segunda pasada quirúrgica para llegar a 1500 palabras Kaggle: comprimir §3 introductorio (solape con §2), reducir §3 "Gemma 4 aplicado" formas 1-4 a párrafos más densos, comprimir §6 Limitaciones (hoy 7 ítems, target 4-5).
- Traducción a inglés (la traducción ES→EN típicamente reduce un 10-15%).
- Sources al final: notas a pie [1]-[4] están en README.md y en research/metrics/impact_stats.md. Si Kaggle requiere bibliografía formal, se añade aparte.
-->
