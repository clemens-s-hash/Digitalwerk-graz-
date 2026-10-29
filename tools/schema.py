"""Zeigt Settings, Optionen und Defaults eines Horizon-Section- oder -Blocks.

Aufruf:
  python3 -I tools/schema.py <theme> sections/slideshow
  python3 -I tools/schema.py <theme> blocks/text
  python3 -I tools/schema.py <theme> sections/marquee blocks/_slide ...
"""
import json, os, re, sys

ROOT = sys.argv[1]


def schema(path):
    text = open(path, encoding='utf-8').read()
    m = re.search(r'\{%-?\s*schema\s*-?%\}(.*?)\{%-?\s*endschema', text, re.S)
    if not m:
        return None
    return json.loads(re.sub(r',(\s*[}\]])', r'\1', m.group(1)))


for target in sys.argv[2:]:
    path = os.path.join(ROOT, target + '.liquid')
    d = schema(path)
    print('=' * 70)
    if d is None:
        print(target, '-> kein Schema')
        continue
    print('%s  name=%r  tag=%r' % (target, d.get('name'), d.get('tag', '')))
    print('  erlaubte Blocks:', [b.get('type') for b in d.get('blocks', [])])
    print('  Presets:', [p.get('name') for p in d.get('presets', [])])
    for s in d.get('settings', []):
        if s.get('type') in ('header', 'paragraph'):
            print('  --', s.get('content'))
            continue
        bits = ['  %-28s %-14s' % (s.get('id'), s.get('type'))]
        if s.get('options'):
            bits.append('opts=' + ','.join(str(o.get('value')) for o in s['options']))
        if 'default' in s:
            bits.append('default=%r' % (s['default'],))
        if s.get('min') is not None:
            bits.append('range=%s..%s' % (s['min'], s['max']))
        print(' '.join(bits))
