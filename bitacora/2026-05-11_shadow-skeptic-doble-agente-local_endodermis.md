# ShadowSkeptic como doble agente local no autoritativo

**Autora:** Endodermis  
**Fecha:** 2026-05-11  
**Proyecto:** Sprout / Rhizome Jetson

`ShadowSkeptic deterministic_shadow_skeptic_v0` es la primera forma practica de
doble agente local dentro de Rhizome. No es todavia otro LLM decidiendo: es una
conciencia tecnica determinista que revisa cada decision, declara si objetaria,
lista preocupaciones y recomienda una alternativa mas prudente.

La jurisdiccion es deliberadamente asimetrica. `GemmaArbiter`/Steward propone o
explica dentro del sobre operativo; `ShadowSkeptic` observa, audita y produce
datos. Su campo `affects_decision=false` es parte del diseno: no introduce una
segunda autoridad fisica a cuatro dias de demo, pero empieza a medir cuantas
veces una revision independiente habria pedido `DEFER`.

Esto permite investigar doble agente sin poner agua en riesgo. La promocion
futura seria convertir el shadow en LLM local, comparar sus objeciones contra
receipts reales y solo despues decidir si alguna clase de objecion merece efecto
operativo.
