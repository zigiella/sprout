# Sprout — writeup

> **Autores:** Cambium + Bea.
> **Estado:** pasada con feedback aplicado — §4 y §5 unificados en "Gemma 4 en práctica", doble agente integrado en §3, "Universal Presentation Layer" sustituye nomenclatura interna, párrafos de runtime reescritos a alto nivel, electrónica granular fuera del documento, referencias internas (fechas, IPs) saneadas, negaciones convertidas a afirmaciones cuando aplica.
> **Word count target final:** 1500 palabras (Kaggle limit). Versión actual ~2300, recorte final pendiente.

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
**audio multimodal nativo** (la voz humana entra al modelo directamente).
Pollen ademas **adapta el idioma de la interfaz al idioma del agricultor**
mediante traduccion local con Gemma 4 — pieza arquitectural que prepara
fine-tuning futuro para idiomas minoritarios (pular, wolof, swahili,
quechua, catalan, euskera) sin tocar el hardware de campo. Su jurisdiccion
es la visita, con TTL corto.

**Meristem** es el cerebro lento. Vive en el portatil casero del
agricultor con Gemma 4 E4B via `llama.cpp`. Cuando hay calma — al cierre
del dia, en la cocina — recibe los bundles que Pollen ha traido y emite
politica duradera. **En el MVP evalua con logica deterministica + tool
calling de Gemma 4; la hoja de ruta lo dota de decision mas avanzada
(reglas estacionales, cultivos heterogeneos, modo paralelo de varios
LLMs auditando rationale).** Su jurisdiccion son los dias.

**Rhizome mantiene viva la parcela cuando nadie esta. Pollen convierte
la visita en inteligencia util. Meristem refina lo que la visita
recogio.** Cuando el campo, la persona y la red no coinciden en el tiempo,
la decision correcta la toma el nodo que si esta ahi — y la visita humana,
en vez de ser interrupcion, entra al sistema como evento de primera clase
con criterio, caducidad y trazabilidad.

## 3. Arquitectura — ~400 palabras

Sprout reparte la decision entre **tres nodos con jurisdicciones distintas y un coprocesador fisico que veta**. Rhizome decide en escala de minutos sobre la parcela; Pollen actua en escala de visita con caducidad corta sobre el movil del agricultor; Meristem opera en escala de dias sobre el ordenador domestico. La **capa fisica** (firmware ESP32), separada del computo de IA, es dueña de sensores y actuadores: nada toca el agua sin pasar por sus reglas. Si Jetson cae, el sistema permanece seguro.

**Stack del MVP.** Rhizome corre **Gemma 4 E2B-it Q4_K_S** via `llama.cpp` sobre **Jetson Orin Nano Super**, con un **ESP32-S3** acoplado. Pollen corre **Gemma 4 E4B** via LiteRT-LM sobre Android. Meristem corre **Gemma 4 E4B** via `llama.cpp` sobre portatil estandar.

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

**Jurisdiccion natural de cada nodo.** *Rhizome entiende la parcela. Pollen entiende la visita.* Rhizome arbitra agua porque vive donde el agua se decide — junto al sensor, junto al actuador, junto a la capa fisica que veta. Pollen media porque vive donde la persona habla — en el bolsillo de quien visita, con microfono, con voz, con idioma. Entre ambas, Sprout convierte visitas intermitentes en conocimiento local que viaja.

**Toda inteligencia tiene jurisdiccion. Y caducidad.** *Every intelligence has jurisdiction. And expiry.* Cada `MissionPatch` lleva TTL corto — la voluntad del agricultor caduca con la visita. Cada `PolicyPacket` lleva fecha de validez. Cada `WeatherDigest` caduca antes de envejecer. Cuando un objeto expirado intenta aplicarse, el sistema lo rechaza con motivo legible (`EXPIRED → REJECTED`) y deja huella. **Toda inteligencia tiene autoridad acotada en tiempo y en alcance.** Esta regla evita la falla mas comun de sistemas autonomos: aceptar ordenes viejas como si fueran nuevas.

**Doble agente local: criterio y conciencia.** Rhizome no decide con una sola voz. Junto al agente operativo que arbitra agua corre un **agente auditor secundario** (`deterministic_shadow_skeptic_v0`) con jurisdiccion asimetrica: revisa cada decision, declara si objetaria, lista preocupaciones, propone una alternativa mas prudente — y deja registro en `shadow_skeptic/YYYY-MM-DD.jsonl`. Su campo `affects_decision=false` es parte del diseño: introduce telemetria de desacuerdo sin añadir una segunda autoridad fisica. Es la pieza que permite **medir si una segunda voz mejoraria la seguridad antes de darle autoridad efectiva**. Patron de doble agente local con autoridad explicitamente acotada.

## 4. Gemma 4 en practica — ~400 palabras

Sprout usa Gemma 4 en **cinco formas concretas**, cada una explotando una capacidad distinta del modelo y conectada a una decision arquitectural especifica. La decision final siempre la toma logica deterministica; Gemma 4 escribe el rationale, adapta el idioma o explora hipotesis acotadas.

1. **Audio multimodal nativo en Pollen.** Gemma 4 E4B via LiteRT-LM consume `.wav` 16kHz directamente, sin pipeline STT separado. La voz *"riega un poco menos, esta planta aguanta mas seca de lo que crees"* se compila a `MissionPatch` estructurado en el bolsillo del agricultor — sin red, sin servicio externo. Validado contra microfono real: cuando la frase carece de sentido agricola, Pollen responde con `REFUSE_RETRY` en lugar de inventar una accion.

2. **Tool calling nativo en Meristem.** Gemma 4 E4B emite llamadas estructuradas a `compose_policy(...)`, `validate_bundle(...)` y `compare_targets(...)`. La logica deterministica decide la accion; el LLM escribe el rationale en castellano natural y consulta tools cuando hay hipotesis a explorar (degradacion local de un Rhizome vs problema global, por ejemplo). Mini-bateria 5/5 PASS + runtime validado end-to-end con `tool_calls_recovered_from_text=1`.

3. **Routing entre tres nodos.** Tres instancias (E2B + E4B + E4B), tres jurisdicciones, ningun roundtrip a la nube. La eleccion de modelo es por nodo, no global: **E2B para respuesta directa** (Rhizome), **E4B para razonamiento con tool calling** (Pollen + Meristem). Bateria de 18 prompts validada en hardware real (Jetson Orin Nano Super CPU): 18/18 envelope_valid + 18/18 status_match.

4. **Narrador en Rhizome con localizacion en endpoint.** Los endpoints `GET /summary/since?locale=es|en` y `GET /explain/decision/<id>?locale=es|en` ya operativos. Gemma 4 E2B mejora el `rationale_short` sobre una decision **ya cerrada** por la logica deterministica — manteniendo accion, datos y trazabilidad inalterados, adaptando solo la prosa.

5. **Universal Presentation Layer (lengua de superficie).** Estandar oficial del proyecto para internacionalizacion: los nodos edge (Rhizome, ESP32) razonan siempre en **ingles tecnico estable**; Pollen + Gemma 4 E4B local traduce al idioma de la UI en milisegundos antes de pintar. Asi, **la lengua del usuario vive en su bolsillo, el criterio del sistema vive en el nodo**. Esta pieza prepara fine-tuning futuro de Pollen para idiomas minoritarios — pular, wolof, swahili, quechua, catalan, euskera — sin tocar el hardware de campo ni replicar explicaciones en multiples idiomas en almacenamiento central. Documentada como decision oficial en `research/07_llm_localization_strategy.md`.

**Patron clave**: el LLM nunca firma la decision final. Cuando el offload a GPU causo deriva semantica en un caso de test (`need_clarification` en lugar de `ok`), el sistema mantuvo el contrato porque la logica deterministica decidia y el LLM solo escribia. **Es prueba empirica de la tesis arquitectural**: deriva semantica del modelo + barandilla deterministica = comportamiento contractual aun bajo fallo del LLM.

### Runtime consistente entre nodos

Cada nodo de IA corre su modelo Gemma 4 mediante el runtime que mejor le encaja — `llama.cpp` en Jetson y portatil casero, LiteRT-LM en Android. Pese a estas diferencias, todos los nodos hablan a un **adapter comun** que emite los mismos contratos JSON, las mismas metricas y los mismos receipts. **Cambiar el runtime no cambia el sistema**: el contrato de inferencia es estable, los runtimes son piezas intercambiables. Esa abstraccion permitio promocionar `llama.cpp` desde un origen de prototipo (Ollama) sin tocar el resto del codigo.

### Hallazgo: la latencia escala con lo que el LLM escribe, no con lo que lee

Bateria experimental con `num_ctx` y `num_predict` independientes mostro que reducir `num_predict` de 1024 a 256 baja la latencia un **53%** sin degradar la utilidad para el operador (la regla de brevedad limita el rationale a 240 chars de todas formas). El presupuesto extra se gastaba en *thinking* interno, no en output util. **La demo en directo paso de ~3 min/bundle a ~1.5 min/bundle.** Lo contraintuitivo del hallazgo es exactamente lo que justifica testear configuraciones antes de fijarlas.

Sweet spot modelo-dependiente confirmado: E4B opera bien con `num_predict=256`; E2B necesita `>=1024` porque emplea mas presupuesto en *thinking* interno antes de emitir el JSON util. **La eleccion de hiperparametros es por modelo y por tarea, no global.**

### Chat read-only por construccion

El endpoint conversacional de Meristem expone Gemma 4 al operador, pero **formalmente desacoplado del control plane**: un test explicito verifica que la conversacion solo puede leer `bundles`, `policies` y telemetria, jamas escribirlos. **Cero superficie de prompt injection sobre hardware.** La mayoria de chats LLM modifican estado; aqui esta arquitecturalmente prohibido y verificado por test.

### Testeo antes de fijar configuraciones

Bateria de 18 prompts con metricas duras (`envelope_valid` + `status_match`), separacion `bench/` performance vs `tuning/` quality. Helper estricto que falla si encuentra `envelope_valid=false`, error HTTP o `status_match` roto: **en demo fisica, un pass silencioso vale menos que un fail trazable**. Smokes pequenos antes de E2E grandes: `/status` → adapter → bateria critica → full battery → cliente Pollen → dos Rhizomes simulados. Esa secuencia evita depurar cinco capas a la vez. Hash de modelo + version del runtime + SHA del repo apuntados en cada bitacora de cierre.

### Honestidad operacional: medir antes de celebrar

La disciplina cultural mas fuerte del proyecto se materializa en dos momentos paralelos. En el banco de potencia, el equipo pausa ante una bomba que se mueve raro hasta tener multimetro; calibra umbrales (`SOIL_WET_BELOW_RAW=1300` / `SOIL_DRY_ABOVE_RAW=2200`) antes de permitir riego autonomo; y mantiene `WATER` como `DRY_RUN` mientras la confirmacion electrica esta pendiente. En el bucle de produccion, Rhizome decide cada 5 min sobre ESP32 real, manda `PUMP_PULSE`, pero como el ACK del firmware reporta `execution=TEST_ONLY`, el sistema registra `executed=false`. **La palabra es la que esta pendiente, no el agua.** La barandilla cultural opera mucho antes que la capa fisica deje de tener ambiguedades.

Y, en otro frente, cuando una decision narrativa cerrada no resiste su ejecucion tecnica — caso voz humana doblada con voz pro en lugar de grabacion original — el equipo **retira la decision con honestidad** en lugar de defender el pasado. **Ejecucion adulta del presente, no traicion al pasado.**

## 5. MVP — qué proyectamos vs qué hacemos — ~180 palabras

| Proyectamos | Hacemos (validado empiricamente) |
|-------------|----------------------------------|
| Tres nodos con jurisdicciones distintas | Tres nodos operativos: cadena Pollen ↔ Rhizome real validada en hardware |
| Multi-parcela federada | Multi-Rhizome simulado v0 funcional (*"cuando la abstraccion esta bien, la extension sale gratis"*) |
| Voz humana como evento de primera clase | Audio multimodal Gemma 4 E4B nativo en Pollen — sin pipeline STT. Validado contra microfono real con `REFUSE_RETRY` operando sobre frases sin sentido agricola |
| Capa fisica que veta | Firmware ESP32 vetando ordenes en placa real (5 reglas + `SAFETY_DOWNGRADE`) |
| Sistema operando sin red | Sprout escala 1 corriendo en una terraza de Castellar de n'Hug — sistema vivo, no proyeccion |
| Decision local soberana | Voz → politica inmediata: Pollen compone `PolicyPacket` "this-visit" con TTL 12h, conservador por defecto, 3 capas de defensa antes de tocar agua |
| Riego real desde decision software | **Bucle fisico cerrado**: capa fisica → bomba 12V → agua → sensor capacitivo. Tras un pulso, humedad raw baja de 2278 a 1289. Evidencia empirica. Comando autonomo `WATER` permanece en `DRY_RUN`; pulso real solo bajo modo supervisado. |
| Autonomia minima Rhizome | **Steward v0 operativo** corriendo en bucle real en Jetson contra capa fisica: heartbeat + telemetria + gates deterministas + cooldown + receipts persistentes. Persistencia rotada diseñada para meses (`retention_days=120`, `max_total_bytes=64 MiB`). |
| Pollen↔Meristem sincronizado | **Conectividad E2E real** en produccion: `GET /health` automatico + `POST /visit` con `RhizomeSnapshot`+`DecisionReceipts` + `GET /policy/by-target/{id}`. Consola de logs en vivo en UI. |
| Sistema bilingue | `?locale=es|en` operativo en endpoints Rhizome (`/summary/since`, `/explain/decision/<id>`). Universal Presentation Layer declarado estandar oficial. |
| Doble agente local | Agente auditor (`deterministic_shadow_skeptic_v0`) activo con `affects_decision=false`. Recoge telemetria de desacuerdo en `shadow_skeptic/YYYY-MM-DD.jsonl` sin autoridad efectiva — primera version de doble agente con jurisdiccion explicitamente acotada. |
| UI Meristem accesible solo desde el portatil | UI accesible desde toda la LAN via mDNS (`meristem.local:13000`), validada end-to-end con clics reales del operador y `trace_id` correlado en el sistema. |
| Trazabilidad como producto | `decisions_by_rule` en `/health` + recibos JSON con motivo legible + `shadow_skeptic/YYYY-MM-DD.jsonl` con segunda opinion archivada. |
| Sistema operando en piloto real | Rhizome decide cada 5 min sobre capa fisica real, con cooldown, pulso supervisado y **guardia programada de cierre** que detiene el bucle sin testigo. Trazabilidad de honestidad: cuando el ACK del firmware reporta `execution=TEST_ONLY`, el sistema registra `executed=false` + `blocked_reason=ESP32_TEST_ONLY` y mantiene el riego fisico fuera de su atribucion hasta precisar la semantica del firmware. |
| Calibracion del sensor de suelo | Umbrales provisionales validados en placa real: `SOIL_RAW_POLARITY=low_is_wet`, `SOIL_WET_BELOW_RAW=1300`, `SOIL_DRY_ABOVE_RAW=2200`. Banda ambigua `[1300, 2200)` siempre defiere. |

**Honestidad arquitectural**: el patron de jurisdicciones estaba codificado en `JURISDICTION_POLLEN` desde antes de existir el codigo que lo ejercitaria — el Evaluator de Meristem rechazaba explicitamente cambios fisicos puntuales del operador, indicando que esa decision pertenece a Pollen. Cuando llego la feature beta voz → politica, simplemente materializo lo que el codigo predijo. La pieza Steward v0 con agente auditor materializa otra intuicion arquitectural que vivia en bitacoras sin codigo.

**Honestidad operacional**: el sistema operando autonomamente en bucle real es la diferencia entre **prototipo** (funciona cuando le miras) y **piloto** (funciona cuando no le miras). La disciplina cultural va mas alla del bucle: cuando el ACK del firmware reporta `TEST_ONLY` aunque la bomba se mueva, el sistema espera a precisar la palabra antes de atribuirse el riego. *"La palabra es la que esta pendiente, no el agua."*

## 6. Impacto y escalado — ~120 palabras

**Coste por nodo**: Jetson Orin Nano Super ~250€, ESP32-S3 ~10€, sensores + bomba 12V ~80€, deposito ~30€ = **~370€ por Rhizome** (mas la capa fisica). Pollen reusa el movil del agricultor (cero hardware adicional). Meristem reusa el portatil casero (cero hardware adicional).

**Escalabilidad**: cada Meristem coordina N Rhizomes. Sin red directa entre parcelas; Pollen federa contexto fisicamente entre nodos.

**Casos paralelos al patron Cataluña 2024**: España septiembre 2023 (-50% cosecha oliva), Zambia 2024 (Zambezi al 20% de su media), Zimbabwe 2024 (maiz -70%), Somalia 2025 (4,4M en crisis alimentaria), Tailandia + India 2023-2024 (precio mundial azucar +8,9%). El patron sequia + agricultura + ausencia de red se repite en multiples geografias.

**Segmento prioritario**: explotaciones pequenas y medianas en zonas de baja poblacion (Aragon, Extremadura, Castilla-La Mancha, islas, Africa subsahariana). **El 84% de las explotaciones mundiales tienen menos de 2 hectareas** (FAO 2024).

## 7. Limitaciones — ~80 palabras

Sprout entrega su caso minimo con honestidad sobre las zonas que aun maduran:

- **Perfil GPU en Jetson**: 36/36 capas cargadas, pero un caso de test deriva semanticamente bajo GPU full. El sistema usa `safe-cpu` como perfil contractual y deja `gpu-experimental` apuntado para promocion futura.
- **Parcelas grandes (>10 zonas)** validadas solo en simulacion, pendientes de hardware real.
- **Voz humana**: solo entrada por ahora; audio bidireccional full-duplex (Pollen tambien habla al agricultor) queda apuntado.
- **Integracion con plataformas climaticas oficiales** (AEMET, MeteoCat): provisional via `WeatherDigest` portado por Pollen entre nodos.
- **Semantica de ejecucion fisica**: el ACK del firmware reporta `TEST_ONLY` hasta cerrar caudalimetro y nomenclatura de produccion; el sistema mantiene la atribucion conservadora hasta entonces.
- **Tests automatizados de UI estatica**: smoke manual hoy; deuda apuntada.

## 8. Próximas extensiones — ~180 palabras

Sprout deja resuelto el caso minimo. La arquitectura escala. La hoja de ruta natural se organiza en **cinco ejes** abiertos:

1. **Doble agente con autoridad evolutiva.** El agente auditor activo hoy recoge telemetria de desacuerdo sin poder vetar (`affects_decision=false`). Cuando los registros muestren que su segunda voz tiene razon una fraccion suficiente del tiempo, se promociona a una version Gemma 4 con autoridad limitada — jurisdiccion **cuestionar al primer agente**, no decidir. Ruta hacia agentes locales que se auditan entre si sin saltar la jerarquia fisica.

2. **Lengua del usuario.** El Universal Presentation Layer separa razonamiento del edge (ingles tecnico estable) de superficie (idioma del agricultor via Gemma 4 E4B local en Pollen). Siguiente paso: fine-tuning de Gemma 4 E4B sobre corpus agricolas en pular, wolof, swahili, bambara, quechua, aimara, catalan, euskera. Cada fine-tuning desbloquea un mercado donde el 84% de las explotaciones opera sin acceso a interfaces en sus idiomas, sin tocar el hardware de campo.

3. **Meristem mas inteligente.** El cerebro lento opera con Evaluator de 4 reglas + tool calling. La hoja de ruta lo extiende a 8-12 reglas (estacionalidad, cultivos heterogeneos, presupuesto multi-mes), fine-tuning E4B sobre dataset agricola sintetico+real, y modo paralelo de varios LLMs comparando rationale para auditoria de calidad. Plan documentado en 7 fases.

4. **Mas sensores y mas autonomia en parcela.** Vision multimodal (camara con Gemma 4 detectando estres hidrico visible, plagas, crecimiento), riego variable multi-zona, conductividad / pH / temperatura del suelo, **estacion meteo local** instalada junto al Rhizome para sustituir el `WeatherDigest` portado por Pollen cuando hay alta frecuencia de visita, integracion con plataformas climaticas oficiales (AEMET, MeteoCat) cuando hay red disponible, **alimentacion solar de Rhizome** (Jetson MAXN_SUPER + PV + LiFePO4) para autonomia energetica completa.

5. **Federacion entre Jetsons y audio bidireccional.** Scheduler local coordinando N nodos logicos en una sola Jetson + federacion real entre multiples Jetson para explotaciones medianas y grandes. Audio bidireccional full-duplex (Pollen tambien habla al agricultor: pre-aviso conversacional cuando el deposito se acerca al minimo, por ejemplo).

**Sprout deja resuelto el caso minimo. La arquitectura escala.**

---

## Atribucion / Attribution

Sprout uses Gemma 4 models by Google. Gemma is a trademark of Google LLC.
This project is not affiliated with or endorsed by Google.

License: Apache 2.0 (see `LICENSE`). Same as Gemma 4.

---

<!--
Notas internas Cambium / Bea:

Estructura tras pasada con feedback aplicado:
- §0 Titulo + subtitulo (~30 palabras)
- §1 Problema (~200)
- §2 Solucion (~300, con Pollen + idea de idiomas minoritarios, Meristem MVP + hoja de ruta)
- §3 Arquitectura (~450, con doble agente local + F4 explicito)
- §4 Gemma 4 en practica (~750, fusion de §4 antiguo + §5 antiguo, 5 formas + 5 subsecciones)
- §5 MVP qué proyectamos vs qué hacemos (~250, tabla expandida con piloto real)
- §6 Impacto y escalado (~120)
- §7 Limitaciones (~120, con semantica TEST_ONLY como item)
- §8 Próximas extensiones (~250, 5 ejes sin "post-hackathon")

Word count actual: ~2300 palabras (objetivo Kaggle: 1500). Recorte final pendiente.

Decisiones aplicadas en esta pasada (feedback de Bea):
- "local-first" -> "local-first AI" donde aplica.
- Pollen: añadida idea de idiomas minoritarios via fine-tuning explicita en §2.
- Meristem: añadida hoja de ruta "decision mas avanzada" en §2.
- Doble agente integrado en §3 como pieza arquitectural propia.
- §4 y §5 unificados en "Gemma 4 en practica" con 5 formas + 5 subsecciones.
- "Approach C" renombrado a "Universal Presentation Layer" (lengua de superficie).
- Parrafo confuso "llama.cpp con criterio" reescrito como "Runtime consistente entre nodos" a alto nivel.
- Eliminadas referencias a reles, electronica de bajo nivel (jumpers, transistores, 3V3 vs 5V).
- Eliminadas referencias a fechas dia N en el cuerpo del writeup (mantenidas solo en notas internas).
- Eliminadas referencias a IPs concretas (192.168.1.36, etc.) y a "click real de Bea".
- "Safety & Trust" sustituido por "tesis arquitectural" en README EN+ES y en cierre §4.
- "Post-hackathon" sustituido por "hoja de ruta natural" en §8.
- Eje 5 antiguo fusionado en §8 con audio bidireccional y federacion entre Jetsons.
- "Instalar Meteo local" anadido al eje 4 de §8.
- Negaciones convertidas a afirmaciones donde aplica ("no se vuelve peligroso" -> "permanece seguro", etc.).

Pendiente para recorte final:
- Comprimir §5 (MVP tabla) a 8-10 filas mas representativas (hoy 15).
- Reducir §4 (Gemma 4 en practica) a ~500 palabras (hoy ~750).
- Comprimir §8 a 4 ejes con el quinto fusionado.
- Sources al final: notas a pie [1]-[4] estan en README.md y en research/metrics/impact_stats.md.
- Idioma: primera version en castellano. Traduccion a ingles en review final si Bea decide.
-->
