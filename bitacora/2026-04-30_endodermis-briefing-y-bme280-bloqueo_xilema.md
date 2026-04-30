# Dia 15 - Briefing Endodermis y bloqueo fisico BME280

## Emisor, receptor y tema

- Emisor: Xilema
- Receptor: Cambium, Bea, Endodermis, Meristem
- Tema: estado dia 15 tras intento BME280, PR #60 y preparacion de Endodermis

## Estado

Hoy se avanzo en tres frentes:

1. El BME280 se intento llevar de pre-cableado a prueba fisica real.
2. Se abrio PR #60 con el bundle minimo Rhizome -> Meristem.
3. Se preparo el briefing tecnico para que Endodermis pueda arrancar Jetson sin invadir firmware ni reglas duras.

## BME280

El firmware y el host harness ya estaban listos, asi que la prueba de hoy atacaba la parte fisica:

- `I2C_SCAN`
- `BME280_PROBE`
- `BME280_READ`
- escenario `bme280_connected_smoke`

Resultado observado:

- `I2C_SCAN count=0 addrs=NONE`
- `BME280_PROBE status=NOT_FOUND error=ESP_ERR_NOT_FOUND sensor_rslt=-4`
- no hubo ningun hit intermitente en `0x76` ni `0x77`
- despues de rehacer soldaduras, el LED verde del modulo dejo de encender

Conclusion:

No trato esto como fallo del firmware. La evidencia apunta a modulo/cabecera/soldadura. Parar aqui es la decision sana: no seguir quemando tiempo con un sensor que ya no da una senal electrica basica.

Decision:

- #56 queda abierto, pero bloqueado por hardware.
- Reintento solo con BME280 presoldado fiable, idealmente STEMMA/Qwiic o breakout con pines ya soldados.
- Cuando llegue, repetir directamente `bme280_connected_smoke`.

## PR #60

PR abierto:

- https://github.com/zigiella/sprout/pull/60

Contenido:

- bundle minimo Rhizome -> Meristem en `code/meristem/examples/rhizome_minimal_handoff/`
- `RhizomeSnapshot` de deposito bajo
- `DecisionReceipt` con `TANK_LOW`
- `PolicyPacket` seed seguro
- RA04 como `PolicyDelta` inseguro que intenta bajar `rules.tank_minimum_pct` a 15
- test que valida rechazo `violates_safety_rule`

Verificacion:

- `python -m pytest code\meristem\tests\test_rhizome_minimal_handoff_examples.py -v` -> 3 passed
- `python -m pytest code\meristem\tests -v` -> 57 passed, 2 skipped

Nota importante:

He usado el shape actual de Meristem (`/ingest` por envelope + `PolicyDelta`) porque `FieldVisit` / `SyncBundle` estan documentados, pero no implementados aun como schemas Pydantic compartidos. No he inventado un bundle teorico que luego nadie pueda ejecutar.

## Endodermis

He creado:

- `docs/52_endodermis_jetson_bringup_brief.md`

El doc fija:

- fronteras de autoridad,
- estado del ESP32,
- estado del BME280,
- stack Gemma 4 E2B + `llama.cpp`,
- comando oficial revalidado contra Jetson AI Lab el 2026-04-30,
- smoke cases obligatorios de Rhizome v0.5,
- plantilla de resultados,
- preguntas que hay que cerrar antes de ejecutar en Jetson.

Punto de control:

Endodermis puede avanzar en Jetson, Docker, `llama.cpp`, metricas y bateria Rhizome. No cambia firmware, reglas duras ni limites fisicos sin visto bueno de Xilema.

## Hallazgos

- El flujo BME280 esta bien planteado como software, pero el primer hardware concreto no es fiable.
- El proyecto necesita distinguir con frialdad entre "bug" y "cobre que no conduce". Hoy era lo segundo.
- El handoff Rhizome -> Meristem ya tiene un minimo ejecutable y testeado.
- Para Endodermis conviene una rampa muy acotada: primero caracterizar Jetson, despues cargar E2B, despues repetir v0.5. No optimizar antes de medir.

## Descartes

- No sigo con este BME280 concreto hasta tener una senal electrica basica.
- No paso a sensores criticos ni bomba con esta incertidumbre fisica.
- No cambio runtime a Ollama.
- No pruebo E4B antes de tener E2B estable en Jetson.

## Siguientes pasos

1. Esperar review/merge de PR #60.
2. Pasar a Endodermis el briefing y usarlo como guion de la conversacion tecnica.
3. Reintentar #56 cuando haya BME280 presoldado.
4. Si Jetson queda listo, ejecutar baseline de placa y luego Gemma 4 E2B con `llama.cpp`.
5. Cuando E2B responda, re-ejecutar bateria Rhizome v0.5 sin retocar prompt salvo fallo nuevo.

## Sensacion de Xilema

Hoy ha sido un dia un poco de taller real: cables, soldadura pobre, sensor que desaparece, y aun asi avance. Me parece sano que el proyecto aguante esto sin dramatizar. Sprout esta dejando de ser una coleccion de ideas bonitas y empieza a comportarse como un sistema con bordes: lo que falla fisicamente se marca como fisico, lo que es contrato se testea, y lo que es inferencia se mide.

Si repensara algo, seria esto: cada nuevo hardware deberia entrar con una mini-rutina de admision antes de tocar codigo. Foto, pinout, continuidad si hay multimetro, alimentacion visible, scan minimo, y solo entonces PR. Es menos romantico, pero nos ahorra fantasmas.
