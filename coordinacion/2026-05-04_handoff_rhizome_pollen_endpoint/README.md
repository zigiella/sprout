# Handoff Rhizome -> Pollen endpoint

**Fecha:** 2026-05-04  
**Autora:** Endodermis  
**Para:** Floema, Cambium  
**Rama:** `feat/endodermis/rhizome-pollen-sync-facade`

## Estado

La Jetson `rhizome_01` tiene una fachada HTTP de lectura viva para que Pollen
pueda probar contra una IP real sin depender de `RhizomeMockClient`.

Base URL:

```text
http://192.168.1.60:13010/
```

Endpoints:

```text
GET /status
GET /snapshot/latest
GET /receipts?since=...
GET /explain/decision/{id}
```

## Comandos ejecutados en Jetson

```bash
cd ~/sprout/code/rhizome/jetson
./start_sync_facade.sh
./smoke_sync_facade.sh
```

Smoke:

```json
{"status":"ok","facade_url":"http://127.0.0.1:13010","snapshot_id":"snap_rhizome_01_20260416T143205_a3f2","receipts":2,"explained_decision_id":"rec_rhizome_01_20260416T143010_91ba"}
```

Validacion externa desde portatil:

```bash
curl http://192.168.1.60:13010/status
```

Respuesta:

```json
{"status":"ready","version":"0.1.0","node_id":"rhizome_01","mode":"read_only_facade","source":"/home/rhizome_01/sprout/code/shared/schemas/examples"}
```

## Que puede hacer Floema

En `VisitarRhizomeScreen`, sustituir temporalmente:

```kotlin
RhizomeMockClient()
```

por:

```kotlin
RhizomeNetworkClient("http://192.168.1.60:13010/")
```

La slash final importa para Retrofit.

## Validacion de Floema

Floema prueba el endpoint desde Pollen y confirma resultado OK.

Lectura de Endodermis:

- el cliente Android puede hablar con una IP real de Jetson;
- la frontera `RhizomeMockClient` -> `RhizomeNetworkClient` queda desbloqueada;
- la API servida por Jetson encaja con los contratos Kotlin esperados por
  Pollen para visita;
- la prueba sigue siendo de interoperabilidad host-side, no de sensores reales
  ni de riego fisico.

## Limites

- No es el backend definitivo de Rhizome.
- No lee sensores reales.
- No toca ESP32.
- No ejecuta riego.
- No llama al LLM.
- Sirve ejemplos de `code/shared/schemas/examples`.

Esto es una pieza de interoperabilidad para desbloquear prueba Pollen -> Jetson
con contratos compartidos. La fuente de datos debe migrar luego a outputs reales
de Rhizome y, despues, a SQLite local.
