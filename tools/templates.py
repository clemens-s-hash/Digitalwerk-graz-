"""Schreibt die Horizon-Templates mit den Inhalten aus dem Shrine-Theme.

Warum generiert und nicht handgeschrieben: die Produktkarte mit Shrines
Aufbau (Bild, Titel + Produkttyp links, Bewertung rechts, Haarlinie, Preis,
Farb-Swatches) steckt in acht Templates. Einmal definiert statt achtmal
abgeschrieben heisst, dass sie in allen acht gleich bleibt.

Nur Einstellungen, die von Horizons Schema-Default abweichen, werden
geschrieben. Shopify ergaenzt den Rest beim Rendern.

Aufruf: python3 -I tools/templates.py <theme-verzeichnis>
"""
import json, os, re, sys

ROOT = sys.argv[1]

# Farben aus Shrines flachen Einstellungen, aufgeloest
BG1 = '{{ settings.color_palette.background }}'   # #FBF9F5  background-1
BG2 = '#F2EDE5'                                   #          background-2
INK = '#1C1A17'                                   #          inverse / accent-1

HEADER = """/*
 * ------------------------------------------------------------
 * Erzeugt von tools/templates.py aus dem Shrine-Export.
 *
 * Diese Datei darf der Shopify-Theme-Editor ueberschreiben.
 * Nach Aenderungen am Generator neu erzeugen, nicht hier und
 * dort gleichzeitig editieren.
 * ------------------------------------------------------------
 */
"""


def write(name, doc):
    path = os.path.join(ROOT, 'templates', name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(HEADER)
        json.dump(doc, fh, indent=2, ensure_ascii=False)
        fh.write('\n')
    print('  %-34s %2d Sections' % (name, len(doc.get('order', []))))


def load(name):
    """Liest ein mitgeliefertes Horizon-Template inklusive Kommentarkopf."""
    path = os.path.join(ROOT, 'templates', name)
    text = open(path, encoding='utf-8').read()
    return json.loads(re.sub(r'^\s*/\*.*?\*/\s*', '', text, flags=re.S))


def order(doc):
    doc['order'] = list(doc['sections'].keys())
    return doc


# ---------------------------------------------------------------------------
# Wiederverwendbare Bausteine
# ---------------------------------------------------------------------------

def product_card(card_id, ratio='portrait', rating=True, swatches=True, ptype=True):
    """Shrines Produktkarte, aus Horizon-Bloecken zusammengesetzt.

    Aufbau wie im alten Theme:
      Bild
      Zeile: [Titel + Produkttyp]  ...  Bewertung
      Haarlinie
      Preis
      Farb-Swatches
    """
    titles = {
        'type': '_product-card-group',
        'settings': {
            'content_direction': 'column',
            'horizontal_alignment_flex_direction_column': 'flex-start',
            'gap': 0,
            'width': 'fill',
            'height': 'fit',
        },
        'blocks': {
            'card-title': {
                'type': 'product-title',
                'settings': {
                    'width': '100%',
                    'alignment': 'left',
                    'type_preset': 'custom',
                    'font': 'var(--font-heading--family)',
                    'font_size': '1.125rem',
                    'line_height': 'tight',
                    'max_width': 'none',
                },
            },
        },
        'block_order': ['card-title'],
    }
    if ptype:
        titles['blocks']['card-type'] = {
            'type': 'solena-product-type',
            'settings': {'source': 'type_then_vendor', 'alignment': 'left'},
        }
        titles['block_order'].append('card-type')

    topline = {
        'type': '_product-card-group',
        'settings': {
            'content_direction': 'row',
            'vertical_on_mobile': True,
            'horizontal_alignment': 'space-between',
            'vertical_alignment': 'flex-start',
            'align_baseline': False,
            'gap': 12,
            'width': 'fill',
            'height': 'fit',
        },
        'blocks': {'card-titles': titles},
        'block_order': ['card-titles'],
    }
    if rating:
        topline['blocks']['card-rating'] = {
            'type': 'review',
            'settings': {
                'stars_style': 'shaded',
                'show_number': True,
                'width': 'fit-content',
                'alignment': 'right',
                'type_preset': 'paragraph',
            },
        }
        topline['block_order'].append('card-rating')

    blocks = {
        'card-gallery': {
            'type': '_product-card-gallery',
            'settings': {'image_ratio': ratio, 'border_radius': 2},
        },
        'card-topline': topline,
        'card-rule': {
            'type': 'solena-hairline',
            'settings': {'thickness': 1, 'padding-block-start': 14, 'padding-block-end': 0},
        },
        'card-price': {
            'type': 'price',
            'settings': {
                'show_sale_price_first': True,
                'width': '100%',
                'alignment': 'left',
                'type_preset': 'custom',
                'font': 'var(--font-body--family)',
                'font_size': '1rem',
            },
        },
    }
    block_order = ['card-gallery', 'card-topline', 'card-rule', 'card-price']

    if swatches:
        blocks['card-swatches'] = {
            'type': 'solena-card-swatches',
            'settings': {
                'swatch_limit': 6,
                'swatch_size': 18,
                'alignment': 'flex-start',
                'padding-block-start': 14,
            },
        }
        block_order.append('card-swatches')

    return {
        'type': '_product-card',
        'static': True,
        'settings': {'product_card_gap': 0, 'border': 'none', 'border_radius': 0},
        'blocks': blocks,
        'block_order': block_order,
    }


def heading(text, preset='h3', align='left', width='100%'):
    return {
        'type': 'text',
        'settings': {
            'text': text,
            'type_preset': preset,
            'font': 'var(--font-heading--family)',
            'width': width,
            'alignment': align,
            'max_width': 'none',
        },
    }


def body(text, align='left', width='100%', max_width='normal'):
    return {
        'type': 'text',
        'settings': {
            'text': text,
            'type_preset': 'rte',
            'width': width,
            'alignment': align,
            'max_width': max_width,
        },
    }


def button(label, link, style='button'):
    return {'type': 'button', 'settings': {'label': label, 'link': link, 'style_class': style}}


def product_list(title, collection, max_products, columns, *, card_ratio='portrait',
                 rating=True, swatches=True, view_all=None, pad=(36, 36),
                 carousel_mobile=False, background=None, heading_preset='h2'):
    """Shrines `featured-collection` als Horizon-`product-list`."""
    header_blocks = {'pl-title': {
        'type': '_product-list-text',
        'settings': {
            'text': title,
            'type_preset': heading_preset,
            'font': 'var(--font-heading--family)',
            'width': 'fit-content',
            'alignment': 'left',
            'max_width': 'none',
        },
    }}
    header_order = ['pl-title']
    if view_all:
        header_blocks['pl-view-all'] = {
            'type': '_product-list-button',
            'settings': {'label': view_all, 'style_class': 'button-secondary'},
        }
        header_order.append('pl-view-all')

    settings = {
        'collection': collection,
        'layout_type': 'grid',
        'carousel_on_mobile': carousel_mobile,
        'max_products': max_products,
        'columns': columns,
        'mobile_columns': '2',
        'columns_gap': 24,
        'rows_gap': 56,
        'section_width': 'page-width',
        'gap': 32,
        'padding-block-start': pad[0],
        'padding-block-end': pad[1],
    }
    if background:
        settings['background_color'] = background

    return {
        'type': 'product-list',
        'settings': settings,
        'blocks': {
            'static-header': {
                'type': '_product-list-content',
                'static': True,
                'settings': {
                    'content_direction': 'row',
                    'horizontal_alignment': 'space-between',
                    'vertical_alignment': 'flex-end',
                    'align_baseline': True,
                    'gap': 12,
                    'width': 'fill',
                },
                'blocks': header_blocks,
                'block_order': header_order,
            },
            'static-product-card': product_card('static-product-card', card_ratio, rating, swatches),
        },
    }


def newsletter(*, disabled=False, pad=(88, 88)):
    """Shrines `newsletter`. Texte unveraendert aus dem Export uebernommen."""
    section = {
        'type': 'section',
        'settings': {
            'content_direction': 'column',
            'horizontal_alignment_flex_direction_column': 'center',
            'gap': 16,
            'section_width': 'page-width',
            'background_color': BG2,
            'padding-block-start': pad[0],
            'padding-block-end': pad[1],
        },
        'blocks': {
            'nl-heading': heading('<h2>Subscribe to our emails</h2>', 'h2', 'center'),
            'nl-text': body(
                '<p>Join our email list for exclusive offers and the latest news.</p>',
                'center', '100%', 'normal'),
            'nl-form': {
                'type': 'email-signup',
                'settings': {
                    'width': 'custom',
                    'custom_width': 50,
                    'border_style': 'all',
                    'border_width': 1,
                    'border_radius': 0,
                    'label': 'Sign up',
                    'style_class': 'button',
                    'display_type': 'text',
                    'integrated_button': False,
                },
            },
        },
        'block_order': ['nl-heading', 'nl-text', 'nl-form'],
    }
    if disabled:
        section['disabled'] = True
    return section


def rich_text(blocks_in_order, *, align='center', background=None, pad=(88, 88),
              width='page-width'):
    """Shrines `rich-text` als `section` mit Text- und Button-Bloecken."""
    settings = {
        'content_direction': 'column',
        'horizontal_alignment_flex_direction_column': 'center' if align == 'center' else 'flex-start',
        'gap': 16,
        'section_width': width,
        'padding-block-start': pad[0],
        'padding-block-end': pad[1],
    }
    if background:
        settings['background_color'] = background
    blocks, order_ = {}, []
    for key, blk in blocks_in_order:
        blocks[key] = blk
        order_.append(key)
    return {'type': 'section', 'settings': settings, 'blocks': blocks, 'block_order': order_}


def accordion(rows, *, open_first=False):
    """Shrines `collapsible_row`-Bloecke als Horizon-`accordion`."""
    blocks, order_ = {}, []
    for i, (title, content) in enumerate(rows, start=1):
        key = 'row-%d' % i
        blocks[key] = {
            'type': '_accordion-row',
            'settings': {'heading': title, 'open_by_default': open_first and i == 1, 'icon': 'none'},
            'blocks': {'text-%d' % i: body(content, 'left', '100%', 'none')},
            'block_order': ['text-%d' % i],
        }
        order_.append(key)
    return {
        'type': 'accordion',
        'settings': {'icon': 'caret', 'dividers': True, 'type_preset': 'h5',
                     'divider_color': '{{ settings.color_palette.color2 }}'},
        'blocks': blocks,
        'block_order': order_,
    }


def media_with_content(image, content_blocks, *, media_position='right', media_width='wide',
                       media_height='80svh', background=None, pad=(96, 96), align='center'):
    """Shrines `image-with-text` als Horizon-`media-with-content`."""
    settings = {
        'media_position': media_position,
        'media_width': media_width,
        'media_height': media_height,
        'section_width': 'page-width',
        'extend_media': False,
        'padding-block-start': pad[0],
        'padding-block-end': pad[1],
    }
    if background:
        settings['background_color'] = background
    blocks, order_ = {}, []
    for key, blk in content_blocks:
        blocks[key] = blk
        order_.append(key)
    return {
        'type': 'media-with-content',
        'settings': settings,
        'blocks': {
            'media': {
                'type': '_media-without-appearance',
                'static': True,
                'settings': {'media_type': 'image', 'image': image, 'image_position': 'cover'},
            },
            'content': {
                'type': '_content-without-appearance',
                'static': True,
                'settings': {
                    'horizontal_alignment_flex_direction_column':
                        'center' if align == 'center' else 'flex-start',
                    'gap': 16,
                },
                'blocks': blocks,
                'block_order': order_,
            },
        },
    }


def gempages_slot(label):
    """Platzhalter fuer eine GemPages-Section.

    Shrine hatte an diesen Stellen `apps`- oder `_blocks`-Sections, deren
    Inhalt in der App liegt und nicht im Theme.

    Als Container dient `sections/section.liquid`, nicht `_blocks`:
    `_blocks` ist in Horizon eine private Section (fuehrender Unterstrich)
    und wird im Lieferzustand an keiner Stelle als Top-Level-Section
    verwendet. `section` nimmt ueber `@app` dieselben App-Bloecke auf.
    """
    return {
        'type': 'section',
        'name': label,
        'settings': {
            'content_direction': 'column',
            'section_width': 'page-width',
            'gap': 0,
            'padding-block-start': 0,
            'padding-block-end': 0,
        },
    }


def app_slot(app, block_name, note=''):
    """Platzhalter-Block, der die Position eines App-Blocks freihaelt.

    App-Bloecke stehen nicht in den Templates, weil `shopify theme check`
    `shopify://apps/...`-Typen offline nicht aufloesen kann. Der Platzhalter
    haelt die Reihenfolge aus dem Shrine-Original und zeigt im Theme-Editor,
    was an diese Stelle gehoert. Im Shop rendert er nichts.
    """
    return {
        'type': 'solena-app-slot',
        'settings': {'app_name': app, 'block_name': block_name, 'note': note},
    }


# ---------------------------------------------------------------------------
# templates/index.json — 9 Sections, Reihenfolge wie im Shrine-Export
# ---------------------------------------------------------------------------

def build_index():
    return order({'sections': {
        # 1. slideshow, ein Slide
        'slideshow': {
            'type': 'slideshow',
            'settings': {
                'display_mode': 'full_frame',
                'section_width': 'full-width',
                'full_frame_on_mobile': True,
                'slide_height': 'large',
                'content_position': 'on-media',
                'corner_radius': 0,
                'slideshow_gap': 0,
                'icons_style': 'none',
                'slideshow_controls_style': 'counter',
                'autoplay': False,
                'padding-block-start': 0,
                'padding-block-end': 0,
            },
            'blocks': {
                'slide-1': {
                    'type': '_slide',
                    'settings': {
                        'media_type_1': 'image',
                        'image_1': 'shopify://shop_images/hf_20260902_173914_1665b126-212b-4577-b96c-3446f36c38ab.png',
                        'content_direction': 'column',
                        'horizontal_alignment_flex_direction_column': 'flex-start',
                        'vertical_alignment_flex_direction_column': 'center',
                        'gap': 16,
                        'toggle_overlay': True,
                        'overlay_color': '#1C1A171A',
                        'overlay_style': 'solid',
                        'padding-inline-start': 80,
                        'padding-block-start': 60,
                        'padding-block-end': 60,
                    },
                    'blocks': {
                        'slide-heading': {
                            'type': '_heading',
                            'settings': {
                                'text': '<h1>Entdecke Solena</h1>',
                                'type_preset': 'h1',
                                'font': 'var(--font-heading--family)',
                                'alignment': 'left',
                                'wrap': 'balance',
                            },
                        },
                        'slide-sub': body(
                            '<p>Weil Design keine Ausnahme sein sollte</p>', 'left', 'fit-content'),
                        'slide-button': button(
                            'Finde jetzt deinen Stil', 'shopify://collections/all'),
                    },
                    'block_order': ['slide-heading', 'slide-sub', 'slide-button'],
                },
            },
            'block_order': ['slide-1'],
        },

        # 2. collection-list, fuenf Kollektionen
        'collection_list': {
            'type': 'collection-list',
            'settings': {
                'collection_list': [
                    'hangeleuchten', 'deckenleuchten', 'tischleuchten',
                    'wandleuchten', 'outdoor-leuchten',
                ],
                'layout_type': 'grid',
                'carousel_on_mobile': True,
                'columns': 5,
                'mobile_columns': '2',
                'max_collections': 5,
                'columns_gap': 24,
                'rows_gap': 40,
                'section_width': 'page-width',
                'gap': 32,
                'padding-block-start': 72,
                'padding-block-end': 88,
            },
            'blocks': {
                'cl-heading': heading('<h2>Collections</h2>', 'h2', 'left', 'fit-content'),
                'static-collection-card': {
                    'type': '_collection-card',
                    'static': True,
                    'settings': {
                        'placement': 'below_image',
                        'horizontal_alignment': 'flex-start',
                        'collection_card_gap': 14,
                        'border': 'none',
                    },
                    'blocks': {
                        'collection-card-image': {
                            'type': '_collection-card-image',
                            'static': True,
                            'settings': {'image_ratio': 'square', 'border_radius': 2},
                        },
                        'cc-title': {
                            'type': 'collection-title',
                            'settings': {
                                'width': '100%',
                                'alignment': 'left',
                                'type_preset': 'custom',
                                'font': 'var(--font-body--family)',
                                'font_size': '1rem',
                                'letter_spacing': 'loose',
                                'case': 'uppercase',
                            },
                        },
                    },
                    'block_order': ['collection-card-image', 'cc-title'],
                },
            },
            'block_order': ['cl-heading'],
        },

        # 3. featured-collection „Solena Bestseller"
        'bestseller': product_list(
            '<h2>Solena Bestseller</h2>', 'bestseller', 16, 5,
            heading_preset='h1', rating=True, swatches=True, pad=(36, 36)),

        # 4. + 5. die beiden leeren GemPages-Sections aus index.json
        'gempages_slot_1': gempages_slot('GemPages Platzhalter 1'),
        'gempages_slot_2': gempages_slot('GemPages Platzhalter 2'),

        # 6. image-with-text
        'image_with_text': media_with_content(
            'shopify://shop_images/hf_20260902_183544_5640de0a-023a-46bd-9a55-b126b3989ad1.png',
            [
                ('iwt-heading', heading(
                    '<h2>Ein Statement für dein Zuhause</h2>', 'h3', 'center', 'fit-content')),
                ('iwt-text', body(
                    '<p>Wo nordische Ruhe auf Design trifft</p>', 'center', 'fit-content')),
                ('iwt-button', button('Mehr lesen', 'shopify://pages/uber-uns', 'button-secondary')),
            ],
            media_position='right', media_width='narrow', media_height='80svh',
            background=BG2, pad=(96, 96), align='center'),

        # 7. featured-product mit den sieben Bloecken des Originals.
        #
        # Horizons `featured-product` nimmt keine Bloecke an, nur ein Produkt
        # und ein Layout. Die Entsprechung ist
        # `featured-product-information`: dieselbe Struktur wie die
        # Produktseite, aber mit eigenem Produkt-Setting.
        #
        # Im Shrine-Original war die Section deaktiviert, alle Bloecke ausser
        # `text` und `title` ebenfalls, und es war KEIN Produkt gesetzt
        # ("product": ""). Beides ist uebernommen; das Produkt muss in
        # Shopify gewaehlt werden.
        'featured_product': {
            'type': 'featured-product-information',
            'disabled': True,
            'settings': {
                'product': '',
                'content_width': 'content-center-aligned',
                'desktop_media_position': 'left',
                'gap': 32,
                'padding-block-start': 88,
                'padding-block-end': 88,
            },
            'blocks': {
                'media-gallery': {
                    'type': '_featured-product-information-carousel',
                    'static': True,
                    'settings': {},
                },
                'product-details': {
                    'type': '_product-details',
                    'static': True,
                    'settings': {
                        'width': 'fill',
                        'details_position': 'flex-start',
                        'gap': 20,
                    },
                    'blocks': {
                        # 1 — text „Immer im Blick", im Original uppercase
                        'fp-eyebrow': {
                            'type': 'text',
                            'settings': {
                                'text': '<p>Immer im Blick</p>',
                                'type_preset': 'custom',
                                'font': 'var(--font-body--family)',
                                'font_size': '0.75rem',
                                'letter_spacing': 'loose',
                                'case': 'uppercase',
                                'width': '100%',
                                'alignment': 'left',
                            },
                        },
                        # 2 — title, im Original h2
                        'fp-title': {
                            'type': 'product-title',
                            'settings': {
                                'width': '100%',
                                'alignment': 'left',
                                'type_preset': 'h3',
                                'font': 'var(--font-heading--family)',
                                'max_width': 'none',
                            },
                        },
                        # 3 — price, im Original deaktiviert
                        'fp-price': {
                            'type': 'price',
                            'disabled': True,
                            'settings': {'show_sale_price_first': True, 'width': '100%'},
                        },
                        # 4 — variant_picker, im Original deaktiviert
                        'fp-variant-picker': {
                            'type': 'variant-picker',
                            'disabled': True,
                            'settings': {},
                        },
                        # 5 — quantity_selector, im Original deaktiviert
                        'fp-quantity': {
                            'type': 'quantity',
                            'disabled': True,
                            'settings': {},
                        },
                        # 6 — buy_buttons, im Original deaktiviert
                        'fp-buy-buttons': {
                            'type': 'buy-buttons',
                            'disabled': True,
                            'settings': {'stacking': False},
                            'blocks': {
                                'quantity': {'type': 'quantity', 'static': True, 'settings': {}},
                                'add-to-cart': {'type': 'add-to-cart', 'static': True,
                                                'settings': {'style_class': 'button'}},
                                'accelerated-checkout': {'type': 'accelerated-checkout',
                                                         'static': True, 'settings': {}},
                            },
                        },
                        # 7 — share, im Original deaktiviert. Horizon hat
                        #     keinen Teilen-Block, daher solena-share.
                        'fp-share': {
                            'type': 'solena-share',
                            'disabled': True,
                            'settings': {'label': 'Share'},
                        },
                    },
                    'block_order': [
                        'fp-eyebrow', 'fp-title', 'fp-price', 'fp-variant-picker',
                        'fp-quantity', 'fp-buy-buttons', 'fp-share',
                    ],
                },
            },
        },

        # 8. featured-collection „Trends 2026"
        'trends': product_list(
            '<h2>Trends 2026</h2>', 'trends', 4, 4,
            heading_preset='h2', rating=True, swatches=True,
            view_all='Alle ansehen', pad=(36, 36)),

        # 9. testimonials
        'testimonials': {
            'type': 'section',
            'settings': {
                'content_direction': 'column',
                'horizontal_alignment_flex_direction_column': 'center',
                'gap': 32,
                'section_width': 'page-width',
                'padding-block-start': 96,
                'padding-block-end': 96,
            },
            'blocks': {
                't-heading': heading(
                    '<h2>Zufriedenheit ist unsere Voraussetzung</h2>', 'h3', 'center'),
                't-row': {
                    'type': 'group',
                    'settings': {
                        'content_direction': 'row',
                        'vertical_on_mobile': True,
                        'horizontal_alignment': 'space-between',
                        'vertical_alignment': 'flex-start',
                        'gap': 24,
                        'width': 'fill',
                        'height': 'fit',
                    },
                    'blocks': {
                        't-1': {'type': 'solena-testimonial', 'settings': {
                            'heading': 'Schnell geliefert, top Qualität!',
                            'text': '<p>Leuchte war in einer Woche da und hat unserem Esszimmer endlich das gewisse Etwas verliehen!</p>',
                            'author': 'Julia S.',
                            'show_stars': True, 'stars': 5, 'alignment': 'center',
                        }},
                        't-2': {'type': 'solena-testimonial', 'settings': {
                            'heading': 'Designer-pieces',
                            'text': '<p>Hab mir 2x die Spira Nachttischleuchte gekauft, kommt echt gut wenn man Ahnung hat wie man sie kombiniert. Wurde bis jetzt von jedem gefragt wo ich die gekauft habe. Top!</p>',
                            'author': 'Thomas W.',
                            'show_stars': True, 'stars': 5, 'alignment': 'center',
                        }},
                        't-3': {'type': 'solena-testimonial', 'settings': {
                            'heading': 'Vorbildlicher Kundenservice',
                            'text': '<p>Hatte eine Frage zu meiner Bestellung und bekam innerhalb weniger Stunden eine hilfreiche Antwort. So muss das sein!</p>',
                            'author': 'Andrea Z.',
                            'show_stars': True, 'stars': 5, 'alignment': 'center',
                        }},
                    },
                    'block_order': ['t-1', 't-2', 't-3'],
                },
            },
            'block_order': ['t-heading', 't-row'],
        },
    }})


# ---------------------------------------------------------------------------
# templates/product.json
# ---------------------------------------------------------------------------

# App-Bloecke stehen bewusst NICHT in den Templates.
#
# `shopify theme check` kann `shopify://apps/...`-Typen offline nicht
# aufloesen und meldet sie als JSONMissingBlock. Die Bloecke werden daher in
# Shopify eingesetzt; PORT.md nennt Position, App und die Einstellungen aus
# dem Shrine-Export. Die Container bleiben erhalten: `product-information`
# nimmt @app-Bloecke auf, und fuer die frueheren `apps`-Sections stehen
# `_blocks`-Sections an derselben Stelle.

PRODUCT_FAQ = [
    ('Wie lange dauert der Versand?',
     '<p>Die Bearbeitung dauert in der Regel 1 bis 2 Werktage. Die Lieferzeit beträgt meist ca. 3 bis 7 Werktage.</p>'),
    ('Ist der Versand kostenlos?',
     '<p>Ja, der Versand innerhalb Deutschlands und Österreich ist kostenlos.</p>'),
    ('Wie kann ich meine Bestellung verfolgen?',
     '<p>Sobald die Bestellung versendet wurde, erhalten Sie eine E-Mail mit einem Tracking-Link.</p>'),
    ('Wie lautet eure Rückgaberichtlinie?',
     '<p>Sie können Artikel innerhalb von 30 Tagen ab Zustellung zurückgeben. Die Artikel müssen ungetragen, unbenutzt, vollständig und im Originalzustand mit Etiketten sein. Die Rücksendekosten trägt der Kunde.</p>'),
    ('Welche Zahlungsmethoden bietet ihr an?',
     '<p>Visa, Mastercard, Maestro, SEPA, American Express, Apple Pay und PayPal.</p>'),
    ('Ist die Zahlung auf eurer Website sicher?',
     '<p>Ja. Ihre Zahlung wird über sichere, verschlüsselte Verbindungen verarbeitet. Zusätzlich stehen Ihnen bekannte Zahlungsarten zur Verfügung.</p>'),
    ('Wie geht ihr mit meinen Daten um?',
     '<p>Wir nutzen Ihre Daten nur zur Bestellabwicklung und zur Bereitstellung unseres Services. Ihre Daten werden nicht für fremde Werbezwecke verkauft.</p>'),
    ('Wie kann ich euch erreichen?',
     '<p>support@solenahome.com</p>'),
]

# Der Markentext aus Shrines rich-text-Section, identisch auf product.json
# und allen acht Premium-Templates.
ABOUT_TEXT = (
    '<p>"Bei Solena dreht sich alles um eines: Licht, das wirklich berührt. '
    'Wir glauben, dass ein Zuhause erst durch die richtige Beleuchtung seinen '
    'Charakter bekommt – deshalb haben wir es uns zur Aufgabe gemacht, '
    'ausschließlich Designerlampen zu führen, die höchsten Ansprüchen an '
    'Qualität, Formgebung und Langlebigkeit gerecht werden.</p>'
    '<p>Kund:innen vertrauen auf Solena, wenn es darum geht, ihr Zuhause in ein '
    'Statement zu verwandeln. Entdecke jetzt unsere Kollektionen und finde die '
    'Leuchte, die zu dir passt – bevor sie ausverkauft ist."</p>'
)

COMPARISON_ROWS = [
    'Persönlicher Kundenservice',
    'Designerlampen zum fairen Preis',
    '30 Tage Geld-zurück-Garantie',
]


def comparison_table():
    blocks, order_ = {}, []
    for i, benefit in enumerate(COMPARISON_ROWS, start=1):
        key = 'cmp-%d' % i
        blocks[key] = {
            'type': '_solena-comparison-row',
            'settings': {'benefit': benefit, 'us': True, 'others': False},
        }
        order_.append(key)
    return {
        'type': 'solena-comparison-table',
        'settings': {
            'us_label': '',
            'others_label': 'Andere',
            'us_column_width': 25,
            'checkmark_color': '#53AF01',
        },
        'blocks': blocks,
        'block_order': order_,
    }


def product_tabs(tabs=None):
    """Die drei Aufklappbereiche als Horizon-`accordion`."""
    tabs = tabs or [
        ('Produktbeschreibung', 'clipboard', None),
        ('Versandinformationen', 'truck',
         '<p>Wir bieten kostenlosen Versand innerhalb Deutschlands an.</p>'
         '<ul><li><strong>Bearbeitungszeit:</strong> 1–2 Werktage</li>'
         '<li><strong>Lieferzeit:</strong> 3–7 Werktage</li></ul>'
         '<p>Der Versand erfolgt zuverlässig mit DHL, inklusive Sendungsverfolgung.</p>'
         '<p>Weitere Informationen findest du in unserer Versandrichtlinie.</p>'),
        ('Rückgabeinformationen', 'return',
         '<p>Rücksendungen sind innerhalb von 30 Tagen nach Erhalt der Ware möglich.'
         '<br/>Der Kaufpreis wird nach Eingang und Prüfung der Rücksendung erstattet.'
         '<br/>Die Rücksendekosten trägt der Käufer.</p>'
         '<p>Weitere Informationen finden Sie in unserer Rückerstattungsrichtlinie.</p>'),
    ]
    blocks, order_ = {}, []
    for i, (title, icon, content) in enumerate(tabs, start=1):
        key = 'tab-%d' % i
        child_key = 'tab-body-%d' % i
        # `{{ product.description }}` im Original heisst: Horizons
        # product-description-Block, nicht ein Text mit Liquid darin.
        if content is None:
            child = {'type': 'product-description', 'settings': {'width': '100%'}}
        else:
            child = body(content, 'left', '100%', 'none')
        blocks[key] = {
            'type': '_accordion-row',
            'settings': {'heading': title, 'icon': icon},
            'blocks': {child_key: child},
            'block_order': [child_key],
        }
        order_.append(key)
    return {
        'type': 'accordion',
        'settings': {
            'icon': 'caret',
            'dividers': True,
            'type_preset': 'h5',
            'divider_color': '{{ settings.color_palette.color2 }}',
        },
        'blocks': blocks,
        'block_order': order_,
    }


def sticky_atc():
    """Shrines `sticky_atc`-Block.

    Einstellungen aus dem Export: erscheint nach dem Scrollen, Beschriftung
    „Zum Warenkorb", Preis und Rabatt-Badge sichtbar, Farbschema
    background-1 — in Horizon also die Standardfarben, kein Override.
    """
    return {
        'type': 'solena-sticky-atc',
        'settings': {
            'display_when': 'after_scroll',
            'button_label': 'Zum Warenkorb',
            'show_image': True,
            'show_price': True,
            'show_price_badge': True,
        },
    }


def product_details_blocks():
    """Die 15 Bloecke der Produktseite in der Reihenfolge aus dem Export."""
    blocks = {
        # 2 — Titel
        'title': {
            'type': 'product-title',
            'settings': {
                'width': '100%',
                'alignment': 'left',
                'type_preset': 'h3',
                'font': 'var(--font-heading--family)',
                'max_width': 'none',
            },
        },
        # 6 — Preis
        'price': {
            'type': 'price',
            'settings': {
                'show_sale_price_first': True,
                'width': '100%',
                'alignment': 'left',
                'type_preset': 'custom',
                'font': 'var(--font-body--family)',
                'font_size': '1.25rem',
            },
        },
        # 7 — Vorteile mit Emoji, im Original deaktiviert
        'emoji-benefits': {
            'type': 'solena-emoji-benefits',
            'disabled': True,
            'settings': {'benefits': '<p>🙌 Benefit</p><p>💪 Benefit</p><p>🌟 Benefit</p>'},
        },
        # 8 — Variantenauswahl
        'variant-picker': {'type': 'variant-picker', 'settings': {}},
        # 9 — Mengenstaffel, im Original deaktiviert
        'quantity': {'type': 'quantity', 'disabled': True, 'settings': {}},
        # 10 — Kaufen-Schaltflaechen
        'buy-buttons': {
            'type': 'buy-buttons',
            'settings': {'stacking': False, 'show_pickup_availability': True},
            'blocks': {
                'quantity': {'type': 'quantity', 'static': True, 'settings': {}},
                'add-to-cart': {'type': 'add-to-cart', 'static': True,
                                'settings': {'style_class': 'button'}},
                'accelerated-checkout': {'type': 'accelerated-checkout', 'static': True,
                                         'settings': {}},
            },
        },
        # 11 — Sticky Add-to-Cart: Horizon hat das als Section-Einstellung,
        #      enable_sticky_add_to_cart. Kein Block noetig.
        # 12 — Bezahl-Icons
        'payment-icons': {
            'type': 'payment-icons',
            'settings': {'horizontal_alignment': 'flex-start', 'gap': 8},
        },
        # 13-15 — die drei Aufklapp-Zeilen
        'tabs': product_tabs(),
    }
    # Die vier App-Bloecke bekommen Platzhalter an ihren Positionen 1, 3, 4
    # und 5, damit die Reihenfolge des Originals erhalten bleibt.
    blocks['app-review-summary-1'] = app_slot(
        'Iconic Blocks', 'Review Summary',
        'Trustpilot-Zeile: 4,5 Sterne, „Über 35.000 Bewertungen", Link at.trustpilot.com')
    blocks['app-benefits'] = app_slot(
        'Iconic Blocks', 'Benefits',
        'liest product.metafields.custom.selling_point_1 bis _4')
    blocks['app-judgeme-badge'] = app_slot(
        'Judge.me', 'Preview Badge', 'Sterne-Vorschau unter dem Titel')
    blocks['app-review-summary-2'] = app_slot(
        'Iconic Blocks', 'Review Summary (zweite Instanz)',
        'im Original mit dem Platzhaltertext „20,921 reviews", ohne Link')
    # 11 — Sticky Warenkorb
    blocks['sticky-atc'] = sticky_atc()

    block_order = [
        'app-review-summary-1',   # 1
        'title',                  # 2
        'app-benefits',           # 3
        'app-judgeme-badge',      # 4
        'app-review-summary-2',   # 5
        'price',                  # 6
        'emoji-benefits',         # 7  (im Original deaktiviert)
        'variant-picker',         # 8
        'quantity',               # 9  (im Original deaktiviert)
        'buy-buttons',            # 10
        'sticky-atc',             # 11
        'payment-icons',          # 12
        'tabs',                   # 13-15
    ]
    return blocks, block_order


def build_product():
    details_blocks, details_order = product_details_blocks()
    return order({'sections': {
        'main': {
            'type': 'product-information',
            'settings': {
                'content_width': 'content-center-aligned',
                'desktop_media_position': 'left',
                'gap': 32,
                # Aus, weil der eigene Block solena-sticky-atc an Position 11
                # steht. Sonst erschienen zwei Leisten.
                'enable_sticky_add_to_cart': False,
                'padding-block-start': 32,
                'padding-block-end': 88,
            },
            'blocks': {
                'media-gallery': {
                    'type': '_product-media-gallery',
                    'static': True,
                    'settings': {
                        'media_presentation': 'carousel',
                        'slideshow_controls_style': 'thumbnails',
                        'slideshow_mobile_controls_style': 'thumbnails',
                        'thumbnail_position': 'bottom',
                        'thumbnail_radius': 0,
                        'aspect_ratio': 'adapt',
                        'constrain_to_viewport': True,
                        'media_fit': 'contain',
                        'media_radius': 2,
                        'extend_media': False,
                        'zoom': True,
                        'video_loop': False,
                        'hide_variants': False,
                    },
                },
                'product-details': {
                    'type': '_product-details',
                    'static': True,
                    'settings': {
                        'width': 'fill',
                        'details_position': 'flex-start',
                        'gap': 20,
                        'sticky_details_desktop': True,
                        'padding-block-start': 0,
                        'padding-block-end': 24,
                    },
                    'blocks': details_blocks,
                    'block_order': details_order,
                },
            },
        },

        # related-products, im Original deaktiviert
        'related_products': {
            'type': 'product-recommendations',
            'disabled': True,
            'settings': {
                'max_products': 4,
                'columns': 4,
                'columns_gap': 24,
                'rows_gap': 56,
                'padding-block-start': 88,
                'padding-block-end': 88,
            },
            'blocks': {
                'static-header': {
                    'type': 'text',
                    'settings': {
                        'text': '<h2>Das könnte dir auch gefallen</h2>',
                        'type_preset': 'h3',
                        'font': 'var(--font-heading--family)',
                        'width': 'fit-content',
                    },
                },
                'static-product-card': product_card('static-product-card', 'square'),
            },
            'block_order': ['static-header'],
        },

        'gempages_product_1': gempages_slot('GemPages Platzhalter 1'),
        'gempages_product_2': gempages_slot('GemPages Platzhalter 2'),

        # rich-text „Über Uns"
        'about': rich_text([
            ('about-heading', heading('<h2>Über Uns</h2>', 'h2', 'center')),
            ('about-text', body(
                ABOUT_TEXT,
                'center', '100%', 'normal')),
        ], background=BG2, width='full-width'),

        # comparison-table „Was uns ausmacht"
        'comparison': {
            'type': 'section',
            'settings': {
                'content_direction': 'column',
                'horizontal_alignment_flex_direction_column': 'center',
                'gap': 32,
                'section_width': 'page-width',
                'padding-block-start': 88,
                'padding-block-end': 88,
            },
            'blocks': {
                'cmp-heading': heading('<h2>Was uns ausmacht</h2>', 'h1', 'center'),
                'cmp-table': comparison_table(),
            },
            'block_order': ['cmp-heading', 'cmp-table'],
        },

        # Platz fuer das Judge.me Review-Widget. Der Container steht, der
        # App-Block kommt in Shopify hinein (PORT.md, App-Bloecke).
        'judgeme_reviews': {
            'type': 'section',
            'name': 'Judge.me Bewertungen',
            'settings': {
                'content_direction': 'column',
                'horizontal_alignment_flex_direction_column': 'center',
                'section_width': 'page-width',
                'gap': 0,
                'padding-block-start': 48,
                'padding-block-end': 48,
            },
            'blocks': {
                'app-judgeme-widget': app_slot(
                    'Judge.me', 'Review Widget',
                    'echte Daten, maximale Breite 700, Shop-Bewertungen aus'),
            },
            'block_order': ['app-judgeme-widget'],
        },

        'gempages_product_3': gempages_slot('GemPages Platzhalter 3'),

        # collapsible-content „Häufig gestellte Fragen"
        'faq': {
            'type': 'section',
            'settings': {
                'content_direction': 'column',
                'horizontal_alignment_flex_direction_column': 'center',
                'gap': 24,
                'section_width': 'page-width',
                'background_color': BG2,
                'padding-block-start': 88,
                'padding-block-end': 88,
            },
            'blocks': {
                'faq-heading': heading('<h2>Häufig gestellte Fragen</h2>', 'h3', 'center'),
                'faq-accordion': accordion(PRODUCT_FAQ),
            },
            'block_order': ['faq-heading', 'faq-accordion'],
        },
    }})


# ---------------------------------------------------------------------------
# templates/product.premium-1 bis -8
#
# Die acht Varianten teilen sich main-product-Aufbau, „Ueber Uns",
# Vergleichstabelle und FAQ mit product.json — per Hash geprueft, alle
# identisch. Unterschiedlich sind nur die drei image-with-text-Sections und
# ihre Position relativ zu related-products.
#
# Inhalte kommen aus tools/premium-content.json, das
# tools/extract-premium.py 1:1 aus dem Shrine-Export liest. So steht der
# Text im Repo, ohne von Hand abgeschrieben zu sein.
# ---------------------------------------------------------------------------

PREMIUM_CONTENT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               'premium-content.json')


def premium_details_blocks(with_emoji_benefits, tabs):
    """main-product der Premium-Templates.

    Reihenfolge weicht von product.json ab: hier kommt der Preis vor den
    Benefits, und es gibt nur zwei App-Bloecke statt vier.
    """
    blocks = {
        'app-review-summary': app_slot(
            'Iconic Blocks', 'Review Summary',
            'Trustpilot-Zeile: 4,5 Sterne, „Über 35.000 Bewertungen", Link at.trustpilot.com'),
        'title': {
            'type': 'product-title',
            'settings': {
                'width': '100%',
                'alignment': 'left',
                'type_preset': 'h3',
                'font': 'var(--font-heading--family)',
                'max_width': 'none',
            },
        },
        'price': {
            'type': 'price',
            'settings': {
                'show_sale_price_first': True,
                'width': '100%',
                'alignment': 'left',
                'type_preset': 'custom',
                'font': 'var(--font-body--family)',
                'font_size': '1.25rem',
            },
        },
        'app-benefits': app_slot(
            'Iconic Blocks', 'Benefits',
            'liest product.metafields.custom.selling_point_1 bis _4'),
        'variant-picker': {'type': 'variant-picker', 'settings': {}},
        'quantity': {'type': 'quantity', 'disabled': True, 'settings': {}},
        'buy-buttons': {
            'type': 'buy-buttons',
            'settings': {'stacking': False, 'show_pickup_availability': True},
            'blocks': {
                'quantity': {'type': 'quantity', 'static': True, 'settings': {}},
                'add-to-cart': {'type': 'add-to-cart', 'static': True,
                                'settings': {'style_class': 'button'}},
                'accelerated-checkout': {'type': 'accelerated-checkout', 'static': True,
                                         'settings': {}},
            },
        },
        'sticky-atc': sticky_atc(),
        'payment-icons': {
            'type': 'payment-icons',
            'settings': {'horizontal_alignment': 'flex-start', 'gap': 8},
        },
        'tabs': product_tabs([(x['heading'], x['icon'],
                               None if x['heading'] == 'Produktbeschreibung' else x['content'])
                              for x in tabs]),
    }
    order_ = ['app-review-summary', 'title', 'price', 'app-benefits']

    if with_emoji_benefits:
        blocks['emoji-benefits'] = {
            'type': 'solena-emoji-benefits',
            'disabled': True,
            'settings': {'benefits': '<p>🙌 Benefit</p><p>💪 Benefit</p><p>🌟 Benefit</p>'},
        }
        order_.append('emoji-benefits')

    order_ += ['variant-picker', 'quantity', 'buy-buttons', 'sticky-atc',
               'payment-icons', 'tabs']
    return blocks, order_


def premium_row(index, row):
    """Eine image-with-text-Zeile eines Premium-Templates."""
    content = [
        ('pr-heading-%d' % index,
         heading('<h2>%s</h2>' % row['heading'], 'h2', 'left', 'fit-content')),
        ('pr-text-%d' % index, body(row['text'], 'left')),
    ]
    if row['button_label']:
        content.append(('pr-button-%d' % index,
                        button(row['button_label'], row['button_link'], 'button-secondary')))
    # Shrines `layout: image_first` heisst Bild links, `text_first` Bild rechts.
    media_position = 'left' if row['layout'] == 'image_first' else 'right'
    return media_with_content(
        row['image'], content,
        media_position=media_position,
        media_width='medium', media_height='auto',
        pad=tuple(row['padding']), align='flex-start')


def build_premium(name, data):
    sections = {}
    row_index = 0
    gem_index = 0
    details_blocks, details_order = premium_details_blocks(
        with_emoji_benefits=name != 'premium-8', tabs=data['tabs'])

    for slot in data['order']:
        if slot == 'main':
            sections['main'] = {
                'type': 'product-information',
                'settings': {
                    'content_width': 'content-center-aligned',
                    'desktop_media_position': 'left',
                    'gap': 32,
                    'enable_sticky_add_to_cart': False,
                    'padding-block-start': 32,
                    'padding-block-end': 88,
                },
                'blocks': {
                    'media-gallery': {
                        'type': '_product-media-gallery',
                        'static': True,
                        'settings': {
                            'media_presentation': 'carousel',
                            'slideshow_controls_style': 'thumbnails',
                            'slideshow_mobile_controls_style': 'thumbnails',
                            'thumbnail_position': 'bottom',
                            'thumbnail_radius': 0,
                            'aspect_ratio': 'adapt',
                            'constrain_to_viewport': True,
                            'media_fit': 'contain',
                            'media_radius': 2,
                            'extend_media': False,
                            'zoom': True,
                            'hide_variants': False,
                        },
                    },
                    'product-details': {
                        'type': '_product-details',
                        'static': True,
                        'settings': {
                            'width': 'fill',
                            'details_position': 'flex-start',
                            'gap': 20,
                            'sticky_details_desktop': True,
                            'padding-block-end': 24,
                        },
                        'blocks': details_blocks,
                        'block_order': details_order,
                    },
                },
            }
        elif slot == 'related':
            sections['related_products'] = {
                'type': 'product-recommendations',
                'disabled': True,
                'settings': {
                    'max_products': 4, 'columns': 4,
                    'columns_gap': 24, 'rows_gap': 56,
                    'padding-block-start': 88, 'padding-block-end': 88,
                },
                'blocks': {
                    'static-header': {
                        'type': 'text',
                        'settings': {
                            'text': '<h2>Das könnte dir auch gefallen</h2>',
                            'type_preset': 'h3',
                            'font': 'var(--font-heading--family)',
                            'width': 'fit-content',
                        },
                    },
                    'static-product-card': product_card('static-product-card', 'square'),
                },
                'block_order': ['static-header'],
            }
        elif slot == 'apps':
            gem_index += 1
            sections['gempages_slot_%d' % gem_index] = gempages_slot(
                'GemPages Platzhalter %d' % gem_index)
        elif slot == 'row':
            row_index += 1
            sections['row_%d' % row_index] = premium_row(row_index,
                                                         data['rows'][row_index - 1])
        elif slot == 'about':
            sections['about'] = rich_text([
                ('about-heading', heading('<h2>Über Uns</h2>', 'h2', 'center')),
                ('about-text', body(ABOUT_TEXT, 'center', '100%', 'normal')),
            ], background=BG2, width='full-width')
        elif slot == 'comparison':
            sections['comparison'] = {
                'type': 'section',
                'settings': {
                    'content_direction': 'column',
                    'horizontal_alignment_flex_direction_column': 'center',
                    'gap': 32,
                    'section_width': 'page-width',
                    'padding-block-start': 88,
                    'padding-block-end': 88,
                },
                'blocks': {
                    'cmp-heading': heading('<h2>Was uns ausmacht</h2>', 'h1', 'center'),
                    'cmp-table': comparison_table(),
                },
                'block_order': ['cmp-heading', 'cmp-table'],
            }
        elif slot == 'faq':
            sections['faq'] = {
                'type': 'section',
                'settings': {
                    'content_direction': 'column',
                    'horizontal_alignment_flex_direction_column': 'center',
                    'gap': 24,
                    'section_width': 'page-width',
                    'background_color': BG2,
                    'padding-block-start': 88,
                    'padding-block-end': 88,
                },
                'blocks': {
                    'faq-heading': heading('<h2>Häufig gestellte Fragen</h2>', 'h3', 'center'),
                    'faq-accordion': accordion(PRODUCT_FAQ),
                },
                'block_order': ['faq-heading', 'faq-accordion'],
            }

    return order({'sections': sections})


# ---------------------------------------------------------------------------
# Collection
# ---------------------------------------------------------------------------

def collection_banner(*, disabled=False):
    """Shrines `main-collection-banner`: Titel und Beschreibung der Kollektion.

    Horizon hat dafuer keine Section. Ein `section`-Container mit dem eigenen
    Block `solena-collection-banner` liefert dasselbe; der Block liest das
    `collection`-Objekt direkt, statt sich auf Liquid in einem Text-Setting
    zu verlassen.
    """
    section = {
        'type': 'section',
        'settings': {
            'content_direction': 'column',
            'horizontal_alignment_flex_direction_column': 'flex-start',
            'gap': 12,
            'section_width': 'page-width',
            'padding-block-start': 48,
            'padding-block-end': 16,
        },
        'blocks': {
            'banner': {
                'type': 'solena-collection-banner',
                'settings': {
                    'show_title': True,
                    'heading_preset': 'h2',
                    'show_description': True,
                    'alignment': 'left',
                },
            },
        },
        'block_order': ['banner'],
    }
    if disabled:
        section['disabled'] = True
    return section


def collection_grid(*, secondary_image=True):
    return {
        'type': 'main-collection',
        'settings': {
            'layout_type': 'grid',
            'product_card_size': 'medium',
            'mobile_product_card_size': 'small',
            'enable_infinite_scroll': False,
            'products_per_page': 20,
            'product_grid_width': 'centered',
            'columns_gap_horizontal': 24,
            'columns_gap_vertical': 50,
            'padding-block-start': 32,
            'padding-block-end': 88,
        },
        'blocks': {
            'filters': {
                'type': 'filters',
                'static': True,
                'settings': {},
            },
            'product-card': product_card('product-card', 'square', rating=False, swatches=True),
        },
    }


def build_collection():
    return order({'sections': {
        'banner': collection_banner(),
        'main': collection_grid(secondary_image=False),
    }})


def build_collection_alle():
    return order({'sections': {
        'banner': collection_banner(disabled=True),
        'intro': rich_text([
            ('intro-heading', heading('<h2>Alle Produkte</h2>', 'h2', 'center')),
            ('intro-text', body(
                '<p>Entdecke unsere gesamte Auswahl an Haustierbedarf – von praktischem '
                'Zubehör bis hin zu sorgfältig ausgewählten Produkten für den Alltag. '
                'Wir legen Wert auf Qualität, Funktionalität und ein gutes '
                'Preis-Leistungs-Verhältnis.</p>', 'center')),
        ], width='full-width'),
        'main': collection_grid(),
    }})


# ---------------------------------------------------------------------------
# Cart, 404, Seiten
# ---------------------------------------------------------------------------

def build_cart():
    base = load('cart.json')
    cart_section = base['sections']['cart-section']
    cart_section['settings'] = dict(cart_section.get('settings', {}))
    cart_section['settings'].update({'padding-block-start': 40, 'padding-block-end': 32})
    return order({'sections': {
        'cart-section': cart_section,
        'alle_produkte': product_list(
            '<h2>Entdecke unsere Produkte</h2>', 'alleprodukte', 4, 4,
            card_ratio='square', rating=False, view_all='Alle ansehen', pad=(88, 88)),
        'you_may_also_like': dict(
            product_list('<h2>You may also like</h2>', 'all', 4, 4,
                         card_ratio='square', rating=False,
                         view_all='Alle ansehen', pad=(88, 88)),
            disabled=True),
        'newsletter': newsletter(disabled=True),
    }})


def build_404():
    base = load('404.json')
    main = base['sections'][next(iter(base['sections']))]
    main['settings'] = dict(main.get('settings', {}))
    return order({'sections': {
        'main': main,
        'newsletter': newsletter(disabled=True),
        'warum_solena': media_with_content(
            'shopify://shop_images/hf_20260830_175243_5e24df53-0fa5-4dd0-91b2-82c65fd85329.png',
            [
                ('ws-heading', heading('<h2>Warum Solena?</h2>', 'h2', 'left', 'fit-content')),
                ('ws-text', body(
                    '<p>Bei Solena glauben wir daran, dass Licht mehr sein kann als nur '
                    'Funktion – es soll Ruhe schaffen, Räume atmen lassen und Eleganz spürbar '
                    'machen. Inspiriert von der Klarheit und Zurückhaltung nordischer '
                    'Wohnkultur, steht jede Leuchte in unserer Kollektion für genau dieses '
                    'Gefühl von stiller Eleganz. Formen, die nicht laut sein wollen, sondern '
                    'zeitlos – für Räume, in denen jedes Detail zählt. Entdecke Beleuchtung, '
                    'die genau diesen Anspruch in dein Zuhause bringt.</p>', 'left')),
            ],
            media_position='right', media_width='narrow', media_height='60svh',
            background=BG2, pad=(96, 96), align='flex-start'),
    }})


def build_page():
    return order({'sections': {
        'main': {
            'type': 'main-page',
            'settings': {'gap': 24, 'padding-block-start': 64, 'padding-block-end': 64},
            'blocks': {'page-content': {'type': 'page-content', 'settings': {}}},
            'block_order': ['page-content'],
        },
        'gempages_page_1': gempages_slot('GemPages Platzhalter 1'),
        'gempages_page_2': gempages_slot('GemPages Platzhalter 2'),
        'trends': product_list(
            '<h2>Trends 2026</h2>', 'trends', 4, 4,
            card_ratio='square', rating=False, view_all='Alle ansehen', pad=(88, 88)),
    }})


def build_page_about():
    rows = [
        ('shopify://shop_images/hf_20260907_175757_f54a24f6-fb40-44cc-8fe1-af4446e6f516.png',
         'Weil Licht Räume verwandelt',
         '<p>Bei Solena glauben wir, dass die richtige Beleuchtung mehr ist als nur Funktion – '
         'sie schafft Atmosphäre, Wärme und Charakter. Von der eleganten Hängelampe bis zur '
         'dezenten Wegleuchte: Wir haben es uns zur Aufgabe gemacht, Beleuchtung zu bieten, '
         'die deinen Raum und deinen Garten wirklich zum Strahlen bringt. Jedes Produkt in '
         'unserem Sortiment wird sorgfältig ausgewählt, um höchsten Ansprüchen an Design und '
         'Qualität gerecht zu werden.</p>', 'left'),
        ('shopify://shop_images/composite_2bc7a3fc-ca7d-43f4-aff2-42df0fa777a4.png',
         'Wir setzen auf treue Kunden',
         '<p>In einer Welt, die ständig nach dem nächsten Klick, dem nächsten Käufer sucht, '
         'haben wir uns bewusst für einen anderen Weg entschieden. Uns geht es nicht darum, '
         'möglichst viele Menschen einmal zu überzeugen – uns geht es darum, dass du '
         'wiederkommst, weil du uns vertraust. Dieses Vertrauen erarbeiten wir uns jeden Tag '
         'neu: durch ehrlichen Service, echte Erreichbarkeit und die Gewissheit, dass wir '
         'hinter jedem Produkt stehen, das wir anbieten. Denn eine Marke, die man '
         'weiterempfiehlt, entsteht nicht durch Zufall – sie entsteht durch Beständigkeit. '
         'Genau das ist unser Versprechen an dich, heute und bei jedem Einkauf danach.</p>',
         'right'),
        ('shopify://shop_images/hf_20260907_184633_b3e0a333-5ed1-445e-9914-db1731aecf87.png',
         'Design kennt keine Grenzen – unser Blick auch nicht',
         '<p>Die schönsten Ideen entstehen nicht an einem einzigen Ort. Sie entstehen dort, wo '
         'Handwerk auf Mut trifft, wo Formen neu gedacht werden, wo Licht zur Kunst wird. '
         'Genau diesem Gespür folgen wir – über Länder und Stile hinweg, immer auf der Suche '
         'nach dem, was ein Zuhause wirklich besonders macht. Was wir finden, überzeugt uns '
         'nicht durch Trends allein, sondern durch echten Charakter. So entsteht ein '
         'Sortiment, das die Vielfalt der Design-Welt in dein Zuhause bringt.</p>', 'left'),
    ]
    sections = {
        'main': {
            'type': 'main-page',
            'settings': {'gap': 24, 'padding-block-start': 64, 'padding-block-end': 64},
            'blocks': {'page-content': {'type': 'page-content', 'settings': {}}},
            'block_order': ['page-content'],
        },
    }
    # Shrines `multirow` mit `image_layout: alternate-left`: die Bildseite
    # wechselt von Zeile zu Zeile. Horizon hat kein multirow, also eine
    # media-with-content-Section je Zeile.
    for i, (image, title, text, side) in enumerate(rows, start=1):
        sections['row_%d' % i] = media_with_content(
            image,
            [
                ('row-heading-%d' % i, heading('<h2>%s</h2>' % title, 'h2', 'left', 'fit-content')),
                ('row-text-%d' % i, body(text, 'left')),
            ],
            media_position='left' if side == 'left' else 'right',
            media_width='medium', media_height='60svh',
            pad=(44, 44), align='flex-start')
    return order({'sections': sections})


def build_page_contact():
    return order({'sections': {
        'main': {
            'type': 'main-page',
            'disabled': True,
            'settings': {'gap': 24, 'padding-block-start': 64, 'padding-block-end': 64},
            'blocks': {'page-content': {'type': 'page-content', 'settings': {}}},
            'block_order': ['page-content'],
        },
        'intro': rich_text([
            ('contact-heading', heading('<h1>Kontakt</h1>', 'h2', 'center')),
            ('contact-text', body(
                '<p>Du hast Fragen zu deiner Bestellung oder zu Produkten? <br/>'
                'Unser liebevolles Kundenservice Team steht dir gerne zur Seite.</p>',
                'center')),
        ], width='full-width'),
        'form': {
            'type': 'section',
            'settings': {
                'content_direction': 'column',
                'horizontal_alignment_flex_direction_column': 'center',
                'gap': 24,
                'section_width': 'page-width',
                'padding-block-start': 88,
                'padding-block-end': 88,
            },
            'blocks': {
                'contact-form': {
                    'type': 'contact-form',
                    'settings': {
                        'width': 'custom',
                        'custom_width': 60,
                        'width_mobile': 'custom',
                        'custom_width_mobile': 100,
                        'border_radius': 0,
                    },
                    'blocks': {
                        'submit': {
                            'type': 'contact-form-submit-button',
                            'static': True,
                            'settings': {},
                        },
                    },
                },
            },
            'block_order': ['contact-form'],
        },
        'details': rich_text([
            ('details-heading', heading('<h2>Kontaktinformationen</h2>', 'h3', 'center')),
            ('details-text', body(
                '<p>support@solenahome.com</p><p>Anschrift:</p>'
                '<p>Kärntnerstraße 1/B402</p><p>8020 Graz</p><p>Österreich</p>', 'center')),
        ], width='full-width'),
    }})


def build_page_faq():
    return order({'sections': {
        'main': {
            'type': 'main-page',
            'disabled': True,
            'settings': {'gap': 24, 'padding-block-start': 64, 'padding-block-end': 64},
            'blocks': {'page-content': {'type': 'page-content', 'settings': {}}},
            'block_order': ['page-content'],
        },
        'faq': {
            'type': 'section',
            'settings': {
                'content_direction': 'column',
                'horizontal_alignment_flex_direction_column': 'center',
                'gap': 24,
                'section_width': 'page-width',
                'background_color': BG2,
                'padding-block-start': 88,
                'padding-block-end': 88,
            },
            'blocks': {
                'faq-caption': {
                    'type': 'text',
                    'settings': {
                        'text': '<p>FAQ</p>',
                        'type_preset': 'custom',
                        'font': 'var(--font-body--family)',
                        'font_size': '0.75rem',
                        'letter_spacing': 'loose',
                        'case': 'uppercase',
                        'width': 'fit-content',
                        'alignment': 'center',
                    },
                },
                'faq-heading': heading('<h1>Häufig gestellte Fragen</h1>', 'h3', 'center'),
                'faq-accordion': accordion([
                    (PRODUCT_FAQ[0][0], PRODUCT_FAQ[0][1]),
                    ('Ist der Versand kostenlos?',
                     '<p>Ja, der Versand innerhalb Deutschlands ist kostenlos.</p>'),
                    (PRODUCT_FAQ[2][0], PRODUCT_FAQ[2][1]),
                    (PRODUCT_FAQ[3][0], PRODUCT_FAQ[3][1]),
                    (PRODUCT_FAQ[4][0], PRODUCT_FAQ[4][1]),
                    (PRODUCT_FAQ[5][0], PRODUCT_FAQ[5][1]),
                    (PRODUCT_FAQ[6][0], PRODUCT_FAQ[6][1]),
                    ('Wie kann ich euch erreichen?', '<p>support@solenahome.com</p>'),
                ]),
            },
            'block_order': ['faq-caption', 'faq-heading', 'faq-accordion'],
        },
        'details': rich_text([
            ('faq-details-heading', heading('<h2>Kontaktinformationen</h2>', 'h3', 'center')),
            ('faq-details-text', body('<p>support@solenahome.com</p>', 'center')),
            ('faq-details-button', button('Zur Kontaktseite', 'shopify://pages/contact')),
        ], width='full-width'),
    }})


def build_page_track_order():
    return order({'sections': {
        'main': {
            'type': 'main-page',
            'disabled': True,
            'settings': {'gap': 24, 'padding-block-start': 64, 'padding-block-end': 64},
            'blocks': {'page-content': {'type': 'page-content', 'settings': {}}},
            'block_order': ['page-content'],
        },
        'track': {
            'type': 'section',
            'settings': {
                'content_direction': 'column',
                'horizontal_alignment_flex_direction_column': 'center',
                'gap': 24,
                'section_width': 'page-width',
                'padding-block-start': 88,
                'padding-block-end': 88,
            },
            'blocks': {
                'track-order': {
                    'type': 'solena-track-order',
                    'settings': {
                        'heading': 'TRACK YOUR ORDER',
                        'heading_preset': 'h1',
                        'input_label': 'Tracking Number',
                        'button_label': 'Track Now',
                        'button_full_width': True,
                        'widget_language': 'de',
                        'widget_height': 560,
                        'max_width': 520,
                    },
                },
            },
            'block_order': ['track-order'],
        },
        'get_in_touch': dict(
            media_with_content(
                '',
                [
                    ('git-heading', heading('<h2>Get in touch!</h2>', 'h2', 'left', 'fit-content')),
                    ('git-text', body(
                        '<p>Pair text with an image to focus on your chosen product, '
                        'collection, or blog post. Add details on availability, style, or even '
                        'provide a review.</p>', 'left')),
                    ('git-button', button('Contact us', 'shopify://pages/contact')),
                ],
                media_position='left', media_width='medium', media_height='auto',
                pad=(96, 96), align='flex-start'),
            disabled=True),
    }})


# ---------------------------------------------------------------------------
# Blog, Artikel, Kollektionsliste, Suche, Passwort
# ---------------------------------------------------------------------------

def append_newsletter(name, *, disabled=False):
    """Haengt Shrines newsletter-Section an ein mitgeliefertes Template."""
    base = load(name)
    base['sections']['newsletter'] = newsletter(disabled=disabled)
    return order(base)


def build_search():
    base = load('search.json')
    results = base['sections']['main']
    results['blocks']['product-card'] = product_card('product-card', 'square', rating=False)
    base['sections']['newsletter'] = newsletter()
    return order(base)


def build_list_collections():
    base = load('list-collections.json')
    section = base['sections'][next(iter(base['sections']))]
    section['settings'] = dict(section.get('settings', {}))
    section['settings'].update({'columns': 3, 'mobile_columns': '2'})
    for blk in (section.get('blocks') or {}).values():
        if blk.get('type') == '_collection-card':
            for child in (blk.get('blocks') or {}).values():
                if child.get('type') == '_collection-card-image':
                    child.setdefault('settings', {})['image_ratio'] = 'square'
    # Shrines Ueberschrift der Seite
    for blk in (section.get('blocks') or {}).values():
        if blk.get('type') == 'group':
            for child in (blk.get('blocks') or {}).values():
                if child.get('type') == 'text':
                    child.setdefault('settings', {})['text'] = '<h1>Collections</h1>'
    base['sections']['newsletter'] = newsletter()
    return order(base)


def build_password():
    base = load('password.json')
    for section in base['sections'].values():
        for blk in (section.get('blocks') or {}).values():
            settings = blk.setdefault('settings', {})
            if blk.get('type') == 'text' and 'text' in settings:
                if settings['text'].startswith('<h'):
                    settings['text'] = '<h1>Opening soon</h1>'
                else:
                    settings['text'] = '<p>Be the first to know when we launch.</p>'
    return order(base)


# ---------------------------------------------------------------------------

print('Templates geschrieben nach %s/templates:' % ROOT)
write('index.json', build_index())
write('product.json', build_product())
write('collection.json', build_collection())
write('collection.alle.json', build_collection_alle())
write('cart.json', build_cart())
write('404.json', build_404())
write('page.json', build_page())
write('page.about-us.json', build_page_about())
write('page.contact.json', build_page_contact())
write('page.faq.json', build_page_faq())
write('page.track-order.json', build_page_track_order())
write('blog.json', append_newsletter('blog.json'))
write('article.json', append_newsletter('article.json'))
write('search.json', build_search())
write('list-collections.json', build_list_collections())
write('password.json', build_password())

premium = json.load(open(PREMIUM_CONTENT, encoding='utf-8'))
for name in sorted(premium):
    write('product.%s.json' % name, build_premium(name, premium[name]))
