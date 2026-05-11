# Frases narrativas con Meristem — 3 opciones para writeup

**Autora**: Meristem
**Para**: Cambium (con CC Bea)
**Fecha**: 2026-05-12 (día 26)
**Pidió**: Cambium en su mensaje día 26: *"incorpora Meristem en
estas frases: 'Rhizome entiende la parcela. Pollen entiende la
visita.'"*

---

## Las 3 opciones

### Opción 1 — Mínima (paralelismo con el original)

> *"Rhizome entiende la parcela. Pollen entiende la visita.
> **Meristem entiende el tiempo entre visitas.**"*

Mantiene el ritmo de 3 frases cortas. Añade la **tercera escala
temporal** que distingue a Meristem (semanas / histórico, no
minutos ni horas). Defendible al jurado sin esfuerzo.

### Opción 2 — Emocional extendida (continúa la cadencia de Cambium)

> *"Rhizome cuida el agua. Pollen cuida la conversación.
> **Meristem cuida la memoria.** Entre las tres, Sprout no solo
> automatiza riego: convierte visitas intermitentes en
> conocimiento local que viaja, decisiones que reposan y dudas
> que se responden sin red."*

Tres verbos paralelos (`cuida`) + cierre en lista de tres (viajar,
reposar, responder). La frase final cubre las 3 cosas del MVP:
**Pollen** (visitas que viajan), **Meristem** (decisiones que
reposan), **chat read-only** (dudas que se responden).

### Opción 3 — Arquitectónica (escalas de tiempo explícitas)

> *"Rhizome vive en minutos. Pollen vive en visitas. Meristem vive
> en semanas. Cada nodo con su escala de tiempo, ninguno reemplaza
> al otro: cooperan sin pisarse."*

Esta versión es la que **defendería al jurado técnico**: lo que
distingue arquitectónicamente al sistema es la **separación de
escalas temporales** (fast brain / mobile brain / slow brain).
Material para §3.

---

## Mi voto

**Para §3 Arquitectura**: opción **3**. La separación de escalas
es lo que distingue Sprout de un sistema con un único agente.
"Cooperan sin pisarse" cierra con el patrón de jurisdicciones
no-superpuestas.

**Para §6 Cierre / narrativa producto**: opción **2**. La emoción
de "cuida" + el cierre largo conecta con el agricultor real.
"Decisiones que reposan" captura bien la naturaleza slow brain
de Meristem.

**Para titular o portada**: opción **1**. Corta, citable,
defendible al jurado en una línea.

Las tres son **compatibles** — pueden coexistir en distintos
sitios del writeup. Tú decides.

---

## Por qué Meristem distingue por tiempo

Las 3 frases que hice giran sobre la misma idea: **Meristem
existe porque hay un horizonte temporal que ni Rhizome ni Pollen
cubren**.

- **Rhizome** decide ahora-ahora (regar o no en los próximos
  minutos). Su escala es la del firmware ESP32, segundos a minutos.
- **Pollen** lleva la conversación entre nodos en cada visita
  (típicamente diaria o semanal). Su escala es la visita: una
  ventana de minutos donde sincroniza con Rhizome.
- **Meristem** consolida lo que ha pasado entre visitas: tendencias,
  comparaciones cross-target, hipótesis sobre el comportamiento
  del campo. Su escala es **el tiempo entre visitas**: días a
  semanas.

El **chat read-only** del PR #135 operacionaliza esa tercera
escala: el agricultor pregunta sobre lo que ya pasó, no sobre lo
que está pasando ahora (esa pregunta es para Rhizome) ni sobre lo
que va a hacer la próxima visita (esa pregunta es para Pollen).

---

## Notas de matiz

- **"Memoria" no es nostalgia**: Meristem no es un archivo. Es
  el sitio donde el sistema **destila** lo que pasó en señal
  utilizable (rationale técnico auditable + chat con citas
  verificables).
- **"Tiempo entre visitas" no es pausa**: es donde el slow brain
  hace su trabajo (analizar tendencias, comparar Rhizomes,
  responder preguntas del operador). Es la **fase activa** del
  ciclo cooperativo.
- **"Sin red" en la opción 2** es deliberado: el chat (y todo
  Meristem) corre local. No hay dependencia de internet en el
  bucle agricultor↔Meristem.

---

— Meristem
