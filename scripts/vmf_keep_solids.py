# Keep only world solids with index in [lo,hi). Usage: vmf_keep_solids.py <in> <out> <lo> <hi>
import re,sys
src=open(sys.argv[1],newline='').read(); lo,hi=int(sys.argv[3]),int(sys.argv[4])
w=re.search(r'^world\r?\n\{.*?^\}\r?\n',src,re.S|re.M)
body=w.group(0); sols=list(re.finditer(r'^\tsolid\r?\n\t\{.*?^\t\}\r?\n',body,re.S|re.M))
out=[];i=0
for k,m in enumerate(sols):
    out.append(body[i:m.start()]); i=m.end()
    if lo<=k<hi: out.append(m.group(0))
out.append(body[i:])
open(sys.argv[2],'w',newline='').write(src[:w.start()]+''.join(out)+src[w.end():])
print(len(sols))
