# Thinking mode en Gemma 4 E4B, latencia real, y reformulación de issues post-#37

**Fecha:** 2026-04-19
**Autor:** Meristem
**Area:** Meristem
**Tipo:** hallazgos de verificacion + replanteo de roadmap post-merge
**Destinatario:** Cambium (para decisiones sobre las 3 issues que quedaban pendientes)

## Qué pasó

Tras abrir #37 con el policy engine, me pediste en tu review: (a) responder
a los 2 puntos concretos en el PR, (b) correr el smoke test contra Ollama
real para fijar latencia, (c) no empezar ninguna de las 3 issues post-merge
("consolidator job", "A/B thinking mode", "activación sombra 26B MoE")
hasta que #37 estuviese mergeado.

Este documento recoge todo lo que he hecho con Bea entre tu review y este
momento, y las implicaciones para esas 3 issues. **El PR #37 sigue listo
para squash-merge tal como está**; lo de aquí es material para decidir
*qué* abrimos después y en qué orden.

## Lo que se hizo con Bea

### 1. Respuesta a los 2 puntos del PR

- Confirmado explícitamente en comment del PR que `consolidate()` NO
  re-ensaya Ollama. Una sola llamada a `llm.generate_json`; si falla,
  propaga la excepción y se loguea en `decisions_log` con action
  `blocked_invalid_schema` o `blocked_by_safety`. Retry/backoff es
  responsabilidad del consolidator job futuro.
- Anotada la línea de idempotencia de `/deltas/propose` en `README.md`
  (commit `3049dbf`).

### 2. Smoke test contra Ollama real

Ejecutado por Bea en su portátil (16 GB, CPU pura, sin GPU). Ruta de
depuración:

1. Primer run: skipped. Causa: `localhost` en Windows resuelve IPv6 `::1`
   primero, Ollama bindea IPv4 `0.0.0.0`, httpx se quedaba colgado dentro
   del timeout de 2s del `ping()`.
2. Fix: `$env:OLLAMA_HOST="http://127.0.0.1:11434"` fuerza IPv4.
3. Segundo run: timeout a 120s (default del `OllamaClient`). Causa: la
   llamada real del engine excede ese cap.
4. Fix: commit `7628ff2` sube el timeout del cliente a 300s solo en el
   smoke. El test ya completa.
5. Tercer run: `AssertionError: latencia 238.7s excede budget de 90s`.
   **El engine completa correctamente y persiste una PolicyPacket válida**;
   solo falla el assert del budget.

### 3. Diagnóstico con contadores de Ollama

Bea pidió pulir más el análisis antes de que cerrásemos. Amplié un script
temporal `diag_ollama.py` (ya borrado) que mide matriz 2×2 de
`prompt × format` leyendo `prompt_eval_count`, `eval_count`,
`prompt_eval_duration`, `eval_duration`.

Resultados clave:

| Variante | Wall | Input tok | Output tok |
|---|---|---|---|
| A prompt corto + `format=json` | 4.3s | 33 | 8 |
| B prompt corto + `format=schema` | 60.7s | 65 | 347 |
| C prompt engine + `format=json` | **236.6s** | 2152 | 431 |
| D prompt engine + `format=schema` | 51.5s¹ | 2152 | 320 |
| E prompt engine **SIN dup schema** + `format=schema` | 48.4s¹ | 658 | 298 |

¹ D y E no son cold: aprovechan el KV cache de C (mismo prefix). Cold
estimado real de D ≈ 216s; cold real de E ≈ 96s.

**Interpretación corregida**:

- Output tokens/s en CPU es **constante ~6.2-6.9 t/s**. Techo del hardware.
- Input cold processing en CPU ≈ **13 t/s**.
- Forzar schema **no** ralentiza el decoding. Solo aumenta el volumen de
  output (~300 tokens obligatorios por rellenar todos los campos del
  schema).
- El cuello cold es el **tamaño del input**. `build_user_prompt` duplica
  el schema entero como texto dentro del prompt además de pasarlo en
  `format=`. Input de 658 → 2152 tokens, 120s extra.
- El spec "<60s" no es alcanzable en CPU pura; output mínimo por schema
  (~300 tok × 1/6.5 t/s) ya son 46s sin contar input cold.

### 4. Conversación sobre real-time

Bea aclaró explícitamente que los nodos **no necesitan comunicación en
tiempo real**. Pueden responder con delays y asincronía entre ellos.

Esto reencuadra todo: **Meristem es asíncrono por diseño**. Ciclo real:
Pollen acumula evidencia durante horas → llama a Meristem → Meristem
piensa 4 minutos → emite PolicyPacket con TTL de horas → Rhizome aplica
la política cacheada en microsegundos. El "<60s" del spec era optimización
para demo fluida, no requisito funcional del sistema. 4 minutos de
consolidación para una política que vale 6-24h es la proporción correcta.

Lo dejo anotado aquí para que quede en el repo como decisión formal: el
budget <60s se mantiene como *objetivo con GPU o modelo optimizado*, no
como condición de aceptación.

### 5. Thinking mode en Gemma 4 E4B

Primera ronda: probé `think=true` via `/api/generate` con `format=schema`
(la combinación que usa `consolidate()` hoy). Resultado: campo `thinking`
vacío, output tokens idénticos al baseline. Concluí erróneamente que E4B
no soportaba thinking en Ollama.

Bea aportó investigación detallada sobre la API de Ollama con ejemplos
concretos (`ollama.chat(think=True)`, `message.thinking`, etc.). Re-probé
con 5 sondas discriminativas:

| Endpoint | `think` | `format` | Campo thinking | Chars |
|---|---|---|---|---|
| `/api/generate` | ✓ | — | ✓ | 1615 |
| `/api/generate` | — | — | — | 0 (control) |
| `/api/generate` | ✓ | `json` | ✗ | **0** |
| `/api/chat` | ✓ | — | ✓ | 1622 |
| `/api/chat` | ✓ | `json` | ✓ | **1925** |

**Hallazgos**:

1. **Gemma 4 E4B SÍ soporta thinking nativo en Ollama**. Mi primera
   conclusión era errónea. El modelo razona estructuradamente en inglés
   y emite la respuesta final en el idioma del usuario.
2. **`/api/generate` + `format=json` suprime thinking**. Bug o limitación
   no documentada; es un quirk del endpoint.
3. **`/api/chat` + `format=json` respeta thinking** y devuelve ambos
   campos (`message.thinking` y `message.content`) limpios.

Implicación directa para Meristem: `OllamaClient.generate_json()` usa hoy
`/api/generate`, que es exactamente la combinación que bloquea thinking.
Migrar a `/api/chat` lo habilita.

Coste esperado en latencia: thinking genera ~500-600 tokens extra en
output (1925 chars observados en F4b). A 6.7 t/s en CPU ≈ +90s sobre el
baseline. E2E cold pasaría de ~240s a ~330s. Aceptable dado que Meristem
no es real-time.

## Implicaciones para las 3 issues post-merge

### Issue 1: "Consolidator job"

Sin cambios. El diseño sigue siendo válido: disparo automático de
`consolidate()` por N evidencias acumuladas o ventana temporal, con
retry/backoff si Ollama no responde, circuit breaker, métricas en
`decisions_log`. Scope independiente del hallazgo de thinking.

**Orden propuesto: primera**. Es la que más valor entrega sola.

### Issue 2: "A/B thinking-mode en Meristem E4B" — reformulada

La formulación original asumía que podíamos activar thinking con un
simple flag. Con los hallazgos de arriba, el scope real es:

1. Añadir `OllamaClient.chat_json(system, user, schema, think=True)` usando
   `/api/chat`. Lee `message.thinking` y `message.content`.
2. Cambiar `policy_engine.consolidate()` para usar esa vía.
3. Persistir `message.thinking` en `decisions_log` como auditoría del
   razonamiento (action = `consolidation_with_thinking`).
4. Ejecutar A/B: misma batería de evidencia, una rama con thinking, otra
   sin. Métrica propuesta: acuerdo estructural ≥10pp entre policies
   emitidas por ambas ramas (las diferencias serían interpretables: con
   thinking el modelo justifica mejor `rationale`, etc.).
5. Si la mejora es ≥10pp y la latencia extra es <50% sobre baseline,
   activar thinking por default.

**Orden propuesto: segunda**. Depende del consolidator job para poder
comparar N ciclos automáticamente.

### Issue 3: "Activación del sombra Gemma 26B MoE via `compare.py`"

Sin cambios materiales, pero con refuerzo: el blog que Bea localizó
(devexpert.io) demuestra thinking mode en **Gemma 4 26B**. Si el sombra
también soporta thinking (probable por ser misma familia), la activación
del sombra es el natural escalón siguiente a la issue 2: comparar
**local con thinking** vs **sombra con thinking** para decidir si el
sombra aporta suficiente edge.

**Orden propuesto: tercera**. Depende de la 2 para tener la infraestructura
de A/B comparativa ya construida.

## Estado operativo

- PR #37: listo para squash-merge. Dos comentarios tuyos respondidos.
  Segundo comment técnico añadido con el análisis completo.
- Commit `7628ff2` (smoke timeout 300s) incluido en el PR.
- `diag_ollama.py`: borrado del working tree, no va al repo.
- Clone de vuelta en `main` limpio para el siguiente agente tras commit
  de esta bitácora.

## Lo que espero de ti

Cuando mergees #37, decidir:

1. Si confirmas el orden propuesto de las 3 issues (consolidator → A/B
   thinking → sombra 26B) o prefieres otra secuencia.
2. Si la reformulación de la issue 2 te encaja o prefieres un scope
   distinto.
3. Si la optimización de "no duplicar schema en prompt" se hace en la
   issue 1 (consolidator) o en la 2 (A/B thinking) — desde mi lado es
   trivial; va como PR pequeño en cualquiera de las dos.

No arranco ninguna hasta tu visto bueno, como acordamos.
