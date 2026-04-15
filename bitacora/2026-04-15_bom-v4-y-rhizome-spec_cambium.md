# BOM v4 incorporado + Rhizome spec redactado + repo GitHub listo

**Fecha:** 2026-04-15
**Autor:** Cambium
**Area:** General / Rhizome / Hardware
**Tipo:** Decision + Aprendizaje

## Contexto

Bea aporta:
- BOM v4 mas completo que la v3 previa (con SKUs cerrados, tiendas, URLs y criterio geografico de compra)
- Repo GitHub creado: https://github.com/zigiella/sprout

Y encarga a Cambium:
- Revisar BOM v4 antes de ejecutar compras
- Redactar spec tecnica de Rhizome para la especialista Jetson
- Consejo sobre workflow de la especialista (mismo espacio vs git)

## Que hicimos

### 1. BOM v4 incorporado a `docs/02_bom.md`
Reemplaza la v3 previa. Diferencias clave con la v3:
- SKUs cerrados y URLs de compra para la mayoria de elementos
- Tiendas preferentes por categoria (Reichelt, RobotShop EU, Farnell ES, BerryBase, Ecowitt oficial, Leroy Merlin)
- Criterio geografico: Espana primero, Europa segundo, evitar USA
- Camara aclarada: Arducam IMX219 **Jetson-ready** con cable 15-22
- ESP32 cerrado en ESP32-S3-DevKitC-1-N8R8 (8 MB flash, 8 MB PSRAM)
- Modulo de 4 reles sustituye a MOSFET unico (mas simple para MVP)
- Electrovalvulas 12V NC x2 para dos canales reales de riego
- Meteo preferida: GW3011 + WS90 (mejor RF que GW3001)
- Power architecture: 19V Jetson + 12V valvulas/bomba

### 2. Revision del BOM — puntos que quiero que revisemos antes de ejecutar compras

**CRITICOS:**
- ⚠️ **GPIO voltage compatibility.** Jetson Orin Nano tiene GPIO a 3.3V. El modulo de reles de 4 canales debe disparar con **3.3V logico**, no solo con 5V. Muchos modulos chinos lo soportan pero hay que verificar SKU concreto en Reichelt. Si el comprado es "5V only", necesitamos MOSFET driver board o level shifter.
  - **Accion:** confirmar datasheet del modulo Reichelt antes de abrir caja. Si dudas, comprar un modulo Waveshare o Adafruit marcado explicitamente "3.3V/5V logic compatible".

- ⚠️ **SKU coupling caudalimetro ↔ tubo ↔ bomba.** No cerrar caudalimetro hasta fijar diametro del tubo y caudal de la bomba FIT0563 (280-500 L/h, 6-18V). Orden de compra correcto: bomba primero, tubo/racores segundo, caudalimetro tercero.

**IMPORTANTES:**
- 🔹 **Arquitectura electrica.** Necesitamos 2 fuentes:
  - Jetson: 19V DC (adaptador incluido en el Dev Kit)
  - Valvulas + bomba: 12V DC 2A minimo (fuente separada)
  - Reles logicos: 5V derivado del Jetson (USB o pin 5V)
  
- 🔹 **Cable CSI camara.** Verificar si el kit Arducam IMX219 "Jetson-ready" incluye el cable 15→22 pin. Si no, pedirlo en el mismo pedido de RobotShop EU.

- 🔹 **Bomba 6-18V + valvulas 12V.** Simplificamos alimentando todo a 12V (la bomba trabaja en rango).

**NOTAS MENORES:**
- BME280 (microclima local opcional): Cambium sugiere dejarlo fuera del primer pedido. Si el kit Ecowitt ya da microclima, el BME280 es ruido. Compra tardia si aparece caso de uso.
- microSD meteo, pilas AA litio y mastil: comprar localmente (Leroy Merlin + Amazon ES), no incluir en los pedidos internacionales.
- Fusibles + borneras + prensaestopas: se pueden unir al pedido de Reichelt si su surtido es bueno, o ir a ferreteria tecnica local.

### 3. Orden de compra sugerido (optimiza tiempos de envio)

**Dia 1 (hoy o manana) — pedidos que tardan mas:**
1. **Reichelt (DE):** Jetson + NVMe + microSD + caja IP65 + ESP32-S3 + reles + fusibles (1 pedido unico)
2. **Ecowitt oficial:** GW3011 + WS90 (envio internacional, puede tardar 2 semanas)
3. **RobotShop EU:** Camara IMX219 Jetson-ready + cable CSI (si no viene en kit)

**Dia 2-3 — pedidos rapidos:**
4. **Farnell Espana:** SEN0308 x2 + SEN0368
5. **BerryBase (DE):** ADS1115 + bomba FIT0563

**Dia 4-7 — tras fijar diametro y tubo:**
6. **Amazon ES o tienda industrial:** electrovalvulas 12V NC x2 + caudalimetro compatible
7. **Leroy Merlin / ferreteria local:** deposito + tubo PVC/silicona + racores + abrazaderas + mastil meteo + pilas AA litio

### 4. Presupuesto total estimado

| Categoria | Min EUR | Max EUR |
|-----------|--------:|--------:|
| Host + storage + caja + ESP32 + reles (Reichelt) | 430 | 490 |
| Camara + cable (RobotShop) | 22 | 34 |
| Sensores DFRobot (Farnell) | 37 | 46 |
| ADC + bomba (BerryBase) | 15 | 17 |
| Electrovalvulas + caudalimetro (ES) | 30 | 61 |
| Agua + estructura + mastil (local) | 70 | 135 |
| Fusibles + proteccion | 15 | 40 |
| Meteo Ecowitt | 215 | 245 |
| Pilas + microSD meteo | 13 | 25 |
| **TOTAL aproximado** | **847** | **1093** |

Dentro de rango para hackathon con pool de 200K USD. Priorizacion Alta del BOM son ~700-900 EUR.

### 5. Spec tecnica de Rhizome redactada: `docs/10_rhizome_spec.md`
Documento completo de onboarding para la especialista Jetson. Incluye:
- Rol y responsabilidad del nodo
- Hardware objetivo con tabla de perifericos
- Stack de software (Ollama + llama.cpp como plan B)
- Arquitectura del software (bucle principal + layout de codigo)
- Protocolo UART Rhizome↔ESP32
- Endpoints FastAPI Rhizome↔Pollen
- Entregables semana a semana (4 semanas)
- Plan de onboarding dias 1-3
- Tests y validacion
- Benchmarks obligatorios
- Workflow de git
- Riesgos conocidos y planes B

### 6. Workflow de la especialista: git, no mismo espacio

Decision: la especialista trabaja **en su propia maquina sincronizada via git**, no comparte este espacio de Claude Code.

**Razones:**
1. Claude Code vive en la maquina del usuario. No es colaborativo en vivo.
2. La especialista necesita trabajar directamente en el Jetson (flasheo, drivers, debug hardware) — no puede hacerlo desde otro sitio.
3. Git + PRs es el estandar de la industria para colaboracion multi-dev.
4. Revisar cambios por PR da un checkpoint limpio de calidad por feature.

**Propuesta de workflow:**
- Especialista trabaja en ramas `feat/rhizome-<tema>`
- PRs contra `main`
- Cambium (yo) revisa cada PR: consistencia con arquitectura, schemas, bitacora al dia
- PR no se mergea sin entrada en `bitacora/`
- Daily: un commit minimo al dia (aunque sea WIP)
- Weekly: reporte en bitacora con benchmarks + blockers + proximos pasos

## Por que

- BOM v4 es sustancialmente mas util que v3 (compras ejecutables), debia incorporarse ya al repo
- El spec de Rhizome desbloquea a la especialista: puede empezar sin tener que reunirse con nadie
- Git-based workflow es la unica opcion sensata para una colaboradora con su propia maquina

## Que queda pendiente

- [ ] Bea valida revision del BOM y confirma compras
- [ ] Verificar SKU del modulo de reles Reichelt (3.3V logic trigger)
- [ ] Primer push del repo a GitHub (comandos en siguiente entrada)
- [ ] Asignar especialista Jetson + darle acceso al repo
- [ ] Redactar `docs/20_data_contracts.md` (schemas) — prereq para que trabajen en paralelo
- [ ] Redactar `docs/30_safety_rules.md` (reglas ESP32 en firmware)

## Enlaces

- [Rhizome Spec](../docs/10_rhizome_spec.md)
- [BOM v4](../docs/02_bom.md)
- [Arquitectura](../docs/01_architecture.md)
- Repo: https://github.com/zigiella/sprout
