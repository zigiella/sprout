# Bloque 1 — Triage 7 observaciones de Meristem sobre código Pollen

**Fecha:** 2026-04-28 (día 13)
**Modera:** Cambium
**Aprueba:** Bea
**Responden:** Floema + Meristem
**Lee:** Xilema

## Contexto

El día 9 (2026-04-24) Meristem absorbió el reframe del proyecto y, entre
sus entregables iniciales, escribió siete observaciones al código Pollen
en `bitacora/2026-04-24_pollen-observaciones-infraestructura_meristem.md`.
El día 10 (2026-04-25) las recalibró en
`bitacora/2026-04-25_pollen-observaciones-recalibradas_meristem.md`
tras detectar que dos eran hipótesis a verificar, no juicios.

Las siete son:

1. `EngineConfig.maxNumTokens=4096` hardcodeado — sin override por arquetipo
2. `SamplerConfig` no expuesto en `sendPrompt` — no podemos tocar `temperature`
3. `resetConversation()` existe pero sin política por arquetipo conectada
4. Métricas en `outputChars`, no tokens
5. `filter_channel_content_from_kv_cache` no explicitado
6. `SystemPrompts.kt`: solo 2 prompts, ambos en español, sin cobertura de los 4 arquetipos
7. Deuda técnica menor: reflection para Message, errores de chunks silenciados

## Lo que ha pasado entre día 10 y día 13

- F5 cerrado día 12: contratos v2, selector arquetipos con
  `resetConversation()` automático, thinking off por defecto + ON
  quirúrgico, `samplerTemperature` separado de `temperatureCelsius`.
- Tuning v0/v0.5 cerrados con scoring HIGH/MEDIUM/LOW.
- R4, R5, R6 + `SAFETY_DOWNGRADE` (Xilema) absorbidos al system prompt.
- R7-bis decisión A (thinking off multi-turn) aplicada en LiteRtInfra.

## Lo que se decide en este bloque

Para cada una de las 7 observaciones, etiqueta acordada por consenso:

- **CERRADA** — la observación está atendida en el código actual o
  cubierta operacionalmente por una decisión arquitectural posterior.
- **MVP** — entra en el alcance del demo del día 30. Hay dueña y plazo.
- **BACKLOG_v1** — no entra al demo. Queda en backlog para tuning v1
  o post-demo. Se documenta con dueña tentativa.
- **NO_APLICA** — la observación ya no es relevante (cambio de scope,
  refutada empíricamente, etc.).

Discrepancias entre Floema y Meristem se documentan con nombre y
apellido. Cambium consolida.

## Plantilla de respuesta

Crea `respuesta_[tu_nombre].md` en esta misma subcarpeta usando:

```
# Respuesta de [Tu nombre] — Bloque 1

## Estado
[...]

## Propuesta
[...]

## Dependencias
[...]

## Preguntas / inquietudes
[...]
```
