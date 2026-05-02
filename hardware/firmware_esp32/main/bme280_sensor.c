#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "sdkconfig.h"

#include "bme280_sensor.h"
#include "bme280.h"
#include "driver/i2c_master.h"
#include "esp_check.h"
#include "esp_err.h"
#include "esp_rom_sys.h"

#define SPROUT_BME280_ADDR_NONE 0x00
#define SPROUT_I2C_XFER_TIMEOUT_MS 1000
#define SPROUT_I2C_PROBE_TIMEOUT_MS 50

typedef struct {
    i2c_master_dev_handle_t dev_handle;
} sprout_bme280_intf_context_t;

static i2c_master_bus_handle_t s_i2c_bus_handle = NULL;
static sprout_bme280_intf_context_t s_intf_context = {
    .dev_handle = NULL,
};
static struct bme280_dev s_bme280_dev = { 0 };
static struct bme280_settings s_bme280_settings = {
    .osr_p = BME280_OVERSAMPLING_1X,
    .osr_t = BME280_OVERSAMPLING_1X,
    .osr_h = BME280_OVERSAMPLING_1X,
    .filter = BME280_FILTER_COEFF_OFF,
    .standby_time = BME280_STANDBY_TIME_0_5_MS,
};
static sprout_bme280_report_t s_last_report = {
    .bus_ready = false,
    .sensor_present = false,
    .measurement_valid = false,
    .address = SPROUT_BME280_ADDR_NONE,
    .chip_id = 0,
    .temperature_c_x100 = -1,
    .humidity_pct_x100 = -1,
    .pressure_pa = -1,
    .last_error = ESP_ERR_INVALID_STATE,
    .last_sensor_result = BME280_E_DEV_NOT_FOUND,
};
static int s_i2c_speed_hz = 100000;

static void sprout_bme280_copy_report(sprout_bme280_report_t *out_report)
{
    if (out_report != NULL) {
        *out_report = s_last_report;
    }
}

static int32_t sprout_scale_to_x100(double value)
{
    const double scaled = value * 100.0;
    const double bias = scaled >= 0.0 ? 0.5 : -0.5;
    return (int32_t)(scaled + bias);
}

static int32_t sprout_round_to_int(double value)
{
    const double bias = value >= 0.0 ? 0.5 : -0.5;
    return (int32_t)(value + bias);
}

static BME280_INTF_RET_TYPE sprout_bme280_i2c_read(uint8_t reg_addr, uint8_t *reg_data, uint32_t len, void *intf_ptr)
{
    if (intf_ptr == NULL || reg_data == NULL || len == 0) {
        s_last_report.last_error = ESP_ERR_INVALID_ARG;
        return BME280_E_COMM_FAIL;
    }

    sprout_bme280_intf_context_t *context = (sprout_bme280_intf_context_t *)intf_ptr;
    const esp_err_t err =
        i2c_master_transmit_receive(context->dev_handle, &reg_addr, sizeof(reg_addr), reg_data, len, SPROUT_I2C_XFER_TIMEOUT_MS);
    s_last_report.last_error = err;
    return (err == ESP_OK) ? BME280_INTF_RET_SUCCESS : BME280_E_COMM_FAIL;
}

static BME280_INTF_RET_TYPE sprout_bme280_i2c_write(
    uint8_t reg_addr,
    const uint8_t *reg_data,
    uint32_t len,
    void *intf_ptr)
{
    if (intf_ptr == NULL || reg_data == NULL || len == 0) {
        s_last_report.last_error = ESP_ERR_INVALID_ARG;
        return BME280_E_COMM_FAIL;
    }

    sprout_bme280_intf_context_t *context = (sprout_bme280_intf_context_t *)intf_ptr;
    uint8_t buffer[16];
    if (len + 1 > sizeof(buffer)) {
        s_last_report.last_error = ESP_ERR_INVALID_SIZE;
        return BME280_E_COMM_FAIL;
    }

    buffer[0] = reg_addr;
    memcpy(&buffer[1], reg_data, len);
    const esp_err_t err = i2c_master_transmit(context->dev_handle, buffer, len + 1, SPROUT_I2C_XFER_TIMEOUT_MS);
    s_last_report.last_error = err;
    return (err == ESP_OK) ? BME280_INTF_RET_SUCCESS : BME280_E_COMM_FAIL;
}

static void sprout_bme280_delay_us(uint32_t period, void *intf_ptr)
{
    (void)intf_ptr;
    esp_rom_delay_us(period);
}

static void sprout_bme280_reset_measurement_fields(void)
{
    s_last_report.measurement_valid = false;
    s_last_report.temperature_c_x100 = -1;
    s_last_report.humidity_pct_x100 = -1;
    s_last_report.pressure_pa = -1;
}

static esp_err_t sprout_bme280_remove_device(void)
{
    if (s_intf_context.dev_handle == NULL) {
        return ESP_OK;
    }

    esp_err_t err = i2c_master_bus_rm_device(s_intf_context.dev_handle);
    if (err == ESP_OK) {
        s_intf_context.dev_handle = NULL;
    }

    return err;
}

static esp_err_t sprout_bme280_open_device(uint8_t address)
{
    ESP_RETURN_ON_ERROR(sprout_bme280_remove_device(), "sprout_bme280", "remove old i2c device");

    const i2c_device_config_t device_config = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_7,
        .device_address = address,
        .scl_speed_hz = (uint32_t)s_i2c_speed_hz,
        .scl_wait_us = 0,
        .flags = {
            .disable_ack_check = 0,
        },
    };

    return i2c_master_bus_add_device(s_i2c_bus_handle, &device_config, &s_intf_context.dev_handle);
}

static esp_err_t sprout_bme280_prepare_sensor(uint8_t address)
{
    ESP_RETURN_ON_ERROR(sprout_bme280_open_device(address), "sprout_bme280", "open i2c bme280 device");

    memset(&s_bme280_dev, 0, sizeof(s_bme280_dev));
    s_bme280_dev.intf = BME280_I2C_INTF;
    s_bme280_dev.intf_ptr = &s_intf_context;
    s_bme280_dev.read = sprout_bme280_i2c_read;
    s_bme280_dev.write = sprout_bme280_i2c_write;
    s_bme280_dev.delay_us = sprout_bme280_delay_us;

    const int8_t rslt = bme280_init(&s_bme280_dev);
    s_last_report.last_sensor_result = rslt;
    if (rslt != BME280_OK) {
        s_last_report.last_error = ESP_ERR_NOT_FOUND;
        return ESP_ERR_NOT_FOUND;
    }

    const int8_t settings_rslt = bme280_set_sensor_settings(
        BME280_SEL_OSR_PRESS | BME280_SEL_OSR_TEMP | BME280_SEL_OSR_HUM | BME280_SEL_FILTER,
        &s_bme280_settings,
        &s_bme280_dev);
    s_last_report.last_sensor_result = settings_rslt;
    if (settings_rslt != BME280_OK) {
        s_last_report.last_error = ESP_FAIL;
        return ESP_FAIL;
    }

    s_last_report.sensor_present = true;
    s_last_report.address = address;
    s_last_report.chip_id = s_bme280_dev.chip_id;
    s_last_report.last_error = ESP_OK;
    s_last_report.bus_ready = true;
    sprout_bme280_reset_measurement_fields();
    return ESP_OK;
}

static esp_err_t sprout_bme280_find_and_prepare(void)
{
    const uint8_t addresses[] = { BME280_I2C_ADDR_PRIM, BME280_I2C_ADDR_SEC };
    for (size_t index = 0; index < sizeof(addresses) / sizeof(addresses[0]); ++index) {
        const uint8_t address = addresses[index];
        esp_err_t err = i2c_master_probe(s_i2c_bus_handle, address, SPROUT_I2C_PROBE_TIMEOUT_MS);
        if (err != ESP_OK) {
            continue;
        }

        err = sprout_bme280_prepare_sensor(address);
        if (err == ESP_OK) {
            return ESP_OK;
        }
    }

    s_last_report.sensor_present = false;
    s_last_report.address = SPROUT_BME280_ADDR_NONE;
    s_last_report.chip_id = 0;
    s_last_report.last_error = ESP_ERR_NOT_FOUND;
    s_last_report.last_sensor_result = BME280_E_DEV_NOT_FOUND;
    sprout_bme280_reset_measurement_fields();
    return ESP_ERR_NOT_FOUND;
}

const sprout_bme280_report_t *sprout_bme280_last_report(void)
{
    return &s_last_report;
}

esp_err_t sprout_bme280_init(const sprout_board_profile_t *profile)
{
    if (s_i2c_bus_handle != NULL) {
        s_last_report.bus_ready = true;
        s_last_report.last_error = ESP_OK;
        return ESP_OK;
    }

    if (profile == NULL) {
        s_last_report.last_error = ESP_ERR_INVALID_ARG;
        return ESP_ERR_INVALID_ARG;
    }

    s_i2c_speed_hz = profile->i2c_speed_hz;
    const i2c_master_bus_config_t bus_config = {
        .i2c_port = profile->i2c_port,
        .sda_io_num = profile->i2c_sda_gpio,
        .scl_io_num = profile->i2c_scl_gpio,
        .clk_source = I2C_CLK_SRC_DEFAULT,
        .glitch_ignore_cnt = 7,
        .intr_priority = 0,
        .trans_queue_depth = 4,
        .flags = {
            .enable_internal_pullup = 1,
            .allow_pd = 0,
        },
    };

    const esp_err_t err = i2c_new_master_bus(&bus_config, &s_i2c_bus_handle);
    s_last_report.bus_ready = (err == ESP_OK);
    s_last_report.last_error = err;
    return err;
}

esp_err_t sprout_bme280_scan(char *address_buffer, size_t buffer_size, uint8_t *count)
{
    if (address_buffer == NULL || buffer_size == 0 || count == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    address_buffer[0] = '\0';
    *count = 0;

    if (s_i2c_bus_handle == NULL) {
        return ESP_ERR_INVALID_STATE;
    }

    const uint8_t addresses[] = { BME280_I2C_ADDR_PRIM, BME280_I2C_ADDR_SEC };
    for (size_t index = 0; index < sizeof(addresses) / sizeof(addresses[0]); ++index) {
        const uint8_t address = addresses[index];
        if (i2c_master_probe(s_i2c_bus_handle, address, SPROUT_I2C_PROBE_TIMEOUT_MS) != ESP_OK) {
            continue;
        }

        char scratch[8];
        snprintf(scratch, sizeof(scratch), "0x%02X", address);
        if (*count > 0) {
            strncat(address_buffer, ",", buffer_size - strlen(address_buffer) - 1);
        }
        strncat(address_buffer, scratch, buffer_size - strlen(address_buffer) - 1);
        (*count)++;
    }

    if (*count == 0) {
        snprintf(address_buffer, buffer_size, "NONE");
    }

    s_last_report.last_error = ESP_OK;
    return ESP_OK;
}

esp_err_t sprout_bme280_probe(sprout_bme280_report_t *report)
{
    if (s_i2c_bus_handle == NULL) {
        s_last_report.last_error = ESP_ERR_INVALID_STATE;
        sprout_bme280_copy_report(report);
        return ESP_ERR_INVALID_STATE;
    }

    const esp_err_t err = sprout_bme280_find_and_prepare();
    sprout_bme280_copy_report(report);
    return err;
}

esp_err_t sprout_bme280_read(sprout_bme280_report_t *report)
{
    if (s_i2c_bus_handle == NULL) {
        s_last_report.last_error = ESP_ERR_INVALID_STATE;
        sprout_bme280_copy_report(report);
        return ESP_ERR_INVALID_STATE;
    }

    if (!s_last_report.sensor_present || s_intf_context.dev_handle == NULL) {
        const esp_err_t probe_err = sprout_bme280_find_and_prepare();
        if (probe_err != ESP_OK) {
            sprout_bme280_copy_report(report);
            return probe_err;
        }
    }

    const int8_t mode_rslt = bme280_set_sensor_mode(BME280_POWERMODE_FORCED, &s_bme280_dev);
    s_last_report.last_sensor_result = mode_rslt;
    if (mode_rslt != BME280_OK) {
        s_last_report.last_error = ESP_FAIL;
        sprout_bme280_copy_report(report);
        return ESP_FAIL;
    }

    uint32_t max_delay_us = 0;
    const int8_t delay_rslt = bme280_cal_meas_delay(&max_delay_us, &s_bme280_settings);
    s_last_report.last_sensor_result = delay_rslt;
    if (delay_rslt != BME280_OK) {
        s_last_report.last_error = ESP_FAIL;
        sprout_bme280_copy_report(report);
        return ESP_FAIL;
    }

    sprout_bme280_delay_us(max_delay_us + 1000, s_bme280_dev.intf_ptr);

    struct bme280_data sensor_data = { 0 };
    const int8_t read_rslt = bme280_get_sensor_data(BME280_ALL, &sensor_data, &s_bme280_dev);
    s_last_report.last_sensor_result = read_rslt;
    if (read_rslt != BME280_OK) {
        s_last_report.last_error = ESP_FAIL;
        sprout_bme280_reset_measurement_fields();
        sprout_bme280_copy_report(report);
        return ESP_FAIL;
    }

    s_last_report.measurement_valid = true;
    s_last_report.temperature_c_x100 = sprout_scale_to_x100(sensor_data.temperature);
    s_last_report.humidity_pct_x100 = sprout_scale_to_x100(sensor_data.humidity);
    s_last_report.pressure_pa = sprout_round_to_int(sensor_data.pressure);
    s_last_report.last_error = ESP_OK;
    sprout_bme280_copy_report(report);
    return ESP_OK;
}
