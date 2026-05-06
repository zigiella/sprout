# Sprout landing-demo

**Status:** primera version funcional (dia 21). HTML/CSS/JS vanilla, sin
diseno final. Venation reescribira CSS sobre esta estructura HTML estable
cuando llegue su turno (dias 22-25). Floema integrara despues.

**Path operativo**: `landing-demo/` en el repo. Se sirve como sitio
estatico (cualquier hosting de archivos vale).

---

## Estructura

```
landing-demo/
├── index.html              hero + 3 nodos + porqué + how-gemma + footer
├── css/
│   └── style.css           CSS funcional (no diseno final)
├── js/
│   ├── api.js              cliente API + mocks deterministas
│   ├── rhizome-demo.js     interaccion Rhizome
│   ├── pollen-demo.js      interaccion Pollen
│   └── meristem-demo.js    interaccion Meristem
├── try/
│   ├── rhizome.html        demo Rhizome (decision + log)
│   ├── pollen.html         demo Pollen (voz->politica BETA)
│   └── meristem.html       demo Meristem (bundles -> policy)
└── README.md               (este archivo)
```

## Como probar localmente

```bash
cd landing-demo
python3 -m http.server 8000
# abrir http://localhost:8000
```

O cualquier servidor estatico (`npx serve .`, `caddy file-server`, etc.).

## Modo API: mock vs live

El cliente `js/api.js` tiene una constante:

```js
const SPROUT_API_MODE = "mock"; // "mock" | "live"
```

**Por defecto**: `"mock"`. La demo funciona standalone sin red, con
respuestas plausibles deterministas para los 3 casos (Rhizome E2B,
Pollen E4B, Meristem E4B). Util para desarrollo + para servir la demo
sin dependencia de cuenta API.

**Cuando arranquemos API real** (Modal, HuggingFace Inference Endpoints
o Cloud Run con llama.cpp):

1. Cambiar `SPROUT_API_MODE = "live"`.
2. Rellenar `SPROUT_API_ENDPOINTS` con las URLs publicadas:
   ```js
   const SPROUT_API_ENDPOINTS = {
     rhizome_e2b: "https://zigiella--gemma-4-e2b.modal.run",
     pollen_e4b: "https://zigiella--gemma-4-e4b-audio.modal.run",
     meristem_e4b: "https://zigiella--gemma-4-e4b-tools.modal.run"
   };
   ```
3. CORS habilitado en cada endpoint para el dominio de la demo
   (`demo.zigiella.com` o equivalente).

## Hosting plan

**Plan A — zigiella.com / Dinahosting** (decision Bea dia 21):
- Subdominio `demo.zigiella.com` o subdirectorio en pagina existente.
- Subir contenido de `landing-demo/` via FTP / panel del hosting.
- DNS: anadir CNAME si subdominio.

**Plan B (provisional) — GitHub Pages**:
- Activar GitHub Pages sobre rama main, carpeta `/landing-demo/`.
- URL temporal: `https://zigiella.github.io/sprout/landing-demo/`.
- Util mientras Bea configura DNS.

## Lo que ESTA en esta primera version

- Estructura HTML completa con copy + textos en EN (master) + tagline ES
- CSS funcional accesible (mobile-friendly, responsive grids)
- Hero + 3 cards + porque-importa + how-gemma + footer
- 3 demos hands-on:
  - **Rhizome**: form de estado del plot + decision + log live (10 ultimas)
  - **Pollen**: textarea (mock de voz) + compilacion -> MissionPatch + estado BETA
  - **Meristem**: 3 escenarios + bundles -> PolicyPacket + decisions_by_rule
- Disclaimer transparente *"DEMO via API · real app runs local"* en cada try
- Atribucion Gemma trademark en footer de cada pagina
- Badge BETA (ambar) en Pollen — color distinto a `signal.seed` (verde lima)

## Lo que NO esta (y se arregla en iteracion 2)

- **Diseno final visual** — Venation reescribe CSS cuando termine cenital + Z99.
- **API real Gemma 4** — actualmente mock determinista. Live cuando configuremos Modal/HF/CloudRun.
- **Endpoint publico Meristem** — opcional (Plan B segun Floema). Si arranca, anadir aqui.
- **Transcripts navegables** del rodaje real — pendiente rodaje + Bract los integra.
- **Diagramas de arquitectura SVG** — actualmente texto, idealmente diagrama renderizado.
- **i18n completo** — tagline aparece en ES e EN; resto solo EN. README.es.md tiene contenido castellano.
- **Animaciones** — sin movimiento por ahora. Venation puede anadir transiciones cuando entre.

## Pasos siguientes

1. **Bea + Cambium**: review de la primera version + decidir hosting (Plan A / Plan B).
2. **Cambium + Bea**: configurar Modal/HF para Gemma 4 cuando haya tiempo (1-2h setup).
3. **Venation**: reescribir CSS sobre estructura estable cuando termine cenital E09 + Z99 (dias 22-25).
4. **Floema**: cuando version visual de Venation este lista, integrar APK demo flavor + Appetize embed en `/try/pollen` para que el jurado pueda probar el APK real al lado de la version web.

---

## Atribucion / Attribution

Sprout uses Gemma 4 models by Google. Gemma is a trademark of Google LLC.
This project is not affiliated with or endorsed by Google.

License: Apache 2.0 (see [`LICENSE`](../LICENSE)). Same as Gemma 4.
