# Cierre día 26 — Meristem a Cambium

**Estado**: cierro por hoy. Working tree limpio en `main`, sin stash, todo committed y pusheado. Lo que sigue es la foto para que mañana arranques con contexto.

---

## PRs Meristem del día 26

| PR | Título corto | Estado |
|---|---|---|
| #142 | día 26 — smoke A+B + tool calling determinista E4B | **mergeado** ✅ |
| #146 | día 26 — ajustes A+C Xilema: códigos canónicos + equivalencia HARD_LIMIT_DOMAIN/SAFETY_DOWNGRADE | abierto, listo para review |
| #147 | día 26 — endpoints HTTP fallback para Pollen (Variante D-bis) | abierto, listo para review |

**Recomendación de orden de merge mañana** (antes del demo, idealmente):

1. Merge #146 primero (cosmético/semántico — no toca runtime, bajo riesgo).
2. Merge #147 después (necesario para que Floema pueda probar — añade endpoints `/pollen/*` HTTP equivalentes al WS).

Si quieres review yo mismo de cualquiera, los dejo claros y atómicos.

---

## Lo que pasó hoy (resumen comprimido)

**Mañana día 26**: smoke A+B en runtime con LLM real (E4B). Identifiqué que el modelo emite tool calls en formatos no estructurados (`<|tool_call>call: name(args)` y `<tool_call>{...}</tool_call>`). Implementé en cascada:

- **Plan A** — parser tolerante en `inference.py` que rescata esos formatos y los mapea al estructurado Ollama-compatible.
- **Plan B** — few-shot ejemplo en ambos system prompts (`prompts.py`) para forzar el formato canónico.
- **Fix `type: function`** — descubrimiento en smoke v5 (llama-server 500 *"Missing tool call type"*) que cierra el bucle.

Resultado smoke v6: **chat_alert invoca `get_recent_history` en runtime y cita los datos reales del stub en la respuesta natural en castellano**. Asterisco día 24 cerrado para el caso conversacional. PR #142 mergeado.

**Tarde**: ajustes pedidos por Xilema. Acepté A (códigos canónicos `TANK_LOW` / `JETSON_HEARTBEAT_LOST` / `ALERT_LATCHED`) y C (documentar equivalencia jurisdiccional `HARD_LIMIT_DOMAIN ≡ SAFETY_DOWNGRADE`). Aplazado B (refactor `PolicyPacket` con campos canónicos de `docs/20_data_contracts.md` §3.4 — invasivo, requiere consensuar con Xilema antes de tocar). PR #146.

**Noche**: Bea quería ensayar E2E con la app Pollen. Floema reveló que su cliente Android usa POST HTTP, no WebSocket. En vez de obligar a rebuild Android, añadí endpoints HTTP equivalentes a los 5 eventos WS (Variante D-bis). Coexisten con el WS de PR #81 sin tocarlo. PR #147.

---

## Lo que queda para mañana

### Bloqueante para demo

1. **Mergear #147** antes de que Floema arranque su app. Si no, los POST `/pollen/hello` devuelven 404.
2. **Floema** confirma que su cliente HTTP usa la spec exacta (en el body del PR #147 está la spec lista para copiar).
3. **Seed BBDD** antes de arrancar Meristem para que el primer "cargar política" devuelva algo visible:
   ```bash
   cd code/meristem_node
   python scripts/seed_demo_policy.py
   ```
   (Script entra con #147.)

### Pendiente sin urgencia

4. **Ajuste B Xilema** — PolicyPacket campos canónicos `horizon_h` / `watering_windows` / `soil_thresholds` / `max_seconds_per_event` / `daily_budget_ml` / `priority_order` / `failsafe_defaults` según docs/20_data_contracts.md §3.4. Mi schema actual usa `rules: dict[str, Any]` genérico — laxo, no respeta el contrato. Refactor invasivo (~2h con tests). PR separado `feat/meristem-d27-policypacket-canonical` cuando Xilema dé scope exacto.

5. **Cosa estética** — pasarle a Venation los 2 archivos editables (`static/styles.css` + `static/index.html`) con sus constraints. Ya documenté qué IDs/clases preservar en mi respuesta a Bea de esta tarde. Si quieres, te mando el resumen formal.

### Riesgos abiertos identificables

- **mDNS desde móvil Android**: si Floema en su app no resuelve `meristem.local`, fallback a IP directa (hoy `192.168.1.36`, pero puede cambiar si Bea mueve PC). Recomendación: que la app permita escribir IP manualmente como fallback.
- **Latencia con LLM real** (~80-140s por visit con E4B): si Bea quiere grabar con LLM real, ensayo aparte. El demo del día con stub es instantáneo y queda igual de bonito visualmente — la inteligencia se demuestra en el take separado del `/chat`.
- **BBDD persistente** (`meristem_node.db`): la dejo con la policy seedeada de hoy. Si mañana se reseedea, no hay error (INSERT OR REPLACE). Si se quiere arrancar limpio, borrarla antes.

---

## Estado del repo

```
branch:  main
status:  clean (solo bitácoras de otras células untracked + meristem_node.db efímera)
stash:   vacío
sync:    up to date with origin/main
```

**Procesos**: ningún Meristem corriendo en background. Puerto :13000 libre.

**Tu working tree** debe estar igual de limpio. Si ves algo modificado de `src/main.py` o `src/ws_manager.py` que **no** es tuyo, es porque PR #147 está en una rama y main no la tiene aún. Confirma con `git log main..origin/main --oneline` (debería estar vacío).

---

## Bonita coda del día

Cuatro PRs en un día (uno mergeado, dos abiertos, uno extra de A+B aplicado y mergeado por la mañana ya): **smoke E2E con LLM real, tool calling determinista, codes canonical Xilema, HTTP fallback para Floema**. El asterisco día 24 que arrastrábamos quedó zanjado. El demo de mañana tiene material concreto en cinco zonas de UI + flow Pollen→Meristem real, no maqueta.

Buen día.

— Meristem
