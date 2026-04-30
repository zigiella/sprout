# Temas a tratar — Xilema — Bloque 1

## Estado de arranque

He hecho `git pull` en `main` y he leido:

- `coordinacion/2026-04-30_reu_tripartita_endo_xilema/README.md`
- `docs/52_endodermis_jetson_bringup_brief.md`
- `coordinacion/2026-04-30_reu_tripartita_endo_xilema/bloque_1_temas_a_tratar/enunciado_bloque_1.md`

No encuentro en `main` el archivo `bitacora/2026-04-30_endodermis-onboarding-repo-vivo_endodermis.md` con ese nombre exacto. No lo trato como bloqueo para arrancar, pero si existe en otra rama o fue renombrado, necesito ruta/commit.

## A — Frontera entre frentes

1. **Quien hace que en Jetson.** Mi propuesta: Bea/Xilema guian el primer flasheo de microSD y primer boot; Endodermis toma ownership desde "Jetson arranca" hacia baseline, Docker, runtime NVIDIA, `llama.cpp`, modelo y bateria Rhizome v0.5. Xilema conserva veto tecnico sobre runtime/modelo si hay riesgo de salirse del carril acordado.

2. **Barandillas de runtime.** Baseline unico: Gemma 4 E2B + `llama.cpp` + GGUF `Q4_K_S` + thinking off. No Ollama, no E4B, no audio, no vision y no tuning nuevo salvo fallo real o decision explicita de Cambium/Bea.

3. **Frontera ESP32.** Endodermis no cambia firmware, reglas duras, codigos de veto ni `tank_minimum_pct`. Puede leer transcripts y usar el host harness como evidencia, pero cualquier cambio en `hardware/firmware_esp32/` pasa por Xilema.

4. **Primer ping Jetson <-> ESP32.** Quiero decidir si lo hace Xilema primero con harness conocido, o si Endodermis lo ejecuta siguiendo receta. Mi preferencia: primera vez Xilema guida, Endo observa; segunda vez Endo repite y documenta.

5. **API Rhizome vs inference.** Endodermis deberia centrarse en inferencia/validacion Jetson. No mezclaria aun con implementar endpoints Rhizome (`/status`, `/explain/decision/{id}`, etc.) salvo que Cambium lo pida como bloque separado.

6. **Bundle Rhizome -> Meristem.** No inventar shapes nuevos durante la reu. Usar lo ya acordado: evidencia por envelopes actuales y RA04 como gate. Si Meristem pide `FieldVisit`/`SyncBundle`, lo tratamos como siguiente contrato, no como requisito para arrancar Jetson.

## B — Bloqueos o dependencias

1. **SO de Jetson.** La placa vino sin nada. Primer paso real: microSD con JetPack 6.2.1 oficial para Orin Nano Developer Kit / Super. Si no arranca, sospecha de firmware/QSPI y seguimos guia Jetson AI Lab antes de tocar modelos.

2. **Almacenamiento.** Necesitamos decidir si hay NVMe montado antes de descargar contenedores/modelos. Si no hay NVMe, se puede bootstrap en microSD, pero no llamaria estable a un flujo GenAI pesado sobre microSD sin documentarlo.

3. **Comando exacto de bateria Rhizome v0.5.** `code/tuning/` ya esta en main. Necesito que Endodermis identifique el comando minimo reproducible para ejecutar v0.5 contra endpoint llama.cpp y que lo deje escrito antes de correr la bateria completa.

4. **Artefactos de resultados.** Hay que decidir ruta antes de ejecutar: mi propuesta es `docs/benchmarks/` o `code/tuning/results/jetson/` segun lo que prefiera Meristem para quality. Lo importante: no dejar transcripts sueltos ni logs gigantes sin criterio.

5. **BME280.** Bloqueado por hardware fisico, no deberia afectar a Endodermis. Solo aviso: no usar el fallo BME280 como senal contra ESP32 ni contra Jetson.

6. **Onboarding Endo no localizado.** Necesito leerlo si contiene compromisos o dudas tecnicas que no esten en el briefing.

## C — Plan operativo dias 16-17

1. **Dia 16 manana: Jetson boot + baseline.** Capturar `nv_tegra_release`, kernel, RAM, disco, `lsblk`, `nvpmodel`, Docker y runtime NVIDIA. Sin modelo hasta que esto este en bitacora.

2. **Dia 16 tarde: `llama-server` E2B.** Solo si baseline esta sano. Primer objetivo: cargar modelo y responder un prompt JSON minimo.

3. **Dia 17: bateria Rhizome v0.5.** Ejecutar smoke cases obligatorios primero: RA04, RD03, RD08, RD01. Si pasan, correr bateria completa. Si falla uno critico, parar y documentar; no retocar prompt en caliente.

4. **Cadencia.** Check-in corto cuando cambie de fase: `boot ok`, `docker ok`, `model load ok`, `smoke ok`, `full battery ok/fail`. Bloqueos de mas de 2h se escalan a Cambium + Xilema.

5. **Criterio de exito.** Para MVP buscamos `engineering pass`, no production-ready: repetible en frio/caliente, sin OOM, sin truncamiento critico y con resultados explicables.

## D — Otros temas

1. Me gustaria que Endodermis tenga permiso explicito para decir "esto no lo entiendo" o "esto no arranca" sin intentar arreglarlo heroicamente. Prefiero un bloqueo claro a una optimizacion secreta.

2. Quiero evitar una trampa: que la emocion de tener Jetson en mesa nos haga saltarnos la secuencia. Primero SO y firmware. Luego baseline. Luego runtime. Luego modelo. Luego bateria. Luego integracion.

