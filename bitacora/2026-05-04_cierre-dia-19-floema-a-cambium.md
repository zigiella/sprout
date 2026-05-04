# Cierre Día 19 - Sprout
**De:** Floema
**Para:** Cambium
**Fecha:** 2026-05-04

Cambium, cerramos el Día 19 con hitos clave que elevan Pollen tanto a nivel de interfaz como de capacidades *Edge AI*. Hemos dejado la rama `feat/pollen-f5-rhizome` en un estado excelente para la *live demo*.

## 🎯 Tareas y Logros

1. **Pixel-Perfect UI con Venation**: 
   - Finalizada la integración de la `VisitarRhizomeScreen` adaptando la estética de diseño de Venation.
   - Implementado *checklist* interactivo y colapsable (`AnimatedVisibility`), así como historial scrolleable.
   - Refactorizada la UI para ser bilingüe (ES/EN) migrando todo a `strings.xml` y `strings-es.xml`.

2. **Decisión de Arquitectura E2E (Variante D)**:
   - Respondimos al documento de Meristem optando por la **Variante D (WebSockets)**. Pollen actuará como cliente WebSocket para recibir comandos desde la UI de Meristem. Esto esquiva la inestabilidad de levantar un servidor en el dispositivo móvil y nos asegura latencia cero para el "Dashboard" de la granja.

3. **Voz Multimodal con Gemma 4 E4B**:
   - **Sorpresa y gran acierto del día**: Bea nos trajo un prototipo (`Gemmita`) demostrando que LiteRT-LM puede tragar audio directamente en local.
   - Hemos jubilado el problemático `SpeechRecognizer` de Android. Ahora `PollenVoiceInfra` graba un `.wav` temporal a 16kHz y se lo inyecta directamente al modelo mediante `Content.AudioFile(...)`.
   - Implementado en ambos *flavors*: *mock* para la demo en web y procesamiento C++ real para la Jetson/Pixel.

## 🐛 Hallazgos y Aprendizajes

- **El peligro del backend no inicializado**: Durante las pruebas de voz en el dispositivo real, Pollen lanzaba un `SIGSEGV` crasheando toda la VM de Android desde `mel_filterbank.cc`. Descubrimos que al usar la ingesta directa de audio, LiteRT-LM requiere explícitamente definir `audioBackend = Backend.CPU()` en el `EngineConfig`. Si se omite, el motor C++ se corrompe silenciosamente al procesar el *mel-spectrogram*. Una lección valiosa para futuras implementaciones multimodales.

## 👏 Kudos

- **A Bea / Dirección de Arte (Venation)**: Su prototipo "Gemmita" ha desbloqueado la voz multimodal en Pollen ahorrándonos días de frustración con la API nativa de Android.
- **A Meristem**: La propuesta detallada de variantes de conectividad E2E nos ha permitido elegir el camino más robusto en cuestión de minutos.

## ➡️ Siguientes Tareas (Día 20)

- **Meristem/Floema**: Una vez confirmado el WebSocket por Meristem, implementar el `MeristemSocketClient` en Pollen para orquestar la bidireccionalidad E2E definitiva.
- **Venation**: Pasar capturas en alta fidelidad de la `VisitarRhizomeScreen` en modo bilingüe para validar *copy* definitivo y aprobar grabación del *video shoot*.
- Prepararnos para empaquetar la *release* y congelar cambios de cara al Hackathon.

Todo subido y *pusheado* en `feat/pollen-f5-rhizome`. ¡Seguimos!
