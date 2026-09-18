const { JSDOM } = require("jsdom");
const fs = require("fs");
const path = require("path");
const assert = require("assert");

const cardSource = fs.readFileSync(
  path.join(__dirname, "..", "..", "custom_components", "plant_monitor", "www", "plant-monitor-card.js"),
  "utf-8"
);

const DEVICE_ID = "dev123";
const SOURCE_DEVICE_ID = "zigbee_device_456"; // the ORIGINAL hardware's device - deliberately different from DEVICE_ID

function makeEntities() {
  return {
    "sensor.pannenkoekenplant_puppy_advies": { entity_id: "sensor.pannenkoekenplant_puppy_advies", device_id: DEVICE_ID, platform: "plant_monitor", translation_key: "advice" },
    "sensor.pannenkoekenplant_puppy_verzorgingstip": { entity_id: "sensor.pannenkoekenplant_puppy_verzorgingstip", device_id: DEVICE_ID, platform: "plant_monitor", translation_key: "care_tip" },
    "sensor.pannenkoekenplant_puppy_bodemvocht": { entity_id: "sensor.pannenkoekenplant_puppy_bodemvocht", device_id: DEVICE_ID, platform: "plant_monitor", translation_key: "soil_moisture" },
    "sensor.pannenkoekenplant_puppy_gezondheidsscore": { entity_id: "sensor.pannenkoekenplant_puppy_gezondheidsscore", device_id: DEVICE_ID, platform: "plant_monitor", translation_key: "health_score" },
    "sensor.pannenkoekenplant_puppy_droogsnelheid": { entity_id: "sensor.pannenkoekenplant_puppy_droogsnelheid", device_id: DEVICE_ID, platform: "plant_monitor", translation_key: "drying_rate" },
    "sensor.pannenkoekenplant_puppy_waterbehoefte": { entity_id: "sensor.pannenkoekenplant_puppy_waterbehoefte", device_id: DEVICE_ID, platform: "plant_monitor", translation_key: "water_prediction" },
    "sensor.pannenkoekenplant_puppy_laatst_water_gegeven": { entity_id: "sensor.pannenkoekenplant_puppy_laatst_water_gegeven", device_id: DEVICE_ID, platform: "plant_monitor", translation_key: "last_watered" },
    "sensor.pannenkoekenplant_puppy_wateringen_deze_week": { entity_id: "sensor.pannenkoekenplant_puppy_wateringen_deze_week", device_id: DEVICE_ID, platform: "plant_monitor", translation_key: "waterings_this_week" },
    "binary_sensor.pannenkoekenplant_puppy_droog": { entity_id: "binary_sensor.pannenkoekenplant_puppy_droog", device_id: DEVICE_ID, platform: "plant_monitor", translation_key: "dry" },
    "binary_sensor.pannenkoekenplant_puppy_te_nat": { entity_id: "binary_sensor.pannenkoekenplant_puppy_te_nat", device_id: DEVICE_ID, platform: "plant_monitor", translation_key: "overwatered" },
    "number.pannenkoekenplant_puppy_droogte_drempel": { entity_id: "number.pannenkoekenplant_puppy_droogte_drempel", device_id: DEVICE_ID, platform: "plant_monitor", translation_key: "dry_threshold" },
    "number.pannenkoekenplant_puppy_overwater_drempel": { entity_id: "number.pannenkoekenplant_puppy_overwater_drempel", device_id: DEVICE_ID, platform: "plant_monitor", translation_key: "wet_threshold" },
    "image.pannenkoekenplant_puppy_foto": { entity_id: "image.pannenkoekenplant_puppy_foto", device_id: DEVICE_ID, platform: "plant_monitor", translation_key: "photo" },
    // The user's OWN linked sensors, on the ORIGINAL hardware's device -
    // deliberately NOT device_id: DEVICE_ID, matching real-world Plant
    // Monitor devices vs. the Zigbee2MQTT (or other) sensor's own device.
    "sensor.zigbee_temp": { entity_id: "sensor.zigbee_temp", device_id: SOURCE_DEVICE_ID, platform: "mqtt" },
    "sensor.zigbee_humidity": { entity_id: "sensor.zigbee_humidity", device_id: SOURCE_DEVICE_ID, platform: "mqtt" },
    "sensor.zigbee_battery": { entity_id: "sensor.zigbee_battery", device_id: SOURCE_DEVICE_ID, platform: "mqtt" },
  };
}

function makeStates() {
  return {
    "sensor.pannenkoekenplant_puppy_advies": { entity_id: "sensor.pannenkoekenplant_puppy_advies", state: "\u2705 Alles OK, geen actie nodig.", attributes: {} },
    "sensor.pannenkoekenplant_puppy_verzorgingstip": {
      entity_id: "sensor.pannenkoekenplant_puppy_verzorgingstip",
      // Deliberately short/truncated .state (as HA's 255-char cap forces
      // in reality) vs. a longer, different full_text attribute - the
      // card must read from full_text, not .state, to pass this test.
      state: "Licht: Bright indirect light....",
      attributes: {
        full_text: "Licht: Bright indirect light.\nWatering: Let the top layer dry.\nToxicity: Non-toxic to pets.",
      },
    },
    "sensor.pannenkoekenplant_puppy_bodemvocht": {
      entity_id: "sensor.pannenkoekenplant_puppy_bodemvocht",
      state: "23",
      attributes: {
        unit_of_measurement: "%",
        temperature_entity_id: "sensor.zigbee_temp",
        humidity_entity_id: "sensor.zigbee_humidity",
        battery_entity_id: "sensor.zigbee_battery",
      },
    },
    "sensor.pannenkoekenplant_puppy_gezondheidsscore": { entity_id: "sensor.pannenkoekenplant_puppy_gezondheidsscore", state: "98", attributes: { unit_of_measurement: "pts" } },
    "sensor.pannenkoekenplant_puppy_droogsnelheid": { entity_id: "sensor.pannenkoekenplant_puppy_droogsnelheid", state: "1.2", attributes: { unit_of_measurement: "%/h" } },
    "sensor.pannenkoekenplant_puppy_waterbehoefte": { entity_id: "sensor.pannenkoekenplant_puppy_waterbehoefte", state: "Over ongeveer 6.0 uur", attributes: {} },
    "sensor.pannenkoekenplant_puppy_laatst_water_gegeven": { entity_id: "sensor.pannenkoekenplant_puppy_laatst_water_gegeven", state: "2026-09-16T10:00:00+00:00", attributes: {} },
    "sensor.pannenkoekenplant_puppy_wateringen_deze_week": { entity_id: "sensor.pannenkoekenplant_puppy_wateringen_deze_week", state: "2", attributes: {} },
    "binary_sensor.pannenkoekenplant_puppy_droog": { entity_id: "binary_sensor.pannenkoekenplant_puppy_droog", state: "off", attributes: {} },
    "binary_sensor.pannenkoekenplant_puppy_te_nat": { entity_id: "binary_sensor.pannenkoekenplant_puppy_te_nat", state: "off", attributes: {} },
    "number.pannenkoekenplant_puppy_droogte_drempel": { entity_id: "number.pannenkoekenplant_puppy_droogte_drempel", state: "20", attributes: {} },
    "number.pannenkoekenplant_puppy_overwater_drempel": { entity_id: "number.pannenkoekenplant_puppy_overwater_drempel", state: "65", attributes: {} },
    "image.pannenkoekenplant_puppy_foto": { entity_id: "image.pannenkoekenplant_puppy_foto", state: "2026-09-16T10:00:00+00:00", attributes: { entity_picture: "/api/image_proxy/image.pannenkoekenplant_puppy_foto?token=abc" } },
    "sensor.zigbee_temp": { entity_id: "sensor.zigbee_temp", state: "19.5", attributes: { device_class: "temperature", unit_of_measurement: "\u00b0C" } },
    "sensor.zigbee_humidity": { entity_id: "sensor.zigbee_humidity", state: "96", attributes: { device_class: "humidity", unit_of_measurement: "%" } },
    "sensor.zigbee_battery": { entity_id: "sensor.zigbee_battery", state: "100", attributes: { device_class: "battery", unit_of_measurement: "%" } },
  };
}

function makeHass({ withHistory = true } = {}) {
  const entities = makeEntities();
  const states = makeStates();
  const devices = { [DEVICE_ID]: { id: DEVICE_ID, name: "Pannenkoekenplant (Puppy)", name_by_user: null, model: "Chinese Money Plant" } };

  const nowSec = Date.now() / 1000;
  const historyResult = withHistory
    ? {
        "sensor.pannenkoekenplant_puppy_bodemvocht": [
          { s: "40", a: {}, lu: nowSec - 14 * 86400 },
          { s: "30", a: {}, lu: nowSec - 7 * 86400 },
          { s: "23", a: {}, lu: nowSec },
        ],
      }
    : { "sensor.pannenkoekenplant_puppy_bodemvocht": [] };

  const calls = [];
  const callWS = async (msg) => {
    calls.push(msg);
    return historyResult;
  };

  return { entities, states, devices, callWS, _calls: calls };
}

async function flushMicrotasks() {
  await new Promise((resolve) => setTimeout(resolve, 0));
  await new Promise((resolve) => setTimeout(resolve, 0));
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

  // --- Test 1: getStubConfig picks a plant_monitor device ---
  const hass = makeHass();
  const stub = PlantMonitorCardCtor.getStubConfig(hass);
  assert.strictEqual(stub.device_id, DEVICE_ID);
  console.log("test_get_stub_config: OK ->", stub);

  // --- Test 2: hero section renders correctly via auto-discovery ---
  const el = document.createElement("plant-monitor-card");
  el.setConfig({ device_id: DEVICE_ID });
  el.hass = hass;
  await flushMicrotasks();

  let html = el.innerHTML;
  assert.ok(html.includes("Pannenkoekenplant (Puppy)"), "device name missing from hero title");
  assert.ok(html.includes("23%"), "moisture % missing from hero");
  assert.ok(html.includes("19.5\u00b0C"), "temperature missing from hero (via device_class lookup)");
  assert.ok(html.includes("96%"), "humidity tile missing/wrong");
  assert.ok(html.includes("100%"), "battery tile missing/wrong");
  assert.ok(html.includes(">Gezond<"), "expected 'Gezond' status when dry=off/overwatered=off");
  assert.ok(html.includes("droog &lt;20%") || html.includes("droog <20%"), "dry threshold label missing");
  assert.ok(html.includes("nat &gt;65%") || html.includes("nat >65%"), "wet threshold label missing");
  assert.ok(html.includes("Over ongeveer 6.0 uur"), "water prediction missing");
  assert.ok(html.includes("Alles OK"), "advice text missing");
  console.log("test_hero_section_render: OK");

  // --- Test 3: history graph renders a path once callWS resolves ---
  assert.strictEqual(hass._calls.length, 1, `expected exactly one callWS call, got ${hass._calls.length}`);
  assert.strictEqual(hass._calls[0].type, "history/history_during_period");
  assert.strictEqual(JSON.stringify(hass._calls[0].entity_ids), JSON.stringify(["sensor.pannenkoekenplant_puppy_bodemvocht"]));
  html = el.innerHTML;
  assert.ok(html.includes("<svg"), "expected an svg history graph once history resolved");
  assert.ok(html.includes("<path"), "expected a path element in the graph");
  assert.ok(html.includes("GRIJS = OPTIMAAL 20-65%"), "optimal-band caption missing/wrong");
  console.log("test_history_graph_render: OK");

  // --- Test 4: no history yet -> friendly empty state, not a crash ---
  const hassNoHistory = makeHass({ withHistory: false });
  const el2 = document.createElement("plant-monitor-card");
  el2.setConfig({ device_id: DEVICE_ID });
  el2.hass = hassNoHistory;
  await flushMicrotasks();
  assert.ok(el2.innerHTML.includes("Nog niet genoeg geschiedenis"), "expected the empty-history message");
  console.log("test_history_empty_state: OK");

  // --- Test 5: care guide expandable section parses "Label: text" lines ---
  html = el.innerHTML;
  assert.ok(html.includes("<details"), "expected a <details> expandable section");
  assert.ok(html.includes("Chinese Money Plant"), "expected the device model in the care-guide summary");
  assert.ok(html.includes("<b>Licht:</b>"), "expected a Licht section label");
  assert.ok(html.includes("Bright indirect light"), "expected Light section content");
  assert.ok(html.includes("Non-toxic to pets"), "expected Toxicity section content");
  console.log("test_care_guide_render: OK");

  // --- Test 6: status badge flips to Droog / Te nat ---
  const hassDry = JSON.parse(JSON.stringify(makeHass()));
  hassDry.states["binary_sensor.pannenkoekenplant_puppy_droog"].state = "on";
  hassDry.callWS = async () => ({ "sensor.pannenkoekenplant_puppy_bodemvocht": [] });
  const el3 = document.createElement("plant-monitor-card");
  el3.setConfig({ device_id: DEVICE_ID });
  el3.hass = hassDry;
  assert.ok(el3.innerHTML.includes(">Droog<"), "expected Droog status badge");
  console.log("test_status_badge_dry: OK");

  // --- Test 7: manual entities override bypasses auto-discovery entirely ---
  const el4 = document.createElement("plant-monitor-card");
  el4.setConfig({
    title: "Manual Override Plant",
    entities: { advice: "sensor.pannenkoekenplant_puppy_advies" },
  });
  el4.hass = hass;
  assert.ok(el4.innerHTML.includes("Manual Override Plant"));
  assert.ok(el4.innerHTML.includes("Alles OK"));
  console.log("test_manual_entities_override: OK");

  // --- Test 8: HTML escaping (defend against a malicious/odd state string) ---
  const hassXss = JSON.parse(JSON.stringify(makeHass()));
  hassXss.states["sensor.pannenkoekenplant_puppy_gezondheidsscore"].state = "<script>x</script>";
  hassXss.callWS = async () => ({ "sensor.pannenkoekenplant_puppy_bodemvocht": [] });
  const el5 = document.createElement("plant-monitor-card");
  el5.setConfig({ device_id: DEVICE_ID });
  el5.hass = hassXss;
  assert.ok(!el5.innerHTML.includes("<script>x</script>"), "raw script tag leaked into innerHTML unescaped");
  console.log("test_html_escaping: OK");

  // --- Test 9: setConfig throws without device_id or entities ---
  let threw = false;
  try {
    document.createElement("plant-monitor-card").setConfig({});
  } catch (e) {
    threw = true;
  }
  assert.ok(threw, "setConfig should throw when neither device_id nor entities given");
  console.log("test_setconfig_requires_target: OK");

  // --- Test 10: clicking the hero dispatches hass-more-info for soil_moisture ---
  const el6 = document.createElement("plant-monitor-card");
  el6.setConfig({ device_id: DEVICE_ID });
  el6.hass = hass;
  let capturedDetail = null;
  el6.addEventListener("hass-more-info", (ev) => { capturedDetail = ev.detail; });
  el6.querySelector(".pm-hero-content").dispatchEvent(new dom.window.MouseEvent("click", { bubbles: true }));
  assert.ok(capturedDetail, "expected a hass-more-info event to fire on hero click");
  assert.strictEqual(capturedDetail.entityId, "sensor.pannenkoekenplant_puppy_bodemvocht");
  console.log("test_click_hero_opens_more_info: OK");

  // --- Test 11: Dutch care-guide categories and a visible expand chevron ---
  const hassDutch = makeHass();
  hassDutch.states["sensor.pannenkoekenplant_puppy_verzorgingstip"].attributes.full_text =
    "Licht: Helder, indirect licht.\nWater geven: Laat de bovenste laag opdrogen.\nGiftigheid: Niet giftig voor huisdieren.";
  const el7 = document.createElement("plant-monitor-card");
  el7.setConfig({ device_id: DEVICE_ID });
  el7.hass = hassDutch;
  const el7html = el7.innerHTML;
  assert.ok(el7html.includes("<b>Licht:</b>"), "expected Dutch 'Licht' category label");
  assert.ok(el7html.includes("<b>Water geven:</b>"), "expected Dutch 'Water geven' category label");
  assert.ok(el7html.includes("<em>Niet giftig voor huisdieren.</em>"), "expected Giftigheid rendered as italic footnote, not a labelled paragraph");
  assert.ok(!el7html.includes("<b>Giftigheid:</b>"), "Giftigheid should not appear as a regular labelled paragraph");
  assert.ok(el7html.includes('class="pm-care-chevron"'), "expected a visible expand/collapse chevron icon");
  console.log("test_dutch_categories_and_chevron: OK");

  // --- Test 12: graph hover shows a tooltip with date + value ---
  const el8 = document.createElement("plant-monitor-card");
  el8.setConfig({ device_id: DEVICE_ID });
  el8.hass = hass;
  await flushMicrotasks();
  const svgEl = el8.querySelector(".pm-graph-svg-inner svg");
  assert.ok(svgEl, "expected the graph svg to exist before testing hover");
  svgEl.getBoundingClientRect = () => ({ left: 0, width: 600, top: 0, height: 90 });
  el8._handleGraphHover({ clientX: 300 });
  const tooltip = el8.querySelector(".pm-tooltip");
  assert.strictEqual(tooltip.style.display, "block", "expected the tooltip to become visible on hover");
  assert.ok(/\d+%/.test(tooltip.textContent), "expected the tooltip to show a percentage value");
  el8._hideGraphTooltip();
  assert.strictEqual(tooltip.style.display, "none", "expected the tooltip to hide again");
  console.log("test_graph_hover_tooltip: OK");

  console.log("\nAll card tests passed.");
}

run().catch((err) => {
  console.error("FAILED:", err);
  process.exit(1);
});
