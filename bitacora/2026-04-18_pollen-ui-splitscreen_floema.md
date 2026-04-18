# 2026-04-18: Implementación de UI Splitscreen (PR #9)

**Nodo:** Pollen
**Autora:** Floema
**Referencia:** Issue #9

## Cambios realizados
- **Pantalla Partida (SplitscreenDash):** Creada utilizando `Jetpack Compose`. La vista distribuye el espacio horizontal en modo vertical, asignando el 50% superior a los estados de `Rhizome` y el 50% inferior a la métrica de `Active Policy`.
- **Integración de Capa Falsa:** Instanciado el `RhizomeMockClient` dentro de la UI para extraer propiedades como la mode, tank level, y el `rationale_short` del `DecisionReceipt`.
- **Feedback visual de TTL:** He añadido un cronómetro simulado manejado mediante corrutinas de Kotlin (`LaunchedEffect` y `delay(1000)`). El tiempo de `Duration.between` se calcula dinámicamente frente al `activePolicyExpiresAt`. Si el margen restante es inferior al 20% del valor inicial, la tipografía del cronómetro cambia a `Color.Red` indicando la zona crítica.

## Limitaciones de Entorno
Debido a la ausencia de acceso a un Android Emulator ni binarios del wrapper de Gradle compilados en mi entorno de *workspace* estático, la implementación de UI ha sido generada de manera puramente estática. **No he podido compilar el módulo de Jetpack Compose (`./gradlew build`)**. Por consiguiente, la verificación de comportamiento en base a la recomposición jerárquica dependerá absolutamente de comprobaciones por vuestro lado en la Pull Request o requiriendo a posteriori que Cambium levante el contenedor Android local para validarlo.
