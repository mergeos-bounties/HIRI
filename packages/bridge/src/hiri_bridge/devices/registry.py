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
            id="binary_sensor.window_bedroom",
            name="Bedroom window",
            domain="binary_sensor",
            model="HIRI-CONTACT-BAT",
            area="bedroom",
            state={"state": "off", "battery": 87},
            attributes={
                "device_class": "window",
                "battery": True,
                "expire_after": 3600,
            },
            adapter="mqtt",
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
            id="cover.living_blinds",
            name="Living room blinds",
            domain="cover",
            model="HIRI-BLIND",
            area="living",
            state={"state": "open", "position": 100, "tilt": 50},
            attributes={"tilt": True, "device_class": "blind"},
        ),
        Device(
            id="climate.living_thermostat",
            name="Living room thermostat",
            domain="climate",
            model="HIRI-THERMO",
            area="living",
            state={
                "hvac_mode": "heat",
                "temperature": 21,
                "current_temperature": 19,
                "preset_mode": "comfort",
            },
            attributes={
                "hvac_modes": ["off", "heat", "cool", "auto"],
                "min_temp": 7,
                "max_temp": 35,
                "preset_modes": ["comfort", "eco", "away", "boost"],
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
            id="lock.side_gate",
            name="Side gate keypad",
            domain="lock",
            model="HIRI-KEYPAD",
            area="garden",
            state={"state": "locked", "code_set": False},
            attributes={
                "code_required": True,
                "code_format": "^[0-9]{4,6}$",
                "supported_features": ["lock", "unlock", "open"],
            },
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
            state={"state": "off", "volume_level": 0.2, "source": "HDMI 1"},
            attributes={
                "source_list": ["HDMI 1", "HDMI 2", "Netflix", "YouTube", "TV"],
            },
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
            id="select.scene_living",
            name="Living room scene",
            domain="select",
            model="HIRI-SCENE",
            area="living",
            state={"option": "day"},
            attributes={
                "options": ["day", "night", "movie", "party", "away"],
            },
            adapter="mqtt",
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
            state={"state": "off", "humidity": 55, "target_humidity": 50, "mode": "normal"},
            attributes={
                "modes": ["normal", "eco", "away", "sleep", "boost"],
                "min_humidity": 30,
                "max_humidity": 80,
            },
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
            attributes={
                "code_arm_required": True,
                "code_disarm_required": True,
                "code": "1234",
            },
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
            attributes={"device_class": "motion", "off_delay": 30},
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
        Device(
            id="sensor.power_panel",
            name="Panel power",
            domain="sensor",
            model="HIRI-PWR",
            area="utility",
            state={"state": 412.0},
            attributes={"unit_of_measurement": "W", "device_class": "power"},
            adapter="mqtt",
        ),
        Device(
            id="sensor.panel_energy",
            name="Panel energy",
            domain="sensor",
            model="HIRI-PWR",
            area="utility",
            state={"state": 1834.7},
            attributes={
                "unit_of_measurement": "kWh",
                "device_class": "energy",
            },
            adapter="mqtt",
        ),
        Device(
            id="switch.washer",
            name="Washer outlet",
            domain="switch",
            model="HIRI-RELAY",
            area="utility",
            state={"state": "off"},
            adapter="mqtt",
        ),
        Device(
            id="binary_sensor.smoke_kitchen",
            name="Kitchen smoke",
            domain="binary_sensor",
            model="HIRI-SMOKE",
            area="kitchen",
            state={"state": "off"},
            attributes={"device_class": "smoke"},
            adapter="mqtt",
        ),
        Device(
            id="switch.range_hood",
            name="Range hood",
            domain="switch",
            model="HIRI-RELAY",
            area="kitchen",
            state={"state": "off"},
            adapter="mqtt",
        ),
        Device(
            id="sensor.noise_living",
            name="Living room noise",
            domain="sensor",
            model="HIRI-DB",
            area="living",
            state={"state": 38.0},
            attributes={"unit_of_measurement": "dB", "device_class": "sound_pressure"},
            adapter="mqtt",
        ),
        Device(
            id="media_player.speaker_kitchen",
            name="Kitchen speaker",
            domain="media_player",
            model="HIRI-SPK",
            area="kitchen",
            state={"state": "off", "volume_level": 0.25},
        ),
        Device(
            id="binary_sensor.leak_laundry",
            name="Laundry leak",
            domain="binary_sensor",
            model="HIRI-LEAK",
            area="utility",
            state={"state": "off"},
            attributes={"device_class": "moisture"},
            adapter="mqtt",
        ),
        Device(
            id="switch.water_shutoff",
            name="Main water shutoff",
            domain="switch",
            model="HIRI-RELAY",
            area="utility",
            state={"state": "off"},
            adapter="mqtt",
        ),
        Device(
            id="sensor.voc_office",
            name="Office VOC",
            domain="sensor",
            model="HIRI-VOC",
            area="office",
            state={"state": 180.0},
            attributes={"unit_of_measurement": "ppb", "device_class": "volatile_organic_compounds"},
            adapter="mqtt",
        ),
        Device(
            id="fan.office_exhaust",
            name="Office exhaust fan",
            domain="fan",
            model="HIRI-FAN",
            area="office",
            state={"state": "off", "percentage": 0},
            attributes={"percentage_step": 25},
        ),
        Device(
            id="sensor.humidity_bathroom",
            name="Bathroom humidity",
            domain="sensor",
            model="HIRI-RH",
            area="bathroom",
            state={"state": 62.0},
            attributes={"unit_of_measurement": "%", "device_class": "humidity"},
            adapter="mqtt",
        ),
        Device(
            id="fan.bathroom_exhaust",
            name="Bathroom exhaust fan",
            domain="fan",
            model="HIRI-FAN",
            area="bathroom",
            state={"state": "off", "percentage": 0},
            attributes={"percentage_step": 25},
        ),
        Device(
            id="binary_sensor.door_front",
            name="Front door contact",
            domain="binary_sensor",
            model="HIRI-DOOR",
            area="entry",
            state={"state": "off"},
            attributes={"device_class": "door"},
            adapter="mqtt",
        ),
        Device(
            id="lock.front_door",
            name="Front door lock",
            domain="lock",
            model="HIRI-LOCK",
            area="entry",
            state={"state": "locked"},
            attributes={"supported_features": ["lock", "unlock"]},
            adapter="mqtt",
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
            elif action == "set_humidity" and domain == "humidifier":
                lo = dev.attributes.get("min_humidity", 30)
                hi = dev.attributes.get("max_humidity", 80)
                target = int(data.get("humidity", 50))
                state["target_humidity"] = max(lo, min(hi, target))
                state["state"] = "on"
            elif action == "set_mode" and domain == "humidifier":
                mode = data.get("mode")
                if mode in dev.attributes.get("modes", []):
                    state["mode"] = mode
                    state["state"] = "on"
        elif domain == "lock":
            if action == "lock":
                state["state"] = "locked"
            elif action == "unlock":
                state["state"] = "unlocked"
            elif action == "open":
                state["state"] = "open"
            if "code" in data:
                state["last_code_set"] = bool(data["code"])
                if "code_set" in state:
                    state["code_set"] = bool(data["code"])
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
            if "option" in data and data["option"] in dev.attributes.get("options", []):
                state["option"] = data["option"]
        elif domain == "button":
            state["last_pressed"] = action or "press"
        elif domain == "vacuum":
            if action in {"start", "return_to_base", "dock"}:
                state["state"] = "cleaning" if action == "start" else "docked"
        elif domain == "alarm_control_panel":
            arm_map = {
                "arm_home": "armed_home",
                "arm_away": "armed_away",
                "arm_night": "armed_night",
                "arm_vacation": "armed_vacation",
                "disarm": "disarmed",
                "trigger": "triggered",
            }
            if action in arm_map:
                required = dev.attributes.get(
                    "code_disarm_required" if action == "disarm" else "code_arm_required",
                    False,
                )
                expected = dev.attributes.get("code")
                if required and action != "trigger" and data.get("code") != expected:
                    state["last_error"] = "invalid_code"
                else:
                    state["state"] = arm_map[action]
                    state.pop("last_error", None)
        elif domain == "media_player":
            if action in {"turn_on", "turn_off", "play", "pause"}:
                state["state"] = "off" if action == "turn_off" else "playing" if action == "play" else "idle"
            if "volume_level" in data:
                state["volume_level"] = data["volume_level"]
            if "source" in data and data["source"] in dev.attributes.get("source_list", []):
                state["source"] = data["source"]
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
