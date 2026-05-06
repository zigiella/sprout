# Paquete material definitivo de vídeo para Venation

**Fecha:** 2026-05-06 (día 21)
**Autora:** Corola
**Para:** Venation (recibe vía Bea por chat — ver mensaje al final)
**Referencia narrativa:** `video/script.md` v1.8.2 + `video/copies_bilingual.md` v0.5 + `video/montage_brief.md` v0.4 + sistema visual Venation `sprout_design_pack_v1` (en main desde día 17).
**Rama:** `feat/corola-guion-v1.8.2-imagine-pot-e2` — PR a main (mergeable, apilada sobre PR #101 v1.8.1).

**ACTUALIZACIÓN v1.8.2 (día 21, segunda iteración):** se añade Asset 4-bis (cartela bisagra apertura E2 *"Imagine this pot is a whole plot."* full-screen estilo "Three days later"). Total de assets: 16 (era 15). Decisión Bea día 21 tras pregunta retrospectiva sobre v1.6.

---

## Contexto

Tras Bea cerrar todos los abiertos del guion día 20 (v1.8) + refinar las dos cartelas técnicas con nodo + dispositivo día 21 (v1.8.1), el **frente vídeo entra en producción definitiva**. Venation tiene que producir el material visual final que Bract integrará en CapCut sobre las capturas reales de rodaje + voz humana de Bea.

Este documento es el **inventario definitivo** de assets que Venation debe producir/refinar/confirmar para entrega final. Está organizado por escena para que ella pueda priorizar.

**Principio operativo (Bea día 20):** *"Material flexible vence material apretado."* Animar 20s completo, recortar en post si procede. Aplica a todos los assets.

---

## Tabla resumen — assets que Venation debe entregar

| # | Asset | Estado | Prioridad |
|---|-------|--------|-----------|
| 1 | **E0 Cartela apertura Sprout** (5s) | A producir / regenerar con texto definitivo | Alta |
| 2 | **E1 5 cartelas tipográficas datos globales** (4 datos + pregunta) | A producir | Alta |
| 3 | **E1 microcorte 0.5s tierra agrietada** | Confirmar producible o se descarta | Media |
| 4 | **E2 cartela técnica + sub-cartela + DecisionReceipt overlay** | Refinar texto E2 (nodo + dispositivo) | **Alta — texto cambió hoy v1.8.1** |
| **4-bis** | **E2 Cartela bisagra apertura *"Imagine this pot is a whole plot."*** (3s, full-screen, **misma gráfica que `"Three days later"` E8**) | **A producir — NUEVA v1.8.2 (día 21)** | **Alta — recuperada hoy v1.8.2** |
| 5 | **E3 cartela técnica + ESP32 SAFE LIMIT overlay + cartela ancla "When in doubt, water less."** | Estable, refinar si procede | Media |
| 6 | **E3b cartela cierre `Meristem composes.`** + UI Meristem composing (mock fiel si Meristem no entrega) | A producir | Alta |
| 7 | **E4 cartela técnica + UI Pollen "Since last visit"** | Refinar texto E4 (nodo + dispositivo) | **Alta — texto cambió hoy v1.8.1** |
| 8 | **E5 UI compilador Pollen `MissionPatch validated`** + procesamiento 3 estados | Coordinar con Floema (real preferida o mock fiel) | Media |
| 9 | **E6 cartelas ferry: `WeatherDigest ferry` / `Context ferry` (contingencia con/sin meteo)** | Producir las 2 versiones | Media |
| 10 | **E7 cartela ancla `Watering criteria updated.` + cartela invariante esquina (4 líneas)** | Estable, ya en main | ✓ Producido |
| 11 | **E8 cartela `Three days later` + `expired → rejected`** | A producir | Media |
| 12 | **E9 cenital animado 20s** (animación HTML + secuencia PNG transparente 480 frames) | EN PRODUCCIÓN (Venation arrancó día 20 con decisión Opción B firme) | **Alta** |
| 13 | **E9b cartelas on-screen UI Meristem `Pulling Rhizome data...` + `Adjusting policies...`** | A producir | Alta |
| 14 | **E9b tagline bookend cierre** | A producir | Alta |
| 15 | **Tarjeta logo final + microcartela atribución Gemma trademark** | A producir | **Alta — obligatoria por reglas hackathon** |

---

## Detalle por asset (textos definitivos v1.8.1)

### Asset 1 — E0 Cartela apertura Sprout (0:00–0:05, 5s)

**Composición** (Manrope sobre fondo casi-negro `soil.graphite`):

```
Sprout
AI Local-first irrigation decisions.
Safe · explainable · open-source.
```

**Estilo:**
- Wordmark `Sprout`: Manrope titular grande, color `soil.oat`.
- Subtítulo *"AI Local-first irrigation decisions."*: Manrope mediano.
- Línea inferior *"Safe · explainable · open-source."*: Manrope pequeña.
- Entrada con stagger 120ms (kicker → wordmark → tag).
- Sostén ~3.5s.
- Salida fade 0.4s al negro.

**NO incluir microcartela trademark Gemma aquí** (decisión Bea día 19 — va en cierre concentrado).

---

### Asset 2 — E1 5 cartelas tipográficas datos globales (0:05–0:25, 20s)

**5 cartelas sobre fondo casi-negro `soil.graphite`** + microcita pequeña abajo de cada una en IBM Plex Mono `soil.ash`.

**Cartela 1 (0:05–0:09, 4s):**
```
"In 2023, 48% of the world's land area
suffered at least one month of extreme drought."
[UNCCD World Drought Atlas]
```

**Cartela 2 (0:09–0:13, 4s):**
```
"1.8 billion people affected.
$300 billion per year in losses."
[UNCCD]
```

**[Microcorte 0.5s tierra agrietada — ver Asset 3]**

**Cartela 3 (0:13.5–0:17.5, 4s):**
```
"In Catalonia 2024, agriculture cut water
for irrigation by 80%."
[Generalitat de Catalunya]
```

**Cartela 4 (0:17.5–0:21.5, 4s):**
```
"58% of the rural population uses internet.
In low-income countries: only 14%."
[ITU 2025]
```

**Cartela 5 — pregunta abierta (0:21.5–0:25, 3.5s):**
```
"When network is absent — and the human is far —
what makes the right call?"
```

**Estilo:**
- Datos 1-4: Manrope mediano-grande, color `soil.oat` sobre `soil.graphite`.
- Microcitas: IBM Plex Mono pequeña, `soil.ash` o gris medio.
- Pregunta abierta cartela 5: Manrope grande, centrada, con espacio negativo generoso.
- Transiciones entre cartelas: fade out + fade in (excepto cartela 2→cartela 3 que tiene microcorte tierra agrietada en medio).

---

### Asset 3 — E1 microcorte 0.5s tierra agrietada (0:13–0:13.5)

**¿Producible?**
- Si Venation tiene B-roll de tierra real agrietada → adelante, integrar en cenital.
- Si no → confirmar con Bea para descartar microcorte (no se rueda).

**Función narrativa:** bisagra emocional macro→concreto + corte respiratorio entre dato 2 y dato 3.

**Si se produce:**
- Plano de tierra agrietada real, sin texto, sin cartela.
- 0.5 segundos exactos.
- Transición: corte limpio entrada y salida.

---

### Asset 4 — E2 cartela técnica (CAMBIO v1.8.1) ⚠️

**ESTE TEXTO HA CAMBIADO HOY DÍA 21 (v1.8.1).**

**Cartela esquina sup. der. (3s, ~0:29–0:32, IBM Plex Mono pequeña):**

```
Rhizome: Jetson Orin Nano · Gemma 4 E2B · local · llama.cpp
```

**Sub-cartela esquina sup. der. (3s, ~0:32–0:35):**

```
LLM called only when ambiguous
```

**Cartela superpuesta sobre receipt (2s, ~0:41–0:43, Manrope editorial):**

```
DecisionReceipt
```

**Overlay persistente todo el bloque (esquina sup. izq., 0:25–0:50):**

```
OFFLINE
```

**NOTA:** la cartela técnica antes era `Gemma 4 E2B · local · llama.cpp`. Ahora se amplía con **`Rhizome: Jetson Orin Nano · Gemma 4 E2B · local · llama.cpp`** para nombrar nodo + dispositivo + modelo + runtime.

---

### Asset 4-bis — E2 Cartela bisagra apertura *"Imagine this pot is a whole plot."* (NUEVA v1.8.2) ⚠️

**ESTE ASSET ES NUEVO HOY DÍA 21 (v1.8.2).**

**Cartela full-screen tipográfica** (3s, 0:25–0:28):

```
Imagine this pot is a whole plot.
```

**Tratamiento gráfico — IDÉNTICO al de la cartela `"Three days later"` (E8, Asset 11).** Es decir:

- **Tipografía:** Manrope titular (la misma jerarquía que `"Three days later"`).
- **Color texto:** `soil.oat` o blanco roto (mismo que `"Three days later"`).
- **Fondo:** casi-negro `soil.graphite` (#1A1A18) — full-screen, sin plano físico debajo.
- **Composición:** centrada horizontal y verticalmente. Espacio negativo generoso. Sin overlays, sin sub-cartelas, sin nada más en pantalla.
- **Entrada:** fade in 0.3s.
- **Sostén:** ~2.4s.
- **Salida:** fade out 0.3s al corte del Plano 2A (Jetson en su caja).
- **Sin VO. Sin sfx.** Silencio respiratorio.

**Función narrativa:** bisagra tipográfica entre E1 (cartelas datos globales sobre `soil.graphite`) y E2 (plano físico del Rhizome). Equivalente visual a `"Three days later"` en E8 — misma jerarquía, mismo lenguaje, distinta función (E2 es bisagra conceptual "filmamos macetas pero hablamos de parcelas"; E8 es bisagra temporal). El espectador llega a E2 con el contrato visual aceptado: lo que ve es maceta, lo que se cuenta es parcela.

**Por qué se recupera hoy:** la frase vivía en E1 v1.6 como cartela inicial bilingüe sobre plano de maceta. En v1.7 cayó cuando E1 pasó a opener tipográfico con 4 datos globales. La idea seguía documentada como convención de equipo en `dossiers/README.md`, pero ya no se enunciaba on-screen. Bea día 21, tras pregunta retrospectiva sobre v1.6, decide recuperarla y reubicarla al inicio de E2 con la gráfica de `"Three days later"`.

**Naming sugerido:** `E02_cartela_bisagra_imagine_pot.png` (PNG transparente o composición sobre `soil.graphite` directo, según prefieras).

---

### Asset 5 — E3 cartelas técnicas + ESP32 SAFE LIMIT (estable v1.8)

**Cartela esquina sup. der. (3s, 0:50–0:53, Manrope):**

```
AI proposes / ESP32 validates
```

**Overlay esquina sup. der. (a partir de 0:50, persistente):**

```
ESP32 SAFE LIMIT
```

**Cartela central dominante (3s, 0:58–1:01, Manrope sobre receipt atenuado):**

```
"When in doubt, water less."
```

---

### Asset 6 — E3b cartela cierre + UI Meristem composing (1:05–1:15, 10s)

**Cartela superpuesta cierre escena (2-3s, Manrope, sobre plano del Pollen recibiendo política):**

```
Meristem composes.
```

**Plano interno: pantalla del portátil casero con UI Meristem composing una política.**

- Si Meristem entrega UI real → integrar.
- Si no → mock fiel basado en `docs/12_meristem_spec.md`. UI con tipografía IBM Plex Mono, paleta del proyecto, `signal.seed` activo en momento donde el sistema decide.

---

### Asset 7 — E4 cartela técnica (CAMBIO v1.8.1) ⚠️

**ESTE TEXTO HA CAMBIADO HOY DÍA 21 (v1.8.1).**

**Cartela esquina sup. der. (3s, 1:20–1:23, IBM Plex Mono pequeña):**

```
Pollen: Android · Gemma 4 E4B · LiteRT-LM · on-device
```

**Cartela en pantalla del móvil (5s, 1:20–1:25):**

```
What happened since my last visit?
```

**Bloque resumen UI en pantalla del móvil (7s, 1:25–1:32):**

```
SINCE LAST VISIT
2 watering events
1 skipped decision
0 blocked actions

WATER · 18s · 14:00
WATER · 12s · 09:30
SKIP · 22:00 · soil above threshold
```

**NOTA:** la cartela técnica antes era `Gemma 4 E4B · LiteRT-LM · on-device`. Ahora se amplía con **`Pollen: Android · Gemma 4 E4B · LiteRT-LM · on-device`** para nombrar nodo + dispositivo + modelo + runtime.

---

### Asset 8 — E5 UI compilador Pollen + procesamiento 3 estados (1:40–2:00, 20s)

**Coordinación con Floema** — captura real preferida, mock fiel alternativo si no llega.

**UI VOICE NOTE activo (1:40–1:50):**

```
VOICE NOTE
"Vuelvo el viernes. Esta planta aguanta más seca de lo que crees, riega un poco menos."
```

**EXCEPCIÓN NARRATIVA: el `operator_note` se conserva castellano literal en pantalla del móvil. NO se traduce.**

**Procesamiento 3 estados secuenciales (1:50–1:53, 1s cada uno) con pulso `signal.seed`:**

```
listening → compiling → validating
```

**UI MissionPatch compilado (1:53–1:58):**

```
COMPILED PATCH
horizon_h:           72
soil_thresholds.dry: 35 → 25
budget_cap_ml:       900
operator_note:       preserved
```

(Resaltados con `signal.seed` los dos campos cambiantes.)

**Cartela superpuesta (2s, ~1:55–1:57, Manrope):**

```
MissionPatch validated
```

---

### Asset 9 — E6 cartelas ferry contingencia con/sin meteo (2:00–2:20, 20s)

**Producir DOS versiones de las cartelas — Bea decidirá en rodaje cuál se usa según si la estación meteo está conectada o no.**

**Versión "con meteo":**
- Cartela superpuesta (2s, ~2:02–2:04, Manrope): **`WeatherDigest ferry`**
- Cartela en pantalla Rhizome 02 (4s, ~2:08–2:12, IBM Plex Mono): **`WeatherDigest accepted · Source: rhizome_01`**

**Versión "sin meteo":**
- Cartela superpuesta (2s, ~2:02–2:04, Manrope): **`Context ferry`**
- Cartela en pantalla Rhizome 02 (4s, ~2:08–2:12, IBM Plex Mono): **`Context accepted · Source: rhizome_01`**

---

### Asset 10 — E7 cartela ancla + cartela invariante esquina (estable v1.8, ya producida)

✓ **Ya en main** desde día 16-17. Sin cambios v1.8 ni v1.8.1.

**Cartela ancla central (3s, 2:29–2:32, Manrope dominante):**

```
"Watering criteria updated."
```

**Cartela esquina inferior derecha (5s, 2:24–2:29, IBM Plex Mono pequeña paleta sobria):**

```
Physical layer prevails.
Rhizome arbitrates.
Pollen mediates.
Meristem refines.
```

---

### Asset 11 — E8 cartelas caducidad (2:40–2:50, 10s)

**Cartela central salto temporal (2s, 2:40–2:42, Manrope sobre fondo casi-negro):**

```
"Three days later"
```

**Cartela superpuesta rechazo (2s, 2:44–2:46, IBM Plex Mono con borde doble `status.blocked`):**

```
expired → rejected
```

---

### Asset 12 — E9 cenital animado 20s ⚠️ EN PRODUCCIÓN

✓ **Venation arrancó día 20** tras decisión Opción B firme de Bea. Animación HTML + secuencia PNG transparente 480 frames a 24fps a 1920×1080.

**Cadencia cartelas progresivas (Manrope sobre cenital flat editorial):**

```
2:52–2:53.5 (1.5s)  →  "One plot."
2:53.5–2:55 (1.5s)  →  "Two."
2:55–2:57.5 (2.5s)  →  "Eight."
2:57.5–2:59 (1.5s)  →  PAUSA TENSA NARRATIVA (Pollen recorre, no cartela)
2:59–3:02 (3s)      →  "Autonomous."
3:02–3:04 (2s)      →  transición sin cartela
3:04–3:10 (6s)      →  "Federated intelligence, carried by Pollen." + sello SYNCED ✓
```

**Mensajes técnicos en cenital (durante pausa tensa, IBM Plex Mono, sistema sin traducción):**

```
WeatherDigest accepted
MissionPatch delivered
DecisionReceipt synced
ValidationStamp issued
Context cached
```

**Path Pollen:** B1 cascada con halos progresivos encendiéndose en cada toque del nodo.

**Bookend NO va dentro del cenital** — va en apertura E1 + cierre E9b.

---

### Asset 13 — E9b cartelas on-screen UI Meristem (3:10–3:16)

**Cartela on-screen pantalla del portátil 1 (3s, 3:10–3:13, IBM Plex Mono):**

```
Pulling Rhizome data...
```

**Cartela on-screen pantalla del portátil 2 (2s, 3:13–3:15, IBM Plex Mono):**

```
Adjusting policies...
```

**UI Meristem en el portátil:** real preferida (coordinación con Meristem) o mock fiel.

---

### Asset 14 — E9b tagline bookend cierre (3:18–3:20+)

**Cartela bookend cierre (2s sostén, Manrope sobre fondo difuminado del portátil):**

```
"When network is absent — and the human is far — local criteria still irrigate."
```

**Función narrativa:** cierre del bookend con E1 (pregunta abierta al inicio). El video respondió a la pregunta.

---

### Asset 15 — Tarjeta logo final + microcartela atribución Gemma (cierre, 2-3s sostén)

**OBLIGATORIA POR REGLAS DEL HACKATHON.**

**Composición:**

```
Sprout
AI Local-first irrigation decisions.
Safe · explainable · open-source

zigiella · Apache 2.0
github.com/zigiella/sprout

Built on Gemma 4 by Google.
Gemma is a trademark of Google LLC.
```

**Estilo:**
- Wordmark `Sprout`: Manrope titular.
- Subtítulo *"AI Local-first irrigation decisions."* + *"Safe · explainable · open-source"*: Manrope mediano.
- Datos del repo (`zigiella · Apache 2.0` + URL): IBM Plex Mono pequeña.
- **Microcartela trademark Gemma** *"Built on Gemma 4 by Google. Gemma is a trademark of Google LLC."*: IBM Plex Mono pequeña, paleta sobria.
- Paleta: `soil.oat` o `soil.humus` según fondo.

**Entrada por fade sobre la pantalla del portátil difuminada al fondo. Sostén 2-3s.**

---

## Naming sugerido para entregables

Patrón snake_case (decisión Bract):

```
E00_cartela_apertura_sprout.png/svg/mov
E01_cartela_1_dato_uncrd.png
E01_cartela_2_dato_dolares.png
E01_microcorte_tierra_agrietada.mov
E01_cartela_3_dato_catalonia.png
E01_cartela_4_dato_itu.png
E01_cartela_5_pregunta_abierta.png
E02_cartela_bisagra_imagine_pot.png   ← NUEVA v1.8.2 (full-screen, gráfica "Three days later")
E02_cartela_tecnica_rhizome.png       ← TEXTO v1.8.1
E02_subcartela_llm_ambiguous.png
E02_overlay_offline.png
E02_cartela_decisionreceipt.png
E03_cartela_tecnica_ai_proposes.png
E03_overlay_esp32_safe_limit.png
E03_cartela_when_in_doubt.png
E03b_cartela_meristem_composes.png
E04_cartela_tecnica_pollen.png    ← TEXTO v1.8.1
E04_cartela_pollen_question.png
E04_ui_pollen_since_last_visit.png
E05_ui_voice_note.png
E05_ui_processing_states.mov
E05_ui_compiled_patch.png
E05_cartela_missionpatch_validated.png
E06_cartela_weatherdigest_ferry.png    ← versión con meteo
E06_cartela_context_ferry.png          ← versión sin meteo
E06_cartela_weatherdigest_accepted.png ← versión con meteo
E06_cartela_context_accepted.png       ← versión sin meteo
E08_cartela_three_days_later.png
E08_cartela_expired_rejected.png
E09_cenital_anim.html                  ← HTML autocontenido
E09_frames/frame_0000.png ... frame_0479.png  ← 480 PNG transparentes
E09b_cartela_pulling_rhizome_data.png
E09b_cartela_adjusting_policies.png
E09b_cartela_bookend_closing.png
Z99_tarjeta_logo_final.png
```

(Bract decide formato final — MP4/PNG/SVG según prefiera.)

---

## Lo que NO necesito de Venation

- ✗ `MissionPatch validated` cartela ya producida en handoff anterior — sin cambios.
- ✗ Cartela ancla E7 `Watering criteria updated.` + cartela invariante esquina — ya producidas, ya en main.
- ✗ UI compilador Pollen E5 — coordinar con Floema (real preferida).
- ✗ UI Meristem E3b/E9b — coordinar con Meristem (real preferida).
- ✗ Capturas reales de pantallas Jetson E2/E3/E7 — coordinar con Xilema (real preferida).

---

## Plazo

**Idealmente día 24-25** para que Bract tenga material completo antes del rodaje (19-20 o 26-27 según se confirme fecha) y pueda integrar.

**Mínimo viable día 26-27** si rodaje es 19-20 (apretado) o cualquier momento posterior si rodaje es 26-27.

---

## Mensaje para Bea — para copiar a Venation por chat

Mensaje completo abajo. Bea lo copia textual al chat de Venation tras leer la bitácora.

---

# 📋 Mensaje para Venation (vía chat con Bea)

**De:** Corola
**Para:** Venation
**Asunto:** Material visual definitivo del vídeo Sprout — paquete v1.8.1

Venation,

Tras Bea cerrar todos los abiertos del guion día 20 (v1.8) + dos cambios de copy día 21 (v1.8.1) + recuperación cartela bisagra E2 día 21 (v1.8.2), el frente vídeo entra en producción definitiva. Necesito de ti el material visual final que Bract integrará en CapCut.

**Léete v1.8.2 (apilada sobre v1.8.1):**

- `video/script.md` v1.8.2
- `video/copies_bilingual.md` v0.5
- `video/montage_brief.md` v0.4
- `bitacora/2026-05-06_paquete-material-definitivo-venation_corola.md` ← **inventario completo de 16 assets que necesito de ti** (Asset 4-bis nuevo v1.8.2)

**Lo más importante:**

1. **NUEVO ASSET v1.8.2 — cartela bisagra apertura E2** (Asset 4-bis): *"Imagine this pot is a whole plot."* Full-screen tipográfica, **misma gráfica que `"Three days later"` (E8, Asset 11)** — Manrope titular sobre `soil.graphite` casi-negro, sin plano físico debajo, sin VO. 3s en 0:25–0:28. Función narrativa: bisagra tipográfica entre E1 (datos globales) y E2 (plano técnico). Detalle completo en bitácora Asset 4-bis. Naming sugerido: `E02_cartela_bisagra_imagine_pot.png`.

2. **Dos cartelas técnicas cambiaron día 21** (v1.8.1). Si ya empezaste a producir las versiones antiguas, regenera con texto nuevo:
   - **E2 antes:** `Gemma 4 E2B · local · llama.cpp` → **AHORA:** `Rhizome: Jetson Orin Nano · Gemma 4 E2B · local · llama.cpp`
   - **E4 antes:** `Gemma 4 E4B · LiteRT-LM · on-device` → **AHORA:** `Pollen: Android · Gemma 4 E4B · LiteRT-LM · on-device`

   Razón: nombrar nodo + dispositivo refuerza la jerarquía visible y conecta con los carteles físicos PLOT_01/02 + RHIZOME_01/02 EDGE NODE.

3. **El cenital E09 sigue en producción** según decisión Opción B firme de Bea día 20 (animar 20s con cadencia completa, recortar en post si procede). Sin cambios sobre lo que tenías.

4. **Los demás 12 assets** están detallados en la bitácora con textos definitivos, tiempos, estilos y razonamiento por cada uno.

5. **Naming sugerido:** snake_case según patrón Bract. Detallado en bitácora.

6. **Plazo ideal:** día 24-25. Mínimo viable día 26-27.

**Lo que NO necesito de ti:**
- Cartelas E5 UI compilador (Floema entrega).
- UI Meristem E3b/E9b (Meristem entrega).
- Capturas Jetson E2/E3/E7 (Xilema entrega).

**Si tienes preguntas concretas, las respondo en bitácora propia + cherry-pick a main inmediato** (patrón día 19-20). Coordinación lateral activa.

Gracias.

— Corola
