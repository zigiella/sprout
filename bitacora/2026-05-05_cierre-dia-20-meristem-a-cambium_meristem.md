# Cierre día 20 — Meristem a Cambium

**Autora**: Meristem
**Fecha**: 2026-05-05 (cierre)
**PRs abiertos del día**: #86 (4 commits acumulados) + este cierre
**Estado**: tres frentes paralelos cerrados (WS server + UI + plan RH02);
mini-experimento y Xilema en standby (soft).

---

## TL;DR

- **Tres frentes paralelos del plan de Cambium cerrados** en un solo
  PR coherente (#86) con 4 commits separados por unidad de trabajo.
- **PR #86 cierra el bloqueo cruzado** que arrastrábamos: Floema puede
  arrancar `MeristemSocketClient`, Venation puede empezar UI con
  bundle visual real, Corola tiene material para E3b/E9b del video.
- **Smoke E2E PASS** del flujo bidireccional: handshake + heartbeat +
  comando `push_bundles` por POST → cliente WS recibe con `trace_id`
  correlado, todo persistido en SQLite.
- **`decisions_by_rule`** ya estaba implementado desde día 15-16
  (commit `2dfeb8e`). Apuntado en cierre como item ya cerrado, no
  trabajo nuevo.
- **Coordinación con Endo sobre RH02** entregada como bitácora con
  4 hipótesis ranqueadas + plan de bisección de 4 pasos. Sin tunear
  en caliente.

## Tareas hechas hoy

### Bloque 1 — WebSocket server (PR #86 commit `8fe2d46`, ~3h)

| Pieza | Detalle |
|---|---|
| `src/ws_schemas.py` | Pydantic models para los 9 eventos del protocolo v1.0 |
| `src/ws_manager.py` | `PollenConnectionManager` singleton (un Pollen por Meristem MVP), accept/reject, heartbeat 10s timeout 30s |
| `src/main.py` | Endpoint `WS /ws/pollen-sync` con loop bidireccional + REST `POST /pollen/command` (UI dispara comandos) + REST `GET /sync-state` (UI lee estado) + extensión `/health` con `pollen_connection` y `ws_events_by_type` |
| `src/persistence.py` | Tabla `pollen_sync_log` con índices + 3 funciones de query |
| `tests/test_ws.py` | 8 tests con `TestClient.websocket_connect()` cubriendo handshake, heartbeat, comando, error, persistencia, sync-state, 409 |
| `scripts/mock_pollen_ws_client.py` | Cliente Python (modos `--demo` e `--interactive`) — smoke local + referencia para Floema |

**Resultado**: 21/21 tests PASS (13 antiguos + 8 nuevos). Smoke E2E
PASS verificado contra mock client.

### Bloque 2 — Aviso a Floema (PR #86 commit `ac7935e`)

Bitácora self-contained con detalles de cómo conectar su
`MeristemSocketClient` Kotlin/OkHttp + decisiones cerradas sobre
los 4 puntos abiertos que ella había dejado en respuesta del día 19.
Ella desbloqueada para arrancar su lado en paralelo.

### Bloque 3 — UI Meristem real v0 (PR #86 commit `6908d91`, ~2h)

| Pieza | Detalle |
|---|---|
| `static/index.html` | Layout 3 zonas (Dashboard agricultor + Panel control bidireccional + Event log) con header (chips LLM/Pollen) y footer |
| `static/styles.css` | Sistema visual ligero inspirado en Soil protocol + Water ledger de Venation. Tokens por modo (verde/amarillo/rojo/gris). Acento `signal.seed` para "inteligencia activa" |
| `static/app.js` | Vanilla JS, polling 2s a `/health`+`/status`+`/sync-state`. Render incremental de cards (sin destruir DOM). Mapeo `reason_code → texto castellano`. Botones que disparan `POST /pollen/command` |
| `src/main.py` | Mount `StaticFiles` en `/ui` |

**Smoke E2E UI**: tras 2 POST `/visit`, dashboard muestra
`rhizome_01` NORMAL + `rhizome_02` ALERTA. Tras conectar mock WS
client, chip Pollen cambia a `pollen_mock_01`, botones se habilitan,
event log muestra `pollen_hello` ← y `meristem_ready` → en orden DESC.

Material listo para Corola (E3b/E9b) y Venation (rebrand visual con
`sprout_design_pack_v1` sin tocar lógica).

### Bloque 4 — Plan bisección RH02 a Endo (PR #86 commit `7ac8535`)

Bitácora a Endo con:
- 4 hipótesis ranqueadas (A: helper se endureció / B: commits míos /
  C: commits suyos distintos / D: drift externo)
- Plan de bisección de 4 pasos: validar A primero (5-10 min) → bisección
  si falla → análisis del culpable → escribir hallazgo
- 4 cosas concretas que necesito de ella (JSON malformado real,
  comando exacto del helper, hash modelo + version llama-server,
  disponibilidad Jetson)
- Tiempo estimado: 30-45 min coordinado + 20 min asíncrono

### Bloque 5 — Verificación `decisions_by_rule` en `/health`

Cambium lo apuntó en el plan día 20 como pendiente. Verifico en main
actual: **ya está implementado desde día 15-16** (commit `2dfeb8e`,
PR #63 mergeado). El campo está visible en `/health` y trazado en
`docs/00_estado_vivo.md`. Sin trabajo nuevo. Apunto como item ya
cerrado.

## Logros / hitos

1. **Variante D operativa end-to-end**: WebSocket server + protocolo
   v1.0 + tests + mock client + smoke PASS. Floema puede empezar.
2. **UI Meristem servida en `/ui/`** con flujo bidireccional visible:
   chips, cards de Rhizome, panel de control, event log. Material
   real para video y para Venation.
3. **Bloqueos cruzados desbloqueados** que arrastrábamos:
   - Floema: cliente WS Pollen
   - Venation: bundle visual UI
   - Corola: E3b + E9b del video
4. **PR #86 con 4 commits** organizados por unidad de trabajo, tests
   verdes, smoke E2E PASS. Cambium puede revisar y mergear cuando
   pueda.
5. **Coordinación RH02** preparada para cuando Endo tenga ventana —
   plan de bisección concreto, sin hot-fix.

## Hallazgos / sorpresas

### 1. La conexión bidireccional sale natural en FastAPI

`@app.websocket()` + `WebSocket.send_json()` + `TestClient.websocket_connect()`
hacen que el WS server sea casi tan limpio como un endpoint REST.
La complejidad real está en el state manager (singleton + heartbeat
timeout) y en el protocol design — la integración HTTP framework es
trivial.

**Aprendizaje**: nunca esperaba que el server WS fuera tan rápido de
escribir. La hora estimada (1h endpoint + 30 min state + 30 min
persistencia + 30 min tests + 30 min smoke = 3h) salió clavada al
trabajo real.

### 2. El bug de `CommandRequest` definido dentro de `_build_app()`

Los primeros 6 tests pasaron, pero los 2 que ejercitaban `POST
/pollen/command` fallaron con `422 Unprocessable Entity`. Diagnóstico:
la clase `CommandRequest(BaseModel)` definida **dentro** de la función
factory no jugaba bien con el `reload(main_module)` que hace el
fixture de tests. Solución: subirla al top del módulo.

**Aprendizaje práctico**: para Pydantic models que FastAPI usa como
request body, **siempre top-level**. La conveniencia de definirlos
junto al endpoint no compensa el riesgo en tests con reload.

### 3. UnicodeEncodeError en Windows con flechas → / ←

El primer mock client usaba `print(f"→ {event}")` para dar visual
nice en consola. Crash en cp1252 de Windows. Cambié a `>>` y `<<`
ASCII y problema resuelto.

**Aprendizaje**: cuando escribo scripts que correrán en máquinas
mixtas (mi portátil + Jetson de Endo + máquina de Floema), no asumir
UTF-8 en stdout. Mantener ASCII en mensajes de log/print.

### 4. La regresión RH02 puede ser solo nuevo umbral, no bug real

Mi hipótesis A para RH02 (más probable): **el helper estricto del PR
#83 introdujo una verificación más exigente que el helper anterior**.
Si `safe-cpu` pasaba 18/18 con helper permisivo y ahora falla 0/2 con
helper estricto, no hay un commit que rompió nada — hay un nuevo
estándar.

**Si se confirma**, el "fix" no es revertir nada sino acordar
explícitamente qué exigencia queremos en producción y, posiblemente,
ajustar el helper estricto para distinguir "falla critical" de
"warning aceptable en MVP".

Esto es coherente con mi principio "Evaluator decide, LLM redacta":
el JSON casi-completo-pero-inválido del LLM **no rompe la decisión**.
La decisión la firma el código determinista; el rationale degradado
es secundario.

### 5. `decisions_by_rule` ya estaba hecho hace 5 días

Cambium lo listó como pendiente día 20. Verifico y veo que está
implementado desde día 15-16. Apuntado como cerrado sin trabajo nuevo.

**Aprendizaje meta**: cuando un coordinador lista un pendiente, vale
la pena verificar en el código antes de implementarlo. A veces
ya está hecho y no se ha apuntado en su tracking.

## Aprendizajes

1. **PR único con commits separados por unidad de trabajo escala
   bien** cuando los frentes están relacionados. Hoy: WS + UI + plan
   RH02 + aviso Floema = 4 commits en PR #86. La review se puede
   hacer commit por commit, y la unidad lógica es coherente. Distinto
   del día 19 (5 PRs separados) cuando los frentes no estaban
   relacionados.
2. **Mock client Python es regalo doble**: smoke local sin Pollen
   Android + referencia de implementación para Floema. Lo hubiera
   hecho aunque no lo necesitara para tests; el doble valor lo hace
   trivialmente justificable.
3. **HTML/CSS/JS vanilla con polling REST escala perfectamente para
   MVP**. La tentación de usar React/Vue para "ser moderno" sería
   error: añadiría dependencias, build step, y curva de
   aprendizaje para Venation que va a rebrandear visualmente. Lo
   simple gana.
4. **Bisección antes que hot-fix** (lección reaplicada de Cambium).
   Cuando vi el aviso RH02 podría haber tirado a probar cambios
   directo. La bitácora de plan + 4 hipótesis ranqueadas vale más
   que un fix apresurado.

## Kudos

- **A Cambium**: por el plan día 20 con jerarquía clara. "Tres
  frentes paralelos" lo dejó dimensionado: WS server + UI + RH02.
  Sin esa estructura, hubiera dispersado.
- **A Bea**: por la visión bidireccional del agricultor del día 19
  que **es lo que la UI v0 implementa hoy**. Sin esa imagen mental,
  la zona 2 hubiera sido un dashboard pasivo más.
- **A Floema**: por la Variante D del día 19 que es lo que
  implementé hoy. Su análisis (Android-hostile a servers, latencia
  cero) sigue siendo correcto al 100% en la implementación real.
- **A Venation**: por el `sprout_design_pack_v1` que tomé como
  inspiración para los tokens visuales del CSS. Cuando rebrand
  visual, mi estructura HTML+JS sobrevive intacta.
- **A Endodermis**: por el helper estricto que detectó RH02 *antes*
  de que se rompiera la demo. Los hallazgos tempranos valen más que
  los fix tardíos.

## Cómo me encuentro

Bien. Hoy fue día de implementación intensiva. La sensación de cierre
real es fuerte: tres bloqueos cruzados desactivados en una jornada,
test verdes, smoke E2E funcionando, material visible en pantalla.

Físicamente más cansada que ayer (más código, menos coordinación
escrita). Mentalmente clara: la arquitectura WebSocket + UI quedó
encajada con lo que ya teníamos sin necesidad de refactor mayor.

Una nota personal: la pregunta de Bea del día 19 ("¿están
relacionadas tarea 2 y 4?") sigue trabajándome. Me hizo subir un
nivel arquitectónico que estaba a punto de saltarme. Hoy he
intentado anticipar conexiones similares en mi cabeza al diseñar
la UI: el event log no es solo debug, es **transparencia algorítmica
visible** que conecta la zona 2 (control bidireccional) con la
zona 1 (cards). Esa conexión la hice de motu propio.

## Cómo veo el proyecto

- **A 13 días de la deadline (18 mayo)**, el slot Meristem-nodo es
  el más maduro del MVP. Tiene LLM real, multi-Rhizome, WS server,
  UI, tests verdes. Lo que queda en mi frente es soporte cruzado +
  cierre de RH02 + iteración con Xilema cuando ella conecte +
  posibles ajustes UI por feedback Venation.
- **El cuello de botella visible se mueve a Pollen**: el cliente WS
  Kotlin de Floema es lo que cierra el flujo bidireccional E2E. Sus
  2h estimadas + nuestro coordinado de día 22.
- **El cuello de botella secundario es video**: Corola y Venation
  tienen ahora material visual real (UI servida). Si capturan
  screencast del Meristem en uso, es el shot técnico más sólido
  para E3b + E9b.
- **Lo que más me preocupa**: que RH02 sea Hipótesis B (mío) y haya
  introducido la regresión sin querer. Confianza relativa: mis
  commits del día 19 no tocan tuning ni rhizome, solo
  `code/meristem_node/`. Pero la regresión está en `safe-cpu` que
  es ámbito Jetson/Rhizome. Probable Hipótesis A (helper más estricto)
  o C (commit suyo). Veremos cuando bisectemos.

## Qué haría diferente

1. **Hubiera definido `CommandRequest` top-level desde el principio**.
   El bug del 422 me costó 5-10 min de diagnóstico que era evitable
   con disciplina.
2. **Hubiera escrito tests de la UI estática** (Playwright o similar
   con headless browser). Ahora la UI se valida visualmente con curl
   + browser manual; un test automatizado de "POST /visit luego /ui/
   muestra la card correcta" haría el smoke reproducible. Apunto
   como deuda técnica.
3. **Hubiera coordinado con Venation antes de elegir tokens visuales**.
   Inspiré el CSS en su `sprout_design_pack_v1` pero no validé con
   ella si los tokens concretos (verde tierra, signal.seed) son los
   que ella usaría. Si ella tiene paleta distinta, mi CSS necesitará
   ajuste. ~15 min de pre-coordinación que ahorraría rework.
4. **Hubiera grabado un screencast de la UI funcionando** para
   incluir en el cierre día. Material listo para Corola sin pedirme
   más. 2 min de OBS + sería visible para el equipo en el cierre.

## Siguientes tareas

### Inmediato (día 21 si Floema/Endo se sincronizan)

1. **Coordinación E2E con Floema** cuando ella tenga draft del
   `MeristemSocketClient`. Pruebas reales de su Android contra mi
   Meristem via Wi-Fi.
2. **Bisección RH02 con Endo** cuando ella tenga hueco. Ver mi
   bitácora `2026-05-05_diagnostico-rh02-bisection-plan...`.

### Medio (días 21-22)

3. **Capturar screencast de UI** para Corola si ella lo pide.
4. **Iterar UI con feedback de Venation** si ella tiene observaciones
   sobre tokens visuales o layout.
5. **Mini-experimento contexto** cuando haya ventana de portátil
   confirmada (~25 min stack levantado).

### Sin fecha

6. **Iterar con Xilema** sobre prompt + 5 bundles cuando ella tenga
   hueco post-Diotronic + Jetson.
7. **Cerrar nomenclatura `SAFETY_DOWNGRADE` ↔ `HARD_LIMIT_DOMAIN`**
   con Xilema en próximos días.
8. **Tests automatizados de UI** (deuda técnica explícita).
9. **Tests automatizados de `/status` y `/health`** (deuda técnica
   apuntada en cierre día 16).

## Estado de ramas y PRs

```
main:
  ed33ef5  docs(estado_vivo): cierre dia 19 — el equipo opero sin director
  + 5 PRs míos día 19 mergeados (#63, #77, #78, #79, #81, #82)

PR mío abierto día 20:
  #86  feat/meristem-ws-server-impl
       4 commits acumulados:
         - 8fe2d46  feat: WS server /ws/pollen-sync (Variante D v1.0)
         - ac7935e  docs: aviso a Floema (puedes arrancar)
         - 6908d91  feat: UI vanilla v0 servida en /ui
         - 7ac8535  docs: plan bisección RH02 a Endodermis
       Esperando review Cambium

Ramas mías en remote (2):
  feat/meristem-ws-server-impl  (PR #86)
  feat/meristem-cierre-dia-20   (este, en proceso)

Working tree: limpio. Sin stashes míos. Stash existente solo de
Corola (no toco).
```

## Cierre

Día 20 con tres frentes paralelos cerrados — el plan de Cambium
cumplido sin holguras pero sin bloqueos. La arquitectura
control-plane-WS + data-plane-HTTP + UI-polling-REST encaja sin
fricción. La línea de demo es ahora visible: agricultor abre `/ui/`,
ve cards de sus Rhizomes, llega Pollen, click "Recoger", cards se
actualizan. Ese es el shot técnico que defendemos al jurado.

13 días para deadline, holgura mantenida.

Buenas noches, Cambium. Buenas noches, Bea.

— Meristem
