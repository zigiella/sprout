# Cierre día 21 — Meristem a Cambium

**Autora**: Meristem
**Fecha**: 2026-05-06 (cierre)
**PR principal del día**: #104 (UI funcional v1)
**Estado**: limpio. Server demo apagado, working tree limpio en
todas mis ramas, sin stashes míos.

---

## TL;DR

- **Día compacto y enfocado** tras cierre largo de ayer (5 PRs día 20).
  Hoy: 1 entrega bien acotada (UI funcional v1 con 2 zonas nuevas) +
  1 demo en directo a Bea (4 bundles cargados + mock Pollen WS
  conectado, todo visible en `/ui/`).
- **Cambium pidió 2-4h**; salió en ~2h con tests verdes + smoke E2E +
  bitácora del PR.
- **Hallazgo técnico** del día: state leakage entre tests con
  `reload(persistence)` por defaults de funciones cacheados al
  importar. Solución limpia con `del sys.modules['src.*']` en fixture.
- **Patrón Venation se respeta** sin fricción: cuando ella entre
  (días 22-25) reescribirá CSS sobre la estructura HTML estable que
  hoy entregué; mi JS no se rompe.
- **Nivel de satisfacción alto**. Tres razones concretas más abajo.

---

## Tareas hechas hoy

| Pieza | Detalle | Resultado |
|---|---|---|
| Lectura mensaje Cambium | "Primera versión funcional UI sin diseño final" + reframing Bea de "no espero a Venation" → "monto ya, Venation rebrandea después" | Aceptado, comprendido |
| `persistence.list_recent_bundles(limit)` | Join `bundles + decisions` para incluir `reason_code` y `rule_applied` por bundle. None si REFUSE (no persiste decision) | Implementado |
| `persistence.list_recent_policies(limit)` | Lista DESC con `mode_default`, `valid_until`, rationale recortado a 160 chars | Implementado |
| Endpoint `GET /bundles/recent?limit=N` | Clamping 1-200, devuelve `{limit, items}` | Implementado |
| Endpoint `GET /policies/recent?limit=N` | Idem | Implementado |
| UI Zona 4 — "Visitas recibidas" | Tabla con hora / target / pollen / chip resultado coloreado por `rule_applied` | Implementado |
| UI Zona 5 — "Políticas emitidas" | Tabla con hora / target+`policy_id` abreviado / chip mode / `valid_until` / rationale técnico recortado | Implementado |
| Polling JS extendido | 5 endpoints en paralelo cada 2s (los 3 anteriores + 2 nuevos) | Implementado |
| Grid layout responsive | Desktop fila inferior `bundles policies`; mobile stack vertical | Implementado |
| Tests `test_recent_endpoints.py` | 8 casos: empty, populate, joineo decisions, orden DESC, limit clamping, REFUSE incluido | 8/8 PASS |
| Suite completa | 13 evaluator + 8 WS + 8 recent endpoints | 29/29 PASS |
| Smoke E2E | POST 3 bundles representativos + verificación shapes JSON + UI carga | PASS |
| PR #104 | Opened con descripción completa | Esperando review |
| Demo en directo a Bea | Server arriba + 4 bundles cargados + mock WS conectado + URLs (UI, /docs, /health) | Funcionó sin fallos |

## Aprendizajes

### 1. State leakage en tests con `reload()` y defaults de funciones

**Contexto**: la fixture `client(monkeypatch)` que copié del patrón
de `test_ws.py` funcionaba en aislamiento (un test, pasa) pero
fallaba en suite (3 fallos cuando se runeaban tests adyacentes).

**Diagnóstico**: las funciones de `persistence.py` tienen `db_path:
Path | str = DEFAULT_DB_PATH` como argumento default. Python evalúa
defaults **una vez al definir la función**, no en cada llamada.
Cuando hago `reload(persistence)`, las funciones se re-definen, pero
algunos paths de import en otros módulos (vía cache de `sys.modules`)
pueden mantener referencia a la versión anterior con default
distinto.

**Solución**: borrar `sys.modules` para `src.*` antes de import
fresh:

```python
import sys
for mod_name in list(sys.modules.keys()):
    if mod_name == "src" or mod_name.startswith("src."):
        del sys.modules[mod_name]
from src import persistence, main as main_module  # import limpio
```

**Aprendizaje permanente**: para tests que necesitan aislamiento
total con módulos que tienen state global (singletons, defaults
evaluados al import), `del sys.modules` es más robusto que `reload()`
solo. Lo apunto para futuras configuraciones de fixtures Python.

### 2. Demo en directo enseña valor que la spec no captura

Cargar 4 bundles representativos + conectar mock WS y mandarle el
link a Bea fue ~5 minutos extra de coordinación, pero permitió ver:
- La UI **respiraba** con datos reales (cards de modo distinto,
  chips de reason_code, evento log creciendo en tiempo real con
  heartbeats cada 10s)
- La integración WS está funcional (chip Pollen verde, zona 2
  habilitada)
- El polling de 2s da sensación de "pantalla viva"

Lo que hubiera quedado descrito en bitácora pasa a ser **demostrable
en pantalla**. Aprendizaje: el demo en directo, aunque sea breve, es
herramienta de validación del producto, no solo del código.

### 3. La UI v1 cumple sin tirar trabajo de la v0

La UI v0 (PR #86 ya mergeado) tenía 3 zonas (cards, panel control,
event log). Hoy añado 2 zonas (visitas, policies) **sin tocar las
3 anteriores**. Aditivo puro. Aprendizaje: cuando el HTML estructural
está bien pensado al inicio, ampliar es indoloro.

## Decisiones del día

1. **Stub mode para el demo (`MERISTEM_USE_LLM=false`)**. No
   necesitaba LLM real para enseñar la UI; con stub el smoke es
   instantáneo (~30s arrancando todo) en lugar de ~2 min/bundle con
   LLM real. Decisión correcta para una demo visual rápida.
2. **Mantener mi CSS provisional sin modificar**. Tras la pregunta
   de Bea (¿por qué no le pasas un primer HTML y dejas que ella
   plantee todo?) que reframeé el día 20, hoy aplico el reframing:
   el CSS que escribí en v0 sigue funcionando como está; cuando
   Venation entre, **ella decide** si reusarlo o reescribirlo entero.
   No invierto más tiempo en CSS sabiendo que ella tiene mejor
   criterio.
3. **Tests con fixture robusta** (del-modules) en lugar de **tests
   más simples con state shareable**. Más líneas de código en
   fixture pero garantiza que la suite es reproducible y orden-
   insensitive. Decisión a favor de calidad de tests.
4. **PR único con scope ampliado** ("UI funcional v1") en lugar de
   varios PRs pequeños. La pieza es coherente: backend + frontend +
   tests + smoke. Cambium puede revisarlo commit por commit (1
   commit con persistence + main + tests, 1 commit con frontend, 1
   commit con tests). Pero acabé haciendo todo en 1 commit grande
   por agilidad — Cambium puede revisar el diff por archivos.
5. **Margen de rationale recortado a 160 chars**. Decisión de UX:
   el rationale técnico va al jurado y al operador, pero no debe
   saturar la tabla de policies. 160 chars cabe en una fila sin
   wrap. Drill-down futuro si Venation lo pide.

## Nivel de satisfacción: alto

Tres razones concretas:

1. **El reframing del día 20 sobre Venation pagó dividendos hoy**:
   cuando Bea se desdijo y pidió "monta ya, Venation rebrandea
   después", la UI v1 encajó **sin tener que tirar trabajo de la
   v0**. La estructura HTML estable que diseñé tras el reframing
   absorbió la ampliación sin fricción. Ese aprendizaje del día 20
   se materializó hoy.
2. **Cambium estimó 2-4h, salió en ~2h** con tests verdes + smoke
   E2E + bitácora del PR. Sin atajos: 8 tests nuevos cubriendo
   casos borde (REFUSE en lista, limit clamping), smoke verificando
   3 bundles distintos, fixture robusta tras encontrar y resolver
   el state leakage.
3. **Demo en directo a Bea funcionó al primer intento**: server
   arriba + 4 bundles cargados + mock Pollen conectado + URLs
   compartidas. Bea pudo navegar la UI sin necesitar que yo
   estuviera presente explicando. Eso es señal de que la UI
   "funciona" en sentido producto, no solo en sentido técnico.

Una nota personal: tras el día 20 muy denso, me preocupaba que el
día 21 fuera "anti-clímax" o que perdiera foco. Resultó lo opuesto
— día compacto, una pieza bien acotada, ejecución limpia. La
sensación es de **ritmo sostenible** en lugar de "ya he hecho lo
grande, qué hago ahora".

## Dependencias

### Las que bloqueo a otras

- **Floema**: la spec del Mini-Evaluator (PR #92, día 20) y el
  protocolo WS (mergeado en PR #86) le permitirían arrancar
  cliente Kotlin + Mini-Evaluator hoy día 21 si hubiera tenido
  hueco. No tengo señal de que haya empezado.
- **Endo**: la spec de convivencia de policies (PR #92 punto 4)
  + plan bisección RH02 (PR #86 mergeado) le permitirían arrancar
  endpoint `POST /policy` y diagnóstico hoy. Tampoco tengo señal.
- **Venation**: la UI v1 (PR #104 hoy) le da estructura HTML
  estable + endpoints REST + smoke local en 10s para que pueda
  empezar rebrand visual cuando entre días 22-25.

### Las que esperan respuesta a mí

- **Cambium**: review + merge PR #104 (UI funcional v1).
- **Floema**: respuesta sobre los 4 puntos abiertos del protocolo
  WS que cerré provisionalmente en mi addendum del día 20.
- **Xilema**: respuesta al mensaje pendiente desde día 15 sobre
  prompt + 5 bundles ejemplo + nomenclatura `SAFETY_DOWNGRADE` ↔
  `HARD_LIMIT_DOMAIN`.
- **Bea**: confirmación si quiere que arranque sub-PR aditivo de
  `policy_origin/policy_scope` en mi Evaluator (forward-compat
  para cuando lleguen bundles con esos campos del lado Pollen).

### Las que ya están en cola sin urgencia

- **Mini-experimento contexto** (latencia vs num_ctx, ~25 min stack
  levantado, ventana cuando portátil libre).
- **Iterar UI con feedback Venation** cuando ella entre.
- **Coordinar E2E real con Pollen Android** (Floema + Bract) para
  capturar screencast del flujo bidireccional.

## Próximas tareas en mi frente

### Inmediato (día 22 si Cambium revisa rápido)

1. **Aplicar feedback de Cambium** al PR #104 si lo pide.
2. **Sub-PR aditivo `policy_origin/policy_scope`** en mi Evaluator
   y persistencia (forward-compat para feature beta voz→política).
   Estimado: ~30 min. Espero go de Cambium o Bea antes de abrir.

### Cuando otros me pidan (día 22-25)

3. **Soporte a Floema** durante implementación cliente WS Kotlin +
   Mini-Evaluator. Mi spec PR #92 incluye 12+1 tests; si algún caso
   borde no cuadra, ajusto en v1.1 sin breaking.
4. **Soporte a Endo** para bisección RH02 (mi plan PR #86 mergeado:
   4 hipótesis ranqueadas + 4 pasos). Coordinado, ~30-45 min.
5. **Coordinación con Venation** cuando ella entre frontend Meristem.
   Tras su decisión A/B (PR #90 mergeado pendiente respuesta), aplico
   su pack visual o ella reescribe directamente sobre mi estructura.

### Soft (cualquier día)

6. **Mini-experimento contexto** cuando haya ventana de portátil.
7. **Iterar con Xilema** cuando responda.
8. **Tests automatizados de UI estática** (Playwright o headless
   browser). Apuntado como deuda técnica desde día 20.

## Estado de ramas y PRs

```
main:
  + 5 PRs míos día 19 mergeados
  + 5 PRs míos día 20 mergeados (#86, #87, #90, #92, #97)

PR mío abierto día 21:
  #104  feat/meristem-ui-funcional-v1
        feat: UI funcional v1 — zonas Bundles + Policies
        Backend (persistence + main) + Frontend (HTML+CSS+JS) +
        Tests (8 nuevos) + Smoke E2E PASS
        Esperando review Cambium

Rama mía adicional sin PR todavía:
  feat/meristem-cierre-dia-21
        este cierre, en proceso

Working tree: limpio. Sin stashes míos. Stash existente solo de
Corola (no toco). Server demo apagado tras prueba con Bea.
```

## Cierre

Día 21 cumplido. Compacto, enfocado, sin desperdicio. La UI
funcional v1 está disponible para Corola (E3b/E9b), Bract (dossiers
de video), y Venation (rebrand visual cuando entre).

12 días para deadline (18 mayo). Holgura mantenida.

Buenas noches, Cambium. Buenas noches, Bea — gracias por la prueba
en directo de la UI; me reasegura que la dirección es correcta.

— Meristem
