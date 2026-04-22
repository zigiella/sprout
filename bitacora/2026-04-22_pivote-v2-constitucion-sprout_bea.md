# Pivote v2 — constitucion de Sprout

Fecha: 2026-04-22
Autora: Bea
Dia 8 de 30

## Que he decidido

Cerramos pivote. Reordeno la arquitectura de Sprout antes de que el proyecto se ensanche mas de lo que podemos sostener en las dos semanas y media que quedan.

Sprout se define a partir de hoy asi:

> **Sprout es una arquitectura local-first para decisiones de riego en parcelas aisladas, con agua limitada, visitas humanas intermitentes y conectividad incierta.**

## Por que cambio

La version 1 tenia buenas piezas pero el MVP se habia ensanchado demasiado:

- demasiada dependencia de una red de tres niveles completa en la demo
- camara fija en Rhizome sin justificacion de valor
- Meristem demasiado complejo para el tiempo disponible, sin hardware ni presupuesto claros
- Pollen ambiguo entre "mula de datos", "chat" y "mini-Meristem"

Eso nos dejaba con mas arquitectura que demo. El proyecto no estaba pidiendo otro nodo; estaba pidiendo que los que ya hay queden dentro de un marco defendible.

Y ademas, el episodio del dia 7 con Floema — la migracion urgente de MediaPipe a LiteRT-LM por incompatibilidad con Android 16 — me recordo que veniamos arrastrando asunciones no verificadas. Antes de seguir codeando sobre cimientos que no hemos pisado, reordeno.

## La nueva constitucion — resumen

Ocho documentos entran en `docs/` hoy como v2:

- `docs/01_architecture.md` — arquitectura v2
- `docs/10_rhizome_spec.md` — Rhizome como corazon del sistema
- `docs/11_pollen_spec.md` — Pollen imprescindible, cuatro responsabilidades
- `docs/12_meristem_spec.md` — Meristem cerebro lento, fuera de demo
- `docs/13_esp32_spec.md` — ESP32 coprocesador de seguridad
- `docs/20_data_contracts.md` — contratos de datos entre nodos
- `docs/30_safety_rules.md` — reglas no negociables
- `docs/40_pitch_video.md` — pitch y video

Las piezas clave del pivote:

### Rhizome sigue siendo el corazon
Lee estado local, decide dentro de un sobre seguro, ejecuta o bloquea a traves del ESP32. Gemma 4 E2B en Jetson Orin Nano Super, con intervencion solo en casos de arbitraje o explicacion — no en el loop para todo.

### Pollen pasa a ser imprescindible
Compilador de intencion humana, auditor itinerante, federador de parcelas, interfaz conversacional de Rhizome. El movil no solo trae datos. Trae criterio. Gemma 4 E4B en Pixel 10 Pro via LiteRT-LM — sujeto a validacion final contra documentacion oficial para Android 16 + 16KB page size.

### Meristem baja de rango operativo
Cerebro lento. Consolida bundles de varias visitas, emite `PolicyPacket`. **No esta en la demo.** Queda especificado como trabajo en curso post-hackathon, con adapter Ollama-compatible ya construido disponible como infraestructura preparada para v2.

### ESP32 sube de rango
No es placa de reles. Es coprocesador de seguridad con firmware propio: dueno de sensores criticos, dueno de actuadores, arbitro de seguridad fisica, guardian del failsafe. Si Jetson se cae, el sistema no se vuelve peligroso.

## Que sale de la ruta critica

- camara fija en Rhizome
- video continuo
- BLE / WiFi Direct sofisticado
- dashboards ricos
- fine-tuning
- multi-Rhizome fisico real
- Meristem en la demo
- dependencia del cloud para que la demo funcione

## Que entra si o si

Entran si o si las ocho escenas del video (`docs/40_pitch_video.md`):

1. Rhizome toma una decision offline.
2. ESP32 acepta o bloquea con reglas duras.
3. Pollen habla con Rhizome y explica una decision pasada.
4. La persona dicta una nueva mision en lenguaje natural.
5. Pollen la compila a politica / patch estructurado.
6. Pollen trae contexto util de otra parcela o de meteo local.
7. Rhizome reevalua y actua.
8. Un comando o contexto caducado se rechaza.

## Que pasa con el trabajo ya abierto

- **PR #32** (Xilema, analisis benchmarks Rhizome) → mergeable tal cual. Sigue siendo instrumentacion valida.
- **PR #34** (Xilema, benchmark multimodal Rhizome) → mergeable. Multimodal queda como infra latente fuera de ruta critica.
- **PR #50** (Meristem, adapter Ollama-compatible) → **mergeable con cartela de "infraestructura preparada para Sprout v2, no en demo del hackathon"**. 4083 lineas de trabajo limpio y 88 tests verdes que queda disponible para cuando retomemos Meristem.
- **Issue #42** → cerrada. No aplica.
- **Issues #43, #44, #45, #47** → archivadas. Dependen de Meristem en demo.
- **Propuesta "Backend cloud propio con Ollama gestionado"** → archivada antes de nacer. Meristem fuera de demo hace que el angulo pierda consumidor inmediato.
- **Trabajo de fine-tuning en `code/finetune/`** → preservado, documentado como "no ejercitado en demo, plan post-hackathon".

Nada se tira. Mucho trabajo cambia de rol — de "pieza de demo" a "infraestructura v2".

## Reparto inmediato del trabajo

- **Xilema / Rhizome:** firmware ESP32 (nuevo y bloqueante), estado materializado + `DecisionReceipt`, API local para Pollen.
- **Floema / Pollen:** **verificacion obligatoria de documentacion oficial LiteRT-LM + Gemma 4 + Android 16 + Pixel 10 Pro antes de cualquier otro trabajo**, luego UX minima + compilador de intencion humana + conversacion con Rhizome.
- **Meristem:** cierre de trazabilidad del trabajo de #50 en writeup. Disponibilidad para apoyar a Xilema con API Rhizome y a Estoma con verificacion de docs segun convenga.
- **Corola / video:** guion v1.0 + shot list v1.0 segun `docs/40_pitch_video.md`. Coordinacion con Floema para plano de compilacion de mision.
- **Estoma + Peri:** archivan hilo de "Ollama propio gestionado". Nuevos hilos: Peri investiga LiteRT-LM + Gemma 4 E4B + Android 16 + Pixel 10 Pro con docs oficiales citadas (ampliando el trabajo que ya dejo en `research/experiments/2026-04-21_litertlm-deprecated-mediapipe_peri.md`). Estoma investiga referentes publicos de demos Gemma 4 + Jetson + movil.

## Proceso preventivo que instauramos

El episodio del dia 7 (migracion LiteRT-LM sin leer docs oficiales antes) no se va a repetir. A partir de hoy:

> **Antes de migrar, adoptar o pivotar cualquier libreria, framework o dependencia troncal del proyecto, se verifica contra la documentacion oficial correspondiente, y se cita URL + version + fecha de lectura en el commit o PR que adopta el cambio.**

Este proceso se aplica primero a la propia verificacion de Pollen (Floema + Peri) como caso fundacional.

## Tesis que defiendo ante el jurado

No defendemos un riego automatizado.

Defendemos esto:

> **Cuando el campo, la persona y la red no coinciden en el tiempo, Sprout reduce la latencia de decision sin renunciar a soberania local, seguridad fisica y explicabilidad.**

## Frase de producto

> **Rhizome mantiene viva la parcela cuando nadie esta. Pollen convierte la visita en inteligencia util.**

## Nota personal

Girar el proyecto el dia 8 cuesta infinitamente menos que girarlo el dia 20. El sistema ya ha demostrado dos veces esta semana que absorbe cambios arquitecturales sin reescribirse — las bitacoras del dia 6 (tres reenfoques de Pollen, Meristem y narrativa) y del dia 7 (pivote MediaPipe → LiteRT-LM) lo dejan por escrito. Hoy le toca al proyecto mismo.

El patron es consistente: **el precio del cambio no se paga en el momento del cambio; se paga en el momento en que se escribe la abstraccion**. Lo hemos escrito ocho veces a lo largo de esta semana en los documentos que entran hoy a `docs/`. Ahora toca ejecutar.

— Bea
