#!/usr/bin/env python3
"""Focused source-analysis seal only; not an activation/publisher/HTTP action."""
import json,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent
def row(p):
 p=Path(p);b=p.read_bytes();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
def save(n,v):
 p=D/n
 if p.exists():raise RuntimeError('Fresh seal only '+n)
 p.write_text(json.dumps(v,indent=2)+'\n')
p=json.loads((D/'prerequisites.json').read_bytes());c=json.loads((D/'source-citations.json').read_bytes());inputs={}
for k,v in p['references'].items():inputs[v['path']]={**row(v['path']),'role':'INDEXED_REFERENCE_ONLY_'+k}
for v in c['files']:inputs[v['source']['path']]={**row(v['source']['path']),'role':'ACTUAL_CITED_SOURCE'}
probe=D.parent/'release-host-plan-v1/consumer-http-probe.template.mjs';inputs[str(probe)]={**row(probe),'role':'EXACT_TINY_PROBE_TEMPLATE_ORIGIN'}
save('input-freeze.json',{'schemaVersion':1,'state':'FINITE_SOURCE_ANALYSIS_REFERENCES_NOT_EXECUTION_CLOSURE','files':list(inputs.values()),'nestedConsumedRowsNotFollowedOrRebased':True,'toolTreesNotCopied':True,'fullFuturePhysicalExecutionClosure':None})
source=json.loads((D/'evidence/source.stdout.log').read_bytes());syntax=json.loads((D/'evidence/syntax.json').read_bytes())
save('results.json',{'schemaVersion':1,'state':'FOCUSED_CONSUMERS355_HTTP_SOURCE_ANALYSIS_AND_UNEXECUTED_TEMPLATES','sourceDataChecks':source['checks'],'parseChecks':len(syntax['records']),'genuineNativeRuntimeOnlyData':True,'newRequestFixtureGroups':2,'baselineProtected29Classic19SemanticBodiesChanged':False,'existingHandlerIsLowLevelWASIResourceNotFetchRequest':True,'wireBodyAdapterImplemented':False,'nativeCancelCleanupSourceGapRetained':True,'fullPublisherRunnerClosureImplemented':False,'futureWholePackagingClosure':None,'actualNewBundleComponentPhaseHosts':None,'allActionAuthorities':None,'helperOrOracleOrGuestOrHostInvoked':False,'operationalAdmission':False,'runtimeAcceptanceClaim':False})
save('source-receipt.json',{'schemaVersion':1,'state':'SEALED_FOCUSED_UNEXECUTED_CONSUMERS355_HTTP_SOURCE_PROPOSAL','sourceOnly':True,'references':len(inputs),'genuineRuntimeContextFamilyIndexSha256':p['references']['actualRuntimeContextFamily']['sha256'],'fourPinsSha256':p['references']['reviewedFourPins']['sha256'],'nativeMetadataProjected':False,'oldNativeOrProofsChanged':False,'allActionsRemainClosed':True,'requiredNext':'new finite355 HTTP source/physical closure/publisher/Root scopes, then actual bundle/component/type-only-clock/two-host proofs; wire-body cleanup is separate unresolved gate'})
files=[]
for f in sorted(D.rglob('*')):
 if f.is_file() and f.name!='index.json':
  r=row(f);files.append({'path':str(f.relative_to(D)),'sha256':r['sha256'],'bytes':r['bytes']})
save('index.json',{'schemaVersion':1,'state':'SEALED_SOURCE_ONLY_FOCUSED_CONSUMERS355_HTTP_GATE_PROPOSAL','files':files,'sourceOnly':True,'ownerActionsInvoked':False})
for v in files:assert row(D/v['path'])['sha256']==v['sha256']
for v in inputs.values():assert all(row(v['path'])[k]==v[k] for k in ['path','sha256','bytes'])
print(json.dumps({'index':row(D/'index.json'),'results':row(D/'results.json'),'receipt':row(D/'source-receipt.json'),'files':len(files),'references':len(inputs)}))
