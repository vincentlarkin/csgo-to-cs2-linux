# Remove top-level VMF entity blocks by classname. Usage: vmf_drop_ents.py <in.vmf> <out.vmf> <classname>...
import re,sys
src=open(sys.argv[1],newline='').read(); drop=set(sys.argv[3:]); out=[]; i=0
for m in re.finditer(r'^entity\r?\n\{.*?^\}\r?\n',src,re.S|re.M):
    cls=re.search(r'"classname" "([^"]+)"',m.group(0)).group(1)
    out.append(src[i:m.start()]); i=m.end()
    if cls in drop: print('dropped',cls)
    else: out.append(m.group(0))
out.append(src[i:]); open(sys.argv[2],'w',newline='').write(''.join(out))
