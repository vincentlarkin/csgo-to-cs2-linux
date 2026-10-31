#!/bin/bash
# Compile every .vmat under an addon's content folder one at a time, retrying crashes.
# One bad material then only costs that file, and the list of FAILED ones is easy to read.
# Usage: rc_each.sh <addon> [subdir, default materials]
C="${STEAM:-$HOME/.local/share/Steam}/steamapps/common/Counter-Strike Global Offensive"
G="$C/game/csgo_addons/$1"; fail=0
find "$C/content/csgo_addons/$1/${2:-materials}" -name '*.vmat' | sort | while read -r f; do
    out="$G/${f#$C/content/csgo_addons/$1/}_c"
    [ -f "$out" ] && [ "$out" -nt "$f" ] && continue
    for try in 1 2 3; do
        "$(dirname "$0")/rc_direct.sh" -game csgo -i "Z:$(printf '%s' "$f" | tr / '\\')" -f >/dev/null 2>&1 && break
    done
    [ -f "$out" ] || echo "FAILED ${f#$C/}"
done
