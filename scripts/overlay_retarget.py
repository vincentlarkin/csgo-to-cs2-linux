# Turn an existing CMapStaticOverlay (a 4-corner overlay in a vmap's KeyValues2 text) into a flat
# W x H rectangle showing another material at a new origin/angles. Used to place a small decal
# (e.g. a port-credit plaque) without Hammer, by re-using an overlay the port doesn't need any more.
# Usage: overlay_retarget.py <in.txt> <out.txt> <current material> <new material> <W> <H> "<x y z>" "<pitch yaw roll>"
# Local frame: +x is the viewer's right, +y is up, +z is the overlay normal (toward the viewer).
# With angles "0 0 90" the overlay faces -Y; "0 90 90" faces +X; "0 180 90" faces +Y; "0 270 90" faces -X.
import re, sys

src = open(sys.argv[1], newline='').read()
NL = '\r\n' if '\r\n' in src else '\n'
old_mat, new_mat = sys.argv[3], sys.argv[4]
w, h = float(sys.argv[5]) / 2, float(sys.argv[6]) / 2
origin, angles = sys.argv[7], sys.argv[8]

lines = src.split(NL)
ind = lambda l: len(l) - len(l.lstrip('\t'))
starts = [i for i, l in enumerate(lines) if l.strip() == '"CMapStaticOverlay"']
for s in starts:
    e = next(j for j in range(s + 2, len(lines)) if ind(lines[j]) == ind(lines[s]) and lines[j].strip() in ('}', '},'))
    block = NL.join(lines[s:e + 1])
    if '"%s"' % old_mat in block:
        break
else:
    sys.exit('no overlay uses ' + old_mat)

def arr(name, kind, values):
    # replace the values of the first "<name>" stream's data array inside the block
    global block
    m = re.search(r'"name" "string" "%s".*?"data" "%s"\s*\[(.*?)\]' % (re.escape(name), kind), block, re.S)
    assert m, name
    body = m.group(1)
    pad = re.search(r'([ \t]*)"', body).group(1)
    new = NL + (',' + NL).join(pad + '"%s"' % v for v in values) + NL + pad[:-1]
    block = block[:m.start(1)] + new + block[m.end(1):]

# vertex order from edgeVertexIndices; corner data (uv/normal/tangent) sits on the half-edge
# *arriving* at a vertex, at even edge indices 0,2,4,6 -> vertices 1,2,3,0 for the importer's quads
evi = [int(x) for x in re.findall(r'"(-?\d+)"', re.search(r'"edgeVertexIndices" "int_array"\s*\[(.*?)\]', block, re.S).group(1))]
assert evi[0::2] == [1, 2, 3, 0], 'unexpected overlay topology %s' % evi
pos = {1: (w, h), 2: (-w, h), 3: (-w, -h), 0: (w, -h)}           # TR, TL, BL, BR
uv = {1: '1 0', 2: '0 0', 3: '0 1', 0: '1 1'}
arr('position:0', 'vector3_array', ['%g %g 0' % pos[v] for v in range(4)])
fv = []
for k in range(8):
    fv.append(uv[evi[k]] if k % 2 == 0 else '0 0')
arr('texcoord:0', 'vector2_array', fv)
arr('normal:0', 'vector3_array', ['0 0 1' if k % 2 == 0 else '0 0 0' for k in range(8)])
arr('tangent:0', 'vector4_array', ['1 0 0 1' if k % 2 == 0 else '0 0 0 0' for k in range(8)])
block = block.replace('"%s"' % old_mat, '"%s"' % new_mat)
block = re.sub(r'("origin" "vector3" )"[^"]*"', r'\1"%s"' % origin, block, count=1)
block = re.sub(r'("angles" "qangle" )"[^"]*"', r'\1"%s"' % angles, block, count=1)
lines[s:e + 1] = block.split(NL)
out = NL.join(lines)
# the prefab's top-level material list must name the new material too
if '"%s"' % new_mat not in out.split('"CMapStaticOverlay"')[0]:
    out = out.replace('"%s",' % old_mat, '"%s",%s\t\t"%s",' % (old_mat, NL, new_mat), 1)
open(sys.argv[2], 'w', newline='').write(out)
print('overlay at', origin, angles, '->', new_mat)
