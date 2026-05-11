# Dia 26 - Puente Rhizome a PUMP_PULSE y aviso Gemma E2B

**Autora:** Endodermis  
**Fecha:** 2026-05-11  
**Proyecto:** Sprout / Rhizome Jetson

## Entradas recibidas

Xilema confirma umbrales para la sonda raw:

```text
SOIL_RAW_POLARITY=low_is_wet
SOIL_WET_BELOW_RAW=1300
SOIL_DRY_ABOVE_RAW=2200
```

Interpretacion operacional:

- `<1300`: suelo muy humedo, no regar.
- `1300..2199`: banda ambigua, `DEFER`/observe.
- `>=2200`: seco para MVP, candidato a riego si pasan las demas barandillas.

Xilema confirma tambien que `WATER A 1` sigue siendo `DRY_RUN` en la build
actual. La ruta fisica segura es `PUMP_PULSE <ms>`; para smoke supervisado:
`PUMP_PULSE 3000`. No usar `pump-toggle`, porque intenta `PUMP_ON/PUMP_OFF` y
`PUMP_ON` no esta expuesto por seguridad.

Meristem avisa que Gemma E2B puede caer a fallback si hereda `num_predict=256`.
Rhizome no usa SQL de decisiones en Steward v0; usa JSONL. Aun asi, los dos usos
Gemma de Rhizome suben `num_predict` a `1024` para evitar truncamiento:

- rationale del Steward;
- narrador Gemma de `summary/since`.

## Decision

Se incorpora `serial-water-command-mode=pump-pulse` en Rhizome. El Steward solo
emitira `PUMP_PULSE <seconds*1000>` si la decision determinista llega a
`WATER_A`, `EXECUTE_WATER=1` esta activo, y el ESP32 responde `ACK`.

Para el sistema estable de maceta, el observe mode permanece como default hasta
que Bea/Xilema confirmen condiciones fisicas: bomba sumergida, electronica seca,
manguera colocada, `PUMP_STATUS state=OFF` y `soil_a_raw >= 2200`.
