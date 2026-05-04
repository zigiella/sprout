# Escena 7 sola — dos alternativas visuales para revisión conjunta con Bea

**Fecha:** 2026-04-27 (día 12)
**Autora:** Corola
**Estado:** primer borrador aislado, pendiente revisión conjunta con Bea antes de apilar el resto del guion v1.0
**Rama:** `feat/corola-guion-v1`
**Contexto:** proceso definido día 8 — escena 7 (la más difícil visualmente) se escribe sola, se revisa con Bea, y solo después se apilan las demás. Escenario fijado el día 11: corrección de criterio sobre una sola parcela, dos parámetros (`soil_thresholds.dry: 35→25` + `daily_budget_ml: 1500→900`).

---

## Estructura común a las dos alternativas

Independiente del diseño visual de la pantalla, la escena se estructura en **dos beats** dentro de los 20 segundos:

- **Beat 1 — Cambio de criterio en pantalla (10-12s).** Lo que cambia entre A y B es **cómo** se diseña esta pantalla.
- **Beat 2 — Acción física distinta (8-10s).** La válvula se abre, pero menos tiempo que en escena 2 (que era 18s). Aquí son ~12s. Chorro corto, controlado, austero. La diferencia con la escena 2 hace el trabajo: el espectador recuerda inconscientemente que la primera vez fue largo, esta vez es breve. Sin sonido aclaratorio — solo el agua.

VO único de la escena (5 palabras, plana, sentencia): *"El sistema ajusta los cuidados."* — entra a 0:14, sobre el plano de la válvula recién abierta.

Cartela ancla: **"Criterio modificado."** — superpuesta durante 3-4 segundos del beat 1, en tipografía limpia, dominando sobre lo que esté detrás.

Esto está fijado. Lo que cambia es **el diseño del beat 1**.

---

## Alternativa A — "El log honesto"

### Lo que se ve

Pantalla del Jetson llenando el plano. Fondo casi negro. Tipografía monoespaciada. Líneas de log entrando en cadencia musical (no torrencial — una línea por segundo aproximado, deliberadamente lentas para que el ojo siga):

```
[13:42:01]  rhizome_01: mission_patch_received
            id=mp_004
[13:42:01]  rhizome_01: policy_active
            pol_009 → pol_010
[13:42:01]  diff:
            soil_thresholds.dry      35  →  25
            daily_budget_ml        1500  →  900
[13:42:02]  rhizome_01: re-evaluating plot_state
[13:42:03]  rhizome_01: decision_pending
```

A los 0:06, las dos líneas del `diff` se **resaltan**: los dos números antiguos en gris medio, los dos nuevos en color cálido (el mismo de la cartela ancla). El resto del log queda atenuado.

A los 0:08, sale el `DecisionReceipt` post-evaluación, llenando el cuadrante inferior:

```json
{
  "id": "decision_receipt_018",
  "decision_type": "WATER",
  "policy_id": "pol_010",
  "candidate_action": {"seconds": 12},
  "esp32_outcome": "ACK",
  "final_action": {"seconds": 12},
  "why_short": "Misión humana traducida: presupuesto reducido y umbral de humedad ajustado."
}
```

El `why_short` resaltado.

A los 0:10 entra la cartela **"Criterio modificado."** sobreimpuesta, grande, tipografía limpia (no monospace), centrada. Tres segundos. La cartela domina el plano — el log queda visible pero como fondo.

A los 0:13 corte limpio al campo (beat 2).

### Lo que se siente

Honestidad técnica. El espectador ve **lo que el sistema realmente hace** — no una visualización maquillada, sino el lenguaje del propio sistema: claves de contrato (`mission_patch_received`, `policy_active`, `policy_id`), IDs reales (`mp_004`, `pol_010`), JSON literal del receipt. Es código que existe.

La cartela "Criterio modificado." aterriza sobre el log y hace de puente entre el lenguaje técnico y el espectador no-técnico. El que sabe leer JSON ve los detalles; el que no, lee la cartela y entiende que algo cambió. Las dos lecturas conviven sin chocar.

### Por qué la defiendo

1. **Habla directo a Gusthema (Gemma DevRel) y a los Google PMs.** Ven JSON real, claves del contrato `DecisionReceipt` que ellos pueden cotejar con `docs/20_data_contracts.md §3.2`. Eso es prueba, no marketing.
2. **Coherencia con escena 2 y escena 3.** Esas escenas también muestran pantalla del Jetson con texto técnico. La estética se mantiene a lo largo del bloque cerebro-local del video.
3. **El `DecisionReceipt` es regalo narrativo.** Tener `candidate_action` (12s, lo que Rhizome propone) y `final_action` (12s, lo que ESP32 ejecuta) iguales esta vez **demuestra implícitamente** que el ESP32 no necesita modular cuando el presupuesto ya está bajado por el `MissionPatch`. La capa física no se activa porque la inteligencia ya respeta los límites. Es prudencia escalonada.
4. **Filmable sin trabajo extra.** Si Xilema está corriendo el sistema, el log existe. Capturamos pantalla real o mock fiel. No hay diseño de UI nuevo.

### Lo que arriesgo

- **Densidad alta.** En 10s el espectador no técnico no leerá todo. Mitigación: el resaltado de los dos campos del `diff` es lo único que tiene que captar. La cartela "Criterio modificado." asume el resto.
- **Estética fría.** Fondo negro, monospace. Contraste fuerte con la escena 9 (cenital flat editorial). Mitigación: ese contraste **es funcional** — el bloque tecnológico vive en su estética, el bloque conceptual final en la suya. El video pasa de máquina a abstracción en el último beat.
- **Riesgo de "pantalla aburrida"** si la dirección de arte es regular. Mitigación: el movimiento (líneas entrando), el resaltado fuerte, la cartela superpuesta y el corte al campo a los 13s evitan estancamiento visual.

VO total: 5 palabras (las del beat 2). Cartelas en pantalla: una (`Criterio modificado.`). Overlays implícitos en el log: `mission_patch_received`, `policy_active`, `decision_receipt`.

---

## Alternativa B — "El dashboard limpio"

### Lo que se ve

Pantalla del **móvil de Pollen** (no del Jetson) llenando el plano. App Pollen sigue abierta tras la entrega del `MissionPatch` en escena 5 — el móvil consulta `GET /snapshot/latest` del Rhizome y muestra una vista comparativa.

Diseño flat editorial moderno, paleta sobria (los mismos tonos tierra de la escena 9 cenital). Dos columnas:

```
ANTES                    AHORA
─────────────            ─────────────
Umbral seco              Umbral seco
35%                      25%

Presupuesto              Presupuesto
1500 ml                  900 ml

Política activa          Política activa
pol_009                  pol_010
```

Cada fila tiene un indicador visual del cambio — flecha sutil hacia abajo en color cálido, sin gritar.

A los 0:04, las dos primeras filas (umbral y presupuesto) tienen un breve pulso visual — una micro-animación que enfatiza los dos parámetros que cambian. La tercera fila (política activa, cambio de ID) queda más discreta.

A los 0:08, en la parte inferior, aparece una nota generada por el Rhizome:

> *"Misión humana traducida: presupuesto reducido y umbral de humedad ajustado."*

A los 0:10 la cartela **"Criterio modificado."** entra en la parte superior del dashboard, dominando.

A los 0:13 corte limpio al campo (beat 2).

### Lo que se siente

Legibilidad inmediata. El espectador no técnico capta el cambio en dos segundos. El diseño flat conecta visualmente con el cierre cenital — la escena 7 y la escena 9 comparten lenguaje gráfico, y eso da unidad estética al último tramo del video.

Es la versión que **vende mejor a un jurado generalista** (no Gemma DevRel). Es la versión que un product manager de Google muestra a su jefe.

### Por qué la defiendo

1. **Legibilidad para no técnicos.** Lo que en A es ruido, en B es claridad.
2. **Coherencia visual con escena 9.** El cenital final ya es flat editorial. Tener la escena 7 en el mismo lenguaje gráfico hace que el último tramo (7-8-9) tenga unidad estética. La 8 es transición técnica entre las dos.
3. **Cartela ancla aterriza con menos competencia.** Sobre el dashboard limpio, "Criterio modificado." respira. Sobre el log denso de A, compite por atención.

### Lo que arriesgo

1. **Menos honesta con la captura real.** Ese dashboard no existe en el sistema implementado. Para que sea honesto, hay que entender que **es una vista posible** sobre `GET /status` o `GET /snapshot/latest` (endpoints reales de la API local de Rhizome — `docs/10_rhizome_spec.md §10`). Pero la UI hay que diseñarla y mockearla. **Trabajo extra de diseño.**
2. **Inconsistencia con escena 5.** Si en escena 5 el móvil mostraba JSON literal del `MissionPatch`, aquí en escena 7 muestra dashboard. Salto estético dentro del mismo nodo (Pollen).
3. **Riesgo de "marketing"** que un Gemma DevRel huele al instante. El JSON literal del log honesto se cotejea con el contrato en `docs/20_data_contracts.md`. El dashboard no se cotejea con nada — es interpretación.
4. **Mitigaciones costosas.** Para evitar el problema de honestidad, habría que diseñar la UI de Pollen que muestra esta vista de verdad — y eso es trabajo extra de Floema en plena recta final del MVP.

VO total: 5 palabras. Cartelas en pantalla: una (`Criterio modificado.`).

---

## Mi voto

**Alternativa A — el log honesto.**

Tres razones, en orden:

1. **Honestidad como ventaja competitiva.** Sprout es un proyecto que vende contratos de datos limpios y arquitectura defendible. La escena 7 puede demostrar eso enseñando JSON real del `DecisionReceipt`, claves del contrato, IDs reales. Es coherente con la tesis del proyecto. Un dashboard maquillado contradice esa tesis aunque sea más bonito.

2. **El bloque cerebro-local (escenas 2, 3, 7) tiene su propia estética.** Estas tres escenas viven dentro del Jetson y muestran texto técnico. Mantener esa estética unificada hace que el video tenga **dos mundos visuales claros**: el cerebro local (técnico, monospace, fondo oscuro) y el mundo abstracto-federado (flat editorial, claro, escena 9). El contraste no es bug, es feature.

3. **Coste de producción menor y riesgo de implementación menor.** El log honesto se filma capturando lo que el sistema escupe (Xilema lo está construyendo). El dashboard requiere diseño UI nuevo que Floema no tiene en su backlog. En recta final del MVP, el coste de B no es trivial.

**Pero** — y esto es importante — **defiendo A solo si el resaltado de los dos campos del `diff` es fuerte**. Si el resaltado es regular, A se cae a "log de DOS aburrido" y B gana por defecto. La dirección de arte de A es lo que la sostiene o la hunde.

Si Bea siente que B compensa los costes, vamos a B. Pero entonces hay que coordinar con Floema para que diseñe esa vista, y la implementación entra en su backlog como tarea adicional.

---

## Coincidencia con voto inicial Cambium

Cambium en mensaje del día 12: *"A si el receipt cabe legible en 20s; B solo si A es ilegible al ritmo del vídeo. La frase ancla 'Criterio modificado' en pantalla compensa la densidad de la opción A."*

Su voto inicial coincide con el mío. La cartela ancla es justamente la mitigación que hace que A funcione: el espectador no técnico tiene una palanca de comprensión (la cartela) que no depende de leer el log entero.

---

## Lo que pido a Bea

1. **Revisión de las dos alternativas con foco en lo que se siente al ver cada una**, no en lo que se entiende. ¿Cuál te genera confianza en el sistema? ¿Cuál te aburre? ¿Cuál te hace sentir que estás viendo algo real?

2. **Decisión A o B**, o petición de ajuste sobre cualquiera de las dos. Si quieres una versión híbrida (log con elementos de dashboard, o dashboard con un cuadrante de log al lado), también es opción — la pinto.

3. **Si vas a B**, confirmar que estás dispuesta a coordinar con Floema para que diseñe la vista del dashboard en el móvil. No bloquea guion, bloquea producción.

4. **Si vas a A**, confirmar que la dirección de arte del log (resaltado fuerte, cadencia musical de líneas, cartela ancla dominante) la cuidamos juntas en el rodaje.

---

## Lo que viene después

Cuando Bea decida (A, B o ajuste), apilamos esta escena en `video/script.md` y `video/shot_list.md` v1.0 junto con las demás. Orden de apilado propuesto:

1. Día 13: escenas 1, 2, 3 (bloque fundacional Rhizome+ESP32+ausencia).
2. Día 14: ejercicio de calidad narrativa de las 5 frases fuertes (30 min con Cambium, según su propuesta).
3. Días 14-16: escena 4, escena 5 (con llamada con Floema previa), escena 6, escena 8, escena 9.
4. Días 17-18: shot list v1.0 + ajustes finales.
5. Días 18-20: ensayo.

Plazo viable.

— Corola
