# simulator/

Simulador del sistema Sprout para ilustrar el escalado en el video y probar comportamiento con 2/4/5/8 nodos Rhizome.

## Proposito

- **Apoyo al video:** zoom-out final del demo de "una terraza" a "una red". 10-15 segundos de animacion.
- **Prueba de rutas Pollen:** visualizar que parcelas visita, en que orden, que contexto transporta.
- **Ensayo de caducidad:** mostrar weather_packets caducando en el camino, policy_deltas rechazados.
- **Prueba de simulacion multi-parcela** sin tener que fabricar 8 Rhizome fisicos.

## Alcance

Minimo viable: script Python que genera una animacion o grafo estatico con matplotlib/graphviz.

Optimo: mini web-app con `vis.js` o `cytoscape.js` que permite:
- Ver parcelas en un mapa (coordenadas ficticias)
- Ver al Pollen moverse entre ellas
- Ver el estado de cada parcela cambiar
- Ver un weather_packet viajando con su TTL restante

Decision concreta en semana 2 segun ancho de banda del equipo.

## Dependencias candidatas

Para version minima:
- `networkx` + `matplotlib`
- `imageio` para generar GIFs

Para version web:
- Vanilla HTML + `vis.js` o `cytoscape.js`
- Python genera escenarios JSON, el front los anima

## Que NO es

- No es un producto nuevo
- No necesita UI compleja
- No sustituye el demo real — lo complementa para el zoom-out
