/**
 * Greenwich Foot Tunnel Lift Status — custom Lovelace card.
 *
 * Renders a responsive tile with the two foot-tunnel rotundas side-by-side.
 * State comes from two binary_sensor entities; every state-dependent colour
 * flows through CSS variables so swapping between "working" and "out of
 * service" is a one-line change per panel.
 *
 * No build step. Dropped into /config/custom_components/greenwich_tunnel/frontend/
 * by the integration and registered as an extra JS module at setup.
 */

const CARD_VERSION = "0.3.0";
const CARD_TYPE = "greenwich-tunnel-card";
const EDITOR_TYPE = "greenwich-tunnel-card-editor";

const DEFAULTS = {
  title: "Greenwich foot tunnel",
  subtitle: "Elevator status",
  footer: "370m under the Thames",
  north_label: "North",
  north_entrance: "Island Gardens",
  south_label: "South",
  south_entrance: "Cutty Sark",
  working_text: "Working",
  broken_text: "Out of service",
  stale_text: "Stale",
  // Show toggles: untick to hide that element from every panel.
  show_rotunda: true,
  show_pill: true,
  show_icon: true,
  font_scale: 1,
  // Spacing overrides: undefined = let the responsive clamp() default take over.
  card_padding: undefined,
  panel_gap: undefined,
  panel_padding: undefined,
  // Per-stack spacing inside each panel (rotunda → title → subtitle → pill → icon).
  gap_rotunda_title: undefined,
  gap_title_subtitle: undefined,
  gap_subtitle_pill: undefined,
  gap_pill_icon: undefined,
  // Per-element font-size overrides (absolute px). Undefined = responsive clamp default.
  title_size: undefined,
  subtitle_size: undefined,
  panel_label_size: undefined,
  panel_entrance_size: undefined,
  pill_size: undefined,
  footer_size: undefined,
};

const COLOURS = {
  working: {
    "--rc-dot": "#27500A",
    "--rc-dark": "#3B6D11",
    "--rc-dome-light": "#C0DD97",
    "--rc-dome-med": "#97C459",
    "--rc-wall-light": "#EAF3DE",
    "--rc-accent": "#639922",
    "--rc-icon": "#27500A",
    "--pill-bg": "#C0DD97",
    "--pill-dot": "#27500A",
    "--pill-text": "#173404",
  },
  broken: {
    "--rc-dot": "#A32D2D",
    "--rc-dark": "#A32D2D",
    "--rc-dome-light": "#F7C1C1",
    "--rc-dome-med": "#F09595",
    "--rc-wall-light": "#FCEBEB",
    "--rc-accent": "#E24B4A",
    "--rc-icon": "#791F1F",
    "--pill-bg": "#F7C1C1",
    "--pill-dot": "#A32D2D",
    "--pill-text": "#501313",
  },
  // Pill-only overlay: applied on top of the last-known working/broken theme so
  // the rotunda still reflects the most recent reading but the pill signals
  // that the data is older than the staleness threshold.
  stalePill: {
    "--pill-bg": "#FDE68A",
    "--pill-dot": "#A16207",
    "--pill-text": "#78350F",
  },
};

const ROTUNDA_SVG = `
<svg class="rotunda" viewBox="-80 -108 160 160" preserveAspectRatio="xMidYMid meet">
  <!-- spire -->
  <circle cx="0" cy="-100" r="3" fill="var(--rc-dot)"/>
  <line x1="0" y1="-97" x2="0" y2="-90" stroke="var(--rc-dot)" stroke-width="2" stroke-linecap="round"/>
  <path d="M-10,-78 A10,12 0 0,1 10,-78 Z" fill="var(--rc-dome-med)" stroke="var(--rc-dark)" stroke-width="0.8"/>
  <rect x="-10" y="-78" width="20" height="10" rx="1" fill="var(--rc-dome-light)" stroke="var(--rc-dark)" stroke-width="0.8"/>
  <line x1="-4" y1="-77" x2="-4" y2="-69" stroke="var(--rc-dark)" stroke-width="0.5"/>
  <line x1="4" y1="-77" x2="4" y2="-69" stroke="var(--rc-dark)" stroke-width="0.5"/>
  <rect x="-13" y="-68" width="26" height="3" rx="1" fill="var(--rc-accent)"/>
  <!-- dome -->
  <path d="M-65,-8 A65,58 0 0,1 65,-8 Z" fill="var(--rc-dome-light)" stroke="var(--rc-dark)" stroke-width="1"/>
  <path d="M-52,-8 Q-46,-48 0,-64 Q46,-48 52,-8" fill="none" stroke="var(--rc-dark)" stroke-width="0.7"/>
  <path d="M-35,-8 Q-30,-52 0,-64 Q30,-52 35,-8" fill="none" stroke="var(--rc-dark)" stroke-width="0.7"/>
  <path d="M-16,-8 Q-12,-56 0,-64 Q12,-56 16,-8" fill="none" stroke="var(--rc-dark)" stroke-width="0.7"/>
  <path d="M-63,-16 Q0,-30 63,-16" fill="none" stroke="var(--rc-dark)" stroke-width="0.5"/>
  <path d="M-57,-28 Q0,-42 57,-28" fill="none" stroke="var(--rc-dark)" stroke-width="0.5"/>
  <path d="M-46,-40 Q0,-52 46,-40" fill="none" stroke="var(--rc-dark)" stroke-width="0.5"/>
  <path d="M-30,-52 Q0,-60 30,-52" fill="none" stroke="var(--rc-dark)" stroke-width="0.5"/>
  <!-- plinth -->
  <rect x="-68" y="-10" width="136" height="6" rx="2" fill="var(--rc-accent)" stroke="var(--rc-dark)" stroke-width="0.6"/>
  <!-- wall + brick pattern -->
  <rect x="-66" y="-4" width="132" height="44" rx="3" fill="var(--rc-wall-light)" stroke="var(--rc-dark)" stroke-width="0.8"/>
  <line x1="-64" y1="7" x2="64" y2="7" stroke="var(--rc-dome-med)" stroke-width="0.6"/>
  <line x1="-64" y1="18" x2="64" y2="18" stroke="var(--rc-dome-med)" stroke-width="0.6"/>
  <line x1="-64" y1="29" x2="64" y2="29" stroke="var(--rc-dome-med)" stroke-width="0.6"/>
  <line x1="-44" y1="-4" x2="-44" y2="7" stroke="var(--rc-dome-med)" stroke-width="0.4"/>
  <line x1="-22" y1="-4" x2="-22" y2="7" stroke="var(--rc-dome-med)" stroke-width="0.4"/>
  <line x1="0" y1="-4" x2="0" y2="7" stroke="var(--rc-dome-med)" stroke-width="0.4"/>
  <line x1="22" y1="-4" x2="22" y2="7" stroke="var(--rc-dome-med)" stroke-width="0.4"/>
  <line x1="44" y1="-4" x2="44" y2="7" stroke="var(--rc-dome-med)" stroke-width="0.4"/>
  <line x1="-55" y1="7" x2="-55" y2="18" stroke="var(--rc-dome-med)" stroke-width="0.4"/>
  <line x1="-33" y1="7" x2="-33" y2="18" stroke="var(--rc-dome-med)" stroke-width="0.4"/>
  <line x1="-11" y1="7" x2="-11" y2="18" stroke="var(--rc-dome-med)" stroke-width="0.4"/>
  <line x1="11" y1="7" x2="11" y2="18" stroke="var(--rc-dome-med)" stroke-width="0.4"/>
  <line x1="33" y1="7" x2="33" y2="18" stroke="var(--rc-dome-med)" stroke-width="0.4"/>
  <line x1="55" y1="7" x2="55" y2="18" stroke="var(--rc-dome-med)" stroke-width="0.4"/>
  <line x1="-44" y1="18" x2="-44" y2="29" stroke="var(--rc-dome-med)" stroke-width="0.4"/>
  <line x1="-22" y1="18" x2="-22" y2="29" stroke="var(--rc-dome-med)" stroke-width="0.4"/>
  <line x1="0" y1="18" x2="0" y2="29" stroke="var(--rc-dome-med)" stroke-width="0.4"/>
  <line x1="22" y1="18" x2="22" y2="29" stroke="var(--rc-dome-med)" stroke-width="0.4"/>
  <line x1="44" y1="18" x2="44" y2="29" stroke="var(--rc-dome-med)" stroke-width="0.4"/>
  <line x1="-55" y1="29" x2="-55" y2="40" stroke="var(--rc-dome-med)" stroke-width="0.4"/>
  <line x1="-33" y1="29" x2="-33" y2="40" stroke="var(--rc-dome-med)" stroke-width="0.4"/>
  <line x1="-11" y1="29" x2="-11" y2="40" stroke="var(--rc-dome-med)" stroke-width="0.4"/>
  <line x1="11" y1="29" x2="11" y2="40" stroke="var(--rc-dome-med)" stroke-width="0.4"/>
  <line x1="33" y1="29" x2="33" y2="40" stroke="var(--rc-dome-med)" stroke-width="0.4"/>
  <line x1="55" y1="29" x2="55" y2="40" stroke="var(--rc-dome-med)" stroke-width="0.4"/>
  <!-- doorway -->
  <rect x="-22" y="12" width="44" height="30" rx="1" fill="var(--rc-dark)"/>
  <rect x="-24" y="10" width="48" height="4" rx="1" fill="var(--rc-accent)" stroke="var(--rc-dark)" stroke-width="0.5"/>
  <rect x="-19" y="16" width="17" height="26" rx="1" fill="var(--panel-bg)"/>
  <rect x="2" y="16" width="17" height="26" rx="1" fill="var(--panel-bg)"/>
  <line x1="0" y1="14" x2="0" y2="42" stroke="var(--rc-dark)" stroke-width="1.5"/>
  <rect x="-16" y="2" width="32" height="6" rx="1" fill="var(--rc-accent)" stroke="var(--rc-dark)" stroke-width="0.4"/>
  <!-- floor -->
  <rect x="-70" y="40" width="140" height="5" rx="1.5" fill="var(--rc-accent)" stroke="var(--rc-dark)" stroke-width="0.6"/>
  <rect x="-72" y="45" width="144" height="4" rx="1" fill="var(--rc-dark)"/>
</svg>`;

const ELEVATOR_WORKING_SVG = `
<svg class="elevator" viewBox="0 0 50 26" preserveAspectRatio="xMidYMid meet">
  <rect x="0" y="0" width="50" height="26" rx="5" fill="var(--rc-wall-light)" stroke="var(--rc-dark)" stroke-width="0.6"/>
  <path d="M25 20L25 8" stroke="var(--rc-icon)" stroke-width="1.5" fill="none" stroke-linecap="round"/>
  <path d="M21 13L25 7L29 13" stroke="var(--rc-icon)" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
</svg>`;

const ELEVATOR_BROKEN_SVG = `
<svg class="elevator" viewBox="0 0 50 26" preserveAspectRatio="xMidYMid meet">
  <rect x="0" y="0" width="50" height="26" rx="5" fill="var(--rc-wall-light)" stroke="var(--rc-dark)" stroke-width="0.6"/>
  <line x1="19" y1="7" x2="31" y2="19" stroke="var(--rc-icon)" stroke-width="1.8" stroke-linecap="round"/>
  <line x1="31" y1="7" x2="19" y2="19" stroke="var(--rc-icon)" stroke-width="1.8" stroke-linecap="round"/>
</svg>`;

const STYLE = `
:host {
  display: block;
  container-type: inline-size;
}
ha-card {
  padding: var(--gtl-card-padding, clamp(12px, 3cqi, 24px));
  background: var(--ha-card-background, var(--card-background-color, #262624));
  color: var(--primary-text-color, #FAF9F5);
  --panel-bg: var(--ha-card-background, var(--card-background-color, #262624));
  --panel-border: rgba(222, 220, 209, 0.3);
}
.header {
  text-align: center;
  margin-bottom: clamp(8px, 2cqi, 16px);
}
.title {
  font-size: var(--gtl-title-size, calc(clamp(16px, 4cqi, 28px) * var(--font-scale, 1)));
  font-weight: 600;
  letter-spacing: 0.01em;
}
.subtitle {
  font-size: var(--gtl-subtitle-size, calc(clamp(12px, 3cqi, 20px) * var(--font-scale, 1)));
  font-weight: 400;
  color: var(--secondary-text-color, #C2C0B6);
  margin-top: 2px;
}
.panels {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--gtl-panel-gap, clamp(8px, 2cqi, 16px));
}
.panel {
  padding: var(--gtl-panel-padding, clamp(10px, 2.5cqi, 20px));
  border: 0.5px solid var(--panel-border);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.panel > * + * {
  margin-top: 0;
}
.rotunda {
  width: 100%;
  max-width: 220px;
  height: auto;
  aspect-ratio: 1 / 1;
}
.panel-label {
  font-size: var(--gtl-panel-label-size, calc(clamp(14px, 3.5cqi, 22px) * var(--font-scale, 1)));
  font-weight: 600;
  margin-top: var(--gtl-gap-rotunda-title, clamp(4px, 1.2cqi, 10px));
}
.panel-entrance {
  font-size: var(--gtl-panel-entrance-size, calc(clamp(11px, 2.6cqi, 16px) * var(--font-scale, 1)));
  color: var(--secondary-text-color, #C2C0B6);
  margin-top: var(--gtl-gap-title-subtitle, clamp(2px, 0.6cqi, 5px));
}
.pill {
  display: inline-flex;
  align-items: center;
  gap: clamp(4px, 1.2cqi, 10px);
  padding: clamp(6px, 1.2cqi, 12px) clamp(14px, 3cqi, 26px);
  border-radius: 999px;
  background: var(--pill-bg);
  color: var(--pill-text);
  font-size: var(--gtl-pill-size, calc(clamp(12px, 3cqi, 18px) * var(--font-scale, 1)));
  font-weight: 600;
  margin-top: var(--gtl-gap-subtitle-pill, clamp(4px, 1.2cqi, 10px));
}
.pill::before {
  content: "";
  width: clamp(6px, 1.5cqi, 10px);
  height: clamp(6px, 1.5cqi, 10px);
  border-radius: 50%;
  background: var(--pill-dot);
}
.elevator {
  width: clamp(30px, 10cqi, 56px);
  height: auto;
  aspect-ratio: 50 / 26;
  margin-top: var(--gtl-gap-pill-icon, clamp(4px, 1cqi, 8px));
}
.footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: clamp(6px, 1.5cqi, 12px);
  margin-top: clamp(8px, 2cqi, 16px);
  font-size: var(--gtl-footer-size, calc(clamp(10px, 2.4cqi, 14px) * var(--font-scale, 1)));
  color: var(--secondary-text-color, #C2C0B6);
}
.footer::before, .footer::after {
  content: "";
  flex: 1;
  border-top: 1px dashed var(--secondary-text-color, #C2C0B6);
  opacity: 0.5;
  max-width: 30%;
}
.unknown {
  --pill-bg: color-mix(in srgb, var(--secondary-text-color, #C2C0B6) 25%, transparent);
  --pill-dot: var(--secondary-text-color, #C2C0B6);
  --pill-text: var(--primary-text-color, #FAF9F5);
}
`;

/**
 * Return the CSS variable block for a panel. Base theme comes from the last-known
 * state ("working" | "broken"); the stale overlay then swaps only the pill vars.
 */
function cssVarsFor(state, { stale = false } = {}) {
  const base = state === "on" ? COLOURS.working : COLOURS.broken;
  const theme = stale ? { ...base, ...COLOURS.stalePill } : base;
  return Object.entries(theme)
    .map(([k, v]) => `${k}: ${v};`)
    .join(" ");
}

class GreenwichTunnelCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = null;
    this._hass = null;
  }

  setConfig(config) {
    if (!config || !config.north_entity || !config.south_entity) {
      throw new Error("north_entity and south_entity are required");
    }
    this._config = { ...DEFAULTS, ...config };
    this._render();
  }

  set hass(hass) {
    const northId = this._config && this._config.north_entity;
    const southId = this._config && this._config.south_entity;
    const prev = this._panelKey(northId) + "|" + this._panelKey(southId);
    this._hass = hass;
    const next = this._panelKey(northId) + "|" + this._panelKey(southId);
    if (!this.shadowRoot.firstChild || prev !== next) {
      this._render();
    }
  }

  _state(entityId) {
    if (!this._hass || !entityId) return null;
    const s = this._hass.states[entityId];
    return s ? s.state : null;
  }

  _isStale(entityId) {
    if (!this._hass || !entityId) return false;
    const s = this._hass.states[entityId];
    return !!(s && s.attributes && s.attributes.is_stale);
  }

  // Combined signature that triggers a re-render when state OR is_stale flips.
  _panelKey(entityId) {
    return `${this._state(entityId)}:${this._isStale(entityId) ? "1" : "0"}`;
  }

  _panelHtml(side) {
    const cfg = this._config;
    const entity = side === "north" ? cfg.north_entity : cfg.south_entity;
    const label = side === "north" ? cfg.north_label : cfg.south_label;
    const entrance = side === "north" ? cfg.north_entrance : cfg.south_entrance;
    const state = this._state(entity);
    const working = state === "on";
    const unknown = state === null || state === "unavailable" || state === "unknown";
    const stale = !unknown && this._isStale(entity);
    const vars = unknown ? "" : cssVarsFor(state, { stale });
    const classes = ["panel"];
    if (unknown) classes.push("unknown");
    const pillText = unknown
      ? "Unknown"
      : stale
        ? cfg.stale_text
        : working
          ? cfg.working_text
          : cfg.broken_text;
    const elevator = working ? ELEVATOR_WORKING_SVG : ELEVATOR_BROKEN_SVG;
    const parts = [];
    if (cfg.show_rotunda) parts.push(ROTUNDA_SVG);
    parts.push(`<div class="panel-label">${escapeHtml(label)}</div>`);
    parts.push(`<div class="panel-entrance">${escapeHtml(entrance)}</div>`);
    if (cfg.show_pill) parts.push(`<div class="pill">${escapeHtml(pillText)}</div>`);
    if (cfg.show_icon) parts.push(elevator);
    return `<div class="${classes.join(" ")}" style="${vars}">${parts.join("")}</div>`;
  }

  _render() {
    if (!this._config) return;
    const scale = Number(this._config.font_scale) || 1;
    const styleVars = [`--font-scale: ${scale};`];
    if (this._config.card_padding !== undefined && this._config.card_padding !== null) {
      styleVars.push(`--gtl-card-padding: ${this._config.card_padding}px;`);
    }
    if (this._config.panel_gap !== undefined && this._config.panel_gap !== null) {
      styleVars.push(`--gtl-panel-gap: ${this._config.panel_gap}px;`);
    }
    if (this._config.panel_padding !== undefined && this._config.panel_padding !== null) {
      styleVars.push(`--gtl-panel-padding: ${this._config.panel_padding}px;`);
    }
    const pxFields = {
      gap_rotunda_title: "--gtl-gap-rotunda-title",
      gap_title_subtitle: "--gtl-gap-title-subtitle",
      gap_subtitle_pill: "--gtl-gap-subtitle-pill",
      gap_pill_icon: "--gtl-gap-pill-icon",
      title_size: "--gtl-title-size",
      subtitle_size: "--gtl-subtitle-size",
      panel_label_size: "--gtl-panel-label-size",
      panel_entrance_size: "--gtl-panel-entrance-size",
      pill_size: "--gtl-pill-size",
      footer_size: "--gtl-footer-size",
    };
    for (const [field, cssVar] of Object.entries(pxFields)) {
      const v = this._config[field];
      if (v !== undefined && v !== null) styleVars.push(`${cssVar}: ${v}px;`);
    }
    this.shadowRoot.innerHTML = `
      <style>${STYLE}</style>
      <ha-card style="${styleVars.join(" ")}">
        <div class="header">
          <div class="title">${escapeHtml(this._config.title)}</div>
          <div class="subtitle">${escapeHtml(this._config.subtitle)}</div>
        </div>
        <div class="panels">
          ${this._panelHtml("north")}
          ${this._panelHtml("south")}
        </div>
        <div class="footer">${escapeHtml(this._config.footer)}</div>
      </ha-card>`;
  }

  getCardSize() {
    return 5;
  }

  static async getConfigElement() {
    if (!customElements.get(EDITOR_TYPE)) {
      customElements.define(EDITOR_TYPE, GreenwichTunnelCardEditor);
    }
    return document.createElement(EDITOR_TYPE);
  }

  static getStubConfig(hass) {
    const pickEntity = (suffix) => {
      const match = Object.keys(hass.states || {}).find((id) =>
        id.startsWith("binary_sensor.greenwich_foot_tunnel") && id.includes(suffix),
      );
      return match || `binary_sensor.greenwich_foot_tunnel_lifts_${suffix}`;
    };
    return {
      north_entity: pickEntity("north_lift_island_gardens"),
      south_entity: pickEntity("south_lift_cutty_sark"),
    };
  }
}

const EDITOR_SCHEMA = [
  {
    name: "north_entity",
    required: true,
    selector: { entity: { domain: "binary_sensor" } },
  },
  {
    name: "south_entity",
    required: true,
    selector: { entity: { domain: "binary_sensor" } },
  },
  { name: "title", selector: { text: {} } },
  { name: "subtitle", selector: { text: {} } },
  { name: "footer", selector: { text: {} } },
  {
    type: "grid",
    schema: [
      { name: "north_label", selector: { text: {} } },
      { name: "north_entrance", selector: { text: {} } },
    ],
  },
  {
    type: "grid",
    schema: [
      { name: "south_label", selector: { text: {} } },
      { name: "south_entrance", selector: { text: {} } },
    ],
  },
  {
    type: "grid",
    schema: [
      { name: "working_text", selector: { text: {} } },
      { name: "broken_text", selector: { text: {} } },
    ],
  },
  { name: "stale_text", selector: { text: {} } },
  {
    type: "grid",
    schema: [
      { name: "show_rotunda", selector: { boolean: {} } },
      { name: "show_pill", selector: { boolean: {} } },
      { name: "show_icon", selector: { boolean: {} } },
    ],
  },
  {
    name: "font_scale",
    selector: {
      number: { min: 0.5, max: 2.5, step: 0.1, mode: "slider" },
    },
  },
  {
    name: "card_padding",
    selector: {
      number: { min: 0, max: 40, step: 2, mode: "slider", unit_of_measurement: "px" },
    },
  },
  {
    name: "panel_gap",
    selector: {
      number: { min: 0, max: 40, step: 2, mode: "slider", unit_of_measurement: "px" },
    },
  },
  {
    name: "panel_padding",
    selector: {
      number: { min: 0, max: 40, step: 2, mode: "slider", unit_of_measurement: "px" },
    },
  },
  {
    name: "gap_rotunda_title",
    selector: {
      number: { min: 0, max: 40, step: 1, mode: "slider", unit_of_measurement: "px" },
    },
  },
  {
    name: "gap_title_subtitle",
    selector: {
      number: { min: 0, max: 40, step: 1, mode: "slider", unit_of_measurement: "px" },
    },
  },
  {
    name: "gap_subtitle_pill",
    selector: {
      number: { min: 0, max: 40, step: 1, mode: "slider", unit_of_measurement: "px" },
    },
  },
  {
    name: "gap_pill_icon",
    selector: {
      number: { min: 0, max: 40, step: 1, mode: "slider", unit_of_measurement: "px" },
    },
  },
  {
    name: "title_size",
    selector: {
      number: { min: 8, max: 48, step: 1, mode: "slider", unit_of_measurement: "px" },
    },
  },
  {
    name: "subtitle_size",
    selector: {
      number: { min: 8, max: 48, step: 1, mode: "slider", unit_of_measurement: "px" },
    },
  },
  {
    name: "panel_label_size",
    selector: {
      number: { min: 8, max: 48, step: 1, mode: "slider", unit_of_measurement: "px" },
    },
  },
  {
    name: "panel_entrance_size",
    selector: {
      number: { min: 8, max: 48, step: 1, mode: "slider", unit_of_measurement: "px" },
    },
  },
  {
    name: "pill_size",
    selector: {
      number: { min: 8, max: 48, step: 1, mode: "slider", unit_of_measurement: "px" },
    },
  },
  {
    name: "footer_size",
    selector: {
      number: { min: 8, max: 48, step: 1, mode: "slider", unit_of_measurement: "px" },
    },
  },
];

const EDITOR_LABELS = {
  north_entity: "North lift entity",
  south_entity: "South lift entity",
  title: "Title",
  subtitle: "Subtitle",
  footer: "Footer text",
  north_label: "North side label",
  north_entrance: "North entrance name",
  south_label: "South side label",
  south_entrance: "South entrance name",
  working_text: "Working pill text",
  broken_text: "Out-of-service pill text",
  stale_text: "Stale pill text",
  show_rotunda: "Show rotunda",
  show_pill: "Show pill",
  show_icon: "Show status icon",
  font_scale: "Font scale",
  card_padding: "Card padding",
  panel_gap: "Gap between panels",
  panel_padding: "Panel padding",
  gap_rotunda_title: "Spacing: rotunda \u2192 title",
  gap_title_subtitle: "Spacing: title \u2192 subtitle",
  gap_subtitle_pill: "Spacing: subtitle \u2192 pill",
  gap_pill_icon: "Spacing: pill \u2192 status icon",
  title_size: "Card title size",
  subtitle_size: "Card subtitle size",
  panel_label_size: "Panel title size (e.g. North)",
  panel_entrance_size: "Panel subtitle size (e.g. Island Gardens)",
  pill_size: "Pill text size",
  footer_size: "Footer text size",
};

class GreenwichTunnelCardEditor extends HTMLElement {
  constructor() {
    super();
    this._config = null;
    this._hass = null;
    this._form = null;
  }

  setConfig(config) {
    this._config = config || {};
    this._syncForm();
  }

  set hass(hass) {
    this._hass = hass;
    this._syncForm();
  }

  connectedCallback() {
    if (this._form) return;
    this._form = document.createElement("ha-form");
    this._form.computeLabel = (schema) => EDITOR_LABELS[schema.name] || schema.name;
    this._form.addEventListener("value-changed", (ev) => this._valueChanged(ev));
    this._syncForm();
    this.appendChild(this._form);
  }

  _syncForm() {
    if (!this._form) return;
    this._form.hass = this._hass;
    this._form.data = { ...DEFAULTS, ...(this._config || {}) };
    this._form.schema = EDITOR_SCHEMA;
  }

  _valueChanged(ev) {
    ev.stopPropagation();
    const value = ev.detail && ev.detail.value ? { ...ev.detail.value } : {};
    // Strip fields that equal the default so the saved YAML stays tidy.
    for (const [key, def] of Object.entries(DEFAULTS)) {
      if (def === undefined) continue;
      if (value[key] === def) delete value[key];
    }
    // Preserve the card type HA expects to see.
    value.type = `custom:${CARD_TYPE}`;
    const event = new Event("config-changed", { bubbles: true, composed: true });
    event.detail = { config: value };
    this.dispatchEvent(event);
  }
}

function escapeHtml(value) {
  if (value === null || value === undefined) return "";
  return String(value).replace(/[&<>"']/g, (ch) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[ch]));
}

if (!customElements.get(CARD_TYPE)) {
  customElements.define(CARD_TYPE, GreenwichTunnelCard);
}
if (!customElements.get(EDITOR_TYPE)) {
  customElements.define(EDITOR_TYPE, GreenwichTunnelCardEditor);
}

window.customCards = window.customCards || [];
if (!window.customCards.find((c) => c.type === CARD_TYPE)) {
  window.customCards.push({
    type: CARD_TYPE,
    name: "Greenwich Tunnel",
    description: "Live rotunda tile for the Greenwich Foot Tunnel lifts",
    preview: false,
    documentationURL: "https://github.com/hypercubian/ha-greenwichtunnel",
  });
}

// eslint-disable-next-line no-console
console.info(
  `%c GREENWICH-TUNNEL-CARD %c v${CARD_VERSION} `,
  "color: #FAF9F5; background: #0f766e; font-weight: 700;",
  "color: #0f766e; background: transparent;",
);
