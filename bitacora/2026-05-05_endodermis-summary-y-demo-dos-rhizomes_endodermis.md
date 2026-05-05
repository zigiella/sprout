# Dia 20 - Summary principal y demo de dos Rhizomes

**Autora:** Endodermis
**Fecha:** 2026-05-05
**Dia de proyecto:** 20
**Rama:** `feat/endodermis/rhizome-visit-summary-demo`

## Contexto

Bea pide dos cosas:

1. convertir "¿Que ha pasado desde mi ausencia?" en el boton principal de Pollen;
2. simular dos Rhizomes para video, documentando con claridad que el segundo
   nodo es una simulacion.

Tambien aparece una pregunta de producto: Pollen muestra `SOIL A` y `SOIL B`
por cada Rhizome. Mi lectura es que esos campos son sondas dentro de cada nodo,
no dos Rhizomes.

## Decision tecnica

Amplio la fachada Rhizome -> Pollen con:

- `GET /summary/since?since=...&locale=es|en`
- `GET /explain/decision/{id}?locale=es|en`
- soporte de `--node-id`
- soporte de `--data-dir`
- script `start_demo_two_rhizomes.sh`

No introduzco llamada LLM en el summary.

## Por que no LLM todavia

El boton principal debe ser muy estable. Para MVP, la "inteligencia" es
determinista:

- cuenta riegos, bloqueos y alertas;
- calcula severidad;
- mira deposito actual;
- mira sondas A/B;
- genera highlights y recomendacion;
- localiza ES/EN.

Gemma 4 E2B puede entrar despues como redactor, pero sobre hechos ya agregados.
No debe inventar ni reinterpretar recibos.

## Demo multi-Rhizome

`rhizome_01`:

```text
http://192.168.1.60:13010/
```

`rhizome_02` simulado:

```text
http://192.168.1.60:13020/
```

Datos simulados:

```text
code/rhizome/demo_data/rhizome_02/
```

Regla narrativa: si se usa en video, se dice como simulacion host-side de
interoperabilidad multi-Rhizome, no como segundo ESP32 fisico.

## Pruebas locales

```bash
cd code/rhizome
python -m unittest tests.test_sync_facade
```

Resultado:

```text
Ran 7 tests
OK
```

Scripts:

```bash
bash -n code/rhizome/jetson/start_sync_facade.sh
bash -n code/rhizome/jetson/smoke_sync_facade.sh
bash -n code/rhizome/jetson/start_demo_two_rhizomes.sh
```

Resultado: OK.
