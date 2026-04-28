# Reglas de seguridad — v2

## 1. Principio rector

La IA puede proponer.  
Solo la capa física puede autorizar la ejecución.

## 2. Reglas no negociables

### 2.1 Depósito bajo
Si `tank_level_pct` cae por debajo del mínimo:
- no se inicia riego,
- se registra rechazo,
- se pasa a modo prudente o alerta según contexto.

### 2.2 Falta de heartbeat
Si el ESP32 no recibe heartbeat reciente del Jetson:
- no acepta nuevas órdenes de riego,
- mantiene actuadores cerrados.

### 2.3 Tiempo máximo por evento
Toda orden de riego tiene límite duro de segundos.

### 2.4 Falta de caudal
Si la bomba/válvula se activa y no aparece caudal esperado:
- cortar,
- alertar,
- bloquear reintento inmediato.

### 2.5 Arranque seguro
Tras reboot del ESP32 o Jetson:
- bomba apagada,
- válvulas cerradas,
- sin auto-reanudación de riego.

### 2.6 Rechazo explícito
Toda orden inválida debe producir motivo legible:
- `TANK_LOW`
- `JETSON_HEARTBEAT_LOST`
- `EVENT_DURATION_OUT_OF_RANGE`
- `NO_FLOW_DETECTED`
- `ALERT_LATCHED`

## 3. Reglas de prudencia de Rhizome

Aunque el ESP32 autorice por física, Rhizome debe degradar a modo conservador si:

- la política está caducada,
- los datos críticos son viejos,
- la visita disputó el estado,
- el presupuesto restante es incierto,
- un digest de meteo cambió el contexto y aún no hay confirmación.

## 4. Prioridad de autoridad

1. stop físico / alert latched
2. límites del ESP32
3. política activa de Rhizome
4. `VisitAmendment` de Pollen
5. `MissionPatch`
6. sugerencias no vinculantes

## 5. Regla de vídeo

El sistema debe enseñar al menos un caso donde:
- la IA propone,
- la capa física bloquea,
- y el bloqueo se explica claramente.

Ese momento aumenta confianza y credibilidad.
