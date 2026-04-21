# research/experiments — indice vivo

Indice de bitacoras de la celula de investigacion (Estoma + Peri). Agrupadas por tema.

**Convenciones:**
- Una linea por bitacora.
- Marca de impacto al principio: 🔴 cambia diseño / 🟡 afina decision / ⚪ archivo.
- Enlace al issue `research-digest` cuando exista.

**Mantenido por:** Estoma.

---

## Runtime Gemma 4 + Ollama

- 🔴 [2026-04-21 · Ventana de contexto Gemma 4 en Ollama](experiments/2026-04-21_ventana-contexto-gemma4_estoma.md) — el contexto efectivo es `min(techo_modelo, asignacion_Ollama_por_VRAM)`; default <24 GiB → 4K. Tags: @meristem, @floema, @xilema, @cambium, @corola. Rescate de la investigacion de Bea del 2026-04-20.

---

## Cuantizacion y hardware edge (Jetson, Raspberry Pi)

- 🔴 [2026-04-21 · Gemma 4 en Jetson Orin Nano Super](experiments/2026-04-21_gemma4-jetson-orin-nano-super_estoma.md) — E2B Q4_K_M es el fit natural (~1.5 GB); Ollama **nativo** (no Docker), JetPack ≥6.2; proxy Gemma 3n e2b ~16.55 tok/s gen. Tags: @xilema, @cambium, @meristem, @floema, @corola.

---

## Thinking mode

_(pendiente)_

## LiteRT en movil (Pollen, Pixel 10 Pro)

_(pendiente)_

## Trucos y problemas conocidos (Ollama, structured output, caching)

_(pendiente — en curso)_
