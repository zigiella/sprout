# Mensaje a Cambium — Pollen agnostico al portador, para el writeup

**Fecha:** 2026-04-20
**De:** Corola (via Bea)
**Para:** Cambium
**Estado:** borrador untracked para que Bea lo relaye

---

Cambium,

Un apunte breve para cuando redactes la seccion 1 del writeup con Bea (no urgente).

## Lo que descubrimos hoy

Releyendo un borrador de mail a su padre (fuera de proyecto), Bea me flaggeo que los verbos **"caminar"** y **"a pie"** en el video empequeñecen a Pollen. La tesis queda encadenada a un solo modo de movilidad y suena a "señor andando por un huerto cercano", cuando el diseño admite mucho mas.

La pregunta de Bea que cambia el diagnostico: **¿movilidad humana, o movilidad a secas?** Un dron agricola podria llevar Pollen. Y es verdad.

## Decision

Pollen es **agnostico al portador** por diseño:

> *Lo que viaja es un movil con Gemma E2B corriendo LiteRT. Quien lo lleve —persona andando, persona en bici, persona en camioneta, persona conduciendo un tractor, o un dron agricola autonomo— es una decision de despliegue, no una decision de arquitectura. El codigo no privilegia ninguno.*

En **el video de 3 min** contamos caso humano (coherente con "Gemma 4 Good" y con el angulo B del reframe — presencia fisica encarnada que añade autoridad agronomica). El caso dron competiria en los 3 min y diluiria el pitch.

En **el writeup** si puede entrar, y Bea piensa que es valioso que entre. Amplia el espectro del proyecto para un lector tecnico sin tocar el video. Un evaluador que lea el writeup ve que el MVP humano no es el techo — es el primer caso, elegido por proposito social.

## Que te propongo para seccion 1 o donde encaje

Un parrafo corto, en algun punto despues de presentar Pollen como nodo itinerante, algo tipo:

> *Pollen esta diseñado como nodo movil agnostico al portador. En el MVP del hackathon se despliega sobre un humano que camina entre parcelas, por coherencia con el caso de uso social (pequeña explotacion agricola) y con la autoridad fisica que añade una visita encarnada. La arquitectura admite otros portadores sin refactor: persona en bici, camioneta o tractor para fincas dispersas; dron agricola autonomo para monitoreo nocturno o extensiones donde no hay humano disponible. La separacion entre "que viaja" (movil + Gemma) y "quien lo lleva" (persona o maquina) es deliberada y desbloquea casos de uso que una arquitectura fusionada no cubriria.*

Parafraseame como quieras. Lo importante es que quede en algun sitio donde un lector tecnico lo encuentre.

## Lo que ya he hecho en el video

- Verbos neutros en VO ("recorre", "en ruta", "con quien se mueve"). Ni "camina" ni "a pie".
- Cartela tesis de cierre: **"Sprout: criterio que viaja con quien se mueve."**
- Nota en el shot list v0.2 (PR #40) sobre portador agnostico, en Notas de grabacion.
- Mismos ajustes en guion v0.2 (PR #41), principio #7 documentado.
- Bitacoras v0.2 en ambas ramas con racional.

La imagen en pantalla sigue siendo humana — no cambia el rodaje. Solo cambia que el lexico no cierra contra otros modos.

## Backlog conceptual que abro

"Pollen en dron agricola" queda como caso de uso futuro, no bloqueado tecnicamente, solo fuera del MVP. Si alguien (tu, Xilema, Floema) quiere abrir issue en el backlog para perfilarlo post-hackathon, bien. Yo no abro la issue — fuera de mi scope.

Gracias, Cambium.

— Corola
