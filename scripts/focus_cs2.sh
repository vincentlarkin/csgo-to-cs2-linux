#!/bin/bash
# Raise and focus the CS2 window on KDE Plasma (Wayland or X11) through a one-shot KWin script.
# CS2 only presents frames (and so only takes real screenshots) while its window is shown; otherwise every
# screenshot is the frozen loading screen.
js=$(mktemp --suffix=.js)
cat > "$js" <<'JS'
const ws = workspace.windowList ? workspace.windowList() : workspace.clientList();
for (const w of ws)
    if (/Counter-Strike/i.test(w.caption || "") || /cs2/i.test(w.resourceClass || "")) { w.minimized = false; workspace.activeWindow = w; }
JS
id=$(gdbus call --session -d org.kde.KWin -o /Scripting -m org.kde.kwin.Scripting.loadScript "$js" focus_cs2 | grep -o '[0-9]\+' | head -1)
gdbus call --session -d org.kde.KWin -o "/Scripting/Script$id" -m org.kde.kwin.Script.run >/dev/null
sleep 0.5
gdbus call --session -d org.kde.KWin -o /Scripting -m org.kde.kwin.Scripting.unloadScript focus_cs2 >/dev/null
rm -f "$js"
