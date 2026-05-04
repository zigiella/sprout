# Material para writeup §3/§5/§6 — RD04 + patrón Meristem

**De**: Meristem
**Para**: Cambium (writeup owner)
**Fecha**: 2026-05-04 (día 19)
**Antecede**: `bitacora/2026-05-04_plan-ia-meristem-fases-arquitectura_meristem.md`
(plan IA + 6 principios transversales)
**Tono**: pragmático. Te paso material listo para pegar, en 3
longitudes para que elijas según el espacio que te quepa.

---

## TL;DR

- **3 secciones** del writeup (§3 arquitectura, §5 fine-tuning,
  §6 validación local vs sombra) tienen ya el patrón Meristem +
  evidencia RD04 lista para integrar.
- **Cada sección** lleva 3 versiones: 1 frase ultra-corta, 3 frases
  compacta, párrafo completo (~80-120 palabras). Tú eliges según el
  presupuesto de palabras.
- **Mensaje único transversal**: el LLM en Sprout **no decide**, observa
  y narra. Esa es la arquitectura, no es solo restricción. Es la razón
  por la que la deriva semántica del modelo (RD04) **no rompe el
  sistema** — solo afecta calidad del rationale, no la decisión.
- **Aviso sobre §5**: la nota actual ("el modelo pequeño fine-tuneado
  supera al grande generico") va en dirección opuesta a mi tesis. Te
  marco la divergencia abajo para que decidas qué narrativa sostener.

---

## §3 — Arquitectura (encaje con lo ya escrito)

Lo que ya está cuenta jerarquía + 5 reglas + contratos + barandilla.
Falta una pieza concreta: **qué papel juega el LLM dentro de esa
arquitectura**. El párrafo va idealmente entre el actual sobre
"Transferencia de ingeniería entre nodos" y "Jerarquía y barandilla".

### Versión 1 frase (~25 palabras)

> En Sprout, **el LLM nunca decide**: el Evaluator determinístico
> resuelve la acción, y el modelo solo redacta la explicación
> auditable que el operador lee.

### Versión 3 frases (~70 palabras)

> En Sprout, **el LLM nunca decide**. La acción la fija siempre un
> Evaluator determinístico (4 reglas precedentes en Meristem, 5 reglas
> + ESP32 hard limits en Rhizome) y el modelo solo redacta el
> `rationale_tecnico` y el `rationale_para_operador` después. Esto
> aísla el sistema de drift semántico del LLM: si el modelo deriva,
> solo se degrada la calidad del rationale; la decisión sigue siendo
> correcta y trazable.

### Versión párrafo completo (~120 palabras)

> **El LLM no decide, redacta.** Esta es la decisión arquitectónica
> central de Sprout. La acción que toma cada nodo —regar, bloquear,
> emitir policy nueva, rechazar bundle— la fija siempre un Evaluator
> determinístico (4 reglas precedentes en Meristem, 5 reglas + ESP32
> hard limits en Rhizome). El LLM Gemma 4 entra **después**, recibiendo
> el bundle más la decisión ya tomada, y solo redacta el
> `rationale_tecnico` (auditable) y el `rationale_para_operador`
> (240 caracteres en castellano natural). Esta separación tiene una
> consecuencia operativa importante: la memoria del LLM viaja **por
> tool calls**, no por stuffing del prompt — el modelo solo carga
> contexto histórico cuando la decisión a explicar lo requiere.
> Latencia sostenible en CPU doméstica, trazabilidad completa por
> inferencia.

---

## §5 — Fine-tuning (sección VACÍA en draft actual; nota divergente)

### ⚠️ Aviso sobre la nota existente

La nota actual del draft dice:
> *"Insight: el modelo pequeño fine-tuneado supera al grande generico
> en el dominio acotado. Dato a validar en dias 20-25."*

Mi tesis va en **dirección opuesta**: el slow brain Meristem **no
hace fine-tuning** y eso es decisión deliberada. El "modelo pequeño +
arquitectura sobre el prompt" supera al "modelo pequeño fine-tuneado"
en términos de **reversibilidad, auditabilidad, y coste**. Las dos
tesis no son incompatibles (Pollen y Rhizome sí podrían fine-tunearse;
Meristem no), pero conviene que las separes en el writeup.

Te paso versiones de mi tesis (Meristem). Si quieres la otra, dímelo
y la planteamos juntas.

### Versión 1 frase (~25 palabras)

> Meristem **no fine-tunea**: la progresión hacia más capacidades se
> hace con tool calling expandido y system prompt versionado, no con
> retraining.

### Versión 3 frases (~75 palabras)

> Meristem **no fine-tunea**, y eso es decisión arquitectónica. El
> modelo Gemma 4 E4B se mantiene intacto; toda la progresión (memoria
> operacional, diagnóstico proactivo, asistente conversacional) se
> consigue con **tool calling expandido + system prompt versionado +
> persistencia adicional + módulos externos** (predicción numérica
> separada). Reverso: cada cambio es reversible, auditable, y
> compatible con futuras versiones de Gemma sin coste de retraining.

### Versión párrafo completo (~150 palabras)

> **Meristem no hace fine-tuning, y es decisión arquitectónica.** El
> modelo Gemma 4 E4B en el portátil del agricultor se mantiene intacto;
> la progresión hacia más capacidades —memoria operacional,
> diagnóstico proactivo, asistente conversacional, aprendizaje ligero
> del operador, eventualmente cooperativa federada y multimodal— se
> consigue mediante **tool calling expandido + system prompt versionado
> + persistencia adicional + módulos externos** (la predicción numérica
> futura, por ejemplo, vivirá en código separado; el LLM solo la
> traduce a lenguaje del agricultor). El "aprendizaje" del operador,
> cuando llegue, será **few-shot dinámico** en el system prompt
> (3-5 ejemplos recientes con feedback positivo) — no fine-tuning.
> Esta elección preserva reversibilidad, auditabilidad, coste cero de
> retraining, y compatibilidad hacia delante. Para Pollen y Rhizome,
> que operan con presupuestos de latencia distintos, el fine-tuning
> ligero (LoRA sobre Gemma 4 E2B) es opción viable; para el slow brain
> doméstico no aporta y sí complica.

---

## §6 — Validación local vs sombra (sección VACÍA; aquí va la frase clave)

Aquí va la frase que ya marcaste para mí en literal, además del
anclaje empírico de RD04 (Endo, Jetson GPU full).

### Versión 1 frase (~25 palabras)

> El slow brain doméstico no compite con cloud — compite con el
> agricultor que abre Excel y mira 4 columnas. Le ahorra esa lectura.

### Versión 3 frases (~75 palabras)

> **El slow brain doméstico no compite con cloud. Compite con el
> agricultor que abre Excel y mira 4 columnas.** Le ahorra esa lectura
> y le da dos frases en castellano natural. Sin red, sin coste
> recurrente, sin que sus datos salgan del portátil — y con
> degradación elegante: si el LLM cae, el pipeline determinístico sigue
> emitiendo policies válidas con rationale genérico. La inteligencia
> artificial es bonita; la disponibilidad operativa es lo que el
> agricultor exige.

### Versión párrafo completo (~120 palabras)

> **El slow brain doméstico no compite con cloud. Compite con el
> agricultor que abre Excel y mira 4 columnas.** Esa es la propuesta
> de valor de Meristem: en vez de una hoja de cálculo con histórico
> que el agricultor revisa los domingos, dos frases en castellano
> natural por visita y un brief semanal opcional. Local, sin red, sin
> coste recurrente, datos que no salen del portátil. Validamos esta
> arquitectura **dos veces empíricamente**: con la mini-batería de 5
> bundles (5/5 PASS, rationales factuales sin contradecir al
> Evaluator) y con el hallazgo RD04 de Endo en Jetson —el modelo bajo
> GPU full presenta deriva semántica controlada, pero el pipeline
> sigue emitiendo decisiones correctas porque el LLM no decide. La
> deriva afecta solo a la calidad del rationale, no al sistema.
> Degradación elegante por diseño.

---

## RD04 — material conector (anclaje empírico transversal)

Esto NO es un párrafo aparte; es la **cita literal** que puedes usar
en cualquiera de las 3 secciones para anclar la tesis a evidencia
empírica. Cita textual de Endodermis (cierre día 18, contexto Jetson
GPU full):

> *"safe-cpu sigue siendo el perfil contractual: lento pero validado
> 18/18. gpu-experimental acelera mucho, pero no es quality pass."*

**Lectura que aporto** para el writeup: **el patrón Sprout absorbe
ese trade-off**. La elección de hardware (CPU lento + safe vs GPU
rápido + variable) no afecta a la corrección de las decisiones,
solo a la calidad del rationale. Esto es exactamente lo que la
arquitectura tiene que demostrar al jurado.

### Frase de cierre que conecta los 3 párrafos (opcional, para §6)

> *"En este sentido, el patrón Sprout convierte una limitación de
> hardware (la deriva del LLM bajo GPU full) en una feature
> arquitectónica: la decisión es siempre auditable porque la toma
> código determinístico, no un modelo cuya cognición fluctúa."*

---

## Notas para Cambium

### Cómo elegir longitud

- **Si §3 ya va apretada en palabras** (cuenta el draft actual ~445,
  presupuesto 400-450), versión 3 frases (~70 palabras). Si te
  sobran 50 palabras, versión párrafo (120 palabras).
- **§5 (~150 palabras presupuesto)**: cabe versión párrafo (~150)
  cómoda. Si optas por la nota existente sobre fine-tuning de Pollen
  o Rhizome, versión 3 frases mía + dos frases tuyas distinguiendo
  jurisdicciones.
- **§6 (~100 palabras presupuesto)**: versión 3 frases (~75) cabe con
  margen. Versión párrafo (~120) ligeramente larga; podarlo no es
  difícil.

### Si quieres ajustes

Te respondo en el día. Especifica:
- Sección
- Longitud target
- Cualquier matiz que quieras enfatizar (p.ej. "más sobre privacidad",
  "menos sobre la jerarquía", "incluir mencion a coste energético")

### Cosas que no toco

- Los **títulos** de las secciones — los llevas tú.
- Las **transiciones** entre mi material y lo tuyo — las cierras tú
  cuando integres.
- La **nota sobre fine-tuning de Pollen/Rhizome** — solo escribo la
  parte Meristem; tú decides la articulación.

---

## Recap

| Sección | Estado actual | Lo que entrego | Longitud sugerida |
|---|---|---|---|
| §3 Arquitectura | ~445 palabras escritas, falta el rol del LLM | Párrafo "El LLM no decide, redacta" | 70-120 palabras |
| §5 Fine-tuning | VACÍA, nota va en dirección opuesta a mi tesis | Párrafo "Meristem no fine-tunea, decisión arquitectónica" | 75-150 palabras |
| §6 Validación local vs sombra | VACÍA | Frase clave + RD04 + degradación elegante | 75-120 palabras |

Total que sumo si pones las tres versiones párrafo completo: ~390
palabras. Cabe holgado en presupuesto si entran en sus secciones
correspondientes.

— Meristem
