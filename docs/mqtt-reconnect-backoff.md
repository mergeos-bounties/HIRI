import { EventEmitter } from 'events';
import mqtt, { MqttClient, IClientOptions } from 'mqtt';

interface MQTTAdapterConfig {
  brokerUrl: string;
  clientId?: string;
  username?: string;
  password?: string;
  reconnectOptions?: {
    initialDelay?: number;
    maxDelay?: number;
    multiplier?: number;
    jitter?: number;
  };
}

export class MQTTAdapter extends EventEmitter {
  private client: MqttClient | null = null;
  private config: MQTTAdapterConfig;
  private reconnectAttempts = 0;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private isManualDisconnect = false;
  
  private readonly DEFAULT_INITIAL_DELAY = 1000;
  private readonly DEFAULT_MAX_DELAY = 60000;
  private readonly DEFAULT_MULTIPLIER = 2;
  private readonly DEFAULT_JITTER = 0.3;

  constructor(config: MQTTAdapterConfig) {
    super();
    this.config = config;
  }

  public connect(): void {
    if (this.client?.connected) {
      return;
    }

    this.isManualDisconnect = false;
    const options: IClientOptions = {
      clientId: this.config.clientId,
      username: this.config.username,
      password: this.config.password,
      clean: true,
      reconnectPeriod: 0,
    };

    this.client = mqtt.connect(this.config.brokerUrl, options);

    this.client.on('connect', () => {
      this.reconnectAttempts = 0;
      this.emit('connected');
    });

    this.client.on('error', (error) => {
      const sanitizedError = this.sanitizeError(error);
      this.emit('error', sanitizedError);
    });

    this.client.on('close', () => {
      if (!this.isManualDisconnect) {
        this.scheduleReconnect();
      }
      this.emit('disconnected');
    });

    this.client.on('message', (topic: string, payload: Buffer) => {
      this.emit('message', topic, payload);
    });
  }

  public disconnect(): void {
    this.isManualDisconnect = true;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.client) {
      this.client.end(true);
      this.client = null;
    }
    this.reconnectAttempts = 0;
  }

  public publish(topic: string, message: string | Buffer, qos: 0 | 1 | 2 = 0): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.client?.connected) {
        reject(new Error('MQTT client not connected'));
        return;
      }

      this.client.publish(topic, message, { qos }, (error) => {
        if (error) {
          reject(this.sanitizeError(error));
        } else {
          resolve();
        }
      });
    });
  }

  public subscribe(topic: string, qos: 0 | 1 | 2 = 0): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.client?.connected) {
        reject(new Error('MQTT client not connected'));
        return;
      }

      this.client.subscribe(topic, { qos }, (error) => {
        if (error) {
          reject(this.sanitizeError(error));
        } else {
          resolve();
        }
      });
    });
  }

  public unsubscribe(topic: string): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.client?.connected) {
        reject(new Error('MQTT client not connected'));
        return;
      }

      this.client.unsubscribe(topic, (error) => {
        if (error) {
          reject(this.sanitizeError(error));
        } else {
          resolve();
        }
      });
    });
  }

  public isConnected(): boolean {
    return this.client?.connected ?? false;
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimer) {
      return;
    }

    const delay = this.calculateBackoffDelay();
    this.reconnectAttempts++;

    this.emit('reconnecting', { attempt: this.reconnectAttempts, delay });

    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      if (this.client) {
        this.client.removeAllListeners();
        this.client.end(true);
        this.client = null;
      }
      this.connect();
    }, delay);
  }

  private calculateBackoffDelay(): number {
    const options = this.config.reconnectOptions || {};
    const initialDelay = options.initialDelay ?? this.DEFAULT_INITIAL_DELAY;
    const maxDelay = options.maxDelay ?? this.DEFAULT_MAX_DELAY;
    const multiplier = options.multiplier ?? this.DEFAULT_MULTIPLIER;
    const jitterFactor = options.jitter ?? this.DEFAULT_JITTER;

    const exponentialDelay = Math.min(
      initialDelay * Math.pow(multiplier, this.reconnectAttempts),
      maxDelay
    );

    const jitter = exponentialDelay * jitterFactor * (Math.random() * 2 - 1);
    const delayWithJitter = Math.max(0, exponentialDelay + jitter);

    return Math.floor(delayWithJitter);
  }

  private sanitizeError(error: Error): Error {
    const sanitized = new Error(error.message);
    sanitized.name = error.name;
    sanitized.stack = error.stack?.replace(
      /(password|token|key|secret|auth)[=:]\s*[^\s&,]+/gi,
      '$1=***'
    );
    
    if ('message' in error) {
      sanitized.message = error.message.replace(
        /(password|token|key|secret|auth)[=:]\s*[^\s&,]+/gi,
        '$1=***'
      );
    }

    return sanitized;
  }
}

export default MQTTAdapter;