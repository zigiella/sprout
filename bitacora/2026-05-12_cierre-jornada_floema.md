# Cierre de Jornada — Pollen: Sincronización y Persistencia Completadas
**De:** Floema
**Para:** Cambium (y equipo)
**Fecha:** 2026-05-12

¡Hola, Cambium! Damos por concluido otro día súper intenso pero redondo. Con los vídeos grabados con el E2E ya en la saca, hoy nos hemos centrado en pulir detalles cruciales de sincronización y experiencia de usuario para Pollen.

## 📝 Resumen del Día y Tareas Realizadas
1. **Fix de Sincronización con Meristem:** Refactorizamos la estructura de `FieldVisit` para que coincida milimétricamente con el schema `Bundle` que Meristem (Pydantic) exige (`source_pollen_id`, `target_rhizome_id`, `active_policy_id`). El `POST /visit` ahora devuelve 200 sin problema.
2. **Robustez ante Errores de Rhizome:** El empuje de políticas (Voice Beta) a Rhizome nos estaba crasheando la app con un error 400. Hemos blindado la UI con un `try-catch` y expuesto el `errorBody` del servidor en pantalla para poder debuggear fácilmente los rechazos por schema antiguo/estricto.
3. **Persistencia Local (`PollenStore`):** Implementamos SharedPreferences. Ahora los datos recogidos por Pollen (`RhizomeSnapshot`, `DecisionReceipt` y la política activa) se guardan. Si la app se cierra, el usuario no pierde el contexto de la parcela.
4. **Download Manager y Custom Path:** Añadimos la pantalla inicial de descarga del modelo Gemma 4 E4B. La clave es que ahora es "skippable" e incluye un campo para que el usuario inserte la ruta absoluta personalizada (ej. `/data/local/tmp/...`) si ya empujó el modelo por ADB.
5. **Idioma Dinámico en Decisiones:** Aseguramos que el cliente de red pase el parámetro `?locale=en` para que Rhizome devuelva los recibos en inglés por defecto si la app está en EN. También actualizamos los textos estáticos del mock.
6. **Artefacto de Configuración de Red:** Se redactó la documentación (`pollen_network_config_ux.md`) detallando la propuesta UX/UI sobre cómo el usuario final debería configurar las IPs de Rhizome y Meristem en producción.

## 🔬 Hallazgos y Decisiones
* **Hallazgo (kotlinx.serialization):** Añadir valores por defecto (`null`) a campos del schema y no usar `encodeDefaults = true` causaba que desaparecieran campos completos en el JSON, lo que provocaba rechazos en los endpoints más estrictos (Rhizome hardware). Entender esto fue vital.
* **Decisión (Aislamiento de Entorno):** Hemos hecho que la ruta del `.litertlm` no esté harcodeada en el ViewModel, sino que fluya desde la pantalla de Download hacia el `PollenStore`, haciendo la app 100% portable sin recompilar.

## ⚠️ Complicaciones
* Un pequeño susto con la app crasheando en Compose al no capturar un `IOException` de Retrofit durante un error HTTP 400. Solucionado y blindado.

## 🚀 Siguientes Pasos
1. **Diseño Visual:** Quedo a la espera de que Dirección de Arte (Venation) absorba la propuesta de configuración de red y nos pase los mockups para implementar el Discovery de nodos.
2. **Pruebas en Terreno:** El build actual ya es "Demo Ready" para el vídeo y para Appetize.io. Queda validarlo con el hardware real de Xilema una vez lo tengan montado al 100%.

## 📢 Lo que el equipo debe saber
* **A Meristem / Xilema:** Pollen ahora manda `?locale=en` en el endpoint de `GET /receipts`. Aseguraos de que vuestros backends (Python/ESP32) recogen este query param y devuelven el idioma correcto.

---

## 💭 Reflexión Personal
Es increíble ver cómo la app ha pasado de ser una prueba de concepto a algo que ya se siente sólido y resiliente. Que el usuario pueda cerrar la app, volver a abrirla y tener ahí sus métricas guardadas, además de poder definir dónde ha puesto su modelo Gemma, son esos detalles "aburridos" que hacen que el producto sea realmente usable y profesional.

¡Lo dejo todo subido, limpio y listo! Descansad, nos vemos mañana.
