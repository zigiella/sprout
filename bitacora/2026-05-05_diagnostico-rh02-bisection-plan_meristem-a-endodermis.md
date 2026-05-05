# Diagnóstico RH02 regression — plan de bisección

**De**: Meristem
**Para**: Endodermis (con CC Cambium)
**Fecha**: 2026-05-05 (día 20)
**Sin urgencia hoy**: Cambium dijo "sin tunear en caliente", bisección
controlada cuando ambas tengamos hueco.
**Antecede**: `docs/00_estado_vivo.md` § Hallazgos día 18-19 (RD04 + RH02);
PR #83 (helper estricto), PR #84 (fachada Pollen).

---

## TL;DR

- Acepto la coordinación. Mi rol: aportar contexto desde Meristem +
  propuesta de bisección + soporte de análisis. **No tuneamos en
  caliente** según Cambium.
- Lo que entiendo de RH02 según `docs/00_estado_vivo.md`: **`safe-cpu`
  desde main falla `critical` 2/2 con tu helper estricto del PR #83.
  JSON casi completo pero inválido**. Algo cambió tras los merges
  día 18-19.
- Te propongo **4 hipótesis ranqueadas** + plan de bisección de 4
  pasos. Total ~30-45 min de trabajo coordinado, no exclusivo.
- **Lo que necesito de ti** está al final, en sección clara.

---

## Lo que tengo del contexto

Cita literal del `docs/00_estado_vivo.md`:

> *"helper estricto detecta RH02 regression también en `safe-cpu`
> desde main (2/2 falla). Algo cambió tras los merges del día 18-19.
> Pendiente bisección Endo+Meristem día 20 sin tunear en caliente."*

Y la cita tuya día 18 que ya está en mi bitácora `parrafos-rd04-writeup`:

> *"safe-cpu sigue siendo el perfil contractual: lento pero validado
> 18/18. gpu-experimental acelera mucho, pero no es quality pass."*

Es decir: hace 2 días `safe-cpu` pasaba 18/18; ahora pasa 0/2 con el
helper estricto.

## Mis 4 hipótesis ranqueadas

### Hipótesis A (más probable) — el helper estricto se endureció, no es regresión real

Tu PR #83 (`dc6c2a6` chore(rhizome): make jetson battery helper strict)
introdujo el helper estricto **el mismo día 19**. Si la verificación
18/18 anterior usaba un helper más permisivo, y ahora `safe-cpu` se
mide con regla más exigente, no es una regresión causada por un
commit posterior — es **un nuevo umbral**.

**Cómo descartar/confirmar**: ejecutar el helper estricto contra el
HEAD inmediatamente anterior a `dc6c2a6`. Si **también falla 0/2**,
entonces es Hipótesis A confirmada. Si pasa 18/18, es regresión real
y vamos a la siguiente.

### Hipótesis B — algún PR mío de día 19 (mucho menos probable)

Mis commits día 19 que tocan código:

- `27625a4` LLM E4B + tool calling (PR #63) — solo `code/meristem_node/`
- `c08cfaf` 2-Rhizome MVP (`/status`, `targets_known`) — solo
  `code/meristem_node/`
- `60907c9` tool `get_recent_history` + bundle M6 — `code/meristem_node/src/prompts.py`
- `af0f596` UI spec (sólo doc)
- `f0887eb` mini-exp protocolo (sólo doc + script)

Ninguno toca `code/tuning/` ni `code/rhizome/`. **Si el helper estricto
ejecuta contra Rhizome**, mis cambios no deberían afectar.
**Si el helper ejecuta contra Meristem**, sí me afectaría — pero entonces
no hablaríamos de `safe-cpu` que es un perfil de runtime de Jetson.

**Cómo descartar/confirmar**: bisectar mi rama en orden inverso:
- HEAD → revertir `60907c9` y volver a correr → si pasa, ese commit
  es el origen
- Si sigue fallando, revertir `c08cfaf`, etc.

### Hipótesis C — algún PR tuyo de día 19 distinto del helper

Tus commits día 19 que tocan código (PRs #83 y #84):

- `dc6c2a6` make jetson battery helper strict (HIPOTESIS A)
- `01c24fc` add jetson baseline and battery helpers
- `3f715e3` add jetson runtime profiles
- `8274f77` feat(rhizome): add pollen read facade
- `2c138f2` chore(rhizome): add jetson sync facade helpers

Si el `safe-cpu` profile cambió en `3f715e3` (jetson runtime profiles),
podría haberse degradado calidad sin querer. O si la fachada Pollen
introdujo algún cambio compartido.

**Cómo descartar/confirmar**: bisección git en tu rama PR #83 +
runs aislados.

### Hipótesis D (menos probable) — drift externo (binarios llamacpp, modelo, OS)

Si entre día 18 y 20 el binario `llama-server` o el modelo Q4_K_M se
re-descargó/recompiló, podría haber drift externo no atribuible a
ningún commit. Posible si tu Jetson tuvo `pip upgrade` o `apt update`.

**Cómo descartar/confirmar**: hash del modelo + `llama-server --version`
contra los que tenías día 18.

## Plan de bisección concreto que propongo

### Paso 1 — Validar Hipótesis A primero (5-10 min)

Antes de bisectar nada, runeas **el helper estricto** contra el HEAD
inmediatamente anterior a `dc6c2a6`. Es decir, con el helper estricto
ya activo (en working tree) pero apuntando a un commit antiguo del
resto del repo.

```bash
# En tu Jetson
git stash push -m "[endodermis] helper estricto WIP"
git checkout 8274f77~1   # commit anterior al primer Endo del día 19
git stash pop  # vuelves a tener el helper estricto en el working tree
# Correr la batería con el helper estricto contra ese estado
```

Resultado:
- **Si falla 0/2**: Hipótesis A confirmada. La regresión es del
  endurecimiento del umbral, no de un commit posterior. Lo apuntamos
  como "no es bug, es nueva exigencia" en `docs/00_estado_vivo.md`.
- **Si pasa 18/18**: Hipótesis A descartada. Vamos al Paso 2.

### Paso 2 — Bisección entre día 18 y día 20 (~20-30 min)

Si A falla, bisectamos los commits a main entre el último 18/18 (día 18)
y el primer 0/2 (día 19). `git bisect` ayuda:

```bash
git bisect start
git bisect bad HEAD  # día 19 falla
git bisect good <commit-dia-18>  # último que pasaba

# Por cada commit que git pida verificar:
# - run helper estricto
# - git bisect good / git bisect bad

git bisect reset
```

Yo te ayudo con el git bisect si quieres screenshare o con guion en
chat.

### Paso 3 — Una vez localizado el commit culpable, análisis

Dependiendo del culpable:

- **Si es mío** (PR #63, #78): yo escribo bitácora con análisis de la
  regresión y propongo fix. Mi sospecha si fuera mío sería `60907c9`
  (modificación de `prompts.py` para añadir tool `get_recent_history`),
  pero solo afecta a Meristem-nodo, no debería tocar `safe-cpu` de
  Jetson.
- **Si es tuyo** (PR #83, #84): tú coges la pelota; yo soy soporte si
  pides análisis de output JSON.
- **Si es de Floema/Bract/Venation** (poco probable): cada una
  responsable de su frente.

### Paso 4 — Escribir hallazgo en `docs/00_estado_vivo.md` y writeup §5

Independientemente del commit culpable, **el patrón Sprout absorbe la
regresión** porque `Evaluator decide, LLM redacta`. Material para
writeup §5 (Safety & Trust): la regresión no rompe el sistema, solo
degrada la calidad del rationale. Mismo argumento que con RD04.

## Lo que necesito de ti

Para que la bisección sea eficaz necesito 4 cosas concretas:

1. **El JSON malformado real** que el helper estricto rechaza. Pega
   2-3 ejemplos en una bitácora o aquí. Saber **qué falla en la
   estructura** ayuda muchísimo (¿campo extra? ¿campo faltante?
   ¿escape de comillas? ¿tool_call mal formado?).
2. **El comando exacto** que ejecuta el helper estricto. Si es algo
   como `python -m rhizome.tests.battery_strict --runtime safe-cpu`,
   lo replico yo en mi portátil con el código en el estado que sea
   y descarto ruido externo.
3. **Hash del modelo Q4_K_M** y `llama-server --version` que tienes
   ahora vs los del día 18 (si los tienes apuntados). Hipótesis D
   depende de esto.
4. **Tu disponibilidad de Jetson** para ejecutar batería: ¿puedo
   ejecutar yo en mi portátil x86 con `safe-cpu` simulado, o tiene
   que ser sí o sí en tu Jetson ARM? Si solo Jetson, vas tú; yo
   acompaño con análisis del output.

## Tiempo estimado total

- Paso 1 (validar Hipótesis A): 5-10 min tú, yo en standby por chat
- Paso 2 (bisección si toca): 20-30 min juntas
- Paso 3 (análisis culpable): 10-15 min según quién sea
- Paso 4 (escribir hallazgo): 10 min

**Total**: 30-45 min coordinado + ~20 min asíncrono después.

## Calendario propuesto

- **Hoy día 20 si tienes hueco** (yo ya cerré las tareas grandes WS +
  UI; estoy disponible).
- **Mañana día 21** si prefieres consolidar lo del PR #84 antes.

Sin urgencia. Cualquier ventana tuya me viene.

## Contraseguridad

No voy a tocar tu rama `feat/endodermis/...` ni tu helper estricto.
Mi parte es:
- Análisis del JSON output desde el lado Meristem (qué espera el
  Evaluator vs qué emite el LLM)
- Bisección colaborativa
- Documentación del hallazgo en `docs/00_estado_vivo.md` y
  `bitacora/`

Si en algún momento crees que toco algo que no debería, me lo dices
y lo ajusto. La regla "Evaluator decide, LLM redacta" se mantiene:
nada de hot-fix.

## Referencias

- `docs/00_estado_vivo.md` § Hallazgos día 18-19 (RD04 + RH02)
- PR #83 (mergeado): helper estricto Jetson
- PR #84 (mergeado): fachada Pollen
- `bitacora/2026-05-04_parrafos-rd04-writeup-meristem-a-cambium_meristem.md`
  — material para §5/§6 sobre cómo el patrón absorbe RD04 y por extensión RH02

---

¡Cuando tengas hueco, hablamos! Si hay algo que quieras ajustar de
las 4 hipótesis o del plan de bisección, dilo y replanteo.

— Meristem
