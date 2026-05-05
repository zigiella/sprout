# Rhizome summary + two-node demo facade

**Fecha:** 2026-05-05  
**Autora:** Endodermis  
**Para:** Bea, Cambium, Floema  
**Rama:** `feat/endodermis/rhizome-visit-summary-demo`

## Decision

El boton principal de Pollen sera:

```text
¿Que ha pasado desde mi ausencia?
```

Rhizome expone un endpoint nuevo:

```text
GET /summary/since?since=<iso|null>&locale=es|en
```

Respuesta minima:

```json
{
  "node_id": "rhizome_01",
  "locale": "es",
  "since": null,
  "severity": "attention",
  "headline": "rhizome_01: conviene revisar lo ocurrido en tu ausencia",
  "summary": "Durante tu ausencia...",
  "highlights": ["..."],
  "recommendation": "...",
  "counts": {
    "total": 2,
    "water": 1,
    "block": 1,
    "alert": 0,
    "other": 0,
    "executed": 1
  },
  "latest_snapshot_id": "...",
  "source": "deterministic_demo_summary",
  "simulation": true
}
```

## Inteligencia aplicada

Para el MVP no llamo al LLM en este endpoint. La inteligencia es determinista:

- cuenta riegos, bloqueos y alertas;
- calcula severidad `ok | attention | alert`;
- cruza receipts con snapshot actual;
- incluye deposito y sondas A/B;
- genera una recomendacion breve;
- localiza salida a `es` o `en`.

Motivo: el boton principal necesita ser rapido, testeable y estable. Gemma 4 E2B
puede entrar despues como redactor sobre hechos ya agregados, no como fuente de
verdad.

## Dos Rhizomes en el video

Se puede simular `rhizome_02` desde la misma Jetson:

```bash
cd ~/sprout/code/rhizome/jetson
./start_demo_two_rhizomes.sh
```

Endpoints:

```text
rhizome_01 -> http://192.168.1.60:13010/
rhizome_02 -> http://192.168.1.60:13020/
```

`rhizome_02` usa:

```text
code/rhizome/demo_data/rhizome_02/
```

Esto debe decirse con claridad en bitacora/writeup si se usa en video:

> rhizome_02 es una simulacion host-side en la misma Jetson para demostrar
> interoperabilidad multi-Rhizome. No representa un segundo ESP32 fisico.

## Sobre SOIL A / SOIL B

En el contrato actual, `soil_moisture_a_pct` y `soil_moisture_b_pct` son dos
sondas de suelo dentro de cada Rhizome. Para la UI conviene etiquetarlas como
`Probe A` / `Probe B` o `Soil probe A/B`, no como dos Rhizomes.

Si el video muestra dos Rhizomes, cada uno puede tener sus propias sondas A/B:

- `rhizome_01`: `:13010`
- `rhizome_02`: `:13020`

## Cambio sugerido para Floema

Anadir al cliente Android:

```kotlin
@GET("/summary/since")
suspend fun getVisitSummary(
    @Query("since") since: String? = null,
    @Query("locale") locale: String = "es"
): VisitSummaryResponse
```

Y usarlo como payload principal del boton.
