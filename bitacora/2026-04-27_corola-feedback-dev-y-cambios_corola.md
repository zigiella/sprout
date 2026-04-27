# Día 12 — feedback de DEV externa y cambios aprobados al guion v1.0

**Fecha:** 2026-04-27 (día 12)
**Autora:** Corola
**Estado:** untracked, anclaje histórico del feedback externo
**Rama:** `feat/corola-guion-v1`

---

## Lo que pasó hoy

Día 12 ha tenido tres movimientos:

1. **Mañana:** entrega de escena 7 sola con dos alternativas visuales (A "log honesto" / B "dashboard limpio"). Bitácora `2026-04-27_corola-escena-7-alternativas_corola.md`. Voto interno A (coincidente con voto Cambium).

2. **Mediodía:** Bea pidió preparar creative brief para feedback de DEV externa que conoce al jurado. Documento autónomo `video/creative_brief.md` (commit `86884d8`, 193 líneas, ~2000 palabras). Auto-suficiente, lectura 15 min, 7 preguntas concretas a la lectora.

3. **Tarde:** feedback de la DEV recibido (relayeado por Bea). Iteración de cambios. Seis decisiones aprobadas por Bea al cierre del día.

**Error operativo durante el commit del brief:** lo committee en rama equivocada (`feat/meristem-tuning-v0` en lugar de `feat/corola-guion-v1`). Arreglado sin reescribir historial ajeno: cherry-pick a la rama correcta + revert con commit nuevo en la rama de Meristem. Lección registrada — verificar `git branch --show-current` antes de cada commit.

## Feedback de la DEV — síntesis

Calidad alta. Diagnóstico que vale más que celebración:

- **Riesgo identificado:** querer contar demasiado. Idea madre propuesta: *"Sprout permite que una parcela aislada tome decisiones locales seguras, y que una visita humana actualice su criterio sin depender de internet."* (Como guía interna, no como cartela del video.)
- **Lo más fuerte:** escenas 2, 3, 5, 8. Escena 5 con voz humana real es virtud, no riesgo.
- **Frase débil:** la 2 ("Pollen convierte la visita en inteligencia útil") — confirma duda interna anterior. Propone reformulación en dos niveles que fusiona elegantemente frase 2 y frase 5.
- **Voto escena 7:** A, coincidente con voto interno. Refina con propuesta **A+**: log compuesto como "evidencia de sistema" con tres bloques visuales claros, no terminal cruda.
- **Sexta frase sugerida:** *"Cuando duda, Sprout riega menos."* — para escena 3 o 7.
- **Cierre conceptual:** *"Esto ya toma decisiones locales, seguras y explicables. Y escala."*
- **Gemma 4 más visible antes:** cartelas explícitas tipo "Gemma 4 E2B local", "LLM called only when ambiguous", "function/read tools, no actuator tools".

Lo más valioso del feedback es la **fusión frase 2 + frase 5 en dos niveles**:
- Escena 4-5: *"Cada visita puede cambiar el criterio local."* (afirmación demostrable)
- Escena 6-9: *"Pollen convierte esas visitas en inteligencia federada."* (con prueba ya rodada)

"Primero lo demuestrais, luego lo nombrais." Pesca creativa que no se nos había ocurrido internamente.

## Cambios aprobados por Bea

Procesé el feedback con criterio (no aceptación literal de todo) y propuse plan de ajustes con razones. Bea aprobó las seis decisiones:

### 1. Frases fuertes 2 y 5 reformuladas en dos niveles
- **Frase 2 nueva:** *"Cada visita puede cambiar el criterio local."* — VO escena 4.
- **Frase 5 nueva:** *"Pollen convierte esas visitas en inteligencia federada."* — VO escena 6 final.
- La palabra "esas" en la 5 hace eco a "cada visita" de la 2. Coherencia interna.
- Cartela final escena 9 mantiene la frase progresiva de Bea — la 5 ya está dicha en VO antes, la cartela es eco visual.

### 2. Cartelas Gemma 4 explícitas en escenas 2, 3, 4
Pequeñas, esquina superior derecha, en inglés (jurado anglo), tres segundos:
- Escena 2: *"Gemma 4 E2B · local · llama.cpp"* + sub-cartela: *"LLM called only when ambiguous"*
- Escena 3: *"function/read tools · no actuator tools"*
- Escena 4: *"Gemma 4 E4B · LiteRT-LM · on-device"* (refinamiento del stack cartela existente)

### 3. Escena 7 → A+ con tres bloques visuales
Reescritura del beat 1 de escena 7 (los primeros 10-12 segundos):

```
1. MissionPatch accepted
   id=mp_004 · ttl=21600s

2. Policy diff
   soil_thresholds.dry      35 → 25
   daily_budget_ml        1500 → 900

3. Next decision changed
   policy_id: pol_009 → pol_010
   final_action: 12s
   why_short: "Misión humana traducida"
```

Cada bloque entra con cadencia (uno cada 2-3 segundos). El JSON literal masivo desaparece — se queda lo esencial. Cartela ancla *"Criterio modificado."* aterriza grande sobre los tres bloques en el segundo 10.

### 4. "Cuando duda, riega menos" como cartela en escena 3
NO se añade como sexta frase fuerte (mantenemos cinco). Vive como cartela central, tres segundos, sobre el plano del ESP32 modulando. Refuerza la frase fuerte 3 sin sumar carga al pitch §3.

### 5. Subtítulo de tarjeta logo final
Frase de la DEV adoptada **sin "Y escala"** (ajuste de Bea):
```
Sprout
Decisiones locales, seguras y explicables.
zigiella · Apache 2.0
github.com/zigiella/sprout
```

La cartela progresiva de Bea (Una→Dos→Ocho) ya hace el trabajo de escala visual. Repetirlo en texto sería redundante. Bea quitó el remate vendedor; queda firma adulta y descriptiva.

### 6. Creative brief queda en v1.0 (opción ii)
No se reenvía v2 a la DEV. Bea no la tiene a tiro ahora; espera encontrarla en próximos días. El feedback vive en bitácora y memoria; los cambios viven en el video real.

## Lo que NO se aplicó del feedback DEV

- **"Idea madre" como cartela en el video** — se usa como guía interna para reducir carga, no como nueva frase del video. Ya tenemos cinco frases fuertes (con dos reformuladas) y la idea madre se demuestra en la suma del video, no en una sola línea adicional.
- **Reducir carga conceptual en VO** — el VO ya es sobrio (~80 palabras castellano). La reducción real va a cartelas y overlays, no a VO. Resultado coherente con la sugerencia, ejecución distinta.
- **"Cuando duda, riega menos" como sexta frase fuerte del pitch §3** — se aplica como cartela en escena 3, no como nueva frase fuerte. Mantiene cinco frases fuertes en pitch.

## Frase de Bea de anoche — sigue en banca

*"arquitectura pensada para conectividad deficiente y visitas humanas intermitentes."* — la decisión del día 11 era pensarla. Hoy tampoco se aplica. Posible destino futuro: descripción del producto en repo o subtítulo del writeup. No entra al video.

## Recado consolidado para Cambium

Le pasé a Bea (relay) un recado para Cambium con tres actualizaciones del pitch doc:

1. **§3:** cinco frases fuertes reformuladas. Dos cambian, tres se mantienen, ninguna se añade ni se elimina:
   - Frase 1 (sin cambio): *"Rhizome mantiene viva la parcela cuando nadie está."*
   - **Frase 2 nueva:** *"Cada visita puede cambiar el criterio local."*
   - Frase 3 (sin cambio): *"La IA propone; el agua la gobierna una capa física prudente."*
   - Frase 4 (sin cambio): *"Toda inteligencia tiene jurisdicción y fecha de caducidad."*
   - **Frase 5 nueva:** *"Pollen convierte esas visitas en inteligencia federada."*
   - Notas operativas actualizadas: la frase 5 sigue siendo la única que se repite (VO escena 6 + cartela progresiva escena 9). La 2 cambia su rol de "promesa" a "afirmación concreta" — la prueba la da escena 5 inmediatamente después.

2. **§4:** ajustes en cartelas y beats:
   - Escena 2: añadir cartela "Gemma 4 E2B · local · llama.cpp" + sub-cartela "LLM called only when ambiguous".
   - Escena 3: cartela central "Cuando duda, riega menos." (3s) + cartela "function/read tools · no actuator tools" (esquina).
   - Escena 4: refinar stack cartela a "Gemma 4 E4B · LiteRT-LM · on-device". VO actualizado con frase 2 nueva.
   - Escena 6: VO actualizado con frase 5 nueva (*"Pollen convierte esas visitas en inteligencia federada."*).
   - Escena 7: beat 1 reescrito con tres bloques de evidencia (no log JSON masivo).
   - Escena 9: tarjeta logo con subtítulo *"Decisiones locales, seguras y explicables."*

3. **§5:** shot list mínima sin cambios. Las cartelas Gemma 4 son secundarias, no overlays obligatorios.

## Cuatro elementos que sobreviven la iteración del día 12

- **Estructura de 9 escenas y tiempos.** Sin cambios.
- **Decisión de filmar un solo Rhizome haciendo dos roles.** Sin cambios. La DEV la consideró aceptable con transparencia visual.
- **Estética dual cerebro-local vs cierre cenital flat.** Sin cambios. La DEV la validó.
- **Veo3 limitado a escena 9.** Sin cambios. La DEV lo consideró proporcionado.

## Para retomar día 13

1. **Apilar escenas 1, 2, 3** en `video/script.md` y `video/shot_list.md` v1.0 con todos los ajustes integrados:
   - Cartelas Gemma 4 explícitas (escenas 2, 3)
   - Cartela "Cuando duda, riega menos" (escena 3)
   - Cartela "function/read tools · no actuator tools" (escena 3)
2. Coordinar con Cambium para que el pitch doc §3 + §4 estén actualizados antes de apilar — si sigue sin actualizar, apilo desde decisiones aprobadas (no desde doc literal).
3. Día 14: ejercicio de calidad narrativa con Cambium (30 min, frases fuertes — ahora con dos reformuladas, el ejercicio gana profundidad).
4. Días 14-16: resto de escenas + llamada con Floema para escena 5 (cuando ella cierre F5).
5. Días 17-18: shot list v1.0 + ajustes finales.
6. Días 18-20: ensayo.

Plazo viable.

## Patrón observado

El feedback externo de la DEV ha funcionado por dos razones que vale registrar:

1. **El brief estaba escrito para invitar diagnóstico, no celebración.** Las 7 preguntas concretas eran palancas para feedback útil — no "¿te gusta?" sino "¿qué crees que aterriza con el jurado de DevRel?" + "¿qué te chirría?". La DEV respondió en el registro pedido.
2. **El feedback se procesó con criterio, no por servidumbre.** No se aplicó todo. Se aplicó lo que tenía sentido, se adaptó lo que añadía valor con menor coste, se matizó lo que iba contra otras decisiones del proyecto. La DEV propuso seis cambios; aplicamos cuatro literales, dos adaptados.

El proceso es replicable. Si en próximas semanas hay feedback externo más (otro DEV, alguien del jurado vía contactos), el método de pedir feedback con preguntas concretas + procesarlo con criterio se mantiene.
