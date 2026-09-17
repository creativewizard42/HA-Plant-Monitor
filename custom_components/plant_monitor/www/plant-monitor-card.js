/**
 * Plant Monitor Card
 *
 * A single-file, dependency-free custom Lovelace card bundled with the
 * Plant Monitor integration. One card = one plant, matching how the rest
 * of the integration is organised (one config entry = one plant).
 *
 * Entities are auto-discovered from `hass.entities` by matching
 * `device_id` + `translation_key` - translation_key is used deliberately
 * because it is stable across languages, unlike entity_id (which is
 * generated from the *translated* entity name, e.g. "advies" in Dutch vs
 * "advice" in English, and therefore unsafe to pattern-match on).
 *
 * If auto-discovery doesn't find something (older HA without the
 * `hass.entities` registry mirror, or a role missing for some reason), an
 * explicit `entities:` map in the card config always overrides it - see
 * README "Dashboard" section for the full list of keys.
 */

const ROLE_BY_TRANSLATION_KEY = {
  advice: "advice",
  care_tip: "care_tip",
  health_score: "health_score",
  drying_rate: "drying_rate",
  water_prediction: "water_prediction",
  last_watered: "last_watered",
  waterings_this_week: "waterings_this_week",
  dry: "dry",
  overwatered: "overwatered",
  dry_threshold: "dry_threshold",
  wet_threshold: "wet_threshold",
  photo: "photo",
};

// Fallback only used when translation_key isn't available on an entry:
// covers both English and Dutch entity_id suffixes (the two languages
// this integration ships translations for).
const ROLE_BY_ID_SUFFIX = {
  advice: "advice",
  advies: "advice",
  care_tip: "care_tip",
  verzorgingstip: "care_tip",
  health_score: "health_score",
  gezondheidsscore: "health_score",
  drying_rate: "drying_rate",
  droogsnelheid: "drying_rate",
  water_prediction: "water_prediction",
  waterbehoefte: "water_prediction",
  last_watered: "last_watered",
  laatst_water_gegeven: "last_watered",
  waterings_this_week: "waterings_this_week",
  wateringen_deze_week: "waterings_this_week",
  dry: "dry",
  droog: "dry",
  overwatered: "overwatered",
  te_nat: "overwatered",
  dry_threshold: "dry_threshold",
  droogte_drempel: "dry_threshold",
  wet_threshold: "wet_threshold",
  overwater_drempel: "wet_threshold",
  photo: "photo",
  foto: "photo",
};

class PlantMonitorCard extends HTMLElement {
  static getStubConfig(hass) {
    const entities = hass && hass.entities ? Object.values(hass.entities) : [];
    const first = entities.find((e) => e.platform === "plant_monitor");
    return { device_id: first ? first.device_id : "" };
  }

  setConfig(config) {
    if (!config || (!config.device_id && !config.entities)) {
      throw new Error("Plant Monitor Card: set either 'device_id' or an 'entities' map.");
    }
    this._config = config;
    this._entityIds = config.entities ? { ...config.entities } : null;
    this._built = false;
  }

  getCardSize() {
    return 4;
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._entityIds) {
      this._resolveEntities();
    }
    this._render();
  }

  _resolveEntities() {
    const deviceId = this._config.device_id;
    const registry = (this._hass && this._hass.entities) || {};
    const found = {};

    for (const entry of Object.values(registry)) {
      if (entry.device_id !== deviceId) continue;
      let role = entry.translation_key ? ROLE_BY_TRANSLATION_KEY[entry.translation_key] : undefined;
      if (!role) {
        const suffix = entry.entity_id.split(".")[1].split("_").slice(-2).join("_");
        const lastWord = entry.entity_id.split(".")[1].split("_").slice(-1)[0];
        role = ROLE_BY_ID_SUFFIX[suffix] || ROLE_BY_ID_SUFFIX[lastWord];
      }
      if (role) found[role] = entry.entity_id;
    }

    this._entityIds = found;
  }

  _entity(role) {
    const id = this._entityIds && this._entityIds[role];
    return id ? this._hass.states[id] : undefined;
  }

  _friendlyDeviceName() {
    const anyState = Object.values(this._entityIds || {})
      .map((id) => this._hass.states[id])
      .find(Boolean);
    if (!anyState) return "Plant";
    const fullName = anyState.attributes.friendly_name || "Plant";
    // Entity friendly_name is usually "<Device> <Entity>" - strip the
    // trailing entity part heuristically by taking everything the device
    // name itself doesn't already tell us; simplest safe bet: show it as-is
    // minus the last word if it clearly matches a known role word.
    return fullName;
  }

  _render() {
    if (!this._hass) return;

    const advice = this._entity("advice");
    const careTip = this._entity("care_tip");
    const health = this._entity("health_score");
    const dryingRate = this._entity("drying_rate");
    const prediction = this._entity("water_prediction");
    const lastWatered = this._entity("last_watered");
    const wateringsWeek = this._entity("waterings_this_week");
    const dry = this._entity("dry");
    const overwatered = this._entity("overwatered");
    const photo = this._entity("photo");

    const title = this._config.title || this._deviceTitleFromAnyEntity() || "Plant Monitor";

    const statusColor = dry && dry.state === "on"
      ? "var(--error-color, #db4437)"
      : overwatered && overwatered.state === "on"
        ? "var(--info-color, #039be5)"
        : "var(--success-color, #43a047)";
    const statusLabel = dry && dry.state === "on"
      ? "Dry"
      : overwatered && overwatered.state === "on"
        ? "Overwatered"
        : "OK";

    const photoUrl = photo && photo.attributes.entity_picture;

    const tile = (label, stateObj, unit) => {
      if (!stateObj) return "";
      const value = stateObj.attributes.unit_of_measurement
        ? `${stateObj.state} ${stateObj.attributes.unit_of_measurement}`
        : stateObj.state;
      return `
        <div class="pm-tile">
          <div class="pm-tile-value">${this._escape(value)}</div>
          <div class="pm-tile-label">${this._escape(label)}</div>
        </div>`;
    };

    if (!this._built) {
      this.innerHTML = `
        <ha-card>
          <style>
            .pm-wrap { padding: 16px; display: flex; flex-direction: column; gap: 12px; }
            .pm-header { display: flex; align-items: center; gap: 12px; }
            .pm-photo {
              width: 64px; height: 64px; border-radius: 12px; object-fit: cover;
              background: var(--secondary-background-color);
              flex-shrink: 0;
            }
            .pm-photo-placeholder {
              width: 64px; height: 64px; border-radius: 12px;
              background: var(--secondary-background-color);
              display: flex; align-items: center; justify-content: center;
              font-size: 28px; flex-shrink: 0;
            }
            .pm-title { font-size: 18px; font-weight: 500; color: var(--primary-text-color); }
            .pm-status {
              margin-left: auto; padding: 4px 10px; border-radius: 12px;
              font-size: 12px; font-weight: 600; color: white; white-space: nowrap;
            }
            .pm-text-block {
              background: var(--secondary-background-color);
              border-radius: 8px; padding: 10px 12px; font-size: 14px;
              color: var(--primary-text-color); white-space: pre-line;
            }
            .pm-text-block b { display: block; margin-bottom: 4px; color: var(--secondary-text-color); font-size: 12px; text-transform: uppercase; }
            .pm-tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(90px, 1fr)); gap: 8px; }
            .pm-tile {
              background: var(--secondary-background-color);
              border-radius: 8px; padding: 8px; text-align: center;
            }
            .pm-tile-value { font-size: 15px; font-weight: 600; color: var(--primary-text-color); }
            .pm-tile-label { font-size: 10px; color: var(--secondary-text-color); margin-top: 2px; }
          </style>
          <div class="pm-wrap">
            <div class="pm-header">
              <div class="pm-photo-slot"></div>
              <div class="pm-title"></div>
              <div class="pm-status"></div>
            </div>
            <div class="pm-advice pm-text-block" style="display:none"><b>Advice</b><span></span></div>
            <div class="pm-caretip pm-text-block" style="display:none"><b>Care tip</b><span></span></div>
            <div class="pm-tiles"></div>
          </div>
        </ha-card>`;
      this._built = true;
    }

    this.querySelector(".pm-title").textContent = title;

    const statusEl = this.querySelector(".pm-status");
    statusEl.textContent = statusLabel;
    statusEl.style.background = statusColor;

    const photoSlot = this.querySelector(".pm-photo-slot");
    photoSlot.innerHTML = photoUrl
      ? `<img class="pm-photo" src="${photoUrl}" alt="">`
      : `<div class="pm-photo-placeholder">🌿</div>`;

    const adviceBlock = this.querySelector(".pm-advice");
    if (advice) {
      adviceBlock.style.display = "";
      adviceBlock.querySelector("span").textContent = advice.state;
    }

    const tipBlock = this.querySelector(".pm-caretip");
    if (careTip) {
      tipBlock.style.display = "";
      tipBlock.querySelector("span").textContent = careTip.state;
    }

    this.querySelector(".pm-tiles").innerHTML = [
      tile("Health", health),
      tile("Drying rate", dryingRate),
      tile("Prediction", prediction),
      tile("Last watered", lastWatered),
      tile("Waterings/wk", wateringsWeek),
    ].join("");
  }

  _deviceTitleFromAnyEntity() {
    const anyId = Object.values(this._entityIds || {})[0];
    if (!anyId || !this._hass) return null;
    const reg = this._hass.entities && this._hass.entities[anyId];
    const deviceId = reg && reg.device_id;
    const device = deviceId && this._hass.devices && this._hass.devices[deviceId];
    return device ? device.name_by_user || device.name : null;
  }

  _escape(value) {
    const div = document.createElement("div");
    div.textContent = String(value);
    return div.innerHTML;
  }
}

customElements.define("plant-monitor-card", PlantMonitorCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "plant-monitor-card",
  name: "Plant Monitor Card",
  description: "Shows one plant's photo, advice, care tip and key stats from the Plant Monitor integration.",
});
