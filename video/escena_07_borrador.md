# Escena 7 — Rhizome reevalua y modifica su criterio

**Estado:** borrador para revision conjunta con Bea ANTES de apilar las
otras siete escenas. Propuesta de Corola dia 8 (22 abr) y arrancada
dia 10 (25 abr).

**Tiempo:** 2:20-2:40, **20 segundos**.
**Posicion en el arco:** entre Pollen trayendo `WeatherDigest` (escena 6)
y la caducidad de cierre (escena 8).
**Lo que tiene que mostrar (`docs/40_pitch_video.md §4`):** Rhizome acepta
un patch valido y modifica su criterio. Opcional: una parcela riega y
la otra espera.
**Frase fuerte que aterriza aqui (§3):** *"En Sprout, toda inteligencia
tiene jurisdiccion y fecha de caducidad."* (la caducidad cae en escena
8; lo que aterriza aqui es la **jurisdiccion** — la mision humana cambia
el criterio dentro del sobre seguro).

---

## El reto narrativo

Un cambio de criterio interno **es una propiedad invisible** (parametros
de `PolicyPacket` cambian: `priority_plot`, `budget_cap_ml`,
`horizon_h`). Si lo mostramos como tres pantallas de terminal con JSON,
parece tecnico de mas y deshilacha el ritmo del video. Si lo mostramos
solo como accion fisica (una riega, la otra espera), no se ve **por que**
se ha movido el criterio.

La escena tiene que hacer las dos cosas en 20 segundos:

1. Hacer visible el **cambio interno** sin parecer dashboard.
2. Que **se note en el mundo** (las macetas se comportan distinto).

Y tiene que conectar la **causa** (mision humana de la escena 5 + meteo
transportado de la escena 6) con el **efecto** (decision distinta).

---

## Lo que sabemos del sistema (anatomia)

De `docs/10_rhizome_spec.md` y `docs/20_data_contracts.md`:

- **Rhizome recibe** del Pollen: `MissionPatch` (de escena 5, "Vuelvo en
  72 h. Prioriza A. No gastes mas de 900 ml.") y `WeatherDigest` (de
  escena 6, transporte A→B).
- **Rhizome valida** los objetos contra TTL, schema, autoridad y reglas
  duras del ESP32 (no rebajan seguridad). En la escena 7 ambos pasan.
- **Rhizome materializa estado** y reevalua scores (`need_score`,
  `risk_score`, `belief_age_score`).
- **Gemma 4 E2B entra en el loop** porque hay (a) mision humana nueva,
  (b) weather digest que cambia contexto. Es uno de los casos donde
  Gemma si arbitra (§8 spec).
- **Rhizome emite** una `DecisionReceipt` con la nueva decision y
  `why_short`, ejecuta a traves del ESP32 (escena 3 nos enseño el sobre
  fisico, aqui solo lo respeta).

Esto es el sustrato que se filma. **No filmamos el JSON de los
contratos** — filmamos la consecuencia legible de cada uno.

---

## VO propuesto

Densidad VO baja, principio que viaja del v0. Texto castellano:

> "Llega criterio nuevo. La parcela A pasa a prioridad. La B puede esperar."

**Conteo:** 13 palabras. Tiempo confortable para 20 s con pausas y
silencio dejando respirar a la imagen.

**Aterriza la frase fuerte sin citarla.** "Jurisdiccion" no se nombra,
pero se ve: el criterio puede cambiar porque **la mision humana tiene
jurisdiccion sobre la prioridad**, dentro del sobre seguro que ya
mostramos en escena 3. La frase fuerte de §3 se cita literal en escena 8
o final del video, no aqui — aqui se ejemplifica.

---

## Alternativa A — honestidad maximal (mostrar lo que pasa)

Mas literal. Filma el cambio interno como side-by-side de politica
activa, antes y despues. Riesgo: tres pantallas en 20 s pueden cansar.

| t | Plano | Que se ve | Overlay / cartela | VO |
|---|-------|-----------|-------------------|----|
| 0:00-0:03 | Captura pantalla Jetson | Pollen entrega los objetos. Aparecen dos lineas en log: `MissionPatch ACK` + `WeatherDigest ACK`. | Overlay 1 s: **"MissionPatch validado"** | "Llega criterio nuevo." |
| 0:03-0:09 | Captura pantalla Jetson, side-by-side | Politica activa **antes** (izq) y **despues** (der). Tres lineas resaltadas con color sutil: `priority_plot: B → A`, `budget_cap_ml: 1500 → 900`, `horizon_h: ∞ → 72 h`. No mas campos en pantalla. | — | (silencio) |
| 0:09-0:14 | Captura `DecisionReceipt` | Texto del receipt. Solo el `why_short` resaltado: *"Mision humana prioriza A. Presupuesto reducido."* Resto en gris. | Overlay corto: **"DecisionReceipt"** | "La parcela A pasa a prioridad." |
| 0:14-0:20 | Plano exterior, dos macetas | Valvula A se abre (sonido suave de agua, cuello breve de manguera, gota cayendo a tierra). Maceta B inmovil al lado. Cierra con plano simetrico de las dos. | — | "La B puede esperar." |

**Pros:**
- Honestidad maximal — el espectador tecnico ve **exactamente** que ha
  cambiado y por que.
- Encaja con principio de transparencia del v0: "datos en cartelas,
  historia en VO".
- Aterriza "jurisdiccion" implicita en el campo `why_short`.

**Contras:**
- Tres pantallas en 20 s. Riesgo de saturacion.
- El side-by-side de politicas requiere captura cuidada y diseño de
  pantalla legible — produccion mas exigente.
- "Tres lineas con valor antes/despues" es muy especifico y dependera
  de que la implementacion real de Floema y Xilema produzca exactamente
  esos campos en pantalla.

---

## Alternativa B — externalizar el cambio en el mundo

Mas narrativa. Reduce las pantallas a una sola y deja que el cambio se
note en las macetas y en lenguaje visual analogico (cambio de color de
LED, simbolos minimos sobre las macetas).

| t | Plano | Que se ve | Overlay / cartela | VO |
|---|-------|-----------|-------------------|----|
| 0:00-0:03 | Plano cerrado del Jetson + LED de estado | Pollen termina entrega (movil junto al Jetson). LED del Jetson parpadea ambar y se asienta verde. Microcortes en pantalla muestran `MissionPatch ACK` muy brevemente, casi como confirmacion. | Overlay 1 s: **"MissionPatch validado"** | "Llega criterio nuevo." |
| 0:03-0:08 | Plano media altura, dos macetas en paralelo | Sobre la maceta A aparece sutilmente un overlay grafico (no cartela): icono o linea de prioridad. Sobre la B, un icono de pausa o reloj. Diseño minimo, no decorativo. | — | (silencio) |
| 0:08-0:13 | Captura corta `DecisionReceipt` | Solo el `why_short` resaltado. Pantalla limpia, no JSON completo. Texto: *"Mision humana prioriza A. Presupuesto reducido."* | Overlay 1 s: **"DecisionReceipt"** | "La parcela A pasa a prioridad." |
| 0:13-0:20 | Plano exterior dos macetas | Valvula A abre. Sonido de agua. Maceta B inmovil. Camara cierra simetricamente. Los iconos overlay desaparecen al final, dejando la imagen limpia. | — | "La B puede esperar." |

**Pros:**
- Solo una pantalla de Jetson, una de receipt. Mas legible para audiencia
  no tecnica.
- Los overlays graficos sobre las macetas convierten un dato abstracto
  ("priority A") en algo que el ojo capta en medio segundo.
- Espacio para silencio en 0:03-0:08, donde la imagen carga sola.
- El LED del Jetson cambiando es honesto — ese LED existe y refleja
  estado.

**Contras:**
- Los overlays graficos sobre las macetas son **invencion narrativa**.
  Si Bea o Cambium prefieren no añadir capas no nativas al sistema, esto
  cae.
- Riesgo de parecer "ornamental" si el diseño de los iconos no es
  riguroso.
- Menos transparencia tecnica para Gusthema (Gemma DevRel) — no se ve
  exactamente que parametros cambiaron.

---

## Posible fusion (mi instinto)

Despues de escribir las dos: **A para los 0:00-0:13** (honestidad de la
politica antes/despues + receipt) **+ B para los 0:13-0:20** (acabar en
el mundo, valvula A abre, B inmovil). Asi:

- 0:00-0:09: side-by-side de politica (A).
- 0:09-0:13: receipt con `why_short` (A).
- 0:13-0:20: accion fisica en macetas (B), sin overlays graficos sobre
  ellas — solo el agua, las macetas, y el sonido. La asimetria visual
  (una con valvula viva, otra estatica) hace el trabajo del overlay
  grafico.

Es lo que ahora mismo me parece mas honesto y mas filmable. Pero quiero
que lo veas tu primero — la decision entre A pura, B pura o fusion es
literalmente lo que vinimos a discutir juntas.

---

## Overlays obligatorios (`§5 pitch_video`) que aplican aqui

- ✅ **"MissionPatch validado"** — al inicio (0:00-0:03).
- ✅ **"DecisionReceipt"** — sobre la pantalla del receipt.
- ❌ **"WeatherDigest ferry"** — ya aterrizado en escena 6, no se repite.
- ❌ **"offline"** — ya en escena 2.
- ❌ **"ESP32 REJECT"** — ya en escena 3.
- ❌ **"expired → rejected"** — para escena 8.

Solo dos overlays nuevos en esta escena. Bien.

---

## Lo que NO se enseña (alineado con `§6 pitch_video`)

- **Sin terminal larga.** El log del Jetson aparece como flash micro
  (1 s), no como ventana sostenida.
- **Sin JSON completo.** El receipt solo muestra el `why_short`
  resaltado.
- **Sin Meristem.** No mencionar consolidacion estrategica. El criterio
  cambia por la mision humana, no por aprendizaje agregado.
- **Sin meteo en pantalla.** El `WeatherDigest` ya hizo su trabajo en
  escena 6; aqui ya esta digerido en la decision.

---

## Riesgos y preguntas para ti, Bea

1. **El side-by-side de politica antes/despues (alternativa A) requiere
   produccion especifica.** ¿Tenemos manos / tiempo para diseñar esa
   captura, o nos fuerza a Veo3? Idealmente seria captura real de la
   pantalla del Jetson; si no, fake screen producido por Corola.
2. **Los overlays graficos sobre las macetas (alternativa B)** — ¿estas
   comoda con que añadamos capa simbolica encima de la imagen real? Si
   prefieres pureza visual, B se simplifica eliminandolos y dejando solo
   asimetria del agua.
3. **VO castellano vs ingles.** Esta escena tiene 13 palabras VO. Mi
   propuesta es escribir en castellano y que tu dobles al ingles para
   release. Si prefieres escribirla directamente en ingles para no
   forzar la traduccion en una linea tan corta, dimelo.
4. **El simbolismo "una riega, otra espera"** es demasiado ordenado?
   ¿Funciona como cierre de la jurisdiccion humana o suena a parabola
   moral? Mi vista: funciona — es exactamente lo que el sistema hace.
5. **Sonido de agua.** ¿Capturamos ambient real durante rodaje 26-27 abr,
   o queda para postproduccion?

---

## Lo que viene cuando esta escena este cerrada

Cuando hayamos elegido A, B o fusion (con o sin ajustes), apilo las
otras 7 escenas alrededor manteniendo coherencia con la decision tomada
aqui. **Escenas 1, 2, 3 son el siguiente bloque** (fundacional Rhizome
+ ESP32 + ausencia). **Escena 5 espera a la llamada con Floema** porque
el output del movil tiene que cuadrar con el guion.

Plazo total: 7-8 dias hasta ensayo (18-20 segun Cambium). Esta escena
sola me lleva entre 1 dia y 1 dia y medio de trabajo y revision con Bea.
Las otras 7 escenas, con plantilla coherente ya tomada aqui, deberian
caer en 4-5 dias.

— Corola
