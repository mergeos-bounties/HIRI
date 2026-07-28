"""Tests for HIRI API key authentication middleware."""

from __future__ import annotations

import os

from hiri.auth import is_auth_enabled, require_auth, set_api_key


def test_auth_disabled_by_default() -> None:
    """When no key is set, auth is disabled."""
    set_api_key(None)
    assert is_auth_enabled() is False


def test_auth_enabled_when_key_set() -> None:
    """When a key is set, auth is enabled."""
    set_api_key("test-key-123")
    assert is_auth_enabled() is True


def test_auth_enabled_via_env() -> None:
    """When HIRI_API_KEY env var is set, auth is enabled."""
    set_api_key(None)
    os.environ["HIRI_API_KEY"] = "env-key-456"
    try:
        assert is_auth_enabled() is True
    finally:
        del os.environ["HIRI_API_KEY"]


def test_passes_with_valid_key() -> None:
    """Request with valid Bearer token passes through."""
    set_api_key("secret-key")
    decorated = require_auth(lambda req: {"ok": True, "data": "protected"})
    result = decorated({"headers": {"Authorization": "Bearer secret-key"}})
    assert result["ok"] is True


def test_rejects_missing_header() -> None:
    """Request without Authorization header is rejected with 401."""
    set_api_key("secret-key")
    decorated = require_auth(lambda req: {"ok": True, "data": "protected"})
    result = decorated({"headers": {}})
    assert result["ok"] is False
    assert result["status"] == 401


def test_rejects_wrong_key() -> None:
    """Request with wrong Bearer token is rejected with 403."""
    set_api_key("secret-key")
    decorated = require_auth(lambda req: {"ok": True, "data": "protected"})
    result = decorated({"headers": {"Authorization": "Bearer wrong-key"}})
    assert result["ok"] is False
    assert result["status"] == 403


def test_passes_without_auth_when_disabled() -> None:
    """When auth is disabled, all requests pass through."""
    set_api_key(None)
    decorated = require_auth(lambda req: {"ok": True, "data": "public"})
    result = decorated({"headers": {}})
    assert result["ok"] is True


def test_auth_persists_until_cleared() -> None:
    """Key persists across calls until set to None."""
    set_api_key("persist-key")
    assert is_auth_enabled() is True
    set_api_key(None)
    assert is_auth_enabled() is False
