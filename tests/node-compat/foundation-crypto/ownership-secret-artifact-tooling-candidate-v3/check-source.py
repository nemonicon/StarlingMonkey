"""Source-only AST, real frozen DATA and pure seam checks. No operational imports."""
from pathlib import Path
import ast,copy,hashlib,json,os,sys,tempfile

OWN=Path(__file__).resolve().parent
assert sys.dont_write_bytecode
checks=[];data={}
def need(value,name):
    assert value,name
    checks.append(name)
def raw(row):
    p=Path(row['path']);a=p.stat();h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    z=p.stat();need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns),'stable DATA '+row['path'])
    need(a.st_size==row['bytes']and h.hexdigest()==row['sha256'],'exact DATA '+row['path']);data[row['path']]={k:row[k]for k in ['path','sha256','bytes']}
    return p
def read(row):return json.loads(raw(row).read_bytes())
def reject(call,name):
    try:call()
    except (AssertionError,KeyError,ValueError,TypeError,StopIteration,FileExistsError):checks.append(name);return
    raise AssertionError('Expected refusal: '+name)
def extracted(names,source,env):
    tree=ast.parse(source);selected=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names]
    assert len(selected)==len(names)
    exec(compile(ast.Module(body=selected,type_ignores=[]),'<extracted actual pure seam>','exec'),env);return env

refs=json.loads((OWN/'references.json').read_text());contract=read(refs['verifierContract']);frame=read(refs['actualVerifierWholeFrame']);receipt=read(refs['freezeReceipt'])
proof=read(refs['actualVerifierReview']['result']);wire=read(refs['actualVerifierContract'])
need(proof['state']==wire['requiredReviewState']and proof['verifiedPassed']is True,'actual f894 DATA proof')
need(frame['metadata']==read(refs['metadata'])and len(frame['metadata'])==75,'all actual75 raw metadata values')
for r,v in zip(frame['metadata']['selectedModuleManifests'],frame['selectedManifests']):
    p=Path(refs['frozenSourceRoot'])/r['path'];need(hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']and json.loads(p.read_bytes())==v,'complete original selected manifest '+r['path'])

model_source=(OWN/'pin_model.py').read_text();env={};exec(compile(model_source,str(OWN/'pin_model.py'),'exec'),env)
# This zero digest is confined to this pure model test, never an action pin.
test_index=dict(path=str(OWN/'index.json'),sha256='0'*64,bytes=0)
pin=env['candidate'](frame,receipt,refs,test_index);document=env['unreviewed_document'](pin);reviewed=env['reviewed_document'](document)
need(document['variants']['normal-off']['verifierFrame']==frame,'whole verifier frame retained without projection')
need(document['variants']['normal-off']['verifierFrame']['metadata']==frame['metadata'],'all75 metadata retained')
need(document['variants']['normal-off']['verifierFrame']['selectedManifests']==frame['selectedManifests'],'all11 complete manifest values retained')
need(all(document['variants'][k]is None for k in ['normal-runtime','gc-off','disabled-off']),'other three variants NULL')
before=copy.deepcopy(frame);pin['verifierFrame']['metadata']['sourceManifest'][0]['sha256']='0'*64
need(frame==before,'candidate owns an independent DATA copy');pin=env['candidate'](frame,receipt,refs,test_index)
export_row=dict(path='/private/tmp/PURE-ONLY-candidate.json',sha256='0'*64,bytes=0);reviewed_row=dict(path='/private/tmp/PURE-ONLY-reviewed.json',sha256='0'*64,bytes=0)
export_review=dict(index=export_row,result=export_row)
review=dict(schemaVersion=3,state='ROOT_SECRET_OWNER355_NORMAL_OFF_VALIDATION_PIN_REVIEW_V3',toolingIndex=test_index,reviewedPins=reviewed_row,actualExportCandidate=export_row,independentExportReview=export_review,actualVerifierReview=refs['actualVerifierReview'],actualFrozenArtifactReview=refs['actualArtifactReview'],**{k:refs[k]for k in ['engine','metadata','freezeReceipt']},nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,validationBootstrapOnly=True,otherVariantsNull=True,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,sourcePromotionAllowed=False)
def select(doc=reviewed,rv=review):return env['select_reviewed'](doc,rv,pin,reviewed_row,export_row,export_review,refs)
selected=select();need(selected==reviewed['variants']['normal-off'],'genuine four-state/flag-only derivation model')
for key in frame['metadata']:
    bad=copy.deepcopy(reviewed);bad['variants']['normal-off']['verifierFrame']['metadata'][key]={'PURE_MUTATION':key}
    reject(lambda:select(bad),'reject metadata projection '+key)
for i in range(11):
    bad=copy.deepcopy(reviewed);bad['variants']['normal-off']['verifierFrame']['selectedManifests'][i]['extraUnreviewedField']=True
    reject(lambda:select(bad),'reject changed full manifest '+str(i))
for label in ['normal-runtime','gc-off','disabled-off']:
    bad=copy.deepcopy(reviewed);bad['variants'][label]=selected;reject(lambda:select(bad),'reject selected extra variant '+label)
for key in ['engine','metadataDescriptor','freezeReceipt','frozenFiles','nativeSourceFiles','externalEmbeddingSources','selectedManifestCount']:
    bad=copy.deepcopy(reviewed);bad['variants']['normal-off'][key]=None;reject(lambda:select(bad),'reject changed pin '+key)
for key in ['toolingIndex','actualVerifierReview','actualFrozenArtifactReview','actualExportCandidate','reviewedPins','independentExportReview','otherVariantsNull','operationalAdmission']:
    bad=copy.deepcopy(review);bad[key]=None;reject(lambda:select(rv=bad),'reject review mismatch '+key)
bootstrap=env['bootstrap_frame'](selected,frame,refs,test_index,export_row,export_row,reviewed_row,export_row,export_row,export_review)
need(bootstrap['verifierFrame']==frame and bootstrap['metadata']==frame['metadata']and bootstrap['selectedManifests']==frame['selectedManifests'],'full direct Python/JS bootstrap DATA contract')
need(bootstrap['metadata']['enginePath']==frame['metadata']['enginePath']and bootstrap['enginePath']==refs['engine']['path'],'raw build enginePath preserved separately from frozen selected engine')

source=(OWN/'artifact_tooling.py').read_text();tree=ast.parse(source)
runtime=extracted(['descriptor','outputs','validate_root','validate_source_peer'],source,dict(Path=Path,BASE=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-artifact-tooling-v3'),TIMEOUT=600,SOURCE_PEER_STATE='INDEPENDENT_CRYPTO_OWNER355_SECRET_ARTIFACT_TOOLING_SOURCE_REVIEW_PASSED_V3'))
root=json.loads((OWN/'future-root-authority.template.json').read_text());root.update(schemaVersion=3,state='ROOT_REVIEWED_SECRET_OWNER355_ARTIFACT_TOOLING_PHASE_V3',toolingIndex=test_index)
for phase in ['export','bootstrap']:
    x=copy.deepcopy(root);out,external=runtime['outputs'](phase);x.update(phase=phase,exportAllowed=phase=='export',bootstrapAllowed=phase=='bootstrap',outputRoot=str(out),externalOutputRoot=str(external),jsOutputRoot=str(Path('/private/tmp/starling-node-compat/crypto-owner355-secret-artifact-tooling-v3'))+'-bootstrap-js-normal-off' if phase=='bootstrap' else None)
    if phase=='bootstrap':x.update(actualExportCandidate=export_row,reviewedPins=reviewed_row,rootPinReview=export_row,independentExportReview=export_review)
    runtime['validate_root'](x,test_index,refs,phase);checks.append('real '+phase+' Root model only')
    for key in ['nativeSourceFiles','selectedManifestCount','nativeSourceIndex','verifierSourceIndex','actualVerifierReview','engine','metadata','freezeReceipt','configuredSourceRoot','frozenSourceRoot','outputRoot','externalOutputRoot','externalParentDeadlineSeconds','expectedCompleteVerifierCalls','metadataProjectionAllowed','engineExecutionAllowed','runtimeAuthority']:
        bad=copy.deepcopy(x);bad[key]={'PURE_MUTATION':True} if key=='runtimeAuthority' else None;reject(lambda:runtime['validate_root'](bad,test_index,refs,phase),'reject '+phase+' Root field '+key)
reject(lambda:runtime['validate_root'](json.loads((OWN/'future-root-authority.template.json').read_text()),test_index,refs,'export'),'unactivated source template refuses')

# Exercise the real parent's argv expression against the real main parser,
# replacing only action endpoints. No authorize/worker/monitor body is called.
parent=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='parent')
assignment=next(n for n in parent.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='argv'for t in n.targets))
expression=ast.Expression(assignment.value);ast.fix_missing_locations(expression)
for phase in ['export','bootstrap']:
    cfg=dict(path='/private/tmp/PURE-ONLY-config.json',sha256='0'*64,bytes=0);f=dict(refs=refs,phase=phase,configRow=cfg)
    argv=eval(compile(expression,'<actual parent argv>','eval'),dict(frame=f,OWN=OWN,json=json))
    need(argv[:3]==[refs['python']['path'],'-B','-I'],'pinned isolated Python argv '+phase)
    need(argv[3:]==[str(OWN/'artifact_tooling.py'),'worker',phase,'--config-descriptor',json.dumps(cfg,separators=(',',':'))],'actual parent worker argv '+phase)
    calls=[]
    class Cap:
        def recheck(self):calls.append('recheck')
    class Sys:pass
    fake=Sys();fake.argv=argv[3:]
    context=dict(Path=Path,OWN=OWN,__file__=str(OWN/'artifact_tooling.py'),sys=fake,json=json,authorize=lambda row,p:(calls.append(('authorize',row,p))or dict(capture=Cap())),worker=lambda f:calls.append('worker'),parent=lambda f:99)
    extracted(['main'],source,context);need(context['main']()==0 and calls==[('authorize',cfg,phase),'worker','recheck'],'genuine caller/callee parser join '+phase)
    fake.argv[3]='--wrong';reject(lambda:context['main'](),'wrong CLI flag refuses '+phase)

authorize=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='authorize');auth=ast.get_source_segment(source,authorize)
need(auth.index("ledger=capture.read")<auth.index('model=load_actual'),'complete protected ledger before custom model import')
need(auth.index('authenticate_actual_review')<auth.index('model=load_actual'),'actual verifier proof before custom imports')
need(auth.index("capture.families.append((Path(refs['frozenRoot'])")<auth.index('model=load_actual'),'full frozen membership before custom imports')
need('finally:capture.recheck()'in auth,'authorize custom import finally protection')
need("finally:frame['capture'].recheck()"in source,'entry final/failure whole protection')
worker=ast.get_source_segment(source,next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='worker'))
need(worker.index("write(out/'whole-verifier-frame.json',verified)")<worker.index("assert verified==frame['historical']"),'full helper return retained before equality')
need(worker.count("helper.verify_frozen(frame['contract'])")==1,'one genuine original helper call')
need(not any(isinstance(n,ast.Attribute)and isinstance(n.ctx,ast.Store)and isinstance(n.value,ast.Name)and n.value.id in ['helper','monitor']for n in ast.walk(tree)),'no helper/global/state rebinding')
js=(OWN/'bootstrap.mjs').read_text()
need(all(line.split('from ',1)[-1].strip().strip(';').strip("'\"").startswith('node:')for line in js.splitlines()if line.startswith('import ')),'JS imports Node built-ins only')
need(js.index('const cfgRow=captureDescriptor(configDescriptor)')<js.index('await c.read(cfgRow)'),'JS caller primitives captured before await')
need(js.index("await write(join(JS_OUT,'stdout.log')")<js.index("need(error===null&&stderr.length===0"),'raw JS parent streams before checks')
need("lines.length===2"in js and "lines[0].pid"in js and "lines[1].observation"in js,'monitor prefix and actual observation roles preserved')
need(js.index('await c.recheck();')<js.index('result=await run('),'JS complete source/protection before child call')
need('if(failure!==null)throw failure' in js and "'post-audit.json'"in js,'JS final/failure protection saved and enforced')
need('recheck does not call helper again' in json.loads((OWN/'api-contract.json').read_text())['returns'],'recheck semantics explicit')

# M1: exercise the actual indexed-input loop and actual Capture.file/recheck
# methods with memory-only fingerprints. Never mutate a real protected input.
manifest=json.loads((OWN/'source-inputs.json').read_text())
loop=next(n for n in authorize.body if isinstance(n,ast.For)and isinstance(n.iter,ast.Subscript)and isinstance(n.iter.value,ast.Name)and n.iter.value.id=='own_inputs')
need(auth.index("own_inputs=capture.read")<auth.index('model=load_actual'),'own complete manifest authenticated before Python custom import')
need(js.index("const ownInputs=await c.read")<js.index('result=await run(')and 'for(const input of ownInputs.files)await c.file(input);'in js,'own complete manifest before JS child action')
donor_path=next(r['path']for r in manifest['files']if r['path'].endswith('/resource-pin-tooling-candidate-v1/pin_model.py'))
def manifest_capture_model(mutation=None,late=False):
    available={r['path']:({k:r[k]for k in ['path','sha256','bytes']},(1,i,r['bytes'],3,4),r['path'])for i,r in enumerate(manifest['files'])}
    def fake_fingerprint(path):
        if str(path)not in available:raise AssertionError('Pure missing input')
        return copy.deepcopy(available[str(path)])
    context=extracted(['descriptor','Capture'],source,dict(Path=Path,copy=copy,fingerprint=fake_fingerprint,exact_tree=lambda *args:None))
    cap=context['Capture']()
    def change():
        if mutation=='missing':del available[donor_path]
        if mutation=='bytes':
            row,identity,physical=available[donor_path];row['sha256']='0'*64;available[donor_path]=(row,identity,physical)
        if mutation=='identity':
            row,identity,physical=available[donor_path];available[donor_path]=(row,(*identity[:-1],999),physical)
    if mutation and not late:change()
    local=dict(capture=cap,own_inputs=manifest)
    exec(compile(ast.Module(body=[loop],type_ignores=[]),'<actual own input loop, memory fingerprints>','exec'),local)
    need(len(cap.rows)==len(manifest['files'])and donor_path in cap.rows,'all complete declared rows captured')
    if mutation and late:change()
    cap.recheck()
manifest_capture_model();checks.append('full current declared input capture and recheck, no filesystem seam')
for mutation in ['missing','bytes','identity']:
    if mutation!='identity':reject(lambda m=mutation:manifest_capture_model(m,False),'initial declared donor refusal '+mutation)
    reject(lambda m=mutation:manifest_capture_model(m,True),'final/failure declared donor refusal '+mutation)
manifest_capture_model('identity',False);checks.append('initial valid bytes capture current identity; later identity change refuses')

# M2: independent DATA translation of the exact new terminal expressions.
# This is not JS execution and does not manufacture an observed timeout cause.
need('childKillReported:error===null?false:'in js and 'timedOut:error===null?false:null'in js and 'timeoutCauseEstablished:false'in js,'kill primitive and timeout cause are distinct')
need('timedOut:error?.killed===true'not in js,'old broad timeout inference absent')
terminal_models=[]
for kind,error,stderr_bytes in [('success',None,0),('zero-with-stderr',None,1),('nonzero',dict(code=1,killed=False),0),('ambiguous-killed',dict(code=None,killed=True),0),('overflow-killed',dict(code='ERR_CHILD_PROCESS_STDIO_MAXBUFFER',killed=True),0),('spawn-error',dict(code='ENOENT'),0)]:
    terminal=dict(rawExitCode=0 if error is None else error.get('code')if type(error.get('code'))is int else None,childKillReported=False if error is None else error.get('killed')if type(error.get('killed'))is bool else None,timedOut=False if error is None else None,timeoutCauseEstablished=False,rawStreamsComplete=error is None,exceptionCode=error.get('code')if error and type(error.get('code'))is str else None)
    accepted=error is None and stderr_bytes==0
    need(accepted==(kind=='success'),'all error/overflow/incomplete or stderr paths refused '+kind)
    if error is not None:need(terminal['timedOut']is None and terminal['timeoutCauseEstablished']is False,'no invented timeout '+kind)
    terminal_models.append(dict(kind=kind,errorData=error,stderrBytes=stderr_bytes,terminal=terminal,accepted=accepted,actualProcessExecuted=False))
(OWN/'correction-models.json').write_text(json.dumps(dict(schemaVersion=1,manifestRows=len(manifest['files']),sourceDonorProtected=donor_path,actualCaptureMethodsAndLoopWithMemoryFingerprints=True,initialMissingOrBytesNegatives=2,finalFailureMissingBytesIdentityNegatives=3,initialValidByteIdentityCaptured=True,jsInputLoopSourceVerified=True,terminalModels=terminal_models,jsExecuted=False,ownerHelpersOrActionsInvoked=False),indent=2)+'\n')

for p in OWN.glob('*.py'):ast.parse(p.read_text());checks.append('Python AST '+p.name)
for p in OWN.glob('future-*.json'):
    v=json.loads(p.read_text());need(v.get('actualProof')is None,'future proof NULL '+p.name)
result=dict(schemaVersion=1,state='SECRET_ARTIFACT_TOOLING_SOURCE_PURE_DATA_CHECKS_PASSED_V3',checks=len(checks),checkNames=checks,authenticatedDataRows=len(data),dataFiles=list(data.values()),pythonAstOnly=True,jsGrammarOrNodeExecuted=False,syntheticZeroDigestRowsConfinedToPureTests=True,operationalEntryBodiesInvoked=False,verifierOrMonitorInvoked=False,exportOrBootstrapInvoked=False,nodeOrEngineInvoked=False)
path=OWN/'pure-results.json';path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(state=result['state'],checks=len(checks),rows=len(data))))
