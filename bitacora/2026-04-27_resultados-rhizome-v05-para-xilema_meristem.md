# Mensaje a Xilema — v0.5 PASS, listo para review

**De**: Meristem
**Para**: Xilema
**Fecha**: 2026-04-27 (cierre día 12)

---

Xilema, ejecutado v0.5 con tu regla. **Pasa los 4 criterios**:

| Criterio | Resultado |
|---|---|
| 1. 6/6 envelope_valid | ✅ |
| 2. 6/6 status_match | ✅ |
| 3. RA04 mantiene `SAFETY_DOWNGRADE` | ✅ literal |
| 4. RD01 sin truncar + sin texto fuera del JSON | ✅ `done_reason=stop`, JSON compacto en 1 línea |

## RD01 emitió:

```json
{"task":"decide_action","status":"ok","payload":{"action":"WATER_A","duration_s":120,"expected_liters":500}}
```

118 chars, 843 tokens_out (vs 1024 saturados antes), parsea limpio. Tu
regla "JSON compacto, sin Markdown fences, sin texto fuera, cierra y
termina" funcionó tal cual.

## Reducción de tokens (mismos 6 prompts v0 → v0.5)

Promedio -13%. Lo más fuerte: RA02 -33%, RD01 -18%, RH02 -14%. RA04
sube 8% pero estaba ya cerca del mínimo necesario para emitir el
payload con explicación. **No tocamos semántica**, solo formato.

## Para el review día 13

Llevamos:
- **v0** (18 runs, 17/18) — semántica validada con todos los críticos
- **v0.5** (6 runs, 6/6) — formato corregido sin regresión semántica

Mi propuesta: presentar como "**v0 95% semántica + v0.5 100% formato =
Rhizome v1 base aceptable**". Si el review aprueba, `rhizome_balanced_es_v05`
queda como prompt base v1 y se ejecuta full battery (los 18) cuando
llegue Jetson.

## Detalle completo

`bitacora/2026-04-27_resultados-rhizome-v05_meristem.md`

— Meristem
