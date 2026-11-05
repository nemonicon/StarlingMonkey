"""Generate exact donor afterimages and immutable input DATA; no owner imports."""
from pathlib import Path
import ast,hashlib,json,os,stat
import context as C
from data_io import descriptor,regular,write
HERE=Path(__file__).resolve().parent;K=HERE.parent;REPO=K.parents[2]
def capture(path):return descriptor(Path(path))
def load(path):return json.loads(Path(path).read_bytes())
proposal=K/'ownership-gc-candidate-v1';proposal_index=capture(proposal/'index.json');assert proposal_index['sha256']=='3b6f04806a8990e99dbda0a1292bbb559801f99f2d21b7b57e5fa6020fa03dcf'
protection=load(proposal/'normal-protection.json');write(HERE/'normal-protection.json',protection)
normal_stage=K/'native-integration-v2-source-stage-root-results.json';stage=load(normal_stage)
assert stage['destination']=='/tmp/starling-node-compat/crypto-owner-source-v2'and len(stage['files'])==1311
files=[]
for r in stage['files']:
    p=Path(C.NORMAL_SOURCE)/r['path'];d=capture(p);assert d['sha256']==r['sha256']and d['bytes']==r['bytes']
    mode=stat.S_IMODE(p.stat().st_mode);assert mode==r['outputMode'];files.append(dict(path=r['path'],original=d,mode=mode))
write(HERE/'stage-inputs.json',dict(schemaVersion=1,state='EXACT_IMMUTABLE_NORMAL355_SOURCE_COPY_PLAN_NOT_EXECUTED',nativeSourceFiles=355,toolRows=922,baseCommit=C.BASE,cloneSource=C.NORMAL_SOURCE,destination=C.SOURCE,files=files,stageExecuted=False))
normal_entry=K/'independent-native-integration-v2-stage-review-v1/normal-off-build-entry.json';entry=load(normal_entry)
donor=K/'native-integration-candidate-v2';corrected=K/'native-freezer-source-amendment-v1/freeze-engine.py'
src=corrected.read_text();body=src[src.index('def main():'):src.index("if __name__ == '__main__':")]
edits=[]
def change(before,after,count=1):
    global body
    assert body.count(before)==count,(before,body.count(before));body=body.replace(before,after);edits.append(dict(before=before,after=after,count=count))
change('def main():','def freeze(CONTEXT, common, source_guard):')
for before,after in [('CONTEXT','context'),('GUARD_PATH','active_guard'),('ENTRY','active_entry'),('REPO','configured_root'),('HERE','artifact_tools'),('OUTPUT','output_root'),('guard.','source_guard.')]:
    change(before,after,body.count(before))
change('validate_plan(plan, receipt_path)','validate_plan(plan, receipt_path, output=output_root)')
change('execute_plan(plan)','execute_plan(plan, output=output_root)')
change("'helperSha256': sha(Path(__file__))", "'helperSha256': sha(active_entry)")
start='def freeze(context, common, source_guard):\n'
bindings="    configured_root=common.REPO\n    artifact_tools=common.HERE\n    output_root=Path(context['freezeRoot'])\n    active_entry=Path(context['entryPath'])\n    active_guard=Path(context['guardPath'])\n    NODE='/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node'\n"
for name in ['RECIPE','POLICY','HELPER','EMBEDDING','ADAPTER','classify','checked','sha','digest','manifest','compile_command','embedding_command','validate_plan','execute_plan','capture_regular','checked_below','tool_dependencies']:bindings+='    '+name+'=common.'+name+'\n'
change(start,start+bindings)
freezer="# Exact versioned corrected-freezer body; no actions at import.\nimport datetime,importlib.util,json,subprocess\nfrom pathlib import Path\n"+body
with(HERE/'freezer-body.py').open('x')as f:f.write(freezer)
write(HERE/'freezer-derivations.json',dict(schemaVersion=1,source=capture(corrected),extractStart='def main():',extractEnd="if __name__ == '__main__':",prefix=freezer[:freezer.index('def freeze(')],edits=edits,globalContextRebinding=False,existingExplicitOutputParametersUsed=True))
exporter=donor/'artifact-tools/export-pin-candidate.py';text=exporter.read_text();function=text[text.index('def candidate('):text.index('def main():')]
before='def candidate(label, output=OUTPUT):';assert function.count(before)==1
after='def candidate(label, output, common):\n    verify_frozen_variant=common.verify_frozen_variant\n    RECIPE=common.RECIPE'
function=function.replace(before,after)
with(HERE/'export-body.py').open('x')as f:f.write('# Exact original candidate body using actual explicit-root verifier.\n'+function)
write(HERE/'export-derivations.json',dict(schemaVersion=1,source=capture(exporter),extractStart='def candidate(',extractEnd='def main():',before=before,after=after,originalFieldConstructionUnchanged=True))
pinned=[capture(normal_stage),capture(normal_entry),capture(Path(C.NORMAL_SOURCE)/'.git/HEAD'),capture(donor/'index.json'),capture(corrected),capture(K/'native-freezer-source-amendment-v1/freezer-guard.py'),capture(proposal/'index.json'),capture(proposal/'normal-protection.json')]
node=dict(path=C.NODE,sha256=C.NODE_SHA,bytes=108619024);regular(node);pinned.append(node)
write(HERE/'references.json',dict(schemaVersion=1,proposalIndex=proposal_index,normalBuildEnvironment=entry['launcherManagedChildEnvironment'],normalStageReceipt=capture(normal_stage),node=node,pinnedInputs=pinned,actualGcStage=None,actualGcBuild=None,actualGcFreeze=None,reviewedGcPins=None,gcNativeRootReview=None,independentGcNativeReview=None))
write(HERE/'future-config.template.json',dict(schemaVersion=1,sourceIndex=None,rootAuthority=None))
root=dict(schemaVersion=1,state=None,phase=None,sourceIndexSha256=None,variant='gc-off',configuredSourceRoot=C.SOURCE,artifactToolsRoot=C.TOOLS,workRoot=C.WORK,freezeRoot=C.FREEZE,nativeSourceFiles=355,externalEmbeddingSources=3,independentSourceReview=None,actualStageResult=None,independentStageReview=None,actualBuildResult=None,engine=None,metadata=None,reviewedGcPins=None,gcNativeRootReview=None,independentGcNativeReview=None,pinCandidateOutput=None,externalParentDeadlineSeconds=7200)
root['actualBuildExternalTerminal']=None
for phase in C.PHASES:root[phase+'Allowed']=False
for flag in ['guestAllowed','keyOperationsAllowed','prototypeWorkloadsAllowed','componentAllowed','nativeSourceChangesAllowed','normalMutationAllowed','metadataProjectionAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed']:root[flag]=False
write(HERE/'future-root-authority.template.json',root)
write(HERE/'future-gc-pins.template.json',dict(schemaVersion=1,state=None,sourceIndexSha256=None,variants={x:None for x in ['normal-off','normal-runtime','gc-off','disabled-off']},actualGcPin=None,rootNativeReview=None,operationalAdmission=False,runtimeAcceptanceClaim=False))
allinputs={}
for r in [*pinned,*[x['original']for x in files]]:allinputs[r['path']]=r
for r in protection['frozenCopyEntries']:
    d=capture(r['path']);assert d['sha256']==r['sha256']and d['bytes']==r['bytes'];allinputs[d['path']]=d
for r in protection['originals']:
    regular(r['original']);allinputs[r['original']['path']]=r['original']
allinputs[protection['freezeReceipt']['path']]=protection['freezeReceipt']
for r in allinputs.values():regular(r)
write(HERE/'input-freeze.json',dict(schemaVersion=1,files=list(allinputs.values()),sourceOnly=True,source355Changed=False,normalOriginalReferenceEntries=1387,normalFrozenMembership=1391,newGcDestinationsCreated=False))
print(json.dumps(dict(state='GC_NATIVE_SOURCE_GENERATED_UNREVIEWED',stageRows=len(files),inputRows=len(allinputs),freezerExactEdits=len(edits),exportExactEdits=1,ownerActionsInvoked=False)))
