"""Finite read/hash/data review sealer; never reruns owner tests or guests."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
HOST=Path('/private/tmp/starling-node-compat/package-bundler-independent-host-v1-20261105')
def row(p,relative=False):
 p=Path(p);assert p.is_file()and not p.is_symlink();b=p.read_bytes()
 return dict(path=p.relative_to(HERE).as_posix()if relative else str(p.absolute()),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def load(p):return json.loads(Path(p).read_bytes())
def write(name,d):(HERE/name).write_text(json.dumps(d,indent=2)+'\n')
captured=row(HERE/'reviewed-package-bundler.mjs');assert captured['sha256']=='5761731ca00f146f836e75d00bf72dc591789748d0100c271b10502abd6d28b7'
current=row(REPO/'tests/node-compat/framework-package-bundler.mjs');assert(current['sha256'],current['bytes'])==(captured['sha256'],captured['bytes'])
old=row(REPO/'tests/node-compat/profile-bundler.mjs');assert old['sha256']=='d1333e8c795098dbab12d1ad93b10fd5b27176541c9a053632531dabde36a4bc'
h=load(HOST/'results.json');assert len(h['cases'])==22 and h['passed']is True and all(r['passed']for r in h['cases'])
assert next(r for r in h['sources']if r['path'].endswith('/framework-package-bundler.mjs'))['sha256']==captured['sha256']
assert next(r for r in h['sources']if r['path'].endswith('/host-test.mjs'))['sha256']==row(HERE/'reviewed-host-test.mjs')['sha256']
for r in h['sources']:assert row(r['path'])==r
write('host-test-results.json',h)
hostfiles=[row(p)for p in sorted(HOST.rglob('*'))if p.is_file()]
assert not any(p.is_symlink()for p in HOST.rglob('*'))
write('host-output-files.json',dict(schemaVersion=1,role='READ_ONLY_EXTERNAL_HOST_TEST_OUTPUT_REFERENCES',root=str(HOST),files=hostfiles,copiedAllBytes=False))
c=load(HERE/'counterexample-evidence/results.json');assert c['sourceSha256']==captured['sha256']and len(c['cases'])==8
assert [r['accepted']for r in c['cases']]==[True,True,True,True,True,False,False,True]
positive=[r for r in h['cases']if not r['expectedRefusal']];assert len(positive)==10
assert all(r[k]['status']==0 and r[k]['signal']is None and r[k]['error']is None for r in positive for k in('original','bundled'))
ledger=load(HERE/'ledger-evidence/results.json');assert ledger['equal']is True
write('results.json',dict(schemaVersion=1,state='INDEPENDENT_PACKAGE_BUNDLER_IMPLEMENTATION_SOURCE_REVIEW_HELD_V1',sourceIndexSha256=None,sourceOnly=True,sourceReviewPassed=False,verifiedPassed=False,reviewedSource=current,capturedSource=captured,unchangedOriginalProfileBundler=old,intendedHostCasesPassed=22,hostToyControlProcesses=20,allIntendedHostProcessesRawZero=True,additionalBoundaryCases=8,residualReferenceAcceptances=6,providedLocalFalseRefusals=2,findings=['M1_PREACTION_DENIAL_VS_RUNTIME_AVAILABILITY_BOUNDARY','M2_PROVIDED_LOCAL_BINDINGS_FALSELY_REFUSED'],transformLedgerMeaning='Incoming transform-code bytes by logical ID; no complete physical/resolver closure claim',bomPhysicalExampleMatches=True,hostBundlerActionsInvoked=True,ownerBundlerFunctionInvoked=True,frameworkPackageExecuted=False,componentizerInvoked=False,nativeCompilerInvoked=False,nativeEngineExecuted=False,guestExecuted=False,generatedCounterexampleModuleImported=False,rootActionAuthority=None,runtimeAcceptance=False,operationalAdmission=False))
write('result-contract.json',dict(schemaVersion=1,state='HELD_OPTIONAL_PACKAGE_BUNDLER_SOURCE_AND_HOST_BOUNDARY_REVIEW_V1',results=row(HERE/'results.json'),reviewedSource=current,requiredCorrection=row(HERE/'required-correction-contract.json'),actualHostTests=row(HERE/'host-test-results.json'),actualCounterexamples=row(HERE/'counterexample-evidence/results.json'),sourceReviewPassed=False,grantsActionOrRuntimeAuthority=False))
for r in hostfiles:assert row(r['path'])==r
assert row(current['path'])==current and row(old['path'])==old
files=[row(p,True)for p in sorted(HERE.rglob('*'))if p.is_file()and p.name!='index.json']
assert not any(p.is_symlink()for p in HERE.rglob('*'))
write('index.json',dict(schemaVersion=1,state='SEALED_HELD_OPTIONAL_PACKAGE_BUNDLER_IMPLEMENTATION_REVIEW_V1',files=files))
print(json.dumps(dict(index=row(HERE/'index.json'),members=len(files),results=row(HERE/'results.json'),contract=row(HERE/'result-contract.json'),correction=row(HERE/'required-correction-contract.json'),reviewedSourceSha256=current['sha256'],hostOutputFiles=len(hostfiles),sourceReviewPassed=False)))
