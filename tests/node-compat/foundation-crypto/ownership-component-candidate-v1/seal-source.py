#!/usr/bin/env python3
"""Finite source/data sealing only. Not a publisher/bootstrap/component/key action."""
import hashlib,json
from pathlib import Path
D=Path(__file__).resolve().parent
EXCLUDED={'index.json','input-freeze.json','source-receipt.json','results.json'}
def row(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def write(n,v):
 p=D/n
 if p.exists():raise RuntimeError('Fresh seal only: '+n)
 p.write_text(json.dumps(v,indent=2)+'\n')
p=json.loads((D/'prerequisites.json').read_bytes());m=json.loads((D/'packaging-context.json').read_bytes());inputs={}
def add(p,kind):
 r=row(p);old=inputs.get(r['path']);assert old is None or all(old[k]==r[k] for k in ['path','sha256','bytes']);inputs[r['path']]={**r,'role':kind}
for key in ['guestIndex','guest','wit','nativeSourceIndex','bootstrapEntry','reviewedNativePins','nativeRootReview','node']:add(p[key]['path'],'original-context-source-or-reviewed-data')
for key in ['guestIndex','nativeSourceIndex']:
 ix=p[key];data=json.loads(Path(ix['path']).read_bytes())
 for member in data['files']:add(Path(ix['path']).parent/member['path'],'immutable-parent-indexed-source')
for key in ['guestReview','nativeReview','publicationReview']:
 ix=p[key]['index'];add(ix['path'],'actual-indexed-independent-proof');data=json.loads(Path(ix['path']).read_bytes())
 for member in data['files']:add(Path(ix['path']).parent/member['path'],'actual-indexed-independent-proof-member')
add(m['publicationIndex']['path'],'pinned-publication-index-not-native-authority')
for member in m['files']:add(Path(m['publicationRoot'])/member['path'],'actual-physical-packaging-tool-source')
for n in ['authority.mjs','proofs.mjs','durable.mjs','durable-host.mjs']:add(D.parent.parent/'foundation-zlib/cost-component-candidate-v1'/n,'unchanged-or-exact-prelude-mechanism-origin')
write('input-freeze.json',{'schemaVersion':1,'state':'SOURCE_PREPARATION_ORIGINAL_CONTEXT_INPUTS','relocationIsNotActivation':True,'files':list(inputs.values()),'packagingLinksCapturedIn':'packaging-context.json','ownerActionsInvoked':False})
pure=json.loads((D/'evidence/pure.stdout.log').read_text());source=json.loads((D/'evidence/source.stdout.log').read_text());syntax=json.loads((D/'evidence/syntax.json').read_text())
write('results.json',{'schemaVersion':1,'state':'CRYPTO_OWNER355_COMPONENT_SOURCE_CANDIDATE_ONLY','sourcePreparationPassed':True,'pureChecks':pure['checks'],'sourceDataChecks':source['checks'],'parseChecks':len(syntax['records']),'packagingPhysicalFiles':4934,'toolFiles':4890,'knownToolLinks':22,'nativeBootstrapDataNormalOnly':True,'componentBuildAuthority':None,'actualComponent':None,'keyExportAuthority':None,'actualLoadingOrWasmtimeProof':None,'positiveBootstrapInvoked':False,'componentizerInvoked':False,'generatedModuleImported':False,'keyOrCryptoOperationsInvoked':False,'workerInvoked':False,'operationalAdmission':False,'runtimeAcceptanceClaim':False})
write('source-receipt.json',{'schemaVersion':1,'state':'SEALED_UNEXECUTED_CRYPTO_OWNER355_COMPONENT_ACTION_SOURCE','sourceOnly':True,'inputs':len(inputs),'futureComponentOutput':'/private/tmp/starling-node-compat/crypto-owner355-component-v1','normalEngineSha256':p['normalEngineSha256'],'nativeSourceFiles':355,'physicalPackagingToolFileRows':4934,'mechanisms':'mechanisms.json','sourcePeerAndRootComponentAuthority':None,'actualComponentOrKeyResult':None,'nativeOrComponentOrKeyActionsInvoked':False})
files=[]
for f in sorted(D.rglob('*')):
 if f.is_file() and f.name!='index.json':
  b=f.read_bytes();files.append({'path':str(f.relative_to(D)),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)})
write('index.json',{'schemaVersion':1,'state':'SEALED_SOURCE_ONLY_CRYPTO_OWNER355_COMPONENT_CANDIDATE','files':files,'sourceOnly':True,'ownerActionsInvoked':False})
for f in files:assert row(D/f['path'])['sha256']==f['sha256']
for r in inputs.values():assert all(row(r['path'])[k]==r[k] for k in ['path','sha256','bytes'])
print(json.dumps({'index':row(D/'index.json'),'results':row(D/'results.json'),'receipt':row(D/'source-receipt.json'),'files':len(files),'inputs':len(inputs)}))
