"""Compact delta/grammar seal; never imports an operational module or guest."""
from pathlib import Path
import ast,hashlib,json,os,subprocess
OWN=Path(__file__).resolve().parent
assert not (OWN/'index.json').exists()
def read(p):return json.loads(Path(p).read_bytes())
def desc(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
refs=read(OWN/'references.json');deriv=read(OWN/'derivations.json');parent=Path(refs['parentCallerIndex']['path']).parent
assert desc(parent/'index.json')==refs['parentCallerIndex']
ix=read(parent/'index.json');parent_checks=0
for row in ix['files']:
 p=parent/row['path'];actual=desc(p);assert actual['sha256']==row['sha256'] and actual['bytes']==row['bytes'];parent_checks+=1
assert {p.relative_to(parent).as_posix()for p in parent.rglob('*')if p.is_file()}=={r['path']for r in ix['files']}|{'index.json'}
for item in deriv['files']:
 assert desc(item['before']['path'])==item['before'] and desc(item['after']['path'])==item['after']
 if 'edits'in item:
  before=Path(item['before']['path']).read_text();after=(OWN/item['path']).read_text();forward=before
  for e in item['edits']:assert forward.count(e['before'])==1;forward=forward.replace(e['before'],e['after'])
  assert forward==after;inverse=after
  for e in reversed(item['edits']):assert inverse.count(e['after'])==1;inverse=inverse.replace(e['after'],e['before'])
  assert inverse==before
oldrefs=read(parent/'references.json')
for k,v in oldrefs.items():assert k=='outputPrefix' or refs[k]==v
assert refs['constructorSourceIndex']==refs['parentCallerIndex']
for arm,row in refs['reusedConstructions'].items():
 assert desc(row['rootObservation']['path'])==row['rootObservation'] and desc(row['result']['path'])==row['result'] and desc(row['component']['path'])==row['component']
 r=read(row['result']['path']);assert r['sourceIndex']==refs['constructorSourceIndex'] and r['arm']==arm and r['component']==row['component'] and r['phase']=='construct' and not r['primaryPresent'] and not r['finalErrors']
root=read(OWN/'root-authority.template.json');assert root['entrySha256']==desc(OWN/'entry.mjs')['sha256'] and root['phase']=='jco' and root['state'].startswith('UNISSUED_')
assert root['sourceIndex']is root['sourceReviewedByRoot']is root['ordinaryHashHmacAllowed']is root['artifactReview']is root['actualComponent']is None
node=refs['node'];assert desc(node['path'])==node
env={k:v for k,v in os.environ.items()if k not in ['NODE_OPTIONS','NODE_PATH']};commands=[]
for name in ['entry.mjs','worker.mjs','test-merge.mjs']:
 argv=[node['path'],'--check',str(OWN/name)];r=subprocess.run(argv,env=env,capture_output=True,timeout=30)
 (OWN/(name+'.grammar.stdout.log')).write_bytes(r.stdout);(OWN/(name+'.grammar.stderr.log')).write_bytes(r.stderr)
 commands.append(dict(argv=argv,rawExitCode=r.returncode,stdout=desc(OWN/(name+'.grammar.stdout.log')),stderr=desc(OWN/(name+'.grammar.stderr.log'))));assert r.returncode==0 and r.stdout==r.stderr==b''
argv=[node['path'],str(OWN/'test-merge.mjs')];r=subprocess.run(argv,env=env,capture_output=True,timeout=30)
(OWN/'merge-test.stdout.json').write_bytes(r.stdout);(OWN/'merge-test.stderr.log').write_bytes(r.stderr)
assert r.returncode==0 and r.stderr==b'';test=read(OWN/'merge-test.stdout.json');assert test['checks']==9 and test['bindingCases']==8 and test['operationalEntryOrJcoChildOrGuestOrCryptoInvoked']is False
ast.parse((OWN/'seal-source.py').read_bytes())
save('grammar-results.json',dict(schemaVersion=1,records=commands,pythonAsts=1,operationalImports=False,guestOrCryptoInvoked=False))
save('test-terminal.json',dict(schemaVersion=1,argv=argv,rawExitCode=r.returncode,stdout=desc(OWN/'merge-test.stdout.json'),stderr=desc(OWN/'merge-test.stderr.log'),syntheticSourceFragmentsOnly=True))
contract=dict(schemaVersion=1,state='SOURCE_ONLY_EXPERIMENTAL_CALLER_NOT_ACTION_AUTHORITY_V2',rootStateRequired='ROOT_REVIEWED_EXPERIMENTAL_HASH_HMAC357_DIAGNOSTIC_PHASE_V2',phases=['jco'],rootMustBindExactCallerIndexAndEntry=True,constructorSourceIndex=refs['constructorSourceIndex'],reusedConstructions=refs['reusedConstructions'],outputPrefix=refs['outputPrefix'],retainedJcoCallOrdinals=[1,2,3],freshJcoCallOrdinals=[1],actualExecution=None,publicAdmission=False,snapshotOrReuseOrSecurityOrCostAcceptance=False)
save('source-contract.json',contract)
save('future-source-review-contract.json',dict(schemaVersion=1,requiredFixedValues=dict(state='INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_DIAGNOSTIC_CALLER_SOURCE_REVIEW_PASSED_V2',schemaVersion=1,sourceOnly=True,sourceReviewPassed=True,constructorSourceIndexSha256=refs['constructorSourceIndex']['sha256'],awaitBeforeMergeVerified=True,ownerActionsInvoked=False,hostActionsInvoked=False,runtimeActionsInvoked=False),sourceIndexSha256Rule='Must equal the actual final index.json SHA256 descriptor after this Source seal; never the constructor7fb identity.',actualRuntimeProof=None))
hist=read(OWN/'preparation-history.json');hist['state']='SEALED_UNEXECUTED_SOURCE_ONLY_SUCCESS_MERGE_CORRECTION';save('preparation-history.json',hist)
save('results.json',dict(schemaVersion=1,state='UNEXECUTED_EXPERIMENTAL_HASH_HMAC357_DIAGNOSTIC_CALLER_SOURCE_COMPLETE_V2',sourceOnly=True,sourcePrepared=True,constructorSourceIndex=refs['constructorSourceIndex'],parentSourceIndex=refs['parentCallerIndex'],priorSourceReviewIndex=refs['priorSourceReviewIndex'],priorJcoObservation=refs['priorJcoObservation'],priorJcoPhaseResult=refs['priorJcoPhaseResult'],priorRawSemanticEvidencePassed=True,priorBookkeepingAccepted=False,awaitBeforeMergeImplemented=True,exactReversibleCodeEdits=5,parentPayloadsAuthenticated=parent_checks,unchangedOriginalReferenceFields=True,sourceSeamPureCases=9,constructionBindingPureCases=8,nodeGrammarChecks=3,pythonAsts=1,nativeLedgerOrTooltreeAuthoringReplay=False,reusedConstructions=refs['reusedConstructions'],nativeEngine=refs['nativeEngine'],nativeMetadata=refs['nativeMetadata'],nativeSourceFiles=357,rawMetadataFields=83,selectedWholeManifests=12,separateOwnedPhase='jco',retainedCallOrdinals=[1,2,3],freshCallOrdinals=[1],actualRuntimeProof=None,sourceIndependentReview=None,rootAuthority=None,operationalEntryImported=False,generatedApplicationImported=False,nativeBuildOrRevalidationOrBundleOrConstructionRerun=False,fixtureOrGuestOrCryptoExecuted=False,publicProfileAdmission=False,liveEvpSnapshotAdmission=False,freezeOrReleaseOrReuseOrSecurityOrCostAcceptance=False,qualifications=['New Source tests only the actual changed orchestration seam and finite arm handoff; original full native/tool authorization remains unchanged and executes only under a new Root grant.','The original four raw outputs are positive semantic DATA; original zero counters/import flags remain incorrect and unaccepted.','Both completed constructors keep original7fb identity, distinct from this new runtime Source.','This Source is unexecuted; corrected bookkeeping still requires actual runtime observation.']))
save('source-receipt.json',dict(schemaVersion=1,result=desc(OWN/'results.json'),references=desc(OWN/'references.json'),derivations=desc(OWN/'derivations.json'),sourceContract=desc(OWN/'source-contract.json'),futureSourceReviewContract=desc(OWN/'future-source-review-contract.json'),grammar=desc(OWN/'grammar-results.json'),pureTest=desc(OWN/'merge-test.stdout.json'),testTerminal=desc(OWN/'test-terminal.json'),operationalActionsInvoked=False))
rows=[]
for p in sorted(OWN.rglob('*')):
 assert not p.is_symlink()
 if p.is_file():row=desc(p);row['path']=p.relative_to(OWN).as_posix();rows.append(row)
save('index.json',dict(schemaVersion=1,state='SEALED_SOURCE_ONLY_EXPERIMENTAL_CALLER_NO_ACTION_AUTHORITY_V2',files=rows))
assert {r['path']for r in rows}|{'index.json'}=={p.relative_to(OWN).as_posix()for p in OWN.rglob('*')if p.is_file()}
for n in ['index.json','results.json','source-receipt.json']:print(json.dumps(desc(OWN/n)))
