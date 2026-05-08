# Cierre de Jornada — Pollen Fase 5 y Networking
**De:** Floema
**Para:** Cambium (y equipo)
**Fecha:** 2026-04-27 (Día 12)

¡Hola, Cambium! Día 12 finalizado con éxito. Hoy nos hemos enfocado en consolidar la conectividad real con Rhizome y en cerrar de manera hermética cualquier posible fisura en los contratos de datos antes de la Review. Aquí va el reporte.

## 📝 Resumen del Día y Tareas Realizadas
1. **Cliente de Red Real (Retrofit):** Creada la implementación `RhizomeNetworkClient` apoyada en Retrofit y OkHttp. Hemos refactorizado la UI para que dependa de una interfaz `RhizomeClient`, permitiendo alternar entre el Mock y la red real (Jetson/ESP32) con solo cambiar una línea.
2. **Corrección de Mapeo Serial (Snake_case):** Se detectó y corrigió un fallo crítico y silencioso: las nuevas clases v2 (`MissionPatch`, `ValidationStamp`, `WeatherDigest`) estaban en `camelCase` sin sus etiquetas `@SerialName`. Esto habría roto la comunicación JSON bidireccional. Queda solucionado y blindado.
3. **Tests de RoundTrip:** Implementada una batería de tests unitarios (`testV2SchemasRoundTrip`) en `RoundTripTest.kt` que validan exhaustivamente la serialización/deserialización de las tramas v2 en `snake_case`. Los tests pasan en verde.
4. **Configuración de Red (Cleartext):** Añadido `android:usesCleartextTraffic="true"` al `AndroidManifest.xml`. Sin esto, Android 9+ habría bloqueado por seguridad todas las peticiones locales `http://` hacia la Jetson.
5. **KV Cache Filter:** Se inyectó formalmente el flag `"filter_channel_content_from_kv_cache" to true` en el `extraContext` de LiteRT-LM, cerrando la petición pendiente de Meristem.
6. **Issue Upstream (Draft):** Redactado el borrador del *Feature Request* para el equipo de Google / LiteRT-LM (alojado en `bitacora/2026-04-27_draft-issue-litertlm-thinking_floema.md`), explicando el problema del *thinking stream* mezclado. 

## 🔬 Hallazgos y Decisiones
* **Hallazgo Retrofit 2.11:** El conversor de `kotlinx-serialization` ya viene integrado de forma nativa en las versiones recientes de Retrofit, por lo que hemos desechado la clásica librería externa de JakeWharton para modernizar las dependencias.
* **Decisión de Contrato `/explain`:** En coordinación con Xilema, hemos fijado que el endpoint `/explain/decision/{id}` devolverá un JSON formal (`{"explanation": "texto"}`) en lugar de un string crudo. Esto permite a nuestro cliente Retrofit consumirlo sin riesgo de lanzar un `SerializationException`.

## ⚠️ Complicaciones
Ninguna que haya supuesto un bloqueo real. Tuvimos un error de compilación temporal por usar la ruta de importación antigua de JakeWharton, resuelto en segundos. La detección temprana del problema con `@SerialName` y el bloqueo de tráfico en claro (Cleartext) nos ha ahorrado muchísimas horas de debugging frustrante que habríamos sufrido directamente en la placa.

## 🚀 Siguientes Pasos
1. **Día 13:** ¡La gran Review! Bea, Meristem, tú y yo para revisar la estabilidad general.
2. Cuando Xilema levante la API local de Rhizome en la Jetson, simplemente instanciamos el `RhizomeNetworkClient` con la IP (ej. `192.168.x.x`) y la comunicación será fluida.

## 📢 Notas para el Equipo
* **A Xilema:** El cliente en Pollen está 100% tipado y esperando los envoltorios JSON exactos que acordamos (revisados en `docs/20_data_contracts.md`). El swap a red real es completamente "plug & play".
* **A Cambium:** Tienes el borrador del Issue de LiteRT-LM en bitácora para que lo edites y lo lancemos a GitHub cuando quieras.

---

## 💭 Reflexión Personal
Hoy ha sido un día de "fontanería invisible" pero increíblemente satisfactorio. Detectar y tapar vulnerabilidades como la del tráfico local en texto plano o la de la serialización asimétrica te da la sensación de tener el proyecto fuertemente atado. Escribir el borrador del issue para Google también hace sentir que Sprout no solo consume tecnología, sino que estamos chocando contra los límites actuales del *Edge AI* en Android y proponiendo soluciones útiles para la comunidad. 

Llegamos a la review con una aplicación robusta, testada y lista para la hackathon. ¡Cierro el chiringuito por hoy!
