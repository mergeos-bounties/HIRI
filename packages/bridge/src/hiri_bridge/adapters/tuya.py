"""Tuya cloud/local adapter with offline mapping table and cloud API support."""

from __future__ import annotations

import json
import logging
from typing import Any

from hiri_bridge.devices.types import Device

logger = logging.getLogger(__name__)

# Offline mapping table: tuya category → HA domain
# https://developer.tuya.com/en/docs/iot/category
TUYA_CATEGORY_MAP: dict[str, dict[str, str]] = {
    # Lighting
    "dj": {"domain": "light", "description": "Light"},
    "dd": {"domain": "light", "description": "Zigbee Light"},
    "fwl": {"domain": "light", "description": "Filament Light"},
    "dc": {"domain": "light", "description": "Zigbee Ceiling Light"},
    "gdn": {"domain": "light", "description": "Garden Light"},
    "tyndd": {"domain": "light", "description": "Ceiling Light"},
    "xdd": {"domain": "light", "description": "Ceiling Light (Zigbee)"},
    # Switches & Sockets
    "kg": {"domain": "switch", "description": "Switch"},
    "cz": {"domain": "switch", "description": "Socket"},
    "pkg": {"domain": "switch", "description": "Power Strip"},
    "znd": {"domain": "switch", "description": "Smart Switch"},
    "wkz": {"domain": "switch", "description": "Scene Switch"},
    "wkg": {"domain": "switch", "description": "Wall Switch"},
    # Sensors
    "wsdcg": {"domain": "sensor", "description": "Temperature/Humidity Sensor"},
    "mcs": {"domain": "binary_sensor", "description": "Contact Sensor"},
    "ywbj": {"domain": "binary_sensor", "description": "Smoke Detector"},
    "rqbj": {"domain": "binary_sensor", "description": "Gas Detector"},
    "sos": {"domain": "binary_sensor", "description": "SOS Button"},
    "pir": {"domain": "binary_sensor", "description": "Motion Sensor"},
    "hps": {"domain": "sensor", "description": "Human Presence Sensor"},
    "zgb": {"domain": "sensor", "description": "Vibration Sensor"},
    "ldcg": {"domain": "sensor", "description": "Luminance Sensor"},
    "szjq": {"domain": "sensor", "description": "Water Detector"},
    "pm2.5": {"domain": "sensor", "description": "PM2.5 Sensor"},
    "co2bj": {"domain": "sensor", "description": "CO2 Detector"},
    # Climate
    "wk": {"domain": "climate", "description": "Thermostat"},
    "kt": {"domain": "climate", "description": "Air Conditioner"},
    "qn": {"domain": "climate", "description": "Heater"},
    "jsq": {"domain": "climate", "description": "Water Heater"},
    "fgn": {"domain": "fan", "description": "Fan"},
    "bcm": {"domain": "climate", "description": "Dehumidifier"},
    "cs": {"domain": "climate", "description": "Humidifier"},
    "lx": {"domain": "climate", "description": "Air Purifier"},
    "kfj": {"domain": "climate", "description": "Air Purifier (Zigbee)"},
    # Covers & Curtains
    "cl": {"domain": "cover", "description": "Curtain"},
    "clkg": {"domain": "cover", "description": "Curtain Switch"},
    "wc": {"domain": "cover", "description": "Window"},
    "ck": {"domain": "cover", "description": "Garage Door"},
    "yksb": {"domain": "cover", "description": "Yard Gate"},
    # Security
    "sm": {"domain": "lock", "description": "Door Lock"},
    "sgbm": {"domain": "lock", "description": "Smart Lock"},
    "video_lock": {"domain": "lock", "description": "Video Door Lock"},
    "jq": {"domain": "alarm", "description": "Alarm"},
    "sgbj": {"domain": "alarm", "description": "Alarm (Zigbee)"},
    # Cameras & Video
    "sp": {"domain": "camera", "description": "Camera"},
    "wl": {"domain": "camera", "description": "Camera (LoRa)"},
    "dp": {"domain": "camera", "description": "Doorbell"},
    "qxj": {"domain": "camera", "description": "Camera (Zigbee)"},
    "doorbell": {"domain": "camera", "description": "Video Doorbell"},
    # Vacuum / Robot
    "sd": {"domain": "vacuum", "description": "Robot Vacuum"},
    "sz": {"domain": "vacuum", "description": "Robot Vacuum (Zigbee)"},
    # Other
    "qt": {"domain": "sensor", "description": "Other Device"},
}

TUYA_FIXTURE: list[dict[str, Any]] = [
    {"id": "bf123light", "name": "Tuya RGB Bulb", "category": "dj", "online": True},
    {"id": "bf456sock", "name": "Tuya Smart Plug", "category": "cz", "online": True},
    {"id": "bf789th", "name": "Tuya Temp/Hum Sensor", "category": "wsdcg", "online": True},
    {"id": "bf000door", "name": "Tuya Door Sensor", "category": "mcs", "online": False},
    {"id": "bf111pir", "name": "Tuya Motion Sensor", "category": "pir", "online": True},
    {"id": "bf222curt", "name": "Tuya Smart Curtain", "category": "cl", "online": True},
    {"id": "bf333lock", "name": "Tuya Smart Lock", "category": "sm", "online": True},
    {"id": "bf444cam", "name": "Tuya Camera", "category": "sp", "online": True},
    {"id": "bf555vac", "name": "Tuya Robot Vacuum", "category": "sd", "online": True},
    {"id": "bf666ac", "name": "Tuya AC Unit", "category": "kt", "online": False},
    {"id": "bf777fan", "name": "Tuya Ceiling Fan", "category": "fgn", "online": True},
    {"id": "bf888alarm", "name": "Tuya Alarm Panel", "category": "jq", "online": True},
]


class TuyaAdapter:
    """Tuya cloud/local adapter.

    Supports two modes:
    - **Fixture mode** (default): returns offline demo devices for testing
    - **Cloud API mode**: uses Tuya IoT API to fetch real devices
      (requires access_id + access_secret, and use_fixture=False)
    """

    name = "tuya"

    def __init__(
        self,
        access_id: str = "",
        access_secret: str = "",
        use_fixture: bool = True,
        base_url: str = "https://openapi.tuyaeu.com",
    ):
        self.access_id = access_id
        self.access_secret = access_secret
        self.use_fixture = use_fixture
        self.base_url = base_url
        self._token: dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Token management
    # ------------------------------------------------------------------

    def _authenticate(self) -> str | None:
        """Authenticate with Tuya IoT API and return an access token.

        Returns None if credentials are missing or authentication fails.
        """
        if not self.access_id or not self.access_secret:
            logger.warning("Tuya: access_id or access_secret not set")
            return None
        try:
            import httpx

            resp = httpx.post(
                f"{self.base_url}/v1.0/token?grant_type=1",
                headers=self._headers(no_token=True),
                timeout=10,
            )
            data = resp.json()
            if data.get("success") and data.get("result"):
                token = data["result"]["access_token"]
                expire = data["result"].get("expire_time", 7200)
                self._token = {"access_token": token, "expires_in": expire}
                return token
            logger.warning("Tuya auth failed: %s", data.get("msg", "unknown"))
        except ImportError:
            logger.warning("httpx not installed; Tuya cloud API unavailable")
        except Exception as exc:
            logger.warning("Tuya auth error: %s", exc)
        return None

    def _headers(self, no_token: bool = False) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if not no_token and self._token.get("access_token"):
            headers["Authorization"] = f"Bearer {self._token['access_token']}"
        return headers

    # ------------------------------------------------------------------
    # Device listing
    # ------------------------------------------------------------------

    def list_remote(self) -> list[Device]:
        """List devices from fixture or Tuya cloud API."""
        if not self.use_fixture and self.access_id and self.access_secret:
            return self._list_cloud() or self._list_fixture()
        return self._list_fixture()

    def _list_cloud(self) -> list[Device] | None:
        """Fetch real devices from Tuya IoT Cloud API."""
        token = self._authenticate()
        if not token:
            return None

        try:
            import httpx

            devices: list[Device] = []
            # Fetch all device list from Tuya (paginated)
            page = 1
            while True:
                resp = httpx.get(
                    f"{self.base_url}/v1.0/devices",
                    headers=self._headers(),
                    params={"page_no": page, "page_size": 50},
                    timeout=15,
                )
                data = resp.json()
                if not data.get("success"):
                    logger.warning("Tuya list devices failed: %s", data.get("msg"))
                    break

                result = data.get("result", {})
                rows = result.get("devices", result.get("list", []))
                if not rows:
                    break

                for row in rows:
                    device = self._cloud_device_to_hiri(row)
                    if device:
                        devices.append(device)

                total = result.get("total", 0)
                if page * 50 >= total:
                    break
                page += 1

            return devices

        except ImportError:
            logger.warning("httpx not installed; Tuya cloud API unavailable")
        except Exception as exc:
            logger.warning("Tuya cloud list error: %s", exc)
        return None

    def _cloud_device_to_hiri(self, row: dict[str, Any]) -> Device | None:
        """Convert a Tuya cloud API device dict to a HIRI Device."""
        device_id = row.get("id", "") or row.get("device_id", "")
        name = row.get("name", "Tuya Device")
        category = row.get("category", "qt")
        online = row.get("online", row.get("is_online", False))
        if isinstance(online, str):
            online = online.lower() == "true"

        mapping = TUYA_CATEGORY_MAP.get(category, TUYA_CATEGORY_MAP["qt"])
        domain = mapping["domain"]

        # Extract state from status array
        state: dict[str, Any] = {"state": "off"}
        status = row.get("status", [])
        for s in status:
            if s.get("code") == "switch_1":
                state["state"] = "on" if s.get("value") else "off"
            elif s.get("code") == "bright_value":
                state["brightness"] = s.get("value")
            elif s.get("code") in ("temp_set", "temperature"):
                state["temperature"] = s.get("value")
            elif s.get("code") == "humidity_value":
                state["humidity"] = s.get("value")

        return Device(
            id=f"{domain}.tuya_{device_id[:12]}" if device_id else "",
            name=name,
            domain=domain,
            manufacturer="Tuya",
            model=category,
            area="home",
            online=bool(online),
            state=state,
            attributes={
                "tuya_id": device_id,
                "category": category,
                "unit_of_measurement": "C" if domain == "sensor" else None,
            },
            adapter="tuya",
        )

    def _list_fixture(self) -> list[Device]:
        """Return offline fixture devices."""
        devices: list[Device] = []
        for row in TUYA_FIXTURE:
            mapping = TUYA_CATEGORY_MAP.get(row["category"], TUYA_CATEGORY_MAP["qt"])
            domain = mapping["domain"]
            state_val = "off" if domain not in ("sensor",) else "22.5"
            if domain == "cover":
                state_val = "closed"
            elif domain == "lock":
                state_val = "locked"
            elif domain == "camera":
                state_val = "idle"
            elif domain == "vacuum":
                state_val = "docked"
            elif domain == "fan":
                state_val = "off"

            devices.append(
                Device(
                    id=f"{domain}.tuya_{row['id']}",
                    name=row["name"],
                    domain=domain,
                    manufacturer="Tuya",
                    model=row["category"],
                    area="home",
                    online=bool(row.get("online", True)),
                    state={"state": state_val},
                    attributes={
                        "tuya_id": row["id"],
                        "category": row["category"],
                        "unit_of_measurement": "C" if domain == "sensor" else None,
                    },
                    adapter="tuya",
                )
            )
        return devices

    # ------------------------------------------------------------------
    # State push (cloud/local)
    # ------------------------------------------------------------------

    def push_state(self, device: Device) -> None:
        """Push a device state change to Tuya cloud (or no-op in fixture mode)."""
        if self.use_fixture or not self._token.get("access_token"):
            return None

        try:
            import httpx

            # Extract Tuya device ID from the attributes
            tuya_id = (device.attributes or {}).get("tuya_id", "")
            if not tuya_id:
                logger.warning("Tuya push: no tuya_id in device attributes")
                return None

            # Build command payload
            commands: list[dict[str, Any]] = []
            state = device.state or {}
            if device.domain == "light":
                if "state" in state:
                    commands.append({"code": "switch_led", "value": state["state"] == "on"})
            elif device.domain == "switch":
                if "state" in state:
                    commands.append({"code": "switch_1", "value": state["state"] == "on"})
            elif device.domain == "cover":
                if state.get("state") == "open":
                    commands.append({"code": "control", "value": "open"})
                elif state.get("state") == "close":
                    commands.append({"code": "control", "value": "close"})

            if commands:
                resp = httpx.post(
                    f"{self.base_url}/v1.0/devices/{tuya_id}/commands",
                    headers=self._headers(),
                    json={"commands": commands},
                    timeout=10,
                )
                data = resp.json()
                if not data.get("success"):
                    logger.warning("Tuya push failed: %s", data.get("msg", "unknown"))

        except ImportError:
            logger.warning("httpx not installed; Tuya push unavailable")
        except Exception as exc:
            logger.warning("Tuya push error: %s", exc)

        return None

    # ------------------------------------------------------------------
    # Mapping table
    # ------------------------------------------------------------------

    @staticmethod
    def mapping_table() -> dict[str, str]:
        """Return a simplified category to domain mapping."""
        return {k: v["domain"] for k, v in TUYA_CATEGORY_MAP.items()}

    @staticmethod
    def full_mapping_table() -> dict[str, dict[str, str]]:
        """Return the full category to {domain, description} mapping."""
        return dict(TUYA_CATEGORY_MAP)
