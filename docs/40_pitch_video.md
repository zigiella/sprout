# Pitch y vídeo — v2

## 1. Pitch de 30 segundos

Sprout es una arquitectura local-first para riego en parcelas aisladas.  
Cada parcela tiene un nodo Rhizome que decide y actúa offline con Gemma 4 E2B sobre Jetson, pero solo dentro de un sobre seguro impuesto por un ESP32. Cuando una persona visita las parcelas, Pollen en Android usa Gemma 4 E4B para hablar con Rhizome, validar su criterio, compilar nuevas prioridades humanas y federar contexto entre nodos. Meristem queda especificado como cerebro lento post-hackathon. El resultado es mejor criterio de riego cuando el campo, la persona y la red no coinciden en el tiempo.

## 2. Pitch de 90 segundos

La agricultura aislada no sufre solo por falta de agua.  
Sufre porque la decisión correcta suele llegar tarde. Si no hay buena conectividad y solo visitas la parcela cada cierto tiempo, acabas regando demasiado tarde, demasiado pronto o con el criterio equivocado.

Sprout reduce esa latencia con tres nodos. Rhizome vive en la parcela y decide offline con sensores, meteo y política vigente. Pero nunca toca el agua directamente: un ESP32 verifica reglas duras y modula o bloquea cada acción. Pollen vive en un móvil Android con Gemma 4 E4B y convierte cada visita en algo mucho más valioso que una sincronización: habla con la persona, pregunta a Rhizome qué hizo, valida el estado real, compila la intención humana, y federa contexto entre parcelas que no tienen red directa entre sí.

En nuestra demo usamos dos macetas como dos parcelas lógicas — una con estación meteo local, otra sin — filmadas con un solo Rhizome físico. Veremos cómo Rhizome sigue funcionando solo, cómo el ESP32 modula una orden por seguridad sin bloquearla, cómo Pollen trae criterio humano y federa contexto fresco entre parcelas, cómo el sistema modifica su criterio de riego cuando la visita aporta información nueva, y cómo rechaza instrucciones o digests que ya no merecen confianza.

## 3. Frases fuertes

- **Rhizome mantiene viva la parcela cuando nadie está.**
- **Pollen convierte la visita en inteligencia útil.**
- **La IA propone; el agua la gobierna una capa física prudente.**
- **Toda inteligencia tiene jurisdicción y fecha de caducidad.**
- **Inteligencia federada con Pollen.**

> Notas operativas:
> - La frase 4 mantiene su forma en el writeup. En el VO de la escena 8 dice *"Toda inteligencia tiene jurisdicción y fecha de caducidad"* sin "En Sprout"; el nombre del producto vive en cartela final, no en VO previo.
> - La frase 5 es la única que se repite en el vídeo: aparece en VO al final de la escena 6 (remate del ferry) y en cartela progresiva durante la escena 9 (cenital federado).

## 4. Estructura del vídeo (3 minutos · 9 escenas)

> **Pivote v2.1 (día 11)**: el guion cierra a 9 escenas (no 8). La escena 8 original se parte en dos — *Caducidad* (10s) + *Cenital federado* (20s) — robando 5s a la escena 4 y 5s a la escena 6 para alimentar el cierre.
>
> **Decisión de rodaje (día 11)**: las dos parcelas lógicas (`rhizome_01` con estación meteo + `rhizome_02` sin meteo) se filman con un solo Rhizome físico — distinto ángulo, distinta maceta, distinta zona de terraza. Los IDs en pantalla hacen el trabajo lógico. La narrativa simula la federación tal como ocurriría en una explotación que empezó con un nodo y añadió otro más adelante. Honesto con el MVP.

| # | Escena | Tiempo | Beat clave |
|---|--------|--------|-----------|
| 1 | La ausencia | 0:00–0:20 (20s) | apertura silenciosa, una parcela visitada periódicamente |
| 2 | Rhizome decide offline | 0:20–0:45 (25s) | sensor → estado → decisión → orden → `DecisionReceipt` + frase fuerte 1 |
| 3 | ESP32 SAFE LIMIT | 0:45–1:00 (15s) | modulación (no rechazo) + frase fuerte 3 |
| 4 | Llega Pollen | 1:00–1:30 (30s) | "¿qué pasó desde mi última visita?" + resumen receipts + frase fuerte 2 |
| 5 | La persona da una misión | 1:30–1:50 (20s) | voz humana coloquial → `MissionPatch` traducido (`operator_note` literal) |
| 6 | Ferry A→B | 1:50–2:10 (20s) | Pollen lleva `WeatherDigest` de `rhizome_01` (con meteo) a `rhizome_02` (sin meteo) + corte limpio + *"Inteligencia federada con Pollen"* (1ª vez) |
| 7 | Criterio modificado | 2:10–2:30 (20s) | side-by-side política antes/después + cartela ancla **"Criterio modificado"** + acción física distinta |
| 8 | Caducidad | 2:30–2:40 (10s) | `expired → rejected` + frase fuerte 4 (sin "En Sprout") |
| 9 | Cenital federado | 2:40–3:00 (20s) | Veo3 flat editorial · 8 parcelas vistas en cenital · Pollen recorriendo · cartela progresiva: *"Una parcela. Dos. Ocho. Autónomas. Inteligencia federada con Pollen."* |

### Detalle por escena

**Escena 1 — La ausencia (0:00–0:20).** Plano de la maceta como parcela lógica visitada periódicamente. Cartela: *"Esto representa parcelas visitadas periódicamente, no continuamente."*

**Escena 2 — Rhizome decide offline (0:20–0:45).** Se ve sensor, estado local, decisión, orden al ESP32, `DecisionReceipt`. Cierre con frase fuerte 1.

**Escena 3 — ESP32 SAFE LIMIT (0:45–1:00).** Modulación, no rechazo: el ESP32 reduce los segundos pedidos por seguridad (`candidate_action.seconds=30 → final_action.seconds=12`) y la diferencia es donde la capa física trabaja. Cartela: *"ESP32 SAFE LIMIT"*. Frase fuerte 3.

**Escena 4 — Llega Pollen (1:00–1:30).** En el móvil: *"¿qué pasó desde mi última visita?"*. Rhizome responde a través del teléfono, se ve resumen de decisiones. Frase fuerte 2.

**Escena 5 — La persona da una misión (1:30–1:50).** Voz humana coloquial real:

> *"Vuelvo el viernes. Esta planta aguanta más seca de lo que crees, riega un poco menos."*

Pollen compila a `MissionPatch` con `horizon_h: 72`, `soil_thresholds.dry: 35→25`, `budget_cap_ml: 1500→900`, y el `operator_note` literal de la voz humana.

**Escena 6 — Ferry A→B (1:50–2:10).** Pollen lleva `WeatherDigest` de `rhizome_01` (con estación meteo) a `rhizome_02` (sin meteo). Corte limpio entre los dos planos del mismo Rhizome físico. VO al final: *"Inteligencia federada con Pollen."*

**Escena 7 — Criterio modificado (2:10–2:30).** Side-by-side de política antes y después en pantalla del receipt:

- `soil_thresholds.dry: 35 → 25`
- `daily_budget_ml: 1500 → 900`

Una sola acción física filmable que demuestra el cambio (la planta riega más tarde y con menos agua que la vez anterior). Cartela ancla: **"Criterio modificado"**.

**Escena 8 — Caducidad (2:30–2:40).** Mostrar un digest o patch caducado que se rechaza. VO con frase fuerte 4: *"Toda inteligencia tiene jurisdicción y fecha de caducidad."*

**Escena 9 — Cenital federado (2:40–3:00).** Veo3 flat editorial. 8 parcelas vistas en cenital, Pollen recorriendo. Cartela progresiva: *"Una parcela. Dos. Ocho. Autónomas. Inteligencia federada con Pollen."* El nombre **Sprout** aparece como cartela final justo antes del fundido.

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
- visión si todavía es frágil,
- Meristem (fuera de demo del hackathon; queda como trabajo en curso post-hackathon).
