#include "mqtt_client.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void mqtt_init_config(mqtt_config_t *config) {
    if (!config) return;
    memset(config, 0, sizeof(mqtt_config_t));
    
    snprintf(config->host, sizeof(config->host), "%s", CONFIG_DEFAULT_MQTT_HOST);
    config->port = CONFIG_DEFAULT_MQTT_PORT;
    config->keepalive = 60;

#if ENABLE_MQTT_TLS
    config->use_tls = true;
#else
    config->use_tls = false;
#endif
}

bool mqtt_load_ca_cert_from_file(mqtt_config_t *config, const char *filepath) {
    if (!config || !filepath) return false;
    
    FILE *f = fopen(filepath, "rb");
    if (!f) {
        printf("[MQTT] Error: Unable to open CA cert file: %s\n", filepath);
        return false;
    }

    fseek(f, 0, SEEK_END);
    long sz = ftell(f);
    fseek(f, 0, SEEK_SET);

    if (sz <= 0) {
        fclose(f);
        return false;
    }

    char *buf = (char *)malloc(sz + 1);
    if (!buf) {
        fclose(f);
        return false;
    }

    size_t read_bytes = fread(buf, 1, sz, f);
    fclose(f);
    buf[read_bytes] = '\0';

    config->ca_cert_pem = buf;
    config->ca_cert_len = read_bytes + 1;
    return true;
}

bool mqtt_client_init(mqtt_client_t *client, const mqtt_config_t *config) {
    if (!client || !config) return false;
    memset(client, 0, sizeof(mqtt_client_t));
    memcpy(&client->config, config, sizeof(mqtt_config_t));
    client->socket_fd = -1;

#if ENABLE_MQTT_TLS
    if (client->config.use_tls) {
        mbedtls_net_init(&client->net_ctx);
        mbedtls_ssl_init(&client->ssl_ctx);
        mbedtls_ssl_config_init(&client->ssl_conf);
        mbedtls_x509_crt_init(&client->ca_cert);
        mbedtls_x509_crt_init(&client->client_cert);
        mbedtls_pk_init(&client->client_key);
        mbedtls_ctr_drbg_init(&client->ctr_drbg);
        mbedtls_entropy_init(&client->entropy);
    }
#endif
    return true;
}

bool mqtt_connect(mqtt_client_t *client) {
    if (!client) return false;

    char port_str[6];
    snprintf(port_str, sizeof(port_str), "%u", client->config.port);

#if ENABLE_MQTT_TLS
    if (client->config.use_tls) {
        int ret;
        const char *pers = "mqtt_tls_client";

        if (client->config.ca_cert_pem == NULL || client->config.ca_cert_len == 0) {
            printf("[MQTT] Error: TLS enabled but no valid CA certificate provided.\n");
            return false;
        }

        // Initialize DRBG seed
        ret = mbedtls_ctr_drbg_seed(&client->ctr_drbg, mbedtls_entropy_func, 
                                    &client->entropy, (const unsigned char *)pers, strlen(pers));
        if (ret != 0) {
            printf("[MQTT] mbedtls_ctr_drbg_seed failed: -0x%04x\n", -ret);
            return false;
        }

        // Parse Root CA Certificate
        ret = mbedtls_x509_crt_parse(&client->ca_cert, 
                                     (const unsigned char *)client->config.ca_cert_pem, 
                                     client->config.ca_cert_len);
        if (ret != 0) {
            printf("[MQTT] mbedtls_x509_crt_parse (CA) failed: -0x%04x\n", -ret);
            return false;
        }

        // Setup Socket
        printf("[MQTT] Connecting TCP socket to %s:%s...\n", client->config.host, port_str);
        ret = mbedtls_net_connect(&client->net_ctx, client->config.host, port_str, MBEDTLS_NET_PROTO_TCP);
        if (ret != 0) {
            printf("[MQTT] mbedtls_net_connect failed: -0x%04x\n", -ret);
            return false;
        }

        // Setup SSL Defaults
        ret = mbedtls_ssl_config_defaults(&client->ssl_conf,
                                          MBEDTLS_SSL_IS_CLIENT,
                                          MBEDTLS_SSL_TRANSPORT_STREAM,
                                          MBEDTLS_SSL_PRESET_DEFAULT);
        if (ret != 0) {
            printf("[MQTT] mbedtls_ssl_config_defaults failed: -0x%04x\n", -ret);
            return false;
        }

        mbedtls_ssl_conf_authmode(&client->ssl_conf, MBEDTLS_SSL_VERIFY_REQUIRED);
        mbedtls_ssl_conf_ca_chain(&client->ssl_conf, &client->ca_cert, NULL);
        mbedtls_ssl_conf_rng(&client->ssl_conf, mbedtls_ctr_drbg_random, &client->ctr_drbg);

        if ((ret = mbedtls_ssl_setup(&client->ssl_ctx, &client->ssl_conf)) != 0) {
            printf("[MQTT] mbedtls_ssl_setup failed: -0x%04x\n", -ret);
            return false;
        }

        if ((ret = mbedtls_ssl_set_hostname(&client->ssl_ctx, client->config.host)) != 0) {
            printf("[MQTT] mbedtls_ssl_set_hostname failed: -0x%04x\n", -ret);
            return false;
        }

        mbedtls_ssl_set_bio(&client->ssl_ctx, &client->net_ctx, mbedtls_net_send, mbedtls_net_recv, NULL);

        // Perform SSL/TLS Handshake
        printf("[MQTT] Performing TLS handshake...\n");
        while ((ret = mbedtls_ssl_handshake(&client->ssl_ctx)) != 0) {
            if (ret != MBEDTLS_ERR_SSL_WANT_READ && ret != MBEDTLS_ERR_SSL_WANT_WRITE) {
                printf("[MQTT] TLS handshake failed: -0x%04x\n", -ret);
                return false;
            }
        }

        // Verify Server Certificate
        uint32_t flags = mbedtls_ssl_get_verify_result(&client->ssl_ctx);
        if (flags != 0) {
            printf("[MQTT] Server certificate verification failed (flags 0x%08x)\n", flags);
            return false;
        }

        printf("[MQTT] TLS connection established successfully with %s:%s\n", client->config.host, port_str);
        client->is_connected = true;
        return true;
    }
#endif

    printf("[MQTT] Plain TCP connection established with %s:%s\n", client->config.host, port_str);
    client->is_connected = true;
    return true;
}

void mqtt_disconnect(mqtt_client_t *client) {
    if (!client || !client->is_connected) return;

#if ENABLE_MQTT_TLS
    if (client->config.use_tls) {
        mbedtls_ssl_close_notify(&client->ssl_ctx);
        mbedtls_net_free(&client->net_ctx);
        mbedtls_x509_crt_free(&client->ca_cert);
        mbedtls_x509_crt_free(&client->client_cert);
        mbedtls_pk_free(&client->client_key);
        mbedtls_ssl_free(&client->ssl_ctx);
        mbedtls_ssl_config_free(&client->ssl_conf);
        mbedtls_ctr_drbg_free(&client->ctr_drbg);
        mbedtls_entropy_free(&client->entropy);
    }
#endif

    client->is_connected = false;
    printf("[MQTT] Disconnected from broker.\n");
}
