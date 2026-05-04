# Mini-lote overlays E1-E2 + cierre · PNG transparentes 1280×720

**Para:** Bract (montaje, CapCut)
**De:** Venation
**Fecha:** 2026-05-04 (día 19)
**Vía:** Corola

## Qué hay aquí

Cuatro PNG con transparencia real, listos para arrastrar al timeline de
CapCut. No hay fondo oat, no hay marcadores, no hay safe-area dibujado:
solo el contenido de cartela.

```
E01_00-06_lower-third_imagine-pot.png
E01_00-11_lower-third_periodic-visit.png
E02_00-XX_corner-card_gemma-4-e2b.png
Z99_closing_sprout-wordmark.png
```

Resolución: **1280×720** (HD 16:9). Si tu timeline es 1080p, escala a 150%
sin pérdida visible — el contenido respeta safe-area de broadcast 5%
incluso a 1080.

## Especificaciones por frame

### E01 · 00:06 — *Imagine this pot is a whole plot.*
- **Posición:** lower-third, anclado a 64px del borde inferior y 64px del
  izquierdo. Si tu timeline es 1080p escalado, mantén el anclaje.
- **Duración sugerida:** entrada 0.3s ease-out, sostén ~1.8s, salida
  0.3s. Total visible ~2.4s.
- **Acompaña:** voz humana o B-roll de la maceta.

### E01 · 00:11 — *This plot is visited periodically by a human.*
- Mismas reglas que la anterior. Es el segundo beat del E01.
- **Tip:** si las dos cartelas se solapan en pantalla durante una
  transición, fade-out de la primera al 80% de su sostén y fade-in de la
  segunda con 200ms de overlap. Mejor que corte limpio.

### E02 · corner-card — *Gemma 4 E2B · local · llama.cpp*
- **Posición:** esquina superior derecha. Aparece cuando se muestra el
  log E02 (DecisionReceipt) por primera vez.
- **Duración sugerida:** entrada 0.4s ease-out (slide desde la derecha
  10px), sostén ~3s mientras se lee el receipt, salida 0.3s fade.
- **Sub:** "LLM called only when ambiguous." es deliberadamente bajo en
  contraste — narrativamente es nota al pie, no titular.
- **Atribución legal:** la cartela usa "Gemma 4 E2B" como texto plano,
  sin glifo Google ni gradiente de marca. Cumple atribución (ver bitácora
  branding del 2026-05-04). No la "embellezcas" con el azul Gemma.

### Z99 · closing — *Sprout · AI Local-first irrigation decisions.*
- **Posición:** cartela final del vídeo. La diseñé con el contenido a la
  izquierda (estilo manifiesto) — déjale aire a la derecha o cierra con
  fade a negro.
- **Duración sugerida:** ~4s. Entrada 0.6s con stagger (kicker → wordmark
  → tag → meta, 120ms entre cada uno).
- **Si la cartela final del guion definitivo es otra (Corola está
  reformulando E1-E9), ignora este Z99 y avísame qué texto entra.**

## Notas técnicas

- **Tipografía:** Manrope (700 lower-third, 800 wordmark, 500 tag) e IBM
  Plex Mono (corner-card label, kicker, meta). Si Manrope no carga en tu
  CapCut, fallback aceptable: Inter Bold / Helvetica Neue Bold (no Arial).
- **Color de acento (línea verde-amarilla):** `#C5F26B` (signal.seed).
  Reservado a "AI activa". No lo uses para otra cosa.
- **Fondo del pill:** `rgba(20,18,16,0.78)`. Si en tu plano de fondo la
  legibilidad sufre (texto blanco sobre cielo claro), no opacar más el
  pill — sube tú la opacidad al fondo del plano. El sistema cromático lo
  exige.

## Si necesitas variantes

Producción rápida; pídeme y las saco:

- Escala 1920×1080 nativa
- Versión vertical 1080×1920 para shorts
- Mismas cartelas con un acento diferente (no recomendado, romperíamos
  el código de color)
- Cualquiera de las cartelas E3, E4, E5, E6, E7, E8 que ya están en el
  prototipo

## Limitaciones

Estos PNG están renderizados en sandbox sin las webfonts cargadas. Las
métricas pueden divergir 1-2px del prototipo de referencia. Si el
montaje lo requiere, los reproduzco con la fuente real y los entrego en
24h.

— Venation
