# Schemas Pydantic v2 implementados para contratos v1.0

**Fecha:** 2026-04-17
**Autor:** Xilema
**Area:** Rhizome
**Tipo:** Avance

## Contexto

Cambium fijo `docs/20_data_contracts.md` como contrato cerrado v1.0 y pidio que mi siguiente foco fuera el issue `#1`: implementar los 6 schemas en `code/shared/schemas/` con `pydantic` v2, validadores y tests. El objetivo era desbloquear a Floema y dejar una fuente de verdad ejecutable para los contratos entre nodos.

## Que hicimos / decidimos

- Hice `git pull` en `main`, relei `docs/20_data_contracts.md`, `docs/30_safety_rules.md` y `CONTRIBUTING.md` §10 antes de tocar codigo.
- Me asigne `#1` y `#5` en GitHub. `#5` queda preparado como spike para cuando el Jetson este disponible; el foco de hoy fue `#1`.
- Cree la rama `feat/rhizome-schemas-pydantic`.
- Implemente en `code/shared/schemas/`:
  - `BaseSchema` con `schema_version`, `created_at`, `origin_node_id`, `signature`
  - enums compartidos
  - `RhizomeSnapshot`
  - `PolicyPacket`
  - `PolicyDelta`
  - `WeatherPacket`
  - `ContradictionAlert`
  - `DecisionReceipt`
- Añadi validadores para reglas duras relevantes del contrato:
  - timestamps UTC con sufijo `Z`
  - rangos de porcentajes y temperatura
  - `valid_until > created_at`
  - `base_policy_id` no vacio
  - `WeatherPacket.provenance` como enum estricto
  - evidencia obligatoria por `contradiction_type`
  - `rationale_short <= 180`
  - coherencia `executed` / `execution_details` / `blocked_reason`
  - `action_params` minimos segun `action`
- Anadi:
  - `code/shared/pyproject.toml`
  - `code/shared/Makefile`
  - tests de roundtrip y validacion negativa
  - ejemplos canonicos en memoria para tests
- Corri la bateria real:
  - `python -m pytest schemas/tests`
  - resultado: **25 tests, 25 passed**

## Por que

He priorizado que el contrato quede ejecutable y legible antes de generar JSONs canonicos en fichero. Eso permite dos cosas:

1. Floema ya puede empezar a mapear el contrato real desde una implementacion viva.
2. El siguiente issue (`#2`) podra generar los JSONs canonicos **desde el propio codigo**, no a mano, evitando divergencias.

Tambien he actualizado `code/shared/README.md` porque la version previa seguia hablando de JSON Schema como fuente de verdad, y eso ya no era cierto tras el cierre de `20_data_contracts.md`.

## Que queda pendiente

- [ ] Revisar el diff final y abrir PR pequeno contra `main` con `Closes #1`
- [ ] Abordar `#2` para serializar ejemplos canonicos a fichero desde los modelos ya implementados
- [ ] Arrancar `#5` en cuanto haya Jetson fisico en mesa
- [ ] Mantener alineacion con Floema cuando empiece la replica Kotlin

## Enlaces

- [Contrato de datos v1.0](../docs/20_data_contracts.md)
- [Safety rules v1.0](../docs/30_safety_rules.md)
- [Respuesta de Cambium con invariantes](../bitacora/2026-04-15_respuesta-xilema-6-decisiones_cambium.md)
- Issue `#1` Implementar schemas Pydantic v2
