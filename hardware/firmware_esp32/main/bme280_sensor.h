#pragma once

#include <stdbool.h>
#include <stdint.h>

#include "esp_err.h"

#include "board_profile.h"

typedef struct {
    bool bus_ready;
    bool sensor_present;
    bool measurement_valid;
    uint8_t address;
    uint8_t chip_id;
    int32_t temperature_c_x100;
    int32_t humidity_pct_x100;
    int32_t pressure_pa;
    esp_err_t last_error;
    int8_t last_sensor_result;
} sprout_bme280_report_t;

esp_err_t sprout_bme280_init(const sprout_board_profile_t *profile);
esp_err_t sprout_bme280_scan(char *address_buffer, size_t buffer_size, uint8_t *count);
esp_err_t sprout_bme280_probe(sprout_bme280_report_t *report);
esp_err_t sprout_bme280_read(sprout_bme280_report_t *report);
const sprout_bme280_report_t *sprout_bme280_last_report(void);
