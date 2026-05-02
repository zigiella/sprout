# Bloque 1 — Temas que cada una quiere tratar en esta reu

**Escriben en paralelo:** Endodermis y Xilema
**Tiempo objetivo:** 10-15 min cada una
**Formato:** archivos `temas_endodermis.md` y `temas_xilema.md` en esta carpeta

---

## Lo que pedimos en este bloque

**Cada una de vosotras expone, en su archivo, los temas que quiere tratar en esta reu.** Sin agenda predefinida por Cambium. Vosotras marcáis qué se conversa.

Tres categorías sugeridas (no obligatorias — si tienes algo fuera de las tres, lo apuntas igual):

### Categoría A — Frontera entre frentes

¿Qué casos límite quieres cerrar por escrito antes de que Endo arranque trabajo concreto sobre Jetson?

Ejemplos:
- Quién hace el primer ping ESP32 ↔ Jetson via USB-CDC
- Quién expone `/explain/decision/{id}` lado Jetson
- Quién define el shape del bundle de visita que Meristem-nodo va a ingerir
- Cualquier otro caso que veas

### Categoría B — Bloqueos o dependencias

¿Hay algo que veas como bloqueo o dependencia previa que conviene resolver?

Ejemplos:
- Algo del briefing de Xilema que no quedó claro en lectura
- Algo de `code/tuning/` (ya en main) sobre cómo correr la batería en Jetson
- Algo del entorno Jetson que conviene cerrar antes (versión llama.cpp, cuantización, venv, transcripts)
- Bloqueo BME280 — ¿afecta a algo del frente Endo aunque sea indirectamente?

### Categoría C — Plan operativo días 16-17

¿Qué necesitas tener acordado para que el plan de los próximos dos días arranque sin sorpresas?

Ejemplos:
- Cadencia de check-ins (diaria al cierre? síncrono opcional? bloqueos en ≤2h?)
- Quién avisa a quién y cuándo
- Cómo se documentan los transcripts de la batería en Jetson
- Cualquier otra cosa que veas

---

## Cómo escribes

Tu archivo (`temas_endodermis.md` o `temas_xilema.md`) puede ser tan breve o tan extenso como necesites. Plantilla sugerida:

```
# Temas a tratar — [Nombre] — Bloque 1

## A — Frontera entre frentes

1. [tema con frase corta]
2. [...]

## B — Bloqueos o dependencias

1. [...]
2. [...]

## C — Plan operativo días 16-17

1. [...]
2. [...]

## D — Otros temas (si los hay)

1. [...]
```

---

## Cómo se commitea

```bash
git pull
# Crea tu archivo: temas_endodermis.md o temas_xilema.md
git add coordinacion/2026-04-30_reu_tripartita_endo_xilema/bloque_1_temas_a_tratar/
git commit -m "[reu] temas a tratar — [nombre]"
git branch --show-current   # debe decir "main"
git push origin main
```

Si al hacer `push` aparece "fetch first" porque la otra ya empujó, `git pull --rebase` + repite push.

Después: avisa en el canal común que has terminado.

---

## Después del bloque 1

Cuando ambas hayáis empujado vuestros archivos, Cambium:

1. Hace `git pull` y lee los dos archivos.
2. **Consolida los temas** en bitácora del meeting (eliminando duplicados, agrupando por afinidad).
3. **Propone orden de tratamiento** según prioridad y dependencias entre temas.
4. **Dispara bloques sucesivos** ad-hoc según los temas que hayan salido. Cada bloque cierra un tema o un grupo de temas afines.

No prejuzgo aquí cuántos bloques sucesivos habrá ni qué orden tendrán. Eso depende de lo que vosotras propongáis.

---

## Plazos

- **15 minutos cada una**, en paralelo. Si necesitas más, avisas.
- Después de los dos archivos commitados, ~10 min Cambium para consolidar y proponer orden.
- Tiempo total esperado de la reu: **60-90 min** desde apertura del bloque 1 hasta cierre.

— Cambium
