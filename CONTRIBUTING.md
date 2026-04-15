# Como trabajamos en Sprout

Guia para cualquier persona que entre al proyecto: desarrolladoras, redactoras, investigadoras, grabadoras.

---

## 1. Filosofia de colaboracion

Sprout es un proyecto de hackathon con deadline corto (18 mayo 2026). Cada persona trabaja en su area pero todo converge en una unica entrega: **video de 3 min + writeup de 1500 palabras + repo publico + live demo**.

Reglas blandas:
- Si no aporta a los 5 puntos de "lo que debe demostrar el video", probablemente sobra
- Si no puedes explicar algo en una frase, probablemente esta mal formulado
- Si algo es ambiguo en docs/, abre una entrada en bitacora/ y pregunta

---

## 2. Roles y zonas del repo

| Rol | Zona principal | Zonas secundarias |
|-----|---------------|-------------------|
| **Cambium** (diseno + orden) | `docs/`, `bitacora/` | todas |
| **Dev Rhizome** (Jetson) | `code/rhizome/`, `hardware/` | `docs/10_rhizome_spec.md` |
| **Dev Pollen** (Android) | `code/pollen/` | `docs/11_pollen_spec.md` |
| **Dev Meristem + Fine-tune** | `code/meristem/`, `code/finetune/` | `docs/12_meristem_spec.md` |
| **Redactoras** | `writeup/`, `video/` | `research/` |
| **Investigadoras** | `research/` | `writeup/` |
| **Grabacion / Edicion** | `video/` | `demo/` |

---

## 3. Flujo de trabajo

### 3.1 Antes de empezar algo nuevo
1. Leer la entrada mas reciente de `bitacora/`
2. Revisar el doc relevante en `docs/`
3. Si vas a cambiar algo que afecta a otros, dejar nota en `bitacora/` con fecha

### 3.2 Durante el trabajo
- Commits pequenos y frecuentes
- Mensaje de commit: `[zona] resumen corto` (ej: `[rhizome] humedad lectura via ADS1115`)
- Rama `main` solo recibe codigo que ya ha sido probado

### 3.3 Al terminar una pieza
- Update en `bitacora/` con fecha, lo que se hizo, lo que queda, decisiones tomadas
- Si hay cambio de arquitectura, actualizar el doc correspondiente en `docs/`

---

## 4. Bitacora: como escribir una entrada

Cada entrada es un archivo en `bitacora/` con nombre:

```
YYYY-MM-DD_<tema-corto>_<autor>.md
```

Ejemplos:
- `2026-04-15_kickoff_cambium.md`
- `2026-04-18_jetson-primer-arranque_ana.md`
- `2026-04-22_pollen-sync-funcionando_maria.md`

Plantilla en [bitacora/README.md](bitacora/README.md).

---

## 5. Convenciones de codigo

### Python (Rhizome, Meristem, Simulator)
- Python 3.11+
- `ruff` para lint, `black` para formato
- Type hints obligatorios en funciones publicas
- Docstrings breves en espanol; comentarios en codigo en espanol
- Tests minimos en `tests/` de cada subproyecto

### Android (Pollen)
- Kotlin
- Jetpack Compose
- Gemma 4 via Google AI Edge / LiteRT (o llama.cpp como fallback)

### Schemas JSON
- Todos los schemas en `code/shared/schemas/`
- Validacion via `pydantic` en Python, via `kotlinx.serialization` en Android

---

## 6. Convenciones de naming

### Archivos de docs
- Numerados con prefijo de dos digitos (`00_`, `01_`, `10_`, etc.)
- Kebab-case para nombres compuestos
- Ejemplo: `docs/20_data_contracts.md`

### Modelos de Gemma 4
Seguir [guia oficial de naming de Google](https://ai.google/documents/32/External_Gemma_Model_Variant_Guidelines.pdf):
- Formato: `sprout/sprout-<componente>-<modelo_base>-v<N>`
- Ejemplo: `sprout/sprout-rhizome-e2b-v1`
- Nunca poner "Gemma" en el nombre del modelo derivado (lo exige la licencia)

### Branches de git
- `main` = produccion / ultima version estable
- `feat/<zona>-<descripcion>` = features en desarrollo
- `fix/<zona>-<descripcion>` = bugfixes
- Ejemplo: `feat/rhizome-audio-sensor`

---

## 7. Secretos y credenciales

**Nunca** commitear:
- API keys (Google AI Studio, HuggingFace, etc.)
- Certificados o tokens
- Archivos `.env`

Usar siempre variables de entorno. Plantilla en `.env.example` si aplica.

Ya existe `.gitignore` con las entradas minimas. Si dudas, pregunta antes de hacer push.

---

## 8. Dudas

Abre una entrada en `bitacora/` con el tema `pregunta-<topic>` y etiqueta a Cambium. O en el canal que estemos usando el equipo.

---

## 9. Checklist antes de cada push

- [ ] El codigo corre sin errores
- [ ] No hay credenciales expuestas
- [ ] Si cambie un contrato de datos, actualice `code/shared/schemas/`
- [ ] Si cambie arquitectura, actualice `docs/`
- [ ] Hice entrada en `bitacora/` con fecha
