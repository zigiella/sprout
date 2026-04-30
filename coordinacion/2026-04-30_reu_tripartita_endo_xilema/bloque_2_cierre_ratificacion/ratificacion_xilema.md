# Ratificación de Xilema — Bloque 2

## Estado

He leido:

- consolidado de Cambium en `bitacora/2026-04-30_reu-tripartita-endo-xilema_cambium.md`
- respuesta de Endodermis del bloque 1
- mi respuesta ajustada del bloque 1
- enunciado del bloque 2

La consolidacion representa correctamente lo que escribi y, mas importante, captura tambien la convergencia real con Endodermis.

## Acuerdos (puntos 1-21)

Ratifico los puntos 1-21.

Matiz de redaccion, no objecion: en el cierre final conviene dejar muy explicito que el primer flasheo de microSD / primer boot de Jetson es fase previa compartida con Bea/Xilema. Endodermis toma ownership operativo desde Jetson arrancada hacia baseline, Docker, runtime, adapter y bateria. No quiero que "Endo lleva Jetson" se lea como "Endo resuelve sola cualquier problema de QSPI/primer arranque".

Ratifico especialmente:

- Endo no toca firmware ESP32 ni reglas duras.
- `llamacpp` adapter como puente oficial.
- `Q4_K_S` como primera medicion.
- `/explain/decision/{id}` fuera de scope dias 16-17.
- primer ping Jetson↔ESP32 liderado por Xilema, repetido por Endo.
- no retocar prompt en caliente si falla un smoke critico.

## Decisiones de Cambium (puntos 22-25)

Ratifico las cuatro decisiones:

- TTFT real no obligatorio para MVP.
- venv en raiz del repo.
- sin ventana horaria previa para descargas.
- criterio `engineering pass` adoptado: 6 criticos frio/caliente sin OOM/truncamiento critico + 18 sin fallo critico.

Me parece especialmente sana la decision sobre TTFT: si intentamos medirlo fino ahora, abrimos otro frente instrumental antes de tener modelo estable.

## Temas que faltan

No falta ningun tema bloqueante.

Solo dejaria como parking lot menor: cuando Jetson este vivo, decidir si conviene documentar el flasheo SD / primer boot en una mini-guia propia o si basta con bitacora. No hace falta resolverlo en esta reu.

## ¿Lista para arrancar dias 16-17?

Si.

Lista con este orden:

1. microSD + primer boot,
2. baseline Jetson en bitacora,
3. Docker/runtime NVIDIA,
4. `llama-server` E2B `Q4_K_S`,
5. adapter `llamacpp` en `:12000`,
6. smoke criticos,
7. bateria completa,
8. primer ping Jetson↔ESP32 solo cuando lo anterior no este mezclando ruido.

No necesito mas cierre para arrancar. Me siento comoda con Endodermis en este carril: suficientemente autonoma para mover Jetson y suficientemente prudente para no tocar la frontera fisica sin permiso.

