#pragma once

#include <stdbool.h>
#include <stddef.h>

typedef struct {
    const char *id;
    const char *label;
    const int *reserved_gpios;
    size_t reserved_gpio_count;
    bool uses_usb_serial_jtag;
    int i2c_port;
    int i2c_sda_gpio;
    int i2c_scl_gpio;
    int i2c_speed_hz;
} sprout_board_profile_t;

const sprout_board_profile_t *sprout_board_profile_active(void);
