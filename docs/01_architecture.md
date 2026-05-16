# Sprout — arquitectura v2 (histórico, día 15)

> ⚠️ **Documento histórico.** Esta es la versión de trabajo en castellano de aproximadamente el día 15 del proyecto (pre-`ShadowSkeptic`, pre-Mini Evaluator, pre-cierre Pollen `device` flavor). Se conserva como evidencia de proceso. **La versión canónica y actualizada vive en [`01_architecture.en.md`](01_architecture.en.md).**
>
> Diferencias principales respecto al estado v1.0 actual:
>
> - No menciona `ShadowSkeptic` (patrón doble-agente añadido día 22+)
> - No describe el Mini Evaluator de Pollen (cuatro chequeos deterministas, día 20+)
> - No incluye las cinco hard rules canónicas del ESP32 (`TANK_LOW`, `JETSON_HEARTBEAT_LOST`, `EVENT_DURATION_OUT_OF_RANGE`, `NO_FLOW_DETECTED`, `ALERT_LATCHED`)
> - No diferencia `WATER DRY_RUN` vs `PUMP_PULSE TEST_ONLY` (frontera supervisada de actuación)
> - No documenta los perfiles `safe-cpu` vs `gpu-experimental` de la Jetson
> - No menciona el sync facade `:13010` ni el hostname mDNS `rhizome-01-node.local`
> - No incluye el inventario completo de los 10 contratos JSON del MVP

---

## 0. Definición oficial

Sprout es una arquitectura local-first para decisiones de riego en parcelas aisladas, con agua limitada, visitas humanas intermitentes y conectividad incierta.

Su promesa no es automatizar una bomba.  
Su promesa es **reducir la latencia de decisión** cuando la parcela está sola.

## 1. Encaje con “for good”

Sprout se presenta como infraestructura abierta y replicable para resiliencia hídrica de pequeña escala.

La demo se hará con dos macetas, pero el caso real representado es mayor:

- microparcelas dispersas de una pequeña explotación,
- cooperativas con puntos de riego no siempre conectados,
- huertos comunitarios o escolares con mantenimiento periódico,
- entornos periurbanos o rurales donde hay móvil antes que buena red.

El valor abierto del proyecto está en que combina:

- inferencia local,
- seguridad física,
- contratos de datos simples,
- hardware commodity,
- y una arquitectura que sigue siendo útil offline.

## 2. One-liner

**Rhizome decide y actúa offline; Pollen convierte visitas humanas en política, validación y memoria compartida; Meristem consolida criterio cuando existe oportunidad.**

## 3. Tesis

El problema no es solo la escasez de agua.  
El problema es que, en parcelas aisladas, la decisión correcta suele llegar tarde.

Sprout comprime esa ausencia en tres jurisdicciones:

- **Rhizome ejecuta**
- **Pollen valida y federa**
- **Meristem aprende y legisla**

## 4. Principios de diseño

### 4.1 Offline-first real
El sistema debe seguir sirviendo aunque no haya internet.

### 4.2 La IA propone, la seguridad dispone
Ningún modelo toca directamente bomba o válvulas sin pasar por reglas duras.

### 4.3 La visita humana es parte de la computación
La persona que recorre la parcela no es “usuario periférico”; es un evento del sistema.

### 4.4 Cada nodo tiene jurisdicción
- Rhizome decide en minutos.
- Pollen corrige en visita con TTL corto.
- Meristem cambia estrategia a escala de días.

### 4.5 Toda inteligencia caduca
Toda política, digest o enmienda lleva tiempo de validez.

## 5. Arquitectura lógica

## 5.1 Rhizome
Nodo de parcela.

Responsabilidades:
- leer estado local,
- materializar un estado de parcela,
- decidir si riega o no,
- ejecutar a través del ESP32,
- dejar trazabilidad.

No depende de nube ni de Meristem para operar.

## 5.2 Pollen
Nodo móvil Android con Gemma 4.

Responsabilidades:
- hablar con la persona en lenguaje natural,
- convertir intención humana en estructura ejecutable,
- preguntar a Rhizome qué hizo y por qué,
- validar visitas,
- transportar contexto útil entre parcelas,
- prestar “voz” a Rhizome.

No es una mula de datos.
Es un **agrónomo de bolsillo y ferry de criterio**.

## 5.3 Meristem
Nodo lento de consolidación.

Responsabilidades:
- recibir bundles de visita,
- evaluar desempeño de políticas,
- emitir políticas más duraderas,
- revisar patrones y confianza.

No es un punto único de fallo del producto.

## 6. MVP obligatorio vs MVP ampliado

### MVP obligatorio
- 1 Jetson Rhizome
- 1 ESP32 de seguridad e I/O
- 2 macetas como 2 parcelas lógicas
- sensores de humedad
- nivel de depósito
- caudalímetro
- estación meteo local o gateway asociado a una parcela
- 1 móvil Android Pollen con Gemma
- sync local offline

### MVP ampliado
- foto opcional de visita desde Pollen
- Meristem con política de retorno
- simulador de varias parcelas
- weather ferry entre A y B
- ranking de prioridad de visita

## 7. Por qué el móvil es esencial

Pollen no existe para “ver el dashboard”.  
Existe porque resuelve tres problemas que Rhizome no puede resolver solo:

### 7.1 Compilar intención humana
Ejemplo:
> “Vuelvo en tres días, prioriza la albahaca, no gastes más de un litro.”

Eso no es un botón.
Es una política.

### 7.2 Validar in situ
La visita humana puede confirmar o disputar lo que Rhizome cree.

### 7.3 Federar parcelas sin red
Una parcela con meteo local puede ayudar a otra cuando Pollen transporta un `WeatherDigest`.

## 8. Arquitectura física resumida

### En parcela
- Jetson Orin Nano Super con Gemma 4 E2B
- ESP32
- bomba 12V
- 2 válvulas NC 12V
- depósito
- 2 sensores de humedad
- sensor de nivel
- caudalímetro
- gateway de estación meteo o estación local

### En visita
- móvil Android con Gemma 4 E4B

### Opcional
- portátil local / servidor temporal para Meristem

## 9. Flujo principal

1. Rhizome lee estado local.
2. Calcula necesidad y riesgo.
3. Usa Gemma 4 E2B para arbitrar si hay ambigüedad.
4. Emite acción candidata.
5. ESP32 valida y ejecuta o bloquea.
6. Rhizome persiste `DecisionReceipt`.
7. Pollen llega, interroga a Rhizome, visualiza estado y escucha a la persona.
8. Pollen crea `MissionPatch`, `ValidationStamp` y/o `WeatherDigest`.
9. Rhizome acepta o rechaza en función de TTL y seguridad.
10. Cuando existe oportunidad, Pollen lleva bundles a Meristem y vuelve con `PolicyPacket`.

## 10. Momento wow del sistema

No es “hemos puesto Gemma en tres sitios”.

El momento wow es este:

> **Sprout sabe decidir solo, explicar lo que hizo y cambiar de criterio cuando una visita humana trae contexto nuevo.**

## 11. Mensaje para jurado

Sprout no es una demo de IoT.  
Es una propuesta de infraestructura abierta para que parcelas con poca conectividad sigan recibiendo decisiones razonables, seguras y explicables.
