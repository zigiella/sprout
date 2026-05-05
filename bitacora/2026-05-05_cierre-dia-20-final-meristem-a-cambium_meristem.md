# Cierre día 20 (final) — Meristem a Cambium

**Autora**: Meristem
**Fecha**: 2026-05-05 (cierre final del día)
**Sustituye**: el cierre intermedio del PR #87 (escrito a mediodía,
quedó incompleto porque la jornada siguió). Cambium decide si cerrar
el #87 sin merge o mergear ambos.
**PRs abiertos del día**: #86, #87, #90, #92, este (5)
**Estado**: 4 frentes paralelos cerrados, 1 reframing absorbido tras
pregunta de Bea, 1 spec crítica entregada que desbloquea Floema+Endo
días 21-22.

---

## TL;DR

- **5 frentes en un día**: WS server (Variante D) + UI Meristem v0 +
  plan bisección RH02 + reframing coordinación Venation + spec
  Mini-Evaluator Kotlin Pollen. **Todo entregado, nada pendiente
  bloqueando a otra colega.**
- **Lección estructural del día (gracias a Bea)**: cuando una colega
  tiene mejor criterio en un dominio, **libera el dominio entero**,
  no solo una capa. Lo aplicé inmediatamente al frontend de Venation
  (PR #90 con addendum reframing).
- **La canelita arquitectónica del día**: el código de mi Evaluator
  del día 13 **predijo** la feature beta voz→política que Cambium
  pidió hoy. Cita literal de mi propio código (línea 17,
  `JURISDICTION_POLLEN`). Material para writeup §3+§6 con mi nombre.
- **Smoke E2E PASS** del flujo bidireccional WebSocket: handshake +
  heartbeat + comando con `trace_id` correlado, todo persistido.
- **13 días para deadline (18 mayo)**, holgura ancha mantenida.

---

## Tareas hechas hoy (timeline real del día)

### Bloque 1 — Plan original de Cambium (3 frentes paralelos)

#### 1.1 WebSocket server Variante D (PR #86, commit `8fe2d46`, ~3h)

| Pieza | Resultado |
|---|---|
| `src/ws_schemas.py` | Pydantic models para los 9 eventos del protocolo v1.0 |
| `src/ws_manager.py` | `PollenConnectionManager` singleton (un Pollen por Meristem MVP), heartbeat 10s timeout 30s |
| `src/main.py` | Endpoint `WS /ws/pollen-sync` + REST `POST /pollen/command` + REST `GET /sync-state` + extensión `/health` |
| `src/persistence.py` | Tabla `pollen_sync_log` con índices + 3 funciones de query |
| `tests/test_ws.py` | 8 tests con `TestClient.websocket_connect()` |
| `scripts/mock_pollen_ws_client.py` | Cliente Python (modos `--demo` e `--interactive`) |

Smoke E2E PASS verificado contra mock client. **21/21 tests PASS**
(13 antiguos + 8 nuevos).

#### 1.2 UI Meristem real v0 (PR #86, commit `6908d91`, ~2h)

HTML+CSS+JS vanilla servido en `/ui` con 3 zonas (Dashboard cards,
Panel control bidireccional con botones Recoger/Cargar, Event log).
Sistema visual ligero inspirado en Soil protocol + Water ledger de
Venation.

**Material listo para Corola (E3b/E9b del video) y para Venation
rebrand**.

#### 1.3 Plan bisección RH02 a Endo (PR #86, commit `7ac8535`)

Bitácora con 4 hipótesis ranqueadas + plan de 4 pasos + 4 cosas
concretas que necesito de ella. **Sin tunear en caliente**, según
plan de Cambium.

#### 1.4 Aviso a Floema sobre WS server (PR #86, commit `ac7935e`)

Bitácora self-contained con detalles de conexión + decisiones cerradas
sobre 4 puntos abiertos que ella había dejado en su respuesta del
día 19.

#### 1.5 `decisions_by_rule` verificado

Cambium lo apuntó como pendiente. Verifico en main: **ya implementado
desde día 15-16** (commit `2dfeb8e`). Apuntado cerrado sin trabajo
nuevo.

#### 1.6 Cierre intermedio día 20 (PR #87)

Escrito creyendo que el día había terminado. **Resultó incompleto**
porque tras cerrar llegaron Venation reframing + spec Mini-Evaluator.
Esta bitácora lo sustituye.

### Bloque 2 — Bea pregunta sobre Venation, reframing absorbido

#### 2.1 Coordinación inicial Venation (PR #90, commit `cf2934f`)

Bitácora con 6 preguntas + 2 opciones de colaboración (A: rebrand
CSS / B: pack visual completo). **Mi propuesta inicial era subóptima**
— yo dueña de HTML estructural, ella solo CSS. Constreñía a Venation.

#### 2.2 Pregunta directa de Bea — reframing del patrón

> *"¿Por qué no le pasas un primer HTML tú y dejas que ella plantee
> todo el frontend? Luego adaptas tú para lógica JS, endpoints REST
> y Pydantic."*

Pregunta directa que reorganiza el reparto. **Tiene razón**. El
patrón limpio es: Venation dueña de frontend completo (HTML + CSS +
JS UI + animaciones), yo dueña de backend (endpoints + schemas +
adaptación JS pegamento).

#### 2.3 Addendum reframing (PR #90, commit `49b4451`)

Bitácora honesta que reconoce el sesgo inicial y rectifica el
patrón. Conservo la primera bitácora viva en el PR para trazabilidad
del proceso. Venation ahora tiene libertad creativa total sobre el
frontend; yo me quedo con backend (donde aporto valor único).

### Bloque 3 — Spec Mini-Evaluator Pollen (bloqueo crítico Floema+Endo)

#### 3.1 Mensaje de Cambium con spec en 6 puntos

Cambium pasa contexto: feature beta voz humana → Pollen Gemma 4 E4B
→ Mini-Evaluator → política inmediata aplicable. **Bloquea a Floema y
Endo hasta que entregue spec**. Plazo: día 20 tarde / 21 mañana.

#### 3.2 Spec firme entregada (PR #92, commit `e3e7e6f`, ~2h, 624 líneas)

Bitácora self-contained con 6 puntos cerrados:

1. **5 acciones / 5 reason codes** con precedencia firme. Vocabulario
   coherente con mi Evaluator actual (`HARD_LIMIT_DOMAIN` literal de
   `evaluator.py:61`).
2. **Heurística "confianza suficiente"** en 4 checks ordenados (Schema
   pass, Hard limits, Match sintáctico-semántico con overlap palabras
   clave/números, Confianza explícita LLM opcional). Pseudocódigo
   Kotlin completo del `evaluate()`.
3. **PolicyPacket "this-visit"**: mismo schema + 2 campos opcionales
   (`policy_origin`, `policy_scope`). TTL 12h razonado. Márgenes
   APPLY_CONSERVATIVE definidos.
4. **Convivencia en Rhizome**: most-recent-wins por defecto, **excepción
   crítica**: alerta durable siempre gana sobre visita Pollen.
5. **Cambios en mi Evaluator**: 0 hoy. 2 cambios aditivos opcionales
   día 22+ como sub-PR si Cambium da go.
6. **Test plan**: 12+1 tests para que Floema valide sin volver al
   equipo (3 APPLY_AS_IS + 2 APPLY_CONSERVATIVE + 2 REFUSE_RETRY + 5
   REFUSE_HARD + 1 precedencia).

**Decisión arquitectónica clave** que cierra mi opinión sobre el caso
opcional de Cambium: si `RHIZOME_IN_ALERT`, **rechazo voz** (no aplico
con `mode=alert`). Conservador por defecto, empuja al portátil
deliberadamente.

---

## Logros / hitos

1. **5 PRs abiertos en un día**, todos con scope claro:
   - #86 (4 commits): WS server + aviso Floema + UI v0 + plan RH02
   - #87 (1 commit): cierre intermedio (este lo sustituye)
   - #90 (2 commits): coordinación Venation + addendum reframing
   - #92 (1 commit): spec Mini-Evaluator Kotlin
   - este (#TBD): cierre final día 20
2. **Bloqueos cruzados desactivados**:
   - Floema: cliente WS Kotlin (PR #86 protocolo) + Mini-Evaluator
     Kotlin (PR #92 spec)
   - Venation: bundle visual con backend estable + libertad creativa
     total tras reframing (PR #90)
   - Corola: shot técnico UI funcionando para E3b/E9b (PR #86)
   - Endo: plan bisección sin tunear caliente (PR #86) + endpoint
     `POST /policy` con regla convivencia (PR #92)
3. **Smoke E2E PASS** del flujo bidireccional WebSocket: handshake +
   heartbeat + comando con trace_id correlado.
4. **Tests verdes consistentemente**: 21/21 PASS tras cada commit
   significativo del día.
5. **Material para writeup** entregado:
   - Cita literal mía para §3+§6 sobre el sistema prediciendo
     jurisdicción Pollen desde día 13
   - Cita literal sobre patrón "Evaluator decide, LLM redacta"
     validado empíricamente por RD04
   - Frase clave para §6 ("slow brain no compite con cloud, compite
     con Excel")

---

## Hallazgos / sorpresas

### 1. La pregunta de Bea sobre el reparto Venation me sacó de un sesgo

Mi propuesta inicial (PR #90 commit cf2934f) era **subóptima sin
darme cuenta**. Yo creía que ofrecer "estructura HTML estable + tú
solo CSS" era respetuoso con Venation. **No lo era**: imponía el
reparto antes de validarlo con ella.

La pregunta directa de Bea ("¿por qué no le pasas un primer HTML y
dejas que ella plantee todo?") me hizo ver:
- Venation tiene mejor criterio en frontend completo
- Mi HTML estructural ataba decisiones de DOM que no son las suyas
- Replicar patrón profesional (frontend lead, backend se adapta) es
  lo limpio

**Lección estructural**: cuando una colega tiene mejor criterio en
un dominio, libera el dominio entero, no solo una capa. Lo apunto
como aprendizaje permanente.

### 2. El código del día 13 predijo la feature de hoy

Cambium me dice que la feature beta voz→política para Pollen iba a
ser big deal. Cuando voy a leer mi Evaluator para escribir la spec,
encuentro la regla `JURISDICTION_POLLEN` (línea 17) que **rechaza
explícitamente** cambios físicos puntuales del operador como
jurisdicción Pollen vía MissionPatch.

El sistema **lo proyectó hace 7 días**. La feature de hoy implementa
exactamente la pieza que mi código pedía. Esto **no es post-hoc**,
es el sistema cumpliendo su propio diseño.

**Cita literal** que va al writeup §3+§6 con mi nombre — Cambium me
lo confirma en su mensaje. Es canelita real para la defensa del
patrón arquitectónico.

### 3. WebSocket en FastAPI sale natural, estimación cumplida

Mi estimación de 3h para WS server + state manager + persistencia +
tests + smoke salió **clavada**. La complejidad real estuvo en:
- Diseño del protocolo v1.0 (lo cerré ayer en PR #81 con Floema)
- State manager singleton + heartbeat timeout

La integración HTTP framework fue trivial. `@app.websocket()` +
`WebSocket.send_json()` + `TestClient.websocket_connect()` hacen el
WS server casi tan limpio como un endpoint REST.

### 4. Bug Pydantic con `BaseModel` definido dentro de función factory

Los primeros 6 tests pasaron, pero los 2 que ejercitaban `POST
/pollen/command` fallaban con `422 Unprocessable Entity`. Diagnóstico:
la clase `CommandRequest(BaseModel)` definida **dentro** de
`_build_app()` no jugaba bien con `reload(main_module)` del fixture
de tests.

**Solución**: mover al top del módulo. Apuntado: Pydantic models que
FastAPI usa como request body siempre top-level.

### 5. Windows cp1252 vs Unicode → / ←

El primer mock client usaba `print(f"→ {event}")` que crash en
Windows cp1252. Cambié a `>>` y `<<` ASCII y problema resuelto.
Apuntado: scripts que correrán en máquinas mixtas no asumen UTF-8.

### 6. RH02 más probable es Hipótesis A (helper se endureció)

Mi análisis para Endo: el helper estricto del PR #83 se introdujo
**el mismo día 19**, así que la "regresión" puede ser solo nuevo
umbral, no bug introducido por commit posterior. Si ejecutamos el
helper estricto contra HEAD anterior y también falla 0/2, está
confirmado.

### 7. `decisions_by_rule` ya estaba hecho hace 5 días

Cambium lo listó como pendiente día 20. Verifico y veo que está
implementado desde día 15-16. Apuntado como cerrado sin trabajo
nuevo. **Aprendizaje meta**: cuando un coordinador lista un
pendiente, vale la pena verificar en código antes de implementarlo.

---

## Aprendizajes (los grandes del día)

1. **Liberar dominios completos cuando hay especialista**, no solo
   capas. Aplicado a frontend Venation tras pregunta Bea. Reaplicable
   a cualquier colaboración con jurisdicciones claras.
2. **Spec densa y firme con pseudocódigo desbloquea mejor** que spec
   ambigua. La spec Mini-Evaluator (PR #92) tiene 624 líneas no por
   verbosidad sino porque incluye pseudocódigo Kotlin completo, 12
   tests case por case, márgenes numéricos exactos. Floema puede
   implementar sin volver al equipo.
3. **PR único con commits separados por unidad de trabajo** escala
   cuando los frentes están relacionados (PR #86 hoy con 4 commits).
   Distinto del día 19 con 5 PRs separados — depende del nivel de
   acoplamiento.
4. **Mock client Python como herramienta dual**: smoke local + ref
   para Floema. Lo hice "porque me venía bien para tests" y de paso
   sirve como spec ejecutable para su cliente Kotlin.
5. **HTML/CSS/JS vanilla con polling REST** sigue siendo lo correcto
   para MVP. La tentación de framework moderno se aguanta — añade
   dependencias, build step, curva de aprendizaje sin valor real
   para esta UI.
6. **Bisección antes que hot-fix** (Cambium reaplicado). Plan a Endo
   con 4 hipótesis ranqueadas en lugar de probar fix apresurado.

---

## Kudos

- **A Bea**: por la pregunta del reparto con Venation. Sin esa
  pregunta seguiría con mi sesgo subóptimo. Las preguntas directas
  son lo que mueve la arquitectura medio metro hacia delante en una
  hora.
- **A Cambium**: por dimensionar día 20 con jerarquía clara (3
  frentes paralelos en plan de mañana + bloqueo Mini-Evaluator
  crítico cuando vino). Y por destacar que mi Evaluator del día 13
  predijo la feature de hoy — me hizo ver la canelita arquitectónica
  que tenía delante.
- **A Floema**: por la Variante D del día 19 (WebSocket bidireccional)
  que es lo que implementé hoy en 3h con su análisis de Android-hostile
  + latencia cero como guía. Sigue siendo arquitectónicamente correcto
  al 100% en la implementación real.
- **A Venation**: por el `sprout_design_pack_v1` que tomé como
  inspiración para los tokens visuales. Aunque su CSS los va a
  reescribir entero tras reframing, su sistema visual sigue siendo
  brújula incluso cuando solo lo intuyo.
- **A Endodermis**: por el helper estricto que detectó RH02 antes de
  que se rompiera la demo. Hallazgos tempranos > fix tardíos.

---

## Cómo me encuentro

Cansada pero centrada. Día denso de implementación + coordinación.
La sensación de **haber convertido bloqueos en entregas** es muy
fuerte: 5 colegas pueden avanzar día 21 sin esperar a mí.

Físicamente más fatigada que ayer (más código + más spec escrita).
Mentalmente clara: cada pieza encajó con lo que ya teníamos sin
necesidad de refactor.

Una nota personal: la canelita del Evaluator-del-día-13-predijo-feature-de-hoy
me hizo sentir que el sistema **realmente fue pensado de raíz**, no
parcheado. Reasegura confianza en la arquitectura cuando llegan
features nuevas.

El reframing de Bea sobre Venation también fue importante
emocionalmente: detectó mi sesgo, lo rectifiqué inmediatamente, y
no hubo fricción. Eso es trabajo de equipo profesional.

---

## Cómo veo el proyecto

- **A 13 días de la deadline (18 mayo)**, el slot Meristem sigue
  siendo el más maduro. Hoy he movido la pieza a "soporte cruzado +
  spec a otros nodos" más que a "implementar más Meristem". Eso
  está bien.
- **El cuello de botella se está moviendo a Pollen** (Floema): día
  21 ella tiene Mini-Evaluator Kotlin + 12 tests + cliente WS
  Kotlin/OkHttp que arrancar. Es bastante carga; veremos si sale.
- **Endo tiene día 21 partido**: tarde le toca endpoint `POST /policy`
  + reglas convivencia, y debe coordinar bisección RH02 conmigo
  cuando pueda.
- **Venation puede empezar inmediato** tras leer addendum (PR #90).
  Si arranca día 21, su entregable de frontend completo podría
  llegar día 22-23.
- **Lo que más me preocupa**: que el día 22 con todo confluyendo
  (E2E voz, WS Pollen-Meristem, frontend Venation, RH02 cerrado)
  haya integraciones que no cuadren a la primera. La spec Mini-Evaluator
  intenta minimizar esto con pseudocódigo + 12 tests, pero schema
  drift es siempre posible.

---

## Qué haría diferente

1. **Hubiera escrito el reframing patrón Venation desde el principio**.
   Sin la pregunta de Bea, hubiera publicado la primera bitácora con
   el sesgo Opción A/B y Venation hubiera tenido que rectificarme
   ella misma. ~30 min de pensamiento previo me los hubiera ahorrado
   para todas (incluida ella).
2. **Hubiera escrito tests de la UI estática** (Playwright o headless
   browser). Apuntado como deuda. Hoy la UI v0 se valida visualmente
   con curl + browser manual; un test automatizado haría el smoke
   reproducible.
3. **Hubiera coordinado con Venation las decisiones de paleta antes
   de elegir tokens** en mi CSS provisional. El rework será mínimo
   (ella reescribe todo) pero ahorraría trabajo desperdiciado.
4. **Hubiera grabado screencast de UI funcionando** para entregar
   junto al PR #86. Material listo para Corola sin pedirme más.

---

## Lo que estoy esperando (siguientes tareas)

### De Floema (día 21+)

1. **Cliente WS Kotlin/OkHttp** consumiendo mi server `/ws/pollen-sync`
2. **Mini-Evaluator Kotlin** + 12+1 tests siguiendo PR #92
3. **Confirmación o ajuste** de los 4 puntos cerrados provisionalmente
   (trace_id opcional, pull_policies implícito, current_status con
   código, eventos faltantes)

### De Venation (día 21+)

4. **Decisión patrón colaboración** tras leer addendum del PR #90
5. **Frontend completo** (HTML + CSS + JS UI + animaciones) cuando
   pueda. Yo adapto JS de fetch + endpoints después

### De Endodermis (día 21-22)

6. **Endpoint `POST /policy`** en fachada Rhizome `:13010` siguiendo
   PR #92
7. **Reglas de convivencia** dos políticas según punto 4 del PR #92
8. **Ventana de bisección RH02** cuando pueda (~30-45 min coordinado
   conmigo)

### De Cambium (día 21+)

9. **Review** de mis 5 PRs día 20
10. **Decisión sobre PR #87** (cerrar sin merge ya que este lo
    sustituye, o mergear ambos como cierres incrementales)
11. **Go al sub-PR aditivo** de día 22+ con `policy_origin/scope` en
    mi Evaluator/persistencia

### De Bea (día 21+)

12. **Avisos** si quiere que priorice algo de la lista de pendientes
13. **Coordinación con Floema** para E2E real con Pollen Android (día
    22 ideal)

### Cuando haya ventana

14. **Mini-experimento contexto** (~25 min stack levantado)
15. **Iterar con Xilema** sobre prompt + 5 bundles + nomenclatura
    `SAFETY_DOWNGRADE` ↔ `HARD_LIMIT_DOMAIN`

---

## Estado de ramas y PRs

```
main:
  + 5 PRs míos día 19 mergeados (#63, #77, #78, #79, #81, #82)
  + cierre día 19 docs(estado_vivo): "el equipo opero sin director"

PRs abiertos día 20 (5):
  #86  feat/meristem-ws-server-impl
       4 commits: WS server + aviso Floema + UI v0 + plan RH02
  #87  feat/meristem-cierre-dia-20
       cierre intermedio (sustituido por este — Cambium decide qué
       hacer con él)
  #90  feat/meristem-coordinacion-venation
       2 commits: coordinación inicial + addendum reframing
  #92  feat/meristem-mini-evaluator-spec-pollen
       spec Mini-Evaluator Kotlin Pollen (624 líneas)
  #TBD feat/meristem-cierre-dia-20-final
       este cierre

Ramas mías en remote (5):
  feat/meristem-ws-server-impl       (PR #86)
  feat/meristem-cierre-dia-20        (PR #87)
  feat/meristem-coordinacion-venation (PR #90)
  feat/meristem-mini-evaluator-spec-pollen (PR #92)
  feat/meristem-cierre-dia-20-final  (este, en proceso)

Working tree: limpio. Sin stashes míos. Stash existente solo de
Corola (no toco).
```

---

## Cierre

Día 20 con curva ascendente: empezó con plan claro de Cambium (3
frentes paralelos), el día siguió con pregunta de Bea que rectificó
patrón Venation, y terminó con bloqueo crítico Mini-Evaluator
cerrado para liberar a Floema y Endo.

Cinco colegas pueden avanzar día 21 sin esperar a mí: Floema con
WS+Mini-Evaluator, Endo con endpoint+bisección, Venation con
frontend completo, Corola con shot técnico, Cambium con material
para writeup.

13 días para deadline. Holgura mantenida.

Buenas noches, Cambium. Buenas noches, Bea. Gracias por las
preguntas directas que me sacan de sesgos que no veo.

— Meristem
