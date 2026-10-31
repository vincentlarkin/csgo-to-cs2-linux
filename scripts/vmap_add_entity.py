# Add a point entity to a Hammer vmap (KeyValues2 text) by cloning an existing CMapEntity
# element with fresh element/node ids and replacing its properties and origin.
# Usage: vmap_add_entity.py <in> <out> <origin "x y z"> key=value [key=value...]   (classname=... required)
# The pseudo-key @angles="pitch yaw roll" sets the entity's rotation instead of a property.
import random, re, sys, uuid

src = open(sys.argv[1], newline='').read()
NL = '\r\n' if '\r\n' in src else '\n'
lines = src.split(NL)
origin = sys.argv[3]
props = [a.split('=', 1) for a in sys.argv[4:]]
angles = dict(props).get('@angles')
props = [kv for kv in props if kv[0] != '@angles']
assert any(k == 'classname' for k, _ in props), 'classname= is required'

def indent_of(l):
    return l[:len(l) - len(l.lstrip('\t'))]

def block_end(ls, start):
    ind = indent_of(ls[start])
    return next(i for i in range(start + 2, len(ls)) if ls[i] in (ind + '}', ind + '},'))

# clone a point entity: a brush entity's mesh children would come along, and their nested "origin"
# lines would be the ones edited
for start in (i for i, l in enumerate(lines) if l.strip() == '"CMapEntity"'):
    end = block_end(lines, start)
    if not any('"CMapMesh"' in l for l in lines[start:end]):
        break
else:
    sys.exit('no point entity to clone')
ent = [re.sub(r'"elementid" "[0-9a-f-]{36}"', lambda m: '"elementid" "%s"' % uuid.uuid4(), l)
       for l in lines[start:end + 1]]
max_node = max(int(n) for n in re.findall(r'"nodeID" "int" "(\d+)"', src))
ent = [re.sub(r'"nodeID" "int" "\d+"', '"nodeID" "int" "%d"' % (max_node + 1), l) for l in ent]
ent = [re.sub(r'"referenceID" "uint64" "0x[0-9a-f]+"', '"referenceID" "uint64" "0x%016x"' % random.getrandbits(64), l)
       for l in ent]

p0 = next(i for i, l in enumerate(ent) if '"entity_properties" "EditGameClassProps"' in l)
p1 = block_end(ent, p0)
pid = next(l for l in ent[p0:p1] if '"elementid"' in l)
ent[p0 + 2:p1] = [pid] + [indent_of(ent[p0]) + '\t"%s" "string" "%s"' % (k, v) for k, v in props]
top = indent_of(ent[0]) + '\t'  # the entity's own keys, not those of nested elements
o = next(i for i, l in enumerate(ent) if l.startswith(top + '"origin" "vector3" '))
ent[o] = indent_of(ent[o]) + '"origin" "vector3" "%s"' % origin
if angles:
    a = next(i for i, l in enumerate(ent) if l.startswith(top + '"angles" "qangle" '))
    ent[a] = indent_of(ent[a]) + '"angles" "qangle" "%s"' % angles
c = next(i for i, l in enumerate(ent) if '"connectionsData" "element_array"' in l)
cend = next(i for i in range(c + 1, len(ent)) if ent[i] == indent_of(ent[c]) + ']')
del ent[c + 2:cend]  # drop any outputs copied from the source entity

# Insert right after the cloned element, keeping element_array comma separation.
ent[-1] = lines[end]
lines[end] = lines[end].rstrip(',') + ','
lines[end + 1:end + 1] = ent
open(sys.argv[2], 'w', newline='').write(NL.join(lines))
print('added', dict(props).get('classname'), 'nodeID', max_node + 1)
