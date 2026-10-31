# Copy a CMapStaticOverlay (found by its material) from one vmap's KeyValues2 text into another's
# world children, with fresh element ids, nodeID and referenceID. Follow with overlay_retarget.py
# to move and size it. Usage: overlay_clone.py <source.txt> <target.txt> <out.txt> <material>
import random, re, sys, uuid

def load(p):
    s = open(p, newline='').read()
    nl = '\r\n' if '\r\n' in s else '\n'
    return s, nl, s.split(nl)

ind = lambda l: len(l) - len(l.lstrip('\t'))
def block_end(ls, start):
    return next(j for j in range(start + 2, len(ls)) if ind(ls[j]) == ind(ls[start]) and ls[j].strip() in ('}', '},'))

src, _, sl = load(sys.argv[1])
mat = sys.argv[4]
for s in (i for i, l in enumerate(sl) if l.strip() == '"CMapStaticOverlay"' and ind(l) == 3):
    e = block_end(sl, s)
    if any('"%s"' % mat in l for l in sl[s:e]):
        blk = sl[s:e + 1]
        break
else:
    sys.exit('no nested overlay uses ' + mat)

tgt, NL, tl = load(sys.argv[2])
blk = [re.sub(r'"elementid" "[0-9a-f-]{36}"', lambda m: '"elementid" "%s"' % uuid.uuid4(), l) for l in blk]
node = max(int(n) for n in re.findall(r'"nodeID" "int" "(\d+)"', tgt)) + 1
blk = [re.sub(r'"nodeID" "int" "\d+"', '"nodeID" "int" "%d"' % node, l) for l in blk]
blk = [re.sub(r'"referenceID" "uint64" "0x[0-9a-f]+"', '"referenceID" "uint64" "0x%016x"' % random.getrandbits(64), l) for l in blk]
# insert after the first world child (a 3-tab element), keeping element_array comma separation
first = next(i for i, l in enumerate(tl) if ind(l) == 3 and l.strip().startswith('"CMap'))
end = block_end(tl, first)
blk[-1] = tl[end]
tl[end] = tl[end].rstrip(',') + ','
tl[end + 1:end + 1] = blk
out = NL.join(tl)
if '"%s"' % mat not in out.split('"CMap')[0]:
    out = re.sub(r'("map_asset_references" "string_array"\s*\[)', lambda m: m.group(1) + NL + '\t\t"%s",' % mat, out, count=1)
open(sys.argv[3], 'w', newline='').write(out)
print('cloned overlay', mat, 'nodeID', node)
