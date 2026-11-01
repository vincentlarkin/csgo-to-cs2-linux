#!/bin/bash
# Import a staged Source 1 map into a CS2 addon: the map pass, then the material/model pass driven by
# the importer's own <map>_refs.txt.
# Usage: import_map.sh <stage dir holding csgo/ and s1content/maps/<map>.vmf> <addon> <map (without .vmf)>
set -e
stage=$(realpath "$1") addon=$2 map=$3
C="${STEAM:-$HOME/.local/share/Steam}/steamapps/common/Counter-Strike Global Offensive"
z() { printf 'Z:%s' "$1" | tr / '\\'; }
mkdir -p "$C/content/csgo_addons/$addon" "$C/game/csgo_addons/$addon"
"$(dirname "$0")/import.sh" -retail -nop4 -nop4sync -logwarnings -src1gameinfodir "$(z "$stage/csgo")" \
    -src1contentdir "$(z "$stage/s1content")" -s2addon "$addon" -game csgo "maps\\$map.vmf" > "$stage/import.log" 2>&1
cp "$C/content/csgo_addons/$addon/maps/${map}_refs.txt" "$stage/refs.txt"
"$(dirname "$0")/import.sh" -retail -nop4 -nop4sync -logwarnings -src1gameinfodir "$(z "$stage/csgo")" \
    -s2addon "$addon" -game csgo -usefilelist "$(z "$stage/refs.txt")" > "$stage/import_mats.log" 2>&1
# -logwarnings writes its logs into the *game* addon folder, which Workshop Tools uploads; they hold local paths
mv "$C/game/csgo_addons/$addon"/source1import*.txt "$stage/" 2>/dev/null || true
echo "imported $(find "$C/content/csgo_addons/$addon" -type f | wc -l) files into content/csgo_addons/$addon"
