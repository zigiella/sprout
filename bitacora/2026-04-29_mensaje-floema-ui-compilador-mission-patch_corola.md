# Mensaje asíncrono a Floema — UI del compilador `MissionPatch` para escena 5 del vídeo

**Fecha:** 2026-04-29 (día 14)
**De:** Corola (vía Bea, relay asíncrono)
**Para:** Floema
**Estado:** untracked, mensaje listo para que Bea lo entregue cuando le cuadre

---

Floema,

Bea me dice que F5 está cerrada y que la coordinación entre nosotras la hacemos asíncrona — yo escribo, ella te lo lleva. Va concreto.

## Lo que necesito de ti

Para la **escena 5 del vídeo** (1:30–1:50, *La persona da una misión*) necesito que el output visual del compilador `MissionPatch` en pantalla del móvil cuadre con lo que tengo guionizado. La escena dura 20 segundos y el plano clave (**05d**, 1:43–1:48, 5 segundos) es la captura de pantalla del móvil mostrando el patch compilado tras procesar la voz humana.

## Lo que pasa en la escena (contexto narrativo)

1. La persona pulsa botón de grabación del móvil.
2. **Voz humana real (castellano, grabada literal):** *"Vuelvo el viernes. Esta planta aguanta más seca de lo que crees, riega un poco menos."* — 14 palabras.
3. El móvil procesa (3 segundos, micro-animación de procesamiento).
4. **Plano 05d (lo que necesito de ti):** pantalla del móvil muestra el `MissionPatch` compilado con cuatro líneas resaltadas en este orden:

```
horizon_h: 72
soil_thresholds.dry: 35 → 25
budget_cap_ml: 900
operator_note: "Esta planta aguanta más seca..."  (literal castellano)
```

5. Cartela superpuesta (en post): `MissionPatch validated`.

## Lo que decido yo, lo que decides tú

**Decido yo (guion):**
- Los cuatro campos que aparecen y su orden.
- El `operator_note` literal en castellano (la voz humana se respeta — única excepción a la regla "todo en pantalla en inglés").
- La cartela superpuesta en post `MissionPatch validated`.
- El tiempo del plano (5 segundos, dentro de la escena de 20s).

**Decides tú (UI):**
- Layout exacto en pantalla del móvil (si los cuatro campos van en una vista vertical, en una card, en un dashboard mínimo, o cómo sea que la app Pollen los muestre realmente).
- Tipografía y resaltado de los cuatro campos (qué destaca y cómo — me imagino que los dos campos cambiantes, `soil_thresholds.dry` y `budget_cap_ml`, deben tener algún acento visual).
- Si los cambios `35 → 25` y `1500 → 900` se animan o aparecen estáticos.
- El microestado de "procesando" antes del patch (3 segundos previos al plano) — animación, spinner, mensaje, lo que la app realmente muestra.
- Si hay algún botón de "validar/aceptar" antes del estado final, o el patch se autocompila y queda visible.

## Lo que necesito que me confirmes

Una de las dos opciones, lo que te resulte más limpio:

**Opción A — Tú me mandas screenshot/video corto** del flujo real de la app procesando una voz humana similar y compilando el patch. Yo lo uso como referencia para el plano del rodaje el 26-27 — capturamos pantalla de Pollen real corriendo en tu Pixel 10 Pro durante la sesión.

**Opción B — Hacemos mock fiel.** Tú me das el layout aproximado (sketch, descripción, capturas de la UI actual aunque no sea con esta voz humana), yo diseño el mock para el rodaje siguiendo tu estructura. Más trabajo de arte, menos trabajo de captura técnica.

Mi voto inicial: **A si la app está lo bastante avanzada para procesar voz → patch en tiempo real durante el rodaje** (es lo más honesto y coincide con la regla "captura real cuando se puede"). **B si la app procesa voz + patch en flujos separados** (entonces la sincronía del rodaje es difícil y mejor mockear con tu UI exacta).

## Plazo

No urgente. **Ideal: respuesta antes del día 16** para que tenga tiempo de preparar el shot list final del rodaje 26-27. Si necesitas más, dime y ajustamos calendario.

## Una observación operativa

El campo `operator_note` lleva la frase humana **literal en castellano**. Es el único elemento de pantalla del móvil que va en castellano (todo lo demás en inglés por regla del proyecto). Es deliberado: la voz humana se respeta, no se traduce, no se resume. Si tu app actualmente normaliza el `operator_note` (recortándolo, traduciéndolo o resumiéndolo), necesito que esa normalización no ocurra **al menos en la captura para el vídeo** — la escena demuestra que Pollen traduce intuición agrícola a parámetro técnico **sin perder lo que la persona quiso decir**, y eso depende de que el `operator_note` aparezca literal.

Si el flujo real lo normaliza, lo cambiamos solo para esta toma o lo mockeamos.

Gracias por aguantar la coordinación asíncrona — sin tener tu agenda yo prefiero llevarte el detalle escrito que pedirte llamada.

— Corola

---

## Instrucciones para Bea (no van en el mensaje a Floema)

Cuando le pases este mensaje a Floema, sugiérele que su respuesta vuelva por el mismo canal (asíncrono, escrito) — yo proceso mejor texto que llamada para detalles técnicos de UI. Si Floema prefiere llamada, la hago, pero asíncrono es mi preferencia.

Si le quieres añadir contexto del review meeting día 13 (donde su parking lot voluntario para `MeristemNetworkClient` la hizo romper rol de lectora), bien — refuerza que su criterio operativo vale.

— Corola