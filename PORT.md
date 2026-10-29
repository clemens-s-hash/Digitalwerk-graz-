# PORT.md — Shrine⁺ 1.3.5 → Horizon 4.3.0

Portierung des Live-Themes **solenahome-redesign-clarity** (Shrine⁺ 1.3.5) auf
**Horizon 4.3.0**.

- Vorlage (nur gelesen): `theme_export__…solenahome-redesign-clarity__29OCT2026-0428pm`
- Ergebnis: `horizon/` in diesem Repo, als ZIP unter `dist/solena-horizon.zip`
- Regel: **kein Shrine-Code kopiert.** Shrine ist optische und funktionale
  Vorlage; umgesetzt mit Horizons eigenen Sections, Theme-Blocks und Snippets.

Stand: Etappen 1–7 abgeschlossen, Etappe 8 (Feinschliff) begonnen.

---

## Inhalt

1. [Status](#1-status)
2. [Drei Korrekturen zur Ausgangslage](#2-drei-korrekturen-zur-ausgangslage)
3. [Design-Tokens](#3-design-tokens)
4. [Was pro Template drin ist](#4-was-pro-template-drin-ist)
5. [Eigene Theme-Blocks](#5-eigene-theme-blocks)
6. [Änderungen an Horizons eigenen Dateien](#6-änderungen-an-horizons-eigenen-dateien)
7. [App-Blöcke — was du in Shopify einsetzen musst](#7-app-blöcke--was-du-in-shopify-einsetzen-musst)
8. [GemPages — was neu gebaut werden muss](#8-gempages--was-neu-gebaut-werden-muss)
9. [Qualitätssicherung](#9-qualitätssicherung)
10. [Bewusst offen geblieben](#10-bewusst-offen-geblieben)
11. [Deine Schritte in Shopify](#11-deine-schritte-in-shopify)
12. [Offene Fragen](#12-offene-fragen)

---

## 1. Status

| Etappe | Inhalt | Status |
|---|---|---|
| 1 | Analyse beider Themes, PORT.md | ✅ |
| 2 | Design-Tokens: Farben, Schriften, Abstände, Button- und Card-Stile | ✅ |
| 3 | Header, Footer, Ankündigungsleiste | ✅ |
| 4 | Startseite | ✅ |
| 5 | Produktseite inkl. aller Blöcke | ✅ |
| 6 | Collection, Cart, Search, 404, About, FAQ, Contact | ✅ |
| 7 | Fehlende Sections als eigene Theme-Blocks | ✅ |
| 8 | Feinschliff per CSS, Theme Check, Mobil-Prüfung | 🟨 |
| 9 | ZIP-Lieferung | ✅ |

Prüfungen: `shopify theme check` **0 Errors**, `tools/verify.py` **0 Fehler**.

| Symbol | Bedeutung |
|---|---|
| ✅ | fertig umgesetzt und geprüft |
| 🟨 | in Arbeit |
| ❓ | warte auf deine Entscheidung |
| ⏭️ | bewusst nicht portiert, Begründung in der Zeile |

---

## 2. Drei Korrekturen zur Ausgangslage

### 2.1 Horizon 4.3.0 hat **keine Color Schemes**

Shrine nutzt flache Farben plus fünf CSS-Klassen-Schemes
(`color-background-1`, `-2`, `color-inverse`, `color-accent-1`, `-2`).
Horizon 4.3.0 hat **auch keine** Schemes, sondern eine globale Palette
(`color_palette` mit `background`, `foreground`, `color1`, `color2`), ein
`background_color` pro Section und `snippets/contrast-override.liquid`, das
den passenden Vordergrund selbst errechnet.

Shrines Schemes sind daher in Hex-Werte aufgelöst:

| Shrine-Scheme | Hintergrund | Vordergrund | Horizon |
|---|---|---|---|
| `background-1` | `#FBF9F5` | `#1C1A17` | globale Palette, kein Override |
| `background-2` | `#F2EDE5` | `#1C1A17` | `background_color: "#F2EDE5"` |
| `inverse` / `accent-1` | `#1C1A17` | `#FBF9F5` | `background_color: "#1C1A17"` |
| `accent-2` | `#7A3B1E` | `#FBF9F5` | `background_color: "#7A3B1E"` |

### 2.2 `_blocks` kommt nicht von GemPages

`_blocks` ist Shopifys eigener Container für freistehende Theme-Blocks —
Horizon hat die Section selbst (`sections/_blocks.liquid`). Die drei
Instanzen im Live-Theme (2× `index.json`, 1× `header-group.json`) sind
**inhaltlich leer**. Sie bleiben als benannte Platzhalter erhalten, weil
`_blocks` App-Blöcke aufnimmt und damit der richtige Ort für die
GemPages-Inhalte ist.

### 2.3 Vier der „neu bauen"-Sections sind im Live-Theme gar nicht aktiv

Von Shrines 79 Sections sind **44 in Templates verwendet**, 35 liegen
ungenutzt im Theme. Nicht verwendet und deshalb nicht nachgebaut:
`bundle-deals`, `pricing-table`, `promo-popup`, `scroll-to-top-btn` — die
letzten drei sind in `settings_data.json` zusätzlich explizit deaktiviert
(`"mode": "disabled"`, `"enable_scroll_btn": false`, `"enabled": false`).

---

## 3. Design-Tokens

### 3.1 Farben ✅

| Shrine | Wert | Horizon |
|---|---|---|
| `colors_background_1` | `#FBF9F5` | `color_palette.background` |
| `colors_text` | `#1C1A17` | `color_palette.foreground` |
| `colors_background_2` | `#F2EDE5` | `color_palette.color2` |
| `colors_accent_2` | `#7A3B1E` | `color_palette.color1`, Sale-Marker |
| `colors_solid_button_labels` | `#FBF9F5` | `palette_primary_button_text` |
| `colors_outline_button_labels` | `#1C1A17` | `palette_secondary_button_text` |
| `sale_badge_color_scheme: accent-2` | `#7A3B1E` | `badge_sale_background_color` |
| `sold_out_badge_color_scheme: background-1` | `#FBF9F5` | `badge_sold_out_background_color` |

### 3.2 Schriften ✅

`type_header_font: jost_n4` → `type_heading_font` **und** `type_accent_font`.
`type_body_font: assistant_n4` → `type_body_font`, `type_subheading_font: assistant_n5`.

Zwei Hürden bei den Größen:

- **Root-Größe.** Shrine lief auf `font-size: 62.5%`, also 1rem = 10px.
  Horizon nutzt den Browser-Default, 1rem = 16px. Jeder rem-Wert ist
  umgerechnet (×10÷16); die px-Sollwerte stehen als Kommentar im CSS.
- **Größenleiter.** Horizon erzeugt `--font-size--h1…h6` aus einer festen
  Leiter (10, 12, 14, 16, 18, 20, 24, 32, 40, 48, 56 …). Shrines
  Zwischengrößen gibt es darin nicht. Lösung: Setting auf den nächsten
  Leiterwert, exakte Größe in `solena-design.css` gepinnt.

| Shrine | mobil | Desktop | Horizon-Preset | Setting | gepinnt |
|---|---|---|---|---|---|
| `.h0` | 32px | 52px | h1 | `type_size_h1: 48` | `2rem` → `3.25rem` |
| `.h1` | 28px | 38px | h2 | `type_size_h2: 40` | `1.75rem` → `2.375rem` |
| `.h2` | 22px | 28px | h3 | `type_size_h3: 32` | `1.375rem` → `1.75rem` |
| `.h3` | 19px | 22px | h4 | `type_size_h4: 24` | `1.1875rem` → `1.375rem` |
| `.h4` | 16px | 16px | h5 | `type_size_h5: 16` | `1rem` |
| `.h5` | 14px | 14px | h6 | `type_size_h6: 14` | `0.875rem` |
| Body | 15px | 15px | paragraph | `type_size_paragraph: 16` | `0.9375rem` |

`.hxl` (64px) kommt in keinem Live-Template vor und entfällt.

### 3.3 Form, Abstand, Button, Card ✅

| Shrine | Wert | Horizon |
|---|---|---|
| `page_width` | 1600 | `page_width: "wide"` + CSS `--wide-page-width: 100rem` |
| `buttons_radius` | 0 | `button_border_radius_primary/secondary: 0`, `pills_border_radius: 0` |
| `inputs_radius` | 0 | `inputs_border_radius: 0` |
| `media_radius` / `card_corner_radius` | 2 | `product_corner_radius: 2`, `card_corner_radius: 2` |
| `badge_corner_radius` 40, `badge_position` top left | | `badge_corner_radius: 100`, `badge_position: "top-left"` |
| `variant_pills_radius` | 0 | `variant_button_radius: 0`, `variant_swatch_radius: 0` |
| `spacing_grid_horizontal/vertical` | 24 / 40→56 | `columns_gap: 24`, `rows_gap: 56` pro Grid |
| alle `*_shadow_*` | 0 | `popover_drop_shadow: false`, `--shadow-*: none` |
| `cart_type` | drawer | `cart_type: "drawer"`, `auto_open_cart_drawer: true` |
| `logo_width` 150 | | `logo_height: 38` / `logo_height_mobile: 30` ❓ Richtwert |

Insgesamt **129 von 133 Settings** gesetzt, generiert und gegen das Schema
validiert von `tools/settings.py`. Die vier übrigen bleiben bewusst auf
Default.

### 3.4 Der Design-Layer ✅

Dein Live-Look steckt nicht in Shrine, sondern in deinem eigenen
`assets/solena-design.css` — 1388 Zeilen. Dazu
`snippets/card-swatches.liquid` (Farbvokabular mit ~90 Einträgen) und die
`ds-*`-Topline in der Produktkarte. Die Git-Historie dieses Repos zeigt,
dass das dein Code ist, nicht Shrines, also wurde er übernommen und auf
Horizons Tokens umgeschrieben:

- `horizon/assets/solena-design.css` — 990 Zeilen, 17 Abschnitte, gegen
  Horizons Tokens (`--color-foreground-rgb`, `--font-h1--size`, `--opacity-*`,
  `--font-body--family`) statt Shrines Dawn-Variablen.
- `horizon/snippets/solena-card-swatches.liquid` — Logik 1:1, Klassennamen
  auf `solena-*` umgestellt.

Der Layer wird in **beiden Layouts zweimal** geladen: im `<head>` nach
`color-palette` und erneut am Ende von `<body>`. Horizon gibt die Styles
seiner Sections und Blocks als `{% style %}` im Body aus; ohne die zweite
Einbindung verliert der Layer jeden Gleichstand bei der Spezifität. Das ist
dasselbe Muster wie in Shrine.

Gemessene Kernwerte, alle im Layer reproduziert: Buttons 12px / `.16em` /
uppercase / `min-height: 54px` / `padding: 0 36px` / Hover `opacity .82`;
Eyebrow 11px / `.18em`; Header 18px Padding, 1px Unterkante, Nav 12.5px /
`.14em`; Karte Bild (radius 2) → Topline → Haarlinie → Preis 16px →
Swatches 18px; Grid 24/56px; Badge Pille 999px; Accordion Haarlinien,
22px Padding; Footer 1px Oberkante, Headings 11px / `.2em`; gedämpfter Text
`rgba(fg, .58)`; Haarlinie `rgba(fg, .12)`; Easing
`cubic-bezier(.22,.61,.36,1)`.

---

## 4. Was pro Template drin ist

Alle Texte, Bild-Handles, Kollektions-Handles und Einstellungen sind aus den
`settings`-Objekten des Shrine-Exports übernommen. Die Templates entstehen
aus `tools/templates.py`, damit die Produktkarte in allen acht Templates
gleich bleibt, in denen sie vorkommt.

### sections/header-group.json ✅

| Shrine | Horizon | Inhalt |
|---|---|---|
| `announcement-bar` + 1 Block | `header-announcements` + `_announcement` | „Kostenloser DHL-Versand inkl. Sendungsverfolgung", Hintergrund `#1C1A17`, 12px uppercase |
| `horizontal-ticker` + 3 Blöcke, **deaktiviert** | `marquee` + 3× `text`, **deaktiviert** | „WELCOME!", „SITEWIDE SALE", „USE CODE X FOR X% OFF!" |
| `header` | `header` + `_header-logo`, `_header-menu` | sticky `always`, Logo links, Menü zentriert, Icons rechts, 1px Unterkante, `main-menu`, Cart-Bubble in Vordergrundfarbe |
| `_blocks` (leer) | `_blocks` „GemPages Platzhalter (Kopfbereich)" | leer, siehe §8 |

**Nicht übertragbar:** Shrines `mobile_menu_title: "Menu"` — Horizon beschriftet
die Schublade über die Sprachdatei. `highlighted_link_color_scheme` entfällt
mit den Schemes; der aktive Menüpunkt bekommt stattdessen die Unterstreichung
aus dem Design-Layer, wie in Shrine.

### sections/footer-group.json ✅

| Shrine | Horizon | Inhalt |
|---|---|---|
| `apps` (leer) | `_blocks` „GemPages Platzhalter (Fußbereich)" | leer, siehe §8 |
| `footer` Block `link_list` | `menu` | „Menü" → `main-menu` |
| `footer` Block `link_list` | `menu` | „Rechtliches" → `rechtliches` |
| `footer` Block `text` | `group` mit 2× `text` | „Kontakt" mit Service-Zeiten, `support@solenahome.com`, Anschrift Graz |
| `payment_enable: true` | `payment-icons` in `footer-utilities` | rechts in der unteren Leiste |
| `branding_text: ""` | `footer-copyright` | `show_powered_by: false` |

**Nicht übertragbar:** `enable_language_selector: true` saß bei Shrine im
Footer. Horizon bietet die Sprachauswahl nur im Header an — dort ist sie
jetzt aktiv (`show_language: true`). Bei nur einer veröffentlichten Sprache
rendert sie ohnehin nichts. Der Ländersteller bleibt aus, wie in Shrine.

### templates/index.json ✅ — 9 Sections

| # | Shrine | Horizon | Inhalt |
|---|---|---|---|
| 1 | `slideshow`, 1 Slide | `slideshow` + `_slide` | „Entdecke Solena" / „Weil Design keine Ausnahme sein sollte" / Button „Finde jetzt deinen Stil" → `/collections/all`; full-width, `slide_height: large`, Counter, Overlay 10 %, Text links mittig |
| 2 | `collection-list`, 5 Blöcke | `collection-list` + `_collection-card` | „Collections"; hangeleuchten, deckenleuchten, tischleuchten, wandleuchten, outdoor-leuchten; 5 Spalten / 2 mobil, square, Swipe mobil, Padding 72/88 |
| 3 | `featured-collection` | `product-list` | „Solena Bestseller" (h1), Kollektion `bestseller`, 16 Produkte, 5 Spalten / 2 mobil, Bewertung an, Padding 36/36 |
| 4 | `_blocks` (leer) | `_blocks` | GemPages Platzhalter 1 |
| 5 | `_blocks` (leer) | `_blocks` | GemPages Platzhalter 2 |
| 6 | `image-with-text`, 3 Blöcke | `media-with-content` | „Ein Statement für dein Zuhause" / „Wo nordische Ruhe auf Design trifft" / „Mehr lesen" → `/pages/uber-uns`; Hintergrund `#F2EDE5`, Bild rechts schmal, Padding 96/96 |
| 7 | `featured-product`, **deaktiviert** | `featured-product`, **deaktiviert** | kein Produkt gesetzt, wie im Original |
| 8 | `featured-collection` | `product-list` | „Trends 2026", Kollektion `trends`, 4 Produkte, 4 Spalten, „Alle ansehen" |
| 9 | `testimonials`, 3 Blöcke | `section` → `group` → 3× `solena-testimonial` | „Zufriedenheit ist unsere Voraussetzung", 3 Spalten, zentriert, Sterne; Julia S. / Thomas W. / Andrea Z. mit den Originaltexten |

**Nicht übertragbar:** Shrines `featured-product` hatte 7 Blöcke
(text, title, price, variant_picker, quantity_selector, buy_buttons, share),
alle einzeln deaktiviert, und kein Produkt. Horizons `featured-product` ist
eine Section ohne Blöcke; sie ist deaktiviert übernommen. Sobald du ein
Produkt setzt, gibt Horizon dort seine eigene Blockstruktur vor.

### templates/product.json ✅ — 9 Sections

`product-information` mit `enable_sticky_add_to_cart: true`, Galerie als
Karussell mit Thumbnails unten, Zoom an, `media_fit: contain`,
`media_radius: 2`, Details sticky, Padding 32/88.

Die 15 Blöcke in der Reihenfolge des Exports:

| # | Shrine-Block | Horizon | Status |
|---|---|---|---|
| 1 | App: Iconic Review Summary | — | ❓ §7, in Shopify einsetzen |
| 2 | `title` | `product-title` (h3, Jost) | ✅ |
| 3 | App: Iconic Benefits | — | ❓ §7 |
| 4 | App: Judge.me Preview Badge | — | ❓ §7 |
| 5 | App: Iconic Review Summary (2.) | — | ❓ §7 |
| 6 | `price` | `price` (20px, weight 500) | ✅ |
| 7 | `emoji_benefits`, deaktiviert | `solena-emoji-benefits`, deaktiviert | ✅ neu gebaut |
| 8 | `variant_picker` (Buttons) | `variant-picker` | ✅ |
| 9 | `quantity_selector`, deaktiviert | `quantity`, deaktiviert | ✅ |
| 10 | `buy_buttons` | `buy-buttons` + `quantity`, `add-to-cart`, `accelerated-checkout` | ✅ |
| 11 | `sticky_atc` | Section-Setting `enable_sticky_add_to_cart` | ✅ ohne Neubau |
| 12 | `payment_badges` | `payment-icons` | ✅ ohne Neubau |
| 13 | `collapsible_tab` „Produktbeschreibung" | `accordion` + `_accordion-row` + `product-description`, Icon `clipboard` | ✅ |
| 14 | `collapsible_tab` „Versandinformationen" | `_accordion-row` + `text`, Icon `truck` | ✅ |
| 15 | `collapsible_tab` „Rückgabeinformationen" | `_accordion-row` + `text`, Icon `return` | ✅ |

Danach:

| Shrine | Horizon | Inhalt |
|---|---|---|
| `related-products`, deaktiviert | `product-recommendations`, deaktiviert | „Das könnte dir auch gefallen" |
| `apps` ×2 (leer) | `_blocks` ×2 | GemPages Platzhalter 1 und 2 |
| `rich-text`, 2 Blöcke | `section` + 2× `text` | „Über Uns" + Markentext, Hintergrund `#F2EDE5`, full-width, zentriert |
| `comparison-table`, 3 Blöcke | `section` + `solena-comparison-table` + 3 Zeilen | „Was uns ausmacht"; Persönlicher Kundenservice / Designerlampen zum fairen Preis / 30 Tage Geld-zurück-Garantie; Haken `#53AF01` |
| `apps` (Judge.me Widget) | `_blocks` „Judge.me Bewertungen" | ❓ §7 |
| `apps` (leer) | `_blocks` | GemPages Platzhalter 3 |
| `collapsible-content`, 8 Blöcke | `section` + `accordion` + 8 Zeilen | „Häufig gestellte Fragen", Hintergrund `#F2EDE5`, alle 8 deutschen Einträge |

**Nicht übertragbar:** Shrines `sticky_atc` hatte den eigenen Button-Text
„Zum Warenkorb"; Horizons eingebaute Leiste nimmt den Text aus der
Sprachdatei („In den Warenkorb legen"). `show_price_badge` hat kein
Gegenstück. `trust_badge_position`/`trust_badge_size` der Section ebenfalls
nicht — die Badges kamen bei Shrine aus der Vitals-App.

### templates/collection.json ✅

| Shrine | Horizon | Inhalt |
|---|---|---|
| `main-collection-banner` | `section` + `solena-collection-banner` | Titel h2 + Beschreibung, Bild aus (`show_collection_image: false`) |
| `main-collection-product-grid` | `main-collection` + `filters` + Produktkarte | 20 Produkte/Seite, 4 Spalten / 2 mobil, square, Bewertung aus, Filter horizontal, Sortierung an, Padding 32/88 |

**Nicht übertragbar:** Shrines `filter_type: horizontal` — Horizons
`filters`-Block hat eine eigene Darstellung ohne diese Wahl.
`enable_quick_add: false` ist global über `quick_add: false` gesetzt.

### templates/collection.alle.json ✅ (neu)

Banner (deaktiviert, wie im Original) → `section` mit „Alle Produkte" und
dem Einleitungstext → Produktraster mit `show_secondary_image: true`.

### templates/cart.json ✅

`main-cart` (Padding 40/32) → `product-list` „Entdecke unsere Produkte"
(Kollektion `alleprodukte`, 4 Produkte, „Alle ansehen") → `product-list`
„You may also like" (deaktiviert) → Newsletter-Section (deaktiviert).

**Nicht übertragbar:** Shrines `main-cart-footer`-Blöcke `discount_field`
(deaktiviert), `subtotal`, `buttons` sind bei Horizon fest in
`_cart-summary` enthalten; der Rabattcode hängt am Theme-Setting
`show_add_discount_code: true`.

### templates/404.json ✅

`main-404` (Horizons Struktur) → Newsletter (deaktiviert) →
`media-with-content` „Warum Solena?" mit dem Originaltext, Hintergrund
`#F2EDE5`, Bild rechts schmal.

### templates/page.json ✅

`main-page` + `page-content` → `_blocks` ×2 (GemPages) → `product-list`
„Trends 2026".

### templates/page.about-us.json ✅ (neu)

`main-page` + drei `media-with-content`-Sections. Shrines `multirow` mit
`image_layout: alternate-left` wechselt die Bildseite von Zeile zu Zeile;
Horizon hat kein `multirow`, also eine Section je Zeile mit
`media_position` links / rechts / links:

1. „Weil Licht Räume verwandelt"
2. „Wir setzen auf treue Kunden"
3. „Design kennt keine Grenzen – unser Blick auch nicht"

**Nicht übertragbar:** Die beiden leeren `rich-text`-Sections am Ende
(eine ohne Blöcke, eine nur mit deaktiviertem Button) enthielten keinen
Inhalt und sind entfallen.

### templates/page.contact.json ✅

`main-page` (deaktiviert) → `section` „Kontakt" + Einleitungstext →
`section` mit `contact-form` (60 % Breite) → `section`
„Kontaktinformationen" mit Mail und Anschrift.

### templates/page.faq.json ✅ (neu)

`main-page` (deaktiviert) → `section` mit Eyebrow „FAQ", Überschrift
„Häufig gestellte Fragen" und `accordion` mit 8 Zeilen (Hintergrund
`#F2EDE5`) → `section` „Kontaktinformationen" mit Button „Zur Kontaktseite".

**Hinweis:** Zwei Antworten standen im Shrine-Export auf dem Platzhalter
„EINFÜGEN" (Kontaktinformationen und „Wie kann ich euch erreichen?"). Ich
habe dort `support@solenahome.com` eingesetzt, wie auf der Produktseite.

### templates/page.track-order.json ✅ (neu)

`main-page` (deaktiviert) → `section` mit `solena-track-order` →
`media-with-content` „Get in touch!" (deaktiviert, wie im Original).

**Hinweis:** Überschrift und Beschriftungen waren im Original **englisch**
(„TRACK YOUR ORDER", „Tracking Number", „Track Now") und sind 1:1
übernommen. Siehe §12.

### templates/blog.json, article.json, list-collections.json, search.json ✅

Horizons Struktur bleibt, Shrines `newsletter`-Section kommt dazu
(Hintergrund `#F2EDE5`, Padding 88/88). Bei `list-collections` auf 3 Spalten
und `square` gesetzt, Überschrift „Collections". Bei `search` trägt das
Raster die Solena-Produktkarte.

**Hinweis:** Die Newsletter-Texte sind im Shrine-Export **englisch**
(„Subscribe to our emails", „Join our email list for exclusive offers and
the latest news.", „Sign up") und 1:1 übernommen. Siehe §12.

### templates/password.json ✅

Horizons `password`-Section mit Shrines Texten „Opening soon" und „Be the
first to know when we launch." — im Original ebenfalls englisch.

---

## 5. Eigene Theme-Blocks

Alle nach Horizons Konventionen: `{% schema %}` mit `"tag": null`,
`contrast-override` für Farben, `spacing-style` und `border-override` für
Abstand und Rahmen, `{{ block.shopify_attributes }}`, Kindblöcke über
`{% content_for 'blocks' %}`. Die Optik liegt in `solena-design.css`, nicht
in den Blöcken — eine Stelle für alles.

| Block | Ersetzt | Wo verwendet |
|---|---|---|
| `solena-testimonial` | Shrines `testimonials`-Section (Block `column`) | index |
| `solena-comparison-table` + `_solena-comparison-row` | `comparison-table` | product |
| `solena-track-order` + `assets/solena-track-order.js` | `track-order` | page.track-order |
| `solena-emoji-benefits` | `emoji_benefits` | product |
| `solena-product-type` | der Produkttyp unter dem Kartentitel | 8 Templates |
| `solena-card-swatches` + `snippets/solena-card-swatches.liquid` | `card-swatches.liquid` | 8 Templates |
| `solena-hairline` | die 1px-Linie in der Produktkarte | 8 Templates |
| `solena-collection-banner` | `main-collection-banner` | collection, collection.alle |

### Warum vier aus deiner Liste nicht gebaut wurden

| Deine Liste | Grund |
|---|---|
| `sticky_atc` | Horizon hat das eingebaut: `enable_sticky_add_to_cart` in `product-information` zeigt Bild, Titel, Variante, Preis und Add-to-Cart. Ein Nachbau wäre doppelt. |
| `payment_badges` | Horizon hat `blocks/payment-icons.liquid`. |
| `icon-bar` | Horizons `section.liquid` hat das Preset `icons_with_text`. Zusätzlich: in keinem der gebauten Templates verwendet, nur in `product.gp-template-bk-default`. |
| `horizontal-ticker` | `marquee` deckt es ab. |
| `vertical-ticker` | Kommt nur in `product.gp-template-bk-default` vor, also in keinem der jetzt gebauten Templates. Wird mit den Premium-Templates gebaut, wenn du sie brauchst — siehe §12. |

### Warum `solena-track-order` eigenen JavaScript-Code hat

Shrines Section band das Widget von **17TRACK** mit einem globalen
`onclick="doTrack()"` und einem Skript-Tag direkt in der Section ein.
`assets/solena-track-order.js` macht dasselbe als Custom Element: lädt
`externalcall.js` erst beim ersten Klick, meldet Fehler im Markup statt per
`alert()`, und lässt sich mehrfach auf einer Seite verwenden, weil die
Container-ID aus der Block-ID kommt. Die aufgerufene Schnittstelle
(`YQV5.trackSingle`) ist die öffentliche Integration von 17TRACK, kein
Theme-Code.

### Warum die Blöcke deutsche Beschriftungen statt `t:`-Schlüsseln haben

Horizons Schemas nutzen `t:`-Verweise auf `locales/*.schema.json`. Für die
eigenen Blöcke stehen die Beschriftungen als Klartext im Schema, wo es um
eigene Felder geht („Vorteil", „Sterne anzeigen"), und als `t:`-Verweis, wo
Horizon den Begriff schon hat (`t:settings.alignment`,
`t:content.padding`). Das hält die Sprachdateien frei von Sonderfällen und
zeigt im Theme-Editor deutsche Labels, passend zum Shop.

---

## 6. Änderungen an Horizons eigenen Dateien

Vier Eingriffe waren nötig. Alle sind klein, kommentiert und begründet.

| Datei | Änderung | Warum |
|---|---|---|
| `snippets/color-palette.liquid` | gibt die Palettenfarben zusätzlich einzeln als `--color-palette-background/-foreground/-color1/-color2` aus | damit der Design-Layer Akzent- und Flächenton nicht hart verdrahtet |
| `sections/marquee.liquid` | `"header"` aus `disabled_on.groups` entfernt, Footer-Sperre bleibt | Shrine zeigte den Lauftext als eigene Section in der Header-Gruppe. Ohne die Änderung lehnt Shopify das Template ab — `tools/verify.py` hat genau das gefunden. |
| `sections/footer-utilities.liquid` | `payment-icons` zu den erlaubten Blöcken ergänzt | Shrine zeigte die Bezahl-Icons in der unteren Fußzeile. Horizon erlaubte dort nur Copyright, Policy-Liste und Social-Links. |
| `blocks/_product-card.liquid`, `blocks/_product-card-group.liquid` | `solena-product-type`, `solena-card-swatches`, `solena-hairline` zu den erlaubten Blöcken ergänzt | diese beiden Blöcke führen ihre Kinder explizit auf, nicht über `@theme` |

Dazu `layout/theme.liquid` und `layout/password.liquid`: zweimal
`solena-design.css` und einmal `microsoft-clarity`.

---

## 7. App-Blöcke — was du in Shopify einsetzen musst

App-Blöcke stehen **nicht** in den Templates. `shopify theme check` kann
`shopify://apps/…`-Typen offline nicht auflösen und meldet sie als
`JSONMissingBlock` — das verträgt sich nicht mit der Vorgabe, dass der
Theme Check fehlerfrei durchläuft. Die Container stehen aber alle an der
richtigen Stelle.

### Produktseite → Section „Produktinformationen" → Bereich Details

Fünf Blöcke, mit den Einstellungen aus dem Shrine-Export:

**1. ganz oben, vor dem Titel — Iconic Blocks → Review Summary**

| Einstellung | Wert |
|---|---|
| Link | `https://at.trustpilot.com` |
| Rating-Text | `Excellent` |
| Bewertungen | `Über 35.000 Bewertungen` |
| Textgröße | 14 |
| Ausrichtung | start |
| Textfarbe | `#000000` |
| Sterne | 4,5 bei Größe 15 |
| Sternfarbe / Hintergrund | `#ffffff` auf `#00b67a` |
| Abstand oben/unten | 10 |

**2. direkt unter dem Titel — Iconic Blocks → Benefits**

| Einstellung | Wert |
|---|---|
| Icon | `bi bi-check2`, Größe 18, Farbe `#000000` |
| Hintergrund | `#fbf9f5`, Radius 10 |
| Textgröße / Abstand / Farbe | 16 / 6 / `#000000` |
| Benefit 1–4 | `{{ product.metafields.custom.selling_point_1.value }}` bis `…_4.value` |
| Innen- und Außenabstand | 0 |

**3. darunter — Judge.me → Preview Badge** (keine Einstellungen)

**4. darunter — Iconic Blocks → Review Summary, zweite Instanz**

Gleiche Einstellungen wie 1, aber ohne Link und mit `20,921 reviews`.
Das sieht nach einem Überrest aus; siehe §12.

Danach folgen die Theme-Blöcke in dieser Reihenfolge: Preis, Vorteile mit
Emoji (aus), Variantenauswahl, Menge (aus), Kaufen-Schaltflächen,
Bezahl-Icons, Aufklappbereich.

### Produktseite → Section „Judge.me Bewertungen"

**Judge.me → Review Widget**

| Einstellung | Wert |
|---|---|
| Datenquelle | echte Daten |
| Maximale Breite | 700 |
| Shop-Bewertungen zeigen | aus |
| Leerzustand | leeres Widget |

### App-Embeds aktivieren

Unter **Online Store → Themes → … → Customize → App embeds**:

| App | Embed | Im Live-Theme |
|---|---|---|
| Judge.me Reviews | `judgeme_core` | aktiv |
| Judge.me Reviews | `cart_drawer_widget` (`review-widget`) | aktiv |
| Judge.me Reviews | `reviews_tab` | deaktiviert |
| Judge.me Reviews | `popup_widget` | deaktiviert |
| Iconic Blocks | `app-embed` | aktiv |
| Google Ads Pixel by Nabu | `script-block` | aktiv |

### Vitals

Shrine enthielt acht `tsapb-*`-Sections der Vitals-App („❤️ Value Icons",
„❤️ Testimonials", „❤️ Image & Text" …). **Keine davon ist in einem
Template verwendet.** Sie sind nicht portiert; wenn du eine brauchst, legt
Vitals sie nach Installation selbst neu an.

---

## 8. GemPages — was neu gebaut werden muss

GemPages-Inhalt liegt in der App, nicht im Theme. An jeder Stelle, an der
Shrine eine `apps`- oder `_blocks`-Section hatte, steht jetzt eine leere,
benannte `_blocks`-Section. `_blocks` nimmt App-Blöcke auf, du musst den
Platz also nur befüllen.

| Template | Platzhalter | Shrine-Original |
|---|---|---|
| `sections/header-group.json` | GemPages Platzhalter (Kopfbereich) | `_blocks`, leer |
| `sections/footer-group.json` | GemPages Platzhalter (Fußbereich) | `apps`, leer |
| `templates/index.json` | GemPages Platzhalter 1 und 2 | 2× `_blocks`, leer |
| `templates/product.json` | GemPages Platzhalter 1, 2 und 3 | 3× `apps`, leer |
| `templates/page.json` | GemPages Platzhalter 1 und 2 | 2× `apps` |

### Seiten, die du in GemPages für Horizon neu bauen musst

| Shrine-Datei | Was es war |
|---|---|
| `templates/page.indoor.json` | Seite „Indoor", Inhalt komplett in GemPages (2× `apps`) |
| `templates/page.json` | die allgemeine Seitenvorlage, Inhalt in GemPages (2× `apps`) |
| `templates/index.gem-1775335711-template.json` | GemPages-Backup der Startseite |
| `templates/index.gp-template-bk-default.json` | GemPages-Backup der Startseite |
| `templates/collection.gp-template-bk-default.json` | GemPages-Backup einer Kollektionsseite |
| `templates/product.gp-template-bk-default.json` | GemPages-Backup einer Produktseite |

Die vier Backup-Templates enthalten **nur native Shrine-Sections**, keine
GemPages-Inhalte — GemPages hat sie beim Umschalten als Sicherung angelegt.
Sie sind damit portierbar, aber als Backups ohne Funktion. Ich habe sie
nicht gebaut; sag Bescheid, wenn du eines davon brauchst.

### GemPages-Dateien aus Shrine

| Datei | Umsetzung |
|---|---|
| `layout/theme.gem-layout-none.liquid` | ⏭️ nicht portiert. Das sind Kopien von Shrines `theme.liquid` mit GemPages-Haken — also Shrine-Code. GemPages legt die Layouts nach Installation für Horizon selbst an. |
| `layout/theme.gempages.blank.liquid` | ⏭️ wie oben |
| `layout/theme.gempages.footer.liquid` | ⏭️ wie oben |
| `layout/theme.gempages.header.liquid` | ⏭️ wie oben |
| `snippets/gp-head.liquid` | ⏭️ wird von GemPages mit dem Layout zusammen angelegt |
| `assets/gp-global.css` | ⏭️ wie oben |
| `sections/gp-variant-selected.liquid` | ⏭️ App-Section, in keinem Template verwendet |
| `blocks/ai_gen_block_1554822.liquid` | ⏭️ von keinem Template referenziert, also tot |

---

## 9. Qualitätssicherung

| Prüfung | Werkzeug | Ergebnis |
|---|---|---|
| Liquid- und Schema-Validierung | `shopify theme check` (CLI 5.0.0) | 372 Dateien, **0 Errors**, 6 Warnings |
| JSON, Referenzen, Block-Architektur, Platzierung, Limits | `tools/verify.py` | 293 Liquid-Dateien, 20 JSON-Dokumente, **0 Fehler, 0 Warnungen** |
| Theme-Settings gegen das Schema | `tools/settings.py` | 129 von 133 gesetzt, 4 bewusst auf Default |

Die sechs Warnings stammen unverändert aus Horizons Lieferzustand:
fünf `UnusedDocParam` in `snippets/divider.liquid`, eine
`ExcessiveSettingsCount` in `sections/header.liquid`.

`tools/verify.py` prüft acht Dinge, die `theme check` nicht abdeckt:

1. Alle JSON-Templates und Section-Groups parsen, inklusive der `/* */`- und
   `//`-Kommentare, die Shopify dort erlaubt.
2. Jede `{% render %}`-Referenz zeigt auf ein existierendes Snippet
   (`{% doc %}`-Beispiele zählen nicht).
3. Jede `| asset_url`-Referenz zeigt auf eine Datei in `assets/`.
4. Jeder Section-Type existiert in `sections/`.
5. Jeder Block-Type existiert in `blocks/` **und** ist im Schema seines
   Elternteils erlaubt — `@theme`, `@app` und statisch per
   `{% content_for 'block' %}` gesetzte Blöcke werden aufgelöst.
6. `enabled_on` / `disabled_on`: darf die Section in dieser Gruppe oder auf
   diesem Template stehen? **Das hat den Marquee-Fehler gefunden**, der den
   Upload gebrochen hätte.
7. `max_blocks` der Section und `limit` je Block-Type.
8. Jeder `t:`-Schlüssel existiert in `locales/en.default.schema.json`.

### Noch offen in Etappe 8

| Punkt | Warum noch offen |
|---|---|
| Mobil- und Desktop-Prüfung im Browser | braucht einen laufenden Store. Ohne Store-Zugang habe ich nur statisch gegen die Breakpoints geprüft: `max-width: 749px` für Handy, `min-width: 750px` und `990px` für Desktop, dieselben Grenzen wie in Shrine. Sobald das Theme in der Vorschau läuft, sag mir, was abweicht. |
| `locales/de.json` | Horizons deutsche Datei deckt Shrines Strings bereits ab — `add_to_cart` heißt in beiden „In den Warenkorb legen", `sold_out` „Ausverkauft". Es war also nichts zu pflegen. Falls du die Sticky-Leiste auf „Zum Warenkorb" willst, ist das ein Eintrag in `products.product.add_to_cart` — der ändert dann aber auch den Hauptbutton. |

---

## 10. Bewusst offen geblieben

| Punkt | Grund |
|---|---|
| `templates/customers/*` (7 Dateien) | Horizon 4.3.0 liefert keine Customer-Templates; Shopify rendert sie aus `layout/theme.liquid`. Ein Nachbau wäre gegen Horizons Architektur. |
| `templates/gift_card.liquid` | Horizon hat eine eigene Version. Shrines zu übernehmen hieße Shrine-Code kopieren. |
| `product.premium-1` bis `premium-8` | ❓ siehe §12 |
| `bundle-deals`, `pricing-table`, `promo-popup`, `scroll-to-top-btn`, `global-music-player`, `music-player` | in keinem Template verwendet, drei zusätzlich per Setting deaktiviert |
| 8× `tsapb-*` (Vitals) | App-Sections, in keinem Template verwendet |
| 30 weitere ungenutzte Shrine-Sections | nicht Teil der Live-Optik |
| `disable_inspect` | kein Gegenstück in Horizon, war ohnehin `false` |
| Checkout-Farben (`#1C1A17`) | gehören ins Shopify-Checkout-Branding, nicht ins Theme |
| `cart_progress_*`, `cart_upsell_1/2`, `enable_countdown_timer` | Shrine-Features im Cart-Drawer. Fortschrittsbalken und beide Upsells waren deaktiviert. Der Countdown-Timer war an, mit dem Text „Kostenloser DHL-Versand inkl. Sendungsverfolgung" — derselbe Text steht schon in der Ankündigungsleiste, deshalb habe ich ihn nicht doppelt gebaut. Sag Bescheid, wenn du ihn im Warenkorb willst. |

---

## 11. Deine Schritte in Shopify

1. **ZIP hochladen** unter Online Store → Themes → Add theme → Upload zip
   file. Noch **nicht veröffentlichen**, erst in der Vorschau prüfen.
2. **Menüs prüfen:** `main-menu` und `rechtliches` müssen unter Navigation
   unverändert existieren. Das Theme verweist auf diese beiden Handles.
3. **Kollektions-Handles prüfen:** `bestseller`, `trends`, `alleprodukte`,
   `hangeleuchten`, `deckenleuchten`, `tischleuchten`, `wandleuchten`,
   `outdoor-leuchten`.
4. **Logo-Höhe nachziehen.** Shrine stellte die Breite auf 150px, Horizon
   skaliert über die Höhe. Ich habe 38px Desktop / 30px mobil gesetzt —
   bitte nach Augenmaß korrigieren.
5. **App-Embeds aktivieren:** Judge.me, Iconic Blocks, Google Ads Pixel by
   Nabu. Siehe §7.
6. **App-Blöcke einsetzen:** vier auf der Produktseite, eines in der
   Section „Judge.me Bewertungen". Positionen und Einstellungen in §7.
7. **GemPages-Inhalte** in die benannten Platzhalter setzen. Siehe §8.
8. **Produkt-Metafelder prüfen:** `custom.selling_point_1` bis `_4` — der
   Iconic-Benefits-Block liest sie aus.
9. **Checkout-Branding** auf `#1C1A17` setzen, unter Settings → Checkout →
   Branding.
10. Erst nach Abnahme veröffentlichen.

---

## 12. Offene Fragen

### Frage 1 — `product.premium-1` bis `premium-8`

Du hast entschieden: alle acht 1:1. Ich habe zuerst `product.json` fertig
gebaut, wie vorgegeben. Die acht Varianten haben je 12 bis 13
`main-product`-Blöcke und zusätzlich zwei bis drei
`image-with-text`-Sections, die sich nur in Reihenfolge, Bildern und Texten
unterscheiden.

Bevor ich sie baue: **brauchst du alle acht, oder reicht eine Vorlage, die
du in Shopify duplizierst?** Mit `product.json` fertig und der Produktkarte
im Generator ist jede weitere Variante wenig Aufwand — aber acht
Templates, die sich nur in Bildern unterscheiden, sind acht Dateien, die du
später einzeln pflegen musst.

Falls alle acht: `vertical-ticker`, `icon-bar`, `results` und
`comparison-slider` kommen in `product.gp-template-bk-default` vor. Soll
ich die vier dann auch bauen? `comparison-slider` und `icon-bar` deckt
Horizon ab, `vertical-ticker` und `results` wären Neubauten.

### Frage 2 — englische Texte

An vier Stellen ist der Originaltext englisch. Ich habe ihn 1:1 übernommen,
weil deine Vorgabe „Texte aus dem Shrine-Export übernehmen" lautete — aber
auf einem deutschen Shop sieht das wie ein Fehler aus:

| Stelle | Text |
|---|---|
| Newsletter (blog, article, search, list-collections, cart, 404) | „Subscribe to our emails" / „Join our email list for exclusive offers and the latest news." / „Sign up" |
| Sendungsverfolgung | „TRACK YOUR ORDER" / „Tracking Number" / „Track Now" |
| Passwortseite | „Opening soon" / „Be the first to know when we launch." |
| Lauftext im Header (deaktiviert) | „WELCOME!" / „SITEWIDE SALE" / „USE CODE X FOR X% OFF!" |

Soll ich das eindeutschen? Dann brauche ich deine Texte, oder ich schlage
welche vor.

### Frage 3 — zweite Trustpilot-Zeile

Die Produktseite hat zwei Iconic-Review-Summary-Blöcke: einen mit deinen
echten Werten, einen mit dem App-Platzhalter „20,921 reviews" ohne Link.
Du hattest zuerst „nur die erste" entschieden, dann in der Zielstruktur
beide Positionen (1 und 5) genannt. Ich habe **beide** dokumentiert, weil
die Zielstruktur die spätere Angabe ist. Wenn die zweite doch raus soll,
lass sie in Shopify einfach weg — am Theme ändert sich nichts.

### Frage 4 — drei App-Snippets

`bucks-cc.liquid` (Currency Converter), `cjpod.liquid` (CJ Dropshipping)
und `kiwiSizing.liquid` (Kiwi Sizing) liegen in Shrine. Welche sind noch
aktiv? Dann binde ich sie ein.
