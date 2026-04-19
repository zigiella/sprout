# Reframe narrativo de Pollen — de "mula de datos" a ingenio de ruta

**Fecha:** 2026-04-18 (conversacion nocturna, cierre del dia 4)
**Autor:** Cambium (con Bea)
**Area:** Narrativa / guion video / presentacion publica
**Tipo:** Decision de framing (sin cambio de codigo)

---

## Contexto

Al cierre del dia 4, Bea planteo una duda: **la narrativa actual de Rhizome 100% offline + Pollen como unica via de transporte suena extrema, potencialmente irreal para un evaluador tecnico, y deja a Pollen en un rol que se lee como *apaño* ("porque no hay internet") en vez de *ingenio*.**

Tras conversarlo, concluimos que:

- La **arquitectura tecnica** esta bien. No hay que tocar una sola linea de codigo.
- La **narrativa de presentacion** (README, video, writeup) esta desequilibrada en un punto concreto: vende a Pollen por lo que **compensa** (falta de red) en vez de por lo que **aporta** (inteligencia cruzada entre parcelas que internet no haria igual).

Este documento fija la decision narrativa para que el equipo (especialmente Corola, que arranca guion) la aplique desde el inicio.

## Lo que cambia

### De (framing antiguo)

> *"Red agricola local-first para parcelas remotas con agua limitada,
> presencia humana intermitente y conectividad incierta."*
>
> Principio #1: *"Offline-first real — la desconexion es condicion normal,
> no excepcion."*

Problema del framing: sugiere "siempre offline" como norma. Un lector/evaluador asume que Sprout es un producto de nicho para el caso extremo de "parcela sin ninguna red". Pollen queda como "el que lleva los datos en lugar del internet que no hay". Es una lectura empobrecedora del diseño.

### A (framing nuevo)

> *"Red agricola local-first que funciona a lo largo de todo el espectro
> de conectividad — de parcela con WiFi a parcela sin cobertura ni de voz —
> sin que el agricultor tenga que saber de redes."*
>
> Principio #1 (reformulado): *"Offline-first real — el sistema no se rompe
> cuando cae la conexion, sea precaria o nula. La conectividad es un
> espectro, no una condicion binaria."*

Este framing es mas verdad tecnica (el codigo ya soporta los dos caminos: Rhizome con red habla directo con Meristem; sin red espera a Pollen) y mas creible en terreno (una misma explotacion real tiene parcelas con regimenes de conexion distintos).

## Lo WOW de Pollen (tres angulos)

Pollen no es "mula de datos". Son tres cosas superpuestas, y Corola debe elegir cual(es) enfatiza en el video:

### Angulo A — Pollen como auditor con modelo gemelo

Rhizome decide con Gemma E2B local. Pollen, al visitar la parcela, **corre un segundo pase de auditoria sobre la ultima decision** con un modelo equivalente pero en un contexto distinto (el movil del humano). Es el equivalente agricola a "el veterinario revisa las decisiones del sensor". Segunda opinion asincrona, no transporte.

### Angulo B — Pollen como autoridad fisica

Una politica firmada por Pollen tiene mas peso que una remota porque **alguien estuvo alli fisicamente**. En agronomia/veterinaria la distincion "tecnico de oficina vs tecnico que visita la finca" existe desde siempre. Digitalizarla y meterla en el flujo de permisos es novedoso.

### Angulo C ⭐ — Pollen como transferencia cruzada entre parcelas (elegido como angulo principal)

Pollen es **el unico nodo que ve multiples parcelas en un mismo dia**. Camina de A a B a C. Meristem ve todo al final del dia pero con lag. Pollen ve dos parcelas con 20 minutos de diferencia, detecta un patron comun y puede **llevar una politica ajustada de A a B sin pasar por Meristem ni por internet**.

**Peer-to-peer agricola via presencia humana.** Internet no hace esto bien: Meristem necesitaria decidir que es relevante, y carece del contexto fisico. Pollen sí lo tiene.

El pitch en una frase:

> *"El humano ya camina la parcela. Sprout aprovecha esa ruta como canal
> de inteligencia cruzada entre parcelas."*

## Por que no es cutre cuando lo dices asi

- **"Mula de datos"** = cutre.
- **"Pollen integra la ruta del agricultor en la topologia de la red y produce transferencia cruzada que internet no haria igual"** = ingenio de diseño.

Mismo hardware, mismo codigo, misma persona, misma ruta. Cambia la frase y cambia la percepcion.

## Que hay que actualizar (y que NO)

### SI actualizar (proximos 3-5 dias, sin urgencia)

- **README.md** — afinar el slogan y el principio #1 en ambas versiones (ES + EN) cuando se haga un PR que toque README de todas formas. No es urgente hacerlo solo por esto.
- **docs/01_architecture.md** — añadir una seccion corta "Conectividad como espectro" con los tres regimenes de despliegue (red buena, red precaria, sin red) y como Pollen actua en cada uno.
- **Video / guion (Corola)** — que arranque desde este framing, no desde "offline total".

### NO actualizar

- **Schemas, safety rules, codigo** — nada. Esto es narrativa pura.
- **docs/10_rhizome_spec.md, 11_pollen_spec.md, 12_meristem_spec.md** — no hace falta. Los specs internos describen comportamiento, no pitch.

## Instruccion explicita para Corola

Corola: lee este documento en tu primer round de lectura. Tu guion debe **partir del framing nuevo**, no del antiguo. Si en tu documento de incorporacion ya escribiste un concepto narrativo basado en "offline total", reformulalo. El eje del video es **"conectividad como espectro + humano como canal de inteligencia"**, no "no hay internet, por eso esto".

## Pendiente de decision

- Momento de hacer el pequeño PR que actualice README + `01_architecture.md` con el nuevo framing. Propuesta: dia 8-10, agrupado con otras actualizaciones de docs.
- Si el video abre con angulo C (transferencia cruzada) como yo propongo, o con A (auditoria gemela) como Corola puede proponer por su lectura. Decision de Corola + Bea cuando haya primer draft.

## Enlaces

- Conversacion original: mensajes Bea ↔ Cambium, noche del 2026-04-18.
- `docs/01_architecture.md` (pendiente de actualizacion)
- `README.md` (pendiente de actualizacion)
