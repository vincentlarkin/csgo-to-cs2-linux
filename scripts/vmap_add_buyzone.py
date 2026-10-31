# Add a box-shaped func_buyzone to a Hammer vmap (KeyValues2 text), cloned from the func_buyzone
# Valve's importer produced for aim_pyrocynical (template: entity origin 0, mesh origin = box
# centre, vertex positions relative to the centre, toolstrigger material).
# Usage: vmap_add_buyzone.py <template.txt> <in> <out> <targetname> <teamnum> <x0 y0 z0> <x1 y1 z1>
import random, re, sys, uuid

tpl_path, src_path, out_path, name, team = sys.argv[1:6]
lo = [float(v) for v in sys.argv[6].split()]
hi = [float(v) for v in sys.argv[7].split()]
centre = [(a + b) / 2 for a, b in zip(lo, hi)]
half = [(b - a) / 2 for a, b in zip(lo, hi)]
fmt = lambda v: ('%g' % v)

tpl = open(tpl_path, newline='').read().split('\r\n')
src = open(src_path, newline='').read()
lines = src.split('\r\n')

# Fresh ids for every element, node and reference in the clone.
max_node = max(int(n) for n in re.findall(r'"nodeID" "int" "(\d+)"', src))
nodes = iter(range(max_node + 1, max_node + 100))
blk = []
for l in tpl:
    l = re.sub(r'"elementid" "[0-9a-f-]{36}"', lambda m: '"elementid" "%s"' % uuid.uuid4(), l)
    l = re.sub(r'"nodeID" "int" "\d+"', lambda m: '"nodeID" "int" "%d"' % next(nodes), l)
    l = re.sub(r'"referenceID" "uint64" "0x[0-9a-f]+"', lambda m: '"referenceID" "uint64" "0x%016x"' % random.getrandbits(64), l)
    blk.append(l)

# Box vertices: keep the template's sign pattern, swap in our half extents.
p = next(i for i, l in enumerate(blk) if '"name" "string" "position:0"' in l)
d = next(i for i in range(p, len(blk)) if '"data" "vector3_array"' in blk[i])
i = d + 2
while blk[i].strip() != ']':
    m = re.match(r'^(\t+)"([-\d.e ]+)"(,?)$', blk[i])
    xyz = [float(v) for v in m.group(2).split()]
    blk[i] = '%s"%s"%s' % (m.group(1), ' '.join(fmt(h if v > 0 else -h) for v, h in zip(xyz, half)), m.group(3))
    i += 1

# Mesh origin is the box centre; the entity itself stays at the world origin.
mesh_origin = next(i for i, l in enumerate(blk) if re.match(r'^\t+"origin" "vector3" ', l))
blk[mesh_origin] = re.sub(r'"[^"]*"$', '"%s"' % ' '.join(fmt(v) for v in centre), blk[mesh_origin])
blk = [re.sub(r'"targetname" "string" "[^"]*"', '"targetname" "string" "%s"' % name, l) for l in blk]
blk = [re.sub(r'"TeamNum" "string" "[^"]*"', '"TeamNum" "string" "%s"' % team, l) for l in blk]

# Insert after the first top-level entity, keeping element_array comma separation.
ind = lambda l: len(l) - len(l.lstrip('\t'))
start = next(i for i, l in enumerate(lines) if l.strip() == '"CMapEntity"')
end = next(k for k in range(start + 2, len(lines)) if lines[k].strip() in ('}', '},') and ind(lines[k]) == ind(lines[start]))
assert ind(blk[0]) == ind(lines[start]), 'template nesting differs from target'
blk[-1] = lines[end]
lines[end] = lines[end].rstrip(',') + ','
lines[end + 1:end + 1] = blk
open(out_path, 'w', newline='').write('\r\n'.join(lines))
print('added', name, 'team', team, 'centre', centre, 'half', half)
