# Rename materials whose names carry GoldSrc prefix characters ({ ~ + -), which Source 2 rejects as
# "illegal resource name" (the map compile then fails on missing materials and crashes).
# Renames the .vmt/.vtf files in a staged materials folder and rewrites references in every .vmt and VMF.
# Usage: vmf_safe_names.py <staged materials dir> <map.vmf>...
import os, re, sys

MAP = {'{': 'alpha_', '~': 'lit_', '+': 'anim_', '-': 'rand_'}
def safe(name):
    out = ''.join(MAP.get(c, c) if not (c.isalnum() or c in '_.') else c for c in name)
    return out.lower()

root = sys.argv[1]
ren = {}  # old material path (lowercase, no extension, relative to materials/) -> new
for d, _, files in os.walk(root):
    for f in files:
        base, ext = os.path.splitext(f)
        if ext.lower() not in ('.vmt', '.vtf') or safe(base) == base.lower():
            continue
        rel = os.path.relpath(os.path.join(d, base), root).replace(os.sep, '/').lower()
        new = os.path.join(d, safe(base) + ext.lower())
        os.rename(os.path.join(d, f), new)
        ren[rel] = os.path.relpath(os.path.join(d, safe(base)), root).replace(os.sep, '/')

if not ren:
    sys.exit('nothing to rename')
for old, new in sorted(ren.items()):
    print(f'{old} -> {new}')
# longest first so a name that prefixes another isn't replaced early
pat = re.compile('|'.join(re.escape(o).replace('/', r'[/\\]') for o in sorted(ren, key=len, reverse=True)), re.I)
fix = lambda m: ren[m.group(0).replace('\\', '/').lower()]
targets = [os.path.join(d, f) for d, _, fs in os.walk(root) for f in fs if f.lower().endswith('.vmt')] + sys.argv[2:]
for p in targets:
    src = open(p, newline='', encoding='latin-1').read()
    out = pat.sub(fix, src)
    if out != src:
        open(p, 'w', newline='', encoding='latin-1').write(out)
