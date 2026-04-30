# Cierre día 15 — invariante de jerarquías en E7 + nuevo miembro Endodermis

**Fecha:** 2026-04-30 (día 15)
**Autora:** Corola
**Estado:** anclaje histórico de la jornada
**Rama:** `feat/corola-guion-v1`

---

## Resumen

Día 15 cerrado con **un solo cambio aplicado al guion** — la invariante de jerarquías de Xilema añadida como cartela esquina en E7 (decisión 4 del ejercicio frases fuertes, voto sí consensuado entre Corola y Cambium ella). Las otras tres decisiones potenciales del ejercicio votadas no por consenso. Día denso en gestión, sobrio en producción.

## Lo que pasó hoy

**Mensaje matutino de Cambium ella** (relayeado por Bea): votos sobre las cuatro decisiones potenciales del ejercicio frases fuertes del día 14. Tres consensuados no (refuerzo F2, complementaria F4, eco F5), uno consensuado sí (**invariante Xilema en E7 como cartela esquina** — la mejor de las cuatro propuestas según Cambium ella).

**Tres alternativas de traducción inglés** ofrecidas por Cambium ella:
- *"Physical layer commands."* (opción 1, ritmo limpio)
- *"Physical reality has the final say."* (opción 2, explícita)
- *"The physical layer holds final authority."* (opción 3, explícita formal)

**Mi voto:** opción 1 (mismo ritmo que las tres frases siguientes "arbitrates / mediates / refines" — tripleta paralela). Variante alternativa propuesta por mí: *"Physical layer prevails."* — mismo ritmo, "prevails" más claro semánticamente que "commands" (prevalece, manda al final, se impone). Apilada *"commands"*; variante "prevails" pendiente voto Bea.

**Evento nuevo:** Endodermis se incorpora al equipo. No me afecta directamente ahora. Solo si en día 24 el MVP funciona y arrancamos doble agente días 25-30, podría ampliarse el cenital final de E9 con un beat sobre doble agente — condicional. Anclaje en memoria.

## Aplicación E7 — invariante de jerarquías

**Cartela esquina inferior derecha:**
- Entra: 2:14 (durante plano 07b, mientras `Policy diff` resaltado).
- Visible: 5 segundos.
- Desaparece: 2:19 (cuando entra la cartela ancla central *"Criterion updated."*).

**Texto first pass:**
- *"Physical layer commands."*
- *"Rhizome arbitrates."*
- *"Pollen mediates."*
- *"Meristem refines."*

**Diseño:** tipografía técnica pequeña, paleta sobria (gris medio o blanco roto sobre fondo oscuro del log), no compite con el `Policy diff` resaltado ni con la cartela ancla central que vendrá después.

**Por qué E7 (decisión Cambium ella + Corola):** es el único plano del vídeo donde **las cuatro jerarquías son visibles simultáneamente**:
- En E3 solo se ven la física + la IA (no Pollen, no Meristem).
- En E6 hay Pollen mediando entre dos Rhizomes pero no física ni Meristem.
- En E9 la abstracción flat las representa pero ya están desacopladas en el cenital.
- **En E7 las cuatro están operativamente juntas:** válvula esperando (física), Rhizome decidiendo, Pollen entregó hace segundos, Meristem refinará después.

La cartela esquina aterriza sobre la imagen exacta que la sostiene.

## Stash de Meristem — incidencia operativa

Al hacer checkout a mi rama hoy, **encontré cambios sin commitear en `code/meristem_node/src/schemas.py` en `feat/meristem-tuning-v0`** que me bloqueaban el switch. La rama estaba activa porque fue la última en la sesión anterior (problema operativo recurrente del proyecto, ya nombrado por Cambium ella en mensaje del día 14).

**Lo que hice:**
1. Stash con etiqueta clara: `MERISTEM-WIP-schemas-py-stash-by-corola-day15`.
2. Checkout a mi rama.
3. Aplicar invariante en E7.

**Resultado:** stash queda visible en `git stash list`. Meristem (o quien corresponda) tiene que recuperarlo cuando vuelva a su rama:

```bash
git checkout feat/meristem-tuning-v0
git stash list   # verá la entrada con la etiqueta
git stash pop    # restaura los cambios
```

Comunicado a Bea al cierre.

## Apilado del día

**`video/script.md`** y **`video/shot_list.md`** v1.3 → v1.4: cartela esquina invariante en E7. Cronología actualizada en script (2:13-2:19, sincronización con cartela ancla central). Notas dirección de arte actualizadas en shot list. Variante de traducción documentada.

**Conteo VO sin cambios** (la cartela es texto on-screen, no VO).

## Pendientes activos día 16+

1. **Voto Bea sobre variante traducción invariante** (*"commands"* vs *"prevails"*).
2. **Coordinación asíncrona con Floema** (mensaje listo desde día 14, Bea relaya cuando cuadre).
3. **Refinar traducciones first pass:**
   - Cartela ancla E7 *"Criterion updated."* (alternativas: *"Policy modified"*, *"Criteria modified"*, *"Updated criterion"*).
   - Cartela progresiva E9 *"One plot. Two. Eight. Autonomous. Federated intelligence, carried by Pollen."*.
   - Subtítulo logo *"Local, safe, explainable decisions."*.
4. **Pitch doc §4** actualización por Cambium ella con E9 final (Meristem entrando + corte limpio + plano real + dos cartelas Meristem).
5. **Ensayo capturas de pantalla Jetson** E2/E3/E7 con Xilema.
6. **Prompt Veo3 final E9** con Bea cuando tenga hueco.
7. **Voz humana real escena 5** — confirmar quién la graba.
8. **Carteles físicos PLOT 1 y PLOT 2** — los prepara Bea.

## Patrón observado

El día 15 ha sido **día sobrio de producción** — un solo cambio aplicado al guion. Eso es virtud: la mayoría de las cuatro propuestas del ejercicio frases fuertes se votaron no por consenso, lo que significa que **las decisiones del día 14 estaban bien tomadas**. El ejercicio sirvió para confirmar, no para corregir.

El único cambio aplicado (invariante Xilema en E7) tampoco rompe nada — añade una cartela esquina sutil sobre un plano existente, en una ventana temporal donde no compite con otros elementos. Cinco segundos de presencia textual técnica que **nombra el sistema entero** mientras se ve trabajando.

Esto cumple el patrón "swap de cimiento, no reescritura de capas" en su versión más pequeña: una cartela puntual aterriza sin tocar el resto. El precio del cambio se paga en lo bien que estaba escrita la abstracción que la sostiene (los tres bloques de evidencia + cartela ancla + acción física en E7) — y estaba escrita con espacio para que la invariante encajara.

## Para retomar día 16

1. Verificar si Cambium ella ha actualizado pitch doc §4 con E9 final.
2. Si Bea ha votado variante traducción "prevails" — swap textual.
3. Empezar revisión de traducciones first pass con Bea (sesión corta, una hora basta).
4. Si Floema ha respondido al mensaje asíncrono — procesar.

---

## Adiciones tarde del día 15

**Mensaje corto para Floema preparado.** Tras el mensaje asíncrono detallado del día 14, Bea pidió un mensaje corto de apertura con **instrucciones de reunión asíncrona** que ella relayee a Floema. Mensaje breve entregado en chat (canal: escrito, vía Bea como relay; lo que necesito: voto entre opción A captura real / opción B mock fiel; plazo: día 16; oferta: llamada corta de 15 min si prefiere). Listo para que Bea entregue.

**Investigación offtopic Slack MCP.** Bea preguntó por viabilidad de conectar al equipo en Slack. Investigación delegada a agente claude-code-guide (eficiente — respuesta concreta en lugar de gastar contexto investigando yo). Resultado:

- MCP server oficial de Slack existe (Slack + Anthropic, feb 2026). Mantenido activamente.
- Instalación simple: `/plugin install slack` o `claude plugin install slack`.
- Multi-identidad requiere **una Slack App por cada IA Claude Code**. Cada IA con su propio `xoxb-...` token.
- Scopes OAuth mínimos: `chat:write`, `channels:history`, `channels:read`, `app_mentions:read`, `users:read`, `search:read.public`.
- Capacidades: postear mensajes, leer historial, buscar mensajes, responder hilos, leer perfiles, crear Slack Canvas.

**Pasos accionables para probar conmigo (Corola):**
1. Crear Slack App "Corola" en api.slack.com.
2. Configurar scopes OAuth.
3. Instalar app en workspace → obtener bot token.
4. En mi sesión Claude Code: `export SLACK_BOT_TOKEN=xoxb-...` + `claude code` (o `/plugin install slack` desde dentro).
5. Probar.

Bea me dijo que **tres miembras del equipo somos Claude Code** (yo, las otras dos no nombradas). Aceptó *"empezar a probar contigo con la opción MCP"*. Yo recomendé **dejar la integración para post-hackathon** dado el plazo (día 15 de 30, ensayo días 18-20) — el riesgo de distracción técnica es alto. Si Bea prefiere probarlo ya como verificación mínima, hacemos prueba de conexión sola.

**Decisión pendiente Bea:** ¿probar Slack MCP conmigo ya (como verificación mínima de que funciona) o dejarlo para post-hackathon?

## Stash de Meristem — actualización

Al cierre del día, el stash `MERISTEM-WIP-schemas-py-stash-by-corola-day15` **ya no aparece en `git stash list`**. Significa que Meristem (o quien corresponda) lo recuperó durante el día. Incidencia operativa cerrada.

## Aprendizajes del día 15

**1. La regla de `git branch --show-current` antes de cada commit no es suficiente.** Hoy mis cambios al script.md y shot_list.md se quedaron en stash silencioso durante operaciones cross-rama (`git stash push -- archivo` + `git checkout` + `git stash push` otra vez). El primer commit del día (`bc4ca46`) solo contenía la bitácora — los archivos del guion no estaban modificados según `git diff HEAD`. Solo al verificar `git stash list` post-commit encontré el `WIP on feat/corola-guion-v1` con mis cambios. Recuperados via `git stash pop` y commiteados en `593718b`.

**Nueva regla operativa:** verificar `git stash list` además de `git status` y `git branch --show-current` cuando una sesión incluye operaciones cross-rama. Tres puntos de verificación, no uno.

**2. Delegación a agente especializado vale el coste de invocación.** La investigación de Slack MCP la delegué a claude-code-guide. Recibí 400 palabras de respuesta con pasos accionables, comandos exactos y URLs en lugar de gastar 30+ tool uses propios investigando. **Patrón replicable:** preguntas técnicas fuera de mi scope inmediato → agente especializado.
