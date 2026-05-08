# Cierre día 23 — Meristem a Cambium

**Autora**: Meristem
**Fecha**: 2026-05-08 (cierre)
**PRs míos abiertos hoy**: #124 (mini-experimento contexto)
**Estado**: limpio. Stack apagado, working tree clean, todo pusheado.

---

## TL;DR

- **Día corto y enfocado en una sola pieza grande**: el mini-experimento
  contexto que arrastraba como deuda desde el día 19. Ejecutado con
  LLM real, **6/6 OK**, hallazgo principal **rechaza mi hipótesis
  original** (latencia plana, no superlineal).
- **3 bugs encontrados y arreglados** durante el experimento. Uno de
  ellos (parser estricto vs keys EN/ES) tiene **implicación retroactiva
  importante**: la mini-batería del día 16 (5/5 PASS reportado) puede
  haber tenido casos al stub fallback no detectados.
- **Caída del proceso de Claude** durante el experimento, sin pérdida
  de datos (todo había sido pusheado antes). Bea me avisó al volver y
  verifiqué el estado en remote — limpio.
- **PR #124 abierto** con material para writeup §3 (frase candidata
  cerrada).

---

## Tareas hechas hoy

| Pieza | Resultado |
|---|---|
| Pre-experimento: hacer `num_ctx` configurable en `inference.py` (header `X-Meristem-Num-Ctx`, propagación hasta `_post_chat`) | Done, tests 36/36 PASS |
| Pre-experimento: subir `HTTP_TIMEOUT_S` 180→600s | Done |
| Levantar stack completo (llama-server :8080 + adapter :11434 + meristem :13000 con LLM real) | Done |
| Smoke single visit con LLM real | Falló inicialmente (cayó a stub_fallback) |
| Diagnóstico falló silencioso | 3 bugs detectados |
| Bug 1: parser estricto rechazaba JSON con keys traducidas al inglés | Parser tolerante con fallbacks (snake/camel, ES/EN) |
| Bug 2: timeouts cliente (300s script) / server (180s→600s) desincronizados | Alineado a 600s ambos |
| Bug 3: encoding cp1252 en Windows con flechas Unicode `→` | Cambiado a `->` ASCII (mismo bug del mock client día 20) |
| Re-ejecutar experimento focused: 1 bundle (M1) × 6 num_ctx (1024-32768) | **6/6 OK** con LLM real |
| Generar gráfica + tabla MD via `plot_mini_exp.py` | Done en `docs/figures/` |
| Bitácora 280+ líneas con limitaciones y deudas honestas | Done |
| Apagar stack + cleanup BBDD | Done |
| PR #124 abierto con descripción completa | Done |

## Logros / hitos

1. **PR #124 con la deuda del día 19 cerrada**. Mini-experimento
   contexto pasó de "apuntado en bitácora" a "ejecutado con datos
   reales".
2. **Hallazgo arquitectónico que rechaza mi propia hipótesis**:
   latencia E2E plana (~217-292s, variación ~35%) en rango 32× de
   `num_ctx` (1024 → 32768). No es superlineal como predije día 19.
   Esto **valida desde otro ángulo** el principio "memoria por tools,
   no por stuffing": el motivo no es ahorrar latencia (que es plana)
   sino footprint de RAM + transparencia algorítmica.
3. **3 bugs críticos arreglados**, uno con efecto retroactivo en
   métricas previas. Apuntado en bitácora para re-correr mini-batería
   día 16 con parser tolerante post-merge.
4. **Frase candidata literal entregada** para writeup §3.
5. **Sesión sobrevivió la caída de Claude** sin pérdida — disciplina
   de push temprano se confirma una vez más.

## Hallazgos / sorpresas

### 1. La hipótesis del día 19 estaba equivocada — latencia plana

**Predicción día 19**: "doblar `num_ctx` triplica la latencia,
crecimiento superlineal".

**Evidencia día 23**: 217s @ 1024, 282s @ 4096, 292s @ 32768. **35%
de variación en 32× de num_ctx**. No es ni siquiera lineal — es casi
plano.

**Razón probable**: en bundles pequeños (~1500 tokens prompt) con
`num_predict=1024`, el coste dominante es eval del rationale +
thinking, no la reserva de contexto. Llama.cpp KV cache es eficiente
con num_ctx grande aunque el prompt sea pequeño.

**Lectura**: tener una hipótesis y rechazarla con datos es **mejor
resultado** que confirmarla. La arquitectura sigue siendo correcta
("memoria por tools") pero por otro motivo (RAM + transparencia, no
latencia).

### 2. El parser estricto puede haber inflado el "5/5 PASS" del día 16

Bug crítico encontrado durante el diagnóstico: `_parse_rationale_json`
buscaba estrictamente las keys `rationale_tecnico` /
`rationale_para_operador`. **El modelo a veces traduce los keys al
inglés** (`technical_rationale` / `user_friendly_rationale`) aunque
el system prompt pide formato exacto en castellano.

Cuando el parser fallaba, `_compose_rationale` caía al stub
fallback **sin alarma visible** porque:
- El stub devuelve texto válido (no error visible al cliente)
- El smoke verifica `status="ok"` y `reason_code` correctos — ambos
  vienen del Evaluator determinista, NO del LLM
- El `llm_metrics.mode` quedaba en `stub_fallback` pero nadie lo
  inspeccionaba

**Implicación**: la mini-batería del día 16 (5/5 PASS reportado)
**probablemente tuvo algún caso al stub no detectado**. La calidad
cualitativa del rationale puede haber sido inferior a lo reportado.

**Solución**: parser tolerante con fallbacks a múltiples variantes
(snake/camel, ES/EN). Apuntado en bitácora del PR #124: re-correr
mini-batería día 16 con parser tolerante para tener números reales.

### 3. Caída de Claude durante el experimento

A mitad del flujo, el proceso de Claude se cayó. Bea me avisó al
volver. Verifiqué git inmediatamente:
- Working tree limpio
- Up-to-date con origin
- PR #124 OPEN
- 2 commits del experimento en remote (`27e8daa` + `0d09fdd`)

**Sin pérdida de trabajo**. La disciplina de "push temprano tras cada
commit significativo" volvió a salvar. Apuntado como evidencia más
del patrón.

## Aprendizajes

1. **Hipótesis con datos reales > intuición arquitectónica**. Mi
   predicción del día 19 (latencia superlineal) era plausible pero
   no se sostuvo. Vale la pena ejecutar experimentos aunque parezcan
   "lo que ya sabemos".
2. **Bugs silenciosos son los más peligrosos**. El parser estricto
   no producía error visible — solo degradación silenciosa. La única
   forma de detectarlo fue el debug explícito de qué devolvía el
   LLM. **Lección práctica**: añadir aserciones explícitas en pipelines
   de validación (parser falló → log warning, no solo None silencioso).
3. **Push temprano sigue salvando ante caídas**. Cuarta vez en el
   proyecto que una caída del proceso (Claude o branch jumping del
   día 17-19) no causa pérdida porque cada commit estaba en remote.
   Patrón confirmado.
4. **Timeout pipelines deben escalar consistentemente**. Cliente 300s
   vs server 180s vs LLM real 5+ min causaba síntomas confusos
   (script daba `?` mientras server seguía procesando). Lección:
   alinear timeouts cliente ≥ server ≥ tarea estimada × 2.
5. **Encoding cp1252 con Unicode**: bug recurrente (mock client día
   20, mini_exp script día 23). Apuntado como patrón para futuras
   utilidades — scripts que correrán en máquinas mixtas no asumen
   UTF-8 stdout.

## Decisiones del día

1. **No tocar la doc obsoleta `:12000`** en docstrings de
   `inference.py` y `main.py`. El adapter real es `:11434`. Hay
   override via env var pero el default histórico se mantiene.
   Apuntado para coordinar con Cambium si vale rotar el default —
   afecta otros consumidores históricos.
2. **N=1 por celda** en versión LIGHT, sin repeticiones. Aceptable
   para mini-experimento (busco tendencia, no análisis estadístico).
   Versión con N≥3 queda como deuda post-MVP.
3. **Solo M1 (clean)** en el experimento focused. M3 y M6 quedaron
   sin medir limpio porque el primer experimento tuvo timeouts
   desalineados que invalidaron sus runs. Apuntado para post-MVP.
4. **Apagar stack al final**: liberar recursos del portátil para que
   Bea pueda usarlo para video / otras pruebas. Cleanup completo
   (BBDD borrada, procesos kill).
5. **PR único con scope claro** ("mini-experimento + parser
   tolerante + bugs adyacentes"). 2 commits separados para review
   limpia: preparación + resultados.

## Nivel de satisfacción: alto

Tres razones concretas:

1. **Convertí una deuda de 4 días en datos reales con material para
   writeup**. El mini-experimento estaba apuntado desde día 19;
   ejecutarlo cierra una promesa pendiente.
2. **Aprendí algo que rechaza mi propia hipótesis**. Es un resultado
   más interesante que confirmar lo que pensaba — me obliga a
   articular el principio "memoria por tools" de forma más matizada.
3. **El bug del parser tolerante es un hallazgo de seguridad real**.
   Si la mini-batería día 16 tuvo casos al stub no detectados, la
   confianza en el "5/5 PASS" se relativiza. Mejor saberlo ahora
   con tiempo de re-correr que descubrirlo en demo.

Una sombra: gasté más tiempo del previsto en el diagnóstico (3 bugs
en cadena). Si hubiera levantado el stack día 19 mismo, los bugs
se hubieran detectado antes.

## Cómo veo el proyecto

- **A 10 días del deadline (18 mayo)**, el slot Meristem sigue
  cerrado en su parte funcional. Mi trabajo va siendo cada vez más
  de soporte cruzado + cierre de deudas técnicas, menos de feature
  nueva.
- **Cuello de botella visible**: PRs míos esperan review/merge de
  Cambium. #124 es el último; mientras se mergea no puedo arrancar
  el siguiente sub-PR limpio.
- **Lo que más me preocupa**: que la mini-batería día 16 con parser
  tolerante revele que muchas evaluaciones cayeron al stub. Si pasa,
  hay que re-validar el "patrón funciona empíricamente" con datos
  honestos. No es desastre — el patrón sigue funcionando, solo que
  necesita medirse mejor.

## Esperando

- **Cambium**: review + merge de PR #124 (mini-experimento)
- **Floema**: smoke E2E real cuando ella tenga ventana (pendiente
  desde día 22)
- **Endo**: bisección RH02 cuando hueco mutuo (PR #87 mergeado
  día 20 con plan)
- **Venation**: respuesta sobre rebrand UI v0 (PR #90 abierto desde
  día 19)
- **Xilema**: prompt + 5 bundles + nomenclatura `SAFETY_DOWNGRADE`
  ↔ `HARD_LIMIT_DOMAIN` (sin urgencia)
- **Bea**: priorización si quiere algo distinto mañana

## Próximas tareas en mi frente

### Inmediato (día 24)

1. **Aplicar feedback de Cambium al PR #124** si lo pide.
2. **Re-correr mini-batería día 16** con el parser tolerante
   (post-merge de #124) para tener métricas reales del 5/5 PASS.
   Estimado ~25 min con stack ya validado.

### Soporte cruzado (día 24+)

3. **Floema**: si hace smoke E2E real, asistir como referencia
   operativa.
4. **Endo**: bisección RH02 cuando ventana mutua.
5. **Venation**: cuando responda al reframing del PR #90, adaptar
   backend al frontend que entregue.

### Cuando haya ventana

6. **Mini-experimento bundles M3/M6** con condiciones limpias (mismo
   stack, parser tolerante, timeouts alineados). ~30-45 min.
7. **Mini-experimento N=3 repeticiones** para análisis estadístico
   real. Apuntado como deuda post-MVP.
8. **Mensaje pendiente Xilema** cuando ella tenga hueco.

### Sin fecha

9. **Rotar default `:12000` → `:11434`** en docstrings si Cambium
   da go (afecta otros consumidores históricos).
10. **Tests automatizados de UI estática** (deuda apuntada desde
    día 20).

## Estado de ramas y PRs

```
main (al cierre día 23):
  + PR #122 mergeado (sub-PR aditivo policy_origin/policy_scope, día 22)
  + PR #117/#119 mergeados (i18n + runbook + reflexión, día 22)
  + PR #123 mergeado (curado writeup buenas prácticas, día 23)

PR mío abierto día 23:
  #124  feat/meristem-mini-experimento-contexto
        2 commits: preparación + resultados con bitácora honesta
        Esperando review Cambium

Rama mía adicional sin PR todavía:
  feat/meristem-cierre-dia-23
        este cierre, en proceso

Working tree: limpio. Sin stashes míos. Stack apagado. BBDD del
experimento borrada.
```

## Cierre

Día 23 con una sola entrega grande pero importante: el experimento
que arrastraba como deuda desde el día 19 está cerrado con datos
reales y bitácora honesta. La hipótesis original quedó rechazada
con evidencia, lo cual es mejor resultado que confirmarla.

10 días para deadline. Holgura mantenida.

Buenas noches, Cambium. Buenas noches, Bea. Gracias por la
profesionalidad recíproca y por seguir confiando en mi criterio
cuando los hallazgos contradicen mis propias predicciones.

— Meristem
