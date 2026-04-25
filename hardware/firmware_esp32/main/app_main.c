#include <ctype.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

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
} sprout_telemetry_snapshot_t;

static const char *TAG = "sprout_esp32";
static sprout_state_t s_state = SPROUT_STATE_SAFE_IDLE;
static int64_t s_last_host_heartbeat_ms = -1;
static sprout_telemetry_snapshot_t s_telemetry = {
    .soil_a_raw = -1,
    .soil_b_raw = -1,
    .tank_level_raw = -1,
    .tank_level_pct = -1,
    .flow_pulses = 0,
    .bme280_connected = false,
};

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
    uint32_t flash_bytes = 0;
    const size_t psram_bytes = esp_psram_get_size();
    const esp_app_desc_t *app_desc = esp_app_get_description();
    const char *fw_version = (app_desc != NULL && app_desc->version[0] != '\0') ? app_desc->version : SPROUT_FW_VERSION;

    esp_err_t flash_err = esp_flash_get_physical_size(NULL, &flash_bytes);
    if (flash_err != ESP_OK) {
        flash_bytes = 0;
    }

    const int64_t host_age_ms = sprout_host_age_ms();
    printf(
        "STATUS_REPORT state=%s fw=%s board=%s uptime_ms=%" PRIi64 " flash_bytes=%" PRIu32
        " psram_bytes=%u telemetry_mode=STUB host_link=%s host_age_ms=%" PRIi64
        " hb_timeout_ms=%d tank_min_pct=%d max_water_s=%d source=%s\n",
        sprout_state_name(s_state),
        fw_version,
        profile->id,
        sprout_uptime_ms(),
        flash_bytes,
        (unsigned int)psram_bytes,
        sprout_host_link_name(sprout_host_link_state()),
        host_age_ms,
        CONFIG_SPROUT_HOST_HEARTBEAT_TIMEOUT_MS,
        CONFIG_SPROUT_TANK_MINIMUM_PCT,
        CONFIG_SPROUT_MAX_WATER_SECONDS,
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
        "flow_pulses=%" PRIu32 " bme280=%s\n",
        field,
        s_telemetry.soil_a_raw,
        s_telemetry.soil_b_raw,
        s_telemetry.tank_level_raw,
        s_telemetry.tank_level_pct,
        s_telemetry.flow_pulses,
        s_telemetry.bme280_connected ? "CONNECTED" : "DISCONNECTED");
    fflush(stdout);
}

static void sprout_emit_reject(const char *reason, const char *command)
{
    printf("REJECT reason=%s cmd=%s\n", reason, command);
    fflush(stdout);
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
        "bme280=%s host_link=%s host_age_ms=%" PRIi64 " source=%s\n",
        s_telemetry.soil_a_raw,
        s_telemetry.soil_b_raw,
        s_telemetry.tank_level_raw,
        s_telemetry.tank_level_pct,
        s_telemetry.flow_pulses,
        s_telemetry.bme280_connected ? "CONNECTED" : "DISCONNECTED",
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
        sprout_emit_reject("FUERA_DE_RANGO", line);
        return true;
    }

    if (!(strcmp(plot, "A") == 0 || strcmp(plot, "B") == 0 || strcmp(plot, "BOTH") == 0)) {
        sprout_emit_reject("FUERA_DE_RANGO", line);
        return true;
    }

    int seconds = 0;
    if (!sprout_parse_int(seconds_text, &seconds) || seconds <= 0 || seconds > CONFIG_SPROUT_MAX_WATER_SECONDS) {
        sprout_emit_reject("FUERA_DE_RANGO", line);
        return true;
    }

    if (s_state == SPROUT_STATE_ALERT_LATCHED) {
        sprout_emit_reject("ALERTA_LATCHED", line);
        return true;
    }

    if (sprout_host_link_state() != SPROUT_HOST_LINK_FRESH) {
        sprout_emit_reject("HEARTBEAT_PERDIDO", line);
        return true;
    }

    if (s_telemetry.tank_level_pct >= 0 && s_telemetry.tank_level_pct < CONFIG_SPROUT_TANK_MINIMUM_PCT) {
        sprout_emit_reject("DEPOSITO_BAJO", line);
        return true;
    }

    sprout_emit_ack_water(plot, seconds);
    return true;
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

        if (strcmp(line, "RESET_SENSOR_STUBS") == 0) {
            sprout_reset_telemetry_stubs();
            sprout_emit_ack("RESET_SENSOR_STUBS");
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
