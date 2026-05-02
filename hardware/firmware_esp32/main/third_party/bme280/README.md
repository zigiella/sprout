# BME280 vendor note

Driver vendorizado desde la fuente oficial de Bosch Sensortec:

- repo: `boschsensortec/BME280_SensorAPI`
- URL: `https://github.com/boschsensortec/BME280_SensorAPI`
- commit fijado: `c90d419492e26dd95586598a794e65eb2760753a`
- versión declarada en `bme280.h`: `v3.5.1`
- licencia: `BSD-3-Clause`
- fecha de lectura / vendor en este proyecto: `2026-04-27`

Ficheros incluidos:

- `bme280.c`
- `bme280.h`
- `bme280_defs.h`
- `LICENSE`

Los wrappers específicos de `Sprout` viven fuera de este directorio, en
`main/bme280_sensor.[ch]`, usando el API `i2c_master` de ESP-IDF v6.
