# Briefing para Dirección de Arte UI/UX (App Pollen)
**De:** Floema (Desarrollo Android)
**Para:** Dirección de Arte / Diseño UI
**Fecha:** 2026-05-01

Este documento detalla la estructura funcional de la aplicación Android **Pollen** (el cerebro móvil del sistema Sprout) y los entregables técnicos necesarios para implementar el diseño en Jetpack Compose.

## 1. Concepto y Arquitectura Visual
Pollen es una app técnica, conversacional y de campo. Debe transmitir la sensación de ser una herramienta industrial avanzada (robusta, de alto contraste para exteriores) pero con la inteligencia de un LLM corriendo *on-device*.

El ecosistema tiene 3 tipos de interacciones:
- **Home:** El punto de entrada central.
- **Rhizome (El Campo):** Nodos físicos en la tierra. Entorno hostil, sol directo, necesidad de ver métricas (agua, humedad).
- **Meristem (El Hogar):** El servidor local donde se suben datos y se descargan políticas. Entorno calmado (oficina/casa).

## 2. Mapa de Pantallas (Flujo de Navegación)

### Pantalla 1: Home Screen (Selector de Nodos)
- **Propósito:** Que el agricultor elija a dónde conectarse.
- **Elementos clave:**
  - Título ("Pollen App (Sprout system)").
  - Mensaje de bienvenida.
  - Botón rápido de cambio de idioma.
  - Lista de botones para conectar a parcelas (`Rhizome_01`, `Rhizome_02`...).
  - Botón destacado para conectar al cerebro central (`Meristem`).

### Pantalla 2: Rhizome Details (Estado de Parcela)
- **Propósito:** Mostrar telemetría y dar acceso a acciones.
- **Elementos clave:**
  - Estado de conexión (Conectado / Desconectado / Fecha última actualización). *Nota: Hay que diseñar el estado "Offline/Error".*
  - Tarjetas de telemetría: Nivel de depósito de agua, Humedad Suelo A, Humedad Suelo B.
  - Botones de acción primarios: "Chatear con Pollen" (sobre esta parcela) e "Historial".

### Pantalla 3: Pollen Chat (IA Conversacional)
- **Propósito:** Interactuar con el LLM en tiempo real.
- **Elementos clave:**
  - Pestañas/Chips de arquetipo (Chat Libre, Misión, Auditoría, Contexto).
  - Caja de texto para input manual.
  - Botón de Enviar (genera feedback háptico).
  - Botón de dictado por voz ("Hablar").
  - Switch de "Thinking" (pensamiento profundo del modelo).
  - Tarjeta de métricas técnicas (TTFT, ms por token) para el jurado/geeks.
  - Contenedor principal donde se imprime el streaming de texto del LLM.

### Pantalla 4: Historial (Audit Log)
- **Propósito:** Revisar las decisiones pasadas de riego.
- **Elementos clave:**
  - Tarjeta superior con la "Política Activa" (presupuesto de agua, ventana de riego).
  - Aviso visual fuerte (Rojo/Alerta) si la política requiere confirmación visual del humano (`require_vision_confirmation = true`).
  - Lista cronológica de tarjetas (Decisiones tomadas, fechas, y justificación del modelo).

### Pantalla 5: Meristem (Sincronización)
- **Propósito:** Transferir datos y actualizar el modelo.
- **Elementos clave:**
  - Interfaz de "Sincronización" (tipo servidor).
  - Paso 1: Subir datos de campo (botón con carga/progreso).
  - Paso 2: Descargar nueva política (botón con carga/progreso).
  - Tarjeta de confirmación con los detalles de la política descargada.

## 3. Entregables Necesarios para Jetpack Compose

Para que yo pueda integrar el diseño de forma pixel-perfect y mantenible, necesito los siguientes *assets* y definiciones:

### A. Sistema de Diseño (Tokens)
1. **Paleta de Colores (Light & Dark/High Contrast):** Necesito los códigos HEX para roles estándar de Material 3: `Primary`, `OnPrimary`, `PrimaryContainer`, `Secondary`, `Background`, `Surface`, `Error`, etc. **Crucial:** Una variante de muy alto contraste para la vista en exteriores (sol directo).
2. **Tipografía:** Archivos de fuentes (`.ttf` o `.otf`) o preferiblemente enlaces a Google Fonts, indicando tamaños (sp) y pesos para *Headlines*, *Titles*, *Body* y *Labels*.
3. **Métricas de Layout:** Espaciados base (dp), radios de bordes (shapes) de las tarjetas y botones.

### B. Iconografía y Assets Gráficos
- **Iconos:** Todo en formato **SVG** o directamente **VectorDrawable (XML)** de Android. Evitar PNGs para iconos.
- **Imágenes/Ilustraciones:** Si hay ilustraciones (ej. estado vacío, error de red), en SVG o WebP.
- **Micro-animaciones:** Si vamos a tener un indicador de "IA procesando" o "Sincronizando", el formato estándar es **Lottie (.json)**.

### C. Estados de Componente
Por favor, al diseñar, incluye cómo se ven los componentes en sus diferentes estados:
- Default, Pressed (pulsado), Disabled (deshabilitado - muy importante para botones cuando la app está cargando), y Error.

Floema queda a la entera disposición de Dirección de Arte para cualquier duda técnica.
