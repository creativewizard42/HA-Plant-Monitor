/**
 * Plant Monitor Card
 *
 * A single-file, dependency-free custom Lovelace card bundled with the
 * Plant Monitor integration. One card = one plant. Three sections, matching
 * the project's own reference dashboard:
 *   1. Hero: photo background, moisture/temperature readout, a red-green
 *      gradient bar, humidity/battery/temperature tiles, water prediction
 *      and advice.
 *   2. A 14-day soil-moisture history graph with the "optimal" dry/wet
 *      range shaded, fetched via the history/history_during_period
 *      websocket command.
 *   3. An expandable, multi-section care guide (light, watering, humidity,
 *      temperature, fertilizing, repotting, common problems, toxicity),
 *      parsed from the care_tip sensor's "Label: text" lines.
 *
 * Entities are auto-discovered from `hass.entities` by matching
 * `device_id` + `translation_key` - translation_key is used deliberately
 * because it is stable across languages, unlike entity_id (which is
 * generated from the *translated* entity name, e.g. "advies" in Dutch vs
 * "advice" in English, and therefore unsafe to pattern-match on).
 *
 * If auto-discovery doesn't find something (older HA without the
 * `hass.entities` registry mirror, or a role missing for some reason), an
 * explicit `entities:` map in the card config always overrides it.
 */

const HISTORY_DAYS = 14;
const HISTORY_REFRESH_MS = 5 * 60 * 1000;

const ROLE_BY_TRANSLATION_KEY = {
  advice: "advice",
  care_tip: "care_tip",
  soil_moisture: "soil_moisture",
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
  advice: "advice", advies: "advice",
  care_tip: "care_tip", verzorgingstip: "care_tip",
  soil_moisture: "soil_moisture", bodemvocht: "soil_moisture",
  health_score: "health_score", gezondheidsscore: "health_score",
  drying_rate: "drying_rate", droogsnelheid: "drying_rate",
  water_prediction: "water_prediction", waterbehoefte: "water_prediction",
  last_watered: "last_watered", laatst_water_gegeven: "last_watered",
  waterings_this_week: "waterings_this_week", wateringen_deze_week: "waterings_this_week",
  dry: "dry", droog: "dry",
  overwatered: "overwatered", te_nat: "overwatered",
  dry_threshold: "dry_threshold", droogte_drempel: "dry_threshold",
  wet_threshold: "wet_threshold", overwater_drempel: "wet_threshold",
  photo: "photo", foto: "photo",
};

const CARE_SECTION_ICONS = {
  light: "\u2600\ufe0f",
  watering: "\ud83d\udca7",
  humidity: "\ud83c\udf2b\ufe0f",
  temperature: "\ud83c\udf21\ufe0f",
  fertilizing: "\ud83c\udf31",
  repotting: "\ud83e\udeb4",
  "common problems": "\u26a0\ufe0f",
  toxicity: "\ud83d\udc3e",
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
    this._historyPoints = null;
    this._historyFetchedAt = 0;
    this._historyForEntity = null;
  }

  getCardSize() {
    return 9;
  }

  set hass(hass) {
    this._hass = hass;
    if (!this._entityIds) {
      this._resolveEntities();
    }
    this._render();
    this._maybeFetchHistory();
  }

  _resolveEntities() {
    const deviceId = this._config.device_id;
    const registry = (this._hass && this._hass.entities) || {};
    const found = {};

    for (const entry of Object.values(registry)) {
      if (entry.device_id !== deviceId) continue;
      let role = entry.translation_key ? ROLE_BY_TRANSLATION_KEY[entry.translation_key] : undefined;
      if (!role) {
        const objectId = entry.entity_id.split(".")[1];
        const suffix2 = objectId.split("_").slice(-2).join("_");
        const suffix1 = objectId.split("_").slice(-1)[0];
        role = ROLE_BY_ID_SUFFIX[suffix2] || ROLE_BY_ID_SUFFIX[suffix1];
      }
      if (role) found[role] = entry.entity_id;
    }

    this._entityIds = found;
  }

  _entity(role) {
    const id = this._entityIds && this._entityIds[role];
    return id ? this._hass.states[id] : undefined;
  }

  _deviceTitleAndModel() {
    const anyId = Object.values(this._entityIds || {})[0];
    if (!anyId || !this._hass || !this._hass.entities || !this._hass.devices) {
      return { name: this._config.title || "Plant", model: null };
    }
    const reg = this._hass.entities[anyId];
    const device = reg && this._hass.devices[reg.device_id];
    return {
      name: this._config.title || (device && (device.name_by_user || device.name)) || "Plant",
      model: device ? device.model : null,
    };
  }

  async _maybeFetchHistory() {
    const soilId = this._entityIds && this._entityIds.soil_moisture;
    if (!soilId || !this._hass || typeof this._hass.callWS !== "function") return;

    const now = Date.now();
    const entityChanged = this._historyForEntity !== soilId;
    if (!entityChanged && now - this._historyFetchedAt < HISTORY_REFRESH_MS) return;
    this._historyFetchedAt = now;
    this._historyForEntity = soilId;

    try {
      const start = new Date(now - HISTORY_DAYS * 24 * 60 * 60 * 1000).toISOString();
      const result = await this._hass.callWS({
        type: "history/history_during_period",
        start_time: start,
        entity_ids: [soilId],
        minimal_response: false,
        significant_changes_only: false,
        no_attributes: true,
      });
      const raw = (result && result[soilId]) || [];
      this._historyPoints = raw
        .map((entry) => {
          const tsSeconds = entry.lu ?? entry.last_updated;
          const stateStr = entry.s ?? entry.state;
          const value = parseFloat(stateStr);
          if (!Number.isFinite(tsSeconds) || !Number.isFinite(value)) return null;
          return { t: tsSeconds * 1000, v: value };
        })
        .filter(Boolean);
    } catch (err) {
      this._historyPoints = null;
    }
    this._renderGraph();
  }

  _render() {
    if (!this._hass) return;

    if (!this._built) {
      this._buildSkeleton();
      this._built = true;
    }

    this._renderHero();
    this._renderGraph();
    this._renderCareGuide();
  }

  _buildSkeleton() {
    this.innerHTML = `
      <ha-card>
        <style>${this._css()}</style>
        <div class="pm-hero">
          <div class="pm-hero-photo"></div>
          <div class="pm-hero-scrim"></div>
          <div class="pm-hero-top">
            <div class="pm-hero-title"></div>
            <div class="pm-hero-status"></div>
          </div>
          <div class="pm-hero-mid">
            <div class="pm-hero-moisture"></div>
            <div class="pm-hero-temp"></div>
          </div>
          <div class="pm-bar-wrap">
            <div class="pm-bar"><div class="pm-bar-marker"></div></div>
            <div class="pm-bar-labels">
              <span class="pm-bar-dry"></span>
              <span class="pm-bar-wet"></span>
            </div>
          </div>
        </div>
        <div class="pm-tiles"></div>
        <div class="pm-lines">
          <div class="pm-water-need"></div>
          <div class="pm-advice"></div>
        </div>

        <div class="pm-section-divider"></div>
        <div class="pm-graph-section">
          <div class="pm-graph-header">
            <span class="pm-graph-title">BODEMVOCHT</span>
            <span class="pm-graph-days">${HISTORY_DAYS} DAGEN</span>
          </div>
          <div class="pm-graph-svg-slot"></div>
          <div class="pm-graph-footer">
            <span>${HISTORY_DAYS} D TERUG</span>
            <span class="pm-graph-optimal"></span>
            <span>NU</span>
          </div>
        </div>

        <div class="pm-section-divider"></div>
        <details class="pm-care">
          <summary class="pm-care-summary"></summary>
          <div class="pm-care-body"></div>
        </details>
      </ha-card>`;
  }

  _css() {
    return `
      ha-card { overflow: hidden; padding: 0; background: var(--card-background-color); }
      .pm-hero { position: relative; height: 190px; overflow: hidden; color: white; }
      .pm-hero-photo {
        position: absolute; inset: 0; background-size: cover; background-position: center;
        background-color: var(--secondary-background-color);
      }
      .pm-hero-scrim {
        position: absolute; inset: 0;
        background: linear-gradient(to top, rgba(10,10,10,0.92) 0%, rgba(10,10,10,0.35) 55%, rgba(10,10,10,0.05) 100%);
      }
      .pm-hero-top { position: absolute; top: 10px; left: 12px; right: 12px; display: flex; align-items: flex-start; justify-content: space-between; z-index: 1; }
      .pm-hero-title { font-size: 16px; font-weight: 700; text-shadow: 0 1px 4px rgba(0,0,0,0.8); }
      .pm-hero-status {
        padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 700;
        background: rgba(0,0,0,0.5); backdrop-filter: blur(3px); white-space: nowrap;
      }
      .pm-hero-mid { position: absolute; left: 12px; right: 12px; bottom: 46px; display: flex; align-items: baseline; gap: 12px; z-index: 1; }
      .pm-hero-moisture { font-size: 34px; font-weight: 800; text-shadow: 0 2px 6px rgba(0,0,0,0.8); }
      .pm-hero-temp { font-size: 18px; font-weight: 600; opacity: 0.95; text-shadow: 0 2px 6px rgba(0,0,0,0.8); }
      .pm-bar-wrap { position: absolute; left: 12px; right: 12px; bottom: 14px; z-index: 1; }
      .pm-bar {
        position: relative; height: 6px; border-radius: 3px;
        background: linear-gradient(to right, #ef4444, #f59e0b, #22c55e, #3b82f6);
      }
      .pm-bar-marker {
        position: absolute; top: -3px; width: 2px; height: 12px; background: white;
        box-shadow: 0 0 3px rgba(0,0,0,0.8); transform: translateX(-1px);
      }
      .pm-bar-labels { display: flex; justify-content: space-between; font-size: 10px; opacity: 0.85; margin-top: 4px; }
      .pm-tiles {
        display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px;
        padding: 12px; box-sizing: border-box;
      }
      .pm-tile {
        background: var(--secondary-background-color); border-radius: 10px;
        padding: 8px 4px; text-align: center;
      }
      .pm-tile-icon { font-size: 15px; }
      .pm-tile-value { font-size: 14px; font-weight: 700; color: var(--primary-text-color); margin-top: 2px; }
      .pm-tile-label { font-size: 10px; color: var(--secondary-text-color); margin-top: 1px; }
      .pm-lines { padding: 0 12px 12px; display: flex; flex-direction: column; gap: 6px; }
      .pm-water-need, .pm-advice {
        font-size: 13px; color: var(--primary-text-color);
        background: var(--secondary-background-color); border-radius: 8px; padding: 8px 10px;
      }
      .pm-section-divider { height: 1px; background: var(--divider-color); margin: 0; }
      .pm-graph-section { padding: 12px; box-sizing: border-box; }
      .pm-graph-header { display: flex; justify-content: space-between; font-size: 11px; font-weight: 700; letter-spacing: 0.04em; color: var(--secondary-text-color); margin-bottom: 6px; }
      .pm-graph-svg-slot svg { display: block; width: 100%; height: auto; }
      .pm-graph-footer { display: flex; justify-content: space-between; font-size: 10px; color: var(--secondary-text-color); margin-top: 4px; }
      .pm-graph-optimal { font-weight: 600; }
      .pm-graph-empty { font-size: 12px; color: var(--secondary-text-color); text-align: center; padding: 24px 0; }
      .pm-care { padding: 4px 12px 12px; }
      .pm-care-summary { cursor: pointer; font-size: 13px; font-weight: 600; color: var(--primary-text-color); padding: 8px 0; list-style: none; }
      .pm-care-summary::-webkit-details-marker { display: none; }
      .pm-care-summary::before { content: "\\25B6"; display: inline-block; margin-right: 6px; font-size: 10px; transition: transform 0.15s ease; }
      details[open] .pm-care-summary::before { transform: rotate(90deg); }
      .pm-care-body { padding-top: 6px; display: flex; flex-direction: column; gap: 10px; }
      .pm-care-item b { display: block; font-size: 12px; color: var(--secondary-text-color); text-transform: uppercase; letter-spacing: 0.03em; margin-bottom: 2px; }
      .pm-care-item span { font-size: 13px; color: var(--primary-text-color); line-height: 1.4; }
    `;
  }

  _renderHero() {
    const soil = this._entity("soil_moisture");
    const tempEntity = this._entityStateForRole("temperature");
    const dryTh = this._entity("dry_threshold");
    const wetTh = this._entity("wet_threshold");
    const dry = this._entity("dry");
    const overwatered = this._entity("overwatered");
    const photo = this._entity("photo");
    const advice = this._entity("advice");
    const prediction = this._entity("water_prediction");
    const battery = this._entityStateForRole("battery");
    const humidity = this._entityStateForRole("humidity");

    const { name } = this._deviceTitleAndModel();
    this.querySelector(".pm-hero-title").textContent = `\ud83c\udf3f ${name}`;

    const soilVal = soil ? parseFloat(soil.state) : null;
    const dryVal = dryTh ? parseFloat(dryTh.state) : 20;
    const wetVal = wetTh ? parseFloat(wetTh.state) : 70;

    let statusText = "Onbekend";
    let statusColor = "rgba(255,255,255,0.5)";
    if (dry && dry.state === "on") { statusText = "Dorstig"; statusColor = "#ef4444"; }
    else if (overwatered && overwatered.state === "on") { statusText = "Te nat"; statusColor = "#3b82f6"; }
    else if (soilVal !== null) { statusText = "Gezond"; statusColor = "#22c55e"; }
    const statusEl = this.querySelector(".pm-hero-status");
    statusEl.textContent = statusText;
    statusEl.style.border = `1px solid ${statusColor}`;
    statusEl.style.color = statusColor;

    const photoUrl = photo && photo.attributes && photo.attributes.entity_picture;
    this.querySelector(".pm-hero-photo").style.backgroundImage = photoUrl ? `url(${photoUrl})` : "none";

    this.querySelector(".pm-hero-moisture").textContent = soilVal !== null ? `${soilVal}%` : "\u2014";
    this.querySelector(".pm-hero-temp").textContent = tempEntity ? `${tempEntity.state}\u00b0C` : "";

    this.querySelector(".pm-bar-marker").style.left = `${Math.max(0, Math.min(100, soilVal ?? 0))}%`;
    this.querySelector(".pm-bar-dry").textContent = `droog <${dryVal}%`;
    this.querySelector(".pm-bar-wet").textContent = `nat >${wetVal}%`;

    this.querySelector(".pm-tiles").innerHTML = [
      this._tile("\ud83d\udca7", humidity ? `${humidity.state}%` : "\u2014", "Lucht"),
      this._tile("\ud83d\udd0b", battery ? `${battery.state}%` : "\u2014", "Batterij"),
      this._tile("\ud83c\udf21\ufe0f", tempEntity ? `${tempEntity.state}\u00b0` : "\u2014", "Temp"),
    ].join("");

    this.querySelector(".pm-water-need").innerHTML =
      `\ud83d\udca7 <b>Waterbehoefte:</b> ${this._escape(prediction ? prediction.state : "Onbekend")}`;
    this.querySelector(".pm-advice").innerHTML = advice ? this._escape(advice.state) : "";
  }

  // temperature/humidity/battery aren't in ROLE_BY_* (they're the user's
  // own linked sensors, not Plant Monitor's own entities) - look them up
  // via the device's other entities by device_class instead.
  _entityStateForRole(kind) {
    const anyId = Object.values(this._entityIds || {})[0];
    if (!anyId || !this._hass || !this._hass.entities) return undefined;
    const reg = this._hass.entities[anyId];
    const deviceId = reg && reg.device_id;
    if (!deviceId) return undefined;
    for (const entry of Object.values(this._hass.entities)) {
      if (entry.device_id !== deviceId) continue;
      const state = this._hass.states[entry.entity_id];
      if (!state) continue;
      const deviceClass = state.attributes && state.attributes.device_class;
      if (kind === "temperature" && deviceClass === "temperature") return state;
      if (kind === "humidity" && deviceClass === "humidity") return state;
      if (kind === "battery" && deviceClass === "battery") return state;
    }
    return undefined;
  }

  _tile(icon, value, label) {
    return `
      <div class="pm-tile">
        <div class="pm-tile-icon">${icon}</div>
        <div class="pm-tile-value">${this._escape(value)}</div>
        <div class="pm-tile-label">${this._escape(label)}</div>
      </div>`;
  }

  _renderGraph() {
    const slot = this.querySelector(".pm-graph-svg-slot");
    if (!slot) return;

    const dryTh = this._entity("dry_threshold");
    const wetTh = this._entity("wet_threshold");
    const dryVal = dryTh ? parseFloat(dryTh.state) : 20;
    const wetVal = wetTh ? parseFloat(wetTh.state) : 70;
    this.querySelector(".pm-graph-optimal").textContent =
      `GRIJS = OPTIMAAL ${dryVal}-${wetVal}%`;

    const points = this._historyPoints;
    if (!points || points.length < 2) {
      slot.innerHTML = `<div class="pm-graph-empty">Nog niet genoeg geschiedenis (${HISTORY_DAYS} dagen nodig)</div>`;
      return;
    }

    const width = 600;
    const height = 140;
    const toY = (v) => height - (Math.max(0, Math.min(100, v)) / 100) * height;
    const minT = points[0].t;
    const maxT = points[points.length - 1].t;
    const span = Math.max(1, maxT - minT);
    const toX = (t) => ((t - minT) / span) * width;

    const bandTop = toY(wetVal);
    const bandBottom = toY(dryVal);

    const path = points
      .map((p, i) => `${i === 0 ? "M" : "L"}${toX(p.t).toFixed(1)},${toY(p.v).toFixed(1)}`)
      .join(" ");

    slot.innerHTML = `
      <svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none">
        <rect x="0" y="${bandTop.toFixed(1)}" width="${width}" height="${(bandBottom - bandTop).toFixed(1)}"
          fill="var(--secondary-text-color)" opacity="0.15" />
        <path d="${path}" fill="none" stroke="#22c55e" stroke-width="2" />
      </svg>`;
  }

  _renderCareGuide() {
    const careTip = this._entity("care_tip");
    const summary = this.querySelector(".pm-care-summary");
    const body = this.querySelector(".pm-care-body");
    const { model } = this._deviceTitleAndModel();

    summary.textContent = model ? `Verzorgingstips \u2014 ${model}` : "Verzorgingstips";

    if (!careTip || !careTip.state) {
      body.innerHTML = `<div class="pm-care-item"><span>Geen verzorgingstip ingesteld.</span></div>`;
      return;
    }

    // care_tip's state is "Label: text" lines, one section per line - see
    // species_data.json / the config flow's care step.
    const lines = String(careTip.state).split("\n").filter(Boolean);
    body.innerHTML = lines
      .map((line) => {
        const idx = line.indexOf(":");
        if (idx === -1) return `<div class="pm-care-item"><span>${this._escape(line)}</span></div>`;
        const label = line.slice(0, idx).trim();
        const text = line.slice(idx + 1).trim();
        const icon = CARE_SECTION_ICONS[label.toLowerCase()] || "\ud83c\udf3f";
        return `<div class="pm-care-item"><b>${icon} ${this._escape(label)}</b><span>${this._escape(text)}</span></div>`;
      })
      .join("");
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
  description: "Photo hero, 14-day moisture history and expandable care guide for one Plant Monitor plant.",
});
