"""Seal compact UNEXECUTED diagnostic caller Source. No tool/API invocation."""
from pathlib import Path
import ast,hashlib,json,os,subprocess
OWN=Path(__file__).resolve().parent
assert not (OWN/'index.json').exists()
def read(n):return json.loads((OWN/n).read_bytes())
def desc(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
refs=read('references.json');root=read('root-authority.template.json');root['entrySha256']=desc(OWN/'entry.mjs')['sha256'];save('root-authority.template.json',root)
assert root['state'].startswith('UNISSUED_')and root['sourceIndex']is root['sourceReviewedByRoot']is root['artifactReview']is None
source_test=read('source-test.stdout.json');failure_test=read('failure-test.stdout.json')
assert source_test['readOnlyLedgerRows']==21451 and source_test['pureCases']==24 and failure_test['pureNonfiniteThrowCases']==3
assert (OWN/'source-test.stderr.log').read_bytes()==(OWN/'failure-test.stderr.log').read_bytes()==b''
node=refs['node'];assert desc(node['path'])==node
grammar=[]
for name in ['entry.mjs','worker.mjs','test-source.mjs','test-failure-records.mjs']:
 argv=[node['path'],'--check',str(OWN/name)];r=subprocess.run(argv,env={k:v for k,v in os.environ.items()if k not in['NODE_OPTIONS','NODE_PATH']},capture_output=True,timeout=30);(OWN/(name+'.grammar.stdout.log')).write_bytes(r.stdout);(OWN/(name+'.grammar.stderr.log')).write_bytes(r.stderr);assert r.returncode==0 and not r.stderr;grammar.append(dict(argv=argv,rawExitCode=0,stdoutBytes=len(r.stdout),stderrBytes=0))
for p in OWN.glob('*.py'):ast.parse(p.read_bytes())
save('grammar-results.json',dict(schemaVersion=1,state='SOURCE_GRAMMAR_ONLY_PASSED',records=grammar,pythonAsts=2,packageOrFixtureOrGeneratedImports=False,compilerOrGuestOrCryptoExecuted=False))
save('preparation-history.json',dict(schemaVersion=1,state='SEALED_UNEXECUTED_EXPERIMENTAL357_CALLER_SOURCE',sourceOnly=True,actualArtifactReviewKnownAsData=True,rootAuthority=None,componentBuilt=False,guestOrCryptoExecuted=False,publicProfileAdmission=False))
save('results.json',dict(schemaVersion=1,state='UNEXECUTED_EXPERIMENTAL_HASH_HMAC357_DIAGNOSTIC_CALLER_SOURCE_COMPLETE_V1',sourceOnly=True,sourcePrepared=True,nativeEngine=refs['nativeEngine'],nativeMetadata=refs['nativeMetadata'],nativeSourceFiles=357,rawMetadataFields=83,selectedWholeManifests=12,fixtureSourceIndex=refs['fixtureIndex'],knownNativeArtifactReview=refs['knownArtifactReview'],knownNativeArtifactContract=refs['knownArtifactContract'],comparatorSource=refs['comparator'],sourceReadGuardRows=21451,toolTreeDigests=3,pureFailureCases=27,nodeGrammarChecks=4,pythonAsts=2,separateOwnedPhases=['bundle','construct','jco'],applicationArms=['bundled','raw-fixture'],fullComponentCaptureBeforeInterfaceAudit=True,synchronousScalarCallEnforced=True,rawBeforeSemantics=True,wholeComparatorReturnRetained=True,actualHelperTerminalFieldsEnforced=True,failureAttemptsAndReturnsRecorded=True,retainedCallOrdinals=[1,2,3],freshCallOrdinals=[1],ordinaryJcoCallsPlanned=4,stockWasmtimeImplemented=False,additionalRuntimeTransportsRequireSeparateSourceOrRootReview=True,sourceReviewedByRoot=None,sourceIndependentReview=None,rootAuthority=None,componentizerInvoked=False,packageImported=False,generatedApplicationImported=False,fixtureOrGuestOrCryptoExecuted=False,oracleRerun=False,nativeBuildOrFreeze=False,fullNativeMetadataClonedIntoOldFrame=False,publicProfileAdmission=False,liveEvpSnapshotAdmission=False,freezeOrReleaseOrReuseOrSecurityOrCostAcceptance=False,qualifications=['Direct Root Source review plus actual issued config is required; templates grant nothing.','Current read-only proof preserves original recipe0/parents1+1/preservationfalse; no old BUILD-success frame is created.','The full native ledger was replayed only by read/hash utilities in Source tests; no admission/helper was called.','Shared diagnostic bookkeeping was exercised with synthetic throws/returns, not generated guest calls.','Extra generated utility exports need actual type/loading review before runtime Root grant.','Bundled aliases test canonicalization; only the tagged raw-fixture arm can observe direct bare/prefixed guest resolution.','Live EVP INIT safety, snapshots, secret erasure/finalizers, full Nodecrypto/Next, reproducible freeze and adoption remain open.']))
save('source-receipt.json',dict(schemaVersion=1,result=desc(OWN/'results.json'),references=desc(OWN/'references.json'),sourceContract=desc(OWN/'source-contract.json'),grammar=desc(OWN/'grammar-results.json'),sourceGuardAndPureTest=desc(OWN/'source-test.stdout.json'),targetedFailureTest=desc(OWN/'failure-test.stdout.json'),operationalActionsInvoked=False))
rows=[]
for p in sorted(OWN.rglob('*')):
 assert not p.is_symlink()
 if p.is_file():r=desc(p);r['path']=p.relative_to(OWN).as_posix();rows.append(r)
save('index.json',dict(schemaVersion=1,state='SEALED_SOURCE_ONLY_EXPERIMENTAL_CALLER_NO_ACTION_AUTHORITY_V1',files=rows))
assert {r['path']for r in rows}|{'index.json'}=={p.relative_to(OWN).as_posix()for p in OWN.rglob('*')if p.is_file()}
for name in ['index.json','results.json','source-receipt.json']:print(json.dumps(desc(OWN/name)))
