#!/bin/bash
# Install a radar image for an addon map: PSD + vtex under panorama/images/overheadmaps, the overview
# txt (with T/CT spawn markers) under the game addon's resource/overviews, then compile the vtex.
# Usage: radar_install.sh <addon> <map> <image.png|.dds> <pos_x> <pos_y> <scale> "<T spawn x y>" "<CT spawn x y>"
set -e
addon=$1 map=$2 img=$3 px=$4 py=$5 sc=$6; read -r tx ty <<<"$7"; read -r cx cy <<<"$8"
C="${STEAM:-$HOME/.local/share/Steam}/steamapps/common/Counter-Strike Global Offensive"
O="$C/content/csgo_addons/$addon/panorama/images/overheadmaps"; mkdir -p "$O" "$C/game/csgo_addons/$addon/resource/overviews"
tmp=$(mktemp --suffix=.png); python3 -I -c "from PIL import Image; Image.open('$img').convert('RGBA').resize((1024,1024)).save('$tmp')"
python3 -I "$(dirname "$0")/psd.py" "$tmp" "$O/${map}_radar.psd"; rm -f "$tmp"
T=$(dirname "$0")/templates; [ -d "$T" ] || T=$(dirname "$0")/../templates
sed "s/aim_legocity_cs2/$map/g" "$T/radar_psd.vtex" > "$O/${map}_radar_psd.vtex"
frac() { python3 -I -c "print('%.3f' % ($1))"; }
cat > "$C/game/csgo_addons/$addon/resource/overviews/$map.txt" <<TXT
"$map"
{
	"material"		"overviews/$map"
	"pos_x"		"$px"
	"pos_y"		"$py"
	"scale"		"$sc"
	"rotate"		"0"
	"zoom"		"1.000000"

	"verticalsections"
	{
		"default"
		{
			"AltitudeMax" "10000"
			"AltitudeMin" "-10000"
		}
	}

	"CTSpawn_x"		"$(frac "($cx - $px) / ($sc * 1024)")"
	"CTSpawn_y"		"$(frac "($py - $cy) / ($sc * 1024)")"
	"TSpawn_x"		"$(frac "($tx - $px) / ($sc * 1024)")"
	"TSpawn_y"		"$(frac "($py - $ty) / ($sc * 1024)")"
}
TXT
"$(dirname "$0")/rc.sh" -game csgo -i "Z:$(printf '%s' "$O/${map}_radar_psd.vtex" | tr / '\\')" -f >/dev/null 2>&1
ls "$C/game/csgo_addons/$addon/panorama/images/overheadmaps/${map}_radar_psd.vtex_c"
