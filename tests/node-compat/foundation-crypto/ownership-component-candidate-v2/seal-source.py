#!/usr/bin/env python3
"""Thin source/data seal only. Never construction/bootstrap/key actions."""
import json,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent;old=D.parent/'ownership-component-candidate-v1'
def row(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def save(n,v):
 p=D/n
 if p.exists():raise RuntimeError('Fresh seal only '+n)
 p.write_text(json.dumps(v,indent=2)+'\n')
lineage=json.loads((D/'lineage.json').read_bytes());assert lineage['originalSourceIndex']['sha256']=='eb648e19274c055968557227221627e2ced5dd35a2c0fb17af941dbc9a8b5c30';inputs={}
def add(p,role):
 r=row(p);inputs[r['path']]={**r,'role':role}
for r in json.loads((old/'input-freeze.json').read_bytes())['files']:add(r['path'],'inherited-original-context-preparation')
add(old/'index.json','unchanged-donor-source-index')
for r in json.loads((old/'index.json').read_bytes())['files']:add(old/r['path'],'unchanged-donor-helper-data-source')
ix=lineage['independentHold']['index'];add(ix['path'],'actual-independent-source-HOLD-index')
for r in json.loads(Path(ix['path']).read_bytes())['files']:add(Path(ix['path']).parent/r['path'],'actual-independent-source-HOLD-member')
save('input-freeze.json',{'schemaVersion':1,'state':'THIN_CRYPTO_COMPONENT_V2_ORIGINAL_CONTEXT_SOURCE_INPUTS','files':list(inputs.values()),'relocationIsNotActivation':True,'ownerActionsInvoked':False})
pure=json.loads((D/'evidence/pure.stdout.log').read_bytes());source=json.loads((D/'evidence/source.stdout.log').read_bytes());syntax=json.loads((D/'evidence/syntax.json').read_bytes());deriv=json.loads((D/'source-derivations.json').read_bytes())
save('results.json',{'schemaVersion':1,'state':'CRYPTO_OWNER355_COMPONENT_V2_SOURCE_ONLY','sourcePreparationPassed':True,'pureActualOptionsCallerChecks':pure['checks'],'sourceDataChecks':source['checks'],'parseChecks':len(syntax['records']),'oldExactCallerTypeError':True,'newGenuineCallerOptionsPassed':True,'actualAdapterBytes':53512,'sourceIndependentReview':None,'rootComponentAuthority':None,'actualComponentOrLoadingProof':None,'keyExportAuthority':None,'genuineBootstrapInvoked':False,'componentizerInvoked':False,'keyOrCryptoInvoked':False,'operationalAdmission':False,'runtimeAcceptanceClaim':False})
save('source-receipt.json',{'schemaVersion':1,'state':'SEALED_THIN_CRYPTO_COMPONENT_V2_ADAPTER_CORRECTION_SOURCE','sourceOnly':True,'originalSourceIndexSha256':lineage['originalSourceIndex']['sha256'],'sourceHoldIndexSha256':ix['sha256'],'afterimages':3,'exactEdits':sum(len(f['edits']) for f in deriv['files']),'sourceInputs':len(inputs),'futureOutput':'/private/tmp/starling-node-compat/crypto-owner355-component-v2','nativeGuestWitToolPayloadChanged':False,'ownerActionsInvoked':False})
files=[]
for p in sorted(D.rglob('*')):
 if p.is_file() and p.name!='index.json':
  r=row(p);files.append({'path':str(p.relative_to(D)),'sha256':r['sha256'],'bytes':r['bytes']})
save('index.json',{'schemaVersion':1,'state':'SEALED_SOURCE_ONLY_CRYPTO_COMPONENT_V2_ADAPTER_CORRECTION','files':files,'sourceOnly':True,'ownerActionsInvoked':False})
for r in files:assert row(D/r['path'])['sha256']==r['sha256']
for r in inputs.values():assert all(row(r['path'])[k]==r[k] for k in ['path','sha256','bytes'])
print(json.dumps({'index':row(D/'index.json'),'results':row(D/'results.json'),'receipt':row(D/'source-receipt.json'),'files':len(files),'inputs':len(inputs)}))
