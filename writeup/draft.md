# Sprout — writeup (draft en curso)

> **Autores:** Cambium + Bea. Corola no toca este documento (scope: video).
> Issue: #11.
> Estado: **esqueleto navegable**, contenido por escribir en sesiones Cambium ↔ Bea los dias 6-25.

---

## 0. Titulo + subtitulo — ~30 palabras

<!--
Objetivo: titulo pegadizo + subtitulo que resume el proyecto en una linea.

Candidatos de titulo (a elegir con Bea):
- Sprout: reducing absence in remote farming
- Sprout: water decisions, offline, on time
- Sprout: a farm network that doesn't need the internet

Candidatos de subtitulo:
- "El agua no se pierde solo por escasez. Se pierde porque la decision llega tarde."
- "Un diseño de red agricola que convierte la ruta del agricultor en canal de inteligencia."

Decision: dia 20 (tras video rodado, sabremos mejor cual pega).
-->

## 1. Problema — ~200 palabras

Una parcela de almendros a cuarenta kilometros del pueblo mas cercano. El
agricultor la visita una vez por semana, a veces menos. Entre visita y
visita, el suelo decide solo: o recibe agua a tiempo, o no la recibe.
Cuando el agricultor vuelve, el problema ya ha pasado — solo queda medir
cuanto se perdio.

La escena no es anecdota. La ITU mide en 2025 una brecha de 27 puntos
entre cobertura movil urbana (85%) y rural (58%) en paises desarrollados;
en Australia, el 90% del territorio vive sin conectividad fiable. El
Banco de España atribuye entre un 20% y un 30% de las perdidas de trigo
de la campaña 2022-23 al retraso en decisiones agronomicas, no a escasez
absoluta de recurso. IRRIFRAME sirve a 40.000 explotaciones en
Emilia-Romaña desde un servidor central — un modelo que funciona donde
hay red y se degrada donde no la hay.

El denominador comun no es la falta de agua. Es el **lag** entre lo que
pasa en la parcela y la decision que deberia corregirlo. Cuando la red
falla o el agricultor no esta, ese lag se mide en dias. Cerrar el lag
exige llevar la decision donde hay agua — no al reves.

<!-- Fuentes: research/narrative_sources.md (ITU 2025, BdE 2025, IRRIFRAME, Australia Regional Tech Hub). -->

## 2. Solucion — ~300 palabras

<!--
Los tres nodos + frase clave + por que funciona SIN depender de internet
continuo (pero tampoco ASUMIR offline total — *usar framing del espectro
de conectividad, ver bitacora 2026-04-18_reframe-narrativo-pollen*).

Puntos a cubrir:
- Rhizome: nodo edge, decisiones locales seguras, Gemma 4 E2B
- Pollen: NO "mula de datos". Transferencia cruzada entre parcelas via
  presencia humana. Auditor con modelo gemelo. Autoridad fisica.
  (tres angulos, elegir el/los que encajen con el video)
- Meristem: consolidacion estrategica, Gemma 4 E4B local

Frase clave candidata:
"Rhizome ejecuta, Pollen transporta inteligencia cruzada, Meristem aprende."

Matiz del nuevo framing (obligatorio):
"Sprout no es un sistema para parcelas sin internet. Es un sistema que
funciona en todo el espectro de conectividad — WiFi, 4G intermitente,
o nada — sin que el agricultor tenga que saber de redes."
-->

## 3. Arquitectura — ~350 palabras

<!--
- Diagrama (reutilizar de docs/01_architecture.md renderizado como PNG)
- Stack: Python + pydantic + FastAPI + Ollama (Meristem/Rhizome),
  Kotlin + LiteRT (Pollen), ESP32 firmware (Rhizome fisico)
- Reglas duras: §30 safety rules resumidas (5 limites fisicos no negociables)
- Flujo: RhizomeSnapshot -> evidencia -> Meristem consolida -> PolicyDelta
  -> Rhizome aplica bajo validacion firmware
- Esquemas v1.0 (contratos de datos frozen) — valor de ingenieria

Visuales obligatorios:
- [ ] Diagrama 3-nodos (existe, exportar)
- [ ] Tabla safety rules (generar)
- [ ] Ciclo de vida de una politica (dibujar)
-->

## 4. Demostracion — ~250 palabras

<!--
Lo que muestra el video + 1-2 screenshots.

Coordinar con Corola cuando tenga shot list cerrado (dia 12-15).
Preguntas para Corola:
- ¿Que escena abre el video?
- ¿Donde se ve el momento WOW de Pollen (transferencia cruzada)?
- ¿Que quedara en pantalla como "prueba de funcionamiento"?

Screenshots obligatorios:
- [ ] Splitscreen dashboard de Pollen (ya implementado, PR #20 y #30)
- [ ] Output de Meristem emitiendo un PolicyDelta
- [ ] Firmware ESP32 rechazando una regla que viola §30 (si Xilema entrega issue #4)
-->

## 5. Fine-tuning — ~150 palabras

<!--
- Dataset: sintetico + real (describir proporcion)
- Metodo: Unsloth LoRA sobre Gemma 4 E2B (el modelo edge)
- Benchmarks: p50 latencia, tok/s, acierto vs ground truth
- Insight: "el modelo pequeño fine-tuneado supera al grande generico en
  el dominio acotado". Dato a validar en dias 20-25.

Pendiente:
- Datos reales de finetune (ver code/finetune/)
- Resultados de PR #32 (Xilema) para el angulo comparativo
-->

## 6. Validacion local vs sombra — ~100 palabras

<!--
"Meristem ejecuta enteramente local con Gemma 4 E4B. En paralelo, un modo
sombra OPCIONAL compara el output con Gemma 31B remoto para auditar
acuerdo/desacuerdo. En produccion el sombra esta OFF; solo se usa durante
desarrollo para calibrar la calidad del modelo local."

Punto clave de honestidad: el proyecto NO depende de internet ni de modelos
remotos. El modo sombra es herramienta de validacion, no de ejecucion.

Datos a rellenar: % de acuerdo cuando el sombra estuvo encendido (dia 22-25).
-->

## 7. Impacto y escalado — ~100 palabras

<!--
- Coste por nodo (BOM): ~X€ Rhizome + Y€ Pollen (movil reutilizado) + Z€
  Meristem (portatil estandar)
- Escalabilidad: cada Meristem puede coordinar N Rhizomes (estimar N)
- Segmento: explotaciones pequeñas y medianas en zonas de baja poblacion
  (Aragon, Extremadura, Castilla-La Mancha, Andalucia interior, islas)
- Transferencia a otros dominios: acuicultura, invernaderos aislados,
  apicultura nomada
-->

## 8. Limitaciones — ~50 palabras

<!--
Ser honestos, no defensivos. Lista corta:
- Parcelas muy grandes (>10 zonas) no probadas
- Pollen depende de visita humana (~semanal) — si la ruta falta, Meristem
  no recibe consolidacion
- Safety rules §30 son para riego; otros dominios requeririan otras reglas
- No probado en produccion real, solo en demo controlado con datos sinteticos
  realistas
-->

## 9. Cierre — ~50 palabras

<!--
Frase final potente. Candidatos:

1. "La agricultura no se salvara con mas datos. Se salvara con decisiones
   a tiempo, tomadas donde hay agua."
2. "Sprout no sustituye al agricultor. Le deja mas tiempo para ser
   agricultor."
3. "Cuatro modelos Gemma pequeños, correctamente orquestados, pesan mas
   que uno grande aislado."

Decision: dia 25, tras video y demos.
-->

---

## Checklist del writeup (para tracking interno Cambium/Bea)

- [ ] Conseguir cifra opener del problema (dia 6-8)
- [ ] Generar diagrama arquitectura exportable a PNG (dia 10)
- [ ] Cerrar titulo + subtitulo con Bea (dia 20)
- [ ] Sesion escritura conjunta seccion 1-2 (dia 6 o 7)
- [ ] Sesion escritura conjunta seccion 3-4 (dia 12-13)
- [ ] Sesion escritura conjunta seccion 5-7 (dia 18-20)
- [ ] Review final conjunto (dia 27-28)
- [ ] Recorte a 1500 palabras (dia 29)

## Proximas sesiones agendables

| Dia | Foco | Output esperado |
|-----|------|-----------------|
| 6 o 7 | Seccion 1 (problema) + datos opener | 200 palabras + fuentes citadas |
| 12-13 | Seccion 3 (arquitectura) | 350 palabras + diagrama escogido |
| 18-20 | Secciones 5-7 (fine-tuning, validacion, impacto) | Con datos reales de PR finetune |
| 27-28 | Review completo + recorte | Version entregable |
