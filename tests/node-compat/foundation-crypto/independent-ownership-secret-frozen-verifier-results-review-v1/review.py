"""Independent actual verifier DATA audit. Never imports an owner module/helper."""
from pathlib import Path
import ast
import hashlib
import json
import os
import shlex
import stat

P = Path(__file__).resolve().parent
K = P.parent
checks, seen, physical = 0, {}, {}


def need(value, message):
    global checks
    checks += 1
    if not value:
        raise AssertionError(message)


def identity(s):
    return s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns


def row(path):
    path = Path(path)
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return dict(path=str(path), sha256=h.hexdigest(), bytes=path.stat().st_size)


def verify(value, role='input'):
    expected = {k:value[k] for k in ['path','sha256','bytes']}
    p = Path(expected['path'])
    need(p.is_absolute() and p.is_file() and not p.is_symlink(), 'ordinary absolute DATA file')
    a, real = p.stat(), str(p.resolve())
    if real not in physical:
        actual = row(p)
        need(actual == expected and identity(a) == identity(p.stat()), 'full stable streamed hash ' + str(p))
        physical[real] = dict(sha256=actual['sha256'], bytes=actual['bytes'], identity=identity(a))
    saved = physical[real]
    need(saved['sha256'] == expected['sha256'] and saved['bytes'] == expected['bytes'] and saved['identity'] == identity(a), 'exact repeated descriptor and identity')
    if str(p) not in seen:
        seen[str(p)] = dict(expected, roles=set())
    seen[str(p)]['roles'].add(role)
    return p


def parse(raw):
    def pairs(values):
        result = {}
        for key, value in values:
            need(key not in result, 'no duplicate JSON key')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=lambda _: (_ for _ in ()).throw(AssertionError('nonfinite JSON')))


def data(value, role='JSON'):
    return parse(verify(value, role).read_bytes())


def local(name):
    need(type(name) is str and name and not name.startswith('/') and '\\' not in name and '\0' not in name and all(p not in ('','.','..') for p in name.split('/')), 'finite local name')
    return name


def membership(root, names, private=False):
    actual = set()
    need(root.is_dir() and not root.is_symlink(), 'ordinary root')
    for p in root.rglob('*'):
        s = p.lstat()
        need(not p.is_symlink(), 'no source/evidence leaf link')
        if p.is_file():
            actual.add(p.relative_to(root).as_posix())
            if private:
                need(stat.S_IMODE(s.st_mode) == 0o600, 'private retained data')
        else:
            need(p.is_dir(), 'ordinary directory')
            if private:
                need(stat.S_IMODE(s.st_mode) == 0o700, 'private directory')
    if private:
        need(stat.S_IMODE(root.stat().st_mode) == 0o700, 'private root mode')
    need(actual == set(names), 'whole physical membership')


def family(value):
    ix = data(value, 'source-or-proof-index')
    root, names, rows = Path(value['path']).parent, {'index.json'}, []
    need(ix['schemaVersion'] == 1 and type(ix['files']) is list, 'indexed schema')
    for item in ix['files']:
        name = local(item['path'])
        need(name not in names, 'unique indexed file')
        names.add(name)
        r = dict(item, path=str(root / name))
        verify(r, 'indexed-member')
        rows.append(r)
    membership(root, names)
    return rows


rootrow = dict(path=str(K/'ownership-secret-frozen-verifier-v1-root-results.json'),sha256='30759e2937dafa856b1c2f03b2e2b1b95bab0213b4066839b874119c25673c34',bytes=3347)
root = data(rootrow, 'actual-Root-observation')
need(root['state'] == 'ROOT_OBSERVED_SECRET_OWNER355_COMPLETE_FROZEN_VERIFIER_EXIT_ZERO_UNREVIEWED_V1' and root['rootToolSession'] == 83988 and root['rawRootControllerExitCode'] == 0, 'Root recorded enclosing zero; no fabricated stdout')
need(root['rootCommandStdoutBytesRetainedInRepository'] is False, 'Root command stdout not a repository artifact')
own_rows = family(root['controllerSourceIndex'])
need(root['controllerSourceIndex']['sha256'] == '0fc0082da7d9842bf9bd9e46a28760e2cea5f698eec62880f0150c572d94a78f', 'actual controller source identity')
peer_rows = family(root['sourceReview']['index'])
need(root['sourceReview']['result'] in peer_rows, 'controller source peer indexed')
peer = data(root['sourceReview']['result'], 'actual-controller-source-peer')
need(peer['state'] == 'INDEPENDENT_CRYPTO_OWNER355_SECRET_VERIFIER_CONTROLLER_SOURCE_REVIEW_PASSED_V1' and peer['controllerSourceIndexSha256'] == root['controllerSourceIndex']['sha256'] and peer['sourceOnly'] is peer['sourceReviewPassed'] is True, 'actual source-only caller review')
for key in ['ownerActionsInvoked','hostActionsInvoked','verifierActionsInvoked']:
    need(peer[key] is False, 'source review scope ' + key)
controller_dir = Path(root['controllerSourceIndex']['path']).parent
refs = data(next(r for r in own_rows if r['path'] == str(controller_dir/'references.json')), 'exact-controller-references')
families = []
for value in refs['families']:
    families.append(dict(index=value['index'], members=len(family(value['index']))))
contract = data(refs['verifierContract'], 'actual-original-helper-contract')
authority = data(root['rootAuthority'], 'actual-read-only-Root-authority')
config = data(root['config'], 'actual-controller-config')
need(config['controllerIndex'] == root['controllerSourceIndex'] and config['rootAuthority'] == root['rootAuthority'], 'actual source/config/Root relation')
need(authority['state'] == 'ROOT_REVIEWED_SECRET_OWNER355_FROZEN_VERIFIER_READ_ONLY_V1' and authority['phase'] == 'verify-frozen-read-only' and authority['variant'] == 'normal-off' and authority['verifierReadOnlyAllowed'] is True and authority['expectedVerifierCalls'] == 1 and authority['externalParentDeadlineSeconds'] == 600, 'one finite actual read-only phase')
need(authority['controllerIndex'] == config['controllerIndex'] and authority['controllerIndependentReview'] == root['sourceReview'] and authority['controllerEntry'] in own_rows, 'actual entry and controller peer')
for key in ['verifierSourceIndex','verifierSourceReview','verifierContract','verifierEntry','actualArtifactReview','actualArtifactContract','nativeSourceIndex','freezerSourceIndex','engine','metadata','freezeReceipt','frozenRoot']:
    need(authority[key] == refs[key], 'original actual authority role ' + key)
for key in ['nativeBuildAllowed','nativeFreezeAllowed','gcReconfigureAllowed','ninjaAllowed','ownerHelperAllowed','nodeAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','exportAllowed','bootstrapAllowed','componentAllowed','operationalAdmission','runtimeAcceptanceClaim','metadataProjectionAllowed','sourcePromotionAllowed','timingAllowed']:
    need(authority[key] is False, 'closed phase scope ' + key)
for key in ['actualVerifierResult','independentActualVerifierReview','actualExport','reviewedPins','actualBootstrap','runtimeAuthority']:
    need(authority[key] is None, 'new phase outcome not projected')
verify(authority['issuerSource'], 'Root-issuer-source-DATA')
verifier_peer = data(refs['verifierSourceReview']['result'], 'complete-helper-source-peer')
need(verifier_peer['state'] == 'INDEPENDENT_CRYPTO_OWNER355_SECRET_FROZEN_VERIFIER_SOURCE_REVIEW_PASSED_V1' and verifier_peer['verifierSourceIndexSha256'] == refs['verifierSourceIndex']['sha256'] and verifier_peer['sourceOnly'] is verifier_peer['sourceReviewPassed'] is True, 'complete original helper source proof')
for key in ['ownerActionsInvoked','verifierHelpersInvoked','exportOrBootstrapInvoked']:
    need(verifier_peer[key] is False, 'prior helper source review remains source-only')
need(contract['originalToolingRoot'] == str(Path(refs['verifierEntry']['path']).parent) and contract['frozenRoot'] == refs['frozenRoot'] and contract['configuredSourceRoot'] == refs['configuredSourceRoot'] and contract['workRoot'] == refs['workRoot'], 'actual original/configured/frozen roles distinct')
need(contract['nativeSourceIndex'] == refs['nativeSourceIndex'] and contract['freezerSourceIndex'] == refs['freezerSourceIndex'] and contract['actualArtifactReview'] == refs['actualArtifactReview'], 'actual source/freezer/frozen-proof provenance')
need(contract['implementationPhase'] == 'VERIFIER_ONLY_EXPORT_PIN_BOOTSTRAP_UNIMPLEMENTED' and contract['frozenVerifierImplemented'] is True and all(contract[k] is False for k in ['exportEntryImplemented','pinModelImplemented','bootstrapApiImplemented']), 'no unimplemented export/bootstrap claim')
artifact = data(refs['actualArtifactReview']['result'], 'current-frozen-artifact-proof')
artifact_contract = data(refs['actualArtifactContract'], 'frozen-artifact-contract')
need(artifact['state'] == artifact_contract['requiredReviewState'] and artifact['verifiedPassed'] is True, 'genuine actual frozen proof')
for key, value in artifact_contract['requiredFixedValues'].items():
    need(artifact[key] == value, 'whole frozen-proof fixed value ' + key)
need(artifact['artifacts'] == artifact_contract['artifacts'] and artifact['coverage'] == artifact_contract['requiredCoverage'], 'whole frozen-artifact map and coverage')
for key, value in artifact_contract['requiredExactDescriptors'].items():
    need(artifact['artifacts'][key] == value, 'exact frozen contract role ' + key)
for source_row in data(refs['verifierSourceInputs'], 'helper-source-inputs')['files']:
    verify(source_row, 'helper-source-input')
ledger = data(refs['artifactInputLedger'], 'complete-current-original-and-frozen-input-ledger')
for source_row in ledger['files']:
    verify(source_row, 'full-frozen-proof-input')

receipt = data(contract['freezeReceipt'], 'actual-frozen-receipt')
need(receipt['state'] == contract['expectedFrozenReceiptState'] and receipt['label'] == 'normal-off' and len(receipt['copies']) == 1902, 'actual complete frozen receipt')
need(receipt['nativeSourceIndexed'] == contract['nativeSourceIndex'] and receipt['freezerSourceIndexed'] == contract['freezerSourceIndex'] and receipt['actualBuildReview'] == contract['actualBuildReview'], 'actual native/freezer/BUILD tuple')
copies, names, originals = {}, {'normal-off-freeze-receipt.json'}, 0
freeze_root = Path(contract['frozenRoot'])
for value in receipt['copies']:
    path = Path(value['path'])
    need(path.is_relative_to(freeze_root) and value['path'] not in copies, 'unique confined frozen copy')
    names.add(path.relative_to(freeze_root).as_posix())
    copies[value['path']] = value
    verify(value, 'complete-frozen-copy')
    need(path.stat().st_nlink == 1 and type(value['shared']) is bool, 'independent physical frozen copy; shared is planning DATA')
    if value['original'] is not None:
        original = dict(path=value['original'],sha256=value['sha256'],bytes=value['bytes'])
        verify(original, 'caller-original-preservation-DATA')
        a, b = Path(original['path']).stat(), path.stat()
        need((a.st_dev,a.st_ino) != (b.st_dev,b.st_ino), 'original/copy independent inodes')
        originals += 1
need(originals == 1899 and len(names) == 1903, 'all original references and frozen membership')
membership(freeze_root, names, private=True)
normal = data(refs['normalProtection'], 'separate-old-normal-protection')
need(normal['originalReferenceEntries'] == len(normal['originals']) == 1387 and len(normal['requiredNormalFreezeMembership']) == 1391, 'old normal exact protection shape')
verify(normal['freezeReceipt'], 'old-normal-receipt')
for value in normal['frozenCopyEntries']:
    verify(value, 'old-normal-frozen-data')
for value in normal['originals']:
    verify(value['original'], 'old-normal-original-data')
    verify(value['frozen'], 'old-normal-frozen-pair')
membership(Path(normal['freezeReceipt']['path']).parent, normal['requiredNormalFreezeMembership'])

metadata = data(contract['metadata'], 'whole-unchanged-native-metadata')
policy = data(contract['policy'], 'actual-355-source-policy')
need(metadata['sourceManifest'] == policy['expectedNativeSourceManifest'] and len(metadata['sourceManifest']) == 355 and len(metadata['componentizeSourceManifest']) == 3, 'whole actual355/native plus3embedding sources')
need(metadata['enginePath'] == receipt['originalEngine'] and metadata['engineSha256'] == contract['engine']['sha256'] and metadata['engineBytes'] == contract['engine']['bytes'] and receipt['originalMetadataPath'] == metadata['enginePath'] + '.build.json', 'unchanged raw build paths and exact frozen engine tuple')
need(metadata['buildRecipeSha256'] == contract['recipeData']['sha256'] == receipt['recipeSha256'], 'actual new8350 recipe')
for key, policy_key in [('cryptoSecretFailureSourcePolicy','cryptoSecretFailureSourcePolicy'),('cryptoKeyOwnershipPolicy','cryptoKeyOwnershipSourcePolicy'),('classicTraceSourcePolicy','classicTraceSourcePolicy')]:
    need(metadata[key] == receipt[key] == policy[policy_key], 'full unchanged native policy ' + key)
for rows, prefix, count in [(metadata['sourceManifest'],'source',355),(metadata['componentizeSourceManifest'],'componentize-source',3)]:
    need(len(rows) == count and len({r['path'] for r in rows}) == count, 'exact source set')
    for value in rows:
        r = copies[str(freeze_root/prefix/local(value['path']))]
        need(r['sha256'] == value['sha256'], 'native/external source bytes agree whole metadata')
need(len(receipt['toolDependencyClosure']) == len({r['sourcePath'] for r in receipt['toolDependencyClosure']}) == 1424, 'full actual tool/source closure')
for value in receipt['toolDependencyClosure']:
    r = copies[str(freeze_root/'tooling/repository'/local(value['sourcePath']))]
    need(r['path'] == value['path'] and r['sha256'] == value['sha256'] and r['bytes'] == value['bytes'], 'actual frozen tool source mapping')
selected, selected_names, module_names = [], [], set()
need(len(metadata['selectedModuleManifests']) == 11, 'all eleven selected manifests')
for value in metadata['selectedModuleManifests']:
    name = local(value['path'])
    need(name not in selected_names, 'unique selected manifest')
    r = copies[str(freeze_root/'source'/name)]
    need(r['sha256'] == value['sha256'], 'manifest exact bytes')
    m = data(r, 'whole-unchanged-selected-manifest')
    need(type(m['modules']) is dict and not module_names.intersection(m['modules']), 'unique complete selected module names')
    module_names.update(m['modules'])
    if 'profileVersion' in value:
        need(value['profileVersion'] == m['profileVersion'], 'preserved real manifest profile version')
    selected.append(m)
    selected_names.append(name)

controller = data(root['actualControllerObservation'], 'actual-controller-observation')
terminal = data(root['actualMonitorTerminal'], 'actual-owned-worker-terminal')
saved_frame = data(root['actualWholeFrame'], 'whole-retained-helper-return')
raw_stdout = verify(root['actualRawStdout'], 'full-actual-child-stdout').read_bytes()
raw_stderr = verify(root['actualRawStderr'], 'full-actual-child-stderr').read_bytes()
raw_frame = parse(raw_stdout)
need(raw_stdout.endswith(b'\n') and raw_stderr == b'' and raw_frame == saved_frame, 'one complete JSON stdout value equals entire saved frame')
commands = dict(databaseRows=68,policyCpp=62,otherConfigured=5,generatedNull=1,strictCpp=4,privateCpp=6,embeddingSeparate=1,secretCpp=2)
expected = dict(schemaVersion=1,state='SECRET_OWNER355_FROZEN_BYTES_AND_METADATA_VERIFIED_NO_ACTION_AUTHORITY_V1',variant='normal-off',nativeSourceIndex=contract['nativeSourceIndex'],freezerSourceIndex=contract['freezerSourceIndex'],engine=contract['engine'],metadataDescriptor=contract['metadata'],freezeReceipt=contract['freezeReceipt'],metadata=metadata,selectedManifests=selected,selectedManifestPaths=selected_names,configuredSourceRoot=contract['configuredSourceRoot'],sourceRoot=contract['frozenSourceRoot'],componentizeSourceRoot=contract['componentizeSourceRoot'],workRoot=contract['workRoot'],freezerOriginalToolingRoot=contract['freezerOriginalToolingRoot'],verifierOriginalToolingRoot=contract['originalToolingRoot'],frozenFilesVerified=1902,frozenMembership=1903,originalReferenceCountAsData=1899,originalReferencesReopened=False,commands=commands,registryModuleExecuted=False,allOriginalSdkOrArchivesCopied=False,buildSemanticProvenance=contract['actualBuildReview'],actualFrozenArtifactReview=contract['actualArtifactReview'],runtimeBackendProof=dict(verified=False,version=None,vernum=None),engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,grantsActionAuthority=False)
need(saved_frame == expected, 'whole actual frame equals independent unchanged metadata/manifest/context model')
need(saved_frame['metadata'] == metadata and saved_frame['selectedManifests'] == selected, 'no projection of any metadata or manifest field')
need(receipt['runtimeBackendProof'] == saved_frame['runtimeBackendProof'], 'unknown runtime backend proof remains false/null/null')

# Read actual command DATA independently; no compiler/helper executes.
database = data(contract['compileCommands'], 'actual68-command-database')
cpp = {r['path'] for r in metadata['sourceManifest'] if r['path'].endswith('.cpp') and r['path'].startswith(('builtins/','runtime/'))}
need(len(database) == 68 and len(cpp) == 62, 'actual DB/native CPP distinction')
native = [r for r in database if r['file'] in {contract['configuredSourceRoot']+'/'+p for p in cpp}]
other = [r for r in database if r not in native]
need(len(native) == len({r['file'] for r in native}) == 62 and len(other) == 6, 'actual native selection')
need(sum(r['file'].startswith(contract['configuredSourceRoot']+'/') for r in other) == 5 and sum(r['file'].startswith(contract['workRoot']+'/') and r['file'].endswith('/null.cpp') for r in other) == 1, 'five other configured sources plus generated null')
strict_paths={'runtime/engine.cpp','runtime/event_loop.cpp','runtime/node_tick_queue.cpp','builtins/web/event/event-target.cpp'}
strict=[];private=[];secret=[]
for value in native:
    relative=value['file'][len(contract['configuredSourceRoot'])+1:]
    args=shlex.split(value['command'])
    need(args.count('-c')==1 and args[args.index('-c')+1]==value['file'] and '-fsyntax-only' not in args and [x for x in args if x.startswith('-O')]==['-O3'] and '-DNDEBUG' in args, 'genuine actual Release compile command')
    need(not any(x.startswith(('-DDEBUG','-DNODE_COMPAT_OOM_TESTING','-DNODE_COMPAT_GC_STRESS','-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY')) for x in args), 'normal noDEBUG/OOM/GC/runtime-only command')
    if relative in strict_paths:strict.append(value['command'])
    if relative in policy['privateTargetCpp']:private.append(value['command'])
    if relative in ['builtins/web/crypto/crypto-key.cpp','builtins/web/crypto/crypto-algorithm.cpp']:secret.append(value['command'])
need(sorted(strict)==sorted(metadata['strictEventExceptionPolicy']['actualNativeCompileCommands']) and len(strict)==4, 'all4 strict policy commands')
need(sorted(private)==sorted(metadata['classicStreamsPolicy']['actualPrivateTargetCompileCommands']) and len(private)==6, 'all6 private compile commands')
need(secret==metadata['cryptoSecretFailureBuildEvidence']['changedNativeCompileCommands'] and len(secret)==2, 'actual2 changed crypto CPP commands')
need([r['command'] for r in native]==metadata['internalTickPolicy']['actualLayoutCompileCommands'], 'all actual native layout commands')
need(not any(r['file'].endswith('/embedding/embedding.cpp') for r in database) and len(metadata['actualEmbeddingCompileCommands'])==1, 'embedding is separate, not a DB row')
cache_text=verify(contract['cmakeCache'], 'raw-CMake-cache').read_text();cache_values={}
for line in cache_text.splitlines():
    k,sep,rest=line.partition(':')
    if sep and '=' in rest:cache_values[k]=rest.partition('=')[2]
need(metadata['requestedCMakeOptions']==metadata['observedCMakeOptions'], 'requested/observed actual CMake options agree')
for key,value in metadata['observedCMakeOptions'].items():need(cache_values[key]==value, 'raw CMake option '+key)
need(cache_values['CMAKE_BUILD_TYPE']=='Release' and cache_values['NODE_COMPAT_GC_STRESS']==cache_values['NODE_COMPAT_OOM_TESTING']==cache_values['NODE_COMPAT_ENTROPY_MODE']=='OFF', 'normal actual CMake variant')

# Static call/context proof plus actual clean single worker; never import it.
source=Path(refs['verifierEntry']['path']).read_text();tree=ast.parse(source)
imports=set()
for node in ast.walk(tree):
    if isinstance(node,ast.Import):imports.update(a.name.split('.')[0]for a in node.names)
    elif isinstance(node,ast.ImportFrom):imports.add(node.module.split('.')[0])
need(imports=={'pathlib','hashlib','json','re','shlex','stat'}, 'actual standard-only helper imports, no process/native loader')
controller_source=Path(authority['controllerEntry']['path']).read_text();controller_ast=ast.parse(controller_source)
worker=next(n for n in controller_ast.body if isinstance(n,ast.FunctionDef) and n.name=='worker')
calls=[n for n in ast.walk(worker) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='helper' and n.func.attr=='verify_frozen']
need(len(calls)==1 and len(calls[0].args)==1, 'exact single real helper call in authenticated worker source')
worker_text=ast.get_source_segment(controller_source,worker)
need("helper.HERE==VERIFIER" in worker_text and "str(helper.FROZEN)==frame['contract']['frozenRoot']" in worker_text and worker_text.index('helper.verify_frozen(')<worker_text.index("write(OUT/'whole-frame.json'")<worker_text.index('print(json.dumps(value)'), 'actual context check and complete-return retention before print')
need(not any(isinstance(n,ast.Attribute) and isinstance(n.value,ast.Name) and n.value.id=='helper' and isinstance(n.ctx,ast.Store) for n in ast.walk(worker)), 'no helper attribute assignment/global/path/context rebinding')
need(controller['state']=='ROOT_OBSERVED_SECRET_OWNER355_FROZEN_VERIFIER_RAW_ZERO_UNREVIEWED_V1' and controller['errors']==[] and controller['sourceAndOriginalProtectionRechecked'] is True and controller['rawExitCode']==0, 'actual complete controller observation')
observation=controller['observation']
need(observation['fullReturnedFrame']==root['actualWholeFrame'] and observation['rawStdout']==root['actualRawStdout'] and observation['helperCalls']==1 and observation['wholeStdoutAndSavedFrameJsonEqual'] is observation['wholeFrameModelPassed'] is True, 'actual one-call returned-frame observation')
need(observation['syscallIsolationObserved'] is False and observation['callerSourceAndOriginalPreservationReadsSeparate'] is True and observation['helperOriginalReferencesReopened'] is False, 'source-flow read boundary, not syscall isolation')
need(terminal['pid']==65475 and terminal['rawExitCode']==0 and terminal['authority']==root['rootAuthority'] and terminal['stdout']==root['actualRawStdout'] and terminal['stderr']==root['actualRawStderr'], 'actual raw child/Root/streams')
need(terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True and terminal['timeout'] is terminal['forcedCleanup'] is False and all(terminal[k]==[] for k in ['signals','errors','interruptedSignals','remainingObservedPids']) and len(terminal['finalGroups'])==1 and terminal['finalGroups'][0]['alive'] is False, 'actual clean owned cleanup')
external=Path(authority['externalOutputRoot']);output=Path(authority['outputRoot'])
started=data(row(external/'started.json'), 'actual-worker-started')
need(started['pid']==65475 and started['authority']==root['rootAuthority'] and started['timeoutSeconds']==600 and started['argv'][1:]==['-B','-I',authority['controllerEntry']['path'],'worker',json.dumps(root['config'],separators=(',',':'))], 'actual isolated worker/controller/config argv')
need(Path(started['argv'][0]).is_file(), 'actual Python invocation path')
launcher=Path(started['argv'][0])
need(str(launcher)=='/Applications/Xcode.app/Contents/Developer/usr/bin/python3' and launcher.is_symlink(), 'actual recorded Xcode Python launcher alias')
launcher_link=os.readlink(launcher)
need(launcher_link=='../../Library/Frameworks/Python3.framework/Versions/3.9/bin/python3', 'exact current launcher link text')
launcher_target=launcher.resolve(strict=True)
need(str(launcher_target)=='/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9', 'actual canonical Python target; raw argv remains unchanged')
launcher_target_row=row(launcher_target)
verify(launcher_target_row, 'current-resolved-Python-launcher-target-DATA-not-historical-attestation')
owned=data(row(external/'owned-0000.json'), 'actual-owned-worker-record')
need(owned['sequence']==0 and terminal['observedProcesses']==[owned['process']] and owned['process']['pid']==owned['process']['pgid']==65475 and terminal['finalGroups'][0]['pgid']==65475, 'single actual observed worker session')
raw_observed=data(row(output/'raw-terminal-observed.json'), 'actual-preinterpretation-raw-terminal')
need(raw_observed['terminal']==root['actualMonitorTerminal'] and raw_observed['stdout']==root['actualRawStdout'] and raw_observed['stderr']==root['actualRawStderr'] and raw_observed['interpretationPending'] is True, 'raw streams/terminal retained before interpretation')
membership(output, {'whole-frame.json','raw-terminal-observed.json','controller-observation.json'}, private=True)
membership(external, {'started.json','owned-0000.json','terminal.json','stdout.log','stderr.log'}, private=True)
for directory in [output,external]:
    for p in directory.iterdir():verify(row(p), 'actual-raw-output-closure');need(p.stat().st_nlink==1, 'independently linked actual output')
for key in ['actualExport','reviewedPins','actualBootstrap','independentActualVerifierReview']:need(root[key] is None and controller[key] is None, 'later action/outcome remains null '+key)
for value in [root,controller,saved_frame]:
    for key in ['engineExecuted','guestExecuted','operationalAdmission','runtimeAcceptanceClaim']:
        need(value[key] is False, 'actual verifier/engine/runtime distinction '+key)
need(launcher.is_symlink() and os.readlink(launcher)==launcher_link and launcher.resolve(strict=True)==launcher_target, 'current observed launcher alias stable')
for real,saved in physical.items():need(identity(Path(real).stat())==saved['identity'], 'final current source/original/frozen/raw identity stable')
result=dict(schemaVersion=1,verifiedPassed=True,rootObservation=rootrow,controllerSourceIndex=root['controllerSourceIndex'],controllerSourceReview=root['sourceReview'],verifierSourceIndex=refs['verifierSourceIndex'],verifierSourceReview=refs['verifierSourceReview'],actualArtifactReview=refs['actualArtifactReview'],actualArtifactContract=refs['actualArtifactContract'],nativeSourceIndex=contract['nativeSourceIndex'],freezerSourceIndex=contract['freezerSourceIndex'],actualRootAuthority=root['rootAuthority'],actualConfig=root['config'],actualControllerObservation=root['actualControllerObservation'],actualMonitorTerminal=root['actualMonitorTerminal'],actualWholeFrame=root['actualWholeFrame'],actualRawStdout=root['actualRawStdout'],actualRawStderr=root['actualRawStderr'],engine=contract['engine'],metadata=contract['metadata'],freezeReceipt=contract['freezeReceipt'],verifierContract=refs['verifierContract'],families=families,checks=checks,uniqueReferencePaths=len(seen),uniquePhysicalFilesHashed=len(physical),coverage=dict(nativeSources=355,externalEmbeddingSources=3,selectedManifests=11,frozenCopies=1902,frozenFiles=1903,originalReferenceEntries=1899,toolClosureRows=1424,protectedOldNormalFiles=1391,protectedOldNormalOriginalEntries=1387,actualOutputFiles=3,actualExternalFiles=5,actualObservedOwnedWorkers=1,actualHelperCallsSourceAndTerminalSupported=1,metadataFields=len(metadata),selectedModuleNames=len(module_names)),commands=commands,actualWholeFrameEqualsUnchangedMetadataAndAllSelectedManifests=True,actualRawStdoutAndSavedFrameJsonEqual=True,rawStdoutSerializationByteEqualToPrettyFrame=False,sourceContextsNotRebound=True,helperPayloadReadScopeSourceFlowFrozenOnly=True,callerOriginalPreservationReadsSeparate=True,syscallIsolationObserved=False,rootCommandStdoutRepositoryArtifact=None,enclosingRootControllerExitIsRootRecorded=True,ownedWorkerExitIndependentlyDecoded=True,actualExport=None,reviewedPins=None,actualBootstrap=None,engineExecuted=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,reviewerHelpersOrControllersOrMonitorsNodeEngineRuntimeInvoked=False)
(P/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
(P/'python-launcher-alias.DATA.json').write_text(json.dumps(dict(schemaVersion=1,actualRawArgv=started['argv'],currentLauncherAlias=dict(path=str(launcher),linkText=launcher_link,resolvedTarget=str(launcher_target)),currentTargetDescriptor=launcher_target_row,actualObservedComm=owned['process']['command'],rawArgvOrContextRewritten=False,observationIsCurrentAliasSnapshotNotHistoricalExecutableAttestation=True),indent=2)+'\n')
(P/'input-hashes.json').write_text(json.dumps(dict(schemaVersion=1,files=[dict(v,roles=sorted(v['roles']))for v in sorted(seen.values(),key=lambda v:v['path'])],reviewerOwnerActionsInvoked=False),indent=2)+'\n')
print(json.dumps(dict(actualVerifierDataPassed=True,checks=checks,paths=len(seen),frozenCopies=1902,metadataFields=len(metadata),selectedManifests=11,actualHelperCalls=1,reviewerOwnerActionsInvoked=False)))
