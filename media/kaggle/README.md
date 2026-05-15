# media/kaggle/

Canonical image gallery delivered for The Gemma 4 Good Hackathon submission. Organised under Venation's naming convention:

```
sprout-{kind}-{topic}-NN.{png,svg}
```

Where `{kind}` ∈ {`photo`, `ui`, `diagram`} and `NN` is a zero-padded variant counter.

## Contents

| Kind | Count | Notes |
|------|------:|-------|
| `photo` | 11 | hero, rhizome hardware (open/internal/macro/bench), bom, planter (detail/setup), terrace (empty), meristem-macro, workshop-wide |
| `ui` | 8 | meristem dashboard (2 panels), pollen mobile (5 screens), receipt terminal |
| `diagram` | 3 SVG + 3 PNG | architecture-overview · authority-stack · double-agent — all dark-grey canvas `#3a3733` for card legibility |
| `descriptions.md` | 1 | EN alt + caption for every image, suggested usage by surface |

## Diagram fix (day 30)

The three diagram SVGs have a **warm-grey background (`#3a3733`)**, lifted from the original near-black `#0E0E0C` so the graphite AI cards (Rhizome, Pollen, Steward, ShadowSkeptic) stand out cleanly. The deterministic oat cards (ESP32, Meristem, Valve, State bundle, DecisionReceipt, Disagreement log) retain strong contrast against the new background.

The descriptions.md file says "warm-grey background" to reflect this — if you ever revert to a near-black canvas, update the alt text there too.

## How to use this folder

- **Kaggle media gallery (5–6 slot max):** see the `suggested usage by surface` table at the bottom of `descriptions.md`.
- **Writeup embeds:** the three diagrams are already embedded in `writeup/draft.md` using the `media/sprout-*.png` files at repo root (same content, different filename — keeps the writeup URLs short).
- **Landing page:** uses the SVGs from `media/` (not from `media/kaggle/`) so the page can scale them losslessly. The kaggle/ folder is the PNG-first delivery for static surfaces.
- **Social / external:** every image has alt + caption in `descriptions.md` ready to copy-paste.

## Image authorship

- **Photographs:** Sprout team — locations in Castellar de n'Hug, Catalonia, Spain (see [`CREDITS.md`](../../CREDITS.md)).
- **UI screenshots:** captured from the Pollen Android app (device flavor) and the Meristem laptop dashboard.
- **Diagrams:** Venation v1.8 design system (Manrope + IBM Plex Mono on warm-grey canvas, AI cards in graphite with signal-seed accent, deterministic cards in oat).

## Cover image — separate

The Kaggle competition cover lives at `../sprout-cover-local-first-ai.png` (1920×1080, by Bea + Venation) and is **not duplicated here**. The cover is governed by the Kaggle submission UI directly, not by the writeup body.
