"""Pure/data/AST regression only; never import owner guards, native/common or actions."""
from pathlib import Path
import ast,copy,hashlib,json,types
OWN=Path(__file__).resolve().parent
K=OWN.parent
NATIVE=K/'ownership-gc-native-candidate-v2'
checks=[]
def check(name,value):
    assert value,name
    checks.append(dict(name=name,passed=True))
def refuses(name,fn):
    try:fn()
    except (AssertionError,KeyError,TypeError,ValueError):check(name,True)
    else:raise AssertionError(name+' accepted')
def extract(path,names,extra):
    tree=ast.parse(path.read_bytes());nodes=[]
    for n in tree.body:
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name in names:nodes.append(n)
        elif isinstance(n,ast.Assign) and all(isinstance(t,ast.Name) for t in n.targets) and all(isinstance(n.value,ast.Constant) for t in n.targets):nodes.append(n)
    env=dict(extra);exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),env);return env

guard=OWN/'amendment-guard.py'
env=extract(guard,{'select_helper'},{'Path':Path})
inputs=json.loads((NATIVE/'stage-inputs.json').read_bytes())
source='/private/tmp/starling-node-compat/crypto-owner355-gc-v2-source'
normal='/private/tmp/starling-node-compat/crypto-owner-source-v2'
tools=source+'/tests/node-compat/foundation-crypto/native-integration-candidate-v2/artifact-tools'
select=env['select_helper'];args=(source,tools,normal)
selected=select(inputs,*args)
suffix=[r for r in inputs['files'] if r['path'].endswith('/artifact-tools/artifact_common.py')]
check('actual eleven suffix rows retained',len(suffix)==11)
check('old first suffix differs from actual crypto helper',suffix[0]['original']['sha256']!=selected['sha256'])
check('exact crypto descriptor selected',selected==dict(path=tools+'/artifact_common.py',sha256=env['HELPER_SHA'],bytes=19299))
check('actual selected staged bytes are exact',len(Path(selected['path']).read_bytes())==selected['bytes'] and hashlib.sha256(Path(selected['path']).read_bytes()).hexdigest()==selected['sha256'])
check('permuted suffix order cannot select another helper',select(dict(files=list(reversed(inputs['files']))),*args)==selected)
unique=[r for r in inputs['files'] if r['path']==env['NATIVE_RELATIVE']][0]
refuses('missing exact row',lambda:select(dict(files=[r for r in inputs['files'] if r!=unique]),*args))
refuses('duplicate exact row even identical',lambda:select(dict(files=inputs['files']+[copy.deepcopy(unique)]),*args))
for field,value in [('sha256','0'*64),('bytes',15391),('path',normal+'/wrong/artifact_common.py')]:
    changed=copy.deepcopy(inputs);next(r for r in changed['files'] if r['path']==env['NATIVE_RELATIVE'])['original'][field]=value
    refuses('wrong selected original '+field,lambda c=changed:select(c,*args))
refuses('misrooted tools',lambda:select(inputs,source,tools+'/wrong',normal))
refuses('misrooted configured source',lambda:select(inputs,source+'/wrong',tools,normal))
# Execute exact native-import seam with explicit mocked importlib/sys/controller/native objects.
# No real module or owner helper is imported; all calls are tracked below.
def seam(preexisting=None,context_path=None,io_path=None):
    log=[];captured=[dict(path='config',sha256='c'*64,bytes=1)]
    cfg=dict(sourceIndex=dict(path=str(NATIVE/'index.json'),sha256='ed0665046ec293b846069df0c050a388b1d717abbf4a0e56c64d8bd17d9a6d05',bytes=4777),helperAmendmentIndex=dict(path=str(OWN/'index.json'),sha256='a'*64,bytes=1),helperAmendmentAuthority=dict(path='new-amendment-authority',sha256='b'*64,bytes=1))
    native_root=dict(role='new genuine native phase',independentBuildReview=dict(index=dict(path=str(K/'independent-ownership-gc-v2-native-build-review-v1/index.json'))))
    original_frame=dict(sourceIndex=cfg['sourceIndex'],rootAuthority=dict(role='native-root'),peerIndex=dict(role='native-peer-index'),peerResult=dict(role='native-peer-result'),capsules=[])
    originals=copy.deepcopy(original_frame)
    fake_sys=types.SimpleNamespace(modules={} if preexisting is None else {preexisting:object()},path=[])
    native=types.SimpleNamespace(C=types.SimpleNamespace(__file__=context_path or str(NATIVE/'context.py'),SOURCE=source,TOOLS=tools))
    native.authorize=lambda row,phase:(log.append(('native-authorize',row,phase)) or original_frame)
    native.recheck=lambda frame:log.append(('native-recheck',frame['sourceIndex']))
    def execute(module):
        log.append(('native-module-import',str(NATIVE/'guard.py')))
        module.__dict__.update(native.__dict__)
        fake_sys.modules['data_io']=types.SimpleNamespace(__file__=io_path or str(NATIVE/'data_io.py'))
    lib=types.SimpleNamespace(util=types.SimpleNamespace(spec_from_file_location=lambda name,path:types.SimpleNamespace(loader=types.SimpleNamespace(exec_module=execute)),module_from_spec=lambda spec:types.SimpleNamespace()))
    controller=types.SimpleNamespace(NATIVE=NATIVE,SOURCE=source,TOOLS=tools,NATIVE_SHA=cfg['sourceIndex']['sha256'])
    controller.authorize=lambda row:(log.append(('controller-authorize',row)) or (cfg,native_root,captured,None,[]))
    controller.recheck=lambda rows,indices:log.append(('controller-recheck',len(rows)))
    controller.read=lambda row:cfg if row==captured[0] else dict(independentSourceReview=dict(role='amendment-peer',index=dict(path=str(K/'future-helper-source-peer/index.json'))))
    controller.checked=lambda row:log.append(('checked',row))
    e=extract(guard,{'authorize','recheck'},{'Path':Path,'sys':fake_sys,'importlib':lib})
    result=e['authorize'](captured[0],controller)
    return result,originals,log,fake_sys,cfg
f,originals,log,sy,cfg=seam()
for key in ('sourceIndex','rootAuthority','peerIndex','peerResult'):
    check('genuine native frame '+key+' unchanged',f[key]==originals[key])
check('amendment indexed role distinct',f['helperAmendmentFrame']['index']==cfg['helperAmendmentIndex'] and f['sourceIndex']!=f['helperAmendmentFrame']['index'])
check('native authorize genuine freeze phase',any(x[0]=='native-authorize' and x[2]=='freeze' for x in log))
check('complete controller authentication precedes native import',log[0][0]=='controller-authorize' and log[1][0]=='native-module-import')
check('native path inserted genuinely without fake modules',sy.path==[str(NATIVE)] and set(sy.modules)=={'data_io'})
check('both frames rechecked',any(x[0]=='native-recheck' for x in log) and any(x[0]=='controller-recheck' for x in log))
for name in ('context','data_io','guard'):refuses('pre-existing native module rejected '+name,lambda n=name:seam(preexisting=n))
refuses('wrong native context module path',lambda:seam(context_path=str(OWN/'context.py')))
refuses('wrong native data_io module path',lambda:seam(io_path=str(OWN/'data_io.py')))
# Actual delegate bodies cannot invent admission or receipt observations.
calls=[];native=types.SimpleNamespace(validate_admission=lambda v:calls.append(('admission',v)),validate_receipt_roles=lambda *a:calls.append(('roles',a)))
e=extract(guard,{'validate_admission','validate_receipt_roles'},{})
frame={'_genuineNativeGuard':native,'sourceIndex':{'sha256':'native'},'helperAmendmentFrame':{'index':{'sha256':'amendment'}}}
v={'raw':'unmodified'};e['validate_admission'](frame,v)
check('admission is genuine direct delegate',calls[-1]==('admission',v))
receipt={'freezerSourceCorrection':dict(nativeSourceIndexSha256='native',helperAmendmentSourceIndexSha256='amendment')}
e['validate_receipt_roles'](frame,receipt,'active','donor')
check('receipt roles are genuine direct delegate',calls[-1]==('roles',(receipt,'active','donor')))
wrong=copy.deepcopy(receipt);wrong['freezerSourceCorrection']['nativeSourceIndexSha256']='amendment'
refuses('native receipt identity cannot be projected',lambda:e['validate_receipt_roles'](frame,wrong,'active','donor'))
wrong=copy.deepcopy(receipt);wrong['freezerSourceCorrection']['helperAmendmentSourceIndexSha256']='native'
refuses('helper receipt identity cannot be relabelled',lambda:e['validate_receipt_roles'](frame,wrong,'active','donor'))
# Pure authority data fixtures use finite indexed rows, never actual authority/actions.
ce=extract(OWN/'controller.py',{'validate_amendment_data'},{'family':lambda ix:[dict(path=str(OWN/'freeze.py'),sha256='e'*64,bytes=1)],'OWN':OWN,'NATIVE_SHA':cfg['sourceIndex']['sha256'],'OUT':Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-freeze-helper-v1-external-root'),'SOURCE':source,'TOOLS':tools,'WORK':'/private/tmp/starling-node-compat/crypto-owner355-gc-v2-build','FREEZE':'/private/tmp/starling-node-compat/crypto-owner355-gc-v2-freeze'})
a=json.loads((OWN/'future-helper-root.template.json').read_bytes());a['state']='ROOT_REVIEWED_CRYPTO_OWNER355_GC_FREEZER_HELPER_AMENDMENT_V1';a['freezeAllowed']=True
a.update(helperAmendmentIndexed=cfg['helperAmendmentIndex'],nativeSourceIndexed=cfg['sourceIndex'],nativeRootAuthority=dict(path='native-authority'),activeFreezerEntry=dict(path=str(OWN/'freeze.py'),sha256='e'*64,bytes=1),externalControllerEntry=dict(path=str(OWN/'controller.py'),sha256='f'*64,bytes=1),externalControllerIndex=cfg['helperAmendmentIndex'])
c=copy.deepcopy(cfg);c['rootAuthority']=a['nativeRootAuthority']
n=dict(helperAmendmentEntry=a['activeFreezerEntry'],externalControllerEntry=a['externalControllerEntry'],externalParentDeadlineSeconds=2400,engine=a['engine'],metadata=a['metadata'],independentBuildReview=a['independentBuildReview'])
ce['validate_amendment_data'](a,c,n,cfg['helperAmendmentIndex']);check('valid dual-context authority fixture',True)
for key,val in [('nativeRootAuthority',{}),('nativeSourceIndexed',{}),('helperAmendmentIndexed',{}),('externalOutputRoot','wrong'),('engine',{}),('metadata',{}),('priorFailure',{})]:
    q=copy.deepcopy(a);q[key]=val;refuses('wrong amendment authority '+key,lambda q=q:ce['validate_amendment_data'](q,c,n,cfg['helperAmendmentIndex']))
for key in ('buildAllowed','guestAllowed','engineExecutionAllowed','metadataProjectionAllowed','normalMutationAllowed'):
    q=copy.deepcopy(a);q[key]=True;refuses('forbidden authority '+key,lambda q=q:ce['validate_amendment_data'](q,c,n,cfg['helperAmendmentIndex']))
# Exact reversible donor afterimages, including helper-neutral body substance.
for file,donor,proof in [('freezer-body.py',NATIVE/'freezer-body.py','freezer-body-derivation.json'),('controller.py',K/'ownership-gc-freeze-controller-candidate-v1/controller.py','controller-derivation.json')]:
    p=json.loads((OWN/proof).read_bytes());text=(OWN/file).read_text()
    if 'inserted'in p:
        assert text.count(p['inserted'])==1;text=text.replace(p['inserted'],'')
        text=text.replace("    own_data = read(own_index)\n    assert own_data['sourceOnly'] is True and own_data['state'] == 'SEALED_SOURCE_ONLY_CRYPTO_OWNER355_GC_FREEZER_HELPER_AMENDMENT_V1'\n",'')
    for row in reversed(p['changes']):
        assert text.count(row['after'])==1;text=text.replace(row['after'],row['before'])
    check('exact donor reversal '+file,text==donor.read_text())
# All action-bearing local imports and native helper seams are source data below.
ft=(OWN/'freeze.py').read_text();ct=(OWN/'controller.py').read_text();gt=guard.read_text();bt=(OWN/'freezer-body.py').read_text()
for name,value in [
 ('primitive entire self authentication precedes controller import',ft.index('names|{\'index.json\'}')<ft.index("'gc_helper_amendment_controller'")),
 ('amendment authority before native import',gt.index('controller.authorize(config_row)')<gt.index("spec_from_file_location('genuine_crypto_gc_native_guard'")),
 ('real common import after exact check',gt.index('controller.checked(row)')<gt.index("'genuine_gc_staged_crypto_artifact_common'")),
 ('real common roots asserted no assignment',all(not isinstance(n,ast.Assign) or all(not isinstance(t,ast.Attribute) or t.attr not in ('HERE','REPO','OUTPUT') for t in n.targets) for n in ast.walk(ast.parse(gt)))),
 ('wrong old loader never called','native.load_common(' not in gt and 'guard.load_common(frame)' in ft),
 ('new actual freeze entry and external output',"str(OWN / 'freeze.py')"in ct and "freeze-helper-v1-external-root"in ct),
 ('native sourceIndex never reassigned',not any(isinstance(n,(ast.Assign,ast.AnnAssign,ast.AugAssign)) and any(isinstance(t,ast.Subscript) and isinstance(t.value,ast.Name) and t.value.id=='frame' and isinstance(t.slice,ast.Constant) and t.slice.value=='sourceIndex' for t in (n.targets if isinstance(n,ast.Assign) else [n.target])) for n in ast.walk(ast.parse(gt)))),
 ('active actual wrapper remains helperSha source',"context['active']['sha256']"in bt and "active_entry"in bt),
 ('dual indexed capsule roles explicit',"'nativeSourceIndexed': context['sourceIndex']"in bt and "'helperAmendmentIndexed': context['helperAmendmentFrame']['index']"in bt),
 ('new metadata capsule identity honest',"'nativeSourceIndexSha256': context['sourceIndex']['sha256']"in bt and "'helperAmendmentSourceIndexSha256'"in bt),
 ('failure finally rechecks both frames','finally:\n        guard.recheck(frame)'in ft),
 ('controller finally rechecks captured families','finally:\n        recheck(captured, family_indices)'in ct),
 ('build proof fixed exact reviewed proof',"assert build_peer == refs['actualBuildProof']"in ct),
 ('freezer unchanged explicit output APIs','validate_plan(plan, receipt_path, output=output_root)'in bt and 'execute_plan(plan, output=output_root)'in bt)
]:check(name,value)
syntax=[]
for p in sorted(OWN.glob('*.py')):
    ast.parse(p.read_bytes());syntax.append(p.name)
result=dict(schemaVersion=1,state='PURE_SOURCE_DATA_HELPER_SELECTION_REGRESSION_PASSED_V1',checks=checks,checkCount=len(checks),pythonAst=syntax,realSuffixMatches=suffix,selected=selected,nativeOrCommonHelpersImported=False,allImportedNativeSeamsMocked=True,ownerActionsInvoked=False,processesSpawned=False,sourceOnly=True)
(OWN/'source-regression-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(checks=len(checks),pythonAst=len(syntax),state=result['state'])))
