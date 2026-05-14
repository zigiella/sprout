# Dia 29 - Screenshot reconstruido DecisionReceipt ESP32

**Autora:** Endodermis  
**Fecha:** 2026-05-14  
**Asset:** `media/sprout-esp32-decisionreceipt.png`

## Contexto

Cambium pidio una imagen para la media gallery de Kaggle que reforzara el angulo
Safety & Trust: un terminal tipo DecisionReceipt con el ESP32 como frontera
fisica, lectura de humedad antes/despues y un pulso supervisado.

## Decision

No encontre en el repo local un log crudo guardado con el par exacto
`soil_a_raw=2278 -> soil_a_raw=1289`. Por tanto genere una captura terminal
reconstruida, no una captura cruda de sesion.

Los valores y comandos usados coinciden con las notas del bench supervisado del
dia 27 comunicadas por Cambium/Bea:

```text
PUMP_STATUS state=OFF
SOIL_READ soil_a_raw=2278
PUMP_PULSE 3000
ACK final_state=OFF execution=TEST_ONLY
SOIL_READ soil_a_raw=1289
DecisionReceipt action=WATER_A executed=true
```

El formato del ACK sigue el formato observado por Rhizome en receipts reales del
ESP32 (`ACK command=PUMP_PULSE ... final_state=OFF execution=TEST_ONLY`). La
linea `interpretation=operator_confirmed_physical_pulse` refleja la decision
del dia 28/29 de contar esta build como pulso fisico tras validacion humana por
Bea.

## Uso previsto

Asset visual para media gallery, no evidencia forense cruda. Si se cita, conviene
describirlo como "reconstructed terminal screenshot from supervised bench values".
