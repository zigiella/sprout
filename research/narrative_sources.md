# Fuentes de narrativa con evidencia — Sprout

**Autora:** Bea
**Fecha:** 2026-04-19
**Uso:** material base para video (Corola) y writeup (Cambium + Bea). Cada punto trae claim, dato, fuente autoritativa, sugerencia de voz en off y plano.

---

## Frase madre

**El cambio climatico esta haciendo que el agua sea mas incierta, la observacion mas dificil y las decisiones tardias mas caras. Sprout existe para llevar criterio operativo a parcelas donde no puedes estar cada dia y donde no puedes depender siempre de la red.**

La primera mitad se sustenta en IPCC, Banco de España, FAO e ITU. La segunda mitad esta alineada con el brief y la arquitectura del proyecto.

---

## 1. El contexto real

**Claim.** El campo para el que diseñamos no vive en conectividad continua.

**Dato.** En 2025 usa internet el 85% de la poblacion urbana mundial, frente al 58% de la rural. En paises de renta baja, solo el 14% de la poblacion rural esta conectada.

**Fuente.** ITU, *Facts and Figures 2025*. [[ITU][1]] [[ITU-FF2025][2]]

**Voz en off.** "No estamos diseñando para una finca perfecta con nube, cobertura y supervision constante. Diseñamos para donde la red falla y la decision no puede esperar."

**Plano.** Mapa rural, movil sin cobertura, plano corto de parcela aislada, interfaz local funcionando sin conexion.

---

## 2. La escala del problema

**Claim.** La agricultura mundial esta formada, sobre todo, por explotaciones pequeñas y familiares.

**Dato.** Hay mas de 608 millones de explotaciones en el mundo. Mas del 90% son explotaciones familiares. Las de menos de 2 hectareas representan el 84% del total, aunque operan solo alrededor del 12% de la tierra agricola y producen aproximadamente el 36% de los alimentos mundiales.

**Fuente.** FAO, *Farms, family farms, farmland distribution and farm labour*. [[FAO][3]]

**Voz en off.** "La agricultura global no se parece a las demos. Se parece mucho mas a millones de pequeñas decisiones tomadas con recursos limitados."

**Plano.** Mosaico de parcelas pequeñas, manos, deposito pequeño, bomba sencilla, contraste con dashboard sofisticado que no encaja.

---

## 3. El agua esta en el centro

**Claim.** Cuando mejoras la gestion del agua en agricultura, actuas sobre el nucleo del problema.

**Dato.** Segun FAO AQUASTAT, el 69% de las extracciones globales de agua corresponde a agricultura, frente al 12% municipal y el 19% industrial.

**Fuente.** FAO AQUASTAT, metodologia de usos del agua.

**Voz en off.** "El agua agricola no es un detalle. Es la mayor palanca del sistema."

**Plano.** Grafico simple de reparto del uso del agua, corte a riego real, deposito bajando, suelo seco.

---

## 4. El Mediterraneo entra en una fase mas dura

**Claim.** El cambio climatico no es un decorado. Esta endureciendo el comportamiento del agua en el Mediterraneo.

**Dato.** El IPCC concluye con alta confianza que aumentaran la severidad e intensidad de las sequias mediterraneas, disminuira la humedad del suelo, bajara la escorrentia anual y, bajo escenarios medios o altos, la probabilidad de sequias extremas aumentara entre un 200% y un 300%.

**Fuente.** IPCC AR6 WG1, capitulo 10. [[IPCC][4]]

**Voz en off.** "El problema ya no es una mala temporada. Es una nueva condicion operativa."

**Plano.** Paisaje mediterraneo seco, calor visible, hojas caidas, comparacion entre mapas o estaciones.

---

## 5. La misma parcela empieza a pedir mas agua

**Claim.** Con mas calor y menos lluvia util, el cultivo exige decisiones de riego mas finas y mas frecuentes.

**Dato.** En Cerdeña, un estudio de 2025 proyecta aumentos de demanda hidrica del 12% al 14% en trigo y cebada, y aumentos del 4% al 7% en otros cultivos relevantes bajo escenarios futuros.

**Fuente.** *Irrigation Science* 2025, estudio sobre demanda hidrica de cultivos en Cerdeña.

> ⚠ **Verificar URL de la fuente.** El documento original cita [IPCC] para este punto, pero el estudio es de *Irrigation Science* 2025. Antes de usar publico, localizar DOI real del paper.

**Voz en off.** "El clima no solo trae menos agua. Tambien hace que el calendario de riego deje de servir."

**Plano.** Calendario tachado, sensor, hoja lacia, variacion de temperatura, cambio de estado en Rhizome.

**Nota.** La idea de "decisiones mas finas y frecuentes" es una inferencia razonable a partir del aumento de demanda hidrica y de variabilidad climatica. Esta apoyada por la evidencia, pero la frase en si es interpretacion estrategica.

> Recomendacion Cambium: este punto queda **fuera del video** por ser "soft", se mantiene en el writeup como matiz honesto.

---

## 6. Decidir tarde ya tiene coste medible

**Claim.** La decision tardia ya no es una molestia. Tiene impacto economico real.

**Dato.** El Banco de España estima que la escasez de agua de 2022 y 2023 redujo entre un 20% y un 30% los rendimientos del trigo y la cebada, y al menos un 10% los del olivar.

**Fuente.** Banco de España, Boletin Economico 2025/T2, articulo 07. [[BdE][5]]

**Voz en off.** "Cuando el agua falla y la respuesta llega tarde, la perdida ya no es teorica. Ya aparece en el rendimiento."

**Plano.** Corte de cosecha, espiga, olivo, descenso grafico de rendimiento, plano de recibo de ejecucion.

---

## 7. La buena gestion del riego ya ha demostrado escala

**Claim.** El valor de decidir mejor el riego ya se ha probado a escala real.

**Dato.** IRRINET-IRRIFRAME cubre mas de 40.000 explotaciones, casi el 40% del area regada de Emilia-Romaña. Entre 2007 y 2013 genero ahorros de mas de 50 millones de m³, y en 2013 gestionaba cerca del 55% del regadio italiano con ahorros de unos 100 millones de m³ al año.

**Fuente.** EU CAP Network, caso IRRINATE-IRRIFRAME. [[EU-CAP][6]]

**Voz en off.** "La inteligencia de riego no es una promesa. Ya ha demostrado escala. El problema es que no llega igual a todas partes."

**Plano.** Mapa de Italia, interfaz simple de recomendaciones, SMS o app ligera, paso luego a la arquitectura de Sprout.

---

## 8. La ultima milla del dato sigue rota

**Claim.** No basta con tener prediccion climatica. Hay que convertirla en criterio utilizable.

**Dato.** Una revision sistematica de 2025 sobre servicios climaticos en Africa subsahariana concluye que funcionan mejor los modelos participativos y contextuales, que fallan los modelos top-down, y que entre las barreras principales estan la mala infraestructura digital, la baja alfabetizacion y los sesgos de genero.

**Fuente.** *Frontiers in Climate* 2025, revision sistematica. [[Frontiers][7]]

**Voz en off.** "El dato no sirve por existir. Sirve cuando alguien puede usarlo a tiempo."

**Plano.** Pantalla con prevision, agricultor sin acceso, luego transicion a Pollen llevando contexto y Meristem ajustando politica.

---

## 9. Ya existen despliegues que usan canales ligeros

**Claim.** La respuesta no es esperar conectividad perfecta. La respuesta es hacer llegar criterio util por canales viables.

**Dato.** La plataforma desarrollada por KALRO con apoyo del Banco Mundial ofrece actualizaciones agroclimaticas, informacion de mercado y recomendaciones climaticamente inteligentes por app, web y SMS. El material oficial indica alcance de mas de ocho millones de pequeños agricultores. KALRO describe ademas KAOP como una plataforma que genera advisories agroclimaticos localizados y los disemina por portal web y SMS.

**Fuente.** World Bank Academy, KALRO, KAOP. [[WB][8]]

**Voz en off.** "El futuro no pasa por una app bonita. Pasa por hacer que la informacion correcta llegue por el canal que si existe."

**Plano.** SMS entrando, movil sencillo, web minima, luego Pollen sincronizando deltas.

---

## 10. La ausencia humana es un problema logistico, no poetico

**Claim.** En explotaciones remotas, revisar el agua puede implicar horas de desplazamiento.

**Dato.** En una estacion ganadera del Territorio del Norte australiano, de 2,1 millones de acres y 14.000 cabezas, la falta de cobertura movil fiable en el 90% de la propiedad hacia que el control manual del agua implicara largas distancias, mas trabajo y costes operativos altos.

**Fuente.** Regional Tech Hub, Australia. [[RegionalTech][9]]

**Voz en off.** "Hay lugares donde comprobar si queda agua no es pulsar un boton. Es perder medio dia."

**Plano.** Coche, pista, deposito, tanque, contraste con monitorizacion remota y decision local.

---

## 11. Reducir visitas tambien es impacto

**Claim.** La monitorizacion util no elimina a la persona, pero reduce visitas rutinarias y permite intervenir mejor.

**Dato.** En un caso apoyado por Agriculture Victoria, una explotacion con un bloque a 30 km redujo revisiones rutinarias de cercas de al menos dos veces por semana a una media de una vez cada quince dias, con un beneficio neto estimado de 4.760 dolares en un año.

**Fuente.** Caso de adopcion tecnologica rural citado por Agriculture Victoria y Farmo. [[RegionalTech][9]]

**Voz en off.** "No se trata de sacar a la persona del sistema. Se trata de que no tenga que estar fisicamente donde no hace falta."

**Plano.** Chequeo remoto, alertas, visita solo cuando hay contradiccion o riesgo, conexion con Pollen.

---

## 12. Ahi encaja Sprout

**Claim.** Sprout no vende automatizacion ciega. Vende criterio operativo cuando no puedes estar alli y no puedes depender de internet.

**Dato.** El brief define Sprout como red agricola local-first para parcelas remotas con agua limitada, presencia humana intermitente y conectividad incierta. El problema no es automatizar una bomba, sino reducir la ausencia; y el sistema debe funcionar offline, con seguridad fisica, politicas trazables y estrategia que viaja entre Rhizome, Pollen y Meristem.

**Fuente.** Brief y arquitectura del MVP de Sprout (`docs/00_brief.md`, `docs/01_architecture.md`).

**Voz en off.** "Sprout existe para llevar criterio operativo a parcelas donde el agua es limitada, la presencia humana es intermitente y la red no siempre esta."

**Plano.** Rhizome leyendo señales, Pollen transportando contexto, Meristem ajustando politica, ejecucion o bloqueo con recibo.

---

## Seleccion recomendada

### Para video (60 s, 3-4 puntos)

Mi seleccion preferida (Cambium):

1. **Conectividad rural** (ITU 85/58) — establece terreno.
2. **Coste en España** (Banco de España 20-30%) — gancho emocional cercano.
3. **Precedente que funciona** (IRRIFRAME 40.000 explotaciones).
4. **Ausencia logistica** (Australia / Agriculture Victoria) — si sobra tiempo.

Punto 5 (Cerdeña) y punto 8 (Africa subsahariana) quedan **fuera del video**: el primero por ser inferencia estrategica, el segundo por geografia lejana para un jurado europeo.

### Para writeup (4 minutos de lectura, ~1500 palabras)

Todos los 12 puntos son utiles. Enlazar las fuentes como citations al final.

---

## Banco de claims de reserva

Utiles para subtitulos, slides, postproduccion.

- "El 69% del agua extraida en el mundo se usa en agricultura."
- "Solo el 58% de la poblacion rural mundial usa internet."
- "Hay mas de 608 millones de explotaciones en el mundo y mas del 90% son familiares."
- "En el Mediterraneo, la probabilidad de sequias extremas puede crecer entre un 200% y un 300%."
- "La sequia de 2022 y 2023 redujo entre un 20% y un 30% el rendimiento de trigo y cebada en España."
- "IRRIFRAME ya cubre mas de 40.000 explotaciones."
- "KALRO y el Banco Mundial han llevado advisories agroclimaticos a mas de ocho millones de pequeños agricultores."
- "Los servicios climaticos funcionan mejor cuando son participativos y contextuales."

---

## Fuentes

[1]: https://www.itu.int/en/mediacentre/Pages/PR-2025-11-17-Facts-and-Figures.aspx "ITU Press Release"
[2]: https://www.itu.int/ff2025 "ITU Facts and Figures 2025"
[3]: https://www.fao.org/family-farming/detail/en/c/1261522/ "FAO — Farms, family farms"
[4]: https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-10/ "IPCC AR6 WG1 Chapter 10"
[5]: https://www.bde.es/wbe/es/publicaciones/analisis-economico-investigacion/boletin-economico/2025t2-articulo-07-el-impacto-de-la-sequia-en-la-produccion-agricola-espanola-.html "Banco de España, BE 2025/T2"
[6]: https://eu-cap-network.ec.europa.eu/good-practice/irrinate-irriframe-sustainable-irrigation-management_en "EU CAP Network — IRRINATE-IRRIFRAME"
[7]: https://www.frontiersin.org/journals/climate/articles/10.3389/fclim.2025.1616691/full "Frontiers in Climate 2025"
[8]: https://academy.worldbank.org/en/planet/agriculture/digital-ag-series-big-data-platform-scaling-up-data-driven-digital-agriculture-learnings-from-the-kenya-experience "World Bank Academy — KALRO/KAOP"
[9]: https://regionaltechhub.org.au/on-farm-connectivity-program-case-study-remote-watering/ "Regional Tech Hub Australia"
