#!/bin/bash
# BSPSource CLI on native Linux Java (modules extracted from the Windows bundle). Usage: bspsrc.sh [options] <file.bsp>
exec java -Djava.awt.headless=true --module-path "${BSPSRC_MODS:-$(dirname "$0")/../tools/bspsrc_mods}" -m info.ata4.bspsrc.app/info.ata4.bspsrc.app.src.BspSourceLauncher "$@"
