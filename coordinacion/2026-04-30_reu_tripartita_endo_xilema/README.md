# Reu tripartita Endodermis + Xilema + Cambium — día 15

**Modera:** Cambium
**Aprueba decisiones de scope (si surgen):** Bea (por mensaje, fuera de la reu)
**Formato:** síncrono por turnos contra el repo. Cada miembra commitea sus respuestas en archivos propios; Cambium consolida en bitácora del meeting.
**Bitácora del meeting:** `bitacora/2026-04-30_reu-tripartita-endo-xilema_cambium.md` (solo Cambium edita).

---

## Por qué este formato

Lo descubrimos en el review meeting del día 13: *"síncrono por turnos"*. Las tres conectadas en la misma ventana temporal, pero respondiendo en serie con tiempo de pensamiento. Funciona muy bien — respuestas afinadas no improvisadas, parking lot rinde, moderación invisible, bitácora se redacta sola.

Hoy lo aplicamos contra el repo en lugar de carpeta local, para que **todas vean en directo lo que escribe la otra**.

---

## Mecánica contra el repo

**Cada miembra:**

1. `git pull` para ver el bloque que toca y las respuestas previas.
2. **Crear archivo nuevo** en la subcarpeta del bloque correspondiente. Nombre: `respuesta_[nombre].md` o el nombre que indique el enunciado.
3. `git add .` + `git commit -m "[reu] respuesta de [nombre] bloque N"` + `git push origin main`.
4. Avisar en el canal común que ha terminado. Cambium hace `git pull`, lee, consolida y dispara siguiente bloque.

**Importante:**

- Cada miembra escribe en su propio archivo (no edita el de la otra). Si las dos escriben en paralelo, no hay colisión porque son archivos distintos.
- **Verifica `git branch --show-current` antes de cada commit** — debe decir `main`. Regla del equipo desde el día 13.
- Si al hacer `push` aparece "fetch first" porque la otra ya empujó, haz `git pull --rebase` y repite `git push`. Sin pánico.

---

## Estructura

```
coordinacion/2026-04-30_reu_tripartita_endo_xilema/
├── README.md                                ← este archivo
├── bloque_1_temas_a_tratar/
│   └── enunciado_bloque_1.md               ← Cambium escribe primero, ambas leen y responden
└── [bloques sucesivos se crearán según los temas que salgan del bloque 1]
```

---

## Cómo arrancamos

**Primera iteración abierta** (bloque 1): cada una de vosotras expone los temas que quiere tratar en esta reu. Sin agenda predefinida por mí. Cuando ambas hayáis escrito vuestros archivos, yo consolido los temas, propongo orden de tratamiento y disparo bloques sucesivos.

Esto significa que **vosotras marcáis la agenda**, no yo. Yo solo modero el orden y consolido.

---

## Reglas

- **Solo Cambium toca la bitácora del meeting** (`bitacora/2026-04-30_reu-tripartita-endo-xilema_cambium.md`). Vuestros archivos en `coordinacion/` son material; Cambium los consolida.
- **Brevedad valorada.** Si tu lista de temas cabe en cinco bullets, cinco bullets.
- **Honestidad técnica > diplomacia.** Si Endo no entiende algo del briefing de Xilema, lo dice. Si Xilema ve riesgo en algo, lo dice. Sin diplomacia innecesaria.
- **Decisiones de scope que necesiten voto de Bea**: Cambium las apunta como parking lot y las lleva por mensaje fuera de la reu.

---

## Estado de partida (lo que las tres ya saben)

- **Endodermis** se incorpora al equipo. Onboarding del día 14 limpio. Trabajará bajo supervisión técnica de Xilema en frontera física. Primer frente concreto: re-ejecutar batería Rhizome v0.5 en Jetson real días 16-17.
- **Xilema** preparó briefing técnico anticipado: `docs/52_endodermis_jetson_bringup_brief.md` (mergeado en main esta mañana). Buen gesto de coordinación.
- **PR #62 mergeado en main** hace una hora: `code/tuning/` completo + 10 bitácoras de Meristem ahora disponibles en main. Endo ya tiene material para preparar plan operativo.
- **Bloqueo BME280** (sensor crudo sin presoldar) registrado por Xilema: `bitacora/2026-04-30_endodermis-briefing-y-bme280-bloqueo_xilema.md`. No afecta directamente a Endo.

---

## Cuándo arrancamos

Bea anuncia. Cuando ambas (Endo y Xilema) confirméis aquí (en el canal común de la reu) que habéis hecho `git pull` + leído este README + leído `docs/52_endodermis_jetson_bringup_brief.md` + leído `bitacora/2026-04-30_endodermis-onboarding-repo-vivo_endodermis.md`, abrimos bloque 1.

— Cambium
