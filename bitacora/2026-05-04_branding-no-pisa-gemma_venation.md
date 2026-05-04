# Auditoria branding propio — no pisa Gemma

**Fecha:** 2026-05-04
**Autor:** Venation
**Area:** General
**Tipo:** Decision

## Contexto

Cambium pide bitacora corta confirmando que el sistema visual de Sprout no
pisa atributos de Gemma (color oficial, tipografia oficial, marca "G"). Es
prerequisito para la atribucion legal del repo.

## Que hicimos / decidimos

Auditoria del sistema visual de Sprout contra los atributos visuales de
Gemma. Resultado:

### Color
- **Sprout `signal.seed`**: `#C5F26B` (amarillo verdoso, muy luminoso, casi
  lima). Reservado a inteligencia activa o decision en proceso.
- **Gemma azul oficial**: rango `#1A73E8` / `#4285F4` (Google blue family).
- **No hay solapamiento**. Familias cromaticas distintas (verde-amarillo vs
  azul). Ningun token de Sprout cae en azul Google.

### Tipografia
- **Sprout UI**: Manrope (open-source, Florian Karsten, OFL).
- **Sprout datos / JSON**: IBM Plex Mono (open-source, IBM, OFL).
- **Gemma oficial**: Google Sans / Product Sans (propietarias Google).
- **No hay solapamiento**. Ninguna tipografia de Sprout pertenece a la
  familia Google Sans / Product Sans.

### Marca
- **Sprout**: nombre de palabra completo, sin glifo aislado. Sello
  secundario "AI Local-first" en texto plano sobre Manrope.
- **Gemma**: glifo "G" caracteristico (gradiente azul-violeta-rosa).
- **Sprout no usa ninguna "G" aislada como marca**. No hay glifo Sprout
  derivado, inspirado o cercano al glifo Gemma.

### Iconografia
- Iconografia Sprout en `handoff/icons/` es lineal, neutra, sin gradientes
  multicolor caracteristicos de la marca Gemma.

## Por que

Gemma es modelo (E2B local en Rhizome, E4B local en Pollen) usado bajo
licencia Gemma de Google. La atribucion legal exige que el branding del
producto que usa el modelo no se confunda con el branding del modelo. Esto
es lo mismo que un fabricante que usa un motor: puede decir "con motor X"
pero no puede vestirse de marca X.

## Que queda pendiente

- [ ] Si el writeup final menciona Gemma, hacerlo en texto plano sin
      replicar la marca visual Google.
- [ ] Si en algun asset futuro entra un logotipo Gemma como atribucion,
      usarlo intacto (no estilizar, no recolorear) y mantenerlo
      visualmente separado del branding Sprout.

## Enlaces

- [bitacora/2026-05-02_onboarding_venation.md](2026-05-02_onboarding_venation.md)
- [docs/50_pollen_gemma4_e4b_guide.md](../docs/50_pollen_gemma4_e4b_guide.md)
