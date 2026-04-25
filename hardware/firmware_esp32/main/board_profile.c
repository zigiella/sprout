#include "sdkconfig.h"

#include "board_profile.h"

static const int N16R8_USB_OTG_RESERVED_GPIOS[] = {19, 20, 35, 36, 37, 45, 46};
static const int DEVKITC_N8R8_RESERVED_GPIOS[] = {19, 20, 35, 36, 37, 45, 46, 48};

static const sprout_board_profile_t PROFILE_N16R8_USB_OTG = {
    .id = "n16r8_usb_otg",
    .label = "ESP32-S3 N16R8 USB OTG",
    .reserved_gpios = N16R8_USB_OTG_RESERVED_GPIOS,
    .reserved_gpio_count = sizeof(N16R8_USB_OTG_RESERVED_GPIOS) / sizeof(N16R8_USB_OTG_RESERVED_GPIOS[0]),
    .uses_usb_serial_jtag = true,
};

static const sprout_board_profile_t PROFILE_DEVKITC_N8R8 = {
    .id = "devkitc_n8r8",
    .label = "ESP32-S3-DevKitC-1 N8R8",
    .reserved_gpios = DEVKITC_N8R8_RESERVED_GPIOS,
    .reserved_gpio_count = sizeof(DEVKITC_N8R8_RESERVED_GPIOS) / sizeof(DEVKITC_N8R8_RESERVED_GPIOS[0]),
    .uses_usb_serial_jtag = true,
};

const sprout_board_profile_t *sprout_board_profile_active(void)
{
#if CONFIG_SPROUT_BOARD_PROFILE_DEVKITC_N8R8
    return &PROFILE_DEVKITC_N8R8;
#else
    return &PROFILE_N16R8_USB_OTG;
#endif
}
