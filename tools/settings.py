"""Builds horizon/config/settings_data.json from the Solena token mapping.

Every id is validated against config/settings_schema.json so a typo cannot
slip into the theme. Ids left out keep their schema default; they are
reported so the mapping stays reviewable.
"""
import json, os, sys

HORIZON = sys.argv[1]
SCHEMA = os.path.join(HORIZON, 'config', 'settings_schema.json')

BG   = '{{ settings.color_palette.background }}'   # #FBF9F5
FG   = '{{ settings.color_palette.foreground }}'   # #1C1A17
C1   = '{{ settings.color_palette.color1 }}'       # #7A3B1E  (Shrine accent-2)
C2   = '{{ settings.color_palette.color2 }}'       # #F2EDE5  (Shrine background-2)

MAP = {
    # --- Logo & Favicon -----------------------------------------------------
    'logo': 'shopify://shop_images/hf_20260910_063833_7ae1e3de-0e28-47b6-8e9f-050e1a4662ee-removebg-preview.png',
    'favicon': 'shopify://shop_images/image.png',
    # Shrine stellte die Logobreite auf 150px. Horizon skaliert ueber die
    # Hoehe, daher ein Richtwert, der in Shopify nachgezogen werden kann.
    'logo_height': 38,
    'logo_height_mobile': 30,

    # --- Farben -------------------------------------------------------------
    # Shrine: colors_background_1 #FBF9F5 / colors_text #1C1A17
    #         colors_background_2 #F2EDE5 / colors_accent_2 #7A3B1E
    'color_palette': {
        'background': '#FBF9F5',
        'foreground': '#1C1A17',
        'color1': '#7A3B1E',
        'color2': '#F2EDE5',
    },
    'page_background_color': BG,
    'page_text_color': FG,

    # --- Seitenbreite -------------------------------------------------------
    # Shrine page_width 1600. Horizons 'wide' ist 150rem; solena-design.css
    # hebt --wide-page-width auf 160rem.
    'page_width': 'wide',

    # --- Schriften ----------------------------------------------------------
    'type_body_font': 'assistant_n4',
    'type_subheading_font': 'assistant_n5',
    'type_heading_font': 'jost_n4',
    'type_accent_font': 'jost_n4',

    # Groessen folgen Horizons Leiter; die exakten Shrine-Werte pinnt
    # solena-design.css nach.
    'type_size_paragraph': '16',          # Shrine 15px
    'type_line_height_paragraph': 'body-loose',

    'type_font_h1': 'heading', 'type_size_h1': '48',   # Shrine .h0  52px
    'type_line_height_h1': 'display-tight', 'type_letter_spacing_h1': 'heading-tight', 'type_case_h1': 'none',
    'type_font_h2': 'heading', 'type_size_h2': '40',   # Shrine .h1  38px
    'type_line_height_h2': 'display-tight', 'type_letter_spacing_h2': 'heading-tight', 'type_case_h2': 'none',
    'type_font_h3': 'heading', 'type_size_h3': '32',   # Shrine .h2  28px
    'type_line_height_h3': 'display-tight', 'type_letter_spacing_h3': 'heading-tight', 'type_case_h3': 'none',
    'type_font_h4': 'heading', 'type_size_h4': '24',   # Shrine .h3  22px
    'type_line_height_h4': 'display-tight', 'type_letter_spacing_h4': 'heading-tight', 'type_case_h4': 'none',
    'type_font_h5': 'heading', 'type_size_h5': '16',   # Shrine .h4  16px
    'type_line_height_h5': 'display-tight', 'type_letter_spacing_h5': 'heading-normal', 'type_case_h5': 'none',
    'type_font_h6': 'heading', 'type_size_h6': '14',   # Shrine .h5  14px
    'type_line_height_h6': 'display-tight', 'type_letter_spacing_h6': 'heading-normal', 'type_case_h6': 'none',

    # --- Animationen --------------------------------------------------------
    # Shrine kennt keine Seitenuebergaenge; der Bild-Zoom der Karte
    # (scale 1.04 ueber 0.9s) wird in solena-design.css exakt nachgebaut,
    # deshalb bleibt Horizons eigener Hover-Effekt aus.
    'page_transition_enabled': False,
    'transition_to_main_product': False,
    'add_to_cart_animation': False,
    'card_hover_effect': 'none',

    # --- Badges -------------------------------------------------------------
    'badge_position': 'top-left',
    'badge_corner_radius': 100,                # Pille, Shrine CSS: 999px
    'badge_sale_background_color': C1,         # Shrine sale_badge = accent-2
    'badge_sale_text_color': BG,
    'badge_sold_out_background_color': BG,     # Shrine sold_out = background-1
    'badge_sold_out_text_color': FG,
    'badge_font_family': 'body',
    'badge_text_transform': 'none',

    # --- Buttons ------------------------------------------------------------
    'palette_primary_button_background': FG,
    'palette_primary_button_text': BG,
    'palette_primary_button_border': FG,
    'primary_button_border_width': 0,
    'button_border_radius_primary': 0,
    'type_font_button_primary': 'body',
    'button_text_case_primary': 'uppercase',
    'palette_secondary_button_background': 'rgba(0,0,0,0)',
    'palette_secondary_button_text': FG,
    'palette_secondary_button_border': FG,
    'secondary_button_border_width': 1,
    'button_border_radius_secondary': 0,
    'type_font_button_secondary': 'body',
    'button_text_case_secondary': 'uppercase',
    'pills_border_radius': 0,

    # --- Warenkorb ----------------------------------------------------------
    'cart_type': 'drawer',
    'product_title_case': 'default',
    'cart_price_font': 'body',
    'auto_open_cart_drawer': True,
    'show_cart_note': False,
    'cart_note_open_by_default': False,
    'show_add_discount_code': True,
    'show_installments': True,
    'show_accelerated_checkout_buttons': True,
    'empty_cart_button_link': '/collections/all',
    'cart_thumbnail_border': 'none',
    'cart_thumbnail_border_radius': 2,

    # --- Drawer -------------------------------------------------------------
    'drawer_background_color': BG,
    'drawer_text_color': FG,
    'drawer_border_color': FG,

    # --- Icons --------------------------------------------------------------
    'icon_stroke': 'default',

    # --- Eingabefelder ------------------------------------------------------
    'palette_input_background': BG,
    'palette_input_text': FG,
    'palette_input_border': FG,
    'input_border_width': 1,
    'inputs_border_radius': 0,
    'type_preset': 'paragraph',

    # --- Popover & Modal ----------------------------------------------------
    'popover_background_color': BG,
    'popover_text_color': FG,
    'popover_border_radius': 0,
    'popover_border_color': FG,
    'popover_border_width': 1,
    'popover_drop_shadow': False,
    'popover_shadow_color': FG,

    # --- Preise -------------------------------------------------------------
    'currency_code_enabled_product_pages': False,
    'currency_code_enabled_product_cards': False,
    'currency_code_enabled_cart_items': False,
    'currency_code_enabled_cart_total': False,

    # --- Produktkarten ------------------------------------------------------
    # Shrine: enable_quick_add war auf allen Produktlisten aus.
    'quick_add': False,
    'mobile_quick_add': False,
    'quick_add_background': BG,
    'quick_add_text': FG,
    'show_second_image_on_hover': True,
    'product_card_carousel': False,

    # --- Suche --------------------------------------------------------------
    'product_corner_radius': 2,     # Shrine media_radius 2
    'card_corner_radius': 2,        # Shrine card_corner_radius 2
    'card_title_case': 'default',

    # --- Swatches -----------------------------------------------------------
    'show_variant_image': False,
    'variant_swatch_width': 18,     # Shrine .ds-card__swatch 1.8rem
    'variant_swatch_height': 18,
    'variant_swatch_radius': 0,
    'variant_swatch_border_style': 'solid',
    'variant_swatch_border_width': 1,
    'variant_swatch_border_opacity': 25,

    # --- Variantenauswahl ---------------------------------------------------
    'palette_variant_background': 'rgba(0,0,0,0)',
    'palette_variant_text': FG,
    'palette_variant_border': FG,
    'palette_selected_variant_background': FG,
    'palette_selected_variant_text': BG,
    'palette_selected_variant_border': FG,
    'variant_button_border_width': 1,
    'variant_button_radius': 0,
    'variant_button_width': 'default-width-buttons',
}

schema = json.load(open(SCHEMA, encoding='utf-8'))
known, options = {}, {}
for group in schema:
    for s in group.get('settings', []):
        sid = s.get('id')
        if not sid:
            continue
        known[sid] = s.get('type')
        if s.get('options'):
            options[sid] = [o.get('value') for o in s['options']]

unknown = sorted(set(MAP) - set(known))
if unknown:
    sys.exit('Unbekannte Setting-IDs (nicht im Schema): %s' % unknown)

bad = []
for sid, val in MAP.items():
    if sid in options and not isinstance(val, (dict, bool)) and str(val) not in options[sid]:
        bad.append('%s=%r erlaubt: %s' % (sid, val, options[sid]))
if bad:
    sys.exit('Ungueltige Option:\n  ' + '\n  '.join(bad))

data = {'current': dict(MAP), 'presets': {'Solena': dict(MAP)}}
out = os.path.join(HORIZON, 'config', 'settings_data.json')
with open(out, 'w', encoding='utf-8') as fh:
    json.dump(data, fh, indent=2, ensure_ascii=False)
    fh.write('\n')

missing = sorted(set(known) - set(MAP))
print('settings_data.json geschrieben: %d von %d Settings gesetzt.' % (len(MAP), len(known)))
print('Auf Schema-Default belassen (%d): %s' % (len(missing), ', '.join(missing) or '-'))
