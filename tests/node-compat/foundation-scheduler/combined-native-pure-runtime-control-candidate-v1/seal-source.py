"""Seal SOURCE only, never issue Root/config or invoke any operational API."""
from pathlib import Path
import ast,hashlib,json
OWN=Path(__file__).resolve().parent
def row(p,relative=False):
 b=p.read_bytes();return{'path':p.relative_to(OWN).as_posix()if relative else str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def dump(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
assert not(OWN/'index.json').exists(),'Immutable after seal'
source=json.loads((OWN/'source-check-results.json').read_bytes());assert source['passed']is True
pure=json.loads((OWN/'evidence/node-2/1.stdout.log').read_bytes());assert pure['passed']is True and pure['cases']==75
for folder in ['node-1','node-2']:
 for p in(OWN/'evidence'/folder).glob('*.terminal.json'):assert json.loads(p.read_bytes())['exitCode']==0
assert json.loads((OWN/'evidence/source-2/terminal.json').read_bytes())['exitCode']==0
ast_count=0
for p in OWN.glob('*.py'):ast.parse(p.read_text(),filename=str(p));ast_count+=1
refs=json.loads((OWN/'references.json').read_bytes());assert not Path(refs['outputRoot']).exists()and not Path(refs['outputRoot']+'-external-root').exists()
assert(OWN/'wave.mjs').read_bytes()==Path(refs['waveDonor']['path']).read_bytes()
dump('preparation-history.json',{'schemaVersion':1,'operationalActionsInvoked':False,
 'stages':['source derivation1, full source check1,8 grammar+75 pure cases','Root draft correction: register failed-child partial tree before terminal assertions','Root draft correction: exact artifact contract state/fixed values and scalar signatures','Complete actual producer input modes/identity/membership bookends','Final derivation3, updated entry grammar+75pure, full source check2'],
 'allExecutedPreparationTestsPassed':True,'targetFixtureOrGeneratedCodeImported':False,'nativeApiOrOwnedWorkloadInvoked':False,
 'modelLimits':'Synthetic future Root/values and injected memory filesystem; no benign child or native/runtime experiment',
 'readerOrTargetFailuresClaimed':False})
result={'schemaVersion':1,'state':'COMBINED355_PRELIMINARY_PURE_CONTROL_SOURCE_READY_UNEXECUTED_V1','sourceOnly':True,
 'independentSourceReview':None,'rootAuthority':None,'actualConfig':None,'actualRuntimeResult':None,
 'scope':'Preliminary genuine combined355 pure ordinary control, not full6/17 scope completion',
 'nativeSourceFiles':355,'externalEmbeddingSources':3,'fullMetadataFields':80,'selectedWholeManifests':11,
 'schedule':{'nodeFixtureOracleCalls':3,'retainedJcoCalls':3,'freshJcoCalls':1,'freshStockWasmtimeCalls':3,'componentValues':7,'totalSuccessfulCapturedValues':10,'freshOrdinal':1},
 'nativeAdmission':{'api':refs['nativeApi'],'sourceIndex':refs['nativeApiSourceIndex'],'actualPureReview':refs['actualPureReview'],'actualPureContract':refs['actualPureContract'],'parentApiInvocationsRequired':1,'childNativeApiInvocations':0,'wholeOriginal9eaaDataPreserved':True,'serializedCallableReused':False},
 'lifecycles':{'outerMonitor':refs['monitorEntry'],'outerParentSeconds':1200,'ownedChildMs':60000,'originalRunOwnedCommandUsed':True,'processesDirectoryBeforeLaunch':True,'partialChildrenRegisteredBeforeTerminal':True,'scope':'One parent native API covers children via full before/final bookends; child authentication is explicitly Source/artifact-only'},
 'checks':{'finiteSourceChecks':source['checks'],'currentFullHashFiles':source['fullHashFiles'],'currentLogicalBytes':source['logicalBytes'],'sourceFamilies':source['families'],'privatePackageFiles':4889,'privatePackageLinks':21,'hostPureModelCases':75,'initialNodeGrammarChecks':8,'updatedEntryGrammarChecks':1,'pythonAstChecks':ast_count,'failedChildPartialMemoryRegression':True},
 'ownerActionsInvoked':False,'hostWorkloadsInvoked':False,'nativeApiInvoked':False,'fixtureOrGeneratedApplicationImported':False,'engineOrGuestInvoked':False,'wasmtimeInvoked':False,'compilerOrPackagerInvoked':False,
 'allNewAuthoritiesUnissued':True,'allSixFixtureGateComplete':False,'fullSeventeenGateComplete':False,'resourceRuntimeExercised':False,'fullNextCompatibility':False,'deploymentAccepted':False,'adoptionAllowed':False,'operationalAdmission':False,'runtimeAcceptanceClaim':False,
 'limits':['No actual oracle/component values exist for this new Source yet','No mapping/transpile/component construction permission; original zero-import pure loading tuple only','Host pure models prove no filesystem failure recovery, runtime feasibility, timer/drop/GC/reset or native ownership behavior','2GiB disk check is start-only;60s child and1200s parent are operational bounds, not timing data','Complete raw retained before semantic comparisons, but failed capture cannot claim full retention','No all6/all17/resource/Next/deployment/adoption completion or permission']}
dump('results.json',result)
dump('source-receipt.json',{'schemaVersion':1,'state':'SOURCE_ONLY_PRESERVATION_RECEIPT_NO_RUNTIME_AUTHORITY','results':row(OWN/'results.json'),'sourceChecks':row(OWN/'source-check-results.json'),'pureEvidence':row(OWN/'evidence/node-2/1.stdout.log'),'sourceInputs':row(OWN/'source-inputs.json'),'derivations':row(OWN/'source-derivations.json'),'predecessorsMutated':False,'allActionSlotsNullOrFalse':True,'sourceMemberRule':'Exclude ONLY own root index.json, include any nested index'})
payload=[row(p,True)for p in sorted(OWN.rglob('*'))if p.is_file()and p not in[OWN/'index.json',OWN/'member-ledger.json']]
dump('member-ledger.json',{'schemaVersion':1,'scope':'all payload except own ledger and only own root index','files':payload})
members=[row(p,True)for p in sorted(OWN.rglob('*'))if p.is_file()and p!=OWN/'index.json'];dump('index.json',{'schemaVersion':1,'files':members})
assert not any(p.is_symlink()for p in OWN.rglob('*'))
assert{p.relative_to(OWN).as_posix()for p in OWN.rglob('*')if p.is_file()}=={r['path']for r in members}|{'index.json'}
assert all(row(OWN/r['path'],True)==r for r in members)
print(json.dumps({'index':row(OWN/'index.json'),'results':row(OWN/'results.json'),'receipt':row(OWN/'source-receipt.json'),'indexedMembers':len(members),'actualFiles':len(members)+1,'targetActionsInvoked':False}))
