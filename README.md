# csgo-to-cs2-linux

These are notes and scripts for porting old CS:GO Workshop maps to CS2 on a Linux box with no Windows PC.

Valve's Workshop Tools (source1import, resourcecompiler, dmxconvert and CS2 itself) run under Proton. Everything here drives them from the shell. The vmap edits that would normally need Hammer clicks are done on the KeyValues2 text form, so a whole port can be built, lit, tested and screenshotted headlessly.

Maps ported with this so far:

| CS2 map | Original | Notes |
| --- | --- | --- |
| `awp_neon_cs2` | awp_neon by Pr0F | AWP-only Custom mode via cs_script, buy zones, probes, nav |
| `aim_pyrocynical_cs2` | [aim_pyrocynical](https://steamcommunity.com/sharedfiles/filedetails/?id=630383830) by Lefty | 3D-sky horizon painted into the panorama, displacements rebuilt, music, decals |
| `aim_legocity_cs2` | [AIM DEAGLE](https://steamcommunity.com/sharedfiles/filedetails/?id=1564248936) by Bunny | Deagle Custom mode, radar, lighting rebalanced to the original's look |

**[FINDINGS.md](FINDINGS.md) is the useful part.** It lists every gotcha hit along the way and what fixed it.

## Requirements

- CS2 with the **Counter-Strike 2 Workshop Tools** DLC. In Steam > CS2 > Properties > Compatibility, force **Proton Experimental**, so the Windows tools get installed and can run.
- Python 3 with Pillow. Java 17+ for BSPSource.
- [BSPSource](https://github.com/ata4/bspsrc), for decompiling the BSP to a VMF. `scripts/bspsrc.sh` runs it on native Java: unzip the Windows release and copy the module folders (`info.ata4.bspsrc.*`, `org.apache.*`, `info.picocli`, ...) into `tools/bspsrc_mods/`, or point `BSPSRC_MODS` at them.

The wrappers assume Steam is in `~/.local/share/Steam`. Set `STEAM=/path/to/Steam` to override.

## Pipeline

```
legacy Workshop .bin  ──unzip──▶  map.bsp
map.bsp  ──bspsrc.sh──▶  map_d.vmf + embedded materials/sounds
map_d.vmf  ──vmf_add_header.py──▶  importable VMF
stage/{csgo,s1content}  ──import.sh (source1import)──▶  content/csgo_addons/<addon>/maps/<map>.vmap + prefabs
prefabs  ──dmx.sh──▶  KeyValues2 text  ──vmap_*.py / disp2mesh.py / hand edits──▶  dmx.sh back to binary
<map>.vmap  ──build.sh (resourcecompiler)──▶  game/csgo_addons/<addon>/maps/<map>.vpk
play.sh  ──▶  CS2 tools mode; buildcubemaps; shoot.sh for screenshots
Workshop Tools  ──▶  publish
```

1. **Decompile.** An old Workshop download sits in `steamapps/workshop/content/730/<id>/` as a `.bin`, which is a zip holding the `.bsp`. Run `bspsrc.sh -o out.vmf map.bsp`. Have BSPSource unpack the embedded files too.
2. **Stage for the importer.** Make a folder called exactly `csgo`, holding a `gameinfo.txt` like the one below plus the map's custom materials, models and sounds. Make a second folder whose `maps/` holds the VMF. Run `vmf_add_header.py` on the VMF first.
   ```
   "GameInfo" { "game" "port" "type" "multiplayer_only"
     FileSystem { "SteamAppId" "730" SearchPaths { "Game" "|gameinfo_path|." } } }
   ```
3. **Import.** Paths are Wine `Z:` paths:
   ```
   import.sh -retail -nop4 -nop4sync -logwarnings \
     -src1gameinfodir 'Z:\home\you\stage\csgo' -src1contentdir 'Z:\home\you\stage\s1content' \
     -s2addon <addon> -game csgo 'maps\<map>_d.vmf'
   ```
4. **Fix up.** Convert the vmap and its prefabs to text (`dmx.sh -i 'Z:\...\x.vmap' -o 'Z:\...\x.txt' -oe keyvalues2`, and back with `-oe binary`; the wrappers `cd` into the game's bin folder, so always pass full `Z:` paths) and edit them:
   - add a light probe volume, light_environment and nav seeds (`vmap_add_entity.py`)
   - add buy zones (`vmap_add_buyzone.py`)
   - rebuild displacements (`disp2mesh.py`)
   - remove broken entities (`vmap_drop_entities.py`)
   - write proper `csgo_complex` vmats where the importer's look wrong

   See FINDINGS.md for why each is needed.

   Compile single assets (vmat, vtex, vsndevts, the `.js` rules script) with `rc.sh -game csgo -i 'Z:\...\file' -f`.
5. **Build.** `PRESET=test NOVIS=1 build.sh <addon> <map>` gives a 25-second preview. Use `PRESET=final` for release.
6. **Test.** `play.sh <addon> <map> custom -netconport 2121`. Then run `buildcubemaps` in the console. Don't skip it.
7. **Screenshot.** `con.py 2 "sv_cheats 1" "noclip" "cl_drawhud 0" "r_drawviewmodel 0"`, then `shoot.sh out.png "x y z" "pitch yaw 0"`.
8. **Publish** from the Workshop Tools window, after the pre-publish checks in FINDINGS.md.

## Scripts

| Script | What it does |
| --- | --- |
| `import.sh`, `rc.sh`, `dmx.sh` | Run source1import / resourcecompiler / dmxconvert under Proton |
| `build.sh` | Headless map compile: geometry, physics, vis, nav and baked lighting. `PRESET=test\|final`, `NOVIS=1` |
| `play.sh` | Launch CS2 in tools mode on an addon map in casual/competitive/deathmatch/custom |
| `con.py`, `shoot.sh`, `shot2png.py` | Send console commands over `-netconport`; take a screenshot from a fixed camera; fix the TGA's swapped red/blue |
| `bspsrc.sh` | BSPSource CLI on native Java |
| `vmf_add_header.py` | Add the `versioninfo`/`viewsettings` blocks BSPSource leaves out (the importer crashes without them) |
| `vmf_drop_ents.py`, `vmf_keep_solids.py` | Strip entities or bisect world solids, to find what crashes the importer |
| `vmap_add_entity.py` | Clone a CMapEntity with fresh ids and set its classname, keys, origin and angles |
| `vmap_drop_entities.py` | Remove CMapEntity elements by classname |
| `vmap_add_buyzone.py` | Add a box `func_buyzone` from `templates/buyzone_template.txt` |
| `disp2mesh.py` | Rebuild the displacements the importer drops, as closed half-edge meshes (`templates/worldmesh_template.txt`) |
| `cube2latlong.py`, `vtf2png.py` | Source 1 skybox faces (VTF → PNG) → equirectangular panorama for CS2's `sky.vfx` |
| `sky_paint_ring.py` | Paint a 3D skybox's translucent panels (e.g. a glowing horizon ring) into the sky panorama |
| `radar.py`, `psd.py` | Draw a radar image from the VMF's brushes; write it as the flat PSD CS2's radar vtex expects |
| `make_port_credit.py` | The small "Ported to CS2" plaque decal (edit the text for your own) |
| `vpkx.py` | Extract a VPK (v1/v2, `_dir` + `_NNN`), for auditing what a Workshop item actually ships |
| `mdmp.py`, `ptyrun.py` | Read the crash address/module out of a minidump; capture a command's output through a pty |

`cs_script/` holds the per-map rules scripts (point_script, compiled to `.vjs`). They apply the original map's loadout only in the Custom game mode and touch no convars that would persist into later maps. Valve's `cs_script_demo` addon ships the `point_script.d.ts` typings.

The vmap scripts work on the **text** form and keep CRLF line endings. `.gitattributes` keeps the templates CRLF too.

## Credit

Credit the original mapper in the Workshop description. Old maps rarely state a license, and many of their authors have been inactive for years. Ask if you can reach them.

## License

MIT, for the scripts and notes in this repo. The maps and their assets belong to their authors and aren't included.
