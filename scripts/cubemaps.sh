#!/bin/bash
# Launch an addon map, run buildcubemaps, and wait until the map's vpk has been rewritten with them.
# Leaves the game running (map reloaded, bots kicked, noclip camera ready for shoot.sh).
# Usage: cubemaps.sh <addon> <map> [mode]
cd "$(dirname "$0")"
C="${STEAM:-$HOME/.local/share/Steam}/steamapps/common/Counter-Strike Global Offensive/game/csgo_addons/$1/maps/$2.vpk"
before=$(stat -c %Y "$C")
setsid -f ./play.sh "$1" "$2" "${3:-casual}" -netconport 2121 >/dev/null 2>&1
sleep 30
until python3 -I con.py 1 status 2>/dev/null | grep -q "$2 |"; do sleep 5; done
sleep 10; ./focus_cs2.sh
python3 -I con.py 1 "sv_cheats 1" "bot_quota 0" "bot_kick" "buildcubemaps" >/dev/null
until [ "$(stat -c %Y "$C")" != "$before" ]; do sleep 5; done
sleep 15
until python3 -I con.py 1 status 2>/dev/null | grep -q "$2 |"; do sleep 5; done
sleep 10; ./focus_cs2.sh
python3 -I con.py 1 "sv_cheats 1" "bot_quota 0" "bot_kick" "mp_warmup_end" "jointeam 1" "noclip 1" "cl_drawhud 0" "r_drawviewmodel 0" >/dev/null
sleep 3
echo "cubemaps built into $2.vpk"
