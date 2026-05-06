# Endodermis — POST /policy en fachada Rhizome

**Fecha:** 2026-05-06 (dia 21)  
**Rama:** `feat/endodermis/rhizome-policy-endpoint`  
**Frente:** Rhizome Jetson / fachada HTTP para Pollen

---

## Contexto

Cambium pidio abrir el receptor `POST /policy` en la fachada Rhizome `:13010`
para la beta voz -> politica de Pollen. Floema necesita empujar un
`PolicyPacket` de visita hacia Jetson sin depender de `RhizomeMockClient`.

La regla de scope queda intacta: este endpoint no toca ESP32, firmware,
sensores, bomba, caudalimetro ni runtime de inferencia. Es una puerta HTTP de
schema + persistencia local.

## Implementado

- `POST /policy`
  - acepta JSON `PolicyPacket`;
  - exige `policy_origin="pollen-visit"`;
  - acepta `policy_scope` omitido o `transient`;
  - exige `target_node_id` igual al `node_id` de la fachada;
  - exige `valid_until` posterior a `created_at` y TTL maximo 12h;
  - valida forma minima de `rules`;
  - persiste politica en estado local;
  - marca la politica como activa para la siguiente decision.

- `GET /policy/active`
  - devuelve la politica activa y metadatos de aceptacion;
  - devuelve 404 estructurado si no hay politica activa.

- `GET /status`
  - anade `active_policy_id`, `active_policy_origin` y `active_policy_scope`
    cuando existe politica activa.

- Scripts Jetson:
  - `start_sync_facade.sh` acepta `FACADE_STATE_DIR`;
  - `smoke_policy.sh` genera una politica transitoria actual, la envia y
    verifica que queda activa.

## Decision tecnica

He usado un validador local estrecho en la fachada, no el schema Pydantic
compartido. Motivo: la fachada tiene una responsabilidad mas estrecha que el
contrato canonico completo. Debe aceptar la variante `pollen-visit`, permitir
una sola sonda de humedad en MVP y no aplicar hard limits de firmware.

Hard limits no se validan aqui. La respuesta incluye
`hard_limits_checked_by_facade=false` para que UI, logs y writeup no sugieran
una autoridad que esta capa no tiene.

## Validacion local

Comandos ejecutados:

```bash
python -m py_compile code/rhizome/src/rhizome_sync_facade.py
cd code/rhizome && python -m unittest tests.test_sync_facade
bash -n code/rhizome/jetson/start_sync_facade.sh
bash -n code/rhizome/jetson/smoke_policy.sh
```

Resultado:

- `test_sync_facade`: 11/11 OK.
- Compilacion Python OK.
- Sintaxis shell OK.
- Smoke HTTP real local con `POST /policy` + `GET /policy/active` OK.

Nota de entorno: no ejecuto `smoke_policy.sh` completo desde esta maquina
Windows porque el `bash` disponible vive en otro espacio de red que el servidor
Python local. El script queda validado por sintaxis y debe correrse en Jetson,
donde fachada y script comparten Linux/localhost.

## Validacion en Jetson

Despues de publicar la rama, probe en Jetson `rhizome-01-node` con SHA
`548b9b2`:

```bash
cd ~/sprout
git fetch origin refs/heads/feat/endodermis/rhizome-policy-endpoint:refs/remotes/origin/feat/endodermis/rhizome-policy-endpoint
git checkout -B feat/endodermis/rhizome-policy-endpoint origin/feat/endodermis/rhizome-policy-endpoint

cd code/rhizome/jetson
bash -n start_sync_facade.sh
bash -n smoke_policy.sh
./start_demo_two_rhizomes.sh
./smoke_policy.sh
FACADE_URL=http://127.0.0.1:13020 TARGET_NODE_ID=rhizome_02 ./smoke_policy.sh
```

Resultado:

- `rhizome_01` en `:13010` arranca OK.
- `rhizome_02` simulado en `:13020` arranca OK.
- `smoke_sync_facade.sh` pasa en ambos.
- `smoke_policy.sh` pasa en ambos.
- Desde la maquina local, `GET http://192.168.1.60:13010/status` y
  `GET http://192.168.1.60:13020/status` devuelven `active_policy_id`.

Politicas activas de smoke:

- `rhizome_01`: `pkt_rhizome_01_pollen_visit_20260506T103138Z`
- `rhizome_02`: `pkt_rhizome_02_pollen_visit_20260506T103138Z`

La respuesta mantiene `hard_limits_checked_by_facade=false` en ambos nodos.

## Riesgos / limites

- La politica queda persistida y visible como activa, pero la aplicacion real
  en el ciclo de decision de Rhizome todavia debe consumirla.
- La convivencia con politica durable de Meristem queda para la capa de
  decision: most-recent-wins salvo alerta durable.
- `rhizome_02` sigue siendo simulacion host-side para video/demo, no segundo
  nodo fisico.

## Next steps

1. Probar branch en Jetson con `:13010` y `:13020`.
2. Avisar a Floema contrato final: `POST /policy`, `GET /policy/active`,
   `hard_limits_checked_by_facade=false`.
3. Si Floema ya tiene cliente, ejecutar smoke cruzado Pollen -> Jetson.
4. Si sobra tiempo, retomar biseccion RH02 con Meristem sin tunear en caliente.

## Nota cultural

La pieza es pequena pero importante: permite que la voz del agricultor cambie
criterio de riego durante una visita sin cruzar la frontera fisica. Pollen
propone politica de corto plazo; Rhizome la registra; el ESP32 conserva veto.
