"""Liest die acht Premium-Produkt-Templates aus dem Shrine-Export aus.

Die acht unterscheiden sich nur in den drei image-with-text-Sections und
deren Position. rich-text, comparison-table, collapsible-content und
related-products sind in allen acht und in product.json identisch (per
Hash geprueft). Auch die drei collapsible_tab-Bloecke werden mitgelesen,
damit ein Abweichen auffaellt.

Ergebnis: tools/premium-content.json, von tools/templates.py gelesen.
So steht der Inhalt 1:1 im Repo, ohne von Hand abgeschrieben zu sein.

Aufruf: python3 -I tools/extract-premium.py <shrine-export> <ausgabedatei>
"""
import json, os, re, sys, glob

SRC, OUT = sys.argv[1], sys.argv[2]


def load(path):
    text = open(path, encoding='utf-8').read()
    return json.loads(re.sub(r'^\s*/\*.*?\*/\s*', '', text, flags=re.S))


result = {}
for path in sorted(glob.glob(os.path.join(SRC, 'templates', 'product.premium-*.json'))):
    name = os.path.basename(path)[len('product.'):-len('.json')]
    doc = load(path)

    rows, tabs = [], []
    # Reihenfolge der Sections, damit die image-with-text-Bloecke an
    # derselben Stelle wie im Original landen.
    order = []
    for sid in doc['order']:
        section = doc['sections'][sid]
        stype = section['type']

        if stype == 'image-with-text':
            settings = section['settings']
            entry = {
                'image': settings.get('image', ''),
                'layout': settings.get('layout', 'image_first'),
                'image_width': settings.get('desktop_image_width', 'medium'),
                'padding': [settings.get('padding_top', 96), settings.get('padding_bottom', 96)],
                'heading': '',
                'text': '',
                'button_label': '',
                'button_link': '',
            }
            for bid in section.get('block_order', []):
                block = section['blocks'][bid]
                if block.get('disabled'):
                    continue
                bs = block['settings']
                if block['type'] == 'heading':
                    entry['heading'] = bs.get('heading', '')
                elif block['type'] == 'text':
                    entry['text'] = bs.get('text', '')
                elif block['type'] == 'button':
                    entry['button_label'] = bs.get('button_label', '')
                    entry['button_link'] = bs.get('button_link', '')
            rows.append(entry)
            order.append('row')
        elif stype == 'main-product':
            order.append('main')
            for bid in section.get('block_order', []):
                block = section['blocks'][bid]
                if block['type'] != 'collapsible_tab':
                    continue
                bs = block['settings']
                tabs.append({
                    'heading': bs.get('heading', ''),
                    'icon': bs.get('icon', 'none'),
                    'content': bs.get('content', ''),
                    'disabled': bool(block.get('disabled')),
                })
        elif stype == 'related-products':
            order.append('related')
        elif stype == 'apps':
            order.append('apps')
        elif stype == 'rich-text':
            order.append('about')
        elif stype == 'comparison-table':
            order.append('comparison')
        elif stype == 'collapsible-content':
            order.append('faq')
        else:
            order.append(stype)

    result[name] = {'order': order, 'rows': rows, 'tabs': tabs}

with open(OUT, 'w', encoding='utf-8') as fh:
    json.dump(result, fh, indent=2, ensure_ascii=False, sort_keys=True)
    fh.write('\n')

for name, data in sorted(result.items()):
    print('%-10s  %d image-with-text, %d Aufklappbereiche, Reihenfolge: %s'
          % (name, len(data['rows']), len(data['tabs']), ' '.join(data['order'])))
