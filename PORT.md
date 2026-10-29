# PORT.md — Shrine⁺ 1.3.5 → Horizon 4.3.0

Portierung des Live-Themes **solenahome-redesign-clarity** (Shrine⁺ 1.3.5) auf
**Horizon 4.3.0**.

- Quelle (Vorlage, nur lesen): `theme_export__…solenahome-redesign-clarity__29OCT2026-0428pm`
- Ziel (Neubau): `horizon/` in diesem Repo
- Regel: **kein Shrine-Code wird kopiert.** Shrine dient ausschließlich als
  optische und funktionale Vorlage. Umgesetzt wird mit Horizons eigenen
  Sections, Theme-Blocks und Snippets.

Stand: Etappe 2 (Design-Tokens) abgeschlossen.

---

## Status-Legende

| Symbol | Bedeutung |
|---|---|
| ✅ | fertig umgesetzt und geprüft |
| 🟨 | in Arbeit |
| ⬜ | geplant, noch nicht angefangen |
| ❓ | warte auf deine Entscheidung |
| ⏭️ | bewusst nicht portiert (Begründung in der Zeile) |

---

## 1. Was die Analyse ergeben hat — drei Korrekturen zu deinen Annahmen

Drei Punkte aus deiner Aufgabenstellung stimmen so nicht. Sie ändern den Plan
an mehreren Stellen, deshalb stehen sie vorne.

### 1.1 Horizon 4.3.0 hat **keine Color Schemes**

Das ist der wichtigste Punkt. Shrine nutzt flache Farben (Dawn-Erbe) plus
fünf CSS-Klassen-Schemes (`color-background-1`, `-2`, `color-inverse`,
`color-accent-1`, `-2`). Horizon 4.3.0 hat **auch keine** Color Schemes —
sondern genau eine globale Palette:

```json
"color_palette": { "background": "#ffffff", "foreground": "#000000",
                   "color1": "#333333", "color2": "#DFDFDF" }
```

Dazu kommen Element-Paletten (`palette_primary_button_*`,
`palette_input_*`, `palette_variant_*`, `badge_*`, `drawer_*`, `popover_*`),
die per Liquid auf `{{ settings.color_palette.* }}` verweisen dürfen. Jede
Section hat ein eigenes `background_color`; `snippets/contrast-override.liquid`
und `snippets/brightness-opacities.liquid` rechnen daraus automatisch den
passenden Vordergrund und die Transparenzstufen.

**Konsequenz:** Shrines Schemes werden nicht auf Horizon-Schemes gemappt
(die gibt es nicht), sondern aufgelöst in konkrete Hex-Werte pro Section:

| Shrine-Scheme | Hintergrund | Vordergrund | Horizon-Umsetzung |
|---|---|---|---|
| `background-1` | `#FBF9F5` | `#1C1A17` | globale Palette (Default, kein Override) |
| `background-2` | `#F2EDE5` | `#1C1A17` | `background_color: "#F2EDE5"` an der Section |
| `inverse` | `#1C1A17` | `#FBF9F5` | `background_color: "#1C1A17"` (Kontrast automatisch) |
| `accent-1` | `#1C1A17` | `#FBF9F5` | wie `inverse` |
| `accent-2` | `#7A3B1E` | `#FBF9F5` | `background_color: "#7A3B1E"` |

Das ist kein Nachteil: das Ergebnis ist identisch, nur die Pflege läuft über
Section-Farben statt über Scheme-Namen.

### 1.2 `_blocks` kommt **nicht** von GemPages — und ist leer

`_blocks` ist Shopifys eigener Container für freistehende Theme-Blocks.
Horizon hat die Section selbst: `horizon/sections/_blocks.liquid`. Es gibt
drei Instanzen im Live-Theme (2× `index.json`, 1× `header-group.json`) —
**alle drei ohne Inhalt** (`"settings": {}`, keine Blocks). Da ist nichts zu
portieren.

Der einzige echte Theme-Block in Shrine ist
`blocks/ai_gen_block_1554822.liquid` („Die 5 Bestseller Produkte nebeneinander
mit name und preis"). Er wird **von keinem Template referenziert** und ist
damit tot. Siehe Frage 2 unten.

### 1.3 Die GemPages-Templates sind echte Shrine-Templates, keine GemPages-Seiten

`index.gem-1775335711-template.json`, `index.gp-template-bk-default.json`,
`collection.gp-template-bk-default.json`, `product.gp-template-bk-default.json`
sind von GemPages **angelegte Backup-Kopien**, enthalten aber ausschließlich
native Shrine-Sections (slideshow, featured-collection, image-with-text,
featured-product, testimonials bzw. main-product). Sie sind technisch
portierbar. Die Frage ist nur, ob du sie brauchst — siehe Frage 2.

Echte GemPages-Inhalte stecken dagegen in den `apps`-Sections (App-Embed-Blocks)
auf `page.json`, `page.indoor.json` und den Produktseiten. Die liegen in der
App, nicht im Theme — dazu Frage 2.

---

## 2. Bestandsaufnahme in Zahlen

| | Shrine⁺ 1.3.5 (Quelle) | Horizon 4.3.0 (Ziel, Lieferzustand) |
|---|---|---|
| sections | 79 (+2 group.json) | 42 (+2 group.json) |
| blocks | 1 (ungenutzt) | 95 (46 öffentlich, 49 privat `_*`) |
| snippets | 72 | 144 |
| assets | 105 | 125 |
| templates | 32 | 13 |
| layout | 6 (1 echt + 5 GemPages) | 2 |
| locales | 52 (de.json vorhanden) | 57 (de.json + de.schema.json vorhanden) |

Von Shrines 79 Sections sind **44 tatsächlich in Templates verwendet**,
35 liegen ungenutzt im Theme. Das reduziert den Nachbau erheblich:

**Ungenutzt und damit nicht zu bauen** (⏭️): `bundle-deals`, `pricing-table`,
`promo-popup`, `scroll-to-top-btn`, `global-music-player`, `music-player`,
`collage`, `multicolumn`, `logo-list`, `image-banner`, `image-slider`,
`featured-blog`, `video`, `section-divider`, `page`, `custom-liquid`,
`iconic-rotating-bar-curve`, `gp-variant-selected`, 8× `tsapb-*`,
sowie die Cart-/Password-Hilfssections.

Vier davon stehen in deiner „musst du neu bauen"-Liste — `bundle-deals`,
`pricing-table`, `promo-popup`, `scroll-to-top-btn`. Alle vier sind im
Live-Theme **nicht eingesetzt**, und `promo-popup`, `scroll-to-top-btn` und
`global-music-player` sind in `settings_data.json` zusätzlich explizit
deaktiviert (`"mode": "disabled"`, `"enable_scroll_btn": false`,
`"enabled": false`). Ich baue sie daher nicht nach. Wenn du einen davon
willst, sag Bescheid.

---

## 3. Design-Tokens — Mapping Shrine → Horizon

### 3.1 Farben

| Shrine-Setting | Wert | Horizon-Ziel | Status |
|---|---|---|---|
| `colors_background_1` | `#FBF9F5` | `color_palette.background` | ✅ |
| `colors_text` | `#1C1A17` | `color_palette.foreground` | ✅ |
| `colors_background_2` | `#F2EDE5` | `color_palette.color2` (Flächen-/Linienton) | ✅ |
| `colors_accent_1` | `#1C1A17` | = foreground, Buttons/`inverse` | ✅ |
| `colors_accent_2` | `#7A3B1E` | `color_palette.color1`, Sale-Marker | ✅ |
| `colors_solid_button_labels` | `#FBF9F5` | `palette_primary_button_text` | ✅ |
| `colors_outline_button_labels` | `#1C1A17` | `palette_secondary_button_text` | ✅ |
| `sale_badge_color_scheme: accent-2` | `#7A3B1E` | `badge_sale_background_color` | ✅ |
| `sold_out_badge_color_scheme: background-1` | `#FBF9F5` | `badge_sold_out_background_color` | ✅ |
| `checkout_button_color` / `checkout_accent_color` | `#1C1A17` | Checkout-Branding (Shopify-Admin, nicht Theme) | ❓ Schritt in Shopify |

### 3.2 Schriften

| Shrine | Horizon | Status |
|---|---|---|
| `type_header_font: jost_n4` | `type_heading_font: jost_n4`, `type_accent_font: jost_n4` | ✅ |
| `type_body_font: assistant_n4` | `type_body_font: assistant_n4`, `type_subheading_font: assistant_n5` | ✅ |
| `heading_scale: 100`, `body_scale: 100` | Horizon hat keine Scale-Faktoren, sondern Größen pro Preset (`type_size_h1…h6`, `type_size_paragraph`) | ✅ |

Shrines Headline-Größen kommen nicht aus den Theme-Settings, sondern aus
`assets/solena-design.css`. Zweite Hürde: Shrine lief auf einem
62.5%-Root (1rem = 10px), Horizon auf dem Browser-Default (1rem = 16px).
Alle rem-Werte sind deshalb umgerechnet (Shrine-rem × 10 ÷ 16).

Horizons Größenleiter (`10, 12, 14, 16, 18, 20, 24, 32, 40, 48, 56, …`)
kennt Shrines Zwischenwerte nicht. Die Settings bekommen daher den nächsten
Leiterwert, die exakte Größe pinnt `solena-design.css` nach — damit bleibt
der Theme-Editor benutzbar und das Rendering trotzdem pixelgleich:

| Shrine | mobil | Desktop | Horizon-Preset | Setting | in CSS gepinnt |
|---|---|---|---|---|---|
| `.h0` | 32px | 52px | h1 | `type_size_h1: 48` | `2rem` → `3.25rem` |
| `.h1` | 28px | 38px | h2 | `type_size_h2: 40` | `1.75rem` → `2.375rem` |
| `.h2` | 22px | 28px | h3 | `type_size_h3: 32` | `1.375rem` → `1.75rem` |
| `.h3` | 19px | 22px | h4 | `type_size_h4: 24` | `1.1875rem` → `1.375rem` |
| `.h4` | 16px | 16px | h5 | `type_size_h5: 16` | `1rem` |
| `.h5` | 14px | 14px | h6 | `type_size_h6: 14` | `0.875rem` |
| Body | 15px | 15px | paragraph | `type_size_paragraph: 16` | `0.9375rem` |

`.hxl` (64px) kommt in keinem Live-Template vor und entfällt.

Zusätzlich global, alles in `solena-design.css` gepinnt: alle Headlines
`font-weight: 400`, `letter-spacing: -0.01em` (h1 ab 750px `-0.02em`),
`line-height: 1.14` (h1: 1.08); Body `line-height: 1.7`.

### 3.3 Form, Abstand, Button, Card

| Shrine | Wert | Horizon | Status |
|---|---|---|---|
| `page_width` | 1600 | `page_width: "wide"` + CSS-Override `--wide-page-width: 100rem` (= 1600px bei 16px-Root) | ✅ |
| `buttons_radius` | 0 | `button_border_radius_primary: 0`, `…_secondary: 0`, `pills_border_radius: 0` | ✅ |
| `buttons_border_thickness` | 1 | `secondary_button_border_width: 1`, `primary_…: 0` | ✅ |
| `inputs_radius` | 0 | `inputs_border_radius: 0` | ✅ |
| `media_radius` | 2 | `product_corner_radius: 2`, `card_corner_radius: 2` | ✅ |
| `card_corner_radius` | 2 | `card_corner_radius: 2` | ✅ |
| `badge_corner_radius` | 40 | `badge_corner_radius: 100` (Pille, s. CSS `999px`) | ✅ |
| `badge_position` | `top left` | `badge_position: "top-left"` | ✅ |
| `variant_pills_radius` | 0 | `variant_button_radius: 0`, `variant_swatch_radius: 0` | ✅ |
| `spacing_grid_horizontal` | 24 | `columns_gap: 24` pro Grid-Section | ✅ |
| `spacing_grid_vertical` | 40 → CSS-Override 56 | `rows_gap: 56` pro Grid-Section | ✅ |
| `spacing_sections` | 0 | Section-Padding pro Section (Horizon hat kein globales Section-Gap) | ✅ |
| alle `*_shadow_*` | 0 | `popover_drop_shadow: false`, keine Schatten | ✅ |
| `cart_type` | `drawer` | `cart_type: "drawer"` | ✅ |
| `enable_cart_discount` | true | `show_add_discount_code: true` | ✅ |
| `show_cart_note` | false | `show_cart_note: false` | ✅ |
| `show_cart_payment_badges` | true | Payment-Icons-Block im Cart-Drawer | ✅ |
| `predictive_search_enabled` + `_show_price` | true | Horizon: immer an, Preis über Predictive-Search-Blocks | ✅ |
| `logo_width` | 150 | `logo_height: 36` / `logo_height_mobile: 28` (Horizon skaliert über Höhe) | ✅ |
| `logo`, `favicon` | `shopify://shop_images/…` | 1:1 übernehmbar | ✅ |
| `currency_code_enabled` | false | alle vier `currency_code_enabled_*: false` | ✅ |
| `disable_inspect` | false | kein Gegenstück in Horizon | ⏭️ |
| `enable_countdown_timer` + `timer_text` | true, „Kostenloser DHL-Versand inkl. Sendungsverfolgung" | Shrine-Feature im Cart-Drawer; Nachbau als eigener Horizon-Block | ✅ |
| `cart_progress_*`, `cart_upsell_1/2` | alle deaktiviert | — | ⏭️ nicht aktiv |

### 3.4 Die eigentliche Optik: `assets/solena-design.css`

Dein Live-Look kommt nicht aus Shrine, sondern aus **deinem eigenen**
1388-zeiligen Design-Layer `assets/solena-design.css` (19 Abschnitte,
in diesem Repo in `assets/` und über `layout/theme.liquid` zweifach geladen,
damit er nach den Section-Stylesheets greift).

Dasselbe gilt für `snippets/card-swatches.liquid` (152 Zeilen, Farbvokabular
mit ~90 Einträgen, Variantenerkennung) und die `ds-*`-Erweiterungen in
`snippets/card-product.liquid`. Laut Git-Historie dieses Repos
(`Farbwortschatz um die fehlenden Werte von Amber und Milo ergänzt`,
`Farberkennung aus den Varianten verbessert`, `Bestseller-Reihe zentriert`) ist
das **dein Code, nicht Shrines**.

**Annahme, unter der ich arbeite:** diese drei Dateien darf ich übernehmen und
auf Horizons CSS-Variablen umschreiben. Sie fallen nicht unter „kein
Shrine-Code". Konkret entsteht daraus:

- `horizon/assets/solena-design.css` — neu geschrieben gegen Horizons Tokens
  (`--color-foreground`, `--color-background`, `--opacity-*`,
  `--font-body--family`, …) statt Shrines (`--color-foreground` als
  RGB-Tripel, `--font-body-family`, `--ds-*`).
- `horizon/snippets/solena-card-swatches.liquid` — Logik 1:1, Markup an
  Horizons Card-Blocks angepasst.
- Das Topline-Layout (Titel + Produkttyp links, Rating rechts, Haarlinie,
  Preis, Swatches) wird in Horizon **nicht** per Snippet-Patch gebaut, sondern
  aus Horizon-Blocks komponiert: `_product-card-group` (row) → `group`
  (column) mit `product-title` + `text` → `review`; darunter `price` und der
  Swatch-Block. Die Haarlinie kommt aus den `border`-Settings des Group-Blocks.

Gemessene Kern-Werte, die in Horizon reproduziert werden müssen:

| Element | Soll-Wert |
|---|---|
| Buttons | 1.2rem, weight 500, `letter-spacing: .16em`, uppercase, `min-height: 5.4rem`, `padding: 0 3.6rem`, radius 0, Hover = `opacity .82` |
| Secondary Button | transparent, 1px Rahmen `rgba(fg,.22)`, Hover = volle Füllung |
| Eyebrow/Label | 1.1rem, `letter-spacing: .18em`, uppercase, weight 500 |
| Header | 1.8rem Padding oben/unten, 1px Unterkante `rgba(fg,.12)`, Logo links / Navigation zentriert / Icons rechts |
| Nav-Item | 1.25rem, `letter-spacing: .14em`, uppercase, weight 500, Hover `opacity .6`, aktiv = Unterstrich |
| Announcement Bar | `min-height: 3.8rem`, 1.1rem, `letter-spacing: .18em`, uppercase |
| Produktkarte | Bild (radius 2) → Topline → Haarlinie 1px → Preis 1.6rem → Swatches 1.8rem Quadrate |
| Karten-Titel | 1.7rem mobil / 1.9rem ab 990px, weight 500 |
| Produkt-Grid | `column-gap: 2.4rem`, `row-gap: 5.6rem` (mobil 1.2 / 3.2) |
| Badge | Pille `999px`, 1.15rem, weight 500, oben links, 1.2rem Abstand |
| Accordion | Haarlinien oben/unten, `summary` 2.2rem Padding, Titel 1.6rem weight 500 |
| Footer | 1px Oberkante, `padding-top: 6.4rem`, Block-Headings 1.1rem `letter-spacing: .2em` uppercase, Links 1.4rem gedämpft |
| Gedämpfter Text | `rgba(foreground, .58)` |
| Haarlinie | `rgba(foreground, .12)`, stark: `.22` |
| Flächenton | `rgba(foreground, .035)` |
| Section-Rhythmus | 9.6rem Desktop / 6.4rem mobil |
| Easing | `cubic-bezier(.22,.61,.36,1)` |

---

### 3.5 Was Etappe 2 konkret angelegt hat

| Datei | Was drin steht |
|---|---|
| `horizon/config/settings_data.json` | neu geschrieben, 129 von 133 Settings gesetzt. Zusätzlich als Preset `Solena` abgelegt, damit du jederzeit auf diesen Stand zurücksetzen kannst. |
| `horizon/assets/solena-design.css` | der Design-Layer, Abschnitte 1–5 (Tokens, Typographie, Buttons, Formulare, Form, Seitenrhythmus). Die Komponenten-Abschnitte 6–17 kommen mit den Etappen 3–8 dazu. |
| `horizon/layout/theme.liquid` | lädt `solena-design.css` zweimal — im `<head>` nach `color-palette` und erneut am Ende von `<body>`. Horizon gibt die Styles seiner Sections und Blocks als `{% style %}` im Body aus; ohne die zweite Einbindung verliert der Layer jeden Gleichstand bei der Spezifität. Dazu `microsoft-clarity`. |
| `horizon/layout/password.liquid` | dieselben zwei Einbindungen |
| `horizon/snippets/color-palette.liquid` | gibt die Palettenfarben zusätzlich einzeln als `--color-palette-background/-foreground/-color1/-color2` aus, damit der Design-Layer den Akzent- und Flächenton nicht hart verdrahten muss |
| `horizon/snippets/microsoft-clarity.liquid` | aus dem Shrine-Theme übernommen (dein eigener Code, Projekt-ID `yn9k3648hz`) |
| `tools/settings.py` | generiert `settings_data.json` aus der Token-Zuordnung und validiert jede ID und jeden Options-Wert gegen `settings_schema.json`. Eine falsche ID bricht ab, statt stumm im Theme zu landen. |
| `tools/verify.py` | das Prüfskript aus Abschnitt 7 |

Zwei Dinge, die bewusst nicht aus den Settings kommen:

- **Seitenbreite.** Horizons `wide` liefert `150rem` (2400px bei 16px-Root).
  Shrine stand auf 1600px. Der Design-Layer setzt
  `--wide-page-width: 100rem`.
- **Karten-Hover.** Shrine zoomte das Kartenbild über 0.9s auf `scale(1.04)`.
  Keiner von Horizons vier Effekten (`lift`, `scale`, `subtle-zoom`, `none`)
  trifft das, deshalb steht `card_hover_effect` auf `none` und der Zoom wird
  in Etappe 4 exakt nachgebaut.

## 4. Mapping-Tabelle — Sections (live genutzte)

### 4.1 Header-Gruppe

| Shrine | Live-Einstellung | Horizon-Umsetzung | Status |
|---|---|---|---|
| `announcement-bar` + Block `announcement` | „Kostenloser DHL-Versand inkl. Sendungsverfolgung", zentriert, Scheme `inverse` | `sections/header-announcements.liquid` + Block `_announcement`, `background_color: #1C1A17` | ⬜ |
| `horizontal-ticker` (3 Text-Blocks) | **deaktiviert** | `sections/marquee.liquid` + `text`-Blocks, `disabled: true` — 1:1 inkl. Deaktivierung | ⬜ |
| `header` | sticky `always`, Linie, Logo `middle-left`, Menü `main-menu`, aktiver Link hervorgehoben, Mobile-Logo zentriert, Padding 20/20 | `sections/header.liquid` + `blocks/_header-logo`, `_header-menu`; Layout `logo-left menu-center icons-right` per CSS | ⬜ |
| `_blocks` (leer) | — | ⏭️ leer, nichts zu portieren |  |

### 4.2 Footer-Gruppe

| Shrine | Live-Einstellung | Horizon-Umsetzung | Status |
|---|---|---|---|
| `apps` (leer) | GemPages-Platzhalter | ❓ siehe Frage 2 | ❓ |
| `footer` Block `link_list` „Menü" | `main-menu`, 3 Spalten | `blocks/menu.liquid` in `sections/footer.liquid` | ⬜ |
| `footer` Block `link_list` „Rechtliches" | Menü `rechtliches`, 4 Spalten | `blocks/menu.liquid` | ⬜ |
| `footer` Block `text` „Kontakt" | Langer RTE-Text mit Service-Zeiten, Mail, Anschrift Graz | `blocks/text.liquid` | ⬜ |
| `footer` Sprachwähler an, Länderwähler aus | `enable_language_selector: true` | `sections/footer-utilities.liquid` | ⬜ |
| `footer` Payment-Icons an | `payment_enable: true` | `blocks/payment-icons.liquid` | ⬜ |
| `footer` Social aus, Policy aus, Follow-on-Shop aus | | entsprechende Blocks weglassen | ⬜ |

### 4.3 Startseite (`index.json`)

| # | Shrine-Section | Inhalt | Horizon-Umsetzung | Status |
|---|---|---|---|---|
| 1 | `slideshow` (1 Slide) | „Entdecke Solena" / „Weil Design keine Ausnahme sein sollte" / Button „Finde jetzt deinen Stil" → `/collections/all`; full_bleed, large, Counter, Overlay 10 %, Text links mittig, kein Textkasten | `sections/slideshow.liquid` Preset `slideshow_full_frame` + Block `_slide` mit `text`/`button` | ⬜ |
| 2 | `collection-list` (5 Blocks) | Titel „Collections", h1, square, 5 Spalten Desktop / 2 mobil, Swipe mobil; Kollektionen: hangeleuchten, deckenleuchten, tischleuchten, wandleuchten, outdoor-leuchten; Padding 72/88 | `sections/collection-list.liquid` Preset `collections_grid` + `_collection-card`-Blocks | ⬜ |
| 3 | `featured-collection` | „Solena Bestseller", h0, Kollektion `bestseller`, 16 Produkte, 5 Spalten / 2 mobil, Rating an, Zweitbild an, Padding 36/36 | `sections/product-list.liquid` Preset `products_grid` + `_product-card` mit `_product-card-gallery`, `product-title`, `text`(Typ), `review`, `price`, Swatches | ⬜ |
| 4+5 | `_blocks` ×2 | leer | ⏭️ nichts zu portieren | |
| 6 | `image-with-text` (3 Blocks) | Bild + „Ein Statement für dein Zuhause" (h2) / „Wo nordische Ruhe auf Design trifft" / Button „Mehr lesen" → `/pages/uber-uns`; large, Bild schmal, Text zuerst, Section-Scheme `background-2`, Padding 96/96 | `sections/media-with-content.liquid` Preset `editorial`, `background_color: #F2EDE5` | ⬜ |
| 7 | `featured-product` (7 Blocks) | **deaktiviert**, kein Produkt gesetzt | `sections/featured-product.liquid`, `disabled: true` — 1:1 inkl. Deaktivierung | ⬜ |
| 8 | `featured-collection` | „Trends 2026", h1, Kollektion `trends`, 4 Produkte, 4 Spalten, „Alle ansehen" an | `sections/product-list.liquid` wie #3 | ⬜ |
| 9 | `testimonials` (3 Blocks) | „Zufriedenheit ist unsere Voraussetzung", h2, 3 Spalten, zentriert, Sterne an, Quotes an; Julia S. / Thomas W. / Andrea Z. mit deutschen Texten | **Neubau**: `sections/section.liquid` + neuer Theme-Block `solena-testimonial` (Rahmen-Karte, Titel, Text, Autor, Sterne) | ⬜ |

### 4.4 Produktseite (`product.json`)

Die Section `main-product` hat 14 Block-Instanzen (nicht 15 — der 15. war ein
Judge.me-Preview-Badge, der im Export vom 16:28 Uhr nicht mehr drin ist).

| # | Shrine-Block | Status live | Horizon-Umsetzung | Status |
|---|---|---|---|---|
| 1 | App: `iconic-blocks/iconic-review-summary-first` | aktiv — Trustpilot-Zeile, 4.5 Sterne, „Über 35.000 Bewertungen", Link `at.trustpilot.com`, grünes Badge `#00b67a` | App-Block. Horizon erlaubt `@app` in `product-information` → **App neu einbinden** (siehe §6). Fallback-Nachbau als `solena-review-summary`-Block, falls du willst | ❓ |
| 2 | `title` | aktiv, h2, links, nicht uppercase | `blocks/product-title.liquid` | ⬜ |
| 3 | App: `iconic-blocks/iconic-benefits-first` | aktiv — 4 Benefits aus Metafeldern `custom.selling_point_1…4`, Icon `bi bi-check2`, BG `#fbf9f5`, radius 10 | App-Block → neu einbinden; Fallback-Nachbau `solena-benefits` liest dieselben Metafelder | ❓ |
| 4 | App: `iconic-review-summary-first` (2.) | aktiv, Dummy-Text „20,921 reviews" | wirkt wie Überrest. ❓ brauchst du den zweiten? | ❓ |
| 5 | `price` | aktiv, `layout: price_first` | `blocks/price.liquid` | ⬜ |
| 6 | `emoji_benefits` | **deaktiviert** | ⏭️ |  |
| 7 | `variant_picker` | aktiv, `picker_type: button`, keine Swatches | `blocks/variant-picker.liquid` (`variant_button_width: equal-width-buttons`) | ⬜ |
| 8 | `quantity_selector` (Bundle & Save) | **deaktiviert** | ⏭️ |  |
| 9 | `buy_buttons` | aktiv, dynamische Checkout-Buttons an, uppercase | `blocks/buy-buttons.liquid` + `quantity`, `add-to-cart`, `accelerated-checkout` | ⬜ |
| 10 | `sticky_atc` | aktiv, `after_scroll`, „Zum Warenkorb", Preis + Badge | **Neubau**: Theme-Block `solena-sticky-atc` (Horizon hat kein Gegenstück) | ⬜ |
| 11 | `payment_badges` | aktiv | `blocks/payment-icons.liquid` | ⬜ |
| 12 | `collapsible_tab` „Produktbeschreibung" | aktiv, Icon `clipboard`, `{{ product.description }}` | `blocks/accordion.liquid` + `_accordion-row` mit `product-description` | ⬜ |
| 13 | `collapsible_tab` „Versandinformationen" | aktiv, Icon `truck`, deutscher Text (DHL, 1–2 / 3–7 Werktage) | `blocks/accordion.liquid` + `_accordion-row` | ⬜ |
| 14 | `collapsible_tab` „Rückgabeinformationen" | aktiv, Icon `return`, deutscher Text (30 Tage) | `blocks/accordion.liquid` + `_accordion-row` | ⬜ |

Section-Settings `main-product`: Galerie `thumbnail_slider`, Medien links,
`media_size: large`, Zoom `lightbox`, Sticky-Info an, Thumbnails mobil an,
Padding 32/88 → `_product-media-gallery` mit `media_presentation: thumbnail`,
`thumbnail_position: bottom`, `zoom: true`; `_product-details` mit
`sticky_details_desktop: true`.

Weitere Sections auf `product.json`:

| Shrine-Section | Status live | Horizon-Umsetzung | Status |
|---|---|---|---|
| `related-products` | **deaktiviert** | `sections/product-recommendations.liquid`, `disabled: true` | ⬜ |
| `apps` ×2 (leer) | aktiv, leer | ❓ Frage 2 | ❓ |
| `rich-text` (heading + text) | „Über Uns" h1 + langer Markentext, zentriert, Scheme `background-2`, full width, Padding 88/88 | `sections/section.liquid` Preset `rich_text_section` + `text`-Blocks, `background_color: #F2EDE5` | ⬜ |
| `comparison-table` (3 Rows) | „Was uns ausmacht" h0; Zeilen: „Persönlicher Kundenservice", „Designerlampen zum fairen Preis", „30 Tage Geld-zurück-Garantie"; uns ✓ / Andere ✗; Häkchen `#53af01`, Layout `table_second`, Logo-Breite 90/60 | **Neubau**: `sections/section.liquid` + Theme-Block `solena-comparison-table` mit Row-Sub-Blocks | ⬜ |
| `apps` (Judge.me `review_widget`) | aktiv, `max_width: 700`, echte Daten | App-Block → Judge.me in Horizon neu einbinden (§6) | ❓ |
| `apps` (leer) | aktiv, leer | ❓ Frage 2 | ❓ |
| `collapsible-content` (8 Rows) | „Häufig gestellte Fragen" h2, zentriert, Container-Scheme `background-2`; 8 deutsche FAQ-Einträge (Versanddauer, Versandkosten, Tracking, Rückgabe, Zahlarten, Sicherheit, Daten, Kontakt) | `sections/section.liquid` Preset `faq_section` + `blocks/accordion.liquid` + 8× `_accordion-row` | ⬜ |

### 4.5 Übrige Templates

| Template | Shrine-Sections | Horizon-Umsetzung | Status |
|---|---|---|---|
| `collection.json` | `main-collection-banner`, `main-collection-product-grid` | `sections/main-collection.liquid` + `filters` + `_product-card`; Banner als `section.liquid` davor | ⬜ |
| `collection.alle.json` | Banner (deaktiviert), `rich-text` (3 Blocks), Grid | wie oben + `section.liquid` | ⬜ |
| `collection.indoor.json` | Banner, Grid | wie `collection.json` | ⬜ |
| `cart.json` | `main-cart-items`, `main-cart-footer` (3 Blocks), 2× `featured-collection` (1 deaktiviert), `newsletter` (deaktiviert) | `sections/main-cart.liquid` (`_cart-title`, `_cart-products`, `_cart-summary`) + `product-list` | ⬜ |
| `search.json` | `main-search`, `newsletter` | `sections/search-header.liquid` + `search-results.liquid` | ⬜ |
| `404.json` | `main-404` (deaktiviert), `newsletter` (deaktiviert), `image-with-text` | `sections/main-404.liquid` + `media-with-content.liquid` | ⬜ |
| `page.about-us.json` | `main-page`, `multirow` (3 Rows), 2× `rich-text` | `main-page.liquid` + 3× `section.liquid` (Preset `image_with_text`) + `rich_text_section` | ⬜ |
| `page.faq.json` | `main-page` (deaktiviert), `collapsible-content` (8 Rows), `rich-text` (3 Blocks) | `section.liquid` Preset `faq_section` + `accordion` | ⬜ |
| `page.contact.json` | `main-page` (deaktiviert), `rich-text`, `contact-form`, `rich-text` | `main-page.liquid` + `section.liquid` Preset `contact_form` | ⬜ |
| `page.track-order.json` | `main-page` (deaktiviert), `track-order`, `image-with-text` (deaktiviert) | **Neubau**: Theme-Block `solena-track-order` (Bestellnummer + E-Mail → `/account/login`) | ⬜ |
| `page.json`, `page.indoor.json` | `main-page` (deaktiviert), 2× `apps`, `featured-collection` | ❓ Frage 2 (GemPages) | ❓ |
| `blog.json`, `article.json` | `main-blog`/`main-article` + `newsletter` | `main-blog.liquid` / `main-blog-post.liquid` + `section.liquid` Preset `email_signup` | ⬜ |
| `list-collections.json` | `main-list-collections`, `newsletter` | `main-collection-list.liquid` | ⬜ |
| `password.json` | `email-signup-banner` (3 Blocks) | `sections/password.liquid` + `email-signup` | ⬜ |
| `customers/*.json` (7) | `main-account`, `main-login`, … | Horizon rendert Kundenseiten über `layout/theme.liquid` + Shopify-Defaults; es gibt **keine** `templates/customers/*` in Horizon 4.3.0 | ⏭️ Horizon-Standard, kein Nachbau nötig |
| `gift_card.liquid` | Shrine-Version | Horizon hat eigene `templates/gift_card.liquid` | ⏭️ Horizon-Standard |
| `index.gem-*.json`, `*.gp-template-bk-default.json` | GemPages-Backups | ❓ Frage 2 | ❓ |
| `product.premium-1…8.json` | 8 Varianten der Produktseite | ❓ Frage 1 | ❓ |

### 4.6 Sections aus deiner „neu bauen"-Liste — tatsächlicher Bedarf

| Section | Live verwendet? | Entscheidung | Status |
|---|---|---|---|
| `testimonials` | ja (`index.json`, Premium-Templates) | neu bauen als Theme-Block | ⬜ |
| `comparison-table` | ja (`product.json`, alle Premium-Templates) | neu bauen als Theme-Block | ⬜ |
| `track-order` | ja (`page.track-order.json`) | neu bauen als Theme-Block | ⬜ |
| `icon-bar` | nur in `product.gp-template-bk-default.json` | Horizon hat `section.liquid` Preset `icons_with_text` → **kein Neubau nötig** | ⬜ |
| `comparison-slider` | nur in `product.gp-template-bk-default.json` | Horizon-Block `comparison-slider` vorhanden → kein Neubau | ⬜ |
| `results` | nur in `product.gp-template-bk-default.json` | ❓ hängt an Frage 1/2 | ❓ |
| `vertical-ticker` | nur in `product.gp-template-bk-default.json` | ❓ hängt an Frage 1/2 | ❓ |
| `bundle-deals` | **nein** | ⏭️ nicht im Live-Theme eingesetzt | |
| `pricing-table` | **nein** | ⏭️ nicht eingesetzt | |
| `promo-popup` | **nein**, zusätzlich `mode: disabled` | ⏭️ | |
| `scroll-to-top-btn` | **nein**, zusätzlich `enable_scroll_btn: false` | ⏭️ | |
| `sticky_atc` (Produkt-Block) | ja | neu bauen als Theme-Block | ⬜ |
| Cart-Countdown (`enable_countdown_timer`) | ja, Text „Kostenloser DHL-Versand…" | neu bauen als Theme-Block im Cart-Drawer | ⬜ |

---

## 5. Horizon-Gegenstücke — Korrekturen zu deiner Liste

Deine Entsprechungsliste stimmt überwiegend. Drei Abweichungen:

| Deine Annahme | Tatsächlich in Horizon 4.3.0 |
|---|---|
| `featured-collection` → `product-list` **oder** `featured-collection`-Block | `blocks/featured-collection.liquid` ist ein **Block für den Footer/Group-Kontext**, kein Ersatz für eine Produkt-Grid-Section. Für die Startseite ist `sections/product-list.liquid` (Presets `products_grid` / `products_carousel` / `products_editorial`) das richtige Gegenstück. |
| `collapsible-content` → `accordion`-Block | Richtig, aber `accordion` ist ein **Block**, keine Section. Er braucht einen Träger: `sections/section.liquid` mit Preset `faq_section`. |
| `rich-text`/`multirow` → `section` + `group`/`text` | Richtig. `section.liquid` hat dafür die Presets `rich_text_section` und `image_with_text`. |

Zusätzliche Horizon-Presets, die Arbeit sparen und die du noch nicht auf dem
Schirm hattest: `icons_with_text` (→ `icon-bar`), `image_compare`
(→ `comparison-slider`), `multicolumn`, `split_showcase`, `contact_form`,
`email_signup`, `video_section`, `pull_quote`, `large_logo`.

---

## 6. Apps — was in Shopify neu eingebunden werden muss

Aus `config/settings_data.json → current.blocks` und den `apps`-Sections:

| App | Was sie im Live-Theme tut | In Horizon nötig |
|---|---|---|
| **Judge.me Reviews** | App-Embed `judgeme_core` (aktiv), `cart_drawer_widget` (aktiv, `review-widget`), `reviews_tab` (deaktiviert), `popup_widget` (deaktiviert); Review-Widget-Block auf der Produktseite | App-Embed in Horizon aktivieren, Review-Widget-Block in `product-information` bzw. eine eigene Section einsetzen |
| **Iconic Blocks** | App-Embed aktiv; Blocks `iconic-review-summary-first` (2×) und `iconic-benefits-first` auf der Produktseite | App-Embed aktivieren, drei Blocks neu platzieren. Horizon erlaubt `@app` in `product-information` |
| **Google Ads Pixel by Nabu** | App-Embed `script-block` (aktiv) | App-Embed aktivieren |
| **GemPages** | 5 eigene Layouts (`theme.gempages.*`, `theme.gem-layout-none`), `snippets/gp-head.liquid`, `assets/gp-global.css`, `sections/gp-variant-selected.liquid`, `apps`-Sections, 4 Backup-Templates | ❓ Frage 2 |
| **Vitals** | 8 `tsapb-*`-Sections („❤️ Value Icons", „❤️ Testimonials", …) — **keine davon in einem Template verwendet** | nur dokumentiert; wenn du Vitals-Sections brauchst, legt die App sie nach Installation selbst neu an |
| **Microsoft Clarity** | `snippets/microsoft-clarity.liquid`, eingebunden in `layout/theme.liquid` | eigener Code, wird nach Horizon übernommen (32 Zeilen) |
| Weitere Shrine-Snippets mit App-Bezug | `bucks-cc.liquid`, `cjpod.liquid`, `kiwiSizing.liquid` | ❓ gehören zu Apps (Currency Converter, CJ Dropshipping, Kiwi Sizing) — sag mir, welche aktiv sind |

---

## 7. Qualitätssicherung

Zwei Werkzeuge laufen nach jeder Etappe:

| Prüfung | Werkzeug | Stand nach Etappe 2 |
|---|---|---|
| Liquid- und Schema-Validierung | `shopify theme check` (CLI 5.0.0) | 358 Dateien, **0 Errors, 6 Warnings** — die sechs sind `UnusedDocParam` aus Horizons Lieferzustand, unverändert |
| JSON valide, keine toten Referenzen, Block-Architektur | `tools/verify.py` (eigenes Skript) | 283 Liquid-Dateien, 16 JSON-Dokumente, **0 Fehler, 0 Warnungen** |
| Theme-Settings gegen das Schema | `tools/settings.py` | 129 von 133 Settings gesetzt, 4 bewusst auf Schema-Default |

`tools/verify.py` prüft sechs Dinge, die `theme check` nicht abdeckt:

1. Alle JSON-Templates und Section-Groups parsen — inklusive der `/* */`- und
   `//`-Kommentare, die Shopify dort erlaubt.
2. Jede `{% render %}`-Referenz zeigt auf ein existierendes Snippet
   (`{% doc %}`-Beispiele zählen nicht).
3. Jede `| asset_url`-Referenz zeigt auf eine Datei in `assets/`.
4. Jeder Section-Type in einem Template existiert in `sections/`.
5. Jeder Block-Type existiert in `blocks/` **und** ist im Schema seines
   Elternteils erlaubt — `@theme`, `@app` und statisch per
   `{% content_for 'block' %}` gesetzte Blocks werden dabei aufgelöst.
6. Jeder `t:`-Übersetzungsschlüssel in einem Schema existiert in
   `locales/en.default.schema.json`.

| Noch offen | Wann |
|---|---|
| Deutsche Texte, `locales/de.json` pflegen | Etappe 8 |
| Mobil-Ansicht prüfen | Etappe 8, per Playwright gegen `shopify theme dev`, falls Store-Zugang vorhanden; sonst Breakpoint-Review im Code |

## 8. Was ich bewusst offen lasse

| Punkt | Grund |
|---|---|
| `templates/customers/*` | Horizon 4.3.0 liefert keine Customer-Templates; Shopify rendert sie aus `layout/theme.liquid`. Ein Nachbau wäre gegen Horizons Architektur. |
| `gift_card.liquid` | Horizon hat eine eigene Version. Shrines Variante zu übernehmen hieße Shrine-Code kopieren. |
| 8× `tsapb-*` (Vitals) | App-Sections, nicht Theme-Code. Werden von der App nach Installation neu angelegt. |
| `bundle-deals`, `pricing-table`, `promo-popup`, `scroll-to-top-btn`, `global-music-player` | In keinem Template verwendet; drei davon zusätzlich per Setting deaktiviert. |
| `blocks/ai_gen_block_1554822.liquid` | Von keinem Template referenziert. Siehe Frage 2. |
| 30 weitere ungenutzte Shrine-Sections | nicht Teil der Live-Optik |
| `disable_inspect` | kein Gegenstück in Horizon; war ohnehin `false` |
| Checkout-Farben (`checkout_accent_color`, `checkout_button_color`) | gehören ins Shopify-Checkout-Branding, nicht ins Theme |

---

## 9. Deine Entscheidungen

| Frage | Entscheidung | Folge fuer den Port |
|---|---|---|
| `product.premium-1` bis `premium-8` | **alle acht 1:1** | Acht eigene Horizon-Templates, jedes mit seinen eigenen Bildern und Texten. Dadurch werden `icon-bar`, `comparison-slider`, `results` und `vertical-ticker` doch gebraucht (sie stecken in `product.gp-template-bk-default`), siehe naechste Zeile. |
| GemPages | **alles mitnehmen, was geht** | Die vier Backup-Templates werden als Horizon-Templates nachgebaut. Die `apps`-Sections entstehen als `_blocks`-Sections mit `@app`-Aufnahme an denselben Stellen, damit du die GemPages-Bloecke in Horizon nur neu einsetzen musst. Die GemPages-Layouts (`theme.gempages.*`) werden als Horizon-Layouts neu geschrieben, nicht von Shrine kopiert. `gp-head.liquid` und `gp-global.css` sind App-Dateien, keine Shrine-Dateien, und werden uebernommen. |
| Zweite Trustpilot-Zeile | **nur die erste** | Die zweite `iconic-review-summary-first`-Instanz mit dem Platzhaltertext „20,921 reviews" entfaellt. |

Aus der ersten Entscheidung folgt, dass `results` und `vertical-ticker`
doch nachgebaut werden muessen — beide kommen in
`product.gp-template-bk-default.json` vor. `icon-bar` und
`comparison-slider` decken Horizons Presets `icons_with_text` und
`image_compare` ab.

### Noch offen

| Punkt | Was ich brauche |
|---|---|
| Logo-Hoehe | Shrine stellte die Logo**breite** auf 150px, Horizon skaliert ueber die **Hoehe**. Ich habe 38px Desktop / 30px mobil gesetzt. Das ist ein Richtwert — bitte in Shopify nachziehen, sobald das Theme in der Vorschau laeuft. |
| `bucks-cc.liquid`, `cjpod.liquid`, `kiwiSizing.liquid` | Drei App-Snippets aus Shrine (Currency Converter, CJ Dropshipping, Kiwi Sizing). Sag mir, welche davon aktiv sind, dann binde ich sie ein. |

## 10. Was du anschließend selbst in Shopify machen musst

(wird bis zur Lieferung ergänzt)

1. Theme-ZIP unter **Online Store → Themes → Add theme → Upload zip file** hochladen.
2. Logo und Favicon neu zuweisen, falls die `shopify://shop_images/…`-Referenzen
   nicht automatisch greifen.
3. Menüs prüfen: `main-menu` und `rechtliches` müssen unter
   **Navigation** unverändert existieren.
4. App-Embeds aktivieren: Judge.me, Iconic Blocks, Google Ads Pixel by Nabu
   (+ ggf. GemPages, Vitals).
5. App-Blocks neu platzieren: Judge.me Review-Widget, Iconic Review-Summary,
   Iconic Benefits.
6. Checkout-Branding (`#1C1A17`) unter **Settings → Checkout → Branding** setzen.
7. Produkt-Metafelder `custom.selling_point_1…4` prüfen — der Benefits-Block
   liest sie aus.
8. Erst nach Abnahme auf der Vorschau veröffentlichen.

---

## 11. Fortschritt

| Etappe | Inhalt | Status |
|---|---|---|
| 1 | Analyse beider Themes, PORT.md | ✅ |
| 2 | Design-Tokens: Farben, Schriften, Abstände, Button- und Card-Stile | ✅ |
| 3 | Header, Footer, Announcement Bar | ⬜ |
| 4 | Startseite | ⬜ |
| 5 | Produktseite inkl. aller Blöcke | ⬜ |
| 6 | Collection, Cart, Search, 404, About, FAQ, Contact | ⬜ |
| 7 | Fehlende Sections als eigene Theme-Blocks | ⬜ |
| 8 | Feinschliff per CSS, Theme Check, Mobil-Prüfung | ⬜ |
| 9 | ZIP-Lieferung | ⬜ |
