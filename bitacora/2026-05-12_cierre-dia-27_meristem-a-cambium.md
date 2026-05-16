# Cierre día 27 — Meristem a Cambium

**Estado**: cierro por hoy. Working tree limpio en `main`, sin stash, Meristem apagado. Lo que sigue es la foto para mañana día 28.

---

## Gracias por los merges de mañana

Ayer dejé 2 PRs abiertos (#146 codes canonical A+C, #147 HTTP endpoints). Hoy he visto que **mergeaste #147 y #150** (el de Venation UI) antes de que arrancáramos el demo. Eso desbloqueó que Floema pudiera probar inmediatamente con la app HTTP en lugar de tener que rebuild Android con WS. Gracias.

**#146 sigue abierto** — sin urgencia. Cuando tengas hueco para review, ahí está.

---

## Lo que pasó hoy (día 27)

### Demo E2E con Floema — funcionó tras 3 iteraciones

1. **Conexión**: `POST /pollen/hello` desde móvil `192.168.1.23` → 200 OK. mDNS resolvió `meristem.local` desde Android sin problemas. Chip Pollen verde en UI Meristem en <2s. ✅
2. **Cargar política (primer intento)**: `GET /policy/by-target/rhizome_01` → 200 OK, pero la app Android rompió al parsear el JSON. Reintentó 3 veces. Le pasé a Floema el **shape exacto** del `PolicyPacket` con notas sobre los sospechosos típicos (timezone en `valid_until`, `rules` como Map abierto, campos `policy_origin`/`policy_scope` añadidos día 23).
3. **Cargar política (segundo intento)**: Floema ajustó el parser, → todo OK. `POST /pollen/policies-pulled` llegó limpio.
4. **Descargar datos (primer intento)**: `POST /visit` 3 veces con **422 Unprocessable Content**. Pydantic rechazaba el bundle. Le pasé a Floema el **schema exacto del Bundle** con los 4 campos requeridos (`source_pollen_id`, `target_rhizome_id`, `active_policy_id`, `rhizome_snapshot`) + ejemplo válido `bundle_M1_clean.json`. Sospecha apuntada: camelCase vs snake_case en Kotlin.
5. **Descargar datos (segundo intento)**: funcionó. Bea me mandó screenshot mostrando card de `rhizome_01` con `CAUTION · CONSERVATIVE`, *"Ambiguous data in last visit"*, contador conservative: 1. El Evaluator detectó `EVIDENCE_LOW_CONFIDENCE` y emitió policy ajustada. Persistencia + UI sincronización funcionando. ✅

**Resultado**: ciclo Pollen ↔ Meristem cerrado en runtime. Material limpio para el video de demo.

### QUICKSTART_USUARIO_DOMESTICO.md

Bea me pidió redactar la guía de uso para el agricultor/cooperativa con portátil doméstico. Lo dejé en `code/meristem_node/QUICKSTART_USUARIO_DOMESTICO.md` (untracked, mismo patrón que la bitácora de ayer — decides tú si lo persistes en git o lo integras al writeup).

Estructura:
- Parte 1: Instalación inicial (lo hace el voluntario tech una vez).
- Parte 2: Uso diario — **un comando único**, siete pasos numerados sin asumir programación.
- Parte 3: Modo IA real (opcional, honesto sobre latencia ~1-3 min y 6 GB RAM).
- Troubleshooting de los 3 problemas vistos en demo (mDNS, UI no actualiza, puerto ocupado).
- FAQ que cubre privacidad ("¿salen mis datos?" → no), offline, terminal abierta, portátil cerrado.

Tono alineado con el storytelling "slow brain doméstico". Modo stub recomendado por defecto para uso diario; LLM real como opción "para cuando hay tiempo".

**Mi sugerencia**: si encaja, lo conviertes en `docs/40_quickstart_usuario_domestico.md` con numeración y lo enlazas desde el README. O lo integras al writeup como apéndice. Tú mandas.

### 2 detalles cosméticos vistos en el screenshot del demo

Para que Venation los considere si tiene hueco (no bloqueante):

1. **"01 · ALMANAQUE · Your plot today"** — mezcla idioma en el header (numeración en castellano, resto inglés cuando el toggle está en EN). Probable: `i18n.js` no tiene clave para el prefijo numérico.
2. **"Last sync: 2h ago"** — el bundle acaba de llegar pero la UI muestra "2 horas". Sospecha: el `received_at` que viene del bundle Pollen trae timestamp del firmware ESP32 (que puede ir desfasado del reloj real) en lugar del momento de recepción del server. Si quiere ajustarse, la UI debería usar el `received_at` del server, no del payload del bundle.

Bea decide si pasa a Venation; ninguno toca runtime.

---

## Mis PRs día 26-27

| PR | Título | Estado |
|---|---|---|
| #142 | smoke A+B + tool calling determinista E4B | **mergeado** ✅ (día 26) |
| #146 | codes canonical A+C Xilema (TANK_LOW, JETSON_HEARTBEAT_LOST, ALERT_LATCHED + equivalencia HARD_LIMIT_DOMAIN ≡ SAFETY_DOWNGRADE) | abierto, esperando review |
| #147 | endpoints HTTP fallback para Pollen (Variante D-bis) | **mergeado** ✅ (día 27, gracias) |

No abro PR para QUICKSTART por hoy — lo dejo untracked igual que la bitácora de ayer; tú decides cómo lo persistes.

---

## Pendiente para mañana día 28

### Lo que arrastro del día 26-27

1. **Ajuste B Xilema — refactor PolicyPacket campos canónicos**. Mi `PolicyPacket.rules` es un `dict[str, Any]` genérico; el contrato canónico de `docs/20_data_contracts.md` §3.4 pide campos tipados (`horizon_h`, `watering_windows`, `soil_thresholds`, `max_seconds_per_event`, `daily_budget_ml`, `priority_order`, `failsafe_defaults`). Refactor invasivo (~2h con tests). Aplazado a día 27 mañana, ahora día 28. **Antes de tocarlo conviene consensuar con Xilema el scope exacto** (¿breaking change que rompe lo que viaja a Rhizome, o adición opcional con `rules` como fallback?).

### Lo que vimos hoy y conviene cerrar

2. **PR #146** review/merge para limpiar nomenclatura antes de grabar video final (cita códigos en el writeup).
3. **2 detalles cosméticos UI** — a Venation si tiene hueco.
4. **PolicyPacket schema**: ahora que Floema parseó OK, conviene escribir un **doc breve** "shape canónico del PolicyPacket Meristem→Pollen" — 1 página, JSON ejemplo + tabla de tipos + notas (timezone, charset, campos opt nuevos). Es lo que improvisé esta tarde y le di a Bea para Floema; merece existir como referencia estable. Idea: `docs/22_policy_packet_shape.md`. ¿Lo hago yo mañana o lo coges tú al integrar el writeup?

### Material disponible para el writeup

- Smoke v6 resultados (JSON con `tool_calls_log` y respuesta natural en castellano del chat_alert).
- Screenshot del demo de hoy (Bea lo tiene).
- QUICKSTART como apéndice de "cómo se instala en una cooperativa real".
- Bitácoras día 26-27 con la cascada de iteraciones técnicas (smoke v2→v6 con tool calling, Variante D-bis HTTP fallback).

---

## Estado del repo

```
branch:    main
status:    limpio (solo bitácoras y QUICKSTART untracked + BBDD efímera + static.zip de Venation)
stash:     vacío
sync:      up to date with origin/main
procesos:  ninguno corriendo (:13000 libre)
```

**El `static.zip` en `code/meristem_node/`** no es mío — debe ser el residuo de cuando Bea descomprimió el aporte de Venation. Si te molesta en el status, bórralo (no tiene función).

---

## Coda

Día 27 con menos código nuevo que el 26, pero con la satisfacción de **ver el ciclo cerrarse con un móvil real**. Floema persistió tres iteraciones con buena disposición; cada vez que el demo rompía, el log de Meristem me dio diagnóstico claro para pasarle a Floema spec exacta. La sensación es que la arquitectura aguanta — y la documentación canónica del PolicyPacket (sugerencia 4 de arriba) cierra un riesgo silencioso que ahora viaja entre nodos sin contrato escrito.

Buen día.

— Meristem
