# Pollen — especificación v2

## 1. Rol

Pollen es el nodo itinerante Android con Gemma 4 E4B.

Responde a esta pregunta:

> **¿Qué criterio humano y qué contexto nuevo merecen entrar en el gobierno local de esta parcela?**

## 2. Por qué es esencial

Pollen no es opcional en la historia del producto.

Es la pieza que:

- compila intención humana,
- valida visitas,
- federa parcelas desconectadas,
- y hace a Rhizome explicable sin poner pantalla en la parcela.

## 3. Responsabilidades

### 3.1 Compilador de misión
Convierte voz o texto en estructura ejecutable.

Ejemplo:
> “Vuelvo en 72 horas. Prioriza parcela A. Presupuesto máximo 1 litro.”

Salida:
- `MissionPatch`

### 3.2 Auditor itinerante
Habla con Rhizome, revisa receipts, escucha a la persona y emite:
- `ValidationStamp`
- `VisitAmendment` si procede

### 3.3 Federador de parcelas
Transporta contexto útil:
- `WeatherDigest`
- prioridad temporal
- bundles pendientes
- políticas de retorno

### 3.4 Interfaz conversacional de Rhizome
Permite que la persona pregunte:
- “¿Por qué no regaste ayer?”
- “¿Qué cambió desde mi última visita?”
- “¿Qué parcela te preocupa más?”

Pollen traduce la pregunta a consulta estructurada y vuelve a traducir receipts a lenguaje natural.

## 4. Qué no hace

- no ejecuta actuadores,
- no salta la seguridad del ESP32,
- no emite políticas de largo plazo,
- no sustituye a Meristem.

## 5. Conectividad

Pollen debe funcionar en tres modos:

- **modo visita local**: habla con Rhizome por Wi‑Fi local / hotspot / LAN directa
- **modo tránsito**: guarda bundles offline
- **modo consolidación**: cuando hay oportunidad, sincroniza con Meristem

## 6. Entradas

- voz y texto humanos,
- preguntas del agricultor,
- snapshot y receipts de Rhizome,
- bundles pendientes,
- meteo local de una parcela,
- foto opcional de visita,
- reloj y geolocalización opcional del móvil.

## 7. Salidas

- `MissionPatch`
- `ValidationStamp`
- `WeatherDigest`
- `VisitAmendment`
- `FieldVisit`
- `SyncBundle` hacia Meristem

## 8. Gemma 4 en Android

**Decision pendiente (dia 10): E4B vs A4B como modelo objetivo de Pollen.**

- **E4B** era la eleccion inicial del pivote v2 por coherencia edge-mobile.
- **A4B** (26B MoE, 3.8B activos, 256K contexto) esta validado empiricamente en Pixel 10 Pro via AI Edge Gallery (corre enteramente sobre LiteRT-LM offline). Mas capacidad de razonamiento, mas memoria de contexto.
- Guia tecnica comparativa y plan de implementacion en `docs/50_pollen_gemma4_a4b_guide.md`.

La spec del resto de este documento se mantiene agnostica al modelo concreto hasta que se cierre la decision.

Gemma se usa para cuatro tareas esenciales:

### 8.1 NLU y compilación
Lenguaje natural → JSON validado

### 8.2 Explicación
Receipts y estado → respuesta legible y breve

### 8.3 Auditoría
Señales de Rhizome + visita → confirmar / disputar / pedir prudencia

### 8.4 Compresión de contexto
Muchos eventos → digest pequeño y transportable

## 9. Visión y audio

### Obligatorio
- voz o texto

### Opcional para el MVP
- foto de visita
- una sola escena visual de validación

La cámara no forma parte de la ruta crítica.

## 10. Capa de datos de Pollen

### SQLite o Room
- `pending_uploads`
- `downloaded_bundles`
- `field_visits`
- `mission_patches`
- `validation_stamps`
- `weather_digests`
- `visit_amendments`
- `conversation_cache`
- `sync_sessions`

## 11. UX mínima

Pantallas mínimas:

1. **Visitar Rhizome**
   - conectar
   - ver resumen corto
   - preguntar “qué pasó”

2. **Dar nueva misión**
   - grabar voz o escribir
   - ver JSON validado
   - enviar

3. **Transportar contexto**
   - ver qué bundles lleva
   - entregar o retener

4. **Historial corto**
   - últimas visitas
   - últimas decisiones

## 12. Definición de hecho

Pollen está listo cuando puede:

1. conectarse a Rhizome sin internet,
2. descargar snapshot y receipts,
3. convertir voz en `MissionPatch`,
4. generar una explicación legible de una decisión pasada,
5. transportar un `WeatherDigest` de A a B,
6. emitir un `ValidationStamp`,
7. cerrar una visita con un `FieldVisit`.
