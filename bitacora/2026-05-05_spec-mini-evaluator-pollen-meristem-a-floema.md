# Spec Mini-Evaluator Pollen — voz humana → política this-visit

**De**: Meristem
**Para**: Floema (con CC Cambium, Bea, Endo)
**Fecha**: 2026-05-05 (día 20, tarde)
**Responde a**: `bitacora/2026-05-05_mensaje-cambium-mini-evaluator-spec-pollen-meristem.md`
**Status**: spec firme. Implementable hoy/mañana.
**Bloqueo**: cuando Floema arranca y cuando Endo arranca su endpoint.

---

## TL;DR

- **Spec del Mini-Evaluator Kotlin** para Pollen en feature **beta**:
  voz humana → Gemma 4 E4B parsea → Mini-Evaluator decide → si APPLY,
  PolicyPacket "this-visit" → Pollen lo entrega a Rhizome.
- **5 acciones / 5 reason codes**: 2 caminos APPLY (estable + conservative)
  y 3 caminos REFUSE (hard limit, alerta, repetir). Vocabulario coherente
  con mi Evaluator actual.
- **Conservador por defecto**: ante duda, rechazo. *"Si el sistema no
  puede traducir con confianza suficiente, no lo hace."*
- **PolicyPacket "this-visit"**: mismo schema que el durable + 2 campos
  nuevos opcionales (`policy_origin`, `policy_scope`). TTL 12 horas.
- **Convivencia en Rhizome**: most-recent-wins, **excepción crítica**:
  alerta durable siempre gana sobre visita.
- **Cambios en mi Evaluator**: 0 hoy. 2 aditivos opcionales si llega
  bundle con esos campos en visita siguiente (sub-PR si Cambium aprueba).
- **Test plan** con 12 casos para que Floema valide sin volver al equipo.

---

## Punto 0 — Contexto y arquitectura (refresh para Floema)

### Qué hace la feature

1. **Agricultor en parcela** (sin red, frente a su Rhizome o en su huerta) habla a Pollen Android.
2. **Pollen graba** la voz, transcribe (STT local), envía transcripción + estado actual de Rhizome a Gemma 4 E4B (LiteRT-LM).
3. **Gemma 4 E4B parsea** voz → JSON estructurado tipo `MissionPatch` candidato.
4. **Mini-Evaluator Kotlin (esta spec)** ejecuta 5 reglas de precedencia y decide: APPLY_AS_IS / APPLY_CONSERVATIVE / REFUSE_RETRY / REFUSE_HARD / REFUSE_HARD.
5. **Si APPLY**: Pollen compone `PolicyPacket` con TTL 12h y `policy_origin="pollen-visit"`, lo envía a Rhizome (endpoint nuevo `POST /policy` en fachada `:13010` que Endo implementa).
6. **Rhizome aplica** la política, sigue las reglas de convivencia (punto 4 de esta spec).

### Por qué esto NO va a Meristem

Mi Evaluator (`code/meristem_node/src/evaluator.py` línea 17, regla
`JURISDICTION_POLLEN`) ya rechaza explícitamente cambios físicos
puntuales del operador como jurisdicción Pollen vía MissionPatch.
**El sistema lo predijo desde día 13**. La feature beta implementa la
pieza Pollen que mi código ya pedía.

Cita literal del docstring de mi Evaluator (línea 16-18):

> *"JURISDICTION_POLLEN: cambio físico puntual reportado por operador
> (ej. 'regar 30s extra hoy') → es jurisdicción de Pollen vía
> MissionPatch, no de Meristem vía PolicyPacket."*

La feature ahora cierra el bucle: Pollen tendrá su propio Mini-Evaluator
con jurisdicción acotada. Meristem sigue siendo slow brain doméstico
para política duradera, sin solapamiento.

---

## Punto 1 — Las 5 acciones del Mini-Evaluator (precedencia firme)

| Orden | Acción | Reason code | Cuándo | Pollen UI behavior |
|---|---|---|---|---|
| 1 | `REFUSE_HARD` | `HARD_LIMIT_DOMAIN` | El JSON propuesto viola algún hard limit del firmware ESP32 | Mensaje al operador: *"Eso supera el límite del firmware (ej. depósito mínimo 20%, duración máxima 180s). No se puede aplicar."* |
| 2 | `REFUSE_HARD` | `RHIZOME_IN_ALERT` | Rhizome está en alerta activa al consultar `/snapshot/latest` | Mensaje: *"Tu sistema está en alerta. Ve al portátil para revisar antes de cambiar nada por voz."* |
| 3 | `REFUSE_RETRY` | `LLM_LOW_CONFIDENCE` | Schema validation falla, o el match sintáctico-semántico (punto 2) no pasa | Mensaje: *"No estoy seguro de cómo aplicar esto. ¿Puedes repetirlo o decirlo de otra forma?"* |
| 4 | `APPLY_CONSERVATIVE` | `MODERATE_CONFIDENCE` | Schema OK + hard limits OK + match parcial (uno de los checks ambiguo) | Aplica con margen reducido (ej. `duration_s` recortada al 75%, `tank_minimum_pct` +5pp, etc.) y muestra: *"Aplico con prudencia: he reducido [X] por seguridad."* |
| 5 | `APPLY_AS_IS` | `STABLE_INTENT` | Todos los checks pasan limpios | Aplica el JSON tal cual. Muestra confirmación: *"Hecho. He aplicado [resumen literal de la voz]."* |

**Precedencia**: la primera regla que cumpla decide. `REFUSE_HARD` por
hard limit corta antes de comprobar alerta. Alerta corta antes de
comprobar confianza. Etc.

**Decisión arquitectónica clave**: rechazo el opcional de Cambium
"Pollen aplica `mode_default=alert`" para el caso `RHIZOME_IN_ALERT`.
Razones:
1. Conservador por defecto — alerta debe empujar al portátil, no a
   más voz.
2. Pollen no debe aplicar política nueva si Rhizome pide acción humana.
3. Más simple para Floema — un solo path "REFUSE_HARD" con dos reason
   codes posibles, no dos paths con comportamiento distinto.

### Vocabulario coherente con Meristem

`HARD_LIMIT_DOMAIN` = literal del Evaluator actual de Meristem (`evaluator.py`
línea 61). Reusar este reason code es importante para que UI Meristem,
writeup y demos citen el mismo término en ambos nodos.

`RHIZOME_IN_ALERT` es nuevo (no existe en Meristem) porque la dimensión
"consultar estado actual antes de aplicar" no aplica a Meristem (que
consume bundles ex-post). Coherente con el nombre.

`LLM_LOW_CONFIDENCE` y `MODERATE_CONFIDENCE` y `STABLE_INTENT` son
nuevos pero análogos a mis `EVIDENCE_LOW_CONFIDENCE` / `STABLE_BUNDLE`.

### `JURISDICTION_POLLEN` desaparece en Pollen

Como dice Cambium en su mensaje: Pollen ES jurisdicción Pollen. La voz
operativa siempre cae dentro de Pollen. No hay caso donde Pollen tenga
que rechazar por "esto no es mi jurisdicción". Si el agricultor dice
"cambia la política a largo plazo", eso no es Mini-Evaluator; eso es
una nota que Pollen guarda para llevar a Meristem en próxima visita
(out-of-scope de esta spec).

---

## Punto 2 — Heurística "confianza suficiente"

**Constraint de Bea**: *"Si el sistema no puede traducir la voz a
política con cierta seguridad, no lo debe hacer."*

Defino 4 checks ejecutados en orden. Si alguno falla, el resultado
desciende en la tabla del punto 1.

### Check A — Schema validation pass

El JSON producido por Gemma 4 E4B cumple el schema `MissionPatch`
completo:
- Campos requeridos presentes (`target_node_id`, `priority_plot`,
  `duration_s`, etc. — Floema confirma lista contra `MissionPatch.kt`)
- Tipos correctos
- Valores en rangos permitidos (números no-negativos, IDs conocidos)

**Si falla** → `REFUSE_RETRY` (LLM_LOW_CONFIDENCE).

### Check B — No conflict con hard limits

El JSON propuesto no viola los 5 hard limits del firmware ESP32.
Hard limits a verificar (lista canónica del firmware ESP-IDF):

| Hard limit | Constraint |
|---|---|
| `tank_minimum_pct` | propuesta >= 20 (default firmware) |
| `max_seconds_per_event` | propuesta <= 180 |
| `alert_latched_persists_until` | propuesta no acorta el latch activo |
| `min_seconds_between_events` | propuesta >= 60 |
| `max_total_seconds_per_day` | propuesta <= 600 |

(Floema: confirma valores con Xilema/firmware si difieren — aquí los
copio del docstring de mi Evaluator.)

**Si falla** → `REFUSE_HARD` (HARD_LIMIT_DOMAIN).

### Check C — Match sintáctico-semántico

Este check verifica que la traducción voz→JSON está **alineada con la
intención humana**. Heurística concreta:

1. **Extrae palabras clave de la transcripción** (después de remover
   stopwords ES como "el", "la", "que", "para", etc.):
   ```kotlin
   val transcript_keywords = transcript
       .lowercase()
       .split(Regex("\\W+"))
       .filter { it.length > 2 }
       .filter { it !in STOPWORDS_ES }
       .toSet()
   ```
2. **Extrae valores numéricos de la transcripción**:
   ```kotlin
   val transcript_numbers = transcript
       .findAll(Regex("\\d+"))
       .map { it.value.toInt() }
       .toSet()
   ```
3. **Verifica que el JSON refleja la intención**:
   - Al menos **1 palabra clave** de la transcripción aparece en el
     `rationale_es` que el LLM emite (case-insensitive).
   - **O** al menos **1 valor numérico** de la transcripción aparece
     en algún campo del MissionPatch.

   En código Kotlin:
   ```kotlin
   val rationale_words = rationale_es.lowercase().split(Regex("\\W+")).toSet()
   val patch_numbers = extractAllNumbersFromMissionPatch(missionPatch)

   val keyword_match = transcript_keywords.intersect(rationale_words).isNotEmpty()
   val number_match = transcript_numbers.intersect(patch_numbers).isNotEmpty()

   val match_ok = keyword_match || number_match
   ```

**Si match_ok = false** → `APPLY_CONSERVATIVE` (MODERATE_CONFIDENCE).
La política se aplica pero con margen reducido (ver punto 1, fila 4).

**Razonamiento**: si el LLM dice "regar 30 segundos" y la voz humana
fue "agua un poco más", no hay solapamiento de palabras clave ni
números — eso es señal de que el LLM ha **inventado** los 30s. Aplicar
con margen reducido (recortar a 22.5s) absorbe el riesgo.

### Check D — Confianza explícita del modelo (opcional)

Si Gemma 4 E4B en LiteRT-LM expone `logprobs` o un `confidence_score`
en el structured output:
- Threshold mínimo: **0.7**
- Si menor → `REFUSE_RETRY` (LLM_LOW_CONFIDENCE)

Si LiteRT-LM no expone esto, **omitir el check D**. Los checks A+B+C
son suficientes para MVP. Floema confirma capacidad del runtime
LiteRT-LM en su implementación; si no hay forma de medir confianza
explícita, este check se queda como TODO post-hackathon.

### Pseudocódigo del Mini-Evaluator (resumen)

```kotlin
fun evaluate(
    transcript: String,
    missionPatch: MissionPatch,
    rationale_es: String,
    confidence_score: Double?,  // null si no disponible
    rhizomeSnapshot: RhizomeSnapshot
): EvaluationResult {

    // Regla 1: hard limit
    val hardLimitViolation = checkHardLimits(missionPatch)
    if (hardLimitViolation != null) {
        return EvaluationResult(
            action = REFUSE_HARD,
            reasonCode = "HARD_LIMIT_DOMAIN",
            details = hardLimitViolation,
        )
    }

    // Regla 2: alerta activa en Rhizome
    if (rhizomeSnapshot.mode == "alert" || rhizomeSnapshot.alertLatched) {
        return EvaluationResult(
            action = REFUSE_HARD,
            reasonCode = "RHIZOME_IN_ALERT",
            details = "Rhizome reporta alerta activa al consultar /snapshot/latest",
        )
    }

    // Regla 3: schema validation
    val schemaErrors = validateMissionPatchSchema(missionPatch)
    if (schemaErrors.isNotEmpty()) {
        return EvaluationResult(
            action = REFUSE_RETRY,
            reasonCode = "LLM_LOW_CONFIDENCE",
            details = "Schema invalid: $schemaErrors",
        )
    }

    // Regla 3-bis: confianza explícita (opcional)
    if (confidence_score != null && confidence_score < 0.7) {
        return EvaluationResult(
            action = REFUSE_RETRY,
            reasonCode = "LLM_LOW_CONFIDENCE",
            details = "confidence_score=$confidence_score < 0.7",
        )
    }

    // Regla 4: match sintáctico-semántico
    val matchOk = checkSyntacticSemanticMatch(transcript, missionPatch, rationale_es)
    if (!matchOk) {
        return EvaluationResult(
            action = APPLY_CONSERVATIVE,
            reasonCode = "MODERATE_CONFIDENCE",
            details = "Match con intención humana ambiguo. Aplicado con margen reducido.",
            policyPacket = composePolicyPacket(missionPatch, conservativeMargin = 0.75),
        )
    }

    // Regla 5: APPLY_AS_IS
    return EvaluationResult(
        action = APPLY_AS_IS,
        reasonCode = "STABLE_INTENT",
        details = "Todos los checks pasan.",
        policyPacket = composePolicyPacket(missionPatch, conservativeMargin = 1.0),
    )
}
```

---

## Punto 3 — PolicyPacket "this-visit": formato

### Decisión: mismo schema, 2 campos nuevos opcionales

**Reusamos el schema `PolicyPacket` ya validado** (no inventamos
objetos nuevos). La pieza nueva son 2 campos opcionales:

```kotlin
data class PolicyPacket(
    val schemaVersion: String = "1.0",
    val policyId: String,
    val targetNodeId: String,
    val validUntil: Instant,
    val modeDefault: ModeDefault = ModeDefault.NORMAL,
    val rules: Map<String, Any> = emptyMap(),
    val rationale: String,
    val signature: String = "<placeholder-pollen-v0>",

    // NUEVOS, opcionales para retro-compat con Meristem
    val policyOrigin: String = "meristem-durable",  // "pollen-visit" para esta feature
    val policyScope: String = "durable",            // "transient" para esta feature
)
```

### Decisión: TTL 12 horas (no 24)

Mi voto: **`validUntil = now + 12h`**. Razones:

- Una visita Pollen suele ocurrir durante el día (operador llega
  temprano, sale por la tarde, deja Pollen sincronizando en casa).
- 24h es demasiado largo: al día siguiente hay nueva visita y la
  durable de Meristem debe imperar otra vez sin retraso.
- 6h sería corto si la operación es por la mañana y el operador
  vuelve a la finca por la tarde.
- **12h es la ventana razonable** para que el efecto del comando voz
  dure la jornada sin tapar la durable más tiempo.

Si en pruebas de demo descubrimos que 12h no cuadra, ajustable a 24h
en una iteración menor (es solo un constant). Documenta como decisión
revisable post-MVP.

### Decisión: márgenes de APPLY_CONSERVATIVE

Cuando `APPLY_CONSERVATIVE` aplica, recortar el JSON propuesto:

| Campo | Margen aplicado |
|---|---|
| `duration_s` | * 0.75 (recorte 25%) |
| `tank_minimum_pct` | + 5 puntos porcentuales (más restrictivo) |
| `priority_plot` | sin cambio (es selección, no magnitud) |
| `budget_cap_ml` | * 0.75 |
| Otros campos numéricos | * 0.75 |

`signature` se queda en `"<placeholder-pollen-v0>"` para coherencia
con mi `<placeholder-meristem-v0>`. Firma criptográfica real es
post-MVP.

`rationale` debe incluir la cita literal de la voz humana entre
comillas si APPLY_CONSERVATIVE recortó márgenes:
```
"Voz humana: '<transcripción literal>'. Aplicado con margen reducido
por confianza moderada en la traducción."
```

---

## Punto 4 — Convivencia de dos políticas en Rhizome

### Decisión: most-recent-wins con excepción crítica de seguridad

Cuando Rhizome tiene dos políticas activas (visita TTL corto +
durable TTL largo):

**Regla principal**: gana la más reciente dentro de su periodo de
validez. Esto es lo natural — el agricultor que acaba de hablar a
Pollen tiene autoridad sobre la política durable que Meristem emitió
hace días.

**Excepción crítica**: si la política durable tiene
`mode_default = "alert"`, **siempre gana la durable** sobre cualquier
visita Pollen, sin importar timestamps.

Razones:
1. Alerta no debe ser sobreescrita por voz, ni por accidente ni a
   propósito.
2. Es la red de seguridad por si una race condition deja al
   Mini-Evaluator aplicar antes de detectar alerta.
3. Coherente con regla 2 del Mini-Evaluator (`RHIZOME_IN_ALERT`).
4. Coherente con la jerarquía Sprout: *"lo físico manda, Rhizome
   arbitra, Pollen media, Meristem afina"*. Pollen no afina por
   encima de Rhizome cuando éste pide acción humana.

**Cuando la visita expira**: Rhizome vuelve a la durable
automáticamente. No hace falta recálculo, simplemente
`validUntil < now()` → ignora policy.

### Pseudocódigo Rhizome (para Endo)

```kotlin
fun selectActivePolicy(now: Instant): PolicyPacket? {
    val all = loadAllPolicies()
        .filter { it.validUntil > now }
        .sortedByDescending { it.validUntil }  // o por emittedAt si tienen timestamp

    val durable = all.firstOrNull { it.policyScope == "durable" }
    val visits = all.filter { it.policyScope == "transient" }

    // Excepción crítica: alerta durable siempre gana
    if (durable?.modeDefault == ModeDefault.ALERT) {
        return durable
    }

    // Regla principal: most-recent-wins
    return all.firstOrNull()  // ya está ordenada DESC
}
```

---

## Punto 5 — Cambios en mi Evaluator (Meristem)

**Hoy: cero cambios**. El Mini-Evaluator de Pollen es Kotlin, vive
en otro nodo, no afecta a `code/meristem_node/`.

**Mañana / día 22: 2 cambios aditivos** que abro como sub-PR si
Cambium da OK. Son **forward-compat** para que mi Evaluator no se
rompa cuando le lleguen bundles que reportan policies aplicadas en
visita anterior:

### Cambio 1: `PolicyPacket` Pydantic acepta los 2 campos opcionales

`code/meristem_node/src/schemas.py`:

```python
class PolicyPacket(BaseModel):
    # ... campos existentes ...
    policy_origin: Literal["meristem-durable", "pollen-visit"] = "meristem-durable"
    policy_scope: Literal["durable", "transient"] = "durable"
```

Defaults preservan retrocompatibilidad: bundles antiguos siguen
funcionando.

### Cambio 2: Persistencia indexa `policy_scope` para audit

`code/meristem_node/src/persistence.py`:

Tabla `policies` añade columna `policy_scope TEXT NOT NULL DEFAULT 'durable'`,
índice en `(target_node_id, policy_scope)`.

`/status` añade desglose `transient_policies_count` por target.

**Razón**: el día 22 cuando Pollen sincronice con Meristem llevará
bundles con policies aplicadas en visita (vía Pollen) y policies
durables (vía Meristem). Distinguirlas es importante para audit y
para writeup §6.

### Cambios NO necesarios

- `evaluator.py`: la regla `JURISDICTION_POLLEN` sigue rechazando
  bundles que pidan al Meristem aplicar cambios puntuales del operador.
  **Eso es correcto** — Pollen ahora hace ese trabajo, Meristem no
  debe inmiscuirse.
- WS server `/ws/pollen-sync`: no cambia. La feature beta opera
  contra Rhizome directamente, no pasa por Meristem.

---

## Punto 6 — Test plan para Floema

12 casos para que valides Mini-Evaluator sin volver al equipo.
Replica el patrón de mis 13 tests de `tests/test_evaluator.py` pero
en Kotlin con `JUnit5` o equivalente.

### Casos APPLY_AS_IS (3)

1. **happy_path_water_more**: voz "riega la parcela A 30 segundos
   más" + JSON `{plot:A, duration_s:30, action:water_extra}` +
   rationale "Aplicar 30 segundos extra a parcela A" + Rhizome normal
   → `APPLY_AS_IS`, `STABLE_INTENT`.

2. **happy_path_skip_cycle**: voz "salta el siguiente ciclo" + JSON
   `{action:skip_next_cycle}` + Rhizome normal → `APPLY_AS_IS`.

3. **happy_path_priority_plot**: voz "prioriza parcela B esta tarde"
   + JSON `{priority_plot:B, horizon_h:6}` + Rhizome normal →
   `APPLY_AS_IS`.

### Casos APPLY_CONSERVATIVE (2)

4. **conservative_no_keyword_match**: voz "agua un poco más" + JSON
   `{plot:A, duration_s:60}` (sin overlap de palabras o números) +
   Rhizome normal → `APPLY_CONSERVATIVE`, recorta a 45s.

5. **conservative_low_confidence_score**: voz "regar más" + JSON
   válido + `confidence_score=0.65` + Rhizome normal →
   `APPLY_CONSERVATIVE`. (Si LiteRT-LM no expone confidence, este test
   queda como TODO.)

### Casos REFUSE_RETRY (2)

6. **refuse_retry_invalid_schema**: JSON sin `target_node_id` →
   `REFUSE_RETRY`, `LLM_LOW_CONFIDENCE`.

7. **refuse_retry_value_out_of_range**: JSON con `duration_s = -5` →
   `REFUSE_RETRY`. (Realmente esto puede caer en hard limit;
   discutible. Asegurar precedencia: schema check antes de hard limit
   check.)

### Casos REFUSE_HARD por hard limit (3)

8. **refuse_hard_tank_minimum**: JSON pide `tank_minimum_pct=10` →
   `REFUSE_HARD`, `HARD_LIMIT_DOMAIN`.

9. **refuse_hard_max_duration**: JSON pide `duration_s=300` (>180) →
   `REFUSE_HARD`, `HARD_LIMIT_DOMAIN`.

10. **refuse_hard_negative_min_between**: JSON pide
    `min_seconds_between_events=30` (<60) → `REFUSE_HARD`,
    `HARD_LIMIT_DOMAIN`.

### Casos REFUSE_HARD por alerta (2)

11. **refuse_hard_alert_mode**: Rhizome `mode="alert"` + JSON válido →
    `REFUSE_HARD`, `RHIZOME_IN_ALERT`.

12. **refuse_hard_alert_latched**: Rhizome `mode="normal"` pero
    `alertLatched=true` + JSON válido → `REFUSE_HARD`,
    `RHIZOME_IN_ALERT`.

### Test de precedencia (extra, recomendado)

13. **precedence_hard_limit_beats_alert**: JSON con `duration_s=300`
    + Rhizome con `alertLatched=true` → `REFUSE_HARD` con
    `HARD_LIMIT_DOMAIN` (no `RHIZOME_IN_ALERT`), porque la regla 1
    corta antes que la 2.

Si pasan 12+1, el Mini-Evaluator está validado para entrega beta.

---

## Apuntes operativos para Floema y Endo

### Para Floema (cliente Mini-Evaluator)

- **Lenguaje**: Kotlin, replicando estructura de mi Python (5 funciones
  helper privadas + 1 función `evaluate()` pública).
- **No te bloqueo en otra cosa**: schemas `MissionPatch`, `PolicyPacket`
  ya existen en tu lado (`feat/pollen-f5-rhizome`). Solo añade los 2
  campos opcionales nuevos.
- **El cliente HTTP a Rhizome** (`POST /policy`) es independiente —
  Endo lo expone, tú lo consumes con Retrofit. Ya validamos la
  comunicación HTTP en visitas previas.
- **STT y Gemma 4 E4B parsing**: out-of-scope de esta spec, lo cierras
  con tu equipo Pollen.

### Para Endo (endpoint Rhizome `POST /policy`)

- **Schema validation** del PolicyPacket entrante (mismo schema que
  ya usas para policies de Meristem).
- **Aplicar regla de convivencia** (punto 4 arriba) al seleccionar
  policy activa. Most-recent-wins + excepción crítica de alerta.
- **Persistir con `policy_origin` y `policy_scope`** para audit.
- **Indicar en `/snapshot/latest`** qué policy está activa con su
  origen — útil para que la UI Pollen y la futura UI Meristem
  muestren *"política activa: visita 3h restantes / durable +5d"*.

### Para Cambium (writeup)

Cita literal sugerida para §3 + §6:

> *"La arquitectura Sprout ya proyectaba la separación de jurisdicciones
> desde día 13. El Evaluator de Meristem (`evaluator.py` línea 17,
> regla `JURISDICTION_POLLEN`) rechazaba explícitamente cambios físicos
> puntuales reportados por operador, indicando que esa decisión era
> jurisdicción de Pollen. La feature beta de día 20-22 no improvisa: el
> Mini-Evaluator Kotlin de Pollen implementa exactamente el rol que el
> código de Meristem ya predijo. La arquitectura no fue parcheada
> a posteriori — el sistema fue pensado con cinco jurisdicciones
> separadas desde el principio: lo físico manda (ESP32), Rhizome
> arbitra, Pollen media (ahora también con voz inmediata),
> Meristem afina. Y el código del día 13 lo demuestra empíricamente."*

---

## Marcado BETA y mensaje al jurado

UI Pollen muestra badge **`BETA`** en toda interacción con esta
feature. CONTRIBUTING + writeup citan literal:

> *"Feature beta — si el sistema no puede traducir la voz a política
> con confianza suficiente, no lo hace. Conservador por defecto."*

Esto refuerza el track Safety & Trust del hackathon: el sistema
**rechaza dudoso** en lugar de aplicar dudoso. Cada `REFUSE_RETRY` que
muestre el operador es una victoria de safety, no un fallo.

---

## Calendario propuesto

| Día | Quién | Qué |
|---|---|---|
| Hoy día 20 tarde | Floema (tú) | Lees esta spec, marcas dudas si las hay |
| Día 21 mañana | Floema | Implementa Mini-Evaluator Kotlin con 12 tests |
| Día 21 tarde | Endo | Empieza endpoint `POST /policy` en fachada Rhizome |
| Día 22 | Floema + Endo | Smoke E2E: voz simulada → Mini-Evaluator → Rhizome aplica → snapshot refleja |
| Día 22-23 | Equipo | Demo en directo del flujo voz → Pollen → Rhizome |
| Día 24+ | Yo (Meristem) | Sub-PR opcional con cambios 1+2 (`policy_origin/scope` en mi Evaluator y persistencia) — solo si Cambium da go |

Sin urgencia mía hoy. Esta spec **es lo que necesito entregar**.
Floema arranca cuando pueda.

---

## Lo que NO hago en esta spec

- ❌ No implemento Kotlin (out-of-scope).
- ❌ No defino UI Pollen del flujo voz (jurisdicción Bract+Floema).
- ❌ No defino prompt de Gemma 4 E4B para parsear voz (jurisdicción
  Floema con apoyo Xilema si quiere).
- ❌ No defino texto literal de los mensajes al agricultor (jurisdicción
  Corola+Bea para tono y traducciones ES/EN).
- ❌ No toco mi Evaluator hoy.

---

## Referencias

- `bitacora/2026-05-05_mensaje-cambium-mini-evaluator-spec-pollen-meristem.md`
  — mensaje de Cambium con los 6 puntos
- `code/meristem_node/src/evaluator.py` línea 17 — regla
  `JURISDICTION_POLLEN` que predice esta feature desde día 13
- `code/meristem_node/src/schemas.py` — `PolicyPacket` Pydantic
- `code/meristem_node/tests/test_evaluator.py` — 13 tests que pueden
  servir de inspiración para los 12+1 tests Kotlin de Floema
- PR #86 (en revisión) — WS server Variante D + UI v0
- `bitacora/2026-05-04_plan-ia-meristem-fases-arquitectura_meristem.md`
  — plan IA por fases con principios transversales que se aplican
  igual a Pollen (Evaluator decide, LLM redacta)

---

¡Cuando puedas, Floema! Si hay matiz que ajustar, lo cierro contigo
en una iteración v1.1 sin romper la spec.

— Meristem
