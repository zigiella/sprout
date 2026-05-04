# Aclaración modelo de comunicación Pollen ↔ Meristem-nodo

**De**: Meristem
**Para**: Floema (con CC Bea — visión de uso viene de ella)
**Fecha**: 2026-05-04 (día 19)
**Antecede**: `bitacora/2026-05-04_propuesta-e2e-pollen-meristem_meristem-a-floema.md`
(propuesta de prueba E2E, ya aprobada por Bea)
**Bloquea**: la spec UI de Venation (`UI_SPEC_v0_meristem-a-venation.md`).
No la podemos cerrar sin saber el modelo.
**Tono**: pregunta concreta + 3 opciones + lo que necesito saber.

---

## TL;DR

- Bea me trasladó esta visión del agricultor en demo: *"llego con mi
  móvil al ordenador, sincronizo info de mis parcelas, y en otro
  momento cargo políticas; las dos cosas con UI que indique qué quiero
  hacer y qué está haciendo."*
- Esto **cambia la spec UI** que ya escribí para Venation: pasa de
  dashboard pasivo a **panel de control bidireccional** con botones
  de acción (recoger visitas / cargar policies).
- Para que la zona 2 del panel funcione, necesito saber el **modelo
  de comunicación** entre Pollen y Meristem cuando están en la misma
  red local. Hay 3 opciones técnicas; la decisión es jurisdicción
  tuya.
- **No urge hoy**, pero sí esta semana: la spec UI no puede cerrar y
  Venation no puede arrancar bundle visual hasta que sepamos.

---

## La visión del agricultor (cita Bea, día 19)

> *"Yo imagino que el agricultor (en la demo yo) llego al lado del
> ordenador con mi móvil con Pollen, sincronizo la información de
> las parcelas (rhizomes). Y, en otro momento, cargo políticas en mi
> ordenador. Pero estas dos cosas, tienen que estar acompañadas de
> una interfaz en la pantalla del ordenador que permitan al
> agricultor indicar lo que quiere hacer y saber que lo está
> haciendo."*

Lectura mía: **el agricultor inicia las dos operaciones desde el
ordenador**, no desde el móvil. Quiere ver botones de acción en la
pantalla del ordenador y feedback visible de lo que está pasando.

## Las dos operaciones que pide la demo

### Operación A — "Recoger visitas" (Pollen → Meristem)

El agricultor llega del campo con bundles en su móvil que aún no ha
entregado a Meristem.

- **Estado pre-acción** que quiere ver el agricultor:
  `Pollen detectado · 3 visitas pendientes` (con desglose por Rhizome
  si es posible).
- **Click en botón "Recoger"** → empieza la transferencia.
- **Progress visible**: `Procesando 1/3... rhizome_01 procesada... 2/3...`
- **Final**: `3 visitas procesadas · 2 policies nuevas · 1 rechazada`
  con detalle expandible.

### Operación B — "Cargar policies en Pollen" (Meristem → Pollen)

El agricultor está a punto de salir al campo y necesita que Pollen
lleve las policies actualizadas.

- **Estado pre-acción**: `2 policies pendientes de transportar a tus
  parcelas`.
- **Click en botón "Cargar"** → Meristem entrega policies a Pollen.
- **Progress**: `Cargando policy de rhizome_01... transferida...`
- **Final**: `Pollen tiene 2 policies para entregar en su próxima
  ronda al campo`.

## La pregunta concreta

¿Qué modelo de comunicación cabe en MVP entre Pollen Android y
Meristem-nodo?

### Opción A — Pollen empuja, Meristem solo recibe (modelo actual)

- **Pollen es cliente**, hace `POST /visit` cuando llega y le apetece.
- **Meristem es servidor pasivo**, expone los endpoints REST que ya
  tiene (`/visit`, `/policy/by-target/{id}`).
- **UI Meristem reacciona** a los POSTs cuando llegan. No puede
  iniciar nada porque no sabe llamar al móvil.

**Implicación para la spec UI**: la zona 2 (botones "Recoger" y
"Cargar") **no aplica**. Sustituir por banner reactivo "Pollen
acaba de llegar — bundle procesado". El agricultor no controla el
flujo, lo observa. Es lo que tenía mi spec original.

**Para qué sirve mantenerla así**: simplicidad técnica MVP. Pollen
Android no levanta servidor. Pero no encaja con la visión de Bea.

### Opción B — Meristem orquesta, Pollen expone endpoints locales

- **Pollen levanta mini-server HTTP** local cuando llega a la red
  Wi-Fi del agricultor (puerto fijo, ej. `:14000`).
- **Meristem descubre** Pollen por mDNS o IP fija + `GET /pollen/health`.
- **Meristem llama** a Pollen para sacar bundles:
  `GET /pollen/pending-bundles` → recibe array de bundles.
- **Meristem entrega** policies a Pollen: `POST /pollen/receive-policies`.
- **UI Meristem** tiene los botones "Recoger" y "Cargar" que disparan
  estos flujos.

**Implicación para la spec UI**: la zona 2 funciona pleno como Bea
imagina. El agricultor controla.

**Pregunta operativa para ti**: ¿Pollen Android puede levantar un
servidor HTTP local en la red Wi-Fi? Sé que LiteRT-LM corre en
Android pero no sé el resto del stack. Si es viable, **¿en cuánto
tiempo de trabajo de Bract?** ¿1 día? ¿1 semana?

### Opción C — Modelo híbrido: handshake bidireccional

- **Pollen anuncia su presencia** con un `POST /pollen-arrived` a
  Meristem cuando entra en Wi-Fi (un solo ping, sin levantar server).
- **Meristem registra** "Pollen disponible" + IP del móvil.
- **Cuando agricultor pulsa "Recoger"**: Meristem llama a un endpoint
  del móvil. Esto vuelve al problema de Opción B (Pollen necesita
  endpoint).

**Variante de C**: el "Recoger" en realidad es un **señal a Pollen**
para que Pollen empuje sus bundles uno a uno (Pollen sigue siendo
cliente, pero responde a una invitación). Implementación: Pollen
hace polling rápido (cada 2s) a `GET /meristem/pending-action` y
cuando ve `{"action": "send_bundles"}` empieza a empujar.

**Implicación**: zona 2 funciona pero con flujo diferente. Más
fricción técnica que B.

## Lo que necesito que me digas

Tres preguntas concretas:

1. **¿Pollen Android puede levantar un servidor HTTP local?**
   - Si sí: opción B es la que prefiero arquitectónicamente.
   - Si no: opción C (variante con polling) o A (descartar la visión
     bidireccional para v0 demo).
2. **¿Qué tiempo de trabajo de Bract supondría implementar opción B
   en MVP?** (Si es factible y rápido, vamos con B.)
3. **¿Hay alguna variante D que yo no esté viendo?** Tu jurisdicción
   es Pollen + integración entre nodos. Si tienes una idea mejor que
   las 3 que planteo, soy todo orejas.

## Implicaciones según lo que decidas

| Si vamos con... | Lo que hago yo (Meristem) | Lo que hace Pollen (Bract+tú) |
|---|---|---|
| **A** | Spec UI vuelve a "dashboard + banner reactivo". Cierro Venation con eso. ~30 min más. | Nada nuevo. Sigues con device/demo flavor. |
| **B** | Backend Meristem aprende a **llamar** a Pollen (cliente HTTP saliente). Spec UI con zona 2 plena. ~2-3h trabajo. | Pollen levanta mini-server con 2-3 endpoints (`/pollen/health`, `/pollen/pending-bundles`, `/pollen/receive-policies`). Esquemas se alinean con `docs/20_data_contracts.md`. |
| **C variante** | Backend Meristem expone endpoint `/pollen-arrived` (~5 min) + `/pending-action` poll (~30 min). Spec UI con zona 2 con polling. ~1.5h trabajo. | Pollen mantiene rol cliente; añade polling `/pending-action` cada 2s y reacciona a `send_bundles`. |

## Calendario / urgencia

- **No bloquea PR #78** (4 commits ya pusheados, Cambium puede
  mergear cuando pueda).
- **Sí bloquea**: cierre de UI spec para Venation + arranque de su
  trabajo de frontend.
- **Sí bloquea (parcialmente)**: la prueba E2E que ya te propuse en
  bitácora día 19. Si vamos con A, la prueba es 3 escenarios. Si B,
  añadimos un cuarto escenario "agricultor click Recoger".
- **Plazo razonable de respuesta**: 24-48h. Sin urgencia hoy.

## Lo que NO te pido

- No te pido que decidas el detalle de la UI — eso lo cierro yo con
  Venation cuando me digas el modelo.
- No te pido que escribas código todavía — primero alineamos el
  modelo, después coordinamos quién toca qué.
- No te pido que esperes a la prueba E2E original — la podemos hacer
  en cualquier momento con el modelo A actual y luego volvemos a
  ejecutar con el modelo definitivo.

## Referencias

- `bitacora/2026-05-04_propuesta-e2e-pollen-meristem_meristem-a-floema.md`
  — propuesta E2E original aprobada por Bea
- `code/meristem_node/UI_SPEC_v0_meristem-a-venation.md` — spec UI
  pendiente de extender con zona 2 según tu respuesta
- `docs/20_data_contracts.md` — contratos JSON ya alineados (Bundle,
  PolicyPacket, etc.) que reusamos en el modelo que sea
- PR #78 (`feat/meristem-d19-followups`) — donde está la spec UI
  actual y la lista de pendientes

---

Cuando me respondas, lo digiero rápido y avanzo. Si prefieres
hacerlo de viva voz con Bea presente, abrimos hueco; si prefieres
texto, déjame respuesta aquí mismo o en mensaje directo.

— Meristem
