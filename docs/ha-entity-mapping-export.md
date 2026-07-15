"""Home Assistant entity mapping export for HIRI protocol."""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class DeviceClass(str, Enum):
    """Home Assistant device classes."""
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    PRESSURE = "pressure"
    BATTERY = "battery"
    POWER = "power"
    ENERGY = "energy"
    CURRENT = "current"
    VOLTAGE = "voltage"
    ILLUMINANCE = "illuminance"
    MOTION = "motion"
    OCCUPANCY = "occupancy"
    DOOR = "door"
    WINDOW = "window"
    SWITCH = "switch"
    LIGHT = "light"


class StateClass(str, Enum):
    """Home Assistant state classes."""
    MEASUREMENT = "measurement"
    TOTAL = "total"
    TOTAL_INCREASING = "total_increasing"


@dataclass
class EntityMapping:
    """HIRI to Home Assistant entity mapping."""
    hiri_id: str
    entity_id: str
    friendly_name: str
    device_class: Optional[str] = None
    state_class: Optional[str] = None
    unit_of_measurement: Optional[str] = None
    icon: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None


@dataclass
class DeviceInfo:
    """Home Assistant device information."""
    identifiers: List[str]
    name: str
    manufacturer: str
    model: Optional[str] = None
    sw_version: Optional[str] = None
    hw_version: Optional[str] = None
    configuration_url: Optional[str] = None


@dataclass
class DiscoveryPayload:
    """Home Assistant MQTT discovery payload."""
    name: str
    unique_id: str
    state_topic: str
    device: DeviceInfo
    availability_topic: Optional[str] = None
    device_class: Optional[str] = None
    state_class: Optional[str] = None
    unit_of_measurement: Optional[str] = None
    icon: Optional[str] = None
    value_template: Optional[str] = None
    json_attributes_topic: Optional[str] = None
    command_topic: Optional[str] = None
    payload_on: Optional[str] = None
    payload_off: Optional[str] = None
    optimistic: Optional[bool] = None


class HAEntityExporter:
    """Export HIRI entity mappings for Home Assistant."""

    def __init__(self, mqtt_prefix: str = "homeassistant"):
        """Initialize exporter with MQTT discovery prefix."""
        self.mqtt_prefix = mqtt_prefix
        self.mappings: List[EntityMapping] = []

    def add_mapping(self, mapping: EntityMapping) -> None:
        """Add entity mapping."""
        self.mappings.append(mapping)

    def add_sensor(
        self,
        hiri_id: str,
        name: str,
        device_class: Optional[DeviceClass] = None,
        state_class: Optional[StateClass] = None,
        unit: Optional[str] = None,
        icon: Optional[str] = None,
    ) -> None:
        """Add sensor mapping."""
        entity_id = f"sensor.hiri_{hiri_id.lower().replace('-', '_')}"
        mapping = EntityMapping(
            hiri_id=hiri_id,
            entity_id=entity_id,
            friendly_name=name,
            device_class=device_class.value if device_class else None,
            state_class=state_class.value if state_class else None,
            unit_of_measurement=unit,
            icon=icon,
        )
        self.add_mapping(mapping)

    def add_binary_sensor(
        self,
        hiri_id: str,
        name: str,
        device_class: Optional[DeviceClass] = None,
        icon: Optional[str] = None,
    ) -> None:
        """Add binary sensor mapping."""
        entity_id = f"binary_sensor.hiri_{hiri_id.lower().replace('-', '_')}"
        mapping = EntityMapping(
            hiri_id=hiri_id,
            entity_id=entity_id,
            friendly_name=name,
            device_class=device_class.value if device_class else None,
            icon=icon,
        )
        self.add_mapping(mapping)

    def add_switch(
        self,
        hiri_id: str,
        name: str,
        icon: Optional[str] = None,
    ) -> None:
        """Add switch mapping."""
        entity_id = f"switch.hiri_{hiri_id.lower().replace('-', '_')}"
        mapping = EntityMapping(
            hiri_id=hiri_id,
            entity_id=entity_id,
            friendly_name=name,
            device_class="switch",
            icon=icon,
        )
        self.add_mapping(mapping)

    def generate_discovery_config(
        self,
        mapping: EntityMapping,
        device_info: DeviceInfo,
        state_topic_base: str = "hiri/state",
    ) -> Dict[str, Any]:
        """Generate Home Assistant MQTT discovery configuration."""
        component = mapping.entity_id.split(".")[0]
        object_id = mapping.entity_id.split(".")[1]

        config_topic = f"{self.mqtt_prefix}/{component}/{object_id}/config"
        state_topic = f"{state_topic_base}/{mapping.hiri_id}"

        payload = DiscoveryPayload(
            name=mapping.friendly_name,
            unique_id=f"hiri_{mapping.hiri_id}",
            state_topic=state_topic,
            device=device_info,
            availability_topic=f"{state_topic_base}/availability",
            device_class=mapping.device_class,
            state_class=mapping.state_class,
            unit_of_measurement=mapping.unit_of_measurement,
            icon=mapping.icon,
            value_template="{{ value_json.state }}",
            json_attributes_topic=state_topic,
        )

        if component == "switch":
            payload.command_topic = f"hiri/command/{mapping.hiri_id}"
            payload.payload_on = "ON"
            payload.payload_off = "OFF"
            payload.optimistic = False

        config_dict = asdict(payload)
        config_dict["device"] = asdict(device_info)
        
        # Remove None values
        config_dict = {k: v for k, v in config_dict.items() if v is not None}
        if "device" in config_dict:
            config_dict["device"] = {
                k: v for k, v in config_dict["device"].items() if v is not None
            }

        return {
            "topic": config_topic,
            "payload": config_dict,
        }

    def export_mappings(self) -> Dict[str, Any]:
        """Export all mappings as JSON."""
        return {
            "version": "1.0.0",
            "protocol": "HIRI",
            "mqtt_prefix": self.mqtt_prefix,
            "mappings": [
                {
                    "hiri_id": m.hiri_id,
                    "entity_id": m.entity_id,
                    "friendly_name": m.friendly_name,
                    "device_class": m.device_class,
                    "state_class": m.state_class,
                    "unit_of_measurement": m.unit_of_measurement,
                    "icon": m.icon,
                    "attributes": m.attributes,
                }
                for m in self.mappings
            ],
        }

    def export_discovery_configs(
        self, device_info: DeviceInfo
    ) -> List[Dict[str, Any]]:
        """Export Home Assistant discovery configurations for all mappings."""
        return [
            self.generate_discovery_config(mapping, device_info)
            for mapping in self.mappings
        ]

    def export_to_file(self, filename: str) -> None:
        """Export mappings to JSON file."""
        with open(filename, "w") as f:
            json.dump(self.export_mappings(), f, indent=2)

    def export_discovery_to_file(
        self, filename: str, device_info: DeviceInfo
    ) -> None:
        """Export discovery configurations to JSON file."""
        configs = self.export_discovery_configs(device_info)
        with open(filename, "w") as f:
            json.dump({"discoveries": configs}, f, indent=2)


def create_default_mappings() -> HAEntityExporter:
    """Create default HIRI to Home Assistant entity mappings."""
    exporter = HAEntityExporter()

    # Environmental sensors
    exporter.add_sensor(
        "temp-001",
        "Room Temperature",
        DeviceClass.TEMPERATURE,
        StateClass.MEASUREMENT,
        "°C",
        "mdi:thermometer",
    )
    exporter.add_sensor(
        "humidity-001",
        "Room Humidity",
        DeviceClass.HUMIDITY,
        StateClass.MEASUREMENT,
        "%",
        "mdi:water-percent",
    )
    exporter.add_sensor(
        "pressure-001",
        "Atmospheric Pressure",
        DeviceClass.PRESSURE,
        StateClass.MEASUREMENT,
        "hPa",
        "mdi:gauge",
    )

    # Power monitoring
    exporter.add_sensor(
        "power-001",
        "Power Consumption",
        DeviceClass.POWER,
        StateClass.MEASUREMENT,
        "W",
        "mdi:flash",
    )
    exporter.add_sensor(
        "energy-001",
        "Energy Usage",
        DeviceClass.ENERGY,
        StateClass.TOTAL_INCREASING,
        "kWh",
        "mdi:lightning-bolt",
    )

    # Binary sensors
    exporter.add_binary_sensor(
        "motion-001", "Motion Detected", DeviceClass.MOTION, "mdi:motion-sensor"
    )
    exporter.add_binary_sensor(
        "door-001", "Front Door", DeviceClass.DOOR, "mdi:door"
    )
    exporter.add_binary_sensor(
        "window-001", "Living Room Window", DeviceClass.WINDOW, "mdi:window-closed"
    )

    # Switches
    exporter.add_switch("switch-001", "Main Light", "mdi:lightbulb")
    exporter.add_switch("switch-002", "Fan", "mdi:fan")

    return exporter


if __name__ == "__main__":
    # Example usage
    exporter = create_default_mappings()

    device_info = DeviceInfo(
        identifiers=["hiri_device_001"],
        name="HIRI Protocol Device",
        manufacturer="HIRI",
        model="v1.0",
        sw_version="1.0.0",
        configuration_url="http://hiri.local",
    )

    # Export mappings
    exporter.export_to_file("ha_entity_mappings.json")
    print("Entity mappings exported to ha_entity_mappings.json")

    # Export discovery configurations
    exporter.export_discovery_to_file("ha_discovery_configs.json", device_info)
    print("Discovery configurations exported to ha_discovery_configs.json")

    # Print sample output
    print("\nSample mapping:")
    print(json.dumps(exporter.export_mappings(), indent=2))