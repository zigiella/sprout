# README + CONTRIBUTING bilingues ES+EN

**Fecha:** 2026-04-18
**Autor:** Cambium
**Area:** Docs / onboarding publico
**Tipo:** Decision + ejecucion

---

## Contexto

Issue #15 (P1, abierto el dia 2). El repo es publico; las dos puertas de entrada (`README.md`, `CONTRIBUTING.md`) estaban solo en espanol. Una persona externa anglofona no podia orientarse.

Al mismo tiempo, tenemos ~500 paginas de docs internas y una bitacora en vivo. Traducirlas bilingue seria un **sumidero de mantenimiento** que nadie iba a sostener durante el sprint.

## Decision

Dos capas de idioma, formalizadas en [CONTRIBUTING §13](../CONTRIBUTING.md#13-idiomas-del-repo):

| Zona | Idioma |
|------|--------|
| `README.md`, `CONTRIBUTING.md` | Bilingue ES + EN |
| `docs/`, `bitacora/` | Solo ES |
| Commits, issues, PRs, codigo | Libre |

**Operativa:** al editar README o CONTRIBUTING, se actualizan **ambas** secciones en el mismo PR. Si solo se toca una, issue automatico `priority:P1` para sincronizar.

## Ejecucion

- `README.md`: reescrito con estructura `[ES](#ancla) · [EN](#ancla)` al inicio, ES primero, EN despues, separados por `---`. Contenido equivalente pero no traduccion literal: el slogan *"El agua ya no se pierde solo por escasez..."* se adapto a *"Water is no longer lost only to scarcity. It is also lost because the decision arrives late."* — el ritmo en ingles pide un cierre mas corto.
- `CONTRIBUTING.md`: misma estructura. Las 12 secciones ES se replican en ingles preservando semantica. Nueva §13 "Idiomas del repo" que documenta la regla explicita.
- Enlaces internos: ambas secciones enlazan al mismo `docs/` y `bitacora/` (que son ES-only). Anclas `#contributing-es` / `#contributing-en` y `#sprout-es` / `#sprout-en` para saltar entre idiomas.

## Por que no traduccion literal

- Las convenciones del equipo (roles, codenames, flujo de PR) funcionan igual en ES y EN, pero algunos giros no.
- "Regla dura" -> "Hard rule" suena natural en ambos. "Regla blanda" -> "Soft rules" tambien.
- Ejemplos de paths (`bitacora/2026-04-15_kickoff_cambium.md`) se dejan como estan en ambas versiones — son nombres de archivo reales.

## Verificacion

- [x] Anchors markdown funcionan (`#sprout-es`, `#sprout-en`, `#contributing-es`, `#contributing-en`)
- [x] Enlaces relativos a `docs/`, `bitacora/`, `CONTRIBUTING.md` validos desde ambas secciones
- [x] Regla de idiomas escrita en §13 y referenciada desde README
- [x] Banner bilingue al inicio con emojis de bandera (visibilidad inmediata)

## Pendiente

Ninguno. Cierra #15.

Si aparece un tercer idioma (demanda improbable pero posible si el proyecto cruza fuera del circulo ES+EN), la decision sera abrir otro archivo (`README.fr.md`) en vez de extender el bilingue a trilingue. Dos columnas es legible; tres es ilegible.

## Enlaces

- Issue: #15
- [README.md bilingue](../README.md)
- [CONTRIBUTING.md bilingue](../CONTRIBUTING.md)
- [CONTRIBUTING §13 "Idiomas del repo"](../CONTRIBUTING.md#13-idiomas-del-repo)
