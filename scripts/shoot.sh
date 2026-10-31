#!/bin/bash
# Take a CS2 screenshot from a fixed camera through the netcon port and save it as a PNG.
# Usage: shoot.sh <out.png> "<x y z>" "<pitch yaw roll>"
C="${STEAM:-$HOME/.local/share/Steam}/steamapps/common/Counter-Strike Global Offensive/game"
python3 -I "$(dirname "$0")/con.py" 2 "setpos $2" "setang $3" >/dev/null
sleep 1.5
before=$(ls -t "$C"/csgo_addons/*/screenshots/*.tga 2>/dev/null | head -1)
python3 -I "$(dirname "$0")/con.py" 2 "screenshot" >/dev/null
sleep 1
after=$(ls -t "$C"/csgo_addons/*/screenshots/*.tga 2>/dev/null | head -1)
[ "$after" != "$before" ] && python3 -I "$(dirname "$0")/shot2png.py" "$after" "$1" && echo "$1"
