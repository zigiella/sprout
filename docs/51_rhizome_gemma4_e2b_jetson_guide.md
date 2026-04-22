# Guía técnica de desarrollo

## Gemma 4 E2B en Jetson Orin Nano Super (8 GB)

Versión: 2026-04-22

## Objetivo

Esta guía está pensada para una programadora que quiera desarrollar sobre **Gemma 4 E2B** en un **Jetson Orin Nano Super de 8 GB** con una ruta realista, reproducible y relativamente estable.

La conclusión práctica es simple:

- **Ruta recomendada**: `llama.cpp` usando el contenedor de NVIDIA para Jetson y el checkpoint GGUF recomendado para Orin Nano.
- **Ruta avanzada**: `vLLM` si necesitas especialmente la parte de audio o un servidor más cercano a despliegue tipo API.
- **Ruta experimental**: `Ollama`. Se puede instalar en Jetson, pero **hoy no es la opción que yo recomendaría para Gemma 4 E2B en Orin Nano Super 8 GB**.

## Resumen ejecutivo

### Qué sí encaja bien

**Gemma 4 E2B** es, dentro de la familia Gemma 4, el modelo que mejor encaja en **Jetson Orin Nano**. NVIDIA y Jetson AI Lab lo colocan como la opción natural para esta máquina. La familia Gemma 4 está soportada en Jetson mediante **vLLM** y **llama.cpp**, pero la propia guía oficial dice que en **Orin Nano** la ruta sencilla y directa es **llama.cpp** con el checkpoint GGUF adecuado.

### Qué no compraría como promesa fácil

**Ollama** en Jetson funciona como plataforma general y se instala sin drama, pero para **Gemma 4 E2B en Orin Nano 8 GB** hay señales públicas de que **no está fino todavía**: la propia guía de Jetson AI Lab indica que **Gemma 4 no funciona en Orin Nano con Ollama ahora mismo**, y en Ollama hay un issue abierto donde el runner falla en Orin Nano y un colaborador apunta a que el modelo va al límite de memoria y que el runner **no tiene mmap loading**, mientras que con `llama.cpp` sí se puede cargar justo al límite.

## Arquitectura recomendada

### Opción A. Recomendada

**Jetson Orin Nano Super 8 GB + JetPack 6.x + NVMe SSD + swap + MAXN SUPER + llama.cpp container + GGUF Q4_K_S**

Esto es lo más razonable si quieres:

- arrancar rápido
- no pelearte con RAM de más
- tener un endpoint local y una UI mínima en `localhost:8080`
- desarrollar encima con el menor número posible de variables rotas

### Opción B. Avanzada

**Jetson Orin Nano Super 8 GB + vLLM container + modelo Hugging Face E2B**

Úsala si necesitas:

- aproximarte más a un servicio tipo API
- reasoning y tool calling desde el arranque
- la parte de **audio**, porque la guía oficial indica un **problema actual de audio con E2B bajo llama.cpp en Orin**

### Opción C. Experimental

**Jetson Orin Nano Super 8 GB + Ollama**

Úsala solo si quieres probar, documentar o comparar. Hoy no la tomaría como baseline de desarrollo para Gemma 4 E2B en esta placa.

## Lo que se sabe del modelo

Gemma 4 E2B es el modelo pequeño de Gemma 4 orientado a edge. Jetson AI Lab resume sus características principales así:

- **2.3B parámetros efectivos**
- **5.1B contando embeddings**
- **128K de contexto**
- entrada **texto, imagen y audio**
- **function calling** nativo
- soporte de **ASR** y traducción hablada en clips de hasta **30 segundos**

En Jetson, esto abre casos de uso interesantes para:

- asistentes locales
- inspección visual
- agentes ligeros con herramientas
- robots y smart machines
- OCR y razonamiento multimodal

## Requisitos recomendados

### Hardware

- Jetson Orin Nano Super Developer Kit, **8 GB RAM**
- microSD de **64 GB o más** para el arranque inicial
- **NVMe SSD** muy recomendable para modelos, caches y swap
- refrigeración y alimentación correctas

### Software base

- **JetPack 6.x / L4T r36.x**
- Docker funcional
- red operativa para descargar contenedores y pesos
- acceso SSH si vas en modo headless

## Preparación del sistema

### 1. Deja la placa en un estado sano

La guía oficial de Jetson AI Lab para Orin Nano pasa por:

- firmware actualizado
- JetPack 6.2.x
- modo de potencia **MAXN SUPER**

En JetPack 6.2 el modo por defecto es **25 W**, y la guía recomienda pasar a **MAXN SUPER** para desbloquear el máximo rendimiento.

### 2. Usa NVMe SSD

Jetson AI Lab recomienda SSD NVMe tanto para el sistema de contenedores como para los pesos y caches. En esta clase de flujos no es un capricho. Es la diferencia entre una máquina soportable y una máquina torpe.

### 3. Optimiza RAM

En un Orin Nano de 8 GB la memoria es el cuello de botella más vulgar y más decisivo. Jetson AI Lab recomienda varias medidas.

#### Desactivar el escritorio temporalmente

```bash
sudo init 3
# volver al escritorio cuando lo necesites
sudo init 5
```

#### Desactivar el escritorio al arranque si vas por SSH

```bash
sudo systemctl set-default multi-user.target
# para reactivar el entorno gráfico al arranque
sudo systemctl set-default graphical.target
```

#### Desactivar servicios no necesarios

```bash
sudo systemctl disable nvargus-daemon.service
```

#### Crear swap en SSD

```bash
sudo systemctl disable nvzramconfig
sudo fallocate -l 16G /ssd/16GB.swap
sudo mkswap /ssd/16GB.swap
sudo swapon /ssd/16GB.swap
```

Añade esto al final de `/etc/fstab`:

```fstab
/ssd/16GB.swap  none  swap  sw 0 0
```

## Ruta recomendada: Gemma 4 E2B con llama.cpp

La guía oficial de Gemma 4 on Jetson es muy clara para **Orin Nano**: **E2B es una gran opción** y **llama.cpp es la ruta directa**.

### Comando recomendado

```bash
sudo docker run -it --rm --pull always --runtime=nvidia --network host \
  -v $HOME/.cache/huggingface:/root/.cache/huggingface \
  ghcr.io/nvidia-ai-iot/llama_cpp:latest-jetson-orin \
  llama-server -hf unsloth/gemma-4-E2B-it-GGUF:Q4_K_S
```

### Qué hace este comando

- usa el contenedor oficial de `llama.cpp` para Jetson Orin
- descarga el checkpoint **GGUF** recomendado para E2B en Orin Nano
- levanta `llama-server`
- expone una UI básica en:

```text
http://localhost:8080
```

### Cuándo usar esta ruta

Úsala como **baseline de desarrollo** si tu prioridad es:

- texto
- pruebas rápidas
- consumo de memoria razonable
- mínima complejidad operativa

### Cosas que debes saber

- E2B y E4B soportan audio a nivel de familia, pero la guía de Jetson AI Lab marca un **problema actual de audio con E2B en llama.cpp sobre Orin**.
- Si el audio es parte central de tu producto, mira la ruta vLLM.

## Ruta avanzada: Gemma 4 E2B con vLLM

La misma guía oficial indica que **vLLM** suele ofrecer **mejor rendimiento de serving** que `llama.cpp`, y es la opción que Jetson AI Lab recomienda cuando quieres algo más parecido a despliegue serio.

### Cuándo compensa

- si vas a construir un servicio local más estable para tu aplicación
- si quieres **reasoning** y **tool calling** desde el arranque
- si quieres mantener abierta la posibilidad de usar la parte de audio de E2B

### Comando base

```bash
sudo docker run -it --rm --pull always --runtime=nvidia --network host \
  -v $HOME/.cache/huggingface:/root/.cache/huggingface \
  ghcr.io/nvidia-ai-iot/vllm:gemma4-jetson-orin \
  vllm serve google/gemma-4-E2B-it \
    --enable-auto-tool-choice \
    --reasoning-parser gemma4 \
    --tool-call-parser gemma4
```

### Activar thinking en la petición

Aunque arranques el servidor con los flags de Gemma 4, la guía oficial aclara que el reasoning **no se activa por defecto** en cada request. Debes pasar `enable_thinking=true` dentro de `chat_template_kwargs`.

Ejemplo mínimo:

```bash
curl -sN http://127.0.0.1:8000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "google/gemma-4-E2B-it",
    "messages": [{"role": "user", "content": "hi"}],
    "chat_template_kwargs": {"enable_thinking": true},
    "stream": true
  }'
```

### Advertencias

- Si no haces streaming, la propia guía advierte que puede haber casos donde el texto de pensamiento se mezcle con la respuesta final.
- No mezcles formatos a lo loco: checkpoints de Hugging Face para `vLLM`, checkpoints **GGUF** para `llama.cpp`.

## Ollama: estado real y recomendación

## ¿Se puede instalar Ollama en Jetson?

Sí.

Jetson AI Lab dice que el instalador oficial soporta Jetson:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

También hay ruta Docker en Jetson, y la documentación oficial de Ollama avisa que en sistemas JetPack debes pasar `JETSON_JETPACK=5` o `JETSON_JETPACK=6` al contenedor oficial porque Ollama no puede detectar automáticamente la versión de JetPack.

## ¿Lo recomiendo para Gemma 4 E2B en Orin Nano Super?

**No como camino principal.**

### Por qué no

Hay tres señales demasiado claras:

1. **Jetson AI Lab** afirma directamente que **Gemma 4 no funciona en Orin Nano con Ollama ahora mismo**.
2. En **Ollama issue #15398**, un usuario reporta que `gemma4:e2b` falla en Jetson Orin Nano y un colaborador de Ollama dice que el runner va al límite de memoria y que **no tiene mmap loading**, mientras que con `llama.cpp` sí se puede cargar justo al borde.
3. En el foro de NVIDIA aparece gente intentando usar `gemma4:e2b` con Ollama nativo en Orin Nano y topándose con errores o caídas.

### Qué haría yo con Ollama

- lo dejaría como **anexo experimental**
- lo usaría para comparar experiencia o para otros modelos menos al límite
- no lo pondría en el camino crítico de un proyecto que tenga fechas

### Si aun así quieres probarlo

#### Instalación nativa

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### Prueba tentativa

```bash
OLLAMA_DEBUG=1 ollama run gemma4:e2b
```

#### Expectativa honesta

- puede fallar con `EOF` o `500 Internal Server Error`
- puede cargar más memoria de la esperada
- puede terminar moviendo más trabajo a CPU del deseable

## Flujo de desarrollo recomendado

## Fase 1. Baseline estable

Objetivo: verificar que la máquina queda lista y el modelo responde.

1. JetPack 6.x en orden
2. MAXN SUPER activado
3. SSD montado
4. swap activa
5. escritorio desactivado si vas por SSH
6. arranque con `llama.cpp`
7. prueba manual desde `http://localhost:8080`

Entregable: una sesión reproducible donde E2B arranca siempre.

## Fase 2. Integración de aplicación

Una vez `llama.cpp` responda de forma consistente, construye tu aplicación cliente encima. En esta fase yo mantendría el foco en:

- prompts
- plantillas de sistema
- validación de latencia
- límites de contexto útiles
- consumo térmico y estabilidad a sesiones largas

## Fase 3. Solo si hace falta, pasar a vLLM

Migra a `vLLM` si necesitas una de estas cosas:

- razonamiento controlado con `enable_thinking`
- tool calling desde el servidor
- mejor ruta para audio
- serving más serio

Haz este cambio **después** de tener un baseline estable, no antes. El error habitual es abrir demasiados frentes a la vez y terminar culpando al modelo de un problema de infraestructura.

## Trucos prácticos

### Limpia caché de página si vienes de un arranque fallido

```bash
sudo sysctl -w vm.drop_caches=3
```

La guía de Jetson AI Lab lo recomienda al reintentar modelos grandes o cuando una carga anterior ha dejado memoria retenida.

### Mata procesos previos antes de volver a lanzar

Asegúrate de que no quede un contenedor o servidor anterior ocupando memoria. En un Orin Nano, la memoria “fantasma” te puede arruinar una prueba y hacerte creer que el comando correcto está mal.

### No mezcles checkpoints

- `vLLM` → modelos Hugging Face listados por Jetson AI Lab
- `llama.cpp` → checkpoints **GGUF**

### No conviertas Ollama en religión

Ollama es cómodo. Eso no lo vuelve adecuado para cualquier combinación de placa, memoria y modelo. En esta máquina y con este modelo, hoy parece ser más una fuente de ruido que una ventaja.

## Casos de uso razonables en esta placa

Con Gemma 4 E2B en Orin Nano Super yo apuntaría a:

- asistentes locales de texto
- inspección visual ligera
- OCR o análisis de imágenes con prompts cortos
- agentes simples con herramientas
- prototipos de robótica con inferencia local

No lo trataría como un servidor universal para cargas pesadas o sesiones enormes. La placa es muy capaz para su tamaño, pero sigue siendo una placa de 8 GB, no un juguete mágico que obedece al marketing.

## Matriz de decisión

| Escenario | Ruta recomendada |
|---|---|
| Quiero que funcione hoy y con el menor dolor posible | `llama.cpp` |
| Quiero texto + audio + tool calling y estoy dispuesto a afinar más | `vLLM` |
| Quiero la experiencia más simple tipo Ollama y me da igual probar algo verde | `Ollama` |
| Quiero producción ligera y repetible en Orin Nano Super 8 GB | `llama.cpp`, y luego evaluar `vLLM` |

## Checklist de validación

### Validación de plataforma

- [ ] JetPack 6.x instalado
- [ ] Modo MAXN SUPER activado
- [ ] SSD NVMe montado
- [ ] Docker operativo
- [ ] swap activa
- [ ] GUI desactivada si aplica

### Validación de modelo

- [ ] El contenedor descarga el modelo sin errores
- [ ] `llama-server` arranca
- [ ] `localhost:8080` responde
- [ ] Se puede completar al menos una conversación corta
- [ ] No aparecen OOM ni bloqueos repetidos

### Validación de integración

- [ ] Tu cliente puede enviar prompts repetidamente
- [ ] La latencia es aceptable para el caso de uso
- [ ] La placa no entra en inestabilidad térmica
- [ ] El sistema se recupera bien tras reinicios y relanzamientos

## Conclusión

Para **Gemma 4 E2B en Jetson Orin Nano Super**, mi recomendación es clara:

1. **Empieza por `llama.cpp`** con el comando oficial de Jetson AI Lab.
2. **Prepara bien la máquina**: JetPack 6.x, MAXN SUPER, SSD, swap y RAM optimizada.
3. **Usa `vLLM`** si de verdad necesitas audio o una capa de serving más formal.
4. **No tomes Ollama como base del proyecto** mientras siga el estado actual de memoria y compatibilidad en Orin Nano para `gemma4:e2b`.

## Fuentes

- Jetson AI Lab, *Gemma 4 on Jetson*  
  https://www.jetson-ai-lab.com/tutorials/gemma4-on-jetson/

- Jetson AI Lab, *Gemma 4 E2B model page*  
  https://www.jetson-ai-lab.com/models/gemma4-e2b/

- Jetson AI Lab, *Introduction to GenAI on Jetson: How to Run LLMs and VLMs*  
  https://www.jetson-ai-lab.com/tutorials/genai-on-jetson-llms-vlms/

- Jetson AI Lab, *Ollama on Jetson*  
  https://www.jetson-ai-lab.com/tutorials/ollama/

- Jetson AI Lab, *Initial Setup Guide for Jetson Orin Nano Developer Kit*  
  https://www.jetson-ai-lab.com/tutorials/initial-setup-jetson-orin-nano/

- Jetson AI Lab, *RAM Optimization*  
  https://www.jetson-ai-lab.com/tutorials/ram-optimization/

- Jetson AI Lab, *SSD + Docker Setup*  
  https://www.jetson-ai-lab.com/tutorials/ssd-docker-setup/

- NVIDIA Developer Blog, *Bringing AI Closer to the Edge and On-Device with Gemma 4*  
  https://developer.nvidia.com/blog/bringing-ai-closer-to-the-edge-and-on-device-with-gemma-4/

- NVIDIA Developer Forums, *No luck with Gemma 4 on Jetson Nano Super*  
  https://forums.developer.nvidia.com/t/no-luck-with-gemma-4-on-jetson-nano-super/365620

- Ollama issue #15398, *gemma4 e2B does not work on Jetson Orin Nano*  
  https://github.com/ollama/ollama/issues/15398

- Ollama docs, *Docker*  
  https://docs.ollama.com/docker

- Ollama docs, *Linux install*  
  https://docs.ollama.com/linux
