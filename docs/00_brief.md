# Brief inicial de proyecto

## Proyecto
Sprout

## Qué estamos construyendo
Sprout es una red agrícola local-first para parcelas remotas con agua limitada, presencia humana intermitente y conectividad incierta. Cada parcela puede gestionarse sola con un nodo **Rhizome**, pero el sistema mejora cuando **Pollen** y **Meristem** transforman sensores, visión, memoria operativa y meteo compartida en criterio local, políticas seguras distribuidas y acción offline.

Sprout no existe para “automatizar una bomba”. Existe para **reducir la ausencia** cuando nadie puede estar en el cultivo cada día.

## Problema que resolvemos
Los pequeños cultivos remotos no fallan solo por falta de agua. Fallan por falta de presencia.

Cuando la visita humana es semanal y la conectividad es irregular, casi toda decisión llega tarde o llega ciega:
- tarde para detectar estrés hídrico
- tarde para corregir una mala política
- tarde para aprovechar la lluvia o una bajada térmica
- tarde para evitar gastar un agua que no volverá

El problema no es automatizar una bomba. El problema es que, cuando solo puedes ir al cultivo una vez por semana, casi siempre llegas tarde.

## Tesis del proyecto
Cada parcela debe poder seguir viva sola durante largos periodos. El sistema no depende de conectividad continua. La mejora del sistema ocurre cuando el conocimiento circula físicamente entre nodos.

Una parcela con meteo no solo se protege a sí misma. Puede proteger a otras cuando **Pollen** transporta contexto fresco con caducidad.

## Por qué este diseño
Sprout ataca un problema real con cinco propiedades a la vez:
- escasez de agua
- baja conectividad
- autonomía operativa
- despliegue local y replicable
- infraestructura útil en entornos remotos

Esto importa porque casi ninguna propuesta del mercado resuelve las cinco juntas sin asumir conectividad continua o infraestructura cloud.

## Qué NO es Sprout
- no es un temporizador con marketing
- no es una app cloud que “tolera cortes”
- no es teleoperación agrícola remota
- no es un chatbot para plantas
- no es una plataforma inmensa de agricultura de precisión
- no es un dashboard vestido de impacto

## Qué SÍ es Sprout
- una infraestructura local para cuidado autónomo
- una arquitectura con seguridad física por debajo de la IA
- una red donde la estrategia viaja
- un sistema que sigue siendo útil aunque falte internet
- un prototipo pequeño con visión de escalado creíble
- una forma de distribuir criterio cuando la presencia humana es intermitente

## Arquitectura resumida
- **Rhizome**: nodo autónomo de parcela. Observa, interpreta y ejecuta dentro de límites físicos.
- **Pollen**: nodo itinerante. Lleva contexto, meteo prestada, deltas de política y revisiones de campo.
- **Meristem**: nodo estratégico. Consolida patrones, revisa políticas y emite criterio más duradero.

Frase de arquitectura:

**Rhizome ejecuta, Pollen transporta y revisa, Meristem aprende y reajusta.**

## Qué hace especial a cada nodo
### Rhizome
No es un terminal obediente. Interpreta localmente una política vigente a partir de señales que pueden contradecirse: humedad, imagen, depósito, memoria operativa y meteo disponible.

### Pollen
No es un simple sincronizador. Es un **ferry de inteligencia contextual con caducidad**. Transporta tres cosas: weather packets, policy deltas y contradiction alerts.

### Meristem
No teleopera. Distribuye criterio. Revisa patrones entre parcelas y emite políticas más duraderas.

## Demostrador del MVP
El prototipo será deliberadamente pequeño, pero más rico de lo que parece.

### MVP físico
- un solo host **Rhizome** físico
- dos maceteros que simulan **dos parcelas lógicas**
- dos sensores de humedad, uno por macetero
- cámara
- depósito
- caudalímetro en el MVP
- bomba o sistema de riego controlable
- meteo local asociada a una de las dos parcelas
- la otra parcela sin meteo local

### Nodos del sistema en el MVP
- **Rhizome**: host edge que ejecuta dos identidades lógicas de parcela
- **Pollen**: **Pixel 10 Pro** como nodo itinerante principal del demostrador
- **Meristem**: servicio estratégico con arquitectura objetivo local-first. En el sprint del MVP puede haber un atajo temporal de implementación externo, pero el proyecto debe respirarse como sistema local y no cloud-dependent

## Qué debe demostrar el vídeo
Solo cinco cosas:
1. el sistema funciona offline en la parcela
2. la IA no es adorno y genera una salida estructurada útil
3. existe una capa física de seguridad que valida o bloquea
4. **Pollen** cambia el criterio transportando contexto fresco
5. el sistema sabe cuándo una información ha **caducado** y deja de usarla

## Clímax narrativo del proyecto
La idea que debe quedar en la cabeza de quien vea el proyecto es esta:

**cada parcela puede sobrevivir sola, pero el sistema mejora cuando la estrategia circula.**

Y una segunda idea, muy importante:

**no basta con que el contexto viaje; el sistema debe saber cuándo deja de merecer confianza.**

## Caso fuerte del MVP
El caso fuerte del prototipo es este:
- una parcela tiene meteo local
- otra no
- **Pollen** transporta meteo prestada con TTL
- Rhizome reinterpreta la política con ese contexto nuevo
- en una variante del caso, ese weather packet llega caducado y el sistema decide no usarlo

Eso enseña tres cosas a la vez:
- distribución física de contexto
- prudencia operacional
- inteligencia local bajo incertidumbre

## Límite de alcance del MVP
No intentar demostrar todo el sistema futuro.

### Sí entra
- decisión local de Rhizome sobre dos parcelas lógicas
- uso visible de sensor, cámara, depósito, caudalímetro y política
- un paso de Pollen con contexto nuevo
- un caso explícito de **caducidad** de información
- revisión de Meristem y devolución de política más afinada
- una acción ejecutada o bloqueada con recibo trazable
- conectividad oportunista útil si aparece
- zoom out final hacia red de parcelas y Pollen circulando
- un simulador interno de red para ilustrar 2, 4, 5 u 8 Rhizome

### No entra en el núcleo del MVP
- red de muchos nodos físicos reales
- drones reales en funcionamiento
- fine-tuning
- capa grande de RAG visible
- dashboards complejos
- automatización total de despliegue
- memoria estacional profunda como parte central de la demo

## Principios no negociables
1. **Offline-first real**
2. **La IA propone, la seguridad dispone**
3. **No enviamos órdenes, enviamos políticas**
4. **Toda decisión importante deja trazabilidad**
5. **Pollen transporta deltas, no “todo”**
6. **Toda política o contexto útil tiene caducidad**
7. **El prototipo debe ser filmable y entendible en menos de un minuto**

## Riesgos a vigilar
- convertir Sprout en “otro riego inteligente”
- inflar demasiado el perímetro técnico
- esconder la capa física de seguridad
- hacer que Pollen parezca decorado sin función real
- que Meristem suene a servidor central del que depende todo
- vender como local lo que en el MVP aún sea un atajo temporal externo
- explicar demasiado y enseñar poco en vídeo

## Qué necesita el equipo ahora
- una arquitectura estable y consistente con la v4
- un MVP técnico muy acotado
- contratos de datos mínimos
- una estructura de repo público limpia
- una narrativa coherente para writeup y vídeo
- una lista de compra cerrada y priorizada
- un simulador simple para visualizar escalado y caducidad

## Criterio para decidir cualquier cosa
Si una pieza no mejora uno de estos cinco puntos, probablemente sobra para el MVP:
- claridad visual
- credibilidad técnica
- encaje real con Gemma 4
- impacto humano comprensible
- singularidad de la arquitectura
