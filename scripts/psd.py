# Write an image as a flat, uncompressed RGBA Photoshop file (CS2 radar sources are .psd).
# Usage: psd.py <in.png> <out.psd>
import struct, sys
from PIL import Image
im = Image.open(sys.argv[1]).convert('RGBA'); w, h = im.size
hdr = b'8BPS' + struct.pack('>H6xHIIHH', 1, 4, h, w, 8, 3)  # version 1, 4 channels, 8-bit RGB
body = struct.pack('>III', 0, 0, 0) + struct.pack('>H', 0)    # no color data/resources/layers, raw
body += b''.join(ch.tobytes() for ch in im.split())            # planar R, G, B, A
open(sys.argv[2], 'wb').write(hdr + body)
