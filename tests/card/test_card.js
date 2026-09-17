const { JSDOM } = require("jsdom");
const fs = require("fs");
const path = require("path");
const assert = require("assert");

const cardSource = fs.readFileSync(
  path.join(__dirname, "..", "..", "custom_components", "plant_monitor", "www", "plant-monitor-card.js"),
  "utf-8"
);

function makeHass() {
  const deviceId = "dev123";
  const entities = {
    "sensor.pannenkoekenplant_puppy_advies": { entity_id: "sensor.pannenkoekenplant_puppy_advies", device_id: deviceId, platform: "plant_monitor", translation_key: "advice" },
    "sensor.pannenkoekenplant_puppy_verzorgingstip": { entity_id: "sensor.pannenkoekenplant_puppy_verzorgingstip", device_id: deviceId, platform: "plant_monitor", translation_key: "care_tip" },
    "sensor.pannenkoekenplant_puppy_gezondheidsscore": { entity_id: "sensor.pannenkoekenplant_puppy_gezondheidsscore", device_id: deviceId, platform: "plant_monitor", translation_key: "health_score" },
    "sensor.pannenkoekenplant_puppy_droogsnelheid": { entity_id: "sensor.pannenkoekenplant_puppy_droogsnelheid", device_id: deviceId, platform: "plant_monitor", translation_key: "drying_rate" },
    "sensor.pannenkoekenplant_puppy_waterbehoefte": { entity_id: "sensor.pannenkoekenplant_puppy_waterbehoefte", device_id: deviceId, platform: "plant_monitor", translation_key: "water_prediction" },
    "sensor.pannenkoekenplant_puppy_laatst_water_gegeven": { entity_id: "sensor.pannenkoekenplant_puppy_laatst_water_gegeven", device_id: deviceId, platform: "plant_monitor", translation_key: "last_watered" },
    "sensor.pannenkoekenplant_puppy_wateringen_deze_week": { entity_id: "sensor.pannenkoekenplant_puppy_wateringen_deze_week", device_id: deviceId, platform: "plant_monitor", translation_key: "waterings_this_week" },
    "binary_sensor.pannenkoekenplant_puppy_droog": { entity_id: "binary_sensor.pannenkoekenplant_puppy_droog", device_id: deviceId, platform: "plant_monitor", translation_key: "dry" },
    "binary_sensor.pannenkoekenplant_puppy_te_nat": { entity_id: "binary_sensor.pannenkoekenplant_puppy_te_nat", device_id: deviceId, platform: "plant_monitor", translation_key: "overwatered" },
    "image.pannenkoekenplant_puppy_foto": { entity_id: "image.pannenkoekenplant_puppy_foto", device_id: deviceId, platform: "plant_monitor", translation_key: "photo" },
    // A totally unrelated entity on the SAME device_id-space to make sure we don't false-match:
    "sensor.unrelated_thing": { entity_id: "sensor.unrelated_thing", device_id: "otherdevice", platform: "other_integration" },
  };

  const states = {
    "sensor.pannenkoekenplant_puppy_advies": { entity_id: "sensor.pannenkoekenplant_puppy_advies", state: "\u2705 All good, no action needed.", attributes: { friendly_name: "Pannenkoekenplant (Puppy) Advies" } },
    "sensor.pannenkoekenplant_puppy_verzorgingstip": { entity_id: "sensor.pannenkoekenplant_puppy_verzorgingstip", state: "Let the top layer dry before watering again.", attributes: {} },
    "sensor.pannenkoekenplant_puppy_gezondheidsscore": { entity_id: "sensor.pannenkoekenplant_puppy_gezondheidsscore", state: "98", attributes: { unit_of_measurement: "pts" } },
    "sensor.pannenkoekenplant_puppy_droogsnelheid": { entity_id: "sensor.pannenkoekenplant_puppy_droogsnelheid", state: "1.2", attributes: { unit_of_measurement: "%/h" } },
    "sensor.pannenkoekenplant_puppy_waterbehoefte": { entity_id: "sensor.pannenkoekenplant_puppy_waterbehoefte", state: "In about 12.0 hours", attributes: {} },
    "sensor.pannenkoekenplant_puppy_laatst_water_gegeven": { entity_id: "sensor.pannenkoekenplant_puppy_laatst_water_gegeven", state: "2026-09-16T10:00:00+00:00", attributes: {} },
    "sensor.pannenkoekenplant_puppy_wateringen_deze_week": { entity_id: "sensor.pannenkoekenplant_puppy_wateringen_deze_week", state: "2", attributes: {} },
    "binary_sensor.pannenkoekenplant_puppy_droog": { entity_id: "binary_sensor.pannenkoekenplant_puppy_droog", state: "off", attributes: {} },
    "binary_sensor.pannenkoekenplant_puppy_te_nat": { entity_id: "binary_sensor.pannenkoekenplant_puppy_te_nat", state: "off", attributes: {} },
    "image.pannenkoekenplant_puppy_foto": { entity_id: "image.pannenkoekenplant_puppy_foto", state: "2026-09-16T10:00:00+00:00", attributes: { entity_picture: "/api/image_proxy/image.pannenkoekenplant_puppy_foto?token=abc" } },
  };

  const devices = {
    dev123: { id: deviceId, name: "Pannenkoekenplant (Puppy)", name_by_user: null },
  };

  return { entities, states, devices, deviceId };
}

async function run() {
  const dom = new JSDOM(`<!doctype html><html><body></body></html>`, { runScripts: "outside-only" });
  global.window = dom.window;
  global.document = dom.window.document;
  global.HTMLElement = dom.window.HTMLElement;
  global.customElements = dom.window.customElements;

  dom.window.eval(cardSource);
  const PlantMonitorCardCtor = dom.window.customElements.get("plant-monitor-card");
  assert.ok(PlantMonitorCardCtor, "custom element did not register");
  console.log("test_custom_element_registers: OK");

  const { entities, states, devices, deviceId } = makeHass();
  const hass = { entities, states, devices };

  // --- Test 1: getStubConfig picks a plant_monitor device ---
  const stub = PlantMonitorCardCtor.getStubConfig(hass);
  assert.strictEqual(stub.device_id, deviceId);
  console.log("test_get_stub_config: OK ->", stub);

  // --- Test 2: full render via auto-discovery (translation_key based) ---
  const el = document.createElement("plant-monitor-card");
  el.setConfig({ device_id: deviceId });
  el.hass = hass;

  const html = el.innerHTML;
  assert.ok(html.includes("All good, no action needed"), "advice text missing from render");
  assert.ok(html.includes("Let the top layer dry"), "care tip text missing from render");
  assert.ok(html.includes("98 pts"), "health score tile missing/wrong");
  assert.ok(html.includes("1.2 %/h"), "drying rate tile missing/wrong");
  assert.ok(html.includes("In about 12.0 hours"), "prediction tile missing/wrong");
  assert.ok(html.includes('src="/api/image_proxy/image.pannenkoekenplant_puppy_foto?token=abc"'), "photo <img> src missing/wrong");
  assert.ok(html.includes(">OK<"), "expected OK status badge when dry=off and overwatered=off");
  assert.ok(html.includes("Pannenkoekenplant (Puppy)"), "device title missing");
  console.log("test_full_render_auto_discovery: OK");

  // --- Test 3: status badge flips to Dry when the dry binary_sensor is on ---
  const hassDry = JSON.parse(JSON.stringify(hass));
  hassDry.states["binary_sensor.pannenkoekenplant_puppy_droog"].state = "on";
  const el2 = document.createElement("plant-monitor-card");
  el2.setConfig({ device_id: deviceId });
  el2.hass = hassDry;
  assert.ok(el2.innerHTML.includes(">Dry<"), "expected Dry status badge");
  console.log("test_status_badge_dry: OK");

  // --- Test 4: manual entities override bypasses auto-discovery entirely ---
  const el3 = document.createElement("plant-monitor-card");
  el3.setConfig({
    title: "Manual Override Plant",
    entities: { advice: "sensor.pannenkoekenplant_puppy_advies" },
  });
  el3.hass = hass;
  assert.ok(el3.innerHTML.includes("Manual Override Plant"));
  assert.ok(el3.innerHTML.includes("All good, no action needed"));
  console.log("test_manual_entities_override: OK");

  // --- Test 5: HTML escaping (defend against a malicious/odd state string) ---
  const hassXss = JSON.parse(JSON.stringify(hass));
  hassXss.states["sensor.pannenkoekenplant_puppy_gezondheidsscore"].state = "<script>x</script>";
  delete hassXss.states["sensor.pannenkoekenplant_puppy_gezondheidsscore"].attributes.unit_of_measurement;
  const el4 = document.createElement("plant-monitor-card");
  el4.setConfig({ device_id: deviceId });
  el4.hass = hassXss;
  assert.ok(!el4.innerHTML.includes("<script>x</script>"), "raw script tag leaked into innerHTML unescaped");
  assert.ok(el4.innerHTML.includes("&lt;script&gt;"), "expected escaped value in tile");
  console.log("test_html_escaping: OK");

  // --- Test 6: setConfig throws without device_id or entities ---
  let threw = false;
  try {
    document.createElement("plant-monitor-card").setConfig({});
  } catch (e) {
    threw = true;
  }
  assert.ok(threw, "setConfig should throw when neither device_id nor entities given");
  console.log("test_setconfig_requires_target: OK");

  console.log("\nAll card tests passed.");
}

run().catch((err) => {
  console.error("FAILED:", err);
  process.exit(1);
});
