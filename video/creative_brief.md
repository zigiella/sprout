# Sprout — creative brief del vídeo de presentación

**Versión:** v1.0 (guion conceptualmente cerrado, pendiente apilar escenas 1-3 + producción)
**Fecha:** 2026-04-27 (día 12 de 30)
**Equipo:** zigiella (Bea, Cambium, Corola, Floema, Xilema, Meristem, Estoma, Peri)
**Hackathon:** The Gemma 4 Good — concurso internacional de Google sobre uso de la familia Gemma 4 para el bien común
**Contexto del documento:** lo lees porque conoces al jurado y nos haces el favor de mirarlo. Gracias.

---

## La pregunta que resolvemos

¿Cómo se cuida una parcela agrícola cuando la persona, el campo y la red no coinciden en el tiempo?

Pequeñas explotaciones: huerto urbano, microparcelas dispersas, cooperativas con puntos de riego no siempre conectados, escuelas con mantenimiento periódico. Lo que estos casos comparten no es la falta de agua, es la falta de **decisión a tiempo**. La persona pasa cada cierto tiempo. La red va y viene. La planta no espera.

## Qué es Sprout

> Una arquitectura local-first para decisiones de riego en parcelas aisladas, con agua limitada, visitas humanas intermitentes y conectividad incierta.

Tres nodos lógicos, cada uno con jurisdicción:

- **Rhizome** vive en la parcela. Lee sensores, decide regar o no, ejecuta a través de un coprocesador de seguridad. Gemma 4 E2B sobre Jetson Orin Nano Super, vía llama.cpp. Nunca toca el agua directamente.
- **ESP32** es la capa física prudente. Modula órdenes inseguras, no solo las rechaza. Tiene reglas duras grabadas en firmware. Si el Jetson cae, el sistema no se vuelve peligroso.
- **Pollen** vive en un móvil Android del visitante. Gemma 4 E4B sobre LiteRT-LM. Habla con la persona, traduce intención humana a política, audita lo que Rhizome decidió, federa contexto entre parcelas que no tienen red entre sí.

Hay un cuarto nodo, **Meristem** — cerebro lento de consolidación post-visita — pero **queda fuera de la demo del hackathon**. La decisión es deliberada: el alcance del video es lo que se puede demostrar real con el MVP que llegará al rodaje el 26-27 de abril. Meristem queda especificado como trabajo en curso, con adapter Ollama-compatible ya construido (PR #50, 4083 líneas, 88 tests verdes) disponible como infraestructura preparada para Sprout v2.

## Tesis ante el jurado

> Cuando el campo, la persona y la red no coinciden en el tiempo, Sprout reduce la latencia de decisión sin renunciar a soberanía local, seguridad física y explicabilidad.

No defendemos riego automatizado. Defendemos infraestructura abierta para que parcelas con poca conectividad sigan recibiendo decisiones razonables, seguras y explicables.

---

## La idea creativa del video

Tres minutos. Nueve escenas. La estructura responde a una decisión narrativa explícita: **el video tiene dos mundos visuales claros que se rozan en el último beat.**

- **Mundo 1 — el cerebro local (escenas 1-7).** Estética técnica, pantalla del Jetson, JSON real del sistema, monoespaciada, fondo oscuro. Lo que ves es lo que el sistema realmente escupe — claves del contrato (`DecisionReceipt`, `MissionPatch`, `WeatherDigest`), IDs reales (`pol_010`, `mp_004`), JSON literal cotejable con la documentación pública del proyecto. Es la versión que un Gemma DevRel puede pausar y verificar campo a campo.
- **Mundo 2 — la red posible (escena 9).** Estética flat editorial moderna. Veo3 generando 8 parcelas vistas en cenital, dispuestas en mosaico irregular sobre paleta tierra, con un nodo abstracto recorriéndolas. Sin cielo realista, sin sombras realistas — abstracción gráfica que **eleva la escala**.

La transición entre los dos mundos es el último beat: la maceta real del rodaje sufre un morph sutil hasta convertirse en una de las 8 parcelas flat del cenital. El video pasa de **filmado** a **diagramado** en un solo plano. Esto no es decoración: el sistema es *uno hoy y muchos mañana*, y la estética hace ese salto antes de que la cartela final lo nombre.

### Decisiones creativas que sostienen el video

**Densidad en cartelas, no en VO.** Los datos fuertes (claves de contrato, IDs, parámetros) viven en pantalla. La voz castellana (~80 palabras en 3 minutos, doblaje EN al cierre) hace la historia. Esto permite doblaje sin apretar y permite que el espectador pueda pausar para leer detalle técnico si quiere.

**Apertura silenciosa.** Los primeros 20 segundos: una maceta sola, una cartela en castellano traducida al inglés, cero VO. El jurado anglo entra sin fricción idiomática. Cuando el VO arranca a los 0:24, ya están dentro.

**Voz humana real.** En la escena 5, la persona graba una frase coloquial — *"Vuelvo el viernes. Esta planta aguanta más seca de lo que crees, riega un poco menos."* — y el sistema la traduce en pantalla a parámetros técnicos: `horizon_h: 72`, `soil_thresholds.dry: 35→25`, `budget_cap_ml: 1500→900`, `operator_note` literal. Es el momento más humano del video y la prueba más limpia de qué hace Pollen: traduce intuición agrícola a parámetro ejecutable, **sin perder lo que la persona quiso decir**.

**Verbo neutro, agnóstico al portador.** Pollen es móvil itinerante. Lo que viaja es el dispositivo con Gemma — quien lo lleve (persona andando, en bici, en camioneta, dron agrícola autónomo) es decisión de despliegue. El video evita "caminar" y "a pie"; usa "en ruta" y "se mueve". La narrativa del video muestra caso humano — coherencia con *Gemma 4 Good* y autoridad física encarnada — pero el lenguaje no encadena la tesis a un solo modo de movilidad.

**Estética dual deliberada.** El bloque cerebro-local vive en su mundo (técnico, monospace). El cierre vive en el suyo (flat editorial). El contraste es estructural, no accidental: refleja que Sprout es **arquitectura concreta hoy y promesa de red mañana**.

---

## Estructura del video — 9 escenas, 3 minutos

| # | Escena | Tiempo | Beat clave |
|---|--------|--------|-----------|
| 1 | La ausencia | 0:00–0:20 (20s) | apertura silenciosa, una maceta como parcela visitada periódicamente |
| 2 | Rhizome decide offline | 0:20–0:45 (25s) | sensor → estado → decisión → orden → `DecisionReceipt` |
| 3 | ESP32 SAFE LIMIT | 0:45–1:00 (15s) | modulación de orden por seguridad (no rechazo total) |
| 4 | Llega Pollen | 1:00–1:30 (30s) | móvil pregunta "¿qué pasó desde mi última visita?" |
| 5 | La persona da una misión | 1:30–1:50 (20s) | voz humana coloquial → `MissionPatch` traducido |
| 6 | Ferry A→B | 1:50–2:10 (20s) | Pollen lleva `WeatherDigest` de `rhizome_01` (con meteo) a `rhizome_02` (sin meteo) |
| 7 | Criterio modificado | 2:10–2:30 (20s) | side-by-side de política antes/después + acción física distinta |
| 8 | Caducidad | 2:30–2:40 (10s) | `expired → rejected` — el sistema rechaza un digest viejo |
| 9 | Cenital federado | 2:40–3:00 (20s) | Veo3 flat editorial · 8 parcelas en cenital · Pollen-nodo recorriendo |

**Decisión de rodaje:** las dos parcelas lógicas de la escena 6 (`rhizome_01` y `rhizome_02`) se filman con un **solo Rhizome físico** — distinto ángulo, distinta maceta, distinta zona de terraza, distintos IDs en pantalla. Es honesto con el MVP: simula la federación tal como ocurriría en una explotación pequeña que empezó con un nodo y añadió otro más adelante.

---

## Las cinco frases fuertes — distribución y dosificación

El video se sostiene narrativamente sobre cinco afirmaciones, cada una atada a la imagen exacta que la sostiene:

1. **"Rhizome mantiene viva la parcela cuando nadie está."** Aterriza en escena 2 sobre el `DecisionReceipt` y el agua saliendo de la válvula. Es la promesa del sistema offline-first.

2. **"Pollen convierte la visita en inteligencia útil."** Aterriza en escena 4 — el móvil consultando, recibiendo resumen de decisiones. **Pero** la frase no se afirma sin prueba: la escena 5 *demuestra* la conversión cuando la voz humana coloquial se traduce a `MissionPatch`. La frase 2 es promesa; la escena 5 es la prueba. *(Nota interna: esta frase ha sido cuestionada por la directora creativa principal del proyecto durante la iteración. La salvamos manteniendo el VO en escena 4 y reforzando la demostración en escena 5. Si la frase no se sostuviera, sería el primer hilo a tirar.)*

3. **"La IA propone; el agua la gobierna una capa física prudente."** Aterriza en escena 3 sobre el ESP32 modulando los segundos de riego pedidos. La capa física no rechaza — modula. La diferencia entre `candidate_action` (lo que Rhizome propone) y `final_action` (lo que ESP32 ejecuta) es donde la prudencia trabaja.

4. **"Toda inteligencia tiene jurisdicción y fecha de caducidad."** Aterriza en escena 8 sobre el `WeatherDigest` viejo siendo rechazado por TTL. La caducidad como virtud, no como bug.

5. **"Inteligencia federada con Pollen."** Es la única frase que se repite. Aparece en VO al final de la escena 6 (remate del ferry, justo cuando el Rhizome B acepta el digest que Pollen trajo) y en cartela durante la escena 9 (cierre cumbre). La aparición doble es deliberada: las frases que se repiten son las que el espectador recuerda.

---

## Cierre del video

La escena 9 lleva una **cartela progresiva** dosificada en tres beats sincronizados con el avance del nodo Pollen entre las 8 parcelas:

> *Una parcela. Dos. Ocho.*
>
> *Autónomas.*
>
> *Inteligencia federada con Pollen.*

Sobre la imagen del nodo recorriendo, mensajes en pantalla aparecen y desaparecen al ritmo de cada toque — `WeatherDigest accepted`, `MissionPatch delivered`, `DecisionReceipt synced`, `ValidationStamp issued`, `WeatherDigest cached`. Cada uno es un objeto del contrato de datos visto antes en el video. Repetición de palabras conocidas refuerza coherencia.

Tarjeta final: `Sprout · zigiella · Apache 2.0 · github.com/zigiella/sprout`.

Sin VO en escena 9. La voz se quedó en escena 8. El cenital es predominantemente visual + cartela progresiva.

---

## Decisión abierta — escena 7, dos alternativas visuales

Esta es la escena donde la dirección creativa interna está dividida y donde tu opinión nos vendría especialmente bien.

La escena muestra el **cambio de criterio** del sistema tras recibir el `MissionPatch` de la persona. Dos parámetros cambian: `soil_thresholds.dry: 35→25` y `daily_budget_ml: 1500→900`. Hay dos formas posibles de diseñar la pantalla que muestra ese cambio:

**Alternativa A — "El log honesto".** Pantalla del Jetson llenando el plano. Fondo oscuro, monoespaciada, log entrando en cadencia musical con claves del contrato (`mission_patch_received`, `policy_active`, `pol_009 → pol_010`), `diff` con los dos campos resaltados, `DecisionReceipt` en JSON literal. La cartela ancla *"Criterio modificado."* aterriza grande sobre el log.

**Alternativa B — "El dashboard limpio".** Pantalla del móvil de Pollen con vista flat editorial moderna, dos columnas (ANTES / AHORA), estética coherente con el cierre cenital de la escena 9. Legibilidad inmediata para no técnicos. Pero es una vista que no existe en el sistema implementado — habría que diseñar la UI.

**Voto interno:** A, por tres razones —
- Honestidad técnica como ventaja competitiva (un Gemma DevRel cotejará con la documentación pública y todo cuadrará).
- Coherencia con bloque cerebro-local (escenas 2 y 3 ya viven en pantalla técnica).
- Coste de producción menor sin invadir backlog del equipo de Pollen en recta final del MVP.

**Pregunta a la lectora:** ¿qué crees que aterriza mejor con el jurado de DevRel — la honestidad técnica de A, o la legibilidad de B? ¿Hay un riesgo de que A resulte "demasiado pantalla de DOS" si la dirección de arte no es fina, y entonces compense más B aunque sea interpretación?

---

## Cosas sobre las que pedimos tu opinión

1. **Las cinco frases fuertes.** ¿Aterrizan donde están dosificadas? ¿Hay alguna que sientas débil? La frase 2 ya está bajo observación interna.

2. **La estética dual.** ¿El contraste entre el bloque cerebro-local (técnico) y el cierre cenital (flat editorial) funciona, o es demasiado salto? ¿Has visto algo similar funcionar en videos de hackathon dirigidos a jurado DevRel?

3. **La voz humana real en escena 5.** *"Vuelvo el viernes. Esta planta aguanta más seca de lo que crees, riega un poco menos."* es 14 palabras de una persona real. ¿Te parece riesgo o virtud? ¿Crees que el jurado la sentirá auténtica o teatralizada?

4. **La decisión de filmar las dos parcelas con un solo Rhizome físico.** ¿Crees que se notará como recurso? ¿Hay manera de que el rodaje proteja contra ese riesgo, o es aceptable que se note (porque es exactamente lo que pasaría en una explotación que empezó con un nodo)?

5. **El uso de Veo3 limitado a la escena 9.** ¿Es proporcionado, o crees que el video necesita más generación para sostenerse visualmente con un jurado acostumbrado a producción alta?

6. **Lo que falta.** Si hubiera una sexta frase fuerte que el video debería tener para alguien que conoce a Glenn Cameron, Kristen Quan, Gus Martins (Gemma DevRel) o Ian Ballantyne — ¿cuál sería?

7. **Cualquier otra cosa.** Si hay algo que te chirría, que te aburre, que te emociona, que te confunde — dilo. El feedback honesto vale más que el educado.

---

## Lo que el video promete y lo que entrega

**Promete:**
- Un sistema agrícola local-first que decide solo, explica lo que hizo, modula con seguridad física, escucha a la persona y federa contexto entre parcelas sin red.
- Tres tiers oficiales de Gemma 4 distribuidos en sus tiers oficiales de despliegue: E2B en edge (Rhizome / Jetson), E4B en mobile con razonamiento (Pollen / Pixel 10 Pro), 26B A4B en laptop (Meristem / portátil — fuera de demo).

**Entrega:**
- Un MVP filmable los días 26-27 de abril con Jetson + ESP32 + dos macetas + un móvil + un solo Rhizome físico haciendo dos roles lógicos.
- Una arquitectura completa documentada en repositorio público (Apache 2.0).
- Voz humana real en escena 5 grabada por una persona del equipo.
- Plano cenital generado con Veo3 estética flat editorial moderna.

**No entrega (deliberado):**
- Meristem en demo. Cerebro lento queda como trabajo en curso post-hackathon.
- Visión por cámara fija. Fuera de ruta crítica.
- Multi-Rhizome físico real. Decisión de filmar uno haciendo de dos.
- Fine-tuning. Trabajo preservado pero fuera de demo.
- Conectividad cloud para que la demo funcione. Todo offline en la grabación.

---

## Quién está detrás

Equipo zigiella, ocho miembros con roles diferenciados. Cada uno trabaja en su scope con autonomía y se coordina vía bitácoras y PRs en repositorio público.

- **Bea** — directora creativa principal, lectura crítica del proyecto, doblaje EN.
- **Cambium** — arquitectura, redacción de bitácoras estabilizadoras, redactor del writeup.
- **Corola** — guion + producción del video, autora de este documento.
- **Floema** — ingeniería de Pollen (móvil + LiteRT-LM + Gemma 4 E4B).
- **Xilema** — ingeniería de Rhizome (Jetson + Gemma 4 E2B + harness de evaluación).
- **Meristem** — adapter Ollama-compatible y modelo 26B A4B (post-hackathon).
- **Estoma + Peri** — célula de investigación, validación contra documentación oficial.

El proyecto se ha pivotado cinco veces en doce días — una de ellas estructural (constitución v2 día 8), las demás puntuales (verbo neutro, modelo objetivo de Pollen, modelo objetivo de Meristem, una parcela en lugar de dos en escena 7). Cada pivote ha sido absorbido sin reescritura de capas porque las abstracciones (cartelas, frases fuertes, contratos de datos) fueron escritas como tales desde el inicio. Esto es relevante para el jurado porque la **tesis del proyecto se demuestra empíricamente en su propio proceso**: el coste del cambio se paga en la abstracción, no en el cambio.

---

## Cómo nos llega tu feedback

Bea coordina. Lo que nos digas, en el formato que quieras (texto, llamada, notas en este documento), le llega a Bea y de ahí al equipo. Si tienes preguntas antes de dar feedback, también vale.

Gracias por mirar.

— Corola
*directora creativa del video, equipo zigiella*
