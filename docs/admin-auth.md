# Admin API Auth Token

## Setup

Set the admin token in your config:

```yaml
admin_api:
  enabled: true
  token: "<your-token>"
  header: "X-Admin-Token"
```

Generate a token:

```
openssl rand -hex 32
```

## Usage

Requests need the header:

```
GET /api/admin/status
X-Admin-Token: <your-token>
```

Returns 401 if missing or invalid.
