** Apuntes sobre cómo activar Thinking en Gemma 4 E4B con LiteRT-LM**. 

La idea central es esta:

**en LiteRT-LM, thinking no aparece como un switch bonito y universal tipo `think=True` en la API Python**. El runtime sí está preparado para ello, pero lo articula mediante **prompt templates, `extra_context` y canales de salida**. Google documenta Gemma 4 E4B como modelo soportado en LiteRT-LM, y la propia base de LiteRT-LM contempla “thinking” como canal separado y como variable inyectable en plantilla. ([developers.googleblog.com][1])

## Qué sí existe hoy

Gemma 4 incluye capacidades de thinking a nivel de familia, pero la guía oficial de Google para “Thinking mode in Gemma” se apoya en **Transformers**, no en LiteRT-LM. En paralelo, LiteRT-LM ya soporta Gemma 4 en edge, dispone de API de conversación, tool use, multimodalidad y plantillas de prompt, y su configuración interna contempla canales separados como uno de *thinking*. Esa combinación es la pista importante: **LiteRT-LM no inventa thinking por su cuenta, lo expone a través del template y del sistema de channels**. ([Google AI for Developers][2])

## Qué modelo usar

Para Gemma 4 E4B en LiteRT-LM, el paquete comunitario oficial es:

`litert-community/gemma-4-E4B-it-litert-lm`

Ese paquete incluye el archivo `gemma-4-E4B-it.litertlm`, con un tamaño publicado de **3.65 GB**, pensado para Android, iOS, desktop, IoT y web. El mismo model card indica soporte de hasta **32k de contexto** en esta conversión LiteRT-LM. ([huggingface.co][3])

## La pieza clave que casi nadie explica bien

En **Kotlin**, la documentación de LiteRT-LM ya enseña explícitamente este patrón:

* pasar `enable_thinking = true` en `extraContext`
* usar variables del template como `{% if enable_thinking %}`
* separar salida en canales

Además, la configuración de conversación define `channels` como partes de la salida separadas de la respuesta principal, con el ejemplo literal de un canal de *thinking*. Y el motor de plantillas declara que `extra_context` sirve, entre otras cosas, para **habilitar thinking mode**. ([GitHub][4])

Eso significa que, aunque la página Python de LiteRT-LM todavía no traiga un ejemplo específico de thinking para Gemma 4 E4B, **la API Python sí expone `extra_context` y filtrado del contenido de canal en la KV cache**, así que el patrón correcto en Python es análogo al de Kotlin. ([GitHub][5])

## Patrón mental correcto

No pienses “¿dónde está el flag de thinking en LiteRT-LM?”.
Piensa esto:

1. **el modelo/template debe saber interpretar `enable_thinking`**
2. **la conversación debe poder recibir `extra_context`**
3. **si quieres separar razonamiento de respuesta, debes definir o heredar `channels`**
4. **conviene filtrar ese canal fuera de la KV cache para no reinyectar su basura interna en turnos siguientes** ([GitHub][6])

Eso último importa más de lo que parece. La gente mete thinking en producción y luego se extraña de que el modelo se vuelva viscoso, reiterativo o innecesariamente largo. Normal: le has hecho rumiar sus propias tripas.

## Camino mínimo con CLI

La CLI oficial de LiteRT-LM se instala con `uv` o `pip` y puede descargar modelos desde Hugging Face con `--from-huggingface-repo`. La documentación pone el ejemplo con E2B, pero el mecanismo es genérico y el repositorio E4B existe con su `.litertlm`. ([Google AI for Developers][7])

```bash
uv tool install litert-lm
```

o

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install litert-lm
```

La propia CLI está documentada para Linux, macOS, Windows vía WSL y Raspberry Pi. ([Google AI for Developers][7])

### Ejecución base con E4B

```bash
litert-lm run \
  --from-huggingface-repo=litert-community/gemma-4-E4B-it-litert-lm \
  gemma-4-E4B-it.litertlm \
  --prompt="Explica la diferencia entre RAG y fine-tuning"
```

La documentación enseña exactamente esta forma de uso con E2B; aquí solo se sustituye por el repo y el fichero E4B que sí están publicados en Hugging Face. ([Google AI for Developers][7])

## Activar thinking con CLI usando preset

La vía más limpia hoy, si quieres control real, es usar un `preset.py` y pasar **`extra_context`**. La CLI del repo crea conversaciones con `extra_context` y se lo pasa al motor de plantillas. ([GitHub][8])

### `preset.py`

```python
system_instruction = "Eres un asistente técnico. Piensa antes de responder."

tools = []

messages = [
    {
        "role": "system",
        "content": [{"type": "text", "text": system_instruction}],
    }
]

extra_context = {
    "enable_thinking": True
}
```

### Ejecutar

```bash
litert-lm run \
  --from-huggingface-repo=litert-community/gemma-4-E4B-it-litert-lm \
  gemma-4-E4B-it.litertlm \
  --preset=preset.py
```

Aquí hay un matiz delicado: **esto presupone que el prompt template del modelo usa `enable_thinking`**. En Kotlin, la documentación oficial muestra precisamente ese nombre de variable, y el motor de plantillas de LiteRT-LM está diseñado para este tipo de extras. En Python, no he encontrado una página oficial que lo ejemplifique para Gemma 4 E4B con ese snippet exacto, así que te lo doy como patrón sólidamente soportado por la arquitectura, no como copia literal de la página Python. ([GitHub][4])

## Activar thinking con la API Python

La API Python oficial de LiteRT-LM funciona en Linux y macOS, y hoy ya declara soporte para GPU, multimodalidad y tool use. También expone conversación, streaming y `extra_context`. ([Google AI for Developers][9])

### Ejemplo base

```python
import litert_lm

litert_lm.set_min_log_severity(litert_lm.LogSeverity.ERROR)

model_path = "gemma-4-E4B-it.litertlm"

with litert_lm.Engine(
    model_path,
    backend=litert_lm.Backend.GPU,   # o CPU
) as engine:
    with engine.create_conversation(
        messages=[
            {
                "role": "system",
                "content": [
                    {"type": "text", "text": "Eres un asistente técnico. Razona antes de responder."}
                ],
            }
        ],
        extra_context={
            "enable_thinking": True
        },
        filter_channel_content_from_kv_cache=True,
    ) as conversation:
        response = conversation.send_message(
            "Diseña una arquitectura edge para Gemma 4 E4B con tool use local."
        )
        print(response)
```

### Streaming

```python
import litert_lm

with litert_lm.Engine("gemma-4-E4B-it.litertlm") as engine:
    with engine.create_conversation(
        extra_context={"enable_thinking": True},
        filter_channel_content_from_kv_cache=True,
    ) as conversation:
        for chunk in conversation.send_message_async(
            "Analiza ventajas y riesgos de usar thinking on-device."
        ):
            print(chunk)
```

La parte documentada de forma explícita aquí es:

* `Engine(...)`
* `create_conversation(...)`
* `send_message(...)`
* `send_message_async(...)`
* `extra_context`
* `filter_channel_content_from_kv_cache` como mecanismo para no persistir thinking/reasoning en la KV cache. ([Google AI for Developers][9])

## Cómo separar thinking de la respuesta final

LiteRT-LM está preparado para canales. En Kotlin, `Channel` se define con `channelName`, `start` y `end`, y el contenido se escribe en `Message.channels`. La configuración de conversación explica que esos canales son salidas separadas como un canal de thinking. ([GitHub][10])

La consecuencia práctica es esta:

* si el metadata/template del modelo ya trae el canal configurado por defecto, puedes heredar esa configuración
* si no, necesitas definir el canal de forma explícita en la capa que uses
* la respuesta final debería quedar en `content`
* el razonamiento separado debería caer en `channels["thinking"]` o equivalente, según binding y metadata del modelo. ([GitHub][6])

Aquí es donde muchos ejemplos de internet hacen teatro. Enseñan thinking, pero no te cuentan si sale mezclado en texto plano, si va a un canal estructurado o si termina contaminando el historial. Y eso cambia por completo la robustez del sistema.

## Qué haría yo en un MVP serio

Usaría este criterio:

### Para prototipado rápido

CLI + `preset.py` + `extra_context={"enable_thinking": True}`.
Te deja validar si el template del modelo responde bien al thinking sin escribir demasiada infraestructura. ([GitHub][8])

### Para app real

API Python o Kotlin con:

* backend GPU cuando exista soporte estable en tu plataforma
* `extra_context={"enable_thinking": True}`
* `filter_channel_content_from_kv_cache=True`
* streaming
* captura explícita de channels si tu binding lo expone bien ([Google AI for Developers][9])

### Para Android en producción

Si el dispositivo soporta **Android AI Core**, el propio model card de E4B dice que **Gemma 4 vía Gemini Nano / AI Core es la ruta recomendada para producción**. LiteRT-LM sigue siendo valioso para portabilidad y control, pero en Android puro el camino bendecido por Google no siempre pasa por tu runtime custom. ([huggingface.co][3])

## Límites y zonas turbias

Aquí viene la parte menos decorativa y más honesta.

### 1. La documentación de thinking en LiteRT-LM no está todavía cerrada del todo

La guía oficial de Gemma para thinking está en Transformers. En LiteRT-LM, el soporte aparece repartido entre docs de Kotlin, API base e internals del runtime. Funciona más como **capacidad arquitectónica** que como botón uniforme y perfectamente documentado en todas las bindings. ([Google AI for Developers][2])

### 2. Hay problemas reales en dispositivos concretos

Hay issues abiertos recientes para **Gemma 4 E4B** con fallos de inicialización en ciertos Samsung Exynos 2600 y otros problemas de estabilidad móviles. También hay un issue reciente que reporta fallos al pasar de `max_num_tokens=4096` en la variante `.litertlm` de E4B. No es doctrina oficial, pero sí barro de campo que conviene conocer antes de prometer una app milagrosa. ([GitHub][11])

### 3. 32k de contexto no significa 32k sin dolor

El model card publica hasta **32k** para E4B en LiteRT-LM, pero el issue citado sugiere que en algunos entornos reales el comportamiento estable puede quedarse por debajo. La teoría y el runtime no siempre se saludan por la mañana. ([huggingface.co][3])

## Receta práctica que yo probaría primero

1. descarga `gemma-4-E4B-it.litertlm` del repo comunitario oficial
2. arranca con CLI
3. usa `preset.py` con `enable_thinking=True`
4. verifica si el razonamiento sale separado o mezclado
5. pasa luego a Python API con `filter_channel_content_from_kv_cache=True`
6. sube contexto con cautela y benchmarking real en tu hardware objetivo ([huggingface.co][12])

## Mi conclusión

**Sí, Gemma 4 E4B puede usarse con thinking en LiteRT-LM.**
La forma correcta no es buscar un `enable_thinking` mágico de alto nivel en todas las APIs, sino entender que LiteRT-LM lo maneja mediante **plantillas, `extra_context` y channels**. Hoy, la evidencia oficial más clara está en Kotlin e internals del runtime; Python ya expone las piezas necesarias para replicar el patrón de forma razonable y coherente. ([GitHub][4])


[1]: https://developers.googleblog.com/bring-state-of-the-art-agentic-skills-to-the-edge-with-gemma-4/?utm_source=chatgpt.com "Bring state-of-the-art agentic skills to the edge with Gemma 4"
[2]: https://ai.google.dev/gemma/docs/capabilities/thinking "Thinking mode in Gemma  |  Google AI for Developers"
[3]: https://huggingface.co/litert-community/gemma-4-E4B-it-litert-lm "litert-community/gemma-4-E4B-it-litert-lm · Hugging Face"
[4]: https://github.com/google-ai-edge/LiteRT-LM/blob/main/docs/api/kotlin/getting_started.md "LiteRT-LM/docs/api/kotlin/getting_started.md at main · google-ai-edge/LiteRT-LM · GitHub"
[5]: https://github.com/google-ai-edge/LiteRT-LM/blob/main/python/litert_lm/interfaces.py "LiteRT-LM/python/litert_lm/interfaces.py at main · google-ai-edge/LiteRT-LM · GitHub"
[6]: https://github.com/google-ai-edge/LiteRT-LM/blob/main/kotlin/java/com/google/ai/edge/litertlm/Config.kt "LiteRT-LM/kotlin/java/com/google/ai/edge/litertlm/Config.kt at main · google-ai-edge/LiteRT-LM · GitHub"
[7]: https://ai.google.dev/edge/litert-lm/cli "LiteRT-LM CLI  |  Google AI Edge  |  Google AI for Developers"
[8]: https://github.com/google-ai-edge/LiteRT-LM/blob/main/python/litert_lm_cli/model.py "LiteRT-LM/python/litert_lm_cli/model.py at main · google-ai-edge/LiteRT-LM · GitHub"
[9]: https://ai.google.dev/edge/litert-lm/python "LiteRT-LM Python API  |  Google AI Edge  |  Google AI for Developers"
[10]: https://github.com/google-ai-edge/LiteRT-LM/blob/main/kotlin/java/com/google/ai/edge/litertlm/Config.kt?utm_source=chatgpt.com "LiteRT-LM/kotlin/java/com/google/ai/edge/litertlm/Config.kt at main ..."
[11]: https://github.com/google-ai-edge/LiteRT/issues/6743?utm_source=chatgpt.com "Regression: Gemma-4-E4B-it cannot initialize on mobile (LiteRT ... - GitHub"
[12]: https://huggingface.co/litert-community/gemma-4-E4B-it-litert-lm/tree/main "litert-community/gemma-4-E4B-it-litert-lm at main"
