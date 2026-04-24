# Bitácora F0: Inventario de Modelo Gemma 4 E4B (Pollen)

**Fecha:** 2026-04-24
**Autor:** Floema
**Fase:** F0 — Captura

## 1. Identificación del Modelo

Siguiendo la guía operativa `50_pollen_gemma4_e4b_guide.md` y el requisito de baseline estricto para Pollen, queda documentado el artefacto validado que utilizaremos a partir de ahora:

- **Nombre original:** `gemma-4-E4B-it.litertlm` (no se alterará su nombre)
- **Tamaño exacto:** `3,654,467,584 bytes` (aprox. 3.41 GB)
- **Hash SHA-256:** `F335F2BFD1B758DC6476DB16C0F41854BD6237E2658D604CBE566BCEFD00A7BC`
- **Formato:** `.litertlm` (nativo para Google LiteRT-LM)

## 2. Contexto Operativo

- **Origen:** Descargado de Hugging Face por Bea y probado empíricamente en AI Edge Gallery.
- **Ruta PC (Entorno de desarrollo):** `C:\DATA\PETS\TEST\T6A2-POLLEN\models\gemma-4-E4B-it.litertlm` (Ubicado fuera del repositorio principal para evitar inflar el historial de Git).
- **Backend objetivo (F1):** **CPU**. (Se descarta GPU inicialmente por los bugs conocidos de drivers en Tensor G5 / Android 16 documentados en la guía v2. GPU queda tras feature flag futuro).
- **Fecha de validación:** 2026-04-24.

## 3. Estado de la Arquitectura

Con este inventario aseguramos que no habrá mutaciones fantasmas del archivo en las futuras integraciones. El SHA-256 es nuestra garantía. 

La rama activa es `feat/pollen-f0-capture`. La fase F0 se da por completada. Siguiente objetivo: **F1 — Chat texto**, donde inyectaremos este modelo exacto en el móvil para lograr carga estable y conversación en streaming.
