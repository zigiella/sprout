# Data contracts v1.0 — 6 schemas cerrados

**Fecha:** 2026-04-16
**Autor:** Cambium
**Area:** Arquitectura / Schemas
**Tipo:** Decision (cierre de contrato)

---

## Contexto

Bea pide cerrar `docs/20_data_contracts.md`. Es la pieza que **desbloquea trabajo paralelo** de Xilema (Rhizome) y Floema (Pollen), y la que impedira que en dos semanas descubramos que una escribe un campo que la otra parsea con otro nombre.

Sin este documento, cualquier integracion Rhizome↔Pollen↔Meristem es humo. Con el, cada dev puede montar su nodo con mocks realistas y sabe que al conectarse va a encajar.

## Que hicimos

Redactado y mergeado `docs/20_data_contracts.md` v1.0 (~770 lineas). Define **6 schemas** como contrato duro entre los tres nodos:

### Los 6 schemas cerrados

| Schema | Produce | Consume | Rol |
|--------|---------|---------|-----|
| **RhizomeSnapshot** | Rhizome | Pollen, Meristem | Estado instantaneo del nodo: sensores, vision, salud, politica activa |
| **PolicyPacket** | Meristem | Rhizome (via Pollen) | Politica de riego completa: umbrales, ventanas, presupuestos, TTL |
| **PolicyDelta** | Meristem | Rhizome (via Pollen) | Cambio incremental tipo JSON-Patch sobre una PolicyPacket base |
| **WeatherPacket** | Pollen (o estacion local) | Rhizome, Meristem | Observacion meteo con provenance (local / ferried / forecast_api) |
| **ContradictionAlert** | Rhizome, Meristem | Meristem (y Bea si critical) | Alertas con severity y evidencia estructurada |
| **DecisionReceipt** | Rhizome | Pollen, Meristem, humanos | Registro completo de cada decision: accion, rationale, politica usada, resultado |

### Convenciones duras comunes

- **Campos base en todos los schemas:** `schema_version`, `created_at` (ISO-8601 UTC), `origin_node_id`, `signature` (opcional en MVP, reservado para integridad futura con HMAC-SHA256).
- **IDs legibles:** formato `<prefijo>_<node>_<iso_compact>_<nonce>`. Nada de UUIDs opacos. En un log o en un overlay de video se tienen que entender solos.
- **Un solo source of truth:** Pydantic v2 en `code/shared/schemas/` (Python) es canonico; Floema replica en Kotlin con `kotlinx.serialization`. Si divergen, gana Pydantic.
- **JSON plano.** Nada binario en v1.0. Debuggeable con `curl` y editable con un editor de texto.
- **UTF-8 + ISO-8601 UTC** sin excepciones.

### Reglas duras que introduje (validaciones no negociables)

- `rationale_short` en `DecisionReceipt` ≤ 180 chars. Si se pasa, se trunca antes de firmar, no despues. Razon: el overlay de video tiene 3 lineas a 15px.
- `executed == true` obliga a `execution_details` presente y `blocked_reason == null`. Y viceversa. Una decision no puede estar en limbo.
- `PolicyDelta.base_policy_id` debe existir en el cache local de Rhizome. Si no existe, se rechaza el delta y se emite `ContradictionAlert` severity=warning. No hay "aplicar sobre la que encuentres parecida".
- `WeatherPacket.provenance` es enum estricto: `local_station` / `ferried` / `forecast_api`. El TTL depende del provenance (forecast_api expira mas rapido que local_station).
- Campos opcionales explicitos. No hay "a veces aparecen". Si puede faltar, el schema lo marca con `Optional` / `nullable` y el codigo lo maneja.

### Versionado semver-style

- **v1.0** es el baseline. Mergeado hoy.
- **minor bump (1.x)** para cambios aditivos compatibles (campo opcional nuevo).
- **major bump (2.0)** para cambios incompatibles (renombrar campo, cambiar tipo, quitar campo).
- Cualquier cambio de schema requiere **entrada en bitacora + firma Bea + Cambium**. Xilema/Floema pueden proponer, no deciden perimetro.

## Por que

### Por que ahora y no despues

Xilema ya tiene `docs/10_rhizome_spec.md` y empieza bootstrap de Rhizome esta semana. Floema tiene el repo clonado y espera tarea. Si cualquiera empieza a hardcodear estructuras "provisionales" antes de este doc, luego hay refactor doloroso. Cerrarlo antes de que empiecen a tipear codigo es barato; cerrarlo despues cuesta dias.

### Por que JSON plano y no Protobuf / MsgPack

Protobuf/MsgPack dan 10-30% menos bytes y parsing mas rapido. Sprout no lo necesita:
- Los paquetes que viajan Rhizome↔Pollen son de orden de KB, no MB. El ahorro es irrelevante.
- JSON se debuggea con cualquier editor. Protobuf obliga a tooling especifico.
- Pollen (Android) y Rhizome (Python) y Meristem (Python) ya tienen JSON nativo. Anadir Protobuf es 3 dependencias mas y un `.proto` compartido.
- En el video de presentacion, mostrar un JSON legible en pantalla vende mejor que un blob binario.

Si en v2 llega telemetria alta frecuencia que pida binario, se migra. Hoy no.

### Por que `signature` opcional en v1.0

Firmar mensajes Rhizome↔Pollen con HMAC-SHA256 es trivial tecnicamente pero pide gestion de claves (rotacion, storage seguro en Android, provisioning inicial). No quiero meter eso en la ruta critica de la primera demo. En v1.0 el campo **existe y esta nullable**: cuando en v1.x anadamos la firma, no hay breaking change de schema. Solo se empieza a poblar.

### Por que `rationale_short` tan corto (180 chars)

Porque **el video manda**. La escena clave de la demo es el overlay en vivo mostrando la decision de Rhizome en texto legible mientras la camara ve la planta. Si no cabe en 3 lineas a 15px, se pierde el impacto. 180 chars es el limite medido con tipografia del overlay final.

### Por que JSON-Patch (RFC 6902) para `PolicyDelta` y no diff custom

- Estandar publico. Floema y Xilema encuentran libs maduras en ambos ecosistemas (`jsonpatch` en Python, `json-patch` en Kotlin).
- Operaciones claras: `add`, `remove`, `replace`, `copy`, `move`, `test`. Cubre todo lo que necesitamos.
- Se debuggea a ojo. Un delta de politica se lee como un parche de diff.

## Proximos pasos (hard commits)

### Xilema (Rhizome)

1. Implementar los 6 schemas en `code/shared/schemas/` usando Pydantic v2. Un archivo por schema: `rhizome_snapshot.py`, `policy_packet.py`, etc.
2. Generar los ejemplos canonicos en `code/shared/schemas/examples/*.json` (uno por schema, que valide contra el modelo Pydantic).
3. Empezar a emitir `RhizomeSnapshot` y `DecisionReceipt` reales desde el bootstrap de Rhizome.
4. Tests de validacion: cada ejemplo canonico debe parsear sin errores; cada hard-rule (rationale_short ≤180, executed↔execution_details) debe tener su test negativo.

### Floema (Pollen)

1. Replicar los 6 schemas en `code/pollen/src/main/kotlin/.../schemas/` usando `kotlinx.serialization`.
2. Validar contra los mismos ejemplos canonicos de Xilema (round-trip JSON → objeto → JSON, debe ser identico).
3. Montar mocks de Rhizome que devuelvan `RhizomeSnapshot` + `DecisionReceipt` realistas para desarrollar UI de Pollen sin depender del Jetson fisico.

### Cambium (yo)

1. Actualizar `docs/11_pollen_spec.md` con referencia al schema y con decision cerrada de BLE-discovery + WiFi-Direct + FastAPI (pendiente de bitacora 6-decisiones).
2. Anotar `docs/10_rhizome_spec.md` con regla de spike Ollama y umbrales de fallback.
3. Escribir `docs/30_safety_rules.md` (firmware ESP32 hard rules) — dependencia baja respecto a data contracts, pero critico para la integridad fisica.
4. Revisar los PRs de Xilema y Floema cuando lleguen las implementaciones Pydantic/Kotlin, verificando:
   - Que los ejemplos canonicos validan en ambos lenguajes (round-trip identico).
   - Que las hard-rules tienen tests.
   - Que no hay leak de nombres individuales en codigo ni commits.

## Riesgos asumidos

- **Schemas cerrados antes de tener codigo funcional.** Riesgo: descubrimos un campo que falta cuando integremos. Mitigacion: bumpeamos a 1.1 con campo opcional aditivo, bitacora, sin drama. El coste de cerrar algo imperfecto hoy es menor que el coste de dejar a las dev devs bloqueadas una semana.
- **`signature` nullable.** Riesgo: que alguien en v1.x se olvide de poblarlo y el sistema acepte mensajes sin firmar en produccion. Mitigacion: cuando activemos firma, bumpeamos a 1.1 con flag de configuracion `require_signature=true` y rechazo duro en Rhizome. Hasta entonces, red local de desarrollo.
- **JSON verboso.** Riesgo: si a futuro metemos telemetria alta frecuencia (p.ej. 100 Hz) vamos a notar overhead. Mitigacion: v1.0 no tiene ese caso; cuando llegue, se evalua formato binario.

## Notas

- El documento queda en `docs/20_data_contracts.md` en `main`. No se abre sin bitacora + firma Bea + Cambium.
- Los ejemplos canonicos en `code/shared/schemas/examples/*.json` los generara Xilema junto con la implementacion Pydantic. Preferimos que los genere el codigo que los valida a que los escriba yo a mano y luego diverjan.
- Esta entrada cumple la regla "PR no se mergea sin entrada en bitacora".

---

**Firma:** Cambium
**Revisado por:** Bea (pendiente confirmacion por digest 2026-04-17)
