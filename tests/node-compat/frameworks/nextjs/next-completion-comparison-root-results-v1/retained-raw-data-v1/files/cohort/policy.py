"""Fixed cohort Root policy. Import is inert; original guards load only after binding."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import re
import shutil
import stat
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
REPO = HERE.parents[4]
PLAN_SHA = '5613cd968b0a86c79abe5a6cc2ca3a3cec2047786a49736963390ee570d334bf'
ACTOR_REFS = {'a': {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-completion-a-runtime-candidate-v1/index.json', 'sha256': '9736914fd8dc9413a018b007e166b723e12476be4906fa403110022eba751d64', 'bytes': 4414}, 'b': {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-completion-b-runtime-candidate-v1/index.json', 'sha256': '3a00ff3a75535939efd4d4e667e59ea69653e76a3faeb4041ca62ac002b4e3d7', 'bytes': 4528}, 'c': {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-completion-c-runtime-candidate-v1/index.json', 'sha256': '98cfe8692f5d7f935412e655c30e2d8cf347203a1c14b1b90346e43b3462cdb7', 'bytes': 4392}, 'd': {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-completion-d-runtime-candidate-v1/index.json', 'sha256': 'cd38d1dcca9375af8b90ebd59e6143b94b6eb5a999d4ef77593fb4f7b3ed670f', 'bytes': 4528}}
NEW_REVIEW_REFS = {'b': {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-completion-await-b-construction-root-results-v1/actual-construction-review.json', 'sha256': 'b35640a94a77f12ca8db7c07f49d085362a3eac1a89eb93c484e36caa6ba3df6', 'bytes': 35702}, 'd': {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-completion-await-d-construction-root-results-v1/actual-construction-review.json', 'sha256': '94cbfa54533811b00d7376a3bf063d39a3ba4d2217dec3338d085b9767f376e8', 'bytes': 36438}}
PYTHON = dict(path='/opt/homebrew/Cellar/python@3.11/3.11.10/Frameworks/Python.framework/Versions/3.11/bin/python3.11', sha256='b76df9b72b06c2592c34e234c10fb51a587fa4aaf3d57fd98325ea2774f4f758', bytes=52640)
FULL_GUARD = dict(path=str(BASE/'next-full-build-runtime-root-results-v1/run-full-native-requests.py'), sha256='47c9cab9461a63aa12b38e6f4e8cae3cc714270c370a313fab571f53991cdfe0', bytes=14500)
WORLD_GUARD = dict(path=str(BASE/'peer-disconnect-root-results-v3/launch-peer-v3-construction.py'), sha256='b7a15f315cde9f87d511eaf2cb0c315853bf343965e825b78abddfb68be82921', bytes=4683)
MONITOR = dict(path=str(BASE.parents[1]/'foundation-crypto/ownership-gc-build-controller-candidate-v1/monitor.py'), sha256='86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe', bytes=15094)
APP_REVIEW = dict(path=str(BASE/'next-portable-cache-app-build-root-results-v1/actual-build-review-v2.json'), sha256='163133f1db2d8957bfeb871a26de3c5b3f588ef303c18ae27336120ee19941e2', bytes=7841)
VM_REVIEW = dict(path=str(BASE/'next-portable-cache-stock-v2-root-results-v1/actual-vm-seam-review.json'), sha256='0ac120ab1d043644ee941bf9300ac2e39c21c52145d35975c7082b81c75dc782', bytes=6417)
VM_RESULT = dict(path='/private/tmp/starling-node-compat/next-portable-cache-vm-seam-v2-first/result.json', sha256='b75a4064bd8138cfc83d0cee2c6f513507fbbd80a8118909b9475305e34b4f7d', bytes=2763)
OLD_REVIEW_REFS = {
 'a': dict(path=str(BASE/'next-fetch-resource-cleanup-next-construction-root-results-v1/actual-construction-review.json'), sha256='9256cdd520f28a1b56b04d6bc1884bd075f4c727e6d9fc8c725fec2518cab47b', bytes=21217),
 'c': dict(path=str(BASE/'next-guest-completion-construction-root-results-v1/actual-construction-review.json'), sha256='ee7511ace711a08cf72c6fd4ab0c9ede88e6a621d56851a04b1143fd5dea0a3a', bytes=29645)}
COMMON_FALSE = ('ordinaryExportsInvoked','httpServed','appMountedAtInit','filesystemFixtureMountedAtInit','deployedFetchProbeInvoked','deployedImportOrFilesystemProbeInvoked','runtimeAccepted','nodeParityProved','productionProfilePromoted')
ROOT_FILES = ('policy.py','prepare-cohort.py','run-native-trial.py','run-cohort.py','launch-cohort.py')

def require(value, message):
    if not value: raise ValueError(message)

def descriptor(value):
    return isinstance(value,dict) and set(value)=={'path','sha256','bytes'} and isinstance(value['path'],str) and isinstance(value['sha256'],str) and re.fullmatch('[a-f0-9]{64}',value['sha256']) is not None and type(value['bytes']) is int and value['bytes']>=0

def require_bound():
    require(all(descriptor(ACTOR_REFS[k]) for k in 'abcd') and all(descriptor(NEW_REVIEW_REFS[k]) for k in 'bd'), 'Unbound Root Source; all four genuine actor indices and both new reviews must bind before any guard/output/action')

def stamp(p):
    s=p.lstat(); return(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)

def row(path):
    path=Path(path); before=stamp(path)
    require(path.is_absolute() and path.resolve()==path and stat.S_ISREG(before[2]) and before[3]==1,'Canonical unique regular input required')
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(4*1024*1024),b''): h.update(chunk)
    require(stamp(path)==before,'Input changed during hashing')
    return dict(path=str(path),sha256=h.hexdigest(),bytes=before[4])

def verify(ref):
    require(descriptor(ref) and row(ref['path'])==ref,'Exact descriptor required')

def read(path):
    path=Path(path); before=stamp(path)
    require(before[4]<=64*1024*1024 and path.resolve()==path and stat.S_ISREG(before[2]) and before[3]==1,'Bounded JSON input')
    value=json.loads(path.read_bytes()); require(stamp(path)==before,'JSON read bookend'); return value

def read_ref(ref):
    verify(ref); return read(ref['path'])

def family(ref):
    index=read_ref(ref); root=Path(ref['path']).parent; names={'index.json'}; dirs=set()
    for item in index['files']:
        rel=Path(item['path']); require(not rel.is_absolute() and '..' not in rel.parts and rel.as_posix()==item['path'] and item['path'] not in names,'Safe family member')
        names.add(item['path']); dirs.update(x.as_posix() for x in rel.parents if x!=Path('.'))
        verify(dict(item,path=str(root/rel)))
    nodes=list(root.rglob('*')); require(not any(p.is_symlink() for p in nodes),'No family symlink')
    require({p.relative_to(root).as_posix() for p in nodes if p.is_file()}==names and {p.relative_to(root).as_posix() for p in nodes if p.is_dir()}==dirs,'Exact family namespace')

def load_original(name, ref):
    verify(ref); spec=importlib.util.spec_from_file_location(name,ref['path']); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

def originals():
    require_bound()
    require(__debug__ and sys.flags.isolated and sys.dont_write_bytecode and row(Path(sys.executable).resolve())==PYTHON,'Pinned isolated Root Python')
    return load_original('original_completion_comparison_native_guard',FULL_GUARD),load_original('original_completion_comparison_world_guard',WORLD_GUARD)

def load_plan():
    require(row(HERE/'plan.json')['sha256']==PLAN_SHA,'Original fixed plan changed')
    plan=read(HERE/'plan.json'); require([x['arm'] for x in plan['trials']]==['stock','a','b','c','d','stock','d','c','b','a'] and [x['sequence'] for x in plan['trials']]==list(range(1,11)),'Fixed ten-trial order')
    require(len({x['runId'] for x in plan['trials']})==10 and len({x['outputRoot'] for x in plan['trials']})==10,'Ten distinct namespaces')
    return plan

def actor_path(arm):
    require(arm in 'abcd' and len(arm)==1,'Native arm')
    return BASE/('next-completion-'+arm+'-runtime-candidate-v1')

def review_ref(arm):
    return OLD_REVIEW_REFS[arm] if arm in OLD_REVIEW_REFS else NEW_REVIEW_REFS[arm]

def schema_policy(arm, review):
    """Pure, explicit schema policy; never mutates or fills an old review."""
    states={'a':'COORDINATED_REAL_NEXT_INTEROP_COMPONENT_INIT_DATA_REVIEW_PASSED_V1','c':'COORDINATED_GUEST_PUBLIC_COMPLETION_COMPONENT_INIT_DATA_REVIEW_PASSED_V1','b':'COORDINATED_NEXT_AWAIT_VARIANT_COMPONENT_INIT_DATA_REVIEW_PASSED_V1','d':'COORDINATED_NEXT_AWAIT_VARIANT_COMPONENT_INIT_DATA_REVIEW_PASSED_V1'}
    require(review['state']==states[arm] and review['verifiedPassed'] is True and review['completeReturnedImportAuditVerified'] is True,'Genuine coordinated review state/audit')
    require(all(review[k] is False for k in COMMON_FALSE),'Published common INIT-only flags')
    owner_key='complementaryOwnerWorldReview' if arm=='a' else 'actualOwnerWorldReview'
    require(descriptor(review[owner_key]),'Genuine schema-specific owner reference')
    if arm=='a': require('deployedCompletionDiagnosticObserved' not in review,'Pinned legacy A field must remain absent')
    else: require(review['deployedCompletionDiagnosticObserved'] is False,'Published diagnostic scope flag')
    if arm in 'bd': require(review['variant']==arm.upper(),'Actual review variant')
    return dict(arm=arm,reviewState=states[arm],ownerReviewKey=owner_key,ownerReview=review[owner_key],diagnosticFieldPolicy='genuinely-absent-in-pinned-A' if arm=='a' else 'published-false',reviewRewritten=False)

def trial_for_authority(a, path):
    plan=load_plan(); found=[t for t in plan['trials'] if t['runId']==a['runId']]
    require(len(found)==1,'Declared runId'); t=found[0]
    require(a['comparisonArm']==t['arm'] and a['comparisonSequence']==t['sequence'] and a['comparisonPlan']==row(HERE/'plan.json') and str(Path(path).resolve())==t['authorityPath'],'Exact fixed trial authority context')
    return t

def capacity():
    free=shutil.disk_usage('/private/tmp').free; require(free>=1073741824,'At least1GiB required immediately before each action'); return free

def source_proofs(): return [row(HERE/name) for name in ROOT_FILES]+[row(HERE/'plan.json')]

def verify_proofs(proofs):
    require({r['path'] for r in proofs}=={str(HERE/name) for name in ROOT_FILES}|{str(HERE/'plan.json')},'Whole Root driver proof roles')
    for ref in proofs: verify(ref)

def fresh(trial):
    for name in ['outputRoot','ownerOutputRoot','authorityPath']:
        p=Path(trial[name]); require(not p.exists() and not p.is_symlink(),'Declared namespace already present: '+str(p))
    if trial['arm']!='stock':
        p=HERE/(trial['runId']+'-full-world-guard.json'); require(not p.exists() and not p.is_symlink(),'World receipt already present')

def write_new(path,value):
    data=(json.dumps(value,indent=2)+'\n').encode()
    with Path(path).open('xb') as f: os.fchmod(f.fileno(),0o600); f.write(data); f.flush(); os.fsync(f.fileno())

def clean_owner(t):
    return type(t.get('rawExitCode')) is int and t['rawExitCode'] in (0,1) and t.get('timeout') is False and t.get('forcedCleanup') is False and t.get('parentOwnedGroupGone') is True and t.get('allObservedOwnedGroupsGone') is True and all(t.get(k)==[] for k in ['errors','signals','interruptedSignals','remainingObservedPids']) and all(x.get('alive') is False and x.get('signalAllowed') is False for x in t.get('finalGroups',[]))

def classify_published(arm, terminal, observation, result, client):
    """Pure continuation policy, not a validator or a pass conversion."""
    reasons=[]
    if not clean_owner(terminal): reasons.append('unsafe-original-owner')
    if not isinstance(observation,dict) or observation.get('ownedGroupsClean') is not True or observation.get('protectedInputsPreserved') is not True: reasons.append('protection-or-observation-invalid')
    if not isinstance(result,dict) or not isinstance(client,dict): return dict(valid=False,reasons=reasons+['missing-final-result'],originalAllPassed=False)
    if type(result.get('passed')) is not bool: reasons.append('missing-original-pass-predicate')
    if arm=='stock':
        if result.get('originalApplicationInputsPreserved') is not True or result.get('prepared') is not True: reasons.append('stock-preparation-or-preservation-invalid')
    else:
        if result.get('originalInputsPreserved') is not True or result.get('readonlyAppPreserved') is not True: reasons.append('native-preservation-invalid')
        server=result.get('server') or {}; cap=server.get('stdoutCapture') or {}
        if server.get('exit')!={'code':0,'signal':None,'error':None} or server.get('forcedCleanup') is not False: reasons.append('native-server-not-cleanly-reaped')
        if not (cap.get('state')=='RAW_STDOUT_CAPTURE_FINALIZED_COMPLETE_V1' and cap.get('limitBytes')==8388608 and all(cap.get(k) is True for k in ['complete','pipeEof','fileClosed','fileBoundVerified','finalized']) and all(cap.get(k) is False for k in ['overflow','partialWritePossible','unretainedBytesUnknown']) and cap.get('errors')==[] and type(cap.get('fileBytes')) is int and 0<=cap['fileBytes']<=8388608 and cap.get('completeWriteBytes')==cap.get('lastReservedWriteCeiling')==cap['fileBytes']): reasons.append('native-capture-incomplete')
        if (result.get('client') or {}).get('exit') not in ({'code':0,'signal':None,'error':None},{'code':1,'signal':None,'error':None}): reasons.append('native-client-not-natural')
    browser=client.get('browser') or {}; net=browser.get('netlog') or {}
    if client.get('browserExit') not in ({'code':0,'signal':None},{'code':1,'signal':None}): reasons.append('browser-not-naturally-reaped')
    if not (isinstance(client.get('http'),list) and len(client['http'])==24 and isinstance(client.get('portableCache'),dict) and len(client['portableCache'].get('records',[]))==5 and isinstance(client.get('portableCacheValidation'),dict) and isinstance(client.get('supplemental'),dict) and len(client['supplemental'].get('observations',[]))==6 and isinstance(client.get('supplementalValidation'),dict) and isinstance(client.get('streaming'),dict) and isinstance(client.get('cacheInvalidation'),dict) and isinstance(browser.get('tests'),list) and len(browser['tests'])==2): reasons.append('incomplete-profile-publication')
    if not (browser.get('browserClosed') is True and net.get('completeJson') is True and net.get('fsynced') is True and net.get('errors')==[] and descriptor(net.get('file')) and net['file']['bytes']<=20971520): reasons.append('required-browser-netlog-publication-invalid')
    # Recorded case deadlines, bounded partial-body errors and semantic false
    # validations are outcomes, not new infrastructure gates.
    return dict(valid=not reasons,reasons=reasons,originalAllPassed=bool(terminal.get('rawExitCode')==0 and observation.get('hostExperimentPassed' if arm=='stock' else 'passed') is True and result.get('passed') is True),rawExitCode=terminal.get('rawExitCode'))


def native_admission(a, plan, native, world):
    """Current full-suite authority, actual constructor roles and genuine world; no actor here."""
    arm=a['comparisonArm']; actor=actor_path(arm)
    assert a['constructionDataReview']==review_ref(arm)
    assert a['state'] == 'ROOT_NEXT_WASMTIME_DEPLOYMENT_AUTHORIZED_V2' and a['unissued'] is False
    assert a['sourceIndex'] == ACTOR_REFS[arm] == row(actor / 'index.json') and a['plan'] == row(actor / 'plan.json')
    assert a['wrapperPython'] == PYTHON and a['fullNativeGuardImplementation'] == FULL_GUARD
    assert a['worldGuardImplementation'] == WORLD_GUARD
    template = read(actor / 'root-authority-template.json')
    for key in ['localhostServeAllowed', 'actualNextGuestAllowed', 'browserAllowed']:
        assert a[key] is True and template[key] is None
    for key in ['compilerAllowed', 'componentConstructionAllowed', 'externalDeploymentAllowed', 'adoptionAllowed']:
        assert a[key] is template[key] is False
    assert re.fullmatch('[a-z0-9][a-z0-9-]{0,47}', a['runId'])
    native.family(a['sourceIndex']); native.family(a['constructionCallerIndex']); native.family(a['inputSourceIndex'])
    for key, expected in [('component', plan['expectedComponent']), ('engine', plan['expectedEngine']),
                          ('nativeMetadata', plan['expectedNativeMetadata'])]:
        verify(a[key]); assert all(a[key][name] == expected[name] for name in ['sha256', 'bytes'])
    assert a['engine'] == plan['expectedEngine'] and a['nativeMetadata'] == plan['expectedNativeMetadata']
    assert plan['stdoutCapturePolicy']['maxGlobalRawBytes'] == 8388608
    assert plan['wasmtimePolicy']['noLoggingPrefix'] is True
    assert plan['browserSource']['sha256'] == 'f19d6c42ea44897ed026ba437657a9749396ee138301e5abbfaa17eb508c7ffa'
    assert plan['outputPrefix'] == '/private/tmp/starling-node-compat/next-wasmtime-deployment'
    for key in ['node', 'monitor', 'wasmtime']:
        verify(plan[key])
    verify(PYTHON); verify(FULL_GUARD); verify(WORLD_GUARD)
    for ref in plan['protectedInputs'] + a['engineBuildEvidence'] + a['nativeProtectedInputs']:
        verify(ref)
    for ref in a['nativeSourceFamilies']:
        native.family(ref)
    policy = plan['requiredExternalRootAdmission']
    assert a['constructionDataReview'] == policy['constructionReview']
    assert a['fullNativeBuildReview'] == policy['fullNativeBuildReview']
    assert a['applicationBuildDataReview'] == policy['applicationBuildReview']
    assert a['applicationRootIdentityEvidence'] == policy['applicationRootIdentity']
    c = read(a['constructionResult']['path']); review = read(a['constructionDataReview']['path'])
    root_policy=schema_policy(arm,review)
    assert a['reviewPolicy']==root_policy
    selection=plan['comparisonArm']
    assert selection['arm']==arm.upper() and selection['ownerReviewKey']==root_policy['ownerReviewKey'] and selection['ownerReview']==root_policy['ownerReview']
    assert selection['constructionReview']==a['constructionDataReview'] and selection['constructionReviewState']==review['state']
    assert review['verifiedPassed'] is review['completeReturnedImportAuditVerified'] is True
    assert c['passed'] is True and c['error'] is None and c['finalProtection']['unchanged'] is True
    assert c['entryMode'] == review['entryMode'] == 'real-next'
    for key in ['ordinaryExportsInvoked', 'httpServed', 'appMountedAtInit', 'productionProfilePromoted']:
        assert c[key] is False
    for key in ['ordinaryExportsInvoked', 'httpServed', 'appMountedAtInit', 'filesystemFixtureMountedAtInit',
                'deployedFetchProbeInvoked', 'deployedImportOrFilesystemProbeInvoked', 'runtimeAccepted',
                'nodeParityProved', 'productionProfilePromoted']:
        assert review[key] is False
    assert review['actualResult'] == a['constructionResult']
    assert review['callerIndex'] == c['callerIndex'] == a['constructionCallerIndex']
    assert review['rootAuthority'] == c['rootAuthority'] and review['plan'] == c['plan']
    assert review['fullBuildReview'] == a['fullNativeBuildReview']
    for key in ['component', 'componentAudit', 'engine', 'nativeMetadata', 'inputEntry', 'inputSourceIndex']:
        assert review[key] == c['artifacts'][key] == a[key]
    verify(c['rootAuthority']); verify(c['plan'])
    ctor = read(c['rootAuthority']['path']); ctor_plan = read(c['plan']['path'])
    assert ctor['state'] == 'ROOT_NEXT_NATIVE_COMPONENT_CONSTRUCTION_V2' and ctor['entryMode'] == 'real-next'
    assert ctor['callerIndex'] == a['constructionCallerIndex']
    assert ctor_plan['inputSourceIndex'] == a['inputSourceIndex'] and ctor_plan['entries']['real-next'] == a['inputEntry']
    if arm in 'bd':
        fixture=read(Path(a['inputSourceIndex']['path']).with_name('plan.json'))
        assert ctor_plan['variant']==arm.upper() and fixture['entries'][arm.upper()]==fixture['variants'][arm.upper()]['entry']==a['inputEntry']
    assert len(ctor['metadataExpectedFixedValues']) == 31 and len(ctor['engineBuildEvidence']) == 39
    assert len(ctor['newSourceEvidence']) == 18
    assert ctor['componentizeInitAllowed'] is True
    for key in ['ordinaryExportsAllowed', 'httpServingAllowed', 'networkAllowed', 'nativeBuildAllowed',
                'packageMutationAllowed', 'globalPinMutationAllowed', 'debugAllowed',
                'applicationMountAtInitAllowed', 'deployedResnapshotAllowed']:
        assert ctor[key] is False
    for key in ['engine', 'nativeMetadata', 'metadataExpectedFixedValues', 'engineBuildEvidence']:
        assert ctor[key] == a[key]
    assert c['artifacts']['engineBuildEvidence'] == a['engineBuildEvidence']
    metadata = read(a['nativeMetadata']['path'])
    assert metadata['engine'] == a['engine'] and metadata['metadataKind'] == 'EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_ACTUAL_V1'
    for key, value in a['metadataExpectedFixedValues'].items():
        assert metadata[key] == value, key
    native.protect_full_build(a, metadata)
    outer = read(a['constructionOuterTerminal']['path'])
    assert native.clean(outer) and outer['authority'] == c['rootAuthority']
    for key in ['stdout', 'stderr']:
        verify(outer[key])
    assert [item['label'] for item in c['commands']] == ['componentize-init', 'component-validate', 'component-wit']
    for command in c['commands']:
        verify(command['terminal']); terminal = read(command['terminal']['path'])
        assert native.clean(terminal) and terminal['authority'] == c['rootAuthority']
        assert command['rawExitCode'] == 0 and command['clean'] is True
        for key in ['stdout', 'stderr']:
            assert terminal[key] == command[key]; verify(command[key])
    app_review = read(a['applicationBuildDataReview']['path'])
    assert app_review['state'] == 'PORTABLE_CACHE_APP_HOST_BUILD_DATA_REVIEW_PASSED_V1' and app_review['verifiedPassed'] is True
    assert app_review['actualResult'] == plan['applicationBuildResult']
    assert app_review['sourceFiles'] == 31 and app_review['unchangedParentFiles'] == 28
    assert a['applicationInputs'] == plan['applicationInputs'] and a['applicationSource'] == plan['applicationSource']
    root_identity = read(a['applicationRootIdentityEvidence']['path'])
    assert root_identity['inventory'] == a['applicationInputs']
    assert {k:root_identity['rootIdentity'][k] for k in ['dev', 'ino', 'mode', 'nlink']} == plan['applicationRootIdentity']
    assert root_identity['rootIdentity']['path'] == a['applicationSource']
    assert a['worldSourceIndex'] == ctor['worldSourceIndex'] == plan['worldFamily']['sourceIndex']
    assert a['constructionDataReview'] == plan['acceptedConstructionReview']
    assert a['inputEntry'] == plan['comparisonArm']['inputEntry']
    assert a['inputSourceIndex'] == plan['comparisonArm']['inputSourceIndex']
    assert a['worldInputs'] == [ref for ref in ctor['newSourceEvidence'] if ref['path'].endswith('.wit')]
    world_authority = dict(callerIndex=a['constructionCallerIndex'], newSourceEvidence=ctor['newSourceEvidence'],
                           worldSourceIndex=a['worldSourceIndex'])
    current = world.world_guard(world_authority)
    saved = read(a['constructionWorldGuard']['path'])
    assert saved['unchanged'] is True and saved['before'] == saved['after'] == current
    return current



def assemble_native(trial, native, world):
    arm=trial['arm']; actor=actor_path(arm)
    assert row(actor/'index.json')==ACTOR_REFS[arm]
    native.family(ACTOR_REFS[arm]); actor_plan=read(actor/'plan.json')
    assert actor_plan['prospectiveActualBindingsPending'] is False
    ctor_review_ref=review_ref(arm); ctor_review=read_ref(ctor_review_ref)
    root_policy=schema_policy(arm,ctor_review)
    assert actor_plan['acceptedConstructionReview']==ctor_review_ref
    construction_ref=ctor_review['actualResult']; construction=read_ref(construction_ref)
    ctor_path=Path(ctor_review['rootAuthority']['path']); ctor_dir=Path(ctor_review_ref['path']).parent
    constructor=read_ref(ctor_review['rootAuthority'])
    root=Path(construction_ref['path']).parent
    assert construction['passed'] is True and construction['error'] is None and construction['finalProtection']['unchanged'] is True
    for key in ['callerIndex','plan','rootAuthority']: assert ctor_review[key]==construction[key]
    for key in ['component','componentAudit','engine','nativeMetadata','inputSourceIndex','inputEntry']: assert ctor_review[key]==construction['artifacts'][key]
    assert len(constructor['metadataExpectedFixedValues'])==31 and len(constructor['engineBuildEvidence'])==39 and len(constructor['newSourceEvidence'])==18
    app_dir = BASE / 'next-portable-cache-app-build-root-results-v1'
    app_review_ref = row(app_dir / 'actual-build-review-v2.json')
    assert app_review_ref['sha256'] == '163133f1db2d8957bfeb871a26de3c5b3f588ef303c18ae27336120ee19941e2'
    app_review = read(app_review_ref['path'])
    assert app_review['verifiedPassed'] is True
    assert app_review['state'] == 'PORTABLE_CACHE_APP_HOST_BUILD_DATA_REVIEW_PASSED_V1'
    assert app_review['sourceFiles'] == 31 and app_review['unchangedParentFiles'] == 28
    assert actor_plan['applicationBuildReview'] == app_review_ref
    assert actor_plan['applicationBuildResult'] == app_review['actualResult']
    assert actor_plan['applicationInputs'] == row(Path(actor_plan['applicationInputs']['path']))
    component = construction['artifacts']['component']
    assert component == ctor_review['component'] == row(Path(component['path']))
    assert actor_plan['expectedComponent'] == {key: component[key] for key in ['sha256', 'bytes']}
    # Fresh wire assembled explicitly; no old authority or protection array is retargeted.
    authority = dict(schemaVersion=1, state='ROOT_NEXT_WASMTIME_DEPLOYMENT_AUTHORIZED_V2', unissued=False,
        sourceIndex=row(actor / 'index.json'), plan=row(actor / 'plan.json'),
        constructionResult=construction_ref, component=component,
        componentAudit=construction['artifacts']['componentAudit'],
        localhostServeAllowed=True, actualNextGuestAllowed=True, browserAllowed=True,
        compilerAllowed=False, componentConstructionAllowed=False,
        externalDeploymentAllowed=False, adoptionAllowed=False,
        constructionCallerIndex=constructor['callerIndex'],
        constructionDataReview=ctor_review_ref, applicationBuildDataReview=app_review_ref,
        rootLaunchMinimumFreeBytes=1073741824, runId=trial['runId'],
        wrapperPython=PYTHON, fullNativeGuardImplementation=FULL_GUARD,
        rootPreparation=row(HERE/'prepare-cohort.py'), rootWrapper=row(HERE/'run-native-trial.py'),
        applicationSource=actor_plan['applicationSource'], applicationInputs=actor_plan['applicationInputs'],
        applicationRootIdentityEvidence=actor_plan['applicationRootIdentityEvidence'])
    for key in ['inputEntry', 'inputSourceIndex']:
        authority[key] = construction['artifacts'][key]
    for key in ['engine', 'nativeMetadata', 'metadataExpectedFixedValues', 'engineBuildEvidence']:
        authority[key] = constructor[key]
    external = Path(str(root) + '-external-root')
    authority['constructionOuterTerminal'] = row(external / 'terminal.json')
    authority['constructionWorldGuard'] = row(external / 'world-guard.json')
    authority['worldGuardImplementation'] = WORLD_GUARD
    authority['worldSourceIndex'] = constructor['worldSourceIndex']
    authority['worldInputs'] = [ref for ref in constructor['newSourceEvidence'] if ref['path'].endswith('.wit')]
    assert len(authority['worldInputs']) == 8
    build = Path(authority['nativeMetadata']['path']).parent
    metadata = read(authority['nativeMetadata']['path'])
    build_result = read(build / 'result.json')
    authority['fullNativeBuildResult'] = row(build / 'result.json')
    authority['fullNativeBuildObservation'] = row(Path(str(build) + '-root-monitor') / 'observation.json')
    authority['fullNativeBuildReview'] = row(BASE / 'next-native-fetch-resource-cleanup-root-results-v1/actual-build-review.json')
    build_review = read(authority['fullNativeBuildReview']['path'])
    authority['fullNativeBuildSourceIndex'] = build_review['callerSourceIndex']
    authority['fullBuildGeneratedNullSource'] = row(build / 'build/starling-raw.wasm/null.cpp')
    assert build_review['verifiedPassed'] is True
    assert build_review['engine'] == authority['engine'] and build_review['metadata'] == authority['nativeMetadata']
    assert build_review['actualResult'] == authority['fullNativeBuildResult']
    authority['nativeSourceFamilies'] = [authority['fullNativeBuildSourceIndex'],
        row(BASE / 'next-native-portable-source-v6/index.json'),
        row(BASE / 'next-native-fetch-resource-cleanup-candidate-v2/index.json'),
        row(BASE / 'next-module-fileurl-interop-candidate-v2/index.json'),
        row(BASE / 'next-portable-cache-handler-candidate-v2/index.json'),
        row(BASE / 'next-portable-cache-app-build-v1/index.json')]
    refs, by_path = [], {}

    def add(ref):
        assert set(ref) == {'path', 'sha256', 'bytes'}
        assert row(Path(ref['path'])) == ref
        if ref['path'] in by_path:
            assert by_path[ref['path']] == ref
        else:
            refs.append(ref)
            by_path[ref['path']] = ref

    assert len(build_result['sourceCopies']) == 825
    for copy in build_result['sourceCopies']:
        add(copy['source'])
        add(copy['target'])
    assert len(refs) == 1650
    for key in ['fullNativeBuildResult', 'fullNativeBuildObservation', 'fullNativeBuildReview',
                'fullBuildGeneratedNullSource', 'nativeMetadata', 'engine', 'component', 'componentAudit',
                'wrapperPython', 'fullNativeGuardImplementation', 'worldGuardImplementation',
                'constructionDataReview', 'applicationBuildDataReview', 'applicationRootIdentityEvidence']:
        add(authority[key])
    for key in ['actualLibrary', 'actualSavedFrameHeader', 'actualConfigHeader', 'actualConfdefs',
                'patchedSpiderMonkeyEvidence', 'savedFramePatchIndex', 'actualAggregateLock',
                'offlineCargoConfig', 'portableCargoSelection', 'validatedCargoProofCapsule',
                'validatedCargoProofIndex', 'sourceComposition']:
        add(metadata[key])
    additions = [HERE/name for name in ROOT_FILES] + [HERE/'plan.json', ctor_path,
        ctor_dir / 'actual-construction-review.json', Path(root_policy['ownerReview']['path']), root / 'result.json', root / 'component-audit.json',
        external / 'started.json', external / 'terminal.json', external / 'world-guard.json',
        Path(authority['worldGuardImplementation']['path']), app_dir / 'actual-build-review-v2.json',
        app_dir / 'actual-build-review.json', app_dir / 'actual-build-owner-tool-review.json',
        app_dir / 'standalone-root-identity.json', app_dir / 'admission.json', app_dir / 'observation.json',
        Path(actor_plan['applicationBuildResult']['path']), Path(actor_plan['applicationInputs']['path'])]
    outer = read(external / 'terminal.json')
    additions += [Path(outer[key]['path']) for key in ['stdout', 'stderr']]
    additions += [Path(ref['path']) for ref in constructor['newSourceEvidence'] + constructor['engineBuildEvidence']]
    for command in construction['commands']:
        assert command['rawExitCode'] == 0 and command['clean'] is True
        additions += [Path(command[key]['path']) for key in ['terminal', 'stdout', 'stderr']]
    catalogue_path = BASE / 'next-portable-cache-app-build-v1/fixture-inputs.json'
    catalogue = read(catalogue_path)
    assert len(catalogue['files']) == 31
    fixture_root = REPO / catalogue['repositoryFixture']
    additions += [fixture_root / ref['path'] for ref in catalogue['files']]
    additions += [Path(ref['path']) for ref in actor_plan['preservedD990FailureBaselines']]
    for path in additions:
        add(row(path))
    authority['nativeProtectedInputs'] = refs
    authority['comparisonArm']=arm
    authority['comparisonSequence']=trial['sequence']
    authority['comparisonPlan']=row(HERE/'plan.json')
    authority['reviewPolicy']=root_policy
    authority['driverSourceProofs']=source_proofs()
    authority['rootReview']='Fixed declared comparison trial; all original gates preserved. Explicit pinned review-schema policy only, not rewritten reviews. Current actual31/39/18 and fresh825 source-target pairs; original guards in original contexts. Raw1 semantic failures remain failures; no retries, cause, private identity or promotion.'
    assert str(Path(actor_plan['outputPrefix']+'-'+trial['runId']))==trial['outputRoot']
    native_admission(authority,actor_plan,native,world)
    return authority


def stock_admission(authority, plan):
    fixed=load_plan()
    require(authority['sourceIndex']==fixed['stockSourceIndex'] and authority['plans']==fixed['stockPlans'],'Held Stock index/plans')
    family(authority['sourceIndex']); verify(authority['plans'])
    require(plan['outputPrefix']=='/private/tmp/starling-node-compat/next-portable-cache-stock-v2' and plan['arms']['stock']['timeoutSeconds']==300,'Original Stock prefix/cap')
    require(authority['state']=='ROOT_NEXT_BROWSER_PHASE_MATCHED_HOST_AUTHORIZED_V1' and authority['arm']=='stock','Stock API')
    require(all(k not in authority for k in ['outputRoot','monitorOutputRoot','argv']),'No Stock namespace/argv overrides')
    require(authority['localhostServerAllowed'] is authority['browserAllowed'] is True and all(authority[k] is False for k in ['compilerAllowed','nativeBuildAllowed','guestAllowed','engineAllowed','externalApplicationDeploymentAllowed']),'Stock-only permissions')
    for ref in plan['sourceFamilies']: family(ref)
    for ref in plan['protectedInputs']: verify(ref)
    app=read_ref(APP_REVIEW)
    require(app['state']=='PORTABLE_CACHE_APP_HOST_BUILD_DATA_REVIEW_PASSED_V1' and app['verifiedPassed'] is True and authority['applicationBuildDataReview']==plan['applicationBuildReview']==APP_REVIEW,'Genuine app review')
    require(app['actualResult']==plan['applicationBuildResult'] and app['applicationInventory']==plan['applicationInputs'] and app['standaloneRootIdentity']==plan['applicationRootIdentityEvidence'],'App/Stock role joins')
    vm=read_ref(VM_REVIEW); result=read_ref(VM_RESULT)
    require(authority['vmSeamDataReview']==VM_REVIEW and authority['vmSeamResult']==VM_RESULT and vm['state']=='INDEPENDENT_NODE22_DEFAULT_VM_LOADER_SEAM_DATA_REVIEW_PASSED_V2' and vm['verifiedPassed'] is True and vm['actualResult']==VM_RESULT,'Genuine external VM seam')
    require(result['passed'] is True and result['errors']==[] and result['node']=='v22.14.0' and result['oldExpectedError']['code']=='ERR_VM_DYNAMIC_IMPORT_CALLBACK_MISSING','Original VM observation')
    require(result['newDefaultClass']==dict(defaultSameAsRealNodeRequire=True,repeatedNamespaceIdentity=True,constructedValue='main-loader:7',candidateSynchronousRequireIsSeparate=True),'Real default-loader class result')
    require(plan['arms']['stock']['browserSource']['sha256']=='f19d6c42ea44897ed026ba437657a9749396ee138301e5abbfaa17eb508c7ffa','Same default browser')

def assemble_stock(trial):
    fixed=load_plan(); plans=read_ref(fixed['stockPlans'])
    a=dict(schemaVersion=1,state='ROOT_NEXT_BROWSER_PHASE_MATCHED_HOST_AUTHORIZED_V1',arm='stock',runId=trial['runId'],sourceIndex=fixed['stockSourceIndex'],plans=fixed['stockPlans'],localhostServerAllowed=True,browserAllowed=True,compilerAllowed=False,nativeBuildAllowed=False,guestAllowed=False,engineAllowed=False,externalApplicationDeploymentAllowed=False,applicationBuildDataReview=APP_REVIEW,vmSeamDataReview=VM_REVIEW,vmSeamResult=VM_RESULT,comparisonArm='stock',comparisonSequence=trial['sequence'],comparisonPlan=row(HERE/'plan.json'),driverSourceProofs=source_proofs(),rootReview='Declared matched Node control only, public default loader and owned cache parent; same app/browser/all original gates. No native/Wasm/build/guest permission, retry, reliability or promotion.')
    stock_admission(a,plans)
    require(plans['outputPrefix']+'-'+trial['runId']==trial['outputRoot'],'Declared Stock output')
    return a

def prepared_cohort(path):
    require_bound(); path=Path(path).resolve()
    require(path==HERE/'cohort-authority.json','Fixed cohort authority path')
    c=read(path); require(c['state']=='ROOT_FIXED_COMPLETION_COMPARISON_AUTHORIZED_V1' and c['comparisonPlan']==row(HERE/'plan.json') and c['cohortOuterSeconds']==7200 and c['cohortRunAllowed'] is True and c['actorBindings']==ACTOR_REFS and c['newReviewBindings']==NEW_REVIEW_REFS,'Prepared whole cohort')
    verify_proofs(c['driverSourceProofs']); plan=load_plan()
    require(len(c['trials'])==10 and [x['trial'] for x in c['trials']]==plan['trials'],'Exact prepared ten-authority order')
    for item in c['trials']:
        verify(item['authority']); a=read_ref(item['authority'])
        require(item['authority']['path']==item['trial']['authorityPath'],'Declared authority file')
        require(trial_for_authority(a,item['authority']['path'])==item['trial'],'Authority/trial binding')
        verify_proofs(a['driverSourceProofs'])
    return c

def inspect_outcome(trial, authority_ref):
    """Read complete original publication; partial/missing evidence stops, false gates do not."""
    arm=trial['arm']; output=Path(trial['outputRoot']); monitor=Path(trial['ownerOutputRoot'])
    terminal=read(monitor/'terminal.json'); observation=read(monitor/'observation.json')
    a=read_ref(authority_ref); started=read(monitor/'started.json')
    plan=read_ref(a['plans'] if arm=='stock' else a['plan'])
    expected_argv=([plan['node']['path'],str(Path(a['sourceIndex']['path']).with_name('run-stock.mjs')),str(output),plan['standaloneSource'],plan['browserTools'],trial['runId']] if arm=='stock' else [plan['node']['path'],str(actor_path(arm)/'deploy.mjs'),authority_ref['path']])
    require(started['authority']==authority_ref and started['argv']==expected_argv and started['timeoutSeconds']==trial['ownerSeconds'],'Original monitor exact argv/cap')
    for key in ['stdout','stderr']: verify(terminal[key])
    require(terminal['authority']==authority_ref and observation['terminal']==row(monitor/'terminal.json'),'Owner authority/observation join')
    require(observation['runId']==trial['runId'] and observation['outputRoot']==trial['outputRoot'] and observation['rawExitCode']==terminal['rawExitCode'],'Original observation context')
    require(observation['result']==row(output/'result.json'),'Whole original result published')
    result=read(output/'result.json')
    expected_observation_pass=terminal['rawExitCode']==0 and observation['ownedGroupsClean'] and observation['protectedInputsPreserved'] and result.get('passed') is True
    require(observation['hostExperimentPassed' if arm=='stock' else 'passed']==expected_observation_pass,'Original observation pass predicate')
    if arm=='stock':
        client=result
    else:
        require(result['rootAuthority']==authority_ref and result['sourceIndex']==a['sourceIndex'] and result['runId']==trial['runId'] and result['outputRoot']==trial['outputRoot'],'Native result context')
        client=read_ref(result['client']['result'])
        raw_ref=result['server']['stdout']; verify(raw_ref)
        require(raw_ref['path']==str(output/'wasmtime.stdout.log') and raw_ref['bytes']==result['server']['stdoutCapture']['fileBytes'],'Complete raw capture descriptor')
        receipt=read(HERE/(trial['runId']+'-full-world-guard.json'))
        require(receipt['authority']==authority_ref and receipt['unchanged'] is receipt['nativeInputsPreserved'] is True and receipt['before']==receipt['after'],'Original-context final guard receipt')
    net=(client.get('browser') or {}).get('netlog') or {}
    if descriptor(net.get('file')): verify(net['file'])
    outcome=classify_published(arm,terminal,observation,result,client)
    return dict(outcome,terminal=row(monitor/'terminal.json'),observation=row(monitor/'observation.json'),result=row(output/'result.json'),client=row(output/'result.json') if arm=='stock' else result['client']['result'],browserStrictPassed=(client.get('browser') or {}).get('passed'),browserFunctionalPassed=(client.get('browser') or {}).get('functionalPassed'),legacyCacheInvalidation=client.get('cacheInvalidation'),stdoutCapture=None if arm=='stock' else result['server']['stdoutCapture'])

def error_data(error):
    return dict(type=type(error).__name__,message=str(error)[:4096])

