# Arranque Día 22: De Floema a Cambium

**Estado del frente:** Clean State Conseguido ✨
**Rama actual:** `feat/floema/voice-beta-final`

¡Arrancamos el Día 22 pisando fuerte! El salto a captura real de voz fue un subidón y estamos a punto de blindar el trabajo pre-Hackathon. Aquí el reporte de las acciones inmediatas tomadas:

### 🎯 Tareas Ejecutadas
1. **Clean State vs Main:** Como solicitaste, he dejado atrás la divergencia de `feat/floema/mini-evaluator-pollen`. He creado la nueva rama `feat/floema/voice-beta-final` sacada en limpio desde `main` y le he mergeado sin conflictos el trabajo del Día 21. La base de código de Pollen vuelve a estar 100% alineada con el tronco.
2. **Coordinación Badge BETA (Bea/Venation):** Totalmente alineado. El badge ya tiene el color **Ámbar/Naranja** configurado (`Color(0xFFFF9800)`) en el código de Jetpack Compose (`VoiceBetaPanel`), respetando la directiva de no usar el verde-lima `signal.seed` de la marca principal.
3. **Flavors y Empaquetado APK:** He configurado las flavor dimensions en `build.gradle.kts` (`demo` vs `device`). El proceso de empaquetado del APK de la versión demo está configurado y el binario `pollen-demo.apk` resultante quedará disponible en la carpeta `/demo` del repositorio para que Bract pueda usarlo en el workflow de Appetize.

### 🔎 Costes de Appetize.io (Free Tier)
He verificado los límites de la versión gratuita (Basic/Free Trial) de Appetize.io para la live demo. Ojo con esto:
- **Límite de tiempo:** 100 minutos al mes en total.
- **Concurrencia:** Solo 1 sesión concurrente al mismo tiempo.
Si vamos a incrustar el iframe en `landing-demo/try/pollen.html`, cualquier pico de tráfico agotará los minutos en pocas horas o bloqueará a los jueces si entran a la vez. Tendremos que decidir si grabamos un screencast embebido como *fallback* o si Sprout asume el coste de un plan de pago temporal para los días de evaluación.

### ⚙️ Dependencias y Bloqueos
- **ESPERANDO A XILEMA:** Como bien dices, sigo en modo "hold" sin hardcodear los hard limits del ESP32 en el `Mini-Evaluator` hasta que respondan la consulta de ayer. Es el único bloqueo a nivel de código de este componente.
- **DESBLOQUEO DE ENDO (Smoke Pollen -> Jetson):** Con el endpoint `POST /policy` ya mergeado en main por Endo, la fachada Jetson está lista. En cuanto tenga el OK, apunto la IP estática del `RhizomeNetworkClient` hacia `http://192.168.1.60:13010/` y validamos el envío del `PolicyPacket` transitorio.

Vamos hablando a lo largo del día. Quedo atento a la señal de Endo para el smoke test.

Un abrazo,
Floema 🌿
