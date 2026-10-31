#!/bin/bash
# Launch CS2 Workshop Tools and load an addon map in a given game mode.
# Usage: play.sh <addon> <map> [casual|competitive|deathmatch|custom] [extra cs2 args...]
# The map is loaded from a generated cfg because Proton quotes "+map x nomapvalidation=true",
# which the map command then rejects as malformed options.
STEAM=${STEAM:-$HOME/.local/share/Steam}
C="$STEAM/steamapps/common/Counter-Strike Global Offensive"
export STEAM_COMPAT_DATA_PATH=$STEAM/steamapps/compatdata/730
export STEAM_COMPAT_CLIENT_INSTALL_PATH=$STEAM
export SteamAppId=730 SteamGameId=730
# Hammer bakes lighting in-process; without this its denoiser calls CUDA, which Proton lacks, and crashes.
export OIDN_DEVICE_CUDA=0
addon=$1 map=$2; shift 2
mode=competitive
case "$1" in casual|competitive|deathmatch|custom) mode=$1; shift;; esac
case $mode in   # game_type/game_mode values from gamemodes.txt
    casual) gt=0 gm=0;; competitive) gt=0 gm=1;; deathmatch) gt=1 gm=2;; custom) gt=3 gm=0;;
esac
mkdir -p "$C/game/csgo_addons/$addon/cfg"
printf 'game_type %s\ngame_mode %s\nmap %s nomapvalidation=true\n' $gt $gm "$map" > "$C/game/csgo_addons/$addon/cfg/load_$map.cfg"
cd "$C/game/bin/win64"
exec "$STEAM/steamapps/common/Proton - Experimental/proton" run "$C/game/bin/win64/cs2.exe" -steam -retail -tools -vulkan -addon "$addon" -condebug +exec "load_$map" "$@"
