"""Independent actual bootstrap DATA read/hash/JSON only; never rerun an API."""
from pathlib import Path
import hashlib,json,stat
HERE=Path(__file__).resolve().parent;K=HERE.parent
SOURCE=K/'ownership-secret-artifact-bootstrap-v3-root-controller-candidate-v1'
BASE=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-artifact-tooling-v3')
OUT=Path(str(BASE)+'-bootstrap-root-observer')
rows={};identities={};trees=[];checks=[]
def need(v,n):assert v,n;checks.append(n)
def write(n,v):
    with(HERE/n).open('x')as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
def actual(p):
    p=Path(p);a=p.stat();assert p.is_file()and not p.is_symlink();h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    z=p.stat();ident=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,str(p.resolve()))
    assert ident(a)==ident(z);return dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size),ident(z)
def checked(d):
    d={k:d[k]for k in ['path','sha256','bytes']}
    if d['path']in rows:assert rows[d['path']]==d
    else:a,i=actual(d['path']);assert a==d;rows[d['path']]=d;identities[d['path']]=i
    return d
def current(p):d,_=actual(p);return checked(d)
def read(d):checked(d);return json.loads(Path(d['path']).read_bytes())
def tree(base,names,private=False):
    base=Path(base);assert base.is_dir()and not base.is_symlink();found=set()
    if private:assert stat.S_IMODE(base.stat().st_mode)==0o700
    for p in base.rglob('*'):
        assert not p.is_symlink()
        if p.is_dir():
            if private:assert stat.S_IMODE(p.stat().st_mode)==0o700
        else:
            assert p.is_file();found.add(p.relative_to(base).as_posix())
            if private:assert stat.S_IMODE(p.stat().st_mode)==0o600 and p.stat().st_nlink==1
    assert found==set(names);trees.append((base,set(names),private))
def family(ix):
    v=read(ix);base=Path(ix['path']).parent;names={'index.json'}
    for m in v['files']:
        n=m['path'];assert n not in names and not n.startswith('/')and all(x not in ['','.','..']for x in n.split('/'))
        names.add(n);checked(dict(m,path=str(base/n)))
    tree(base,names);return v
def strict(a,b):
    if type(a)is not type(b):return False
    if type(a)is dict:return set(a)==set(b)and all(strict(a[k],b[k])for k in a)
    if type(a)is list:return len(a)==len(b)and all(strict(x,y)for x,y in zip(a,b))
    return a==b
root_row=current(OUT/'root-observation.json');need(root_row['sha256']=='7a620cb72ca55d9ae23cf18db29a81ae2866ea1a5650ed8b4fb3c40f0e246fb4'and root_row['bytes']==4536,'exact actual Root bootstrap observation')
root=read(root_row);family(root['controllerIndex']);need(root['controllerIndex']['sha256']=='d99d5447167cda836c7c62654d6120ed6fbabd0ab951f7b7e9b3a6cbbbea4ce1','original d99 source')
refs=read(current(SOURCE/'references.json'));inputs=read(current(SOURCE/'source-inputs.json'))
need(len(inputs['files'])==27976 and len(inputs['families'])==14,'complete declared27976/14 family closure')
for d in inputs['files']:checked(d)
for d in inputs['families']:family(d)
tr=read(refs['toolingReferences']);family(refs['toolingIndex']);family(refs['toolingSourceReview']['index']);family(refs['exportReview']['index'])
source_authority=read(root['rootAuthority']);config=read(root['config'])
family(source_authority['sourceIndependentReview']['index']);sp=read(source_authority['sourceIndependentReview']['result'])
need(sp['state']=='INDEPENDENT_CRYPTO_OWNER355_SECRET_BOOTSTRAP_ROOT_CONTROLLER_SOURCE_REVIEW_PASSED_V1'and sp['controllerSourceIndexSha256']==root['controllerIndex']['sha256']and sp['sourceReviewPassed']is True,'genuine34839 source peer')
need(source_authority['sourceIndependentReview']['index']['sha256']=='34839c01425dbd1dc418ed7e6673a9a9ca9d9511adb225d9ee01b22c4ea7e059','exact source review index')
need(config==dict(schemaVersion=1,state='SECRET355_BOOTSTRAP_ROOT_CONTROLLER_CONFIG_V1',phase='bootstrap-js',controllerIndex=root['controllerIndex'],rootAuthority=root['rootAuthority']),'actual narrow JS config')
need(source_authority['state']=='ROOT_REVIEWED_SECRET355_BOOTSTRAP_CONTROLLER_PHASE_V1'and source_authority['phase']=='bootstrap-js'and source_authority['bootstrapJsAllowed']is True and source_authority['pinDerivationAllowed']is False,'separate issued JS authority')
for k in ['nativeBuildAllowed','nativeFreezeAllowed','gcReconfigureAllowed','ninjaAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','componentAllowed','runtimeAcceptanceClaim','operationalAdmission','sourcePromotionAllowed','metadataProjectionAllowed','timingAllowed','moduleAdmissionAllowed']:need(source_authority[k]is False,'no JS authority '+k)
for d in [refs['toolingInputs'],tr['protectedInputLedger'],refs['exportInputLedger']]:
    for r in read(d)['files']:checked(r)

derive_review_row=current(K/'ownership-secret-artifact-bootstrap-v3-derived-pins-root-review.json');derive_review=read(derive_review_row)
derive_obs=read(derive_review['actualObservation']);pins_row=derive_review['reviewedPins'];pins=read(pins_row);pin_review_row=derive_review['rootPinReview'];pin_review=read(pin_review_row)
candidate=read(refs['exportCandidate']);deltas=[]
def diff(a,b,path=()):
    if type(a)is dict and type(b)is dict:
        assert set(a)==set(b)
        for k in a:diff(a[k],b[k],path+(k,))
    elif type(a)is list and type(b)is list:
        assert len(a)==len(b)
        for i in range(len(a)):diff(a[i],b[i],path+(i,))
    elif type(a)is not type(b)or a!=b:deltas.append(dict(path=list(path),before=a,after=b))
diff(candidate,pins)
expected=[dict(path=['state'],before='UNREVIEWED_SECRET_OWNER355_NORMAL_OFF_PIN_CANDIDATE_V3',after='ROOT_REVIEWED_SECRET_OWNER355_NORMAL_OFF_VALIDATION_PINS_V3'),dict(path=['reviewRequired'],before=True,after=False),dict(path=['variants','normal-off','state'],before='unreviewed-secret-owner355-normal-off-pin-v3',after='reviewed-secret-owner355-normal-off-pin-v3'),dict(path=['variants','normal-off','reviewRequired'],before=True,after=False)]
need(strict(deltas,expected)and strict(derive_review['exactChanges'],expected),'whole recursive typed derivation exactly4changes')
need(set(pins['variants'])=={'normal-off','normal-runtime','gc-off','disabled-off'}and all(pins['variants'][k]is None for k in ['normal-runtime','gc-off','disabled-off']),'other three actual variants NULL')
derive_cfg=read(derive_obs['config']);derive_authority=read(derive_obs['rootAuthority'])
need(derive_cfg['phase']=='derive-pins'and derive_cfg['controllerIndex']==root['controllerIndex']and derive_cfg['rootAuthority']==derive_obs['rootAuthority'],'separate actual derive config')
need(derive_authority['phase']=='derive-pins'and derive_authority['pinDerivationAllowed']is True and derive_authority['bootstrapJsAllowed']is False and derive_authority['sourceIndependentReview']==source_authority['sourceIndependentReview'],'separate actual derive permission')
need(derive_review['rawDeriveExit']==0 and derive_obs['state']=='ROOT_DERIVED_SECRET355_VALIDATION_PIN_DATA_UNREVIEWED_V1','Root-reported derive0 plus exact actual observation')
need(derive_obs['reviewedPins']==pins_row and derive_obs['rootPinReview']==pin_review_row,'actual derived output tuples')
expected_review=read(refs['pinReviewTemplate']);expected_review.update(state='ROOT_SECRET_OWNER355_NORMAL_OFF_VALIDATION_PIN_REVIEW_V3',toolingIndex=refs['toolingIndex'],reviewedPins=pins_row,actualExportCandidate=refs['exportCandidate'],independentExportReview=refs['exportReview'])
need(strict(pin_review,expected_review),'all schema3 Root pin-review fields unchanged except documented bindings')
for n,d in [('reviewed-validation-pins.json',pins_row),('root-pin-review.json',pin_review_row),('derivation-observation.json',derive_review['actualObservation'])]:
    copied=current(K/'ownership-secret-artifact-bootstrap-v3-derived-pins-data-v1'/n);need(copied['sha256']==d['sha256']and copied['bytes']==d['bytes'],'Root repo DATA copy exact '+n)
tree(refs['pinOutputRoot'],['reviewed-validation-pins.json','root-pin-review.json','derivation-observation.json'],True)

js_observation=read(current(OUT/'js-observation.json'));need(strict(root['observer'],js_observation),'whole nested and retained observer values equal')
need(js_observation['apiCalls']==js_observation['returnedRecheckCalls']==1 and js_observation['error']is js_observation['protectionError']is None,'one observed API and returned recheck success')
api_cfg_row=source_authority['toolingBootstrapConfig'];api_authority_row=source_authority['toolingBootstrapAuthority'];api_cfg=read(api_cfg_row);api_authority=read(api_authority_row)
need(api_cfg==dict(schemaVersion=3,state='SECRET_OWNER355_ARTIFACT_TOOLING_CONFIG_V3',phase='bootstrap',toolingIndex=refs['toolingIndex'],rootAuthority=api_authority_row),'original d62 bootstrap config actual')
need(api_authority['bootstrapAllowed']is True and api_authority['exportAllowed']is False and api_authority['reviewedPins']==pins_row and api_authority['rootPinReview']==pin_review_row,'original API bootstrap-only authority pin tuples')
for k in ['nativeSourceIndex','verifierSourceIndex','actualVerifierReview','actualArtifactReview','engine','metadata','freezeReceipt','configuredSourceRoot','frozenSourceRoot','frozenRoot']:need(api_authority[k]==tr[k],'original source/metadata role '+k)
public_row=js_observation['wholePublicData'];frame_row=js_observation['retainedPythonFrame'];public=read(public_row);frame=read(frame_row)
need(strict(public,frame)and public_row['sha256']==frame_row['sha256']and public_row['bytes']==frame_row['bytes']==2030522,'whole41field public DATA byte-equal full Python frame')
need(Path(public_row['path']).stat().st_ino!=Path(frame_row['path']).stat().st_ino,'independent public/Python output files')
whole=read(current(Path(refs['bootstrapOutputRoot'])/'whole-verifier-frame.json'));historical=read(tr['actualVerifierWholeFrame'])
need(strict(whole,historical)and strict(frame['verifierFrame'],whole)and strict(frame['pin'],pins['variants']['normal-off']),'whole genuine verifier/pin data unchanged')
metadata=read(tr['metadata']);need(len(metadata)==75 and strict(frame['metadata'],metadata)and strict(whole['metadata'],metadata),'all75 metadata fields and types unchanged')
need(len(frame['selectedManifests'])==11 and strict(frame['selectedManifests'],whole['selectedManifests'])and strict(frame['selectedManifestPaths'],whole['selectedManifestPaths']),'all11 whole manifests and paths')
expected_frame=dict(schemaVersion=3,state='SECRET_OWNER355_NORMAL_OFF_VALIDATION_BOOTSTRAP_PASSED_V3',variant='normal-off',toolingIndex=refs['toolingIndex'],rootAuthority=api_authority_row,config=api_cfg_row,nativeSourceIndex=tr['nativeSourceIndex'],freezerSourceIndex=tr['freezerSourceIndex'],verifierSourceIndex=tr['verifierSourceIndex'],actualVerifierReview=tr['actualVerifierReview'],actualFrozenArtifactReview=tr['actualArtifactReview'],actualExportCandidate=refs['exportCandidate'],independentExportReview=refs['exportReview'],reviewedPins=pins_row,rootPinReview=pin_review_row,pin=pins['variants']['normal-off'],verifierFrame=whole,nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,enginePath=tr['engine']['path'],engine=tr['engine'],metadataDescriptor=tr['metadata'],freezeReceipt=tr['freezeReceipt'],metadata=metadata,selectedManifests=whole['selectedManifests'],selectedManifestPaths=whole['selectedManifestPaths'],originalToolingRoot=tr['originalToolingRoot'],configuredSourceRoot=tr['configuredSourceRoot'],sourceRoot=tr['frozenSourceRoot'],frozenRoot=tr['frozenRoot'],componentizeSourceRoot=tr['componentizeSourceRoot'],workRoot=tr['workRoot'],currentCompleteVerifierCalls=1,rawFrameRetained=True,validationBootstrapOnly=True,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,grantsRuntimeAuthority=False)
need(len(frame)==41 and strict(frame,expected_frame),'all41 original frame fields exact independently assembled DATA contract')
shape=read(js_observation['publicReturnShape']);callable_meta=read(js_observation['callableDescriptor'])
need(shape['returnObjectFrozen']is True and len(shape['ownFields'])==42 and [x['key']for x in shape['ownFields']]==list(frame)+['recheck'],'complete42 own-property shape no omitted field')
def js_type(v):return 'object'if v is None or type(v)in [list,dict]else 'boolean'if type(v)is bool else 'number'if type(v)in [int,float]else 'string'
for item in shape['ownFields']:
    k=item['key'];need(item==dict(key=k,keyType='string',valueType='function'if k=='recheck'else js_type(frame[k]),enumerable=True,configurable=False,writable=False,getter='undefined',setter='undefined'),'exact own property descriptor '+k)
need(callable_meta==dict(property='recheck',valueType='function',enumerable=True,configurable=False,writable=False,ownName='recheck',ownLength=0,returnObjectFrozen=True),'genuine callable descriptor retained without invoking')
need(read(current(OUT/'returned-recheck-start.json'))==dict(schemaVersion=1,callNumber=1)and read(current(OUT/'returned-recheck-result.json'))==dict(schemaVersion=1,fulfilled=True,valueType='undefined'),'one fulfilled returned recheck recorded')
need(read(current(OUT/'api-call-start.json'))==dict(schemaVersion=1,api=refs['bootstrapEntry'],config=api_cfg_row,callNumber=1),'single API announcement original entry/config')

def monitor(folder,authority,timeout):
    folder=Path(folder);t=read(current(folder/'terminal.json'));s=read(current(folder/'started.json'))
    need(type(t['rawExitCode'])is int and t['rawExitCode']==0 and t['authority']==authority,'raw0 actual monitor '+str(folder))
    for k in ['timeout','forcedCleanup']:need(t[k]is False,'no '+k+' '+str(folder))
    for k in ['signals','errors','interruptedSignals','remainingObservedPids']:need(t[k]==[],'no '+k+' '+str(folder))
    need(t['parentOwnedGroupGone']is t['allObservedOwnedGroupsGone']is True and t['finalGroups']and all(g['alive']is False for g in t['finalGroups']),'all observed groups gone '+str(folder))
    need(s['pid']==t['pid']and s['authority']==authority and s['timeoutSeconds']==timeout,'started tuple '+str(folder))
    names={'terminal.json','started.json','stdout.log','stderr.log'}
    for i,p in enumerate(t['observedProcesses']):
        n='owned-'+str(i).zfill(4)+'.json';e=read(current(folder/n));need(e['sequence']==i and e['process']==p,'exact process event '+str(folder)+'/'+str(i));names.add(n)
    need(len({p['pid']for p in t['observedProcesses']})==len(t['observedProcesses']),'distinct observed process identities '+str(folder))
    for k in ['stdout','stderr']:checked(t[k])
    need(t['stderr']['bytes']==0,'empty monitor stderr '+str(folder));tree(folder,names,True)
    return t,s
outer,outer_start=monitor(refs['observerExternalRoot'],root['rootAuthority'],1800)
inner,inner_start=monitor(refs['bootstrapExternalRoot'],api_authority_row,600)
owner_row=current(OUT/'owner.json');owner=read(owner_row);s=OUT.stat()
need(owner==dict(schemaVersion=1,controllerIndex=root['controllerIndex'],rootAuthority=root['rootAuthority'],config=root['config'],outputRoot=str(OUT),outputIdentity=[s.st_dev,s.st_ino]),'real parent output inode/owner')
need(outer_start['argv']==[refs['node']['path'],str(SOURCE/'ownership-secret-artifact-bootstrap-v3-root-controller.mjs'),json.dumps(root['config'],separators=(',',':')),json.dumps(owner_row,separators=(',',':'))],'plain exact Node argv no execArgv flags')
need(outer['pid']==13692 and outer['observedProcesses'][0]['pid']==13692,'original actual Node PID')
need(inner_start['argv']==[refs['python']['path'],'-B','-I',str(Path(refs['toolingIndex']['path']).parent/'artifact_tooling.py'),'worker','bootstrap','--config-descriptor',json.dumps(api_cfg_row,separators=(',',':'))],'exact original Python worker argv')
python_processes=[p for p in outer['observedProcesses']if '/Python'in p['command']]
need(len(python_processes)==2 and len(inner['observedProcesses'])==1 and inner['pid']==14294,'one observed Python parent and worker only')
need(python_processes[0]['pid']==14109 and python_processes[0]['ppid']==outer['pid']and python_processes[1]==inner['observedProcesses'][0]and python_processes[1]['ppid']==14109,'actual Node to Python parent to owned worker ancestry')
need(all(p['command']==refs['node']['path']or '/Python'in p['command']or p['command']in ['/bin/ps','(ps)']for p in outer['observedProcesses']),'only observed Node/Python operation plus sampler roles')
need(read(outer['stdout'])==dict(observation=current(OUT/'js-observation.json')),'whole raw Node stdout exact observation')
api_js=Path(refs['bootstrapJsRoot']);api_terminal=read(current(api_js/'terminal.json'))
need(api_terminal==dict(schemaVersion=3,rawExitCode=0,signal=None,childKillReported=False,timedOut=False,timeoutCauseEstablished=False,rawStreamsComplete=True,exceptionCode=None,enclosingRootControllerRequiredForIndependentCleanupReview=True),'actual original execFile parent raw0/complete/no ambiguous timeout claim')
need((api_js/'stderr.log').read_bytes()==b'','empty original API parent stderr');current(api_js/'stderr.log')
parent_lines=[json.loads(b)for b in Path(current(api_js/'stdout.log')['path']).read_bytes().splitlines()if b]
python_observation_row=current(Path(refs['bootstrapOutputRoot'])/'controller-observation.json');python_observation=read(python_observation_row)
need(parent_lines==[dict(pid=inner['pid'],timeoutSeconds=600),dict(observation=python_observation_row,completeUnreviewed=True)],'complete two raw Python parent JSONL roles')
need(strict(read(inner['stdout']),frame),'whole raw worker JSON equals actual bootstrap frame')
need(python_observation['completePhaseReturn']==frame_row and python_observation['rawTerminal']==current(Path(refs['bootstrapExternalRoot'])/'terminal.json')and python_observation['sourceAndOriginalProtectionRechecked']is True and python_observation['errors']==[],'genuine original Python collector roles')
need(read(current(api_js/'post-audit.json'))==dict(schemaVersion=3,sourceAndProofProtectionRechecked=True,engineExecuted=False,operationalAdmission=False),'actual API final audit')

receipt=read(tr['freezeReceipt']);names={'normal-off-freeze-receipt.json'}
for r in receipt['copies']:
    checked(r);p=Path(r['path']);names.add(p.relative_to(tr['frozenRoot']).as_posix());need(p.stat().st_nlink==1,'single-link frozen '+r['path'])
    if r['original']is not None:
        checked(dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes']));a=p.stat();b=Path(r['original']).stat();need((a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino),'independent frozen copy '+r['path'])
need(len(receipt['copies'])==1902 and len(names)==1903,'actual full1902/1903 frozen roles');tree(tr['frozenRoot'],names,True)
normal=read(tr['normalProtection']);checked(normal['freezeReceipt'])
for d in normal['frozenCopyEntries']:checked(d)
for d in normal['originals']:checked(d['original']);checked(d['frozen'])
need(len(normal['requiredNormalFreezeMembership'])==1391 and normal['originalReferenceEntries']==1387,'old normal1391/1387 protected');tree(Path(normal['freezeReceipt']['path']).parent,normal['requiredNormalFreezeMembership'])
for m,v in zip(metadata['selectedModuleManifests'],frame['selectedManifests']):
    d=current(Path(tr['frozenSourceRoot'])/m['path']);need(d['sha256']==m['sha256']and strict(read(d),v),'full selected manifest '+m['path'])
for folder,names in [(OUT,['owner.json','api-call-start.json','public-return-shape.json','whole-public-data.json','callable-property.json','returned-recheck-start.json','returned-recheck-result.json','js-observation.json','raw-terminal-observed.json','root-observation.json']),(Path(refs['bootstrapOutputRoot']),['whole-verifier-frame.json','bootstrap-frame.json','raw-terminal-observed.json','controller-observation.json']),(api_js,['stdout.log','stderr.log','terminal.json','post-audit.json'])]:
    for n in names:current(folder/n)
    tree(folder,names,True)
need(root['rawExitCode']==0 and root['error']is root['protectionError']is None and root['sourceAndOriginalProtectionRechecked']is True,'actual parent result raw0/protection')
for path,i in identities.items():
    p=Path(path);s=p.stat();need((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,str(p.resolve()))==i,'final stable '+path)
for base,names,private in list(trees):tree(base,names,private)
write('input-hashes.json',dict(schemaVersion=1,files=list(rows.values()),readHashJsonDataOnly=True,ownerActionsInvoked=False))
write('checks.json',dict(schemaVersion=1,checks=len(checks),names=checks,helperApiRecheckMonitorNodeOrEngineRerun=False))
coverage=dict(controllerMembers=40,sourceInputs=27976,fixedFamilies=14,nativeSources=355,externalEmbeddingSources=3,metadataFields=75,selectedWholeManifests=11,frozenEntries=1902,frozenTreeFiles=1903,oldNormalFiles=1391,oldNormalOriginalEntries=1387,publicDataOwnFields=41,totalOwnProperties=42,observedApiCalls=1,observedReturnedRecheckCalls=1,observedOuterProcesses=len(outer['observedProcesses']),observedPythonOperationProcesses=2,ownedWorkerProcesses=1,apiParentJsonlRecords=2,wholePublicDataBytes=public_row['bytes'],pinChanges=4,otherVariantsNull=3)
write('audit-results.json',dict(schemaVersion=1,rootObservation=root_row,coverage=coverage,checks=len(checks),paths=len(rows),logicalBytes=sum(d['bytes']for d in rows.values()),typedFullFramesEqual=True,completePinDataDeltaReviewed=True,allObservedOwnedGroupsGone=True,fullSourceAndOriginalProtectionCurrent=True,noConcreteActualEvidenceBlockerFound=True,reviewerActionsInvoked=False))
write('actual-descriptors.json',dict(schemaVersion=1,controllerSourceIndex=root['controllerIndex'],controllerSourceReview=source_authority['sourceIndependentReview'],toolingSourceIndex=refs['toolingIndex'],toolingSourceReview=refs['toolingSourceReview'],actualExportReview=refs['exportReview'],actualExportCandidate=refs['exportCandidate'],actualExportRootObservation=refs['exportRootObservation'],rootObservation=root_row,jsObservation=current(OUT/'js-observation.json'),rootAuthority=root['rootAuthority'],config=root['config'],deriveRootReview=derive_review_row,deriveObservation=derive_review['actualObservation'],deriveAuthority=derive_obs['rootAuthority'],deriveConfig=derive_obs['config'],reviewedPins=pins_row,rootPinReview=pin_review_row,originalApiAuthority=api_authority_row,originalApiConfig=api_cfg_row,wholePublicData=public_row,retainedPythonFrame=frame_row,publicReturnShape=js_observation['publicReturnShape'],callableDescriptor=js_observation['callableDescriptor'],returnedRecheckStart=current(OUT/'returned-recheck-start.json'),returnedRecheckResult=current(OUT/'returned-recheck-result.json'),outerNodeTerminal=current(Path(refs['observerExternalRoot'])/'terminal.json'),apiPythonParentTerminal=current(api_js/'terminal.json'),ownedPythonWorkerTerminal=current(Path(refs['bootstrapExternalRoot'])/'terminal.json'),engine=tr['engine'],metadata=tr['metadata'],freezeReceipt=tr['freezeReceipt'],nativeSourceIndex=tr['nativeSourceIndex'],freezerSourceIndex=tr['freezerSourceIndex'],verifierSourceIndex=tr['verifierSourceIndex']))
print(json.dumps(dict(state='INDEPENDENT_ACTUAL_SECRET355_BOOTSTRAP_DATA_AUDIT_PASSED',checks=len(checks),paths=len(rows),coverage=coverage,reviewerActionsInvoked=False)))
