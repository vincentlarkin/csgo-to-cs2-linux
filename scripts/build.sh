#!/bin/bash
# Full CS2 map build (geometry, physics, vis, nav, baked lighting). Usage: build.sh <addon> <mapname>
# PRESET=test   quick look: 512 lightmaps at draft quality (minutes instead of tens of minutes)
# PRESET=final  release, like Hammer's Final Compile: 2048 lightmaps at final quality
# (default is Hammer's Full Compile: 1024 at standard quality). LIGHTMAP_RES/LIGHTMAP_QUALITY override.
# NOVIS=1 skips the visibility step; for small open maps whose 3D sky gets culled by vis.
# RC=rc_direct.sh runs the compiler through wine directly so its log prints to the terminal; THREADS=n caps threads.
case "$PRESET" in
    test) res=512 quality=0 ;; final) res=2048 quality=2 ;; *) res=1024 quality=1 ;;
esac
res=${LIGHTMAP_RES:-$res} quality=${LIGHTMAP_QUALITY:-$quality}
vis=-vis; [ "$NOVIS" = 1 ] && vis=
C="${STEAM:-$HOME/.local/share/Steam}/steamapps/common/Counter-Strike Global Offensive"
# resourcecompiler is a Windows program: hand it the vmap as a Wine Z: drive path
V="Z:$(printf '%s' "$C/content/csgo_addons/$1/maps/$2.vmap" | tr / '\\')"
OIDN_DEVICE_CUDA=0 exec "$(dirname "$0")/${RC:-rc.sh}" -threads ${THREADS:-$(nproc)} -fshallow -maxtextureres 256 -dxlevel 110 -unbufferedio -noassert \
  -i "$V" -world -phys $vis -nav -gridnav -nompi -nop4 \
  -bakelighting -lightmapMaxResolution $res -lightmapVRadQuality $quality -lightmapCompressionDisabled 0 -lightmapDisableFiltering 0
