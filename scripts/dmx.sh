#!/bin/bash
# Run CS2 dmxconvert under Proton. Usage: dmx.sh <args...>
STEAM=${STEAM:-$HOME/.local/share/Steam}
C="$STEAM/steamapps/common/Counter-Strike Global Offensive"
export STEAM_COMPAT_DATA_PATH=$STEAM/steamapps/compatdata/730
export STEAM_COMPAT_CLIENT_INSTALL_PATH=$STEAM
cd "$C/game/bin/win64"
"$STEAM/steamapps/common/Proton - Experimental/proton" run "$C/game/bin/win64/dmxconvert.exe" "$@"
