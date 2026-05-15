# Sprout: criterios locales para el agua cuando no hay nadie

**Subtítulo:** IA abierta y local para decisiones sobre el agua bajo ausencia, con autoridad acotada, recibos firmados y un veto físico.

## El problema

El riego remoto falla cuando las decisiones llegan tarde. Una parcela cambia cada hora: el suelo se seca, los depósitos se vacían, el tiempo cambia, las válvulas fallan, aparecen plagas y las prioridades se mueven. La persona que entiende el campo lo visita periódicamente. La red aparece intermitentemente. La decisión, aun así, tiene que ocurrir cerca del agua.

Sprout apunta a ese hueco de decisión. Los criterios de riego inmediato viven en el campo. La intención humana entra durante la visita. La política de medio plazo se revisa en casa, después de que los recibos y los bundles de visita hayan vuelto.

La demo usa macetas vivas como sustituto de pequeñas parcelas, huertos comunitarios, invernaderos escolares rurales y zonas cooperativas donde conectividad y presencia humana llegan a fragmentos.

## Qué es Sprout

Sprout es una arquitectura local-first de IA para decisiones de agua bajo ausencia. Combina tres nodos Gemma 4 con una capa de veto físico:

- **Rhizome** lee la parcela y arbitra la acción inmediata.
- **Pollen** media la visita y compila la intención humana.
- **Meristem** refina la política de la siguiente ventana en casa.
- **ESP32** posee la frontera física de seguridad.

La invariante operativa es simple: **lo físico manda, Rhizome arbitra, Pollen media, Meristem afina.** La autoridad física crece al acercarse al agua; la autoridad de contexto y política crece al alejarse de ella.

Cada inteligencia tiene jurisdicción. Cada instrucción tiene caducidad.

![Vista general de la arquitectura de Sprout: ESP32 y Rhizome en el campo, Pollen en el móvil, Meristem en casa, con MissionPatch y DecisionReceipt fluyendo en sync y Bundle / PolicyDiff en sync eventual.](https://raw.githubusercontent.com/zigiella/sprout/main/media/sprout-architecture-overview.png)

*Tres jurisdicciones, una decisión sobre el agua. La válvula solo se abre tras el ACK del ESP32.*

## Rhizome y ESP32

Rhizome corre Gemma 4 E2B sobre Jetson Orin Nano Super mediante `llama.cpp`. Lee telemetría local, aplica gates deterministas de seguridad y necesidad, y elige entre `WATER`, `DEFER`, `SKIP` y `BLOCK`.

Rhizome no mueve agua directamente. Emite una acción candidata y un `DecisionReceipt` firmado. El recibo registra evidencia, política activa, acción candidata, resultado del ESP32, acción final y rationale. Cuando una persona regresa, el sistema explica lo que ha pasado a través de los recibos. La explicación está anclada en evidencia registrada.

Gemma 4 E2B mejora el rationale local sobre hechos ya cerrados por la lógica determinista. La acción la fija el steward y los gates de seguridad. La explicación se vuelve útil para una persona sin convertirse en la fuente de autoridad física.

El coprocesador de seguridad ESP32 corre firmware ESP-IDF a medida y posee la capa física. Comprueba heartbeat, estado del depósito, límites de duración, estado de alerta y seguridad del actuador. Bloquea comandos no seguros y registra razones legibles como `JETSON_HEARTBEAT_LOST`, `TANK_LOW`, `EVENT_DURATION_OUT_OF_RANGE` y `ALERT_LATCHED`.

La ruta física de banco incluye un relé, una bomba 12V, lecturas reales de humedad de suelo y pulsos `PUMP_PULSE` supervisados. El `WATER` autónomo permanece conservador en `DRY_RUN`; la prueba física supervisada usa `TEST_ONLY`.

## El patrón doble-agente

Sprout incluye un patrón doble-agente local dentro de Rhizome. El steward primario cierra la decisión a través de gates deterministas: telemetría, política, TTL, cooldown, estado del depósito, estado de seguridad y modo de ejecución. Un segundo agente local, `ShadowSkeptic`, audita la decisión y registra objeciones con `affects_decision=false`.

`ShadowSkeptic` crea evidencia de seguridad. Marca alternativas conservadoras, señales de desconfianza y motivos para revisar una situación. Nunca riega, nunca vetoa, nunca reescribe la acción final y nunca toca la ruta del ESP32.

Esa frontera le da al segundo agente una jurisdicción precisa: observar, cuestionar, registrar. Cada desacuerdo se convierte en un evento medible. Versiones futuras pueden promover objeciones recurrentes y útiles a gates deterministas. Incluso el escepticismo tiene jurisdicción.

![Patrón doble-agente de Sprout: el bundle de estado se divide en el agente Operacional — que decide dentro del sobre seguro y emite un DecisionReceipt con acción y rationale — y ShadowSkeptic, que objeta sin autoridad y escribe un log de Disagreement con affects_decision=false.](https://raw.githubusercontent.com/zigiella/sprout/main/media/sprout-double-agent.png)

*Una segunda voz sin autoridad física. El desacuerdo se vuelve dato, no acción.*

## Pollen

Pollen corre sobre Android con Gemma 4 E4B mediante LiteRT-LM. Convierte una visita humana en inteligencia estructurada que el campo puede usar de inmediato.

Una persona dice: *"Vuelvo el viernes. Esta planta aguanta más seca de lo que crees; riégala un poco menos."* Pollen captura audio local, lo pasa a Gemma 4 E4B, compila la instrucción en un `MissionPatch` con caducidad, valida el patch con guardrails deterministas y rechaza instrucciones incoherentes o no seguras.

Un `MissionPatch` carga un TTL corto porque pertenece a una visita concreta. Los objetos tardíos caducan. Los objetos caducados son rechazados y registrados con un motivo legible.

Pollen también transporta contexto entre Rhizomes desconectados. Lleva objetos `WeatherDigest`, partes de visita, recibos, validaciones y mission patches. Un teléfono llega a muchos sitios antes de que llegue conectividad estable.

Pollen le da además a Rhizome una interfaz humana. Cuando una persona pregunta qué ha pasado desde la última visita, Pollen traduce los recibos y los resúmenes locales a un lenguaje sobre el que la persona puede actuar.

## Meristem

Meristem corre en el portátil de casa del agricultor con Gemma 4 E4B mediante `llama.cpp`. Ingesta los bundles que Pollen trae, evalúa decisiones recientes con lógica determinista y revisión asistida por tool calling, y emite objetos `PolicyPacket` duraderos para la siguiente ventana de política.

Meristem no decide riego inmediato. Refina los criterios después de que la presión de los minutos haya pasado: qué parcela necesita atención, qué sensor merece menos confianza, cómo deberían cambiar los presupuestos de agua y qué patrones emergen entre visitas.

Un `PolicyPacket` carga una ventana de validez. Su autoridad pertenece a los días, no a los segundos. Rhizome lo valida antes de usarlo. El ESP32 permanece por encima en la jerarquía de seguridad.

## Por qué Gemma 4 importa aquí

Sprout usa Gemma 4 donde la inteligencia local cambia el sistema.

Gemma 4 E2B le da a Rhizome explicación local y razonamiento acotado sobre hardware edge limitado. Gemma 4 E4B le da a Pollen comprensión multimodal de audio en Android a través de LiteRT-LM, así que el conocimiento de campo hablado se convierte en un `MissionPatch` validado sin pasar por la nube ni por un servicio de speech-to-text separado. Gemma 4 E4B le da a Meristem revisión de política asistida por tool calling sobre un portátil casero a través de `llama.cpp`.

El trabajo de configuración del modelo es parte de la ingeniería. Probamos tamaño de contexto, presupuesto de salida, disciplina de prompt y comportamiento de thinking sobre runtimes locales. Un resultado práctico moldeó la ruta de demo: la longitud del output condicionó la latencia con más fuerza que el contexto de entrada en la ruta de Meristem. Outputs estructurados más cortos preservaron el contrato y mejoraron la usabilidad.

Cada nodo tiene un perfil de modelo distinto. Rhizome necesita outputs cortos, estables, acotados. Pollen necesita comprensión de audio, capacidad de refusal y fidelidad de schema. Meristem dedica más tiempo a revisión de política y rationale. La configuración del modelo pasa a ser una propiedad de la jurisdicción.

## Autoridad acotada

Sprout firma decisiones, hace caducar la autoridad y registra los rechazos.

La ruta crítica empieza con comprobaciones deterministas: validación de schema, TTL, autoridad, cooldown, estado del depósito, heartbeat, hard limits y creación de recibo. Gemma 4 escribe rationales, compila criterios humanos, adapta el lenguaje de superficie y apoya la revisión. La autoridad física final permanece en la capa de seguridad.

Un `MissionPatch` representa la visita y carga un TTL corto. Un `PolicyPacket` representa una ventana de política más amplia y carga su validez. Un `WeatherDigest` caduca antes de que el contexto meteorológico envejezca. Los objetos tardíos son rechazados y registrados.

La capa doble-agente sigue la misma regla. `ShadowSkeptic` registra objeciones. Esas objeciones se vuelven dato. Las objeciones probadas pueden ascender más adelante a reglas deterministas. El agente actual permanece observacional.

![Authority stack de Sprout: Gemma sobre Rhizome propone una acción candidata de 30s; el ESP32 valida el sobre físico — nivel de depósito, duty cycle, caudal — y emite una acción final de 12s, ACK · limited by tank, firmada en un DecisionReceipt.](https://raw.githubusercontent.com/zigiella/sprout/main/media/sprout-authority-stack.png)

*La IA propone. El ESP32 valida. El modelo nunca toca la válvula directamente.*

## Qué hemos construido

El MVP implementa el patrón sobre hardware, móvil y portátil.

Rhizome corre en Jetson con Gemma 4 E2B mediante `llama.cpp`. Produce rationales locales sobre decisiones deterministas, persiste recibos y expone resúmenes para Pollen.

Pollen tiene un flavor demo en Android y una ruta device que usa LiteRT-LM con Gemma 4 E4B y entrada de audio. Compila voz en `MissionPatch`, valida el resultado y devuelve estados de rechazo para instrucciones inseguras o incoherentes.

Meristem corre localmente con evaluación determinista y soporte de tool calling sobre Gemma 4 E4B. Ingesta bundles de visita y produce ventanas de política.

El firmware del ESP32 corre sobre hardware real y expone la ruta de seguridad. Soporta pulsos de bomba supervisados y lecturas de humedad de suelo. La demo mantiene el agua autónoma conservadora y la prueba física explícita.

Rhizome también incluye `ShadowSkeptic`, un segundo auditor local. Disiente con seguridad, escribe evidencia y mantiene `affects_decision=false`.

## Por qué el patrón escala

La unidad de valor de Sprout es una decisión con autoridad acotada. Esa unidad escala de dos macetas a múltiples parcelas porque los contratos siguen siendo pequeños: `DecisionReceipt`, `MissionPatch`, `WeatherDigest`, `ValidationStamp`, `FieldVisit` y `PolicyPacket`.

Una cooperativa puede correr Rhizomes en parcelas dispersas, llevar Pollen en visitas rutinarias y revisar política en casa. Un huerto comunitario puede preservar conocimiento voluntario como mission patches con caducidad y un alcance claro.

## Cómo lo hemos construido

Sprout se construyó en una ventana de 30 días por una humana y un equipo de agentes IA especializados por rol, trabajando bajo restricciones escritas. Cada agente tiene una jurisdicción definida, una identidad explícita y autoría versionada en el historial de git.

La metodología refleja la arquitectura. El repositorio es el contrato. Las bitácoras — diarios de desarrollo en castellano — registran cada decisión arquitectural, cada giro y cada dependencia entre frentes. Los mensajes de inicio de día siguen una plantilla fija que nombra las interrelaciones entre agentes. Los commits de git llevan la identidad del agente inline para que la traza siga siendo revisable.

Este patrón no es decoración. Produjo artefactos que un hackathon suele saltarse: una capa doble-agente de seguridad operativa dentro de Rhizome, tres jurisdicciones Gemma 4 independientes integradas a través de pequeños contratos JSON y un coprocesador físico de seguridad que rechaza comandos no seguros por diseño, no por parche. Proceso y producto comparten la misma invariante: jurisdicción con caducidad.

El detalle de metodología y el índice de bitácoras viven en [`CONTRIBUTING.md`](../CONTRIBUTING.md) y la carpeta [`bitacora/`](../bitacora/).

## Trabajo futuro

Las siguientes iteraciones extienden el mismo modelo de autoridad. Un caudalímetro cerrará la semántica de producción del `WATER` autónomo. Una estación meteorológica local enriquecerá los objetos `WeatherDigest`. La entrada de cámara añadirá evidencia visual de planta sin volverse autoritativa. Pollen soportará conversación de campo en full-duplex. Meristem añadirá reglas estacionales, evaluación de política multi-cultivo y revisión asistida por tools más fuerte.

El patrón doble-agente madurará a través de la medición. `ShadowSkeptic` ya registra objeciones sin autoridad de actuación. Iteraciones futuras compararán objeciones con resultados posteriores, medirán falsos positivos y falsos negativos, y promoverán objeciones probadas y recurrentes a gates deterministas.

El idioma forma parte del roadmap. Sprout mantiene los contratos internos estables, mientras Pollen adapta el idioma de superficie en el edge. El trabajo futuro incluye fine-tuning de Gemma 4 para vocabulario agrícola local e idiomas minoritarios.

## Conclusión

Sprout preserva el criterio de campo durante la ausencia. Convierte visitas en inteligencia operativa. Rechaza instrucciones caducadas. Registra lo que pasó. Le da a la IA local una segunda voz escéptica antes de darle a esa voz cualquier autoridad.

**Sprout es IA abierta y local para decisiones sobre el agua bajo ausencia: autoridad acotada, recibos firmados, una segunda voz local que audita sin autoridad y una capa física que puede decir no.**

---

**Repositorio:** https://github.com/zigiella/sprout · Apache 2.0
**Punto de entrada para evaluación:** [`SUBMISSION.md`](../SUBMISSION.md)
**Versión inglesa canónica:** [`writeup/draft.md`](draft.md) — esta es la traducción al castellano del draft EN principal de la entrega.

*Construido sobre Gemma 4 de Google. Gemma is a trademark of Google LLC. Este proyecto no está afiliado ni respaldado por Google.*
