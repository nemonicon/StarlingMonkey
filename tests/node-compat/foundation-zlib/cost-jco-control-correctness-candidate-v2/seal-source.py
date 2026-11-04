#!/usr/bin/env python3
"""Thin immutable source seal/data rehash. No control/helper/guest action."""
import json,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent;Z=D.parent;old=Z/'cost-jco-control-correctness-candidate-v1'
def row(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def save(n,v):
 p=D/n
 if p.exists():raise RuntimeError('Fresh seal only '+n)
 p.write_text(json.dumps(v,indent=2)+'\n')
inputs={}
def add(p,role):
 r=row(p);inputs[r['path']]={**r,'role':role}
for r in json.loads((old/'input-freeze.json').read_bytes())['files']:add(r['path'],'inherited-exact-original-preparation-context')
add(old/'index.json','unchanged-donor-source-index')
for r in json.loads((old/'index.json').read_bytes())['files']:add(old/r['path'],'unchanged-donor-source')
lineage=json.loads((D/'lineage.json').read_bytes())
for name in ['rootFailure','requiredCorrection','originalSourcePeerIndex']:add(lineage[name]['path'],'actual-original-failure-or-history')
ix=lineage['failureReview']['index'];add(ix['path'],'actual-independent-failure-proof-index')
for r in json.loads(Path(ix['path']).read_bytes())['files']:add(Path(ix['path']).parent/r['path'],'actual-independent-failure-proof-member')
actual=json.loads((D/'evidence/directory.stdout.log').read_bytes())
for p in Path(actual['root']).rglob('*'):
 if p.is_file():add(p,'actual-benign-directory-regression-not-guest')
save('input-freeze.json',{'schemaVersion':1,'state':'THIN_CONTROL_V2_ORIGINAL_CONTEXT_SOURCE_INPUTS','files':list(inputs.values()),'relocationIsNotActivation':True,'ownerGuestOrCodecActionsInvoked':False})
source=json.loads((D/'evidence/source.stdout.log').read_bytes());syntax=json.loads((D/'evidence/syntax.json').read_bytes())
save('results.json',{'schemaVersion':1,'state':'COST_CONTROL_DIRECTORY_V2_SOURCE_CANDIDATE_ONLY','sourcePreparationPassed':True,'sourceDataChecks':source['checks'],'parseChecks':len(syntax['records']),'actualBenignDirectoryChecks':actual['checks'],'benignHostChildrenStarted':1,'missingDirActualENOENT':True,'preparedDirActualRawZeroOwnedCleanup':True,'controlWorkersInvoked':False,'genuinePreflightInvoked':False,'guestOrProviderOrCodecInvoked':False,'actualNewControlResults':None,'sourceIndependentReview':None,'rootActionAuthority':None,'operationalAdmission':False,'runtimeAcceptanceClaim':False})
save('source-receipt.json',{'schemaVersion':1,'state':'SEALED_THIN_CONTROL_DIRECTORY_V2_SOURCE','sourceOnly':True,'oldSourceIndexSha256':lineage['originalSourceIndex']['sha256'],'failureIndexSha256':ix['sha256'],'derivedAfterimages':2,'exactEditOperations':10,'originalWorkerLoaderCollectorPreserved':True,'sourceInputs':len(inputs),'newOutputRoot':'/private/tmp/starling-node-compat/zlib-cost-jco-control-correctness-v2','newRootAction':None,'actualGuestControlActionsInvoked':False})
files=[]
for p in sorted(D.rglob('*')):
 if p.is_file() and p.name!='index.json':
  r=row(p);files.append({'path':str(p.relative_to(D)),'sha256':r['sha256'],'bytes':r['bytes']})
save('index.json',{'schemaVersion':1,'state':'SEALED_SOURCE_ONLY_CONTROL_DIRECTORY_V2_CORRECTION','files':files,'sourceOnly':True,'ownerGuestActionsInvoked':False})
for r in files:assert row(D/r['path'])['sha256']==r['sha256']
for r in inputs.values():assert all(row(r['path'])[k]==r[k] for k in ['path','sha256','bytes'])
print(json.dumps({'index':row(D/'index.json'),'results':row(D/'results.json'),'receipt':row(D/'source-receipt.json'),'files':len(files),'inputs':len(inputs)}))
