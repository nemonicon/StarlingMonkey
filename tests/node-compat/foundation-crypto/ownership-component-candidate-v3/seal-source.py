#!/usr/bin/env python3
"""Finite source/data seal only. No bootstrap/component/key or publishing action."""
import json,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent;K=D.parent;old=K/'ownership-component-candidate-v2'
def row(p):
 p=Path(p);h=hashlib.sha256();size=0
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b);size+=len(b)
 return {'path':str(p),'sha256':h.hexdigest(),'bytes':size}
def save(n,v):
 p=D/n
 if p.exists():raise RuntimeError('Fresh seal only '+n)
 p.write_text(json.dumps(v,indent=2)+'\n')
inputs={}
def add(p,role):
 r=row(p);prior=inputs.get(r['path']);assert prior is None or all(prior[k]==r[k] for k in ['path','sha256','bytes']);inputs[r['path']]={**r,'role':role}
for r in json.loads((old/'input-freeze.json').read_bytes())['files']:add(r['path'],'inherited-original-preparation-context')
add(old/'index.json','immutable-v2-HOLD-source-index')
for r in json.loads((old/'index.json').read_bytes())['files']:add(old/r['path'],'immutable-v2-source-member')
c=json.loads((D/'bootstrap-context.json').read_bytes());lineage=json.loads((D/'lineage.json').read_bytes())
for proof,role in [(c['actualBootstrapReview'],'actual-completed-read-only-bootstrap-proof'),(lineage['sourceHold'],'immutable-v2-independent-source-HOLD')]:
 ix=proof['index'];add(ix['path'],role+'-index')
 for r in json.loads(Path(ix['path']).read_bytes())['files']:add(Path(ix['path']).parent/r['path'],role+'-member')
for name in ['actualContract','actualFrame','actualRootResults','configuredSourceIndex','configuredBootstrapEntry','configuredToolPins','configuredPolicy']:add(c[name]['path'],'explicit-context-'+name)
ix=c['configuredSourceIndex']
for r in json.loads(Path(ix['path']).read_bytes())['files']:add(Path(ix['path']).parent/r['path'],'actual-configured68b6-member')
tools=json.loads(Path(c['configuredToolPins']['path']).read_bytes());policy=json.loads(Path(c['configuredPolicy']['path']).read_bytes());assert len(tools['toolDependencies'])==922 and len(policy['expectedNativeSourceManifest'])==355
for r in tools['toolDependencies']:add(Path(c['configuredSourceRoot'])/r['path'],'actual-configured-tool922')
for r in policy['expectedNativeSourceManifest']:
 for root in [c['configuredSourceRoot'],c['sourceRoot']]:add(Path(root)/r['path'],'actual-configured-or-frozen-native355')
save('input-freeze.json',{'schemaVersion':1,'state':'CRYPTO_COMPONENT_V3_EXPLICIT_ORIGINAL_CONFIGURED_FROZEN_SOURCE_INPUTS','files':list(inputs.values()),'originalPreparationReferencesAreNotRelocated':True,'configuredNativeSources':355,'configuredTools':922,'frozenNativeSources':355,'bootstrapOrComponentOrKeyActionInvoked':False})
context=json.loads((D/'evidence/context.stdout.log').read_bytes());options=json.loads((D/'evidence/options.stdout.log').read_bytes());source=json.loads((D/'evidence/source.stdout.log').read_bytes());syntax=json.loads((D/'evidence/syntax.json').read_bytes());deriv=json.loads((D/'source-derivations.json').read_bytes())
save('results.json',{'schemaVersion':1,'state':'CRYPTO_OWNER355_COMPONENT_V3_SOURCE_ONLY_CONTEXT_CORRECTION','sourcePreparationPassed':True,'pureContextChecks':context['checks'],'pureOptionsChecks':options['checks'],'sourceDataChecks':source['checks'],'parseChecks':len(syntax['records']),'actualPositiveValuesAreRetainedJsonDataOnly':True,'originalPrepEntryKeptAsDataOnly':True,'staged355ExecutableIndexAndTool922BeforeImport':True,'genuineReturnedFrameMustRemainUnchanged':True,'adapterCorrectionRetained':True,'sourceHeadAtResumption':'e7c6e2ce4f430811b90bcad77620c1e549963ca0','historicalBaselineIdentifier':'54b','historicalNativeMetadataRewritten':False,'sourceIndependentReview':None,'rootComponentAuthority':None,'actualNewComponent':None,'keyExportAuthority':None,'genuineBootstrapInvoked':False,'componentizerJcoOrGeneratedModuleInvoked':False,'keyCryptoGcGuestOrHostInvoked':False,'operationalAdmission':False,'runtimeAcceptanceClaim':False})
save('source-receipt.json',{'schemaVersion':1,'state':'SEALED_CRYPTO_COMPONENT_V3_CONFIGURED_EXECUTABLE_CONTEXT_SOURCE','sourceOnly':True,'parentSourceIndexSha256':lineage['previousSourceIndex']['sha256'],'parentHoldIndexSha256':lineage['sourceHold']['index']['sha256'],'actualReadOnlyBootstrapReviewIndexSha256':c['actualBootstrapReview']['index']['sha256'],'actualTwoContextContractSha256':c['actualContract']['sha256'],'guardAfterimages':1,'exactGuardEdits':len(deriv['guard']['edits']),'unchangedCopies':len(deriv['unchangedCopies']),'sourceInputs':len(inputs),'futureOutput':'/private/tmp/starling-node-compat/crypto-owner355-component-v3','sourcePeerAndRootAction':None,'ownerActionsInvoked':False})
files=[]
for p in sorted(D.rglob('*')):
 if p.is_file() and p.name!='index.json':
  r=row(p);files.append({'path':str(p.relative_to(D)),'sha256':r['sha256'],'bytes':r['bytes']})
save('index.json',{'schemaVersion':1,'state':'SEALED_SOURCE_ONLY_CRYPTO_COMPONENT_V3_CONFIGURED_CONTEXT_CORRECTION','files':files,'sourceOnly':True,'ownerActionsInvoked':False})
for r in files:assert row(D/r['path'])['sha256']==r['sha256']
for r in inputs.values():assert all(row(r['path'])[k]==r[k] for k in ['path','sha256','bytes'])
print(json.dumps({'index':row(D/'index.json'),'results':row(D/'results.json'),'receipt':row(D/'source-receipt.json'),'files':len(files),'inputs':len(inputs)}))
