# Endodermis — smoke main Jetson + cambio de IP WiFi

**Fecha:** 2026-05-08 (dia 23)  
**Frente:** Rhizome Jetson / fachada Pollen  
**Jetson actual:** `192.168.1.31`

---

## Contexto

Cambium pidio repetir desde `main`:

- `start_demo_two_rhizomes.sh`
- `smoke_policy.sh`

La Jetson habia cambiado de WiFi y dejo de responder en la IP historica
`192.168.1.60`. Bea confirmo nueva IP:

```text
192.168.1.31 172.17.0.1
```

## Validacion desde main

En Jetson:

```bash
cd ~/sprout
git checkout main
git pull --ff-only origin main
cd code/rhizome/jetson
bash -n start_sync_facade.sh
bash -n smoke_policy.sh
bash -n start_demo_two_rhizomes.sh
./start_demo_two_rhizomes.sh
./smoke_policy.sh
FACADE_URL=http://127.0.0.1:13020 TARGET_NODE_ID=rhizome_02 ./smoke_policy.sh
```

Resultado:

- `main` en SHA `1cfd4f9`.
- `rhizome_01` arranca en `:13010`.
- `rhizome_02` simulado arranca en `:13020`.
- Smoke lectura OK en ambos.
- Smoke `POST /policy` OK en ambos.
- Respuesta mantiene `hard_limits_checked_by_facade=false`.

## Hallazgo pequeno

`start_demo_two_rhizomes.sh` imprimia endpoints hardcodeados con
`192.168.1.60`, que ya no era la IP actual. La fachada funcionaba bien, pero
la cartela operativa podia confundir a Pollen o a rodaje.

## Microfix propuesto

Rama:

```text
feat/endodermis/demo-host-ip-output
```

Commit:

```text
60e6075 fix(rhizome): print current Jetson demo host
```

Cambio: el script calcula `DEMO_HOST` con `hostname -I`, prioriza IP
`192.168.*` y permite override por variable de entorno.

Validacion del microfix en Jetson:

- la cartela ya imprime:

```text
rhizome_01 -> http://192.168.1.31:13010/
rhizome_02 -> http://192.168.1.31:13020/
```

- `smoke_policy.sh` vuelve a pasar en `rhizome_01` y `rhizome_02`.
- Desde maquina local, `GET /status` responde en `192.168.1.31:13010` y
  `192.168.1.31:13020`.

## Nota

El microfix no cambia contrato, seguridad, politicas ni runtime de inferencia.
Solo evita mostrar una IP obsoleta cuando cambia la WiFi.
