"""Independent DATA/source review only. Never imports an owner module or acts."""
from pathlib import Path
import ast, copy, hashlib, json, stat

REPO=Path('/Users/dan/dev/StarlingMonkey')
S=REPO/'tests/node-compat/foundation-scheduler'
A=S/'combined-native-integration-candidate-v1'
B=S/'combined-native-stage-controller-candidate-v1'
OUT=Path(__file__).resolve().parent
STAGE=S/'independent-combined355-stage-controller-source-review-v1'
EXPECTED_A='08bfe069eec4d0bbfa8ad09b81ac4e0667f380de847de860c58495258c28df65'
EXPECTED_B='b1a21da1c0b925de8a7ccfb55113bff7487662051f95ba21d95b75e494864f1a'
checks=0;captured={};families={};aliases={};pure=0

def check(value,label):
    global checks
    assert value,label
    checks+=1

def physical(path):
    p=Path(path)
    check(p.is_absolute() and '..' not in p.parts,'absolute confined descriptor')
    if str(p).startswith('/tmp/'):p=Path('/private'+str(p))
    return p

def descriptor(p):
    p=Path(p);h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)

def verify(row):
    d={k:row[k] for k in ('path','sha256','bytes')};p=physical(d['path'])
    for q in (p,*p.parents):check(not q.is_symlink(),'no symlink '+str(q))
    t=p.stat();check(stat.S_ISREG(t.st_mode) and t.st_size==d['bytes'],'regular size '+str(p))
    identity=(t.st_dev,t.st_ino,t.st_size,t.st_mtime_ns,t.st_ctime_ns,stat.S_IMODE(t.st_mode))
    if str(p) not in captured:
        check(descriptor(p)['sha256']==d['sha256'],'full SHA '+str(p))
        captured[str(p)]=(d,identity)
    else:
        prior,old_identity=captured[str(p)]
        check((prior['sha256'],prior['bytes'],old_identity)==(d['sha256'],d['bytes'],identity),'consistent repeated descriptor '+str(p))
    aliases.setdefault(str(p),set()).add(d['path'])
    u=p.stat();check((u.st_dev,u.st_ino,u.st_size,u.st_mtime_ns,u.st_ctime_ns,stat.S_IMODE(u.st_mode))==identity,'stable read '+str(p))
    return p

def load(p):return json.loads(Path(p).read_bytes())

def family(root,expected=None):
    d=descriptor(root/'index.json')
    if expected:check(d['sha256']==expected,'held family SHA')
    verify(d);v=load(root/'index.json');names=set();rows=[d]
    for r in v['files']:
        n=r['path'];check(not n.startswith('/') and all(x not in ('','.','..') for x in n.split('/')),'safe member')
        check(n not in names,'unique member');names.add(n)
        row=dict(path=str(root/n),sha256=r['sha256'],bytes=r['bytes']);verify(row);rows.append(row)
    actual=set()
    for p in root.rglob('*'):
        check(not p.is_symlink(),'family link refusal')
        if p.is_file():actual.add(p.relative_to(root).as_posix())
    check(actual==names|{'index.json'},'exact family membership')
    families[str(root)]=d;return rows

def extracted(text,names,namespace):
    nodes={n.name:n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}
    exec(compile(ast.Module(body=[nodes[n] for n in names],type_ignores=[]),'<independent-pure-extraction>','exec'),namespace)
    return namespace

def refuse(fn,label):
    global pure
    try:fn()
    except (AssertionError,TypeError,KeyError,ValueError):check(True,label);pure+=1;return
    raise AssertionError('accepted negative '+label)

a_rows=family(A,EXPECTED_A);b_rows=family(B,EXPECTED_B)
for root in (A,B):
    for r in load(root/'input-hashes.json')['files']:verify(r)
refs=load(B/'references.json');monitor=physical(refs['monitorIndex']['path']).parent
m_rows=family(monitor,refs['monitorIndex']['sha256']);check(refs['monitorEntry'] in m_rows,'genuine monitor member')
policy=load(A/'policy.json');native=load(A/'native-origins.json')['files'];tools=load(A/'tool-origins.json')['files']
parent=load(REPO/'tests/node-compat/foundation-crypto/ownership-secret-integration-candidate-v1/policy.json')
before={r['path']:r['sha256'] for r in parent['expectedNativeSourceManifest']}
after={r['path']:r['sha256'] for r in native}
changed={p for p in before if before[p]!=after[p]}
expected={'builtins/web/timers.cpp','runtime/event_loop.cpp','host-apis/wasi-0.2.0/host_api.cpp','include/extension-api.h','builtins/node-compat/zlib/kernel.cpp','builtins/node-compat/zlib/factories.generated.h','builtins/node-compat/export-manifest.zlib.node-v22.14.0.json'}
check(len(before)==len(after)==len(native)==355 and before.keys()==after.keys(),'full genuine355 inventory')
check(changed==expected and sum(before[p]==after[p] for p in before)==348,'348+7 exact')
check(policy['expectedNativeSourceManifest']==[dict(path=r['path'],sha256=r['sha256']) for r in native],'current355 policy full equality')
origins={}
for r in native+tools:
    verify(dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes']));origins[r['path']]=physical(r['original'])
check(len(tools)==1226 and not set(after)&{r['path'] for r in tools},'native/tool disjoint')
check({r['path']:r for r in load(A/'stage-input-plan.json')['files']}=={r['path']:r for r in native+tools},'whole original plan union independent of ordering')
for r in load(A/'derivations.json')['changedFiles']:
    verify(r['afterimage']);verify(r['reviewedPayload'])
    check(Path(r['afterimage']['path']).read_bytes()==Path(r['reviewedPayload']['path']).read_bytes(),'reviewed exact native payload '+r['path'])
for key in ('cryptoKeyOwnershipSourcePolicy','cryptoSecretFailureSourcePolicy','streamConsumersSourcePolicy','zlibSourcePolicy'):
    check(policy[key]==parent[key],'immutable ancestry '+key)
for p in ['CMakeLists.txt','cmake/builtins.cmake','builtins/node-compat/register.cpp']+[r['path'] for r in parent['cryptoKeyOwnershipSourcePolicy']['changes']]+[r['path'] for r in parent['cryptoSecretFailureSourcePolicy']['changes']]:
    check(before[p]==after[p],'preserved native registration/crypto '+p)
check(len(policy['expectedComponentizeSourceManifest'])==3,'external3 ancestry')
check(len(policy['selectedModuleManifests'])==len(policy['selectedManifestValues'])==11,'eleven complete manifests')
for r,value in zip(policy['selectedModuleManifests'],policy['selectedManifestValues']):
    check(descriptor(origins[r['path']])['sha256']==r['sha256'] and load(origins[r['path']])==value,'whole selected manifest')
check(sum(r['path'].endswith('.cpp') and r['path'].startswith(('builtins/','runtime/')) for r in native)==62,'62 policy CPP')
delta_count=0
for d in load(A/'exact-derivations.json')['files']:
    verify(d['before']);verify(d['after']);old=Path(d['before']['path']).read_text();new=Path(d['after']['path']).read_text()
    fwd=old;rev=new
    for e in reversed(d['edits']):
        i=e['beforeOffset'];check(fwd[i:i+len(e['before'])]==e['before'],'forward offset');fwd=fwd[:i]+e['after']+fwd[i+len(e['before']):]
        j=e['afterOffset'];check(rev[j:j+len(e['after'])]==e['after'],'reverse offset');rev=rev[:j]+e['before']+rev[j+len(e['after']):];delta_count+=1
    check(fwd==new and rev==old,'whole forward/reverse tooling')
helper=(A/'layer-policy.py').read_text();recipe=(A/'proposed/tests/node-compat/build-engine.sh').read_text()
check('PARENT.' not in helper and 'sys.modules' not in helper,'no parent/global interception')
check(helper.index('authenticate_inputs()\nBASE_ROOT')<helper.index('BASE=json.loads'),'authenticate before ancestry')
check(helper.index('authenticate_inputs()\n    path=REPO')<helper.index('spec=importlib.util.spec_from_file_location'),'before genuine codec import')
check(recipe.index('codec.after(')<recipe.index('model.validate_metadata(')<recipe.index("with open(artifact + '.build.json', 'x')"),'fresh full metadata sequence')
check('metadata=json.loads' not in recipe and "'normal-off'" in recipe,'no historical metadata loader')
check('CMAKE_C_COMPILER_LAUNCHER= -DCMAKE_CXX_COMPILER_LAUNCHER=' in recipe and 'CCACHE_DISABLE=1 SCCACHE_DISABLE=1 CARGO_INCREMENTAL=0' in recipe,'fresh native/Rust cache guard')
check(recipe.index('Fresh combined355 ABI source/build/artifact paths required')<recipe.index('mkdir -p "$source_dir/lib"'),'fresh guard before external source creation')
for k in ['configuredSourceRoot','workRoot','freezeRoot']:check(not Path(policy['contexts'][k]).exists(),'future context absent')
registration=origins['builtins/node-compat/register.cpp'].read_text();cmake=origins['cmake/builtins.cmake'].read_text()
check('install_zlib(engine' in registration and 'install_stream_consumers(engine)' in registration,'genuine registrar retains optional modules')
for symbol in ['builtins::web::timers','builtins::web::crypto','NODE_COMPAT_ZLIB','NODE_COMPAT_STREAM_CONSUMERS']:
    check(symbol in cmake,'genuine CMake '+symbol)
ns=extracted(helper,['expected','_macro','_release','task_selection_commands'],dict(Path=Path,shlex=__import__('shlex'),POLICY=policy,ANCESTOR=load(REPO/'tests/node-compat/foundation-scheduler/integration-candidate-v1/policy.json')))
ns['_release'](['-O3','-DNDEBUG']);ns['_macro'](['-DX=1'],'X',True);pure+=2
for words in [['-O2','-DNDEBUG'],['-O3'],['-O3','-DNDEBUG','-DDEBUG=1']]:refuse(lambda w=words:ns['_release'](w),'release negative')
for words in [['-DX=0'],['-DX=1','-DX=1'],['-DX=1','-UX'],['-D','X=1']]:refuse(lambda w=words:ns['_macro'](w,'X',True),'macro negative')
controller=(B/'controller.py').read_text();tree=ast.parse(controller)
const=dict(REPO=REPO,OWN=B,SOURCE_SHA=EXPECTED_A,MONITOR_SHA=refs['monitorIndex']['sha256'],Path=Path,BASE='54b3329b3ce818fd1f244e871e9c259b63667cda',TIMEOUT=600)
for k,v in [('DEST','configuredSourceRoot'),('WORK','workRoot'),('FREEZE','freezeRoot')]:const[k]=Path(policy['contexts'][v])
const.update(OUT=Path('/private/tmp/starling-node-compat/combined-native355-v1-stage-external-root'),JOURNAL=Path('/private/tmp/starling-node-compat/combined-native355-v1-stage.json'))
cn=extracted(controller,['safe','plan_model','source_peer_model','stage_peer_model','root_model','terminal_model'],const)
plan=load(B/'stage-copy-plan.json')['files'];cn['plan_model'](plan,native,tools,a_rows);pure+=1
for r in plan:
    check(stat.S_IMODE(verify(dict(path=r['original'],sha256=r['sha256'],bytes=r['bytes'])).stat().st_mode)==r['sourceMode'],'exact original mode')
check(len(plan)==1613 and len({r['path'] for r in plan})==1613,'1613 unique targets')
for bad in ['../x','/x','a//b','a\\b','.git/config','a/./b']:
    refuse(lambda p=bad:cn['safe'](p),'confined target negative')
for kind in ['missing','duplicate','hash','role','mode']:
    rows=copy.deepcopy(plan)
    if kind=='missing':rows.pop()
    elif kind=='duplicate':rows[-1]=rows[0]
    elif kind=='hash':rows[0]['sha256']='0'*64
    elif kind=='role':rows[0]['roles']=['WRONG']
    else:rows[0]['sourceMode']=0o7777
    refuse(lambda rows=rows:cn['plan_model'](rows,native,tools,a_rows),'plan '+kind)
own=b_rows[0];rt=load(B/'root-authority.template.json')
refuse(lambda:cn['root_model'](rt,own,refs),'unissued Root template')
rt.update(state='ROOT_REVIEWED_COMBINED355_SOURCE_STAGE_V1',phase='source-stage-only',sourceStageAllowed=True,stageControllerIndex=own,stageControllerEntry=descriptor(B/'controller.py'))
cn['root_model'](rt,own,refs);pure+=1
for key,value in [('nativeBuildAllowed',True),('configuredSourceRoot','/wrong'),('expectedStageCopies',1424),('nativeSourceFiles',342),('baselineRevision','wrong'),('metadataProjectionAllowed',True),('privateBackendEvidenceHookEnabled',True),('actualBuildResult',{})]:
    v=copy.deepcopy(rt);v[key]=value;refuse(lambda v=v:cn['root_model'](v,own,refs),'Root '+key)
check(controller.index('frame=authorize(config_row)')<controller.index("spec=importlib.util.spec_from_file_location('genuine_combined355_stage_monitor'"),'full auth before custom monitor import')
check('finally:recheck(frame)' in controller and 'failureInputRecheckPassed' in controller,'parent and worker failure rechecks')
check("'--no-local','--no-checkout'" in controller and "'checkout','--detach',BASE" in controller,'genuine pinned detached clone')
check("module.monitor(argv,str(REPO),{**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},OUT,TIMEOUT,frame['config']['rootAuthority'])" in controller,'genuine six argument monitor API')
check("s.st_nlink==1" in controller and "not in original_ids" in controller,'ownership before truncate')
check("record['stdout']=durable" in controller and "record['terminal']=durable" in controller,'raw Git command retention')
check("shutil.disk_usage(DEST.parent).free>=2*1024**3" in controller,'2GiB stage initial floor')
for p in [const['DEST'],const['WORK'],const['FREEZE'],const['OUT'],const['JOURNAL']]:check(not p.exists() and not p.is_symlink(),'action roots absent')
asts=0
for root in (A,B):
    for p in root.rglob('*.py'):
        ast.parse(p.read_text());asts+=1
monitor_tree=ast.parse(Path(refs['monitorEntry']['path']).read_text())
mon=next(n for n in monitor_tree.body if isinstance(n,ast.FunctionDef) and n.name=='monitor')
check([x.arg for x in mon.args.args]==['argv','cwd','environment','output','timeout_seconds','authority'],'actual monitor positional API')
check(len(a_rows)==32 and len(b_rows)==17,'complete family sizes')
# All checks are finished before the final physical source/protection bookend.
for path,(d,identity) in captured.items():
    p=Path(path);t=p.stat();check((t.st_dev,t.st_ino,t.st_size,t.st_mtime_ns,t.st_ctime_ns,stat.S_IMODE(t.st_mode))==identity,'final original identity/mode')
    check(descriptor(p)['sha256']==d['sha256'],'final original full hash')
for root,d in list(families.items()):family(Path(root),d['sha256'])
ledger=[dict(**d,physicalPath=p,originalDescriptorPaths=sorted(aliases[p]),mode=identity[-1]) for p,(d,identity) in sorted(captured.items())]
def write(p,value):p.write_text(json.dumps(value,indent=2)+'\n')
write(OUT/'input-hashes.json',dict(schemaVersion=1,files=ledger))
audit=dict(schemaVersion=1,state='INDEPENDENT_COMBINED355_SOURCE_DATA_AUDIT_PASSED',checks=checks,uniqueFiles=len(captured),inputBytes=sum(r['bytes'] for r in ledger),integrationSourceIndex=a_rows[0],stageControllerSourceIndex=b_rows[0],monitorSourceIndex=refs['monitorIndex'],integrationFamilyMembers=len(a_rows)-1,stageControllerFamilyMembers=len(b_rows)-1,originalIntegrationInputs=1590,originalControllerInputs=1637,nativeSourceFiles=355,retainedParentNativeFiles=348,changedNativeFiles=sorted(changed),externalEmbeddingSources=3,selectedManifestCount=11,toolRows=1226,stageCopies=1613,toolingOffsetEdits=delta_count,pureExtractedCases=pure,pythonAstFiles=asts,finalOriginalHashIdentityModeAndMembershipRechecked=True,ownerModulesImported=False,gitStageBuildFreezeHelperCompilerEngineGuestActionsInvoked=False)
write(OUT/'audit-data.json',audit)
STAGE.mkdir(exist_ok=True)
write(STAGE/'audit-data.json',audit)
print(json.dumps(audit))
