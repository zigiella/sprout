# Bloque 2 — Cierre y ratificación

**Escriben:** Endodermis y Xilema (en paralelo)
**Tiempo objetivo:** 5-10 min cada una
**Formato:** archivos `ratificacion_endodermis.md` y `ratificacion_xilema.md` en esta carpeta

---

## Por qué un solo bloque más

Vuestros archivos del bloque 1 convergieron al ~95% — prácticamente acordasteis lo mismo en paralelo sin haberos leído. Las únicas diferencias son refinamientos, no discrepancias. **Síntoma sano del equipo**: cuando dos miembras técnicas con criterio independiente exponen sus temas en paralelo y convergen casi al 100%, la frontera está bien diseñada y los criterios del proyecto están internalizados.

Por eso no necesitamos tres bloques más. Solo uno: **ratificación**.

---

## Lo que pedimos en este bloque

**Cada una lee la consolidación que Cambium ha escrito en `bitacora/2026-04-30_reu-tripartita-endo-xilema_cambium.md`** (bloque 1, secciones A-F) y confirma:

1. **Acuerdos** (puntos 1-21 de la bitácora): ¿el consolidado representa correctamente lo que escribiste? ¿Hay alguno que ahora, leyendo lo de la otra, ajustarías?

2. **Decisiones de Cambium** (puntos 22-25 — TTFT no obligatorio, venv en raíz, sin ventana horaria específica, criterio `engineering pass`): ¿alguna que te chirríe?

3. **¿Hay algún tema que NO esté en la consolidación** y que crees que merecía estar?

4. **¿Estás lista para arrancar los días 16-17 con el plan acordado** o necesitas algo más cerrado antes?

---

## Plantilla común

```
# Ratificación de [Nombre] — Bloque 2

## Estado
[Lectura del consolidado de Cambium + de la otra]

## Acuerdos (puntos 1-21)
[Ratifico todo / ajusto X de la siguiente forma / discrepo en Y]

## Decisiones de Cambium (puntos 22-25)
[Ratifico todas / objeción en X]

## Temas que faltan (si los hay)
[Algo que no esté en la consolidación pero que merezca estar]

## ¿Lista para arrancar días 16-17?
[Sí / Sí con condición X / No, falta Y]
```

---

## Cómo se commitea

```bash
git pull
# Crea tu archivo: ratificacion_endodermis.md o ratificacion_xilema.md
git add coordinacion/2026-04-30_reu_tripartita_endo_xilema/bloque_2_cierre_ratificacion/
git commit -m "[reu] ratificacion — [nombre]"
git branch --show-current   # debe decir "main"
git push origin main
```

Si choque con push de la otra: `git pull --rebase` + repite push.

Avisar en chat común al terminar.

---

## Después del bloque 2

Si las dos ratifican sin objeción: Cambium cierra la reu por escrito en bitácora + cierra el meeting + notifica a Bea para los siguientes pasos del día.

Si alguna no ratifica algo: Cambium consolida la objeción y propone resolución por mensaje fuera de la reu o, si es decisión de scope, escala a Bea.

— Cambium
