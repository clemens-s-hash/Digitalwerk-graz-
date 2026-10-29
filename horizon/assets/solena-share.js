/**
 * Teilen-Schaltflaeche.
 *
 * Nutzt die Web-Share-API, wo der Browser sie anbietet (vor allem mobil),
 * und kopiert sonst den Link in die Zwischenablage. Scheitert beides,
 * bleibt die Schaltflaeche stumm statt einen Fehler zu zeigen.
 */
class SolenaShare extends HTMLElement {
  connectedCallback() {
    this.trigger = this.querySelector('[data-share-trigger]');
    this.label = this.querySelector('[data-share-label]');
    if (!this.trigger) return;

    this.originalLabel = this.label?.textContent ?? '';
    this.onClick = this.onClick.bind(this);
    this.trigger.addEventListener('click', this.onClick);
  }

  disconnectedCallback() {
    this.trigger?.removeEventListener('click', this.onClick);
    if (this.resetTimeout) clearTimeout(this.resetTimeout);
  }

  flashLabel() {
    if (!this.label) return;
    this.label.textContent = this.dataset.copiedLabel || this.originalLabel;
    if (this.resetTimeout) clearTimeout(this.resetTimeout);
    this.resetTimeout = setTimeout(() => {
      this.label.textContent = this.originalLabel;
    }, 2000);
  }

  async onClick() {
    const url = this.dataset.shareUrl || window.location.href;
    const title = this.dataset.shareTitle || document.title;

    if (navigator.share) {
      try {
        await navigator.share({ title, url });
        return;
      } catch (error) {
        // Abbruch durch den Nutzer ist kein Fehler; auf Kopieren ausweichen.
        if (error instanceof DOMException && error.name === 'AbortError') return;
      }
    }

    try {
      await navigator.clipboard.writeText(url);
      this.flashLabel();
    } catch (error) {
      // Ohne Zwischenablage-Rechte bleibt nichts zu tun.
    }
  }
}

if (!customElements.get('solena-share')) {
  customElements.define('solena-share', SolenaShare);
}
