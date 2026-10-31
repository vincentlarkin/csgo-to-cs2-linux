# Extract a VPK v1/v2 (single or _dir + _NNN archives). Usage: vpkx.py <x_dir.vpk|x.vpk> <outdir>
import struct, sys, os
path, out = sys.argv[1], sys.argv[2]
d = open(path, 'rb').read()
sig, ver, tree = struct.unpack_from('<III', d, 0)
assert sig == 0x55aa1234, hex(sig)
hdr = 12 if ver == 1 else 28
p = hdr; end = hdr + tree
def cstr():
    global p
    e = d.index(b'\0', p); s = d[p:e].decode('utf-8', 'replace'); p = e + 1; return s
base = path[:-8] if path.endswith('_dir.vpk') else None
n = 0
while True:
    ext = cstr()
    if not ext: break
    while True:
        dirn = cstr()
        if not dirn: break
        while True:
            name = cstr()
            if not name: break
            crc, pre, arc, off, ln, term = struct.unpack_from('<IHHIIH', d, p); p += 18
            pre_data = d[p:p + pre]; p += pre
            if arc == 0x7fff:
                data = d[end + off:end + off + ln]
            else:
                data = open('%s_%03d.vpk' % (base, arc), 'rb').read()[off:off + ln] if ln else b''
            rel = os.path.join('' if dirn == ' ' else dirn, name + ('.' + ext if ext != ' ' else ''))
            fp = os.path.join(out, rel); os.makedirs(os.path.dirname(fp) or out, exist_ok=True)
            open(fp, 'wb').write(pre_data + data); n += 1
print('extracted', n)
