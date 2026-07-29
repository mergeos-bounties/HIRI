#ifndef MQTT_CLIENT_H
#define MQTT_CLIENT_H

#ifndef ENABLE_MQTT_TLS
#define ENABLE_MQTT_TLS 0
#endif

#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>

#if ENABLE_MQTT_TLS
#include "mbedtls/net_sockets.h"
#include "mbedtls/ssl.h"
#include "mbedtls/entropy.h"
#include "mbedtls/ctr_drbg.h"
#include "mbedtls/error.h"
#include "mbedtls/certs.h"
#endif

#ifndef CONFIG_DEFAULT_MQTT_HOST
#define CONFIG_DEFAULT_MQTT_HOST "mqtt-ha-broker.local"
#endif

#ifndef CONFIG_DEFAULT_MQTT_PORT
#if ENABLE_MQTT_TLS
#define CONFIG_DEFAULT_MQTT_PORT 8883
#else
#define CONFIG_DEFAULT_MQTT_PORT 1883
#endif
#endif

typedef struct {
    char host[256];
    uint16_t port;
    uint16_t keepalive;
    bool use_tls;
    
    // CA Certificate PEM content or path reference
    const char *ca_cert_pem;
    size_t ca_cert_len;
    
    // Optional client credentials for mTLS
    const char *client_cert_pem;
    size_t client_cert_len;
    const char *client_key_pem;
    size_t client_key_len;
} mqtt_config_t;

typedef struct {
    mqtt_config_t config;
    bool is_connected;
    int socket_fd;
#if ENABLE_MQTT_TLS
    mbedtls_net_context net_ctx;
    mbedtls_ssl_context ssl_ctx;
    mbedtls_ssl_config ssl_conf;
    mbedtls_x509_crt ca_cert;
    mbedtls_x509_crt client_cert;
    mbedtls_pk_context client_key;
    mbedtls_entropy_context entropy;
    mbedtls_ctr_drbg_context ctr_drbg;
#endif
} mqtt_client_t;

void mqtt_init_config(mqtt_config_t *config);
bool mqtt_client_init(mqtt_client_t *client, const mqtt_config_t *config);
bool mqtt_connect(mqtt_client_t *client);
void mqtt_disconnect(mqtt_client_t *client);
bool mqtt_load_ca_cert_from_file(mqtt_config_t *config, const char *filepath);

#endif // MQTT_CLIENT_H
