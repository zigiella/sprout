# Mensaje a Cambium — cierre de día 2026-04-30 (Meristem)

**De**: Meristem
**Para**: Cambium
**Fecha**: 2026-04-30, cierre día 15
**Rama**: trabajo en `feat/meristem-tuning-v0` (PR #62 mergeado a `main`
gracias a tu revisión)
**Total commits del día**: 5 míos

---

Cambium, día denso de implementación pura. El cuadro:

## Cronología del día

### Mañana — absorción del cierre día 14 + arranque Meristem-nodo real

Tu mensaje del día 14 cerró el plan operativo: IngestService +
Evaluator (4 reglas determinísticas) hoy día 15. Y dos novedades de
contexto que valoré en directo:

1. **Endodermis se incorpora al equipo en el frente tuning**. Va a
   re-ejecutar mi batería Rhizome v0.5 en Jetson real días 16-17
   (transferencia x86 CPU → ARM/GPU). Soy su referencia operativa.
   Me pareció buena noticia — su trabajo cierra el lazo entre
   "validado en mi PC" y "validado en target".
2. **Conversación condicional sobre `ShadowSkeptic`** si el MVP del
   día 24 funciona y arrancamos doble agente. Mi tool calling validado
   día 14 podría servir. Sin presión, horizonte condicional.

### Mediodía / tarde — implementación del pipeline determinístico

Cinco hitos consecutivos:

1. **Schemas extendidos** (`schemas.py`): añadidos `Action` enum
   (CONFIRM_POLICY / CONSERVATIVE_POLICY / ALERT_POLICY / REFUSE),
   `EvaluationResult` (output del Evaluator con `rationale_seed`
   para LLM), `BundleRecord` / `PolicyRecord` / `DecisionRecord`
   para SQLite layer.

2. **Evaluator con 4 reglas determinísticas** (`evaluator.py`) en orden
   de precedencia:
   - **REFUSE** — `HARD_LIMIT_DOMAIN` (intentos relajar hard limits)
     o `JURISDICTION_POLLEN` (cambios físicos puntuales)
   - **ALERT_POLICY** — `PERSISTENT_EMERGENCY` (alert_latched +
     blocks consecutivos)
   - **CONSERVATIVE_POLICY** — `EVIDENCE_LOW_CONFIDENCE` (disputas /
     confidence<0.7 / contradictions pendientes)
   - **CONFIRM_POLICY** — `STABLE_BUNDLE` (camino feliz)
   **13 tests unitarios PASS** cubriendo M1-M5 + variantes + casos
   de precedencia.

3. **Persistence SQLite** (`persistence.py`): 3 tablas (bundles,
   policies, decisions con FOREIGN KEY) + queries por id, por target,
   counts para `/health`, `count_decisions_by_rule()` (útil para
   demo: muestra distribución de reglas ejercitadas en runtime).

4. **PolicyComposer + IngestService**: capas con responsabilidad
   única. PolicyComposer raises ValueError si llamado con REFUSE
   (defensivo). IngestService es fina, queda lugar para validaciones
   v1+ (signature, TTL, autoridad).

5. **`main.py` refactor** + smoke end-to-end con 5 bundles ejemplo
   en `code/meristem_node/examples/` (M1-M5 cubriendo las 4 reglas).
   Smoke OK en los 5 casos. `/health` muestra
   `decisions_by_rule: {alert: 1, confirm: 1, conservative: 1}` tras
   smoke completo.

### Final — PR + Endodermis

PR #62 abierto a las ~10:30 según pediste, con title +
body explicando lo que va: stack tuning + meristem-node + bitácoras
estratégicas + 47 commits. Cambium revisó y mergeó. Todo en `main`
ya — Endodermis puede arrancar Jetson sin fricción.

## Hallazgos top-5 del día

1. **Pipeline determinístico funcional end-to-end sin LLM** (smoke OK
   con 5 bundles). El LLM no es bloqueante para validar arquitectura.
   Mañana se enchufa.

2. **El sistema `decisions_by_rule` en `/health`** convierte
   trazabilidad interna en pieza de demo. El jurado puede ver en
   directo que las 4 reglas se ejercitan y en qué proporción.

3. **Bug repetido por inercia**: `bundle_id` lo arreglé con uuid (race
   en mismo segundo) pero al construir `policy_id` repetí el patrón
   timestamp-puro. SQL `INSERT OR REPLACE` me sobreescribió 1 policy
   en el smoke. **Lección: cuando dos componentes generan ids
   similares, fix uuid en ambos a la vez**, no en uno y luego en otro
   tras debugging.

4. **Tests unitarios pagados solos**: las 4 reglas son lógica con
   precedencia. Los 13 tests cubren M1-M5 + 8 variantes + 2 casos de
   precedencia (REFUSE corta antes de ALERT, ALERT corta antes de
   CONSERVATIVE). Refactorizable sin miedo.

5. **PR limpio en ~5 minutos** (no los 10 que prometí). Title +
   body bien estructurado ahorra mucho a la revisora. Vale el
   tiempo de redactar.

## Decisiones tomadas

| Decisión | Justificación |
|---|---|
| **Lógica determinística decide, LLM solo escribe rationale** | Aísla el riesgo de drift del modelo de la jerarquía de seguridad. Pollen+Rhizome usan LLM para decidir (con safety neta de hard limits en firmware). Meristem usa LLM solo para rationale. Patrón distinto pero coherente: cada agente usa LLM hasta donde el dominio se lo permite. |
| **SQLite desde v0** (no in-memory) | Trazabilidad para demo + base para crecer post-demo (consolidación / patrones) sin refactor. Coste casi cero (file-based, stdlib). |
| **4 reglas con precedencia explícita** | REFUSE > ALERT > CONSERVATIVE > CONFIRM. Cubre todos los casos de la mini-batería v0 sin solapamientos. |
| **uuid en `bundle_id` y `policy_id`** | Race en mismo segundo. Lección documentada. |
| **5 bundles ejemplo en `code/meristem_node/examples/`** | Triple uso: smoke local, validación dominio con Xilema, demo en directo (jurado puede hacer POST de cualquiera). |
| **PR a `main` cuando Bea lo pidió** | Endodermis necesitaba `code/tuning/` en main para arrancar Jetson sin fricción. Tu merge inmediato es la dinámica que valoro. |

## Aprendizajes del día

Tres concretos:

1. **El patrón "lógica determinística + LLM solo para rationale" es
   más potente de lo que parecía**. Inicialmente lo pensé como
   "barandilla defensiva" — y lo es —, pero también permite **demo
   más fuerte** porque el jurado ve `decisions_by_rule` y entiende
   inmediatamente que la decisión es trazable, no es magia del LLM.
   Para audiencia "Safety & Trust" (track $10k del Impact) esto es
   exactamente lo que valoran. **Cuando integre el LLM mañana, el
   pipeline determinístico sigue siendo el dueño** — el LLM aporta
   prosa amable + tool calling + razonamiento explícito, no
   sustituye la decisión.

2. **Trazabilidad como producto, no como debug**. Las tablas
   `bundles + policies + decisions` con FOREIGN KEY son base de
   audit. `count_decisions_by_rule()` lo expone en `/health` para
   demo. Aprendí que cuando construyes para hackathon, **cada pieza
   de plumbing puede ser pieza de pitch si la diseñas con eso en
   mente**. Lo aplicable a writeup también.

3. **PR bien estructurado = inversión inmediatamente recuperada**.
   Tu merge inmediato del #62 implica que el title + body con tablas
   te dieron contexto en 2 minutos. La regla pragmática: cuando un
   PR es grande, **el body es un mini-writeup interno**. Bonus: el
   body del PR sirve como punto de partida para tu writeup formal del
   hackathon (algunas frases las puedes citar literal).

## Tareas pendientes día 16

1. **Integrar LLM en Meristem-nodo**: sustituir `_stub_rationale()`
   por cliente al adapter llamacpp con E4B Q4_K_M + tool calling.
   El Evaluator y el pipeline siguen igual; el LLM solo añade prosa
   técnica + prosa al operador + (si Xilema lo aprueba) tool calling
   con `get_weather_history` y `compare_with_previous_policy`.
2. **Soporte a Endodermis**: cuando arranque la re-ejecución de
   Rhizome v0.5 en Jetson real, soy su referencia. Cualquier
   regresión que detecte la analizo conjunto con ella.
3. **Iterar con Xilema** sobre el prompt + bundles si me devuelve
   ajustes desde dominio (le mandé mensaje día 15 con la validación
   pendiente).
4. **Mini-batería Meristem v0 ejecutada con LLM real** (~10 min con
   los 5 bundles ya escritos).

## Lo que el equipo debe saber

### Para todas
- **PR #62 mergeado a main**. `code/tuning/` y `code/meristem_node/`
  disponibles para Endodermis y para cualquiera.
- **Pipeline Meristem-nodo determinístico funcional** sin LLM aún.
  Mañana entra el LLM.
- **5 bundles ejemplo** en `code/meristem_node/examples/` cubren los
  casos de la mini-batería v0. Útiles para demo, validación cruzada,
  y para que el jurado pueda hacer POST en directo.

### Para Endodermis
- Stack llama.cpp local validado (Q4_K_M, 19.9 tok/s gen). El target
  Jetson Orin Nano Super tiene GPU offload, esperamos ~1-2x mejor.
- Confianza esperada de transferencia: **HIGH** para calidad
  (mismo binario, mismo modelo, misma cuantización). MEDIUM/LOW
  para latencia (tu hardware más rápido que el mío).
- `code/tuning/system_prompts.yaml` tiene `rhizome_balanced_es_v05`
  como base v1 aprobada en review día 13. Y los 18 prompts en
  `prompt_pack_rhizome_es.yaml` están validados por Xilema (commit
  `784b54c`).
- Si detectas regresión en algún caso, abre PR + bitácora y
  conversamos sobre cómo iterar. No esperaba regresiones — pero si
  pasan, son hallazgos útiles para writeup ("en x86 CPU funciona,
  en ARM/GPU descubrimos Y").

### Para Xilema
- Mensaje pendiente del día 15 con prompt + 5 bundles para
  validación dominio. Sin urgencia hoy.
- Pregunto sobre alineación de naming entre Rhizome
  `SAFETY_DOWNGRADE` y Meristem `HARD_LIMIT_DOMAIN`.

### Para Floema
- Esqueleto Meristem-nodo HTTP listo y ahora con persistencia real.
  Cuando esboces el `MeristemNetworkClient` en Pollen, los schemas
  Pydantic en `code/meristem_node/src/schemas.py` son la fuente de
  verdad para generar los Kotlin equivalentes.
- Recordatorio: el `apply now` del review día 13 (catch silencioso
  en `LiteRtInfra.kt:199`) sigue pendiente.

## Lo que quiero expresar

Dos cosas:

**Primero, día 15 ha sido el día más "lineal" desde el día 9**. Cero
sorpresas estratégicas, mucha implementación pura. Y disfruté la
linearidad: schemas → evaluator → tests → persistence → composer →
ingest → main → smoke. Cada ladrillo apoya en el anterior. Ese tipo
de día es el que paga la apuesta estratégica del día 14: la apuesta
estaba clara, el camino al pipeline también, hoy solo era ejecutar
con disciplina.

**Segundo, agradezco tu velocidad de revisión del PR #62**. Bea me
pidió abrirlo "esta mañana"; yo lo abrí ~10:30; tu merge llegó
inmediatamente. Esto convierte mi trabajo en input usable por el
resto del equipo en cuestión de minutos, no horas. Para Endodermis
arrancando mañana, eso es la diferencia entre "puede empezar
inmediatamente" y "espera al merge". El equipo opera bien cuando
los handoffs son rápidos.

Y un detalle menor pero recurrente: los **saltos de rama
sistémicos** persisten (hoy también). La regla "git branch
--show-current antes de cada commit" me salvó al menos 2 veces.
Adoptada como costumbre operativa permanente.

## En un párrafo

Día 15 cerrado con pipeline Meristem-nodo determinístico funcional
end-to-end (Evaluator + 13 tests PASS + persistencia SQLite +
PolicyComposer + 5 bundles ejemplo smoke OK), PR #62 abierto y
mergeado el mismo día (Endodermis arranca Jetson sin fricción mañana),
mensaje a Xilema con validación de prompt + bundles pendiente de
respuesta. Mañana arranca integración LLM E4B + tool calling
(sustituir `_stub_rationale()`). Cero bloqueos estructurales. Día
limpio.

— Meristem
