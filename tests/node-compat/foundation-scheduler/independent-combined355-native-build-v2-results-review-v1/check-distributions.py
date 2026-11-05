"""Whole installed SDK/SM/external source versus pinned archive DATA, no tools."""
from pathlib import Path
import hashlib,json,os,tarfile
P=Path(__file__).resolve().parent;d=json.loads((P/'audit-data.json').read_bytes());m=json.loads(Path(d['metadata']['path']).read_bytes());work=Path(d['workRoot']);seen={};checks=0
def need(v,n):
 global checks
 assert v,n;checks+=1
def digest(stream):
 h=hashlib.sha256();n=0
 for b in iter(lambda:stream.read(1048576),b''):h.update(b);n+=len(b)
 return h.hexdigest(),n
def verify(p,h=None,size=None):
 p=Path(p);a=p.stat()
 with p.open('rb')as f:got,n=digest(f)
 b=p.stat();need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns),'stable actual distribution file');need((h is None or got==h)and(size is None or n==size),'exact installed archive member bytes');seen[str(p)]=dict(path=str(p),sha256=got,bytes=n);return seen[str(p)]
sdk=next(r for r in m['downloadedArchives']if Path(r['path']).name=='wasi-sdk-30.0-arm64-macos.tar.gz');build=Path(m['cmakeCachePath']).parent
specs=[dict(name='wasi-sdk30',archive=sdk,root=work/'cache/wasi-sdk/85e6',prefix='wasi-sdk-30.0-arm64-macos',overrides={},stamp=None),dict(name='spidermonkey147',archive=dict(path=str(work/'spidermonkey-release.tar.gz'),sha256=m['archivePins']['spiderMonkeySha256']),root=Path(m['zlibSelectedCodecInput']['selectedDistribution']),prefix='spidermonkey-dist-release',overrides={},stamp=m['archivePins']['spiderMonkeySha256']),dict(name='ComponentizeJS-external-source',archive=dict(path=str(work/'componentize-source.tar.gz'),sha256=m['archivePins']['componentizeJsSha256']),root=Path(next(line.split('=',1)[1]for line in Path(m['cmakeCachePath']).read_text().splitlines()if line.startswith('CMAKE_HOME_DIRECTORY:'))),prefix='ComponentizeJS-'+m['componentizeJsRevision'],overrides={r['path']:r['sha256']for r in m['componentizeSourceManifest']},stamp=m['archivePins']['componentizeJsSha256'])]
summaries=[];aliases=[]
for spec in specs:
 archive=verify(spec['archive']['path'],spec['archive']['sha256']);root=spec['root'];expected={};changed=[]
 with tarfile.open(archive['path'])as tar:
  for entry in tar.getmembers():
   name=entry.name.rstrip('/');need(name==spec['prefix']or name.startswith(spec['prefix']+'/'),'exact bounded archive prefix')
   relative=name[len(spec['prefix']):].lstrip('/')
   if not relative:continue
   need(all(v not in('','.','..')for v in relative.split('/'))and relative not in expected,'finite unique archive member');target=root/relative;expected[relative]=entry.type
   if entry.isdir():need(target.is_dir()and not target.is_symlink(),'ordinary installed archive directory')
   elif entry.issym():need(target.is_symlink()and os.readlink(target)==entry.linkname,'exact declared installed SDK/source alias');aliases.append(dict(path=str(target),linkText=entry.linkname,resolved=str(target.resolve()),distribution=spec['name']))
   elif entry.isfile():
    h,n=digest(tar.extractfile(entry));override=spec['overrides'].get(relative)
    if override is not None:changed.append(dict(path=relative,beforeSha256=h,afterSha256=override));h=override;n=None
    need(target.is_file()and not target.is_symlink(),'ordinary installed archive file');verify(target,h,n)
   elif entry.islnk():
    other=root/entry.linkname.removeprefix(spec['prefix']+'/');need(target.is_file()and os.path.samefile(target,other),'exact declared SDK hard-link reference');verify(target)
   else:raise AssertionError('unsupported archive entry type')
 generated=[]
 if spec['name']=='ComponentizeJS-external-source':
  # The genuine recipe mkdir/lib and native CMake target publish this output;
  # it is new build evidence, never represented as an archive source member.
  need((root/'lib').is_dir()and not(root/'lib').is_symlink(),'declared native output directory')
  generated.append(verify(root/'lib/starlingmonkey_embedding.wasm',d['engine']['sha256'],d['engine']['bytes']))
  expected['lib']=b'5';expected['lib/starlingmonkey_embedding.wasm']=b'0'
 if spec['stamp']:
  stamp=root/'.source-archive-sha256';need(stamp.read_text()==spec['stamp']+'\n','actual source archive stamp');verify(stamp);expected['.source-archive-sha256']=b'0'
 actual=set()
 for parent,dirs,files in os.walk(root,followlinks=False):
  for n in dirs+files:actual.add(str((Path(parent)/n).relative_to(root)))
 need(actual==set(expected),'whole actual distribution membership')
 need(set(r['path']for r in changed)==set(spec['overrides']),'only exact declared external3 afterimages')
 summaries.append(dict(name=spec['name'],archive=archive,root=str(root),entries=len(expected),regularFiles=sum(t in[b'0',b'\x00']for t in expected.values()),declaredAliases=sum(t==b'2'for t in expected.values()),currentExternalOverrides=changed,separateActualGeneratedOutputs=generated,wholeMembershipVerified=True))
cache={}
for line in Path(m['cmakeCachePath']).read_text().splitlines():
 k,s,v=line.partition(':')
 if s and'='in v:cache[k]=v.partition('=')[2]
cbindgen=verify(Path(cache['CBINDGEN_EXECUTABLE']).resolve());need(cbindgen['path']==str(work/'tools/bin/cbindgen'),'actual selected cbindgen physical path')
value=dict(schemaVersion=1,verifiedPassed=True,checks=checks,distributions=summaries,referenceAliases=aliases,cbindgen=cbindgen,extraInputs=list(seen.values()),archivedAndInstalledReferencesOnly=True,filesCopiedOrToolsInvoked=False)
with(P/'distribution-review.json').open('x')as f:json.dump(value,f,indent=2);f.write('\n')
print(json.dumps(dict(distributionReviewPassed=True,checks=checks,files=len(seen),distributions=[dict(name=r['name'],entries=r['entries'])for r in summaries],ownerActionsInvoked=False)))
