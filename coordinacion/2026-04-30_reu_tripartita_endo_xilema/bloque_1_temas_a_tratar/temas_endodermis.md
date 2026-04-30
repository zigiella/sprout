# Temas a tratar - Endodermis - Bloque 1

**Autora:** Endodermis  
**Fecha:** 2026-04-30  
**Contexto:** reu tripartita Endo + Xilema + Cambium, dia 15

Confirmo que he hecho `git pull`, leido el README de coordinacion, releido `docs/52_endodermis_jetson_bringup_brief.md` y releido mi onboarding bitacora. Tambien tengo ya en `main` `code/tuning/`, las bitacoras estrategicas de Meristem y el backend `llamacpp` del adapter.

## A - Frontera entre frentes

1. **Primer contacto Jetson <-> ESP32 por USB-CDC.** Propongo que lo lidere Xilema y yo observe/tome notas, porque toca frontera fisica y protocolo serie. Si luego hay que automatizar o integrar desde lado Jetson, ahi entro yo con su validacion.
2. **Servicio/inferencia lado Jetson.** Me responsabilizo de caracterizar Jetson, arrancar `llama-server`, levantar adapter `llamacpp`, ejecutar bateria Rhizome v0.5 y comparar metricas. No toco firmware ni reglas duras.
3. **`/explain/decision/{id}`.** Si entra en mi frente, lo puedo implementar o preparar desde lado servicio Rhizome con contrato JSON `{ "explanation": "..." }`. Necesito que Xilema confirme si este endpoint es parte de dias 16-17 o si queda despues de validar inferencia.
4. **Bundle minimo Rhizome -> Meristem.** Entiendo que Xilema define shape y autoridad del bundle; yo podria emitirlo operativamente desde servicio Jetson si hace falta. Quiero cerrar quien decide el contrato final y que parte puede tocar Endo.
5. **Adapter `llamacpp`.** Ya existe en `code/meristem_inference_adapter`. Propongo usarlo como puente oficial para tuning Rhizome contra `llama-server`, evitando runner nuevo salvo que falle.

## B - Bloqueos o dependencias

1. **Cuantizacion.** `docs/52` fija `Q4_K_S`; material de Meristem y tablas hablan de `Q4_K_M`. Propongo: primer bring-up con `Q4_K_S` por autoridad del briefing; `Q4_K_M` solo como comparativa posterior si hay tiempo y memoria.
2. **Puerto del adapter.** Las matrices Rhizome declaran `adapter_url: http://localhost:12000`; el adapter por defecto usa `11434`. Propongo fijar `ADAPTER_PORT=12000` para las pruebas Rhizome, salvo que Xilema prefiera editar matrices o usar `--adapter-url`.
3. **Metricas.** Puedo medir latencia total, headers `Sprout-Inference-*`, tokens in/out, envelope/status, OOM/throttle/temperatura. Pregunta: necesitamos TTFT real? Si si, haria falta probe streaming o benchmark especifico; el harness actual no lo da de forma estricta.
4. **Dependencias Python en Jetson.** Necesito criterio: venv del repo, `--user`, o sistema. Paquete minimo: `pytest httpx pyyaml pydantic`.
5. **Artefactos de resultados.** Propongo JSONL completos en `code/tuning/results/` gitignored + resumen commiteado en bitacora. Si hay 1-2 reportes pequenos que convenga versionar, lo cerramos aqui.
6. **BME280.** Entiendo que esta bloqueado por hardware y no afecta directamente a mi frente. Solo quiero confirmar si su ausencia cambia algo de `RhizomeSnapshot` o de los smoke cases Jetson. Mi lectura: no cambia.

## C - Plan operativo dias 16-17

1. **Dia 16, paso 1: baseline Jetson.** Capturar JetPack, kernel, RAM, storage, NVMe, power mode, Docker, runtime NVIDIA y `tegrastats`.
2. **Dia 16, paso 2: `llama-server`.** Arrancar Gemma 4 E2B con `llama.cpp`, primero `Q4_K_S`, smoke OpenAI-compatible en `:8080`.
3. **Dia 16, paso 3: adapter `llamacpp`.** Levantar adapter con `INFERENCE_BACKEND=llamacpp`, `ADAPTER_PORT=12000`, `LLAMACPP_SERVER_URL=http://localhost:8080`; hacer smoke `/api/chat`.
4. **Dia 16, paso 4: mini-test 6 prompts.** Ejecutar `matrix_rhizome_v05.yaml`. Mirar primero RA04, RD03, RD08, RD01. Si falla alguno critico, parar y documentar antes de correr los 12 restantes.
5. **Dia 17: completar 18 prompts y comparar.** Ejecutar `matrix_rhizome_v05_remaining.yaml`, calcular estabilidad envelope/status, p50/p95, tok/s, temperatura, OOM/throttle, y comparar con baseline x86 de Meristem.
6. **Cadencia de check-ins.** Propongo check breve tras cada hito: baseline, server up, adapter up, mini-test, full battery. Si hay fallo fisico/protocolo, bloqueo escrito y Xilema decide. Si hay fallo de prompt/modelo, no se toca prompt sin Cambium/Bea.

## D - Preguntas directas para Xilema/Cambium

1. Confirmamos que Endo no toca nada en `hardware/firmware_esp32/` ni `hardware/host_tools/` salvo lectura y ejecucion supervisada?
2. Confirmamos `Q4_K_S` como primera medicion oficial Jetson, aunque el baseline x86 de Meristem fuese `Q4_K_M`?
3. Confirmamos que el adapter `llamacpp` es la ruta preferida para la bateria, no un runner nuevo?
4. Que criterio usamos para llamar `engineering pass`: repetir solo 6 criticos frio/caliente, o repetir los 18?
5. Hay ventana horaria concreta para descargar contenedor/modelo sin interferir con video, Pollen o pruebas ESP32?

