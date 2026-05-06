# Guía de rodaje · Sprout vídeo v1.8.3 — Castellar de n'Hug

**Para:** Bea, durante rodaje.
**Versión guion:** v1.8.3 (`script.md` + `montage_brief.md` v0.5).
**Fecha:** 2026-05-06 (día 21).
**Autora:** Bract.

---

## Cómo usar este documento

1. Llévalo en el móvil o impreso. Marca con ☑ las tomas que vas haciendo.
2. **No improvises el orden**: graba escena por escena en el orden de
   este documento. Si la luz o el clima te obligan a cambiar, anótalo
   en *Notas* al final y avisas a Bract para reordenar en montaje.
3. Si algo sale mal, sigue. Marca en *Notas* qué falló y si conviene
   repetir mañana o puede sustituirse por otra cosa (Bract decide en
   montaje).

---

## Atrezzo a preparar la noche anterior

### Carteles físicos (Manrope SemiBold + IBM Plex Mono micro-IDs, fondo `soil.oat` o kraft mate)

- ☐ `PLOT_01 with RHIZOME_01` (cartel maceta, A5 mínimo)
- ☐ `PLOT_02 with RHIZOME_02` (cartel maceta, A5 mínimo)
- ☐ `RHIZOME_01 / EDGE NODE` (cartel caja electrónica, A6)
- ☐ `RHIZOME_02 / EDGE NODE` (cartel caja electrónica, A6 — intercambiable con el anterior sobre la misma cajita)

### Hardware

- ☐ Cajita Jetson + ESP32 dentro
- ☐ Sensor de humedad clavable
- ☐ Válvula visible (ideal con manguera transparente para que se vea el agua)
- ☐ Maceta principal (PLOT_01) con planta de tomate / fresa / lo que sea visible
- ☐ Maceta secundaria (PLOT_02) zona distinta de la terraza, planta distinta
- ☐ Garrafa o depósito de agua con conexión a la válvula
- ☐ LED del Jetson visible (debe parpadear cuando decide)
- ☐ Móvil con app Pollen funcionando (con UI Floema o mock fiel)
- ☐ Portátil casero con UI Meristem funcionando (con UI Meristem o mock fiel)

### Cámara y audio

- ☐ Móvil de rodaje (cámara principal)
- ☐ Trípode o mini-trípode flexible
- ☐ Micrófono externo o lapel (ideal para la voz humana E5)
- ☐ Power banks cargados
- ☐ Memoria libre: mínimo 32 GB en el dispositivo de grabación
- ☐ App de claqueta o cuenta atrás (opcional pero útil)

### Logística

- ☐ Espacios listos: terraza con dos zonas + cocina con portátil sobre mesa
- ☐ Plano contingente si llueve (cubrir maceta, mover lo que sea exterior bajo techo)
- ☐ Identificación clara entre PLOT_01 y PLOT_02 (la cámara y los carteles tienen que distinguirlos sin lugar a dudas)

---

## Convenciones de toma (válidas para todas las escenas)

- **Mínimo 3 takes por plano útil.** Si el primero te convence, sigue grabando dos más. Cuesta menos grabar de más que volver a Castellar.
- **Pre-roll y post-roll**: empieza grabando ~2 s antes y termina ~2 s después del momento útil. Bract recorta en montaje.
- **Wild track** (ambiente sin acción): graba 30 s del ambiente sonoro de la terraza, 30 s de cocina y 30 s de cualquier sonido específico (válvula, agua) por separado, **sin hablar y sin moverte**. Útil para parchear audio en montaje.
- **Identifica cada toma**: con palabra (*"E2 plano 2A take 2"*) o con palmada antes del *acción*. Bract puede catalogar fácil después.
- **Si dudas, rueda más**: rueda más segundos, rueda más takes, rueda otro encuadre. Es la materia prima.

---

## Por escena (solo lo que tú grabas)

### E2 · Rhizome decide en local · 0:25–0:50

#### Plano 2A · Jetson en su caja · ~1 s útil

Plano cerrado del Jetson dentro de la caja. Carteles **`PLOT_01 with RHIZOME_01`** + **`RHIZOME_01 / EDGE NODE`** visibles. LED del Jetson parpadea cuando "decide" (puedes simularlo encendiendo manualmente). Cámara baja al sensor de humedad clavado en tierra.

- **Encuadre**: cerrado sobre la cajita.
- **Movimiento**: estático o ligero tilt-down al sensor al final.
- **Duración a grabar**: 5-6 s (montaje recorta a 1 s útil).
- **Takes mínimos**: 3.
- **Atrezzo**: cajita Jetson + ESP32 + LED visible, cartel caja, cartel maceta, sensor humedad clavado.
- **Audio**: ambiente exterior (viento sutil).
- **Notas**: __________________________

#### Plano 2D · Válvula abriéndose · 5 s útil

Plano de la válvula. Se abre. Sonido de agua sobre tierra.

- **Encuadre**: cerrado sobre la válvula.
- **Movimiento**: estático.
- **Duración a grabar**: 8-10 s.
- **Takes mínimos**: 3.
- **Atrezzo**: válvula, manguera, garrafa, tierra debajo.
- **Audio**: agua cayendo sobre tierra (en directo si la mecánica lo permite, si no graba wild track aparte).
- **Notas**: __________________________

#### Plano 2E · Sostenido sobre el agua · 2 s útil

Continuación del 2D. La cámara se mantiene sobre el agua cayendo.

- **Encuadre**: igual que 2D, sin moverse.
- **Movimiento**: estático.
- **Duración a grabar**: graba 2D y 2E como una sola toma de 10-12 s; Bract corta en montaje.
- **Notas**: __________________________

---

### E3 · ESP32 SAFE LIMIT · 0:50–1:05

#### Plano 3A · Cajita ESP32 · 3 s útil

Plano cerrado de la cajita ESP32. Cartel **`RHIZOME_01 / EDGE NODE`** visible. **LED ámbar encendido — atención, no alarma.**

- **Encuadre**: cerrado.
- **Movimiento**: estático.
- **Duración a grabar**: 6 s.
- **Takes mínimos**: 3.
- **Atrezzo**: cajita, cartel, LED ámbar (cambiar el LED del Jetson o usar otro LED).
- **Audio**: click electrónico sutil del LED si lo tienes; si no, wild track.
- **Notas**: __________________________

#### Plano 3D · Válvula chorro corto · 4 s útil

Plano de la válvula. Se abre. **Pero menos tiempo del propuesto** (chorro de ~12 s real cronometrado vs los 18 s del plano 2D). La diferencia visual es la prueba narrativa.

- **Encuadre**: igual que 2D para que se note la diferencia de duración.
- **Movimiento**: estático.
- **Duración a grabar**: 6-8 s (montaje deja 4 útiles).
- **Takes mínimos**: 3.
- **Atrezzo**: válvula, manguera, agua.
- **Audio**: agua cayendo, claramente más breve que en 2D.
- **Notas**: __________________________

---

### E3b · Meristem prepara la política (cocina) · 1:05–1:15

#### Plano 3bA · Cocina con portátil · 3 s útil

Plano de la cocina. **Tú de espaldas o en perfil borroso (no se ve cara).** Portátil casero abierto sobre mesa.

- **Encuadre**: medio. Tú al lado del portátil, no centrada.
- **Movimiento**: estático.
- **Duración a grabar**: 6 s.
- **Takes mínimos**: 3.
- **Atrezzo**: portátil con UI Meristem corriendo o mock, mesa de cocina con elementos cotidianos sutiles (taza, cuaderno).
- **Audio**: ambiente cocina sutil.
- **Notas**: __________________________

#### Plano 3bB · Detalle pantalla portátil · 4 s útil

Cámara se acerca a la pantalla del portátil. UI Meristem componiendo política.

- **Encuadre**: cerrado sobre pantalla.
- **Movimiento**: ligero zoom-in o estático.
- **Duración a grabar**: 6-8 s.
- **Takes mínimos**: 3.
- **Notas**: si la UI Meristem real no entrega, Bract pondrá un mock fiel encima en montaje. Tú graba el plano del portátil con cualquier pantalla; el contenido se sustituye en post.
- **Notas**: __________________________

#### Plano 3bC · Pollen recibe sobre la mesa · 3 s útil

Plano sobre la mesa: el móvil (Pollen) recibe la política del portátil. Visualmente conexión entre los dos dispositivos.

- **Encuadre**: medio cerrado, los dos dispositivos visibles.
- **Movimiento**: estático.
- **Duración a grabar**: 5-6 s.
- **Takes mínimos**: 3.
- **Notas**: __________________________

---

### E4 · Llega Pollen · 1:15–1:40

#### Plano 4A · Persona entra · 5 s útil

Cambio de luz. Entras en plano. **No vemos cara — vemos manos, móvil en la mano.** Cartel `PLOT_01` visible al fondo. Plano medio. Te acercas a la maceta.

- **Encuadre**: medio. Recorta cabeza, deja manos y torso.
- **Movimiento**: la persona se mueve, la cámara puede ser estática o seguirla con paneo lento.
- **Duración a grabar**: 8-10 s.
- **Takes mínimos**: 3.
- **Atrezzo**: móvil con app Pollen abierta, planta visible, cartel PLOT_01.
- **Audio**: ambiente exterior.
- **Notas**: __________________________

#### Plano 4D · Mirando la planta · 8 s útil

Plano tuyo mirando la planta, contrastando lo que ves con lo que el móvil te dice. Sin diálogo, plano respiratorio.

- **Encuadre**: medio o medio cerrado, sin cara.
- **Movimiento**: estático.
- **Duración a grabar**: 12-15 s.
- **Takes mínimos**: 3.
- **Atrezzo**: planta, móvil en la mano.
- **Audio**: ambiente exterior. **Wild track de 30 s después de esta toma**.
- **Notas**: __________________________

---

### E5 · La persona da una misión · 1:40–2:00

⚠️ **Esta escena tiene voz humana en castellano grabada al natural. Hazlo en silencio absoluto.** Si hay viento fuerte, ráfaga de tractores, o cualquier ruido, espera y repite.

#### Plano 5A · Pulsar grabar · 3 s útil

Plano cercano. Pulsas el botón de grabación de voz. Acercas el móvil a la cara. **Sin labios en cuadro** — vemos tu mano sosteniendo el móvil.

- **Encuadre**: cerrado sobre mano + móvil.
- **Duración a grabar**: 5 s.
- **Takes mínimos**: 3.
- **Atrezzo**: móvil con UI VOICE NOTE activo en pantalla.
- **Audio**: click de grabación nítido.
- **Notas**: __________________________

#### Plano 5B · Voz humana · 7 s útil

Dices, en castellano, **literal y calmada**:

> *"Vuelvo el viernes. Esta planta aguanta más seca de lo que crees, riega un poco menos."*

- **Encuadre**: igual que 5A, sostenido sobre el móvil.
- **Tono**: tranquilo, casi casual. No teatral, no recitado, conversacional.
- **Duración a grabar**: 12-15 s incluyendo respiraciones.
- **Takes mínimos**: **5** (es la voz que va al corte final, queremos opciones).
- **Audio**: micro lapel o de mano cerca, **silencio absoluto alrededor**.
- **Notas críticas**:
  - Esta toma se va a usar en la versión castellano y se subtitulará al inglés. Es **la única excepción narrativa**: el resto del VO va en inglés.
  - Si te equivocas, no pares: termina la frase y vuelve a empezar. Bract elige el take limpio.
- **Notas libres**: __________________________

#### Plano 5E · Plano cerrado del móvil · 2 s útil

Plano cerrado del móvil tras grabar. Patrón de respiración antes del corte.

- **Encuadre**: cerrado.
- **Duración a grabar**: 4 s.
- **Notas**: __________________________

---

### E6 · Ferry A→B · 2:00–2:20

⚠️ **PLOT_01 NO lleva estación meteo en plano físico** (decisión Bea día 21, ruta principal sin meteo). Si al final tienes tiempo y quieres añadirla, dímelo: hay una versión de cartelas en plan B reactivable.

#### Plano 6A · Persona junto al PLOT_01 · 5 s útil

Plano tuyo junto a PLOT_01. Carteles **`PLOT_01 with RHIZOME_01`** + **`RHIZOME_01 / EDGE NODE`** visibles. **Sin estación meteo**. El móvil descarga el `Context bundle`.

- **Encuadre**: medio. PLOT_01 a un lado, tú al otro, móvil visible.
- **Duración a grabar**: 8 s.
- **Takes mínimos**: 3.
- **Atrezzo**: PLOT_01 + carteles + móvil.
- **Notas**: __________________________

#### Plano 6C · Persona junto al PLOT_02 · 8 s útil

Plano tuyo junto a **PLOT_02** (otra zona de la terraza, otra planta, cartel `PLOT_02`). Pollen entrega el bundle al Rhizome 02.

- **Encuadre**: medio. **Cambio claro de fondo respecto a 6A** (otra zona, otra planta).
- **Duración a grabar**: 12 s.
- **Takes mínimos**: 3.
- **Atrezzo**: PLOT_02 + carteles + móvil.
- **Notas críticas**:
  - El cartel sobre la cajita Rhizome cambia (`RHIZOME_01` → `RHIZOME_02`). **Sustitúyelo entre tomas**.
  - Visualmente la planta tiene que ser **distinguible** del PLOT_01 para que se note que es otra parcela.
- **Notas**: __________________________

#### Plano 6D · Rhizome 02 con bundle · 3 s útil

Plano del Rhizome 02 con bundle aceptado. La cámara respira.

- **Encuadre**: cerrado sobre la cajita con cartel `RHIZOME_02`.
- **Duración a grabar**: 5 s.
- **Notas**: __________________________

#### Plano 6E · Sostenido · 3 s útil

Continuación 6D. Plano sostenido para que la VO en EN encaje (la añade Bract en post).

- **Duración a grabar**: graba 6D y 6E juntos (8-10 s totales).
- **Notas**: __________________________

---

### E7 · CLIMAX · Watering criteria updated · 2:20–2:40

#### Plano 7E · Válvula chorro corto y controlado · 8 s útil

Plano de la maceta y la válvula. Se abre. **Menos tiempo que en E2** — chorro corto, calculado, austero (12 s real cronometrado vs 18 s en E2). La diferencia es la prueba narrativa.

- **Encuadre**: igual que 2D para que se note la diferencia.
- **Duración a grabar**: 10-12 s.
- **Takes mínimos**: 3.
- **Atrezzo**: válvula, manguera, agua, maceta visible.
- **Audio**: agua cayendo, **claramente más breve que en 2D**.
- **Notas**: si por logística no podéis cronometrar exactamente, Bract recorta en montaje al tiempo que necesita.
- **Notas**: __________________________

---

### E9b · Meristem recibe + cierre íntimo (cocina) · 3:10–3:20

#### Plano 9bA · Cocina con portátil · 3 s útil

**Continuidad visual con E3b** (misma cocina, misma posición). Tú de espaldas o perfil borroso. Portátil abierto. Móvil sobre la mesa entregando datos al portátil.

- **Encuadre**: similar a 3bA pero ligeramente distinto (otra hora del día, luz cambiada si se puede).
- **Duración a grabar**: 6 s.
- **Takes mínimos**: 3.
- **Atrezzo**: igual que E3b.
- **Notas**: si conseguís que la cocina sea **misma cocina pero hora distinta** (mañana vs tarde, luz visiblemente distinta), refuerza el bookend narrativo.
- **Notas**: __________________________

#### Plano 9bC · Cutaway opcional a macetas reales · 2 s útil

⭐ **OPCIONAL. Si tienes tiempo, grábalo. Si no, Bract sigue con plano cocina.**

Cutaway micro a las macetas reales en la terraza (Sprout escala 1 corriendo). Refuerza la convención maceta-parcela del cierre.

- **Encuadre**: cerrado sobre las macetas.
- **Duración a grabar**: 5 s.
- **Notas**: __________________________

#### Plano 9bD · Vuelta a la cocina · 2 s útil

Vuelta al plano cocina para cerrar.

- **Duración a grabar**: 4-5 s.
- **Notas**: __________________________

---

## VO de referencia en castellano (graba aparte, no durante rodaje en cuadro)

Esto es **audio aparte**, sin imagen. Lo grabas tú **en castellano como
referencia para timing y sincronización en montaje**. La versión inglés
master se hace después (doblaje con ElevenLabs o regrabación tuya en
inglés en otra sesión).

Idealmente: día previo o posterior al rodaje, en interior silencioso, con
el mismo micro que usas para la voz humana E5.

Tono **calmado, declarativo, no enfático**. Pausa entre frase y frase
(útil para que Bract pueda recortar limpio en montaje). No teatral.

Frases que lees (todas, en orden, en castellano):

| Escena | VO castellano referencia |
|---|---|
| E2 plano 2B | *"Esta parcela no está sola. Tiene un cerebro local. Lee el suelo. Decide."* |
| E2 plano 2C | *"Y firma lo que hace, para que se pueda explicar."* |
| E2 plano 2E (frase ancla 1) | *"Rhizome mantiene viva la parcela — sin nadie, sin red."* |
| E3 plano 3B (frase ancla 3) | *"La IA propone, la capa física dispone."* |
| E3b plano 3bC | *"Meristem compone la política."* |
| E4 plano 4D (frase ancla 2) | *"Cada visita de Pollen puede cambiar el criterio local."* |
| E5 plano 5E | *"Lo que la persona dice se convierte en política."* |
| E6 plano 6A | *"Pollen trae preguntas, respuestas y contexto."* |
| E6 plano 6E (frase ancla 5) | *"Pollen convierte esas visitas en inteligencia federada."* |
| E7 plano 7E | *"El sistema ajusta los cuidados."* |
| E8 plano 8C (frase ancla 4) | *"Toda inteligencia tiene jurisdicción. Y caducidad."* |
| E9b plano 9bD (frase ancla 6) | *"Meristem guarda y procesa. Mañana, aprenderá."* |

**Graba cada frase 3 veces como mínimo** y déjame elegir el take.

**Cómo lo nombras**: en archivo separado por escena (`vo_E2_2B_take1.wav`,
etc.) o en una sola sesión continua diciendo *"E2 plano 2B take 1"* antes
de cada frase. Bract corta y cataloga después.

**Excepción** — la voz humana de E5 plano 5B *"Vuelvo el viernes…"* va en
cuadro durante rodaje, no aquí. Esa es la única VO que se graba con la
imagen.

---

## Lo que NO grabas (otra gente lo entrega o ya está)

- Capturas de pantalla del Jetson (E2, E3, E7) → Xilema o mock fiel.
- Capturas de pantalla del móvil Pollen (E4, E5) → Floema o mock fiel.
- Capturas de pantalla del portátil Meristem (E3b, E9b) → Meristem o mock fiel.
- Cartelas tipográficas (E0, E1×5, E2 bisagra, E03 ancla, E08, E09b bookend, Z99) → Venation, ya entregadas.
- Cenital E9 animado → ya integrado en montaje.

Si en rodaje pasas cerca de una pantalla técnica encendida con la UI real corriendo, **graba un take de respaldo** por si la captura oficial no llega a tiempo. Plano cerrado, 5 s. No te preocupes por la calidad de la pantalla, es respaldo de emergencia.

---

## Checklist final por toma

Cada vez que terminas un plano:

- ☐ Mínimo 3 takes grabados
- ☐ Pre-roll y post-roll incluidos
- ☐ Wild track de la zona si es la primera vez allí (30 s)
- ☐ Marca en este documento que está hecho
- ☐ Si algo falló, anotado en *Notas*

---

## Plan B si algo importante sale mal

| Si falla… | Plan B |
|---|---|
| Voz humana E5 (ruido, te equivocas todas las takes) | Re-grabamos en interior silencio absoluto otro día. No es bloqueante. |
| LED Jetson no parpadea | Bract hace pulsar en post (cartela superpuesta o cambio de brillo). |
| Válvula no abre limpio | Tú giras manualmente y cortamos en montaje. |
| Tiempo de chorro mal cronometrado | Bract recorta en montaje, no se ve. |
| Cartel se cae a mitad de toma | Continúa, lo levantamos en post o recorta. |
| Llueve | Cocina E3b, E9b se puede grabar bajo techo. Aprovecha. |
| Te queda batería | Para. Carga. No hay prisa. |
| Te entran ganas de improvisar un plano que no estaba | Hazlo. Mándamelo. Si funciona, lo monto. Si no, no perdimos nada. |

---

## Lista de prioridad de tomas (si te quedas sin tiempo)

**Imprescindibles** (sin esto no hay corte):

1. E2 plano 2D-E (válvula abierta)
2. E5 plano 5B (voz humana)
3. E6 plano 6A + 6C (PLOT_01 → PLOT_02 con cambio claro de fondo y cartel)
4. E7 plano 7E (válvula chorro corto)
5. E9b plano 9bA (cocina con portátil)

**Importantes** (sin esto Bract apaña con cartelas / capturas):

6. E2 plano 2A (Jetson en caja)
7. E3 plano 3A (cajita ESP32 con LED ámbar)
8. E3 plano 3D (válvula chorro corto controlado)
9. E3b plano 3bA-bC (cocina + portátil + transferencia)
10. E4 plano 4A + 4D (persona + planta)
11. E5 plano 5A + 5E (mano + móvil)

**Opcionales** (gana puntos pero el corte funciona sin):

12. E9b plano 9bC (cutaway macetas reales)
13. Cualquier captura de pantalla en directo si pasas cerca de una

---

## Notas libres del rodaje

(usa este espacio para apuntar lo que se desvía del plan, ideas, cosas que decir a Bract)

```
Día 1:
_________________________________________________

Día 2:
_________________________________________________

Día 3:
_________________________________________________
```

---

— Bract
