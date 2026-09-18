/**
 * Plant Monitor Card
 *
 * A single-file, dependency-free custom Lovelace card bundled with the
 * Plant Monitor integration. One card = one plant. Visually aligned with
 * the project's own hand-built reference dashboard (full-bleed photo hero
 * with a glass-morphism overlay, a dark history-graph panel, and a
 * flowing markdown-style expandable care guide):
 *   1. Hero: the photo IS the card background for its full height; name +
 *      status pill top, moisture/temperature readout, a red-green-blue
 *      gradient bar, three glass tiles (humidity/battery/temperature) and
 *      a water-need/advice footnote all overlaid on a bottom-up scrim.
 *   2. A dark panel with a 14-day soil-moisture history graph (smoothed
 *      line, shaded "optimal" dry/wet band) fetched via the
 *      history/history_during_period websocket command.
 *   3. An expandable care guide rendered as flowing bold-labelled
 *      paragraphs (Light/Watering/Humidity/.../Toxicity), parsed from the
 *      care_tip sensor's "Label: text" lines.
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

  // temperature/humidity/battery aren't Plant Monitor's own entities and
  // are NOT on the same HA "device" as this integration's entities either
  // (they stay on the original hardware's device) - so we read the
  // actual linked entity_ids straight from the soil_moisture sensor's own
  // attributes (exposed there server-side) instead of guessing.
  _entityStateForRole(kind) {
    const soil = this._entity("soil_moisture");
    if (!soil) return undefined;
    const attrKey = `${kind}_entity_id`;
    const linkedId = soil.attributes && soil.attributes[attrKey];
    return linkedId ? this._hass.states[linkedId] : undefined;
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
          <div class="pm-hero-scrim"></div>
          <div class="pm-hero-top">
            <div class="pm-hero-title"></div>
            <div class="pm-hero-status"><ha-icon class="pm-status-icon"></ha-icon><span class="pm-status-text"></span></div>
          </div>
          <div class="pm-hero-content">
            <div class="pm-hero-mid">
              <div class="pm-hero-moisture"></div>
              <div class="pm-hero-temp"></div>
            </div>
            <div class="pm-bar"><div class="pm-bar-marker"></div></div>
            <div class="pm-bar-labels">
              <span class="pm-bar-dry"></span>
              <span class="pm-bar-wet"></span>
            </div>
            <div class="pm-tiles"></div>
            <div class="pm-footnote">
              <div><b>\ud83d\udca7 Waterbehoefte:</b> <span class="pm-water-need"></span></div>
              <div class="pm-advice"></div>
            </div>
          </div>
        </div>

        <div class="pm-graph-panel">
          <div class="pm-graph-header">
            <span class="pm-graph-title">BODEMVOCHT</span>
            <span class="pm-graph-days">${HISTORY_DAYS} DAGEN</span>
          </div>
          <div class="pm-graph-svg-slot">
            <div class="pm-graph-svg-inner"></div>
            <div class="pm-tooltip"></div>
          </div>
          <div class="pm-graph-footer">
            <span>${HISTORY_DAYS} D TERUG</span>
            <span class="pm-graph-optimal"></span>
            <span>NU</span>
          </div>
        </div>

        <details class="pm-care">
          <summary class="pm-care-summary"><span class="pm-care-chevron">\u25b6</span><span class="pm-care-summary-text"></span></summary>
          <div class="pm-care-body"></div>
        </details>
      </ha-card>`;

    this.querySelector(".pm-hero-content").addEventListener("click", () => {
      const soilId = this._entityIds && this._entityIds.soil_moisture;
      if (!soilId) return;
      this.dispatchEvent(
        new CustomEvent("hass-more-info", {
          bubbles: true,
          composed: true,
          detail: { entityId: soilId },
        })
      );
    });

    const graphSlot = this.querySelector(".pm-graph-svg-slot");
    graphSlot.addEventListener("mousemove", (ev) => this._handleGraphHover(ev));
    graphSlot.addEventListener("mouseleave", () => this._hideGraphTooltip());
  }

  _css() {
    return `
      ha-card { overflow: hidden; padding: 0; background: var(--card-background-color); }

      .pm-hero {
        position: relative; min-height: 260px; overflow: hidden; color: white;
        background-color: #111; background-size: cover; background-position: center;
        display: flex; flex-direction: column; justify-content: flex-end;
        border-radius: 18px 18px 0 0; box-shadow: 0 6px 20px rgba(0,0,0,0.3);
      }
      .pm-hero-scrim {
        position: absolute; inset: 0;
        background: linear-gradient(0deg, rgba(6,9,7,0.94) 0%, rgba(6,9,7,0.82) 55%, rgba(6,9,7,0.1) 100%);
      }
      .pm-hero-top { position: absolute; top: 10px; left: 12px; right: 12px; display: flex; align-items: flex-start; justify-content: space-between; z-index: 1; }
      .pm-hero-title { font-size: 16px; font-weight: 800; color: #f8fafc; text-shadow: 0 1px 5px rgba(0,0,0,0.9); }
      .pm-hero-status {
        background: var(--pm-status-color, #94a3b8); color: #0b1220; font-size: 11px; font-weight: 800;
        padding: 4px 10px; border-radius: 999px; display: flex; align-items: center; gap: 4px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.5); white-space: nowrap;
      }
      .pm-status-icon { --mdc-icon-size: 13px; }
      .pm-hero-content { position: relative; z-index: 1; padding: 46px 12px 12px 12px; }
      .pm-hero-mid { display: flex; align-items: baseline; gap: 14px; }
      .pm-hero-moisture { font-size: 32px; font-weight: 800; color: var(--pm-status-color, #f1f5f9); line-height: 1; }
      .pm-hero-temp { font-size: 20px; font-weight: 700; color: #f1f5f9; line-height: 1; }
      .pm-bar {
        position: relative; height: 7px; border-radius: 4px; margin-top: 9px;
      }
      .pm-bar-marker {
        position: absolute; top: -3px; width: 4px; height: 13px; background: #fff;
        border-radius: 2px; box-shadow: 0 0 4px rgba(0,0,0,0.9); transform: translateX(-2px);
      }
      .pm-bar-labels { display: flex; justify-content: space-between; font-size: 9.5px; color: #9ca3af; margin-top: 3px; }
      .pm-tiles { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin-top: 11px; }
      .pm-tile {
        background: rgba(255,255,255,0.09); border-radius: 10px; padding: 6px 4px; text-align: center;
      }
      .pm-tile ha-icon { --mdc-icon-size: 15px; }
      .pm-tile-value { font-size: 12.5px; font-weight: 700; color: #f1f5f9; }
      .pm-tile-label { font-size: 8.5px; color: #9ca3af; }
      .pm-footnote {
        margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.12);
        font-size: 10.5px; color: #e2e8f0; line-height: 1.45;
      }
      .pm-advice { margin-top: 3px; color: #cbd5e1; }

      .pm-graph-panel {
        background: #0b1220; border: 1px solid rgba(255,255,255,0.08);
        margin: 8px; border-radius: 14px; padding: 12px 14px 10px 14px; box-sizing: border-box;
      }
      .pm-graph-header { display: flex; justify-content: space-between; align-items: baseline; }
      .pm-graph-title { font-size: 11px; font-weight: 800; letter-spacing: 0.6px; color: #e2e8f0; }
      .pm-graph-days { font-size: 10px; font-weight: 600; letter-spacing: 0.6px; color: #9ca3af; }
      .pm-graph-svg-slot { margin-top: 4px; }
      .pm-graph-svg-slot svg { display: block; width: 100%; height: 90px; }
      .pm-graph-footer { display: flex; justify-content: space-between; font-size: 9.5px; font-weight: 600; letter-spacing: 0.3px; color: #9ca3af; padding-top: 4px; }
      .pm-graph-empty { font-size: 11px; color: #9ca3af; text-align: center; padding: 24px 0; }

      .pm-care { padding: 4px 14px 14px; }
      .pm-care-summary { cursor: pointer; font-size: 13px; font-weight: 700; color: var(--primary-text-color); padding: 8px 0; list-style: none; display: flex; align-items: center; gap: 6px; }
      .pm-care-summary::-webkit-details-marker { display: none; }
      .pm-care-chevron { display: inline-block; font-size: 10px; transition: transform 0.15s ease; }
      details[open] .pm-care-chevron { transform: rotate(90deg); }
      details[open] .pm-care-summary { margin-bottom: 2px; }
      .pm-care-body { padding-top: 6px; font-size: 13px; line-height: 1.6; color: var(--primary-text-color); }
      .pm-care-body p { margin: 0 0 12px; }
      .pm-care-body em { display: block; margin-top: 4px; color: var(--secondary-text-color); }

      .pm-hero-content { cursor: pointer; }
      .pm-tooltip {
        position: absolute; pointer-events: none; background: rgba(11,18,32,0.95); color: #f1f5f9;
        border: 1px solid rgba(255,255,255,0.15); border-radius: 6px; padding: 4px 8px;
        font-size: 10.5px; white-space: nowrap; transform: translate(-50%, -110%); display: none; z-index: 2;
      }
      .pm-graph-svg-slot { position: relative; margin-top: 4px; }
    `;
  }

  _renderHero() {
    const hero = this.querySelector(".pm-hero");
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
    let statusColor = "#94a3b8";
    let statusIcon = "mdi:help-circle";
    if (soilVal !== null) {
      if (dry && dry.state === "on") { statusText = "Droog"; statusColor = "#ef4444"; statusIcon = "mdi:water-alert"; }
      else if (overwatered && overwatered.state === "on") { statusText = "Te nat"; statusColor = "#38bdf8"; statusIcon = "mdi:water"; }
      else { statusText = "Gezond"; statusColor = "#22c55e"; statusIcon = "mdi:check-circle"; }
    }
    hero.style.setProperty("--pm-status-color", statusColor);
    this.querySelector(".pm-status-text").textContent = statusText;
    this.querySelector(".pm-status-icon").setAttribute("icon", statusIcon);

    const photoUrl = photo && photo.attributes && photo.attributes.entity_picture;
    hero.style.backgroundImage = photoUrl ? `url(${photoUrl})` : "none";

    this.querySelector(".pm-hero-moisture").textContent = soilVal !== null ? `${soilVal}%` : "\u2014";
    this.querySelector(".pm-hero-temp").textContent = tempEntity ? `${parseFloat(tempEntity.state).toFixed(1)}\u00b0C` : "\u2014";

    const L = Math.max(0, Math.min(100, dryVal));
    const H = Math.max(L, Math.min(100, wetVal));
    const v = soilVal !== null ? Math.max(0, Math.min(100, soilVal)) : 0;
    this.querySelector(".pm-bar").style.background =
      `linear-gradient(90deg, #ef4444 0%, #ef4444 ${L}%, #22c55e ${L}%, #22c55e ${H}%, #38bdf8 ${H}%, #38bdf8 100%)`;
    this.querySelector(".pm-bar-marker").style.left = `${v}%`;
    this.querySelector(".pm-bar-dry").textContent = `droog <${L}%`;
    this.querySelector(".pm-bar-wet").textContent = `nat >${H}%`;

    const battVal = battery ? parseFloat(battery.state) : null;
    const battIcon = battVal === null ? "mdi:battery-unknown" : battVal < 20 ? "mdi:battery-alert" : "mdi:battery";
    const battColor = battVal === null ? "#94a3b8" : battVal < 20 ? "#ef4444" : battVal < 50 ? "#f59e0b" : "#a3e635";

    this.querySelector(".pm-tiles").innerHTML = [
      this._tile("mdi:water-percent", "#38bdf8", humidity ? `${humidity.state}%` : "\u2014", "Lucht"),
      this._tile(battIcon, battColor, battVal !== null ? `${battVal}%` : "\u2014", "Batterij"),
      this._tile("mdi:thermometer", "#f472b6", tempEntity ? `${parseFloat(tempEntity.state).toFixed(1)}\u00b0` : "\u2014", "Temp"),
    ].join("");

    this.querySelector(".pm-water-need").textContent = prediction ? prediction.state : "Onbekend";
    this.querySelector(".pm-advice").textContent = advice ? advice.state : "";
  }

  _tile(icon, color, value, label) {
    return `
      <div class="pm-tile">
        <ha-icon icon="${icon}" style="color:${color};"></ha-icon>
        <div class="pm-tile-value">${this._escape(value)}</div>
        <div class="pm-tile-label">${this._escape(label)}</div>
      </div>`;
  }

  _renderGraph() {
    const slot = this.querySelector(".pm-graph-svg-inner");
    if (!slot) return;

    const dryTh = this._entity("dry_threshold");
    const wetTh = this._entity("wet_threshold");
    const dryVal = dryTh ? parseFloat(dryTh.state) : 20;
    const wetVal = wetTh ? parseFloat(wetTh.state) : 70;
    this.querySelector(".pm-graph-optimal").textContent =
      `GRIJS = OPTIMAAL ${dryVal}-${wetVal}%`;

    const points = this._historyPoints;
    this._renderedGraphPoints = null;
    if (!points || points.length < 2) {
      slot.innerHTML = `<div class="pm-graph-empty">Nog niet genoeg geschiedenis (${HISTORY_DAYS} dagen nodig)</div>`;
      return;
    }

    const width = 600;
    const height = 90;
    const toY = (v) => height - (Math.max(0, Math.min(100, v)) / 100) * height;
    const minT = points[0].t;
    const maxT = points[points.length - 1].t;
    const span = Math.max(1, maxT - minT);
    const toX = (t) => ((t - minT) / span) * width;

    const bandTop = toY(wetVal);
    const bandBottom = toY(dryVal);
    const xy = points.map((p) => [toX(p.t), toY(p.v)]);
    const path = this._smoothPath(xy);

    slot.innerHTML = `
      <svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none">
        <rect x="0" y="${bandTop.toFixed(1)}" width="${width}" height="${(bandBottom - bandTop).toFixed(1)}"
          fill="#94a3b8" opacity="0.15" />
        <path d="${path}" fill="none" stroke="#f97316" stroke-width="1.5" />
        <line class="pm-hover-line" x1="0" y1="0" x2="0" y2="${height}" stroke="#f1f5f9" stroke-width="1" opacity="0" />
        <circle class="pm-hover-dot" cx="0" cy="0" r="3.5" fill="#f97316" stroke="#fff" stroke-width="1.5" opacity="0" />
        <circle cx="${xy[xy.length - 1][0].toFixed(1)}" cy="${xy[xy.length - 1][1].toFixed(1)}" r="3" fill="#ef4444" stroke="#fff" stroke-width="1" />
      </svg>`;

    // Stored for hover hit-testing: SVG-space coordinates + the original
    // point (timestamp + value) + the SVG's own viewBox width, since the
    // hover handler needs to convert real mouse-pixel X back to this
    // coordinate space (the SVG scales to the container's actual width).
    this._renderedGraphPoints = { xy, points, viewBoxWidth: width };
  }

  _handleGraphHover(ev) {
    const data = this._renderedGraphPoints;
    const svg = this.querySelector(".pm-graph-svg-inner svg");
    if (!data || !svg) {
      this._hideGraphTooltip();
      return;
    }
    const rect = svg.getBoundingClientRect();
    if (rect.width === 0) return;
    const relativeX = ev.clientX - rect.left;
    const svgX = (relativeX / rect.width) * data.viewBoxWidth;

    // Nearest point by X distance in SVG space.
    let nearestIdx = 0;
    let nearestDist = Infinity;
    data.xy.forEach(([x], i) => {
      const dist = Math.abs(x - svgX);
      if (dist < nearestDist) {
        nearestDist = dist;
        nearestIdx = i;
      }
    });

    const [px, py] = data.xy[nearestIdx];
    const point = data.points[nearestIdx];

    const hoverLine = svg.querySelector(".pm-hover-line");
    const hoverDot = svg.querySelector(".pm-hover-dot");
    if (hoverLine) {
      hoverLine.setAttribute("x1", px.toFixed(1));
      hoverLine.setAttribute("x2", px.toFixed(1));
      hoverLine.setAttribute("opacity", "0.4");
    }
    if (hoverDot) {
      hoverDot.setAttribute("cx", px.toFixed(1));
      hoverDot.setAttribute("cy", py.toFixed(1));
      hoverDot.setAttribute("opacity", "1");
    }

    const tooltip = this.querySelector(".pm-tooltip");
    if (tooltip) {
      const date = new Date(point.t);
      const dateLabel = date.toLocaleDateString("nl-NL", { day: "numeric", month: "short" });
      const timeLabel = date.toLocaleTimeString("nl-NL", { hour: "2-digit", minute: "2-digit" });
      tooltip.textContent = `${dateLabel} ${timeLabel} \u2014 ${point.v}%`;
      tooltip.style.display = "block";
      tooltip.style.left = `${(px / data.viewBoxWidth) * 100}%`;
      tooltip.style.top = `${(py / 90) * 100}%`;
    }
  }

  _hideGraphTooltip() {
    const tooltip = this.querySelector(".pm-tooltip");
    if (tooltip) tooltip.style.display = "none";
    const svg = this.querySelector(".pm-graph-svg-inner svg");
    if (svg) {
      const hoverLine = svg.querySelector(".pm-hover-line");
      const hoverDot = svg.querySelector(".pm-hover-dot");
      if (hoverLine) hoverLine.setAttribute("opacity", "0");
      if (hoverDot) hoverDot.setAttribute("opacity", "0");
    }
  }

  // Simple, dependency-free curve smoothing (quadratic bezier through
  // midpoints) so the line reads like the reference design's smoothed
  // apexcharts line rather than a jagged polyline.
  _smoothPath(points) {
    if (points.length < 3) {
      return points.map((p, i) => `${i === 0 ? "M" : "L"}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ");
    }
    let d = `M${points[0][0].toFixed(1)},${points[0][1].toFixed(1)}`;
    for (let i = 1; i < points.length - 1; i++) {
      const mx = (points[i][0] + points[i + 1][0]) / 2;
      const my = (points[i][1] + points[i + 1][1]) / 2;
      d += ` Q${points[i][0].toFixed(1)},${points[i][1].toFixed(1)} ${mx.toFixed(1)},${my.toFixed(1)}`;
    }
    const last = points[points.length - 1];
    d += ` L${last[0].toFixed(1)},${last[1].toFixed(1)}`;
    return d;
  }

  _renderCareGuide() {
    const careTip = this._entity("care_tip");
    const summaryText = this.querySelector(".pm-care-summary-text");
    const body = this.querySelector(".pm-care-body");
    const { model } = this._deviceTitleAndModel();

    summaryText.innerHTML = `\ud83c\udf3f Verzorgingstips \u2014 ${this._escape(model || "")}`;

    // The sensor's *state* is capped at 255 characters by Home Assistant
    // itself - the full multi-section text lives in the full_text
    // attribute instead (falls back to .state for older integration
    // versions or a custom entities: override pointing at something else).
    const fullText = careTip && careTip.attributes && careTip.attributes.full_text
      ? careTip.attributes.full_text
      : careTip && careTip.state;

    if (!fullText) {
      body.innerHTML = `<p>Geen verzorgingstip ingesteld.</p>`;
      return;
    }

    // "Label: text" lines, one section per line - see species_data.json /
    // the config flow's care step. Giftigheid (toxicity) is shown as an
    // italic footnote, matching the reference design, instead of a
    // labelled paragraph like the others.
    const lines = String(fullText).split("\n").filter(Boolean);
    const paragraphs = [];
    let toxicityLine = "";
    for (const line of lines) {
      const idx = line.indexOf(":");
      if (idx === -1) {
        paragraphs.push(`<p>${this._escape(line)}</p>`);
        continue;
      }
      const label = line.slice(0, idx).trim();
      const text = line.slice(idx + 1).trim();
      if (label.toLowerCase() === "giftigheid" || label.toLowerCase() === "toxicity") {
        toxicityLine = `<em>${this._escape(text)}</em>`;
        continue;
      }
      paragraphs.push(`<p><b>${this._escape(label)}:</b> ${this._escape(text)}</p>`);
    }
    body.innerHTML = paragraphs.join("") + toxicityLine;
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
