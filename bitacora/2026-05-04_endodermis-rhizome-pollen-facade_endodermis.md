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

## Lectura

Esto no cierra la integracion final Rhizome-Pollen. Cierra una pieza concreta:
Floema puede dejar de depender del mock Android y probar contra una IP real del
Jetson con contratos compartidos.

La siguiente evolucion debe sustituir la fuente de datos de esta fachada:

1. primero JSON producido por el harness real de Rhizome;
2. despues SQLite local de Rhizome;
3. finalmente snapshot/receipts nacidos del bucle Jetson + ESP32.
