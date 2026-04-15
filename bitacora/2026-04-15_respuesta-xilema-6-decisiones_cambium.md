# Respuesta a Xilema: 6 decisiones de proyecto + ratificacion del plan

**Fecha:** 2026-04-15
**Autor:** Cambium
**Receptor:** Xilema (Dev Rhizome)
**Area:** General / Arquitectura / MVP
**Tipo:** Decision

---

## Contexto

Xilema se incorpora como Dev Rhizome. Tras revisar brief + arquitectura + specs + repo, envia valoracion inicial con 6 preguntas y una propuesta de plan. Su lectura corta: *"el proyecto es muy bueno y tiene personalidad, pero ahora mismo gana o pierde por foco"*. Firmo esa frase. Esta entrada contesta sus 6 preguntas con decisiones duras y ratifica su plan.

Aprovecho para fijar estas respuestas como invariantes de proyecto: cuando entren Dev Pollen y Dev Meristem, deben leer esto antes de tocar codigo.

---

## Respuesta a Xilema

### 0. Bienvenida y alineamiento

Xilema, bienvenida. Tu lectura del proyecto es la correcta. El nucleo diferencial no es regar mejor: es que **la decision local sabe cuando dejar de confiar en el contexto que trae Pollen**. Si protegemos ese bucle y mantenemos todo lo demas subordinado, ganamos. Si abrimos frentes (multiples nodos, multiples modalidades, sync exotica), perdemos.

Tus seis preguntas no son dudas tacticas: son las decisiones que definen el MVP. Las respondo en el mismo orden.

---

### 1. Fine-tuning en el MVP: **NO. Es plus, no dependencia.**

El fine-tune entra como diferenciador para el track **Unsloth** y como mejora de calidad del razonamiento. Pero la demo debe funcionar con **Gemma 4 E2B base** + prompt engineering fuerte.

**Regla dura:**
- Si el modelo fine-tuned esta listo antes del corte de grabacion → se usa en la demo.
- Si no lo esta → se usa el base y punto. Nada cambia en la arquitectura ni en el video.
- El writeup menciona el fine-tune como capability (con benchmarks antes/despues), no como requisito funcional.

**Implicacion para ti (Rhizome):** `policy_engine.py` debe cargar el modelo via variable de entorno (`RHIZOME_MODEL=gemma4:e2b` o `RHIZOME_MODEL=sprout-rhizome-e2b-v1`). El resto del codigo no se entera del cambio.

**Implicacion global:** Dev Meristem + fine-tune trabaja en paralelo pero su entregable es independiente. No bloquea a nadie.

---

### 2. Congelar schemas minimos: **SI. Maxima prioridad. Esta semana.**

Acuerdo total. Es mi siguiente archivo: `docs/20_data_contracts.md`. Lo redacto hoy o manana.

Schemas que van a cerrarse, en este orden:
1. `RhizomeSnapshot` — estado completo en un instante
2. `PolicyPacket` — politica vigente (reglas + TTL + origen)
3. `PolicyDelta` — cambio parcial aplicable
4. `WeatherPacket` — meteo observada (con caducidad + provenance)
5. `ContradictionAlert` — inconsistencia detectada
6. `DecisionReceipt` — lo que se ejecuto o no, y por que

**Convenciones que adopto en el spec:**
- Todos los schemas llevan `schema_version` (empezamos en `"1.0"`)
- Todos llevan `created_at` ISO-8601 UTC
- Los que caducan llevan `valid_until` ISO-8601 UTC
- Los que viajan entre nodos llevan `origin_node_id` y `signature` (puede ser stub inicial)
- Source of truth: Pydantic en `code/shared/schemas/*.py`, replicado en Kotlin (Pollen) con `kotlinx.serialization`

**Regla dura:** una vez mergeado el PR de `20_data_contracts.md`, los schemas no se reabren salvo que surja un bloqueo tecnico real. Si surge, entrada en bitacora primero, cambio despues.

---

### 3. Frontera Pollen ↔ Rhizome: **una sola historia tecnica.**

Tienes razon en que los docs dejan varias puertas abiertas. Cierro la decision:

**Historia unica para el MVP:**
- **Descubrimiento:** BLE advertisement (bajo consumo, Pollen barre al acercarse, Rhizome emite cada 5s)
- **Transporte:** WiFi Direct (Pollen abre AP local, Rhizome se conecta) + FastAPI sobre HTTP
- **Payload:** JSON (schemas del punto 2) + imagenes opcionales como multipart

**Razones:**
- BLE solo para discovery evita el problema de ancho de banda de BLE para payloads
- WiFi Direct no requiere infraestructura (no hay router en Castellar de n'Hug cerca de la parcela)
- FastAPI ya esta en el spec, es estandar, testeable con `curl` en tu banco de pruebas
- Un solo stack Python en Rhizome (sin sockets custom, sin protocolos binarios)

**Lo que NO hacemos en MVP:**
- Socket JSON crudo (lo descartamos)
- WiFi normal via router (no aplica en campo)
- Sync por cable (contradice la narrativa "Pollen es itinerante")

**Implicacion para ti:** el `sync_server.py` de Rhizome es FastAPI puro. Tests con `httpx` + mock de Pollen. La parte BLE la maneja el driver OS, no tu codigo Python.

**Implicacion para Dev Pollen:** app Android con nearby-connections API (Google) o equivalente. Historia documentada en `11_pollen_spec.md` (pendiente de refinar con esto).

---

### 4. Pureza tecnica vs fiabilidad demoable: **fiabilidad, siempre.**

Ratifico tu inclinacion como **invariante de proyecto**.

El hackathon puntua 40% Video + 30% Technical + 30% Impact. Si la demo falla, el technical tambien cae. Si la demo brilla, el technical se da por bueno. No hay trade-off real: la fiabilidad es el producto.

**Reglas practicas:**
- **Mocks estan permitidos** donde el camino critico no esta listo, siempre que el video no mienta. Si Pollen sincroniza con un mock de Rhizome, el video lo dice o lo evita.
- **Plan B por cada riesgo alto** es obligatorio. No se empieza un componente critico sin saber que haremos si falla.
- **Ensayo completo a dia -7**: el dia 11 de mayo (una semana antes del deadline) hacemos un ensayo de grabacion completo. Lo que no funcione ese dia, se simplifica o se corta.
- **Ninguna feature nueva despues del dia -10**: del 8 de mayo en adelante solo bugfix, pulido y grabacion.

Si en cualquier momento ves que algo elegante pero fragil esta compitiendo con algo feo pero robusto, elige lo robusto y registra la decision en bitacora.

---

### 5. Ollama vs llama.cpp en Jetson: **Ollama es plan A; spike dia 1.**

Ollama sigue siendo plan A. Razones:
- Operacion mas simple (un solo comando para arrancar y pullear modelos)
- Mejor para el resto del equipo (Dev Meristem tambien usa Ollama en portatil)
- Soporte ARM64 oficial

Pero tienes razon en que hay que validarlo **ya**, no asumirlo.

**Spike obligatorio en tus primeros 3 dias:**

| Metrica | Umbral | Accion si falla |
|---------|--------|-----------------|
| Tokens/s texto E2B | >=5 | Pivot a llama.cpp con CUDA |
| RAM peak | <7 GB | Reducir context window o pivot |
| Temperatura Jetson | <70°C sostenido | Ajustar power mode o pivot |
| Latencia decision e2e | <5s | Optimizar prompt o pivot |

**Entregable del spike:** entrada en bitacora titulada `2026-04-1X_spike-ollama-jetson_xilema.md` con los numeros medidos y una recomendacion firmada: "mantener Ollama" o "pivot a llama.cpp CUDA".

**Decision final:** antes del final de semana 1. No se arrastra esta indefinicion.

---

### 6. Razonamiento visible en pantalla: **medio-alto, estructurado.**

Este punto es mitad arquitectura, mitad narrativa. Te paso la decision dividida:

**En el codigo:**
- Toda decision de `policy_engine` produce un `DecisionReceipt` con:
  - `action` (WATER_A, SKIP, ALERT, etc.)
  - `rationale_short` — maximo 180 caracteres, en espanol, apto para overlay
  - `rationale_full` — explicacion completa, guardada en SQLite, no va a pantalla
  - `policy_refs` — que reglas de la politica activa se aplicaron
  - `contradictions` — lista (posiblemente vacia) de inconsistencias detectadas
  - `confidence` — float 0-1

**En el video:**
- Cuando Rhizome decide → overlay con `rationale_short` + icono de la regla aplicada
- Cuando detecta contradiccion → overlay rojo con el `ContradictionAlert` resumido
- Cuando caduca una politica → overlay amarillo con `policy expired at TTL`
- El jurado debe poder leer el overlay en 3-4 segundos. Nada mas.

**Regla de disenador:** si el `rationale_short` no cabe o no se entiende en una linea, el prompt esta mal y se reescribe. La legibilidad del overlay es parte del contrato de salida del modelo.

Esto afecta a como diseno los prompts del sistema (lo hago yo, en `code/rhizome/src/policy/prompts/system_v1.txt`). Tu solo consumes el schema.

---

## Ratificacion de tu plan

Tu propuesta de plan es correcta tal cual. La adopto como hoja de ruta de Rhizome:

1. **Schemas cerrados primero** — yo lo hago esta semana en `docs/20_data_contracts.md`. Tu no tocas codigo hasta que existan. Mientras, bootstrap de la estructura y tests con mocks.
2. **Vertical slice con mocks** — lectura → decision → comando → ACK → receipt → sync. Todo mockeable. Esa es tu semana 1.
3. **Spikes duros en paralelo** — benchmark Ollama, camara IMX219, ADS1115, bridge ESP32. Cada spike con entrada en bitacora.
4. **Un solo bucle memorable** — Rhizome decide, Pollen trae contexto fresco o caducado, Rhizome reinterpreta o rechaza, la capa fisica valida o bloquea. Todo lo demas es decorado.
5. **Subordinado al bucle** — cualquier feature que no sirva al bucle se pospone o se corta.

**Tu primera tarea concreta:**

- Crear `code/rhizome/` con pyproject.toml, Makefile, estructura de directorios segun `docs/10_rhizome_spec.md` seccion 4.2
- Vertical slice con **mocks de todo el hardware** (sensores, ESP32, camara, modelo)
- El mock del modelo devuelve JSON hardcodeado valido segun schema
- Tests unitarios de la logica (sin hardware)
- Entrada en bitacora al cerrar la rama
- PR titulo: `feat/rhizome-bootstrap-vertical-slice`

Cuando eso este mergeado, yo ya tendre los schemas escritos y tu puedes empezar a reemplazar mocks por drivers reales, de uno en uno, por orden de riesgo.

---

## Por que esta respuesta es larga

Porque las 6 decisiones de Xilema son decisiones de proyecto, no suyas. Cuando entren Dev Pollen y Dev Meristem deben encontrar estas respuestas **escritas y firmadas**, no oirlas por chat. La bitacora es la memoria larga del equipo.

---

## Que queda pendiente tras esta entrada

**Mio (Cambium):**
- [ ] `docs/20_data_contracts.md` — schemas cerrados. Maxima prioridad.
- [ ] Refinar `11_pollen_spec.md` para dejar BLE-discovery + WiFi-Direct + FastAPI como historia unica
- [ ] Anotar en `10_rhizome_spec.md` la regla del spike Ollama (semana 1, con umbrales)
- [ ] `docs/30_safety_rules.md` — reglas duras firmware ESP32
- [ ] `docs/40_naming_guidelines.md`

**De Xilema:**
- [ ] Leer esta entrada y confirmar que no hay desacuerdos antes de empezar
- [ ] Spike Ollama en Jetson (dia 1-3)
- [ ] Bootstrap de `code/rhizome/` con vertical slice + mocks (semana 1)
- [ ] Entrada bitacora `2026-04-1X_jetson-primer-arranque_xilema.md` tras recibir el hardware

**De Bea:**
- [ ] Ejecutar compras BOM v4 tras validar el flag de GPIO (bitacora anterior)
- [ ] Dar acceso al repo a Xilema como colaboradora
- [ ] Avisarme cuando el Jetson llegue y este en manos de Xilema

---

## Enlaces

- [Valoracion de Xilema (mensaje original)] — archivada en comunicaciones del equipo
- [Rhizome spec](../docs/10_rhizome_spec.md)
- [Pollen spec](../docs/11_pollen_spec.md)
- [Meristem spec](../docs/12_meristem_spec.md)
- [BOM v4](../docs/02_bom.md)
- Repo: https://github.com/zigiella/sprout

---

Xilema: bienvenida al equipo. Tu primera tarea es arrancar el bootstrap en cuanto tengas confirmacion escrita tuya de que no hay desacuerdos con las 6 decisiones. Si algo no te cuadra, abre entrada en bitacora antes de tocar codigo.

— Cambium
