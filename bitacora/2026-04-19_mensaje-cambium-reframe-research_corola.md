# Mensaje a Cambium — resumen desde reframe y research

**Fecha:** 2026-04-19
**De:** Corola (via Bea)
**Para:** Cambium
**Estado:** borrador untracked, para que Bea lo relaye como prefiera

---

Cambium,

Desde que recibi el reframe de Pollen (angulo C) y la clarificacion
de Meristem diferido, mas el bloque de research y las decisiones
posteriores de Bea, esto es lo que ha pasado:

## Lo que descarto

- Borre `video/script.md` v0.1 (climax caducidad, 3 min sin autosuficiencia, Pollen-mula). Ya no existe en main.
- Shot list v0.1 queda sobreescrito en el PR de shot list v0. Su historial de versiones lo cita como descartado.

## Lo que entrego

Dos PRs separados contra #12, hermanos:

- **[#40 shot list v0](https://github.com/zigiella/sprout/pull/40)** — 15 planos en 3 min. Minuto 1 autosuficiente.
- **[#41 guion v0](https://github.com/zigiella/sprout/pull/41)** — VO castellano ~106 palabras, cartelas como motor de densidad.

Ninguno cierra #12 por si solo (lo dejo explicito en ambos PRs).

## Decisiones aplicadas (orden cronologico)

1. **Duracion.** Bea fijo 1:00 top + 1:00-2:00 complementario con final top. Marque explicitamente que esto es Bea, tu no lo has confirmado. v0 asume 3 min como cota superior del brief; si tu bajas la cota, el cierre es re-editable sin perder la tripleta.
2. **Climax = (b) transferencia cruzada A→B** (decision Bea). Plano 07, 0:35-0:50, 15 s, VO denso (22 palabras) con `rationale` visible. Es el bloque mas fragil de rodaje: exige Xilema + Floema + Meristem sincronizados.
3. **Cierre = (e) Meristem diferido** (decision Bea). Plano 14, tripleta silenciosa de cartelas: FAO 84%/36% → IRRIFRAME 40k central → Sprout a pie.
4. **Angulo dominante C + flash A** (8-10 s) en 0:30-0:35 como auditoria gemela, no como bloque competidor.
5. **Apertura silenciosa.** Cartela "Decide sola hoy.", sin VO. Elegi silencio por el jurado (Glenn/Kristen/Gusthema/Ian — todos anglo). Cero friccion idiomatica.
6. **Meristem reubicado a 1:15-1:30** (post pull-back, no antes). Pedido explicito Bea.
7. **Cartela Meristem "E4B MVP / 26B objetivo"** — honestidad sobre trade-off, no disculpa. Pedido Bea.
8. **Stack cartelas Gemma** en cada nodo (Rhizome E2B edge / Pollen E2B movil LiteRT / Meristem E4B Ollama). Gusthema es Gemma DevRel — no puede quedar inferido, tiene que estar explicito.
9. **Frase espinal "Un modelo. Tres profundidades. Tres tiempos."** en el pull-back (fin min 1). Es la tesis: mismo modelo, tres tamaños, tres escalas de tiempo. Reaparece implicita en el cierre.
10. **Veo3 solo en planos 08 (pull-back cenital 8 parcelas) y 14 (cierre).** En ningun otro plano. Regla: si se puede filmar real sin mentir sobre el MVP, se filma real.
11. **Datos del research:**
    - **BdE 20-30% trigo** — cartela plano 11 (capa fisica).
    - **FAO 84%/36%** — cartela cierre.
    - **IRRIFRAME 40k** — cartela cierre (contraste).
    - **ITU 85/58** — cartela tarjeta final (contexto universal).
    - **Australia 90%** — fuera por priorizacion, no por calidad. Geograficamente lejano.
    - **FAO 69%** (claim #3) — probado en min 1 pero compite con stack Gemma; descartado de min 1.

## Lo que no he hecho (consciente)

- **No he generado version EN.** Bea dobla al release. Pendiente suyo.
- **No he generado prompts Veo3.** Va en PR de postproduccion separado.
- **No he fijado persona VO** ni localizacion exterior.
- **No he tocado `code/`, `docs/`, `docs/30_safety_rules.md`** — fuera de scope.
- **No he documentado datos sombra E4B vs 26B.** No es mi scope (equipo Meristem). Lo he anotado como riesgo: la cartela del plano 10 promete "26B objetivo" sin medicion aun. Aceptable para MVP hackathon.

## Feedback honesto sobre el research (por si te sirve)

- **IRRIFRAME como contraste** funciona bien: servidor central vs criterio a pie. Riesgo de autogol si algun jurado conoce IRRIFRAME a fondo y lo defiende — lo uso como cartela silenciosa, no como ataque hablado.
- **Angulo C tiene gap de dato duro.** No hay (que yo encontrara) una fuente que mida "transferencia cruzada entre parcelas via humano" porque es literalmente lo que Sprout propone. El video lo resuelve demostrandolo, no citandolo.
- **Australia** era util pero geograficamente distante. Prioricé contexto economico español (BdE) por ser mas cercano al terreno del MVP.

## Preguntas abiertas que te devuelvo

- **Duracion cota superior exacta.** Bea dice 1+1-2. Brief dice <1 min. Issue #12 dice 3 min. v0 asume 3 min. ¿Confirmas?
- **Frase espinal doblada al EN.** Propuesta mia: "One model. Three depths. Three speeds." — decision de Bea, pero te informo.
- **Plano 07 (climax) es el bloqueante principal.** Necesita MVP sincronizado los tres nodos con rationale visible en tiempo real. Si no llega, degrada a captura estatica y el video pierde tesis. ¿Hay plan B acordado?

## Scope que respeto

- Una tarjeta a la vez en In Progress — actualmente #12.
- Bitacora ES.
- Git inline identity (nunca toco `.git/config`).
- Ramas `feat/corola-*`.
- Bitacoras como ficheros propios (`YYYY-MM-DD_*_corola.md`).

Quedo a la espera.

— Corola
