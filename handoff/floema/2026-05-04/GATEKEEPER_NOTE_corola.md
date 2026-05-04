# Nota de Corola (gatekeeper) sobre este paquete

**Fecha:** 2026-05-04 (día 19)
**Autora:** Corola
**Para:** Floema
**Estado:** referencia visual — no canónica, no para integrar a ciegas.

---

## Qué tienes aquí

Material producido por Venation (directora de arte) para tu frente Pollen, traído al repo desde el paquete `handoff/corola/2026-05-04/floema/` (entregado por Bea como ZIP fuera del repo, día 19).

```
handoff/floema/2026-05-04/
├── README.md          ← README de Venation con detalle de qué es canónico
├── Pollen.html        ← HTML compilado del prototipo bilingüe (referencia visual)
├── jsx/
│   ├── android-frame.jsx
│   ├── app.jsx
│   ├── components.jsx
│   ├── i18n.jsx
│   ├── screens-core.jsx
│   └── screens-ext.jsx
└── GATEKEEPER_NOTE_corola.md  ← este archivo
```

## Por qué está en el repo y no en Slack/mail

Venation propuso dos vías en el README del paquete original:

> *"Vía sugerida: directo por Slack/mail sin commit. O rama `feat/venation/jsx-reference` si prefieres trazabilidad."*

Yo elegí inicialmente la primera (sin commit). Bea me señaló que el flujo del equipo zigiella es **repo-first** — todas leemos el repo. Cambio: voy con la segunda opción de Venation (`feat/venation/jsx-reference`), traigo el material al repo donde tú lo encuentras sin esperar relay.

## Léete el README de Venation primero

`README.md` en esta misma carpeta tiene **detalle de qué es canónico y qué no**. Resumen rápido (de su README):

- **Canónico (úsalo como referencia para alinear `code/pollen/`):** spacings, radios, sombras, tokens visuales del design pack día 16.
- **NO canónico:** microcopy. La verdad sigue siendo `strings.xml` / `strings-es.xml` en `code/pollen/`. Si hay divergencia entre los `.jsx` y tus strings, **gana tu código**.

## No es código para integrar literal

Los `.jsx` son **prototipo de Venation** para visualizar la app Pollen con tokens correctos. **No son código de producción** — están pensados como referencia para que tú decidas qué tokens visuales aplican a `code/pollen/` sin reescribir lógica.

Venation lo dice literal en su onboarding (`bitacora/2026-05-02_onboarding_venation.md` §"Por qué"):

> *"Floema decide qué entra y cuándo en `code/pollen/`. Mi prototipo bilingüe es referencia, no sustitución. La conversación útil con ella es: qué tokens visuales del design pack se aplican al código existente sin reescribir lógica. Mientras no la tenga, no toco `code/pollen/`."*

## Cómo coordinar con Venation desde aquí

Por decisión de Bea día 18, la coordinación con Venation funciona así:

- **Mensajes ágiles tú ↔ Venation:** vía Bea como relay (Venation no escribe en repo directo, lee main, te responde por Bea).
- **Si tú produces un PR sobre `code/pollen/` adoptando algún token visual de este material:** Venation lo lee en main y te puede comentar via Bea.
- **Si encuentras divergencias o necesitas refinamientos:** dilo a Bea, ella relayea.

## Sobre el flujo de identidad git

Los archivos del paquete los commiteo con identidad inline `Venation <venation@sprout.local>` (autoría real). Esta nota gatekeeper, con identidad `Corola <corola@zigiella.local>`. Sin persistir en `.git/config`.

## Lo que NO hago como gatekeeper

- **No integro yo a `code/pollen/`.** Eso es tu scope.
- **No decido qué tokens aplican.** Es decisión tuya con Venation.
- **No abro issue de tracking sobre `code/pollen/`.** Cuando estés lista para integrar, abres tu propio issue/PR.

## Si tienes dudas sobre este material

- **Sobre tokens visuales / coherencia con design pack:** Venation (vía Bea relay).
- **Sobre cómo encaja esto con `code/pollen/`:** decisión tuya + posible consulta Cambium ella sobre arquitectura.
- **Sobre el formato del paquete o trazabilidad en repo:** yo (Corola), via repo o vía Bea.

— Corola
