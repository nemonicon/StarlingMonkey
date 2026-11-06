"""Independent DATA reader only; no target module imports or process/action calls."""
from pathlib import Path
import sys, json, hashlib, os, stat
root=Path(sys.argv[1]); expected=sys.argv[2]
observed={}; families={}; contract_findings=[]; counters={'hashChecks':0,'trees':0}
selected={'/tmp/starling-node-compat/zlib-source-v4/tests/node-compat/classic-streams-admission.mjs','/tmp/starling-node-compat/zlib-source-v4/tests/node-compat/zlib-admission.mjs'}
def physical(p):
 logical=str(p)
 if logical.startswith('/tmp/'):
  assert logical in selected and os.readlink('/tmp')=='private/tmp' and str(Path('/tmp').resolve())=='/private/tmp'
  p=Path('/private'+logical)
 for q in [p,*p.parents]: assert not q.is_symlink(),str(q)
 return p
def checked(row):
 p=physical(Path(row['path'])); s=p.stat();assert stat.S_ISREG(s.st_mode)
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 z=p.stat();assert (s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_mode,z.st_nlink,z.st_size,z.st_mtime_ns,z.st_ctime_ns)
 assert s.st_size==row['bytes'] and h.hexdigest()==row['sha256'],row['path']
 bare={k:row[k] for k in ['path','sha256','bytes']};prior=observed.setdefault(row['path'],bare);assert prior==bare
 counters['hashChecks']+=1
 return p
def read(row):return json.loads(checked(row).read_text())
def desc(p):
 b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def family(row):
 ix=read(row); parent=Path(row['path']).parent; names=['index.json']
 for x in ix['files']:
  p=Path(x['path']);assert not p.is_absolute() and '..' not in p.parts and x['path'] not in names
  names.append(x['path']);checked({**x,'path':str(parent/p)})
 actual=[]
 for d,ds,fs in os.walk(parent):
  for n in ds+fs:assert not (Path(d)/n).is_symlink()
  actual.extend(str((Path(d)/n).relative_to(parent)) for n in fs)
 assert sorted(actual)==sorted(names),str(parent)
 families[row['path']]=row
 return ix
def walk(v):
 if isinstance(v,dict):
  if {'path','sha256','bytes'}<=v.keys():checked(v)
  else:
   for x in v.values():walk(x)
 elif isinstance(v,list):
  for x in v:walk(x)
def tree(spec):
 base=Path(spec['root']);rows=[]
 for d,ds,fs in os.walk(base,followlinks=False):
  for n in ds+fs:
   p=Path(d)/n;s=p.lstat();r=dict(path=str(p.relative_to(base)),kind='link' if p.is_symlink() else 'directory' if p.is_dir() else 'file',mode=stat.S_IMODE(s.st_mode))
   if p.is_symlink():r.update(linkText=os.readlink(p),resolved=str(p.resolve(strict=True)))
   elif p.is_file():b=p.read_bytes();r.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
   else:assert p.is_dir()
   rows.append(r)
 rows.sort(key=lambda r:r['path']);raw=json.dumps(rows,separators=(',',':'),ensure_ascii=False).encode()
 assert stat.S_IMODE(base.stat().st_mode)==spec['rootMode'] and len(rows)==spec['entries'] and hashlib.sha256(raw).hexdigest()==spec['sha256'],str(base)
 counters['trees']+=1
source_index_row=desc(root/'index.json');row=source_index_row;assert row['sha256']==expected
family(row);refs=json.loads((root/'references.json').read_text());walk(refs)
for name in ['nativeSourceIndex','producerIndex','revalidationSourceIndex','fixtureIndex']:
 if name in refs:family(refs[name])
for key in ['oracleReview','artifactReview','knownArtifactReview']:
 if refs.get(key):family(refs[key]['index'])
if refs.get('comparator'):
 ix=family(refs['comparator']['index']); target=refs['comparator']['module']
 assert sum(str(Path(refs['comparator']['index']['path']).parent/x['path'])==target['path'] and x['sha256']==target['sha256'] and x['bytes']==target['bytes'] for x in ix['files'])==1
for pair,contract in [(refs['oracleReview'],refs['oracleContract']),(refs['knownArtifactReview'],refs['knownArtifactContract'])]:
 ix=family(pair['index']);v=read(pair['result']);k=read(contract)
 for row in [pair['result'],contract]:
  assert sum(str(Path(pair['index']['path']).parent/x['path'])==row['path'] and x['sha256']==row['sha256'] and x['bytes']==row['bytes'] for x in ix['files'])==1
 assert v['schemaVersion']==1 and v['verifiedPassed'] is True and v['state']==k['requiredReviewState']
 for group in ['requiredFixedValues','requiredExactDescriptors','requiredVerifiedProperties']:
  for name,value in k.get(group,{}).items():assert v[name]==value,(name,pair)
 if k.get('requiredCoverage') and v.get('coverage')!=k['requiredCoverage']:contract_findings.append(dict(code='M1_REQUIRED_COVERAGE_RESULT_JOIN_MISSING',pair=pair,contract=contract,resultHasCoverage='coverage' in v,requiredCoverage=k['requiredCoverage']))
a=read(refs['revalidationResult']);ledger=read(a['inputHashes'])
for item in ledger['files']:checked(item)
aliases=read(a['referenceAliases'])
for x in aliases['symlinks']:assert os.readlink(x['path'])==x['linkText'] and str(Path(x['path']).resolve())==x['resolved']
for x in refs['toolTrees']:tree(x)
m=read(refs['nativeMetadata']);assert len(m)==83 and len(m['sourceManifest'])==357 and len(m['componentizeSourceManifest'])==3 and len(m['selectedModuleManifests'])==12
assert m['engineSha256']==refs['nativeEngine']['sha256'] and m['nodeCryptoHashHmacEnabled'] is True and m['nodeCryptoAuditedBorrowEnabled'] is False and m['entropyPolicy']=='off' and m['gcStress'] is False and m['oomTesting'] is False
manifests=[]
for x in m['selectedModuleManifests']:
 p=Path(refs['configuredSourceRoot'])/x['path'];manifests.append(read(dict(path=str(p),sha256=x['sha256'],bytes=p.stat().st_size)))
assert manifests==a['producerAdmission']['selectedManifests']
assert a['originalParentExitCodes']==[1,1] and a['originalBuildAccepted'] is False
for x in list(observed.values()):checked(x)
for x in list(families.values()):family(x)
for x in refs['toolTrees']:tree(x)
print(json.dumps(dict(schemaVersion=1,dataAuthenticationPassed=True,sourceContractCompatible=not contract_findings,contractJoinFindings=contract_findings,sourceIndex=source_index_row,uniqueRegularFiles=len(observed),closedFamilies=len(families),**counters,metadataFields=83,nativeSourceFiles=357,embeddingSources=3,selectedManifests=12,actualActions=False,reviewerAuthorshipDisclosure='Reviewer authored comparator dependency, not diagnostic caller.'),indent=2))
