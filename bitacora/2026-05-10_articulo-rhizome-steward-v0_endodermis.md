# Rhizome Steward v0: autonomia local-first con Gemma 4, Jetson y veto fisico

Sprout no intenta demostrar que una IA pueda "regar una planta". Intenta
demostrar algo bastante mas dificil: que una arquitectura local-first puede
tomar decisiones utiles en un entorno fisico real, con conectividad incierta,
agua limitada y seguridad verificable. La implementacion de **Rhizome Steward
v0** convierte esa idea en un bucle minimo pero verdadero de autonomia.

Rhizome corre sobre **Jetson Orin Nano Super** y actua como el nodo local de
parcela. Su mision no es tocar actuadores directamente, sino observar, decidir
dentro de su jurisdiccion y dejar trazabilidad. La frontera fisica pertenece al
**ESP32**, que conserva autoridad sobre sensores criticos, bomba, caudalimetro,
reglas duras y failsafe. En Sprout, la inteligencia propone; lo fisico veta.

La nueva implementacion cierra el ciclo operativo:

```text
ESP32 heartbeat
-> ESP32 telemetry
-> RhizomeSnapshot
-> safety/need gate determinista
-> Gemma 4 rationale opcional
-> WATER opcional via ESP32
-> DecisionReceipt
-> logs rotados
-> facade_data para Pollen
```

La decision clave es que casi todo el sistema es determinista. Rhizome no espera
que el LLM "se porte bien" para ser seguro. El steward evalua humedad, deposito,
cooldown, presupuesto diario de riegos y estado del enlace con ESP32 antes de
plantear cualquier accion. Si no entiende una lectura, aplaza. Si el deposito
esta bajo, alerta. Si no hay permiso explicito, no manda agua. Si manda agua, lo
hace siempre a traves del ESP32.

Gemma 4 entra donde aporta valor sin comprometer seguridad: como inteligencia
local de explicacion contractual. Con `--gemma-rationale-url`, Rhizome puede
llamar al adapter compatible con Ollama/llama.cpp y pedir a **Gemma 4 E2B** que
mejore el `rationale_short` de una decision ya tomada. No puede cambiar la
accion, no puede autorizar agua y no puede inventar hechos. Esto hace que Gemma
4 sea visible y util para el usuario sin convertirlo en una autoridad fisica.

La configuracion tambien refleja esa filosofia. El modo por defecto es prudente:
`WATER` queda bloqueado salvo que se pase `--execute-water`. La duracion maxima
esta limitada a `30s`, el cooldown evita riegos repetidos por ruido de sensor y
existe un limite de eventos autonomos diarios. Para sensores de humedad aun no
calibrados a porcentaje, el steward acepta umbrales raw explicitos, documentados
y visibles en el comando. Nada queda escondido.

En Jetson, la capa operativa queda empaquetada en wrappers reproducibles:

```bash
./run_steward_once.sh
ESP32_MODE=serial ESP32_PORT=/dev/ttyACM0 ./run_steward_once.sh
ESP32_MODE=serial ESP32_PORT=/dev/ttyACM0 EXECUTE_WATER=1 WATER_SECONDS=8 ./run_steward_once.sh
```

Para operacion continua:

```bash
ESP32_MODE=serial ESP32_PORT=/dev/ttyACM0 ./start_steward_loop.sh
```

El steward decide cada 15 minutos por defecto y mantiene heartbeat entre
decisiones. Ademas escribe estado para que Pollen pueda leerlo mediante la
fachada existente. Eso permite que el movil vea snapshots, recibos y
explicaciones sin acoplarse al mecanismo interno de Rhizome.

La persistencia se diseno para sobrevivir semanas o meses sin reventar la
microSD. Por defecto escribe en:

```text
~/.local/share/sprout/rhizome_steward/
├── telemetry_samples/YYYY-MM-DD.jsonl
├── decision_receipts/YYYY-MM-DD.jsonl
├── shadow_skeptic/YYYY-MM-DD.jsonl
├── current_snapshot.json
├── last_decision_receipt.json
└── facade_data/
```

El store aplica retencion por dias y presupuesto total de bytes. No sustituye al
SSD, que sigue siendo recomendable para operacion larga y modelos, pero evita la
trampa clasica de los pilotos edge: dejar logs creciendo indefinidamente hasta
romper el sistema.

La integracion con **llama.cpp** es estrategica. Sprout ha mantenido un adapter
comun compatible con el estilo Ollama para poder mover inferencia entre
desarrollo local, Ollama provisional y `llama-server` en Jetson. En las pruebas
previas, el perfil `safe-cpu` conserva contrato y por eso sigue siendo el perfil
demo. El perfil GPU experimental demostro que Gemma 4 E2B Q4_K_S puede cargar
en Jetson con una configuracion especifica, pero tambien revelo regresiones
contractuales en casos concretos. La decision fue correcta: rendimiento si, pero
no a costa de estabilidad semantica.

La capa mas interesante para futuro es `ShadowSkeptic`. Implementa una version
experimental de doble agente, pero no afecta al resultado. Revisa cada decision,
registra si habria objetado, que preocupacion detecta y que accion recomendaria,
siempre con `affects_decision=false`. Esto permite recoger datos reales antes de
decidir si merece evolucionar hacia un segundo agente LLM. Es una forma madura
de innovar: abrir la puerta sin meter riesgo en el actuador.

Lo que hace fuerte esta implementacion no es una unica pieza brillante, sino la
composicion de capas:

- ESP32 como veto fisico independiente.
- Rhizome Steward como bucle autonomo minimo.
- Gates deterministas como nucleo de seguridad.
- Gemma 4 como explicacion local y auditabilidad.
- llama.cpp como camino de paridad con Jetson.
- DecisionReceipt como memoria verificable.
- Pollen como interfaz humana de visita.
- Logs rotados como operacion real, no demo fragil.
- ShadowSkeptic como investigacion segura de doble agente.

## Mejoras futuras

La siguiente evolucion natural es convertir el steward en servicio supervisado
con `systemd`, anadir calibracion formal de humedad, usar feedback real del
caudalimetro en `execution_details`, instalar el SSD para modelo y retencion
larga, y conectar `WeatherDigest` para aplazar riego si hay lluvia probable.

En Gemma 4, las mejoras mas prometedoras son: resumen inteligente de "que paso
desde mi ausencia", explicaciones multilingues para Pollen, structured output
mas estricto con llama.cpp, estabilizacion del perfil GPU y un `ShadowSkeptic`
LLM que siga sin vetar al principio, pero aprenda a detectar inconsistencias.

La ambicion de Rhizome Steward v0 es pequena en superficie y grande en
arquitectura: riega poco, bloquea bien, explica corto y deja recibo. Eso es
exactamente lo que un nodo edge deberia hacer cuando el agua, el hardware y la
confianza importan.
