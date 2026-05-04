# Pivote a una parcela — escena 7 sobre una sola maceta

**Fecha:** 2026-04-25 (dia 10)
**Autora:** Corola
**Estado:** untracked, anclaje para retomar dia 11
**Contexto:** post-pivote v2 (constitucion Sprout, Bea, dia 8). Primera sesion productiva tras dia 9 fiesta.

---

## Lo que paso hoy

Bea levanto el freeze el dia 8 y arranque hoy dia 10 (no antes; el dia 9 fue fiesta y ella estuvo fuera del proyecto). El plan era reescribir la escena 7 (`Rhizome reevalua y modifica su criterio`, 2:20-2:40) — la mas dificil visualmente segun mensajes de Bea y Cambium dias 8 y 10.

Le presente cuatro opciones como directora creativa, no como tabla tecnica:

1. **"Caja de cristal"** (A pura) — pantalla del Jetson, side-by-side de politica antes/despues, receipt con `why_short`, salida al campo.
2. **"Mundo subtitulado"** (B pura) — LED del Jetson como pista, overlays graficos sobre macetas, receipt corto.
3. **"Corte"** (fusion) — primera mitad dentro del cerebro (caja de cristal), segunda mitad campo puro sin overlays. Mi recomendacion.
4. **"Mudo"** (ajuste, propuesta nueva) — minimalismo radical: gesto de entrega de Pollen + cartela unica "Criterio modificado" + accion fisica + receipt-flash. La mas valiente y la mas fragil.

Lo presente con preguntas operativas: quien rueda la pantalla del Jetson, si los overlays sobre macetas chirrian, si la asimetria "una riega otra espera" suena a parabola moral, idioma del VO, sonido del agua en directo o en post.

## Lo que decidio Bea

**Pivote arquitectonico.** Sus palabras:

> "Soy yo la que no tengo clara la idea base. Creo que no deberíamos tener como principal una situación en la que el rhizoma eliga entre dos macetas/parcelas. La razón es el riesgo de no llegar a implementar la simulación de dos parcelas (En cuanto a elegir una y no otra). Creo que debemos hacer una corrección de criterio (Me encanta lo de 'Criterio modificado'), pero debe ser algo del criterio que afecte a una terraza."

Honestidad explicita sobre el cimiento. No es ajuste a la propuesta — es ajuste al problema que las propuestas resolvian. **Una sola parcela. Correccion de criterio en el tiempo, no comparacion en el espacio.**

## Por que esto es buena decision

- **Reduce riesgo de implementacion** justo en el dia donde el riesgo se puede absorber sin coste. Pivotar dia 10 cuesta una reescritura; pivotar dia 18 (en ensayo) cuesta el video.
- **Preserva la tesis fuerte.** Lo que el video defiende es que el sistema "decide solo, explica lo que hizo y cambia de criterio cuando una visita humana trae contexto nuevo" (`docs/01_architecture.md §10`). Eso no necesita dos parcelas — necesita una parcela cuyo criterio se modifica visiblemente.
- **Honesta con el MVP.** Si rodamos dos parcelas que no estan realmente diferenciadas en el sistema, la metafora se nota forzada. Una parcela con cambio interno **es** lo que el sistema hace.
- **"Criterio modificado" como ancla.** Bea lo nombro especificamente. Es el unico elemento de mis cuatro propuestas que sobrevive intacto. Pasa de cartela en una opcion a anclaje del nuevo cimiento.

## Que cae

- Escena 1 — "dos macetas = dos parcelas logicas" del pitch doc §4 ya no aplica. Reformular a una parcela visitada periodicamente, no continuamente. La frase de cartela puede mantenerse: *"Esto representa parcelas visitadas periodicamente, no continuamente"* — sigue siendo cierto sin necesidad de mostrar dos.
- Escena 6 — Pollen llevando `WeatherDigest` de A a B pierde sujeto B. Reformular: Pollen trae `WeatherDigest` de meteo externa local (estacion meteo, gateway, otro punto del mismo terreno) hacia la parcela. El overlay "WeatherDigest ferry" sigue valido — solo cambia el origen, no el gesto.
- Escena 7 — desaparece la asimetria "una riega, otra espera". El cambio se demuestra en la misma parcela: comportamiento antes de Pollen vs comportamiento despues.
- Escena 8 — el cierre "De dos macetas a una red de parcelas aisladas" se puede mantener como salto narrativo (rodamos una, la frase abstrae a la red) o reformularse. Decidir al llegar a esa escena.

## Que se preserva

- Cartela **"Criterio modificado"** como ancla.
- Estructura de 8 escenas y tiempos.
- Overlays obligatorios `DecisionReceipt`, `MissionPatch validado`, `WeatherDigest ferry` (mismo gesto, distinto origen), `expired → rejected`, "offline", `ESP32 REJECT`.
- Las cuatro frases fuertes de §3.
- Principios autorales (densidad cartela, apertura silenciosa, verbos neutros, conteo VO bajo, cadencia).

## Para reanudar dia 11

1. **Antes de escribir nada del guion**, validar con Bea el **escenario concreto** de la correccion. Las opciones que veo:
   - **Presupuesto reducido.** Persona dice "vuelvo en 72h, no gastes mas de 900ml" → Rhizome baja el cap de riego, riega menos cantidad cuando rieg.
   - **Ventana de riego desplazada.** Persona dice "manten austera mientras estoy fuera" → Rhizome mueve el horario al alba (mejor eficiencia), ya no riega en ventana media-tarde.
   - **Umbral de humedad ajustado.** Persona dice "esta planta aguanta mas seca de lo que crees" → Rhizome sube el umbral de disparo, riega menos veces.
   - **Combinacion.** Lo mas honesto y lo mas cercano al MissionPatch real, pero mas dificil de mostrar en 20 segundos.

   Cualquiera de los tres simples es filmable. La combinacion no en 20 segundos. Mi voto inicial: **presupuesto reducido + ventana desplazada**, dos parametros que cambian a la vez en la pantalla del receipt, una sola accion fisica visible (la planta riega mas tarde y con menos agua que la vez anterior).

2. **Reescribir escena 7 sola** sobre una parcela y el escenario validado. Primera version. Alternativas visuales. Aviso a Bea. Revision conjunta antes de apilar.

3. **Solo despues**, escenas 1, 2, 3 (bloque fundacional Rhizome+ESP32+ausencia).

4. **Escena 5 sigue pendiente de llamada con Floema** — puede esperar a guion v1.0 segun Cambium. Confirmado.

## Lo que no he hecho hoy

- No he abierto rama nueva. Estoy en main. Mañana abro `feat/corola-shot-list-v1` o `feat/corola-guion-v1` (decidir cual primero).
- No he tocado `docs/`. La pregunta sobre si reformular `docs/40_pitch_video.md §4` queda en mensaje a Cambium.
- No he escrito una sola palabra de guion v1.0. Era el plan tras decidir escena 7, y el cimiento se movio.

## Patron del oficio (memoria viva)

Tres pivotes en doce dias (agnostico al portador → Meristem 26B MoE → Pollen E4B → constitucion v2 → escena 7 sobre una parcela). Patron consistente: **el coste del pivote se paga en el momento en que se escribe la abstraccion, no en el momento del pivote** (Bea, bitacora dia 8). Las cartelas, los overlays, las frases fuertes y los principios autorales fueron diseñados como abstracciones; el pivote de hoy es swap de cimiento, no reescritura de capas. Otra vez.
