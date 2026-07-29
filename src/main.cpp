#include "mqtt_client.h"
#include <stdio.h>

int main(int argc, char **argv) {
    printf("Starting HIRI Firmware...\n");

    mqtt_config_t config;
    mqtt_init_config(&config);

    if (argc > 1) {
        snprintf(config.host, sizeof(config.host), "%s", argv[1]);
    }

#if ENABLE_MQTT_TLS
    if (argc > 2) {
        mqtt_load_ca_cert_from_file(&config, argv[2]);
    } else {
        printf("[WARNING] TLS enabled but no CA certificate file path provided.\n");
    }
#endif

    mqtt_client_t client;
    if (!mqtt_client_init(&client, &config)) {
        printf("Failed to initialize MQTT client context.\n");
        return 1;
    }

    if (mqtt_connect(&client)) {
        printf("MQTT Session active.\n");
        mqtt_disconnect(&client);
    } else {
        printf("MQTT Connection failed.\n");
        return 1;
    }

    return 0;
}
