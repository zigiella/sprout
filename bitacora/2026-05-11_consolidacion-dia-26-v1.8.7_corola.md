# Consolidación día 26 — bump v1.8.7 + 5 votos Corola aplicados sobre snapshot Bract

**Fecha:** 2026-05-11 (día 26)
**Autora:** Corola
**Para:** Bract + Bea + Cambium ella (gatekeeper) + Venation (info)
**Origen:** primera sesión activa de Corola tras 5 días de ausencia operativa (días 22-25). Bea retoma contacto hoy día 26 *"He tenido que tirar millas con el guion, con el rodaje y con Bract porque se me tiraba el tiempo encima."* Da acceso al snapshot textual del video que Bract preparó (`corola-video-snapshot.md`, regenerable). Bea me pide review + formalización de cambios.

---

## Contexto operativo — 5 días sin ciclo de validación

Mi último cierre fue día 21 con 6 PRs Corola mergeadas (#101, #107, #108, #109, #110, #113), cartelería delegada a Venation, 4 mensajes preparados para chat con Venation/Bract. Días 22-25 sin contacto. Día 26 Bea retoma con:

- **El rodaje sucedió** (probablemente día ~25-26 según calendario que Bea movió).
- **Bract ha montado en CapCut** los 3 bloques principales (Rhizome / Pollen / Meristem) con planos reales del rodaje + animaciones Venation + UI Pollen/Meristem + VO doblada con voz pro DbwW de ElevenLabs.
- **Bea + Bract han iterado copy** intensamente días 24-25-26 sin ciclo de validación con Corola (legítimo por presión de timing).
- **Master actual:** 3:08.5 (188.5s, v1.8.7 según numeración interna del proyecto).

**Convención operativa que establecemos hoy día 26:**

`script.md` + `copies_bilingual.md` + `montage_brief.md` = **doc estable** (espina narrativa, historial, decisiones consolidadas, frases fuertes).
`corola-video-snapshot.md` (Bract, regenerable) = **fuente viva** (estado real del montaje en CapCut, timeline por asset, VOs con MP3 generados, decisiones de copy cronológicas días 24-26).

Los dos se complementan, no se solapan. Esta bitácora documenta la sincronización entre ambos al cierre del día 26.

---

## Lectura del snapshot Bract

He leído el snapshot completo (`C:\DATA\PETS\CLAUDE\equipo-agentes\video-proyecto\produccion\handoffs\corola-video-snapshot.md`). Detalla:

- **Estructura por bloques** (VIDEO 1 Rhizome 43s + VIDEO 2 Pollen 70s + VIDEO 3 Meristem 75.5s)
- **Timeline visual** (cada clip, cartela overlay y PIP con timestamp master)
- **Tabla de VOs side-by-side ES + EN** (21 VOs cubriendo los 3 bloques)
- **Cartelas con texto visible** (9 cartelas que funcionan como VO por sí mismas, sin subtítulo encima)
- **Vocabulario controlado** del proyecto
- **Estilo de subtítulos** (font-size, color, pastilla, posición por tipo de VO)
- **Decisiones de copy cronológicas** días 24-26
- **Pipeline TTS** (voz ElevenLabs DbwW, settings, 21 MP3 generados, estado de replicación por bloque)
- **Pendientes que afectan a copy**

Trabajo limpio, formato denso pero accesible. Reconoce los cambios estructurales del periodo + me pide voto razonado sobre 5 puntos.

---

## Cambios estructurales del periodo días 22-26 (consolidados en v1.8.7)

| # | Cambio | Origen | Impacto |
|---|--------|--------|---------|
| 1 | **Estructura simplificada a 3 bloques** (VIDEO 1/2/3 = Rhizome/Pollen/Meristem). Las 12 escenas v1.8.x viven como beats dentro de los bloques. Master 3:08.5 (188.5s) | Bea + Bract días 23-25 | Operacional para montaje. Narrativa preservada. |
| 2 | **E8 Caducidad ELIMINADO** del video. Concepto `expiry` comprimido en VO E4b *"with expiry"* | Bea día ~24-25 (revisa decisión propia día 20) | F4 sale del video. **Recuperar F4 en writeup/landing** para Safety & Trust del Gemma Hackathon. |
| 3 | **VO master EN definitivo con voz pro ElevenLabs `DbwWo4rVEd5NrejHYUnm`** (settings 0.7/0.9/0.1/0.9, multilingual_v2). 21 MP3 generados | Bea + Bract día 26 | Bea confirmó *"BUAH! queda fetén."* — calidad alta. |
| 4 | **Voz humana E5 doblada con DbwW** (no Bea castellano literal). Excepción narrativa día 18-19 retirada conscientemente | Bea día 26: *"la mía quedaba fatal"* | Pérdida de "voz humana real" como gesto deliberado de autenticidad. Aceptable por consistencia operativa con voz pro. |
| 5 | **Cartela `Imagine this pot is a whole plot.` (v1.8.2) dividida en 2 cartelas** para mejor cadencia visual: `E02_imagine_pot_opaque` + `E02_imagine_pot_whole_plot` | Bract día ~24 | Refinamiento de tempo. Acertado. |
| 6 | **Cenital v1.8 Opción B (cadencia escalonada `One plot. Two. Eight. Autonomous.`) eliminada.** Sustituida por discurso lineal explicativo sobre fondo claro | Bea + Bract días 25-26 | Poesía v1.8 → discurso didáctico. Funciona mejor para jurado hackathon (anglosajón técnico que lee rápido). Recuperar poesía en writeup. |
| 7 | **Vocabulario unificado por Bract día 26** — *criterios* → *políticas* en E3b VO | Bract día 26, escalado a Corola | Asimetría intencional necesaria — no unificar todo. Ver Voto 1 abajo. |
| 8 | **Cartelería física producida e impresa** | Venation diseñó días 22-23 + Bea imprimió + laminó antes de rodaje | Ejecutado limpio según bitácora `2026-05-06_carteleria-fisica-rodaje_corola.md`. |

---

## 5 votos Corola día 26 aplicados como decisión

### Voto 1 — Vocabulario `policy` vs `criteria`: mantener asimetría intencional

**Inconsistencia detectada:** "policies" ahora en E3b + E4b + E5 + cenital; "criteria" sigue en E4 ("change the local criteria") y Z99 cierre ("the criteria keep irrigating").

**Voto:** mantener la asimetría. NO unificar.

- **Policy** = regla operativa concreta que viene de Meristem, vive con caducidad, viaja con Pollen.
- **Criteria** = criterio LOCAL del Rhizome (decisión persistente). Las policies pueden modificarlo.

Conceptualmente funciona: *Pollen brings policies → Rhizome integrates them → its local criteria adapt → it keeps irrigating*. El espectador casual no necesita verbalizar la diferencia, la siente.

**Z99 NO se toca.** *"the criteria keep irrigating"* es identitario del proyecto desde v1.7. Cambiarlo a *"policies keep irrigating"* mata el cierre.

**Acción:** documentar en vocabulario controlado del snapshot Bract una línea más explícita:
```
- Criteria / criterio — criterio local del Rhizome
  (decisión persistente que las policies modifican). NO unificar con policy.
```

### Voto 2 — Compresión expiry en E4b: acepto para video, recuperar F4 en writeup

**Cambio:** *"Pollen brings new policies (with expiry) to each Rhizome."* comprime E8 entero.

**Voto:** acepto para video. **Recuperar F4 (*"Every intelligence has jurisdiction. And expiry."*) en writeup/landing/submission** — sigue siendo argumento clave para Safety & Trust del Gemma Hackathon. Hablarlo con Cambium ella en cierre de writeup.

**Sugerencia opcional para reforzar levemente en video:** la cartela `CartelaPollen.png` (0:43-0:46) podría incluir un sub-text pequeño *"Policies expire."* en la ficha técnica, debajo de "Mobile node". Tres palabras, no rompe el ritmo, ancla el concepto. Decisión pendiente Bea/Bract.

### Voto 3 — Refinamiento VO cenital

**Cambio Bract día 26:** *"The Sprout system supports one plot."* / *"It also supports two plots."* / *"And it supports many more plots."* sustituye la cadencia poética v1.8 *"One plot. Two. Eight. Autonomous."*

**Voto:** acepto la dirección (claridad para jurado anglosajón). Refinamiento menor:

- *"The Sprout system supports one plot."* → ***"Sprout starts with one plot."*** (verbo más activo, recupera wordmark sin "system supports" palabra ladrillo).
- *"It also supports two plots."* (mantener — bien)
- *"And it supports many more plots."* → ***"And many more plots."*** (telegráfico, ahorra redundancia)

Total VO: igual de tiempo, gana naturalidad.

### Voto 4 — Cierre Z99: recuperar adverbios potentes del tagline v1.7+

**Cambio Bract día 26:** *"Sprout: When there is no network, and no one is near, the criteria keep irrigating."*

**Comparación con tagline v1.7+ original:**

| Antes (v1.7+) | Día 26 |
|---------------|--------|
| `When network is absent` | `When there is no network` |
| `and the human is far` | `and no one is near` |
| `local criteria still irrigate` | `the criteria keep irrigating` |
| (sin prefijo) | `Sprout: ...` |

Lo que se pierde: **"local"** (anclaba edge-first), **"still"** (adverbio de persistencia), **"the human"** vs **"no one"** (concreción visual narrativa > abstracción).

**Voto aplicado:** recuperar los adverbios potentes manteniendo el prefijo "Sprout:" para brand recall:

> **`Sprout: When network is absent, and the human is far, local criteria still irrigate.`**

Recupera "local" + "still" + "the human" + mantiene prefijo Sprout. Compromiso óptimo entre poesía v1.7+ y identificación marca día 26.

### Voto 5 — Cartelas E10 verbos viscerales

**Versión actual:** `Rhizome. Arbitrates the plot.` / `Pollen. Mediates.` / `Meristem. Refines.`

**Alternativa Bract propuesta:** `Holds / Carries / Composes`.

**Voto:** alternativa Bract gana, con 1 ajuste:

- `Rhizome. Holds the plot.` ✅
- `Pollen. Carries.` ⚠️ → ***`Pollen. Carries between plots.`*** (cierra el verbo, refuerza el ferry)
- `Meristem. Composes.` ✅ (alineado con VO E3b cenital *"Meristem composes policies"*)

**Razones:**
1. Verbos físicos/antropomórficos > institucionales.
2. Memorables (el espectador retiene "carries" mejor que "mediates").
3. Coherencia con VO cenital existente (`Meristem composes policies`).
4. Coherencia con tagline visceral (`criteria keep irrigating`) y F1 (`Rhizome keeps the plot alive`).

**Para invariante E7 (escalada a Bea sin respuesta) — propuesta lista para aplicar:**

```
Physical layer prevails.
Rhizome holds.
Pollen carries.
Meristem composes.
```

Verbo final del 4-stack en simetría con "prevails" (presente simple, monosílabo o bisílabo). Mantenemos "prevails" porque es el verbo de la capa física que Xilema reivindicó día 15 y sigue correcto.

**Si Bea no responde antes del cierre del proyecto, decido yo con venia de Bract y abro bitácora documentando la decisión.**

### Voto 6 (bonus) — Bilingüe en cartelas

**Pendiente Bract:** ¿bilingüe ES/EN en cartelas E07b + E10 + Z99, o solo EN?

**Voto:** **mantener solo EN** una vez se quite ES del subtítulo. El doblaje EN con voz pro DbwW hace el video universal anglo. Bilingüe en cartelas añade complejidad visual sin ganancia narrativa. Coordino con Venation si hace falta refrescar cartelas.

---

## Observaciones registradas (sin ser preguntas directas de Bract)

### Obs.1 — Voz humana E5 doblada conscientemente con DbwW

La decisión cerrada día 18-19 (con seis votos firmes de Bea) era voz humana E5 en castellano literal sin traducir. Hoy día 26 Bea confirma: *"consciente, la mía quedaba fatal."* Decisión revisada legítima. Se retira la excepción narrativa cerrada día 18-19. El texto EN se mantiene en italic en pantalla marcando que es voice note del operador (no narradora), pero hablada por DbwW.

**Aprendizaje cultural:** "*Decisiones de calidad pueden retirar decisiones narrativas previas si la ejecución no soporta la intención.*" La voz humana real de Bea era intención narrativa fuerte (autenticidad), pero la ejecución técnica no lo soportaba. Aceptar el dub pro es honesto operativamente. La intención (voice note del operador) se preserva visualmente (italic + comillas + tipografía diferenciada).

### Obs.2 — Cenital E9 reescrito completo

Cadencia v1.8 Opción B (decisión firme Bea día 20, *"animar 20s con cadencia completa, recortar en post si procede"*) se ha eliminado completamente. Ahora es discurso lineal explicativo.

**Aceptar la decisión:** funciona mejor para jurado anglosajón hackathon que la cadencia poética (que requeriría que el espectador se detuviera a interpretar la metáfora de la escala 1→2→8→autonomous).

**Aprendizaje cultural:** "*Material flexible vence material apretado*" funcionó al revés esta vez. Bea decidió día 20 animar 20s con cadencia completa para tener flexibilidad de recorte; en post-rodaje, decidió que el lenguaje completo era el que NO funcionaba para el contexto del concurso, y reescribió la VO sobre el mismo cenital animado. La flexibilidad estaba en el material animado de Venation (el cenital funciona con cualquier VO encima), no en la cadencia textual.

### Obs.3 — Mi error día 21 documentado (review lote v1.8.1 PR #109)

Día 21 hice review del lote Venation y pedí ajuste sobre Asset 9 (`WeatherDigest`) que era decisión Bea cerrada en caliente con Venation. Aprendizaje registrado en bitácora `2026-05-06_review-lote-venation-v1.8.1_corola.md` Adenda: "Cuando vea descarte en lote entregado, preguntar antes de pedir ajuste — la decisión podría haberse cerrado lateralmente sin pasar por mí."

**Este aprendizaje es lo que aplico hoy día 26.** El snapshot Bract muestra decisiones de copy día 24-26 que NO pasaron por mí, y mi respuesta es: aceptar las que funcionan, sugerir refinamientos sobre las que pueden mejorar, registrar las que rompen decisiones narrativas cerradas pero respetar la decisión Bea cuando es consciente.

---

## Pendientes registrados

1. **Cartela invariante E7 escalada a Bea sin respuesta** — propuesta Corola día 26 lista para aplicar (4 verbos viscerales `prevails / holds / carries / composes`). Si Bea no responde antes del cierre, decido yo con venia de Bract.
2. **Sub-text opcional `Policies expire.` en `CartelaPollen.png`** — sugerencia Corola día 26. Decisión pendiente Bea/Bract.
3. **Recuperación F4 (`Every intelligence has jurisdiction. And expiry.`) en writeup/landing** — coordinación con Cambium ella en cierre de submission.
4. **API key ElevenLabs:** rotar al cierre del proyecto (Bea la pegó en chat con Bract hoy).
5. **VOs EN definitivas TTS pendientes en VIDEO 1 + VIDEO 2** (ya activas en VIDEO 3). Bract replica día 27.

---

## Mensaje listo para Bract (ya redactado en chat con Bea, copia trazable aquí)

[Mensaje completo de respuesta a las 5 preguntas de Bract + 2 observaciones está redactado en chat con Bea hoy día 26. Bea decide si lo relayea por chat a Bract o si lo deja consolidado solo en esta bitácora + en los docs v1.8.7 + v0.7 + v0.6. Si Bea relayea, Bract lee texto puro; si no, Bract lee al regenerar el snapshot tras los próximos cambios o al consultar los docs.]

**Decisión Bea cerrada hoy día 26:** "1. vale, 2. consciente, la mía quedaba fatal."
- 1 = sí formalizo cambios en `script.md` / `copies_bilingual.md` con bump v1.8.7 + PR (esta bitácora).
- 2 = confirma voz humana E5 retirada conscientemente.

---

## Historial de versiones del documento

- **v1** (2026-05-11, día 26, Corola) — primera versión. Consolidación día 26 tras 5 días de ausencia. 5 votos Corola aplicados sobre snapshot Bract + cambios estructurales del periodo días 22-26 documentados. Convención `doc estable + fuente viva` formalizada. Aplicado a `script.md` v1.8.7, `copies_bilingual.md` v0.7, `montage_brief.md` v0.6. Pendientes registrados (cartela invariante E7, sub-text Pollen, F4 en writeup, rotación API key ElevenLabs, replicación TTS VIDEO 1+2).
