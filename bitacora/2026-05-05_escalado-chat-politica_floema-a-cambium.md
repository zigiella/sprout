# Escalado: Transformación de Voz a Política desde el Chat
**De**: Floema
**Para**: Cambium, Meristem
**Fecha**: 2026-05-05

Equipo, 

Bea ha levantado un requerimiento clave para la live demo (Día 20): quiere que **el chat de Pollen sea capaz de interpretar órdenes de voz y transformarlas directamente en una política (PolicyPacket) que se envíe a Rhizome**. 

Ejemplo: El agricultor dice *"Riega 10 minutos menos el sector B"*, y el LLM lo traduce en un JSON válido para que el nodo lo asimile.

Actualmente esto supera la arquitectura implementada en el Chat de Pollen. Para que esto funcione, necesitamos definir:

1. **Prompt Engineering / Structured Output**: El modelo Gemma 4 E4B que corre en el móvil (LiteRT-LM) necesita instrucciones claras y herramientas para devolver un JSON que mapee exactamente con el esquema `PolicyPacket`.
2. **Ciclo de validación**: ¿Confiamos ciegamente en el JSON que escupe el modelo local y lo enviamos al ESP32/Jetson? Pollen necesitaría una capa de parseo seguro.
3. **Contrato de API**: Necesitamos un endpoint en Rhizome (ej. `POST /policy`) para que Pollen empuje la política generada de emergencia. Actualmente Pollen recibe políticas descargándolas de Meristem, no las inyecta en Rhizome directamente desde el chat.

### Opciones para el Hackathon:

- **Opción A (Real)**: Implementar este flujo completo (Prompt estructurado en Pollen -> parseo -> POST a la Jetson). Riesgo alto de alucinaciones en vivo.
- **Opción B (Demo)**: Hardcodear un "Wake Word" o trigger en el Chat. Si la transcripción contiene la palabra "Riega", el chat responde con un texto fijo *"Política generada: reduciendo riego 10 minutos. Enviando a Rhizome..."* y simular el envío.

Avisadme cómo procedemos con esta feature a nivel de arquitectura y si entra para la v0.
