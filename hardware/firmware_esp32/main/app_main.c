#include <ctype.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "bme280_sensor.h"
#include "board_profile.h"
#include "sdkconfig.h"
#include "esp_app_desc.h"
#include "esp_err.h"
#include "esp_flash.h"
#include "esp_log.h"
#include "esp_psram.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "nvs_flash.h"

#define SPROUT_FW_VERSION "0.1.0"

typedef enum {
    SPROUT_STATE_SAFE_IDLE = 0,
    SPROUT_STATE_READY,
    SPROUT_STATE_EXECUTING,
    SPROUT_STATE_DEGRADED,
    SPROUT_STATE_ALERT_LATCHED,
} sprout_state_t;

typedef enum {
    SPROUT_HOST_LINK_MISSING = 0,
    SPROUT_HOST_LINK_FRESH,
    SPROUT_HOST_LINK_STALE,
} sprout_host_link_t;

typedef struct {
    int soil_a_raw;
    int soil_b_raw;
    int tank_level_raw;
    int tank_level_pct;
    uint32_t flow_pulses;
    bool bme280_connected;
    bool bme280_measurement_valid;
    int32_t bme280_temp_c_x100;
    int32_t bme280_humidity_pct_x100;
    int32_t bme280_pressure_pa;
} sprout_telemetry_snapshot_t;

typedef struct {
    bool present;
    char plot[8];
    int seconds;
    char outcome[32];
    int64_t at_ms;
} sprout_water_attempt_t;

static const char *TAG = "sprout_esp32";
static sprout_state_t s_state = SPROUT_STATE_SAFE_IDLE;
static int64_t s_last_host_heartbeat_ms = -1;
static int64_t s_last_alert_ms = -1;
static sprout_telemetry_snapshot_t s_telemetry = {
    .soil_a_raw = -1,
    .soil_b_raw = -1,
    .tank_level_raw = -1,
    .tank_level_pct = -1,
    .flow_pulses = 0,
    .bme280_connected = false,
    .bme280_measurement_valid = false,
    .bme280_temp_c_x100 = -1,
    .bme280_humidity_pct_x100 = -1,
    .bme280_pressure_pa = -1,
};
static sprout_water_attempt_t s_last_water_attempt = {
    .present = false,
    .plot = "NONE",
    .seconds = -1,
    .outcome = "NONE",
    .at_ms = -1,
};
static char s_last_reject_reason[32] = "NONE";
static char s_last_alert_code[32] = "NONE";

static int64_t sprout_uptime_ms(void)
{
    return esp_timer_get_time() / 1000;
}

static const char *sprout_state_name(sprout_state_t state)
{
    switch (state) {
    case SPROUT_STATE_SAFE_IDLE:
        return "SAFE_IDLE";
    case SPROUT_STATE_READY:
        return "READY";
    case SPROUT_STATE_EXECUTING:
        return "EXECUTING";
    case SPROUT_STATE_DEGRADED:
        return "DEGRADED";
    case SPROUT_STATE_ALERT_LATCHED:
        return "ALERT_LATCHED";
    default:
        return "UNKNOWN";
    }
}

static int64_t sprout_host_age_ms(void)
{
    if (s_last_host_heartbeat_ms < 0) {
        return -1;
    }

    return sprout_uptime_ms() - s_last_host_heartbeat_ms;
}

static sprout_host_link_t sprout_host_link_state(void)
{
    const int64_t host_age_ms = sprout_host_age_ms();
    if (host_age_ms < 0) {
        return SPROUT_HOST_LINK_MISSING;
    }

    if (host_age_ms <= CONFIG_SPROUT_HOST_HEARTBEAT_TIMEOUT_MS) {
        return SPROUT_HOST_LINK_FRESH;
    }

    return SPROUT_HOST_LINK_STALE;
}

static const char *sprout_host_link_name(sprout_host_link_t link_state)
{
    switch (link_state) {
    case SPROUT_HOST_LINK_FRESH:
        return "FRESH";
    case SPROUT_HOST_LINK_STALE:
        return "STALE";
    case SPROUT_HOST_LINK_MISSING:
    default:
        return "MISSING";
    }
}

static void sprout_copy_token(char *destination, size_t destination_size, const char *source)
{
    snprintf(destination, destination_size, "%s", source);
}

static int64_t sprout_alert_age_ms(void)
{
    if (s_last_alert_ms < 0) {
        return -1;
    }

    return sprout_uptime_ms() - s_last_alert_ms;
}

static int64_t sprout_last_water_age_ms(void)
{
    if (!s_last_water_attempt.present || s_last_water_attempt.at_ms < 0) {
        return -1;
    }

    return sprout_uptime_ms() - s_last_water_attempt.at_ms;
}

static void sprout_record_reject(const char *reason)
{
    sprout_copy_token(s_last_reject_reason, sizeof(s_last_reject_reason), reason);
}

static void sprout_record_water_attempt(const char *plot, int seconds, const char *outcome)
{
    s_last_water_attempt.present = true;
    sprout_copy_token(s_last_water_attempt.plot, sizeof(s_last_water_attempt.plot), plot);
    sprout_copy_token(s_last_water_attempt.outcome, sizeof(s_last_water_attempt.outcome), outcome);
    s_last_water_attempt.seconds = seconds;
    s_last_water_attempt.at_ms = sprout_uptime_ms();
}

static void sprout_clear_alert_latch(void)
{
    sprout_copy_token(s_last_alert_code, sizeof(s_last_alert_code), "NONE");
    s_last_alert_ms = -1;
    if (s_state == SPROUT_STATE_ALERT_LATCHED) {
        s_state = SPROUT_STATE_SAFE_IDLE;
    }
}

static void sprout_trim_ascii(char *line)
{
    size_t len = strlen(line);
    while (len > 0 && (line[len - 1] == '\n' || line[len - 1] == '\r' || isspace((unsigned char)line[len - 1]))) {
        line[--len] = '\0';
    }

    size_t offset = 0;
    while (line[offset] != '\0' && isspace((unsigned char)line[offset])) {
        offset++;
    }

    if (offset > 0) {
        memmove(line, line + offset, strlen(line + offset) + 1);
    }
}

static void sprout_emit_hello(void)
{
    const sprout_board_profile_t *profile = sprout_board_profile_active();
    printf(
        "HELLO fw=%s state=%s board=%s uptime_ms=%" PRIi64 "\n",
        SPROUT_FW_VERSION,
        sprout_state_name(s_state),
        profile->id,
        sprout_uptime_ms());
    fflush(stdout);
}

static void sprout_emit_status_report(const char *source)
{
    const sprout_board_profile_t *profile = sprout_board_profile_active();
    const sprout_bme280_report_t *bme280_report = sprout_bme280_last_report();
    uint32_t flash_bytes = 0;
    const size_t psram_bytes = esp_psram_get_size();
    const esp_app_desc_t *app_desc = esp_app_get_description();
    const char *fw_version = (app_desc != NULL && app_desc->version[0] != '\0') ? app_desc->version : SPROUT_FW_VERSION;
    char bme280_addr_text[8] = "NONE";

    esp_err_t flash_err = esp_flash_get_physical_size(NULL, &flash_bytes);
    if (flash_err != ESP_OK) {
        flash_bytes = 0;
    }

    if (bme280_report->sensor_present) {
        snprintf(bme280_addr_text, sizeof(bme280_addr_text), "0x%02X", bme280_report->address);
    }

    const int64_t host_age_ms = sprout_host_age_ms();
    printf(
        "STATUS_REPORT state=%s fw=%s board=%s uptime_ms=%" PRIi64 " flash_bytes=%" PRIu32
        " psram_bytes=%u telemetry_mode=HYBRID i2c_bus=%s i2c_sda=%d i2c_scl=%d bme280_addr=%s host_link=%s host_age_ms=%" PRIi64
        " hb_timeout_ms=%d tank_min_pct=%d max_water_s=%d last_reject=%s alert_code=%s alert_age_ms=%" PRIi64
        " last_water_plot=%s last_water_seconds=%d last_water_outcome=%s last_water_age_ms=%" PRIi64
        " source=%s\n",
        sprout_state_name(s_state),
        fw_version,
        profile->id,
        sprout_uptime_ms(),
        flash_bytes,
        (unsigned int)psram_bytes,
        bme280_report->bus_ready ? "READY" : "ERROR",
        profile->i2c_sda_gpio,
        profile->i2c_scl_gpio,
        bme280_addr_text,
        sprout_host_link_name(sprout_host_link_state()),
        host_age_ms,
        CONFIG_SPROUT_HOST_HEARTBEAT_TIMEOUT_MS,
        CONFIG_SPROUT_TANK_MINIMUM_PCT,
        CONFIG_SPROUT_MAX_WATER_SECONDS,
        s_last_reject_reason,
        s_last_alert_code,
        sprout_alert_age_ms(),
        s_last_water_attempt.plot,
        s_last_water_attempt.seconds,
        s_last_water_attempt.outcome,
        sprout_last_water_age_ms(),
        source);
    fflush(stdout);
}

static void sprout_emit_ack(const char *command)
{
    printf(
        "ACK command=%s state=%s host_link=%s host_age_ms=%" PRIi64 "\n",
        command,
        sprout_state_name(s_state),
        sprout_host_link_name(sprout_host_link_state()),
        sprout_host_age_ms());
    fflush(stdout);
}

static void sprout_emit_ack_sensor_stub(const char *field)
{
    printf(
        "ACK command=SET_SENSOR_STUB field=%s soil_a_raw=%d soil_b_raw=%d tank_level_raw=%d tank_level_pct=%d "
        "flow_pulses=%" PRIu32 " bme280=%s bme280_valid=%s bme280_temp_c_x100=%" PRIi32
        " bme280_humidity_pct_x100=%" PRIi32 " bme280_pressure_pa=%" PRIi32 "\n",
        field,
        s_telemetry.soil_a_raw,
        s_telemetry.soil_b_raw,
        s_telemetry.tank_level_raw,
        s_telemetry.tank_level_pct,
        s_telemetry.flow_pulses,
        s_telemetry.bme280_connected ? "CONNECTED" : "DISCONNECTED",
        s_telemetry.bme280_measurement_valid ? "true" : "false",
        s_telemetry.bme280_temp_c_x100,
        s_telemetry.bme280_humidity_pct_x100,
        s_telemetry.bme280_pressure_pa);
    fflush(stdout);
}

static void sprout_emit_reject(const char *reason, const char *command)
{
    printf("REJECT reason=%s cmd=%s\n", reason, command);
    fflush(stdout);
}

static void sprout_emit_alert(const char *code, bool latched)
{
    printf(
        "ALERT code=%s latched=%s state=%s uptime_ms=%" PRIi64 "\n",
        code,
        latched ? "true" : "false",
        sprout_state_name(s_state),
        sprout_uptime_ms());
    fflush(stdout);
}

static void sprout_raise_alert(const char *code, bool latched)
{
    sprout_copy_token(s_last_alert_code, sizeof(s_last_alert_code), code);
    s_last_alert_ms = sprout_uptime_ms();
    if (latched) {
        s_state = SPROUT_STATE_ALERT_LATCHED;
    }
    sprout_emit_alert(code, latched);
}

static void sprout_emit_ack_water(const char *plot, int seconds)
{
    printf(
        "ACK command=WATER plot=%s seconds=%d execution=DRY_RUN state=%s host_link=%s tank_level_pct=%d\n",
        plot,
        seconds,
        sprout_state_name(s_state),
        sprout_host_link_name(sprout_host_link_state()),
        s_telemetry.tank_level_pct);
    fflush(stdout);
}

static void sprout_emit_telemetry_report(const char *source)
{
    printf(
        "TELEMETRY_REPORT soil_a_raw=%d soil_b_raw=%d tank_level_raw=%d tank_level_pct=%d flow_pulses=%" PRIu32 " "
        "bme280=%s bme280_valid=%s bme280_temp_c_x100=%" PRIi32 " bme280_humidity_pct_x100=%" PRIi32
        " bme280_pressure_pa=%" PRIi32 " host_link=%s host_age_ms=%" PRIi64 " source=%s\n",
        s_telemetry.soil_a_raw,
        s_telemetry.soil_b_raw,
        s_telemetry.tank_level_raw,
        s_telemetry.tank_level_pct,
        s_telemetry.flow_pulses,
        s_telemetry.bme280_connected ? "CONNECTED" : "DISCONNECTED",
        s_telemetry.bme280_measurement_valid ? "true" : "false",
        s_telemetry.bme280_temp_c_x100,
        s_telemetry.bme280_humidity_pct_x100,
        s_telemetry.bme280_pressure_pa,
        sprout_host_link_name(sprout_host_link_state()),
        sprout_host_age_ms(),
        source);
    fflush(stdout);
}

static void sprout_reset_telemetry_stubs(void)
{
    s_telemetry.soil_a_raw = -1;
    s_telemetry.soil_b_raw = -1;
    s_telemetry.tank_level_raw = -1;
    s_telemetry.tank_level_pct = -1;
    s_telemetry.flow_pulses = 0;
    s_telemetry.bme280_connected = false;
    s_telemetry.bme280_measurement_valid = false;
    s_telemetry.bme280_temp_c_x100 = -1;
    s_telemetry.bme280_humidity_pct_x100 = -1;
    s_telemetry.bme280_pressure_pa = -1;
}

static void sprout_apply_bme280_report(const sprout_bme280_report_t *report)
{
    if (report == NULL) {
        return;
    }

    s_telemetry.bme280_connected = report->sensor_present;
    s_telemetry.bme280_measurement_valid = report->measurement_valid;
    if (report->measurement_valid) {
        s_telemetry.bme280_temp_c_x100 = report->temperature_c_x100;
        s_telemetry.bme280_humidity_pct_x100 = report->humidity_pct_x100;
        s_telemetry.bme280_pressure_pa = report->pressure_pa;
        return;
    }

    s_telemetry.bme280_temp_c_x100 = -1;
    s_telemetry.bme280_humidity_pct_x100 = -1;
    s_telemetry.bme280_pressure_pa = -1;
}

static bool sprout_parse_int(const char *value_text, int *out_value)
{
    char *end_ptr = NULL;
    long parsed = strtol(value_text, &end_ptr, 10);
    if (end_ptr == value_text || *end_ptr != '\0') {
        return false;
    }

    if (parsed < INT32_MIN || parsed > INT32_MAX) {
        return false;
    }

    *out_value = (int)parsed;
    return true;
}

static bool sprout_handle_set_sensor_stub(const char *line)
{
    const char *prefix = "SET_SENSOR_STUB ";
    const size_t prefix_len = strlen(prefix);
    if (strncmp(line, prefix, prefix_len) != 0) {
        return false;
    }

    char scratch[CONFIG_SPROUT_COMMAND_MAX_LINE_LENGTH];
    strncpy(scratch, line + prefix_len, sizeof(scratch) - 1);
    scratch[sizeof(scratch) - 1] = '\0';

    char *field = strtok(scratch, " ");
    char *value = strtok(NULL, " ");
    char *unexpected = strtok(NULL, " ");

    if (field == NULL || value == NULL || unexpected != NULL) {
        sprout_emit_reject("BAD_ARGS", line);
        return true;
    }

    if (strcmp(field, "SOIL_A") == 0) {
        int parsed = -1;
        if (!sprout_parse_int(value, &parsed)) {
            sprout_emit_reject("BAD_VALUE", line);
            return true;
        }
        s_telemetry.soil_a_raw = parsed;
        sprout_emit_ack_sensor_stub(field);
        return true;
    }

    if (strcmp(field, "SOIL_B") == 0) {
        int parsed = -1;
        if (!sprout_parse_int(value, &parsed)) {
            sprout_emit_reject("BAD_VALUE", line);
            return true;
        }
        s_telemetry.soil_b_raw = parsed;
        sprout_emit_ack_sensor_stub(field);
        return true;
    }

    if (strcmp(field, "TANK_LEVEL") == 0) {
        int parsed = -1;
        if (!sprout_parse_int(value, &parsed)) {
            sprout_emit_reject("BAD_VALUE", line);
            return true;
        }
        s_telemetry.tank_level_raw = parsed;
        sprout_emit_ack_sensor_stub(field);
        return true;
    }

    if (strcmp(field, "TANK_LEVEL_PCT") == 0) {
        int parsed = -1;
        if (!sprout_parse_int(value, &parsed) || parsed < 0 || parsed > 100) {
            sprout_emit_reject("BAD_VALUE", line);
            return true;
        }
        s_telemetry.tank_level_pct = parsed;
        sprout_emit_ack_sensor_stub(field);
        return true;
    }

    if (strcmp(field, "FLOW_PULSES") == 0) {
        int parsed = -1;
        if (!sprout_parse_int(value, &parsed) || parsed < 0) {
            sprout_emit_reject("BAD_VALUE", line);
            return true;
        }
        s_telemetry.flow_pulses = (uint32_t)parsed;
        sprout_emit_ack_sensor_stub(field);
        return true;
    }

    if (strcmp(field, "BME280") == 0) {
        if (strcmp(value, "CONNECTED") == 0) {
            s_telemetry.bme280_connected = true;
            sprout_emit_ack_sensor_stub(field);
            return true;
        }

        if (strcmp(value, "DISCONNECTED") == 0) {
            s_telemetry.bme280_connected = false;
            sprout_emit_ack_sensor_stub(field);
            return true;
        }

        sprout_emit_reject("BAD_VALUE", line);
        return true;
    }

    sprout_emit_reject("UNKNOWN_FIELD", line);
    return true;
}

static bool sprout_handle_water_command(const char *line)
{
    const char *prefix = "WATER ";
    const size_t prefix_len = strlen(prefix);
    if (strncmp(line, prefix, prefix_len) != 0) {
        return false;
    }

    char scratch[CONFIG_SPROUT_COMMAND_MAX_LINE_LENGTH];
    strncpy(scratch, line + prefix_len, sizeof(scratch) - 1);
    scratch[sizeof(scratch) - 1] = '\0';

    char *plot = strtok(scratch, " ");
    char *seconds_text = strtok(NULL, " ");
    char *unexpected = strtok(NULL, " ");

    if (plot == NULL || seconds_text == NULL || unexpected != NULL) {
        sprout_record_reject("EVENT_DURATION_OUT_OF_RANGE");
        sprout_emit_reject("EVENT_DURATION_OUT_OF_RANGE", line);
        return true;
    }

    if (!(strcmp(plot, "A") == 0 || strcmp(plot, "B") == 0 || strcmp(plot, "BOTH") == 0)) {
        sprout_record_reject("EVENT_DURATION_OUT_OF_RANGE");
        sprout_emit_reject("EVENT_DURATION_OUT_OF_RANGE", line);
        return true;
    }

    int seconds = 0;
    if (!sprout_parse_int(seconds_text, &seconds) || seconds <= 0 || seconds > CONFIG_SPROUT_MAX_WATER_SECONDS) {
        sprout_record_reject("EVENT_DURATION_OUT_OF_RANGE");
        sprout_record_water_attempt(plot, seconds, "REJECT_EVENT_DURATION_OUT_OF_RANGE");
        sprout_emit_reject("EVENT_DURATION_OUT_OF_RANGE", line);
        return true;
    }

    if (s_state == SPROUT_STATE_ALERT_LATCHED) {
        sprout_record_reject("ALERT_LATCHED");
        sprout_record_water_attempt(plot, seconds, "REJECT_ALERT_LATCHED");
        sprout_emit_reject("ALERT_LATCHED", line);
        return true;
    }

    if (sprout_host_link_state() != SPROUT_HOST_LINK_FRESH) {
        sprout_record_reject("JETSON_HEARTBEAT_LOST");
        sprout_record_water_attempt(plot, seconds, "REJECT_JETSON_HEARTBEAT_LOST");
        sprout_emit_reject("JETSON_HEARTBEAT_LOST", line);
        sprout_raise_alert("JETSON_HEARTBEAT_LOST", false);
        return true;
    }

    if (s_telemetry.tank_level_pct >= 0 && s_telemetry.tank_level_pct < CONFIG_SPROUT_TANK_MINIMUM_PCT) {
        sprout_record_reject("TANK_LOW");
        sprout_record_water_attempt(plot, seconds, "REJECT_TANK_LOW");
        sprout_emit_reject("TANK_LOW", line);
        sprout_raise_alert("TANK_LOW", true);
        return true;
    }

    sprout_record_water_attempt(plot, seconds, "ACK_DRY_RUN");
    sprout_emit_ack_water(plot, seconds);
    return true;
}

static void sprout_emit_i2c_scan_report(const char *addresses, uint8_t count)
{
    printf("I2C_SCAN count=%u addrs=%s\n", count, addresses);
    fflush(stdout);
}

static void sprout_emit_bme280_probe_report(const sprout_bme280_report_t *report)
{
    char addr_text[8] = "NONE";
    char chip_id_text[8] = "NONE";
    if (report->sensor_present) {
        snprintf(addr_text, sizeof(addr_text), "0x%02X", report->address);
        snprintf(chip_id_text, sizeof(chip_id_text), "0x%02X", report->chip_id);
    }

    printf(
        "BME280_PROBE status=%s address=%s chip_id=%s i2c_bus=%s error=%s sensor_rslt=%d\n",
        report->sensor_present ? "CONNECTED" : "NOT_FOUND",
        addr_text,
        chip_id_text,
        report->bus_ready ? "READY" : "ERROR",
        esp_err_to_name(report->last_error),
        report->last_sensor_result);
    fflush(stdout);
}

static void sprout_emit_bme280_read_report(const sprout_bme280_report_t *report, const char *source)
{
    char addr_text[8] = "NONE";
    char chip_id_text[8] = "NONE";
    if (report->sensor_present) {
        snprintf(addr_text, sizeof(addr_text), "0x%02X", report->address);
        snprintf(chip_id_text, sizeof(chip_id_text), "0x%02X", report->chip_id);
    }

    printf(
        "BME280_REPORT status=%s address=%s chip_id=%s temp_c_x100=%" PRIi32
        " humidity_pct_x100=%" PRIi32 " pressure_pa=%" PRIi32 " error=%s sensor_rslt=%d source=%s\n",
        report->measurement_valid ? "CONNECTED" : (report->sensor_present ? "PROBED" : "NOT_FOUND"),
        addr_text,
        chip_id_text,
        report->temperature_c_x100,
        report->humidity_pct_x100,
        report->pressure_pa,
        esp_err_to_name(report->last_error),
        report->last_sensor_result,
        source);
    fflush(stdout);
}

static void sprout_heartbeat_task(void *arg)
{
    (void)arg;
    const sprout_board_profile_t *profile = sprout_board_profile_active();

    while (true) {
        printf(
            "HEARTBEAT state=%s board=%s uptime_ms=%" PRIi64 " host_link=%s host_age_ms=%" PRIi64 "\n",
            sprout_state_name(s_state),
            profile->id,
            sprout_uptime_ms(),
            sprout_host_link_name(sprout_host_link_state()),
            sprout_host_age_ms());
        fflush(stdout);
        vTaskDelay(pdMS_TO_TICKS(CONFIG_SPROUT_HEARTBEAT_INTERVAL_MS));
    }
}

static bool sprout_read_command_line(char *line, size_t line_size)
{
    size_t index = 0;

    while (true) {
        int ch = fgetc(stdin);
        if (ch == EOF) {
            clearerr(stdin);
            vTaskDelay(pdMS_TO_TICKS(50));
            continue;
        }

        if (ch == '\r' || ch == '\n') {
            if (index == 0) {
                continue;
            }

            line[index] = '\0';
            return true;
        }

        if (!isprint((unsigned char)ch)) {
            continue;
        }

        if (index + 1 >= line_size) {
            line[index] = '\0';
            return true;
        }

        line[index++] = (char)ch;
    }
}

static void sprout_command_loop(void)
{
    char line[CONFIG_SPROUT_COMMAND_MAX_LINE_LENGTH];

    while (true) {
        if (!sprout_read_command_line(line, sizeof(line))) {
            continue;
        }

        sprout_trim_ascii(line);
        if (line[0] == '\0') {
            continue;
        }

        if (strcmp(line, "HELLO") == 0) {
            sprout_emit_hello();
            continue;
        }

        if (strcmp(line, "STATUS") == 0) {
            sprout_emit_status_report("command");
            continue;
        }

        if (strcmp(line, "HOST_HEARTBEAT") == 0 || strcmp(line, "JETSON_HEARTBEAT") == 0) {
            s_last_host_heartbeat_ms = sprout_uptime_ms();
            sprout_emit_ack("HOST_HEARTBEAT");
            continue;
        }

        if (strcmp(line, "TELEMETRY") == 0) {
            sprout_emit_telemetry_report("command");
            continue;
        }

        if (strcmp(line, "I2C_SCAN") == 0) {
            char addresses[CONFIG_SPROUT_I2C_SCAN_BUFFER_BYTES];
            uint8_t count = 0;
            const esp_err_t err = sprout_bme280_scan(addresses, sizeof(addresses), &count);
            if (err != ESP_OK) {
                sprout_emit_reject("I2C_BUS_ERROR", line);
                continue;
            }

            sprout_emit_i2c_scan_report(addresses, count);
            continue;
        }

        if (strcmp(line, "BME280_PROBE") == 0) {
            sprout_bme280_report_t report = { 0 };
            (void)sprout_bme280_probe(&report);
            sprout_apply_bme280_report(&report);
            sprout_emit_bme280_probe_report(&report);
            continue;
        }

        if (strcmp(line, "BME280_READ") == 0) {
            sprout_bme280_report_t report = { 0 };
            (void)sprout_bme280_read(&report);
            sprout_apply_bme280_report(&report);
            sprout_emit_bme280_read_report(&report, "command");
            continue;
        }

        if (strcmp(line, "RESET_SENSOR_STUBS") == 0) {
            sprout_reset_telemetry_stubs();
            sprout_emit_ack("RESET_SENSOR_STUBS");
            continue;
        }

        if (strcmp(line, "RESET_ALERT") == 0) {
            sprout_clear_alert_latch();
            sprout_emit_ack("RESET_ALERT");
            continue;
        }

        if (sprout_handle_set_sensor_stub(line)) {
            continue;
        }

        if (sprout_handle_water_command(line)) {
            continue;
        }

        if (strcmp(line, "STOP") == 0) {
            sprout_emit_ack("STOP");
            continue;
        }

        sprout_emit_reject("UNKNOWN_COMMAND", line);
    }
}

static void sprout_init_nvs(void)
{
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);
}

void app_main(void)
{
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);

    sprout_init_nvs();
    sprout_reset_telemetry_stubs();

    const sprout_board_profile_t *profile = sprout_board_profile_active();
    ESP_ERROR_CHECK(sprout_bme280_init(profile));
    esp_log_level_set("i2c.master", ESP_LOG_NONE);
    ESP_LOGI(TAG, "booting board=%s state=%s", profile->id, sprout_state_name(s_state));

    sprout_emit_hello();
    sprout_emit_status_report("boot");

    xTaskCreate(
        sprout_heartbeat_task,
        "sprout_heartbeat",
        4096,
        NULL,
        tskIDLE_PRIORITY + 1,
        NULL);

    sprout_command_loop();
}
