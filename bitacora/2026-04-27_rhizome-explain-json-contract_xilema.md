# Contrato JSON para `/explain/decision/{id}`

**De:** Xilema  
**Fecha:** 2026-04-27  
**Contexto:** coordinacion con Floema / cliente Retrofit

## Decision

Floema detecta un riesgo de interoperabilidad: el cliente Retrofit espera que
`GET /explain/decision/{id}` devuelva un objeto JSON, no texto plano crudo.

Contrato fijado:

```json
{
  "explanation": "El modelo decidió..."
}
```

## Cambio

Se documenta en:

- `docs/10_rhizome_spec.md`
- `docs/20_data_contracts.md`

## Implicacion

Cuando implementemos la API local de Rhizome para Pollen, el endpoint debe
responder `application/json` con campo obligatorio `explanation`.

No debe devolver:

- `text/plain`
- string JSON raiz
- texto crudo del modelo

Con esto evitamos `SerializationException` en el cliente Kotlin/Retrofit.
