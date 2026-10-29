#!/usr/bin/env bash
# Packt horizon/ als ZIP, das direkt in Shopify unter
# Online Store > Themes > Add theme > Upload zip file hochladbar ist.
#
# Shopify erwartet die sieben Theme-Ordner auf der obersten Ebene des
# Archivs. Systemdateien (.DS_Store, __MACOSX, Thumbs.db) lehnt der Upload
# ab, deshalb werden sie ausgeschlossen.
#
# Aufruf:  tools/build-zip.sh [zielverzeichnis]
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
theme="$repo/horizon"
out_dir="${1:-$repo/dist}"
stamp="$(date +%Y%m%d-%H%M)"
zip_path="$out_dir/solena-horizon-$stamp.zip"

[ -d "$theme/config" ] || { echo "Kein Theme in $theme" >&2; exit 1; }

mkdir -p "$out_dir"
rm -f "$zip_path"

cd "$theme"
zip -q -r -X "$zip_path" \
  assets blocks config layout locales sections snippets templates \
  -x '*.DS_Store' -x '__MACOSX/*' -x '*/Thumbs.db' -x '*.orig' -x '*.rej'

# Gegenprobe: liegen die Ordner wirklich auf der obersten Ebene?
top="$(unzip -Z1 "$zip_path" | cut -d/ -f1 | sort -u | tr '\n' ' ')"
echo "ZIP:      $zip_path"
echo "Groesse:  $(du -h "$zip_path" | cut -f1)"
echo "Dateien:  $(unzip -Z1 "$zip_path" | grep -vc '/$')"
echo "Oberste Ebene: $top"
