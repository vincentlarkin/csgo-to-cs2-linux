# Remove CMapEntity elements by classname from a Hammer vmap (KeyValues2 text).
# Usage: vmap_drop_entities.py <in> <out> <classname>...
import re, sys

src = open(sys.argv[1], newline='').read()
NL = '\r\n' if '\r\n' in src else '\n'
lines = src.split(NL)
drop = set(sys.argv[3:])
ind = lambda l: len(l) - len(l.lstrip('\t'))

i = 0
while i < len(lines):
    if lines[i].strip() != '"CMapEntity"':
        i += 1
        continue
    end = next(k for k in range(i + 2, len(lines)) if lines[k].strip() in ('}', '},') and ind(lines[k]) == ind(lines[i]))
    m = re.search(r'"classname" "string" "([^"]+)"', NL.join(lines[i:end]))
    if not (m and m.group(1) in drop):
        i = end + 1
        continue
    print('dropped', m.group(1))
    del lines[i:end + 1]
    # Removing the last element of an element_array leaves a dangling comma on the one before it.
    if lines[i].strip() == ']' and lines[i - 1].endswith('},'):
        lines[i - 1] = lines[i - 1][:-1]
open(sys.argv[2], 'w', newline='').write(NL.join(lines))
