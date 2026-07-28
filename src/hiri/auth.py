"""Optional API key authentication for HIRI admin API.

Usage:
    from hiri.auth import require_auth, set_api_key

    # Enable auth with env var HIRI_API_KEY
    set_api_key("my-secret-key")
    # or let it read from HIRI_API_KEY env var

    # Protect a route
    @require_auth
    def my_handler(request):
        ...
"""

from __future__ import annotations

import os
from functools import wraps
from typing import Any, Callable

_api_key: str | None = None


def set_api_key(key: str | None) -> None:
    """Set the API key for authentication. None disables auth."""
    global _api_key
    _api_key = key


def get_api_key() -> str | None:
    """Get the current API key, falling back to environment variable."""
    global _api_key
    if _api_key is not None:
        return _api_key
    env_key = os.environ.get("HIRI_API_KEY")
    if env_key:
        return env_key
    return None


def require_auth(handler: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator that requires a valid API key in the request.

    Usage:
        @require_auth
        def my_handler(request):
            ...

    The request must include an 'Authorization: Bearer <key>' header.
    If auth is disabled (no key set), all requests pass through.
    """
    api_key = get_api_key()

    # If no API key is configured, auth is disabled — pass through
    if api_key is None:
        return handler

    @wraps(handler)
    def wrapper(request: dict[str, Any], *args: Any, **kwargs: Any) -> dict[str, Any]:
        auth_header = request.get("headers", {}).get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return {"ok": False, "status": 401, "error": "Missing or invalid Authorization header"}
        token = auth_header.removeprefix("Bearer ").strip()
        if token != api_key:
            return {"ok": False, "status": 403, "error": "Invalid API key"}
        return handler(request, *args, **kwargs)

    return wrapper


def is_auth_enabled() -> bool:
    """Check if authentication is currently enabled."""
    return get_api_key() is not None
