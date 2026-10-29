/**
 * Sendungsverfolgung ueber den 17TRACK-Widget-Dienst.
 *
 * Shrine band das Widget mit einem globalen `onclick="doTrack()"` und einem
 * Skript-Tag direkt in der Section ein. Hier uebernimmt ein Custom Element
 * dieselbe Aufgabe: es laedt externalcall.js erst beim ersten Klick, meldet
 * Fehler im Markup statt per alert() und laesst sich mehrfach auf einer
 * Seite verwenden, weil die Container-ID aus der Block-ID kommt.
 *
 * Die aufgerufene API (window.YQV5.trackSingle) ist die oeffentliche
 * Schnittstelle von 17TRACK, kein Theme-Code.
 */
const SCRIPT_SRC = 'https://www.17track.net/externalcall.js';

let scriptPromise = null;

function loadTrackingScript() {
  if (window.YQV5 && typeof window.YQV5.trackSingle === 'function') {
    return Promise.resolve();
  }

  if (!scriptPromise) {
    scriptPromise = new Promise((resolve, reject) => {
      const existing = document.querySelector(`script[src="${SCRIPT_SRC}"]`);
      const script = existing || document.createElement('script');

      script.addEventListener('load', () => resolve(), { once: true });
      script.addEventListener(
        'error',
        () => {
          // Ein fehlgeschlagener Ladevorgang darf den naechsten Versuch nicht
          // blockieren, sonst bleibt das Formular nach einem Netzaussetzer tot.
          scriptPromise = null;
          reject(new Error('17TRACK konnte nicht geladen werden.'));
        },
        { once: true }
      );

      if (!existing) {
        script.src = SCRIPT_SRC;
        script.async = true;
        document.head.appendChild(script);
      }
    });
  }

  return scriptPromise;
}

class SolenaTrackOrder extends HTMLElement {
  connectedCallback() {
    this.input = this.querySelector('[data-track-input]');
    this.button = this.querySelector('[data-track-submit]');
    this.result = this.querySelector('[data-track-result]');
    this.error = this.querySelector('[data-track-error]');

    if (!this.input || !this.button || !this.result) return;

    this.onSubmit = this.onSubmit.bind(this);
    this.button.addEventListener('click', this.onSubmit);
    this.input.addEventListener('keydown', (event) => {
      if (event.key === 'Enter') {
        event.preventDefault();
        this.onSubmit();
      }
    });
  }

  disconnectedCallback() {
    this.button?.removeEventListener('click', this.onSubmit);
  }

  showError(message) {
    if (!this.error) return;
    this.error.textContent = message;
    this.error.hidden = false;
  }

  clearError() {
    if (!this.error) return;
    this.error.hidden = true;
    this.error.textContent = '';
  }

  async onSubmit() {
    const number = this.input.value.trim();

    this.clearError();

    if (!number) {
      this.showError(this.dataset.emptyMessage || '');
      this.input.focus();
      return;
    }

    this.button.setAttribute('aria-busy', 'true');

    try {
      await loadTrackingScript();

      window.YQV5.trackSingle({
        YQ_ContainerId: this.result.id,
        YQ_Height: Number(this.dataset.height) || 560,
        YQ_Fc: '0',
        YQ_Lang: this.dataset.lang || 'de',
        YQ_Num: number,
      });
    } catch (error) {
      this.showError(this.dataset.errorMessage || '');
    } finally {
      this.button.removeAttribute('aria-busy');
    }
  }
}

if (!customElements.get('solena-track-order')) {
  customElements.define('solena-track-order', SolenaTrackOrder);
}
