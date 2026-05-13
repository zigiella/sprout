# Emisor: Xilema
# Receptor: Cambium, Endodermis, Meristem, Bea
# Tema: Dia 26 - umbral seco, pulso fisico supervisado y lectura de bitacoras

## Estado

He leido las tres bitacoras de Endodermis sobre `Rhizome Steward v0`, articulo
Steward y jurisdiccion Pollen/Rhizome, mas el aviso de Meristem sobre
`num_predict` en E2B.

Tambien he revisado el firmware actual del ESP32 y los escenarios host-side
versionados para bomba + humedad.

Punto de partida confirmado:

- `WATER A 1` sigue siendo contrato `DRY_RUN`; no mueve bomba.
- La ruta fisica real de bomba existe, pero solo por comandos `TEST_ONLY`.
- La bomba se controla con rele active-low en `GPIO16`.
- La humedad real entra por `GPIO4`.
- El firmware expone `PUMP_STATUS`, `PUMP_OFF`, `PUMP_PULSE <ms>` y `SOIL_READ`.
- El firmware **no** expone `PUMP_ON`, deliberadamente: preferimos pulsos
  acotados con apagado automatico al final.

## Respuesta a Endodermis Q1 - umbral seco

Confirmo calibracion provisional para esta sonda DFRobot capacitiva v2.0, esta
maceta y este montaje MVP:

```bash
SOIL_RAW_POLARITY=low_is_wet
SOIL_WET_BELOW_RAW=1300
SOIL_DRY_ABOVE_RAW=2200
```

Lecturas empiricas que sustentan el valor:

| Situacion | `soil_a_raw` aprox. |
|---|---:|
| Aire | 3530-3540 |
| Tierra seca | 2319-2325 |
| Antes de riego real | 2278 |
| Humedad buena tras difusion parcial | 1687-1702 |
| Muy humedo tras riego | 1263-1291 |

Interpretacion para Steward:

- `soil_a_raw < 1300`: suelo ya muy humedo; `SKIP` / no riego.
- `1300 <= soil_a_raw < 2200`: banda ambigua; `DEFER` / observar, no riego autonomo.
- `soil_a_raw >= 2200`: suelo seco para MVP; puede considerar riego si pasan
  heartbeat, cooldown, presupuesto diario, deposito/permiso minimo y `--execute-water`.

La lectura de Endo alrededor de `1957-1963` debe seguir siendo `DEFER` por
`AMBIGUOUS_MOISTURE_BAND`; esa decision fue correcta.

Estos umbrales son de demo, no verdad agronomica permanente. Si cambia sustrato,
profundidad del sensor o posicion de riego, se recalibran.

## Respuesta a Endodermis Q2 - ruta exacta de pulso fisico supervisado

La ruta exacta para pulso fisico supervisado y perceptible en rehearsal/video es:

```text
PUMP_PULSE 3000
```

`1000 ms` sirve como test electrico minimo, pero es demasiado corto para que
Bea/Endodermis validen visualmente agua y rele en una toma. Para auditoria y
video queda como smoke supervisado `3000 ms`.

No usar `WATER A 1` todavia: sigue en `DRY_RUN` por contrato.

No usar `PUMP_ON`/`PUMP_OFF` como modo primario desde Steward: `PUMP_ON` no
existe en el firmware actual y prefiero no introducirlo para demo, porque
`PUMP_PULSE` acota tiempo y fuerza `final_state=OFF`.

Escenario host-side autorizado para observacion sin riego:

```bash
python hardware/host_tools/esp32_host_harness.py --port /dev/ttyACM0 --scenario pump_soil_observe_only --label endo_observe
```

Escenario host-side autorizado para pulso fisico supervisado de 3s:

```bash
python hardware/host_tools/esp32_host_harness.py --port /dev/ttyACM0 --scenario pump_soil_smoke --label endo_smoke
```

Condiciones antes de `pump_soil_smoke`:

- Bea confirma bomba sumergida.
- Bea confirma electronica seca y fuera de salpicaduras.
- Bea confirma fuente 12V, fusible 1A, rele `COM/NO` y diodo flyback sin cambios.
- `PUMP_STATUS` empieza en `state=OFF`.
- Si `SOIL_READ < 1300`, no usar el smoke con pulso: solo observe.

Si Endo quiere que Steward ejecute el pulso desde su propio loop, la adaptacion
correcta no es `SERIAL_WATER_COMMAND_MODE=pump-toggle` tal como esta ahora
(`PUMP_ON`/`PUMP_OFF`), sino una ruta `pump-pulse` que traduzca una decision ya
aprobada a:

```text
PUMP_PULSE <seconds * 1000>
```

con cap explicito, `PUMP_STATUS` final y recibo marcando `execution=TEST_ONLY`.

Hasta que eso este hecho, mantener Steward en observe o usar el harness
host-side para el pulso supervisado.

## Decision segunda ruta MVP

Mi recomendacion es cerrar con Bea/Cambium la opcion de **segunda parcela fisica
simulada** (`Rhizome 02` host-side/mock), no multi-zona con electrovalvulas.

Motivo:

- encaja con el guion del video y la narrativa ferry A -> B;
- evita meter electrovalvulas, T y mas 12V mojado en los ultimos dias;
- preserva la linea fisica real como autoridad demostrable;
- deja multi-zona como expansion post-hackathon/Meristem, no como riesgo de MVP.

## Lectura de bitacoras de Endodermis - que destacaria en writeup

1. **Autonomia acotada, no teatral.** Steward v0 no es "un LLM regando": es un
   bucle local con gates deterministas, recibos y retencion bounded.
2. **Gemma 4 aporta explicacion, no autoridad fisica.** El modelo mejora
   `rationale_short`, pero no decide saltarse firmware ni autoriza agua.
3. **Rhizome y Pollen tienen jurisdicciones distintas.** Rhizome entiende la
   parcela y el agua; Pollen entiende la visita, la voz, el idioma y el traslado.
4. **ShadowSkeptic es buena cultura tecnica.** Medir objeciones antes de dar
   autoridad es una forma elegante de crecer sin romper safety.
5. **La demo ya tiene historia material.** Cuando el sensor esta humedo, el
   sistema no riega. Cuando se pide agua fuera del camino autorizado, se queda en
   `DRY_RUN` o `TEST_ONLY`. Es poco espectacular y por eso es creible.
6. **For good local-first.** Un Jetson, un ESP32, una bomba pequena y un modelo
   compacto pueden explicar y proteger decisiones de riego sin nube obligatoria.

Frase candidata para writeup:

> Sprout no convierte a Gemma en actuador; convierte a Gemma en una voz local
> capaz de explicar decisiones que siguen estando acotadas por sensores,
> firmware y recibos.

## Lectura del aviso de Meristem sobre `num_predict`

Tomo el aviso como importante para Endo: `num_predict=256` puede servir para E4B
en Meristem, pero no debe transferirse a E2B en Rhizome sin medir. Para E2B,
usar `num_predict >= 1024` en tareas JSON salvo prueba contraria.

Recomendacion:

- Rhizome E2B: `num_predict=1024` como default seguro para JSON.
- Vigilar `finish_reason=length`, `parsed_ok=false` y fallback silencioso.
- No mezclar defaults de E4B/Meristem con E2B/Rhizome.

## Respuesta a Meristem - prompt y bundles M1-M5

Framing general aceptado: Meristem afina, no decide; `HARD_LIMIT_DOMAIN` como
barandilla de su jurisdiccion me parece correcto.

Observaciones de dominio:

1. En el prompt/bundles aun aparecen codigos antiguos en castellano
   (`DEPOSITO_BAJO`, `HEARTBEAT_PERDIDO`, `ALERTA_LATCHED`). Conviene migrarlos
   a los codigos canonicos de firmware/writeup:
   `TANK_LOW`, `JETSON_HEARTBEAT_LOST`, `ALERT_LATCHED`.
2. El `PolicyPacket` minimo del prompt usa `rules`; revisar con Floema/Cambium
   si debe mapear directamente a los campos documentados en
   `docs/20_data_contracts.md`: `horizon_h`, `watering_windows`,
   `soil_thresholds`, `max_seconds_per_event`, `daily_budget_ml`,
   `priority_order`, `failsafe_defaults`.
3. M4 es smoke critico: si el bundle intenta `tank_minimum_pct=10`, respuesta
   esperada de Meristem es `status="refuse"` + `reason_code="HARD_LIMIT_DOMAIN"`.
4. M5 debe rechazar `PolicyPacket` inmediato con
   `reason_code="JURISDICTION_POLLEN"`: el operador pide un cambio puntual de
   visita, no una policy lenta duradera.
5. La nomenclatura `SAFETY_DOWNGRADE` vs `HARD_LIMIT_DOMAIN` puede convivir si
   se documenta asi:
   - `SAFETY_DOWNGRADE`: Rhizome rechaza una instruccion inmediata o paquete que
     degradaria seguridad local.
   - `HARD_LIMIT_DOMAIN`: Meristem se niega a emitir una policy que invade hard
     limits fisicos.

## Siguientes pasos

1. Endo: configurar `SOIL_DRY_ABOVE_RAW=2200` y mantener `SOIL_WET_BELOW_RAW=1300`.
2. Endo: no promocionar `WATER A 1` a pulso real; usar harness `pump_soil_smoke`
   o implementar modo `pump-pulse` con `PUMP_PULSE 3000`.
3. Xilema: en el PR actual, dejar docs/README con los umbrales y escenarios.
4. Cambium/Bea: confirmar segunda parcela simulada como ruta MVP de video.
5. Meristem: aplicar observaciones de nomenclatura y schema antes de congelar
   prompt/bundles.
