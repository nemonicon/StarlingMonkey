"""Authoring-only stdlib Source/data/AST check. Never calls the adapter/API.
Writes own check result; do not rerun after the family is sealed.
"""
from pathlib import Path
import ast,hashlib,json,os,stat
P=Path(__file__).resolve().parent;seen={};checks=0
def need(v,label):
 global checks
 checks+=1
 if not v:raise AssertionError(label)
def checked(r):
 p=Path(r['path']);a=p.lstat();need(stat.S_ISREG(a.st_mode),'ordinary input');h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 b=p.lstat();need((a.st_dev,a.st_ino,a.st_mode,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_mode,b.st_size,b.st_mtime_ns,b.st_ctime_ns),'stable current input');need(h.hexdigest()==r['sha256']and a.st_size==r['bytes'],'actual current fixed input');seen[str(p)]=r
def read(n):return json.loads((P/n).read_bytes())
def family(r):
 checked(r);p=Path(r['path']);v=json.loads(p.read_bytes());names={'index.json'}
 for x in v['files']:
  need(x['path']not in names,'unique family member');names.add(x['path']);checked(dict(x,path=str(p.parent/x['path'])))
 need(not any(q.is_symlink()for q in p.parent.rglob('*'))and names=={q.relative_to(p.parent).as_posix()for q in p.parent.rglob('*')if q.is_file()},'complete exact Source family')
refs=read('references.json');base=read('source-inputs.json');extra=read('artifact-inputs.json');need(not({r['path']for r in base['files']}&{r['path']for r in extra['files']}),'disjoint compact regular input tables')
for r in [*base['files'],*extra['files']]:checked(r)
for r in base['families']:family(r)
failure=json.loads(Path(refs['originalFailureReview']['result']['path']).read_bytes());contract=json.loads(Path(refs['originalFailureContract']['path']).read_bytes());need(failure['state']==contract['requiredReviewState']and failure['coverage']==contract['requiredCoverage'],'genuine whole failure contract')
for group in ['requiredFixedValues','requiredExactDescriptors']:
 for k,v in contract[group].items():need(failure[k]==v,'whole failure required value '+k)
need(refs['producerControllerIndex']==failure['controllerSourceIndex']and refs['engine']==failure['engine']and refs['metadata']==failure['metadata'],'original P3 and actual candidate identity')
ix=refs['indexException'];need(ix['originalExpected']['sha256']=='03f5eb17e6e77d6f864844d2be53e887055d58cd463b124bff1af876e01d17a3'and ix['currentActual']['sha256']=='bfbb4330c521a31a813a4a69af53d3858691db5ff58cddd5234815622d32d629','exact historical/current exception')
need(stat.S_IMODE(Path(ix['currentActual']['path']).stat().st_mode)==0o600 and ix['modeChanges']==[dict(path=ix['currentActual']['path'],expected=0o644,actual=0o600)],'exact mode exception')
for key in ['originalIndexPreimageRetained','indexStatOnlyDeltaProved','exactIndexWriterProved','oldResultOrSourceChanged']:need(ix[key]is False,'no historical repair claim')
need(next(r for r in base['files']if r['path']==ix['currentActual']['path'])==ix['currentActual'],'only current index is a live Source row')
trees=read('artifact-trees.json')['trees']
for tree in trees:
 root=Path(tree['root']);actual=[]
 for parent,dirs,files in os.walk(root,followlinks=False):
  for name in dirs+files:
   p=Path(parent)/name;actual.append(dict(path=p.relative_to(root).as_posix(),kind='symlink'if p.is_symlink()else'directory'if p.is_dir()else'file',mode=stat.S_IMODE(p.lstat().st_mode)))
 need(sorted(actual,key=lambda x:x['path'])==tree['entries'],'complete current tree/modes')
for r in read('reference-aliases.json')['symlinks']:need(os.readlink(r['path'])==r['linkText']and str(Path(r['path']).resolve(strict=True))==r['resolved'],'current alias')
for root in [refs['outputRoot'],refs['externalOutputRoot'],refs['freezeRoot']]:need(not Path(root).exists()and not Path(root).is_symlink(),'future roots absent')
asts={}
for p in P.glob('*.py'):asts[p.name]=ast.parse(p.read_text());checks+=1
entry=(P/'revalidate.py').read_text();need('controller.bootstrap'not in entry and 'setattr('not in entry and 'subprocess'not in entry,'no original bootstrap/rebinding/process API')
need("argument=dict(io=io,refs=producerRefs,ownIndex=refs['producerControllerIndex'])"in entry and 'admission.admit(argument,lambda unused:recheck(frame))'in entry,'genuine actual P3 callable/context')
need(entry.index("io.write(out/'producer-admission-return.json',wholeReturn)")<entry.index("frame['models'].result(result,refs)"),'whole returned DATA before caller assertions')
original=Path(refs['producerAdmission']['path']).read_text();admit=next(n for n in ast.parse(original).body if isinstance(n,ast.FunctionDef)and n.name=='admit');need([x.arg for x in admit.args.args]==['frame','recheck'],'actual P3 two-argument API')
need('ownIndex=refs[\'producerControllerIndex\']'in entry and "adapterSourceIndex=frame['adapterIndex']"in entry,'owner/adapter provenance split')
for name in ['nativeBuildAllowed','compilerAllowed','gitAllowed','engineExecutionAllowed','cryptoAllowed','freezeAllowed']:need(read('root-authority.template.json')[name]is False,'unissued false permission')
before=list(seen.values())
for r in before:checked(r)
result=dict(schemaVersion=1,state='SOURCE_CHECKS_ONLY_NO_ADAPTER_ACTION',passed=True,checks=checks,uniqueCurrentInputs=len(seen),currentLogicalBytes=sum(x['bytes']for x in seen.values()),directBaseRows=len(base['files']),artifactAdditionalRows=len(extra['files']),completeSourceFamilies=len(base['families']),completeCurrentTrees=len(trees),aliases=len(read('reference-aliases.json')['symlinks']),pythonAsts=len(asts),currentBeforeFinalHashesStable=True,originalP3ApiOrHelperImported=False,adapterBootstrapOrRunInvoked=False,actualRevalidationProof=None,engineExecuted=False,cryptoOperationsInvoked=False)
(P/'source-check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
