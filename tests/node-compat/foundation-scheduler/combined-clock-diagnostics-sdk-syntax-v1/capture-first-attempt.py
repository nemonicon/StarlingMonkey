"""Read/hash first-attempt outcomes; do not rerun or import an owner helper."""
from pathlib import Path
import hashlib,json,os,shlex,stat
HERE=Path(__file__).resolve().parent
P=Path('/private/tmp/starling-node-compat/combined-clock-diagnostics-v1-sdk-syntax')
FROZEN=Path('/private/tmp/starling-node-compat/combined-native355-v2-freeze')
CONFIGURED=Path('/private/tmp/starling-node-compat/combined-native355-v1-source')
def d(p):
 b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def j(p):return json.loads(p.read_text())
def put(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
plan=j(P/'plan.json');result=j(P/'result.json');guard=j(P/'original-protection-final.json')
assert [r['rawExitCode'] for r in result['commands']]==[0,0,0,1,0]
copies=[];evidence=HERE/'raw';evidence.mkdir(exist_ok=False)
for file in sorted((P/'commands').rglob('*')):
 if not file.is_file():continue
 target=evidence/file.relative_to(P/'commands');target.parent.mkdir(parents=True,exist_ok=True)
 target.write_bytes(file.read_bytes());copies.append({'original':d(file),'copy':d(target)})
mapped={os.path.normpath(r['name']):Path(r['external-contents']) for r in j(P/'overlay.json')['roots']}
dependencies=[]
for command in plan['commands']:
 terminal=j(P/'commands'/command['id']/'terminal.json')
 assert terminal['allObservedOwnedGroupsGone'] and not terminal['forcedCleanup'] and not terminal['signals'] and not terminal['errors'] and not terminal['timeout']
 dep=Path(command['dependencyFile'])
 if not dep.exists():continue
 text=dep.read_text().replace('\\\n',' ');tokens=shlex.split(text.split(':',1)[1]);rows=[]
 for token in tokens:
  normalized=os.path.normpath(token);p=mapped.get(normalized,Path(normalized))
  assert p.is_file(),p
  rows.append({'reportedPath':token,'actualReadBytes':d(p),'mappedSource':normalized in mapped})
 assert any(r['reportedPath'].endswith('/include/clock-lifecycle-diagnostics.h') for r in rows),command['id']
 dependencies.append({'id':command['id'],'dependencyFile':d(dep),'headersAndMainInput':rows})
 target=evidence/'dependencies'/dep.name;target.parent.mkdir(exist_ok=True);target.write_bytes(dep.read_bytes());copies.append({'original':d(dep),'copy':d(target)})
metadata=j(FROZEN/'normal-off.engine.wasm.build.json');post=[]
for row in metadata['sourceManifest']:
 for root in [FROZEN/'source',CONFIGURED]:
  path=root/row['path'];actual=d(path);assert actual['sha256']==row['sha256']
  post.append({'file':actual,'modeNow':stat.S_IMODE(path.stat().st_mode)})
embedding_root=Path(plan['commands'][-1]['argv'][-1]).parents[1]
for row in metadata['componentizeSourceManifest']:
 for root in [FROZEN/'componentize-source',embedding_root]:
  path=root/row['path'];actual=d(path);assert actual['sha256']==row['sha256'];post.append({'file':actual,'modeNow':stat.S_IMODE(path.stat().st_mode)})
for name,sha in [('normal-off.engine.wasm','355550f1d0bdc7455fd81ffbd739ac1453a56f3537b277eb644441d87434af3b'),('normal-off.engine.wasm.build.json','5f3be8851739635beaee6550ad03c7afed9e6eebb0607840ebd12e4a095354d3'),('normal-off-freeze-receipt.json','9ce681402425f2bc59134bec5b48c98ee20fe15d42abf7ecaa1df920e05fded4')]:
 path=FROZEN/name;actual=d(path);assert actual['sha256']==sha;post.append({'file':actual,'modeNow':stat.S_IMODE(path.stat().st_mode)})
put(HERE/'dependency-observations.json',{'schemaVersion':1,'units':dependencies,'scope':'Actual four successful frontends; Source paths interpreted through the exact retained VFS, not hashed as old configured bytes.'})
put(HERE/'raw-copy-map.json',{'schemaVersion':1,'copies':copies})
put(HERE/'additional-parent-post-check.json',{'schemaVersion':1,'files':post,'scope':'Current hash comparison to authentic compiled metadata/known artifact hashes; these extra paths have no separately captured per-attempt before-mode receipt. Do not backdate this check.'})
put(HERE/'results.json',{'schemaVersion':1,'state':'DIAGNOSTIC_SDK_FIRST_ATTEMPT_FOUR_FRONTENDS_PASSED_ONE_DRIVER_INPUT_REFUSAL_V1',
 'sourceIndex':result['sourceIndex'],'actualResult':d(P/'result.json'),'actualPlan':d(P/'plan.json'),'originalProtectionBefore':d(P/'original-protection-before.json'),'originalProtectionFinal':d(P/'original-protection-final.json'),
 'rawExitCodes':[0,0,0,1,0],'allFiveGroupsGone':True,'noSignalsTimeoutForcedCleanupOrErrors':True,'sourceChangesApplied':False,'compilerFrontendPassedUnits':['event-loop','timers','host-api','embedding'],'newBuiltinFrontendEntered':False,
 'newBuiltinFailure':'clang driver filesystem input-existence check refuses new virtual-only original path before frontend; exact180B stderr retained.',
 'commonDiagnosticHeaderReachedInFourDependencyLists':True,'allFiveFrontendSyntaxPassed':False,'protectedBeforeAndAfterFiles':guard['unchangedFiles'],'sdkAliasesUnchanged':31,
 'additionalParentPostCheck':d(HERE/'additional-parent-post-check.json'),'protectionQualification':'Configured355 originals and four replaced frozen preimages were not separately snapshotted before this attempt; current hashes match authentic parent. Selected10879 original inputs have full pre/post hash/mode/inode evidence.',
 'compilerOnlyNoObjectOrLinkRequested':True,'nativeEngineOrGuestExecuted':False,'abiLinkNativeAdmissionOrRuntimeClaim':False,
 'proposedCorrection':'Same unchanged7aed source/VFS/defines/includes/SDK; only private builtin main input becomes existing staged CPP. No four-unit rerun needed without shared Source changes.'})
print(json.dumps({'copiedRawFiles':len(copies),'dependencyUnits':len(dependencies),'additionalParentPostFiles':len(post),'result':d(HERE/'results.json')}))
