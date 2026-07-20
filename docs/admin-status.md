# Admin: Adapter Status Page

## Overview

Web page showing connected adapter status and configuration form.

## Status Display

| Field | Description |
|-------|-------------|
| Adapter ID | Unique identifier |
| Connection | Connected/Disconnected |
| Last seen | Timestamp |
| Devices | Count of paired devices |
| Firmware | Version string |

## Config Form

- MQTT broker address
- MQTT port
- Discovery prefix
- Refresh interval

## API

```
GET /api/admin/adapters
POST /api/admin/adapter/config
```
