# Rebuild a VMF's displacements (which source1import dropped) as closed Hammer meshes:
# the sculpted grid on top, vertical sides and a bottom face, all as CS2 half-edge polygon meshes
# cloned from a world mesh template.
# Usage: disp2mesh.py <map.vmf> <worldmesh_template.txt> <in.vmap text> <out.vmap text>
import math, random, re, sys, uuid

vmf_path, tpl_path, in_path, out_path = sys.argv[1:5]
vmf = open(vmf_path, errors='replace').read().replace('\r', '')

def block(side, name):
    m = re.search(r'\n\t+%s\n\t+\{(.*?)\n\t+\}' % name, side, re.S)
    return [float(x) for x in ' '.join(re.findall(r'"row\d+" "([^"]+)"', m.group(1))).split()]

def vec(s):
    return [float(v) for v in s.strip('[]() ').split()]

def displacements():
    for solid in re.findall(r'\n\tsolid\n\t\{.*?\n\t\}', vmf, re.S):
        sides = re.findall(r'\n\t\tside\n\t\t\{.*?\n\t\t\}', solid, re.S)
        for side in sides:
            if 'dispinfo' not in side:
                continue
            p = [vec(x) for x in re.findall(r'\(([^)]+)\)', re.search(r'"plane" "([^"]+)"', side).group(1))]
            corners = [p[0], p[1], p[2], [a + c - b for a, b, c in zip(*p)]]  # winding order
            start = vec(re.search(r'"startposition" "([^"]+)"', side).group(1))
            k = min(range(4), key=lambda i: sum((a - b) ** 2 for a, b in zip(corners[i], start)))
            corners = corners[k:] + corners[:k]
            power = int(re.search(r'"power" "(\d)"', side).group(1))
            elev = float(re.search(r'"elevation" "([^"]+)"', side).group(1))
            pts = [vec(x) for x in re.findall(r'\(([^)]+)\)', ' '.join(re.findall(r'"plane" "([^"]+)"', solid)))]
            yield dict(corners=corners, n=2 ** power + 1, elev=elev, normals=block(side, 'normals'),
                       dists=block(side, 'distances'), bottom=min(q[2] for q in pts))

def grid(d, swap):
    """Vertex positions [row][col]. Rows run p0->p1 and columns p0->p3 (swap exchanges them)."""
    c, n = d['corners'], d['n']
    if swap:
        c = [c[0], c[3], c[2], c[1]]
    out = []
    for i in range(n):
        a = [c[0][k] + (c[1][k] - c[0][k]) * i / (n - 1) for k in range(3)]
        b = [c[3][k] + (c[2][k] - c[3][k]) * i / (n - 1) for k in range(3)]
        row = []
        for j in range(n):
            base = [a[k] + (b[k] - a[k]) * j / (n - 1) for k in range(3)]
            idx = i * n + j
            nrm = d['normals'][idx * 3:idx * 3 + 3]
            row.append([base[k] + nrm[k] * d['dists'][idx] for k in range(2)] + [base[2] + nrm[2] * d['dists'][idx] + d['elev']])
        out.append(row)
    return out

def seam_error(grids):
    """Mean height mismatch between vertices of different displacements that share x,y."""
    pts = {}
    for g_i, g in enumerate(grids):
        for row in g:
            for v in row:
                pts.setdefault((round(v[0]), round(v[1])), []).append((g_i, v[2]))
    errs = [abs(a[1] - b[1]) for vs in pts.values() for a in vs for b in vs if a[0] < b[0]]
    return (sum(errs) / len(errs) if errs else 0.0), len(errs)

disps = list(displacements())
best = min((seam_error([grid(d, s) for d in disps]) + (s,) for s in (False, True)), key=lambda r: r[0])
print('displacements', len(disps), 'seam error %.2f over %d shared points, swap=%s' % best)
SWAP = best[2]

# ---------- half-edge mesh from polygons ----------
def build(verts, faces):
    """faces: list of (vertex loop, material index). Returns half-edge arrays (dest convention)."""
    he_v, he_f, he_next, key = [], [], [], {}
    face_first = []
    for f, (loop, _) in enumerate(faces):
        first = len(he_v)
        for k, v in enumerate(loop):
            he_v.append(loop[(k + 1) % len(loop)])  # half-edge from loop[k] to loop[k+1]
            he_f.append(f)
            he_next.append(first + (k + 1) % len(loop))
            key[(v, loop[(k + 1) % len(loop)])] = len(he_v) - 1
        face_first.append(first)
    opp = [None] * len(he_v)
    for (a, b), h in key.items():
        opp[h] = key[(b, a)]  # closed manifold mesh: every edge has a twin
    # Reorder so twins are adjacent (2e, 2e+1), matching how Hammer stores edges.
    order, seen = [], set()
    for h in range(len(he_v)):
        if h not in seen:
            order += [h, opp[h]]; seen |= {h, opp[h]}
    remap = {old: new for new, old in enumerate(order)}
    he = dict(v=[he_v[o] for o in order], f=[he_f[o] for o in order],
              next=[remap[he_next[o]] for o in order], opp=[remap[opp[o]] for o in order])
    he['face_edge'] = [remap[x] for x in face_first]
    src = {}
    for h in range(len(he['v'])):
        src.setdefault(he['v'][he['opp'][h]], h)  # an outgoing half-edge per vertex
    he['vert_edge'] = [src[v] for v in range(len(verts))]
    return he

def mesh_for(d):
    g = grid(d, SWAP)
    n = d['n']
    verts = [v for row in g for v in row]
    top = lambda i, j: i * n + j
    # Bottom ring: one vertex under each boundary vertex of the grid, at the brush's base.
    ring = [top(0, j) for j in range(n)] + [top(i, n - 1) for i in range(1, n)] + \
           [top(n - 1, j) for j in range(n - 2, -1, -1)] + [top(i, 0) for i in range(n - 2, 0, -1)]
    bottom_idx = {}
    for t in ring:
        bottom_idx[t] = len(verts)
        verts.append([verts[t][0], verts[t][1], d['bottom']])
    faces = []
    # Orientation: make the top face normals point up.
    def up(loop):
        a, b, c = (verts[x] for x in loop[:3])
        u = [b[k] - a[k] for k in range(3)]; w = [c[k] - a[k] for k in range(3)]
        return u[0] * w[1] - u[1] * w[0] > 0
    flip = not up([top(0, 0), top(0, 1), top(1, 1)])
    for i in range(n - 1):
        for j in range(n - 1):
            for tri in ([top(i, j), top(i, j + 1), top(i + 1, j + 1)], [top(i, j), top(i + 1, j + 1), top(i + 1, j)]):
                faces.append((tri[::-1] if flip else tri, 0))
    # Sides: quads between consecutive ring vertices; bottom: one polygon, all opposite winding.
    for k in range(len(ring)):
        a, b = ring[k], ring[(k + 1) % len(ring)]
        quad = [b, a, bottom_idx[a], bottom_idx[b]]
        faces.append((quad[::-1] if flip else quad, 0))
    bottom = [bottom_idx[t] for t in ring]
    faces.append((bottom if flip else bottom[::-1], 1))
    return verts, faces

# ---------- emit KeyValues2 ----------
tpl = open(tpl_path, newline='').read().split('\r\n')
src_text = open(in_path, newline='').read()
lines = src_text.split('\r\n')
max_node = max(int(x) for x in re.findall(r'"nodeID" "int" "(\d+)"', src_text))
fmt = lambda v: ('%.4f' % v).rstrip('0').rstrip('.') if abs(v - round(v)) > 1e-6 else str(int(round(v)))

def set_array(blk, header_pred, values, quote=True):
    """Replace the contents of the first '[' ... ']' array after the header line matching header_pred."""
    h = next(i for i, l in enumerate(blk) if header_pred(l))
    o = next(i for i in range(h, len(blk)) if blk[i].strip() == '[')
    c = next(i for i in range(o, len(blk)) if blk[i].strip() == ']' and blk[i].startswith(blk[o][:-1]))
    ind = blk[o][:-1] + '\t'
    vals = ['"%s"' % v if quote else v for v in values]
    blk[o + 1:c] = [ind + v + (',' if k < len(vals) - 1 else '') for k, v in enumerate(vals)]

def set_size(blk, array_name, size):
    h = next(i for i, l in enumerate(blk) if '"%s" "CDmePolygonMeshDataArray"' % array_name in l)
    s = next(i for i in range(h, len(blk)) if '"size" "int"' in blk[i])
    blk[s] = re.sub(r'"\d+"$', '"%d"' % size, blk[s])

def stream(name):
    return lambda l: '"name" "string" "%s"' % name in l

def emit(d, node):
    verts, faces = mesh_for(d)
    he = build(verts, faces)
    centre = [(min(v[k] for v in verts) + max(v[k] for v in verts)) / 2 for k in range(3)]
    nh, nf = len(he['v']), len(faces)
    # Per-corner data (index = half-edge): uv from the original moon tiling, flat face normal.
    def fnormal(loop):
        a, b, c = (verts[x] for x in loop[:3])
        u = [b[k] - a[k] for k in range(3)]; w = [c[k] - a[k] for k in range(3)]
        nrm = [u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0]]
        L = math.sqrt(sum(x * x for x in nrm)) or 1
        return [x / L for x in nrm]
    fn = [fnormal(loop) for loop, _ in faces]
    uv = [[-verts[he['v'][h]][0] / 512 + 0.25, -verts[he['v'][h]][1] / 512] for h in range(nh)]
    blk = [re.sub(r'"elementid" "[0-9a-f-]{36}"', lambda m: '"elementid" "%s"' % uuid.uuid4(), l) for l in tpl]
    blk = [re.sub(r'"nodeID" "int" "\d+"', '"nodeID" "int" "%d"' % node, l) for l in blk]
    blk = [re.sub(r'"referenceID" "uint64" "0x[0-9a-f]+"', '"referenceID" "uint64" "0x%016x"' % random.getrandbits(64), l) for l in blk]
    q = lambda name: (lambda l: '"%s"' % name in l and '_array' in l)
    set_array(blk, q('vertexEdgeIndices'), he['vert_edge'])
    set_array(blk, q('vertexDataIndices'), range(len(verts)))
    set_array(blk, q('edgeVertexIndices'), he['v'])
    set_array(blk, q('edgeOppositeIndices'), he['opp'])
    set_array(blk, q('edgeNextIndices'), he['next'])
    set_array(blk, q('edgeFaceIndices'), he['f'])
    set_array(blk, q('edgeDataIndices'), [h // 2 for h in range(nh)])
    set_array(blk, q('edgeVertexDataIndices'), range(nh))
    set_array(blk, q('faceEdgeIndices'), he['face_edge'])
    set_array(blk, q('faceDataIndices'), range(nf))
    set_array(blk, q('materials'), ['materials/custom/moon_surface.vmat', 'materials/tools/toolsnodraw.vmat'])
    set_size(blk, 'vertexData', len(verts))
    set_array(blk, stream('position:0'), [' '.join(fmt(v[k] - centre[k]) for k in range(3)) for v in verts])
    set_size(blk, 'faceVertexData', nh)
    set_array(blk, stream('texcoord:0'), ['%s %s' % (fmt(a), fmt(b)) for a, b in uv])
    set_array(blk, stream('normal:0'), [' '.join(fmt(x) for x in fn[he['f'][h]]) for h in range(nh)])
    set_array(blk, stream('tangent:0'), ['1 0 0 -1'] * nh)
    set_size(blk, 'edgeData', nh // 2)
    # Edge flags (first flags:0 stream) and face flags (second), all zero.
    flags = [i for i, l in enumerate(blk) if '"name" "string" "flags:0"' in l]
    for idx, count in zip(flags, (nh // 2, nf)):
        sub = blk[idx:]
        set_array(sub, lambda l: '"data" "int_array"' in l, [0] * count)
        blk[idx:] = sub
    set_size(blk, 'faceData', nf)
    set_array(blk, stream('textureScale:0'), ['0.25 0.25'] * nf)
    set_array(blk, stream('textureAxisU:0'), ['-1 0 0 256'] * nf)
    set_array(blk, stream('textureAxisV:0'), ['0 -1 0 0'] * nf)
    set_array(blk, stream('materialindex:0'), [m for _, m in faces])
    set_array(blk, stream('lightmapScaleBias:0'), [0] * nf)
    set_array(blk, q('subdivisionLevels'), [0] * nh)
    o = next(i for i, l in enumerate(blk) if re.match(r'^\t+"origin" "vector3" ', l))
    blk[o] = re.sub(r'"[^"]*"$', '"%s"' % ' '.join(fmt(c) for c in centre), blk[o])
    return blk, len(verts), nf

# Insert after the first world mesh in the target.
ind = lambda l: len(l) - len(l.lstrip('\t'))
start = next(i for i, l in enumerate(lines) if l.strip() == '"CMapMesh"')
end = next(k for k in range(start + 2, len(lines)) if lines[k].strip() in ('}', '},') and ind(lines[k]) == ind(lines[start]))
assert ind(tpl[0]) == ind(lines[start]), 'template nesting differs from target'
new = []
for k, d in enumerate(disps):
    blk, nv, nf = emit(d, max_node + 1 + k)
    blk[-1] = blk[-1].rstrip(',') + ','
    new += blk
    print('mesh %d: %d verts, %d faces, base z %g' % (k, nv, nf, d['bottom']))
lines[end] = lines[end].rstrip(',') + ','
new[-1] = new[-1].rstrip(',') + (',' if lines[end + 1].strip() not in (']',) else '')
lines[end + 1:end + 1] = new
open(out_path, 'w', newline='').write('\r\n'.join(lines))
