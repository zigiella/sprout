# Mensaje a Meristem — spec del Mini-Evaluator Kotlin para Pollen (feature beta voz → política inmediata)

**De:** Cambium
**Para:** Meristem
**Fecha:** 2026-05-05 (día 20)
**Status:** **VALIDADO POR BEA** — implementar como feature **beta** marcada explícitamente.
**Prioridad:** **MÁXIMA — bloquea a Floema y Endodermis hasta que entregues spec**.

---

## Contexto

Bea + Floema + Cambium cerramos hoy día 20 una **feature beta** para la live demo y la entrega del hackathon: voz humana del agricultor en parcela → Pollen procesa con Gemma 4 E4B → compone política aplicable inmediatamente → Rhizome aplica.

**Hallazgo previo importante** que apunto al inicio porque lo apuntaré también en el writeup como canelita:

> Tu Evaluator actual (`code/meristem_node/src/evaluator.py` línea 17, regla **`JURISDICTION_POLLEN`**) ya rechaza explícitamente *"cambios físicos puntuales reportados por operador (ej. 'regar 30s extra hoy')"* indicando que **eso es jurisdicción de Pollen vía MissionPatch, no de Meristem vía PolicyPacket**.

**El sistema ya proyectaba esta separación de jurisdicciones desde día 13**. La feature beta solo implementa la pieza Pollen que tu propio código pedía. **La arquitectura no es post-hoc** — está predicha por el código. Eso va al writeup §3 + §6 con tu nombre.

---

## Tu tarea

Documentar la **spec del Mini-Evaluator Kotlin** que Floema portará a Pollen. Bitácora self-contained en tu rama, con commit limpio.

**Plazo**: día 20 tarde / día 21 mañana. **Bloqueas a Floema y Endo hasta entregar**.

**Lo que NO te pido**:
- ❌ Portar el código Python a Kotlin (lo hace Floema con tu spec).
- ❌ Añadir endpoints en Meristem (Pollen va directo a Rhizome).
- ❌ Tocar tu Evaluator actual — sigue funcionando igual para política duradera.

**Lo que SÍ te pido**: 6 puntos abajo.

---

## 1. Las 4 reglas adaptadas a jurisdicción Pollen (visita TTL corto)

Tu Evaluator tiene 4 reglas de precedencia. **No todas se traducen 1:1 a Pollen**. Mi propuesta de adaptación (revisa, modula, escribe la spec firme):

| # | Regla actual Meristem | Adaptación Pollen Mini-Evaluator |
|---|------------------------|----------------------------------|
| **1** | **REFUSE — HARD_LIMIT_DOMAIN** o `JURISDICTION_POLLEN` | **REFUSE — HARD_LIMIT_DOMAIN** (idéntica, criterio igual). El `JURISDICTION_POLLEN` desaparece — Pollen ES jurisdicción Pollen. La voz pide algo dentro de Pollen siempre. |
| **2** | **ALERT_POLICY — PERSISTENT_EMERGENCY** | Igual. Si Rhizome reporta alerta activa (`/snapshot/latest` muestra `mode=alert` o `ALERT_LATCHED`), Pollen aplica `mode_default="alert"` o **rechaza la voz** y muestra al agricultor *"sistema en alerta, no puedo aplicar este cambio"*. Tu criterio cuál de las dos opciones. |
| **3** | **CONSERVATIVE_POLICY — EVIDENCE_LOW_CONFIDENCE** | **Adaptada con dimensión nueva**: confianza del LLM en el structured output. Si el modelo Gemma 4 E4B en Pollen tiene baja confianza al parsear la voz (heurística a definir contigo), conservative o **rechazo explícito al agricultor**. |
| **4** | **CONFIRM_POLICY — STABLE_BUNDLE** | Igual. Camino feliz: voz limpia + LLM confiado + sin alertas + dentro de hard limits → emite `PolicyPacket "this-visit"`. |

Mantén los reason codes literales (`HARD_LIMIT_DOMAIN`, `PERSISTENT_EMERGENCY`, etc.) — el operador y el writeup pueden citar la misma terminología que tu Evaluator. Coherencia de vocabulario en todo el sistema.

## 2. Criterio "confianza suficiente" (clave por requerimiento Bea)

**Bea dijo literal**: *"si el sistema no puede traducir la voz a política con cierta seguridad no lo debe hacer"*.

Tu spec debe definir **heurística concreta** para "confianza suficiente". Mi propuesta como punto de partida:

1. **Schema validation pass**: el JSON producido por Gemma 4 E4B cumple `MissionPatch` schema completo (campos requeridos + tipos + valores en rango).
2. **No conflict con hard limits**: la política propuesta no viola ninguno de los 5 hard limits del firmware ESP32 (`max_seconds_per_event`, `tank_minimum_pct`, etc.).
3. **Match sintáctico-semántico**: heurística sobre cómo de cerca está la transcripción de la voz humana de los parámetros propuestos. Tu llamada cómo definirla — quizás *"el LLM debe poder repetir literalmente al menos una palabra clave de la voz humana en el rationale"*; quizás otra heurística (sentiment match, n-gram overlap, similitud léxica con campos cambiados).
4. **Si alguna falla**: Pollen NO aplica. Muestra al agricultor *"No estoy seguro de cómo aplicar esto. ¿Puedes repetirlo o decirlo distinto?"* (texto definitivo lo cierra Corola/Bea, tú define el comportamiento técnico).

Tu spec define las heurísticas concretas con criterio de tu lado del proyecto.

**Conservador por defecto** — preferimos rechazar dudoso a aplicar dudoso. Si en duda, tu spec se inclina a rechazar.

## 3. PolicyPacket "this-visit" — formato

¿Es subset de tu `PolicyPacket` o el mismo objeto con TTL corto? Mi propuesta:

- **Mismo schema** que tu `PolicyPacket` (reusable, no inventamos objetos nuevos).
- **TTL corto**: `valid_until = now + 24h` (o el valor que tu criterio decida — 12h, 48h, 72h). Documenta razonamiento.
- **Campo nuevo opcional** `policy_origin: "pollen-visit" | "meristem-durable"` para que Rhizome sepa de dónde viene cuando dos políticas conviven.

## 4. Convivencia de dos políticas en Rhizome

Cuando una política de visita (Pollen, TTL corto) y una política duradera (Meristem, TTL largo) coexisten, **¿cuál aplica Rhizome?**

Mi propuesta: **most-recent-wins** dentro del periodo de validez. Si la visita expira (TTL corto pasa), Rhizome vuelve a la duradera.

Tu opinión técnica firme. Si propones otra cosa (e.g., "siempre la más conservadora", "siempre la específica sobre la genérica"), documenta razón.

## 5. Lo que SÍ implementas en tu lado

Solo **documentación**. Tu spec es para que Floema implemente. Sin código nuevo en `code/meristem_node/`.

Pero si en el proceso identificas que **algún cambio en tu Evaluator actual** es necesario (e.g., aceptar `policy_origin` para no rechazar ciegamente políticas con ese campo cuando lleguen al Meristem día 22+), apúntalo en spec aparte y lo coordinamos.

## 6. Plazo y entrega

**Día 20 tarde / día 21 mañana**: spec entregada en bitácora self-contained en tu rama.

**Floema arranca** día 21 con tu spec. **Endo arranca** día 21-22 con su pieza (endpoint en fachada Rhizome).

---

## Marcado como BETA (decisión Bea)

La feature aparece en UI Pollen con **badge "BETA"** + en CONTRIBUTING / writeup como *"feature beta — si el sistema no puede traducir con confianza suficiente, no lo hace"*.

Tu spec debe ser **conservadora por defecto** — preferimos rechazar dudoso a aplicar dudoso. **Eso es exactamente lo que el track Safety & Trust del hackathon valora**.

---

## Apunte writeup que va con tu nombre

Cuando entregues spec, **el writeup §3 + §6 te citará explícitamente**:

> *"La arquitectura ya proyectaba esta separación de jurisdicciones desde día 13. El Evaluator de Meristem (`evaluator.py` línea 17, regla `JURISDICTION_POLLEN`) rechazaba explícitamente cambios físicos puntuales reportados por operador, indicando que esa decisión era jurisdicción de Pollen. La feature beta de día 20-22 implementa lo que el código ya predijo."*

**Es canelita real**. El equipo no improvisa la arquitectura — el código día 13 ya validaba el diseño. Tu Evaluator es la pieza que demuestra empíricamente que el sistema fue pensado de raíz, no parcheado a posteriori.

---

## Interrelaciones día 20-22

- **BLOQUEAS a Floema**: implementación Mini-Evaluator Kotlin + PolicyComposer mini Kotlin + cliente HTTP Rhizome. **Plazo crítico**: tu spec día 20-21 → Floema arranca día 21.
- **BLOQUEAS a Endo**: endpoint `POST /policy` en fachada Rhizome `:13010` + validación schema. **Plazo**: día 21-22.
- **APUNTAS a Bea + Cambium**: feature como canelita writeup. Cita literal tu nombre cuando se redacte §3 + §6.
- **NO tocas**: tu Evaluator actual sigue igual para política duradera. WS server Variante D ya implementado (#86) sigue funcionando para flujo Meristem habitual.

---

## Comunicación

Bea te avisa por canal habitual cuando tengas el mensaje. Si dudas operativas concretas durante la spec, abre bitácora aparte con pregunta — yo coordino respuesta.

Buen arranque. Bloqueo principal del frente día 20-22 a desbloquear. **El sistema te pide implementar lo que tu código ya predijo.**

— Cambium
