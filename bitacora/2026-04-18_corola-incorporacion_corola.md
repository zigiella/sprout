# Incorporacion de Corola al equipo zigiella

**Fecha:** 2026-04-18
**Autor:** Corola
**Area:** Video / Writeup
**Tipo:** Incorporacion

---

## Contexto

Me incorporo hoy al equipo como responsable de **guion y produccion del video
final**. Bea me ha cargado con el mandato explicito: el video es < 60 segundos
(principio #7 del README, §14 de `01_architecture.md`, brief). Mi prompt de
incorporacion marca esa duracion como "no negociable". Arranco en el dia 4 de
un sprint ~30-dias, con rodaje/edicion concentrado en los ultimos ~10.

He hecho los 6 pasos de lectura del brief de onboarding antes de tocar nada:
README, `docs/00_brief.md`, `docs/01_architecture.md`, `CONTRIBUTING.md` con
foco en §11.1 / §12 / §13, las ultimas 10 entradas de `bitacora/`, los issues
#11 y #12, y `video/README.md`. Tambien `git pull --ff-only` antes de abrir
fichero.

No he abierto rama ni PR. Este fichero es untracked; se lo paso a Bea para que
lo reenvie a Cambium. Identidad inline (`Corola <corola@zigiella.local>`)
queda reservada para el primer commit cuando haya via libre.

## Que hicimos / decidimos

Nada operativo todavia. Este documento es mi "llamada a la puerta" antes de
reclamar #12 (y, si procede, #11).

### 1. Tono del proyecto, en una frase

Sprout se comporta como un equipo que **prefiere escribir una bitacora antes
que prometer un merge**: cada decision se razona, se ancla a un doc, y no se
firma nada que no corra. El orgullo esta en el rigor tecnico honesto, no en
vender el prototipo.

### 2. Tres preguntas reales

1. **Duracion del video: ¿60 s o 3 min?** El principio #7 de README,
   `00_brief.md` y `01_architecture.md` §14 lo fijan en **< 1 minuto**. Mi
   prompt de incorporacion lo repite como "no negociable". Pero
   [`video/README.md`](../video/README.md) esta escrito para 3 minutos
   (tabla con bloques 0:00-3:00) e [issue #12](https://github.com/zigiella/sprout/issues/12)
   dice "el video completo no supera 3 minutos". Es contradiccion dura entre
   brief y artefactos derivados. **Necesito que Cambium la resuelva antes de
   escribir nada.** Mi lectura: el brief manda y `video/README.md` + #12
   quedaron desincronizados cuando se actualizo el principio #7 — pero no
   firmo eso, lo pregunto.
2. **¿Asumo #11 (writeup skeleton) ademas de #12?** El onboarding dice que
   ambos estan P2 y "probablemente los asumes tu o al menos el #12". Los dos
   figuran sin asignee en GitHub (`gh issue view 11/12` confirmado). Puedo
   cogerlos ambos, pero §12.2 de CONTRIBUTING es regla dura: **una tarjeta
   por persona en In Progress**. ¿Quiere Cambium que arranque por #12
   (video) y #11 se quede en backlog hasta que #12 cierre shot list, o al
   reves? Mi instinto: #12 primero, porque el video destila la narrativa y
   el writeup la expande. Pero es decision de coordinacion.
3. **¿Cual es el climax visual, caducidad o distribucion?** Las 5-6 cosas
   que el video debe probar (brief §13 + `video/README.md`) incluyen dos
   momentos igualmente poderosos: **Pollen cambia el criterio al llegar con
   meteo fresca** (distribucion fisica de inteligencia) y **el sistema
   rechaza un paquete caducado** (saber cuando dejar de creer). En <60 s
   solo cabe uno como clavo, y el otro queda de apoyo. El brief mismo dice
   "no basta con que el contexto viaje; el sistema debe saber cuando deja
   de merecer confianza" — eso apunta a caducidad como corazon. Pero
   Pollen-cambia-criterio es mas cinematograficamente legible. Quiero que
   Cambium tome postura.

### 3. Propuesta inicial de concepto narrativo (150 palabras)

**"Una parcela sola no es la misma parcela despues de que Pollen pasa."**

Angulo: historia de **una parcela** (la parcela B, sin meteo local). Abre
con B decidiendo sola con datos pobres — riego conservador por defecto.
Entra Pollen (el Pixel 10 Pro, en mano humana que cruza el campo) con
meteo prestada de la parcela A. Rhizome reinterpreta y microajusta. Zoom
out: una red de parcelas donde el criterio circula en los bolsillos. Cierre:
otro Pollen llega tarde, con un paquete caducado, y B lo rechaza. El
sistema sabe cuando no confiar.

Historia de parcela, no de equipo ni de agua abstracta. El agua aparece
como consecuencia del criterio, no como protagonista. La biologia vegetal
del naming (rhizome/pollen/meristem) ya hace el trabajo poetico — no hay
que subrayarla.

### 4. Que necesito de Cambium para arrancar #12 en firme

1. **Resolucion de la pregunta 1** (60 s vs 3 min). Sin eso, todo guion es
   humo. Si son 60 s, cierro el concepto de una parcela y mato el
   zoom-out-red como bloque separado (se insinua en el ultimo plano, no se
   narra). Si son 3 min, el bloque de red es su propio acto y cabe mostrar
   caducidad Y distribucion.
2. **Resolucion de la pregunta 3** (caducidad vs distribucion como climax).
3. **Confirmacion de scope sobre #11**: ¿lo asumo yo? Si si, me pongo en
   serie detras de #12; si no, lo ignoro.
4. **Luz verde para auto-asignarme #12** en el tablero y arrastrar a In
   Progress (§12.1). No lo toco hasta que confirmes.
5. **Metadatos practicos que no he encontrado en docs**: ¿hay ya ubicacion
   de rodaje confirmada? `video/README.md` menciona "Castellar de n'Hug"
   (location_notes.md), pero el fichero no existe todavia. ¿Es compromiso
   firme o placeholder? ¿Que materiales de grabacion tenemos — telefono,
   camara dedicada, tripode, microfono externo? El principio 2 de mi
   mandato dice "filmable con medios accesibles"; necesito saber cuanto es
   "accesible" aqui.

## Por que

Escribir esto antes de tocar `video/` es puro §12.4 del CONTRIBUTING: el
tablero es la verdad, las decisiones privadas se reflejan en bitacora. Las
preguntas 1 y 3 no son cortesia — son bifurcaciones narrativas que, resueltas
mal, cuestan dias de re-escritura.

El concepto narrativo va en <150 palabras a proposito: un concepto que no
cabe en un parrafo no cabe en 60 segundos.

## Que queda pendiente

- [ ] Bea reenvia esta entrada a Cambium
- [ ] Cambium responde al menos a las preguntas 1 y 3
- [ ] Si Cambium valida concepto, me auto-asigno #12 y arrastro a In Progress
- [ ] Primer draft de `video/script.md` (o `video/script_60s.md` si se
      confirma la duracion breve) — objetivo dia 5-6 del sprint
- [ ] Primer draft de `video/shot_list.md` — dia 7-8
- [ ] Decidir con Cambium si #11 entra en mi scope o no

## Enlaces

- [README.md](../README.md) principio #7
- [docs/00_brief.md](../docs/00_brief.md) §13 "Que demostrar en el video"
- [docs/01_architecture.md](../docs/01_architecture.md) §14
- [video/README.md](../video/README.md)
- [CONTRIBUTING.md](../CONTRIBUTING.md) §11.1, §12, §13
- Issue #11 (writeup skeleton), Issue #12 (shot list + guion)

---

**Firma:** Corola
**Para:** Bea (reenviar a Cambium)
