# CS:GO maps → CS2, on Linux

## What we set out to do

When CS2 replaced CS:GO, a lot of old community maps were left behind. They still sit on the Steam Workshop, but CS2 can't load them. Nobody had ported some favourites, so we decided to do it ourselves.

There was one catch: Valve's map tools only run on Windows, and this was done on a Linux PC. So the real goal was to see whether a whole map port could be done on Linux, start to finish, without ever opening Valve's map editor.

## What we accomplished

It worked. Three old maps are now playable in CS2 and ready for the Workshop:

| Map | Originally made by | What it is |
| --- | --- | --- |
| **awp_neon** | Pr0F | A neon AWP duel arena |
| **aim_pyrocynical** | [Lefty](https://steamcommunity.com/sharedfiles/filedetails/?id=630383830) | A synthwave aim map with a glowing pink horizon and its own music |
| **aim_legocity** | [Bunny](https://steamcommunity.com/sharedfiles/filedetails/?id=1564248936) | A Deagle aim map built out of giant Lego bricks |

Each one plays like the original:
- Bots work.
- The map has a radar.
- Lighting and colours were matched to the old version.
- In CS2's **Custom** game mode it uses the original rules: AWPs only, Deagles only, and so on.
- Other game modes are left alone.

## How it works, in plain terms

1. **Take the old map apart.** The old map file is turned back into an editable source file.
2. **Run it through Valve's converter.** Valve ships a CS:GO→CS2 importer. It runs on Linux through Proton, Steam's Windows compatibility layer.
3. **Fix what the converter breaks.** This is most of the work. The converter loses things:
   - terrain
   - glowing surfaces
   - lighting
   - buy zones
   - bot navigation
   - weapon rules

   Small scripts in this repo put each of them back.
4. **Build and test.** Compile the map, load it in CS2, walk around, compare to the original, repeat.
5. **Publish.** Take screenshots, check nothing private gets uploaded, credit the original creator, and post it to the Workshop.

## What's in this repo

- **[GUIDE.md](GUIDE.md)**: the full step-by-step, with commands. Start here if you want to port a map yourself.
- **[FINDINGS.md](FINDINGS.md)**: everything that went wrong and how it was fixed. This is the most useful part if you get stuck.
- **`scripts/`**: the helper scripts. Each one does one small job, like "add buy zones" or "fix the sky".
- **`cs_script/`**: the little rule scripts that give players the right weapons in each map.
- **`templates/`**: building blocks some of the scripts copy from.

## Before you start

You'll need:
- CS2 with the free **Workshop Tools** add-on, running through Proton
- Python 3
- Some comfort with the terminal

Every step is in GUIDE.md. Expect some trial and error: old maps are all a little different.

## Credit where it's due

The maps belong to the people who made them. This repo only has tools and notes, no map files. If you port someone's map, credit them in the Workshop description, and ask first if you can reach them.

## License

The scripts and notes are MIT licensed. Use them however you like.
