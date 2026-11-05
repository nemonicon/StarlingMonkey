"""Thin Source-only successor preparation, never an operational phase."""
from pathlib import Path
import hashlib,json
OWN=Path(__file__).resolve().parent;OLD=OWN.parent/'clock-v13-runtime-candidate-v1';HOLD=OWN.parent/'independent-clock-v13-runtime-source-review-v1'

def desc(path):return dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size)
def read(path):return json.loads(Path(path).read_bytes())
def write(name,value):(OWN/name).write_text(json.dumps(value,indent=2)+'\n')
def family(path):
 ix=desc(path/'index.json');return [ix]+[dict(path=str(path/r['path']),sha256=r['sha256'],bytes=r['bytes']) for r in read(ix['path'])['files']]
assert desc(OLD/'index.json')['sha256']=='3107eee7440638cef9b54d9add797cc5ffda8c766f8fd060b550be7493d0f939'
assert desc(HOLD/'index.json')['sha256']=='05ec90ba7cbca8aa6b333b6daf3231f8a674b613529c85c98a64fafd96ccc37c'
changes={};renames=[('clock-v13-runtime-candidate-v1','clock-v13-runtime-candidate-v2'),('CLOCK_V13_REACTDOM_DIFFERENTIAL_V1','CLOCK_V13_REACTDOM_DIFFERENTIAL_V2'),('CLOCK_V13_REACTDOM_CONFIG_V1','CLOCK_V13_REACTDOM_CONFIG_V2'),('INDEPENDENT_CLOCK_V13_REACTDOM_RUNTIME_SOURCE_REVIEW_PASSED_V1','INDEPENDENT_CLOCK_V13_REACTDOM_RUNTIME_SOURCE_REVIEW_PASSED_V2')]

def edit(name,pairs):
 before=(OLD/name).read_text();work=before;steps=[]
 for a,b in pairs:
  count=work.count(a);assert count>0,(name,a);work=work.replace(a,b);steps.append(dict(before=a,after=b,occurrences=count))
 (OWN/name).write_text(work);changes[name]=dict(output=name,donor=desc(OLD/name),after=desc(OWN/name),edits=steps)
edit('entry.mjs',renames+[
 ('let primary=null;','let primary=null,primaryPresent=false;'),
 ('let native=null,primary=null;','let native=null,primary=null,primaryPresent=false;'),
 ('catch(error){primary=error;throw error;}','catch(error){primaryPresent=true;primary=error;throw error;}'),
 ('if(primary!==null)','if(primaryPresent)'),
 ("  need(refs.actualArtifactReview&&refs.actualArtifactContract,'Real completed artifact proof, never NULL readiness');", "  const held=await c.proof(refs.previousSourceHold),correction=await c.read(refs.requiredCorrectionContract);need(held.state==='INDEPENDENT_CLOCK_V13_REACTDOM_RUNTIME_SOURCE_REVIEW_HELD_V1'&&held.sourceReviewPassed===false&&held.sourceIndexSha256===refs.previousSourceIndex.sha256&&same(correction.heldSourceIndex,refs.previousSourceIndex),'Exact prior null-presence Source HOLD, never action authority');\n  need(refs.actualArtifactReview&&refs.actualArtifactContract,'Real completed artifact proof, never NULL readiness');")])
edit('body.mjs',[
 ('CLOCK_V13_MAPPED_OUTPUT_COMPLETE_UNREVIEWED_V1','CLOCK_V13_MAPPED_OUTPUT_COMPLETE_UNREVIEWED_V2'),('CLOCK_V13_MAPPED_OUTPUT_COMPLETE_EXTERNAL_RAW_ZERO_AND_SEPARATE_REVIEW_REQUIRED','CLOCK_V13_MAPPED_OUTPUT_COMPLETE_EXTERNAL_RAW_ZERO_AND_SEPARATE_REVIEW_REQUIRED_V2'),('ROOT_REVIEWED_CLOCK_V13_MAPPED_OUTPUT_V1','ROOT_REVIEWED_CLOCK_V13_MAPPED_OUTPUT_V2'),('CLOCK_V13_REACTDOM_CONFIG_V1','CLOCK_V13_REACTDOM_CONFIG_V2'),('CLOCK_V13_JCO_SESSION_COMPLETE_UNREVIEWED_V1','CLOCK_V13_JCO_SESSION_COMPLETE_UNREVIEWED_V2'),('CLOCK_V13_REACTDOM_DIFFERENTIAL_COMPLETE_UNREVIEWED_V1','CLOCK_V13_REACTDOM_DIFFERENTIAL_COMPLETE_UNREVIEWED_V2'),
 ('let primary=null,finalErrors=[]','let primary=null,primaryPresent=false,finalErrors=[]'),('catch(error){primary=error;}','catch(error){primaryPresent=true;primary=error;}'),('if(primary!==null||finalErrors.length)','if(primaryPresent||finalErrors.length)'),('if(primary!==null)throw primary','if(primaryPresent)throw primary'),('primary:observed(primary)','primaryPresent,primary:observed(primary)')])
edit('models.mjs',[(renames[1])]);edit('wave.mjs',[])
edit('external.py',[renames[0],renames[1],renames[2],renames[3],('CLOCK_V13_SLICE_EXTERNAL_RAW_ZERO_UNREVIEWED_V1','CLOCK_V13_SLICE_EXTERNAL_RAW_ZERO_UNREVIEWED_V2')])
edit('test-pure.mjs',[renames[1]])
refs=read(OLD/'references.json');refs['originalRoot']=str(OWN);refs['state']='CLOCK_V13_REACTDOM_RUNTIME_SOURCE_REFERENCES_NOT_AUTHORITY_V2';refs['mappedOutputRoot']='/private/tmp/starling-node-compat/clock-v13-jco-mapped-v2';refs['runtimeOutputRoot']='/private/tmp/starling-node-compat/clock-v13-runtime-v2';refs['previousSourceIndex']=desc(OLD/'index.json');refs['previousSourceHold']=dict(index=desc(HOLD/'index.json'),result=desc(HOLD/'results.json'));refs['requiredCorrectionContract']=desc(HOLD/'required-correction-contract.json');write('references.json',refs)
old_inputs=read(OLD/'source-inputs.json');rows={r['path']:r for r in old_inputs['files']}
for r in family(OLD)+family(HOLD):
 if r['path'] in rows:assert rows[r['path']]==r
 rows[r['path']]=r
families=[*old_inputs['families'],desc(OLD/'index.json'),desc(HOLD/'index.json')];assert len({r['path'] for r in families})==len(families)
write('source-inputs.json',dict(schemaVersion=1,files=sorted(rows.values(),key=lambda r:r['path']),families=families,sourceAndNativeAndActualArtifactsProtected=True,noToolTreeCopied=True,inheritedSourceIndex=desc(OLD/'index.json'),heldReview=refs['previousSourceHold']))
for name in ['future-config.template.json','future-root-authority.template.json','future-mapped-output-review.template.json','future-source-review-contract.json','future-results-review-contract.json']:
 value=read(OLD/name)
 def change(v):
  if isinstance(v,dict):return {k:change(x) for k,x in v.items()}
  if isinstance(v,list):return [change(x) for x in v]
  if not isinstance(v,str):return v
  for a,b in renames:v=v.replace(a,b)
  for a,b in [('UNISSUED_CLOCK_V13_REACTDOM_ROOT_V1','UNISSUED_CLOCK_V13_REACTDOM_ROOT_V2'),('UNISSUED_CLOCK_V13_MAPPED_OUTPUT_REVIEW_V1','UNISSUED_CLOCK_V13_MAPPED_OUTPUT_REVIEW_V2'),('ROOT_REVIEWED_CLOCK_V13_MAPPED_OUTPUT_V1','ROOT_REVIEWED_CLOCK_V13_MAPPED_OUTPUT_V2'),('CLOCK_V13_REACTDOM_DIFFERENTIAL_COMPLETE_UNREVIEWED_V1','CLOCK_V13_REACTDOM_DIFFERENTIAL_COMPLETE_UNREVIEWED_V2'),('INDEPENDENT_CLOCK_V13_REACTDOM_DIFFERENTIAL_RESULTS_REVIEW_PASSED_V1','INDEPENDENT_CLOCK_V13_REACTDOM_DIFFERENTIAL_RESULTS_REVIEW_PASSED_V2')]:v=v.replace(a,b)
  return v
 write(name,change(value))
write('derivations.json',dict(schemaVersion=1,parentSourceIndex=desc(OLD/'index.json'),heldReview=refs['previousSourceHold'],requiredCorrectionContract=refs['requiredCorrectionContract'],files=list(changes.values()),componentNativeGuestOracleScheduleOrFourCoresChanged=False,noModuleGlobalsRebound=True))
write('preparation-history.json',dict(schemaVersion=1,state='SOURCE_PREPARATION_UNSEALED_V2',previousSource=desc(OLD/'index.json'),sourceHold=refs['previousSourceHold'],nullSentinelOnlySemanticCorrection=True,allNewPhaseAndMappedRuntimeSlotsUnissued=True,actionsInvoked=False))
print(json.dumps(dict(sourceFilesPrepared=list(changes),inputRows=len(rows),families=len(families),noActionInvoked=True)))
