/**
 * Sticky Add-to-Cart-Leiste.
 *
 * Shrine zeigte unten eine Leiste mit Preis, Rabatt-Badge und einem Button
 * „Zum Warenkorb", sobald die eigentlichen Kaufen-Schaltflaechen aus dem
 * Bild gescrollt waren.
 *
 * Diese Leiste bedient keinen eigenen Warenkorb-Aufruf. Sie klickt den
 * echten Add-to-Cart-Button des Produktformulars, damit Horizons
 * Variantenlogik, Mengenregeln, Fehlermeldungen und Cart-Drawer
 * unveraendert greifen. `dataset.puppet` ist die Markierung, die Horizon
 * selbst fuer fremdgesteuerte Klicks benutzt.
 */
class SolenaStickyAtc extends HTMLElement {
  connectedCallback() {
    this.bar = this.querySelector('[data-sticky-bar]');
    this.button = this.querySelector('[data-sticky-submit]');
    if (!this.bar || !this.button) return;

    this.onClick = this.onClick.bind(this);
    this.button.addEventListener('click', this.onClick);

    if (this.dataset.displayWhen === 'always') {
      this.setVisible(true);
      return;
    }

    this.watchBuyButtons();
  }

  disconnectedCallback() {
    this.button?.removeEventListener('click', this.onClick);
    this.observer?.disconnect();
  }

  /** Das Produktformular dieser Seite, ohne die Leiste selbst. */
  get productForm() {
    return document.querySelector('product-form-component');
  }

  get targetButton() {
    return this.productForm?.querySelector('[ref="addToCartButton"]') ?? null;
  }

  setVisible(visible) {
    this.bar.dataset.visible = visible ? 'true' : 'false';
    this.bar.setAttribute('aria-hidden', visible ? 'false' : 'true');
  }

  watchBuyButtons() {
    const anchor = this.productForm;

    if (!anchor || typeof IntersectionObserver === 'undefined') {
      // Ohne Beobachter waere die Leiste nie erreichbar, also dauerhaft zeigen.
      this.setVisible(true);
      return;
    }

    this.observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          // Nur zeigen, wenn die Schaltflaechen nach OBEN aus dem Bild sind.
          // Beim ersten Laden liegen sie darunter; dort soll nichts erscheinen.
          const scrolledPast = !entry.isIntersecting && entry.boundingClientRect.top < 0;
          this.setVisible(scrolledPast);
        }
      },
      { threshold: 0 }
    );

    this.observer.observe(anchor);
    this.setVisible(false);
  }

  onClick() {
    const target = this.targetButton;
    if (!target || target.disabled) return;

    target.dataset.puppet = 'true';
    target.click();
  }
}

if (!customElements.get('solena-sticky-atc')) {
  customElements.define('solena-sticky-atc', SolenaStickyAtc);
}
