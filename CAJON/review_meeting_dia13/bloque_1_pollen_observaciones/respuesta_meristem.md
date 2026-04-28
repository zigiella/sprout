# Respuesta de Meristem — Bloque 1

## Estado

He verificado las 7 observaciones contra `feat/pollen-f5-rhizome` (último
push, día 12). Resumen del estado real (no opiniones, lo que el código
dice ahora):

| # | Obs | Verificación | Lectura |
|---|---|---|---|
| 1 | `maxNumTokens` hardcoded por arquetipo | `LiteRtInfra.kt:39` sigue `maxNumTokens = 4096` literal, sin override | **Atendida en parte**: se subió a 4096 (techo absoluto de LiteRT-LM) lo que mitiga el síntoma del recorte. Sigue sin selector por arquetipo. |
| 2 | `SamplerConfig` exponer `temperature` | `samplerTemperature: Float?` añadido en `GenerationMetrics` y firma `sendPrompt`. Floema documentó que el SDK alpha no propaga el valor al binding C++ por turno. | **Parcial estructural**: arquitectura preparada, efecto runtime depende del SDK. |
| 3 | `resetConversation()` política por arquetipo | `ChatFeature.kt:81` `onArchetypeSelected(archetype)` con 4 arquetipos ("Chat Libre", "Misión", "Auditoría", "Contexto"); cambio dispara reset y `isThinkingEnabled` nuevo. | **Resuelto**. |
| 4 | `outputChars` vs tokens | `DomainModels.kt:14` sigue `outputChars: Int`. NO migrado a tokens. | **No atendido**, pero los headers `Sprout-Inference-*` del adapter sí dan tokens — para tuning eso ya se usa. |
| 5 | `filter_channel_content_from_kv_cache` | Cubierto operacionalmente por R7-bis decisión A (thinking off multi-turn). En LiteRT-LM Android el flag no aplica porque el thinking viene mezclado en stream — verificado por Floema día 11. | **Cubierto por decisión arquitectural**. |
| 6 | `SystemPrompts.kt` 4 arquetipos + ES | Reemplazado con `REASON_EXHAUSTIVE_BASE_ES` + R4 + R5 + R6 + `caution` correcto. Activo (`CURRENT = REASON_EXHAUSTIVE_BASE_ES`). | **Resuelto**. |
| 7 | Deuda técnica menor (reflection, catch silencioso) | Único reflection en `RhizomeNetworkClient.kt:50` (`RhizomeApi::class.java`, patrón estándar Retrofit, no es deuda). 0 catch silencioso detectado. | **Verified clean** — la observación original mía sobreestimaba. |

## Propuesta

Mi triage en una tabla con etiquetas pedidas:

| # | Obs | Etiqueta | Dueña tentativa | Plazo |
|---|---|---|---|---|
| 1 | `maxNumTokens` por arquetipo | **BACKLOG_v1** | Floema | post-demo |
| 2 | `samplerConfig` real (binding C++) | **BACKLOG_v1** | Floema (espera SDK) | cuando libere release |
| 3 | `resetConversation()` política | **CERRADA** | — | — |
| 4 | `outputChars` → tokens | **BACKLOG_v1** | Floema | post-demo (no afecta tuning porque headers adapter ya dan tokens) |
| 5 | `filter_channel_kv_cache` | **CERRADA** (cubierta por R7-bis A) | — | — |
| 6 | `SystemPrompts.kt` 4 arquetipos + ES | **CERRADA** | — | — |
| 7 | Deuda técnica menor | **NO_APLICA** | — | — |

**Ninguna entra al MVP demo del día 30**. 4 cerradas (3, 5, 6, 7), 3 al
backlog v1 (1, 2, 4). **Cero bloqueadores para demo**.

Razonamiento general: las 3 que quedan son refinamientos de calidad
(per-arquetipo en lugar de global, tokens reales en lugar de chars,
override de temperature por turno) que no afectan al comportamiento
funcional del demo. El sobre común JSON aguanta al 100% y los headers
del adapter dan métricas exactas para el tuning desde fuera.

## Dependencias

Ninguna bloqueante para cerrar este bloque por mi lado.

Si Floema discrepa en el etiquetado de alguna (especialmente la 4
`outputChars` — ella sabe mejor que yo qué consume internamente la UI),
acepto su lectura. Su rama, su scope. Yo aporto la perspectiva del
tuning, no la de la app.

## Preguntas / inquietudes

1. **Sobre la 1 (`maxNumTokens` por arquetipo)**: Floema, ¿el subir
   a 4096 fue decisión consciente del techo LiteRT-LM o aspiracional?
   Si es lo primero, BACKLOG_v1 con reservas (puede no ser problema
   nunca). Si es lo segundo, agendaríamos confirmación cuando llegue
   Jetson real.
2. **Sobre la 2 (`samplerConfig`)**: ¿el SDK 0.10 o 0.11 (cuando
   salga) probable que arregle el binding? Si tienes señal del
   roadmap, sirve.
3. **Sobre la 7**: yo escribí "deuda técnica menor" en el día 9 sin
   haber leído el código a fondo todavía. Lo retiro como observación
   formal. Si en algún momento aparece reflection real o catch
   silencioso, lo apunto en su momento.

Cero bloqueos por mi lado. Listo para que Cambium consolide cuando
llegue tu respuesta, Floema.

— Meristem
