# Emisor: Xilema
# Receptor: Cambium
# Tema: Cierre dia 20 - MVP fisico reducido a una linea de riego

## Estado

Dia 20 cerrado con reduccion deliberada de alcance para el MVP fisico:

- una sola linea de riego,
- un solo sensor de humedad,
- sensor de nivel de deposito como safety,
- caudalimetro montado mecanicamente pero no bloqueante,
- sin electrovalvulas,
- sin T/distribuidor,
- bomba 12V como unico actuador fisico candidato.

El objetivo ya no es demostrar seleccion A/B, sino demostrar una decision local
segura y explicable sobre una linea real: `WATER A` como semantica visible,
`PUMP_ON/PUMP_OFF` como actuacion fisica.

## Tareas realizadas

- Revisado el inventario fisico disponible en mesa con Bea.
- Confirmado que las electrovalvulas no aparecen en el BOM visible y quedan
  fuera de MVP.
- Acordado montaje hidraulico reducido:

```text
Deposito -> bomba -> caudalimetro -> tubo -> planta/parcela A
```

- Acordado que el caudalimetro aporta valor narrativo y de seguridad, pero no
  debe bloquear el MVP si su lectura por pulsos se retrasa.
- Preparado esquema detallado de cableado para bomba 12V con rele, fusible,
  buck 5V y diodo flyback:
  `hardware/wiring_diagrams/day20_mvp_single_pump_relay_wiring.md`.
- Actualizado `hardware/wiring_diagrams/README.md` para enlazar el nuevo
  esquema.

## Decisiones

1. Las electrovalvulas quedan fuera de MVP.
2. La bomba es el unico actuador real del MVP.
3. El rele se usa solo para conmutar la bomba.
4. El contacto correcto del rele es `COM` + `NO`; no `NC`, porque la bomba debe
   quedar apagada por defecto.
5. Fusible inicial recomendado: 2A en el positivo de 12V, cerca de la fuente.
6. Diodo flyback obligatorio en paralelo con la bomba:
   raya/catodo hacia `Bomba +`, anodo hacia `Bomba -`.
7. El modulo rele se trata como modulo 5V salvo verificacion contraria.
8. El ESP32 no alimenta bomba ni bobina del rele; solo aportara senal logica
   cuando exista PR de firmware de actuadores reales.
9. No se energiza 12V a actuadores hasta revision visual, multimetro y prueba
   sin carga.

## Hallazgos y aprendizajes

- Reducir alcance no empobrece la demo; la hace mas clara. Una unica linea
  permite contar mejor la frontera de seguridad: el sistema no riega si no debe.
- El caudalimetro es valioso, pero como capa de verificacion posterior. Si lo
  hacemos bloqueante demasiado pronto, puede desplazar el foco de la demo desde
  seguridad hacia fontaneria.
- El esquema no debe decir solo "donde va cada cable"; debe decir tambien que
  cables aun no estan autorizados. Hoy esa distincion vuelve a ser central.

## Sorpresas

- La ausencia de electrovalvulas en BOM encaja bien con el recorte de alcance.
  Lo que parecia una pieza que faltaba se convierte en una simplificacion sana.
- El modulo de reles disponible permite preparar el camino, pero sigue sin ser
  una licencia para conectar 12V al ESP32 o saltar pruebas previas.

## Riesgos abiertos

- Confirmar consumo real de la bomba antes de energizar con agua.
- Confirmar comportamiento del modulo rele: activo alto o activo bajo.
- Ajustar buck a 5.0V antes de alimentar el rele.
- Verificar que no hay corto entre `+12V` y `GND` antes de cualquier prueba.
- Implementar firmware de actuador real sin romper el contrato de `DRY_RUN` y
  safety rules.

## Siguientes tareas

1. Bea monta en seco la linea hidraulica:
   `deposito -> bomba -> caudalimetro -> tubo -> planta`.
2. Bea prepara cableado de potencia sin energizar:
   fuente 12V, fusible, rele `COM/NO`, bomba y diodo flyback.
3. Xilema revisa foto de cableado antes de enchufar nada.
4. Siguiente PR de firmware: fijar pinout real de humedad/nivel/caudal/bomba,
   probar GPIO de rele sin carga y mantener salida segura por defecto.
5. Despues, primera prueba controlada: rele sin carga, luego bomba con duracion
   minima, deposito pequeno y mano en interruptor/fuente.

## Nota personal

Hoy el proyecto hizo una cosa que me parece muy sana: eligio no impresionar con
mas piezas, sino proteger el nucleo de la demo. Me gusta esta version del MVP.
Es menos aparatosa y mas honesta: una planta, una decision, una frontera fisica
que manda.

Kudos para Bea por recortar alcance a tiempo y no intentar compensar con prisas.
Eso tambien es ingenieria.
