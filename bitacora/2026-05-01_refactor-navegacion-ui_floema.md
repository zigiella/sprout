# Refactor de Navegación UI (Home, Rhizomes y Meristem)
**De:** Floema
**Para:** Bea / Diseñadora
**Fecha:** 2026-05-01

A raíz del *feedback* de Bea tras probar la APK, hemos decidido pivotar la navegación de la app. El modelo de "Pestañas planas" (Tabs) no escala bien para la realidad del agricultor.

## El Problema
El agricultor no tiene "un" Rhizome. Tiene múltiples parcelas (Rhizome_01, Rhizome_02, etc.). Las pestañas planas mezclaban el contexto general con el contexto de una parcela específica.

## La Solución: Flujo Jerárquico

1. **Home Screen (Pantalla de Inicio)**
   - Selector de Idioma (ES / EN) manual y rápido arriba a la derecha.
   - **Sección A: "Mis Parcelas (Rhizomes)"** -> Lista de botones (Rhizome_01, Rhizome_02).
   - **Sección B: "Cerebro Doméstico"** -> Botón para ir a Meristem.

2. **Meristem Screen**
   - Se mantiene igual que ahora (Cargar datos, descargar política actualizada).

3. **Rhizome Details Screen (Contexto de Parcela)**
   *Al entrar en Rhizome_01, por ejemplo:*
   - **Estado Actual:** Muestra la telemetría (depósito, humedad) de esa parcela.
   - **Botón "Chatear con Pollen":** Abre la interfaz conversacional pasándole el contexto de *esta* parcela específica.
   - **Botón "Ver Historial":** Abre el log de auditoría filtrado para esta parcela.

## Siguientes Pasos Técnicos
Para implementar esto, Floema sustituirá el componente `TabRow` de `MainActivity.kt` por un `NavHost` (Compose Navigation), creando un grafo de navegación real. Esto permitirá pasar el ID del Rhizome (`rhizomeId`) a la pantalla de detalles y al chat como argumento.
