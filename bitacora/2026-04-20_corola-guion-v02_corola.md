# Guion v0.2 — ajuste narrativo sobre verbos de movilidad

**Fecha:** 2026-04-20
**Autora:** Corola
**Area:** Video / narrativa
**Tipo:** Ajuste sobre PR #41 en curso (hermano del ajuste shot list v0.2 en PR #40)

---

## Origen

Mismo origen que el ajuste del shot list (PR #40, v0.2): releyendo un borrador de mail al padre de Bea — fuera de scope proyecto — Bea identifico que los verbos **"caminar"** y **"a pie"** encadenan la tesis de Pollen a un solo modo de movilidad. Racional completo en `bitacora/2026-04-20_corola-shot-list-v02_corola.md`.

Resumen de la decision (copiada para que este rationale funcione standalone):

1. Tesis Pollen en el video: **humana** (agricultor con movil entre parcelas).
2. Arquitectura Pollen: **agnostica al portador** (persona andando/en bici/en camioneta/en tractor, o dron agricola). Hecho tecnico, no se cuenta en el video pero si en writeup / Q&A.
3. Lexico del video: **verbo neutro** ("se mueve", "en ruta", "recorre", "quien se mueve"). La imagen en pantalla es humana; el lenguaje no cierra contra otros modos.

## Cambios en v0.2 del guion

| Bloque | v0 | v0.2 | Delta |
|---|---|---|---|
| 0:18-0:25 (Pollen entra) | "Alguien ya camina esta ruta." | "Alguien ya recorre esta ruta." | mismo numero palabras (5), verbo neutro |
| 0:35-0:50 (CLIMAX) | "En el camino de A a B, el criterio se ajusta..." | "En ruta de A a B, el criterio se ajusta..." | 22 → 20 palabras |
| 2:30-2:50 (CIERRE cartela) | "Sprout: criterio que viaja a pie." | "Sprout: criterio que viaja con quien se mueve." | cartela, no VO |
| Principio #7 (cierre) | cita antigua | cita nueva + nota explicita: verbo neutro protege agnostia-portador | documentacion |

**Total VO: 103 palabras** (antes 105, -2 por acortar climax).

## Por que me convence

- **VO 0:18-0:25 "recorre"** es mas limpio que "camina" y no presupone pie. Encaja con la imagen de humano con movil caminando en el plano (lo que se ve) pero no excluye otros modos si mañana esa imagen se amplia.
- **VO climax "En ruta"** es mas conciso y mas fuerte. "En el camino" sonaba literal; "en ruta" suena a trayecto intencional con propósito. Y me ahorra 2 palabras en el bloque mas denso del video — beneficio lateral.
- **Cartela cierre "criterio que viaja con quien se mueve"** es la frase tesis en su forma definitiva. "Quien" es gramaticalmente humano en castellano pero no encadena. La tripleta final gana: FAO (escala) → IRRIFRAME (contraste: centralizado) → Sprout (alternativa: criterio distribuido con el que se mueve). La oposicion con IRRIFRAME es ahora mas nitida.

## Linea 2:10-2:30 "despierta con el criterio" — no cambia

Mantengo el voto estilistico. "Despierta" no tiene el problema de "caminar": no encadena a un modo de transporte, solo a una metafora de ciclo dia/noche — que es exactamente lo que ese plano cuenta (Meristem diferido aterrizando al amanecer). Confirmado.

## Impacto en otros documentos

- **shot_list.md v0.2** (PR #40): ajustes paralelos. Cambios de descripcion de planos + cartela + nota en Notas de grabacion. Ver `bitacora/2026-04-20_corola-shot-list-v02_corola.md`.
- **Writeup:** Cambium recoge la arquitectura agnostica al portador de Pollen como hecho tecnico para seccion 1. Nota explicita en el bitacora del shot list v0.2 para que la recupere al redactar.
- **README / docs/01_architecture.md:** no toco en este PR. Si al hacer el PR de docs futuro (reframe Pollen) aparece lexico "a pie" o "caminar", se ajusta entonces.

## Enlaces

- PR #41 (guion v0)
- PR #40 (shot list, commit paralelo v0.2)
- `bitacora/2026-04-20_corola-shot-list-v02_corola.md` (racional compartido sobre agnostia-portador)
- `bitacora/2026-04-18_reframe-narrativo-pollen_cambium.md`
- Conversacion Bea↔Corola 2026-04-20
