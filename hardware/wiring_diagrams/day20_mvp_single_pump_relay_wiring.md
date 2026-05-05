# Dia 20 - MVP una linea: bomba 12V con rele

**Objetivo:** montar la parte de potencia del MVP reducido: una unica linea de
riego con una bomba 12V, sin electrovalvulas y sin distribuidor en T.

Alcance fisico del MVP:

```text
Deposito -> bomba 12V -> caudalimetro -> tubo -> planta/parcela A
```

Alcance electrico de este documento:

- fuente 12V
- fusible
- modulo rele 5V
- bomba 12V
- diodo flyback
- buck 12V->5V para alimentar el rele
- frontera de control con ESP32

## 0. Barandilla

No energizar 12V hasta completar:

- inspeccion visual del cableado,
- continuidad sin cortos entre `+12V` y `GND`,
- orientacion del diodo flyback,
- fuente 12V desconectada mientras se manipulan cables,
- ESP32 en `SAFE_IDLE`,
- firmware todavia en `DRY_RUN` para cualquier orden `WATER`.

El ESP32 **no alimenta la bomba** y **no alimenta la bobina del rele**. Solo
manda una senal logica a `IN1` cuando el firmware lo autorice.

## 1. Componentes usados

| Pieza | Uso |
|---|---|
| Fuente 12V DC | Alimenta bomba y buck 5V. |
| Fusible 2A inicial | Protege la rama de 12V del MVP. |
| Portafusible | Debe ir en el positivo de 12V, cerca de la fuente. |
| Buck 12V->5V | Alimenta el modulo rele. |
| Modulo rele 5V, canal 1 | Conmuta el positivo de la bomba. |
| Bomba 12V | Actuador unico del MVP. |
| Diodo 1N400x | Flyback en paralelo con bomba. |
| ESP32-S3 | Control logico, no potencia. |

Fusible inicial recomendado: **2A**. Si la bomba indica consumo nominal mayor
que 1A, revisar antes de energizar.

## 2. Esquema electrico completo

```text
                              DOMINIO 12V

          Fuente 12V +
              |
              |  rojo
              v
        [FUSIBLE 2A]
              |
              |  +12V_PROTEGIDO
              +----------------------------+
              |                            |
              |                            v
              |                       Buck IN+
              |                       Buck IN-
              |                            ^
              |                            |
              |                       GND comun
              |
              v
        Rele canal 1 COM
        Rele canal 1 NO
              |
              |  +12V conmutado
              v
          Bomba +
          Bomba -
              |
              v
          Fuente 12V -


        Diodo flyback en paralelo con la bomba:

          Bomba + ----|<|---- Bomba -
                    raya
                    del diodo
                    hacia Bomba +
```

Lectura del diodo:

- lado con raya del diodo -> `Bomba +`,
- lado sin raya del diodo -> `Bomba -`.

## 3. Conexion de potencia, cable a cable

| Desde | Hasta | Cable / nota |
|---|---|---|
| Fuente 12V `+` | Entrada portafusible | Rojo, fuente desconectada. |
| Salida portafusible | Rele canal 1 `COM` | Rojo, `+12V_PROTEGIDO`. |
| Rele canal 1 `NO` | Bomba `+` | Rojo, positivo conmutado. |
| Bomba `-` | Fuente 12V `-` | Negro, retorno de bomba. |
| Diodo lado con raya | Bomba `+` | Flyback, catodo. |
| Diodo lado sin raya | Bomba `-` | Flyback, anodo. |

No usar `NC`. Queremos que la bomba este apagada por defecto.

## 4. Buck 5V para alimentar el modulo rele

El modulo rele de la foto se trata como modulo de **5V** salvo que su serigrafia
demuestre otra cosa.

```text
Fuente 12V + / despues del fusible -> Buck IN+
Fuente 12V - / GND comun           -> Buck IN-

Buck OUT+ ajustado a 5V            -> Rele VCC
Buck OUT-                          -> Rele GND
```

Antes de conectar el rele al buck:

1. Alimentar solo el buck desde 12V.
2. Medir `OUT+` contra `OUT-`.
3. Ajustar a **5.0V** con el potenciometro si hace falta.
4. Apagar fuente.
5. Conectar buck al rele.

No conectar el buck a `5V` del ESP32. El buck alimenta el rele; el ESP32 queda
alimentado por USB.

## 5. Conexion de control ESP32 -> rele

Esta parte se conecta **despues** de validar potencia sin cortos.

| Desde | Hasta | Estado |
|---|---|---|
| Buck `OUT+ 5V` | Rele `VCC` | Necesario para bobina/electronica del rele. |
| Buck `OUT-` | Rele `GND` | Comun con fuente 12V. |
| ESP32 `GND` | Rele `GND` / GND comun | Necesario para referencia de `IN1`. |
| ESP32 `GPIO16` candidato | Rele `IN1` | Pendiente firmware real, no usar hasta PR. |

Notas:

- Muchos modulos de rele son `active-low`: `IN1=LOW` enciende el rele y
  `IN1=HIGH` lo apaga.
- Por eso el firmware debe arrancar con la salida en estado seguro antes de
  permitir actuadores reales.
- Si el modulo tiene jumper `JD-VCC/VCC`, dejarlo en configuracion simple con
  una sola alimentacion 5V mientras no se documente aislamiento real.

## 6. Estados esperados del rele

Con `COM` y `NO`:

| Estado rele | Contacto `COM-NO` | Bomba |
|---|---|---|
| Rele apagado | Abierto | OFF |
| Rele activado | Cerrado | ON |

Si la bomba queda encendida con el rele apagado, se ha usado `NC` por error.
Apagar fuente y mover el cable a `NO`.

## 7. Checklist antes de energizar 12V

Con fuente desconectada:

- `+12V` pasa por fusible antes de llegar al rele.
- Bomba `+` viene desde `NO`, no desde `NC`.
- Bomba `-` vuelve al negativo de la fuente.
- Diodo con raya hacia `Bomba +`.
- No hay cable de `+12V` tocando protoboard del ESP32.
- No hay cable de bomba conectado a GPIO del ESP32.
- No hay agua por encima o cerca de la electronica.
- Si hay multimetro: continuidad entre `+12V` y `GND` no debe pitar como corto.

## 8. Secuencia de prueba recomendada

### 8.1 Prueba sin ESP32

1. Fuente 12V apagada.
2. Revisar cableado.
3. Encender fuente 12V con la entrada `IN1` del rele sin conectar al ESP32.
4. La bomba debe seguir **apagada**.
5. Si la bomba arranca, apagar inmediatamente: contacto mal elegido o rele
   activado por entrada flotante.

### 8.2 Prueba de rele sin bomba

Antes de bomba real con agua, probar el canal del rele sin carga o con una carga
segura si se dispone de ella. Confirmar que se oye el clic y que `COM-NO` abre
/ cierra.

### 8.3 Prueba con ESP32

Solo despues de PR de firmware de actuadores reales:

1. ESP32 arranca en `SAFE_IDLE`.
2. `STATUS` muestra actuadores bloqueados o `DRY_RUN`.
3. `WATER A 3` no debe energizar bomba si falta heartbeat o deposito seguro.
4. Primer ensayo real: duracion minima, deposito con poca agua y mano en
   interruptor/fuente.

## 9. Decision MVP

Las electrovalvulas quedan fuera de MVP. La semantica visible del sistema se
mantiene como `WATER A`, pero fisicamente solo existe una linea de riego:

```text
PUMP_ON -> agua hacia parcela A
PUMP_OFF -> sin riego
```

`WATER B` y `WATER BOTH` pueden seguir rechazandose o mantenerse como rutas no
montadas hasta que vuelva el diseno de dos parcelas.
