"""Supplemental actual evidence/current parent input read/hash checks only."""
from pathlib import Path
import hashlib,json,os
P=Path(__file__).resolve().parent;N=Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-crypto/ownership-gc-native-candidate-v2')
def row(p):
 p=Path(p);h=hashlib.sha256();n=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b);n+=len(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=n)
def exact(r):
 p=Path(r['path']);a=p.stat();v=row(p);b=p.stat();assert (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns)
 assert v=={k:r[k]for k in ['path','sha256','bytes']};return v
spec=json.loads((P/'actual-evidence-inputs.json').read_bytes());rootrow=dict(path=str(N.parent/'ownership-gc-v2-stage-root-results.json'),sha256='77e795e7f5c27754d70028ff62c4358a8cfa3b5ffd7c80e3f554d14478d4e470',bytes=2832);exact(rootrow);root=json.loads(Path(rootrow['path']).read_bytes());authority=json.loads(Path(spec['rootAuthority']['path']).read_bytes())
assert spec['genericMonitorSourceIndex']['sha256']=='71b7f8e54ae2e21d6673d054a20efa7b1e00409d22d8af7c5b064ad9a6380ddf'
assert spec['stageControllerSourceIndex']['sha256']=='29d59208114b7cb0aed21be2fe09bd35a1efc9de841d49157e3e83378790700d'
assert spec['controllerReview']['index']['sha256']=='e3c0589e199821bddae9693590c5da79d818eaad316fa91ed71c7ed3eb128a83' and spec['controllerReview']['result']['sha256']=='e00ee2b096987d8c28c78c7879020e53fe31dce0c60a156df9648d53312093f2'
assert authority['externalControllerIndex']==spec['stageControllerSourceIndex']and authority['genericMonitorIndex']==spec['genericMonitorSourceIndex']and authority['externalControllerReview']==spec['controllerReview']and authority['independentSourceReview']==spec['sourceReview']
for k in ['sourceIndex','rootAuthority','config']:assert root[k]==spec[k]
assert root['actualStageResult']==spec['journal']and root['externalParentTerminal']==spec['externalTerminal']and root['externalParentStarted']==spec['started']and root['rootToolSessionId']==49205 and root['rootObservedToolRawExitCode']==0
assert authority['inheritedStageInputsDestinationIsHistoricalDataOnly']and authority['actualStageDestinationMustMatchContextNotInheritedAnnotation']
manifestrow=row(N/'input-freeze.json');inputs=json.loads((N/'input-freeze.json').read_bytes());assert len(inputs['files'])==2852
for r in inputs['files']:exact(r)
refs=json.loads((N/'references.json').read_bytes())
for r in refs['pinnedInputs']:exact(r)
# Retained process observations are reconciled with complete monitor terminal DATA.
terminal=json.loads(Path(spec['externalTerminal']['path']).read_bytes());out=Path(spec['externalTerminal']['path']).parent
owned=[];inventory=[]
for p in sorted(out.iterdir()):
 assert p.is_file()and not p.is_symlink()and p.stat().st_nlink==1;inventory.append(row(p))
 if p.name.startswith('owned-'):
  e=json.loads(p.read_bytes());assert e['sequence']==len(owned);owned.append(e)
assert [e['process']for e in owned]==terminal['observedProcesses']
assert terminal['pid']==44203 and terminal['remainingObservedPids']==[] and all(g['alive']is False for g in terminal['finalGroups'])
assert {e['process']['pgid']for e in owned}<={g['pgid']for g in terminal['finalGroups']}
assert {p.name for p in out.iterdir()}=={'terminal.json','started.json','stdout.log','stderr.log'}|{f'owned-{i:04d}.json'for i in range(len(owned))}
value=dict(schemaVersion=1,verifiedPassed=True,rootResult=rootrow,sourceInputManifest=manifestrow,sourceInputRowsFinallyRehashed=2852,runtimePinnedInputsFinallyRehashed=len(refs['pinnedInputs']),controllerSourcePair=spec['controllerReview'],exactActualNewPairBound=True,observedProcessRecords=len(owned),ownedChildPid=44203,allRetainedObservationsReconciled=True,remainingObservedPids=[],allObservedOwnedGroupsGone=True,externalEvidenceInventory=inventory,historicalPlanDestination='/private/tmp/starling-node-compat/crypto-owner355-gc-v1-source',actualConfiguredSourceRoot='/private/tmp/starling-node-compat/crypto-owner355-gc-v2-source',historicalAnnotationExplicitlyQualifiedByRoot=True,readerActionsInvoked=False)
(P/'final-closure-review.json').write_text(json.dumps(value,indent=2)+'\n')
print(json.dumps(dict(finalInputRows=2852,runtimePinnedRows=len(refs['pinnedInputs']),observedProcessRecords=len(owned),newControllerPairBound=True,readHashOnly=True)))
