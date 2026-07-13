from __future__ import annotations

from hiri_bridge.devices.types import Device

# Home Assistant MQTT discovery topic prefix
DISCOVERY_PREFIX = "homeassistant"


def discovery_topic(device: Device) -> str:
    # homeassistant/<component>/<node_id>/<object_id>/config
    node = "hiri"
    object_id = device.id.replace(".", "_")
    return f"{DISCOVERY_PREFIX}/{device.domain}/{node}/{object_id}/config"


def state_topic(device: Device) -> str:
    return f"hiri/state/{device.id.replace('.', '/')}"


def command_topic(device: Device) -> str:
    return f"hiri/cmd/{device.id.replace('.', '/')}"


def discovery_payload(device: Device) -> dict:
    """Build HA MQTT discovery config for a device."""
    base = {
        "name": device.name,
        "unique_id": f"hiri_{device.id.replace('.', '_')}",
        "state_topic": state_topic(device),
        "availability_topic": "hiri/status",
        "payload_available": "online",
        "payload_not_available": "offline",
        "device": {
            "identifiers": [f"hiri_{device.id}"],
            "manufacturer": device.manufacturer,
            "model": device.model,
            "name": device.name,
            "suggested_area": device.area,
        },
    }
    domain = device.domain
    if domain in {"light", "switch", "fan", "siren", "humidifier"}:
        base["command_topic"] = command_topic(device)
        base["payload_on"] = "ON"
        base["payload_off"] = "OFF"
    if domain == "light":
        base["brightness"] = True
        base["brightness_scale"] = 255
        base["supported_color_modes"] = ["brightness", "color_temp"]
        if device.attributes.get("rgb"):
            base["supported_color_modes"] = ["rgb", "brightness", "color_temp"]
        if device.attributes.get("effect_list"):
            base["effect"] = True
            base["effect_list"] = device.attributes["effect_list"]
    if domain == "climate":
        base["modes"] = device.attributes.get(
            "hvac_modes", ["off", "heat", "cool", "auto"]
        )
        base["min_temp"] = device.attributes.get("min_temp", 16)
        base["max_temp"] = device.attributes.get("max_temp", 30)
        base["temp_step"] = 0.5
        base["current_temperature_topic"] = state_topic(device)
        base["mode_command_topic"] = command_topic(device) + "/mode"
        base["temperature_command_topic"] = command_topic(device) + "/temp"
        preset_modes = device.attributes.get("preset_modes")
        if preset_modes:
            base["preset_modes"] = preset_modes
            base["preset_mode_command_topic"] = command_topic(device) + "/preset"
            base["preset_mode_state_topic"] = state_topic(device) + "/preset"
    if domain == "cover":
        base["command_topic"] = command_topic(device)
        base["position_topic"] = state_topic(device) + "/position"
        base["set_position_topic"] = command_topic(device)
        base["payload_open"] = "OPEN"
        base["payload_close"] = "CLOSE"
        base["payload_stop"] = "STOP"
        base["position_open"] = 100
        base["position_closed"] = 0
        if device.attributes.get("tilt"):
            base["tilt_status_topic"] = state_topic(device) + "/tilt"
            base["tilt_command_topic"] = command_topic(device) + "/tilt"
            base["tilt_min"] = 0
            base["tilt_max"] = 100
    if domain == "fan":
        base["percentage"] = True
        base["preset_modes"] = device.attributes.get("preset_modes", ["low", "medium", "high"])
        base["percentage_command_topic"] = command_topic(device)
        base["preset_mode_command_topic"] = command_topic(device) + "/preset"
        base["preset_mode_state_topic"] = state_topic(device) + "/preset"
    if domain == "humidifier":
        base["target_humidity_command_topic"] = command_topic(device) + "/humidity"
        base["current_humidity_topic"] = state_topic(device) + "/current_humidity"
        base["min_humidity"] = device.attributes.get("min_humidity", 30)
        base["max_humidity"] = device.attributes.get("max_humidity", 80)
        modes = device.attributes.get("modes")
        if modes:
            base["modes"] = modes
            base["mode_command_topic"] = command_topic(device) + "/mode"
            base["mode_state_topic"] = state_topic(device) + "/mode"
    if domain == "sensor":
        base["unit_of_measurement"] = device.attributes.get("unit_of_measurement", "")
        dev_class = device.attributes.get("device_class")
        base["device_class"] = dev_class
        # Cumulative meters (energy/gas/water/volume) must report
        # total_increasing so HA long-term statistics + the Energy dashboard
        # treat them as running totals rather than instantaneous readings.
        total_classes = {"energy", "gas", "water", "volume", "precipitation"}
        base["state_class"] = device.attributes.get(
            "state_class",
            "total_increasing" if dev_class in total_classes else "measurement",
        )
        if "last_reset" in device.attributes:
            base["last_reset_value_template"] = device.attributes["last_reset"]
    if domain == "binary_sensor":
        base["device_class"] = device.attributes.get("device_class", "opening")
        base["payload_on"] = "ON"
        base["payload_off"] = "OFF"
        if "off_delay" in device.attributes:
            # Auto-clear after N seconds (e.g. motion/PIR sensors)
            base["off_delay"] = device.attributes["off_delay"]
        if "expire_after" in device.attributes:
            base["expire_after"] = device.attributes["expire_after"]
        if device.attributes.get("battery"):
            # Battery-powered contact: expose a JSON attributes topic so HA
            # can surface the battery level reported alongside the state.
            base["json_attributes_topic"] = state_topic(device) + "/attributes"
    if domain == "lock":
        base["command_topic"] = command_topic(device)
        base["payload_lock"] = "LOCK"
        base["payload_unlock"] = "UNLOCK"
        base["state_locked"] = "LOCKED"
        base["state_unlocked"] = "UNLOCKED"
        if device.attributes.get("code_required"):
            # PIN/door-code stub: HA expects a code_format regex and a
            # dedicated topic reporting whether a code was set locally.
            base["code_format"] = device.attributes.get("code_format", "^[0-9]{4,8}$")
            base["code_state_topic"] = state_topic(device) + "/code"
    if domain == "number":
        base["command_topic"] = command_topic(device)
        base["min"] = device.attributes.get("min", 0)
        base["max"] = device.attributes.get("max", 100)
        base["step"] = device.attributes.get("step", 1)
    if domain == "select":
        base["command_topic"] = command_topic(device)
        base["options"] = device.attributes.get("options", [])
        # HA select needs a value template pointing at the reported option so
        # the frontend reflects the active choice instead of the raw payload.
        base["value_template"] = "{{ value_json.option }}"
    if domain == "button":
        base["command_topic"] = command_topic(device)
        base["payload_press"] = "PRESS"
    if domain == "camera":
        base["topic"] = state_topic(device)
    if domain == "vacuum":
        base["command_topic"] = command_topic(device)
        base["supported_features"] = ["start", "return_home", "battery"]
    if domain == "media_player":
        base["command_topic"] = command_topic(device)
        # Expose selectable inputs + volume/source support so HA renders the
        # source dropdown and the right transport controls.
        source_list = device.attributes.get("source_list")
        if source_list:
            base["source_list"] = source_list
            base["source_command_topic"] = command_topic(device) + "/source"
        base["supported_features"] = device.attributes.get(
            "supported_features",
            ["turn_on", "turn_off", "play", "pause", "volume_set"],
        )
    if domain == "alarm_control_panel":
        base["command_topic"] = command_topic(device)
        base["supported_features"] = device.attributes.get(
            "supported_features",
            ["arm_home", "arm_away", "arm_night", "arm_vacation", "trigger"],
        )
        # Advertise whether a code is required to arm/disarm so HA renders the
        # keypad instead of bare arm buttons.
        base["code_arm_required"] = device.attributes.get("code_arm_required", False)
        base["code_disarm_required"] = device.attributes.get("code_disarm_required", False)
    if domain == "water_heater":
        base["command_topic"] = command_topic(device)
        base["temperature_unit"] = "C"
        base["min_temp"] = device.attributes.get("min_temp", 30)
        base["max_temp"] = device.attributes.get("max_temp", 70)
        # Expose operation modes (incl. eco/away) + a dedicated mode topic so
        # HA can toggle away mode instead of only setting a target temperature.
        modes = device.attributes.get("modes")
        if modes:
            base["modes"] = modes
            base["mode_command_topic"] = command_topic(device) + "/mode"
            base["mode_state_topic"] = state_topic(device) + "/mode"
    return base


def export_discovery(devices: list[Device]) -> list[dict]:
    out = []
    for d in devices:
        out.append(
            {
                "topic": discovery_topic(d),
                "payload": discovery_payload(d),
                "state_topic": state_topic(d),
                "command_topic": command_topic(d) if d.domain != "sensor" else None,
                "device_id": d.id,
            }
        )
    return out
