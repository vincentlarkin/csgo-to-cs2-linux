# Paint a Source 1 3D-skybox's translucent panels (e.g. aim_pyrocynical's pink horizon ring) into an
# equirectangular sky panorama, so the effect shows without a CS2 3D skybox. Ray-casts from the sky
# camera (plus eye height / scale) through each panorama pixel against the VMF's vertical panel faces
# that use MATERIAL, samples that material's texture with the face's own uaxis/vaxis, alpha-blends.
# The panels were LightmappedGeneric, so they are darkened by their lightmap: AMBIENT everywhere plus
# SUN * cos where the ring faces the light_environment (linear scales). Blending is done in linear
# light, which matches the soft falloff in the original's screenshots; sRGB blending gives a hard band.
# Usage: sky_paint_ring.py <map.vmf> <material> <texture.png> <panorama_in.png> <panorama_out.png> "<cam x y z>" <scale>
#        ["<sun pitch yaw>" <ambient> <sun>]
import math, re, sys
from PIL import Image

vmf, material, tex_path, pano_in, pano_out, cam, scale = sys.argv[1:8]
cam = [float(v) for v in cam.split()]; scale = float(scale)
sun_pitch, sun_yaw = [math.radians(float(v)) for v in (sys.argv[8] if len(sys.argv) > 8 else '-55 52').split()]
ambient = float(sys.argv[9]) if len(sys.argv) > 9 else 1.0
sun = float(sys.argv[10]) if len(sys.argv) > 10 else 0.0
eye = 166.0 / scale  # player eye height in the arena (~102 floor + 64), in skybox units
# light_environment pitch is negative pointing down; yaw is where the light travels, so the sun sits opposite
to_sun = (-math.cos(sun_yaw) * math.cos(sun_pitch), -math.sin(sun_yaw) * math.cos(sun_pitch), -math.sin(sun_pitch))

# per-channel gain on the panels: the texture's green reads dusty mauve at lightmap brightness, while the
# original's screenshots show a clean magenta-purple (green ~5); 0.3 matches them
TINT = (1.0, 0.3, 1.0)
lin = [(i / 255.0) ** 2.2 for i in range(256)]
def srgb(x):
    return int(round(255 * min(1.0, max(0.0, x)) ** (1 / 2.2)))

src = open(vmf, errors='replace').read().replace('\r', '')
faces = []
for side in re.findall(r'\n\t\tside\n\t\t\{.*?\n\t\t\}', src, re.S):
    if '"%s"' % material not in side:
        continue
    pts = [[float(v) - cam[i] for i, v in enumerate(x.split())] for x in re.findall(r'\(([^)]+)\)', re.search(r'"plane" "([^"]+)"', side).group(1))]
    ua = re.search(r'"uaxis" "\[([^\]]+)\] ([^"]+)"', side); va = re.search(r'"vaxis" "\[([^\]]+)\] ([^"]+)"', side)
    if abs(pts[0][2] - pts[1][2]) < 1e-3 and abs(pts[1][2] - pts[2][2]) < 1e-3:
        continue  # horizontal face; only the vertical panels form the horizon
    xy = sorted({(round(p[0], 3), round(p[1], 3)) for p in pts})
    zs = [p[2] for p in pts]
    (ax, ay), (bx, by) = xy[0], xy[-1]
    faces.append(dict(a=xy[0], b=xy[-1], z0=min(zs), z1=max(zs),
                      u=[float(v) for v in ua.group(1).split()], us=float(ua.group(2)),
                      v=[float(v) for v in va.group(1).split()], vs=float(va.group(2))))
print('panel faces', len(faces))

tex = Image.open(tex_path).convert('RGBA'); tw, th = tex.size; tp = tex.load()
pano = Image.open(pano_in).convert('RGB'); W, H = pano.size; pp = pano.load()

def hit(dx, dy):
    """Nearest panel along a horizontal direction: (distance, face, x, y)."""
    best = None
    for f in faces:
        (ax, ay), (bx, by) = f['a'], f['b']
        ex, ey = bx - ax, by - ay
        den = dx * ey - dy * ex
        if abs(den) < 1e-9:
            continue
        t = (ax * ey - ay * ex) / den          # ray distance
        s = (ax * dy - ay * dx) / den          # position along the face, 0..1
        if t > 0 and -1e-6 <= s <= 1 + 1e-6 and (best is None or t < best[0]):
            best = (t, f, t * dx, t * dy)
    return best

painted = 0
for x in range(W):
    ph = math.pi * (1 - 2 * (x + 0.5) / W)    # same azimuth convention as cube2latlong.py
    h = hit(math.cos(ph), math.sin(ph))
    if not h:
        continue
    t, f, hx, hy = h
    # the ring faces the camera, so the facing normal is just the reversed view direction; using it per
    # column instead of per face keeps the 32 flat panels from showing as stripes of lightmap brightness
    L = ambient + sun * max(0.0, -(math.cos(ph) * to_sun[0] + math.sin(ph) * to_sun[1]))
    for y in range(H):
        el = math.pi * (0.5 - (y + 0.5) / H)
        if abs(el) > 1.2:
            continue
        z = eye + t * math.tan(el)
        if not (f['z0'] <= z <= f['z1']):
            continue
        p = (hx + cam[0], hy + cam[1], z + cam[2])  # texture axes are in world space
        u = (sum(a * b for a, b in zip(p, f['u'][:3])) / f['us'] + f['u'][3]) / tw
        v = (sum(a * b for a, b in zip(p, f['v'][:3])) / f['vs'] + f['v'][3]) / th
        r, g, b, a = tp[int(u % 1 * tw) % tw, min(th - 1, max(0, int(v * th)))]  # Source clamps v
        al = a / 255.0
        if al <= 0:
            continue
        pp[x, y] = tuple(srgb(lin[c] * L * k * al + lin[s] * (1 - al)) for c, k, s in zip((r, g, b), TINT, pp[x, y]))
        painted += 1
pano.save(pano_out)
print('painted pixels', painted, 'of', W * H)
