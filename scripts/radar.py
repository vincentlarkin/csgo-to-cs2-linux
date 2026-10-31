# Render a top-down CS radar image from a Source 1 VMF's brushes (axis-aligned bounding boxes),
# in the usual radar style: light walkable floor, mid-tone cover, dark walls.
# Usage: radar.py <map.vmf> <out.png> <size_px> <pos_x> <pos_y> <scale> [max_bottom_z]
# pos_x/pos_y are the world coordinates of the image's top-left corner and scale is world
# units per pixel at 1024 px, exactly as in resource/overviews/<map>.txt.
import re, sys
from PIL import Image, ImageDraw, ImageFilter

vmf, out = sys.argv[1], sys.argv[2]
size = int(sys.argv[3]); pos_x, pos_y, scale = map(float, sys.argv[4:7])
max_bottom = float(sys.argv[7]) if len(sys.argv) > 7 else 1e9  # skip brushes floating above this
px = scale * 1024 / size  # world units per output pixel

src = open(vmf, errors='replace').read().replace('\r', '')
boxes = []
for s in re.findall(r'\n\tsolid\n\t\{.*?\n\t\}', src, re.S):
    if all(m.upper().startswith('TOOLS/') for m in re.findall(r'"material" "([^"]+)"', s)):
        continue
    pts = [tuple(map(float, p)) for p in re.findall(r'\(([-\d.e]+) ([-\d.e]+) ([-\d.e]+)\)', s)]
    lo = [min(p[i] for p in pts) for i in range(3)]; hi = [max(p[i] for p in pts) for i in range(3)]
    if lo[2] > max_bottom:
        continue
    boxes.append((lo, hi))
zmin = min(b[1][2] for b in boxes); zmax = max(b[1][2] for b in boxes)

img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
def shade(top):
    rise = top - zmin
    if rise <= 16: return (150, 178, 196, 255)   # floor
    if rise <= 240: return (88, 112, 130, 255)   # cover / platforms a player can stand on
    return (24, 32, 42, 255)                     # walls and tall structures
for lo, hi in sorted(boxes, key=lambda b: b[1][2]):
    rect = [(lo[0] - pos_x) / px, (pos_y - hi[1]) / px, (hi[0] - pos_x) / px, (pos_y - lo[1]) / px]
    d.rectangle(rect, fill=shade(hi[2]))
# Thin dark outline around the playable shape so edges read clearly on the HUD.
alpha = img.getchannel('A')
edge = alpha.filter(ImageFilter.MaxFilter(5))
outline = Image.new('RGBA', img.size, (10, 14, 20, 255)); outline.putalpha(edge)
outline.alpha_composite(img)
outline.save(out)
print('boxes', len(boxes), 'z', zmin, zmax)
