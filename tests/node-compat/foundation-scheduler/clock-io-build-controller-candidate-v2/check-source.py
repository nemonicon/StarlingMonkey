"""Read/AST and injected pure models only. No operational entrypoint or tool."""
from pathlib import Path
import ast,copy,hashlib,json,os,re,tarfile,types

HERE=Path(__file__).resolve().parent
source=(HERE/'controller.py').read_text();tree=ast.parse(source);checks=[]
def check(v,name):assert v,name;checks.append(name)
def refuses(fn,name):
    try:fn()
    except (ValueError,KeyError,TypeError,AssertionError):checks.append(name);return
    raise AssertionError('Expected refusal: '+name)
def extract(names,context):
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names];assert len(nodes)==len(names)
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'<genuine extracted Source functions>','exec'),context);return context
refs=json.loads((HERE/'references.json').read_text());proposal=Path(refs['sourceIndex']['path']).parent
frame=dict(tools=json.loads((proposal/'tool-cut-references.json').read_text()),cut=json.loads((proposal/'source-cut.json').read_text()),plan=json.loads((proposal/'future-build-plan.json').read_text()),context=json.loads((HERE/'host-context.json').read_text()))
root_source=Path('/private/tmp/starling-node-compat/import-abi-clock-io-v1-source');work=Path('/private/tmp/starling-node-compat/import-abi-clock-io-v1-build');package=Path('/private/tmp/starling-node-compat/import-abi-clock-io-v1-package');external=Path('/private/tmp/starling-node-compat/import-abi-clock-io-v1-build-v2-external-root')
unit_names=['adapter_input_guard_refuses_unknown_payloads_before_parse','pure_and_clock_only_keep_distinct_capabilities','stream_profiles_keep_poll_and_stream_transport','explicitly_selected_world_io_is_retained']
env=dict(Path=Path,os=os,re=re,SOURCE=root_source,WORK=work,PACKAGE=package,EXTERNAL=external,PROPOSAL=proposal,SOURCE_SHA=refs['sourceIndex']['sha256'],FLOOR=800*1024**2,MAX_CRATE_BYTES=128*1024**2,UNIT_FILTERS=unit_names)
extract(['need','local','phase_model','materialization_plan','command_plan','archive_model','archive_member_model','tree_model','compiler_environment','unit_result_model'],env)
copies,aliases=env['materialization_plan'](frame);commands=env['command_plan'](frame)
check(len(copies)==5138 and len(aliases)==21,'real271+5+4862 copy plan and21aliases; no copy performed')
check(len({r['path']for r in copies})==5138,'unique actual declared destinations')
check(sum(Path(r['path']).is_relative_to(root_source)for r in copies)==271,'source271 distinct from package4867')
check(len(commands)==8 and [c['unitFilter']for c in commands if c['unitFilter']] == unit_names,'four separately selected real unit filters')
check(sum(c['timeoutSeconds']for c in commands)==7200,'one outer cap; command maxima not additional time')
check(all(c['argv'][0]==frame['tools']['cargo']['path']and c['argv'][c['argv'].index('--jobs')+1]=='1' for c in commands[:6]),'actual Cargo jobs1')
check(all(c['argv'][1]==str(package/'node_modules/@bytecodealliance/jco/dist/jco.js')for c in commands[-2:]),'Jco exact private CLI rebase only')
check(frame['plan']['commandPlans'][2]['argv'][1]==frame['tools']['jcoEntry']['path'],'original Source plan remains original')
for target in ['sourceRoot','workRoot','packageRoot']:
    bad=copy.deepcopy(frame);bad['plan'][target]='/private/tmp/WRONG';refuses(lambda:env['materialization_plan'](bad),'wrong role '+target)
bad=copy.deepcopy(frame);bad['tools']['jsToolchain']['files'].pop();refuses(lambda:env['materialization_plan'](bad),'missing tool file')
bad=copy.deepcopy(frame);bad['tools']['jsToolchain']['symlinks'][0]['target']='/outside';refuses(lambda:env['materialization_plan'](bad),'absolute alias')
bad=copy.deepcopy(frame);bad['cut']['files'][0]['path']='../outside';refuses(lambda:env['materialization_plan'](bad),'copy traversal')

root=json.loads((HERE/'future-root-authority.template.json').read_text());root.update(state='ROOT_REVIEWED_CLOCK_IO_TOOLS_BUILD_V2',phase='build-clock-io-tools')
for k in ['stageAllowed','privateVendorAllowed','downloadThreeLockedArchivesAllowed','rustBuildAndUnitTestsAllowed','jcoToolPackagingAllowed','prunerRefusalUnitTestAllowed']:root[k]=True
for k in ['adapterPublicationAllowed','adapterPruningAllowed','validAdapterPruningAllowed','nativeEngineBuildAllowed','applicationComponentAllowed','applicationGuestAllowed','keyOrCryptoAllowed','timingAllowed','sourcePromotionAllowed','operationalAdmission','runtimeAcceptanceClaim']:root[k]=False
env['phase_model'](root);checks.append('finite actual phase model only; no authority issued')
for key in ['sourceIndex','sourceRoot','workRoot','packageRoot','externalRoot','deadlineSeconds','requiredStartFreeBytes','minimumBoundaryFreeBytes','diskFloorPolicy','expectedCommandCount','prunerRefusalUnitTestAllowed','validAdapterPruningAllowed']:
    bad=copy.deepcopy(root);bad[key]=None;refuses(lambda:env['phase_model'](bad),'Root field mismatch '+key)
refuses(lambda:env['phase_model'](json.loads((HERE/'future-root-authority.template.json').read_text())),'NULL template refuses')
original=dict(HOME='/PURE/HOME',CODEX_HOME='/PURE/CODEX',PATH='/unsafe/bin',CC='/unsafe/cc',CARGO_TARGET_DIR='/unsafe',RUSTFLAGS='unsafe',PYTHONPATH='/unsafe',NODE_OPTIONS='unsafe',LANG='C')
out=env['compiler_environment'](frame,original)
check(out['HOME']==original['HOME']and out['CODEX_HOME']==original['CODEX_HOME'],'HOME and CODEX_HOME preserved values')
check(not any(k in out for k in ['CC','RUSTFLAGS','PYTHONPATH','NODE_OPTIONS','CARGO_TARGET_DIR']),'unrelated inherited compiler/loader overrides omitted')
check(out['CARGO_HOME']==str(work/'cargo-home')and out['TMPDIR']==str(work/'tmp')and out['CARGO_NET_OFFLINE']=='true','private offline Cargo and tmp')
check(out['CARGO_BUILD_JOBS']==out['BINARYEN_CORES']==out['RAYON_NUM_THREADS']=='1','singlejob/thread env')
check(original['PATH']=='/unsafe/bin'and original['RUSTFLAGS']=='unsafe','source environment not mutated')

for name in unit_names:
    text='running 1 test\ntest stub_wasi::clock_io_policy_tests::'+name+' ... ok\ntest result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 3 filtered out; finished in 0.00s\n'
    env['unit_result_model'](text,name);checks.append('one real filter parser '+name)
    refuses(lambda:env['unit_result_model'](text.replace('running 1 test','running 0 tests'),name),'zero-match result refuses '+name)
    refuses(lambda:env['unit_result_model'](text.replace('0 ignored','1 ignored'),name),'ignored result refuses '+name)
check(all('fn '+n+'()' in (proposal/'after/crates/spidermonkey-embedding-splicer/src/stub_wasi.rs').read_text()for n in unit_names),'all four exact Rust definitions are actual Source')

base=[dict(name='crate-1/Cargo.toml',kind='file',bytes=1),dict(name='crate-1/src/lib.rs',kind='file',bytes=2)]
check(env['archive_member_model']('crate-1',base)[1]==3,'regular metadata model only; no extraction')
for name,change in [('traversal',dict(name='crate-1/../escape',kind='file',bytes=1)),('symlink',dict(name='crate-1/link',kind='refused',bytes=0)),('outsideprefix',dict(name='other/Cargo.toml',kind='file',bytes=1)),('generatedchecksum',dict(name='crate-1/.cargo-checksum.json',kind='file',bytes=1)),('oversized',dict(name='crate-1/big',kind='file',bytes=33*1024**2)),('duplicate',base[0]),('parentafterchild',dict(name='crate-1/src',kind='file',bytes=1))]:
    refuses(lambda:env['archive_member_model']('crate-1',base+[change]),'tar metadata refusal '+name)
crate_data=[]
for item in frame['tools']['lockedRegistryArchives']:
    # Existing compressed archives are parsed as DATA only; no extraction,
    # vendor path, copy, network, Cargo or build operation is invoked.
    p=Path(item['descriptor']['path']);b=p.read_bytes();check(hashlib.sha256(b).hexdigest()==item['descriptor']['sha256'],'cached archive SHA '+item['name'])
    with tarfile.open(p,'r:*')as t:
        descriptions=[dict(name=m.name,kind='directory'if m.isdir()else('file'if m.isfile()else'refused'),bytes=m.size)for m in t]
    expected,total=env['archive_member_model'](item['name']+'-'+item['version'],descriptions)
    crate_data.append(dict(name=item['name'],version=item['version'],files=len(expected),unpackedBytes=total))
check(len(crate_data)==118 and sum(r['unpackedBytes']for r in crate_data)<512*1024**2,'actual118 existing archive headers fit declared bounds;3missing stay future')

for root_path in [root_source,package]:
    expected={str(Path(r['path']).relative_to(root_path)):r['source'] for r in copies if Path(r['path']).is_relative_to(root_path)}
    alias_map={str(Path(r['path']).relative_to(package)):r for r in aliases}if root_path==package else{}
    inventory=dict(files=[dict(v,relativePath=n)for n,v in expected.items()],links=[dict(path=n)for n in alias_map])
    env['tree_model'](inventory,expected,alias_map);checks.append('exact declared tree model '+str(root_path))
    bad=copy.deepcopy(inventory);bad['files'].pop();refuses(lambda:env['tree_model'](bad,expected,alias_map),'missing copied member '+str(root_path))
    bad=copy.deepcopy(inventory);bad['files'].append(dict(relativePath='unexpected',sha256='0'*64,bytes=0));refuses(lambda:env['tree_model'](bad,expected,alias_map),'unlisted copied member '+str(root_path))

# Execute the genuine raw_step against injected memory-only IO/monitor/space.
class MemPath:
    files=set()
    def __init__(self,value):self.value=value
    def __truediv__(self,name):return MemPath(self.value+'/'+name)
    @property
    def parent(self):return MemPath(self.value.rsplit('/',1)[0])
    def __str__(self):return self.value
    def mkdir(self,**kw):pass
    def is_file(self):return self.value in self.files
    def is_symlink(self):return False
def raw_case(code=0,timeout=False,spaces=(10**12,10**12),monitor_throws=False,writer_throws=False):
    MemPath.files=set();saved=[];calls=[];values=iter(spaces)
    def disk(p):
        v=next(values)
        if isinstance(v,Exception):raise v
        return types.SimpleNamespace(free=v)
    terminal=dict(authority={'PURE':True},rawExitCode=code,timeout=timeout,forcedCleanup=timeout,allObservedOwnedGroupsGone=True,parentOwnedGroupGone=True,signals=[],errors=[],interruptedSignals=[],remainingObservedPids=[],finalGroups=[dict(alive=False)])
    class Monitor:
        def monitor(self,*args):
            calls.append('monitor')
            folder=str(args[3]);MemPath.files.update(folder+'/'+n for n in ['stdout.log','stderr.log'])
            if monitor_throws:raise OSError('injected monitor failure')
            MemPath.files.add(folder+'/terminal.json');return terminal
    fakeos=types.SimpleNamespace(O_RDONLY=0,O_NOFOLLOW=0,open=lambda *a:1,fsync=lambda fd:None,close=lambda fd:None)
    def desc(p):return dict(path=str(p),sha256='0'*64,bytes=0)
    def save(p,v):
        if writer_throws:raise OSError('injected summary write failure')
        saved.append(copy.deepcopy(v));return desc(p)
    context=dict(WORK=MemPath('/PURE/work'),SOURCE=MemPath('/PURE/source'),FLOOR=800*1024**2,shutil=types.SimpleNamespace(disk_usage=disk),time=types.SimpleNamespace(monotonic=lambda:1.0),os=fakeos,row=desc,save=save,read=lambda d:terminal)
    extract(['need','local','raw_step'],context);caught=None
    try:context['raw_step'](dict(monitor=Monitor(),config=dict(rootAuthority={'PURE':True})),'pure-command',['PURE_ONLY'],{},600)
    except (ValueError,OSError)as e:caught=type(e).__name__
    return saved,calls,caught
saved,calls,error=raw_case();check(error is None and calls==['monitor']and saved[0]['afterFreeBytes']==10**12 and saved[0]['diskFloorMonitoredDuringCommand']is False,'real raw_step injected normal-post-space seam')
for name,kwargs in [('nonzero',dict(code=1)),('timeout',dict(timeout=True)),('postfloor',dict(spaces=(10**12,1))),('prefloor',dict(spaces=(1,10**12))),('prediskerror',dict(spaces=(OSError('before'),10**12))),('postdiskerror',dict(spaces=(10**12,OSError('after')))),('monitorerror',dict(monitor_throws=True))]:
    saved,calls,error=raw_case(**kwargs);check(error is not None and len(saved)==1,'refused raw_step retained summary '+name)
    check('afterFreeBytes'in saved[0]and saved[0]['diskFloorMonitoredDuringCommand']is False,'honest actual post observation '+name)
    if name=='prefloor':check(calls==[]and saved[0]['afterFreeBytes']==10**12,'low pre-floor still observes actual post without launch')
    if name=='postdiskerror':check(saved[0]['afterFreeBytes']is None and saved[0]['diskFloorCheckedBeforeAndAfter']is False,'unavailable post-space is not claimed checked')
saved,calls,error=raw_case(writer_throws=True);check(error=='OSError'and not saved and MemPath.files,'summary writer failure refuses; available memory-stream markers not falsely complete')

# Genuine worker failure join before WORK exists; every effect is injected.
class EmptyPath(MemPath):
    def __truediv__(self,name):return EmptyPath(self.value+'/'+name)
    def is_dir(self):return False
for fail_recheck in [False,True]:
    written=[];calls=[]
    def stage_failure(f):raise ValueError('injected before WORK creation')
    def recheck_failure(f):
        calls.append('recheck')
        if fail_recheck:raise ValueError('injected source protection failure')
    def captured_save(path,value):written.append((str(path),copy.deepcopy(value)));return {'PURE_RESULT':True}
    context=dict(os=types.SimpleNamespace(umask=lambda n:None),WORK=EmptyPath('/PURE/work'),EXTERNAL=EmptyPath('/PURE/external'),
                 load_monitor=lambda f:object(),stage=stage_failure,recheck=recheck_failure,save=captured_save,print=lambda *a,**kw:None,json=json)
    extract(['worker'],context)
    f=dict(root=dict(sourceIndex=refs['sourceIndex']),config=dict(rootAuthority={'PURE_ONLY':True}))
    check(context['worker'](f)==1 and calls==['recheck'],'real worker before-WORK failure rechecks '+str(fail_recheck))
    check(written[0][0]=='/PURE/external/worker-prework-failure.json'and written[0][1]['state']=='CLOCK_IO_TOOLS_BUILD_FAILED_UNACCEPTED_V2','real worker before-WORK durable external fallback '+str(fail_recheck))
    check(written[0][1]['error']['type']=='ValueError'and written[0][1]['prunerFunctionInvokedByRefusalUnitTest']is None,'initial failure and unknown pruner invocation kept '+str(fail_recheck))
    check((written[0][1]['finalProtectionError']is not None)==fail_recheck,'distinct final-protection failure preserves primary error '+str(fail_recheck))

# Actual parent argv expression is fed through the genuine main parser with
# only authorize/parent/worker endpoints replaced; no command is launched.
parent=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='parent')
argv_expr=next(n.value for n in parent.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='argv'for t in n.targets))
expr=ast.Expression(argv_expr);ast.fix_missing_locations(expr)
fake_descriptor=dict(path='/PURE/CONFIG',sha256='0'*64,bytes=0)
argv=eval(compile(expr,'<genuine parent argv DATA>','eval'),dict(frame=frame,HERE=HERE,json=json,config_descriptor=fake_descriptor))
check(argv[:3]==[frame['context']['python']['path'],'-B','-I'],'pinned isolated actual parent argv')
for mode in ['worker','parent']:
    trace=[];fake_sys=types.SimpleNamespace(argv=[argv[3],mode,argv[-1]])
    def authorize_mock(d):trace.append(('authorize',d));return {'PURE':True}
    ctx=dict(sys=fake_sys,json=json,authorize=authorize_mock,parent=lambda f,d:(trace.append(('parent',d))or 0),worker=lambda f:(trace.append('worker')or 0),recheck=lambda f:trace.append('recheck'))
    extract(['need','main'],ctx);check(ctx['main']()==0 and trace[0]==('authorize',fake_descriptor)and trace[-1]=='recheck','genuine parent/main caller join '+mode)
    fake_sys.argv[1]='not-an-action';refuses(lambda:ctx['main'](),'unknown main command refuses '+mode)

auth=ast.get_source_segment(source,next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='authorize'))
load=ast.get_source_segment(source,next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='load_monitor'))
check('spec.loader.exec_module'not in auth and load.index('recheck(frame)')<load.index('spec.loader.exec_module'),'all custom import deferred until complete auth and recheck')
check("finally:\n        recheck(frame)"in source,'main final/failure protection')
check("families.append(value)"in auth and "family(index)"in ast.get_source_segment(source,next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='recheck')),'initial and final complete family membership')
check("EXTERNAL/'worker-prework-failure.json'"in source and "EXTERNAL/'parent-observation.json'"in source,'worker and parent durable failure locations present')
check("prunerFunctionInvokedByRefusalUnitTest=pruner_refusal_test"in source and 'adapterPrunerExecuted=False'not in source,'invalid-pruner unit invocation not mislabeled never invoked')
check(not any(isinstance(n,ast.Attribute)and isinstance(n.ctx,ast.Store)and isinstance(n.value,ast.Name)and n.value.id=='monitor'for n in ast.walk(tree)),'no monitor globals rebinding')
for p in HERE.rglob('*.py'):ast.parse(p.read_text());checks.append('Python AST '+p.relative_to(HERE).as_posix())
# Actual Source redirect handler against injected response/parent endpoints.
import urllib.request,urllib.error
from email.message import Message
redirect_env=dict(urllib=urllib)
redirect_nodes=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef))and n.name in ['RejectDownloadRedirects','download_opener']]
check(len(redirect_nodes)==2,'genuine rejecting subclass and local factory present')
exec(compile(ast.Module(body=redirect_nodes,type_ignores=[]),'<actual redirect Source only>','exec'),redirect_env)
Redirect=redirect_env['RejectDownloadRedirects']
class FakeParent:
    def __init__(self):self.calls=[]
    def open(self,*args,**kwargs):self.calls.append((args,kwargs));raise AssertionError('forbidden redirect followup')
class FakeBody:
    def __init__(self,fail=False):self.closed=False;self.fail=fail
    def close(self):
        self.closed=True
        if self.fail:raise OSError('injected response close failure')
url='https://static.crates.io/crates/windows-sys/windows-sys-0.61.2.crate'
redirect_cases=0
for code in [301,302,303,307,308]:
    for location in [url,'/same-host','https://example.invalid/other','http://example.invalid/downgrade','file:///private/not-opened','not a URL',None]:
        handler=Redirect();parent=FakeParent();handler.add_parent(parent);body=FakeBody();headers=Message()
        if location is not None:headers['Location']=location
        req=urllib.request.Request(url);req.timeout=60
        try:getattr(handler,'http_error_'+str(code))(req,body,code,'redirect',headers)
        except urllib.error.HTTPError as error:
            check(error.code==code and error.filename==url and error.fp is None,'actual reject error carries original URL/status, no body owner '+str(code)+'/'+str(location))
        else:raise AssertionError('redirect accepted')
        check(parent.calls==[] and body.closed,'no fake parent.open and response closed '+str(code)+'/'+str(location));redirect_cases+=1
    handler=Redirect();parent=FakeParent();handler.add_parent(parent);body=FakeBody(fail=True)
    try:handler.redirect_request(urllib.request.Request(url),body,code,'redirect',Message(),url)
    except urllib.error.HTTPError:check(body.closed and not parent.calls,'close failure still refuses redirect '+str(code))
    else:raise AssertionError('close failure accepted')
# Local opener can be constructed without opening a request. Assert that the
# default redirect handler is replaced, no proxy handlers are installed, and
# the global default opener is not mutated. No getproxies/open call is used.
before_opener=urllib.request._opener
client=redirect_env['download_opener']()
check(sum(isinstance(h,Redirect)for h in client.handlers)==1,'actual build_opener installs one rejecting handler')
check(not any(type(h)is urllib.request.HTTPRedirectHandler for h in client.handlers),'default following handler removed')
check(not any(isinstance(h,urllib.request.ProxyHandler)for h in client.handlers),'empty explicit proxy map installs no proxy handlers')
check(urllib.request._opener is before_opener,'local factory preserves global opener')
for code in [301,302,303,307,308]:
    body=FakeBody();headers=Message();headers['Location']=url;req=urllib.request.Request(url)
    try:client.error('http',req,body,code,'redirect',headers)
    except urllib.error.HTTPError as error:check(body.closed and error.fp is None and error.code==code,'actual local opener error dispatch refuses and closes '+str(code))
    else:raise AssertionError('local opener dispatch accepted redirect')

factory=ast.get_source_segment(source,next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='download_opener'))
check('ProxyHandler({})'in factory and not any(isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='install_opener'for n in ast.walk(ast.parse(factory))),'explicit no-proxy factory and no global installer')
check('with client.open(url, timeout=60)'in source and 'urllib.request.urlopen('not in source,'genuine stage consumes rejecting opener')
check("need(response.geturl()==url,'no unknown download redirect')"in source,'post URL assertion retained')
check('for entry in declared[\'files\']'in auth and auth.index('declared = read(row(HERE / \'source-inputs.json\'))')<auth.index("root = read(config['rootAuthority'])"),'all own declared rows authenticated before Root/action/customimport')

# Exercise the actual own-manifest intake block and exact descriptor verifier
# with injected immutable descriptor DATA. No physical input or owner import is
# performed by this model; the separate sealer hashes all real input bytes.
auth_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='authorize')
start=next(i for i,n in enumerate(auth_node.body)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='declared'for t in n.targets))
intake_nodes=auth_node.body[start:start+3]
check(isinstance(intake_nodes[2],ast.For),'actual complete own-manifest intake shape')
intake_code=compile(ast.Module(body=intake_nodes,type_ignores=[]),'<actual Source manifest intake>','exec')
original_inputs=json.loads((Path(refs['predecessorIndex']['path']).parent/'source-inputs.json').read_text())['files']
expected={r['path']:r for r in original_inputs}
manifest_row=dict(path='/PURE/own/source-inputs.json',sha256='0'*64,bytes=0)
def intake_case(manifest):
    seen=[]
    def actual_row(path):
        return copy.deepcopy(manifest_row if str(path)==manifest_row['path']else expected[str(path)])
    context=dict(Path=Path,re=re,HERE=Path('/PURE/own'),row=actual_row,read=lambda r:copy.deepcopy(manifest))
    extract(['need','verify'],context)
    def capture(r):context['verify'](r);seen.append(copy.deepcopy(r))
    context['capture']=capture
    exec(intake_code,context)
    return seen
manifest=dict(schemaVersion=1,files=copy.deepcopy(original_inputs))
check(intake_case(manifest)==original_inputs,'every5606 actual declared row reaches real descriptor verifier before action')
intake_mutations=[]
for name in ['schema','missing-last','first-sha','last-sha','bool-bytes','extra-descriptor-field','missing-sha','over-finite-cap']:
    bad=copy.deepcopy(manifest)
    if name=='schema':bad['schemaVersion']=0
    elif name=='missing-last':bad['files'].pop()
    elif name in ['first-sha','last-sha']:bad['files'][0 if name=='first-sha'else-1]['sha256']='f'*64
    elif name=='bool-bytes':bad['files'][0]['bytes']=True
    elif name=='extra-descriptor-field':bad['files'][0]['projected']=True
    elif name=='missing-sha':del bad['files'][0]['sha256']
    else:bad['files']=[copy.deepcopy(original_inputs[0])for _ in range(8193)]
    refuses(lambda:intake_case(bad),'real manifest intake refuses '+name);intake_mutations.append(name)

# The first two actual recheck loops must revisit every captured descriptor and
# every complete indexed family. Only filesystem/identity lookups are injected.
recheck_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='recheck')
recheck_code=compile(ast.Module(body=recheck_node.body[:2],type_ignores=[]),'<actual descriptor/family recheck loops>','exec')
probe_rows=copy.deepcopy(original_inputs[:2]+original_inputs[-1:])
class IdentityPath:
    state={}
    def __init__(self,value):self.value=str(value)
    def __str__(self):return self.value
    def stat(self):return types.SimpleNamespace(**self.state[self.value])
    def resolve(self):return self.value
def recheck_case(change=None):
    disk={r['path']:copy.deepcopy(r)for r in probe_rows};identities={};seen=[];families=[{'PURE_FAMILY':1},{'PURE_FAMILY':2}];family_calls=[]
    IdentityPath.state={}
    for i,r in enumerate(probe_rows):
        IdentityPath.state[r['path']]=dict(st_dev=1,st_ino=i+1,st_size=r['bytes'],st_mtime_ns=11,st_ctime_ns=12)
        identities[r['path']]=(1,i+1,r['bytes'],11,12,r['path'])
    if change=='bytes':disk[probe_rows[-1]['path']]['sha256']='f'*64
    if change=='inode':IdentityPath.state[probe_rows[-1]['path']]['st_ino']=999
    def actual_row(path):seen.append(str(path));return copy.deepcopy(disk[str(path)])
    def family_model(index):
        if change=='family':raise ValueError('injected changed complete family')
        family_calls.append(index)
    context=dict(Path=IdentityPath,re=re,row=actual_row,family=family_model,frame=dict(captured={r['path']:r for r in probe_rows},identities=identities,families=families))
    extract(['need','verify'],context);exec(recheck_code,context)
    return seen,family_calls
seen,families_seen=recheck_case()
check(seen==[r['path']for r in probe_rows]and len(families_seen)==2,'actual final loops visit all descriptors and all families')
for change in ['bytes','inode','family']:refuses(lambda:recheck_case(change),'actual final loops refuse '+change)

# Execute the genuine custom-import caller with a fake importlib endpoint only.
# A failed preimport recheck must prevent even the fake module creation.
for reject_recheck in [False,True]:
    trace=[];entry=Path('/PURE/monitor/monitor.py')
    def preimport_recheck(frame):
        trace.append('recheck')
        if reject_recheck:raise ValueError('injected full Source change')
    fake_spec=types.SimpleNamespace(loader=types.SimpleNamespace(exec_module=lambda m:trace.append('exec-module-in-memory')))
    fake_importlib=types.SimpleNamespace(util=types.SimpleNamespace(spec_from_file_location=lambda name,path:(trace.append('spec')or fake_spec),module_from_spec=lambda spec:(trace.append('module')or object())))
    context=dict(Path=Path,MONITOR=entry.parent,importlib=fake_importlib,verify=lambda r:trace.append('verify-entry'),recheck=preimport_recheck)
    extract(['need','load_monitor'],context)
    if reject_recheck:
        refuses(lambda:context['load_monitor'](dict(captured={str(entry):{'PURE':True}})),'changed full Source refuses before custom import')
        check(trace==['verify-entry','recheck'],'no fake import endpoint reached after failed protection')
    else:
        context['load_monitor'](dict(captured={str(entry):{'PURE':True}}))
        check(trace==['verify-entry','recheck','spec','module','exec-module-in-memory'],'genuine caller authenticates before only injected import')

result=dict(schemaVersion=1,state='CLOCK_IO_BUILD_CONTROLLER_PURE_DATA_CHECKS_PASSED_V2',checks=len(checks),manifestIntakeCases=9,descriptorAndFamilyRecheckCases=4,preimportProtectionCases=2,redirectCases=redirect_cases,responseCloseFailureCases=5,noProxyLocalFactoryChecks=True,checkNames=checks,cachedArchiveHeaderData=crate_data,isolatedRawStepCases=9,isolatedPreworkFailureCases=2,isolatedMainCallerCases=2,actualSourcePlanOnly=True,actualSourceCopiesPerformed=False,actualVendorExtractionPerformed=False,networkPerformed=False,monitorOrBuildToolInvoked=False,rawStepExecutedOnlyAgainstInjectedMemoryModel=True,rootAuthority=None)
(HERE/'pure-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(state=result['state'],checks=len(checks),cachedArchives=len(crate_data))))
