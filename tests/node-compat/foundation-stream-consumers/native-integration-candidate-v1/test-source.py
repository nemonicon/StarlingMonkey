"""Pure source/AST/macro models + read-only original-context collection. No actions."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,re,shlex,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
PARENT=REPO/'tests/node-compat/foundation-zlib/native-integration-candidate-v4'
checks=[]
def check(name,condition=True):assert condition,name;checks.append(name)
def sha(value):return hashlib.sha256(value).hexdigest()
def read(name):return(HERE/name).read_text()
def main():
    records=json.loads(read('tool-transformations.json'))['records'];assert len(records)==8
    for row in records:
        original=Path(row['origin']).read_text();value=original
        for edit in row['edits']:assert value.count(edit['old'])==edit['count'];value=value.replace(edit['old'],edit['new'])
        assert value==read(row['path'])and sha(value.encode())==row['afterSha256']
        for edit in reversed(row['edits']):
            for at in reversed(edit['afterOffsets']):assert value[at:at+len(edit['new'])]==edit['new'];value=value[:at]+edit['old']+value[at+len(edit['new']):]
        check('exactReverse:'+row['path'],value==original)
    parent_launcher=(PARENT/'artifact-tools/build-one.py').read_text();launcher=read('artifact-tools/build-one.py')
    a=ast.parse(parent_launcher);b=ast.parse(launcher)
    original={n.name:ast.get_source_segment(parent_launcher,n)for n in a.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
    current={n.name:ast.get_source_segment(launcher,n)for n in b.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
    names=['error_record','ExternalTermination','OwnedSession','monitor_owned_command','prepare_output','publish_result','finalize_status']
    for name in names:check('unchangedLifecycle:'+name,current[name]==original[name])
    check('oneJobAndCapacityGuard',all(x in launcher for x in["'NODE_COMPAT_JOBS': '1'","'CARGO_BUILD_JOBS': '1'",'REQUIRED_START_FREE = 2 * 1024 * 1024 * 1024','MINIMUM_FREE = 800 * 1024 * 1024',"'NODE_COMPAT_ZLIB': '1'","'NODE_COMPAT_STREAM_CONSUMERS': '0' if label == 'disabled-off' else '1'"]))
    common=read('artifact-tools/artifact_common.py');tree=ast.parse(common)
    allowed={'classify','exact_release','compile_command'}
    extracted=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in allowed],type_ignores=[])
    contract=json.loads(read('admission-pins.json'));policy=json.loads(read('policy.json'))
    scope={'Path':Path,'HERE':HERE/'artifact-tools','RECIPE':contract['productionRecipeSha256'],'json':json,'shlex':shlex,'LABELS':('normal-off','normal-runtime','gc-off','disabled-off')}
    exec(compile(extracted,'<pure-copied-finite-model>','exec'),scope)
    base={'buildRecipeSha256':scope['RECIPE'],'classicStreamsEnabled':True,'zlibEnabled':True,'streamConsumersEnabled':True,'streamConsumersSourcePolicy':policy['streamConsumersSourcePolicy'],'classicTraceSourcePolicy':policy['classicTraceSourcePolicy'],'gcStress':False,'entropyPolicy':'off'}
    for name in ['profileEnabled','pathEnabled','eventsEnabled','stringDecoderEnabled','assertEnabled','querystringEnabled','utilEnabled','streamWebEnabled','internalTicksEnabled','strictInitialization','abiFixEnabled','bigIntFixEnabled']:base[name]=True
    for name in ['oomTesting','debuggerEnabled','wptSupportEnabled']:base[name]=False
    for label in scope['LABELS']:
        model=copy.deepcopy(base);model.update(gcStress=label=='gc-off',entropyPolicy='runtime-only'if label=='normal-runtime'else'off',streamConsumersEnabled=label!='disabled-off')
        check('syntheticLabel:'+label,scope['classify'](model,label)==(model['gcStress'],model['entropyPolicy']))
    for name,value in [('buildRecipeSha256','4417285083551bb48bdb877de781e31dbac08818081a78e1b28a35b9134aeed2'),('diagnosticOnly',True),('syntheticMetadataOnly',True),('streamConsumersEnabled',False),('zlibEnabled',False),('oomTesting',True),('classicStreamsEnabled',False)]:
        model=copy.deepcopy(base);model[name]=value
        try:scope['classify'](model,'normal-off')
        except AssertionError:pass
        else:raise AssertionError('Bad source model admitted: '+name)
        check('syntheticNegative:'+name)
    flags='clang --target=wasm32-wasi -O3 -DNDEBUG -DNODE_COMPAT_INTERNAL_TICKS=1 -DNODE_COMPAT_STRICT_INITIALIZATION=1 -DNODE_COMPAT_EVENTS_ADD_ABORT_LISTENER=1 -DNODE_COMPAT_ENTROPY_POLICY=1 -DNODE_COMPAT_ZLIB=1 -DNODE_COMPAT_CLASSIC_STREAMS=1 -DNODE_COMPAT_STREAM_WEB=1 -c /synthetic/builtins/node-compat/register.cpp'
    for enabled in [False,True]:
        command=flags+(' -DNODE_COMPAT_STREAM_CONSUMERS=1'if enabled else'')
        scope['compile_command'](command,False,'builtins/node-compat/register.cpp',True,False,True,enabled)
        check('syntheticPrivateConsumerMacro:'+str(enabled))
    for flag in ['-DNODE_COMPAT_STREAM_CONSUMERS=0','-DNODE_COMPAT_STREAM_CONSUMERS=1 -DNODE_COMPAT_STREAM_CONSUMERS=1','-DNODE_COMPAT_STREAM_CONSUMERS=1 -UNODE_COMPAT_STREAM_CONSUMERS','-D NODE_COMPAT_STREAM_CONSUMERS=1','-DNODE_COMPAT_STREAM_CONSUMERS=1 -DDEBUG']:
        try:scope['compile_command'](flags+' '+flag,False,'builtins/node-compat/register.cpp',True,False,True,True)
        except AssertionError:pass
        else:raise AssertionError('Bad macro model admitted')
        check('syntheticMacroNegative:'+flag)
    toolpins=json.loads(read('artifact-tools/tool-pins.json'))
    check('35562Private6AllControlModes',toolpins['nativeSources']==355 and toolpins['actualNativeCommands']=={'consumerON':62,'consumerOFF':62}and toolpins['actualClassicPrivateCommands']=={'consumerON':6,'consumerOFF':6})
    for name in ['runtime-pins.json','bootstrap-pins.json']:check('nullPins:'+name,all(v is None for v in json.loads(read(name))['variants'].values()))
    spec=importlib.util.spec_from_file_location('read_only_stage_data',HERE/'stage.py');stage=importlib.util.module_from_spec(spec);spec.loader.exec_module(stage)
    data=stage.collect() # This helper only reads original indexed/preparation/source bytes.
    check('physical355And767OriginalOrigins',data['nativeRows']==355 and data['toolRows']==767)
    check('originalPreparationContextsOnly',[r['preparationRowsReadOnlyAtOriginalRoot']for r in data['families']]==[2261,506,0,0])
    check('indexedOnlyPeerAndSdk',[r['role']for r in data['families']]==['PREPARATION','PREPARATION','INDEXED_ONLY','INDEXED_ONLY'])
    check('futureRootFivePathsNotReread',data['originalRootFivePreparationHits']==[]and all(r['originalRootFivePathReadByBuild']is False for r in data['fivePathRouting']))
    rowmap={row['path']:row for row in data['files']}
    # Finite graph for these pinned sources, not a general Python/JS parser.
    local=['tests/node-compat/module-selection.mjs','tests/node-compat/core-expectations.mjs','tests/node-compat/stream-consumers-admission.mjs','tests/node-compat/zlib-admission.mjs','tests/node-compat/private-ticks-admission.mjs','tests/node-compat/classic-streams-admission.mjs','builtins/node-compat/validate-manifest.mjs']
    for relative in local:
        source=Path(rowmap[relative]['original']).read_text()
        for specifier in re.findall(r"(?:from\s*|import\s*\()'([^']+)'",source):
            if not specifier.startswith('.'):continue
            target=str((Path(relative).parent/specifier))
            parts=[]
            for part in target.split('/'):
                if part=='..':parts.pop()
                elif part!='.':parts.append(part)
            assert '/'.join(parts)in rowmap,(relative,specifier)
    check('physicalFiniteStaticModuleImports',True)
    required=['tests/node-compat/legacy-stream-web-receipts.json','builtins/node-compat/manifest.schema.json','builtins/node-compat/export-manifest.node-v22.14.0.json','tests/node-compat/foundation-zlib/native-integration-candidate-v4/codec-evidence.py','tests/node-compat/foundation-zlib/native-integration-candidate-v4/compile-input.mjs','tests/node-compat/foundation-zlib/native-integration-candidate-v4/index.json','tests/node-compat/foundation-scheduler/integration-candidate-v1/policy.json','tests/node-compat/foundation-scheduler/integration-candidate-v1/layer-policy.py']
    for path in required:assert path in rowmap
    check('physicalSelectedAndAncestorData',True)
    for missing in [local[0],required[0],required[3]]:
        broken=dict(rowmap);broken.pop(missing)
        try:assert all(path in broken for path in local+required)
        except AssertionError:pass
        else:raise AssertionError('Incomplete physical graph admitted')
        check('missingSourceGraphNegative:'+missing)
    raw_selector=read('artifact-tools/metadata-admission.mjs')
    check('355BuildOnlyNoOperationalSelector','validateStreamConsumersBuildSourceAdmission' in raw_selector and "join(sourceRoot,'tests/node-compat/stream-consumers-admission.mjs')"in raw_selector and 'selectedManifestsForEngine'not in raw_selector)
    check('genuineParentCodecNotMissingChild',"HERE.parent/'codec-evidence.py'"not in common and "REPO/'tests/node-compat/foundation-zlib/native-integration-candidate-v4/codec-evidence.py'"in common)
    check('actualNsOrderAndFrozenMapping',all(x in common for x in["install['path']==witness['install']['path']","checked(mapping[install['path']],install['sha256'])","cache['ENABLE_BUILTIN_WEB_TEXT_CODEC']=='ON'"]))
    for path in HERE.rglob('*.py'):
        if 'history'not in path.relative_to(HERE).parts:ast.parse(path.read_bytes())
    check('pythonAstOnly',True)
    result={'schemaVersion':1,'state':'CONSUMERS355_SOURCE_AND_SYNTHETIC_MODELS_CHECKED_NOT_ADMITTED','checks':checks,'passed':len(checks),'stageCollection':{k:v for k,v in data.items()if k!='files'},'sourceRows':len(data['files']),'factoryCompilerArtifactVerifierBootstrapBundleGuestHostOrTimingExecuted':False}
    output=Path(__import__('os').environ['CONSUMERS_SOURCE_TEST_OUTPUT']);assert not output.exists()
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x')as out:json.dump(result,out,indent=2);out.write('\n')
    print(json.dumps({'state':result['state'],'passed':len(checks),'sourceRows':len(data['files']),'stageCreated':False}))
if __name__=='__main__':main()
