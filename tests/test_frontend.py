"""End-to-end tests for frontend.py: the static file is actually served,
and setup never raises even without a full Lovelace stack."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from homeassistant.setup import async_setup_component

from custom_components.plant_monitor.frontend import STATIC_URL_PATH, async_register_frontend


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


async def test_register_frontend_never_raises(hass):
    # No http/Lovelace setup done at all - the defensive try/except paths
    # (missing hass.http, missing hass.data["lovelace"]) must both hold.
    await async_register_frontend(hass)  # would raise on failure; test passes if it doesn't
    print("test_register_frontend_never_raises: OK")


async def test_card_js_is_actually_served(hass, hass_client):
    assert await async_setup_component(hass, "http", {})
    await async_register_frontend(hass)
    client = await hass_client()
    resp = await client.get(STATIC_URL_PATH)
    assert resp.status == 200
    body = await resp.text()
    assert "customElements.define" in body
    assert "plant-monitor-card" in body
    print("test_card_js_is_actually_served: OK ->", resp.status, f"({len(body)} bytes)")


async def test_calling_twice_is_idempotent(hass, hass_client):
    assert await async_setup_component(hass, "http", {})
    await async_register_frontend(hass)
    await async_register_frontend(hass)  # must not raise or duplicate-register
    client = await hass_client()
    resp = await client.get(STATIC_URL_PATH)
    assert resp.status == 200
    print("test_calling_twice_is_idempotent: OK")
