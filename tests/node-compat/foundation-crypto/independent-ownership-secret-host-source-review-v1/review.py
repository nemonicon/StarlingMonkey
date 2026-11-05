"""Independent Source/DATA audit only; no host/API/helper/guest action."""
from pathlib import Path
import ast,collections,copy,hashlib,importlib.util,json,os,re,stat,sys,time

OWN=Path(__file__).resolve().parent
SOURCE=OWN.parent/'ownership-secret-host-candidate-v1'
EXPECTED='851392e5cca472b6b6f51a92ebcee1dc27b65359b301093d3b04c742519c34c2'
captured={};identities={};families={};checks=0;pure=0
def need(v,label):
 global checks
 assert v,label
 checks+=1
def physical(p):return Path('/private'+p)if p.startswith('/tmp/')else Path(p)
def desc(p):
 p=Path(p);raw=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
def identity(s):return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,stat.S_IMODE(s.st_mode),s.st_nlink)
def verify(r):
 need(type(r)is dict and set(r)=={'path','sha256','bytes'},'exact descriptor')
 p=physical(r['path']);need(p.is_absolute()and str(p)==os.path.normpath(str(p)),'canonical absolute original')
 for q in(p,*p.parents):need(not q.is_symlink(),'no undeclared reference alias')
 a=p.stat();need(stat.S_ISREG(a.st_mode)and a.st_size==r['bytes'],'regular exact size')
 if r['path']in captured:
  need(captured[r['path']]==r and identities[r['path']]==identity(a),'consistent current repeated input');return p
 h=hashlib.sha256()
 with p.open('rb')as f:
  for block in iter(lambda:f.read(4194304),b''):h.update(block)
 need(identity(a)==identity(p.stat())and h.hexdigest()==r['sha256'],'stable full SHA '+str(p))
 captured[r['path']]=dict(r);identities[r['path']]=identity(a);return p
def data(r):return json.loads(verify(r).read_bytes())
def family(r):
 v=data(r);root=Path(r['path']).parent;names={'index.json'};rows=[r]
 need(v['schemaVersion']==1 and len(v['files'])<=2048,'bounded genuine family')
 for item in v['files']:
  name=item['path'];need(name not in names and not name.startswith('/')and '\\'not in name and all(p not in('','.','..')for p in name.split('/')),'unique confined member');names.add(name)
  row=dict(item,path=str(root/name));verify(row);rows.append(row)
 need(not any(p.is_symlink()for p in root.rglob('*'))and{p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names,'whole family membership')
 families[r['path']]=r;return rows
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
def main():
 global checks,pure
 start=time.monotonic();ix=desc(SOURCE/'index.json');need(ix['sha256']==EXPECTED and ix['bytes']==7070,'Root sealed Source tuple')
 source_rows=family(ix);need(len(source_rows)==45,'44 own indexed members')
 refs=data(next(r for r in source_rows if r['path']==str(SOURCE/'references.json')))
 inputs=data(next(r for r in source_rows if r['path']==str(SOURCE/'source-inputs.json')))
 # Inspect real literals by a genuine inert import, never AST namespace injection.
 spec=importlib.util.spec_from_file_location('independent_real_secret355_host_external',SOURCE/'external.py');external=importlib.util.module_from_spec(spec);spec.loader.exec_module(external)
 need(external.OWN==SOURCE==Path(external.__file__).resolve().parent,'actual OWN Python context')
 need(external.REPO==OWN.parents[3]and str(external.OUTPUT)==refs['outputRoot']and str(external.OUT)==refs['externalOutputRoot'],'real repository/output constants')
 need(not external.OUTPUT.exists()and not external.OUT.exists(),'no host phase outputs created')
 need(len(inputs['files'])==len({r['path']for r in inputs['files']})==len(inputs['modeRows'])==34403,'whole unique declared original protection')
 need(sum(r['bytes']for r in inputs['files'])==2691407402,'declared logical input bytes')
 for row in inputs['files']:verify(row)
 for row in inputs['families']:family(row)
 need(len(inputs['families'])==38,'38 inherited complete families')
 need({r['file']['path']:r['file']for r in inputs['modeRows']}=={r['path']:r for r in inputs['files']},'mode rows cover every declared descriptor')
 for row in inputs['modeRows']:need(stat.S_IMODE(verify(row['file']).stat().st_mode)==row['mode'],'current protected mode')
 for tree in inputs['historicalDonorTrees']:
  root=Path(tree['root']);need(not any(p.is_symlink()for p in root.rglob('*'))and{p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==set(tree['names']),'explicit historical donor exact tree')
 package=data(refs['packagingMap']);root=Path(package['publicationRoot']);s=root.lstat()
 need(package['state']=='EXACT_EXISTING_PACKAGING_PHYSICAL_ROLES_NOT_NATIVE_AUTHORITY'and package['originalZlibNativeFactsConsumed']is package['costActionStatesReused']is False,'package role DATA only')
 need(not root.is_symlink()and stat.S_IMODE(s.st_mode)==0o700 and(s.st_dev,s.st_ino)==(package['rootIdentity']['device'],package['rootIdentity']['inode']),'actual package root identity')
 expected={r['path']:r for r in package['files']};links={r['destination']:r for r in package['links']};seen=set();seenlinks=set()
 need(len(expected)==4934 and len(links)==22,'full physical package roles')
 for role in package['roleRoots']:
  role_root=root/role;need(role_root.is_dir()and not role_root.is_symlink(),'ordinary role root')
  for p in role_root.rglob('*'):
   n=p.relative_to(root).as_posix();s=p.lstat()
   if p.is_symlink():
    v=links[n];need(os.readlink(p)==v['newLinkText']and p.resolve()==root/v['mappedTarget'],'literal package alias');seenlinks.add(n)
   elif p.is_dir():need(stat.S_IMODE(s.st_mode)==0o700,'private package directory')
   else:
    v=expected[n];need(stat.S_ISREG(s.st_mode)and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==v['mode'],'package file mode/link count');verify(dict(path=str(p),sha256=v['sha256'],bytes=v['bytes']));seen.add(n)
 need(seen==set(expected)and seenlinks==set(links),'complete package file/link membership')
 actual=data(refs['actualRuntimeReview']['result']);contract=data(refs['actualRuntimeContract']);ar=data(refs['actualArtifactReview']['result']);ac=data(refs['actualArtifactContract'])
 need(refs['actualRuntimeReview']['result']in family(refs['actualRuntimeReview']['index'])and refs['actualRuntimeContract']in family(refs['actualRuntimeReview']['index']),'actual Jco pair/contract indexed')
 need(refs['actualArtifactReview']['result']in family(refs['actualArtifactReview']['index'])and refs['actualArtifactContract']in family(refs['actualArtifactReview']['index']),'actual construction pair/contract indexed')
 for group in('requiredFixedValues','requiredExactDescriptors'):
  for k,v in contract[group].items():need(actual[k]==v,'whole actual Jco contract '+k)
 need(actual['coverage']==contract['requiredCoverage']and actual['artifacts']==contract['artifacts']==refs['artifacts']==ar['artifacts']==ac['artifacts'],'whole proof coverage/artifact roles')
 exact=contract['requiredExactDescriptors'];jco=Path(exact['actualIndex']['path']).parent;actual_ix=data(exact['actualIndex']);names={'index.json','completion.json'}
 for r in actual_ix['files']:
  need(r['path']not in names,'unique actual Jco inventory');names.add(r['path']);verify(dict(r,path=str(jco/r['path'])))
 verify(exact['actualCompletion']);need(len(actual_ix['files'])==54 and len(names)==56,'actual Jco54indexed/56files')
 need(not any(p.is_symlink()for p in jco.rglob('*'))and{p.relative_to(jco).as_posix()for p in jco.rglob('*')if p.is_file()}==names,'whole exact actual Jco membership')
 wrapper=data(exact['rawWrapper']);oracle=data(exact['nodeOracle'])
 need(list(wrapper)==['schemaVersion','name','args','kind','observed']and wrapper['name']=='validate'and wrapper['args']==[]and wrapper['kind']=='return'and wrapper['observed']['type']=='string'and type(wrapper['observed']['value'])is str,'actual whole wrapper typed observed.value')
 need(len(json.loads(wrapper['observed']['value'])['records'])==4,'four actual guarded wrapper cases')
 meta=data(refs['metadata']);need(len(meta)==75 and len(meta['sourceManifest'])==355 and len(meta['componentizeSourceManifest'])==3 and len(meta['selectedModuleManifests'])==11,'original901 native context75/355/3/11')
 need(refs['artifacts']['component']['sha256']=='c067000d2612088ce430be124de0efeccd4ba12d287b858d9aca2a429c425f30'and refs['engine']['sha256']=='901c7ba55cf48d0dc2b74e6a8f75f41d215a95946aeb89afcf592d576b60a1a7','actual component/native binary roles')
 entry=(SOURCE/'entry.mjs').read_text();body=(SOURCE/'run.mjs').read_text();protocol=(SOURCE/'protocol.mjs').read_text()
 need("const ORIGINAL='"+str(SOURCE)+"'"in entry and 'HERE===ORIGINAL' in entry,'actual JS entry literal/current module context')
 need("monitor.monitor(argv,str(REPO),{**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},OUT,2400,root_row)"in(SOURCE/'external.py').read_text(),'genuine original six-argument monitor call')
 need('await mkdir(join(out.root,\'processes\'),{mode:0o700})'in body and body.index("await mkdir(join(out.root,'processes')")<body.index('await runOwnedCommand('),'real collector directory precondition')
 need(body.index('strictTerminal(terminal)')<body.index('parseScalarStringOutput(')<body.index("need(value===frame.jcoWrapper.observed.value"),'raw collector then strict WAVE then whole equality')
 need("return ['run','--invoke','validate()',r.path]"in protocol,'actual stock Wasmtime zero-argument scalar syntax')
 closure=data(next(r for r in source_rows if r['path']==str(SOURCE/'module-closure.json')))
 declared={r['path']:r for r in closure['modules']};edges=[]
 for path,row in declared.items():
  text=verify(row).read_text()
  for line in text.splitlines():
   if line.startswith(('import ','export '))and'from 'in line:
    m=re.search(r"from ['\"]([^'\"]+)['\"]",line);need(m is not None,'static module syntax known')
    specifier=m.group(1)
    if not specifier.startswith('node:'):
     target=str((Path(path).parent/specifier).resolve());need(target in declared,'every nonbuiltin static dependency declared');edges.append((path,specifier,target))
 need(len(declared)==10 and len(edges)==14 and len(closure['edges'])==15,'all10modules/14static+1dynamic edges')
 need("await import(pathToFileURL(join(HERE,'run.mjs')))"in entry,'only new authenticated dynamic body path')
 for edge in closure['edges']:
  if edge['kind']=='static':need((edge['caller'],edge['specifier'],edge['target'])in edges,'actual static edge tuple')
 need(closure['pythonCustomImport']['target']==refs['monitorEntry'],'actual monitored module context')
 deriv=data(next(r for r in source_rows if r['path']==str(SOURCE/'derivations.json')));edits=0
 for item in deriv['files']:
  before=verify(item['donor']).read_bytes();after=verify(item['after']).read_bytes();work=before
  for edit in reversed(item['edits']):
   a,b=edit['before'].encode(),edit['after'].encode();n=edit['beforeOffset'];need(work[n:n+len(a)]==a,'forward byte offset');work=work[:n]+b+work[n+len(a):];edits+=1
  need(work==after,'exact forward donor derivation')
  for edit in reversed(item['edits']):
   a,b=edit['before'].encode(),edit['after'].encode();n=edit['afterOffset'];need(work[n:n+len(b)]==b,'reverse byte offset');work=work[:n]+a+work[n+len(b):]
  need(work==before,'exact reverse donor derivation')
 need(len(deriv['files'])==6 and edits==435,'six donor files435 exact edits')
 # Genuine inert external module constants were checked first. These fixtures
 # exercise only its pure authority function and never become issued documents.
 future=json.loads((SOURCE/'future-root-authority.template.json').read_bytes());need(future['sourceIndex']is future['sourceIndependentReview']is future['entry']is None,'future action unissued')
 model={**future,'sourceIndex':ix,'entry':desc(SOURCE/'entry.mjs'),'externalController':desc(SOURCE/'external.py')};external.root_model(model,ix,refs);pure+=1
 for k,v in [('freshProcesses',2),('fullMetadataFields',80),('nativeSourceFiles',342),('guardedPrototypeCase3Allowed',False),('generatedJsAllowed',True),('retainedApiAllowed',True),('gcPressureAllowed',True),('actualRuntimeReview',None),('externalParentDeadlineSeconds',7200)]:
  try:external.root_model({**model,k:v},ix,refs)
  except(AssertionError,KeyError):pure+=1
  else:raise AssertionError('pure Python mutation accepted '+k)
 for p in SOURCE.glob('*.py'):ast.parse(p.read_text(),filename=str(p));checks+=1
 for key,row in captured.copy().items():need(identities[key]==identity(physical(key).stat()),'all captured input identity/mode/link stable at end')
 for row in list(families.values()):
  base=Path(row['path']).parent
  for r in [row]+[dict(v,path=str(base/v['path']))for v in json.loads((base/'index.json').read_bytes())['files']]:need(desc(Path(r['path']))==r,'complete family final fullhash')
  family(row)
 need(not external.OUTPUT.exists()and not external.OUT.exists(),'no output or host action')
 save('checks.json',dict(schemaVersion=1,passed=True,sourceIndex=ix,checks=checks,pythonPureCases=pure,actualOwnContextInertImported=True,namespaceOrFrameInjected=False,declaredInputCount=34403,declaredInputBytes=2691407402,uniqueReadHashInputs=len(captured),uniqueReadHashLogicalBytes=sum(r['bytes']for r in captured.values()),inheritedFamilies=38,allAuthenticatedFamilies=len(families),packagingFiles=4934,packagingAliases=22,actualJcoIndexedFiles=54,actualJcoActualFiles=56,historicalDonorTrees=len(inputs['historicalDonorTrees']),modules=10,staticEdges=14,dynamicEdges=1,reversibleFiles=6,reversibleEdits=435,allCapturedIdentitiesStableAtEnd=True,allFamiliesFullHashRecheckedAtEnd=True,allLargeInputBytesRehashedTwice=False,ownerActionsInvoked=False,hostActionsInvoked=False,runtimeActionsInvoked=False,elapsedReadHashSeconds=time.monotonic()-start))
 save('references.json',dict(schemaVersion=1,sourceIndex=ix,sourceInputs=desc(SOURCE/'source-inputs.json'),actualRuntimeReview=refs['actualRuntimeReview'],actualRuntimeContract=refs['actualRuntimeContract'],actualArtifactReview=refs['actualArtifactReview'],actualArtifactContract=refs['actualArtifactContract'],runtimeExactDescriptors=exact,component=refs['artifacts']['component'],engine=refs['engine'],metadata=refs['metadata'],node=refs['node'],wasmtime=refs['wasmtime'],python=refs['pythonExecutable'],sourceFamilies=list(families.values()),moduleClosure=desc(SOURCE/'module-closure.json')))
 print(json.dumps(dict(passed=True,checks=checks,purePythonCases=pure,uniqueInputs=len(captured))),flush=True)
if __name__=='__main__':
 assert sys.dont_write_bytecode
 try:main()
 except BaseException as error:
  save('reader-failure-'+str(time.time_ns())+'.json',dict(schemaVersion=1,name=type(error).__name__,message=str(error),checksCompleted=checks,ownerActionsInvoked=False));raise
