# Borrador escena 7 — Rhizome reevalua y modifica criterio

**Fecha:** 2026-04-25 (dia 10)
**Autora:** Corola
**Rama:** `feat/corola-escena-07-borrador`
**Estado:** PR draft a main para revision conjunta con Bea
**No cierra ningun issue por si solo.** Es entrega aislada para validar
la escena mas dificil del video antes de apilar las otras siete.

---

## Por que esta escena, primero, sola

Bea identifico la escena 7 como la mas susceptible de deshilachar el
ritmo del video si no se resuelve bien. Lo dijo en su mensaje de pivote
v2 dia 8: *"Es la escena mas dificil — como mostrar un cambio de
criterio interno en 20 segundos sin que parezca tecnico de mas. Cuando
tengas primer borrador, avisame y la miramos juntas antes de que se
apile."*

Mi propuesta dia 8 fue arrancar por aqui aislada. Bea no tuvo capacidad
de pasar dia 9 (fiesta) ni dia 10 hasta hoy. Lo entrego hoy.

**Logica del orden:** si la escena 7 condiciona el lenguaje visual del
resto (overlays sobre objeto fisico vs solo pantalla; densidad de cortes
internos; relacion entre pantalla de Jetson y plano exterior), tomar
esa decision aqui me ahorra tener que refactorizar las otras 7 escenas
si la cambiamos despues.

## Que se ha hecho

1. **Releido `docs/10_rhizome_spec.md` y `docs/20_data_contracts.md`**
   para conocer la anatomia exacta de lo que pasa internamente:
   `MissionPatch` recibido + `WeatherDigest` recibido → reglas de
   aceptacion (TTL, schema, autoridad, ESP32 envelope) → estado
   materializado se actualiza → Gemma 4 E2B arbitra (caso §8 mision
   humana nueva + weather digest cambia contexto) → emite nueva
   `DecisionReceipt` → ESP32 ejecuta.
2. **Escrito `video/escena_07_borrador.md`** con:
   - Reto narrativo articulado.
   - VO castellano propuesto (13 palabras).
   - **Dos alternativas visuales completas** (A honestidad maximal con
     side-by-side de politica antes/despues; B externalizada con LED
     del Jetson + overlays graficos sobre macetas).
   - **Una propuesta de fusion** (A en 0:00-0:13, B sin overlays
     graficos en 0:13-0:20).
   - Overlays obligatorios que aplican (solo dos: "MissionPatch
     validado" y "DecisionReceipt").
   - Lo que NO se enseña (sin terminal larga, sin JSON completo, sin
     Meristem, sin meteo en pantalla).
   - 5 preguntas concretas para Bea.

## Lo que NO se ha hecho (consciente)

- **No he tocado las otras 7 escenas.** Plan aislado, como prometi
  dia 8.
- **No he abierto `video/shot_list.md` ni `video/script.md` v1.0.**
  Escena 7 es entrega aparte para validacion. Cuando se cierre, la
  estructura de los dos ficheros principales arranca con la escena 7
  ya decidida.
- **No he generado prompts Veo3.** Ninguna alternativa lo requiere
  necesariamente. Si la alternativa A se queda como esta y produccion
  exige fake screens producidos por mi, lo discutimos.
- **No he aplicado naming Gemma de v2** (`Pollen E4B`, `Rhizome E2B`)
  en cartelas de esta escena, porque esta escena no muestra cartela
  stack — solo overlays funcionales. Las cartelas de stack Gemma
  apareceran en escenas 2 (Rhizome E2B), 4-5 (Pollen E4B) y/o creditos
  finales.
- **No he agendado la llamada con Floema.** Bea queda en agendarla; la
  llamada puede esperar a guion v1.0 segun Cambium dia 10.

## Decisiones de fondo de este borrador

1. **Cambio interno = mostrar la consecuencia legible, no el JSON.**
   El receipt aparece, pero solo el `why_short` se resalta. Tres
   parametros antes/despues, no diez. Lo demas en gris o fuera de
   plano.
2. **El mundo tiene que cerrar la escena.** En las dos alternativas,
   los ultimos 6-7 segundos son plano exterior con macetas y agua. El
   sistema cambia el criterio, pero la prueba de que cambio esta en
   la accion fisica, no en la pantalla.
3. **Una sola frase tesis aterrizada implicita.** "Toda inteligencia
   tiene jurisdiccion y fecha de caducidad" se ejemplifica aqui en la
   parte de jurisdiccion (la mision humana cambia el criterio). La
   caducidad la cierra escena 8. La frase literal solo aparece (si
   aparece) al final del video.
4. **Densidad VO baja.** 13 palabras castellano para 20 s. Principio
   del v0 que viaja al v1.0.

## Apertura para Bea

Las 5 preguntas del documento son las que necesito que decidamos
juntas:
- Capacidad de produccion para side-by-side de politica (A).
- Comodidad con overlays graficos sobre las macetas (B).
- Idioma de partida del VO.
- Simbolismo "una riega, otra espera" — funciona o suena a parabola.
- Sonido de agua — ambient real o postproduccion.

## Riesgos asumidos

- **Si Bea prefiere el sistema visual de B y rechaza overlays graficos
  sobre macetas**, B colapsa a "solo asimetria del agua". Sigue
  funcionando, pero pierde la capa simbolica.
- **Si Bea prefiere A pura**, hay que producir el side-by-side de
  pantalla con cuidado de diseño.
- **Si la fusion gana**, el corte 0:13 es donde la escena se juega
  ritmicamente — hay que asegurar transicion fluida pantalla → exterior.

## Plazo

Hoy es dia 10. Ensayo previsto dia 18-20. Esta escena con revision de
Bea: 1-1.5 dias. Apilado de las otras 7 con coherencia: 4-5 dias. Total
margen: 6-7 dias para llegar a guion + shot list estables antes de
ensayo. Si la revision de Bea de esta escena se demora 2 dias, el
margen se aprieta pero no rompe.

— Corola
