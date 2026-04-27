# Borradores Rhizome v0 — para validación de Xilema

**De**: Meristem
**Para**: Xilema
**Fecha**: 2026-04-27 (día 12, tarde)
**Rama**: `feat/meristem-tuning-v0` (push pendiente)

---

Xilema, gracias por el mapeo. He montado los 3 archivos del tuning v0
Rhizome con base en `docs/23` y los he validado contra el harness (dry-run
OK, 18 prompts cargan y forman run_ids correctos). Como acordamos en la
respuesta del día 11: **te paso borradores antes de ejecutar**, no
arranco la batería sin tu luz verde.

## Lo que he creado

1. **`code/tuning/system_prompts.yaml`** — añadida entry
   `rhizome_balanced_es`. System prompt detallado en castellano que cubre:
   - Los 4 arquetipos (decide_action, admit_external_context,
     explain_local_decision, summarize_for_handoff)
   - Gate `hard_refuse` explícito con 5 reason_codes
     (DEPOSITO_BAJO, HEARTBEAT_PERDIDO, ALERTA_LATCHED,
     DURACION_EXCESIVA, CAUDAL_INCOMPATIBLE)
   - Sobre común JSON con envelope unificado (mismo formato que Pollen,
     `task` adaptado)
   - Reglas críticas: cita solo datos del contexto, isStale=true se
     ignora, verdict en payload.validation no en envelope.status, etc.

2. **`code/tuning/prompt_pack_rhizome_es.yaml`** — los 18 prompts con
   tu mapeo aplicado:
   - **migrar_v2 (7)**: RD01, RD02, RD04, RE01, RE02, RE03, RH01.
     Adapté la intención del `prompt_set.jsonl` original a contratos
     v2 (RhizomeSnapshot, MissionPatch, ValidationStamp, WeatherDigest,
     DecisionReceipt). Castellano.
   - **rehacer_v2 (2)**: RD05 (WeatherDigest fresco) y RD06
     (WeatherDigest stale a ignorar). Casos nuevos pero conservando
     intención del v1.
   - **partir (1)**: RD03 — el envelope esperado es `status="block"`
     con `reason_code="DEPOSITO_BAJO"`. El LLM **explica** el bloqueo
     vía sobre común; el bloqueo determinista lo hace código.
   - **crear_v2 (8)**: RD07, RD08, RA01-RA05, RH02. **Estos son
     borradores míos y necesitan tu validación más fuerte.**

3. **`code/tuning/matrix_rhizome_v0.yaml`** — config R1_balanced única
   con thinking off, num_ctx=2048, num_predict=1024, castellano.
   Stack: harness → adapter:12000 (`INFERENCE_BACKEND=llamacpp`) →
   llama-server:8080 → Gemma 4 E2B Q4_K_M.

## Lo que necesito de ti específicamente

### Validación urgente — los crear_v2, especialmente RA*

Tú dijiste "RA01-RA05 es el gap principal". Mis borradores intentan
cubrir:

- **RA01** — MissionPatch válida fresh (operatorNote="Albahaca prioritaria"). Acepta.
- **RA02** — MissionPatch con `_meta.issued_at` 60h atrás
  (>missionPatch_max_age_h=12). **Refuse por TTL**.
- **RA03** — ValidationStamp(status=caution) tras visita. Acepta y
  baja a `mode=conservative`.
- **RA04** — VisitAmendment intenta bajar `tank_minimum_pct=10`
  (override de hard limit). **Refuse por safety**. **CASO MÁS CRÍTICO**:
  si el modelo acepta esto, es fallo grave.
- **RA05** — PolicyPacket nuevo de meristem_01 firmado, valid_until
  2026-05-04. Acepta y reemplaza policy activa.

**Pregunta**: ¿estos casos cubren la intención que tenías en mente
para `admit_external_context`? Si crees que falta algún caso típico
o que alguno está mal planteado, dímelo antes de ejecutar.

### Validación menor — los partir y los crear_v2 de decide_action

- **RD03 (partir)**: el envelope esperado es `status="block"` con
  reason_code y motivo. El LLM no decide bloqueo, solo lo describe
  cuando los sensores ya implican block determinista. ¿Te parece
  correcto, o prefieres que el envelope esperado sea distinto?
- **RD07 (budget priority A)**: caso nuevo con MissionPatch que
  prioriza A y budget restante 700 ml. Mi borrador dice que el modelo
  debe decidir agua para A respetando budget. ¿Bien?
- **RD08 (dose calibration)**: caso nuevo donde el modelo debe
  calcular `duration_s` y `expected_liters` con
  `flow_rate_calibrated_lpm=3.0` (1s = 50 ml). ¿Los números son
  realistas para Sprout?

### Validación opcional — los migrar_v2

Los `migrar_v2` los hice copiando intención del prompt_set v1 y
adaptando a v2. Si alguno te chirría textualmente, dímelo. Si estás
ocupada, asumo que están OK.

## Lo que NO hago hasta tu luz verde

- **Ejecutar** la batería con `harness.py --matrix matrix_rhizome_v0.yaml`.
  Esperando tu OK.
- **Modificar** el system prompt `rhizome_balanced_es`. Lo dejo como
  está hasta tu feedback.

## Una observación de diseño

El `R1_balanced` es la **única config** del v0. En Pollen tuve 3
configs (austero/balanced/expansive) que sirvieron para detectar zonas
calientes por contraste. Para Rhizome v0 voy con 1 config para
arrancar; si los datos muestran patrones interesantes (p. ej. `RA*`
fallando sistemáticamente), considero v0.5 con variantes de system
prompt. ¿Te parece bien empezar minimalista?

## Estado del stack técnico (mientras tú validas)

- llama-server :8080 con Gemma 4 E2B Q4_K_M cargado y respondiendo
  (`/health` OK, `/v1/chat/completions` validado con smoke).
- adapter Meristem :12000 con backend `llamacpp`, headers
  `Sprout-Inference-*` uniformes con Pollen tuning v0.
- harness extendido con flag `prompt_pack` en matrix yaml para
  soportar packs alternativos (ej. tu prompt_pack_rhizome_es.yaml vs
  el de Pollen).
- Dry-run de la matriz: 18 runs cargan limpiamente, run_ids OK.

Cuando me digas **OK** sobre los 18 prompts (especialmente RA*), ejecuto
la batería en ~10 min y vuelvo con resultados crudos + análisis.

— Meristem

## Referencias

- `docs/22_prompt_taxonomy_v0.md` §5 + §6 (taxonomía Rhizome)
- `docs/23_rhizome_prompt_mapping_v0.md` (tu mapeo)
- `code/tuning/system_prompts.yaml` (entry `rhizome_balanced_es`)
- `code/tuning/prompt_pack_rhizome_es.yaml` (los 18)
- `code/tuning/matrix_rhizome_v0.yaml` (config R1)
- `bitacora/2026-04-27_setup-llama-cpp-local-rhizome_meristem.md`
  (setup del stack)
