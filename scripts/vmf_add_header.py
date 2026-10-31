# Prepend the versioninfo/viewsettings blocks that BSPSource omits and source1import requires.
import sys
p=sys.argv[1]; src=open(p,newline='').read()
if src.lstrip().startswith('versioninfo'): sys.exit('already has header')
hdr=('versioninfo\n{\n\t"editorversion" "400"\n\t"editorbuild" "10342"\n\t"mapversion" "1"\n\t"formatversion" "100"\n\t"prefab" "0"\n}\n'
     'viewsettings\n{\n\t"bSnapToGrid" "1"\n\t"bShowGrid" "1"\n\t"bShowLogicalGrid" "0"\n\t"nGridSpacing" "8"\n\t"bShow3DGrid" "0"\n}\n')
nl='\r\n' if '\r\n' in src[:2000] else '\n'
open(p,'w',newline='').write(hdr.replace('\n',nl)+src)
