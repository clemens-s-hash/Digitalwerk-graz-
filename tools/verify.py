"""Prueft das Horizon-Theme auf das, was `shopify theme check` nicht sieht.

  1. Alle JSON-Templates und Section-Groups parsen (Shopify erlaubt einen
     fuehrenden /* */-Kommentar, den json.load nicht kennt).
  2. Jede {% render %}- und {% include %}-Referenz zeigt auf ein Snippet,
     das existiert.
  3. Jede | asset_url-Referenz zeigt auf eine Datei in assets/.
  4. Jeder Section-Type in einem Template existiert in sections/.
  5. Jeder Block-Type in einem Template existiert in blocks/ und ist im
     Schema seines Elternteils erlaubt (@theme/@app werden aufgeloest).
  6. Jeder t:-Uebersetzungsschluessel in einem Schema existiert in
     locales/en.default.schema.json.

Aufruf: python3 -I verify.py <theme-verzeichnis>
"""
import json, os, re, sys
from collections import defaultdict

ROOT = sys.argv[1]
errors, warnings = [], []


def rel(p):
    return os.path.relpath(p, ROOT)


def strip_comments(text):
    """Entfernt // und /* */ ausserhalb von Strings.

    Shopify erlaubt beides in Templates und in locales/*.schema.json.
    """
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c == '"':
            j = i + 1
            while j < n:
                if text[j] == '\\':
                    j += 2
                    continue
                if text[j] == '"':
                    j += 1
                    break
                j += 1
            out.append(text[i:j])
            i = j
        elif text.startswith('//', i):
            i = text.find('\n', i)
            if i == -1:
                break
        elif text.startswith('/*', i):
            end = text.find('*/', i + 2)
            i = n if end == -1 else end + 2
        else:
            out.append(c)
            i += 1
    return ''.join(out)


def load_jsonc(path):
    return json.loads(strip_comments(open(path, encoding='utf-8').read()))


def liquid_schema(path):
    text = open(path, encoding='utf-8').read()
    m = re.search(r'\{%-?\s*schema\s*-?%\}(.*?)\{%-?\s*endschema', text, re.S)
    if not m:
        return None
    raw = re.sub(r',(\s*[}\]])', r'\1', m.group(1))
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        errors.append('%s: Schema ist kein valides JSON (%s)' % (rel(path), exc))
        return None


def listing(folder, suffix='.liquid'):
    d = os.path.join(ROOT, folder)
    if not os.path.isdir(d):
        return set()
    return {f[: -len(suffix)] for f in os.listdir(d) if f.endswith(suffix)}


snippets = listing('snippets')
sections = listing('sections') | listing('sections', '.json')
blocks = listing('blocks')
assets = set(os.listdir(os.path.join(ROOT, 'assets')))

liquid_files = []
for folder in ('sections', 'snippets', 'blocks', 'layout', 'templates'):
    d = os.path.join(ROOT, folder)
    for base, _, files in os.walk(d):
        for f in files:
            if f.endswith('.liquid'):
                liquid_files.append(os.path.join(base, f))

# --- 1. JSON-Templates und Section-Groups -----------------------------------
json_docs = {}
for folder in ('templates', 'sections', 'config'):
    d = os.path.join(ROOT, folder)
    for base, _, files in os.walk(d):
        for f in files:
            if not f.endswith('.json'):
                continue
            p = os.path.join(base, f)
            try:
                json_docs[p] = load_jsonc(p)
            except json.JSONDecodeError as exc:
                errors.append('%s: kein valides JSON (%s)' % (rel(p), exc))

# --- 2./3. render- und asset_url-Referenzen ---------------------------------
RENDER = re.compile(r"\{%-?\s*(?:render|include)\s+'([^']+)'")
ASSET = re.compile(r"'([^']+?)'\s*\|\s*(?:asset_url|asset_img_url)")

DOCBLOCK = re.compile(r'\{%-?\s*(doc|comment)\s*-?%\}.*?\{%-?\s*end\1\s*-?%\}', re.S)

for p in liquid_files:
    # {% doc %}-Beispiele und {% comment %}-Bloecke zaehlen nicht als Referenz.
    text = DOCBLOCK.sub('', open(p, encoding='utf-8').read())
    for name in RENDER.findall(text):
        if '{{' in name or '[' in name:
            continue
        if name not in snippets:
            errors.append("%s: render '%s' — snippets/%s.liquid fehlt" % (rel(p), name, name))
    for name in ASSET.findall(text):
        if '{{' in name:
            continue
        if name not in assets:
            errors.append("%s: asset_url '%s' — assets/%s fehlt" % (rel(p), name, name))

# --- 4./5. Section- und Block-Types in Templates ----------------------------
schemas = {}
for name in sections:
    p = os.path.join(ROOT, 'sections', name + '.liquid')
    if os.path.exists(p):
        schemas[('section', name)] = liquid_schema(p)
for name in blocks:
    schemas[('block', name)] = liquid_schema(os.path.join(ROOT, 'blocks', name + '.liquid'))


STATIC_CHILD = re.compile(r"content_for\s+'block'[^%]*?type:\s*'([^']+)'")


def static_children(kind, name):
    """Block-Types, die das Element per {% content_for 'block' %} selbst setzt.

    Statische Blocks stehen nicht im `blocks`-Array des Schemas, tauchen in
    den Templates aber auf. Sie sind erlaubt, wenn das Liquid sie aufruft.
    """
    folder = 'sections' if kind == 'section' else 'blocks'
    p = os.path.join(ROOT, folder, name + '.liquid')
    if not os.path.exists(p):
        return set()
    return set(STATIC_CHILD.findall(open(p, encoding='utf-8').read()))


def allowed_children(kind, name):
    """Welche Block-Types darf dieses Element enthalten? None = unbekannt."""
    schema = schemas.get((kind, name))
    if schema is None:
        return None
    out, has_theme = static_children(kind, name), False
    for entry in schema.get('blocks', []):
        t = entry.get('type')
        if t == '@theme':
            has_theme = True
        elif t == '@app':
            out.add('@app')
        elif t:
            out.add(t)
    if has_theme:
        out |= {b for b in blocks if not b.startswith('_')}
    return out


def check_limits(container_kind, container_name, node, where):
    """Prueft max_blocks der Section und `limit` je Block-Type.

    Shopify lehnt beim Upload ab, was darueber liegt; `theme check` nicht.
    """
    schema = schemas.get((container_kind, container_name))
    if schema is None:
        return
    children = node.get('blocks') or {}

    max_blocks = schema.get('max_blocks')
    if max_blocks and len(children) > max_blocks:
        errors.append('%s: %s "%s" hat %d Blocks, erlaubt sind %d (max_blocks)'
                      % (where, container_kind, container_name, len(children), max_blocks))

    limits = {e['type']: e['limit'] for e in schema.get('blocks', [])
              if e.get('limit') and e.get('type')}
    if not limits:
        return
    counts = defaultdict(int)
    for blk in children.values():
        counts[blk.get('type')] += 1
    for btype, limit in limits.items():
        if counts[btype] > limit:
            errors.append('%s: %s "%s" hat %d Blocks vom Typ "%s", erlaubt ist %d (limit)'
                          % (where, container_kind, container_name,
                             counts[btype], btype, limit))


def check_blocks(container_kind, container_name, node, where):
    allowed = allowed_children(container_kind, container_name)
    check_limits(container_kind, container_name, node, where)
    for bid, blk in (node.get('blocks') or {}).items():
        btype = blk.get('type', '')
        if btype.startswith('shopify://apps/'):
            if allowed is not None and '@app' not in allowed:
                warnings.append('%s: App-Block %s in %s, das keine @app-Blocks erlaubt'
                                % (where, bid, container_name))
            continue
        if btype not in blocks:
            errors.append('%s: Block-Type "%s" (%s) — blocks/%s.liquid fehlt'
                          % (where, btype, bid, btype))
            continue
        if allowed is not None and btype not in allowed:
            errors.append('%s: Block-Type "%s" ist in %s "%s" nicht erlaubt (%s)'
                          % (where, btype, container_kind, container_name, sorted(allowed)))
        check_blocks('block', btype, blk, where)


def context_of(path):
    """Wo wird diese JSON-Datei gerendert? ('group', <name>) oder ('template', <name>)."""
    base = os.path.basename(path)
    if path.startswith(os.path.join(ROOT, 'sections')) and base.endswith('-group.json'):
        return 'group', base[: -len('-group.json')]
    if path.startswith(os.path.join(ROOT, 'templates')):
        return 'template', base.split('.')[0]
    return None, None


def check_placement(stype, where, kind, name):
    """Prueft enabled_on / disabled_on des Section-Schemas.

    Horizon sperrt einige Sections fuer die Header- und Footer-Gruppe oder
    bindet sie an bestimmte Templates. Shopify lehnt das beim Upload ab,
    `theme check` sieht es nicht.
    """
    schema = schemas.get(('section', stype))
    if schema is None or kind is None:
        return
    key = 'groups' if kind == 'group' else 'templates'

    enabled = schema.get('enabled_on')
    if enabled is not None:
        allowed_here = enabled.get(key)
        if allowed_here is None:
            if enabled.get('groups' if key == 'templates' else 'templates') is not None:
                errors.append('%s: Section "%s" ist nur fuer %s zugelassen, nicht fuer %s "%s"'
                              % (where, stype, enabled, kind, name))
            return
        if name not in allowed_here:
            errors.append('%s: Section "%s" ist nur in %s %s zugelassen, nicht in "%s"'
                          % (where, stype, key, allowed_here, name))

    disabled = schema.get('disabled_on')
    if disabled is not None and name in (disabled.get(key) or []):
        errors.append('%s: Section "%s" ist in %s "%s" gesperrt (disabled_on %s)'
                      % (where, stype, kind, name, disabled))


for p, doc in json_docs.items():
    if not isinstance(doc, dict) or 'sections' not in doc:
        continue
    where = rel(p)
    kind, ctx_name = context_of(p)
    for sid, sec in doc['sections'].items():
        stype = sec.get('type', '')
        if stype not in sections:
            errors.append('%s: Section-Type "%s" (%s) — sections/%s.liquid fehlt'
                          % (where, stype, sid, stype))
            continue
        if stype.startswith('_'):
            # Sections mit fuehrendem Unterstrich sind privat. Horizon setzt
            # sie nur per {% content_for %} ein, nie als Top-Level-Section;
            # Shopify rendert die Seite sonst nicht.
            errors.append('%s: "%s" (%s) ist eine private Section und darf nicht '
                          'als Top-Level-Section stehen' % (where, stype, sid))
        check_placement(stype, where, kind, ctx_name)
        check_blocks('section', stype, sec, where)
    for sid in doc.get('order', []):
        if sid not in doc['sections']:
            errors.append('%s: order nennt "%s", das nicht in sections steht' % (where, sid))
    for sid, sec in doc['sections'].items():
        for bid in sec.get('block_order', []):
            if bid not in (sec.get('blocks') or {}):
                errors.append('%s/%s: block_order nennt "%s", das nicht in blocks steht'
                              % (where, sid, bid))

# --- 6. Uebersetzungsschluessel ---------------------------------------------
def flatten(d, prefix=''):
    out = set()
    for k, v in d.items():
        key = prefix + k
        if isinstance(v, dict):
            out |= flatten(v, key + '.')
        else:
            out.add(key)
    return out


schema_keys = set()
sp = os.path.join(ROOT, 'locales', 'en.default.schema.json')
if os.path.exists(sp):
    schema_keys = flatten(load_jsonc(sp))

T_KEY = re.compile(r'"(t:[a-zA-Z0-9_.\[\]-]+)"')
missing_t = defaultdict(list)
for name in sorted(sections | blocks):
    for folder in ('sections', 'blocks'):
        p = os.path.join(ROOT, folder, name + '.liquid')
        if not os.path.exists(p):
            continue
        text = open(p, encoding='utf-8').read()
        m = re.search(r'\{%-?\s*schema\s*-?%\}(.*?)\{%-?\s*endschema', text, re.S)
        if not m:
            continue
        for key in T_KEY.findall(m.group(1)):
            if key[2:] not in schema_keys:
                missing_t[rel(p)].append(key)
for p, keys in sorted(missing_t.items()):
    errors.append('%s: Uebersetzungsschluessel fehlt in locales/*.schema.json: %s'
                  % (p, ', '.join(sorted(set(keys)))))

# --- Ausgabe ----------------------------------------------------------------
print('Geprueft: %d Liquid-Dateien, %d JSON-Dokumente, %d Sections, %d Blocks, %d Assets'
      % (len(liquid_files), len(json_docs), len(sections), len(blocks), len(assets)))
for w in warnings:
    print('  WARNUNG  ' + w)
for e in errors:
    print('  FEHLER   ' + e)
print('%d Fehler, %d Warnungen' % (len(errors), len(warnings)))
sys.exit(1 if errors else 0)
