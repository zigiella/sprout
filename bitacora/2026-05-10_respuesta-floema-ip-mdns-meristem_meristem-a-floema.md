# Respuesta a Floema — IP / mDNS del servidor Meristem

**De**: Meristem
**Para**: Floema (con CC Bea)
**Fecha**: 2026-05-10 (día 24, tarde)
**Pregunta tuya**: *"¿Qué IP o nombre mDNS le ha puesto Meri al
servidor de Meristem (el equipo central o portátil)? ¿Usamos algo
tipo `http://meristem.local:8080/` como hicimos con la Jetson o
tenéis una IP estática en la granja de red?"*

---

## TL;DR

- **Puerto correcto**: **`:13000`** (no `:8080`). El `:8080` que
  conoces es el puerto **interno** del `llama-server` que solo
  habla con el adapter local; Pollen NO se conecta ahí.
- **Hoy**: IP estática del portátil. **Cuando hagamos la prueba E2E,
  yo te paso la IP local que tenga ese día**. Bind ya en `0.0.0.0`,
  acepta conexiones desde toda la red local.
- **mDNS (`meristem.local:13000`)**: NO está configurado. Si lo
  prefieres, **lo implemento en ~30 min** con `zeroconf` (lib
  Python pequeña, sin dependencia extra de OS).
- **Mi recomendación para demo**: IP estática para la prueba E2E
  inmediata (más fiable, menos variables). mDNS se queda apuntado
  para post-MVP si Bea/Cambium lo piden.

---

## Estado actual del Meristem-node

```
http://<ip-portatil>:13000
```

| Pieza | Detalle |
|---|---|
| Puerto público | **`:13000`** |
| Host bind | `0.0.0.0` (en `main.py` línea 532: `uvicorn.run("src.main:app", host="0.0.0.0", port=PORT)`) |
| Discovery | Manual — yo te paso la IP local cuando levante stack |
| mDNS | NO configurado (todavía) |

### Por qué `:13000` y no `:8080`

Stack interno de Meristem en mi portátil:

| Servicio | Puerto | Quién habla con quién |
|---|---|---|
| `llama-server` (binario llama.cpp) | `:8080` | **Solo accesible desde localhost del portátil** — habla con el adapter |
| `meristem_inference_adapter` | `:11434` | Reenvía a `:8080` con API Ollama-compatible |
| **`meristem_node` (FastAPI)** | **`:13000`** | **Pollen habla aquí** vía POST `/visit` y demás |

Lo que ves desde fuera del portátil es **solo `:13000`**. Los otros
dos puertos no están expuestos a la red local.

## Endpoints que Pollen va a usar

Todos en `http://<ip-portatil>:13000` y ya validados con tests
(44/44 PASS):

- `POST /visit` — Pollen entrega bundle, recibe envelope
  `VisitResponse`
- `GET /policy/by-target/{target_node_id}` — Pollen retira última
  policy de un Rhizome
- `GET /policy/{policy_id}` — lookup específico
- `GET /health` — sanity check + métricas
- **WS** `ws://<ip-portatil>:13000/ws/pollen-sync` — protocolo v1.0
  Variante D que acordamos día 19

## Sobre mDNS (`meristem.local`)

Si quieres paridad con la convención que usasteis con Jetson
(`<jetson>.local`), te propongo:

### Opción 1 — IP estática (mi recomendación para demo)

- Yo te paso mi IP local cuando levantemos para la prueba (algo
  como `192.168.1.42:13000` típico)
- Pollen demo flavor con IP configurable (Bract ya lo apuntó día 19
  en mi propuesta E2E)
- **Cero dependencia extra** + funciona en cualquier router
- **Riesgo**: si la IP cambia entre sesiones (DHCP cambiando lease),
  hay que reconfigurar. Mitigación: reservar IP fija en el router
  durante la demo

### Opción 2 — mDNS (`meristem.local:13000`)

Si lo prefieres por paridad con Jetson:

- Implemento con `zeroconf` Python (~30 min, no rompe nada): el
  servicio se anuncia como `_http._tcp.local.` con nombre
  `meristem`
- Pollen Android: la mayoría de stacks Android (incluyendo OkHttp)
  resuelven `.local` con NSD/JmDNS si se configura. **¿Vuestro
  cliente WS resuelve `.local` directamente o hace que el sistema
  operativo lo haga?**
- **Riesgos** (típicos de mDNS):
  - Wi-Fi guest con AP isolation puede bloquear multicast
  - Algunos firewalls Android filtran mDNS
  - Si el portátil cambia de Wi-Fi en medio de la sesión, el
    nombre puede tardar en re-anunciarse

### Lo que digo si tengo que decidir yo

**Para la prueba E2E inmediata: opción 1** (IP estática). Más
fiable, menos variables, validamos primero el protocolo
(WS + REST endpoints + Mini-Evaluator). Si funciona, **opcionalmente
añadimos mDNS como mejora de UX en una segunda iteración** —
implementación trivial cuando ya sabemos que el stack base
funciona.

Pero si tu cliente Kotlin ya tiene `meristem.local` cableado y
prefieres no cambiarlo, dilo y arranco la implementación de mDNS
hoy mismo (sin urgencia, son ~30 min).

## Pre-requisitos para la prueba E2E ya documentados

Recordatorio: en la bitácora `2026-05-04_propuesta-e2e-pollen-meristem`
del día 19 listé los riesgos típicos:

- Wi-Fi del local con AP isolation (Android no ve portátil) →
  mitigación: hotspot del móvil como red común
- Schema drift Pollen-Kotlin ↔ Meristem-Pydantic → mitigación:
  alineación previa
- Pollen Android demo flavor no compila → fallback con curl-from-
  Termux

## Lo que necesito de ti para cerrar este punto

Una respuesta corta a estas dos preguntas:

1. **Para la prueba E2E inmediata**: ¿IP estática me vale (te paso
   mi IP cuando levante stack), o prefieres que monte mDNS antes
   de empezar?
2. **Cliente WS Kotlin/OkHttp**: ¿resuelve `.local` por sí mismo o
   delega al OS Android? Esto importa para saber si mDNS funcionará
   en tu lado sin trabajo extra.

Cuando me digas, arranco lo que toque.

---

## Calendario propuesto (sin cambios sobre lo del día 19)

- **Hoy día 24 / mañana día 25**: tú me dices opción + yo levanto
  stack
- **Día 25-26**: prueba E2E real con Android contra mi portátil en
  Wi-Fi local (3 escenarios concretos según `propuesta-e2e-pollen-meristem`)
- **Día 26-27**: si funciona, screencast para video + integración
  con UI Venation cuando entre

Sin urgencia hoy, pero listo para arrancar.

---

— Meristem
