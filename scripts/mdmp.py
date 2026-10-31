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
# For a jump to address 0, the caller is the return address on top of the faulting thread's stack.
if 6 in streams:
    _,rva=streams[6]; csz,crva=struct.unpack_from('<II',d,rva+8+152)
    rsp,=struct.unpack_from('<Q',d,crva+0x98)
    mem=[]
    if 5 in streams:
        _,r=streams[5]; c=struct.unpack_from('<I',d,r)[0]
        for i in range(c):
            st,sz,mr=struct.unpack_from('<QII',d,r+4+i*16); mem.append((st,sz,mr))
    def rd(a):
        for st,sz,mr in mem:
            if st<=a<st+sz-8: return struct.unpack_from('<Q',d,mr+a-st)[0]
    shown=0
    for k in range(0,0x400,8):
        v=rd(rsp+k)
        if v is None: break
        for b,s,nm in mods:
            if b<=v<b+s and shown<8: print('stack+%#x'%k,nm,'+',hex(v-b)); shown+=1
