# Draw the small "Ported to CS2 by Vince" plaque decal (muted neon text, pixel penguin, Steam profile URL) in
# the palette of aim_pyrocynical's "Created by Teschke" overlay. Writes <out>_color.tga and <out>_trans.tga
# (1024x512), laid out for the 112x48 overlay it is shown on.
# Usage: make_port_credit.py <out_prefix> [preview.png]
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BOLD = '/usr/share/fonts/open-sans/OpenSans-ExtraBoldItalic.ttf'
REG = '/usr/share/fonts/open-sans/OpenSans-Semibold.ttf'
PINK, CYAN, PALE = (235, 120, 215), (90, 210, 235), (225, 215, 240)
W, H = 1400, 600  # 112x48 overlay aspect, squashed to 1024x512 at the end

PENGUIN = [
    '......KKKK......',
    '....KKKKKKKK....',
    '...KKKKKKKKKK...',
    '...KKWWKKWWKK...',
    '..KKWKWKKWKWKK..',
    '..KKWWWOOWWWKK..',
    '..KKKOOOOOOKKK..',
    '..KKKKOOOOKKKK..',
    '.KKPPPPPPPPPPKK.',
    '.KKWWWWWWWWWPPK.',
    'KKKWWWWWWWWWWPKK',
    'KKWWWWWWWWWWWWKK',
    'KKWWWWWWWWWWWWKK',
    'KKWWWWWWWWWWWWKK',
    '.KWWWWWWWWWWWWK.',
    '.KKWWWWWWWWWWKK.',
    '..KKWWWWWWWWKK..',
    '...KKKKKKKKKK...',
    '..OOOO....OOOO..',
    '.OOOOO....OOOOO.',
]
COLORS = {'K': (25, 18, 45), 'W': (225, 225, 235), 'O': (230, 160, 50), 'P': PINK}

def glow(layer, color, radius, strength):
    a = layer.getchannel('A').filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(radius))
    a = a.point(lambda v: min(255, int(v * strength)))
    g = Image.new('RGBA', layer.size, color + (0,)); g.putalpha(a)
    return g

lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
cell = 22
assert all(len(r) == len(PENGUIN[0]) for r in PENGUIN)
px, py = 60, (H - len(PENGUIN) * cell) // 2
for j, row in enumerate(PENGUIN):
    for i, c in enumerate(row):
        if c in COLORS:
            d.rectangle((px + i * cell, py + j * cell, px + (i + 1) * cell - 1, py + (j + 1) * cell - 1), fill=COLORS[c])
tx = px + len(PENGUIN[0]) * cell + 60
d.text((tx, 120), 'PORTED TO CS2', font=ImageFont.truetype(BOLD, 112), fill=PINK)
d.text((tx, 250), 'BY VINCE', font=ImageFont.truetype(BOLD, 112), fill=PINK)
d.text((tx + 4, 410), 'steamcommunity.com/id/SaintVince', font=ImageFont.truetype(REG, 50), fill=PALE)

out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
out.alpha_composite(glow(lay, CYAN, 8, 0.6))
out.alpha_composite(lay)
out.putalpha(out.getchannel('A').point(lambda v: v * 85 // 100))  # a touch see-through so it sits in the wall

out = out.resize((1024, 512), Image.LANCZOS)
out.convert('RGB').save(sys.argv[1] + '_color.tga')
out.getchannel('A').save(sys.argv[1] + '_trans.tga')
if len(sys.argv) > 2:
    bg = Image.new('RGBA', (W, H), (60, 80, 220, 255))
    bg.alpha_composite(out.resize((W, H)))
    bg.convert('RGB').resize((700, 300)).save(sys.argv[2])
