# Minimal minidump reader: print the exception code/address and which module it falls in.
import struct,sys
d=open(sys.argv[1],'rb').read()
n,off=struct.unpack_from('<II',d,8)
streams={}
for i in range(n):
    t,sz,rva=struct.unpack_from('<III',d,off+i*12); streams[t]=(sz,rva)
def name(rva):
    l=struct.unpack_from('<I',d,rva)[0]; return d[rva+4:rva+4+l].decode('utf-16-le')
mods=[]
if 4 in streams:
    _,rva=streams[4]; cnt=struct.unpack_from('<I',d,rva)[0]
    for i in range(cnt):
        b=rva+4+i*108; base,size=struct.unpack_from('<QI',d,b); nrva=struct.unpack_from('<I',d,b+20)[0]
        mods.append((base,size,name(nrva).split('\\')[-1]))
if 6 in streams:
    _,rva=streams[6]; code,flags,rec,addr=struct.unpack_from('<IIQQ',d,rva+8)
    print('code',hex(code),'addr',hex(addr))
    for b,s,nm in mods:
        if b<=addr<b+s: print('in',nm,'+',hex(addr-b))
    np=struct.unpack_from('<I',d,rva+8+24)[0]
    print('params',[hex(x) for x in struct.unpack_from('<%dQ'%min(np,4),d,rva+8+32)])
