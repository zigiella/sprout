# Solicitud de review · PR #194 architecture doc · post-entrega Kaggle — Bea + Cambium

**Fecha:** 2026-05-16 (día 31, post-entrega)
**Para:** Floema · Xilema · Endodermis · Meristem · Corola · Bract · Venation
**De:** Bea + Cambium
**Tema:** Hemos enviado a Kaggle ayer; reescrito desde cero el doc de arquitectura del repo; pedimos vuestra mirada antes de mergear.

---

## Lo primero

**Enviado.** Ayer por la tarde Bea pulsó el botón Submit en Kaggle y Sprout entró oficialmente a las tres categorías principales del concurso bajo licencia CC-BY 4.0. El plazo de cambios menores sigue abierto hasta el 19 de mayo a las 01:59 GMT+2.

**Gracias.** Treinta días. Lo que ha entrado es un sistema real — código, hardware, vídeo, writeup EN+ES, galería, créditos. Cada una de vosotras tiene firmado un frente. No es retórica.

---

## Lo que pedimos hoy

Hemos reescrito desde cero la documentación arquitectural del repo. La versión vieja (en castellano, día 15) ya no reflejaba lo que de verdad construimos. La nueva está en EN como canónica, refleja v1.0 real, y queremos vuestra mirada antes de mergear.

**PR abierta como Draft:**
https://github.com/zigiella/sprout/pull/194

**Doc directo:**
https://github.com/zigiella/sprout/blob/feat/cambium/architecture-en-rewrite/docs/01_architecture.en.md

### Quién revisa qué

| Frente | Sección del doc | Tú revisas |
|---|---|---|
| ESP32 firmware | §3.1 Field (state machine, 5 hard rules, `PUMP_PULSE TEST_ONLY`, GPIOs) + §5.1 priority order | **Xilema** |
| Rhizome Jetson | §3.1 Field (`safe-cpu`/`gpu-experimental`, batería 18/18, day-27 supervised pulses) + §5.2 dual-agent `ShadowSkeptic` | **Endodermis** |
| Pollen Android | §3.2 Mobile (LiteRT-LM, demo/device flavors, D watermark + banner, Mini Evaluator 4 checks, 16 kHz audio) | **Floema** |
| Meristem node | §3.3 Home (FastAPI + SQLite, evaluator de 4 reglas, mDNS, WebSocket+HTTP fallback día 27, tool calling validado día 14) | **Meristem** |
| Validation status | §8 (cifras: 18/18 prompts, 12 pulsos día 27, 5/5 mini-battery) | quien generó cada cifra confirma la suya |
| Decision flow | §6 (los 19 pasos end-to-end) | revisión global, pero específicamente las miembras técnicas |
| Narrativa / framing | §1, §2 (Operating invariant), §9 (Out of scope) | **Corola, Bract, Venation** — opcional, por si veis algo que choque con el tono del vídeo o la marca |

### Cómo responder

Tres caminos válidos, elegid el que os encaje:

**A — Comentario en la PR de GitHub** (más rápido, vinculado al cambio exacto)
Abrid la PR #194, comentad línea por línea o en el thread general. Si tenéis acceso a la cuenta `zigiella`, podéis incluso pushear correcciones directas a la rama `feat/cambium/architecture-en-rewrite`.

**B — Bitácora** (la canónica del proyecto)
Cread `bitacora/2026-05-1X_review-architecture-doc_<vuestro-nombre>.md` con vuestros comentarios estructurados. Cambium las recoge y aplica.

**C — Respuesta de chat a Bea** (más informal)
Si preferís texto plano, mandadle a Bea vuestros puntos y ella los relaya a Cambium para que los aplique. Esto vale para cosas pequeñas; si son varias secciones, mejor B.

### Qué esperamos de la review

- **Fidelidad técnica.** ¿La descripción de vuestro nodo refleja lo que hicisteis? Cifras correctas, identificadores reales (`SOIL_A`, `GPIO16`, paths, ports), comportamiento honesto bajo los casos límite.
- **Honestidad sobre fronteras.** Si algo está en el doc como "validado" pero en realidad es "supervisado" o "parcial", marcadlo.
- **Cosas que falten.** Si vuestro frente tiene una pieza importante que el doc no menciona y debería, decidlo.
- **NO necesitamos:** prosa más bonita ni completitud absoluta. Esto es un documento canónico de arquitectura, no un blog post. Si la frase es técnicamente correcta, está bien.

### Cuándo

Idealmente **antes del fin del día 32** (mañana, 2026-05-17). Si necesitáis más tiempo, decidlo y vemos. La PR se queda en Draft hasta que firmemos todas; cuando estén las reviews aplicadas, pasa a Ready y mergea.

---

Si veis algo que se cuenta mejor desde vuestro frente que desde la coordinación, escribidlo. No nos ofendemos. **El doc tiene que ser preciso, no consensuado.**

Gracias otra vez por estos 30 días. Pase lo que pase con el jurado, lo construido existe.

🌿

— **Bea** (project lead) + **Cambium** (coordinación)
Sprout · Castellar de n'Hug · Barcelona · 16 de mayo de 2026
