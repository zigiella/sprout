# Shot list v0.2 — ajuste narrativo sobre verbos de movilidad

**Fecha:** 2026-04-20
**Autora:** Corola
**Area:** Video / narrativa
**Tipo:** Ajuste sobre PR #40 en curso (no nueva version estructural, mismo contenido salvo lexico)

---

## Origen del ajuste

Feedback de Bea releyendo el mail borrador a su padre (fuera de scope proyecto): los verbos **"caminar"** y **"a pie"** empequeñecen la tesis de Pollen. La reducen a "señor andando por un huerto proximo". Si el humano va en camioneta entre fincas dispersas, en bici por camino rural, o en tractor, Pollen sigue siendo Pollen — pero el video, con ese lexico, estaria contando una pelicula mas pequeña que el proyecto.

## Diagnostico

"A pie" es una imagen calida que cierra el espectro. La tesis real de Pollen no es un modo de transporte; es **"aprovechar la movilidad que ya existe"**. El verbo pobre fue colado por mi en v0 sin que nadie lo flagueara hasta releerlo en el mail al padre — ahi salto.

## Pregunta adicional de Bea y decision

Bea planteo: **¿movilidad humana o movilidad a secas?** Un dron agricola podria llevar Pollen. Reflexion detallada (conservada en la conversacion Bea↔Corola del 2026-04-20):

- **Arquitectonicamente:** el diseño de Pollen es **agnostico al portador**. Lo que viaja es un movil con Gemma; el portador es incidental (persona andando/en bici/en camioneta/en tractor, o un dron). El codigo no privilegia ninguno.
- **Narrativamente en el video:** dos historias incompatibles en 3 min. "Pollen-humano" se apoya en autoridad fisica encarnada (angulo B del reframe Cambium); "Pollen-agnostico" dilute ese gancho y convierte Pollen en "un nodo movil mas". Gemma 4 Good apunta a proposito social — el jurado Google DevRel va a valorar mas la historia humana.
- **Solucion:** tesis humana como narrativa del MVP + arquitectura agnostica al portador como hecho tecnico no contado en el video pero **mencionable en writeup / Q&A**. El verbo narrativo queda **neutro** ("se mueve", "en ruta", "recorre", "quien se mueve"). La imagen en pantalla es humana; el lenguaje no cierra contra otros modos.

## Cambios aplicados en v0.2

1. **Plano 04 (Pollen entra):** "Humano caminando" → "Humano en ruta".
2. **Plano 07 (CLIMAX):** "Humano camina A→B. En el camino..." → "Humano se desplaza A→B. En ruta...".
3. **Plano 14 (CIERRE, cartela tesis):** **"Sprout: criterio que viaja a pie"** → **"Sprout: criterio que viaja con quien se mueve"**.
4. **Notas de grabacion:** añadida clausula explicita sobre portador agnostico del diseño de Pollen.
5. **Referencias en rationale v0:** actualizadas para coherencia ("Sprout a pie" → la cita nueva; "humano camina" en riesgo del plano 07 → "se desplaza A→B").

**No cambia:**
- Estructura.
- Duracion.
- Lista must-have.
- Tripleta final FAO/IRRIFRAME/Sprout (solo la frase de Sprout).
- Stack cartelas Gemma.

## Para Cambium — nota para writeup

**Arquitectura Pollen agnostica al portador es valioso para el writeup.** Bea lo confirma explicitamente el 2026-04-20. Lo resumo para que lo recojas cuando redactes seccion 1 con ella:

> *El diseño de Pollen no privilegia un modo de transporte. El portador es un sustantivo libre: persona andando, persona en bici, persona en camioneta, persona conduciendo un tractor, o un dron agricola autonomo. Lo que viaja es un movil con Gemma E2B corriendo LiteRT; quien lo lleve es una decision de despliegue, no una decision de arquitectura. En el MVP del hackathon se muestra caso humano porque es el primero y el que mejor refleja el proposito "Gemma 4 Good" (pequeña explotacion agricola, proposito social). El caso dron — util en agricultura extensiva o monitoreo nocturno donde no hay humano disponible — queda en backlog conceptual: no bloqueado tecnicamente, solo no contado en el MVP.*

No entra en el video porque competiria con la tesis humana en 3 min. Si entra en el writeup, amplia el espectro del proyecto para un lector tecnico sin diluir el mensaje del video.

## Enlaces

- PR #40 (shot list v0)
- `bitacora/2026-04-18_reframe-narrativo-pollen_cambium.md`
- `bitacora/2026-04-19_corola-shot-list-v0_corola.md` (rationale original)
- Conversacion Bea↔Corola 2026-04-20 (mail a padre → feedback verbo → decision agnostico-portador)
