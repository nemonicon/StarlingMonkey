"""Finite source/data/pure checks. No producer/helper/toolchain action is imported."""
import ast,copy,hashlib,json,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
checks=0
def check(ok,label):
    global checks
    assert ok,label
    checks+=1
def load(p):return json.loads(Path(p).read_bytes())
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify(row):
    p=Path(row.get('original',row['path']))
    check(p.is_absolute()and p.is_file()and not p.is_symlink(),'regular input '+str(p))
    check(p.stat().st_size==row['bytes']and digest(p)==row['sha256'],'hash '+str(p))
def functions(text,names):
    tree=ast.parse(text)
    return ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[])
policy=load(HERE/'policy.json');native=load(HERE/'native-origins.json')['files']
tools=load(HERE/'tool-origins.json')['files'];auth=load(HERE/'donor-inputs.json')['files']
recipe=(HERE/'proposed/tests/node-compat/build-engine.sh').read_text()
helper=(HERE/'layer-policy.py').read_text()
base=load(REPO/'tests/node-compat/foundation-crypto/ownership-secret-integration-candidate-v1/policy.json')
ancestor=load(REPO/'tests/node-compat/foundation-scheduler/integration-candidate-v1/policy.json')
before={r['path']:r['sha256']for r in base['expectedNativeSourceManifest']}
after={r['path']:r['sha256']for r in native}
check(len(native)==len(after)==355 and before.keys()==after.keys(),'whole355 exact paths')
check(sum(before[p]==after[p]for p in before)==348,'exact348 retained')
changed={p for p in before if before[p]!=after[p]}
expected_changes={'builtins/web/timers.cpp','runtime/event_loop.cpp','host-apis/wasi-0.2.0/host_api.cpp','include/extension-api.h','builtins/node-compat/zlib/kernel.cpp','builtins/node-compat/zlib/factories.generated.h','builtins/node-compat/export-manifest.zlib.node-v22.14.0.json'}
check(changed==expected_changes,'seven exact changes')
for row in native:verify(row)
for row in tools:verify(row)
check(len(tools)==len({r['path']for r in tools})and len(tools)>1193,'unique tools with selector compile primitive donor')
check(not set(after)&{r['path']for r in tools},'native and tooling disjoint')
check(len(auth)==len(tools)-1 and {r['path']for r in auth}=={r['path']for r in tools if r['path']!='tests/node-compat/build-engine.sh'},'preimport donor closure')
for row in auth:
    matching=next(r for r in tools if r['path']==row['path'])
    check(all(row[k]==matching[k]for k in('path','sha256','bytes')),'auth row exact')
for row in load(HERE/'input-hashes.json')['files']:verify(row)
check(policy['expectedNativeSourceManifest']==[dict(path=r['path'],sha256=r['sha256'])for r in native],'full policy manifest')
for key in('cryptoKeyOwnershipSourcePolicy','cryptoSecretFailureSourcePolicy','streamConsumersSourcePolicy','zlibSourcePolicy'):
    check(policy[key]==base[key],'historical lineage stays exact '+key)
for path in['builtins/node-compat/register.cpp','cmake/builtins.cmake']+[r['path']for r in policy['cryptoKeyOwnershipSourcePolicy']['changes']]+[r['path']for r in policy['cryptoSecretFailureSourcePolicy']['changes']]:
    check(before[path]==after[path],'crypto/registration/CMake retained '+path)
selector=load(REPO/'tests/node-compat/foundation-scheduler/task-selection-integration-candidate-v1/policy.json')
check(len(set(after)-{r['path']for r in selector['expectedNativeSourceManifest']})==13,'thirteen355-only paths retained')
check(len(policy['expectedComponentizeSourceManifest'])==3,'external embedding three')
check(len(policy['selectedModuleManifests'])==len(policy['selectedManifestValues'])==11,'eleven complete manifests')
origin={r['path']:Path(r['original'])for r in native}
for row,value in zip(policy['selectedModuleManifests'],policy['selectedManifestValues']):
    check(digest(origin[row['path']])==row['sha256']and load(origin[row['path']])==value and row['profileVersion']==value['profileVersion'],'manifest bytes and full value '+row['path'])
check(sum(r['path'].endswith('.cpp')and r['path'].startswith(('builtins/','runtime/'))for r in native)==62,'62 policy CPP')
check(policy['admissionModelSha256']==digest(HERE/'native-admission-model.py'),'admission SHA before import')
check("POLICY_SHA256='"+digest(HERE/'policy.json')+"'"in helper,'literal policy SHA')
check("AUTH_SHA256='"+digest(HERE/'donor-inputs.json')+"'"in helper,'literal donor SHA')
check(helper.index('authenticate_inputs()\nBASE_ROOT')<helper.index('BASE=json.loads'),'authenticate before ancestor data')
check(helper.index('authenticate_inputs()\n    path=REPO')<helper.index('spec=importlib.util.spec_from_file_location'),'before codec import')
check('PARENT.'not in helper and 'sys.modules'not in helper,'no parent/global interception')
check('actual_metadata'not in helper and 'native-integration-candidate-v2/artifact-tools'not in helper,'no legacy classifier')
scope={'ANCESTOR':ancestor,'POLICY':policy,'Path':Path,'shlex':__import__('shlex')}
exec(compile(functions(helper,{'expected','resolved','_macro','_release','task_selection_commands'}),'<extracted-pure-source-functions>','exec'),scope)
selector_text=(REPO/'tests/node-compat/foundation-scheduler/task-selection-integration-candidate-v1/layer-policy.py').read_text()
check(ast.dump(functions(helper,{'task_selection_commands'}))==ast.dump(functions(selector_text,{'task_selection_commands'})),'exact donor generic selector/caller compile primitive')
for relative,entry in policy['sourceLayer'].items():
    parent=ancestor['sourceLayer'].get(relative)
    if entry['beforeSha256']is None:continue
    original=parent['beforeSha256']if parent else entry['beforeSha256']
    check(scope['expected'](relative,original)==entry['afterSha256'],'actual source-layer composition '+relative)
def refused(fn,label):
    try:fn()
    except (AssertionError,KeyError,TypeError,ValueError):check(True,label);return
    raise AssertionError('must refuse '+label)
scope['_macro'](['-DX=1'],'X',True);check(True,'macro exact positive')
scope['_macro']([],'X',False);check(True,'macro absent positive')
for words in[['-DX=0'],['-DX=1','-DX=1'],['-DX'],['-DX=1','-UX'],['-D','X=1']]:refused(lambda w=words:scope['_macro'](w,'X',True),'macro conflict')
scope['_release'](['-O3','-DNDEBUG']);check(True,'release positive')
for words in[['-O2','-DNDEBUG'],['-O3'],['-O3','-DNDEBUG','-DDEBUG=1'],['-O3','-O2','-DNDEBUG'],['-O3','-DNDEBUG','-DNODE_COMPAT_OOM_TESTING=1']]:refused(lambda w=words:scope['_release'](w),'release conflict')
selector_rows=[dict(file='/synthetic/repo/'+name,command='clang++ -O3 -DNDEBUG -DNODE_COMPAT_ENTROPY_POLICY=1 -c /synthetic/repo/'+name)for name in('host-apis/wasi-0.2.0/host_api.cpp','runtime/event_loop.cpp')]
check(len(scope['task_selection_commands'](selector_rows,'/synthetic/repo',{'entropyPolicy':'off'}))==2,'pure selector actual-path command positive')
for rows in [selector_rows[:1],selector_rows+selector_rows[:1],[dict(r,command=r['command']+' -DNODE_COMPAT_INTERNAL_TICKS=1')for r in selector_rows],[dict(r,command=r['command'].replace('-c /synthetic','-c /wrong'))for r in selector_rows]]:refused(lambda r=rows:scope['task_selection_commands'](r,'/synthetic/repo',{'entropyPolicy':'off'}),'selector caller command conflict')
# Derive requested options from the literal actual producer, not old metadata.
parts=[];lines=recipe.splitlines(True)
for i,line in enumerate(lines):
    match=re.search(r"<<'([A-Z0-9_]+)'",line)
    if match:
        label=match.group(1);j=next(j for j in range(i+1,len(lines))if lines[j].strip()==label)
        text=''.join(lines[i+1:j]);ast.parse(text);parts.append(text);check(True,'embedded Python AST '+label)
metadata_source=next(p for p in parts if '\nmetadata = {'in p)
literal_options=next(n.value for n in ast.parse(metadata_source).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='requested_cmake_options'for t in n.targets))
values=dict(build_type='Release',entropy_mode='OFF',stress='0',oom='0',**{key+'_enabled':'1'for key in['path','events','string_decoder','assert','querystring','util','stream_web','ticks','classic','zlib','consumers']})
options=eval(compile(ast.Expression(literal_options),'<literal requested options>','eval'),{},values)
check(options['CMAKE_C_COMPILER_LAUNCHER']==options['CMAKE_CXX_COMPILER_LAUNCHER']=='','launcher reuse disabled')
check(recipe.index('Fresh combined355 ABI source/build/artifact paths required')<recipe.index('mkdir -p "$source_dir/lib"'),'fresh guard before source creation')
check(recipe.index('CCACHE_DISABLE=1 SCCACHE_DISABLE=1')<recipe.index('cmake -S'),'cache disabled before configure')
check(recipe.index('codec.after(')<recipe.index('model.validate_metadata(')<recipe.index("with open(artifact + '.build.json', 'x')"),'real metadata after witness before sidecar')
check('metadata=json.loads'not in recipe and "normal-off.engine.wasm.build.json"not in recipe,'no old metadata input')
check('all eleven native selections'in recipe and '"$stress" == 0'in recipe,'fixed normalOFF selection')
check(all(not Path(p).exists()for p in policy['contexts'].values()),'no configured/work/freeze action')
# Pure model fixture is wholly synthetic: it tests rejection only and cannot
# create a sidecar, read an engine or establish compiler/runtime evidence.
model_ast=ast.parse((HERE/'native-admission-model.py').read_text())
check(all(isinstance(n,(ast.Expr,ast.FunctionDef))for n in model_ast.body),'pure model has no imports/actions')
model={};exec(compile(model_ast,'<pure synthetic model>','exec'),model)
native_commands=['synthetic-native-'+str(i)for i in range(62)]
other=['synthetic-host-api']+['synthetic-other-'+str(i)for i in range(4)]
embedding=['synthetic-embedding']
m=dict(buildRecipeSha256='recipe',sourceManifest=copy.deepcopy(policy['expectedNativeSourceManifest']),componentizeSourceManifest=copy.deepcopy(policy['expectedComponentizeSourceManifest']),entropyPolicy='off',requestedCMakeOptions=options,observedCMakeOptions=copy.deepcopy(options),selectedModuleManifests=copy.deepcopy(policy['selectedModuleManifests']),enginePath='/synthetic/engine.wasm',cmakeCachePath='/synthetic/build/CMakeCache.txt',actualEmbeddingCompileCommands=embedding)
for field in('profileEnabled','internalTicksEnabled','classicStreamsEnabled','pathEnabled','eventsEnabled','stringDecoderEnabled','assertEnabled','querystringEnabled','utilEnabled','streamWebEnabled','zlibEnabled','streamConsumersEnabled','abiFixEnabled','bigIntFixEnabled','strictInitialization'):m[field]=True
for field in('gcStress','oomTesting','debuggerEnabled','wptSupportEnabled'):m[field]=False
m.update(internalTickPolicy=dict(version=policy['version'],policyFileSha256='policy',helperSha256='helper',actualLayoutCompileCommands=native_commands),strictEventExceptionPolicy=dict(version=policy['strictPolicyVersion'],actualNativeCompileCommands=native_commands[:4]),protectedAbortListenerPolicy=dict(version=policy['protectedPolicyVersion']),classicStreamsPolicy=dict(actualPrivateTargetCompileCommands=native_commands[:6]),cryptoKeyOwnershipPolicy=copy.deepcopy(policy['cryptoKeyOwnershipSourcePolicy']),cryptoSecretFailureSourcePolicy=copy.deepcopy(policy['cryptoSecretFailureSourcePolicy']),cryptoKeyOwnershipBuildEvidence=dict(cryptoBuiltinEnabled=True,installationSource=dict(count=1),changedNativeCompileCommands=native_commands[:3]),cryptoSecretFailureBuildEvidence=dict(cryptoBuiltinEnabled=True,changedNativeCompileCommands=native_commands[:2],faultInjectionObserved=False,runtimeValidation=None))
for field,key in[('resourceOwnershipPolicy','resourceOwnershipSourcePolicy'),('taskSelectionPolicy','taskSelectionSourcePolicy'),('zlibErrorSemanticsPolicy','zlibErrorSemanticsSourcePolicy'),('combinedNativeSourcePolicy','combinedSourcePolicy')]:m[field]=dict(sourcePolicy=copy.deepcopy(policy[key]),policyFileSha256='policy',helperSha256='helper')
m['resourceOwnershipPolicy'].update(timerInstallation=dict(webTimersEnabled='ON'),nativeRuntimeValidation=None,fullResetOrReuse=False)
m['taskSelectionPolicy'].update(allNativeDependentsRequireRebuild=True,nativeAllInvalidRuntimeValidation=None,fullResetOrReuse=False,actualHostApiCompileCommands=other[:1],actualEventLoopCompileCommands=native_commands[:1])
m['zlibErrorSemanticsPolicy'].update(runtimeValidation=None,remainingDeviationsApproved=False,remainingRecordedDifferences=15)
m['zlibSelectedCodecInput']={'SYNTHETIC':'NOT_BUILD_EVIDENCE'}
m['zlibPolicy']=dict(moduleManifestSha256=policy['zlibManifestSha256'],runtimeBackendProof=dict(verified=False,version=None,vernum=None),codecWitness=dict(selectedCompileInput=copy.deepcopy(m['zlibSelectedCodecInput']),runtimeBackendProof=dict(verified=False,version=None,vernum=None),sourceInputsCheckedBeforeAndAfterBuild=True,actualKernelCompileCommands=native_commands[:1]))
m['streamConsumersPolicy']=dict(moduleManifestSha256=policy['streamConsumersSourcePolicy']['moduleManifestSha256'],installationOrder=dict(decoderBeforeNode=True))
fresh=dict(state='ACTUAL_FRESH_COMBINED355_ABI_PRECONFIGURE_PATH_OBSERVATION_V1',configuredSourceRoot=policy['contexts']['configuredSourceRoot'],workRoot=policy['contexts']['workRoot'],sourceDir='/synthetic/external',buildDir='/synthetic/build',artifact='/synthetic/engine.wasm',sourceDirExisted=False,buildDirExisted=False,artifactExisted=False,compilerLauncherReuseAllowed=False,rustIncrementalReuseAllowed=False)
m['combinedNativeSourcePolicy'].update(configuredSourceRoot=policy['contexts']['configuredSourceRoot'],workRoot=policy['contexts']['workRoot'],externalConfiguredSourceRoot='/synthetic/external',selectedManifests=copy.deepcopy(policy['selectedManifestValues']),sourceManifestCheckedBeforeAndAfterBuild=True,actualCompileDatabaseRows=68,actualPolicyCppCompileCommands=native_commands,actualOtherConfiguredCompileCommands=other,actualGeneratedNullCompileCommands=['synthetic-null'],actualSeparateEmbeddingCompileCommands=embedding,privateBackendEvidenceHookEnabled=False,freshAbiEvidence=fresh,runtimeValidation=None,operationalAdmission=False)
def validate(value):return model['validate_metadata'](value,policy,'policy','helper','recipe',policy['expectedComponentizeSourceManifest'],'normal-off')
check(validate(m)==dict(state='FINITE_COMBINED355_NORMAL_OFF_METADATA_SHAPE_ONLY_V1',nativeFiles=355,engineRead=False,runtimeAccepted=False,grantsAuthority=False),'pure synthetic positive')
mutations=[]
for path,value in[(('gcStress',),True),(('entropyPolicy',),'runtime-only'),(('buildRecipeSha256',),'old'),(('sourceManifest',),m['sourceManifest'][:-1]),(('componentizeSourceManifest',),[]),(('zlibPolicy','runtimeBackendProof','verified'),True),(('taskSelectionPolicy','sourcePolicy'),{}),(('combinedNativeSourcePolicy','actualCompileDatabaseRows'),67),(('combinedNativeSourcePolicy','actualPolicyCppCompileCommands'),native_commands[:-1]),(('combinedNativeSourcePolicy','actualOtherConfiguredCompileCommands'),other[:-1]),(('combinedNativeSourcePolicy','freshAbiEvidence','buildDirExisted'),True),(('combinedNativeSourcePolicy','freshAbiEvidence','sourceDir'),'/wrong'),(('combinedNativeSourcePolicy','selectedManifests'),[]),(('combinedNativeSourcePolicy','privateBackendEvidenceHookEnabled'),True),(('zlibErrorSemanticsPolicy','remainingDeviationsApproved'),True),(('cryptoKeyOwnershipBuildEvidence','installationSource','count'),0),(('classicStreamsPolicy','actualPrivateTargetCompileCommands'),native_commands[:5]),(('strictEventExceptionPolicy','actualNativeCompileCommands'),native_commands[:3]),(('taskSelectionPolicy','actualHostApiCompileCommands'),['wrong']),(('internalTickPolicy','actualLayoutCompileCommands'),['wrong']),(('observedCMakeOptions','CMAKE_CXX_COMPILER_LAUNCHER'),'ccache'),(('observedCMakeOptions','ENABLE_BUILTIN_WEB_TIMERS'),'OFF'),(('selectedModuleManifests',),m['selectedModuleManifests'][:-1]),(('syntheticMetadataOnly',),True),(('diagnosticOnly',),True)]:
    value_m=copy.deepcopy(m);target=value_m
    for key in path[:-1]:target=target[key]
    target[path[-1]]=value
    refused(lambda q=value_m:validate(q),'metadata counterexample '+'.'.join(path));mutations.append('.'.join(path))
for row in load(HERE/'exact-derivations.json')['files']:
    source=Path(row['before']['path']).read_text();target=Path(row['after']['path']).read_text();forward=source;inverse=target
    for e in reversed(row['edits']):
        i=e['beforeOffset'];check(forward[i:i+len(e['before'])]==e['before'],'forward delta preimage');forward=forward[:i]+e['after']+forward[i+len(e['before']):]
    for e in reversed(row['edits']):
        i=e['afterOffset'];check(inverse[i:i+len(e['after'])]==e['after'],'inverse delta preimage');inverse=inverse[:i]+e['before']+inverse[i+len(e['after']):]
    check(forward==target and inverse==source,'whole tooling forward and inverse '+row['after']['path'])
for p in sorted(HERE.glob('*.py')):
    if p.name=='helper-prefix.template.py':continue
    ast.parse(p.read_text());check(True,'Python AST '+p.name)
syntax=subprocess.run(['/bin/bash','-n',str(HERE/'proposed/tests/node-compat/build-engine.sh')],capture_output=True)
check(syntax.returncode==0 and syntax.stdout==syntax.stderr==b'','Bash parse-only')
checked_sources=[dict(path=str(p.absolute()),sha256=digest(p),bytes=p.stat().st_size)for p in[HERE/n for n in('policy.json','layer-policy.py','native-admission-model.py','prepare.py','helper-prefix.template.py','check-source.py','exact-derivations.json','donor-inputs.json','native-origins.json','tool-origins.json','stage-input-plan.json','proposed/tests/node-compat/build-engine.sh')]]
result=dict(schemaVersion=1,state='COMBINED355_SOURCE_DATA_PURE_AND_GRAMMAR_CHECKS_PASSED',checks=checks,checkedSources=checked_sources,nativeFiles=355,retainedNativeFiles=348,changedNativeFiles=7,toolRows=len(tools),donorAuthenticationRows=len(auth),selectedManifestCount=11,policyCppCount=62,expectedCompileDatabaseRows=68,expectedStrictCommands=4,expectedPrivateCommands=6,expectedExternalEmbeddingCommands=1,syntheticModelOnly=True,syntheticMetadataCounterexamples=mutations,bashParseOnly=dict(argv=syntax.args,exitCode=syntax.returncode,stdoutBytes=0,stderrBytes=0),embeddedPythonAstCount=len(parts),producerExecuted=False,ownerHelperImported=False,compilerInvoked=False,engineExecuted=False,guestExecuted=False,stageCreated=False,metadataProduced=False)
(HERE/'source-check-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
