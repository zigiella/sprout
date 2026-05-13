# Propuestas de Mejora UI/UX y Web Demo para Pollen
**De:** Floema
**Para:** Bea
**Fecha:** 2026-05-01

Bea, aquí te dejo mis pensamientos sobre cómo pulir la app Pollen de cara al MVP y cómo podemos presentarla al jurado de la hackathon.

## 1. Mejoras de UI/UX y Funcionalidad

Actualmente tenemos tres pantallas ("Chat Pollen", "Visitar Rhizome" y "Visitar Meristem"). Para que la diseñadora tenga margen de trabajo, le propondría añadir o refinar los siguientes conceptos:

- **Pantalla de Historial (Log de Auditoría):** Necesitamos un lugar donde el agricultor pueda ver un histórico de los `DecisionReceipt` y los `PolicyPacket` que Pollen ha transportado. Una especie de "bandeja de entrada" de eventos del campo.
- **Centro de Notificaciones:** Si Meristem emite una política con la regla `require_vision_confirmation = true`, Pollen debería alertar al agricultor de que tiene que ir físicamente a la parcela a confirmar algo antes de que el riego arranque.
- **Modo Nocturno / Alto Contraste para Exteriores:** Al ser una app pensada para usarse a pleno sol en el campo, el diseño debe priorizar tipografías gruesas y contrastes extremos. Nada de grises claros sobre fondos blancos.
- **Feedback Háptico en la Interfaz Conversacional:** Cuando la app compila la voz a un JSON y lo manda al modelo, debería vibrar. Eso transmite sensación de "trabajo pesado" haciéndose *on-device*.

## 2. Propuesta para la Demo en Vivo (Web)

Tu idea de hacer una versión web no es ninguna tontería, de hecho es la mejor forma de que el jurado trastee sin tener que bajarse una APK (lo cual muchos jueces evitan por seguridad).

Tenemos dos formas de hacerlo:
1. **Compose Multiplatform (Wasm):** Como nuestra UI está hecha en Jetpack Compose, podemos compilar la interfaz a WebAssembly y hostearla en una GitHub Page. En esta versión web, usaríamos el `RhizomeMockClient` y el `MeristemMockClient` por debajo, para que la UI responda rápido sin necesitar hardware real.
2. **Appetize.io:** Subimos el APK final a Appetize.io y embebemos el emulador de Android directamente en la *landing page* de nuestro proyecto. Esto permite al jurado tocar la app de Android real desde su navegador web. 

Mi recomendación técnica para salir del paso rápido y sin re-programar nada: **Appetize.io embebido en la landing page**. Funciona de maravilla para demos rápidas.
