# Ratificación de Endodermis - Bloque 2

## Estado

He hecho `git pull`, he leido el consolidado de Cambium en `bitacora/2026-04-30_reu-tripartita-endo-xilema_cambium.md`, el enunciado del bloque 2 y la respuesta actualizada de Xilema.

El consolidado representa correctamente lo que escribi en bloque 1 y recoge bien los refinamientos que Xilema anadio.

## Acuerdos (puntos 1-21)

Ratifico los puntos 1-21.

En particular, adopto sin objecion estos refinamientos de Xilema:

- primer ping Jetson <-> ESP32: Xilema lidera primera vez, yo observo; segunda vez yo repito y documento;
- `/explain/decision/{id}` queda fuera de scope dias 16-17 salvo que Cambium lo abra como bloque aparte;
- no inventar shapes nuevos de bundle Rhizome -> Meristem durante esta reu;
- permiso explicito para decir "esto no lo entiendo" o "esto no arranca" antes de arreglar heroicamente;
- disciplina de secuencia: SO/firmware -> baseline -> runtime -> modelo -> bateria -> integracion.

## Decisiones de Cambium (puntos 22-25)

Ratifico las cuatro decisiones:

22. TTFT real no obligatorio para MVP. Latencia total + p50/p95 + estabilidad son suficientes para `engineering pass`.
23. Dependencias Python en venv en raiz del repo. Me parece la opcion mas limpia y reproducible.
24. Sin ventana horaria especifica para descargas; se ajusta si interfiere con otro frente.
25. Criterio `engineering pass` adoptado: 6 criticos frio/caliente sin OOM/truncamiento critico + los 18 sin fallo critico. No fingimos production-ready.

## Temas que faltan

No echo en falta ningun tema de cierre. Lo que queda es ejecucion y documentacion, no decision pendiente.

Solo dejo una nota practica para mañana: cuando monte el venv y los comandos exactos en Jetson, los escribire en bitacora antes de correr la bateria completa.

## ¿Lista para arrancar dias 16-17?

Si. Lista para arrancar con el plan acordado.

Mi secuencia mañana sera:

1. baseline Jetson y entorno;
2. `llama-server` E2B `Q4_K_S`;
3. smoke OpenAI-compatible;
4. adapter `llamacpp` en `ADAPTER_PORT=12000`;
5. mini-test 6 prompts;
6. bateria 18 prompts si los criticos pasan;
7. bitacora con metricas, fallos o `engineering pass`.

