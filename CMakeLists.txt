cmake_minimum_required(VERSION 3.16)
project(hiri_firmware C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Feature Flags
option(ENABLE_MQTT_TLS "Enable TLS/SSL encryption for MQTT connections (production HA)" OFF)

if(ENABLE_MQTT_TLS)
    add_compile_definitions(ENABLE_MQTT_TLS=1)
    message(STATUS "MQTT TLS encryption: ENABLED")
else()
    add_compile_definitions(ENABLE_MQTT_TLS=0)
    message(STATUS "MQTT TLS encryption: DISABLED (Standard TCP)")
endif()

# Core Firmware Target
add_executable(hiri_firmware
    src/main.cpp
    src/mqtt_client.cpp
)

target_include_directories(hiri_firmware PUBLIC include)

# Dependencies
if(ENABLE_MQTT_TLS)
    find_package(MbedTLS REQUIRED)
    target_link_libraries(hiri_firmware PRIVATE MbedTLS::mbedtls MbedTLS::mbedcrypto MbedTLS::mbedx509)
endif()
