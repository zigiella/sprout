# Estrategia de Internacionalización (i18n) para Modelos LLM en Borde: El Enfoque C

**Fecha:** 2026-05-10
**Autor:** Floema & Usuario
**Contexto:** Interfaz Pollen / Jetson Edge / Sprout System

Durante el desarrollo de la interfaz de la aplicación Pollen y la lectura de las justificaciones (rationales) de las decisiones emitidas por los nodos Rhizome (Jetson/ESP32), se debatió sobre cómo gestionar el idioma de los textos técnicos generados por inteligencia artificial que el usuario lee en su pantalla.

Se acordó implementar arquitectónicamente el **Enfoque C** ("Capa de Presentación Universal").

## El Problema
Los nodos físicos en el campo (Jetson) generan JSONs estructurales (`DecisionReceipt`) que contienen explicaciones en texto libre generadas por un LLM ligero (e.g. Gemma 2B) acerca de por qué tomaron una decisión de riego (`rationaleShort` y `rationaleFull`). 
Si el sistema escala globalmente, es un anti-patrón obligar al hardware perimetral a gestionar diccionarios de traducción o a inferir en idiomas poco comunes según quién esté operando el equipo de campo.

## El Enfoque C: Desacoplamiento de Idioma en el Borde
1. **Pivote Agnóstico/Estandarizado en Borde:** 
   El sistema perimetral (Rhizome / Jetson) siempre "piensa" y genera sus logs y *rationales* en un idioma base acordado (generalmente Inglés Técnico) o en su propio idioma por defecto. Estos datos en crudo se guardan en Meristem (el servidor central) garantizando auditorías homogéneas y sin fricción técnica.

2. **Gemma 4 (Local) como Traductor Semántico de Interfaz:** 
   La aplicación móvil Pollen actúa como la capa de presentación universal. Utilizando el modelo local pesado (Gemma 4 E4B corriendo en LiteRT-LM), la app traduce automáticamente cualquier texto libre de los `DecisionReceipts` al idioma de la interfaz del usuario en milisegundos *antes* de pintarlo por pantalla (solo si detecta que no está en el idioma correcto).

## Beneficios Estratégicos
- **Agnosticidad del Hardware:** Si en un futuro se implanta Sprout en una comunidad rural africana, no es necesario reprogramar ni hacer *fine-tuning* de los modelos que corren en las placas ESP32/Jetson.
- **Preparación para Idiomas Minoritarios:** Al trasladar el peso de la traducción a la app móvil de la interfaz, basta con hacer un *fine-tuning* a Gemma 4 en el móvil para que entienda y se exprese en un idioma minoritario (e.g. Pular, Wolof). El modelo traducirá el log base en inglés a la jerga local.
- **Eficiencia de Almacenamiento:** Las bases de datos centrales no almacenan la misma explicación replicada en siete idiomas distintos. El dato viaja en un solo idioma; la pantalla lo renderiza en el que corresponda.

Esta directiva queda como estándar oficial para el manejo de idiomas en la UI de telemetría de Sprout.
