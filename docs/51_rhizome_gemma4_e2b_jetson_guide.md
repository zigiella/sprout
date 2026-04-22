# Guía técnica de desarrollo

## Gemma 4 E2B + llama.cpp en Jetson Orin Nano Super

Versión orientada a desarrollo e integración.

---

## 1. Objetivo

Esta guía define una base técnica para ejecutar **Gemma 4 E2B** en un **Jetson Orin Nano Super** usando **llama.cpp** como runtime principal.

La decisión de arquitectura aquí es deliberada:

- **Modelo**: Gemma 4 E2B
- **Hardware**: Jetson Orin Nano Super, normalmente con **8 GB de RAM**
- **Runtime recomendado**: **llama.cpp**
- **Serving**: `llama-server`
- **Ruta no recomendada como baseline en este hardware**: Ollama

Jetson AI Lab indica que en **Orin Nano** el modelo que mejor encaja de la familia Gemma 4 es **E2B**, y que para ese caso **llama.cpp** es la ruta más directa. La misma guía señala que, en **Orin Nano**, **Gemma 4 no funciona con Ollama ahora mismo**. [Fuente: Jetson AI Lab, “Gemma 4 on Jetson”]

---

## 2. Qué es Gemma 4 E2B y por qué tiene sentido aquí

Según la tarjeta oficial de modelo de Google, Gemma 4 es una familia abierta multimodal con cuatro tamaños: **E2B, E4B, 26B A4B y 31B**. Los modelos pequeños son los que añaden soporte de audio, mientras que la familia completa admite texto e imagen y genera texto como salida. [Fuente: Google AI, “Gemma 4 model card”]

Jetson AI Lab describe **Gemma 4 E2B** como la variante más pequeña de la familia y la posiciona para:

- asistentes offline
- copilotos de robótica
- OCR ligero y document QA
- pipelines agentic locales con tool calling y huella reducida

Además, Jetson AI Lab resume E2B como un modelo configurado para ejecutarse en Jetson con **vLLM** y **llama.cpp**, y remite a la tarjeta oficial de Google para sus capacidades base: contexto largo, multimodalidad y function calling. [Fuente: Jetson AI Lab, “Gemma 4 E2B”]

### Lectura práctica

En un **Jetson Orin Nano Super**, la elección buena no es la más glamourosa, sino la que permite:

- arrancar siempre
- no vivir al borde del OOM
- servir localmente con una latencia razonable
- conservar espacio para integración con cámara, sensores, ASR, TTS u otra lógica de aplicación

Por eso **E2B** es el punto de partida correcto.

---

## 3. Arquitectura recomendada

### Baseline de referencia

- **JetPack**: JP 6.x sobre L4T r36.x
- **Almacenamiento**: NVMe SSD recomendado para modelos y cachés
- **Contenedor**: `ghcr.io/nvidia-ai-iot/llama_cpp:latest-jetson-orin`
- **Modelo GGUF**: `unsloth/gemma-4-E2B-it-GGUF:Q4_K_S`
- **Servidor**: `llama-server`
- **UI local**: `http://localhost:8080`

Jetson AI Lab deja este flujo expresamente documentado para **Orin Nano**. [Fuente: Jetson AI Lab, “Gemma 4 on Jetson”]

### Por qué `llama.cpp`

Jetson AI Lab dice que, en términos generales, **vLLM** suele rendir mejor como motor de serving, mientras que **llama.cpp** sigue siendo una buena opción si quieres la ruta **GGUF**. En **Orin Nano**, sin embargo, el tutorial baja a tierra y recomienda directamente **E2B + llama.cpp** como camino más sencillo. [Fuente: Jetson AI Lab, “Gemma 4 on Jetson”]

### Por qué no tomar Ollama como baseline aquí

La misma guía oficial de Jetson AI Lab dice literalmente que **Gemma 4 no funciona en Orin Nano con Ollama ahora mismo**. Eso no significa que Ollama sea inútil en Jetson. Significa que, para **este modelo y este hardware concretos**, no deberías planificar el proyecto alrededor de esa ruta. [Fuente: Jetson AI Lab, “Gemma 4 on Jetson”]

---

## 4. Casos de uso razonables en este hardware

Con **Gemma 4 E2B + llama.cpp** en Orin Nano Super, los casos más sensatos son:

### Asistentes locales y edge copilots

- chat local
- consulta técnica embebida
- asistentes de campo
- controladores de dispositivos con lenguaje natural

### Visión ligera y multimodalidad pragmática

- OCR ligero
- document QA simple
- comprensión básica de imágenes
- copilotos de cámara para inspección guiada

### Robótica y sistemas físicos

- agente local que combine texto, imagen y reglas
- decisiones asistidas en robots pequeños
- interfaces por voz si la arquitectura externa resuelve STT/TTS

### Tool calling local

Gemma 4 soporta function calling y razonamiento configurable a nivel de familia. En Jetson AI Lab también se destaca el uso de reasoning y tool calling con Gemma 4, sobre todo bajo vLLM. [Fuente: Google AI, “Gemma 4 model card”; Jetson AI Lab, “Gemma 4 on Jetson”]

---

## 5. Requisitos previos

### Hardware

- Jetson Orin Nano Super
- fuente oficial o equivalente adecuada
- microSD si el sistema está sobre SD
- **NVMe SSD muy recomendable**
- conectividad de red
- espacio suficiente para contenedores y modelos

Jetson AI Lab recomienda de forma explícita **NVMe SSD** tanto en la guía inicial como en la guía de SSD + Docker, porque los contenedores y modelos ocupan bastante y el flujo GenAI se vuelve torpe si todo vive en almacenamiento limitado. [Fuente: Jetson AI Lab, “Initial Setup Guide for Jetson Orin Nano Developer Kit”; “SSD + Docker Setup”]

### Software base

- JetPack 6.x
- Docker operativo
- runtime NVIDIA disponible para contenedores
- acceso al terminal por monitor o SSH

Jetson AI Lab documenta JetPack 6.2 como base de preparación y coloca JP 6 / L4T r36.x como requisito para Orin en la guía de Gemma 4 on Jetson. [Fuente: Jetson AI Lab, “Initial Setup Guide for Jetson Orin Nano Developer Kit”; “Gemma 4 on Jetson”]

---

## 6. Preparación de la placa

### 6.1. Instalar o actualizar JetPack

Jetson AI Lab describe el flujo completo para dejar un Orin Nano listo para JP 6.2, incluyendo comprobación de firmware UEFI, actualización de QSPI si hace falta y arranque posterior con JetPack 6.x. [Fuente: Jetson AI Lab, “Initial Setup Guide for Jetson Orin Nano Developer Kit”]

### 6.2. Habilitar modo de máximo rendimiento

La guía inicial de Jetson AI Lab incluye el paso de desbloquear el modo **Super performance**, y señala que las actualizaciones recientes de software mejoran notablemente el rendimiento del Orin Nano. [Fuente: Jetson AI Lab, “Initial Setup Guide for Jetson Orin Nano Developer Kit”]

### 6.3. Montar SSD NVMe y mover Docker

La guía **SSD + Docker Setup** explica cómo:

- instalar físicamente el NVMe
- verificarlo
- formatearlo y montarlo
- reubicar el almacenamiento de Docker

Esto no es adorno. En GenAI local, si el modelo, las capas del contenedor y la caché viven en almacenamiento estrecho, el sistema se degrada enseguida. [Fuente: Jetson AI Lab, “SSD + Docker Setup”]

---

## 7. Comando de arranque recomendado

Este es el comando oficial que Jetson AI Lab publica para **Orin Nano + Gemma 4 E2B + llama.cpp**:

```bash
sudo docker run -it --rm --pull always --runtime=nvidia --network host \
  -v $HOME/.cache/huggingface:/root/.cache/huggingface \
  ghcr.io/nvidia-ai-iot/llama_cpp:latest-jetson-orin \
  llama-server -hf unsloth/gemma-4-E2B-it-GGUF:Q4_K_S
```

Después, la interfaz queda disponible en:

```text
http://localhost:8080
```

[Fuente: Jetson AI Lab, “Gemma 4 on Jetson”]

---

## 8. Qué está haciendo realmente este comando

### Contenedor

Usa el contenedor oficial de NVIDIA AI IoT para **llama.cpp sobre Jetson Orin**.

### Caché de Hugging Face

Monta `~/.cache/huggingface` del host para evitar descargas redundantes y facilitar reinicios.

### Modelo

Descarga y sirve una versión **GGUF cuantizada** del modelo instruction-tuned de Gemma 4 E2B.

### Cuantización

La guía oficial para Orin Nano usa **`Q4_K_S`**. En este tipo de dispositivo, la cuantización no es una opción cosmética. Es la diferencia entre algo desplegable y algo ornamental.

---

## 9. Flujo de verificación

### 9.1. Verificar Docker

```bash
docker --version
```

### 9.2. Verificar que NVIDIA runtime está activo

```bash
docker info | grep -i runtime
```

### 9.3. Lanzar el servidor

Usar el comando anterior.

### 9.4. Abrir la UI local

Desde el navegador del propio Jetson o desde otro equipo en la red:

```text
http://IP_DEL_JETSON:8080
```

### 9.5. Probar prompts básicos

Ejemplos:

- “Resume este texto en 5 líneas.”
- “Extrae tareas y riesgos de esta nota.”
- “Explícame este error de sistema.”

---

## 10. Diseño de integración recomendado

### Opción 1. Integración mínima

Usar `llama-server` como servicio local y consumirlo desde otra aplicación mediante HTTP.

Adecuado para:

- apps Python externas
- Node.js
- dashboards locales
- pruebas rápidas de copilotos

### Opción 2. Servicio embebido en sistema edge

Mantener `llama-server` como proceso local persistente y envolverlo con una capa de negocio que:

- reciba datos de sensores
- prepare prompts
- ejecute funciones locales
- gestione contexto y memoria de sesión

### Opción 3. Multimodalidad acotada

Aunque la familia E2B admite audio e imagen, la propia guía de Jetson AI Lab avisa de que **hay un problema actual con el audio de E2B bajo llama.cpp en Orin**. Si el audio es importante, recomiendan usar los modelos pequeños de Gemma 4 a través de **vLLM**. [Fuente: Jetson AI Lab, “Gemma 4 on Jetson”]

Eso deja una decisión nítida:

- si tu primera meta es **texto y serving local estable**, usa `llama.cpp`
- si tu primera meta es **audio serio**, no diseñes sobre `llama.cpp` sin validar antes esa parte

---

## 11. Riesgos y límites reales

### 11.1. Audio en llama.cpp

Jetson AI Lab documenta explícitamente una incidencia actual con **audio en E2B bajo llama.cpp para Orin**. Eso invalida cualquier guía que te prometiera audio plug-and-play como baseline de proyecto en esta combinación. [Fuente: Jetson AI Lab, “Gemma 4 on Jetson”]

### 11.2. Ollama

No lo tomes como ruta de referencia para Gemma 4 E2B en Orin Nano. La propia guía oficial lo desaconseja de facto al decir que **no funciona ahora mismo**. [Fuente: Jetson AI Lab, “Gemma 4 on Jetson”]

### 11.3. Contexto y expectativas

Google documenta hasta **128K de contexto** para E2B. Eso no significa que debas comportarte como si cada caso de uso fuese a tolerar prompts gigantes sin coste. En Jetson pequeño, el presupuesto térmico, la memoria y la latencia siguen mandando. [Fuente: Google AI, “Gemma 4 model card”; Jetson AI Lab, “Gemma 4 E2B”]

### 11.4. No confundir servir con medir

Jetson AI Lab tiene una guía específica de benchmarking donde deja claro que medir rendimiento implica fijarse en:

- **TTFT**
- throughput
- latencia

Servir el modelo no equivale a conocer su comportamiento real bajo carga. [Fuente: Jetson AI Lab, “GenAI Benchmarking: LLMs and VLMs on Jetson”]

---

## 12. Checklist técnica para una programadora

### Infraestructura

- [ ] JetPack 6.x instalado
- [ ] firmware/UEFI y QSPI actualizados si hacía falta
- [ ] modo Super performance habilitado
- [ ] SSD NVMe instalado y montado
- [ ] Docker usando almacenamiento en SSD
- [ ] acceso por SSH confirmado

### Runtime

- [ ] contenedor `llama_cpp:latest-jetson-orin` descargado
- [ ] caché de Hugging Face persistida
- [ ] comando de `llama-server` probado
- [ ] UI local accesible en el puerto 8080

### Aplicación

- [ ] prompts base de prueba definidos
- [ ] límite de contexto operativo fijado por caso de uso
- [ ] timeout y reintentos definidos
- [ ] logging de inferencia activado
- [ ] estrategia de fallback definida si el servidor no responde

### Producto

- [ ] caso de uso principal acotado
- [ ] texto como baseline
- [ ] audio tratado como experimental salvo validación propia
- [ ] Ollama descartado como baseline en esta placa

---

## 13. Sugerencia de roadmap

### Fase 1. Bring-up

Objetivo: arrancar modelo, responder prompts y estabilizar servicio.

### Fase 2. Integración

Objetivo: conectar `llama-server` con la aplicación, herramientas y fuentes de datos.

### Fase 3. Medición

Objetivo: benchmark básico con prompts representativos y sesiones sostenidas.

### Fase 4. Endurecimiento

Objetivo: gestión de errores, watchdog, reinicios, control térmico, logging y límites de contexto.

### Fase 5. Extensión

Objetivo: decidir si merece añadir visión, audio, tool calling o migrar parte del stack a `vLLM`.

---

## 14. Recomendación final

Si lo que quieres es una base **que funcione** en **Jetson Orin Nano Super**, la combinación correcta hoy es:

- **Gemma 4 E2B**
- **llama.cpp**
- **GGUF cuantizado**
- **NVMe SSD**
- **JetPack 6.x**

Eso es coherente con la guía oficial de Jetson AI Lab y con la posición de Google sobre la familia Gemma 4 como modelos multimodales abiertos desplegables desde edge hasta sistemas mayores. [Fuente: Jetson AI Lab, “Gemma 4 on Jetson”; Google AI, “Gemma 4 model card”]

La versión honesta de la historia es esta: en este hardware, **la elegancia no está en perseguir la variante más grande ni el runtime más cómodo, sino en elegir el camino que no te rompa la placa ni la paciencia**.

---

## 15. Fuentes

1. Jetson AI Lab. **Gemma 4 on Jetson**. https://www.jetson-ai-lab.com/tutorials/gemma4-on-jetson/
2. Jetson AI Lab. **Gemma 4 E2B**. https://www.jetson-ai-lab.com/models/gemma4-e2b/
3. Jetson AI Lab. **Initial Setup Guide for Jetson Orin Nano Developer Kit**. https://www.jetson-ai-lab.com/tutorials/initial-setup-jetson-orin-nano/
4. Jetson AI Lab. **SSD + Docker Setup**. https://www.jetson-ai-lab.com/tutorials/ssd-docker-setup/
5. Jetson AI Lab. **GenAI Benchmarking: LLMs and VLMs on Jetson**. https://www.jetson-ai-lab.com/tutorials/genai-benchmarking/
6. Google AI for Developers. **Gemma 4 model card**. https://ai.google.dev/gemma/docs/core/model_card_4
