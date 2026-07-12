from __future__ import annotations

import json
from pathlib import Path

from hiri_bridge.config import REGISTRY_PATH
from hiri_bridge.devices.types import DOMAINS, Device


def default_seed_devices() -> list[Device]:
    """Broad demo registry covering major HA domains."""
    seeds = [
        Device(
            id="light.living_main",
            name="Living room light",
            domain="light",
            model="HIRI-RGBW",
            area="living",
            state={"state": "off", "brightness": 0, "color_temp": 350, "effect": "none"},
            attributes={
                "rgb": True,
                "effect_list": ["none", "colorloop", "pulse"],
            },
        ),
        Device(
            id="switch.pump_a",
            name="Farm pump A",
            domain="switch",
            model="HIRI-RELAY",
            area="farm",
            state={"state": "off"},
            adapter="mqtt",
        ),
        Device(
            id="binary_sensor.door_front",
            name="Front door",
            domain="binary_sensor",
            model="HIRI-CONTACT",
            area="entry",
            state={"state": "off"},
            attributes={"device_class": "door"},
        ),
        Device(
            id="sensor.soil_moisture_1",
            name="Soil moisture bed 1",
            domain="sensor",
            model="HIRI-SOIL",
            area="farm",
            state={"state": 42.5},
            attributes={"unit_of_measurement": "%", "device_class": "moisture"},
            adapter="mqtt",
        ),
        Device(
            id="sensor.temp_greenhouse",
            name="Greenhouse temperature",
            domain="sensor",
            model="HIRI-TH",
            area="farm",
            state={"state": 28.1},
            attributes={"unit_of_measurement": "°C", "device_class": "temperature"},
        ),
        Device(
            id="climate.bedroom_ac",
            name="Bedroom AC",
            domain="climate",
            model="HIRI-AC",
            area="bedroom",
            state={"hvac_mode": "off", "temperature": 26, "current_temperature": 29},
            attributes={
                "hvac_modes": ["off", "heat", "cool", "auto", "dry", "fan_only"],
                "min_temp": 16,
                "max_temp": 30,
                "preset_modes": ["eco", "boost", "sleep"],
            },
        ),
        Device(
            id="cover.garage",
            name="Garage door",
            domain="cover",
            model="HIRI-COVER",
            area="garage",
            state={"state": "closed", "position": 0, "tilt": 0},
        ),
        Device(
            id="lock.front",
            name="Front lock",
            domain="lock",
            model="HIRI-LOCK",
            area="entry",
            state={"state": "locked"},
        ),
        Device(
            id="fan.ceiling_lr",
            name="Ceiling fan",
            domain="fan",
            model="HIRI-FAN",
            area="living",
            state={"state": "off", "percentage": 0, "preset_mode": "low"},
            attributes={"preset_modes": ["low", "medium", "high", "breeze"]},
        ),
        Device(
            id="media_player.tv_living",
            name="Living TV",
            domain="media_player",
            model="HIRI-TV",
            area="living",
            state={"state": "off", "volume_level": 0.2},
        ),
        Device(
            id="vacuum.bot_1",
            name="Vacuum bot",
            domain="vacuum",
            model="HIRI-VAC",
            area="home",
            state={"state": "docked", "battery": 100},
        ),
        Device(
            id="camera.yard",
            name="Yard camera",
            domain="camera",
            model="HIRI-CAM",
            area="yard",
            state={"state": "idle"},
            attributes={"stream_url": "rtsp://192.0.2.10/stream"},
        ),
        Device(
            id="button.panic",
            name="Panic button",
            domain="button",
            model="HIRI-BTN",
            area="entry",
            state={},
        ),
        Device(
            id="number.feed_dose",
            name="Feed dose ml",
            domain="number",
            model="HIRI-DOSE",
            area="farm",
            state={"value": 50},
            attributes={"min": 0, "max": 500, "step": 10, "unit": "ml"},
        ),
        Device(
            id="select.mode_farm",
            name="Farm mode",
            domain="select",
            model="HIRI-MODE",
            area="farm",
            state={"option": "auto"},
            attributes={"options": ["auto", "manual", "sleep"]},
        ),
        Device(
            id="siren.alarm",
            name="Siren",
            domain="siren",
            model="HIRI-SIREN",
            area="home",
            state={"state": "off"},
        ),
        Device(
            id="humidifier.bedroom",
            name="Bedroom humidifier",
            domain="humidifier",
            model="HIRI-HUM",
            area="bedroom",
            state={"state": "off", "humidity": 55},
        ),
        Device(
            id="water_heater.boiler",
            name="Boiler",
            domain="water_heater",
            model="HIRI-WH",
            area="utility",
            state={"state": "off", "temperature": 45},
        ),
        Device(
            id="alarm_control_panel.home",
            name="Home alarm",
            domain="alarm_control_panel",
            model="HIRI-ALARM",
            area="home",
            state={"state": "disarmed"},
        ),
        Device(
            id="binary_sensor.window_kitchen",
            name="Kitchen window",
            domain="binary_sensor",
            model="HIRI-CONTACT",
            area="kitchen",
            state={"state": "off"},
            attributes={"device_class": "window"},
        ),
        Device(
            id="sensor.pm25_living",
            name="Living PM2.5",
            domain="sensor",
            model="HIRI-AQI",
            area="living",
            state={"state": 12.0},
            attributes={"unit_of_measurement": "µg/m³", "device_class": "pm25"},
            adapter="mqtt",
        ),
        Device(
            id="sensor.battery_gate",
            name="Gate sensor battery",
            domain="sensor",
            model="HIRI-BATT",
            area="entry",
            state={"state": 87},
            attributes={"unit_of_measurement": "%", "device_class": "battery"},
            adapter="mqtt",
        ),
        Device(
            id="fan.living_ceiling",
            name="Living ceiling fan",
            domain="fan",
            model="HIRI-FAN",
            area="living",
            state={"state": "off", "percentage": 0, "oscillating": False},
            attributes={"percentage_step": 25, "preset_modes": ["breeze", "sleep"]},
        ),
        Device(
            id="sensor.co2_office",
            name="Office CO2",
            domain="sensor",
            model="HIRI-CO2",
            area="office",
            state={"state": 640.0},
            attributes={"unit_of_measurement": "ppm", "device_class": "carbon_dioxide"},
            adapter="mqtt",
        ),
        Device(
            id="switch.irrigation_bed1",
            name="Irrigation bed 1",
            domain="switch",
            model="HIRI-RELAY",
            area="farm",
            state={"state": "off"},
            adapter="mqtt",
        ),
        Device(
            id="light.office_desk",
            name="Office desk lamp",
            domain="light",
            model="HIRI-RGBW",
            area="office",
            state={"state": "off", "brightness": 0, "color_temp": 320},
            attributes={"rgb": True},
        ),
        Device(
            id="binary_sensor.motion_hall",
            name="Hall motion",
            domain="binary_sensor",
            model="HIRI-PIR",
            area="entry",
            state={"state": "off"},
            attributes={"device_class": "motion"},
            adapter="mqtt",
        ),
        Device(
            id="sensor.humidity_bathroom",
            name="Bathroom humidity",
            domain="sensor",
            model="HIRI-TH",
            area="bathroom",
            state={"state": 62.0},
            attributes={"unit_of_measurement": "%", "device_class": "humidity"},
            adapter="mqtt",
        ),
        Device(
            id="switch.exhaust_fan",
            name="Bathroom exhaust",
            domain="switch",
            model="HIRI-RELAY",
            area="bathroom",
            state={"state": "off"},
            adapter="mqtt",
        ),
        Device(
            id="sensor.illuminance_desk",
            name="Desk illuminance",
            domain="sensor",
            model="HIRI-LUX",
            area="office",
            state={"state": 320.0},
            attributes={"unit_of_measurement": "lx", "device_class": "illuminance"},
            adapter="mqtt",
        ),
        Device(
            id="light.hallway_strip",
            name="Hallway LED strip",
            domain="light",
            model="HIRI-RGBW",
            area="entry",
            state={"state": "off", "brightness": 0, "color_temp": 300},
            attributes={"rgb": True, "effect_list": ["none", "pulse"]},
        ),
    ]
    return seeds


class DeviceRegistry:
    def __init__(self, path: Path | None = None):
        self.path = path or REGISTRY_PATH
        self._devices: dict[str, Device] = {}

    def load_or_seed(self) -> None:
        if self.path.exists():
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            self._devices = {d["id"]: Device.model_validate(d) for d in raw}
        else:
            self.seed()

    def seed(self) -> None:
        self._devices = {d.id: d for d in default_seed_devices()}
        self.save()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [d.model_dump() for d in self._devices.values()]
        self.path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def list(self) -> list[Device]:
        return sorted(self._devices.values(), key=lambda d: d.id)

    def get(self, device_id: str) -> Device | None:
        return self._devices.get(device_id)

    def upsert(self, device: Device) -> Device:
        self._devices[device.id] = device
        self.save()
        return device

    def apply_command(self, device_id: str, action: str, data: dict | None = None) -> Device:
        dev = self._devices.get(device_id)
        if not dev:
            raise KeyError(f"unknown device {device_id}")
        data = data or {}
        state = dict(dev.state)
        domain = dev.domain
        if domain in {"light", "switch", "fan", "siren", "humidifier", "water_heater"}:
            if action in {"turn_on", "on"}:
                state["state"] = "on"
                if "brightness" in data:
                    state["brightness"] = data["brightness"]
                if "percentage" in data:
                    state["percentage"] = data["percentage"]
                if "color_temp" in data:
                    state["color_temp"] = data["color_temp"]
                if "rgb_color" in data:
                    state["rgb_color"] = data["rgb_color"]
                if "effect" in data:
                    state["effect"] = data["effect"]
                if "preset_mode" in data:
                    state["preset_mode"] = data["preset_mode"]
            elif action in {"turn_off", "off"}:
                state["state"] = "off"
                if "brightness" in state:
                    state["brightness"] = 0
                if "percentage" in state:
                    state["percentage"] = 0
            elif action == "set_percentage" and domain == "fan":
                state["percentage"] = int(data.get("percentage", 50))
                state["state"] = "on" if state["percentage"] else "off"
            elif action == "set_preset_mode" and domain == "fan":
                state["preset_mode"] = data.get("preset_mode", "low")
                state["state"] = "on"
        elif domain == "lock":
            if action == "lock":
                state["state"] = "locked"
            elif action == "unlock":
                state["state"] = "unlocked"
            if "code" in data:
                state["last_code_set"] = bool(data["code"])
        elif domain == "cover":
            if action == "open":
                state["state"] = "open"
                state["position"] = 100
            elif action == "close":
                state["state"] = "closed"
                state["position"] = 0
            elif action == "set_position":
                pos = int(data.get("position", 50))
                state["position"] = pos
                state["state"] = "open" if pos > 0 else "closed"
            elif action == "set_tilt":
                state["tilt"] = int(data.get("tilt", 0))
        elif domain == "climate":
            if "hvac_mode" in data:
                state["hvac_mode"] = data["hvac_mode"]
            if "temperature" in data:
                state["temperature"] = data["temperature"]
            if "preset_mode" in data:
                state["preset_mode"] = data["preset_mode"]
            if action in {"set_hvac_mode", "set_temperature", "set_preset_mode"}:
                if "hvac_mode" in data:
                    state["hvac_mode"] = data["hvac_mode"]
                if "temperature" in data:
                    state["temperature"] = data["temperature"]
                if "preset_mode" in data:
                    state["preset_mode"] = data["preset_mode"]
        elif domain == "number":
            if "value" in data:
                state["value"] = data["value"]
        elif domain == "select":
            if "option" in data:
                state["option"] = data["option"]
        elif domain == "button":
            state["last_pressed"] = action or "press"
        elif domain == "vacuum":
            if action in {"start", "return_to_base", "dock"}:
                state["state"] = "cleaning" if action == "start" else "docked"
        elif domain == "alarm_control_panel":
            if action in {"arm_home", "arm_away", "disarm"}:
                state["state"] = {
                    "arm_home": "armed_home",
                    "arm_away": "armed_away",
                    "disarm": "disarmed",
                }[action]
        elif domain == "media_player":
            if action in {"turn_on", "turn_off", "play", "pause"}:
                state["state"] = "off" if action == "turn_off" else "playing" if action == "play" else "idle"
            if "volume_level" in data:
                state["volume_level"] = data["volume_level"]
        else:
            state["last_action"] = action
            state.update(data)
        dev = dev.model_copy(update={"state": state})
        self._devices[device_id] = dev
        self.save()
        return dev

    def stats(self) -> dict:
        by_domain: dict[str, int] = {}
        for d in self._devices.values():
            by_domain[d.domain] = by_domain.get(d.domain, 0) + 1
        return {
            "total": len(self._devices),
            "online": sum(1 for d in self._devices.values() if d.online),
            "by_domain": by_domain,
            "supported_domains": DOMAINS,
        }
