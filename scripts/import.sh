#!/bin/bash
# Run CS2's source1import.exe under Proton. Usage: import.sh <source1import args...>
STEAM=${STEAM:-$HOME/.local/share/Steam}
C="$STEAM/steamapps/common/Counter-Strike Global Offensive"
export STEAM_COMPAT_DATA_PATH=$STEAM/steamapps/compatdata/730
export STEAM_COMPAT_CLIENT_INSTALL_PATH=$STEAM
cd "$C/game/csgo/import_scripts"
"$STEAM/steamapps/common/Proton - Experimental/proton" run "$C/game/bin/win64/source1import.exe" "$@"
