"""Seal own Source after read/hash/pure and grammar-only observations; no owner API."""
from pathlib import Path
import hashlib
import json
import subprocess
import time
HERE=Path(__file__).resolve().parent
assert not(HERE/'index.json').exists(),'Never mutate a sealed family'
def row(p):
    b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(n):return json.loads((HERE/n).read_text())
def write(n,v):(HERE/n).write_text(json.dumps(v,indent=2)+'\n')
refs=read('references.json');check=read('source-check-results.json')
assert check['passed']is True and check['declaredFiles']==11581 and check['declaredFamilies']==11
node=refs['node'];assert row(Path(node['path']))==node
entry=row(HERE/'build.mjs');started=time.monotonic()
result=subprocess.run([node['path'],'--check',str(HERE/'build.mjs')],capture_output=True,timeout=30)
(HERE/'grammar.stdout.log').write_bytes(result.stdout);(HERE/'grammar.stderr.log').write_bytes(result.stderr)
write('grammar.terminal.json',dict(schemaVersion=1,argv=[node['path'],'--check',str(HERE/'build.mjs')],executable=node,source=entry,rawExitCode=result.returncode,timeout=False,stdout=row(HERE/'grammar.stdout.log'),stderr=row(HERE/'grammar.stderr.log'),operationalSeconds=time.monotonic()-started,syntaxCheckerUsed=True,sourceModuleEvaluated=False,importsEvaluated=False,ownerAPIsInvoked=False,componentOrEngineOrGuestInvoked=False))
assert result.returncode==0 and result.stdout==result.stderr==b''
write('source-check.terminal.json',dict(schemaVersion=1,actualUnifiedExecSessionId=35215,rawExitCode=0,stdout=row(HERE/'check-source.stdout.log'),stderr=row(HERE/'check-source.stderr.log'),source=row(HERE/'check-source.py'),ownerAPIsInvoked=False))
(HERE/'README.md').write_text("""# Experimental selected-clock v13 construction Source

SEALED UNREVIEWED SOURCE. No native preflight, loader, package, Wizer, componentizer, engine or guest action ran in preparation. One pinned Node22 --check grammar invocation on the final caller succeeded without evaluating imports or its module body. Root/source-peer/action/actual-component/runtime slots remain NULL or explicitly false.

`buildClockV13Component({configDescriptor})` is the concrete dormant constructor. It authenticates its complete family,11,581 declared physical inputs,11 inherited families,Root/config/independent Source peer and original native/loader contexts before its first custom import. It uses the genuine repeatable `classicPreflight({variant:'normal-off'})` read/hash API in its original context and retains its entire actual frame DATA plus the fresh recheck callable descriptor. The real accepted native context is d544/9,973,355B, the complete64-field bfa sidecar,342 native files,3 embedding files and9 whole manifests. There is no metadata/source/global rebinding or one-shot bootstrap replay.

The original native preflight requires its historical two environment paths as consumed-context integrity checks. They stay exact and are clearly distinct from the loaderV2's own explicit new package. The native preflight reads old packaging/tool files but imports no old packager,Rolldown or Jco package. The new construction Node must be fresh with plain execArgv[], selected clean startup/NAPI state and an empty caller-owned0700 TMPDIR. The loader authenticates its actual package and artifacts in its original context and bookends its call. Native and own whole Source rechecks also surround construction and failure.

The complete original772B ReactDOM-edge guest and actual487,929B packages-v2 bundle8db23 are byte-identical copies, including the full real ReactDOM renderer. The nine-module graph,eight physical transform inputs and exact React/ReactDOM19.3.1 package manifests remain retained/protected. This caller consumes the already-retained bundle to preserve fresh package/dependency import order; it does not import Rolldown or rerun bundling before the new loader. The original genuine bundler/toolchain APIs remain Source/provenance references; no abbreviated,caught or facade workload replaces the original.

The call selects only monotonic-clock,wall-clock and poll@0.2.10. Stdio,random,http and fetch-event are disabled; clocks remain enabled. The original explicit pruned87777 adapter is passed, with enableFeatures[],enableAotfalse and env{}. No custom host service or default packager/adapter promotion is added. On return it retains complete bytes,full emitted WIT/audit,transpile metadata and all generated files,without importing the generated module or calling any ordinary export.

Important limit: reviewed loaderV2 audits final imports before returning. If that audit refuses without a byte-bearing error,this caller gets no component/WIT. Such a failed attempt remains unaccepted with its raw error; no complete graph or instantiation claim follows. Capture-before-selection on that failure remains an open evidence improvement. No hook or globals patch is invented. A genuine new Root-controlled external owned watchdog and raw-observation phase are still required; the operational parent is not implemented in this Source packet. The external contract requires1800s owned Node under2400s owned phase and complete argv/rawstreams/terminal/cleanup. No in-worker JS timer is claimed to interrupt blocking Wizer.

Preparation passed130,901 read/hash/data checks over11,591 observed paths and21 explicit Python data-model cases. It authenticated all6,414 original native consumed inputs,two tool-tree inventories/22 aliases,all342+3 native files,full real library/source graph and the loader's complete original Source/proof/package intake. The pure cases exercise finite policy widening,byte transport and generated output confinement models; they do not execute JS owner functions. Initial preparation incorrectly left23 original consumed-manifest paths relative in the new intake. The genuine API resolves those against its original HERE; the new intake was corrected to those exact physical roles,without altering the old manifest. Failed preparation source/raw outputs are preserved.

ReactDOM construction is only the first clock-capability probe. It does not complete clock-profile admission or broader Next.js compatibility. `future-full-clock-runtime-requirements.json` retains all seven original resource cases,all nine manifests/native Buffer,Date/monotonic/snapshot/resumption,timer ordering/cancel/self-clear,handled/fatal callbacks,fresh+retained instances,all-invalid/surviving queues,interest settlement,teardown and stock-host instantiation. Historical two-interface failures stay failed. Any selector fix must use its actual new reviewed native generation; current accepted v13 is not projected into that fix. Request epochs,fallible enqueue,cached pollables,reset/reuse and ALS remain separate unresolved lifecycle work. Complete actual component/core/type/adapter graph and standard0.2.10 import review precede any runtime phase.
""")
write('results.json',dict(schemaVersion=1,state='CLOCK_V13_COMPONENT_CONSTRUCTION_SOURCE_SEALED_UNREVIEWED_V1',sourceOnly=True,sourceIndependentReview=None,rootAuthority=None,actualComponent=None,actualRuntimeAuthority=None,entry=entry,loaderSourceIndex=refs['loaderSourceIndex'],loaderSourcePeer=refs['loaderSourcePeer'],nativePreflight=refs['nativePreflight'],nativeEngine=refs['nativeEngine'],nativeMetadata=refs['nativeMetadata'],nativeSourceFiles=342,externalEmbeddingSources=3,rawMetadataFields=64,selectedWholeManifests=9,wholeOriginalReactDomGuest=True,wholeOriginalReactDomBundle=refs['bundle'],originalBundle=refs['originalBundle'],selectedInterfaces=refs['selectedInterfaces'],disableFeatures=refs['disableFeatures'],declaredInputFiles=11581,completeFamilies=11,sourceChecks=check['checks'],pureDataModels=21,syntaxCheckerUsed=True,syntaxCheckerRawExitCode=0,sourceModuleImported=False,nativePreflightInvoked=False,loaderInvoked=False,packageOrComponentizerInvoked=False,engineOrGuestExecuted=False,ordinaryGuestExportsInvoked=False,generatedModuleImported=False,keyOrCryptoWorkloadsInvoked=False,operationalAdmission=False,runtimeAcceptanceClaim=False,fullClockProfileAcceptance=False,externalOperationalControllerImplemented=False,loaderAuditMayRejectBeforeReturningBytes=True,captureBeforeSelectionFailureEvidenceImprovementOpen=True,remainingGates=['Independent Source review and new paired Root/config/owned-controller authority','Actual fresh owned construction/raw0/complete whole returned artifacts,or preserved unaccepted failure','Independent actual root/core/type/adapter/ABI/import/loading-protocol review','Full separately authorized clock/resource/ReactDOM runtime and lifecycle suite,not construction-only acceptance']))
write('preparation-history.json',dict(schemaVersion=1,state='SOURCE_PREPARATION_CHECKED_SEALED_UNREVIEWED',ownerAPIActionsInvoked=False,failedAttempt='preparation-history/attempt1',correction='Resolve original consumed-manifest relative paths only against genuine original native HERE;23 duplicate rows collapse to11581 unique current absolute runtime inputs',grammarOnlyCheckExecuted=True,rootOrSourcePeerOrActualActionsIssued=False))
write('source-receipt.json',dict(schemaVersion=1,state='SEALED_CLOCK_V13_COMPONENT_CONSTRUCTION_SOURCE_UNREVIEWED_V1',result=row(HERE/'results.json'),sourceCheck=row(HERE/'source-check-results.json'),grammar=row(HERE/'grammar.terminal.json'),entry=entry,sourceIndependentReview=None,rootAuthority=None,actualComponent=None,ownerActionsInvoked=False,operationalAdmission=False))
rows=[]
for p in sorted(HERE.rglob('*')):
    assert not p.is_symlink()
    if p.is_file()and p.name!='index.json':
        d=row(p);d['path']=p.relative_to(HERE).as_posix();rows.append(d)
write('index.json',dict(schemaVersion=1,files=rows))
for d in rows:
    actual=row(HERE/d['path']);assert actual['sha256']==d['sha256']and actual['bytes']==d['bytes']
for n in ['index.json','results.json','source-receipt.json']:print(n,json.dumps(row(HERE/n)))
print('members',len(rows))
