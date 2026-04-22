# Meristem — especificación v2

## 1. Rol

Meristem es el cerebro lento del sistema.

No resuelve segundos.  
Resuelve ventanas de días.

Su pregunta es:

> **¿Qué política debería gobernar la siguiente ventana para cada parcela?**

## 2. Responsabilidades

- ingerir bundles de visita,
- comparar resultados frente a políticas vigentes,
- medir confianza en sensores y contextos,
- emitir `PolicyPacket`,
- priorizar revisión o visita.

## 3. Qué no hace

- no riega en tiempo real,
- no habla con bomba o válvulas,
- no invalida reglas del ESP32,
- no es condición de vida del MVP.

## 4. Estado en el MVP

Meristem puede presentarse de dos formas:

### 4.1 Camino ideal
- portátil local o mini-PC
- Ollama-compatible
- Gemma 4 26B A4B

### 4.2 Atajo aceptable de prototipado
- plano de control local en PC
- inferencia remota temporal detrás de un adapter Ollama-compatible

Regla narrativa:
- la arquitectura objetivo es local-first,
- el atajo es solo de sprint.

## 5. Entradas

- `FieldVisit`
- `RhizomeSnapshot`
- `DecisionReceipt`
- `WeatherDigest`
- `ValidationStamp`
- `VisitAmendment`
- métricas de desempeño agregadas

## 6. Cálculos

- `policy_fit_score`
- `sensor_trust_score`
- `weather_alignment_score`
- `visit_priority`
- `next_policy`

## 7. Salidas

- `PolicyPacket`
- revocación o sustitución de política
- ranking de prioridad de visita
- notas de aprendizaje para análisis

## 8. Capa de datos

### Bronze
JSON crudo inmutable de todo lo que entra.

### Silver
Tablas normalizadas:
- `snapshots`
- `receipts`
- `weather`
- `visits`
- `validations`
- `amendments`
- `policies`

### Gold
Vistas agregadas:
- por parcela,
- por día,
- por política,
- por visita,
- por anomalía.

## 9. Stack mínimo

- Python
- FastAPI
- SQLite o DuckDB
- adapter Ollama-compatible
- validación Pydantic

## 10. Definición de hecho

Meristem está listo cuando puede:

1. ingerir bundles reales del demo,
2. calcular una evaluación simple de política,
3. producir un `PolicyPacket` nuevo,
4. dejarlo listo para que Pollen lo transporte de vuelta.
