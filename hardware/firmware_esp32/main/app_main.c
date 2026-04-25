#include <ctype.h>
#include <inttypes.h>
#include <stdbool.h>
#include <stdint.h>
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

static const char *TAG = "sprout_esp32";
static sprout_state_t s_state = SPROUT_STATE_SAFE_IDLE;

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

    printf(
        "STATUS_REPORT state=%s fw=%s board=%s uptime_ms=%" PRIi64 " flash_bytes=%" PRIu32
        " psram_bytes=%u source=%s\n",
        sprout_state_name(s_state),
        fw_version,
        profile->id,
        sprout_uptime_ms(),
        flash_bytes,
        (unsigned int)psram_bytes,
        source);
    fflush(stdout);
}

static void sprout_emit_reject(const char *reason, const char *command)
{
    printf("REJECT reason=%s cmd=%s\n", reason, command);
    fflush(stdout);
}

static void sprout_heartbeat_task(void *arg)
{
    (void)arg;
    const sprout_board_profile_t *profile = sprout_board_profile_active();

    while (true) {
        printf(
            "HEARTBEAT state=%s board=%s uptime_ms=%" PRIi64 "\n",
            sprout_state_name(s_state),
            profile->id,
            sprout_uptime_ms());
        fflush(stdout);
        vTaskDelay(pdMS_TO_TICKS(CONFIG_SPROUT_HEARTBEAT_INTERVAL_MS));
    }
}

static void sprout_command_loop(void)
{
    char line[CONFIG_SPROUT_COMMAND_MAX_LINE_LENGTH];

    while (true) {
        if (fgets(line, sizeof(line), stdin) == NULL) {
            clearerr(stdin);
            vTaskDelay(pdMS_TO_TICKS(50));
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
