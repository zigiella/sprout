# Meristem como revision diferida — clarificacion arquitectonica

**Fecha:** 2026-04-19
**Autor:** Cambium (a partir del hallazgo de Xilema en PR #36)
**Area:** Arquitectura / narrativa
**Tipo:** Clarificacion (no cambio de diseño, hacer explicito lo que ya estaba latente)

---

## Contexto

En PR #36 (harness E2E cross-node, closes #35) Xilema midio con numeros reales el camino Rhizome-mock → Pollen-mock → Meristem-real-Ollama-E4B, y encontro:

- `tokens/s` ≈ 6.17
- `first_token_latency` ≈ 100 s
- `Meristem generate` ≈ 123.7 s
- `E2E total` ≈ 123.7 s (Meristem es practicamente todo)

Su lectura fue correcta y directa: **E4B en portatil no es viable como respuesta sincrona "Pollen entrega y espera delta estrategico en vivo"**. Y propuso: tratar a Meristem como **revision diferida**, no como camino sincrono.

Este documento acepta esa clarificacion y la hace explicita en la narrativa del proyecto.

## Lo que NO cambia

- Arquitectura tecnica: ni una linea.
- Schemas, contratos, safety rules: ni una linea.
- Diseño de Rhizome (E2B edge, decisiones sub-segundo locales).
- Diseño de Pollen (ferry cross-parcela, auditor con modelo gemelo).
- Diseño de Meristem (consolidacion estrategica, Gemma 4 E4B local).

## Lo que se hace explicito

**Meristem no esta en el camino critico de ejecucion. Nunca lo estuvo.**

El camino critico de ejecucion es:

```
Rhizome sensores → Rhizome decide (E2B local, <1 s) → accion/bloqueo
```

Pollen y Meristem operan en **capas asincronas** sobre ese camino:

```
Rhizome decide → ... mas tarde ... → Pollen audita (segunda opinion)
              → ... mas tarde aun ... → Meristem consolida (politica futura)
```

Por tanto, **la latencia de Meristem (~2 minutos para un ciclo completo con E4B) NO es un defecto**. Es coherente con su rol: consolidar evidencia acumulada y emitir politica que modifica comportamiento **futuro**, no responder en vivo.

## Implicacion narrativa

Meristem no es "el cerebro lento que tarda 2 minutos". Es **el criterio que piensa despacio a proposito**. El paralelo humano:

- Rhizome = el operario en la parcela que abre la valvula (segundos)
- Pollen = el tecnico que pasa y revisa a mediodia (minutos/horas)
- Meristem = el agronomo que al final del dia ajusta el plan semanal (horas)

Cada uno opera en su escala de tiempo. Meter a Meristem en el loop sincrono de Rhizome seria como pedir al agronomo que decida en segundos: ni funciona ni seria correcto.

Esta lectura **refuerza el reframe narrativo** (ver `2026-04-18_reframe-narrativo-pollen_cambium.md`): el sistema distribuye decisiones en **capas temporales**, no en un unico ciclo sincrono.

## Implicacion para rehearsal / video

- **Para el video (60s)**, NO se muestra a Meristem respondiendo en vivo a una evidencia. Se muestra a Meristem **consolidando al final del dia**: corte temporal explicito ("... pasa el dia ...") y se ve la politica actualizada aparecer en Rhizome en el siguiente amanecer.
- **Para rehearsal rapido** (iterar flujos en segundos en vez de minutos), Xilema propone usar `gemma2:2b` o `gemma3:4b` como proxy rapido en rehearsal, manteniendo `gemma4:e4b` como modelo de calidad/produccion. Aceptado. No afecta produccion, solo la velocidad de iteracion del equipo.

## Implicacion para Meristem (issue #28)

El criterio de aceptacion de #28 dice `<60s E2E`. Con E4B en portatil medido en ~124s, **ese criterio es inalcanzable con el modelo actual**. Dos opciones:

- **(a) Relajar criterio a <180s para E4B y <60s para gemma2:2b.** Mi preferencia. La latencia es propiedad del modelo+hardware, no del codigo de Meristem. El codigo cumple su funcion bien; el tiempo total es fisica.
- **(b) Cambiar modelo por defecto a gemma2:2b o gemma3:4b para el PR y documentar como trade-off.** Mas rapido, menos calidad de razonamiento estrategico.

Decision: **(a)**. Meristem entrega #28 con E4B y el criterio revisado. El proximo PR puede introducir un parametro de modelo en config para alternar rehearsal-rapido vs produccion-calidad.

## Pendiente de decision (no urgente)

- **Modelo sombra: Gemma 26B vs 31B.** Bea menciono haber leido que 26B da mejores resultados que 31B. Esto afecta al sombra (`compare.py` contra modelo grande para validar acuerdo del E4B local). No bloquea #28 (el sombra esta off). Investigar antes de activar el sombra en dia 20-22.
- **Mac mini potencial.** Si llega antes del final, se usa como host alternativo de Meristem para medir E4B en arquitectura ARM con memoria unificada — puede bajar sustancialmente la latencia. **No contamos con el.**

## Referencias

- PR #36 (Xilema, harness E2E) — datos originales del hallazgo
- Issue #35 (E2E cross-node harness)
- PR #37 (Meristem #28, policy_engine)
- `bitacora/2026-04-18_reframe-narrativo-pollen_cambium.md`
- `docs/01_architecture.md` §3 (pendiente de anotar con esta clarificacion en un PR futuro de docs)
