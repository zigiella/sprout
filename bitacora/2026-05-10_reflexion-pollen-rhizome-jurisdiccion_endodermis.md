# Reflexion Endodermis — Pollen, Rhizome y jurisdiccion de la visita

**Fecha:** 2026-05-10 (dia 24)
**Frente:** arquitectura Rhizome/Pollen
**Contexto:** conversacion con Bea sobre si Pollen debe seguir siendo nodo
inteligente o podria reducirse a interfaz de Rhizome.

---

## Pregunta

Si Pollen no tuviera Gemma 4 y fuese solo una app que pone interfaz a Rhizome,
¿que podria hacer Rhizome? ¿Que debe hacerse necesariamente en Pollen? ¿Como se
justifica mantener Pollen como nodo inteligente?

## Tesis corta

Una Pollen minima podria ser solo interfaz, grabadora y transporte hacia
Rhizome. Pero una Pollen inteligente sigue teniendo sentido porque su
jurisdiccion natural no es el agua, sino la visita humana.

Rhizome entiende la parcela. Pollen entiende la visita.

## Lo que Rhizome podria asumir si Pollen fuese tonta

Con Gemma 4 E2B en Jetson, Rhizome podria hacer mas de lo que parecia al
principio:

- recibir un WAV grabado por Pollen;
- transcribir o interpretar la intencion humana;
- convertir voz en una intencion estructurada;
- generar `MissionPatch`, `PolicyPacket` de visita o equivalente;
- explicar decisiones a traves de Pollen;
- resumir "que paso desde mi ausencia";
- leer snapshots, receipts e historico local;
- detectar anomalias locales;
- preparar texto multilingue para que Pollen solo lo renderice.

Esto es tecnicamente viable porque Gemma 4 E2B en Rhizome puede actuar como
cerebro local multimodal y Pollen podria ser solo microfono, pantalla y cliente.

## Por que no deberia ser el camino principal

Que Rhizome pueda hacerlo no significa que deba cargar con todo.

Rhizome ya tiene una jurisdiccion critica:

- observar parcela;
- hablar con ESP32;
- decidir riego en escala de minutos;
- mantener heartbeat;
- escribir `DecisionReceipt`;
- explicar decisiones;
- sobrevivir offline;
- no volverse peligroso.

Si ademas asume conversacion humana, multilinguismo, notas de voz, comparacion
entre parcelas, UX de visita y mediacion cultural, Rhizome deja de ser nodo de
parcela y empieza a ser cerebro total del sistema. Eso debilita una de las
fortalezas de Sprout: jurisdicciones claras.

## Lo que si pertenece naturalmente a Pollen

Pollen vive donde vive la persona: en el movil, durante la visita, cerca de la
voz, la camara, la pantalla y el contexto humano.

Por eso Pollen debe asumir, o al menos es el mejor lugar para asumir:

- capturar intencion humana;
- recoger notas de voz y observaciones;
- conversar sobre lo observado;
- mostrar estado y explicaciones de forma comprensible;
- comparar varios Rhizomes durante una ruta;
- transportar conocimiento entre parcelas sin internet;
- convertir la visita en contratos caducables;
- emitir intenciones con TTL o `valid_until`;
- adaptar idioma, tono, accesibilidad y confianza a la agricultora;
- mediar consentimiento humano sin tocar actuadores.

Una frase util:

> Rhizome cuida el agua; Pollen cuida la relacion entre persona, conocimiento y
> territorio.

## Pollen como inteligencia federada

Pollen no es solo pantalla. Es el nodo que recorre parcelas y reparte
conocimiento entre ellas. Al visitar varios Rhizomes, puede comparar estados,
detectar diferencias, llevar observaciones de una parcela a otra y devolver a la
agricultora una vision de conjunto.

Esto justifica la frase:

> Pollen convierte cada visita humana en inteligencia federada: recoge
> observaciones locales, las estructura, las transporta entre parcelas y devuelve
> explicaciones comprensibles en el idioma de la agricultora.

## Idiomas minoritarios y adaptacion local

El argumento mas fuerte para mantener Gemma 4 en Pollen es el lenguaje humano.

En el futuro, Pollen podria recibir fine-tuning, adaptacion o prompt packs para
entender mejor idiomas minoritarios o infrarrepresentados: suahili, pular,
wolof, bambara, quechua u otras lenguas locales. Ese trabajo encaja mejor en el
nodo que escucha a la persona que en el nodo que protege la frontera fisica.

¿Podria hacerse en Rhizome? Si. Pero seria pedir demasiado a Rhizome: agricultor,
interprete, operador, memoria local, juez de riego y puente entre parcelas. En
una arquitectura segura, esa carga se reparte.

## Formulacion para writeup

Propuesta de parrafo:

> Una version minima de Pollen podria ser solo una interfaz hacia Rhizome. Pero
> mantener Gemma 4 en Pollen separa dos inteligencias distintas: Rhizome entiende
> la parcela; Pollen entiende la visita. Esa separacion permite adaptar lenguaje,
> voz y contexto humano sin cargar al nodo fisico ni comprometer la frontera de
> seguridad.

Y una version mas emocional:

> Rhizome cuida el agua. Pollen cuida la conversacion. Entre ambas, Sprout no
> solo automatiza riego: convierte visitas intermitentes en conocimiento local
> que viaja.

## Decision recomendada

Mantener dos niveles posibles:

1. **Pollen simple viable:** interfaz, microfono, pantalla, transporte y cliente
   de Rhizome. Sirve como fallback y reduce riesgo.
2. **Pollen inteligente aspiracional/MVP fuerte:** nodo Gemma 4 de visita que
   entiende voz, observaciones, comparacion multi-parcela e intencion humana.

Arquitectonicamente, la version inteligente es mas poderosa porque evita que
Rhizome se convierta en monolito. Pollen no debe decidir agua. Debe convertir
presencia humana en contexto estructurado, caducable y transportable.
