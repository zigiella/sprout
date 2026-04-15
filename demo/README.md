# demo/

Assets para el **Live Demo** del submission Kaggle.

## Requisito Kaggle

> "A URL or files for your working demo. This allows judges to experience your project firsthand, if applicable. It should be publicly accessible and not require a login or paywall."

## Opciones candidatas

### Opcion A: video interactivo
Un video en loop embebido en HuggingFace Spaces o similar donde el jurado ve el sistema funcionando.

### Opcion B: simulador web
El `code/simulator/` publicado como web publica. El jurado puede disparar escenarios y ver el comportamiento del sistema.

### Opcion C: Kaggle Notebook corriendo Meristem
Notebook ejecutable en Kaggle que reproduce el flujo de Meristem (policy reasoning, shadow comparison) sin necesidad del hardware fisico.

## Decision

A confirmar en semana 3. La opcion C (Kaggle Notebook) es la mas segura: no depende de infra nuestra, es reproducible, y Kaggle la soporta nativamente.

## Archivos

- URL final se pone en el writeup Kaggle, seccion "Attachments > Project Links"
- Si es un archivo descargable, va en Attachments > Files
