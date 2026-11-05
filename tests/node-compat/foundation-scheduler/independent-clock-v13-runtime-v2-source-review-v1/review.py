"""Finite V2 correction review; read/hash, real inert context, AST/DATA only."""
from pathlib import Path
import ast,hashlib,importlib.util,json,os,stat,sys,time
OWN=Path(__file__).resolve().parent
SOURCE=OWN.parent/'clock-v13-runtime-candidate-v2'
EXPECTED='135d1e45ea4214a99e2a835cfab0b212c92519ea6600a7c802336e7a323be384'
checked={};signatures={};families={};checks=0
def need(v,label):
 global checks
 assert v,label
 checks+=1
def physical(p):return Path('/private'+p)if p.startswith('/tmp/')else Path(p)
def signature(s):return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,stat.S_IMODE(s.st_mode),s.st_nlink)
def desc(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def verify(r):
 need(type(r)is dict and set(r)=={'path','sha256','bytes'},'descriptor shape')
 p=physical(r['path']);need(p.is_absolute()and str(p)==os.path.normpath(str(p)),'original canonical path')
 for q in(p,*p.parents):need(not q.is_symlink(),'no undeclared alias')
 s=p.stat();need(stat.S_ISREG(s.st_mode)and s.st_size==r['bytes'],'regular exact bytes')
 if r['path']in checked:
  need(checked[r['path']]==r and signatures[r['path']]==signature(s),'stable repeated input');return p
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 need(signature(s)==signature(p.stat())and h.hexdigest()==r['sha256'],'stable whole input SHA')
 checked[r['path']]=dict(r);signatures[r['path']]=signature(s);return p
def data(r):return json.loads(verify(r).read_bytes())
def family(r):
 v=data(r);root=Path(r['path']).parent;names={'index.json'};rows=[r]
 need(v['schemaVersion']==1 and 0<len(v['files'])<=2048,'genuine finite family')
 for item in v['files']:
  n=item['path'];need(n not in names and not n.startswith('/')and '\\'not in n and all(p not in('','.','..')for p in n.split('/')),'safe unique family member');names.add(n);row=dict(item,path=str(root/n));verify(row);rows.append(row)
 need(not any(p.is_symlink()for p in root.rglob('*'))and{p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names,'exact whole family membership')
 families[r['path']]=r;return rows
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
def main():
 global checks
 start=time.monotonic();ix=desc(SOURCE/'index.json');need(ix['sha256']==EXPECTED and ix['bytes']==6338,'Root Source pin')
 rows=family(ix);need(len(rows)==41,'40 own members')
 refs=data(next(r for r in rows if r['path']==str(SOURCE/'references.json')));inputs=data(next(r for r in rows if r['path']==str(SOURCE/'source-inputs.json')))
 # Actual module path first; do not fabricate module globals for pure tests.
 spec=importlib.util.spec_from_file_location('independent_actual_clock_v2_external',SOURCE/'external.py');external=importlib.util.module_from_spec(spec);spec.loader.exec_module(external)
 need(external.OWN==SOURCE==Path(external.__file__).resolve().parent and external.REPO==OWN.parents[3],'genuine inert external OWN/REPO')
 need(refs['originalRoot']==str(SOURCE),'actual V2 source context')
 need(len(inputs['files'])==len({r['path']for r in inputs['files']})==12079 and len(inputs['families'])==18,'full finite intake')
 for r in inputs['files']:verify(r)
 for r in inputs['families']:family(r)
 need(sum(r['bytes']for r in inputs['files'])==1374542216,'declared logical bytes')
 old_rows=family(refs['previousSourceIndex']);held_rows=family(refs['previousSourceHold']['index'])
 need(refs['previousSourceHold']['result']in held_rows and refs['requiredCorrectionContract']in held_rows,'indexed old HOLD/correction')
 held=data(refs['previousSourceHold']['result']);correction=data(refs['requiredCorrectionContract'])
 need(held['sourceReviewPassed']is False and held['state']=='INDEPENDENT_CLOCK_V13_REACTDOM_RUNTIME_SOURCE_REVIEW_HELD_V1'and held['sourceIndex']==correction['heldSourceIndex']==refs['previousSourceIndex'],'no old HOLD promotion')
 old_root=Path(refs['previousSourceIndex']['path']).parent;old_refs=json.loads((old_root/'references.json').read_bytes());old_inputs=json.loads((old_root/'source-inputs.json').read_bytes())
 current={r['path']:r for r in inputs['files']}
 need(len(old_inputs['files'])==11995 and all(current[r['path']]==r for r in old_inputs['files']),'all11995 inherited original rows unchanged')
 need(all(current[r['path']]==r for r in old_rows+held_rows),'complete old Source/HOLD members in new preimport intake')
 preserved=('artifacts','generatedFiles','component','nativeEngine','nativeMetadata','guest','bundle','oracleValue','oracleEvidence','mappingOptions','inlineCoreModules','selectedInterfaces','node','nativePreflight','nativePins','nativeSourceRoot','nativeEmbeddingSourceRoot','requiredNativeReadOnlyEnvironment','loaderPackageRoot','jcoApi','shimClocksUrl','shimIoUrl','monitorIndex','monitorEntry','wasmtime')
 for key in preserved:need(refs[key]==old_refs[key],'unchanged actual role '+key)
 for key in('mappedOutputRoot','runtimeOutputRoot'):
  need(refs[key].endswith('-v2')and refs[key]!=old_refs[key]and not Path(refs[key]).exists()and not Path(refs[key]+'-external-root').exists(),'fresh inactive V2 phase namespace')
 pkg=data(refs['packageInventory'])['package'];root=Path(pkg['root']);need(str(root)==refs['loaderPackageRoot']and not root.is_symlink()and stat.S_IMODE(root.stat().st_mode)==0o700,'real private package root')
 files={r['relativePath']:r for r in pkg['files']};links={r['path']:r for r in pkg['links']};need(len(files)==4889 and len(links)==21,'unchanged complete package roles');actual=set()
 for p in root.rglob('*'):
  n=p.relative_to(root).as_posix();s=p.lstat()
  if p.is_symlink():
   l=links[n];need(os.readlink(p)==l['target']and str(p.resolve())==l['resolvedPath']and p.resolve().is_relative_to(root),'literal selected package alias');actual.add(n)
  elif p.is_dir():need(stat.S_IMODE(s.st_mode)==0o700,'private package directory')
  else:
   r=files[n];need(s.st_nlink==1 and stat.S_IMODE(s.st_mode)==r['mode'],'package ordinary file mode/link');verify({k:r[k]for k in('path','sha256','bytes')});actual.add(n)
 need(actual==set(files)|set(links),'whole package membership')
 proof_rows=family(refs['actualArtifactReview']['index']);need(refs['actualArtifactReview']['result']in proof_rows and refs['actualArtifactContract']in proof_rows,'actual component proof pair/contract')
 proof=data(refs['actualArtifactReview']['result']);contract=data(refs['actualArtifactContract'])
 need(proof['artifacts']==contract['artifacts']==refs['artifacts']and len(refs['artifacts'])==14 and proof['generatedFiles']==contract['generatedFiles']==refs['generatedFiles']and len(refs['generatedFiles'])==7,'whole immutable original artifact/generated maps')
 meta=data(refs['nativeMetadata']);need(len(meta)==64 and len(meta['sourceManifest'])==342 and len(meta['componentizeSourceManifest'])==3 and len(meta['selectedModuleManifests'])==9,'genuine accepted342/3/64/9 not355')
 for r in refs['artifacts'].values():verify(r)
 need(len(refs['inlineCoreModules'])==3 and refs['generatedFiles']['clock_v13.core.wasm']['bytes']==15687023,'physical main plus three inline core identities')
 command=refs['oracleEvidence']['command'];oracle=data(command['stdout']);need(oracle['status']=='passed'and oracle['value']==refs['oracleValue'],'actual complete retained Node oracle')
 need(command in data(refs['oracleEvidence']['report'])['commands']and json.loads(refs['oracleValue'])['bytes']==45,'exact original report and full45 HTML bytes')
 entry=(SOURCE/'entry.mjs').read_text();body=(SOURCE/'body.mjs').read_text();external_text=(SOURCE/'external.py').read_text()
 need("const ORIGINAL='"+str(SOURCE)+"'"in entry and 'HERE===ORIGINAL'in entry,'actual JS main/own context')
 need(body.count('catch(error){primaryPresent=true;primary=error;}')==body.count('if(primaryPresent||finalErrors.length)')==body.count('primaryPresent,primary:observed(primary)')==3,'all three body presence branches/records')
 need(entry.count('primaryPresent=true;primary=error;throw error;')==entry.count('if(primaryPresent)throw new AggregateError')==2,'both entry combined-failure branches')
 need('primary!==null'not in entry+body,'old ambiguous sentinel absent')
 need("const held=await c.proof(refs.previousSourceHold)"in entry and entry.index('for(const r of inputs.files)await c.file(r)')<entry.index('await import(pathToFileURL(f.refs.nativePreflight.path))'),'complete inherited Source auth before genuine native API import')
 need("monitor.monitor(argv,str(REPO),env,out,1200,root_row)"in external_text and "OWN=REPO/'tests/node-compat/foundation-scheduler/clock-v13-runtime-candidate-v2'"in external_text,'genuine external context/six-argument original monitor API')
 need("for k in ['HOME','home','CODEX_HOME']:assert env.get(k)==os.environ.get(k)"in external_text,'home variables preserved')
 need("scenario==='retained'?3:1"in body and "for(let n=0;n<3;n++)"in body and "['run','--invoke','run()',f.refs.component.path]"in body,'unchanged retained3/fresh1 and freshWT3 schedule')
 deriv=data(next(r for r in rows if r['path']==str(SOURCE/'derivations.json')));edits=0
 for item in deriv['files']:
  before=verify(item['donor']).read_text();after=verify(item['after']).read_text();work=before
  for edit in item['edits']:
   need(work.count(edit['before'])==edit['occurrences'],'exact forward occurrences');work=work.replace(edit['before'],edit['after']);edits+=1
  need(work==after,'exact full forward successor')
  for edit in reversed(item['edits']):need(work.count(edit['after'])==edit['occurrences'],'exact reverse occurrences');work=work.replace(edit['after'],edit['before'])
  need(work==before,'exact full reverse donor')
 need(len(deriv['files'])==6 and edits==27,'six files27 exact substitutions')
 for p in SOURCE.glob('*.py'):ast.parse(p.read_text(),filename=str(p));checks+=1
 future=json.loads((SOURCE/'future-root-authority.template.json').read_bytes());cfg=json.loads((SOURCE/'future-config.template.json').read_bytes());mapped=json.loads((SOURCE/'future-mapped-output-review.template.json').read_bytes())
 need(future['phase']is future['sourceIndex']is future['entry']is future['sourceIndependentReview']is future['outputRoot']is future['actualMappedOutputReview']is None and cfg['sourceIndex']is cfg['rootAuthority']is None and mapped['mappingResult']is mapped['index']is mapped['mappingRootAuthority']is None,'new operational slots unissued')
 for key,r in checked.copy().items():need(signatures[key]==signature(physical(key).stat()),'complete input physical stability')
 for ixrow in list(families.values()):
  base=Path(ixrow['path']).parent
  for r in [ixrow]+[dict(v,path=str(base/v['path']))for v in json.loads((base/'index.json').read_bytes())['files']]:need(desc(Path(r['path']))==r,'final complete family fullhash')
  family(ixrow)
 save('checks.json',dict(schemaVersion=1,passed=True,checks=checks,sourceIndex=ix,declaredInputs=12079,declaredInputBytes=1374542216,inheritedOriginalRowsUnchanged=11995,inheritedFamilies=18,allAuthenticatedFamilies=len(families),ownSourceMembers=40,uniqueReadHashInputs=len(checked),uniqueReadHashLogicalBytes=sum(r['bytes']for r in checked.values()),packageFiles=4889,packageAliases=21,actualOwnContextInertImported=True,namespaceInjected=False,threeBodyPresenceBranches=True,twoEntryCombinedPresenceBranches=True,threeTruthfulFailurePresenceFields=True,derivedFiles=6,reversibleEdits=27,preservedArtifactRows=14,preservedGeneratedRows=7,allFourCoreIdentitiesUnchanged=True,fullNativeMetadataFields=64,nativeSources=342,externalSources=3,wholeManifests=9,allFamilyBytesRehashedAtEnd=True,allInputIdentitiesStableAtEnd=True,allLargeOriginalBytesRehashedTwice=False,ownerActionsInvoked=False,hostActionsInvoked=False,runtimeActionsInvoked=False,elapsedReadHashSeconds=time.monotonic()-start))
 save('references.json',dict(schemaVersion=1,sourceIndex=ix,previousSourceIndex=refs['previousSourceIndex'],previousSourceHold=refs['previousSourceHold'],requiredCorrectionContract=refs['requiredCorrectionContract'],sourceInputs=desc(SOURCE/'source-inputs.json'),actualArtifactReview=refs['actualArtifactReview'],actualArtifactContract=refs['actualArtifactContract'],component=refs['component'],nativeEngine=refs['nativeEngine'],nativeMetadata=refs['nativeMetadata'],node=refs['node'],parser=refs['parser'],oracleEvidence=refs['oracleEvidence'],oracleValue=refs['oracleValue'],mappingOptions=refs['mappingOptions'],mappedOutputRoot=refs['mappedOutputRoot'],runtimeOutputRoot=refs['runtimeOutputRoot'],sourceFamilies=list(families.values())))
 print(json.dumps(dict(passed=True,checks=checks,declaredInputs=12079,actions=False)),flush=True)
if __name__=='__main__':
 assert sys.dont_write_bytecode
 try:main()
 except BaseException as error:save('reader-failure-'+str(time.time_ns())+'.json',dict(schemaVersion=1,name=type(error).__name__,message=str(error),checksCompleted=checks,ownerActionsInvoked=False));raise
