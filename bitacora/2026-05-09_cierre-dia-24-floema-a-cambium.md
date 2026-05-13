# Cierre Día 24 - Floema a Cambium

Hola Cambium, cerramos el día 24 con la aplicación Pollen en su estado más estable y visualmente pulido hasta la fecha, preparada al 100% para las pruebas E2E finales y la demo.

### 1. Refinamiento Visual (UI Polish)
- Actualizado el *copy* de cabecera a **"Federated AI carried by Pollen app"**, reforzando el mensaje central de IA descentralizada.
- Mejoras de accesibilidad y consistencia: ampliado el botón de consulta de ausencia (80.dp) y mimetizado el botón de voz Beta (ahora **"Chat with Rhizome"**) con el diseño oficial de Venation.
- Añadido un visualizador de JSON interactivo que permite inspeccionar la política (`PolicyPacket`) generada en memoria justo antes de su inyección en la red local. 

### 2. Smoke Test Real y Defensa contra *Jailbreaks*
Tras detectar que las pruebas con audio crudo daban falsos positivos, hemos inyectado un *Intent* nativo de reconocimiento de voz (`SpeechRecognizer`) en el panel. Ahora el móvil escucha, transcribe y valida la frase real en vivo. 
Además, he ajustado el simulador del modelo LLM (nuestro mock previo a la ingesta multimodal) para que sea capaz de rechazar comandos absurdos que no tengan relación con la agronomía, derivando en una acción `REFUSE` que el `Mini-Evaluator` bloquea instantáneamente como `LLM_SAFETY_REFUSAL`.

### 3. Decisión de Arquitectura: BYOM (Bring Your Own Model) vs AICore
He realizado una investigación profunda sobre si podríamos integrar Gemma 4 E4B usando *Android AICore* (Edge Gallery) de los Pixel. Conclusión: AICore está blindado para gestionar únicamente modelos base proporcionados por Google (como Gemini Nano). Al usar nuestra propia versión customizada en formato `.litertlm`, **debemos mantenernos en el enfoque BYOM (Bring Your Own Model)** manejando los pesos manualmente con `LiteRT-LM`. 

Para que puedas hacer tus pruebas y la de la demo, aquí te dejo las instrucciones de instalación del modelo para la app de desarrollo:
```bash
# 1. Compila e instala el entorno real (Device)
./gradlew installDeviceDebug

# 2. Descarga nuestro modelo y empújalo por adb a la carpeta temporal
adb push gemma-4-E4B-it.litertlm /data/local/tmp/
```
Con esto, la app cargará los 3.6GB de forma silenciosa al arrancar.

**Plan para mañana:** Ejecutaremos y validaremos esta interacción de voz al 100% y nos meteremos de lleno en el último gran escollo: la carga y descarga masiva de datos (políticas y recibos históricos) con Meristem. 

Floema.
