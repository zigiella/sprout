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

---

## LiteRT en movil (Pollen, Pixel 10 Pro)

- 🔴 [2026-04-21 · LiteRT-LM reemplaza a MediaPipe Tasks GenAI para Gemma 4](experiments/2026-04-21_litertlm-deprecated-mediapipe_peri.md) — Google depreca MediaPipe (`.bin`) en favor de la dependencia `litertlm-android` (`.litertlm`). Pollen debe migrar la orquestación a la nueva clase `Engine`. Tags: @floema, @xilema, @meristem.
- 🔴 [2026-04-22 · Validación operativa: Gemma 4 E4B + LiteRT-LM en Android 16 (Pixel 10 Pro)](experiments/2026-04-22_litertlm-e4b-android16-pixel10pro_peri.md) — Verificación de docs oficiales y bugs abiertos. La Guía 50 es sólida; el bug de GPU #1681 justifica usar CPU como baseline obligatoria en Pollen. Tags: @floema, @bea, @estoma.

---

## Trucos y problemas conocidos (Ollama, structured output, caching)

- 🔴 [2026-04-21 · Trucos y problemas conocidos: Ollama + Gemma 4](experiments/2026-04-21_trucos-problemas-ollama-gemma4_estoma.md) — `format` con JSON schema funciona pero con minas: `think=false`+`format` ignora schema (#15260), fences markdown en E4B/31B (#15595), FA en 31B denso cuelga (#15350), GPU→CPU silencioso (#15237). `/api/chat` > `/api/generate` (templating, tool-calling). `keep_alive=-1` + prompt byte-estable = reuso de KV. Tags: @xilema, @cambium, @meristem, @floema, @corola.
