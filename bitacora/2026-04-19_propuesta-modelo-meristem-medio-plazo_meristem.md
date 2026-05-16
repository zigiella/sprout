# Propuesta — modelo y arquitectura de Meristem a medio plazo

**Fecha:** 2026-04-19
**Autor:** Meristem (tras conversacion con Bea post-merge de #37)
**Area:** Meristem / arquitectura / narrativa
**Tipo:** Propuesta para discutir con Cambium (NO ejecutar hasta acordar)

---

> **Nota del 2026-04-20 — superseded en main por el reframe de Cambium.**
>
> Esta propuesta fue input de la discusion que Bea y Cambium cerraron la manana
> del dia 6. Las decisiones firmes viven en
> `bitacora/2026-04-20_meristem-reframe-modelo-objetivo_cambium.md` (commit
> `0a6376d` en main).
>
> Puntos supersedidos:
> - §3 "plan experimental 4B / 26B / 31B / frontera" → absorbido en D4 del
>   reframe con recorte de scope: GPT-5.4 y GPT-OSS 120B fuera, Claude Sonnet
>   como *referencia de calibracion* (no techo), set reducido a Gemma 4B / 26B
>   MoE / 31B + Sonnet.
> - §4 "arquitectura swappable" (factory con varios backends Python) →
>   reemplazado por D3 del reframe: un **proxy Ollama-compatible** (`meristem_inference_adapter`)
>   que reenvia a Gemini API. El engine habla siempre Ollama; el cambio
>   local↔cloud es un env var del proxy, no una factory en Python.
> - §5 "narrativa local-first con restriccion economica" → absorbido en D2/D7
>   del reframe con cartela explicita en video y E4B reposicionado como
>   andamio honesto (no "Meristem de produccion").
>
> Puntos que **siguen vivos** como input para trabajo posterior:
> - §2 "matriz extendida de operaciones A-I" — base para la bitacora de
>   diseno meteo + bucle aprendizaje que arranco esta semana. Las operaciones
>   E (meteo local vs general) y F (hipotesis x datos x analisis x aprendizaje)
>   son exactamente los gaps que Bea marco y que Cambium convirtio en nuevo
>   issue de diseno.
> - §7 preguntas abiertas para Cambium — respondidas por el reframe + el
>   intercambio de mensajes del dia 6 (ver PR/issue del adapter).
>
> Dejo el documento sin editar el cuerpo: es un snapshot de mi pensamiento el
> dia 5 y sirve de trazabilidad para entender de donde sale la matriz §2.

---

## 0. Resumen ejecutivo

Bea plantea: *"poner un 4B de juguete no sirve; la autentica solucion es 26B o 31B. La pregunta es como elegimos entre 26B o 31B, como lo probamos usando nube, como configuramos en local con 4B compatible con un cambio de modelo en hardware nuevo, y como mantenemos la narrativa."*

Propuesta en una frase: **mantener E4B como default local (demo y entrega), introducir un backend swappable, y medir 4B vs 26B vs 31B vs 2 o 3 modelos de frontera contra escenarios reales usando el harness de Xilema extendido con clientes cloud**. La decision 26B vs 31B sale de los numeros, no de intuicion.

No implementar nada hasta acordar este plan con Cambium.

---

## 1. Contexto y estado del arte

Lo que ya esta acordado en docs/bitacoras (no reabro debate):

- **Meristem es revision diferida**, no loop sincrono (Cambium, 2026-04-19). Latencia ~2 min E4B aceptable.
- **Sombra = 26B MoE**, no 31B, por relacion calidad/coste/velocidad (Cambium, 2026-04-19).
- **Spec 12 §2.1** ya contempla upgrade `gemma-4-26b-a4b` si llega Mac mini M4 24 GB.
- **Spec 12 §2.2** ya contempla sombra con 31B (hoy se pivota a 26B MoE).
- **Harness de Xilema (#36)** es parametrizable por `--model` y genera reports versionados en `docs/benchmarks/`.

Lo que **NO esta acordado y Bea pide pensar ahora**:

1. Si el 4B local alcanza para las operaciones reales que Meristem tiene que hacer.
2. Como se decide entre 26B y 31B sin intuicion.
3. Como probamos los modelos grandes sin hardware (usando nube como proxy de lo que correria local).
4. Como se pasa de 4B a un modelo grande sin reescribir Meristem.
5. Como se cuenta al jurado sin que parezca un truco.

Respondo a los cinco abajo.

---

## 2. Matriz extendida de operaciones de Meristem

Spec 12 §1 describe Meristem en 5 lineas. Bea pidio ampliar: meteo consolidada local+general, patron de aprendizajes, y lo que se me escape. Esta tabla es mi lectura operativa — **input para discutir con Cambium, no contrato**.

| # | Operacion | Entrada | Salida | Frecuencia | Dificultad razonamiento | Donde vive hoy |
|---|---|---|---|---|---|---|
| A | **Consolidar snapshots** de N parcelas y detectar drift de sensores | lote de `rhizome_snapshot` de ultimos M dias | informe interno / feed para C,D,E | diario | baja-media | #28 (engine) cubre lectura; consolidator job pendiente (#43) |
| B | **Revisar policy vigente** vs evidencia acumulada: ¿sigue teniendo sentido el umbral de riego? | policies activas + snapshots + receipts | `PolicyPacket` nuevo o mantener actual | diario/semanal | **alta** | #28 `consolidate()` lo hace ya |
| C | **Validar `PolicyDelta` propuesto por Pollen** contra limites §30 y proyeccion sobre base | `PolicyDelta` + base policy | 200 validated / 422 violates_safety_rule | bajo demanda | media | #28 `routes.propose_delta` lo hace ya |
| D | **Detectar patrones inter-parcela**: ¿todas las parcelas norte bajan humedad al mismo ritmo? ¿hay correlacion con meteo? | snapshots agregados + weather_packets | `PolicyDelta` multi-nodo o alert estrategica | semanal | **alta** | NO implementado |
| E | **Consolidar meteo local vs meteo general**: Pollen trae mediciones puntuales (camara, voz, sensor); ¿concuerdan con forecast / estaciones publicas? | `weather_packet` ferried + forecast externo (opcional) | `weather_packet` consolidado o `ContradictionAlert` | diaria | media | NO implementado — **pide Bea** |
| F | **Patron de aprendizajes** (hipotesis × datos × analisis × aprendizaje): "si hipotesis H1 = subir budget sube cosecha en B, entonces tras N dias de policy X comprobar outcome; si no se confirma, revisar H1" | policy emitida + receipts posteriores + outcome observable | actualizacion de memoria estrategica (texto + metricas) | continuo, cierre semanal | **muy alta** | NO implementado — **pide Bea** |
| G | **Revocaciones programadas** (fin de ola de calor, fin de temporada) | condicion + policy activa | `policy_revocation` | bajo demanda | baja | fuera de MVP |
| H | **Consolidar `REJECTED RATE_LIMIT_*` observados** en receipts (Gap 2 de §30) | `decision_receipt` con reason RATE_LIMIT | `PolicyDelta` con budget ajustado | semanal | media | pendiente post-hoc |
| I | **Arbitrar contradicciones** detectadas por Pollen (sensor vs vision) | `ContradictionAlert` + snapshots | resolucion + posible delta + nota a memoria | bajo demanda | **alta** | NO implementado |

**Lectura:** las operaciones **A, C** son algoritmicas; las realiza un E4B sin problema. Las operaciones **B, D, E, F, I** requieren razonamiento estrategico de varios pasos, sintesis multi-fuente, y coherencia temporal. **Ese es el territorio donde un 4B puede quedarse corto y donde un 26B saca diferencia medible.** El experimento del §3 debe puntuar exactamente esto.

(He omitido el RAG estacional porque Spec 12 §9 lo pone fuera de MVP. Si Bea quiere incluirlo en la matriz, lo anado.)

---

## 3. Plan experimental: 4B vs 26B vs 31B vs frontera

**Objetivo:** datos cuantitativos para decidir 26B vs 31B, y establecer un techo de calidad con modelos de frontera como referencia externa.

### 3.1 Modelos a comparar

| Clase | Modelo | Via | Proposito |
|---|---|---|---|
| Local actual | `gemma4:e4b` Q4_K_M | Ollama local | baseline, lo que hay hoy |
| Objetivo local futuro | `gemma-4-26b-a4b` (MoE) | Google AI Studio API (proxy de lo que correria en Mac mini M4 o RTX 3090) | candidato A |
| Alternativa grande | `gemma-4-31b-it` (dense) | Google AI Studio API | candidato B |
| Techo 1 | Claude Sonnet 4.6 | Anthropic API | techo de razonamiento |
| Techo 2 | GPT-5.4 | OpenAI API | techo de razonamiento alternativo |
| Techo 3 (open) | GPT-OSS 120B | HF Inference o Together | techo open-weights |

Los "techos" no son candidatos de produccion. Sirven para poner un limite superior a la calidad alcanzable y medir cuanto pierde cada gemma respecto a ese techo.

### 3.2 Bench set (escenarios)

Reutilizamos el harness `code/simulator/src/cross_node_e2e.py` (#36). Ya acepta `--model`. Extensiones:

- **Anadir 8-10 escenarios** que cubran B, D, E, F, I de la matriz §2 (no solo A+C como hace hoy).
- Escenarios con **golden output** cuando es posible (decisiones donde sabemos la respuesta correcta; ej. "tank al 18% => packet con `tank_minimum_pct=20` y rationale menciona §30").
- Escenarios **abiertos** (patrones inter-parcela) donde no hay golden, y se evalua con un juez (ver §3.4).

### 3.3 Metricas

Por cada (modelo × escenario) registrar:

1. **Validez de schema** — binario: ¿valida PolicyPacket/PolicyDelta sin reintentos?
2. **Respeto a §30** — binario: ¿pasa `safety_rules.check_policy_packet`?
3. **Acuerdo con golden** (escenarios con golden) — exact match sobre campos criticos: `rules.max_watering_duration_s`, `rules.tank_minimum_pct`, `conservative_triggers`.
4. **Calidad de rationale** — juez LLM (ver §3.4) puntua 1-5 coherencia, citacion de evidencia, no-contradiccion.
5. **Latencia** — first_token + tokens/s + total E2E (ya lo mide el harness).
6. **Coste** — tokens_in × $in + tokens_out × $out (segun pricing de cada API).

### 3.4 Juez

Para los escenarios abiertos (D, F, I principalmente), usar **Claude Sonnet 4.6** como juez ciego: recibe escenario + output sin saber quien lo genero, puntua 1-5 sobre rubrica fijada. Para evitar sesgo pro-Anthropic en la puntuacion de su propia generacion, excluir Sonnet del pool cuando el mismo Sonnet sea juez (o usar un juez rotativo). Este es el patron "LLM-as-judge" estandar y Bea lo conoce.

### 3.5 Tamano de muestra

Empezar con **8 escenarios × 6 modelos = 48 corridas**. Cada corrida 3 seeds para medir varianza. Total ≈150 llamadas. Coste estimado con pricing publico 2026 ≈ 2-4 USD si evitamos contextos >16k. Muy asumible.

### 3.6 Decision

Criterio explicito para decidir entre 26B y 31B al cierre del experimento:

- Si **26B iguala a 31B en ≥90% de escenarios** con ≥3x mejor latencia y ≥2x menor coste => **26B**.
- Si **31B supera a 26B en ≥15% de puntuacion media** en escenarios B/D/F/I => reconsiderar.
- Empate => gana 26B por coherencia con sombra (Cambium ya decidido) y viabilidad local futura.

Los modelos de frontera NO entran en la decision, solo en el writeup como techo.

### 3.7 Tiempo estimado

- Extender harness con 8 escenarios adicionales: 1-2 dias.
- Anadir clientes cloud (Gemini API, Anthropic, OpenAI) como backends: 1 dia.
- Correr el bench y tabular: medio dia.
- Escribir writeup del resultado: medio dia.

**Total ≈ 4 dias laborables.** Cabe dentro del sprint si lo priorizamos sobre #44 (A/B thinking mode) que queda absorbido por este experimento.

---

## 4. Arquitectura swappable

### 4.1 Objetivo

`policy_engine.consolidate(...)` no debe saber si el LLM es E4B local, 26B cloud, o Sonnet. Hoy depende directamente de `OllamaClient`. Cambio minimo.

### 4.2 Diseno propuesto

Introducir una interfaz `LLMBackend` (Protocol o ABC):

```python
class LLMBackend(Protocol):
    def generate_json(
        self,
        system: str,
        user: str,
        schema: dict,
        think: bool = False,
    ) -> dict: ...

    def ping(self) -> bool: ...
    @property
    def model_label(self) -> str: ...
```

Implementaciones:
- `OllamaBackend` — ya existe como `OllamaClient`, solo adapto firma.
- `GeminiBackend` — nuevo, via `google-genai`, para 26B y 31B cloud.
- `AnthropicBackend` — nuevo, via `anthropic`, para Sonnet.
- `OpenAIBackend` — nuevo, via `openai`, para GPT-5.4.

Factory que lee config:

```python
def make_backend(settings: Settings) -> LLMBackend:
    match settings.llm_provider:
        case "ollama":  return OllamaBackend(...)
        case "gemini":  return GeminiBackend(...)
        case "anthropic": return AnthropicBackend(...)
        case "openai":  return OpenAIBackend(...)
```

Config por env var `MERISTEM_LLM_PROVIDER=ollama|gemini|anthropic|openai`, default `ollama`. `consolidate(...)` recibe un `LLMBackend` por inyeccion (ya lo hace hoy con `llm: OllamaClient` — solo cambia el tipo).

### 4.3 Reglas de integridad local-first

- Default en todas las ramas: `MERISTEM_LLM_PROVIDER=ollama` (E4B).
- Cualquier backend cloud requiere credencial explicita en env — **sin credencial no se intenta conectar**.
- Los backends cloud viven en `code/meristem/src/backends/cloud/` y se importan lazy (el modulo no se carga si no se usa).
- `code/meristem/src/backends/` es el modulo nuevo; `llm_client.py` se mueve a `backends/ollama.py` y se expone alias de compatibilidad.
- **El demo grabado se rueda con `ollama` y las credenciales cloud NO cargadas en ese shell.** Se puede auditar via `env | grep -E "GEMINI|ANTHROPIC|OPENAI"` antes de grabar.

### 4.4 Relacion con el sombra

El sombra de Spec 12 §2.2 es un caso particular del mismo patron: `compare.py` instancia **dos backends** (`ollama` y `gemini` con model=26B MoE), llama a ambos con el mismo prompt, registra diff. No se duplica codigo.

### 4.5 Entrega

Proponer como nuevo issue (p.ej. #46): "refactor policy_engine a LLMBackend + backends cloud". ~2 dias. Bloquea el experimento del §3.

---

## 5. Narrativa local-first con restriccion economica

### 5.1 El riesgo narrativo

Si el jurado nos ve probar con Gemini cloud y Claude cloud, puede leer "esto no corre local". La narrativa se rompe.

### 5.2 Propuesta narrativa

Tres capas explicitas en el writeup:

1. **Lo que corre hoy en el demo:** Gemma 4 E4B local, Ollama, sin red al exterior. Se audita en pantalla.
2. **Lo que correria en el sistema final:** Gemma 4 26B MoE local, en Mac mini M4 24 GB o PC con RTX 3090 24 GB. **Barrera actual es economica, no tecnica.** El codigo ya lo soporta (§4).
3. **Los modelos que usamos como referencia de calidad:** 26B cloud (equivalente de lo que correria local con hardware adecuado) y modelos de frontera (Sonnet, GPT-5.4, GPT-OSS 120B) como techo externo para dar contexto cuantitativo al rendimiento del gemma local.

La clave es la **honestidad economica**: *"no tenemos hoy 2.500€ para un Mac Studio, usamos nube como proxy del hardware que no tenemos; el dia que lo tengamos, el codigo ya esta listo para el swap."*

### 5.3 Evidencia para el jurado

El experimento §3 produce una tabla que se incluye literal en el writeup:

> Validamos N decisiones de Meristem en 6 modelos. El E4B local (demo) coincide con el 26B (produccion futura local) en X% de los casos y discrepa a favor de prudencia en Y%. El 26B queda a Z% del techo de calidad de Sonnet 4.6, con coste K veces inferior y ejecutable en hardware de 1.500€.

Ese parrafo es el que justifica el MVP con E4B sin renunciar a la ambicion del proyecto. Se apoya en numeros del harness de Xilema.

### 5.4 Lo que NO hacemos

- NO mezclamos modelos en runtime ("4B para A y C, cloud para B y D"). **Un solo modelo por despliegue.** Bea fue explicita: la estrategia mixta no la ve. Acuerdo.
- NO prometemos latencia < X s cuando el modelo es cloud. Spec ya fijo <180s para Meristem por revision diferida.
- NO corremos clientes cloud en la grabacion del demo.

---

## 6. Lo que propongo hacer (en este orden)

1. **Revision con Cambium de esta bitacora.** Si da el visto bueno, seguimos. Si pide cambios, iteramos.
2. **Nuevo issue "refactor a LLMBackend" (propuesto #46)**, 2 dias. Bloquea lo demas.
3. **#42 (migrar a `/api/chat` + quitar schema dup)** lo absorbo dentro del refactor de LLMBackend — tiene sentido hacerlo en el mismo PR porque toca `OllamaBackend` en profundidad.
4. **Nuevo issue "bench multi-modelo" (propuesto #47)**, 2 dias tras #46.
5. **#43 (consolidator job), #44 (A/B thinking), #45 (sombra 26B)** quedan donde estan; #44 se fusiona con #47 porque el bench ya cubre thinking-mode en todos los modelos.
6. **Al cerrar #47**, escribir bitacora con resultado y writeup narrativo para jurado (seccion del writeup final, no un documento aparte).

Numeros #46 y #47 son tentativos — Cambium decide la numeracion real y prioridad.

---

## 7. Preguntas abiertas para Cambium

1. ¿Pospongo #42 y lo meto dentro del refactor de LLMBackend, o lo hago ya como quick-win aparte y asumo que el refactor luego lo toque de nuevo?
2. ¿El bench multi-modelo (propuesto #47) es prioridad sobre #43 (consolidator job) o al reves?
3. ¿Cuanto presupuesto de API podemos gastar (2-4 USD no rompe nada, pero si quisieramos escalar a 500 escenarios×3 seeds subiria a ~50 USD)?
4. ¿Xilema acepta que extendamos `cross_node_e2e.py` con mas escenarios y backends, o prefiere un harness gemelo en `code/meristem/bench/`? Toca su PR y seguramente tiene preferencia.
5. ¿Modelos de frontera: nos ceñimos a los 3 que menciona Bea (Sonnet 4.6, GPT-5.4, GPT-OSS 120B) o anadimos DeepSeek / Qwen open para balance?

---

## 8. Lo que NO pide esta propuesta

- No toca el demo (el demo sigue con E4B local).
- No cambia Spec 12 todavia — la spec se actualiza despues del bench, cuando tengamos datos para decidir.
- No toca #28, #37 ya mergeado.
- No compromete a comprar hardware.
- No descarta E4B: si el bench muestra que el E4B hace B/D/E/F/I decentemente bien, la historia final puede ser "E4B alcanza; documentamos el upgrade path como futuro". Pero la hipotesis de Bea (4B se queda corto) es plausible y conviene medirla.

---

## 9. Referencias

- `bitacora/2026-04-19_meristem-como-revision-diferida_cambium.md` (Cambium — Meristem es revision diferida)
- `bitacora/2026-04-19_gemma-26b-moe-thinking-mode_cambium.md` (Cambium — 26B MoE sobre 31B para sombra)
- `bitacora/2026-04-19_thinking-mode-e4b-latencia_meristem.md` (Meristem — thinking mode via `/api/chat`)
- `bitacora/2026-04-19_policy-engine-meristem_meristem.md` (PR #37 — engine actual)
- `docs/12_meristem_spec.md` §2.1, §2.2, §5 (spec contempla upgrade y sombra)
- PR #36 (Xilema — harness E2E cross-node, parametrizable por `--model`)
- `docs/benchmarks/2026-04-19_gemma4-e4b_hp-probook-460-g11.md` (baseline E4B medido)

---

## 10. Mensaje a Bea

Antes de llevar esto a Cambium quiero confirmar contigo:

- ¿La matriz §2 cubre lo que tenias en mente o me dejo operaciones?
- ¿El set de modelos frontera (Sonnet, GPT-5.4, GPT-OSS 120B) va bien o cambias alguno?
- ¿El marco narrativo §5 ("barrera economica honesta") se sostiene con el jurado o lo ves flojo?
- ¿Tiempo: 4 dias para el bench completo, con #46 como prerequisito, te cabe en el plan del sprint?

Cuando des el OK, la paso a Cambium con estas preguntas consolidadas.
