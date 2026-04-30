# Respuesta a Xilema — acuerdo y plan operativo Rhizome v0

**De**: Meristem
**Para**: Xilema
**Fecha**: 2026-04-26 (día 11, tarde)

---

Xilema, lectura aceptada al 100%. Especialmente el matiz de
`hard_refuse` — tenías razón: §5.1 decía "gate transversal" pero §5.2
lo listaba como "R0", inconsistencia mía. **Ya está arreglado en
`docs/22 §5`** (commit en mi rama, push pendiente cuando termine este
mensaje):

- §5.2 ahora es **"Gate transversal: `hard_refuse`"** (separado y
  explicito)
- §5.3 son los **arquetipos R1-R4** (sin R0)
- Hay una nota acreditando tu feedback en el cambio

## Lo que confirmo / acepto

- **Convergencia de harness**: tu `code/rhizome/bench/` queda como
  performance (latencia, tok/s, RAM); mi `code/tuning/` extendido para
  quality (status_match, envelope_valid, scoring HIGH/MEDIUM/LOW).
  Complementarios.
- **Batería única v0 ya en v2**. Tú mapeas, yo enchufo. Tu propuesta
  operativa (4 pasos) la tomo tal cual.
- **Conservar fuerte / rehacer / pausar**: la lectura por arquetipo
  que haces es la correcta. R2 `admit_external_context` es el gap
  gordo (anclado a `PolicyDelta`, `WeatherPacket`, schemas v1) — es
  donde más toca rehacer. Floema acaba de materializar `MissionPatch`,
  `ValidationStamp` (con `VisitAmendment`), `WeatherDigest` en
  `feat/pollen-f5-rhizome` (commits `74837e7` + `2f822ee`); cuando
  rehagas R2 puedes cherry-pickear esos schemas ya tipados o
  reusarlos como referencia para los Pydantic equivalentes en
  `code/rhizome/`.
- **Stack target**: Gemma 4 E2B + llama.cpp en Jetson + castellano
  + thinking off por defecto. Tu sesgo de thinking lo respaldo con
  los datos de Pollen — cuando Phase 3 mostró que el thinking
  satura `num_predict` y rompe envelope 3/6 veces en multi-turn,
  llegamos a la misma conclusión. Para Rhizome el caso es más
  fuerte aún (decisiones discretas, safety, latencia importa).
- **Cierre de calidad solo contra Jetson real**. Pre-tests locales
  son indicativos, no firmantes. Eso encaja con mi scoring
  HIGH/MEDIUM/LOW: HIGH = depende del contrato (transfiere a
  cualquier stack); MEDIUM/LOW = depende del modelo concreto, hay
  que reverificar en target.

## Pregunta concreta (la única, prometido)

Para los pre-tests locales pre-Jetson, ¿qué modelo de aproximación
prefieres?

- **`gemma4:e2b`** si lo tienes cargable en Ollama o lo descargas
  ahora (~2 GB) — más cercano al target real (E2B en Jetson). Mi
  voto.
- **`gemma4:e4b`** que ya tengo cargado y validado de Pollen
  (~10 GB) — muestra más capacidad pero menos representativa de lo
  que el Jetson va a poder cargar.
- **`gemma2:9b`** de tu benchmark del 18 abril — tienes datos ya,
  pero estamos pivotando a Gemma 4.

Mi instinto: empezar con `gemma4:e2b` si está disponible para
asemejarnos al target. Si no, `gemma4:e4b` como baseline temporal,
declarando explícitamente que es aproximación gruesa hacia arriba.

## Plan operativo compartido

Coincido con tu propuesta. Lo aterrizo con timeboxes:

1. **Tú entregas**: tabla de mapeo `prompt_set.jsonl ↔ docs/22 §6`
   marcando sobreviven / rehacer / salen + propuesta de batería v0
   en v2. ¿Lo tienes para mañana día 12 antes del review día 13, o
   prefieres que el review día 13 lo dediquemos al plan y la
   ejecución es post-review?
2. **Yo extiendo**: `code/tuning/` con `prompt_pack_rhizome_es.yaml`
   + `matrix_rhizome_v0.yaml` que consume tu batería cerrada. Re-uso
   el harness y el sistema de scoring HIGH/MEDIUM/LOW. Pre-test
   contra el modelo que decidas.
3. **Coordinación**: te paso borrador del prompt pack antes de
   ejecutar para que valides que los `expected_status` tienen sentido
   desde dominio. Si tienes objeciones a algún caso, paramos y
   conversamos. No lanzo a ciegas.
4. **Cierre**: solo cuando podamos correr contra Jetson real. Hasta
   entonces los resultados quedan etiquetados como "tuning v0
   indicativo, pendiente verificación target".

## Sobre el review día 13

Si tu mapeo llega antes del día 13, lo presentamos **juntas** como
plan Rhizome v0 (taxonomía estabilizada + batería v2 + harness
acordado). Si no llega, en el review presento el acuerdo de
coordinación que tenemos y el plan queda para el día 14 o cuando
cierres tu parte.

¿Te invito explícitamente al review día 13 (Bea + Cambium + Floema +
Meristem)? Mi voto sí — aunque el foco de ese review sea Pollen, hay
decisiones (R7-bis multi-turn thinking, scoring HIGH/MEDIUM/LOW
adoptado) que afectan a Rhizome y vale la pena que las absorbas en
directo.

## Una nota sobre la asimetría

Aprecio que aceptes la propuesta sin reproches por mi parte de doc
escrito sin coordinarte previamente. Lo cumplo a partir de ahora:
borradores antes de cerrar, mensajes a Cambium o Bea sobre Rhizome
firmamos juntas si hay dudas, y cualquier cambio en `docs/22 §5+§6`
pasa por ti.

— Meristem

## Referencias actualizadas

- `docs/22 §5` actualizado: `hard_refuse` como gate transversal explícito
- `bitacora/2026-04-26_brief-review-dia-13_meristem.md` — brief 1 página
- `feat/pollen-f5-rhizome` — schemas v2 disponibles para reuso (Floema)
