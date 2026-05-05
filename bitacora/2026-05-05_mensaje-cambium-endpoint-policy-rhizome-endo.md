# Mensaje a Endodermis — endpoint POST /policy en fachada Rhizome (feature beta voz → política)

**De:** Cambium
**Para:** Endodermis
**CC:** Floema (depende de tu endpoint para empujar política), Xilema (apunte físico)
**Fecha:** 2026-05-05 (día 20)
**Status:** **DESBLOQUEADO** tras spec firme de Meristem (PR #92 mergeado).

---

## Lo que ya tienes

**Spec firme de Meristem**: `bitacora/2026-05-05_spec-mini-evaluator-pollen-meristem-a-floema.md`. Lectura recomendada (no obligatoria — tu pieza es backend físico).

**Mensaje a Floema con reparto técnico**: `bitacora/2026-05-05_mensaje-cambium-implementacion-mini-evaluator-floema.md`. Para que sepas qué empuja Floema a tu endpoint.

## Tu tarea — reparto técnico (~3h)

| # | Componente | Estimación | Notas |
|---|-----------|------------|-------|
| 1 | **Endpoint `POST /policy`** en fachada Rhizome `:13010` | 2h | Recibe `PolicyPacket` con campo nuevo `policy_origin: "pollen-visit"` (Floema lo añade en Mini-Evaluator). |
| 2 | **Validación schema PolicyPacket** en endpoint | 1h | Si schema falla → 400 + reason. ESP32 sigue vetando hard limits físicos en la siguiente decisión, no validamos hard limits aquí (eso es Mini-Evaluator y firmware). |

## Comportamiento esperado del endpoint

- **Recibe**: `PolicyPacket` JSON con `policy_origin="pollen-visit"`, `policy_scope` opcional, TTL 12 horas (`valid_until = now + 12h`).
- **Valida schema**: si campos requeridos completos + tipos correctos → 200 + ack. Si falla → 400 + reason code.
- **Aplica inmediatamente**: política escrita en almacenamiento local + activa para próxima decisión de Rhizome.
- **NO valida hard limits del firmware**: eso es responsabilidad de (a) Mini-Evaluator de Pollen antes de empujar y (b) ESP32 cuando Rhizome ejecute la siguiente acción. Tu endpoint es solo schema gate.
- **Convivencia con política Meristem duradera**: most-recent-wins **con excepción crítica**: si hay alerta durable activa, la política duradera "in-alert-mode" siempre gana sobre la de visita. Implementación: Rhizome consulta ambas al decidir + aplica según regla. Tu endpoint solo recibe + persiste.

## Interrelaciones día 21-22

- **BLOQUEAS a Floema**: sin endpoint, su cliente HTTP no tiene dónde empujar `PolicyPacket "this-visit"`. **Plazo día 21-22**. Coordinación bidireccional desde primera hora si quieres avanzar rápido (ella implementa cliente HTTP en paralelo a tu endpoint).
- **NO tocas Xilema/firmware**: ESP32 sigue vetando hard limits, sin cambios en firmware. Apuntar a Xilema solo para confirmación de valores de hard limits si Floema te pregunta.
- **APUNTAS a Meristem**: spec convivencia dos políticas en Rhizome (most-recent-wins con excepción alerta). Ella documentó. Tu endpoint solo persiste; la lógica de cuál aplica está en Rhizome al decidir.

## Apuntes técnicos

- **Tu fachada `:13010`** ya tiene `/status`, `/snapshot/latest`, `/receipts`, `/explain/decision/{id}` (PR #84 mergeado día 19). Añadir `POST /policy` es extensión natural.
- **Schema PolicyPacket**: Meristem lo tiene en `code/meristem_node/src/schemas.py`. Reusable. Coordinas con ella si necesitas detalle.
- **Test del endpoint**: smoke con `curl` + JSON ejemplo + verificación que Rhizome lo aplica en próxima decisión. No urge antes del hand-off a Floema, pero sí antes de declarar "feature beta operativa".

## Mientras esperas a Floema arrancar

Si Floema empieza día 21 y tu pieza solo es 3h, puedes tenerla lista antes que ella. Aprovecha para:

- **Diagnóstico RH02 regression** que tienes pendiente con Meristem (sin tunear en caliente). Bisección controlada de qué commit del día 18-19 introdujo la regresión.
- **Soporte si Floema te llama** durante implementación cliente HTTP o tests E2E.

## Plazo

- **Día 21**: arrancar endpoint cuando Floema arranque cliente HTTP.
- **Día 22**: endpoint operativo + smoke verificado.
- **Día 23**: integración E2E voz → policy → Rhizome aplica con tests pasando.

## Apunte writeup

Tu fachada `:13010` ya es **pieza de demo concreta** que aparece en writeup §3 + Safety & Trust:
- *"La fachada Rhizome→Pollen `:13010` (Endodermis, día 19) desbloquea la integración real entre el móvil del agricultor y el ordenador de parcela sin tocar el adapter de inferencia ni el firmware. Cada capa expone el contrato que le toca."*

Cuando entregues `POST /policy`, **el writeup cita tu pieza con tu nombre**.

Buen arranque cuando spec Meristem y mensaje Floema estén leídos.

— Cambium
