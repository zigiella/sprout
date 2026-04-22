# Pitch y vídeo — v2

## 1. Pitch de 30 segundos

Sprout es una arquitectura local-first para riego en parcelas aisladas.  
Cada parcela tiene un nodo Rhizome que decide y actúa offline con Gemma 4 E2B sobre Jetson, pero solo dentro de un sobre seguro impuesto por un ESP32. Cuando una persona visita las parcelas, Pollen en Android usa Gemma 4 para hablar con Rhizome, validar su criterio, compilar nuevas prioridades humanas y transportar contexto útil entre nodos. Cuando hay oportunidad, Meristem consolida aprendizaje y emite políticas más duraderas. El resultado es mejor criterio de riego cuando el campo, la persona y la red no coinciden en el tiempo.

## 2. Pitch de 90 segundos

La agricultura aislada no sufre solo por falta de agua.  
Sufre porque la decisión correcta suele llegar tarde. Si no hay buena conectividad y solo visitas la parcela cada cierto tiempo, acabas regando demasiado tarde, demasiado pronto o con el criterio equivocado.

Sprout reduce esa latencia con tres nodos. Rhizome vive en la parcela y decide offline con sensores, meteo y política vigente. Pero nunca toca el agua directamente: un ESP32 verifica reglas duras y ejecuta o bloquea. Pollen vive en un móvil Android con Gemma 4 y convierte cada visita en algo mucho más valioso que una sincronización: habla con la persona, pregunta a Rhizome qué hizo, valida el estado real y transporta contexto útil entre parcelas. Meristem queda como cerebro lento para consolidar resultados y emitir políticas mejores.

En nuestra demo usamos dos macetas como dos parcelas lógicas. Una dispone de mejor contexto meteorológico. La otra no. Veremos cómo Rhizome sigue funcionando solo, cómo Pollen trae criterio humano y contexto fresco, y cómo el sistema rechaza instrucciones o digests que ya no merecen confianza.

## 3. Frases fuertes

- **Rhizome mantiene viva la parcela cuando nadie está.**
- **Pollen convierte la visita en inteligencia útil.**
- **La IA propone; el agua la gobierna una capa física prudente.**
- **En Sprout, toda inteligencia tiene jurisdicción y fecha de caducidad.**

## 4. Estructura del vídeo (3 minutos)

### Escena 1 — La ausencia (0:00–0:20)
Plano de dos macetas/parcelas y mensaje:
“Esto representa parcelas visitadas periódicamente, no continuamente.”

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
- pregunta “¿qué pasó desde mi última visita?”
- Rhizome responde a través del teléfono,
- se ve resumen de decisiones.

### Escena 5 — La persona da una misión (1:35–1:55)
Voz o texto:
“Vuelvo en 72 horas. Prioriza A. No gastes más de 900 ml.”

Pollen compila a `MissionPatch`.

### Escena 6 — Contexto transportado (1:55–2:20)
Pollen lleva `WeatherDigest` o bundle de A a B.

### Escena 7 — Rhizome reevalúa (2:20–2:40)
Rhizome acepta el patch válido y modifica su criterio.
Opcional: una parcela riega y la otra espera.

### Escena 8 — Caducidad y cierre (2:40–3:00)
Mostrar un digest o patch caducado que se rechaza.
Cerrar con zoom out:
“De dos macetas a una red de parcelas aisladas.”

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
