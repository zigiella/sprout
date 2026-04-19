# simulator/

Capa de rehearsal e integracion de Sprout. Aqui viven los harnesses que no son
codigo productivo de un nodo, pero que nos dejan ensayar rutas, latencias y
flujo E2E antes de tener todo el hardware real montado.

## Hoy

### 1. Harness E2E cross-node

`src/cross_node_e2e.py` encadena:

- `Rhizome` mock
- `Pollen` mock
- `Meristem` real contra Ollama local

y mide:

- latencia de export desde Rhizome
- latencia de relay por Pollen
- latencia de generacion en Meristem
- latencia total E2E

La salida se versiona en `reports/` como JSON + Markdown.

### 2. Futuro simulador visual

Sigue siendo la carpeta candidata para la animacion/zoom-out del video final:

- grafo multi-parcela
- rutas de Pollen
- weather_packets viajando con TTL
- rechazo de policy_deltas o contexto caducado

## Comandos

Desde `code/simulator/`:

```bash
make test
make e2e
make e2e-smoke
python -m src.cross_node_e2e --model gemma4:e4b --scenario pollen_fresh_weather_review
```

## Que NO es

- No sustituye el demo real
- No decide sobre actuadores
- No debe duplicar logica productiva de Rhizome, Pollen o Meristem

Su trabajo es otro: darnos una capa de ensayo reproducible para detectar roturas
de integracion antes del rehearsal.
