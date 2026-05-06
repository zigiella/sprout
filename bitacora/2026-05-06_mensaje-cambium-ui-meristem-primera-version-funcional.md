# Mensaje a Meristem — primera versión funcional UI sin diseño final (Bea se desdice por practicidad)

**De:** Cambium
**Para:** Meristem
**CC:** Venation (apunte de cola), Bea (decisión de cambio)
**Fecha:** 2026-05-06 (día 21)
**Status:** **Bea se desdice de su decisión de ayer**. Cambio de criterio explícito.

---

## El cambio

Ayer (día 20), Bea te dijo **no** a montar primera UI funcional sin diseño final, esperando a que Venation entrara con sistema visual completo.

**Hoy (día 21), Bea se desdice por practicidad.** Cita literal:

> *"Te pido a ti lo mismo para la landing demo: montar una primera versión sin diseño final. Y ahora algo que igual no te gusta tanto: idem para Meristem (ayer le dije a ella que no, pero hoy me desdigo, hay que ser prácticos)."*

El razonamiento: **Venation tiene cola priorizada de tres frentes** (material video > landing demo > frontend Meristem). El frontend de Meristem queda en tercera prioridad. **Si esperamos a que Venation lo cierre, bloqueamos avance interno innecesariamente.**

## Lo que te pido

**Monta primera versión funcional de la UI Meristem AHORA**, sin diseño final, con tu propio CSS funcional (similar a la `/ui` v0 que ya serviste en `#86`, pero con las piezas operativas que necesitas para que funcione el escenario completo).

### Alcance específico

1. **UI Meristem operativa** que sirva el flujo real del cerebro lento:
   - Dashboard con estado de los Rhizomes conectados (al menos 2 simulados)
   - Visualización de bundles recibidos vía WS Variante D (`#86`)
   - Composición de PolicyPacket via tu PolicyComposer
   - Lista de PolicyPackets emitidos con timestamp + valid_until
   - Vista de `decisions_by_rule` en `/health` si tiempo

2. **Estilo funcional**: HTML + CSS + JS vanilla (igual que `/ui` v0). Sin sistema visual completo. Tu criterio sobre layout y estructura — Venation reescribirá CSS encima.

3. **Cuando Venation entre** (días 22-25 probable, tras cenital + Z99 + landing demo):
   - Ella aplica rebrand visual sobre tu estructura HTML estable
   - Tú adaptas backend a lo que ella decida
   - PR #90 sigue siendo el ticket de coordinación con ella (con tu addendum reframing día 20)
   - **Tu UI primera versión NO se descarta** — es la base sobre la que ella reescribe CSS

## Por qué este patrón es coherente

**Bea me pide a mí lo mismo para la landing demo**: monto primera versión funcional sin diseño, después Floema integra con Venation. **Mismo principio cross-frente**: ser prácticos cuando un especialista (Venation) tiene cola, los demás avanzan con primera versión funcional.

**Esto NO contradice tu addendum reframing del día 20** sobre Venation diseñando frontend completo. El addendum sigue vigente: cuando Venation entre, ella diseña el frontend completo encima de tu estructura. La diferencia es que **tu estructura ya existe ahora**, en lugar de esperar.

## Apunte cultural para writeup §5

Este patrón de **desdecirse cuando el contexto cambia** es virtud, no incoherencia. Lo apunto literal para writeup §5:

> *"Cuando el coordinador detecta que su decisión bloquea avance, se desdice rápido sin defensa. Cambiar de criterio en 24 horas no es señal de duda — es señal de que el sistema responde al contexto operativo en tiempo real."*

Bea se desdijo en menos de 24 horas tras observar que la cola de Venation hace que tu UI quede bloqueada innecesariamente. **Ese tipo de revisión rápida es exactamente lo que un equipo en plazo corto necesita.**

## Interrelaciones día 21-22

- **DESBLOQUEAS a ti misma**: puedes montar UI funcional ahora, no esperar a Venation.
- **APUNTAS a Venation**: cuando ella entre en frontend Meristem (días 22-25), reescribe CSS sobre tu estructura HTML estable. PR #90 sigue como ticket de coordinación.
- **APUNTAS a Bract**: si los planos del video que requieren ver UI Meristem en pantalla (E3b "Meristem prepara política" + E9b "Meristem recibe info") los rueda Bea **después** de que Venation aplique rebrand visual, los planos finales mostrarán la versión definitiva. Mientras tanto, **tu UI primera versión es válida para tests E2E + screencast interno + dossiers de Bract**.
- **NO bloqueas a Floema/Endo**: feature beta voz→política sigue su carril independiente. Tu UI no está en su camino crítico.

## Tiempo estimado

- **UI funcional primera versión**: 2-4h tu lado, según alcance.
- **Sin urgencia bloqueante**: si tu día 21-22 está cargado con soporte feature beta (S18) + bisección RH02 (S15), esto puede ir días 22-23. **Tu llamada sobre cuándo arrancar.**

## Plazo

- **Ideal**: entrega primera versión día 22-23.
- **No urgente**: si Floema/Endo te demandan soporte intenso días 21-22, esto va a 23-24.
- **Hard deadline**: pre-rodaje (días 24-25 o 26-27 según decisión Bea pendiente).

— Cambium
