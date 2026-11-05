"""Small final DATA cross-check; no owner imports or foreign tools."""
import hashlib,json,stat
from pathlib import Path

OWN=Path(__file__).resolve().parent;S=OWN.parent
R=json.loads((S/'task-selection-normal-off-build-v1-root-results.json').read_text())
mp=Path(R['actualMetadataObservation']['metadata']['path']);raw=mp.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='8219b7aaea6f5a311ccd9e2d038edcd213663078f9ff18917c155dfeb51dde4f'
m=json.loads(raw);P=S/'task-selection-integration-candidate-v1'
policy=json.loads((P/'policy.json').read_text());pins=json.loads((P/'baseline-pins.json').read_text())
oldmeta=json.loads(Path(pins['resourceMetadata']['path']).read_text())
assert m['selectedModuleManifests']==oldmeta['selectedModuleManifests']
assert len(m['selectedModuleManifests'])==9
rows=[]
for d in m['selectedModuleManifests']:
 p=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-source')/d['path'];b=p.read_bytes();v=json.loads(b)
 assert hashlib.sha256(b).hexdigest()==d['sha256']and v['profileVersion']==d['profileVersion']
 rows.append(dict(path=str(p),sha256=d['sha256'],bytes=len(b),profileVersion=v['profileVersion']))
assert m['resourceOwnershipPolicy']['sourcePolicy']==policy['resourceOwnershipSourcePolicy']
timer=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-source/builtins/web/timers.cpp')
assert hashlib.sha256(timer.read_bytes()).hexdigest()==policy['taskSelectionSourcePolicy']['timerOwnershipSourceSha256']=='0024d009d11aab0705789f5d72fd8ec87deec9c44bdd8b913d970257aaadc9e4'
mode_observations=[]
for name,n in [('scheduler-resource-selection-v1-stage.json',566),('scheduler-resource-v1-stage.json',501)]:
 j=json.loads((Path('/private/tmp/starling-node-compat')/name).read_text());assert len(j['copies'])==n
 for c in j['copies']:
  p=Path(c['path']);q=Path(c['original']['path'])
  assert stat.S_IMODE(p.stat().st_mode)==stat.S_IMODE(q.stat().st_mode)
  mode_observations.append(dict(path=str(p),original=str(q),currentMatchingMode=stat.S_IMODE(p.stat().st_mode)))
v=dict(schemaVersion=1,verifiedPassed=True,allNineActualManifestRows=rows,actualModuleSelectionUnchangedUnderExplicitNoPublicSurfaceDelta=True,
 resourceOwnershipPolicyUnchanged=True,timerOwnershipSourceSha256=policy['taskSelectionSourcePolicy']['timerOwnershipSourceSha256'],
 currentCopyOriginalModesEqual=mode_observations,modeScope='Actual current pairs. Historical mode facts remain in exact54fc stage proof; no invented fixed old mode baseline.',
 ownerActionsInvoked=False,foreignToolsInvoked=False,engineExecuted=False)
(OWN/'supplemental-data.json').write_text(json.dumps(v,indent=2)+'\n')
print(json.dumps(dict(manifests=9,timerOwnershipPreserved=True,modePairs=len(mode_observations),ownerActionsInvoked=False)))
