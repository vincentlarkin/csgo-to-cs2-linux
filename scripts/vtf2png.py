# VTF (highest mip, single frame) -> PNG. DXT1/DXT5 and the uncompressed RGB(A)/BGR(A) formats.
# Usage: vtf2png.py <out_dir> <file.vtf>...
import struct,sys,io,os
from PIL import Image
RAW={0:('RGBA',4,'RGBA'),1:('RGBA',4,'ABGR'),2:('RGB',3,'RGB'),3:('RGB',3,'BGR'),
     11:('RGBA',4,'ARGB'),12:('RGBA',4,'BGRA'),16:('RGB',4,'BGRX')}
def conv(src,dst):
    d=open(src,'rb').read()
    w,h=struct.unpack_from('<HH',d,16); fmt=struct.unpack_from('<i',d,52)[0]
    if fmt in RAW:  # mips are stored smallest first, so the full-size image is at the end
        mode,bpp,raw=RAW[fmt]; size=w*h*bpp
        Image.frombuffer(mode,(w,h),d[-size:],'raw',raw,0,1).save(dst); return
    bpp={13:8,15:16}[fmt]; size=max(1,w//4)*max(1,h//4)*bpp
    data=d[-size:]
    four=b'DXT1' if fmt==13 else b'DXT5'
    hdr=struct.pack('<4sIIIIIII44xII4s20xI16x',b'DDS ',124,0x1007|0x80000,h,w,size,0,1,32,4,four,0x1000)
    Image.open(io.BytesIO(hdr+data)).save(dst)
for s in sys.argv[2:]:
    conv(s,os.path.join(sys.argv[1],os.path.basename(s)[:-4]+'.png'))
