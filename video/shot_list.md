# Shot list — Sprout

**Version:** v0 (reset sobre v0.1 tras reframe Pollen/Meristem y ajuste duracion)
**Fecha:** 2026-04-19
**Autora:** Corola

Lista tecnica de planos a grabar. Estructura alineada con `script.md` v0
(PR hermano). Duracion objetivo: **1:00 top + 1:00-2:00 complementario
con final top** (decidido por Bea; Cambium pendiente de confirmar cota
superior exacta). Columna **tipo** distingue `real` (MVP funcional),
`B-roll` (paisaje/ambiente), `screen` (captura pantalla) y `veo3`
(generado, solo cuando no se puede filmar sin mentir sobre el MVP).

**Cambios frente a v0.1:**
- Climax ya no es caducidad; climax es **transferencia cruzada A→B** (angulo C).
- Caducidad se conserva como bloque complementario (min 2), no como climax.
- Meristem aparece en min 2 (diferido, timelapse), **no** en min 1.
- Cartela "E4B MVP / 26B objetivo" en Meristem (honestidad sobre trade-off).
- Stack de cartelas Gemma en cada nodo (Rhizome/Pollen/Meristem) — visibilidad para jurado DevRel.
- Plano 8 parcelas cenital en min 1 — via Veo3, no dron.

---

## Minuto 1 (top, autosuficiente)

| N | t | Tipo | Plano | Duracion | Localizacion | Medios |
|---|---|------|-------|----------|--------------|--------|
| 01 | 0:00-0:07 | B-roll | Parcela B sola al amanecer. Plano general estatico. Cartela silenciosa: **"Decide sola hoy."** | 7 s | Exterior (terraza con encuadre "parcela") | Telefono, tripode, luz natural amanecer. |
| 02 | 0:07-0:13 | real | Rhizome sobre mesa: Jetson + sensor humedad + camara. LED verde. Stack cartela: **"Rhizome · Gemma 4 E2B · edge"**. | 6 s | Terraza (MVP) | Telefono, luz controlada. |
| 03 | 0:13-0:18 | screen | Terminal mostrando `decision_receipt` JSON firmado localmente. Overlay: "<1 s, sin red". | 5 s | — | OBS captura 1080p. |
| 04 | 0:18-0:25 | real | Humano caminando con Pixel 10 Pro. Plano medio. Stack cartela: **"Pollen · Gemma 4 E2B · movil, LiteRT"**. | 7 s | Exterior | Telefono + gimbal. |
| 05 | 0:25-0:30 | real | Pollen llega a parcela A. Handshake BLE. Pantalla Pixel: auditoria en curso. | 5 s | Terraza | Telefono + captura sincronizada. |
| 06 | 0:30-0:35 | screen | **Flash A (auditoria gemela).** Split screen: "Rhizome decidio" vs "Pollen auditoria". Acuerdo verde. | 5 s | — | Captura app Pollen. |
| 07 | 0:35-0:50 | real+screen | **CLIMAX (b) — transferencia cruzada A→B.** Humano camina A→B. En el camino, Pixel genera `policy_delta` con rationale visible. Al llegar a B, delta aplicado. | 15 s | Exterior + terraza | Telefono + captura pantalla rationale. |
| 08 | 0:50-1:00 | veo3 | **Pull-back cenital.** De parcela B a 8 parcelas distribuidas. Rutas humanas conectando. Cartela final: **"Criterio que circula en el bolsillo."** | 10 s | — | Veo3 (imposible filmar sin mentir sobre escala MVP). |

---

## Minutos 2-3 (complementario, final top)

| N | t | Tipo | Plano | Duracion | Localizacion | Medios |
|---|---|------|-------|----------|--------------|--------|
| 09 | 1:00-1:15 | B-roll | Timelapse: dia pasa sobre parcela. Sol cruza. Sombras giran. | 15 s | Exterior | Telefono, intervalometro. |
| 10 | 1:15-1:30 | real | Laptop Meristem sobre mesa de cocina. Ollama corriendo E4B. Terminal: structured output `policy_delta` estrategico. Stack cartela: **"Meristem · Gemma 4 E4B · Ollama / MVP local 16 GB / arquitectura objetivo: 26B"**. | 15 s | Indoor | Telefono + captura pantalla. |
| 11 | 1:30-1:50 | real | Detalle ESP32 + caudalimetro + valvula. Intento de apertura. Pantalla Rhizome: `REJECTED: RATE_LIMIT`. Cartela inserto silencioso: **"BdE: 20-30% trigo España perdido por decisiones tardias, 2024."** | 20 s | Terraza | Telefono macro + captura. |
| 12 | 1:50-2:10 | real+screen | **Caducidad.** Pixel entrega paquete fuera de ventana. Pantalla Rhizome: `REJECTED: policy_expired`. Cartela: **"Si llega tarde, no se usa."** | 20 s | Terraza | Telefono + captura. |
| 13 | 2:10-2:30 | B-roll+real | **Amanecer siguiente.** Parcela B al alba. Rhizome arranca. Politica consolidada por Meristem aterriza: nueva regla visible en pantalla. Planta de B sana. | 20 s | Exterior + terraza | Telefono, luz amanecer, captura. |
| 14 | 2:30-2:50 | veo3+screen | **CIERRE (e) — Meristem diferido como tesis.** Zoom-out desde parcela B a red de 8. Cartelas secuenciales silenciosas: **"FAO: 84% explotaciones <2 ha. Producen 36% del alimento."** → **"IRRIFRAME: 40k explotaciones. Servidor central."** → **"Sprout: criterio que viaja a pie."** | 20 s | — | Veo3 + diseno cartelas. |
| 15 | 2:50-3:00 | screen | Tarjeta cierre: logo zigiella + Apache 2.0 + URL repo + cartela micro: **"ITU 2024: 85% conectividad rural global / 58% en zonas remotas."** | 10 s | — | Diseno estatico. |

---

## Planos "must-have" (absolutos)

Si fallan, no hay video:

- **07** — el climax de transferencia cruzada. Sin este, el video no tiene tesis visible.
- **02-03** — Rhizome decidiendo solo con receipt en pantalla. Prueba de que la IA no es decorativa.
- **04-05** — Pollen con Gemma en el movil. Sin este, Pollen no existe visualmente como nodo inteligente (no es mula).
- **10** — Meristem con E4B en laptop + cartela 26B. Honestidad sobre el trade-off MVP.
- **12** — caducidad. Sin este, la capa fisica-temporal es solo un parrafo.
- **13** — amanecer siguiente. Cierra el arco: el criterio aterriza.

---

## Notas de grabacion

- **Hora de rodaje exterior:** amanecer para 01, 04, 09, 13.
- **Reenactment vs demo real:** los planos `real` **no son reenactment**. Se graban contra MVP funcional. Coordinacion con Xilema/Floema/Meristem.
- **Capturas pantalla:** al final del rodaje, con demo pulido.
- **Audio:** VO castellano separado, microfono de mano en ambiente silencioso. Bea dobla a EN para release. Sincronizar en edicion.
- **Veo3:** solo en planos 08 y 14. En ningun otro plano. Si se puede filmar real, se filma real.
- **Cartelas:** motor de densidad informativa. VO poca palabra, cartelas compactas. Tipografia monospace para coherencia con terminales.

---

## Pendiente antes de rodaje

- [ ] Confirmar localizacion exterior (terraza vs. Castellar)
- [ ] Confirmar duracion total exacta con Cambium (1+1-2 min Bea; cota superior?)
- [ ] Fijar persona VO castellano (propuesta: Bea o Corola)
- [ ] Generar planos Veo3 (08, 14) — requiere prompt detallado separado
- [ ] Coordinar con Xilema/Floema/Meristem fecha de MVP filmable
- [ ] Documentar datos sombra (E4B vs 26B) — tarea de Meristem, no bloqueante para rodaje

---

## Historial de versiones

- **v0** (2026-04-19, Corola) — reset tras reframe narrativo (`2026-04-18_reframe-narrativo-pollen_cambium.md`) y clarificacion Meristem diferido (`2026-04-19_meristem-como-revision-diferida_cambium.md`). Climax pasa de caducidad a transferencia cruzada A→B; Meristem se reubica en min 2; se añade cartela 26B objetivo; stack Gemma en cada nodo; Veo3 solo planos 08 y 14. Acepta criterios #12.
- **v0.1** (2026-04-18, Corola) — draft inicial descartado. Construido sobre climax caducidad y arquitectura 3 min sin autosuficiencia min 1.
