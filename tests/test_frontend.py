"""End-to-end tests for frontend.py: the static file is actually served,
and setup never raises even without a full Lovelace stack."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from homeassistant.helpers import issue_registry as ir
from homeassistant.setup import async_setup_component

from custom_components.plant_monitor.const import DOMAIN
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


async def test_storage_mode_lovelace_gets_resource_registered_automatically(hass):
    """The actual happy path: on a normal (storage-mode) dashboard setup,
    the resource must actually land in the collection, and no Repairs
    issue should be created. This is the case that was never tested
    before v0.5.1, which is how a real dependency-ordering bug (lovelace
    not yet set up when we checked hass.data["lovelace"]) shipped without
    being caught - it looked identical to the YAML-mode case from the
    outside, since both made the check bail out early."""
    assert await async_setup_component(hass, "http", {})
    assert await async_setup_component(hass, "lovelace", {})
    await hass.async_block_till_done()

    await async_register_frontend(hass)

    resource_collection = hass.data["lovelace"]["resources"]
    if not resource_collection.loaded:
        await resource_collection.async_load()
    items = resource_collection.async_items()
    matching = [item for item in items if item.get("url") == STATIC_URL_PATH]
    assert matching, f"resource {STATIC_URL_PATH} was not registered; items were {items}"

    issue_registry = ir.async_get(hass)
    assert issue_registry.async_get_issue(DOMAIN, "add_lovelace_resource_manually") is None, (
        "a Repairs issue was created even though auto-registration succeeded"
    )
    print("test_storage_mode_lovelace_gets_resource_registered_automatically: OK")
