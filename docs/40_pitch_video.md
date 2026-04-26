# Pitch y vídeo — v2

## 1. Pitch de 30 segundos

Sprout es una arquitectura local-first para riego en parcelas aisladas.  
Cada parcela tiene un nodo Rhizome que decide y actúa offline con Gemma 4 E2B sobre Jetson, pero solo dentro de un sobre seguro impuesto por un ESP32. Cuando una persona visita la parcela, Pollen en Android usa Gemma 4 E4B para hablar con Rhizome, validar su criterio, compilar nuevas prioridades humanas y traer contexto util de meteo externa. Meristem queda especificado como cerebro lento post-hackathon. El resultado es mejor criterio de riego cuando el campo, la persona y la red no coinciden en el tiempo.

## 2. Pitch de 90 segundos

La agricultura aislada no sufre solo por falta de agua.  
Sufre porque la decisión correcta suele llegar tarde. Si no hay buena conectividad y solo visitas la parcela cada cierto tiempo, acabas regando demasiado tarde, demasiado pronto o con el criterio equivocado.

Sprout reduce esa latencia con tres nodos. Rhizome vive en la parcela y decide offline con sensores, meteo y política vigente. Pero nunca toca el agua directamente: un ESP32 verifica reglas duras y ejecuta o bloquea. Pollen vive en un móvil Android con Gemma 4 y convierte cada visita en algo mucho más valioso que una sincronización: habla con la persona, pregunta a Rhizome qué hizo, valida el estado real y trae contexto fresco a la parcela. Meristem queda como cerebro lento para consolidar resultados y emitir políticas mejores.

En nuestra demo usamos una maceta como parcela lógica visitada periódicamente. Veremos cómo Rhizome sigue funcionando solo, cómo Pollen trae criterio humano y contexto fresco de meteo externa, y cómo el sistema modifica su criterio de riego cuando la visita aporta información nueva — o rechaza instrucciones y digests que ya no merecen confianza.

## 3. Frases fuertes

- **Rhizome mantiene viva la parcela cuando nadie está.**
- **Pollen convierte la visita en inteligencia útil.**
- **La IA propone; el agua la gobierna una capa física prudente.**
- **En Sprout, toda inteligencia tiene jurisdicción y fecha de caducidad.**

## 4. Estructura del vídeo (3 minutos)

> Pivote v2.1 (dia 11): demo sobre **una sola parcela visitada periodicamente**. La diferencia que demuestra el sistema se muestra **en el tiempo** (criterio antes y despues de la visita humana), no **en el espacio** (parcela A vs parcela B). Razon: filmar dos parcelas no diferenciadas en el sistema fuerza la metafora; una parcela con cambio interno **es** lo que el sistema hace. La cartela "Criterio modificado" queda como ancla narrativa de la escena 7.

### Escena 1 — La ausencia (0:00–0:20)
Plano de una maceta como parcela logica y mensaje:
"Esto representa parcelas visitadas periódicamente, no continuamente."

### Escena 2 — Rhizome decide offline (0:20–0:45)
Se ve:
- sensor,
- estado local,
- decisión,
- orden al ESP32,
- `DecisionReceipt`.

### Escena 3 — El ESP32 protege (0:45–1:00)
Mostrar un caso de bloqueo:
- depósito bajo o comando fuera de rango,
- rechazo visible,
- texto corto en pantalla.

### Escena 4 — Llega Pollen (1:00–1:35)
En el móvil:
- pregunta "¿qué pasó desde mi última visita?"
- Rhizome responde a través del teléfono,
- se ve resumen de decisiones.

### Escena 5 — La persona da una misión (1:35–1:55)
Voz o texto, con escenario tipo:
"Vuelvo en 72 horas. Manten austera. No gastes mas de 900 ml."

Pollen compila a `MissionPatch` con presupuesto y ventana de riego como parametros visibles del cambio.

### Escena 6 — Contexto transportado (1:55–2:20)
Pollen trae `WeatherDigest` desde meteo externa local (estacion meteo, gateway, otro punto del mismo terreno) hacia la parcela. El gesto del overlay "WeatherDigest ferry" se preserva; cambia el origen, no el gesto.

### Escena 7 — Criterio modificado (2:20–2:40)
Rhizome acepta el `MissionPatch` valido y **modifica su criterio sobre la misma parcela**:
- presupuesto reducido visible en pantalla del receipt,
- ventana de riego desplazada visible en pantalla del receipt,
- una sola accion fisica filmable que demuestra el cambio (la planta riega mas tarde y con menos agua que la vez anterior).

Cartela ancla: **"Criterio modificado"**.

### Escena 8 — Caducidad y cierre (2:40–3:00)
Mostrar un digest o patch caducado que se rechaza.
Cerrar con zoom out narrativo:
"De una parcela a una red de parcelas aisladas."

## 5. Shot list mínima

- overlay “offline”
- overlay “DecisionReceipt”
- overlay “ESP32 REJECT”
- overlay “MissionPatch validado”
- overlay “WeatherDigest ferry”
- overlay “expired → rejected”

## 6. Qué no enseñar

- largas terminales,
- setup eléctrico entero,
- sync complejo,
- visión si todavía es frágil,
- Meristem si no está sólido.
