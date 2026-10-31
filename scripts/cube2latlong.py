# Source 1 skybox faces (Z up) -> equirectangular panorama for CS2 sky.vfx
import math,sys
from PIL import Image
src,out=sys.argv[1],sys.argv[2]
F={k:Image.open(f"{src}{k}.png").convert('RGB') for k in ('ft','bk','lf','rt','up','dn')}
# Source faces: turning right from ft gives lf; up is stored rotated 90 deg clockwise
F['up']=F['up'].rotate(270); F['dn']=F['dn'].rotate(90)
N=F['ft'].size[0]; P={k:v.load() for k,v in F.items()}
W,H=4096,2048; img=Image.new('RGB',(W,H)); o=img.load()
for y in range(H):
    th=math.pi*(0.5-(y+0.5)/H); cz=math.sin(th); r=math.cos(th)
    for x in range(W):
        ph=math.pi*(1-2*(x+0.5)/W); dx=r*math.cos(ph); dy=r*math.sin(ph); dz=cz
        ax,ay,az=abs(dx),abs(dy),abs(dz)
        if ax>=ay and ax>=az:
            if dx>0: f,u,v='ft',-dy/ax,-dz/ax
            else:    f,u,v='bk',dy/ax,-dz/ax
        elif ay>=az:
            if dy>0: f,u,v='rt',dx/ay,-dz/ay
            else:    f,u,v='lf',-dx/ay,-dz/ay
        elif dz>0:   f,u,v='up',-dy/az,dx/az
        else:        f,u,v='dn',-dy/az,-dx/az
        px=min(N-1,int((u+1)/2*N)); py=min(N-1,int((v+1)/2*N))
        o[x,y]=P[f][px,py]
img.save(out)
