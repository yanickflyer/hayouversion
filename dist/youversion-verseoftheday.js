var CARD_VERSION = "1.0.0";

class YouVersionVerseOfTheDay extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.config = {
      entity: "sensor.youversion_verse_of_the_day",
      name: "Verse of the Day",
    };
  }

  setConfig(config) {
    if (!config) {
      throw new Error("You must provide a configuration for the card.");
    }

    this.config = {
      entity: config.entity || "sensor.youversion_verse_of_the_day",
      name: config.name || "Verse of the Day",
    };
  }

  set hass(hass) {
    this._hass = hass;
    this.render();
  }

  getCardSize() {
    return 1;
  }

  render() {
    if (!this._hass) {
      return;
    }

    const stateObj = this._hass.states[this.config.entity];
    const reference = stateObj?.state || "Unknown reference";
    const passage = stateObj?.attributes?.passage || "No verse available.";
    const missingSensor = !stateObj;

    this.shadowRoot.innerHTML = `
      <style>
        .verse-card {
          font-family: sans-serif;
          padding: 16px;
          border-radius: 12px;
          border: 1px solid var(--divider-color, #e0e0e0);
          background: var(--card-background-color, #ffffff);
          color: var(--primary-text-color, #222);
          box-shadow: var(--ha-card-box-shadow, none);
        }
        .verse-title {
          font-weight: 600;
          margin-bottom: 12px;
          font-size: 1.05em;
        }
        .verse-text {
          font-size: 1.1em;
          line-height: 1.5;
          margin-bottom: 10px;
          min-height: 3.5em;
        }
        .verse-reference {
          font-size: 0.9em;
          color: var(--secondary-text-color, #666);
        }
        .error {
          color: var(--error-color, #d32f2f);
          font-size: 0.95em;
        }
      </style>
      <div class="verse-card">
        <div class="verse-title">${this._escapeHtml(this.config.name)}</div>
        ${missingSensor ? `
          <div class="error">Sensor ${this._escapeHtml(this.config.entity)} not found.</div>
        ` : `
          <div class="verse-text">${this._escapeHtml(passage)}</div>
          <div class="verse-reference">${this._escapeHtml(reference)}</div>
        `}
      </div>
    `;
  }

  _escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }
}

customElements.define("youversion-verseoftheday", YouVersionVerseOfTheDay);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "custom:youversion-verseoftheday",
  name: "YouVersion Verse of the Day",
  description: "Displays the YouVersion Verse of the Day from a Home Assistant sensor",
  preview: true,
});
