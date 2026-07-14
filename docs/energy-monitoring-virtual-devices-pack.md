{
  "devices": [
    {
      "id": "energy_main_meter",
      "name": "Main Power Meter",
      "type": "energy_monitor",
      "location": "electrical_panel",
      "metrics": {
        "power_watts": {
          "current": 3450,
          "min": 800,
          "max": 8500,
          "unit": "W"
        },
        "voltage": {
          "current": 240,
          "min": 235,
          "max": 245,
          "unit": "V"
        },
        "current_amps": {
          "current": 14.4,
          "min": 3.3,
          "max": 35.4,
          "unit": "A"
        },
        "energy_kwh": {
          "today": 67.8,
          "week": 485.2,
          "month": 1876.5,
          "unit": "kWh"
        },
        "power_factor": 0.98,
        "frequency_hz": 60
      },
      "status": "online",
      "last_updated": "2026-07-14T04:48:00Z"
    },
    {
      "id": "energy_hvac",
      "name": "HVAC System Monitor",
      "type": "energy_monitor",
      "location": "hvac_unit",
      "metrics": {
        "power_watts": {
          "current": 2200,
          "min": 0,
          "max": 4500,
          "unit": "W"
        },
        "voltage": {
          "current": 240,
          "min": 238,
          "max": 242,
          "unit": "V"
        },
        "current_amps": {
          "current": 9.2,
          "min": 0,
          "max": 18.8,
          "unit": "A"
        },
        "energy_kwh": {
          "today": 42.5,
          "week": 312.8,
          "month": 1245.6,
          "unit": "kWh"
        },
        "power_factor": 0.95,
        "frequency_hz": 60,
        "runtime_hours_today": 18.2
      },
      "status": "online",
      "last_updated": "2026-07-14T04:48:00Z"
    },
    {
      "id": "energy_kitchen",
      "name": "Kitchen Appliances",
      "type": "energy_monitor",
      "location": "kitchen",
      "metrics": {
        "power_watts": {
          "current": 450,
          "min": 0,
          "max": 3800,
          "unit": "W"
        },
        "voltage": {
          "current": 120,
          "min": 118,
          "max": 122,
          "unit": "V"
        },
        "current_amps": {
          "current": 3.75,
          "min": 0,
          "max": 31.7,
          "unit": "A"
        },
        "energy_kwh": {
          "today": 8.9,
          "week": 58.3,
          "month": 234.7,
          "unit": "kWh"
        },
        "power_factor": 0.92,
        "frequency_hz": 60
      },
      "status": "online",
      "last_updated": "2026-07-14T04:48:00Z"
    },
    {
      "id": "energy_solar_panels",
      "name": "Solar Array",
      "type": "solar_monitor",
      "location": "roof",
      "metrics": {
        "power_watts": {
          "current": 0,
          "min": 0,
          "max": 5000,
          "unit": "W",
          "peak_today": 4850
        },
        "voltage": {
          "current": 240,
          "min": 235,
          "max": 245,
          "unit": "V"
        },
        "current_amps": {
          "current": 0,
          "min": 0,
          "max": 20.8,
          "unit": "A"
        },
        "energy_kwh": {
          "today": 28.4,
          "week": 198.7,
          "month": 856.3,
          "unit": "kWh"
        },
        "irradiance": 0,
        "efficiency": 18.5
      },
      "status": "online",
      "last_updated": "2026-07-14T04:48:00Z"
    },
    {
      "id": "energy_ev_charger",
      "name": "EV Charging Station",
      "type": "energy_monitor",
      "location": "garage",
      "metrics": {
        "power_watts": {
          "current": 7200,
          "min": 0,
          "max": 11500,
          "unit": "W"
        },
        "voltage": {
          "current": 240,
          "min": 238,
          "max": 242,
          "unit": "V"
        },
        "current_amps": {
          "current": 30,
          "min": 0,
          "max": 48,
          "unit": "A"
        },
        "energy_kwh": {
          "today": 45.6,
          "week": 156.8,
          "month": 687.2,
          "unit": "kWh"
        },
        "power_factor": 0.99,
        "frequency_hz": 60,
        "charging_state": "active",
        "battery_level": 67
      },
      "status": "online",
      "last_updated": "2026-07-14T04:48:00Z"
    },
    {
      "id": "energy_water_heater",
      "name": "Water Heater",
      "type": "energy_monitor",
      "location": "utility_room",
      "metrics": {
        "power_watts": {
          "current": 4500,
          "min": 0,
          "max": 4500,
          "unit": "W"
        },
        "voltage": {
          "current": 240,
          "min": 238,
          "max": 242,
          "unit": "V"
        },
        "current_amps": {
          "current": 18.8,
          "min": 0,
          "max": 18.8,
          "unit": "A"
        },
        "energy_kwh": {
          "today": 12.3,
          "week": 89.4,
          "month": 378.6,
          "unit": "kWh"
        },
        "power_factor": 1.0,
        "frequency_hz": 60,
        "temperature_f": 125
      },
      "status": "online",
      "last_updated": "2026-07-14T04:48:00Z"
    },
    {
      "id": "energy_office",
      "name": "Home Office",
      "type": "energy_monitor",
      "location": "office",
      "metrics": {
        "power_watts": {
          "current": 380,
          "min": 0,
          "max": 850,
          "unit": "W"
        },
        "voltage": {
          "current": 120,
          "min": 118,
          "max": 122,
          "unit": "V"
        },
        "current_amps": {
          "current": 3.17,
          "min": 0,
          "max": 7.08,
          "unit": "A"
        },
        "energy_kwh": {
          "today": 7.2,
          "week": 52.3,
          "month": 215.8,
          "unit": "kWh"
        },
        "power_factor": 0.88,
        "frequency_hz": 60
      },
      "status": "online",
      "last_updated": "2026-07-14T04:48:00Z"
    },
    {
      "id": "energy_washer_dryer",
      "name": "Laundry Appliances",
      "type": "energy_monitor",
      "location": "laundry_room",
      "metrics": {
        "power_watts": {
          "current": 0,
          "min": 0,
          "max": 5400,
          "unit": "W"
        },
        "voltage": {
          "current": 240,
          "min": 238,
          "max": 242,
          "unit": "V"
        },
        "current_amps": {
          "current": 0,
          "min": 0,
          "max": 22.5,
          "unit": "A"
        },
        "energy_kwh": {
          "today": 3.8,
          "week": 18.6,
          "month": 76.4,
          "unit": "kWh"
        },
        "power_factor": 0.93,
        "frequency_hz": 60
      },
      "status": "online",
      "last_updated": "2026-07-14T04:48:00Z"
    }
  ],
  "dashboard_summary": {
    "total_consumption_now": 18180,
    "total_generation_now": 0,
    "net_consumption": 18180,
    "cost_per_kwh": 0.13,
    "estimated_daily_cost": 28.67,
    "estimated_monthly_cost": 860.10,
    "solar_offset_percentage": 45.7,
    "peak_demand_today": 8500,
    "carbon_saved_kg_month": 428.15,
    "top_consumers": [
      {
        "device": "EV Charging Station",
        "percentage": 39.6
      },
      {
        "device": "Water Heater",
        "percentage": 24.8
      },
      {
        "device": "HVAC System Monitor",
        "percentage": 12.1
      }
    ]
  }
}