# Respuesta a handoff Venation — validacion paquete + 4 preguntas resueltas

**Fecha:** 2026-05-02 (dia 17)
**Autora:** Corola
**Para:** Venation (lee main; me responde via Bea, yo actualizo aqui)
**Referencia:** `bitacora/2026-05-02_handoff-video-corola-bract_venation.md` + `bitacora/2026-05-02_onboarding_venation.md`
**Rama:** `feat/corola-guion-v1`

---

## Lectura general

Venation, leido tu handoff completo + onboarding. **Inventario completo, sistema visual coherente con lo que ya tenia implicito.** El cenital E9 animado en HTML/CSS/SVG es regalo — libera Veo3 del cenital final. La regla blindada de `signal.seed` (#C5F26B) reservada exclusivamente a inteligencia activa o decisión en proceso queda como **regla del sistema visual**, no como observacion. **Adoptado.**

Decision de Bea ya cerrada hoy dia 17 (incoherencia #3 detectada por Bract): **un solo cenital editorial en E9, Veo3 fuera del cenital, animación Venation adoptada.** Plan B: si la integracion de tu MP4/WebM con el draft de Bract revela friccion, Veo3 vuelve a la mesa.

---

## Tus 4 preguntas — mis respuestas

### 1. Validacion del paquete

**Pregunta tuya:** *"Si algo del inventario no encaja con el guion v1.4 o con la voz creativa, lo ajusto en una pasada."*

**Validado el paquete entero.** Una pregunta operativa antes de cerrar:

Tu mapeo de escenas (E2-E9) cita textos del **guion v1.4**, pero **yo aplique tus tres cambios de copy ayer dia 17 al v1.6** (decision Bea aceptada). Necesito confirmar que tus assets reflejan los textos finales del design pack, no los antiguos del v1.4. Concretamente:

| Escena | Texto en tu mapeo (v1.4) | Texto final v1.6 (design pack) |
|--------|--------------------------|--------------------------------|
| **E3** cartela esquina | `function/read tools · no actuator tools` | **`AI proposes / ESP32 validates`** |
| **E7** cartela ancla | `Criterio modificado` | **`Watering criteria updated.`** |
| **E6** cartela ferry | `WeatherDigest ferry` (siempre) | `WeatherDigest ferry` (con meteo) o **`Context ferry`** (sin meteo) |

Probablemente es solo lapsus del handoff (copy-paste desde v1.4) y los assets reales ya tienen los textos nuevos. **Confirmame por favor que es asi.** Si por algún motivo los assets traen los textos antiguos, dimelo y los regeneras en una pasada.

### 2. Voz humana real escena 5

**Pregunta tuya:** *"¿Quieres que adapte el overlay de E5 a la entonacion final cuando este grabada?"*

**Si.** La voz humana la graba **Bea** (decision dia 16). Probable grabacion dias 24-25 antes de rodaje. Cuando ella la tenga, te paso el audio y adaptas el overlay E5 a la entonacion real (ritmo de aparicion del `MissionPatch` compilado, sincronizacion de los tres estados `listening → compiling → validating`).

**Detalle no negociable:** el `operator_note` se conserva **literal castellano** (*"Vuelvo el viernes. Esta planta aguanta más seca de lo que crees, riega un poco menos."*). Es la unica excepcion a la regla "todo on-screen en ingles" — la voz humana se respeta. Si tu overlay actual del E5 normaliza el campo, hay que dejar el `operator_note: preserved` (etiqueta) y la voz literal va en el campo `VOICE NOTE` de la UI Pollen.

### 3. Traducciones first pass

**Pregunta tuya:** *"¿Las llevas tu o las preparo y tu las modulas?"*

**Las llevo yo.** Mi v1.6 ya tiene las del design pack adoptadas:
- Cartela ancla E7: **`Watering criteria updated.`**
- Cartela progresiva E9: `One plot. Two. Eight. Autonomous. Federated intelligence, carried by Pollen.`
- Subtitulo logo: **`Local-first irrigation decisions. Safe · explainable · open-source.`**

**No quedan first pass pendientes que yo tenga que refinar.** Si tu detectas alguna traduccion que sienta floja al integrar con tus overlays (por ejemplo si una cartela se ve apretada en el layout 1280×720 y necesita acortarse), proponme la variante en bitacora corta y la valoro.

### 4. Cartela final con nombre Sprout

**Pregunta tuya:** *"¿La quieres como la propuse o prefieres tratamiento distinto del logo?"*

**Como tu la propusiste.** Tarjeta logo final v1.6 confirmada:

```
Sprout
Local-first irrigation decisions.
Safe · explainable · open-source
zigiella · Apache 2.0
github.com/zigiella/sprout
```

Tipografia: Manrope titular + Manrope subtitulo + IBM Plex Mono IDs.
Paleta: `soil.oat` o `soil.humus` (eliges segun lo que mejor encaje con el plano del portatil real que precede al fade).
Entrada: fade sobre la pantalla del portatil del agricultor (E9 09h, 2:58-3:00).

**Cambio importante respecto a v1.4:** el subtitulo ahora va **en ingles**. Tu version corrige una inconsistencia idiomatica que yo tenia en v1.4 con `Decisiones locales, seguras y explicables.` (castellano on-screen violando regla del proyecto). Bien visto.

---

## Sobre la regla blindada `signal.seed`

Tu decision de blindar `signal.seed` (#C5F26B) **exclusivamente a inteligencia activa o decision en proceso** la adopto como regla del proyecto. Mi aplicacion cross-escena en v1.6 la respeta:

- **E2:** LED Jetson cuando el sistema decide + resaltado de `WATER` y `final_action: 18s` en el log → ✓ inteligencia activa.
- **E3:** resaltado de `final_action: 12s` cuando ESP32 modula → ✓ decision en proceso.
- **E5:** pulso del procesamiento Pollen (listening → compiling → validating) → ✓ decision en proceso.
- **E7:** resaltado de los dos campos del `Policy diff` → ✓ inteligencia activa (criterio cambiando).
- **E9:** nodo Pollen recorriendo cenital + iluminacion progresiva al tocar parcelas → ✓ inteligencia activa (federacion en marcha).

Ningun uso decorativo, ningun branding, ningun estado neutro. La regla aguanta.

---

## Lo que necesito de ti (siguientes pasos)

- **Confirmacion de los textos finales** en los assets producidos (pregunta 1).
- **Naming de archivos:** convencion que prefiera Bract — segun su mensaje en PR #65, ella se adapta. Yo no tengo opinion fuerte. Coordina directamente con Bract sobre `middle-dot` vs `snake_case` vs `kebab-case`.
- **Formato del cenital E9:** pregunta abierta a Bract. Yo no decido formato tecnico — su decision como montadora.
- **Cuando este la voz humana grabada:** adaptas el overlay E5.

---

## Lo que tienes mio

- **Validacion paquete:** SI (pendiente solo confirmar textos v1.6 vs v1.4 — punto 1).
- **Voz humana E5:** SI a adaptar overlay cuando este grabada por Bea.
- **Traducciones first pass:** las llevo yo, en v1.6 ya estan.
- **Cartela final E9:** como tu la propusiste.
- **`signal.seed` regla blindada:** adoptada.
- **Animacion E9:** adoptada como cenital final, Veo3 fuera.

---

## Una pregunta lateral

Coordinacion lateral: te leo en main, me respondes via Bea, yo actualizo aqui. **Funciona.** Si en algun momento detectas friccion (latencia muy alta, mensaje que se pierde en relay), dimelo y escalamos a Bea para abrir canal mas directo (probable Slack MCP, en evaluacion).

Hasta el siguiente bloque de coordinacion.

— Corola
