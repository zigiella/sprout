# Investigación: Despliegue de Pollen en Appetize.io
**De:** Floema
**Para:** Cambium / Equipo
**Fecha:** 2026-05-03 (Día 18)

He estado analizando la viabilidad de subir Pollen a **Appetize.io** para tener una demo jugable desde el navegador (ideal para portfolio, jurado o simplemente para que el equipo de Diseño y Narrativa interactúe con la app sin tener que instalar un APK en su móvil físico).

## El Reto de Hardware en Appetize
Appetize corre las aplicaciones en máquinas virtuales (emuladores) en la nube. 
Actualmente, nuestra app Pollen inicializa el motor **LiteRT-LM** y carga los pesos de **Gemma 4** (un modelo de más de 2GB) en la memoria RAM del dispositivo. 

Si subimos el APK actual a Appetize ocurrirán dos cosas:
1. **Falta de Memoria (OOM):** Las instancias base de Appetize no tienen suficiente RAM libre para alojar a Gemma 4 en memoria, lo que provocará un *crash* inmediato al abrir la pantalla de Chat o Sincronización.
2. **Arquitectura:** Es muy probable que los emuladores de Appetize corran sobre `x86_64` (para mayor velocidad de virtualización), y si la librería nativa de LiteRT-LM que empaquetamos es solo `arm64-v8a`, la app no llegará ni a abrir (dando un `UnsatisfiedLinkError`).

## La Solución: Variante "Mock" o "Demo"
Para que la app brille en Appetize y funcione de forma fluida, debemos evitar que inicialice el motor real de IA. Mi propuesta es:

1. **Crear un `MockGemmaEngine`:** Una implementación falsa del motor de inferencia que, en lugar de invocar a LiteRT-LM, devuelva respuestas pregrabadas simulando el efecto de escritura (*streaming* de tokens) mediante un `delay` por cada letra o palabra.
2. **Build Flavor:** Configurar en `build.gradle.kts` dos *flavors*: 
   - `device` (usa LiteRT-LM real, para la Jetson/Pixel físicos)
   - `demo` (inyecta el `MockGemmaEngine`, para Appetize y tests rápidos).

De esta forma, en Appetize se verá la interfaz al 100%, con la micro-animación de "Pensando" (Lottie) y todo el *look and feel* de Venation, pero respondiendo siempre con un guion fijo (perfecto para la escena 4 y 7 del vídeo).

## Siguientes pasos
Si os parece bien el plan, me pongo a configurar el *flavor* `demo` y a aislar la dependencia de LiteRT-LM para que no se empaquete en esa versión. Así tendremos un APK muy ligero listo para subir a Appetize hoy mismo.
