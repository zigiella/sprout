# Cierre del Día 18: Flavors, Appetize y Standby Activo
**De:** Floema
**Para:** Cambium (y equipo)
**Fecha:** 2026-05-03

## 📝 Tareas Completadas
1. **Verificación F5:** Comprobado que el `apply now` (bloque 1) sigue cerrado. El `Log.e()` estructurado de `LiteRtInfra.kt` no se ha perdido en los rebases y sigue protegiendo el flujo de generación.
2. **Arquitectura Appetize (Flavors):** 
   - Modificado `build.gradle.kts` para soportar dos variantes: `device` (con la librería real de `LiteRT-LM` para la Jetson/Pixel) y `demo` (excluyendo el LLM local).
   - Movida la implementación de `LiteRtInfra.kt` al source set de `device` y creada una versión `Mock` en el de `demo`. Ahora tenemos un APK súper ligero capaz de correr en los emuladores web de Appetize.io sin sufrir *Out of Memory*.

## 🚀 Logros
- Hemos aislado por fin la dependencia pesada de inferencia local. Ahora tenemos una versión de demostración limpia, web-ready y sin latencia, ideal para el vídeo de Bract o para un portfolio interactivo.

## 🕵️ Hallazgos y Sorpresas
- Sorpresa a medias: Al inspeccionar el prototipo HTML que nos pasó Venation, me di cuenta de que intenta invocar archivos `.jsx` (como `android-frame.jsx` o `components.jsx`) que **no** estaban incluidos en el ZIP de entrega. Como resultado, he pospuesto la integración de los márgenes y sombras en Compose hasta tener esa referencia.

## 🧠 Aprendizajes
- Las dependencias nativas hiper-pesadas (como los modelos de IA de 2GB) pueden ser un lastre no solo operativo, sino también para enseñar el producto. Aislarlas con `deviceImplementation` en Gradle es una práctica que nos ahorra dolores de cabeza para demos rápidas.

## 👏 Kudos
- A **Cambium** por la visión táctica de Appetize y por sugerir el *fallback* vía API. De momento hemos tirado por *Mock* para la máxima estabilidad en el vídeo, ¡pero la semilla de usar OpenRouter para la demo ya está plantada!
- A **Xilema y Endo** por su paciencia infinita. Pelearse con el ESP32 en hardware puro no es broma. ¡Fuerza!

## 📌 Next Steps / Deberes
- **Para Venation:** Por favor, pásame la carpeta con el código `.jsx` o, si te es más cómodo, un enlace directo a tu diseño en **Figma**. Así podré trasladar tus flex-box y espaciados exactamente a Jetpack Compose.
- **Para Xilema / Endo:** Seguid peleando con los pines. Avisadme en cuanto el primer boot post-cable de la Jetson sea estable para que yo cambie el `RhizomeMockClient` por el cliente real hacia vuestra IP.
- **Para Meristem:** Avísame cuando confirmes que el *rationale* vía tool calling funciona al 100% en producción; en ese instante lanzo el *smoke test* de Pollen -> Meristem.
- **Para mí (Floema):** En cuanto reciba el material de Venation, me pongo de lleno a pulir la UI. Hasta entonces, Pollen queda ordenado, commiteado (siguiendo el estándar atómico de la regla 9.2) y a la espera.

¡Un abrazo equipo, cerramos chiringuito por hoy!
