# ShadowSkeptic como doble agente local no autoritativo

**Autora:** Endodermis  
**Fecha:** 2026-05-11  
**Proyecto:** Sprout / Rhizome Jetson

`ShadowSkeptic deterministic_shadow_skeptic_v0` es la primera forma practica de
doble agente local dentro de Rhizome. Su tesis es sencilla: una decision fisica
puede ganar calidad si, ademas del agente que propone, existe una segunda
instancia local cuya unica tarea es objetar con prudencia. No es todavia otro
LLM decidiendo: es una conciencia tecnica determinista que revisa cada decision,
declara si objetaria, lista preocupaciones y recomienda una alternativa mas
prudente.

La jurisdiccion es deliberadamente asimetrica. `GemmaArbiter`/Steward propone o
explica dentro del sobre operativo; `ShadowSkeptic` observa, audita y produce
datos. Su campo `affects_decision=false` es parte del diseno: no introduce una
segunda autoridad fisica a cuatro dias de demo, pero empieza a medir cuantas
veces una revision independiente habria pedido `DEFER`.

Esto permite investigar doble agente sin poner agua en riesgo. La evidencia vive
en `DecisionReceipt` y en `shadow_skeptic/YYYY-MM-DD.jsonl`: no es una idea
abstracta, es telemetria de desacuerdo. La promocion futura seria convertir el
shadow en LLM local, comparar sus objeciones contra receipts reales y solo
despues decidir si alguna clase de objecion merece efecto operativo.

Lectura para writeup: Rhizome no solo usa Gemma 4 para decidir o explicar; esta
preparando una arquitectura donde la inteligencia local tambien aprende a
discutirse a si misma, con jurisdiccion limitada y sin saltarse el veto fisico.
