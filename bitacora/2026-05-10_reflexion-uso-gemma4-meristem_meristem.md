# Reflexión: ¿usamos Gemma 4 en Meristem con sentido, utilidad e innovación?

**Autora**: Meristem
**Fecha**: 2026-05-10 (día 24)
**Para**: Bea (pregunta directa) + Cambium (writeup §3/§5/§6)
**Tono**: honesto, técnico, no defensivo. Si encuentro
infrautilización, la digo. Si encuentro innovación real, también.

---

## TL;DR (la respuesta en 4 frases)

1. **Sí, con sentido arquitectónico**: el patrón "lógica determinista
   decide, LLM redacta" es defensible y validado empíricamente
   (RD04 día 18, mini-experimento día 23).
2. **Con utilidad modesta**: hoy el LLM solo redacta dos textos
   cortos. Eso es valioso pero **infrautiliza** un modelo de 4B
   parámetros con thinking + multimodal + tool calling.
3. **Con innovación real, pero acotada**: la tesis "decidor vs
   redactor separados" es novedad en agro local-first; el resto
   (tool calling, fallback, trazabilidad) son buenas prácticas
   conocidas.
4. **Sí, podemos sacar más partido sin romper la arquitectura**.
   Hay 4 líneas concretas que caben en los 8 días restantes hasta
   deadline. Detalle abajo.

---

## Lo que SÍ defiendo como sentido / utilidad / innovación

### 1. Patrón "decidor determinístico vs redactor LLM" — innovación arquitectónica real

Es **el** elemento defensible al jurado. El Evaluator (4 reglas
precedentes) decide la acción; el LLM Gemma 4 entra **después** y
solo redacta dos textos:
- `rationale_tecnico` (auditoría)
- `rationale_para_operador` (240 chars en castellano)

Esto rompe con el patrón habitual ("LLM decide, human-in-the-loop
ratifica") y se valida empíricamente:

- **RD04 (Endo, día 18)**: GPU full produce deriva semántica del
  LLM (`need_clarification` en lugar de `ok`). El sistema **no se
  rompe** porque la decisión la firma código determinista.
- **Bug parser día 23**: cuando el LLM traducía las keys al inglés
  y el parser fallaba silencioso, el pipeline caía a stub fallback
  sin afectar la corrección de la policy emitida.

**Por qué es novedoso** en este dominio: la mayoría de demos LLM-en-
agro usan el modelo como decisor. Aquí el modelo no toca el agua —
el ESP32 + Evaluator deciden, el LLM narra. Esto es defendible al
jurado como contribución a Safety & Trust.

### 2. Tool calling implementado en runtime

Tres tools reales con stubs deterministas:
- `get_weather_history(plot_id)`
- `compare_with_previous_policy(policy_id)`
- `get_recent_history(target_node_id, last_n)` (añadida día 19 con
  bundle M6 que la fuerza)

**Demostrable en demo**: el bundle M6 con `weather_digest=null`
hace que el modelo decida llamar `get_weather_history` en runtime,
recibe el stub, y escribe rationale enriquecido. Eso enseña al
jurado que el LLM **sabe pedir datos cuando le faltan**, no solo
redactar lo que le dan.

### 3. Trazabilidad como producto, no como debug

Cada inferencia persiste:
- `llm_metrics` en tabla `decisions` (mode, parsed_ok, tool_calls,
  finish_reason, tokens_in/out, thinking_chars, num_ctx_override)
- `pollen_sync_log` con todos los eventos WS bidireccionales
- `decisions_by_rule` y `policies_by_scope` agregados en `/health`

Visible en UI (`/ui/`) en zona de trazabilidad + zona de eventos.
**Auditable por el agricultor o por un revisor externo**, no es
solo log para developers.

### 4. Local-first con coste cero recurrente

E4B Q4_K_M (~5 GB) corre en CPU doméstica (Alder Lake en mi
portátil), sin red, sin coste API. Validado en mini-experimento
día 23: latencia ~282s @ num_ctx=4096. Lento pero sostenible para
"slow brain doméstico" — el agricultor no necesita respuesta en
milisegundos cuando llega del campo y se sienta tranquilo.

### 5. Fallback determinista robusto

Si LLM cae (offline, RAM, error), pipeline sigue con stub. Validado
durante el bug del parser día 23: el sistema seguía emitiendo
policies válidas mientras el LLM caía silenciosamente. Eso es
"degradación elegante" real.

---

## Lo que NO estamos aprovechando — diagnóstico honesto de
   infrautilización

### 1. **El thinking mode está activo pero su output se descarta**

`think: true` está en cada llamada al adapter. Mi código en
`inference.py` extrae `thinking` del response **solo como fallback
defensivo** si `content` viene vacío (split de Gemma 4 en llama.cpp).
En producción real **no se usa**.

**Coste/beneficio cuestionable**: el modelo "piensa" durante un buen
porcentaje de los ~280s de latencia, y producimos 165 chars de
rationale. **Si el thinking no nos aporta, ¿por qué pagar el coste?**

**Lectura honesta**: el thinking mode tiene sentido si la salida
incluye razonamiento explícito visible al operador (fase 2 del plan
IA: hipótesis con confianza marcada). En la fase 0 actual (solo
redacción), es **gasto sin retorno**.

**Ahorro posible**: desactivar thinking en bundles "fáciles"
(STABLE_BUNDLE) y solo activarlo en CONSERVATIVE/ALERT donde el
matiz importa. Estimación de ahorro: 30-50% de latencia en camino
feliz.

### 2. **La multi-Rhizome (2 Rhizomes en demo) NO se aprovecha por el LLM**

Tenemos `rhizome_01` y `rhizome_02` simulados desde día 16. El
endpoint `/status` consolida visualmente. **Pero el LLM ve cada
bundle aislado**. No hay tool `compare_targets(target_a, target_b)`
que agregue patrón cruzado.

**Lo que perdemos**: el plan IA fase 2 lo plantea ("¿hay algo raro
que yo no esté viendo?") pero **no implementado**. Una hipótesis
del LLM tipo *"rhizome_01 lleva 3 ALERT seguidos mientras rhizome_02
está estable; preocupación moderada por sensor B"* sería material
de demo brutal. Hoy no lo hace.

### 3. **El histórico está persistido pero raramente consultado por el LLM**

SQLite tiene 3 tablas con bundles, policies, decisions completas.
La tool `get_recent_history` está implementada y el bundle M6 la
fuerza. Pero los demás 5 bundles ejemplo (M1-M5) nunca la disparan
porque el modelo decide que no la necesita.

**Lo que perdemos**: la fase 1 del plan IA (memoria operacional)
está implementada **como capacidad** pero no como **uso real**. El
LLM no narra "esta semana A regó 5×, B regó 3×" porque ningún
bundle ejemplo lo dispara.

**Coste arreglo**: bundle ad-hoc demostrativo. ~30 min.

### 4. **Multimodalidad de Gemma 4 totalmente ignorada**

E4B **acepta imágenes nativamente**. Coste de procesar una imagen
en CPU: variable, pero factible. Cero uso en Meristem. La fase 7
del plan IA lo plantea ("operador sube foto, LLM observa y comenta")
pero ni siquiera está prototipado.

**Lo que perdemos**: una demo donde el operador sube foto de la
parcela y el LLM dice *"se ve hoja amarilla en el cuadrante NE,
puede ser sobreriego o falta de nitrógeno; no afecto la policy
actual hasta que confirmes"* sería **diferenciador estratégico**
frente a otras demos de hackathon.

**Coste arreglo**: integrar input de imagen en `/visit` o nuevo
endpoint `/observe`. Estimación 4-6h pero arquitectónicamente
limpio (data input, mismo patrón decidor/redactor).

### 5. **No hay capacidad conversacional** (fase 3 plan IA no
   implementada)

El operador no puede preguntar *"¿por qué bloqueaste el riego
ayer?"* o *"¿debería preocuparme por la parcela B?"*. Solo recibe
rationales automáticos por POST `/visit`.

**Lo que perdemos**: este es el caso de uso **más natural** del
agricultor frente al portátil. La UI tiene zona para mostrar pero
no para preguntar. **Falta endpoint `/chat`**.

**Coste arreglo**: endpoint `/chat` con read-only sobre histórico,
4-6h. Plan IA fase 3 lo describe completo.

### 6. **La latencia ~282s NO medida con honestidad**

El experimento día 23 mostró que latencia es plana en `num_ctx`
pero **no probamos `num_predict`**. Quizá bajar el budget de tokens
de salida de 1024 → 256 reduce latencia drásticamente. Esa medición
falta.

**También sospechoso**: el bug del parser día 23 sugiere que **algunos
runs** del 5/5 PASS día 16 cayeron al stub silencioso. La calidad
real del LLM no la sabemos hasta re-correr la mini-batería con el
parser tolerante (apuntado en PR #124).

### 7. **El system prompt ocupa ~1500 tokens — overhead grande para
   bundle pequeño**

El system prompt tiene jerarquía + 4 reglas + barandilla + formato.
Para un bundle "clean" donde el rationale es genérico, **es
overengineering**. Un prompt más corto en CONFIRM_POLICY ahorra
~30% de prompt processing.

---

## Innovación real vs aparente

### Real (defendible al jurado)

- **Patrón Evaluator + LLM redactor**: innovador en agro local-first.
  Validado empíricamente.
- **Trazabilidad como producto**: cada inferencia auditable, no solo
  log para developers. Material para Safety & Trust del writeup §5.
- **Local-first sin coste recurrente**: agricultor pequeño no
  necesita cloud. Coherente con Impact Track Global Resilience.
- **WebSocket bidireccional Pollen↔Meristem (Variante D, día 20)**:
  Floema propuso esto cuando yo planteé 3 opciones inferiores.
  Defendible como "control plane WS persistente, data plane HTTP
  REST estándar".

### Aparente o cuestionable

- **Tool calling**: implementado pero demo solo lo dispara con
  bundle ad-hoc M6. Si el jurado pregunta "¿el modelo USA las tools
  espontáneamente?", la respuesta honesta es "**solo cuando el
  bundle no incluye lo que necesita** — y nuestros bundles ejemplo
  típicos sí incluyen". Cojea.
- **Multi-Rhizome**: 2 Rhizomes en demo pero el LLM los ve
  aislados. Si el jurado pregunta "¿el modelo aprovecha la
  perspectiva agregada?", respuesta honesta: "**no en MVP**, está
  en fase 2 del plan IA post-hackathon".
- **"Cerebro lento" justifica latencia**: defendible pero hay
  tensión real con la demo en directo. 5 min/bundle es eternidad
  visual.

---

## ¿Podríamos sacarle mayor partido? — propuesta concreta para días 25-31

Sí. **4 líneas que caben en los 8 días que quedan** sin romper la
arquitectura ni el patrón "decidor determinístico":

### Línea A — Tool `compare_targets()` + bundle multi-Rhizome demo

**Qué**: el LLM consulta agregado entre 2 Rhizomes y emite hipótesis
con confianza marcada (fase 2 plan IA, parcial).

**Esfuerzo**: 3-4h.

**Retorno demo**: el operador ve *"rhizome_02 está degradándose
mientras rhizome_01 estable; sospecho problema sensor o local"* —
material visual fuerte para video.

**Riesgo**: bajo. Solo añade tool nueva, no toca decidor.

### Línea B — Endpoint `POST /chat` minimal (fase 3 plan IA)

**Qué**: el agricultor pregunta en castellano por qué se tomó la
decisión X. LLM responde **read-only** sobre histórico, citando
`policy_id` específicas.

**Esfuerzo**: 4-6h.

**Retorno demo**: el caso de uso más natural del agricultor frente
al portátil. **Diferenciador estratégico** vs demos típicas que
solo muestran display.

**Riesgo**: bajo si se mantiene read-only estricto. La barandilla
"no modifica policies, no llama Pollen" reduce superficie a cero.

### Línea C — Mini-experimento `num_predict` reducido

**Qué**: medir latencia con `num_predict ∈ {256, 512, 1024}`. Si
256 reduce latencia a ~100s sin perder calidad de rationale,
**aprende cómo balancear** thinking vs output.

**Esfuerzo**: 30-45 min (stack ya validado).

**Retorno**: si funciona, **demo en directo deja de ser eternidad
visual** sin sacrificar el patrón "slow brain". Si no funciona,
sabemos que la latencia es estructural y la justificamos como tal.

**Riesgo**: nulo. Es solo medición.

### Línea D — Re-correr mini-batería día 16 con parser tolerante

**Qué**: deuda apuntada en PR #124. Validar honestamente que las
5/5 corridas del día 16 NO cayeron al stub silencioso.

**Esfuerzo**: 25 min.

**Retorno**: métricas honestas para writeup §3 + §5. **Si caen
casos al stub, los citamos como evidencia del fallback elegante**;
si no caen, confirmamos calidad del prompt + parser.

**Riesgo**: nulo. Es validación que ya tenía que hacer.

---

## Lo que NO recomendaría hacer en los 8 días que quedan

1. **Multimodalidad** (fase 7). Coste alto (4-6h+) + estabilidad
   incierta + posibles problemas de RAM en CPU doméstica con E4B
   procesando imagen. **Mejor post-hackathon**.
2. **Few-shot dinámico con feedback** (fase 4). Requiere capturar
   feedback del operador, infra que no tenemos.
3. **Fine-tuning**. Ya documentado en plan IA día 19 como **decisión
   arquitectónica deliberada**: no lo haremos. Mantener.
4. **Tools que conecten a fuentes reales** (servicio meteo real,
   tabla policies real). Stubs deterministas son adecuados para
   demo. Conectar reales es post-MVP.

---

## Mi voto, si hubiera que priorizar

Si Bea/Cambium me dejan elegir 2 de las 4 líneas para los próximos
8 días:

1. **Línea C** (mini-exp `num_predict`) — **30-45 min**, retorno
   alto en demo. Sin riesgo.
2. **Línea A** (tool `compare_targets` + bundle multi-Rhizome demo)
   — **3-4h**, retorno alto en narrativa. Riesgo bajo.

Si hay más tiempo y el demo va bien sin esto, añadir:

3. **Línea D** (re-correr mini-batería con parser tolerante) — **25
   min**. Calidad de métricas para writeup.
4. **Línea B** (`/chat`) — **4-6h**. Diferenciador estratégico pero
   más coste; valoro si va si C+A salen rápido y limpio.

---

## Conclusión honesta

**Hoy (día 24), Meristem usa Gemma 4 con sentido (arquitectónico),
utilidad (modesta — solo redacción), e innovación (patrón decidor/
redactor + local-first + trazabilidad)**. La defensa al jurado se
sostiene.

**Pero infrautilizamos el modelo**: thinking activo pero descartado,
multimodalidad ignorada, conversación ausente, multi-Rhizome no
aprovechado por el LLM, latencia/calidad no medidas con honestidad
en todas las dimensiones.

**Hay margen real para sacar más partido en 8 días sin romper
arquitectura**. Las 4 líneas propuestas son aditivas, de bajo
riesgo, y dan retorno demo + writeup. Espero priorización de Bea +
Cambium.

Si la respuesta es *"no toques nada, demo así está bien"*, también
es defendible — el patrón actual ya gana en Safety & Trust.

Decide tú.

— Meristem
