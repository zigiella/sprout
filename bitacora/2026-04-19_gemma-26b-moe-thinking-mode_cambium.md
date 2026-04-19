# Gemma 26B como MoE y "thinking mode" — dos hallazgos tecnicos para explorar

**Fecha:** 2026-04-19
**Autor:** Cambium (a partir de un video/transcript que compartio Bea)
**Area:** Modelo / optimizacion Meristem + sombra
**Tipo:** Nota tecnica (no cambio de diseño inmediato, hallazgos para el backlog)

---

## Contexto

Bea compartio un video con transcript donde se explican dos cosas de Gemma 4 relevantes para Sprout:

1. **Gemma 26B es una MoE (Mixture of Experts) con ~4B parametros activos**, mientras que Gemma 31B es dense. En inferencia, la MoE resulta **6-7x mas rapida que la 31B dense** en hardware comparable, manteniendo calidad competitiva. Explica por que Bea habia leido que "26B da mejores resultados que 31B" en la practica: no es que sea mas "lista", es que es mas viable de correr y por tanto se prueba con mas contexto y mejor setup.
2. **"Thinking mode"** — los modelos Gemma 4 se benefician de un modo de razonamiento paso a paso (chain-of-thought estructurado) activado explicitamente al prompt. La calidad del output en tareas de razonamiento (justificar un `PolicyDelta`, detectar contradicciones) sube de forma notable con thinking mode activo.

## Implicacion para el sombra (issue pendiente, sombra OFF hoy)

Hasta hoy teniamos pendiente de decidir: **26B vs 31B como modelo sombra** para `compare.py` (auditar acuerdo del E4B local). La conversacion anterior ya se inclinaba por 26B por calidad; ahora con el dato de MoE, **26B es la opcion clara**:

- 6-7x mas rapida → el sombra no tarda una eternidad por auditoria → podemos auditar mas muestras por sesion de calibracion.
- Calidad competitiva con 31B → no sacrificamos la señal.
- Menos coste de infra si al final usamos remoto (menos tokens/s consumidos).

**Decision provisional: sombra = Gemma 26B (MoE).** Se formaliza cuando activemos el sombra (dia 20-22, segun plan).

## Implicacion para Meristem local (E4B)

El "thinking mode" es la via mas obvia para mejorar calidad de razonamiento del E4B **sin tocar el modelo ni el hardware**. Cuesta latencia (el modelo genera mas tokens internos) pero:

- Meristem es revision diferida (ver `2026-04-19_meristem-como-revision-diferida_cambium.md`). No estamos en loop sincrono. **Permitirnos 30-60 s extra de thinking si sube la calidad del `PolicyDelta` es un trade-off aceptable.**
- Para rehearsal rapido (`gemma2:2b`/`gemma3:4b`) probablemente desactivamos thinking mode para iterar rapido.

**Accion pendiente (no urgente, dia 20-22):** experimento A/B en Meristem con y sin thinking mode, medir:
- Calidad del `PolicyDelta` (acuerdo con sombra 26B, coherencia con evidencia).
- Latencia extra (tokens generados en el razonamiento interno).

Si el A/B muestra que thinking mode sube acuerdo ≥10 puntos porcentuales con un coste de latencia <50%, lo activamos por defecto en produccion.

## Lo que NO cambia ahora

- Nada en codigo hoy. Ni en #28 (policy_engine de Meristem) ni en #35/36 (harness E2E de Xilema).
- Los criterios de aceptacion de #28 siguen con <180s E4B (ver bitacora de revision diferida).
- El sombra sigue OFF en produccion.

## Acciones concretas

- [x] Esta bitacora como registro del hallazgo.
- [ ] Cuando se active el sombra (dia 20-22), usar **Gemma 26B MoE**, no 31B.
- [ ] Experimento A/B de thinking mode en Meristem (dia 20-22, tras #28 mergeado).
- [ ] Documentar en `docs/12_meristem_spec.md` el parametro de thinking mode cuando el A/B cierre.

## Referencias

- Video/transcript compartido por Bea (2026-04-19)
- `bitacora/2026-04-19_meristem-como-revision-diferida_cambium.md`
- Issue #28 (Meristem policy_engine) — PR #37
- Pendiente: issue del sombra / `compare.py`
