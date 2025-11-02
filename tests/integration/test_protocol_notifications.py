"""Integration tests covering MCP notification handling."""

import os

import pytest

from fastapi.testclient import TestClient

# Disable OAuth requirements for these tests to exercise bare MCP behavior.
os.environ.setdefault("MCP_OAUTH_ENABLED", "false")

from mcp_memory_service.web.app import app
from mcp_memory_service.web.dependencies import set_storage


class DummyStorage:
    """Simple in-memory stub implementing the storage interface used by MCP handlers."""

    async def store(self, memory):  # pragma: no cover - not exercised but provided for completeness
        return True, "stored"

    async def retrieve(self, query, n_results):
        return []

    async def recall_memory(self, query, n_results):
        return []

    async def search_by_tags(self, tags, operation):
        return []

    async def delete(self, content_hash):
        return True, "deleted"

    async def get_stats(self):
        return {}

    async def get_all_memories(self, limit, offset, memory_type=None, tags=None):
        return []

    async def close(self):
        return None


@pytest.fixture(autouse=True)
def stub_storage(monkeypatch):
    """Replace storage initialization with a lightweight stub for tests."""
    dummy = DummyStorage()

    async def fake_create_storage_backend():
        return dummy

    monkeypatch.setattr("mcp_memory_service.web.app.create_storage_backend", fake_create_storage_backend)
    monkeypatch.setattr("mcp_memory_service.web.dependencies.create_storage_backend", fake_create_storage_backend)
    set_storage(dummy)
    yield
    import mcp_memory_service.web.dependencies as deps
    deps._storage = None


@pytest.fixture()
def http_client():
    """Provide a TestClient that exercises FastAPI startup/shutdown hooks."""
    with TestClient(app) as client:
        yield client


def test_initialize_and_notifications_are_supported(http_client):
    """Ensure the MCP endpoint accepts initialize and subsequent notifications without errors."""
    init_response = http_client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "method": "initialize",
            "id": 1,
            "params": {"capabilities": {}},
        },
    )
    assert init_response.status_code == 200
    payload = init_response.json()
    assert payload["result"]["protocolVersion"] == "2024-11-05"

    notification_response = http_client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "method": "notifications/initialized"},
    )

    assert notification_response.status_code == 204
    assert notification_response.content == b""


def test_register_capabilities_notification_succeeds(http_client):
    """Verify arbitrary MCP notifications receive a no-content acknowledgement."""
    response = http_client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "method": "notifications/registerCapabilities",
            "params": {"registrations": []},
        },
    )

    assert response.status_code == 204
    assert response.content == b""
