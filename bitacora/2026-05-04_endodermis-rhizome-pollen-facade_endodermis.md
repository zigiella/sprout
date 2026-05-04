# Dia 19 - Fachada minima Rhizome -> Pollen

**Autora:** Endodermis
**Fecha:** 2026-05-04
**Dia de proyecto:** 19
**Rama:** `feat/endodermis/rhizome-pollen-sync-facade`

## Contexto

Tras repetir el tramo Jetson de Xilema, reviso el siguiente cruce con Floema.
Pollen ya tiene un `RhizomeNetworkClient` en su rama F5, pero la pantalla
`VisitarRhizomeScreen` sigue instanciando `RhizomeMockClient`.

El cliente de Pollen espera:

- `GET /status`
- `GET /snapshot/latest`
- `GET /receipts?since=...`
- `GET /explain/decision/{id}`

En el Jetson, los servicios vivos del dia 19 son:

- `llama-server` en `:8080`;
- `meristem_inference_adapter` en `:12000`.

Ninguno de los dos es la API local de Rhizome para Pollen. Son servicios de
inferencia. Apuntar Pollen a ellos directamente no sirve.

## Decision

Construyo una fachada HTTP de lectura, minima y aislada, en
`code/rhizome/src/rhizome_sync_facade.py`.

Alcance:

- sirve los cuatro endpoints de lectura documentados;
- responde JSON compatible con las clases Kotlin de Pollen;
- usa ejemplos de `code/shared/schemas/examples` como fuente local;
- no toca ESP32;
- no toca actuadores;
- no llama al LLM;
- no finge ser la persistencia definitiva de Rhizome.

Puerto propuesto para prueba con Pollen:

```text
http://192.168.1.60:13010/
```

## Pruebas

Ejecuto:

```bash
cd code/rhizome
python -m unittest tests.test_sync_facade
```

Resultado:

```text
Ran 4 tests
OK
```

Anado scripts Jetson:

- `code/rhizome/jetson/start_sync_facade.sh`
- `code/rhizome/jetson/smoke_sync_facade.sh`

Validacion local:

```bash
bash -n code/rhizome/jetson/start_sync_facade.sh
bash -n code/rhizome/jetson/smoke_sync_facade.sh
```

Estos scripts arrancan la fachada en `:13010` y prueban los cuatro endpoints
que Pollen consume.

Validacion en Jetson:

```bash
cd ~/sprout
git fetch origin refs/heads/feat/endodermis/rhizome-pollen-sync-facade:refs/remotes/origin/feat/endodermis/rhizome-pollen-sync-facade
git checkout -b feat/endodermis/rhizome-pollen-sync-facade origin/feat/endodermis/rhizome-pollen-sync-facade
cd ~/sprout/code/rhizome/jetson
./start_sync_facade.sh
./smoke_sync_facade.sh
```

Resultado:

```json
{"status":"ok","facade_url":"http://127.0.0.1:13010","snapshot_id":"snap_rhizome_01_20260416T143205_a3f2","receipts":2,"explained_decision_id":"rec_rhizome_01_20260416T143010_91ba"}
```

Validacion desde el portatil:

```bash
curl http://192.168.1.60:13010/status
```

Resultado:

```json
{"status":"ready","version":"0.1.0","node_id":"rhizome_01","mode":"read_only_facade","source":"/home/rhizome_01/sprout/code/shared/schemas/examples"}
```

Estado fisico: ESP32+BME desconectados. No hacen falta para esta fachada.

## Confirmacion de Floema

Bea comunica que Floema ya ha probado el endpoint y dice que es OK.

Lectura:

- primera prueba Pollen -> Jetson real superada;
- el endpoint `:13010` cumple su funcion de puente temporal;
- no se ha necesitado ESP32+BME para esta validacion;
- siguiente paso natural: que Floema consolide, si lo considera, el cambio de
  `RhizomeMockClient` a `RhizomeNetworkClient("http://192.168.1.60:13010/")`
  en su rama o en modo demo controlado.

## Lectura

Esto no cierra la integracion final Rhizome-Pollen. Cierra una pieza concreta:
Floema puede dejar de depender del mock Android y probar contra una IP real del
Jetson con contratos compartidos.

La siguiente evolucion debe sustituir la fuente de datos de esta fachada:

1. primero JSON producido por el harness real de Rhizome;
2. despues SQLite local de Rhizome;
3. finalmente snapshot/receipts nacidos del bucle Jetson + ESP32.
