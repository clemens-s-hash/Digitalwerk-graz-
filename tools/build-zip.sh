#!/usr/bin/env bash
# Packt horizon/ als ZIP, das direkt in Shopify unter
# Online Store > Themes > Add theme > Upload zip file hochladbar ist.
#
# Shopify erwartet die acht Theme-Ordner auf der obersten Ebene des
# Archivs. Systemdateien (.DS_Store, __MACOSX, Thumbs.db) lehnt der Upload
# ab, deshalb werden sie ausgeschlossen.
#
# Der Dateiname bleibt bei jedem Lauf gleich und das Archiv wird mit
# committet, damit es sich ueber GitHub herunterladen laesst. Welcher
# Stand drinsteckt, steht in dist/BUILD.txt und in der Git-Historie.
#
# Aufruf:  tools/build-zip.sh
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
theme="$repo/horizon"
out_dir="$repo/dist"
zip_path="$out_dir/solena-horizon5.zip"

[ -d "$theme/config" ] || { echo "Kein Theme in $theme" >&2; exit 1; }

mkdir -p "$out_dir"
rm -f "$out_dir"/solena-horizon*.zip

cd "$theme"
zip -q -r -X "$zip_path" \
  assets blocks config layout locales sections snippets templates \
  -x '*.DS_Store' -x '__MACOSX/*' -x '*/Thumbs.db' -x '*.orig' -x '*.rej'

files="$(unzip -Z1 "$zip_path" | grep -vc '/$')"
top="$(unzip -Z1 "$zip_path" | cut -d/ -f1 | sort -u | tr '\n' ' ')"

cd "$repo"
{
  echo "Solena Horizon — Theme-Build"
  echo
  echo "Gebaut:       $(date '+%Y-%m-%d %H:%M %Z')"
  echo "Commit:       $(git rev-parse --short HEAD 2>/dev/null || echo '-')"
  echo "Branch:       $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo '-')"
  echo "Dateien:      $files"
  echo "Groesse:      $(du -h "$zip_path" | cut -f1)"
  echo "Oberste Ebene im Archiv: $top"
} > "$out_dir/BUILD.txt"

cat "$out_dir/BUILD.txt"
echo
echo "ZIP: $zip_path"
