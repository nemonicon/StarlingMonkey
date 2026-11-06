"""Source-only canonical manifest correction. No operational entry or helper import."""
from pathlib import Path
import copy,hashlib,json
OWN=Path(__file__).resolve().parent
PARENT=OWN.parent/'combined-clock-diagnostics-native-integration-candidate-v2'
HOLD=OWN.parent/'independent-clock-diagnostic357-native-integration-source-review-v2'
def desc(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(p):return json.loads(Path(p).read_bytes())
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
def main():
 assert not(OWN/'index.json').exists()
 parent_index=desc(PARENT/'index.json');assert parent_index['sha256']=='a52ee25caa3e026ad8efae1955473bea2a98090811d66cea7be911853b5d7c64'
 for r in read(parent_index['path'])['files']:assert desc(PARENT/r['path'])==dict(r,path=str(PARENT/r['path']))
 oldrefs=read(PARENT/'references.json')
 for value in oldrefs['contexts'].values():assert not Path(value).exists(),value
 policy=read(PARENT/'policy.json');before=copy.deepcopy(policy['expectedNativeSourceManifest']);policy['expectedNativeSourceManifest']=sorted(before,key=lambda r:r['path'])
 assert before!=policy['expectedNativeSourceManifest'] and len(before)==357
 assert {r['path']:r['sha256']for r in before}=={r['path']:r['sha256']for r in policy['expectedNativeSourceManifest']}
 save('policy.json',policy)
 (OWN/'native-admission-model.py').write_bytes((PARENT/'native-admission-model.py').read_bytes())
 (OWN/'embedding-diagnostic.UNAPPLIED.patch').write_bytes((PARENT/'embedding-diagnostic.UNAPPLIED.patch').read_bytes())
 edits=[]
 def derive(name,changes):
  before=(PARENT/name).read_text();after=before;rows=[]
  for old,new,count in changes:
   assert after.count(old)==count,(name,old,count,after.count(old));after=after.replace(old,new);rows.append(dict(before=old,after=new,count=count))
  (OWN/name).write_text(after);inverse=after
  for r in reversed(rows):inverse=inverse.replace(r['after'],r['before'])
  assert inverse==before
  edits.append(dict(path=name,before=desc(PARENT/name),after=desc(OWN/name),edits=rows,forwardAndInverseWholeBytesVerified=True))
 derive('layer-policy.py',[(oldrefs['policy']['sha256'],desc(OWN/'policy.json')['sha256'],1)])
 derive('build-engine.sh',[(str(PARENT),str(OWN),2),(oldrefs['helper']['sha256'],desc(OWN/'layer-policy.py')['sha256'],5),(oldrefs['policy']['sha256'],desc(OWN/'policy.json')['sha256'],2)])
 oldcheck="for key in ['controller','recipe','helper','policy','metadataModel','copyPlan','cachePlan','protectedInputs']:assert refs[key]in own_rows"
 newcheck="for key in ['controller','recipe','helper','policy','metadataModel']:assert refs[key]in own_rows\n    shared_rows=family(refs['sharedDataIndex'])\n    for key in ['copyPlan','cachePlan','protectedInputs']:assert refs[key]in shared_rows\n    assert refs['activeProducerContext']==str(OWN)"
 oldreceipt="result=dict(schemaVersion=1,state='CLOCK_DIAGNOSTIC357_SOURCE_STAGE_STARTED_V3',sourceIndex=frame['own'],"
 newreceipt="result=dict(schemaVersion=1,state='CLOCK_DIAGNOSTIC357_SOURCE_STAGE_STARTED_V3',activeProducerContext=str(OWN),sharedSourcePlanData=frame['refs']['copyPlan'],sourceIndex=frame['own'],"
 text=(PARENT/'controller.py').read_text();versions=text.count('_V2')
 # Change protocol states first so the following exact receipt edit reverses cleanly.
 derive('controller.py',[(PARENT.name,OWN.name,1),(oldcheck,newcheck,1),('_V2','_V3',versions),(oldreceipt,newreceipt,1)])
 refs=copy.deepcopy(oldrefs);refs['state']='CLOCK_DIAGNOSTIC357_RUNNABLE_PRODUCER_SOURCE_V3'
 for key,name in [('controller','controller.py'),('recipe','build-engine.sh'),('helper','layer-policy.py'),('policy','policy.json'),('metadataModel','native-admission-model.py')]:refs[key]=desc(OWN/name)
 refs['sharedDataIndex']=parent_index;refs['activeProducerContext']=str(OWN)
 refs['parentProducerIndex']=parent_index;refs['manifestOrderHoldIndex']=desc(HOLD/'index.json')
 for family in [parent_index,refs['manifestOrderHoldIndex']]:
  assert family not in refs['families'];refs['families'].append(family)
 save('references.json',refs)
 root=read(PARENT/'root-authority.template.json');root['state']='ROOT_REVIEWED_CLOCK_DIAGNOSTIC357_PHASE_V3';root['entry']=refs['controller'];save('root-authority.template.json',root)
 config=read(PARENT/'config.template.json');config['state']='CLOCK_DIAGNOSTIC357_CONFIG_V3';save('config.template.json',config)
 for n in ['future-source-review-contract.json','future-stage-review-contract.json','future-build-review-contract.json']:
  value=read(PARENT/n)
  def version(v):
   if isinstance(v,dict):return{k:version(x)for k,x in v.items()}
   if isinstance(v,list):return[version(x)for x in v]
   return v.replace('_V2','_V3')if isinstance(v,str)else v
  save(n,version(value))
 contexts=read(PARENT/'contexts.json');contexts['activeProducerContext']=str(OWN);contexts['pathReuseQualification']='Prior v2 SOURCE/WORK/FREEZE/output paths have never been created. V3 Root/source identities are new; path absence is checked at preparation and operational guards.';save('contexts.json',contexts)
 save('derivations.json',dict(schemaVersion=1,parentSourceIndex=parent_index,holdIndex=refs['manifestOrderHoldIndex'],files=edits,policyChange='Only expectedNativeSourceManifest order is canonicalized; every path/hash and all other policy fields stay identical.',policyBefore=desc(PARENT/'policy.json'),policyAfter=desc(OWN/'policy.json'),unchangedModel=desc(OWN/'native-admission-model.py'),unchangedEmbeddingPatch=desc(OWN/'embedding-diagnostic.UNAPPLIED.patch'),sharedDataDescriptors={k:refs[k]for k in ['copyPlan','cachePlan','protectedInputs']},noNativeOrEmbeddingSourceChanges=True))
 save('preparation-history.json',dict(schemaVersion=1,state='UNSEALED_SOURCE_ONLY_MANIFEST_ORDER_CORRECTION_V3',parentSourceIndex=parent_index,holdIndex=refs['manifestOrderHoldIndex'],allReusedFuturePathsAbsent=True,sourceOnly=True,stageOrHelperOrBuildOrGuestInvoked=False))
 print(json.dumps(dict(policy=refs['policy'],helper=refs['helper'],recipe=refs['recipe'],controller=refs['controller'])))
if __name__=='__main__':main()
