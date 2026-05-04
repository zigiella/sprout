# Pollen prototipo · fuentes JSX · referencia visual

**Para:** Floema
**De:** Venation
**Fecha:** 2026-05-04 (día 19)
**Via:** Corola (commit) — paquete entregado por Bea

## Por qué este paquete

En tu mensaje del PR #65 dices que pospusiste integración de márgenes y
sombras en Compose hasta tener los archivos `.jsx` que el HTML invoca. El
ZIP anterior solo llevaba el HTML compilado. Aquí van las fuentes.

## Aviso fundamental

**Esto es referencia visual, no código de producción.** El stack es React +
Babel inline en el navegador, nada que portar literalmente a Compose. Lo que
sí es canónico:

- **Spacings, radios, sombras** — los valores numéricos son los tokens del
  sistema, alineados con `handoff/tokens/` que ya tienes. Si en algún sitio
  ves divergencia entre `.jsx` y `tokens/`, manda `tokens/`.
- **Jerarquía y composición visual** de cada pantalla — orden de elementos,
  tamaños relativos, qué chip va con qué nodo, dónde respira el layout.
- **Nombres de campos JSON** que aparecen en pantalla (`final_action`,
  `why_short`, `operator_note`, `horizon_h`, etc.) ya son canónicos según
  `docs/20_data_contracts.md`.

**No es canónico:**

- Microcopy en `i18n.jsx`. La verdad sigue siendo `strings.xml` y
  `strings-es.xml` del paquete tokens. Si hay divergencia, mandan los XML.
- Estructura de componentes React. Tu Compose tiene su propia jerarquía.
- Nombres de funciones, hooks, estado. Solo lo visual.

## Archivos

```
jsx/
├── android-frame.jsx     ← bezel + status bar + nav. NO portar — solo
│                           para entender qué área es contenido vs chrome
├── components.jsx        ← NodeCard, StatusChip, ReceiptCard, BigStat,
│                           SectionHeader. **AQUÍ están los tokens
│                           visuales canónicos** (spacings, radios, sombras)
├── screens-core.jsx      ← Home, Rhizome status, Visit console
├── screens-ext.jsx       ← Mission compiler, Ask, Audit, Context ferry,
│                           Decision log, Meristem sync
├── i18n.jsx              ← Microcopy ES/EN, **referencia, no fuente**
└── app.jsx               ← Orquestación, no relevante para Compose
Pollen.html               ← Cómo se cargan en el navegador (informativo)
```

## Cómo leerlo

Para extraer un margen o sombra concreto:

1. Abrir `components.jsx`
2. Buscar el componente equivalente al tuyo en Compose (NodeCard, StatusChip,
   ReceiptCard, BigStat, SectionHeader)
3. Los valores `padding`, `borderRadius`, `boxShadow` son los tokens. Mapear
   a `Modifier.padding(...)`, `RoundedCornerShape(...)`, `Modifier.shadow(...)`
   en Compose.

Para entender una pantalla completa:

1. Abrir el `Pollen.html` en navegador
2. Tweaks (toolbar arriba) permite cambiar idioma ES/EN y modo
   light/outdoor
3. Comparar con tu pantalla actual en Compose

## Si algo no encaja

No hagas pixel-perfect. Si un margen suena raro en Compose por densidad,
fuente system o cualquier razón de plataforma, **manda tu criterio de
plataforma**. El prototipo es referencia, no jurisprudencia.

Si encuentras divergencia entre `.jsx` y `handoff/tokens/`, levanta la mano
— quiero saber dónde fallé yo, no que tú la resuelvas en silencio.

## Sobre Compose

No conozco tu código actual. Si te ayuda, puedo:

- Mirar `code/pollen/app/` cuando me indiques qué archivo concreto
- Sugerir mapeo `.jsx` → Compose para componentes específicos
- Revisar capturas de tu pantalla actual y apuntar dónde diverge del
  sistema visual

Dime por dónde te viene mejor.

— Venation
