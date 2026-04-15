# writeup/

Draft de la entrega Kaggle. Maximo **1500 palabras**.

## Archivos

- `draft.md` — version en curso del writeup (Bea + redactoras, revision Cambium)
- `cover_image/` — imagen de portada del writeup (requisito Kaggle)

## Estructura propuesta

| Seccion | Palabras | Contenido |
|---------|---------:|-----------|
| Titulo + subtitulo | 30 | "Sprout: reducing absence in remote farming" + tagline |
| Problema | 200 | Metricas de impacto + el argumento "decision tardia = agua perdida" |
| Solucion | 300 | Los tres nodos, la frase clave, por que funciona offline |
| Arquitectura | 350 | Diagrama + stack (Gemma 4 + Ollama + LiteRT + Unsloth) + reglas duras |
| Demostracion | 250 | Lo que muestra el video + 1-2 screenshots |
| Fine-tuning | 150 | Unsloth: dataset, metodo, benchmarks |
| Validacion local vs sombra | 100 | "93% acuerdo con Gemma 4 31B, produccion 100% local" |
| Impacto y escalado | 100 | Como escala, para quien, coste estimado |
| Limitaciones | 50 | Honesto, no excusas |
| Cierre | 50 | Frase final potente |

Total: ~1580 palabras, recortables a 1500.

## Criterios de exito del writeup

- Un jurado tecnico lo lee en 4 minutos y entiende la arquitectura
- Un jurado no tecnico entiende el impacto en 2 minutos
- Las 4 metricas de impacto aparecen (opener, FAO/ITU, IRRIFRAME, Banco de Espana)
- Los tracks objetivo estan nombrados (Global Resilience, Ollama, LiteRT, Unsloth)
- El patron Meristem local + sombra queda bien explicado (argumento de honestidad)

## Assets obligatorios

- Cover image (1600x900 recomendado)
- Al menos 2-3 screenshots o graficos en linea
- Diagramas de arquitectura (pueden venir de `docs/` renderizados)
