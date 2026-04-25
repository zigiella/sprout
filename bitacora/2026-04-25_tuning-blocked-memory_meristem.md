# Tuning v0 listo para correr — bloqueado por memoria física

**Autora**: Meristem
**Fecha**: 2026-04-25 (día 10)
**Para**: Bea (decisión), Cambium (informativo)
**Marco**: continuación inmediata de la fase de ejecución del tuning v0
después de cerrar la taxonomía v0 con Bea y dejar el harness listo.

## Estado a momento de escribir

- Rama: `feat/meristem-pollen-tuning-v0`, 3 commits por delante de
  `origin/feat/meristem-pollen-tuning-v0`. Pendientes de push.
  - `e35cfac docs: taxonomia v0 prompts Pollen + Rhizome (cerrada con Bea)`
  - `386509f feat(tuning): rediseno v0 segun taxonomia cerrada con Bea (16 prompts, sobre comun, harness)`
  - `c3c9d14 docs(bitacora): recalibracion observaciones + peticion urgente a Floema`
- `code/tuning/` cerrado: 16 prompts × packs EN+ES, 6 system prompts,
  3 matrices (48 + 16 + 12 = 76 runs), `judge_rubric.md` y `harness.py`.
- Dry-run del harness: pasa. Resuelve correctamente las 76 runs y construye
  los payloads esperados.
- Smoke real: **falla**. Razón abajo.

## El bloqueo

El smoke test del harness intentó llamar a Ollama vía
`meristem_inference_adapter` con `gemma4:e4b`. Ollama devolvió:

```
HTTP 500
{"error":"model requires more system memory (9.7 GiB) than is available (8.3 GiB)"}
```

Cuando lo reintenté ahora, la situación es peor:

| Métrica | Valor |
|---|---|
| Memoria física total del sistema | 16,216,372 KB (~15.5 GiB) |
| Memoria física libre | 1,977,228 KB (~1.9 GiB) |
| Memoria que `gemma4:e4b` requiere | ~9.7 GiB |
| Modelos cargados en Ollama | ninguno (`ollama ps` vacío) |

El gap es estructural: la máquina tiene RAM suficiente en total, pero
otros procesos están ocupando ~13 GiB y dejan menos de 2 GiB para
Ollama. `ollama ps` confirma que el problema no es un modelo zombie
en GPU/CPU — es presión de RAM general del sistema.

## Por qué no sustituyo el modelo unilateralmente

Tengo localmente disponibles:

| Modelo | Tamaño | Uso aproximado |
|---|---|---|
| `gemma4:e4b` | 9.6 GB | objetivo del tuning |
| `gemma3n:e4b` | 7.5 GB | alternativa más cercana |
| `gemma2:9b` | 5.4 GB | otra familia |
| `gemma3:4b` | 3.3 GB | familia anterior |

Sustituir `gemma4:e4b` por cualquiera de los otros invalidaría la
afirmación central del tuning v0:

> "Las recomendaciones tienen confianza HIGH/MEDIUM/LOW de transferir
> al runtime LiteRT-LM real (`gemma-3n-E4B-it-int4`) que corre en
> Pollen, porque Ollama con `gemma4:e4b` aproxima ese stack lo mejor
> que se puede en local."

Si corro contra `gemma3n:e4b` (que es más cercano al modelo de LiteRT-LM
que `gemma4:e4b` mismo, paradójicamente), tengo que añadir un caveat
honesto: "estos resultados son sobre proxy diferente al que dijimos que
íbamos a usar". Eso lo decide Bea, no yo.

## Tres opciones, ordenadas por preferencia

### Opción A — Liberar memoria y reintentar (preferida)

Cerrar Chrome / VS Code / lo que esté ocupando los 13 GiB de RAM,
asegurarme de tener al menos 11 GiB libres, y reintentar el smoke. Las
76 runs estimadas tardan ~25–40 minutos a `temperature=0.3` con un
modelo de 9 GB en CPU/GPU local.

**Ventaja**: no toca la afirmación de transferencia. Resultados
defendibles tal como están planteados.

**Coste**: el operador (yo o quien lleve la sesión) tiene que cerrar
sus otras apps. No siempre práctico si el operador está usando la
máquina para otra cosa en paralelo.

### Opción B — Sustituir por `gemma3n:e4b` con caveat explícito

Correr las 76 runs sobre `gemma3n:e4b` (7.5 GB, cabe holgadamente en
los 8 GiB que sí tenemos disponibles). Documentar en
`code/tuning/README.md` y en el bitácora de cierre que **el modelo de
referencia cambió**, y por qué.

**Ventaja interesante**: `gemma3n:e4b` es la familia que LiteRT-LM
realmente usa (`gemma-3n-E4B-it-int4`), no `gemma4:e4b`. La
transferencia podría ser **más** directa, no menos. La razón por la
que arrancamos con `gemma4:e4b` fue disponibilidad/familiaridad, no
fidelidad.

**Coste**: cambio de criterio a mitad del tuning. Si Bea cerró la
elección de modelo en alguna conversación previa, no tengo registro de
ello — necesito autorización explícita.

### Opción C — Esperar / escalar a 32 GB

Posponer el tuning hasta que la máquina tenga capacidad. No es opción
real con el calendario del demo (día 12 review).

## Mi recomendación

**Opción B con caveat.** Justificación:

1. `gemma3n:e4b` está más cerca de `gemma-3n-E4B-it-int4` (LiteRT-LM)
   que `gemma4:e4b`. La afirmación de transferencia mejora, no
   empeora, si el documento lo declara claramente.
2. El bloqueo de memoria es estructural en la máquina actual; el
   coste de coordinar "cierra Chrome" cada vez que iteremos el tuning
   no es escalable.
3. La taxonomía v0 ya está cerrada y los prompts no dependen del
   modelo concreto — solo dependen de que el modelo sea Gemma-family
   con thinking. `gemma3n:e4b` cumple esa condición.

Si Bea prefiere Opción A por consistencia con lo que dijimos al
arrancar, libero memoria y corro. Si prefiere B, edito `code/tuning/`
para reflejar el modelo y arranco. **No hago ninguna de las dos sin tu
input.**

## Lo que necesito de Bea

Una de estas tres respuestas, lo más cortas posibles:

- "A" — espera a que libere memoria, corre con `gemma4:e4b`.
- "B" — cambia a `gemma3n:e4b`, documenta el motivo, corre. Confianza
  de transferencia se reporta sobre ese stack.
- "C" — para el tuning hoy, retomamos cuando haya 32 GB de RAM o
  máquina con más capacidad.

## Lo que hago mientras esperamos

- Push de los 3 commits a `origin/feat/meristem-pollen-tuning-v0` para
  que Cambium y Floema vean el estado real de la rama.
- Mando la petición a Floema (`bitacora/2026-04-25_peticion-floema-prep-tuning_meristem.md`)
  por canal cuando tenga visto bueno.
- Reviso una vez más `harness.py` y los matrices por si encuentro algo
  ajustable (no anticipo cambios — el dry-run pasa limpio).

## Referencias

- `code/tuning/harness.py` — el smoke test está implementado, falla
  controladamente con el mensaje de Ollama
- `code/tuning/matrix_phase1.yaml` — invariante `model: gemma4:e4b`
  (cambia en Opción B)
- `bitacora/2026-04-25_peticion-floema-prep-tuning_meristem.md` —
  petición pendiente a Floema, no afectada por este bloqueo
- `bitacora/2026-04-25_pollen-observaciones-recalibradas_meristem.md` —
  observaciones del 24 con dos puntos suavizados, no afectadas
