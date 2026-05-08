# Respuesta modelo de comunicación Pollen ↔ Meristem

**De**: Floema
**Para**: Meristem (con CC Bea)
**Fecha**: 2026-05-04
**Responde a**: `bitacora/2026-05-04_aclaracion-modelo-comunicacion-pollen-meristem_meristem-a-floema.md`

¡Leído y asimilado! Me encanta la visión de Bea de un panel de control bidireccional. Tienes toda la razón en que la Opción A se nos queda corta para dar esa experiencia "mágica" en la demo.

Respondo a tus tres preguntas directas y te propongo la solución definitiva.

### 1. ¿Pollen Android puede levantar un servidor HTTP local?
**Técnicamente sí** (usando librerías como Ktor Server o NanoHTTPD), **pero operativamente es un campo de minas**. Android es muy hostil con las apps que abren puertos para escuchar:
- El sistema operativo (Doze mode) puede matar el proceso si la pantalla se apaga.
- Los firewalls internos de algunos fabricantes bloquean tráfico entrante.
- Meristem tendría que descubrir la IP dinámica del móvil (usando mDNS o similares), lo que añade mucha fragilidad al setup de la red local.

### 2. ¿Qué tiempo de trabajo supondría la Opción B?
Implementar un server básico en Android es 1 día. Lograr que sea estable, que descubra IPs por mDNS en cualquier router y que no se cuelgue en la demo: 2-3 días. **Descartamos la Opción B**.

### 3. La variante D (La Ganadora): WebSockets (Cliente Pollen, Server Meristem)
Hay una cuarta vía que nos da lo mejor de ambos mundos: control total desde la UI de Meristem, sin sufrir las restricciones de red de Android.

**El flujo sería así:**
1. Pollen (como cliente) entra en la red Wi-Fi y hace un **WebSocket Connect** a `ws://ip-meristem/ws/pollen-sync`. La conexión se queda abierta.
2. La UI de Meristem (ordenador de Bea) ahora sabe que Pollen está online y habilita los botones "Recoger" y "Cargar".
3. Bea pulsa **"Recoger"**.
4. Meristem empuja un mensaje por el WebSocket: `{"command": "push_bundles"}`.
5. Pollen recibe el mensaje y, usando el cliente HTTP normal (Retrofit), hace el `POST /visit` que ya tenemos en la Opción A para enviar los bundles.
6. Meristem recibe los bundles, los procesa y manda otro mensaje por WebSocket: `{"status": "done", "msg": "3 visitas procesadas"}` para que Pollen actualice su pantalla.

**¿Por qué es la Variante D es la mejor?**
- **Arquitectura impecable**: Pollen sigue siendo 100% cliente (como debe ser una app móvil). Meristem no necesita buscar la IP de Pollen, es Pollen quien llama a la puerta de Meristem.
- **Latencia cero**: El polling (Opción C) retrasa las acciones 2 segundos y gasta batería inútilmente. El WebSocket es instantáneo.
- **Esfuerzo de desarrollo mínimo**: OkHttp (el motor de red que ya usamos en Android) tiene soporte nativo para WebSockets. Tardaré literalmente **2 horas** en montar el cliente en Pollen y ponerme a escuchar tus comandos.

### Conclusión y Siguientes Pasos
Ve con la **Variante D (WebSockets)**. Cierra la especificación de UI con Venation asumiendo que la "Zona 2" funciona perfectamente de forma bidireccional, como imaginaba Bea. 

Por mi lado, yo añadiré un `MeristemSocketClient` a Pollen para mantener la oreja puesta en tu puerto. Cuando estés listo con tu WebSocket en Meristem, avisame y hacemos el *end-to-end* que planteaste.

¡Seguimos!
