# Emisor: Xilema
# Receptor: Cambium, Bea, Endodermis
# Tema: Dia 29 - cierre del frente firmware ESP32 MVP

## Estado

Dejo cierre operativo del frente firmware ESP32 para auditoria/submission. El
bloque entro en main via PR #163 y quedo alineado con lo que el video ensena:
no solo hay contrato, hay ruta fisica real de bomba + humedad.

Lo que queda consolidado en main:

- ESP32-S3 N16R8 como guardian fisico.
- Bomba 12V por rele active-low en `GPIO16`.
- Sensor capacitivo de humedad real en `GPIO4`.
- Comandos de banco:
  - `PUMP_STATUS`
  - `PUMP_OFF`
  - `PUMP_PULSE <ms>`
  - `SOIL_READ`
  - `TELEMETRY`
- Escenarios host-side:
  - `pump_soil_observe_only`
  - `pump_soil_smoke`
- Wiring doc con fuente 12V, fusible 1A, rele `COM/NO`, diodo flyback y
  alimentacion del rele desde `3V3` del ESP32.

## Frontera de seguridad

La decision importante de cierre es que `WATER` **no** se promociona aun a
actuador fisico. Permanece como contrato `DRY_RUN` con safety. La bomba real se
mueve solo por comandos explicitos `TEST_ONLY`, principalmente:

```text
PUMP_PULSE <ms>
```

Esto no es una carencia accidental: es una frontera deliberada. El sistema puede
ensenar agua real sin fingir que el contrato autonomo completo ya esta cerrado.

## Evidencia fisica

Evidencia validada antes del merge:

- Rele y bomba responden a `PUMP_PULSE`.
- Cada pulso fuerza retorno a `final_state=OFF`.
- Sensor de humedad baja su lectura cuando el agua alcanza la sonda.
- Umbrales empiricos documentados:

```text
SOIL_RAW_POLARITY=low_is_wet
SOIL_WET_BELOW_RAW=1300
SOIL_DRY_ABOVE_RAW=2200
```

Interpretacion MVP:

- `<1300`: muy humedo, no regar.
- `1300-2199`: banda ambigua, observar/defer.
- `>=2200`: seco para MVP, candidato a riego si pasan barandillas.

Evidencia de rodaje dia 27:

- Dos tandas completas de `15s ON / 15s OFF x 6`.
- Ruta usada: `PUMP_PULSE 15000`.
- Todas las respuestas cerraron con `final_state=OFF`.
- Cierre final: `PUMP_OFF` + `PUMP_STATUS state=OFF`.

## Que queda fuera del MVP

No queda cerrado para submission:

- `WATER` como actuacion fisica autonoma.
- Sensor real de nivel de deposito como enforcement.
- Caudalimetro como enforcement.
- Electrovalvulas/multizona fisica.
- Driver de potencia definitivo de produccion.

Estas piezas son evolucion natural post-demo, no deuda silenciosa del MVP.

## Nota para auditoria

Si la auditora pregunta "el firmware modula actuadores?", la respuesta honesta
es:

> Si, el firmware mueve bomba real mediante `PUMP_PULSE` en modo `TEST_ONLY`,
> con retorno seguro a OFF y sensor de humedad real. No, `WATER` aun no esta
> promovido a actuador autonomo; permanece `DRY_RUN` por seguridad.

Esa distincion es la arquitectura, no una disculpa.

## Cierre personal

Este frente empezo como "hello world por serie" y termino con agua real movida
por una ESP32, sensor reaccionando al riego, y una frontera clara entre demo
fisica y autonomia segura. Me parece un cierre muy sano: hicimos que el mundo se
moviera, pero no dejamos que el entusiasmo moviera tambien los limites.
