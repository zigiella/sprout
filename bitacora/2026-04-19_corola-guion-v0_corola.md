# Guion v0 — racional

**Fecha:** 2026-04-19
**Autora:** Corola
**Area:** Video / produccion
**Tipo:** Entregable (PR contra #12, hermano del shot list v0)

---

## Que entrega este PR

`video/script.md` v0: guion completo con VO castellano, cartelas y
estructura alineada con `shot_list.md` v0 (PR hermano). ~106 palabras
VO (bajo el objetivo ~180 de Cambium — margen holgado para doblaje EN).

## Decisiones aplicadas

1. **VO minimo, cartelas motor.** La densidad informativa vive en las cartelas (BdE, FAO, IRRIFRAME, ITU, stack Gemma). VO hace historia, no dato. Esto permite doblaje EN sin re-sincronizar datos duros.
2. **Apertura y cierre silenciosos.** Cartela "Decide sola hoy." abre. Tripleta silenciosa cierra. Sin VO, sin idioma, sin friccion para jurado anglo.
3. **Frase espinal "Un modelo. Tres profundidades. Tres tiempos."** en el pull-back (fin min 1). Es la tesis: E2B en Rhizome, E2B en Pollen, E4B en Meristem — mismo modelo, tres profundidades (tamaño), tres tiempos (segundos/minutos/horas). El pull-back es el momento donde esto se dice explicitamente.
4. **Climax denso (22 palabras en 15 s).** 0:35-0:50 es el bloque mas dificil de entender para el espectador nuevo. El VO del climax debe explicar *que* pasa, no solo *mostrarlo*. Las 22 palabras estan calibradas para dar tiempo a leer el `rationale` en pantalla mientras se escucha la linea.
5. **Meristem con cartela 26B.** Pedido explicito Bea. Cartela completa: `Meristem · Gemma 4 E4B · Ollama / MVP local 16 GB / arquitectura objetivo: 26B`. Honesto, no apologetico.
6. **Datos duros en cartelas silenciosas:**
   - BdE 20-30% trigo (plano 11): impacto economico agricola español.
   - FAO 84%/36% (cierre): escala del problema — pequeñas explotaciones son la mayoria del alimento mundial.
   - IRRIFRAME 40k central (cierre): contraste con Sprout — "criterio que viaja con quien se mueve" (cartela ajustada en v0.2, ver `bitacora/2026-04-20_corola-guion-v02_corola.md`).
   - ITU 85/58 (tarjeta final): contexto universal de conectividad rural.
7. **Australia 90% fuera.** Por priorizacion (geografia lejana para jurado global), no por calidad.
8. **Caducidad conservada como bloque complementario** (1:50-2:10). Mantiene el clavo narrativo que estaba en v0.1, pero subordinado a la tesis de circulacion.
9. **Amanecer siguiente (2:10-2:30)** cierra el arco temporal: la politica consolidada por Meristem durante la noche aterriza al alba en Rhizome. Prueba visual de que "diferido" funciona.

## Que NO hace este PR

- No cierra #12. Shot list v0 esta en `feat/corola-shot-list-v0` (PR hermano).
- No incluye version EN. Bea dobla al release, no ahora.
- No genera prompts Veo3. Eso va en PR de postproduccion separado.
- No fija persona VO castellano ni localizacion exterior.

## Riesgos

- **Duracion total no confirmada por Cambium.** Bea dice 1+1-2 con final top; brief dice ≤1 min; video/README.md e issue #12 dicen 3 min. v0 asume 3 min (cota superior brief). Si Cambium baja a <2 min, re-editar cierre (plano 14) sin perder la tripleta.
- **Climax (0:35-0:50) es el bloque mas fragil.** Si el MVP no da rationale visible en tiempo real, el VO queda sin soporte visual. Alternativa degradada: captura estatica del rationale tras el hecho.
- **Doblaje EN de la frase espinal.** "Un modelo. Tres profundidades. Tres tiempos." debe sonar igual de rotunda en EN. Propuesta Bea: "One model. Three depths. Three speeds." — decision suya.

## Enlaces

- Issue #12 (shot list + script)
- PR hermano: `feat/corola-shot-list-v0`
- `bitacora/2026-04-18_reframe-narrativo-pollen_cambium.md`
- `bitacora/2026-04-19_meristem-como-revision-diferida_cambium.md`
- `research/narrative_sources.md`
