idf_component_register(
    SRCS
        "app_main.c"
        "bme280_sensor.c"
        "board_profile.c"
        "third_party/bme280/bme280.c"
    INCLUDE_DIRS
        "."
        "third_party/bme280"
    REQUIRES
        esp_app_format
        esp_adc
        esp_driver_gpio
        esp_driver_i2c
        esp_psram
        esp_timer
        nvs_flash
        spi_flash
)

target_compile_definitions(${COMPONENT_LIB} PRIVATE BME280_USE_FLOATING_POINT)
