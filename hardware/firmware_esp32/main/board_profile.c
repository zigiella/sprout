#include "sdkconfig.h"

#include "board_profile.h"

#if CONFIG_SPROUT_BOARD_PROFILE_DEVKITC_N8R8
static const int ACTIVE_RESERVED_GPIOS[] = {19, 20, 35, 36, 37, 45, 46, 48};
static const sprout_board_profile_t ACTIVE_PROFILE = {
    .id = "devkitc_n8r8",
    .label = "ESP32-S3-DevKitC-1 N8R8",
    .reserved_gpios = ACTIVE_RESERVED_GPIOS,
    .reserved_gpio_count = sizeof(ACTIVE_RESERVED_GPIOS) / sizeof(ACTIVE_RESERVED_GPIOS[0]),
    .uses_usb_serial_jtag = true,
    .i2c_port = 0,
    .i2c_sda_gpio = 8,
    .i2c_scl_gpio = 9,
    .i2c_speed_hz = 100000,
};
#else
static const int ACTIVE_RESERVED_GPIOS[] = {19, 20, 35, 36, 37, 45, 46};
static const sprout_board_profile_t ACTIVE_PROFILE = {
    .id = "n16r8_usb_otg",
    .label = "ESP32-S3 N16R8 USB OTG",
    .reserved_gpios = ACTIVE_RESERVED_GPIOS,
    .reserved_gpio_count = sizeof(ACTIVE_RESERVED_GPIOS) / sizeof(ACTIVE_RESERVED_GPIOS[0]),
    .uses_usb_serial_jtag = true,
    .i2c_port = 0,
    .i2c_sda_gpio = 8,
    .i2c_scl_gpio = 9,
    .i2c_speed_hz = 100000,
};
#endif

const sprout_board_profile_t *sprout_board_profile_active(void)
{
    return &ACTIVE_PROFILE;
}
