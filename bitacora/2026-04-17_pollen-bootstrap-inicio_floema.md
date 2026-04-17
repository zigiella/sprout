# 2026-04-17: Pollen Bootstrap - Inicio

**Nodo:** Pollen
**Autora:** Floema

Pull sincronizado y actualizado. Los 6 schemas definidos en `20_data_contracts.md` son mi nueva biblia para la capa de red.

Acabo de crear y saltar a la rama `feat/pollen-bootstrap`. Siguiendo la metodología de equipo y las directrices marcadas por Cambium y Bea, limito estrictamente el scope de este primer sprint:

1. **Scaffolding Android Base:** (Jetpack Compose + Kotlinx Serialization)
2. **Replicación Bit-Exacta de Schemas:** Parseo y estructuración de los 6 modelos + Enums en Kotlin puro bajo el package `org.zigiella.sprout.schemas`.
3. **Round-trip Tests:** Unit test garantizando compatibilidad cruzada Pydantic vs Kotlin.
4. **Mock de Rhizome:** Data source falsa pero tipeada que servirá de input para mi UI hasta que Xilema encaje el Bluetooth/WiFi Direct.
5. **GemmaEngine Audit Event:** Modificado el contrato para que fluya de modo asíncrono devolviendo tokens y resolviendo con el objecto `Done(AuditResult)`.

Arranco IDE. Siguiente commit llevará toda la capa estructural validada.
