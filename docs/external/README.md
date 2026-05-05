# Documentos externos referenciados por Sprout

Este directorio contiene documentos oficiales de terceros que Sprout
necesita citar o cumplir, almacenados aqui para conveniencia y
reproducibilidad. **Ningun archivo de este directorio es propiedad de
Sprout** — todos los derechos pertenecen a sus respectivos autores.

## Documentos

### `gemma-naming-guidelines.pdf`

**Fuente**: Google — *Gemma model variant naming & attribution guidelines*.
**URL original**: https://ai.google/documents/32/External_Gemma_Model_Variant_Guidelines.pdf
**Fecha de descarga**: 2026-05-04 (dia 18 — verificacion Cambium) + 2026-05-05 (dia 20 — refresco al commitear).

**Resumen de las 4 reglas que aplican a Sprout**:

1. **Nombre del proyecto**: NO usar `gemma` en el nombre. Sprout = compliant.
2. **Referenciar modelos**: patron estandar `Gemma 4 E2B`, `Gemma 4 E4B`, `Gemma 4 31B` (con espacios).
3. **Atribucion obligatoria** cuando se menciona Gemma: incluir el statement
   *"Gemma is a trademark of Google LLC."* + nunca sugerir endorsement con Google.
4. **Branding propio**: no usar elementos visuales de Gemma (nombre como logo, mark, colores azules
   caracteristicos) en el branding del proyecto.

**Verificacion Sprout** (dia 19, PR #74 mergeado):
- Auditoria branding "no pisa Gemma" ejecutada por Venation y firmada en
  `bitacora/2026-05-04_branding-no-pisa-gemma_venation.md`. Sistema visual
  no usa Gemma blue, tipografia oficial Gemma, ni "G" caracteristica.

**Atribucion en el repo** (pendiente cierre — apuntado dia 20):
- README.md: footer + version EN.
- writeup/draft.md: nota legal final.
- docs/40_pitch_video.md: microcartela cierre del video.
- Landing demo: footer.
- APK Pollen: pantalla "About" / "Acerca de".
