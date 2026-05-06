# Cartelería física para el rodaje — diseño delegado a Venation

**Fecha:** 2026-05-06 (día 21, cierre)
**Autora:** Corola
**Para:** Venation (productora) + Bea (impresión y rodaje) + Cambium ella (gatekeeper)
**Origen:** decisión Bea día 21 — delegar el diseño de los carteles físicos del rodaje a Venation (antes la tarea estaba sobre Bea según `script.md` v1.5+).

---

## Contexto

Los **4 carteles físicos** del rodaje viven en el guion desde día 16 (decisión Bea): refuerzan la identidad lógica de cada parcela y cada nodo en el plano físico, hacen la diferenciación inmediata para el espectador, y refuerzan los nombres de los nodos durante todo el rodaje.

Hasta hoy día 21, el guion documentaba que **los preparaba Bea**. Bea decide hoy delegar el **diseño** a Venation por dos razones:

1. **Coherencia visual cross-canal.** Venation es responsable del sistema visual del proyecto (`sprout_design_pack_v1`). Los carteles físicos en plano y las corner cards on-screen comparten naming (`PLOT_01 with RHIZOME_01`, `RHIZOME_01 / EDGE NODE`) — deben sentirse del mismo sistema. Si Venation diseña ambos, la coherencia es automática; si los carteles los hace Bea con tipografía genérica (Helvetica), hay disonancia visual entre el cartel físico que ve la cámara y la corner card que aparece on-screen.
2. **División natural del trabajo.** Bea imprime y lleva al rodaje. Venation diseña el archivo imprimible. Cada una en su rol.

**El cambio operativo:** *"los prepara Bea"* → *"Venation diseña archivos imprimibles, Bea imprime y lamina."*

---

## Inventario — 4 carteles físicos

| # | Texto on-cartel | Función en plano | Aparición |
|---|-----------------|------------------|-----------|
| 1 | `PLOT_01 with RHIZOME_01` | Cartel de maceta — anclar identidad lógica de la parcela 01 al plano físico | Visible desde escena 1 (apertura) y todas las escenas de PLOT_01 (E2, E3, E5, E6 plano A, E7) |
| 2 | `PLOT_02 with RHIZOME_02` | Cartel de maceta — anclar identidad lógica de la parcela 02 al plano físico | Aparece en escena 6 plano C (ferry A→B) |
| 3 | `RHIZOME_01 / EDGE NODE` | Cartel de caja electrónica — fijado a cajita Jetson+ESP32, identifica nodo + rol | Escenas E2, E3, E6 plano A |
| 4 | `RHIZOME_02 / EDGE NODE` | Cartel de caja electrónica — **intercambiable con #3 sobre la misma cajita Jetson+ESP32 entre tomas** (decisión Bea día 16: un solo Rhizome físico haciendo dos roles lógicos) | Escena 6 plano C |

---

## Estilo visual

### Tipografía

Recomendación principal: **IBM Plex Mono** (sistema/datos — son IDs técnicos del sistema, no copy humano). Mayúsculas o capitalización según jerarquía que decida Venation.

Variante alternativa por evaluar (criterio Venation): **Manrope** para los carteles de maceta (#1, #2) si crees que encaja mejor como "etiqueta humana sobre un objeto físico" + IBM Plex Mono para los carteles de caja (#3, #4) que son "ID técnico estampado en hardware". La distinción cartel-maceta-vs-cartel-caja es legítima narrativamente (uno es nivel parcela, otro es nivel nodo).

### Paleta

Recomendación principal: **texto `soil.humus` (#2A221D) sobre fondo `soil.oat` (#F3EDE4)** — paleta sobria, lectura cómoda en plano, coherente con el sistema visual.

Variante de alto contraste (criterio Venation): **blanco roto sobre `soil.graphite` casi-negro** si prefieres carteles más "técnicos" / contraste alto. Menos amable pero más industrial.

**Sin `signal.seed`** en los carteles físicos — esa regla 3% se reserva para acentos de "inteligencia activa" on-screen (LED Jetson, resaltados de campo, etc.). Los carteles físicos son etiquetas pasivas, no inteligencia activa.

### Composición

- **Sobria.** No rotulación de huerto turístico, no infantil, no decorativa.
- **Sin logos/iconos extra** salvo que veas que mejora la lectura. Texto puro suficiente.
- **Mismo lenguaje visual que las corner cards técnicas E2/E4 v1.8.1** del lote — los carteles físicos en plano y las corner cards on-screen deben sentirse del mismo sistema. La banda separada `● RHIZOME ─── EDGE NODE` que ya tienes para las corner cards E2 podría inspirar el diseño del cartel físico de caja, sin punto pulsante (el seed no aplica a un objeto pasivo).

---

## Tamaños sugeridos

Bea decide tamaños finales según las macetas y cajas que tenga, pero como punto de partida:

- **Carteles maceta (#1, #2):** A5 (148×210 mm) o A6 (105×148 mm). Suficiente para legibilidad sin dominar el plano.
- **Carteles caja (#3, #4):** A6 (74×105 mm) o más pequeño. Pequeño, pegado a la cajita Jetson+ESP32 con cinta o etiqueta.

Los carteles deben ser **legibles al primer vistazo** desde la distancia de cámara (1-2 metros para los carteles maceta, plano cerrado para los carteles caja). Tu criterio sobre tamaño de fuente final.

---

## Formato de entrega

- **PDF imprimible** (calidad imprenta, 300 dpi mínimo, fonts embedded) — formato principal, lo que Bea usa para imprimir.
- **PNG/SVG** opcional por si Bea quiere variantes o ajustes finales.
- **Bordes para recorte** (margen razonable para imprimir y recortar limpio sin perder el cuerpo del texto).

---

## Plazo

**Idealmente día 22-23.** Bea necesita imprimir + (opcional) laminar antes del rodaje. **Mínimo viable día 25** para llegar al rodaje 26-27 abril (calendario actual, a confirmar por Bea).

**Más urgente que el lote video** porque es producción material no digital — Bea no puede improvisar en rodaje si los carteles no están listos.

---

## Naming sugerido

```
video/wip/carteleria_fisica/
├── cartel_fisico_maceta_PLOT_01.pdf
├── cartel_fisico_maceta_PLOT_02.pdf
├── cartel_fisico_caja_RHIZOME_01.pdf
└── cartel_fisico_caja_RHIZOME_02.pdf
```

(Si entregas también PNG/SVG, mismo patrón con extensión distinta.)

---

## Coordinación

- **PR a main vía Cambium ella** (mismo flujo que el lote v1.8.1).
- **Coordinación lateral con Bea por chat** si surgen decisiones de tamaño/material físico (laminado o no, plastificado, etc.). Bea decide impresión.
- **Si tienes preguntas sobre tipografía/contraste/composición**, lo cierro yo en bitácora propia + cherry-pick rápido (patrón día 19-20).

---

## Por qué bitácora separada (no asset extra del paquete material video)

He valorado dos opciones:

**A) Añadir como Asset 17 al `paquete-material-definitivo-venation_corola.md`**, manteniendo todo en un único inventario.
**B) Bitácora separada** (esta) con foco propio.

Decido **B** por dos razones:

1. **Separación de concerns.** El paquete material video tiene foco en *assets digitales que Bract integra en CapCut*. La cartelería física es *producción material para plano físico que Bea imprime*. Mezclar rompe el foco del paquete material y confunde el inventario.
2. **Plazo distinto, urgencia distinta.** Cartelería tiene plazo día 22-23 (más urgente). Video tiene plazo día 24-25 (menos urgente). Bitácoras separadas dejan las urgencias claras.

Si en el futuro hay que añadir más producción material no-digital al rodaje (decoración de la terraza, elementos de attrezzo, etc.), seguirá el mismo patrón: bitácora separada por categoría de producción.

---

## 📋 Mensaje para Venation (vía chat con Bea)

(El mensaje completo lo redacté en chat con Bea en el último turno del día 21 — está copiado abajo para trazabilidad.)

---

Venation,

Después del lote v1.8.1 listo, te paso la siguiente tarea: **diseño de la cartelería física para el rodaje** (no es video, es producción material que Bea imprime y lleva al plano).

**Decisión Bea: te encargas tú del diseño** (antes la tarea estaba sobre Bea, ahora delegada a ti porque eres responsable del sistema visual y los carteles deben respetar identidad — Manrope/IBM Plex Mono, paleta del proyecto).

**Lo que necesito que produzcas — 4 carteles físicos imprimibles:**

| # | Texto | Función |
|---|-------|---------|
| 1 | `PLOT_01 with RHIZOME_01` | Cartel de maceta — visible desde escena 1 |
| 2 | `PLOT_02 with RHIZOME_02` | Cartel de maceta — aparece en escena 6 |
| 3 | `RHIZOME_01 / EDGE NODE` | Cartel de caja electrónica — fijado a cajita Jetson+ESP32 |
| 4 | `RHIZOME_02 / EDGE NODE` | Cartel de caja electrónica — intercambiable con el #3 sobre la misma cajita (decisión Bea día 16: un solo Rhizome físico haciendo dos roles lógicos) |

**Estilo visual:**

- **Tipografía:** **IBM Plex Mono** (sistema/datos — son IDs técnicos del sistema, no copy humano). Mayúsculas o capitalización según jerarquía que decidas. Si crees que Manrope encaja mejor para los carteles de maceta (más "etiqueta humana") y Plex Mono para los carteles de caja (más "ID técnico"), tu criterio.
- **Paleta:** texto `soil.humus` (#2A221D) sobre fondo `soil.oat` (#F3EDE4), o variante de contraste alto si lo prefieres (blanco sobre `soil.graphite` casi-negro). Tu criterio según legibilidad en plano.
- **Composición:** sobria, no rotulación de huerto turístico ni infantil. Coherente con la estética técnica del proyecto.
- **Sin logos/iconos extra** salvo que veas que mejora la lectura. Texto puro suficiente.
- **Mismo lenguaje visual que las corner cards técnicas E2/E4 v1.8.1** del lote — los carteles físicos en plano y las corner cards on-screen comparten naming, deben sentirse del mismo sistema.

**Formato:**

- **PDF imprimible** + **PNG/SVG** por si Bea quiere variantes.
- **Tamaños sugeridos** (Bea decide finales según las macetas y cajas que tenga):
  - Cartel maceta (#1, #2): A5 (148×210 mm) o A6 (105×148 mm). Suficiente para legibilidad sin dominar el plano.
  - Cartel caja (#3, #4): A6 o más pequeño (74×105 mm o similar). Pequeño, pegado a la cajita Jetson+ESP32 con cinta.
- **Bordes/laminado:** opcional. Bea lamina si lo ve necesario. Suficiente con que el PDF tenga márgenes razonables para imprimir y recortar limpio.

**Plazo:** antes del rodaje (días 26-27 abril). **Idealmente día 22-23** porque Bea necesita imprimir y laminar antes de ir al rodaje. Más urgente que el lote video porque es producción material no digital.

**Naming sugerido:**

```
cartel_fisico_maceta_PLOT_01.pdf
cartel_fisico_maceta_PLOT_02.pdf
cartel_fisico_caja_RHIZOME_01.pdf
cartel_fisico_caja_RHIZOME_02.pdf
```

Ubicación sugerida en repo: `video/wip/carteleria_fisica/` (o donde decidas). Si entregas también PNG/SVG, mismo patrón.

**Coordinación:** PR a main vía Cambium ella (mismo flujo que el lote v1.8.1). Si tienes preguntas sobre tipografía/tamaño/contraste, lo cierro yo en bitácora propia + cherry-pick rápido (patrón día 19-20).

Gracias.

— Corola

---

## Historial de versiones del documento

- **v1** (2026-05-06, día 21, Corola) — primera versión. Inventario 4 carteles físicos + estilo + plazo + delegación diseño a Venation. Bitácora separada del paquete material video por separación de concerns + plazo distinto. Mensaje para Venation incluido para trazabilidad.
