** Otros apuntes sobre Thinking en Gemma 4 E4B con LiteRT-LM**. 

## Lo que sí está sólido

En la parte oficial, LiteRT-LM deja ver bastante bien el diseño interno. El runtime acepta **`extra_context`** para la plantilla, y el propio código de `prompt_template.h` dice que ese contexto extra puede usarse, por ejemplo, para **habilitar thinking mode**. La guía Kotlin muestra el patrón explícito con `enable_thinking = true` y `Conversation.sendMessage(..., extraContext = ...)`, y `ConversationConfig` documenta además **`channels`** como salidas separadas del canal principal, poniendo como ejemplo un canal de thinking. La CLI/Python pasan `extra_context` y también exponen `filter_channel_content_from_kv_cache`, que sirve para que ese canal no se reinyecte al historial como si fuera respuesta normal. Eso no es humo de marketing: es cableado real del runtime. ([GitHub][1])

También existe soporte oficial público del modelo **`litert-community/gemma-4-E4B-it-litert-lm`**. La tarjeta del modelo publica un fichero de **3.65 GB**, explica que LiteRT-LM mantiene los pesos principales en memoria y memory-mappea parte de embeddings, y da benchmarks por plataforma. En esa misma tarjeta se afirma soporte de hasta **32k de contexto** en LiteRT-LM para E4B, y en Android se añade una nota incómoda pero reveladora: en dispositivos compatibles, **Google recomienda Android AI Core / Gemini Nano como camino de producción**, no necesariamente LiteRT-LM puro. Ese matiz importa bastante más de lo que parece. ([Hugging Face][2])

## Lo que cuentan los experimentos públicos de verdad

La parte menos bonita es esta: **he encontrado pocos experimentos públicos que aíslen explícitamente “thinking on/off” en Gemma 4 E4B dentro de LiteRT-LM** y midan calidad, latencia y separación de canales de forma limpia. En cambio, sí aparecen bastantes pruebas públicas centradas en estabilidad de ejecución, GPU delegates, memoria y límites de contexto. El foco comunitario ahora mismo no está en “qué fino razona E4B en LiteRT-LM”, sino en “¿arranca bien en este hardware sin romperse?”. ([Google AI Developers Forum][3])

Eso no invalida la capacidad. Lo que muestra es otra cosa: **la capacidad existe antes que la ergonomía**. El modelo y el runtime ya traen thinking, pero la experiencia pública todavía no está estabilizada en todos los backends y dispositivos. Es la típica jugada de esta industria: primero te venden el borde del mapa, luego descubres dónde están los pantanos. ([GitHub][1])

## Donde más se está rompiendo

En móvil hay varias señales bastante consistentes. En el foro de Google AI Developers apareció un reporte de **fallo de inicialización de Gemma 4 E4B en Google AI Edge Gallery**. En GitHub hay un issue paralelo para **Samsung Exynos 2600** pidiendo investigar compatibilidad del delegate GPU y un fallback CPU más elegante. En las discusiones del propio modelo en Hugging Face, usuarios comentan que **E2B funciona**, mientras que **E4B puede exceder memoria y llegar a crashear**, y Edge Gallery llega a advertirlo. No es una anécdota aislada; es un patrón que ya se repite en varias superficies. ([Google AI Developers Forum][3])

En iOS el panorama tampoco está domesticado del todo. Hay un issue abierto donde **E4B en `.litertlm` se cae si `max_num_tokens` supera 4096** durante prefill en arm64, aunque la tarjeta del modelo publique soporte de hasta 32k. Y hay otro donde **E4B texto solo funciona**, pero el primer mensaje con imagen provoca crash en prefill dentro de XNNPACK, mientras **E2B sí funciona por la misma ruta de código**. La lectura brutal es esta: la promesa arquitectónica va por delante de la robustez observada, sobre todo si te sales del texto puro. ([GitHub][4])

## Donde sí hay señales mejores

La comparación con **E2B** es útil porque muestra hacia dónde podría madurar E4B. En un issue de Pixel 8, un desarrollador reporta que con `litertlm-android 0.10.0` el modelo cargaba en GPU pero fallaba en decode; reconstruyendo `0.10.1` y aplicando un parche pequeño, consiguió que **Gemma 4 E2B** corriese de extremo a extremo en GPU. En otro issue, un usuario comenta que en **Pixel 9** puede ejecutar E2B en CPU y GPU, con GPU alrededor de **2x más rápido**, aunque no todavía en TPU/NPU. No es E4B, pero sí sugiere que el sendero de estabilización existe y que la comunidad está encontrando fixes de bajo nivel antes de que lleguen como default. ([GitHub][5])

Mi inferencia, y la subrayo como inferencia, es que **E2B está algo más cerca del “usable everywhere” y E4B más cerca del “power tier que aún castiga más la fragilidad del runtime”**. La propia discusión de Hugging Face donde E2B pasa y E4B revienta memoria va en esa dirección. ([GitHub][5])

## Qué dicen los números oficiales y qué dicen entre líneas

La tarjeta pública de E4B en LiteRT-LM da números que son bastante decentes para on-device, pero también revelan el coste material del modelo. En **S26 Ultra**, la tarjeta publica **1293 tokens/s de prefill y 22.1 tokens/s de decode en GPU**, frente a **195 / 17.7 en CPU**, con **710 MB** de memoria en GPU y **3283 MB** en CPU. En **iPhone 17 Pro**, publica **1189 / 25.1** en GPU frente a **159 / 9.7** en CPU. En **Raspberry Pi 5 16GB**, la cosa baja a **51 / 3.2**, con **20.5 s** de TTFT. Traducido: E4B ya es móvil, sí, pero no es un modelo “gratis”. Sigue pidiendo hardware serio o compromisos. ([Hugging Face][2])

Hay otro detalle sutil. La visión general pública de LiteRT-LM muestra benchmarks detallados sobre todo para **E2B** como “featured model”, mientras que E4B queda más desarrollado en la tarjeta específica de Hugging Face. No prueba nada por sí solo, pero sí sugiere que el escaparate público todavía empuja más el caso amable que el caso exigente. El marketing siempre enseña primero la versión que no muerde. ([Google AI for Developers][6])

## Sobre thinking en sí, no solo sobre cargar el modelo

Aquí la evidencia más interesante no viene de LiteRT-LM puro, sino del ecosistema Gemma 4 alrededor. La guía oficial de Gemma explica thinking en Transformers con `enable_thinking=True`, y dos blogs independientes sobre **LM Studio/OpenCode** muestran que el gran problema práctico no es “si Gemma 4 sabe pensar”, sino **si el runtime abre el canal correcto y sabe parsearlo después**. Uno de ellos explica que sin parsing del canal `thought` el modelo puede estar pensando, pero la aplicación no sabe separarlo; otro enseña una plantilla Jinja donde `enable_thinking` abre el canal. Eso encaja muy bien con el diseño de LiteRT-LM, que precisamente expone **`extraContext`** y **`channels`** para ese mismo trabajo. Dicho de otra forma: fuera de LiteRT-LM, el patrón comunitario confirma la intuición de dentro de LiteRT-LM. El problema suele estar en la plomería, no en la capacidad del modelo. ([Google AI for Developers][7])

Eso sí, **no he encontrado todavía una batería pública madura de pruebas A/B de Gemma 4 E4B con LiteRT-LM midiendo `enable_thinking` activado frente a desactivado** con latencia, calidad de answer y comportamiento del canal en Android/iOS/desktop. Hay piezas del puzzle, pero no el paper de campo que uno querría para tomar decisiones con sangre fría. Lo que hay es suficiente para diseñar la ruta técnica, no para fingir que el terreno está asfaltado. ([Google AI Developers Forum][3])

## Lectura de todo esto

Mi veredicto, después de cruzar documentación, issues, foro de Google, discusiones de Hugging Face y blogs independientes, es este:

**Gemma 4 E4B con LiteRT-LM sí tiene thinking de forma estructural.**
**El problema público actual no es activar el concepto, sino estabilizar la ejecución en dispositivos y backends concretos.**
**Los experimentos comunitarios visibles hoy hablan más de runtime que de razonamiento.**
**Si buscas una apuesta seria para producto móvil, E4B con LiteRT-LM parece hoy mejor como vía de exploración controlada que como base cerrada y tranquila para producción generalista**, salvo casos muy medidos o hardware validado uno por uno. En Android compatible, la propia tarjeta del modelo empuja hacia **AI Core / Gemini Nano** como camino recomendado. ([GitHub][8])

La parte que se queda corta en el panorama público es fácil de resumir: encontré **mucha evidencia de compatibilidad, benchmarks y bugs**, y **muy poca evidencia pública de experimentos finos específicamente centrados en thinking-channel de E4B dentro de LiteRT-LM**. Ese vacío también dice algo: todavía estamos en fase de runtime-first, no de polish-first. ([Google AI Developers Forum][3])


[1]: https://github.com/google-ai-edge/LiteRT-LM/blob/main/docs/api/kotlin/getting_started.md "LiteRT-LM/docs/api/kotlin/getting_started.md at main · google-ai-edge/LiteRT-LM · GitHub"
[2]: https://huggingface.co/litert-community/gemma-4-E4B-it-litert-lm "litert-community/gemma-4-E4B-it-litert-lm · Hugging Face"
[3]: https://discuss.ai.google.dev/t/regression-gemma-4-e4b-it-cannot-initialize-on-mobile-litert-engine-error/138016?utm_source=chatgpt.com "Regression: Gemma-4-E4B-it cannot initialize on mobile (LiteRT Engine ..."
[4]: https://github.com/google-ai-edge/LiteRT/issues/6765 "Gemma 4 E4B .litertlm: max_num_tokens >4096 crashes with SIGSEGV in reshape on iOS arm64 · Issue #6765 · google-ai-edge/LiteRT · GitHub"
[5]: https://github.com/google-ai-edge/LiteRT-LM/issues/1850 "Gemma 4 E2B on Pixel 8: 0.10.0 fails on GPU decode, self-built 0.10.1 runtime patch fixes it · Issue #1850 · google-ai-edge/LiteRT-LM · GitHub"
[6]: https://ai.google.dev/edge/litert-lm/overview "LiteRT-LM Overview  |  Google AI Edge  |  Google AI for Developers"
[7]: https://ai.google.dev/gemma/docs/capabilities/thinking?utm_source=chatgpt.com "Thinking mode in Gemma | Google AI for Developers"
[8]: https://github.com/google-ai-edge/LiteRT-LM/blob/main/runtime/components/prompt_template.h "LiteRT-LM/runtime/components/prompt_template.h at main · google-ai-edge/LiteRT-LM · GitHub"
