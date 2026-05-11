# Dia 26 - Loop de maceta, calibracion demo y `TEST_ONLY`

**Autora:** Endodermis  
**Fecha:** 2026-05-11  
**Rama:** `feat/endodermis/serial-write-retry-day26`

## Contexto

Bea pidio pasar de un smoke puntual a una autonomia minima observable: Rhizome
conectado al ESP32 y a la maceta, con decisiones cada 5 minutos, receipts
persistentes y lectura visible desde Pollen. La prueba se hizo con el sensor de
humedad real, sin sensor de deposito y sin caudalimetro funcional en el MVP.

## Cambios realizados

- El loop de Steward quedo en modo prueba supervisada: `DECISION_INTERVAL_S=300`,
  `COOLDOWN_S=300`, `MAX_AUTONOMOUS_WATERS_PER_DAY=96`.
- El umbral temporal de prueba quedo en `SOIL_DRY_ABOVE_RAW=1500` con polaridad
  `low_is_wet`.
- La duracion de pulso subio progresivamente de 3s a 10s y finalmente a 20s
  porque la bomba necesita cebarse antes de sacar agua visible.
- Se expuso `MAX_AUTONOMOUS_WATERS_PER_DAY` en `run_steward_once.sh` para que el
  presupuesto diario no quede hardcodeado durante pruebas.
- Se anadio un indice visual de humedad para demo derivado del raw:
  `soil_moisture_a_pct`, `soil_moisture_a_raw`,
  `soil_moisture_a_pct_estimated=true`, `soil_moisture_calibration=demo_raw_index`.
  La intencion es que Pollen pueda pintar una barra comprensible sin fingir que
  el sensor ya esta calibrado fisicamente.
- Se corrigio la trazabilidad de receipts: si el ESP32 responde
  `execution=TEST_ONLY`, Rhizome ya no cuenta el evento como riego fisico
  ejecutado. El receipt queda como `executed=false`,
  `blocked_reason=ESP32_TEST_ONLY` y conserva `esp32_execution_mode=TEST_ONLY`.

## Hallazgos

Rhizome si esta decidiendo y enviando comandos al ESP32 (`PUMP_PULSE 20000` en la
configuracion final del dia). Bea oyo la bomba en algunos ciclos, pero no de
forma consistente ni necesariamente con salida visible de agua. Todos los ACK
observados devuelven `execution=TEST_ONLY`, asi que la frontera correcta de
trazabilidad es: comando aceptado por ESP32, pero no contabilizado como riego
fisico confirmado.

El nombre `TEST_ONLY` necesita aclaracion con Xilema: puede significar build de
test, ausencia de caudalimetro, o ejecucion fisica sin garantia de agua. Hasta
cerrarlo, Sprout debe hablar con prudencia en Pollen y en receipts.

## Estado al cierre

Steward queda funcionando durante dos horas mas con:

```text
intervalo: 300s
cooldown: 300s
pulso: 20s
comando: PUMP_PULSE 20000
umbral: soil_raw >= 1500
```

Se dejo una guardia de noche que parara el run-loop a las `22:02:54+02:00`.
La fachada REST `:13010` queda viva para que Pollen pueda leer el ultimo estado.

## Pendientes

- Preguntar a Xilema que significa exactamente `execution=TEST_ONLY` en esta
  build y que condicion/firmware habilita ejecucion fisica confirmable.
- Mantener los 20s solo como perfil de prueba supervisada; no promocionarlo a
  default sin caudalimetro o validacion fisica.
- Ajustar el copy de Pollen para distinguir "estimacion demo" de "humedad
  calibrada".
- Manana repetir con bomba conectada, observacion visual y, si Xilema confirma,
  nomenclatura de ejecucion mas precisa para receipts.
