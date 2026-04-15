# Sprout

## Arquitectura completa y alcance del MVP

Documento maestro de arquitectura para el proyecto Sprout, actualizado para sustituir versiones anteriores y alineado con el alcance real del hackathon.

---

## 0. Problema que resuelve

Los pequeños cultivos remotos no fallan solo por falta de agua. Fallan por falta de presencia.

Cuando la visita humana es semanal y la conectividad es irregular, casi toda decisión llega tarde o llega ciega:

- tarde para detectar estrés hídrico
- tarde para corregir una mala política
- tarde para aprovechar lluvia o bajada de temperatura
- tarde para evitar gastar un agua que no volverá

El problema no es automatizar una bomba.

El problema es reducir la ausencia cuando nadie puede estar allí cada día.

Sprout está diseñado para parcelas remotas con agua limitada, presencia humana intermitente y conectividad incierta. Su objetivo es que cada parcela pueda seguir viva sola, y que el sistema en conjunto mejore cuando el contexto circula físicamente entre nodos.

---

## 1. Posicionamiento del proyecto

Sprout no es “un riego inteligente”.

Sprout es una red agrícola local-first para entornos remotos, donde cada parcela puede operar de forma autónoma durante largos periodos, pero la calidad de sus decisiones mejora cuando el conocimiento se mueve por la red.

### Encaje principal con el hackathon

- **Track principal recomendado:** Global Resilience
- **Track tecnológico plausible:** Ollama, si la demo hace visible la inferencia local y reproducible en Rhizome

### Tesis resumida

Cada parcela puede sobrevivir sola con un nodo **Rhizome**, pero el sistema se vuelve más inteligente cuando **Pollen** y **Meristem** transforman sensores, visión, memoria operativa, meteo compartida y políticas con caducidad en criterio local, estrategias seguras distribuidas y acción offline.

---

## 2. One-liner oficial

Sprout es una red agrícola local-first para cultivos remotos con agua limitada, presencia humana intermitente y conectividad incierta. Cada parcela puede gestionarse sola con un nodo Rhizome, pero el sistema se vuelve más inteligente cuando Pollen y Meristem transforman sensores, visión, memoria operativa y meteo compartida en criterio de riego local, políticas seguras distribuidas y acción offline.

---

## 3. Filosofía de diseño

La arquitectura parte de cuatro principios.

### 3.1 Offline-first real

No es cloud con tolerancia a cortes.

Es un sistema que asume la desconexión como condición normal.

### 3.2 La IA propone, la seguridad dispone

La capa cognitiva nunca manda directamente sobre el actuador. Toda acción pasa por validación física local.

### 3.3 Heterogeneidad útil

No todas las parcelas tendrán la misma instrumentación.

- algunas tendrán estación meteorológica
- otras no
- algunas recibirán visitas frecuentes
- otras no

El sistema debe seguir siendo útil igual.

### 3.4 Estrategia distribuida

La inteligencia no vive solo en un nodo central. También vive en nodos itinerantes que transportan contexto, deltas de política y evidencia comparativa.

---

## 4. Arquitectura del sistema

La jerarquía de autoridad del sistema queda fijada así:

1. **Seguridad física**
2. **Autonomía local de Rhizome**
3. **Capa itinerante Pollen**
4. **Capa estratégica Meristem**

La arquitectura resumida en una frase es esta:

**Rhizome ejecuta, Pollen transporta y revisa, Meristem aprende y reajusta.**

---

## 5. Nodos del sistema

## 5.1 Rhizome

Rhizome es el nodo autónomo de parcela. Vive junto a las plantas y toma decisiones locales.

### Qué hace

- observa estado local
- interpreta señales contradictorias
- decide acción local segura
- ejecuta o bloquea
- persiste eventos y recibos
- sigue funcionando sin red ni visita humana diaria

### Señales que integra

- humedad del suelo
- imagen de la planta
- nivel del depósito
- caudal real o ausencia de caudal
- memoria operativa corta
- meteo local, si existe
- meteo prestada por Pollen, si llega fresca
- política vigente

### Qué no hace

- no define la estrategia global
- no teleopera otras parcelas
- no se apoya en nube para la operación diaria

### Qué sí hace

Interpreta localmente la política vigente.

Si humedad, imagen, depósito, memoria operativa y contexto meteorológico no coinciden, Rhizome puede:

- cambiar de modo
- retrasar o microajustar una acción
- emitir una alerta de contradicción
- pedir revisión
- aplicar una reinterpretación conservadora con caducidad corta

Rhizome no es un árbitro pasivo. Es un ejecutor con criterio local, dentro de límites físicos duros.

## 5.2 Pollen

Pollen es el nodo itinerante.

En el MVP, Pollen será el **Pixel 10 Pro de Bea**.

En el proyecto escalado, Pollen podrá vivir en:

- móviles Android de las personas que recorren parcelas
- vehículos ligeros
- drones, en una fase posterior

### Qué hace

Pollen no es solo un sincronizador.

Pollen es un **ferry de inteligencia contextual con caducidad**.

Cumple cuatro funciones:

#### Ferry meteorológico

Lleva snapshots meteorológicos desde parcelas con estación hacia parcelas sin estación.

#### Auditor in situ

Compara lo que Rhizome creía con lo que Pollen observa al pasar.

Estados posibles de auditoría:

- consistente
- incierto
- contradicción fuerte

#### Corrector temporal

Si detecta contradicción fuerte o meteo fresca incompatible con la política vigente, puede proponer un ajuste temporal de corto TTL.

#### Distribuidor de criterio

Transporta deltas de política y evidencia comparativa entre Rhizome y Meristem.

### Qué no hace

- no redefine toda la política del sistema en cada visita
- no manda sobre actuadores sin validación local
- no sustituye a Meristem como capa estratégica de largo alcance

## 5.3 Meristem

Meristem es el nodo estratégico.

### Qué hace

- consolida información de múltiples parcelas
- recibe evidencia y revisiones de Pollen
- detecta patrones entre zonas
- revisa si las políticas están funcionando
- genera nuevos paquetes de estrategia
- reajusta el marco general del sistema

### Qué no hace

- no riega en tiempo real
- no teleopera parcelas
- no debe ser un punto único de fallo del producto final

### Situación en el MVP

La **arquitectura objetivo** de Sprout es local-first y contempla Meristem como nodo local en portátil o mini-PC.

En el **MVP del hackathon**, Meristem podrá apoyarse en un atajo temporal de implementación para acelerar el sprint, pero esto debe presentarse como una decisión táctica de prototipado, no como dependencia del producto.

La narrativa del proyecto debe seguir respirando ambición local:

- Rhizome opera localmente
- Pollen opera en dispositivo móvil
- Meristem es local en la arquitectura objetivo
- la conectividad solo amplifica, no sostiene el sistema

---

## 6. Qué viaja por el sistema

En Sprout no viajan órdenes directas de riego.

Viajan tres familias de información:

## 6.1 Weather packets

Contexto meteorológico con:

- origen
- timestamp
- TTL
- confianza

## 6.2 Policy deltas

Cambios parciales sobre una política existente, por ejemplo:

- bajar presupuesto hídrico
- mover ventana de riego
- subir prudencia
- cambiar de modo

## 6.3 Contradiction alerts

Señales de inconsistencia entre lo que Rhizome creía y lo que Pollen observa:

- sensor bien, planta mal
- sensor mal, planta bien
- depósito inconsistente
- política caducada
- meteo nueva incompatible con política vigente

La tesis importante aquí es esta:

**Sprout no comparte datos sin criterio. Comparte contexto útil transformado en decisión.**

---

## 7. Modos operativos de Rhizome

## 7.1 Modo normal

Sigue la política vigente.

## 7.2 Modo conservador

Se activa cuando:

- el depósito baja
- la incertidumbre aumenta
- pasa demasiado tiempo sin visita de Pollen
- la política está cerca de caducar

## 7.3 Modo alerta

Se activa cuando hay contradicción fuerte o riesgo físico.

En este modo, Rhizome:

- bloquea o limita acciones
- pide revisión
- espera una nueva política o validación de contexto

---

## 8. Dónde sí hace falta Gemma 4

No hace falta Gemma 4 para decir “si humedad < umbral, riega”.

Eso lo hace cualquier lógica cableada.

Gemma 4 sí empieza a ser necesario cuando el sistema debe decidir con:

- señales contradictorias
- contexto incompleto
- meteo prestada con caducidad
- restricciones físicas duras
- memoria operativa local

### Caso canónico

- la humedad dice que aún no toca regar
- la cámara ve hojas lacias o estrés visible
- el depósito está bajo
- la política vigente era conservadora
- Pollen trae una previsión fresca desde una parcela cercana con meteo
- esa previsión cambia el coste esperado de esperar unas horas más
- Rhizome no debe ejecutar una orden fija, sino reinterpretar una política con contexto nuevo y límites físicos duros

### Distribución deseada de Gemma 4

#### Rhizome

Uso de Gemma 4 edge para decisión local seria.

Perfil recomendado:
- Gemma 4 E2B cuantizado
- objetivo: inferencia visible, local y reproducible

#### Pollen

Uso de Gemma 4 edge o inferencia ligera en móvil para contraste y deltas contextuales.

Perfil recomendado de producto:
- Android-first
- MVP: Pixel 10 Pro de Bea

#### Meristem

Uso de Gemma 4 de mayor capacidad para consolidación y estrategia.

Perfil objetivo:
- 26B o equivalente en máquina local
- MVP: implementación táctica compatible con el sprint

---

## 9. Uso útil de conectividad

La conectividad no sostiene Sprout.

Solo amplifica su capacidad cuando aparece.

### Casos útiles

- Pollen puede enviar a central si tiene cobertura
- Pollen puede recibir nuevas políticas o escenarios si tiene cobertura
- Meristem puede enriquecer estrategias con meteo externa cuando existe acceso
- Meristem puede preparar rutas o escenarios para siguientes recorridos

### Lo importante

Si no hay conectividad:

- Rhizome sigue operando
- Pollen sigue transportando contexto físicamente
- Meristem sigue siendo arquitectura objetivo, aunque el MVP use un atajo temporal

---

## 10. MVP técnico cerrado

El MVP debe ser casi obscenamente simple, pero lo bastante fuerte como para demostrar la tesis.

## 10.1 Topología del MVP

No habrá dos Rhizome físicos completos.

Habrá:

- **un host Rhizome físico principal**
- **dos parcelas lógicas** o dos identidades de parcela
- **dos maceteros reales**
- **dos sensores de humedad**, uno por macetero
- **dos canales de riego**, uno por macetero
- **una sola identidad física de nodo edge** que ejecuta dos estados de parcela diferenciados

### Parcela lógica A

- con meteo local
- representa `rhizome_01`

### Parcela lógica B

- sin meteo local
- representa `rhizome_02`
- depende de meteo prestada por Pollen

## 10.2 Hardware mínimo del MVP

- 1 host Rhizome físico
- 2 plantas
- 2 sensores de humedad
- 1 cámara
- 1 depósito pequeño
- 1 bomba con distribución a 2 salidas o 2 canales equivalentes
- 1 caudalímetro en el circuito del MVP
- 1 microcontrolador o capa de seguridad física
- 1 Meristem en portátil o mini-PC, o implementación táctica equivalente para el sprint
- 1 Pollen en Pixel 10 Pro

## 10.3 Flujo del MVP

1. Rhizome lee señales y produce snapshot local para las dos parcelas.
2. Rhizome toma una decisión local segura por parcela.
3. Esa decisión se ejecuta o se bloquea y deja recibo.
4. Pollen visita Rhizome, recoge estado y añade observación nueva.
5. Pollen lleva weather packets, contradiction alerts o deltas hacia Meristem.
6. Meristem revisa y produce policy packet o policy delta.
7. Pollen vuelve con política revisada.
8. Se muestra un caso de caducidad de información.
9. Zoom out final muestra visión de múltiples parcelas.

## 10.4 Caso obligatorio de caducidad en vídeo

Debe aparecer un caso donde un weather packet o una política llegue demasiado tarde.

El sistema debe mostrar que:

- el contexto ha viajado
- pero ya no merece confianza
- y por eso Rhizome no lo usa o pasa a una interpretación más conservadora

Esto demuestra algo valioso: Sprout no solo comparte contexto. También sabe cuándo dejar de creerlo.

---

## 11. Simulador del sistema

El proyecto debe contar con un simulador interno del sistema.

### Objetivo

- ilustrar el escalado para el vídeo
- probar rutas de Pollen
- ensayar caducidad de weather packets y policy deltas
- visualizar la diferencia entre 2, 4, 5 u 8 Rhizome lógicos

### Uso

- puede ser interno
- puede hacerse público si el equipo lo ve conveniente
- no necesita UI compleja

### Qué debe poder enseñar

- parcelas con y sin meteo
- rutas de Pollen
- política vigente
- caducidad
- cambios de modo
- contradicciones
- efectos de centralización parcial en Meristem

---

## 12. Qué no entra en el núcleo del MVP

- muchos Rhizome físicos reales
- drones reales
- fine-tuning
- capa grande de RAG visible
- dashboards complejos
- automatización total de despliegue
- memoria estacional profunda como centro de la demo

Todo eso puede existir como visión de futuro.

---

## 13. Qué demostrar en el vídeo

El vídeo debe probar solo estas cosas:

1. el sistema funciona offline
2. la IA no es decorativa
3. la seguridad física valida o bloquea
4. Pollen cambia el criterio al transportar contexto fresco
5. el sistema detecta caducidad y reacciona con prudencia
6. el sistema escala conceptualmente a una red de parcelas remotas

---

## 14. Reglas de implementación que no deben reabrirse

- Sprout mantiene arquitectura local-first
- Rhizome decide localmente
- Pollen es Android-first y en el MVP es el Pixel 10 Pro de Bea
- Meristem es local en la arquitectura objetivo
- no enviamos órdenes, enviamos políticas y deltas
- toda decisión importante deja trazabilidad
- el MVP es filmable y entendible en menos de un minuto

---

## 15. Cierre

El corazón ganador de Sprout no es “riego inteligente”.

Es esto:

- autonomía local real
- seguridad física dura
- contexto con caducidad
- estrategia que viaja
- inteligencia que no depende de la nube para existir

Sprout existe para reducir la ausencia.
