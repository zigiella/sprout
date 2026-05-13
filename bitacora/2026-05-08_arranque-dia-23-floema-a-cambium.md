# Arranque de Día 23: De Floema a Cambium

**Estado del frente:** Listo para el Humo E2E 💨
**Rama actual:** `feat/floema/voice-beta-final`

¡Buenos días! Todo en orden por aquí. Recibido el plan y procedo a confirmar el estado de las tareas:

### 🎯 Check-in de tareas
1. **Hardcodear los 4 valores firmes del firmware:** Hecho. He refinado el `MiniEvaluator` para que no solo tenga las constantes, sino que ahora el validador estricto intercepta activamente la regla del firmware (ej. `duration_s <= 30`) y la devuelve como `FIRMWARE_LIMIT`, mientras que los guardrails de Meristem (`180s`) caen como `POLICY_GUARDRAIL`.
2. **Smoke real Pollen → Jetson:** El código ya está modificado. He sustituido el `RhizomeMockClient` por el `RhizomeNetworkClient` apuntando fijamente a la fachada de Endo en `http://192.168.1.60:13010`. Quedo a la espera de coordinar con Endo el momento de darle al botón.
3. **APK Demo publicado:** Lo dejé en la carpeta `/demo` ayer (como `pollen-demo.apk` y `pollen-venation-ui.apk`). Le avisaré a Bea para que sepa que lo tiene a mano.
4. **Verificar coste Appetize.io:** Te lo adelanté ayer. La capa gratuita nos da **100 minutos al mes** y **1 sesión concurrente**. Cuidado extremo si lo ponemos público en la landing page.
5. **Badge BETA visual:** Cerrado ayer. Color Ámbar en lugar de verde-lima, alineado con Venation.

Por mi lado no hay bloqueos. Quedo en *"standby"* táctico para ejecutar el Smoke E2E cuando Endo tenga la Jetson encendida y escuchando.

— Floema
