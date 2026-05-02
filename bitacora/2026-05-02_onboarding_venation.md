# Onboarding Venation — direccion de arte

**Fecha:** 2026-05-02
**Autor:** Venation
**Area:** General (con foco en Video y Pollen)
**Tipo:** Avance

## Contexto

Me incorporo formalmente al equipo zigiella en el dia 17 del proyecto, como
direccion de arte, supervisada por Corola en el frente video. Antes de tocar
nada del repo dejo rastro de lo que he leido, lo que entiendo del estado y lo
que voy a hacer (y no hacer) hasta que coordine con Floema, Corola y Bract.

## Que hice / decidi

Lectura obligada antes de cualquier commit:

- `docs/00_estado_vivo.md` — onboarding rapido, dia 16 cierre.
- `CONTRIBUTING.md` completo, especialmente §9.2 (git seguro en maquina
  compartida), §11 (autoria), §12 (flujo de tablero) y §13 (politica de
  idiomas).
- `docs/20_data_contracts.md` + `code/shared/schemas/` — los diez objetos
  canonicos.
- `docs/11_pollen_spec.md` — spec del nodo movil.
- `docs/40_pitch_video.md` — pitch + estructura de las 9 escenas.
- `video/README.md` — alcance del frente video y archivos planificados.

Identidad git local configurada al repo (no `--global`):

```
git config user.name  "Venation"
git config user.email "venation@sprout.local"
```

Rama de trabajo: `feat/venation/design-system-v1`. Verifico los tres puntos de
§9.2 antes de cada commit (`git status` + `git branch --show-current` + `git
stash list`) y prefijo cualquier stash con `[venation]`.

## Por que

Mi trabajo se acopla con dos frentes ya en marcha: Pollen (Floema, blindado y
demo-ready) y Video (Corola guion, Bract montaje). En ambos casos mi rol es
**refinar visualmente**, no reescribir. Antes de proponer cualquier token o
asset necesito hablar con quien manda en cada frente:

- **Floema decide que entra y cuando** en `code/pollen/`. Mi prototipo
  bilingue es referencia, no sustitucion. La conversacion util con ella es
  *"que tokens visuales del design pack se aplican al codigo existente sin
  reescribir logica"*. Mientras no la tenga, no toco `code/pollen/`.
- **Corola es la duena del frente video y mi supervisora directa.** El primer
  encuentro Corola + Bract + yo lo agenda Bea. Hasta entonces dejo handoff
  asincrono en bitacora aparte.

Tambien valido convergencias importantes con la documentacion existente:

- Los schemas que dibuje en mi design pack (`MissionPatch`,
  `DecisionReceipt`, `PolicyPacket`, `WeatherDigest`, `FieldVisit`,
  `SyncBundle`, `ValidationStamp`, `VisitAmendment`) coinciden uno a uno con
  `docs/20_data_contracts.md` y con `code/shared/schemas/`. Los nombres de
  campo tambien (`final_action`, `esp32_outcome`, `why_short`,
  `operator_note`, `horizon_h`, `budget_cap_ml`). El vocabulario esta
  alineado; no necesito reinventar nada.
- La UX minima de Pollen (§11 del spec) — Visitar Rhizome, Dar nueva mision,
  Transportar contexto, Historial — la cubro en el prototipo y la extiendo
  con Audit, Decision log y Meristem sync, que son lectura natural de §3.4
  (interfaz conversacional) y §3.3 (federador) del spec.
- §3.11 introduce `DecisionExplanationResponse` como respuesta JSON de
  `GET /explain/decision/{id}`. Mi pantalla "Ask" en el prototipo consume
  exactamente eso — `explanation` se renderiza como respuesta legible. Es
  punto a verificar con Floema sobre como esta resuelto en `code/pollen/`.

## Decision propia que dejo registrada

`signal.seed` (#C5F26B) lo blindo como **regla del sistema visual**, no como
observacion: se reserva exclusivamente para indicar inteligencia activa o
decision en proceso. No se usa para estados neutros, branding ni decoracion.
Si una pantalla pide seed para algo que no es "IA pensando ahora mismo", la
pantalla esta pidiendo otro token. Cuando se abra el documento del design
system, esa frase entra como regla literal.

## Que queda pendiente

- [ ] Esperar handoff Bea para encuentro Corola + Bract + yo.
- [ ] Esperar canal con Floema para conversacion sobre tokens aplicables a
      `code/pollen/` sin reescribir logica.
- [ ] Bitacora handoff conjunta a Corola y Bract en este mismo dia
      (`2026-05-02_handoff-video-corola-bract_venation.md`).
- [ ] No abrir issue ni mover tarjeta a "In Progress" hasta tener
      coordinacion con los frentes que me afectan. El tablero es la verdad
      (§12.4).
- [ ] Cuando empiece a producir, abrir issue con label `node:cambium`
      (coordinacion/diseno) o el que Cambium considere apropiado para el
      frente arte.

## Enlaces

- [docs/00_estado_vivo.md](../docs/00_estado_vivo.md)
- [docs/11_pollen_spec.md](../docs/11_pollen_spec.md)
- [docs/20_data_contracts.md](../docs/20_data_contracts.md)
- [docs/40_pitch_video.md](../docs/40_pitch_video.md)
- [video/README.md](../video/README.md)
- [CONTRIBUTING.md §9.2](../CONTRIBUTING.md)
