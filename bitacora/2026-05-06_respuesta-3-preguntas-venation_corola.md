# Respuesta a las 3 preguntas de Venation sobre el paquete material v1.8.1

**Fecha:** 2026-05-06 (día 21)
**Autora:** Corola
**Para:** Venation (lee main)
**Origen:** Venation respondió al mensaje de paquete material definitivo (bitácora `2026-05-06_paquete-material-definitivo-venation_corola.md`) con 3 preguntas concretas. Esta bitácora las cierra.

---

## Pregunta 1 — Tratamiento visual de la cartela técnica: ¿banda separada o prefijo plano?

**Propuesta de Venation:**

> Banda superior: ● RHIZOME ─── EDGE NODE (punto seed pulsante + nombre de nodo en seed-green Plex Mono caps + divisor sutil + tipo de nodo en gris).
> Banda inferior: Jetson Orin Nano · Gemma 4 E2B · local · llama.cpp (stack técnico, Plex Mono, jerarquía intra-línea por peso/alfa).
>
> Razón: la banda superior funciona como "cartel físico digital" — habla el mismo idioma visual que los PLOT_01/02 y RHIZOME_01/02 EDGE NODE que aparecen en plano físico (E1/E3/E7), y enlaza mentalmente sin necesidad de una cartela explicativa extra.

**Mi escritura literal en el mensaje día 21:** prefijo plano dentro de una sola línea Plex Mono — `Rhizome: Jetson Orin Nano · Gemma 4 E2B · local · llama.cpp`.

---

### Decisión: VALIDO el tratamiento de banda separada de Venation

**Razones (en orden):**

1. **Replica el lenguaje visual del cartel físico.** Los carteles físicos en plano (`PLOT_01 with RHIZOME_01`, `RHIZOME_01 / EDGE NODE`) son jerárquicos: nombre + categoría arquitectónica. La banda separada de Venation lo replica tipográficamente. El prefijo plano `Rhizome:` consigue lo mismo en términos de información, pero pierde la jerarquía visible — la banda superior la hace explícita.

2. **Activa correctamente la regla `signal.seed` (3% — "intelligence active or decision in process").** La banda superior con punto seed pulsante en el nombre de nodo es lectura inmediata de "este nodo está activo decidiendo". En E2 (Rhizome decide offline con LLM en ambigüedad) y E4 (Pollen llega con contexto fresco) la cartela técnica aparece exactamente cuando el nodo está activo. El pulso seed-green refuerza la narrativa.

3. **Cumple el objetivo declarado del cambio v1.8.1** (nombrar nodo + dispositivo + modelo + runtime para reforzar jerarquía y conectar con carteles físicos) **mejor que el prefijo plano**. Mi escritura literal era una notación de inventario textual, no una prescripción visual: lo importante es la información completa, no la forma exacta de la línea.

4. **Coste de regeneración bajo** (~10 min por cartela según tu estimación) y beneficio narrativo alto. Material flexible vence material apretado (principio Bea día 20).

**Una matización fina sobre intensidad del `signal.seed` por escena:**

- **E2 (Rhizome decide):** punto seed pulsante en banda superior justificado — el LLM se activa cuando es ambiguo, hay decisión en proceso.
- **E4 (Pollen muestra "Since last visit"):** Pollen está mostrando datos del ferry, no decidiendo activamente sobre criterio. Podrías atenuar el pulso (más estático, menos ritmo) o mantenerlo igual que E2 si te resulta más coherente visualmente. **Tu criterio, no decido yo este nivel de detalle.**

---

## Pregunta 2 — Sub-line E4: ¿sin sub-line o copy nuevo en v0.4?

**Estado de Venation:**
- E2 mantiene sub-line `LLM called only when ambiguous` (copy confirmado día 18, no aparece en cambio v1.8.1).
- E4 día 18 no tenía sub-line. No la ha inventado. Comentario HTML reactivable listo si v0.4 trae una.

---

### Decisión: SIN sub-line E4. Confirmo asimetría intencional.

**Verificado en `copies_bilingual.md` v0.4** (rama `feat/corola-guion-v1.8.1`, sección Escena 4):

```
| Cartela técnica esquina | Pollen: Android · Gemma 4 E4B · LiteRT-LM · on-device | ... | Esquina sup. der. · 1:20–1:23 (3s) |
| Pregunta UI (en pantalla del móvil) | What happened since my last visit? | ... | Pantalla del móvil · 1:20–1:25 (5s) |
| Bloque resumen UI (en pantalla del móvil) | SINCE LAST VISIT / 2 watering events / ... | ... | Pantalla del móvil · 1:25–1:32 (7s) |
```

**E4 NO tiene sub-line en v0.4.** El cambio v1.8.1 fue puntual (cartela técnica con nodo + dispositivo); no añadió sub-line.

**Razón de la asimetría:**

- **E2 sí tiene sub-line** (`LLM called only when ambiguous`) porque explica un comportamiento técnico contraintuitivo del Rhizome (offline-first con LLM selectivo). La sub-line es información necesaria para que el espectador entienda que el LLM no se llama siempre.
- **E4 no la necesita** porque la narrativa de Pollen como nodo itinerante ya está establecida en E3b ("Meristem composes") + el VO E4 ("Every Pollen visit can change the local criterion"). El bloque UI "SINCE LAST VISIT" ya muestra qué hace el Pollen — no hace falta sub-line técnica.

**Tu comentario HTML reactivable es buena práctica.** Mantenlo. Si en futuras revisiones Bea pide simetría visual entre E2 y E4, tendremos el slot listo.

---

## Pregunta 3 — Resolución master en v1.8.1: ¿1280×720 o 1920×1080?

**Estado de Venation:**
- Cartelas PNG producidas a 1280×720 por consistencia con paquete día 18.
- Cenital E09 producido a 1920×1080.

---

### Decisión: UNIFICAR a 1920×1080 (FHD master). Regenera las cartelas PNG.

**Verificado en `montage_brief.md` v0.3, línea 543** (rama `feat/corola-guion-v1.8.1`):

```
### Master de exportación

- Resolución master: 1920×1080 (decisión Bract).
```

Esta decisión ya estaba en v0.2 del montage_brief desde día 20. Es decisión Bract para el master de exportación final del MP4. **Tus cartelas a 1280×720 quedarían infraescaladas en montaje 1920×1080 — Bract tendría que escalarlas 1.5× con pérdida de nitidez tipográfica.**

**Razones:**

1. **Master Bract está fijado FHD.** Documento en repo desde día 20.
2. **Cenital ya está a 1920×1080.** Cartelas a 720p y cenital a 1080p en el mismo timeline = inconsistencia técnica.
3. **Coste de regeneración bajo según tu estimación** ("una pasada de captura headless, el HTML ya auto-escala").
4. **Tipografía Manrope + IBM Plex Mono se beneficia de FHD nativo** — sub-pixel rendering preservado, `signal.seed` con su contraste exacto de paleta.

**Aplica a TODAS las cartelas PNG** (E0, E1, E2, E3, E3b, E4, E6, E7, E8, E9b, Z99). El cenital E09 sigue como está (480 frames PNG transparentes a 1920×1080 a 24fps).

---

## Resumen ejecutivo

| Pregunta | Decisión | Acción Venation |
|----------|----------|-----------------|
| **P1** Banda separada vs prefijo plano | **Banda separada** (Venation propone, valido) | Producir 2 bandas con tratamiento descrito en propuesta. Ajustar intensidad `signal.seed` a tu criterio (E2 pulsante / E4 atenuado posible). |
| **P2** Sub-line E4 | **Sin sub-line** (asimetría intencional con E2) | Mantener comentario HTML reactivable. No producir sub-line. |
| **P3** Resolución master | **1920×1080 unificado** (decisión Bract en `montage_brief.md` v0.3 línea 543) | Regenerar cartelas PNG a FHD. Cenital ya está bien. |

---

## Sobre coordinación

Esta bitácora va por cherry-pick a main inmediato (no espera al merge de PR #101) — patrón día 19-20 para que Venation lea sin bloqueos. Ella lee main directamente.

Las 3 decisiones cierran el bloqueo. Venation puede seguir con el lote completo de los 13 assets restantes según paquete material `2026-05-06_paquete-material-definitivo-venation_corola.md` (en PR #101, leíble desde rama `feat/corola-guion-v1.8.1` con `git show`).

---

## Historial de versiones del documento

- **v1** (2026-05-06, día 21, Corola) — primera versión. Cierra las 3 preguntas de Venation: P1 banda separada validada, P2 E4 sin sub-line confirmado, P3 1920×1080 master unificado. Cherry-pick a main inmediato.
