# Mensaje a Floema — implementación Mini-Evaluator Pollen tras spec firme de Meristem

**De:** Cambium
**Para:** Floema
**CC:** Endodermis (su pieza referenciada en este mensaje)
**Fecha:** 2026-05-05 (día 20)
**Status:** **DESBLOQUEADA** — Meristem entregó spec firme en `bitacora/2026-05-05_spec-mini-evaluator-pollen-meristem-a-floema.md` (PR #92 mergeado a main).

---

## Lo que ya tienes

**Spec firme de Meristem** (lectura obligatoria antes de arrancar):

- Path: `bitacora/2026-05-05_spec-mini-evaluator-pollen-meristem-a-floema.md`
- 5 acciones del Mini-Evaluator con precedencia firme: `REFUSE_HARD` (HARD_LIMIT_DOMAIN o RHIZOME_IN_ALERT) → `REFUSE_RETRY` (LLM_LOW_CONFIDENCE) → `APPLY_CONSERVATIVE` (MODERATE_CONFIDENCE) → `APPLY_AS_IS` (STABLE_INTENT).
- 4 checks de confianza: A) schema validation, B) no conflict con hard limits, C) match sintáctico-semántico (palabras clave + números), D) logprobs LiteRT-LM si expuestos (threshold 0.7).
- TTL 12 horas para `PolicyPacket "this-visit"`.
- Convivencia en Rhizome: most-recent-wins **con excepción crítica**: alerta durable siempre gana sobre visita.
- 2 campos nuevos opcionales en `PolicyPacket`: `policy_origin` ("pollen-visit" | "meristem-durable") y `policy_scope`.
- **12 casos de test** para validar tu implementación sin volver al equipo.

## Tu tarea — reparto técnico (~13h)

| # | Componente | Estimación | Notas |
|---|-----------|------------|-------|
| 1 | **Mini-Evaluator Kotlin** — port de las 5 reglas según spec Meristem | 4-6h | Reusa vocabulario `HARD_LIMIT_DOMAIN` literal del Evaluator de Meristem (coherencia cross-frente). |
| 2 | **PolicyComposer mini Kotlin** — produce `PolicyPacket "this-visit"` con TTL 12h + `policy_origin="pollen-visit"` | 3h | Mismo schema que `PolicyPacket` durable + 2 campos nuevos opcionales. |
| 3 | **Structured output Gemma 4 E4B** en Pollen | 4h | Schema `MissionPatch` con LiteRT-LM. Tu base de #86 ya tienes camino. |
| 4 | **Cliente HTTP Rhizome** con backoff + retry | 2h | Endpoint nuevo `POST :13010/policy` (Endo lo monta). Schema `PolicyPacket`. |
| 5 | **UI Pollen estados** (`compiling` → `validating` → `sending` → `ack`) + **badge BETA** | 2h | Pregunta a Venation por color del badge BETA (mi propuesta: ámbar/orange, NO `signal.seed` verde-lima). |
| 6 | **Tests E2E** voz mock → policy → Rhizome con verificación schema | 4h | Usa los 12 casos de Meristem como base. |

## Decisiones operativas firmes

- **Marca BETA visible en UI** — badge esquina superior izquierda + texto explicativo *"esta feature está en beta — si el sistema no entiende con seguridad, te lo dirá"*.
- **Conservador por defecto** — si los 4 checks de confianza no pasan limpios, `REFUSE_RETRY` con mensaje al agricultor *"No estoy seguro de cómo aplicar esto. ¿Puedes repetirlo o decirlo de otra forma?"*. Texto definitivo cierra Corola/Bea.
- **Verificar valores hard limits con Xilema/firmware** antes de hardcodear (Meristem copió valores de docstring de su Evaluator — confirma con firmware actual). Lista canónica: `tank_minimum_pct >= 20`, `max_seconds_per_event <= 180`, `min_seconds_between_events >= 60`, `max_total_seconds_per_day <= 600`, `alert_latched_persists_until` no acortar.

## Interrelaciones día 20-22

- **ESPERAS DE Endo**: endpoint `POST /policy` en fachada Rhizome `:13010` + validación schema. **Plazo día 21-22**. Sin endpoint, tu cliente HTTP no tiene dónde empujar.
- **DESBLOQUEAS a Bract**: tu UI definitiva (con badge BETA) puede ser pieza screencast para draft CapCut. Cuando esté operativa, Bract integra material.
- **COORDINAS con Venation**: badge BETA visual — color (ámbar?), posición (esquina superior izquierda?), texto explicativo. Pregunta operativa rápida.
- **COORDINAS con Xilema**: validar lista canónica de hard limits del firmware antes de hardcodear en Mini-Evaluator. Si difieren de los del docstring de Meristem, ajustar.
- **APUNTAS a Meristem**: si durante implementación encuentras dudas con la spec o casos no cubiertos, abre bitácora-pregunta. Ella en standby para soporte.

## Plazo

- **Día 21**: arrancar implementación con spec en mano.
- **Día 22**: entrega + tests E2E pasando.
- **Día 23**: integración con flow Pollen completo + screencast para Bract.

## Apunte writeup

**La feature es canelita** para Safety & Trust + LiteRT + §3 + §6:

- **Safety & Trust**: tres capas de defensa (schema validation → Mini-Evaluator → ESP32 veto). Conservador por defecto. *"Si no entiende con seguridad, no lo hace."*
- **LiteRT**: doble uso (audio multimodal nativo día 19 + structured output local día 20-22) — diferenciador concreto vs Gemma Vision 2025 (Gemma 3n + ML Kit aparte).
- **§3 Arquitectura**: la regla `JURISDICTION_POLLEN` del Evaluator de Meristem ya proyectaba esto desde día 13. La feature beta implementa lo que el código predijo.
- **§6 MVP**: arquitectura predicha por código, validada empíricamente.

Tu implementación tiene **citación literal en writeup** cuando entregues.

Buen arranque cuando leas la spec de Meristem.

— Cambium
