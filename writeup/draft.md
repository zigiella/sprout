# Sprout — writeup (draft en curso)

> **Autores:** Cambium + Bea. Corola no toca este documento (scope: video).
> Issue: #11.
> Estado: **esqueleto navegable**, contenido por escribir en sesiones Cambium ↔ Bea los dias 6-25.

---

## 0. Titulo + subtitulo — ~30 palabras

<!--
Objetivo: titulo pegadizo + subtitulo que resume el proyecto en una linea.

Candidatos de titulo (a elegir con Bea):
- Sprout: reducing absence in remote farming
- Sprout: water decisions, offline, on time
- Sprout: a farm network that doesn't need the internet

Candidatos de subtitulo:
- "El agua no se pierde solo por escasez. Se pierde porque la decision llega tarde."
- "Un diseño de red agricola que convierte la ruta del agricultor en canal de inteligencia."

Decision: dia 20 (tras video rodado, sabremos mejor cual pega).
-->

## 1. Problema — ~200 palabras

Una parcela de almendros a cuarenta kilometros del pueblo mas cercano. El
agricultor la visita una vez por semana, a veces menos. Entre visita y
visita, el suelo decide solo: o recibe agua a tiempo, o no la recibe.
Cuando el agricultor vuelve, el problema ya ha pasado — solo queda medir
cuanto se perdio.

La escena no es anecdota. La ITU mide en 2025 una brecha de 27 puntos
entre cobertura movil urbana (85%) y rural (58%) en paises desarrollados;
en Australia, el 90% del territorio vive sin conectividad fiable. El
Banco de España atribuye entre un 20% y un 30% de las perdidas de trigo
de la campaña 2022-23 al retraso en decisiones agronomicas, no a escasez
absoluta de recurso. IRRIFRAME sirve a 40.000 explotaciones en
Emilia-Romaña desde un servidor central — un modelo que funciona donde
hay red y se degrada donde no la hay.

El denominador comun no es la falta de agua. Es el **lag** entre lo que
pasa en la parcela y la decision que deberia corregirlo. Cuando la red
falla o el agricultor no esta, ese lag se mide en dias. Cerrar el lag
exige llevar la decision donde hay agua — no al reves.

<!-- Fuentes: research/narrative_sources.md (ITU 2025, BdE 2025, IRRIFRAME, Australia Regional Tech Hub). -->

## 2. Solucion — ~300 palabras

Sprout resuelve el lag distribuyendo la decision entre nodos con
**jurisdicciones distintas**. No es una red cooperativa generica; es
un sistema donde cada nodo responde a una pregunta concreta, en una
escala de tiempo concreta, y con autoridad acotada.

**Rhizome** es el nodo autonomo de parcela. Vive junto a los sensores,
lee el estado local y decide si riega, difiere, salta o bloquea —
dentro de un sobre seguro impuesto por un **ESP32 acoplado que ejecuta
firmware propio**. Usa **Gemma 4 E2B** sobre Jetson Orin Nano Super
solo para arbitraje y explicacion, no para toda decision. La mayoria
de pasos son deterministas; Gemma entra cuando hay senales
contradictorias o mision humana nueva. Si la red cae, Rhizome sigue
decidiendo sola. Su jurisdiccion son los minutos.

**El ESP32 es coprocesador de seguridad**, no una placa de reles. Es
dueno de los sensores criticos (humedad, nivel de deposito,
caudalimetro) y de los actuadores (bomba, valvulas), y el unico que
puede autorizar ejecucion fisica. Ninguna orden de riego pasa sin su
visto bueno: tiempo maximo por evento, deposito minimo, verificacion
de caudal, heartbeat con Jetson. **Si Jetson se cae, el sistema no se
vuelve peligroso.** La IA propone; el agua la gobierna una capa fisica
prudente.

**Pollen** es el nodo itinerante. No es un sincronizador de datos: es
el pedazo del sistema que convierte cada visita humana en tres cosas
distintas. Compila intencion humana ("vuelvo en 72 horas, prioriza
parcela A, maximo 900 ml") a `MissionPatch` estructurado con
caducidad; audita decisiones pasadas de Rhizome traduciendo `receipts`
a lenguaje natural; y federa parcelas transportando `WeatherDigest` o
contexto util entre nodos sin red directa. Gemma 4 E4B en Pixel 10 Pro
via LiteRT-LM. Su jurisdiccion es la visita, con TTL corto.

**Meristem** queda especificado como cerebro lento del sistema —
consolida bundles de visitas, evalua desempeno de politicas, emite
politicas mas duraderas. **No esta en la demo del hackathon**; el
sistema se defiende con Rhizome + Pollen + ESP32. Meristem es trabajo
en curso con adapter Ollama-compatible ya construido (disponible como
infraestructura de la version 2 del proyecto), explicitado como tal
ante el jurado.

**Rhizome mantiene viva la parcela cuando nadie esta. Pollen convierte
la visita en inteligencia util.** Esa es la tesis del sistema: cuando
el campo, la persona y la red no coinciden en el tiempo, la decision
correcta la toma el nodo que si esta ahi — y la visita humana, en vez
de ser interrupcion, entra al sistema como evento de primera clase con
criterio, caducidad y trazabilidad.

<!-- Fuentes: bitacora/2026-04-22_pivote-v2-constitucion-sprout_bea.md
     (constitucion v2 de Sprout),
     docs/01_architecture.md, docs/10_rhizome_spec.md,
     docs/11_pollen_spec.md, docs/12_meristem_spec.md,
     docs/13_esp32_spec.md. -->

## 3. Arquitectura — ~400-450 palabras

Sprout reparte la decision entre **tres nodos con jurisdicciones distintas y un coprocesador fisico que veta**. Rhizome decide en escala de minutos sobre la parcela; Pollen actua en escala de visita con caducidad corta sobre el movil del agricultor; Meristem opera en escala de dias sobre el ordenador domestico. El **ESP32**, separado del computo de IA, es dueno de los sensores criticos y de los actuadores: nada toca el agua sin pasar por sus reglas. Si Jetson cae, el sistema no se vuelve peligroso.

**Stack del MVP.** Rhizome corre **Gemma 4 E2B** via `llama.cpp` sobre **Jetson Orin Nano Super**, con un **ESP32-S3** acoplado por USB-CDC nativo ejecutando firmware ESP-IDF propio. Pollen corre **Gemma 4 E4B** via LiteRT-LM sobre movil Android. Cada nodo de IA habla a un *adapter Ollama-compatible* comun que emite headers `Sprout-Inference-*` uniformes — pieza de infraestructura que tambien habilita ejecutar Meristem como consolidador local en el ordenador del agricultor (E4B via `llama.cpp`), reutilizando los mismos contratos de prompt, schema y receipt aunque cada dispositivo use un formato de runtime distinto.

**Cinco reglas no negociables**, implementadas y ejercitadas contra el limite fisico de seguridad en placa real (DRY_RUN):

| Regla | Motivo legible si veta |
|-------|------------------------|
| Jetson heartbeat perdido | `JETSON_HEARTBEAT_LOST` |
| Deposito por debajo del minimo | `TANK_LOW` |
| Duracion del evento fuera de rango | `EVENT_DURATION_OUT_OF_RANGE` |
| Sin caudal tras abrir agua | `NO_FLOW_DETECTED` |
| Alerta latched activa | `ALERT_LATCHED` |

Cada veto emite motivo legible que se almacena en el `DecisionReceipt` y aparece en pantalla. Una sexta regla, `SAFETY_DOWNGRADE`, no rechaza una orden valida: la modula al sobre fisico mas seguro. El receipt registra ambos, `candidate_action` y `final_action`.

**Contratos versionados del MVP.** Diez objetos JSON con autoridad explicita por contrato y caducidad obligatoria: `RhizomeSnapshot`, `DecisionReceipt`, `AlertEvent` los emite Rhizome; `MissionPatch`, `ValidationStamp`, `WeatherDigest`, `VisitAmendment`, `FieldVisit` los emite Pollen; `PolicyPacket` lo emite Meristem; `SyncBundle` lo transporta cualquier nodo (normalmente Pollen). Rhizome acepta cada objeto solo si valida schema, no esta caducado, su autoridad es correcta, y no contradice una regla del ESP32. Toda inteligencia tiene jurisdiccion y fecha de caducidad; todo rechazo deja huella legible — ningun objeto se pierde en silencio.

**Transferencia de ingenieria entre nodos.** Antes de atacar hardware final, ajustamos configuracion, prompts y tests de contrato en nodos simulados sobre `llama.cpp` local. El aprendizaje no fue solo del modelo, sino del metodo: cada nuevo nodo heredo del anterior una bateria de restricciones, ejemplos negativos, formatos JSON, criterios de aceptacion y reglas de seguridad. El segundo system prompt entro a 94% de aciertos en su primera ejecucion frente al 50% del primero. Eso redujo iteracion y aumento estabilidad **sin fine-tuning**.

**Lo que el MVP demuestra y lo que la arquitectura reserva.** El MVP demuestra el bucle corto operativo: Rhizome decidiendo offline, ESP32 vetando o modulando la accion fisica, y Pollen llevando intencion humana de vida corta al campo. La arquitectura reserva la consolidacion a escala de dias en Meristem como cerebro lento domestico, ejercitable con la misma infraestructura.

<!-- Visuales obligatorios para version final:
- [ ] Diagrama 3 nodos + ESP32 (renderizado a PNG desde docs/01_architecture.md)
- [ ] Ciclo de vida de una politica / decision (referencia a docs/01_architecture.md §9)
-->

## 4. Demostracion — ~250 palabras

<!--
Lo que muestra el video + 1-2 screenshots.

Coordinar con Corola cuando tenga shot list cerrado (dia 12-15).
Preguntas para Corola:
- ¿Que escena abre el video?
- ¿Donde se ve el momento WOW de Pollen (transferencia cruzada)?
- ¿Que quedara en pantalla como "prueba de funcionamiento"?

Screenshots obligatorios:
- [ ] Splitscreen dashboard de Pollen (ya implementado, PR #20 y #30)
- [ ] Output de Meristem emitiendo un PolicyDelta
- [ ] Firmware ESP32 rechazando una regla que viola §30 (si Xilema entrega issue #4)
-->

## 5. Fine-tuning — ~150 palabras

<!--
- Dataset: sintetico + real (describir proporcion)
- Metodo: Unsloth LoRA sobre Gemma 4 E2B (el modelo edge)
- Benchmarks: p50 latencia, tok/s, acierto vs ground truth
- Insight: "el modelo pequeño fine-tuneado supera al grande generico en
  el dominio acotado". Dato a validar en dias 20-25.

Pendiente:
- Datos reales de finetune (ver code/finetune/)
- Resultados de PR #32 (Xilema) para el angulo comparativo
-->

## 6. Validacion local vs sombra — ~100 palabras

<!--
"Meristem ejecuta enteramente local con Gemma 4 E4B. En paralelo, un modo
sombra OPCIONAL compara el output con Gemma 31B remoto para auditar
acuerdo/desacuerdo. En produccion el sombra esta OFF; solo se usa durante
desarrollo para calibrar la calidad del modelo local."

Punto clave de honestidad: el proyecto NO depende de internet ni de modelos
remotos. El modo sombra es herramienta de validacion, no de ejecucion.

Datos a rellenar: % de acuerdo cuando el sombra estuvo encendido (dia 22-25).
-->

## 7. Impacto y escalado — ~100 palabras

<!--
- Coste por nodo (BOM): ~X€ Rhizome + Y€ Pollen (movil reutilizado) + Z€
  Meristem (portatil estandar)
- Escalabilidad: cada Meristem puede coordinar N Rhizomes (estimar N)
- Segmento: explotaciones pequeñas y medianas en zonas de baja poblacion
  (Aragon, Extremadura, Castilla-La Mancha, Andalucia interior, islas)
- Transferencia a otros dominios: acuicultura, invernaderos aislados,
  apicultura nomada
-->

## 8. Limitaciones — ~50 palabras

<!--
Ser honestos, no defensivos. Lista corta:
- Parcelas muy grandes (>10 zonas) no probadas
- Pollen depende de visita humana (~semanal) — si la ruta falta, Meristem
  no recibe consolidacion
- Safety rules §30 son para riego; otros dominios requeririan otras reglas
- No probado en produccion real, solo en demo controlado con datos sinteticos
  realistas
-->

## 9. Cierre — ~50 palabras

<!--
Frase final potente. Candidatos:

1. "La agricultura no se salvara con mas datos. Se salvara con decisiones
   a tiempo, tomadas donde hay agua."
2. "Sprout no sustituye al agricultor. Le deja mas tiempo para ser
   agricultor."
3. "Cuatro modelos Gemma pequeños, correctamente orquestados, pesan mas
   que uno grande aislado."

Decision: dia 25, tras video y demos.
-->

---

## Checklist del writeup (para tracking interno Cambium/Bea)

- [ ] Conseguir cifra opener del problema (dia 6-8)
- [ ] Generar diagrama arquitectura exportable a PNG (dia 10)
- [ ] Cerrar titulo + subtitulo con Bea (dia 20)
- [x] Sesion escritura conjunta seccion 1-2 (dia 6 o 7)
- [ ] Sesion escritura conjunta seccion 3-4 (dia 12-13)
- [ ] Sesion escritura conjunta seccion 5-7 (dia 18-20)
- [ ] Review final conjunto (dia 27-28)
- [ ] Recorte a 1500 palabras (dia 29)

## Proximas sesiones agendables

| Dia | Foco | Output esperado |
|-----|------|-----------------|
| 6 o 7 | Seccion 1 (problema) + datos opener | 200 palabras + fuentes citadas |
| 12-13 | Seccion 3 (arquitectura) | 350 palabras + diagrama escogido |
| 18-20 | Secciones 5-7 (fine-tuning, validacion, impacto) | Con datos reales de PR finetune |
| 27-28 | Review completo + recorte | Version entregable |
