# Cierre día 23 — Bract

**Fecha:** 2026-05-08
**Autora:** Bract
**Para:** Cambium (Bea pidió bitácora siguiendo convención Corola)
**Rama:** `feat/bract-cierre-dia-23`

---

## Lo que ha pasado hoy

Bea grabó día 22 en Castellar (10 clips brutos). Hoy hemos abierto el bruto, hecho ingeniería inversa con Gemini 3.1 Pro vía proxies (~$0.20), y construido el primer montaje real con su material. Hemos iterado en olas hasta el draft 17:

1. **Análisis ingenuo** de los 9 clips útiles. Notas en `produccion/rodaje-bea1/NOTAS_INGENIERIA_INVERSA.md` (12 hallazgos relevantes — entre ellos: voz humana de Bea grabada inline en E5, E3D y E7 son byte-idénticos, un asset RHIZOME mal etiquetado).
2. **TerminalLog.tsx** parametrizable + 9 logs por escena (`logs-data.ts`) como provisional hasta que Floema/Xilema/Meristem entreguen capturas reales. Mismo pipeline para sustitución directa.
3. **SplitScreen.tsx** "doble página" — clip izq + log der, con `compact` mode (font/padding reducidos para half-screen) y soporte de freeze frame (PNG del último frame del clip). 5 splits renderizados: E2, E3A, E4b, E5, E6.
4. **Re-trim** de E4 y E4b sin recortes (incluyendo sonrisa final + "Vale" coloquial) y luego E4 a 10.5s tras feedback (corte antes de salir del encuadre).
5. **3 cartelas presentadoras** de agentes — Rhizome / Pollen / Meristem (full-screen tipográfico estilo "Three days later", 3s cada una).
6. **E3b reubicado** del slot 0:48-0:58 al 2:40.5-2:50.5 (antes del cenital). Bookend con E9b funciona mejor ahí, decisión Bea.
7. **Voz off ES dub** completa del guion v1.8.3 (`copies_bilingual.md` v0.6) integrada como track de captions provisional. 14 líneas con las 6 frases fuertes en sus posiciones del guion. SRT humano editable en `data/subtitles-es.srt`. Pendiente: cuando Bea pase API key de ElevenLabs, sintetizo los 14 audios y reemplazo captions por VO real.
8. **Track minutaje doble** (debug, opcional vía `TIMECODE=1 ./run.sh`): absoluto en sup-derecha (dust gris) y relativo a escena en sup-izquierda (seed verde, formato `<short> +<segs>s`). Permite a Bea darme feedback al segundo dentro de cada escena.
9. **Créditos** con cargos Bea finales (*Product Owner / Concept Director / camera / human voice*), papá cariñoso (*Rhizome box · daily journal reader*), localizaciones (Castellar de n'Hug + Barcelona). Compact mode para que las 20 líneas quepan sin overflow.

Bea ha refinado los JSONs al final del día (timings finos de las 14 VOs respecto a la nueva timeline con E3b movido y las cartelas presentadoras). Esos ajustes no están en el draft 17 generado todavía — entrarán mañana con sus ajustes nuevos.

---

## Estado del draft 17

```
Draft ID: c97c8002-db36-41f5-b7e8-a566c31b14f6
Total: 3:43 (223s)
Tracks: 9 (base, clips, logs, overlays, caption rojo, audio, voz off, timecode abs, timecode rel)
materialSummary: videos 38 · audios 2 · texts 461
```

**Estructura v1.8.3-H** — sigue el guion v1.8.3 con dos desviaciones documentadas:

- E1 sin los 4 datos al inicio (Bea decidió "Opción B" día 23: solo pregunta abierta, datos al final como cartela provisional `FourDatosProvisional`)
- 3 cartelas presentadoras (Rhizome / Pollen / Meristem) que el guion v1.8.3 no contempla — añadidas para reforzar la jerarquía narrativa de los 3 agentes según petición Bea día 23 noche.

---

## Pendiente

1. **Voz** (próximo bloque grande): Bea me pasará API key de ElevenLabs. Cojo `subtitles-es.json` → genero 14 audios sintetizados → integro como tracks de audio → bajo volumen del fondo durante VO. Pendiente decidir si el master es ES o EN (guion v1.8.3 dice EN master + ES dub; pero hoy estamos generando con ES por proximidad de Bea con el copy).
2. **Capturas reales Floema** (Pollen UI E4b/E5/E6): petición preparada, Bea va a validar antes de mandar. Cuando lleguen, sustitución 1:1 en `clips.json` sin tocar timing (ese es justo el motivo de los placeholders Remotion).
3. **Capturas Meristem-nodo real** (E3b + E9b): pendiente Meristem-agente. Mientras tanto Placeholder italic *"Meristem composes / stores and processes."* aguanta.
4. **TF1 + 4 datos + créditos finales**: hoy son provisionales. Cuando Venation entregue cartelas finales o Corola valide copy, sustituyo.
5. **Música**: `sonido-fondo1.mp3` está como track 6 (looped 2x). No he podido analizarla con VL — Bea decide si encaja o cambiamos.
6. **Ajustes finos mañana**: Bea anunció "ajustes fáciles" para día 24. Estoy lista.

---

## Archivos críticos

```
sprout-repo/video/copies_bilingual.md v0.6     ← guion fuente VOs
sprout-repo/video/montage_brief.md v0.2        ← brief Corola por escena
produccion/remotion/src/                       ← TerminalLog, SplitScreen,
                                                 Placeholder + 3 cartelas
                                                 + 5 SplitScreens + Creditos
cutcli/10-borrador-rodaje-bea1/                ← pipeline montaje
  data/clips.json (16 clips + 3 cartelas)
  data/logs.json (3 logs residuales)
  data/overlays.json (15 overlays Venation)
  data/subtitles-es.json (14 VOs ES dub)
  data/subtitles-es.srt (mismo, humano editable)
  data/audios.json (2 loops sonido-fondo)
  data/timecode.json + scene-timecode.json (debug)
  run.sh (9 tracks, TIMECODE=1 opcional)
```

---

## Nota personal

Día intenso pero limpio. Bea está dirigiendo con criterio y velocidad — cierra decisiones en una vuelta y deja que el frente avance sin atascos. El pipeline `cut_cli + Remotion` está aguantando bien la iteración rápida (drafts 10→17 en un día sin friction). Cuando lleguemos a voz síntesis y capturas reales, el sistema absorbe los cambios sin tocar timing.

Buenas noches y hasta mañana.

— Bract
