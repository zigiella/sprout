# Recalibración de observaciones a infraestructura Pollen

**Autora**: Meristem
**Fecha**: 2026-04-25
**Antecede**: `bitacora/2026-04-24_pollen-observaciones-infraestructura_meristem.md`
**Origen**: feedback de Bea sobre los siete puntos originales (revisión de
2026-04-25, junto a la taxonomía cerrada en `docs/22_prompt_taxonomy_v0.md`).

## Por qué este documento existe

Bea revisó las siete observaciones del 2026-04-24 y marcó nota amarilla en
dos: el punto 5 (filter_channel_content_from_kv_cache) y el punto 7
(reflection para `Contents` y `Message`). En ambos, mi tono de "esto Floema
no lo ha hecho bien" excedía la evidencia disponible. Ajusto aquí para que
la conversación con Floema arranque con calibración correcta.

Los puntos 1, 2, 3, 4 y 6 quedan como están — ahí la observación se
sostiene tras revisión.

## Punto 5 (recalibrado): `filter_channel_content_from_kv_cache`

**Qué dije el 2026-04-24**: que esa clave debería estar seteada a `true`
explícitamente en el `extraContext` de `LiteRtChatService.sendPrompt`, y
que no verla seteada era un descuido.

**Qué admito el 2026-04-25**: no hay docs públicas de LiteRT-LM que
confirmen ni el default ni cómo cambiar esa clave. La mención en
`research/06_litertlm_thinking_digest.md` que usé como base es un digest
de Peri sobre material no oficial. Mi observación pasa de "Floema debería
ya haberlo seteado" a:

> **Hipótesis a verificar empíricamente**. Si el thinking se acumula en
> el KV cache, dos turnos consecutivos con thinking on deberían producir
> degradación de calidad o corte antes que dos turnos sin thinking.
> La fase 3 del tuning v0 (12 runs, T_OFF vs T_ON a profundidades
> crecientes) aporta evidencia indirecta. En paralelo, Floema puede
> preguntar al SDK / al equipo de LiteRT-LM por el default oficial y por
> cómo cambiarlo si procede.

Esto es más honesto y no exige a Floema que adivine.

## Punto 7 (recalibrado): reflection para `Contents` y `Message`

**Qué dije el 2026-04-24**: que el código usa reflection en
`LiteRtInfra.kt` líneas 143–161 para construir objetos del SDK porque la
API pública no expone los constructores.

**Qué admito el 2026-04-25**: Bea no veía la reflection en el snapshot
que ella miraba. Re-verificando con `git show
origin/feat/pollen-f4-voice:code/pollen/app/src/main/kotlin/net/sprout/pollen/llm/LiteRtInfra.kt`,
la reflection sí está presente en el commit `9f4b562` (rama
`feat/pollen-f4-voice` actual de Floema), líneas 149–167 — leí la rama
correcta pero confundí los rangos. **No** está en `main` (ahí Pollen
todavía no tiene la integración LiteRT-LM real, solo el stub de la rama
anterior).

Ajustes:

- **Cualificar el dónde**: la reflection vive en
  `feat/pollen-f4-voice@9f4b562:code/pollen/app/src/main/kotlin/net/sprout/pollen/llm/LiteRtInfra.kt`,
  líneas **149–167**. Cuando Floema mergee a `main`, las líneas pueden
  moverse — referenciar por contenido (`Contents` constructor reflectivo)
  en futuras revisiones.

- **Bajar el tono de la queja**: la reflection es un workaround
  legítimo si la API pública no expone los constructores. Floema lo
  marca en comentario. La observación útil no es "esto está mal" sino
  "esto crea fragilidad ante upgrades del SDK; conviene anclar la
  versión del SDK y cubrir la reflection con un test mínimo que falle
  ruidosamente cuando cambien los constructores".

- **Errores silenciados (segunda parte del punto 7)**: ese se mantiene.
  Los `catch (t: Throwable) { /* Ignore chunk errors */ }` siguen siendo
  un agujero observable, sobre todo si la fase 3 del tuning produce
  truncamientos por presión de ventana — sin log, no sabremos por qué.

## Lo que mantengo y lo que retiro

| Punto | Estado tras recalibración |
|---|---|
| 1 — `maxNumTokens` hardcodeado | mantenido, sin cambios |
| 2 — `SamplerConfig` no expuesto en `sendPrompt` | mantenido |
| 3 — `resetConversation` sin política por arquetipo | mantenido |
| 4 — métricas en `outputChars`, no tokens | mantenido |
| 5 — `filter_channel_content_from_kv_cache` | **suavizado a hipótesis empírica** |
| 6 — `SystemPrompts.kt` minimo, en castellano | mantenido (la taxonomía v0 lo refuerza) |
| 7a — reflection `Contents`/`Message` | **cualificado a commit y línea exactos, tono más sobrio** |
| 7b — `catch (Throwable) {}` vacíos | mantenido |

## Una nota sobre por qué cualificar es importante

La conversación con Floema funciona si llego con observaciones que se
sostienen. Si meto un "esto debería estar seteado" sin docs que lo
soporten, o si confundo qué rama y qué líneas estoy leyendo, gasto
crédito de revisor sin ganar nada. Bea pilló las dos cosas en un único
pase y eso me ahorra tener esa conversación a mitad de una review más
ruidosa. Lo agradezco y queda como recordatorio: cualificar antes de
afirmar.

## Próximos pasos derivados

1. La petición urgente a Floema (`bitacora/2026-04-25_peticion-floema-prep-tuning_meristem.md`)
   incluye la pregunta directa al SDK sobre `filter_channel_content_from_kv_cache`,
   en lugar de tratarlo como algo que Floema debió haber configurado.
2. Para la review del día 12 (Bea + Cambium + Floema + Meristem), llevo
   esta versión recalibrada en lugar de la original.
3. La fase 3 del tuning queda con métrica explícita (`envelope_valid` +
   degradación entre T_OFF y T_ON a profundidad creciente) que aporta
   evidencia indirecta a la hipótesis de KV cache.

## Referencias

- `bitacora/2026-04-24_pollen-observaciones-infraestructura_meristem.md`
  — versión original
- `docs/22_prompt_taxonomy_v0.md` — taxonomía cerrada con Bea
- `code/tuning/matrix_phase3.yaml` — donde la hipótesis 5 se mide
- `research/06_litertlm_thinking_digest.md` — fuente original (Peri)
  que cité, ahora con la nota de que no tiene respaldo en docs oficiales
