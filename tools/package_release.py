"""Build deterministic v1.0.1 public assets from the manifest, outside the repo."""
import argparse
import hashlib
from pathlib import Path
import zipfile

VERSION='1.0.1'
root=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--output',type=Path,required=True)
a=ap.parse_args()
out=a.output.resolve()
if out.is_relative_to(root):
    ap.error('asset output must be outside the source tree')
out.mkdir(parents=True,exist_ok=True)
paths=[]
for line in (root/'SHA256SUMS').read_text().splitlines():
    digest,name=line.split('  ',1)
    p=root/name
    if not p.resolve().is_relative_to(root) or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
        raise ValueError('manifest mismatch: '+name)
    paths.append(name)
paths.append('SHA256SUMS')
if len(set(paths))!=len(paths):
    raise ValueError('duplicate manifest path')

def build(name,prefix,names):
    target=out/name
    if target.exists():
        raise ValueError('refusing to overwrite '+str(target))
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for relative in sorted(names):
            info=zipfile.ZipInfo(prefix+'/'+relative,(2026,10,14,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16
            z.writestr(info,(root/relative).read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return target

assets=[build('family169-certificate-atlas-v'+VERSION+'.zip','family169-certificate-atlas-v'+VERSION,paths),
        build('family169-independent-audit-v'+VERSION+'.zip','family169-independent-audit-v'+VERSION,
              [p for p in paths if p.startswith('independent/')]+['LICENSE','NOTICE','PROVENANCE.json'])]
checks=out/'SHA256SUMS'
checks.write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in assets))
for p in assets:
    print(p.name,p.stat().st_size,hashlib.sha256(p.read_bytes()).hexdigest())
