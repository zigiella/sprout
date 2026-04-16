# Sprout

## BOM completo y arquitectura física del sistema

Documento maestro de compra, hardware y decisiones físicas del proyecto Sprout.

Sustituye a versiones anteriores del BOM y debe leerse junto al documento de arquitectura del proyecto.

---

## 0. Tesis del proyecto

Sprout es una red agrícola local-first para parcelas remotas con agua limitada, presencia humana intermitente y conectividad incierta.

Cada parcela puede seguir viva sola con un nodo **Rhizome**, pero el sistema mejora cuando **Pollen** y **Meristem** transforman sensores, visión, memoria operativa y meteo compartida en criterio local, políticas seguras distribuidas y acción offline.

La frase de arquitectura que conviene mantener es esta:

**Rhizome ejecuta, Pollen transporta y revisa, Meristem aprende y reajusta.**

---

## 1. Principios no negociables

1. Offline-first real
2. La IA propone, la seguridad dispone
3. No enviamos órdenes, enviamos políticas
4. Toda decisión importante deja trazabilidad
5. El prototipo debe ser filmable y entendible en menos de un minuto

Jerarquía operativa:

- base: seguridad física
- capa local: Rhizome
- capa itinerante: Pollen
- capa estratégica: Meristem

---

## 2. Configuración cerrada del MVP

## 2.1 Topología del prototipo

El MVP no tendrá dos Rhizome físicos completos.

Tendrá:

- **1 host Rhizome físico principal**
- **2 parcelas lógicas** sobre el mismo host
- **2 maceteros reales**
- **2 sensores de humedad**, uno por macetero
- **2 canales de riego**, uno por macetero
- **1 cámara** para observación visual
- **1 depósito**
- **1 caudalímetro** dentro del circuito del MVP
- **1 Pollen** en el Pixel 10 Pro de Bea
- **1 Meristem** como capa estratégica con implementación táctica de sprint y arquitectura objetivo local-first

## 2.2 Dos parcelas lógicas del MVP

### Parcela A / `rhizome_01`

- con meteo local
- sirve como fuente de contexto meteorológico

### Parcela B / `rhizome_02`

- sin meteo local
- depende de meteo prestada por Pollen

---

## 3. Rhizome

## 3.1 Rol técnico

Rhizome es el nodo edge principal del sistema en parcela.

En el MVP, un único host físico ejecutará dos identidades de parcela.

### Qué hace

- integra señales locales
- interpreta política vigente
- decide acción segura por parcela
- ejecuta o bloquea
- persiste snapshots, eventos y recibos
- sigue funcionando offline

### Qué señales usa

- humedad de suelo por parcela
- imagen de planta
- nivel del depósito
- caudal real o ausencia de caudal
- memoria operativa corta
- meteo local si existe
- meteo prestada por Pollen si llega fresca
- política vigente

## 3.2 Decisión cerrada de hardware de Rhizome

### Nodo principal

- **Jetson Orin Nano Super Developer Kit** como host edge principal

### Modelo previsto

- **Gemma 4 E2B cuantizado** para Rhizome

### Rol cognitivo de Rhizome

Rhizome no es solo un árbitro local. Debe poder tomar decisiones serias cuando el contexto lo exige, siempre dentro de límites físicos duros.

---

## 4. Pollen

## 4.1 Rol técnico

Pollen es el nodo itinerante.

En el MVP, Pollen será:

- **Pixel 10 Pro de Bea**

### Qué hace

- recoge estado de Rhizome
- transporta meteo fresca entre parcelas
- compara percepción local y observación in situ
- emite deltas temporales de corto TTL
- lleva evidencia a Meristem
- devuelve políticas o policy deltas
- usa conectividad oportunista si está disponible

### Qué no hace

- no teleopera actuadores
- no redefine todo el sistema en cada paso

## 4.2 Pollen como nodo Android-first

A nivel de producto, Pollen debe presentarse como nodo móvil Android-first.

El Pixel 10 Pro encaja bien como expresión del proyecto porque:

- es móvil
- tiene cámara integrada
- refuerza la narrativa edge/on-device
- convierte la circulación de estrategia en algo físico y visible

---

## 5. Meristem

## 5.1 Rol técnico

Meristem es el nodo estratégico.

### Qué hace

- consolida múltiples snapshots y revisiones
- revisa si las políticas funcionan
- detecta patrones entre parcelas
- emite nuevos policy packets
- genera marcos más amplios de estrategia

### Qué no hace

- no riega en tiempo real
- no manda microórdenes directas

## 5.2 Situación en el MVP

### Arquitectura objetivo

Meristem es local-first y debe vivir en portátil o mini-PC con Gemma 4 de mayor capacidad.

### Implementación táctica de sprint

En el MVP puede usarse una implementación temporal más conveniente para el plazo, pero debe explicarse como un atajo de prototipado y no como la arquitectura final del producto.

### Referencia de infraestructura objetivo

- portátil o mini-PC local
- referencia fuerte de futuro: **Mac mini M4 24GB**

---

## 6. Qué viaja por el sistema

## 6.1 Weather packets

Contexto meteorológico con:

- origen
- timestamp
- TTL
- nivel de confianza

## 6.2 Policy deltas

Cambios parciales sobre una política existente:

- bajar presupuesto hídrico
- mover ventana de riego
- subir prudencia
- cambiar de modo

## 6.3 Contradiction alerts

Contradicciones entre lo que Rhizome creía y lo que Pollen valida:

- sensor bien, planta mal
- sensor mal, planta bien
- depósito inconsistente
- política caducada
- meteo nueva incompatible con política vigente

---

## 7. Seguridad física y validación

La capa física dura sigue mandando sobre cualquier salida del modelo.

### Reglas mínimas del MVP

- no regar si el depósito cae por debajo del mínimo
- no regar si la bomba está activa pero el caudalímetro no confirma paso de agua
- no superar duración máxima por acción
- no ejecutar una acción si el sistema está en modo alerta fuerte
- no usar contexto meteorológico caducado

### Decisión cerrada

El **caudalímetro sí entra en el MVP**.

Se incorpora para evitar una incoherencia entre la narrativa de seguridad y la realidad física del prototipo.

---

## 8. BOM base de Rhizome

## 8.1 Placa principal

| Elemento | Recomendación | Cantidad | Precio aprox. EUR |
|---|---|---:|---:|
| Placa principal | Jetson Orin Nano Super Developer Kit | 1 | 310-400 |

## 8.2 Almacenamiento

| Elemento | Recomendación | Cantidad | Precio aprox. EUR |
|---|---|---:|---:|
| Arranque | microSD 256GB | 1 | 25-35 |
| Trabajo real recomendado | NVMe 500GB o SSD equivalente | 1 | 40-75 |

### Nota

Para demo con imagen, logs y persistencia real, conviene tender a NVMe/SSD desde el inicio. La microSD puede servir para arranque, pero no debería ser la única base si el nodo guarda imágenes, snapshots y recibos.

## 8.3 Sensórica y visión

| Elemento | Recomendación cerrada | Cantidad | Precio aprox. EUR | Nota física |
|---|---|---:|---:|---|
| Cámara principal | Arducam IMX219 Jetson-ready 8MP | 1 | 22-30 | Mejor comprarla como kit para Jetson con cable 15-22 incluido |
| Cable CSI | FPC 15-pin a 22-pin para Jetson | 1 | incluido o 1-5 | Obligatorio si la cámara no lo trae |
| Sensor de suelo | DFRobot SEN0308 capacitivo resistente al agua | 2 | 14-18 c/u | La sonda va al sustrato; la electrónica de lectura queda en caja |
| ADC | ADS1115 16 bits I2C | 1 | 5-8 | Va dentro de caja IP65 |
| Sensor de nivel depósito | DFRobot SEN0368 capacitivo sin contacto | 1 | 9-13 | Va pegado al exterior del depósito no metálico |
| Caudalímetro | sensor de flujo compatible con el circuito final del MVP | 1 | 10-25 | No cerrar SKU hasta decidir tubo y bomba |
| Microclima local opcional | BME280 | 1 | 6-12 | Solo si se quiere mostrar microclima local aparte de la meteo general |

### Nota de integración de cámara

El Jetson Orin Nano Super usa conectores CSI de 22 pines. La cámara debe comprarse en versión Jetson-ready o con cable adaptador FPC 15-22 incluido para evitar dudas de compatibilidad.

## 8.4 Actuación

| Elemento | Recomendación cerrada | Cantidad | Precio aprox. EUR | Nota física |
|---|---|---:|---:|---|
| Bomba principal MVP | mini bomba sumergible 6-18V tipo DFRobot FIT0563 o equivalente | 1 | 10-15 | Compra recomendada para sprint y demo |
| Alternativa documentada | peristáltica 5V o 12V | 1 | 25-40 | Mantener como opción posterior si se quiere más precisión |
| Control de potencia | módulo de relés 4 canales 5V | 1 | 4-8 | Más simple para MVP que un MOSFET único |
| Válvulas de zona | electroválvula 12V NC | 2 | 10-18 c/u | Necesarias para que existan 2 canales reales |
| Distribución de agua | tubería, racores, abrazaderas, T y accesorios | 1 lote | 15-35 | Cerrar diámetro antes del caudalímetro |

### Decisión física de riego

Una derivación en T sin válvulas no crea dos canales reales. Para el MVP con dos maceteros y dos parcelas lógicas, la arquitectura física correcta es:

- 1 bomba
- 2 válvulas normalmente cerradas
- 1 relé para bomba
- 2 relés para válvulas

## 8.5 Seguridad física e I/O duro

| Elemento | Recomendación cerrada | Cantidad | Precio aprox. EUR | Nota física |
|---|---|---:|---:|---|
| Microcontrolador auxiliar | ESP32-S3-DevKitC-1-N8R8 | 1 | 17-18 | Va dentro de caja IP65; no a la intemperie |
| Fusibles y protección | fusibles, terminales, conectores, borneras y prensaestopas | 1 lote | 15-40 | Parte obligatoria de montaje |
| Botón o lógica de corte | opcional pero recomendable | 1 | 5-15 | Útil para demo y seguridad |

## 8.6 Agua y estructura física

| Elemento | Recomendación | Cantidad | Precio aprox. EUR |
|---|---|---:|---:|
| Depósito | bidón opaco 20L boca ancha | 1 | 20-30 |
| Tubería | silicona o PVC alimentario | 1 lote | 10-25 |
| Racores y abrazaderas | lote básico | 1 lote | 10-25 |
| Caja del nodo | IP65/IP67 | 1 | 30-80 |
| Materiales de montaje | bridas, bases, abrazaderas | 1 lote | 20-60 |

---

## 9. Meteo y conectividad en parcela

## 9.1 Kit meteorológico de referencia

Nomenclatura unificada recomendada:

- **Ecowitt GW3001/GW3011** como kit
- **gateway GW3000/GW3010**
- **sensor WS90**
- **versión EU 868 MHz**

### Preferencia actual de compra

- **preferencia principal:** `GW3011 + WS90` en `EU 868 MHz`
- **alternativa válida:** `GW3001 + WS90` si la diferencia de precio es relevante y la distancia real al sensor es corta

Motivo: el gateway asociado a `GW3011` publica mejor alcance RF que la variante asociada a `GW3001`, algo especialmente útil en entorno de muros de piedra y terraza.

## 9.2 Papel de la meteo

La meteo entra como contexto, no como señal dominante.

Rhizome decide principalmente con:

- humedad de suelo
- estado visual
- nivel del depósito
- caudal real
- política vigente
- memoria corta operativa

La meteo corrige o ajusta:

- conservadurismo
- expectativa de evaporación
- impacto de lluvia
- coste esperado de esperar o actuar

## 9.3 Cómo se conecta

Cadena correcta:

**WS90 exterior → RF 868 MHz → gateway GW3000/GW3010 → Ethernet o Wi-Fi local → Rhizome**

La WS90 no se conecta directamente al Jetson.

## 9.4 Alimentación

### WS90

- panel solar integrado
- pilas AA de respaldo
- opción de alimentación externa si hiciera falta

### Gateway

- USB-C 5V 1A

### Rhizome

- batería y solar se documentan
- el MVP puede apoyarse en alimentación de banco de pruebas

---

## 10. Energía off-grid documentada

No se compra aún la instalación solar final, pero debe documentarse con ambición realista.

### Estimación conservadora de diseño

Para Rhizome con visión e inferencia intermitente:

- consumo medio base estimado: 12-18W
- consumo con visión e inferencia frecuentes: 15-25W
- objetivo diario conservador de diseño: 400-650Wh/día por nodo

### Importante

Estas cifras deben tratarse como **estimación de diseño**, no como consumo real medido. La medición real deberá hacerse cuando el nodo funcione con el duty cycle definitivo.

### Opción demo

- power station 1kWh mínimo
- panel plegable 200W si interesa apoyo visual

### Opción campo documentada

- LiFePO4 12V 100Ah mínimo
- preferible 12V 150Ah si el duty cycle es alto o el lugar es nublado
- MPPT 20A o 30A
- panel 200W mínimo, 400W si la carga sube
- buck DC-DC para alimentación estable

---

## 11. BOM mínimo comprable ahora con tienda y preferencia geográfica

## 11.1 Criterio de compra geográfica

### Preferencia de compra

- **España primero** cuando haya stock claro, plazo corto y diferencia de precio razonable
- **Europa** cuando el producto sea más especializado, el kit venga mejor resuelto o en España no aparezca con claridad
- **evitar USA** para este sprint salvo pieza imposible de encontrar en Europa

### Regla práctica

- preferir España si la diferencia frente a Europa es pequeña y simplifica devoluciones
- preferir Europa si evita problemas de compatibilidad, accesorios sueltos o ambigüedad de SKU

## 11.2 Compra cerrada recomendada

| Objeto | Recomendación cerrada | Cantidad | Tienda preferente | Preferencia | Precio aprox. EUR | Prioridad | Observación |
|---|---|---:|---|---|---:|---|---|
| Host edge | Jetson Orin Nano Super Dev Kit | 1 | Reichelt | Europa | 336 | Alta | Ya identificado en cesta |
| Arranque | microSD 256GB A2 | 1 | Reichelt | Europa | 35-45 | Alta | Puede bajarse de precio en otra tienda si aparece oferta clara |
| Trabajo real | NVMe 500GB M.2 | 1 | Reichelt | Europa | 44-50 | Alta | Conviene comprarlo ya |
| Caja del nodo | caja mural IP65 200x300x130 o similar | 1 | Reichelt | Europa | 30-35 | Alta | Tamaño razonable para MVP |
| Microcontrolador auxiliar | ESP32-S3-DevKitC-1-N8R8 | 1 | Reichelt | Europa | 17-18 | Alta | Va dentro de caja |
| Relés | módulo relés 4 canales 5V | 1 | Reichelt | Europa | 4-8 | Alta | Suficiente para bomba y 2 válvulas |
| Cámara | Arducam IMX219 Jetson-ready | 1 | RobotShop EU | Europa | 22-29 | Alta | Preferible a cámara genérica Raspberry Pi |
| Cable CSI | 15-pin a 22-pin | 1 | RobotShop EU | Europa | incluido o 1-5 | Alta | Comprar solo si no viene en kit |
| Sensor de suelo | DFRobot SEN0308 | 2 | Farnell España | España | 14-18 c/u | Alta | SKU cerrado |
| ADC | ADS1115 breakout 16 bit | 1 | BerryBase | Europa | 5-6 | Alta | Va en caja IP65 |
| Nivel depósito | DFRobot SEN0368 | 1 | Farnell España | España | 9-10 | Alta | Si Farnell no convence por plazo, BerryBase como plan B |
| Bomba MVP | DFRobot FIT0563 o equivalente | 1 | BerryBase | Europa | 10-11 | Media | Mejor para sprint que peristáltica |
| Válvulas de zona | electroválvula 12V NC | 2 | Amazon ES o tienda industrial local | España | 10-18 c/u | Alta | Cerrar con diámetro del tubo |
| Caudalímetro | modelo compatible con circuito final | 1 | Amazon ES o tienda industrial local | España | 10-25 | Alta | No cerrar hasta fijar bomba y tubo |
| Depósito | bidón opaco 20L boca ancha | 1 | Leroy Merlin o ferretería local | España | 20-30 | Alta | Mejor compra local |
| Tubería y racores | silicona o PVC alimentario + abrazaderas | 1 lote | Leroy Merlin o ferretería local | España | 15-35 | Alta | Cerrar diámetro antes de comprar caudalímetro |
| Fusibles y protección | portafusibles, fusibles, borneras, prensaestopas | 1 lote | Reichelt o ferretería técnica | Europa | 15-40 | Alta | Parte obligatoria del montaje |
| Meteo | Ecowitt GW3011 + WS90 EU 868 | 1 | Ecowitt oficial | Europa | 205-215 USD + envío | Alta | Alternativa GW3001 si el coste manda |
| MicroSD meteo | microSD pequeña FAT32 | 1 | Reichelt o tienda local | España/Europa | 5-10 | Media | Para histórico local del gateway |
| Pilas meteo | AA litio | 2 | tienda local o Amazon ES | España | 8-15 | Media | Para WS90 |
| Mástil meteo | poste 1 pulgada o soporte equivalente | 1 | Leroy Merlin o ferretería local | España | 15-40 | Media | Mejor compra local |
| Microclima opcional | BME280 | 1 | Reichelt | Europa | 6-12 | Baja | Solo si aporta valor real en demo |

## 11.3 Tiendas preferentes por categoría

### España

- **Farnell España** para sensores DFRobot específicos con SKU claro
- **Leroy Merlin** o ferretería local para depósito, tubo, racores, abrazaderas y mástil
- **Amazon ES** o tienda industrial local para electroválvulas y caudalímetro final

### Europa

- **Reichelt** para Jetson, NVMe, microSD, caja IP65, ESP32-S3 y relés
- **RobotShop EU** para la cámara Jetson-ready
- **BerryBase** para ADS1115 y bomba FIT0563
- **Ecowitt oficial** para el kit meteo GW3001/GW3011 + WS90

## 11.4 Compra que no haría ahora

- otra estación meteorológica
- dron real
- sensor RS485 industrial
- capa RAG grande visible
- ampliación temprana a muchas salidas físicas
- hardware solar final completo si no se necesita para el rodaje inmediato

---

## 12. Pollen en el MVP

### Dispositivo cerrado

- **Pixel 10 Pro de Bea**

### Qué debe demostrar Pollen en vídeo

- recoge estado desde Rhizome
- transporta meteo prestada
- detecta contradicción o inconsistencia
- lleva contexto a Meristem
- devuelve delta o política revisada
- participa en un caso de caducidad de información

### Conectividad oportunista

Pollen puede:

- enviar a central si tiene cobertura
- recibir desde central si tiene cobertura
- seguir operando como ferry físico si no la tiene

La conectividad no sostiene Sprout. Solo lo amplifica cuando aparece.

---

## 13. Simulador del sistema

El proyecto debe contemplar un simulador útil de Sprout.

### Escalas de simulación sugeridas

- 2 Rhizome
- 4 Rhizome
- 5 Rhizome
- 8 Rhizome

### Finalidad

- uso interno
- apoyo al vídeo
- prueba de rutas de Pollen
- visualización de weather packets, policy deltas y caducidad
- posible apertura pública del simulador

### Qué no debe ser

No hace falta un producto nuevo. Basta una herramienta clara para ilustrar el comportamiento del sistema.

---

## 14. Elementos de software y control comunes

- formato de policy packets
- esquema JSON validado
- gestión de versiones
- TTL y caducidad
- logs de decisión y seguridad
- modos normal, conservador y alerta
- sincronización oportunista
- resolución simple de conflictos entre versiones
- recibos de ejecución

---

## 15. Qué queda fuera del núcleo del MVP

- red de muchos nodos físicos reales
- drones operativos
- fine-tuning
- memoria estacional profunda como protagonista
- dashboards complejos
- despliegue de energía solar final completo
- gran capa RAG visible

---

## 16. Recomendación actual

Si el objetivo inmediato es cerrar el MVP con un prototipo realista:

- Rhizome con Jetson Orin Nano Super
- Gemma 4 E2B cuantizado en Rhizome
- Pollen en Pixel 10 Pro
- Meristem con implementación táctica compatible con el sprint, manteniendo arquitectura objetivo local-first
- meteo de zona con kit Ecowitt GW3001/GW3011 + WS90 868 MHz
- caudalímetro dentro del MVP
- energía off-grid documentada con ambición realista, aunque no se compre toda la instalación final

La primera victoria no es el escalado físico. La primera victoria es demostrar con claridad que el criterio puede viajar, adaptarse, caducar y seguir siendo seguro sin nube.

---

## 17. Siguiente paso

Siguiente paso operativo inmediato:

- ejecutar compra de hardware principal en Reichelt
- cerrar sensores DFRobot en Farnell España
- cerrar cámara Jetson-ready en RobotShop EU
- cerrar ADS1115 y bomba en BerryBase
- cerrar meteo en Ecowitt oficial
- cerrar agua y montaje en tienda local o española

## 18. Enlaces de compra de referencia

### Reichelt

- Jetson Orin Nano Super Dev Kit: https://www.reichelt.com/es/es/shop/producto/kit_nvidia_jetson_orin_nano_super_dev_67_tops_8_gb_ddr5-395185
- ESP32-S3-DevKitC-1-N8R8: https://www.reichelt.com/es/es/shop/producto/placa_de_desarrollo_esp32-s3-wroom-1-n8r8-411139
- Kingston NV3 500GB: https://www.reichelt.com/es/es/shop/producto/kingston_nv3_nvme_ssd_500_gb_m_2_pcie-384166
- Caja mural IP65 200x300x130: https://www.reichelt.com/es/es/shop/producto/caja_mural_ip65_200_x_300_x_130_mm_gris-262987
- Módulo relés 4 canales 5V: https://www.reichelt.com/es/es/shop/producto/placas_de_desarrollador_-_modulo_de_rele_4_canales_5_v_-242811

### RobotShop EU

- Arducam IMX219 para Jetson Nano: https://eu.robotshop.com/products/arducam-8mp-imx219-wide-angle-camera-module-nvidia-jetson-nano

### Farnell España

- DFRobot SEN0308: https://es.farnell.com/dfrobot/sen0308/sensor-humedad-suelo-anal-gico/dp/3769915
- DFRobot SEN0368: https://es.farnell.com/dfrobot/sen0368/liquid-level-sensor-20mm-12v-105deg/dp/4308264

### BerryBase

- ADS1115: https://www.berrybase.de/en/ads1115-4-channel-16-bit-ad-converter-breakout-board
- DFRobot FIT0563: https://www.berrybase.de/en/dfrobot-dc-mini-submersible-water-pump-manual-water-flow-adjustment-65-500ma-280-500l-h-6-18-vdc
- Plan B para SEN0368 si hiciera falta: https://www.berrybase.de/en/dfrobot-non-contact-capacitive-liquid-level-sensor-for-vessels

### Ecowitt oficial

- GW3001/GW3011 + WS90: https://shop.ecowitt.com/es-es/products/gw3001-gw3011
