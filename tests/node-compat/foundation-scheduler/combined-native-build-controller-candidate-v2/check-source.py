"""Finite read/hash/AST/extracted pure regression checks. Never imports a helper/action."""
from pathlib import Path
import ast,copy,hashlib,io,json,os,re,shlex,stat
P=Path(__file__).resolve().parent;R=P.parents[3]
checks=0;pure=0

def ck(v,label):
    global checks
    assert v,label;checks+=1

def load(p):return json.loads(Path(p).read_bytes())
def hashfile(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
def good(fn,label):
    global pure
    fn();ck(True,label);pure+=1

def deny(fn,label):
    global pure
    try:fn()
    except(AssertionError,KeyError,ValueError,TypeError,OSError,UnicodeError):ck(True,label);pure+=1;return
    raise AssertionError('negative accepted: '+label)
text=(P/'controller.py').read_text();tree=ast.parse(text)
fns={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
# Execute only standard imports/literal constant assignments and explicit pure/DATA reader functions.
initial=[]
for n in tree.body:
    if isinstance(n,ast.FunctionDef):break
    if isinstance(n,ast.Expr)and isinstance(n.value,ast.Constant):continue
    initial.append(n)
scope={};exec(compile(ast.Module(body=initial,type_ignores=[]),'<controller-standard-only-literals>','exec'),scope)
names=['checked','descriptor','read','family','validate_terminal','clean_environment','require_clean_environment','root_model','stage_model','source_peer_model','controller_peer_model','cache_plan_model','build_environment','stream_copy','failure_model','probe_model','protected_tree_model','staged_inputs']
exec(compile(ast.Module(body=[fns[n]for n in names],type_ignores=[]),'<actual-extracted-pure-DATA-seams>','exec'),scope)
refs=load(P/'references.json');manifest=load(P/'source-inputs.json');snap={}
for row in manifest['files']:
    path=scope['checked'](row);st=path.stat();snap[str(path)]=(row,(st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns,st.st_ctime_ns,stat.S_IMODE(st.st_mode)))
    ck(True,'actual declared protection hash')
for row in manifest['modeRows']:ck(stat.S_IMODE(scope['checked'](row['file']).stat().st_mode)==row['mode'],'exact captured mode')
for row in refs['families']:scope['family'](row);ck(True,'complete own-context inherited family')
for key,fn in [('integrationSourceReview','source_peer_model'),('actualStageReview','stage_model'),('failedBuildReview','failure_model'),('privateRustupProbeReview','probe_model')]:
    pair=refs[key];rows=scope['family'](pair['index']);ck(sum(r==pair['result']for r in rows[1:])==1,'indexed actual proof result')
    value=load(pair['result']['path']);good(lambda value=value,fn=fn:scope[fn](value,refs)if fn!='source_peer_model'else scope[fn](value),'actual '+key+' wire')
    if key=='failedBuildReview':failure=value
    if key=='privateRustupProbeReview':probe=value
    if key=='actualStageReview':stage=value
for row in refs['protectedTreeInventories']:scope['protected_tree_model'](row);ck(True,'755-file failed-work exact membership/mode/hash')
frame=dict(stageJournal=load(refs['stageResult']['path']),copyPlan=load(refs['stageCopyPlan']['path'])['files'])
scope['staged_inputs'](frame);ck(True,'same actual1613 stage; no restage/relabel')
plan=load(P/'cache-plan.json');good(lambda:scope['cache_plan_model'](plan),'four immutable original caches in NEW work')
# Real proof negatives close role/count/phase confusion without calling operational authorize.
for key,val in [('rawCommandCount',5),('allRawExitCodesZero',False),('privateAutoSelfUpdateDisabled',False),('wasm32Wasip1Installed',False),('repeatedInstallPassed',False),('cargoProxyPassed',False),('nativeBuildAuthorityGranted',True)]:
    v=copy.deepcopy(probe);v[key]=val;deny(lambda v=v:scope['probe_model'](v,refs),'probe '+key)
for key,val in [('rawRecipeExitCode',0),('nativeBuildSucceeded',True),('cmakeGuestCompilationReached',True),('engineArtifactProduced',True),('controllerSourceIndexSha256','0'*64),('sourceAndStageInputsPreserved',False),('repeatOrResumeGranted',True)]:
    v=copy.deepcopy(failure);v[key]=val;deny(lambda v=v:scope['failure_model'](v,refs),'failure '+key)
for key,val in [('configuredSourceRoot','/old'),('nativeSourceFiles',342),('stageCopies',1424),('externalEmbeddingSourcesCopiedInStage',3),('grantsNativeBuildAuthority',True)]:
    v=copy.deepcopy(stage);v[key]=val;deny(lambda v=v:scope['stage_model'](v,refs),'stage '+key)
own=dict(path=str(P/'index.json'),sha256='a'*64,bytes=1)
root=load(P/'root-authority.template.json');deny(lambda:scope['root_model'](root,own,refs),'unissued Root closed')
root.update(state='ROOT_REVIEWED_COMBINED355_NORMAL_OFF_BUILD_RETRY_V2',phase='native-build-only',buildAllowed=True,controllerIndex=own,controllerEntry=dict(path=str(P/'controller.py'),sha256='b'*64,bytes=1),cacheSeedCopiesAllowed=True,dependencyNetworkWithinBuildAllowed=True)
good(lambda:scope['root_model'](root,own,refs),'synthetic model-only finite future Root shape')
for key,val in [('workRoot','/private/tmp/starling-node-compat/combined-native355-v1-build'),('configuredSourceRoot','/new/fake-source'),('rootEnvironmentPolicy',{}),('rootLauncherRequired',False),('oldWorkResumeAllowed',True),('persistentPrivateRustupAutoSelfUpdateDisableRequired',False),('selectedManifestCount',9),('nativeSourceFiles',342),('externalEmbeddingSources',0),('parallelBuilds',2),('externalParentDeadlineSeconds',7201),('freezeAllowed',True),('gcAllowed',True),('gcReconfigureAllowed',True),('engineExecutionAllowed',True),('operationalAdmission',True),('actualBuildResult',{})]:
    v=copy.deepcopy(root);v[key]=val;deny(lambda v=v:scope['root_model'](v,own,refs),'Root '+key)
for key in ['retryRecipe','retryHelper','retryPolicy','failedBuildReview','privateRustupProbeReview']:
    v=copy.deepcopy(root);v[key]={};deny(lambda v=v:scope['root_model'](v,own,refs),'Root exact '+key)
parent=dict(HOME='/kept',home='/lower-kept',CODEX_HOME='/also-kept',PATH='/injected',ORDINARY='kept',BASH_FUNC_rustup__='inert',NODE_OPTIONS='inert',CARGO_TARGET_DIR='/old',RUSTC_WRAPPER='/old')
parent['BASH_FUNC_cmake%%']='inert';parent.update({k:'inert'for k in scope['ENV_POLICY']['removeExactNames']});before=copy.deepcopy(parent)
child,removed=scope['clean_environment'](parent)
ck(parent==before and removed==sorted(k for k in parent if k.startswith('BASH_FUNC_')or k in scope['ENV_POLICY']['removeExactNames']),'launcher pure cleaning names only / input immutable');pure+=1
ck(all(child[k]==parent[k]for k in ['HOME','home','CODEX_HOME','ORDINARY']),'all home variables preserved');pure+=1
deny(lambda:scope['require_clean_environment'](parent),'direct dirty parent blocked before custom imports')
good(lambda:scope['require_clean_environment'](child),'clean parent accepted')
for name in ['BASH_FUNC_any%%',*scope['ENV_POLICY']['removeExactNames']]:
    dirty={**child,name:'inert'};deny(lambda dirty=dirty:scope['require_clean_environment'](dirty),'each inherited Bash seam '+name)
env=scope['build_environment'](parent,refs)
ck(all(k not in env for k in removed+['NODE_OPTIONS','CARGO_TARGET_DIR','RUSTC_WRAPPER']),'recipe cleaned too, no function/cache overrides');pure+=1
ck(all(env[k]==parent[k]for k in ['HOME','home','CODEX_HOME'])and env['RUSTUP_HOME']==str(scope['WORK']/'rustup-home')and env['CARGO_HOME']==str(scope['WORK']/'cargo-home'),'private homes, no repurpose');pure+=1
ck(all(env[k]=='1'for k in ['NODE_COMPAT_JOBS','BINARYEN_CORES','RAYON_NUM_THREADS','CARGO_BUILD_JOBS']),'single-job pools');pure+=1
for payload in [b'',b'abc',bytes(range(256))*100]:
    out=io.BytesIO();good(lambda payload=payload,out=out:ck(scope['stream_copy'](io.BytesIO(payload),out)==dict(sha256=hashlib.sha256(payload).hexdigest(),bytes=len(payload))and out.getvalue()==payload,'exact copy bytes/window'),'pure cache copy')
class Short:
    def write(self,b):return len(b)-1
deny(lambda:scope['stream_copy'](io.BytesIO(b'ab'),Short()),'short write refusal')
# Actual new shell's Python pieces are parsed, never executed as recipe/helper bodies.
recipe=(P/'build-engine.sh').read_text();blocks={m.group(1):m.group(2)for m in re.finditer(r"<<'([A-Z]+)'\n(.*?)\n\1(?:\n|$)",recipe,re.S)}
ck('PYRUSTUP'in blocks and 'PYINPUT'in blocks and 'PY'in blocks,'real shell heredoc boundaries')
for name,code in blocks.items():ast.parse(code);ck(True,'actual embedded Python AST '+name)
settings_ast=ast.parse(blocks['PYRUSTUP']);settings_fn=next(n for n in settings_ast.body if isinstance(n,ast.FunctionDef)and n.name=='validate_private_settings')
setting_scope={};exec(compile(ast.Module(body=[settings_fn],type_ignores=[]),'<genuine-preinstall-settings-guard>','exec'),setting_scope)
raw=Path(probe['settings']['path']).read_bytes();good(lambda:setting_scope['validate_private_settings'](raw),'actual probed settings accepted at real preinstall guard')
for bad in [b'',b'auto_self_update = "enable"\n',b'auto_self_update = "check-only"\n',b'auto_self_update = "disable"\nauto_self_update = "disable"\n',b'auto_self_update = "disable" #wrong\n',b'\xff', 'auto_self_update = "disable"']:
    deny(lambda bad=bad:setting_scope['validate_private_settings'](bad),'missing/wrong/duplicate/nonbytes setting refusal')
command='rustup set auto-self-update disable';install='rustup toolchain install 1.88.0 --profile minimal'
ck(recipe.count(command)==recipe.count(install)==1 and recipe.index(command)<recipe.index("<<'PYRUSTUP'")<recipe.index(install),'persistent guard before actual original install')
ck(shlex.split(command)==['rustup',*probe['commands'][0]['argv'][1:]]and shlex.split(install)==['rustup',*probe['commands'][1]['argv'][1:]],'literal command shapes match successful actual probe')
ck('digest(pathlib.Path(actual_recipe))'in recipe and "'buildRecipeSha256': digest(pathlib.Path(actual_recipe))"in recipe and 'sha256_file "$recipe_path" > "$recipe_before"'in recipe,'actual own recipe captured before+after and raw metadata')
ck('digest(pathlib.Path(repo)'not in recipe or "digest(pathlib.Path(repo)/'tests/node-compat/build-engine.sh')"not in recipe,'no old recipe provenance falsely emitted')
ck('repo_root="/private/tmp/starling-node-compat/combined-native355-v1-source"'in recipe and str(P/'build-engine.sh')in recipe,'explicit genuine source versus own recipe contexts')
policy=load(P/'policy.json');oldpolicy=load(refs['originalConfiguredPolicy']['path']);expected=copy.deepcopy(oldpolicy);expected['contexts']['workRoot']=str(scope['WORK']);expected['contexts']['freezeRoot']=str(scope['FREEZE']);ck(policy==expected,'policy ONLY two actual work/freeze contexts changed; all355+3/11 exact')
ck((P/'native-admission-model.py').read_bytes()==Path(refs['metadataModel']['path']).read_bytes(),'own pure shape model bytes')
helper=(P/'layer-policy.py').read_text();ht=ast.parse(helper)
ck("REPO=Path('/private/tmp/starling-node-compat/combined-native355-v1-source')"in helper and 'REPO=HERE.parents'not in helper and "digest(DONOR_INPUTS)==AUTH_SHA256"in helper,'own literal SOURCE; actual original donor authentication')
# Exercise genuine extracted helper readers in their NEW explicit own/staged context.
# No helper module/import/decorate/compiler API is executed.
hscope=dict(Path=Path,hashlib=hashlib,json=json,copy=copy,HERE=P,REPO=scope['SOURCE'],POLICY=policy,POLICY_SHA256=refs['policy']['sha256'],AUTH_SHA256='c837e8eb61329370775e0a24b0c914a6efe6bfcb3e51a03a8ed2ecd41fa807db',DONOR_INPUTS=scope['SOURCE']/'tests/node-compat/foundation-scheduler/combined-native-integration-candidate-v1/donor-inputs.json')
hfunctions={n.name:n for n in ht.body if isinstance(n,ast.FunctionDef)}
exec(compile(ast.Module(body=[hfunctions[n]for n in ['digest','authenticate_inputs','source_manifest','validate_sources']],type_ignores=[]),'<actual-new-helper-extracted-readers>','exec'),hscope)
good(lambda:ck(hscope['source_manifest'](scope['SOURCE'])==policy['expectedNativeSourceManifest'],'actual355 helper source data'),'genuine retry helper context reader')
for bad in [R,P,scope['WORK']]:deny(lambda bad=bad:hscope['source_manifest'](bad),'helper wrong physical configured context')
for code in [text,helper,recipe]:ck(not any(x in code for x in ['sys.modules[','.HERE=','.REPO=','.OUTPUT=','globals().update']),'no donor namespace injection/rebinding')
# Exact byte/offset forward and inverse afterimages (native files are not afterimages here).
der=load(P/'derivations.json')
for row in der['files']:
    old=Path(row['donor']['path']).read_bytes();new=(P/row['output']).read_bytes();ck(hashlib.sha256(old).hexdigest()==row['donor']['sha256'],'donor bytes')
    forward=old
    for e in reversed(row['edits']):at=e['beforeOffset'];before=e['before'].encode();ck(forward[at:at+len(before)]==before,'forward exact offset');forward=forward[:at]+e['after'].encode()+forward[at+len(before):]
    ck(forward==new,'actual afterimage forward')
    reverse=new
    for e in reversed(row['edits']):at=e['afterOffset'];after=e['after'].encode();ck(reverse[at:at+len(after)]==after,'reverse exact offset');reverse=reverse[:at]+e['before'].encode()+reverse[at+len(after):]
    ck(reverse==old,'actual donor reverse')
auth=ast.get_source_segment(text,fns['authorize']);main=ast.get_source_segment(text,fns['main']);worker=ast.get_source_segment(text,fns['worker']);par=ast.get_source_segment(text,fns['parent']);launch=ast.get_source_segment(text,fns['launcher'])
ck("manifest['files']"in auth and "manifest['modeRows']"in auth and 'recheck(frame);return frame'in auth and "protectedTreeInventories=refs['protectedTreeInventories']"in auth,'all4515/modes/old-tree contexts authenticated before custom imports')
ck('finally:recheck(frame)'in main and 'finally:recheck(frame)'in par and "'final-protection-recheck'"in worker,'complete final and failure audits retained')
ck(launch.index('clean_environment')<launch.index('os.execve')and "'parent'"in launch and "write(OBSERVER/'preentry-environment.json'"in launch,'real clean pre-entry exec seam, names only')
ck(par.index('require_clean_environment')<par.index('load_actual')and worker.index('require_clean_environment')<worker.index('load_actual'),'parent+worker reject dirty env before custom lifecycle/monitor imports')
ck("command=[refs['bash']['path'],str(checked(refs['recipe']))]"in worker,'actual own retry recipe launched, staged recipe never overwritten')
ck('monitor.monitor(argv,str(REPO)'in par and 'OUT,TIMEOUT,'in par and 'lifecycle.monitor_owned_command(command,str(SOURCE),env,log,build_free)'in worker,'genuine monitor7200 and explicit build lifecycle')
ck(worker.index('lifecycle.publish_result(')<worker.index("assert result['launcherExitCode']==0"),'raw full result before acceptance')
for key in ['WORK','FREEZE','BUILD_OUTPUT','OUT','OBSERVER']:ck(not scope[key].exists()and not scope[key].is_symlink(),'new dormant root absent '+key)
asts=[]
for p in P.glob('*.py'):ast.parse(p.read_text());asts.append(p.name);ck(True,'own Python AST '+p.name)
for name,(row,identity)in snap.items():
    path=Path(name);st=path.stat();ck(identity==(st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns,st.st_ctime_ns,stat.S_IMODE(st.st_mode)),'final identity/mode');ck(hashfile(path)==row['sha256'],'final bytes')
result=dict(schemaVersion=1,state='COMBINED355_RETRY_SOURCE_DATA_PURE_AST_CHECKS_PASSED_V2',checks=checks,pureCases=pure,inputRows=len(manifest['files']),inputLogicalBytes=sum(r['bytes']for r in manifest['files']),completeFamilies=len(refs['families']),failedWorkProtected=755,stageCopiesRechecked=1613,derivationFiles=len(der['files']),reversibleEdits=sum(len(r['edits'])for r in der['files']),pythonAstFiles=asts,recipeEmbeddedPythonBlocks=len(blocks),nativeSourceFilesChanged=0,actualProbeOnlyData=True,positiveAuthorizeOrPreflightCalled=False,ownerHelperOrActionImported=False,extractedHelperReadOnlySourceFunctionsInvoked=True,cacheCopiesExecuted=False,rustupOrBuildOrCompilerExecuted=False,lifecycleOrMonitorCalled=False,engineOrGuestExecuted=False)
(P/'source-check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
