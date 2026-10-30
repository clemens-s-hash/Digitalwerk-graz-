"""Prueft ein JSON-Template Setting fuer Setting gegen die echten Schemas.

`verify.py` prueft, dass es jede Section und jeden Block gibt. Dieses Skript
geht eine Stufe tiefer und prueft den Inhalt:

  1. Die Datei parst mit json.load, ohne Vorverarbeitung (reines JSON ab `{`).
  2. Jeder Setting-Schluessel kommt im Schema seines Section- oder
     Block-Typs vor.
  3. Jeder select-Wert ist eine echte Option, jeder range-Wert liegt in
     min..max und auf dem step, jede checkbox ist ein Bool, jede
     text_alignment ist left/center/right.
  4. Jeder Block ist im `blocks`-Schema seines Elternteils erlaubt
     (@theme wird aufgeloest, statische Bloecke sind ausgenommen).
  5. `order` und jede `block_order` nennen nur vorhandene IDs, und jeder
     nicht statische Block steht in seiner `block_order`.

Aufruf:  python3 -I tools/check-template.py horizon horizon/templates/index.json
"""
import json, os, re, sys

ROOT = sys.argv[1]
TPL = sys.argv[2]
errors = []
_cache = {}


def schema(kind, name):
    key = (kind, name)
    if key not in _cache:
        path = os.path.join(ROOT, kind, name + '.liquid')
        found = None
        if os.path.exists(path):
            text = open(path, encoding='utf-8').read()
            m = re.search(r'\{%-?\s*schema\s*-?%\}(.*?)\{%-?\s*endschema', text, re.S)
            if m:
                found = json.loads(m.group(1))
        _cache[key] = found
    return _cache[key]


def allowed_blocks(d):
    """Erlaubte Block-Typen eines Schemas. @theme wird aufgeloest, @app nicht."""
    out = set()
    for b in (d or {}).get('blocks', []) or []:
        t = b.get('type')
        if t == '@theme':
            out |= {f[:-7] for f in os.listdir(os.path.join(ROOT, 'blocks'))
                    if f.endswith('.liquid') and not f.startswith('_')}
        elif t and t != '@app':
            out.add(t)
    return out


def check_settings(where, d, settings):
    defs = {s['id']: s for s in (d or {}).get('settings', []) if 'id' in s}
    for key, value in (settings or {}).items():
        if key not in defs:
            errors.append(f'{where}: Setting "{key}" gibt es im Schema nicht')
            continue
        spec = defs[key]
        kind = spec['type']
        if kind == 'select':
            options = [o['value'] for o in spec.get('options', [])]
            if value not in options:
                errors.append(f'{where}: {key}={value!r} ist keine Option ({options})')
        elif kind == 'range':
            if not spec['min'] <= value <= spec['max']:
                errors.append(f'{where}: {key}={value!r} liegt nicht in '
                              f'{spec["min"]}..{spec["max"]}')
            elif (value - spec['min']) % spec.get('step', 1):
                errors.append(f'{where}: {key}={value!r} passt nicht zu '
                              f'step {spec.get("step", 1)}')
        elif kind == 'checkbox':
            if not isinstance(value, bool):
                errors.append(f'{where}: {key}={value!r} ist kein true/false')
        elif kind == 'text_alignment':
            if value not in ('left', 'center', 'right'):
                errors.append(f'{where}: {key}={value!r} ist keine Ausrichtung')


def walk(where, parent_schema, blocks, order):
    allowed = allowed_blocks(parent_schema)
    for bid, block in (blocks or {}).items():
        btype = block['type']
        d = schema('blocks', btype)
        if d is None:
            errors.append(f'{where} > {bid}: Block "{btype}" hat keine Datei oder kein Schema')
            continue
        if btype not in allowed and not block.get('static'):
            errors.append(f'{where} > {bid}: Block "{btype}" ist hier nicht erlaubt')
        check_settings(f'{where} > {bid} ({btype})', d, block.get('settings'))
        walk(f'{where} > {bid}', d, block.get('blocks'), block.get('block_order'))
    for bid in (order or []):
        if bid not in (blocks or {}):
            errors.append(f'{where}: block_order nennt "{bid}", den es nicht gibt')
    for bid, block in (blocks or {}).items():
        if not block.get('static') and bid not in (order or []):
            errors.append(f'{where}: Block "{bid}" fehlt in block_order')


raw = open(TPL, encoding='utf-8').read()
note = ''
if not raw.startswith('{'):
    # Shopify erlaubt einen fuehrenden /* */-Block. Fuer index.json wollten
    # wir reines JSON, die uebrigen Templates tragen ihn weiterhin.
    note = ' (mit fuehrendem Kommentarblock)'
    raw = re.sub(r'^\s*/\*.*?\*/', '', raw, flags=re.S)
try:
    doc = json.loads(raw)
except json.JSONDecodeError as exc:
    print(f'{TPL}: kein gueltiges JSON — {exc}')
    sys.exit(1)

for sid, section in doc['sections'].items():
    d = schema('sections', section['type'])
    if d is None:
        errors.append(f'{sid}: Section "{section["type"]}" hat keine Datei oder kein Schema')
        continue
    check_settings(f'{sid} ({section["type"]})', d, section.get('settings'))
    walk(sid, d, section.get('blocks'), section.get('block_order'))

for sid in doc['order']:
    if sid not in doc['sections']:
        errors.append(f'order nennt "{sid}", den es nicht gibt')
for sid in doc['sections']:
    if sid not in doc['order']:
        errors.append(f'Section "{sid}" fehlt in order')

if errors:
    print('\n'.join(errors))
    sys.exit(1)
print(f'{TPL}: {len(doc["sections"])} Sections, keine Befunde.{note}')
