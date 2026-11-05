"""Read/hash/static/pure extracted validator review. No owner module imports."""
from pathlib import Path
import ast,copy,hashlib,json
P=Path(__file__).resolve().parent;S=P.parent/'ownership-gc-build-controller-candidate-v1'
checks=0;seen={}
def need(v,m):
 global checks
 if not v:raise AssertionError(m)
 checks+=1
def row(p):
 p=Path(p);h=hashlib.sha256();n=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b);n+=len(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=n)
def verify(r):
 p=Path(r['path']);a=p.stat();need(p.is_file()and not p.is_symlink(),'ordinary input');v=row(p);b=p.stat();need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns),'stable full bytes');need(v==r,'exact descriptor '+str(p));seen[str(p)]=v;return r
def data(r):verify(r);return json.loads(Path(r['path']).read_bytes())
def family(r,count=None):
 x=data(r)
 if count is not None:need(len(x['files'])==count,'exact family count')
 names=set();rs=[]
 for e in x['files']:
  n=e['path'];need(n and not n.startswith('/')and all(q not in ('','.','..')for q in n.split('/'))and n not in names,'safe unique family member');names.add(n);v=dict(path=str(Path(r['path']).parent/n),sha256=e['sha256'],bytes=e['bytes']);verify(v);rs.append(v)
 need({str(p.relative_to(Path(r['path']).parent))for p in Path(r['path']).parent.rglob('*')if p.is_file()}==names|{'index.json'},'whole exact family membership');return rs
src=dict(path=str(S/'index.json'),sha256='0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b',bytes=3391)
rs=family(src,20);by={str(Path(r['path']).relative_to(S)):r for r in rs};inputs=data(by['source-inputs.json']);need(len(inputs['files'])==79,'source79 input rows')
for r in inputs['files']:verify(r)
refs=data(by['references.json']);need(len(refs['families'])==6,'full six inherited families')
for r in refs['families']:family(r['index'])
for r in refs['files']:verify(r)
need(refs['nativeSourceReview']['index']['sha256']=='1cc950ddf49925b7b454e8c464cfe3dea1fdfdd9acf6c0d4d66ac58462824e3a'and refs['actualStageReview']['index']['sha256']=='dbf58c99982a8d7d70985046def8111d26c05681b98aeb3fe2fbbcfbcac1121a','exact native-source and actual stage peers')
deriv=data(by['monitor-derivation.json']);verify(deriv['source']);old=Path(deriv['source']['path']).read_text();new=(S/'monitor.py').read_text();need(len(deriv['edits'])==1,'only one monitor edit');e=deriv['edits'][0]
need(old.count(e['before'])==e['count']==1 and old.replace(e['before'],e['after'])==new and new.replace(e['after'],e['before'])==old,'exact full monitor forward/reverse bytes')
need(e['before']=='assert 0 < timeout_seconds <= 2400 and 0 < parent_grace_seconds <= 45'and e['after']=='assert 0 < timeout_seconds <= 7200 and 0 < parent_grace_seconds <= 45','only actual API ceiling2400 to7200')
source=(S/'controller.py').read_text();tree=ast.parse(source);monitor_tree=ast.parse(new)
main=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main');body=ast.get_source_segment(source,main)
need(body.index('authorize(config_row)')<body.index('spec.loader.exec_module(module)')<body.index('module.monitor('),'authentication before custom import before monitor call')
need("assert sys.dont_write_bytecode"in body and "environment = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}"in body,'no sealed-source bytecode mutation; environment preserved')
need("argv = [sys.executable, str(NATIVE / 'build.py'), json.dumps(config_row, separators=(',', ':'))]"in body and "terminal = module.monitor(argv, str(REPO), environment, OUT, 7200, config['rootAuthority'])"in body,'genuine native build-only entry/config and actual API')
need('finally:\n        # Source/proof drift' in body and body.index('finally:')<body.index("assert terminal['rawExitCode']"),'failure/success source audit before acceptance')
need("remainingObservedPids"in body and "not terminal['forcedCleanup']"in body and "not terminal['errors']"in body,'clean corrected monitor result required')
need("terminal = monitor(argv, str(REPO), environment, output, 2400,"in new and "if __name__ == '__main__':"in new,'inherited HTTPmain2400 remains dormant')
authorize=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='authorize');auth=ast.get_source_segment(source,authorize)
for token in ["own_rows = family(own_index)","native_rows = family(config['sourceIndex'])","for item in refs['families']:","validate_stage(root,", "validate_peer(read(peer['result']), own_index)","recheck(captured, family_indices)"]:
 need(token in auth,'complete before-import auth path '+token)
need("for row in family_indices:\n        family(row)"in source,'complete family membership rechecked, not only listed bytes')
# Compile only actual pure root/stage/peer validators plus constant assignments.
selected=[n for n in tree.body if isinstance(n,ast.Assign)]+[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in ('validate_build_root','validate_stage','validate_peer')]
ns={'Path':Path};exec(compile(ast.Module(body=selected,type_ignores=[]),'<actual-validator-pure-only>','exec'),ns)
pure=[]
def good(name,call):call();pure.append(dict(case=name,acceptedAsDataOnly=True))
def bad(name,call):
 try:call()
 except (AssertionError,KeyError,TypeError):pure.append(dict(case=name,rejected=True));return
 raise AssertionError('unsafe pure data accepted '+name)
stage=data(refs['actualStageResult']);peer=data(refs['actualStageReview']['result']);obs=data(refs['actualStageRootObservation']);terminal=data(obs['externalParentTerminal']);rootstage=dict(actualStageResult=refs['actualStageResult'],actualStageRootObservation=refs['actualStageRootObservation'])
good('exact genuine source-stage proof DATA',lambda:ns['validate_stage'](rootstage,stage,peer,obs,terminal))
for k,v in [('state','wrong'),('verifiedPassed',False),('sourceIndexSha256','0'*64),('configuredSourceRoot','/private/tmp/wrong'),('actualStageResult',None),('rootResult',None),('externalParentTerminal',None)]:
 b=copy.deepcopy(peer);b[k]=v;bad('stagepeer '+k,lambda b=b:ns['validate_stage'](rootstage,stage,b,obs,terminal))
for k,v in [('rawExitCode',1),('parentOwnedGroupGone',False),('allObservedOwnedGroupsGone',False),('remainingObservedPids',[7]),('forcedCleanup',True),('timeout',True),('errors',[{}]),('interruptedSignals',[15]),('authority',None)]:
 b=copy.deepcopy(terminal);b[k]=v;bad('stage terminal '+k,lambda b=b:ns['validate_stage'](rootstage,stage,peer,obs,b))
b=copy.deepcopy(stage);b['destination']='/private/tmp/starling-node-compat/crypto-owner355-gc-v1-source';bad('historical v1 destination cannot be actual stage',lambda:ns['validate_stage'](rootstage,b,peer,obs,terminal))
root=data(by['future-root-authority.template.json']);own=src
bad('unissued Root build template',lambda:ns['validate_build_root'](root,own))
root.update(state='ROOT_REVIEWED_CRYPTO_OWNER355_ISOLATED_GC_NATIVE_PHASE_V1',phase='build',sourceIndexSha256=ns['NATIVE_SHA'],buildAllowed=True,externalControllerEntry=dict(path=str(S/'controller.py')),externalControllerIndex=own)
good('synthetic exact build Root shape only',lambda:ns['validate_build_root'](root,own))
for k,v in [('phase','stage'),('variant','normal-off'),('sourceIndexSha256','0'*64),('buildAllowed',False),('externalParentDeadlineSeconds',2400),('externalParentDeadlineSeconds',7201),('configuredSourceRoot','/private/tmp/wrong'),('workRoot','/private/tmp/reused'),('freezeRoot','/private/tmp/reused'),('nativeSourceFiles',350),('engine',{}),('actualBuildResult',{}),('reviewedGcPins',{})]:
 b=copy.deepcopy(root);b[k]=v;bad('Root '+k,lambda b=b:ns['validate_build_root'](b,own))
for flag in ['stageAllowed','freezeAllowed','exportAllowed','bootstrapAllowed','guestAllowed','keyOperationsAllowed','prototypeWorkloadsAllowed','componentAllowed','nativeSourceChangesAllowed','normalMutationAllowed','metadataProjectionAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed']:
 b=copy.deepcopy(root);b[flag]=True;bad('non-build '+flag,lambda b=b:ns['validate_build_root'](b,own))
cp=data(by['future-controller-review.template.json']);bad('unissued controller peer',lambda:ns['validate_peer'](cp,own));cp.update(state='INDEPENDENT_CRYPTO_OWNER355_GC_BUILD_CONTROLLER_SOURCE_REVIEW_PASSED_V1',controllerSourceIndexSha256=own['sha256'],sourceReviewPassed=True)
good('synthetic exact controller-peer shape only',lambda:ns['validate_peer'](cp,own))
for k,v in [('controllerSourceIndexSha256','0'*64),('nativeSourceIndexSha256','0'*64),('sourceOnly',False),('sourceReviewPassed',False),('ownerActionsInvoked',True),('hostActionsInvoked',True),('nativeBuildActionsInvoked',True)]:
 b=copy.deepcopy(cp);b[k]=v;bad('controller-peer '+k,lambda b=b:ns['validate_peer'](b,own))
for label,text,limit in [('old',old,2400),('new',new,7200)]:
 fn=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name=='monitor');assertion=next(n for n in fn.body if isinstance(n,ast.Assert));code=compile(ast.Module(body=[assertion],type_ignores=[]),'<deadline-assert-only>','exec')
 good(label+' deadline maximum',lambda code=code,limit=limit:exec(code,dict(timeout_seconds=limit,parent_grace_seconds=45)))
 bad(label+' deadline over maximum',lambda code=code,limit=limit:exec(code,dict(timeout_seconds=limit+1,parent_grace_seconds=45)))
 bad(label+' unknown grace',lambda code=code:exec(code,dict(timeout_seconds=1,parent_grace_seconds=46)))
need(len([n for n in monitor_tree.body if isinstance(n,(ast.Import,ast.ImportFrom))])>0,'complete standalone monitor module retained')
py=[p for p in S.glob('*.py')]
for p in py:ast.parse(p.read_text())
for r in seen.values():verify(r)
def save(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
save('pure-data-review.json',dict(schemaVersion=1,pureCases=len(pure),cases=pure,onlyActualPureValidatorAndAssertAstExecuted=True,noOwnerModuleImported=True,noMonitorOrMainOrProcessExecuted=True))
save('rehashed-inputs.json',dict(schemaVersion=1,files=list(seen.values()),readHashOnly=True))
save('data-results.json',dict(schemaVersion=1,sourceIndex=src,sourceDataReviewPassed=True,sourceMembers=20,sourceInputRows=79,sourceFamilies=6,distinctInputsRehashed=len(seen),checks=checks,monitorExactEdits=1,oldMonitorApiMaximum=2400,newMonitorApiMaximum=7200,httpSpecificMainStill2400AndNotCalled=True,publicMonitorApiUnchanged=True,authBeforeCustomImportVerified=True,fullFamilyMembershipRechecksVerified=True,actualStageProofBoundAsData=refs['actualStageReview'],actualStageJournal=refs['actualStageResult'],nativeSourceIndexSha256=ns['NATIVE_SHA'],actualConfiguredSourceRoot=ns['SOURCE'],workRoot=ns['WORK'],pureCases=len(pure),pythonAstModules=len(py),storedOwnerEvidenceAuthenticatedOnly=dict(sourceData=899,pure=77,pythonAst=7),ownerActionsInvoked=False,hostActionsInvoked=False,nativeBuildActionsInvoked=False,newRootOrBuildAuthorityIssued=False))
print(json.dumps(dict(sourceDataReviewPassed=True,sourceMembers=20,inputRows=79,pureCases=len(pure),distinctInputs=len(seen),checks=checks)))
