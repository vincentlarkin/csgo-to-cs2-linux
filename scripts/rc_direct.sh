#!/bin/bash
# Run resourcecompiler.exe with Proton's wine directly so its console output stays in this terminal.
STEAM=${STEAM:-$HOME/.local/share/Steam}
P="$STEAM/steamapps/common/Proton - Experimental/files"
C="$STEAM/steamapps/common/Counter-Strike Global Offensive"
export WINEPREFIX=$STEAM/steamapps/compatdata/730/pfx WINEDEBUG=-all
# Proton normally sets these; without them wine uses its builtin wined3d (OpenGL), which crashes resourcecompiler on GPU work
export WINEDLLOVERRIDES="d3d11,d3d10core,dxgi,d3d12,d3d12core,d3d9=n"
export PATH="$P/bin:$PATH" WINEDLLPATH="$P/lib/wine:$P/lib64/wine"
cd "$C/game/bin/win64"
exec "$P/bin/wine" "$C/game/bin/win64/resourcecompiler.exe" "$@"
