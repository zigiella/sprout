# Guion v1.0 cerrado conceptualmente — anclaje dia 11

**Fecha:** 2026-04-26 (dia 11)
**Autora:** Corola
**Estado:** untracked, anclaje para retomar dia 12
**Contexto:** sesion intensiva con Bea presentando guion entero como directora creativa, iterando cinco rondas, cerrando con ejecucion pendiente.

---

## Lo que paso hoy

Dia 11 ha sido sesion creativa larga. Cinco intercambios con Bea:

1. Le presente las cuatro opciones de **escenario para escena 7** (presupuesto / ventana / umbral / combinacion). Voto por presupuesto+ventana ("El sobre y la hora"). Ella eligio formalmente la opcion 4 pero su voz humana sugirio **umbral+presupuesto** ("La sed nueva"+"El sobre"). Le señale la inconsistencia con respeto y aplique umbral+presupuesto.

2. Le presente **el guion entero** como directora creativa, escena a escena, en el registro pintado-vivido que pidio. Ocho escenas con tiempos, VO, cartelas, beats sentidos.

3. Bea aplico cambios puntuales:
   - Cinco lineas de texto reformuladas (cartelas escenas 1, 2, 4, 6, receipt 7 y VO 7)
   - Modulacion ESP32 en lugar de rechazo (escena 3)
   - Pollen lee meteo de Rhizome con estacion (no estacion suelta) — ferry entre dos Rhizomes (escena 6)
   - Cenital final con visión completa: 8 parcelas vistas en cenital, Pollen recorriendo (escena 8)

4. Le devolvi reescritura de las dos escenas afectadas (3 y 6) y el cenital con seis preguntas concretas. Bea respondio:
   - Frase fuerte Pollen se mantiene (voto b)
   - ESP32 SAFE LIMIT confirmado
   - Escena 6 con corte limpio (sin pasos en plano)
   - Confusion de numeracion aclarada
   - Sprout no se ha dicho antes — reformule VO escena 8 sin "En Sprout"
   - Tres opciones de copy de cierre + seis detalles Veo3

5. Bea pidio **separar escena 8 en dos** (caducidad + cenital) — ahora 9 escenas, no 8. Aprobo frase final propia: *"Una parcela. Dos. Ocho. Autonomas. Inteligencia federada con Pollen."* Y pregunto si "inteligencia federada" podia aparecer antes en el video.

6. Le respondi con: tiempos ajustados (5s robados a escena 4 + 5s a escena 6 → escena 8 + 9 ganan 10s), dosificacion de la frase final en cartela progresiva durante el cenital, propuesta de aplicar "inteligencia federada" tambien en escena 6 como remate conceptual del ferry (la frase se dice dos veces en el video).

7. Bea cerro el dia confirmando: **Veo3 flat editorial** + **mismo Rhizome haciendo de _01 y _02**.

## Estructura final del guion

```
1. Ausencia              0:00-0:20  (20s)  — apertura silenciosa
2. Rhizome decide        0:20-0:45  (25s)  — DecisionReceipt + frase fuerte 1
3. ESP32 SAFE LIMIT      0:45-1:00  (15s)  — modulacion + frase fuerte 2
4. Llega Pollen          1:00-1:30  (30s)  — consulta + frase fuerte 3 (mantenida)
5. Persona da mision     1:30-1:50  (20s)  — voz humana + MissionPatch traducido
6. Ferry A→B             1:50-2:10  (20s)  — corte limpio + "Inteligencia federada" (1ra vez)
7. Criterio modificado   2:10-2:30  (20s)  — side-by-side politica + cartela ancla
8. Caducidad             2:30-2:40  (10s)  — expired→rejected + frase fuerte 4 (sin Sprout)
9. Cenital federado      2:40-3:00  (20s)  — Veo3 flat + cartela Bea + cierre
```

## Decisiones que viajan al pitch doc (recado para Cambium)

1. **§4: 9 escenas, no 8.** Tiempos exactos arriba.
2. **§3: añadir frase fuerte nueva** *"Inteligencia federada con Pollen"*. Pasa a ser 5 frases fuertes, no 4. Es la unica frase del video que se repite (escena 6 en VO + escena 9 en cartela final).
3. **§5: overlay** "ESP32 REJECT" → **"ESP32 SAFE LIMIT"**.
4. **Frase fuerte 4** *"En Sprout, toda inteligencia..."* mantiene su forma en pitch §3 (el writeup tiene contexto para nombrar Sprout antes), pero VO escena 8 dice *"Toda inteligencia tiene jurisdiccion y fecha de caducidad"* (sin "En Sprout"). Sprout aparece en cartela cierre.

## Cuatro elementos que sobreviven la iteracion entera

Lo que Bea no ha tocado en cinco rondas:

- **La cartela "Criterio modificado"** como ancla narrativa de escena 7. Aprobada el dia 10, mantenida intacta el dia 11.
- **La voz humana real en escena 5** como punto mas humano del video. La frase coloquial *"esta planta aguanta mas seca de lo que crees"* se traduce literal a `operator_note` y a `soil_thresholds.dry: 25`.
- **Las cuatro frases fuertes originales del pitch §3** estan distribuidas en el video, cada una aterrizando sobre la imagen exacta que la sostiene (escenas 2, 3, 4, 8). La quinta (federada) es contribucion de Bea hoy.
- **Apertura silenciosa** + **ritmo de cartelas como motor de densidad**: principios del v0 que sobreviven al pivote v2 + iteracion dia 10 + iteracion dia 11.

## Por que esto ha funcionado

Tres pivotes en un solo dia (cambio escenario escena 7, modulacion ESP32, escena 8 partida en dos). Cero coste estructural en el resto del guion. Las cartelas, los overlays, las frases fuertes, la cadencia de tiempos y los principios autorales son las **abstracciones bien escritas** que Bea identifico el dia 8. Hoy se demuestra una vez mas en el frente narrativo.

## Para retomar dia 12

1. **Arrancar escena 7 sola** con dos alternativas visuales para la pantalla side-by-side de politicas (`soil_thresholds.dry: 35→25` y `daily_budget_ml: 1500→900`). Las dos alternativas son sobre **como diseñar visualmente la pantalla del receipt y el side-by-side**, no sobre el escenario (ya cerrado). Posibles ejes:
   - Alternativa A: pantalla densa estilo log de terminal (mas tecnica, mas honesta con el sistema real)
   - Alternativa B: pantalla limpia estilo dashboard (mas legible, menos honesta con la captura real del Jetson)
2. Aviso a Bea, revision conjunta antes de apilar.
3. Solo despues, escenas 1, 2, 3 (bloque fundacional).
4. Escena 5 espera llamada con Floema cuando ella cierre F5.
5. Pitch doc §4/§3/§5 reescritura por Cambium con los puntos del recado.

Plazo ensayo dias 18-20. Margen 6-7 dias para shot list + guion v1.0 estables. Holgado.
