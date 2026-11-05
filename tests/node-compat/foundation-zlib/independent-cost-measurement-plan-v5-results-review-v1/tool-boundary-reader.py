"""Typed physical publication/tool-tree verification. Read/hash only."""
from pathlib import Path
import hashlib,json,os
P=Path(__file__).resolve().parent
m=json.loads((P/'rehashed-inputs.json').read_bytes());rows={r['path']:r for r in m['files']}
def row(p):
 p=Path(p);h=hashlib.sha256();n=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b);n+=len(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=n)
def verified(p):
 p=Path(p);r=row(p);w=rows[str(p)];assert {k:r[k]for k in ['path','sha256','bytes']}=={k:w[k]for k in ['path','sha256','bytes']};return json.loads(p.read_bytes())
treespath=Path(__file__).resolve().parents[1]/'cost-tooling-candidate-v3/tool-trees.json'
t=verified(treespath);root=Path('/private/tmp/starling-node-compat/zlib-cost-source-v3');ix=verified(root/'index.json')
assert ix['state']=='FRESH_ZLIB350_COST_SOURCE_PUBLICATION_V1' and len(t['trees'])==2 and len(t['links'])==len(ix['links'])==22
assert root.stat().st_ino==ix['rootIdentity']['inode'] and root.stat().st_dev==ix['rootIdentity']['device']
foundfiles=set();foundlinks=set();founddirs=set()
for parent,dirs,files in os.walk(root,followlinks=False):
 for name in dirs+files:
  p=Path(parent)/name;n=str(p.relative_to(root))
  if p.is_symlink():foundlinks.add(n)
  elif p.is_dir():founddirs.add(n)
  else:assert p.is_file();foundfiles.add(n)
assert foundfiles=={r['path']for r in ix['files']}|{'index.json','completion.json'}
assert foundlinks=={r['destination']for r in t['links']}
assert founddirs==set(ix['directories'])
links=[]
for r in t['links']:
 p=root/r['destination'];assert p.is_symlink() and os.readlink(p)==r['newLinkText'] and str(p.resolve())==str(root/r['mappedTarget'])
 assert p.is_dir() if r['targetKind']=='directory'else p.is_file()
 links.append(dict(path=str(p),linkText=os.readlink(p),resolved=str(p.resolve()),kind=r['targetKind']))
counts=[]
for tree in t['trees']:
 actual={n for n in foundfiles|foundlinks|founddirs if n.startswith(tree['publicationRoot']+'/')}
 expected={r['destination'] if 'destination'in r else tree['publicationRoot']+'/'+r['path']for r in tree['entries']}
 assert actual==expected
 n=0
 for r in tree['entries']:
  if r['kind']=='file':
   p=root/r['destination'];a=row(p);assert not p.is_symlink() and a['sha256']==r['sha256'] and a['bytes']==r['bytes'];n+=1
 counts.append(dict(name=tree['name'],entries=len(tree['entries']),physicalFiles=n))
(P/'tool-boundary-results.json').write_text(json.dumps(dict(schemaVersion=1,verifiedPassed=True,actualSourcePublicationIndex=row(root/'index.json'),actualSourcePublicationRootIdentity=ix['rootIdentity'],toolTrees=counts,links=links,linkCount=22,completePublicationMembershipVerified=True,publishedRegularFiles=len(foundfiles),publishedDirectories=len(founddirs),ownerActionsInvoked=False),indent=2)+'\n')
print(json.dumps(dict(toolTrees=2,links=22,publishedRegularFiles=len(foundfiles),exactMembership=True)))
