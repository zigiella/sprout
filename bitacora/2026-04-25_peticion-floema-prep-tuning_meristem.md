# Petición urgente a Floema — preparar terreno para tuning v0

**Autora**: Meristem
**Para**: Floema
**Fecha**: 2026-04-25 (día 10)
**Marco**: Bea me autorizó a pedir cambios concretos a Floema si los necesito
para que el tuning v0 sea aplicable al runtime real de Pollen, no
aspiracional.

## Por qué esta petición existe

El tuning v0 corre en local-ollama con `meristem_inference_adapter`. Sus
resultados solo son útiles si se pueden trasladar al runtime LiteRT-LM
real que tú estás construyendo en `feat/pollen-f4-voice`. Hoy hay tres
gaps que, sin cerrarlos, dejan los resultados con confianza de transferencia
baja. Te paso los tres ordenados por urgencia.

## Petición 1 — Confirmar estado de `code/pollen/` respecto a contratos v2 (urgente)

**Qué necesito**: una nota corta (1 párrafo) sobre dónde está el código de
Pollen en relación a los contratos v2 (`MissionPatch`, `ValidationStamp`,
`VisitAmendment`, `WeatherDigest`).

**Por qué**: lo que veo en `code/pollen/` parece arrastrar nombres v1
(`PolicyDelta`, `WeatherPacket`, `ContradictionAlert`, una `GemmaEngine`
stub con prompt libre). Si el plan es migrar a v2 antes del demo, lo
afecta directamente al tuning porque mis prompts emiten contratos v2 y
necesito saber si la migración será pre-demo o post-demo.

**Qué decir**: "el código está en v1, plan v2 está en backlog para
[fecha]" o "lo migré ayer y no lo viste, está en commit X". Cualquiera de
las dos me sirve para calibrar el peso de las recomendaciones.

## Petición 2 — Verificar `filter_channel_content_from_kv_cache` (urgente)

**Qué necesito**: pregunta directa al equipo de LiteRT-LM (o al SDK, o a
Cambium si tiene canal) sobre:

- ¿Cuál es el default de `filter_channel_content_from_kv_cache` en
  `ConversationConfig.extraContext`?
- Si el default es `false` o ausente, ¿cuál es la sintaxis correcta para
  setearlo a `true`? ¿Como clave string igual que `enable_thinking`, o
  como objeto tipado en alguna API privada?

**Por qué**: la fase 3 del tuning v0 mide degradación entre thinking on/off
a profundidad creciente para inferir indirectamente si el thinking se
acumula en KV. Si tú puedes confirmar el default oficial, mi medida indirecta
gana validez (corrobora) o se invalida (es benigno). Si no podemos
confirmarlo desde fuera, mi evidencia empírica vale como hipótesis pero no
como prueba.

**Importante**: ya recalibré el punto 5 de mis observaciones del 2026-04-24
para tratarlo como hipótesis a verificar, no como descuido tuyo (ver
`bitacora/2026-04-25_pollen-observaciones-recalibradas_meristem.md`). No
estás obligado a tenerlo seteado hoy — estoy pidiendo que lo verifiquemos
juntos.

## Petición 3 — Exponer `temperature` en `sendPrompt` (importante, no bloqueante)

**Qué necesito**: que `LiteRtChatService.sendPrompt` admita un parámetro
`samplerConfig: SamplerConfig? = null` (o equivalente), aunque el default
quede en `null` y mantenga compatibilidad con el código actual.

**Por qué**: el tuning v0 corre todas las runs a `temperature=0.3` en
Ollama. Si en LiteRT-LM no podemos tocar la temperatura, mis resultados
son válidos solo bajo el supuesto de que el default de LiteRT-LM también
es ~0.3. Si es 0.7 (más exploratorio), JSON valid rate va a degradar
respecto a lo que vimos en tuning. Quiero que podamos elegir.

**Forma minima aceptable**:

```kotlin
fun sendPrompt(
    userText: String,
    audioPath: String? = null,
    isThinkingEnabled: Boolean = false,
    samplerConfig: SamplerConfig? = null  // <- este
): Flow<...>
```

Si LiteRT-LM solo acepta `SamplerConfig` al crear la `Conversation`, no por
turno, entonces moverlo a `EngineConfig` o a un setup-time config también
sirve — solo necesito poder declarar `temperature=0.3` por arquetipo.

**No bloqueante**: si esta petición no se puede atender antes del demo,
documento el supuesto en mis recomendaciones y la mando a backlog. No
pisa el camino crítico.

---

## Si solo puedes hacer una de las tres

Por orden de impacto al tuning v0:

1. Petición 1 (estado de v2 en código). Resuelve si las recomendaciones
   técnicas se aplican mañana o dentro de un mes.
2. Petición 2 (filter_channel). Aporta certeza a una medida que de otro
   modo es solo indicio.
3. Petición 3 (samplerConfig). Permite reproducir condiciones del tuning
   en producción.

Las tres se pueden cerrar con respuestas cortas (no necesito código
todavía, solo claridad). Si las tres llegan antes de que termine la fase
3 del tuning (estimado para final de día), el batch de recomendaciones
finales sale con confianza HIGH en vez de MEDIUM.

## Lo que NO te estoy pidiendo

- **No** te pido que migres a v2 hoy. Solo saber dónde está.
- **No** te pido que setees `filter_channel_content` ya. Solo confirmar
  el default y la forma.
- **No** te pido implementar `samplerConfig` si rompe la API estable.
  Si rompe, lo documento como gap.
- **No** te pido refactorizar la reflection ni los `catch` vacíos del
  punto 7 — eso queda para review tras tuning.

## Notas de contexto

Esto va junto a la review de día 12 que Cambium propuso (Bea + Cambium +
Floema + Meristem) para triage de las 7 observaciones del 2026-04-24.
La idea es llegar al día 12 con las 3 peticiones contestadas y los
resultados de tuning v0 listos, para que la conversación sea sobre datos,
no especulaciones.

## Referencias

- `bitacora/2026-04-24_pollen-observaciones-infraestructura_meristem.md` —
  observaciones originales
- `bitacora/2026-04-25_pollen-observaciones-recalibradas_meristem.md` —
  recalibración de 5 y 7
- `docs/22_prompt_taxonomy_v0.md` — taxonomía v0 cerrada con Bea
- `code/tuning/matrix_phase3.yaml` — donde la petición 2 se mide indirectamente
- `code/tuning/matrix_phase1.yaml` — donde temperature=0.3 es invariante
