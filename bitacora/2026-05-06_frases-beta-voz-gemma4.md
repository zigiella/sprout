# Frases de Referencia para Feature Beta (Voz → Gemma 4 E4B)

Este documento recopila las frases de prueba diseñadas para la evaluación del pipeline `Voz → STT Local → Gemma 4 E4B → Mini-Evaluator`. 

El listado cubre diferentes intenciones operativas y debe usarse como referencia por el equipo (Bract, Venation, Cambium) durante la grabación de los screencasts de la demo.

## 💧 Riego Directo (Watering Commands)
**ESPAÑOL**
* "Riega la parcela A durante 30 segundos más, por favor."
* "Añade un minuto de agua al sector norte, la tierra está muy seca."
* "Aplica un ciclo de riego extra a la maceta principal."
* "Dale un poco más de agua al semillero, unos 15 segundos."

**INGLÉS**
* "Water plot A for another 30 seconds, please."
* "Add a minute of water to the north sector, the soil is too dry."
* "Run an extra watering cycle for the main planter."
* "Give the seedlings a bit more water, around 15 seconds."

## 🚫 Cancelación / Salto (Skip / Cancel Commands)
**ESPAÑOL**
* "Salta el próximo ciclo de riego, va a llover esta tarde."
* "Cancela el riego programado de hoy."
* "No riegues esta noche, la humedad ya es suficiente."
* "Detén el suministro de agua para la parcela sur."

**INGLÉS**
* "Skip the next watering cycle, it's going to rain this afternoon."
* "Cancel today's scheduled watering."
* "Don't water tonight, the moisture levels are high enough."
* "Stop the water supply for the south plot."

## ⚙️ Ajuste de Umbrales (Threshold Overrides)
**ESPAÑOL**
* "Sube el límite máximo de agua a 200 segundos."
* "Ajusta la ventana de riego para que empiece a las 8 de la tarde."
* "Ignora el aviso del nivel del tanque por hoy."
* "Permite regar aunque la humedad del suelo esté por encima del 60%."

**INGLÉS**
* "Increase the maximum watering limit to 200 seconds."
* "Adjust the watering window to start at 8 PM."
* "Ignore the low tank level warning for today."
* "Allow watering even if soil moisture is above 60%."

## 🤔 Consultas y Razonamiento (Audit / Info)
**ESPAÑOL**
* "¿Por qué no se regó la parcela B esta mañana?"
* "Dime el estado actual del tanque de agua."
* "Revisa la última decisión de Rhizome y dime si fue correcta."

**INGLÉS**
* "Why wasn't plot B watered this morning?"
* "Tell me the current water tank level."
* "Audit Rhizome's last decision and tell me if it was correct."

> **💡 Nota de Uso:** Para forzar el comportamiento de bloqueo del Mini-Evaluator en las demos, probad a usar un comando extremo (e.g. "Riega durante 5 horas seguidas"). Esto causará un `REFUSE_HARD` y evidenciará la protección de hard limits del firmware físico.
