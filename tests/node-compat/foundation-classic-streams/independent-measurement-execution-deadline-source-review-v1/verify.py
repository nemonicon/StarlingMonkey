#!/usr/bin/env python3
"""Independent source/data reader; no owner code imports or action mains."""
import ast
import difflib
import hashlib
import json
import math
from pathlib import Path
import stat

HERE=Path(__file__).resolve().parent
FAMILY=HERE.parent
OWNER=FAMILY/'measurement-execution-deadline-amendment-v1'
BASE=FAMILY/'measurement-execution-candidate-v1'
HELPER=FAMILY/'measurement-correctness-persistence-amendment-v1'
seen={}
def checked(path,expected=None,size=None):
 path=Path(path);before=path.lstat();assert stat.S_ISREG(before.st_mode),str(path)
 digest=hashlib.sha256()
 with path.open('rb')as stream:
  for chunk in iter(lambda:stream.read(1024*1024),b''):digest.update(chunk)
 after=path.lstat();assert(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),str(path)
 value=digest.hexdigest()
 if expected is not None:assert value==expected,str(path)
 if size is not None:assert before.st_size==size,str(path)
 seen[str(path)]={'path':str(path),'sha256':value,'bytes':before.st_size};return value
def load(path):checked(path);return json.loads(Path(path).read_bytes())
def indexed(root,pin,count=None):
 checked(root/'index.json',pin);document=load(root/'index.json')
 if count is not None:assert len(document['files'])==count
 for row in document['files']:checked(root/row['path'],row['sha256'],row['bytes'])
 return document
indexed(OWNER,'b0975b544506df8000e21de1bfdc8c4fc07c38d01a850fd56f7be422bee339a9',25)
indexed(BASE,'4b6fdfa51d41120865114b0e8558dbc6e97fdd63007e108a35c264d20bc0280d',43)
indexed(HELPER,'60a8687e9b6bfff4c68df2a36e9dd47ad0f5cd327441f8cf32d63caa67518ba8',35)
peer=FAMILY/'independent-measurement-execution-source-review-v1'
indexed(peer,'96bc44a3c926b3ef4c1f99ba009629b88118162ff54d6358ef0ce29e4e0bd4e0',9)
old_review=load(peer/'results.json');assert len(old_review['mandatoryFindings'])==1 and old_review['mandatoryFindings'][0]['id']=='M1'
manifest=load(OWNER/'input-freeze.json');assert len(manifest['inputs'])==7112
assert manifest['pairAndTimingAuthorityRemainNull']is True
for row in manifest['inputs']:
 path=Path(row['path']);assert path.is_absolute();checked(path,row['sha256'],row['bytes'])

derivations=load(OWNER/'host-derivations.json');assert len(derivations['files'])==3
host_names=[]
for row in derivations['files']:
 name=row['path'];before=(BASE/name).read_text();after=(OWNER/'proposed'/name).read_text()
 assert hashlib.sha256(before.encode()).hexdigest()==row['beforeSha256']
 assert hashlib.sha256(after.encode()).hexdigest()==row['afterSha256']
 a,b=before.splitlines(True),after.splitlines(True)
 opcodes=difflib.SequenceMatcher(None,a,b).get_opcodes()
 assert [list(op)for op in opcodes]==row['opcodes']
 forward=[];reverse=[]
 for tag,i,j,k,l in opcodes:
  if tag=='equal':assert a[i:j]==b[k:l]
  forward.extend(a[i:j]if tag=='equal'else b[k:l])
  reverse.extend(b[k:l]if tag=='equal'else a[i:j])
 assert ''.join(forward)==after and ''.join(reverse)==before
 patch=''.join(difflib.unified_diff(a,b,fromfile='a/'+name,tofile='b/'+name))
 assert patch==(OWNER/row['patch']).read_text()and row['reverseExact']is True
 host_names.append(name)
assert sorted(host_names)==['collect-worker.mjs','measure.mjs','prepare-correctness.mjs']
activation=load(OWNER/'activation-derivation.json');before=(BASE/'activate.py').read_text();after=(OWNER/'activate.py').read_text()
assert hashlib.sha256(before.encode()).hexdigest()==activation['beforeSha256']
assert hashlib.sha256(after.encode()).hexdigest()==activation['afterSha256']
assert(OWNER/'history/base-activate.py').read_text()==before
value=before;positions=[]
for edit in activation['edits']:
 assert edit['count']==1 and value.count(edit['old'])==1
 at=value.index(edit['old']);positions.append(at);value=value[:at]+edit['new']+value[at+len(edit['old']):]
assert len(positions)==5 and value==after
for at,edit in reversed(list(zip(positions,activation['edits']))):
 assert value[at:at+len(edit['new'])]==edit['new'];value=value[:at]+edit['old']+value[at+len(edit['new']):]
assert value==before
assert(OWNER/'authority.py').read_bytes()==(BASE/'authority.py').read_bytes()
helper=load(OWNER/'owned-host-derivation.json');original=(HELPER/'durable-host.mjs').read_text();owned=(OWNER/'owned-host.mjs').read_text()
assert len(helper['edits'])==1 and original.count('timeoutMs<=600000')==1
assert original.replace('timeoutMs<=600000','timeoutMs<=7200000')==owned
assert hashlib.sha256(original.encode()).hexdigest()==helper['beforeSha256']and hashlib.sha256(owned.encode()).hexdigest()==helper['afterSha256']
assert owned.index('await persistFile({output,write,path:terminalPath')<owned.index('return{...outcome,terminalPath,stdout:')

prepare=(OWNER/'proposed/prepare-correctness.mjs').read_text()
measure=(OWNER/'proposed/measure.mjs').read_text()
collector=(OWNER/'proposed/collect-worker.mjs').read_text()
policy=(OWNER/'deadline-policy.mjs').read_text()
audit=(OWNER/'audit-inputs.mjs').read_text()
assert 'spawnSync'not in prepare and 'spawnSync'not in collector
observe=prepare[prepare.index('async function observeCall('):prepare.index('async function identity(')]
assert observe.index("await progress(arm,'call-start'")<observe.index('await invoke()')
assert observe.index("id+'.raw.txt'")<observe.index('JSON.parse(raw)')<observe.index("id+'.observed.json'")
assert "observeCall('inspect'"in prepare and 'for(let i=0;i<14;i++)'in prepare and 'round<3'in prepare
assert prepare.index("await progress(arm,'fresh-Wasmtime-collected'")<prepare.index('assert.equal(actual.terminalExitZeroObserved,true')
assert prepare.index("'wt-'+(i+2)+'.observed.json'")<prepare.index("label:'fresh-WT-'+i")
assert prepare.index("'failure-before-source-audit.json'")<prepare.index('finally{try{postAudit=await runOwnedCommand(')
assert 'if(!operationFailure)operationFailure=auditError' in prepare and 'if(operationFailure)throw operationFailure' in prepare
assert '2*1024**3'in prepare and '800*1024**2'in prepare
assert "arm-results.partial.json"in prepare and 'partialObservationOnly:true'in prepare
assert 'timeoutMs:deadlinePolicy.publicCaseMs'in prepare and 'timeoutMs:deadlinePolicy.sourceAuditMs'in prepare
assert collector.index('await persistFile(')<collector.index('await runOwnedCommand(')
assert 'outcome.terminalExitZeroObserved&&outcome.ownedGroupGone'in collector
assert measure.index("'.budget-plan.json'")<measure.index('assert(Object.values(budgets).every(row=>row.admitted)')<measure.index('for(let repetition=0;repetition<3;repetition++)')
assert 'budgets[arm].requestedMs,budgets[arm]'in measure
assert "deadlinePolicy.pilotMs"in measure and "deadlinePolicy.sourceAuditMs"in measure
assert measure.index("'failure-before-source-audit.json'")<measure.index('}finally{')
assert 'failure??=error'in measure and 'if(failure)throw failure'in measure
assert 'assert.equal(samples.length,126)'in measure and 'assert.equal(calibrations.length,21)'in measure
assert 'for(let i=0;i<3;i++)'in measure and 'sample<7'in measure
assert 'Math.min'not in policy and '7200000' in policy
for term in ['pilot.firstBatchMs*iterations*(3+7)','pilot.firstBatchMs*iterations','120000+2*observedStartupAndEvidenceMs','Math.ceil(2*sampleAndWarmupMs+firstBatchAllowanceMs+startupAllowanceMs)','admitted:requestedMs<=7200000']:
 assert term in policy
def expected_budget(batch,whole,n):return math.ceil(2*(batch*n*10)+batch*n+120000+2*max(0,whole-batch))
assert expected_budget(10,1000,16)==125340 and expected_budget(500000,510000,1)==10640000>7200000
assert "await import('./runtime-preflight.mjs')"in audit and 'executionPreflight('in audit
assert 'instance.exports'not in audit and 'componentize'not in audit and 'batch('not in audit

pair=load(BASE/'future-pair-authority.json');phase=load(BASE/'future-measurement-phase.json')
assert pair['variants']=={'benchmark-classic-on':None,'benchmark-classic-off':None}and pair['rootPairReview']is None
assert all(phase[key]is None for key in ['pairPinsSha256','actualCorrectness','freshFull20And14','freshReplay','freshHttpBothHosts','components','coordinatedWindow'])
assert phase['timingAllowed']is False
names_start="names=['protocol.mjs'";names_end='payload={name:regular('
assert after[after.index(names_start):after.index(names_end)]==before[before.index(names_start):before.index(names_end)]
assert 'load_pair(pin_path' in after and after.index('load_pair(pin_path')<after.index('base_rows=indexed(BASE,BASE_INDEX)')<after.index("spec_from_file_location('benchmark_common'")
assert "payload[name]=regular(HERE/'proposed'/name)"in after and "['deadline-policy.mjs','owned-host.mjs','audit-inputs.mjs']"in after
assert 'metadataRewritten' in after and "OUTPUT=HERE.parent/'measurement-execution-activated-v2'"in after
assert 'stage.mkdir(exist_ok=False)'in after and "open('xb')"in after and 'stage.rename(OUTPUT)'in after
assert not(FAMILY/'measurement-execution-activated-v2').exists()and not(FAMILY/'measurement-execution-activated-v2.staging').exists()
witness=load(OWNER/'public-case5-deadline-witness.json')
assert checked(OWNER/'public-case5-deadline-witness.json')=='793a2f0de42b931fac12c55c570a888add9ced3c2e9b25b09e8bef70363ce45e'
assert witness['originalFailedRunCaseStillUnknown']is True and witness['fullTwentyPlusFourteenPassed']is False and witness['deadlineAdequateForAllCasesClaim']is False
source_tests=load(OWNER/'evidence/source-tests.json');deadline_tests=load(OWNER/'evidence/deadline-tests.json');syntax=load(OWNER/'evidence/syntax-results.json')
assert source_tests['passed']==36 and len(source_tests['checks'])==36
assert deadline_tests['passed']==18 and len(deadline_tests['checks'])==18
assert source_tests['ownerCommandsOrProbesOrActionMainsOrArtifactVerifiersOrGuestOrTimingExecuted']is False
assert deadline_tests['commandsOrProbesOrActualTimingOrGuestExecuted']is False
python=[]
for path in OWNER.glob('*.py'):ast.parse(path.read_text());python.append(path.name)
for row in list(seen.values()):checked(row['path'],row['sha256'],row['bytes'])
report={'schemaVersion':1,'state':'INDEPENDENT_MEASUREMENT_EXECUTION_DEADLINE_SOURCE_REVIEW_PASSED_NO_ACTIONS','ownerIndexSha256':checked(OWNER/'index.json'),'ownerFiles':25,'preparationInputs':7112,'hostAfterimagesReconstructedExactly':host_names,'activationForwardReverseEdits':5,'ownedHelperExactCeilingChanges':1,'sourceM1ResolvedByMandatoryReplacement':True,'old4b6StillRequiresAmendment':True,'unchanged26PayloadAncestryAndGuestProvidersOraclesProtocol':True,'nullPairAndPhasePreserved':True,'onOnlyPinsCannotAuthorizePairOrTiming':True,'caseAndPilotDeadlineMs':600000,'sourceAuditDeadlineMs':180000,'workerHardMaxMs':7200000,'budgetFormula':'ceil(2*pilotBatchMs*N*(3+7) + pilotBatchMs*N +120000 +2*max(0,pilotWholeProcessMs-pilotBatchMs))','wholeFamilyRefusesBeforeWorkersIfEitherBudgetExceedsCap':True,'nClippingOrSamplesOmitted':False,'protocolCounts':{'pilotWorkers':42,'timedWorkers':126,'repetitionsPerArmFamilyComparison':3,'warmups':3,'samplesPerWorker':7,'sharedNBounds':[1,16]},'completeRawObservedTerminalEvidenceBeforeValidation':True,'originalFailureSavedBeforeBoundedAudit':True,'sameOwnedProcessCleanupAndLimitSemanticsAs60a':True,'ownerStoredChecksAuthenticatedNotRerun':{'source':36,'deadline':18,'syntax':11,'inheritedBenignChildren':17},'pythonASTParsed':sorted(python),'concreteSourceBlockers':[],'ownerImportsOrActionMainsOrProbesOrPreflightExecuted':False,'nativeGuestComponentizerHostOrTimingExecuted':False,'runtimeAcceptanceClaim':False,'performanceClaim':False,'futureGateStatus':'Actual four-arm common correctness, full20/14, replay/followon, same-byte both-hostHTTP, artifact review, reviewed pair and Root timing phase/window remain separate mandatory gates.','limitations':['Source review only; fixed larger bounds do not establish adequacy for every case.','Existing in-process Jco calls are not made interruptible; durable starts identify their active call.','Storage/crash/concurrent-writer/general cleanup/reset/ALS guarantees are not claimed.','Only public process RSS; capacity/grow unavailable, raw controls unsubtracted, no C++ stream-state-machine claim.'],'verifiedFiles':sorted(seen.values(),key=lambda r:r['path'])}
with(HERE/'results.json').open('x')as stream:json.dump(report,stream,indent=2);stream.write('\n')
print(json.dumps({'state':report['state'],'verifiedPaths':len(seen),'ownerFiles':25,'inputs':7112,'hostAfterimages':3,'activationEdits':5,'concreteSourceBlockers':0}))
