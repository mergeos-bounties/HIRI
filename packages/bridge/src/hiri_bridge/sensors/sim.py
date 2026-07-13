"""Firmware-style sensor simulators (DHT22 / soil) with deterministic offline tick."""

from __future__ import annotations

import math
import time
from typing import Any


def dht22_reading(*, seed: float | None = None, t: float | None = None) -> dict[str, Any]:
    """
    Simulate DHT22 temperature (°C) and humidity (%RH).

    Uses a smooth sinusoidal day-cycle so demos look alive without hardware.
    """
    now = t if t is not None else time.time()
    phase = (seed or 0.0) + now / 3600.0  # slow drift
    temp = 24.0 + 4.0 * math.sin(phase) + 0.3 * math.sin(phase * 3.1)
    humidity = 55.0 + 12.0 * math.cos(phase * 0.9) + 1.5 * math.sin(phase * 2.2)
    humidity = max(20.0, min(95.0, humidity))
    return {
        "model": "DHT22-sim",
        "temperature_c": round(temp, 1),
        "humidity_pct": round(humidity, 1),
        "ok": True,
        "source": "sim",
    }


def soil_moisture_reading(*, seed: float | None = None, t: float | None = None) -> dict[str, Any]:
    """Simulate capacitive soil moisture % with slow dry-down and irrigation bumps."""
    now = t if t is not None else time.time()
    phase = (seed or 1.0) + now / 7200.0
    base = 48.0 + 18.0 * math.sin(phase)
    # irrigation pulse every ~cycle
    pulse = 12.0 if math.sin(phase * 2) > 0.85 else 0.0
    moisture = max(5.0, min(95.0, base + pulse))
    return {
        "model": "SOIL-sim",
        "moisture_pct": round(moisture, 1),
        "status": "wet" if moisture > 60 else "ok" if moisture > 30 else "dry",
        "ok": True,
        "source": "sim",
    }


_HISTORY: dict[str, list[dict[str, Any]]] = {}


def sensor_history(device_id: str, limit: int = 20) -> list[dict[str, Any]]:
    rows = _HISTORY.get(device_id) or []
    return list(rows[-max(1, min(limit, 100)) :])


def tick_farm_sensors(devices: list[Any]) -> list[dict[str, Any]]:
    """
    Update in-memory Device objects that look like soil/temp sensors.

    `devices` items must have `.id`, `.model`, `.state` attributes (HIRI Device).
    Keeps a short in-process history ring per device id.
    """
    updated: list[dict[str, Any]] = []
    for i, d in enumerate(devices):
        mid = str(getattr(d, "model", "") or "").upper()
        did = str(getattr(d, "id", "") or "")
        reading: dict[str, Any] | None = None
        if "SOIL" in mid or "soil" in did:
            reading = soil_moisture_reading(seed=float(i))
            d.state = {**dict(d.state or {}), "state": reading["moisture_pct"], "status": reading["status"]}
            updated.append({"id": did, **reading})
        elif "TH" in mid or "DHT" in mid or "temp" in did or "greenhouse" in did:
            reading = dht22_reading(seed=float(i + 3))
            # temperature device
            if "humidity" in did or "hum" in mid.lower():
                d.state = {**dict(d.state or {}), "state": reading["humidity_pct"]}
            else:
                d.state = {
                    **dict(d.state or {}),
                    "state": reading["temperature_c"],
                    "humidity": reading["humidity_pct"],
                }
            updated.append({"id": did, **reading})
        if reading is not None and did:
            hist = _HISTORY.setdefault(did, [])
            hist.append({k: v for k, v in reading.items() if k != "model"})
            if len(hist) > 50:
                del hist[:-50]
    return updated
