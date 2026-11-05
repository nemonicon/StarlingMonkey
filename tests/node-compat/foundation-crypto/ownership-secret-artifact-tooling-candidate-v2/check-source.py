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
review=dict(schemaVersion=2,state='ROOT_SECRET_OWNER355_NORMAL_OFF_VALIDATION_PIN_REVIEW_V2',toolingIndex=test_index,reviewedPins=reviewed_row,actualExportCandidate=export_row,independentExportReview=export_review,actualVerifierReview=refs['actualVerifierReview'],actualFrozenArtifactReview=refs['actualArtifactReview'],**{k:refs[k]for k in ['engine','metadata','freezeReceipt']},nativeSourceFiles=355,externalEmbeddingSources=3,selectedManifestCount=11,validationBootstrapOnly=True,otherVariantsNull=True,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,sourcePromotionAllowed=False)
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
runtime=extracted(['descriptor','outputs','validate_root','validate_source_peer'],source,dict(Path=Path,BASE=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-artifact-tooling-v2'),TIMEOUT=600,SOURCE_PEER_STATE='INDEPENDENT_CRYPTO_OWNER355_SECRET_ARTIFACT_TOOLING_SOURCE_REVIEW_PASSED_V2'))
root=json.loads((OWN/'future-root-authority.template.json').read_text());root.update(schemaVersion=2,state='ROOT_REVIEWED_SECRET_OWNER355_ARTIFACT_TOOLING_PHASE_V2',toolingIndex=test_index)
for phase in ['export','bootstrap']:
    x=copy.deepcopy(root);out,external=runtime['outputs'](phase);x.update(phase=phase,exportAllowed=phase=='export',bootstrapAllowed=phase=='bootstrap',outputRoot=str(out),externalOutputRoot=str(external),jsOutputRoot=str(Path('/private/tmp/starling-node-compat/crypto-owner355-secret-artifact-tooling-v2'))+'-bootstrap-js-normal-off' if phase=='bootstrap' else None)
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

for p in OWN.glob('*.py'):ast.parse(p.read_text());checks.append('Python AST '+p.name)
for p in OWN.glob('future-*.json'):
    v=json.loads(p.read_text());need(v.get('actualProof')is None,'future proof NULL '+p.name)
result=dict(schemaVersion=1,state='SECRET_ARTIFACT_TOOLING_SOURCE_PURE_DATA_CHECKS_PASSED_V2',checks=len(checks),checkNames=checks,authenticatedDataRows=len(data),dataFiles=list(data.values()),pythonAstOnly=True,jsGrammarOrNodeExecuted=False,syntheticZeroDigestRowsConfinedToPureTests=True,operationalEntryBodiesInvoked=False,verifierOrMonitorInvoked=False,exportOrBootstrapInvoked=False,nodeOrEngineInvoked=False)
path=OWN/'pure-results.json';path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(state=result['state'],checks=len(checks),rows=len(data))))
