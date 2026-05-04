# Pitch y vídeo — v2

## 1. Pitch de 30 segundos

Sprout es una arquitectura AI local-first para riego en parcelas aisladas.  
Cada parcela tiene un nodo Rhizome que decide y actúa offline con Gemma 4 E2B sobre Jetson, pero solo dentro de un sobre seguro impuesto por un ESP32. Cuando una persona visita las parcelas, Pollen en Android usa Gemma 4 E4B para hablar con Rhizome, validar su criterio, compilar nuevas prioridades humanas y federar contexto entre nodos. Meristem corre en el portátil casero del agricultor — Gemma 4 E4B vía llama.cpp — y refina políticas duraderas: la lógica determinista decide, el LLM solo escribe el rationale en castellano natural. El resultado es mejor criterio de riego cuando el campo, la persona y la red no coinciden en el tiempo.

## 2. Pitch de 90 segundos

La agricultura aislada no sufre solo por falta de agua.  
Sufre porque la decisión correcta suele llegar tarde. Si no hay buena conectividad y solo visitas la parcela cada cierto tiempo, acabas regando demasiado tarde, demasiado pronto o con el criterio equivocado.

Sprout reduce esa latencia con tres nodos. Rhizome vive en la parcela y decide offline con sensores, meteo y política vigente. Pero nunca toca el agua directamente: un ESP32 verifica reglas duras y modula o bloquea cada acción. Pollen vive en un móvil Android con Gemma 4 E4B y convierte cada visita en algo mucho más valioso que una sincronización: habla con la persona, pregunta a Rhizome qué hizo, valida el estado real, compila la intención humana, y federa contexto entre parcelas que no tienen red directa entre sí.

Meristem vive en el portátil casero del agricultor con Gemma 4 E4B vía llama.cpp. Cuando hay calma — al cerrar el día en la cocina, no en el campo — recibe los bundles que Pollen ha traído de las parcelas, evalúa con lógica determinista, y emite una nueva política duradera. El LLM solo escribe el rationale; la decisión es auditable hasta una regla concreta. Es el cerebro lento del sistema.

En nuestra demo usamos dos macetas como dos parcelas lógicas — una con estación meteo local, otra sin — filmadas con un solo Rhizome físico. Veremos cómo Rhizome sigue funcionando solo, cómo el ESP32 modula una orden por seguridad sin bloquearla, cómo Pollen trae criterio humano y federa contexto fresco entre parcelas, cómo el sistema modifica su criterio de riego cuando la visita aporta información nueva, y cómo rechaza instrucciones o digests que ya no merecen confianza.

## 3. Frases fuertes

- **Rhizome mantiene viva la parcela cuando nadie está.**
- **Cada visita puede cambiar el criterio local.**
- **La IA propone; el agua la gobierna una capa física prudente.**
- **Toda inteligencia tiene jurisdicción y fecha de caducidad.**
- **Pollen convierte esas visitas en inteligencia federada.**

> Notas operativas:
> - **Frases 2 y 5 funcionan como par** (reformulación dia 12 tras feedback DEV externa). La 2 se afirma en VO escena 4 — afirmacion testable, no promesa — y la prueba la da escena 5 inmediatamente despues. La 5 cierra la cadena en VO al final de escena 6 con eco "esas" hacia escena 4 (coherencia interna fuerte).
> - **Frase 4** mantiene su forma en el writeup. En el VO de la escena 8 dice *"Toda inteligencia tiene jurisdicción y fecha de caducidad"* sin "En Sprout"; el nombre del producto vive en cartela final, no en VO previo.
> - **La cartela progresiva final de escena 9** mantiene la formulacion *"Inteligencia federada con Pollen"* como eco visual textual — la frase 5 ya esta dicha en VO escena 6, la cartela es remate visual, no repeticion literal.

## 4. Estructura del vídeo (3 minutos · 9-10 escenas)

> **Pivote v2.1 (día 11)**: el guion cierra a 9 escenas (no 8). La escena 8 original se parte en dos — *Caducidad* (10s) + *Cenital federado* (20s) — robando 5s a la escena 4 y 5s a la escena 6 para alimentar el cierre.
>
> **Pivote día 18 (Bea + Cambium)** pendiente cerrar en sesión conjunta tres con Corola (probable día 20):
> - **Cartela apertura nueva (~5 seg)** antes de E1: Sprout + lema + 3 nodos. El espectador entra con marco antes de la ausencia.
> - **E1 reformulada con 4 datos globales**: UNCCD 48% territorio mundial con sequía extrema 2023, UNCCD 1.800M afectados / 300B USD/año, gencat -80% riego agrícola Cataluña 2024, ITU 58% rural mundial. Cataluña como ejemplo del patrón global, no protagonista.
> - **VO master pasa a INGLÉS + subtítulos en inglés.** Versión ES dub aparte. La voz cruda de Bea en E5 (`operator_note`) se mantiene en castellano sin traducir como decisión narrativa deliberada.
> - **E9b nueva** (probable 2:50–3:00, 10s): Bea tecleando en portátil casero con Meristem en pantalla + cutaway a sus macetas reales (Sprout escala 1 corriendo en su terraza de Castellar). Implica que **E9 cenital se puede comprimir a 10s o se mantiene 20s y E9b se acomoda en otra zona** — decisión sesión.
> - **Tagline bookend** (inicio + cierre del video): *"When network is absent — and the human is far — local criteria still irrigate."*
>
> **Decisión de rodaje (día 11)**: las dos parcelas lógicas (`rhizome_01` con estación meteo + `rhizome_02` sin meteo) se filman con un solo Rhizome físico — distinto ángulo, distinta maceta, distinta zona de terraza. Los IDs en pantalla hacen el trabajo lógico. La narrativa simula la federación tal como ocurriría en una explotación que empezó con un nodo y añadió otro más adelante. Honesto con el MVP.

| # | Escena | Tiempo | Beat clave |
|---|--------|--------|-----------|
| 0 | **Cartela Sprout + lema + 3 nodos** *(propuesta día 18, pendiente sesión)* | 0:00–0:05 (5s) | marco antes de la ausencia |
| 1 | La ausencia | 0:05–0:25 (20s) *con datos globales reformulados día 18* | 4 datos globales (UNCCD + gencat + ITU) — escala mundial baja a local |
| 2 | Rhizome decide offline | 0:25–0:50 (25s) | sensor → estado → decisión → orden → `DecisionReceipt` + frase fuerte 1 |
| 3 | ESP32 SAFE LIMIT | 0:50–1:05 (15s) | modulación (no rechazo) + frase fuerte 3 — **wow moment dirigido** |
| 4 | Llega Pollen | 1:05–1:35 (30s) | "¿qué pasó desde mi última visita?" + resumen receipts + frase fuerte 2 |
| 5 | La persona da una misión | 1:35–1:55 (20s) | voz humana coloquial castellano → `MissionPatch` traducido (`operator_note` literal sin traducir) — prueba la frase 2 |
| 6 | Ferry A→B | 1:55–2:15 (20s) | Pollen lleva `WeatherDigest` de `rhizome_01` (con meteo) a `rhizome_02` (sin meteo) + frase fuerte 5 |
| 7 | Criterio modificado | 2:15–2:35 (20s) | side-by-side política antes/después + cartela ancla **`Watering criteria updated.`** + cartela invariante esquina inferior derecha |
| 8 | Caducidad | 2:35–2:45 (10s) | `expired → rejected` + frase fuerte 4 |
| 9 | Cenital federado + Meristem | 2:45–2:55 (10s) *o 2:45–3:00 si E9b se incorpora en otra zona* | cenital animado (Venation, no Veo3) · 8 parcelas · Pollen recorriendo · `SYNCED ✓` · cartela progresiva |
| 9b | **Meristem en la mesa de casa** *(propuesta día 18, pendiente sesión)* | 2:55–3:00 (5s) | plano corto Bea tecleando en portátil + Meristem en pantalla + cutaway micro a macetas — **cierre íntimo doméstico** + tagline bookend |

### Detalle por escena

**Escena 1 — La ausencia (0:00–0:20).** Plano de la maceta como parcela lógica visitada periódicamente. Cartela: *"Esto representa parcelas visitadas periódicamente, no continuamente."*

**Escena 2 — Rhizome decide offline (0:20–0:45).** Se ve sensor, estado local, decisión, orden al ESP32, `DecisionReceipt`. Cierre con frase fuerte 1.

Cartelas (esquina superior derecha, ~3s, en ingles para jurado anglo):
- *"Gemma 4 E2B · local · llama.cpp"*
- sub-cartela: *"LLM called only when ambiguous"*

**Escena 3 — ESP32 SAFE LIMIT (0:45–1:00).** Modulación, no rechazo: el ESP32 reduce los segundos pedidos por seguridad (`candidate_action.seconds=30 → final_action.seconds=12`) y la diferencia es donde la capa física trabaja. Cartela: *"ESP32 SAFE LIMIT"*. Frase fuerte 3.

Cartela narrativa central (3s, sobre plano del ESP32 modulando): ***"Cuando duda, riega menos."*** — refuerza la frase fuerte 3 sin sumar carga al pitch §3.

Cartela esquina (3s): *"function/read tools · no actuator tools"* — explicita que la IA solo lee, no actua sobre hardware.

**Escena 4 — Llega Pollen (1:00–1:30).** En el móvil: *"¿qué pasó desde mi última visita?"*. Rhizome responde a través del teléfono, se ve resumen de decisiones. VO con frase fuerte 2: *"Cada visita puede cambiar el criterio local."*

Cartela esquina (3s): *"Gemma 4 E4B · LiteRT-LM · on-device"*.

**Escena 5 — La persona da una misión (1:30–1:50).** Voz humana coloquial real:

> *"Vuelvo el viernes. Esta planta aguanta más seca de lo que crees, riega un poco menos."*

Pollen compila a `MissionPatch` con `horizon_h: 72`, `soil_thresholds.dry: 35→25`, `budget_cap_ml: 1500→900`, y el `operator_note` literal de la voz humana.

**Escena 6 — Ferry A→B (1:50–2:10).** Pollen lleva `WeatherDigest` de `rhizome_01` (con estación meteo) a `rhizome_02` (sin meteo). Corte limpio entre los dos planos del mismo Rhizome físico. VO al final: *"Inteligencia federada con Pollen."*

**Escena 7 — Criterio modificado (2:10–2:30).** Side-by-side de política antes y después en pantalla del receipt:

- `soil_thresholds.dry: 35 → 25`
- `daily_budget_ml: 1500 → 900`

Una sola acción física filmable que demuestra el cambio (la planta riega más tarde y con menos agua que la vez anterior). Cartela ancla: **"Criterio modificado"**.

**Escena 8 — Caducidad (2:30–2:40).** Mostrar un digest o patch caducado que se rechaza. VO con frase fuerte 4: *"Toda inteligencia tiene jurisdicción y fecha de caducidad."*

**Escena 9 — Cenital federado + Meristem (2:45–2:55 o 2:40–3:00 según sesión día 20).** Animación flat editorial de Venation (sustituye Veo3, decisión Bea día 17). 8 parcelas vistas en cenital, Pollen recorriendo, paquetes tangibles `POLICIES` y `RECEIPTS` viajando entre Meristem y Pollen. Cartela progresiva: *"Una parcela. Dos. Ocho. Autónomas. Inteligencia federada con Pollen."* (versión EN master pendiente cierre — propuesta Cambium *"One plot. Two. Eight. Federated. Autonomous."* es modulación; cadencia Corola actual mantiene *"One plot. Two. Eight. / Autonomous. / Federated intelligence, carried by Pollen."*). Cierre con `SYNCED ✓`.

**Escena 9b — Meristem en la mesa de casa (propuesta día 18, pendiente sesión).** Plano corto: Bea tecleando en portátil casero, terminal/UI de Meristem en pantalla. Posible cutaway micro a las macetas reales en la terraza (Sprout escala 1 corriendo: garrafa-depósito + sensores + ESP32 + Jetson). Cierre con tagline bookend en pantalla negra: *"When network is absent — and the human is far — local criteria still irrigate."*

El nombre **Sprout** aparece como cartela final justo antes del fundido. Microcartela esquina inferior: *"Built on Gemma 4 by Google. Gemma is a trademark of Google LLC."*

## 5. Shot list mínima

- overlay "offline"
- overlay "DecisionReceipt"
- overlay **"ESP32 SAFE LIMIT"**
- overlay "MissionPatch validado"
- overlay "WeatherDigest ferry"
- overlay "expired → rejected"
- cartela ancla "Criterio modificado"
- cartela progresiva final "Una parcela. Dos. Ocho. Autónomas. Inteligencia federada con Pollen."

## 6. Qué no enseñar

- largas terminales,
- setup eléctrico entero,
- sync complejo,
- visión si todavía es frágil.

> **Cambio día 17 (Bea)**: Meristem **sí entra en MVP del vídeo**. Cierre día 16 = LLM E4B integrado con tool calling end-to-end + multi-Rhizome simulado v0 + decisions_by_rule. Es pieza demo blindada para Safety & Trust. Aparece en E9 cenital (paquetes `POLICIES`/`RECEIPTS` viajando entre Meristem y Pollen) y E9b propuesta (Bea tecleando portátil casero con Meristem en pantalla).
