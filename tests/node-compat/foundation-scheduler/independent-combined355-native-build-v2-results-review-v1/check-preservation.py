"""Independent finite DATA replay; no owner imports, Git or native tools."""
from pathlib import Path
import ast,hashlib,json,os,stat,tarfile
P=Path(__file__).resolve().parent;C=P.parent/'combined-native-build-controller-candidate-v2';REPO=P.parents[3];checks=0;seen={}
def need(x,label):
 global checks
 assert x,label;checks+=1
def row(p,h=None,n=None):
 p=Path(p);a=p.stat();need(stat.S_ISREG(p.lstat().st_mode),'regular current file');v=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):v.update(b)
 z=p.stat();need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns),'stable read')
 need((h is None or v.hexdigest()==h)and(n is None or a.st_size==n),'exact file bytes');r=dict(path=str(p),sha256=v.hexdigest(),bytes=a.st_size);seen[str(p)]=r;return r
def read(p):row(p);return json.loads(Path(p).read_bytes())
r=read(C/'references.json');j=read(r['stageResult']['path']);plan=read(r['stageCopyPlan']['path']);source=Path(j['configuredSourceRoot'])
need(len(plan['files'])==1613 and j['copies']==plan['files']==j['copiesCompleted'],'whole actual1613 stage plan')
for x in plan['files']:
 a=Path(x['original']);b=source/x['path'];row(a,x['sha256'],x['bytes']);row(b,x['sha256'],x['bytes']);aa=a.stat();bb=b.stat();need(stat.S_IMODE(aa.st_mode)==stat.S_IMODE(bb.st_mode)==x['sourceMode'],'stage modes unchanged');need((aa.st_dev,aa.st_ino)!=(bb.st_dev,bb.st_ino)and bb.st_nlink==1,'stage ordinary distinct inode')
old=read(r['protectedTreeInventories'][0]['path']);oldroot=Path(old['root']);actual=set()
for q in oldroot.rglob('*'):
 if q.is_file()or q.is_symlink():need(not q.is_symlink(),'no old unexpected symlink');actual.add(str(q.relative_to(oldroot)))
need(actual=={x['path']for x in old['files']}and len(actual)==755,'exact historical failed work membership')
for x in old['files']:
 q=oldroot/x['path'];row(q,x['sha256'],x['bytes']);need(stat.S_IMODE(q.stat().st_mode)==x['mode'],'old failed work mode')
d=read(C/'derivations.json');edits=0
for x in d['files']:
 a=Path(x['donor']['path']).read_bytes();b=Path(x['after']['path']).read_bytes();row(x['donor']['path'],x['donor']['sha256'],x['donor']['bytes']);row(x['after']['path'],x['after']['sha256'],x['after']['bytes']);forward=a;inverse=b
 for e in reversed(x['edits']):
  bef=e['before'].encode();aft=e['after'].encode();o=e['beforeOffset'];need(forward[o:o+len(bef)]==bef,'exact donor edit slice');forward=forward[:o]+aft+forward[o+len(bef):]
 for e in reversed(x['edits']):
  bef=e['before'].encode();aft=e['after'].encode();o=e['afterOffset'];need(inverse[o:o+len(aft)]==aft,'exact successor edit slice');inverse=inverse[:o]+bef+inverse[o+len(aft):]
 need(forward==b and inverse==a,'full forward/inverse source derivation');edits+=len(x['edits'])
need(len(d['files'])==5 and edits==43,'actual five donor files43 edits')
# Interpret only actual literal path assignments; do not inject replacement OWN.
tree=ast.parse((C/'controller.py').read_bytes());constants={}
def literal(n):
 if isinstance(n,ast.Constant):return n.value
 if isinstance(n,ast.Name):return constants[n.id]
 if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='Path'and len(n.args)==1:return Path(literal(n.args[0]))
 if isinstance(n,ast.BinOp)and isinstance(n.op,ast.Div):return literal(n.left)/literal(n.right)
 raise ValueError()
for n in tree.body:
 if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name):
  try:constants[n.targets[0].id]=literal(n.value)
  except(ValueError,KeyError):pass
need(constants['REPO']==REPO and constants['OWN']==C,'actual module OWN/REPO constants')
for k,v in dict(SOURCE=source,WORK=Path('/private/tmp/starling-node-compat/combined-native355-v2-build'),FREEZE=Path('/private/tmp/starling-node-compat/combined-native355-v2-freeze'),BUILD_OUTPUT=Path('/private/tmp/starling-node-compat/combined-native355-v2-normal-off-build-root'),OUT=Path('/private/tmp/starling-node-compat/combined-native355-v2-normal-off-build-external-root'),OBSERVER=Path('/private/tmp/starling-node-compat/combined-native355-v2-build-root-observer'),TIMEOUT=7200,START_FREE=2147483648,STOP_FREE=838860800).items():need(constants[k]==v,'actual module path/budget '+k)
need(not constants['FREEZE'].exists(),'no actual freeze result')
head=source/'.git/HEAD';row(head);need(head.read_text().strip()==j['detachedHead'],'actual detached Git HEAD')
need(not(source/'.git/objects/info/alternates').exists(),'no staged Git alternates')
original_objects={(q.stat().st_dev,q.stat().st_ino)for q in(REPO/'.git/objects').rglob('*')if q.is_file()}
staged_objects=[q for q in(source/'.git/objects').rglob('*')if q.is_file()]
need(all((q.stat().st_dev,q.stat().st_ino)not in original_objects and q.stat().st_nlink==1 for q in staged_objects),'Git object inode disjointness; no Git invoked')
dist=read(P/'distribution-review.json');aliases=dist['referenceAliases'];hard=[]
for s in dist['distributions']:
 with tarfile.open(s['archive']['path'])as t:
  ms=t.getmembers();prefix={'wasi-sdk30':'wasi-sdk-30.0-arm64-macos','spidermonkey147':'spidermonkey-dist-release','ComponentizeJS-external-source':'ComponentizeJS-'+json.loads(Path(json.loads((P/'audit-data.json').read_text())['metadata']['path']).read_text())['componentizeJsRevision']}[s['name']];root=Path(s['root'])
  for e in ms:
   if e.islnk():
    rel=e.name.removeprefix(prefix+'/');other=e.linkname.removeprefix(prefix+'/');a=root/rel;b=root/other;need(os.path.samefile(a,b),'actual archive-declared hardlink');hard.append(dict(path=str(a),target=str(b),archiveMember=e.name,archiveLink=e.linkname,distribution=s['name'],sameInode=True))
for a in aliases:need(Path(a['path']).is_symlink()and os.readlink(a['path'])==a['linkText']and str(Path(a['path']).resolve())==a['resolved'],'current exact reference symlink')
for x in r['hostAliases']if 'hostAliases'in r else[]:pass
out=dict(schemaVersion=1,passed=True,checks=checks,stageCopies=1613,failedWorkFiles=755,sourceDerivationFiles=5,sourceReversibleEdits=43,actualModuleConstantsVerified=True,stagedGitObjectFiles=len(staged_objects),freezeRootAbsent=True,extraInputs=list(seen.values()),ownerToolsInvoked=False)
(P/'preservation-review.json').write_text(json.dumps(out,indent=2)+'\n');(P/'reference-aliases.json').write_text(json.dumps(dict(schemaVersion=1,scope='Original archive and installed reference aliases; not frozen copy inode independence',symlinks=aliases,archiveHardlinks=hard),indent=2)+'\n')
print(json.dumps(dict(preservationAuditPassed=True,checks=checks,files=len(seen),stageCopies=1613,failedWorkFiles=755,sourceEdits=43,symlinks=len(aliases),archiveHardlinks=len(hard))))
