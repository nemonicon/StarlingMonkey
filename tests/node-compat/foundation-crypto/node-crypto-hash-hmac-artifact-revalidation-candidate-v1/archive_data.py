"""Read/hash-only distribution comparisons. No extraction or executable calls."""
from pathlib import Path
import hashlib,os,tarfile
def digest(stream):
 h=hashlib.sha256();n=0
 for b in iter(lambda:stream.read(1048576),b''):h.update(b);n+=len(b)
 return h.hexdigest(),n
def verify(metadata,refs,io):
 m=metadata;work=Path(refs['workRoot']);aliases=[];hardlinks=[];summaries=[]
 def fixed(p,sha=None,size=None):
  r=io.row(Path(p));assert sha is None or r['sha256']==sha;assert size is None or r['bytes']==size;io.checked(r);return r
 sdk=next(r for r in m['downloadedArchives']if Path(r['path']).name=='wasi-sdk-30.0-arm64-macos.tar.gz')
 specs=[dict(name='wasi-sdk30',archive=sdk,root=work/'cache/wasi-sdk/85e6',prefix='wasi-sdk-30.0-arm64-macos',overrides={},stamp=None),dict(name='spidermonkey147',archive=dict(path=str(work/'spidermonkey-release.tar.gz'),sha256=m['archivePins']['spiderMonkeySha256']),root=Path(m['zlibSelectedCodecInput']['selectedDistribution']),prefix='spidermonkey-dist-release',overrides={},stamp=m['archivePins']['spiderMonkeySha256']),dict(name='ComponentizeJS-original-context',archive=dict(path=str(work/'componentize-source.tar.gz'),sha256=m['archivePins']['componentizeJsSha256']),root=Path(m['combinedNativeSourcePolicy']['externalConfiguredSourceRoot']),prefix='ComponentizeJS-'+m['componentizeJsRevision'],overrides={r['path']:r['sha256']for r in m['componentizeSourceManifest']},stamp=m['archivePins']['componentizeJsSha256'])]
 for prefix,cache in [('binaryen-version_123','binaryen/1b13'),('wasm-tools-1.235.0-aarch64-macos','wasm-tools/1448'),('wasmtime-v42.0.1-aarch64-macos','wasmtime/487d'),('weval-v0.5.1-aarch64-macos','weval/9707')]:
  archive=next(r for r in m['downloadedArchives']if Path(r['path']).name.startswith(prefix))
  specs.append(dict(name=prefix,archive=archive,root=work/'cache'/cache,prefix=prefix,overrides={},stamp=None))
 for spec in specs:
  archive=fixed(spec['archive']['path'],spec['archive']['sha256']);root=spec['root'];expected={};changed=[]
  with tarfile.open(archive['path'])as tar:
   for entry in tar:
    name=entry.name.rstrip('/');assert name==spec['prefix']or name.startswith(spec['prefix']+'/');relative=name[len(spec['prefix']):].lstrip('/')
    if not relative:continue
    assert all(x not in('','.','..')for x in relative.split('/'))and relative not in expected
    target=root/relative;expected[relative]=entry.type
    if entry.isdir():assert target.is_dir()and not target.is_symlink()
    elif entry.issym():
     assert target.is_symlink()and os.readlink(target)==entry.linkname;aliases.append(dict(path=str(target),linkText=entry.linkname,resolved=str(target.resolve(strict=True))))
    elif entry.isfile():
     h,n=digest(tar.extractfile(entry));override=spec['overrides'].get(relative)
     if override is not None:changed.append(relative);h=override;n=None
     fixed(target,h,n)
    elif entry.islnk():
     assert entry.linkname.startswith(spec['prefix']+'/');other=root/entry.linkname[len(spec['prefix'])+1:];a=target.stat();b=other.stat();assert(a.st_dev,a.st_ino)==(b.st_dev,b.st_ino);fixed(target)
     hardlinks.append(dict(path=str(target),target=str(other),device=a.st_dev,inode=a.st_ino))
    else:raise AssertionError('unsupported distribution member')
  if spec['name']=='ComponentizeJS-original-context':
   assert(root/'lib').is_dir()and not(root/'lib').is_symlink();fixed(root/'lib/starlingmonkey_embedding.wasm',refs['engine']['sha256'],refs['engine']['bytes']);expected.update({'lib':b'5','lib/starlingmonkey_embedding.wasm':b'0'})
  if spec['stamp']:
   p=root/'.source-archive-sha256';assert p.read_text()==spec['stamp']+'\n';fixed(p);expected['.source-archive-sha256']=b'0'
  actual=set()
  for parent,dirs,files in os.walk(root,followlinks=False):
   for name in dirs+files:actual.add((Path(parent)/name).relative_to(root).as_posix())
  assert actual==set(expected)and set(changed)==set(spec['overrides'])
  summaries.append(dict(name=spec['name'],archive=archive,root=str(root),entries=len(expected),wholeMembershipVerified=True,externalOverrides=changed))
 ssl=m['openssl'];audit=ssl['completeSourceAudit'];fixed(audit['archivePath'],audit['archiveSha256']);expected={}
 with tarfile.open(audit['archivePath'])as tar:
  for entry in tar:
   if not entry.isfile():continue
   prefix,sep,name=entry.name.partition('/');assert prefix=='openssl-3.0.17'and sep and name not in expected and all(x not in('','.','..')for x in name.split('/'))
   h,n=digest(tar.extractfile(entry));override=audit['patchedSources'].get(name);expected[name]=override or h;fixed(Path(audit['sourceDirectory'])/name,override or h,None if override else n)
 actual={p.relative_to(audit['sourceDirectory']).as_posix()for p in Path(audit['sourceDirectory']).rglob('*')if p.is_file()};assert not any(p.is_symlink()for p in Path(audit['sourceDirectory']).rglob('*'))
 assert actual==set(expected)and len(expected)==4650
 canonical=[dict(path=n,sha256=h)for n,h in sorted(expected.items())]
 import json
 assert hashlib.sha256(json.dumps(canonical,separators=(',',':')).encode()).hexdigest()==audit['sourceManifestSha256']
 return dict(schemaVersion=1,distributions=summaries,opensslSources=4650,referenceAliases=aliases,archiveHardlinks=hardlinks,wholeCurrentDistributionBytesAndMembershipVerified=True,toolsOrNativeCodeInvoked=False)
