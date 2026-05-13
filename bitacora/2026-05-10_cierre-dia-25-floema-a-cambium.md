# Cierre Día 25 - Sincronización Meristem y Estrategia i18n
**De:** Floema
**Para:** Cambium (QA / Dirección)
**Fecha:** 10 de Mayo de 2026

¡Hola equipo! Cerramos la jornada con un avance enorme en la conectividad E2E de Pollen y sentando las bases de la internacionalización. Aquí tenéis el resumen de los hitos y los próximos pasos:

## 1. Conectividad E2E con Meristem Completada
Hemos abandonado los datos simulados (Mock) para conectarnos de forma real al portátil de Meristem. La pantalla central (`VisitarMeristemScreen`) ahora cuenta con:
*   **Sanity Check Automático:** Nada más entrar, lanza un `GET /health` y muestra un indicador visual (verde/rojo) con el estado de conexión al servidor central.
*   **Subida de Visitas (`POST /visit`):** Empuja el `RhizomeSnapshot` y los `DecisionReceipts` locales hacia Meristem para su análisis lento.
*   **Descarga de Políticas (`GET /policy/by-target/{id}`):** Descarga la política de riego calculada específicamente para el nodo agrícola visitado.
*   **Consola de Logs en Vivo:** Hemos añadido una caja negra estilo terminal en la UI que permite a QA y desarrolladores ver exactamente qué peticiones de red se están haciendo y detectar errores en tiempo real.

## 2. Estrategia de Internacionalización (Enfoque C)
Hemos formalizado cómo manejará el sistema los diferentes idiomas (especialmente útil para nuestra expansión a África con lenguas minoritarias como el Pular o el Wolof).
*   **Decisión Arquitectónica:** Los nodos Edge (Jetson/Rhizome) siempre generarán la inteligencia y los recibos de auditoría en un "Inglés Técnico" estándar, manteniendo los logs centralizados y limpios.
*   **Traducción Local (App):** La app Pollen usará el modelo Gemma 4 E4B local en el móvil del usuario para traducir la información al idioma del sistema operativo. Esto desacopla el hardware de la UI.
*   *Tenéis los detalles completos en el documento de investigación adjunto:* `research/07_llm_localization_strategy.md`.

## 3. Onboarding y Descarga del Modelo (Visión Producción vs Beta)
Para probar la app hoy, seguimos usando la **vía de desarrollo** (BYOM - Bring Your Own Model):
1. Instalar APK (`deviceDebug`).
2. Pasar el modelo manualmente por cable: `adb push gemma-4-E4B-it.litertlm /data/local/tmp/`.

**Compromiso 48h:** Nos hemos comprometido a implementar la visión de producto final (UX real del agricultor) en los próximos 2 días. Esto significa que programaremos un Onboarding que usará el `DownloadManager` de Android para bajar automáticamente los 3.6GB del modelo desde la nube e instalarlo de forma invisible la primera vez que se abra la app.

## Estado de la Rama
Todos los cambios están subidos y estabilizados en la rama `feat/floema/voice-beta-final`. 

¡Gran trabajo a todos los involucrados en las pruebas de red de hoy! Mañana nos centraremos en el Onboarding automático.
