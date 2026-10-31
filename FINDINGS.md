# Findings

These are the things that went wrong, or weren't obvious, while porting three CS:GO maps to CS2 on Linux. Each entry gives the symptom, the cause and the fix.

## Running Valve's tools under Proton

- **Force Proton Experimental on CS2** and install the Workshop Tools DLC. The native Linux build has no tools.
  The `.exe`s live in `game/bin/win64/`. Run them with `proton run` and `STEAM_COMPAT_DATA_PATH=steamapps/compatdata/730`. See `rc.sh`.
- **Paths are Wine paths.** `/home/you/x` is `Z:\home\you\x`. The wrappers `cd` into `game/bin/win64`, so relative paths break.
- **The importer's console output goes to its own window** and can't be captured from the shell. Use `-logwarnings` and read the log it writes. `ptyrun.py` helps for tools that only print to a terminal.
- **Lighting bakes crash** in Open Image Denoise, which tries CUDA and Proton doesn't provide it. Set `OIDN_DEVICE_CUDA=0`, for both `resourcecompiler -bakelighting` and Hammer's in-process bake. `build.sh` and `play.sh` set it.
- **Map loading:**
  - `map <name>` says "invalid map name" for local addon builds. `map <name> nomapvalidation=true` works.
  - Proton quotes `+map x nomapvalidation=true` on the command line, so the game sees one malformed argument. `play.sh` writes a cfg and runs `+exec` on it instead.
- **`-netconport 2121`** gives a console you can script (`con.py`). It listens on `0.0.0.0`, not localhost, so close the game when you're done.

## Decompiling (BSPSource)

- **BSPSource runs on native Linux Java.** Take its module folders from the Windows release and launch with `--module-path` (`bspsrc.sh`).
- **BSPSource VMFs lack the `versioninfo` and `viewsettings` blocks**, and source1import exits with code 255 without them. `vmf_add_header.py` adds them.
- VMF files are **CRLF**. Keep them that way when editing.
- **The staging Source 1 folder must be named `csgo`.** Otherwise the importer stops at an interactive y/N prompt you can't see (it's in the other window), and it looks like a hang.
- If the importer crashes, bisect: `vmf_drop_ents.py` removes entity classes, and `vmf_keep_solids.py` keeps a range of world solids.

## What the importer gets wrong

- **Materials look like "shaders off" (flat and dull).** The importer drops `$selfillum` and adds a default roughness texture. Write `csgo_complex` vmats by hand for anything that should glow or shine. Its scrolling, decal, unlit and animated (`.mks`) materials come through fine.
- **Displacements are dropped.** Only the brush's nodraw collision survives, so terrain is invisible but solid. `disp2mesh.py` rebuilds each displacement from the VMF's `dispinfo` as a closed half-edge mesh. Details:
  - Rows run p0→p1 from `startposition`.
  - Half-edge corner data belongs to the destination vertex.
  - Positions are mesh-local.
- **Player models render black, and so does lighting on props.** No light probes and no `light_environment` get created. Add an `env_combined_light_probe_volume` (voxel size 24, bounds covering the playable brushes) and a `light_environment`.
- **The sun is about 1/255 of the right strength.** CS:GO's `_light` brightness (0–255) arrives as a 0–1 value divided by 255 again (e.g. 0.039). Re-balance by eye against screenshots of the original. CS:GO maps were often a weak sun plus strong ambient plus fog plus a colour-correction file, so a bright sun alone looks harsh and orange.
- `light_omni2` can come through with brightness `nan`. It's an unused EV field when units are lumens.
- **`info_overlay` decals do survive**, as `CMapStaticOverlay` in the environment prefab. Don't add `env_decal` copies or you get them twice.
- **No buy zones.** CS:GO created them automatically around spawns. CS2 doesn't. Add `func_buyzone` boxes (`vmap_add_buyzone.py`, TeamNum 2 = T, 3 = CT).
- **No nav mesh, so no bots.** Place a `point_nav_walkable` seed on each walkable area and compile with `-nav` (`build.sh` does).
- **3D skybox:** none of the CS2 3D-sky routes worked headless:
  - `sky_camera` in the same map
  - `sky_camera_volume`
  - a `skybox_reference` to a separate skybox map, which is how Valve ships `maps/prefabs/<map>/<map>_skybox.vpk`

  What did work: `sky_paint_ring.py` ray-casts from the sky camera through each panorama pixel and paints the 3D sky's panels into the `env_sky` panorama. See the sky section below.

## Editing vmaps without Hammer

- **`dmxconvert` turns a vmap into KeyValues2 text and back** (`-oe keyvalues2` / `-oe binary`). The text is CRLF, tab-indented, one element per block. World children sit at three tabs of indent.
- **Cloned elements need fresh ids.** Give every `elementid` (UUID), `nodeID` (int, unique in the file) and `referenceID` (uint64) a new value. `vmap_add_entity.py` and `vmap_add_buyzone.py` do this.
- **`element_array` entries are comma-separated.** When you remove the last element, take the trailing comma off the one before it.
- The importer splits a map into a main vmap plus `_gameplay`, `_lighting` and `_environment` prefabs. Edit the prefab that holds the thing. A copy of the main vmap (`map_cs2.vmap`) keeps the importer's original intact.
- **Hiding a mesh:** point its faces' material at `materials/tools/toolsnodraw.vmat` (a text replace of the material path in that mesh element). The geometry stays and simply stops rendering. That's how a sponsor sign was removed.

## Gameplay logic

- **Don't fill `game_player_equip`'s weapon keys.** In CS2 it only equips on touch or input, and filling `weapon0..N` crashed map load with a null dereference in `server.dll`, which `mdmp.py` showed.
- **Use cs_script instead.** Add a `point_script` entity whose `cs_script` key names `maps/scripts/<map>.vjs`. Compile the `.js` with `rc.sh`. The examples in `cs_script/` work like this:
  - `OnPlayerReset` strips weapons and gives the map's loadout (knife + AWP, knife + Deagle, ...).
  - `OnActivate` and `OnRoundStart` disable the buy zones, since map entities come back every round.
  - All of it runs **only in the Custom game mode** (`game_type 3`, `game_mode 0`). Competitive and the other modes keep their stock rules.
  - No convars are set that would carry over to the next map.
- Typings for the API are in Valve's `cs_script_demo` addon (`point_script.d.ts`). Game type and mode numbers are in `gamemodes.txt`.

## Sky

- **Six Source skybox faces become one equirectangular PNG** (`cube2latlong.py`), used through a `sky.vfx` material set as `env_sky`'s skyname in the lighting prefab. Orientation:
  - Turning right from `ft` gives `lf`.
  - `up` is stored rotated 90° and needs a 270° PIL rotation.
- **Painting a 3D sky's horizon ring** (aim_pyrocynical's pink glow):
  - The panels were `LightmappedGeneric`, so in CS:GO they were darkened by their lightmap: ambient plus sun times cos toward the `light_environment`. Unlit they look washed out.
  - Blend in **linear light**. Blending in sRGB gives a hard-edged band instead of the soft falloff seen in the original.
  - Compare against the original Workshop preview image, not memory. Its colours set a green-channel tint.

## Building

- **`build.sh` matches Hammer's compile**:
  - `PRESET=test` (512 draft lightmaps) takes about 25 s on a small map.
  - `PRESET=final` (2048, final quality) takes about 25 min.
- **Small open maps: `NOVIS=1`.** Vis can cull things it shouldn't on tiny arenas, and it saves time.
- **Run `buildcubemaps` after every build.** Without cubemaps, glossy surfaces reflect black at grazing angles. On aim_legocity that made whole buildings seem to "vanish" from one corner. It looked like a vis or fade-distance bug, but it was shiny bricks reflecting nothing. Cubemaps are written into the map's vpk.
- **Light probes bake headless, cubemaps don't.** They need the game running (`buildcubemaps` in the console).

## Radar

- You need `resource/overviews/<map>.txt` (`pos_x`, `pos_y`, `scale`, spawn positions as 0–1 fractions) plus `panorama/images/overheadmaps/<map>_radar.psd` with a `_psd.vtex`.
- `radar.py` draws the image from the VMF's brushes, using the same `pos_x`/`pos_y`/`scale` as the overview file. `psd.py` writes it as a flat RGBA PSD.

## Sounds

- Put WAVs in `content/<addon>/sounds/` and declare them in `soundevents/soundevents_addon.vsndevts` (copy the base events from the addon template).
- Play them through `env_soundscape` with `enablesoundevent`. WAV loop markers (`smpl` chunk) survive into the compiled `vsnd`.

## Screenshots

- Console `screenshot` writes a TGA into the addon's `screenshots/` folder. **Under Vulkan its red and blue are swapped**, because it dumps the swapchain's BGRA bytes. `shot2png.py` swaps them back.
- **A frozen loading-screen frame** in every shot means the game window isn't being presented: Steam isn't running, or the window was never shown or focused. The game also stops rendering while the desktop is locked.
- For posed shots:
  - Run `sv_cheats 1; noclip; cl_drawhud 0; r_drawviewmodel 0`.
  - Then call `shoot.sh out.png "x y z" "pitch yaw 0"` for each angle.
  - Don't `setpos` far outside the playable area, or you'll see the void.

## Publishing

What Workshop Tools uploads is the **game** addon folder (`game/csgo_addons/<addon>/`), minus `cfg/`, `ServerConfig.vdf`, `tools_*` and the `_`-prefixed caches. Before publishing:

- **`addoninfo.txt`**: its `"maps"` key should name the final map, not the importer's `_d` test map.
- **Stale outputs ship too.** Old map vpks (`maps/<map>_d.vpk`) and compiled materials you no longer use (`materials/**/*.vmat_c`, `*.vtex_c`) get uploaded. Move them out.
- **Privacy.** Download your own published item and unpack it (`vpkx.py`, twice, since the map vpk is nested inside):
  - What came through clean: no emails, IPs, SteamIDs, hostnames or project paths. Texture references are relative.
  - The one thing that leaks: every compiled material (`.vmat_c`) records the absolute path of the shader pack it was built against, e.g. `Z:\home\<user>\.local\share\Steam\steamapps\common\Counter-Strike Global Offensive\game\csgo\shaders_pc.vpk`. That reveals your OS username and that you run Linux/Proton. It's standard resourcecompiler behaviour (Windows builds leak `C:\Program Files (x86)\Steam\...` the same way), and it's inside compressed data. Building from a Steam library whose path doesn't contain your username avoids it.
- Publish **Private** first, subscribe on a second look, then make it public.
