"""Read/hash SOURCE preparation only. Does not call a controller, helper or tool."""
from pathlib import Path
import hashlib,json,stat
P=Path(__file__).resolve().parent;S=P.parent;R=P.parents[3]
V=S/'combined-native-build-controller-candidate-v1';SRC=Path('/private/tmp/starling-node-compat/combined-native355-v1-source');WORK=Path('/private/tmp/starling-node-compat/combined-native355-v2-build')
def d(p):
    p=Path(p);h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)
def load(p):return json.loads(Path(p).read_bytes())
def write(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
def pair(p):return dict(index=d(p/'index.json'),result=d(p/'results.json'))
refs=load(V/'references.json');cache=load(V/'cache-plan.json')
for k in ['workRoot','privateRustupHome','privateCargoHome']:cache[k]=cache[k].replace('combined-native355-v1-build','combined-native355-v2-build')
cache['state']='FINITE_COMBINED355_PRIVATE_IMMUTABLE_CACHE_PLAN_V2';write('cache-plan.json',cache)
refs.update(state='COMBINED355_NORMAL_OFF_BUILD_RETRY_SOURCE_REFERENCES_V2',parentControllerIndex=d(V/'index.json'),failedBuildReview=pair(S/'independent-combined355-native-build-bootstrap-failure-review-v1'),privateRustupProbeReview=pair(S/'independent-rustup-private-bootstrap-probe-review-v1'),recipe=d(P/'build-engine.sh'),policy=d(P/'policy.json'),helper=d(P/'layer-policy.py'),metadataModel=d(P/'native-admission-model.py'),cachePlan=d(P/'cache-plan.json'))
failure=load(refs['failedBuildReview']['result']['path']);probe=load(refs['privateRustupProbeReview']['result']['path'])
refs['failedBuildResult']=failure['actualBuildResult'];refs['failedBuildObservation']=failure['rootObservation']
refs['protectedTreeInventories']=[failure['failedWorkInventory']]
refs['originalConfiguredRecipe']=d(SRC/'tests/node-compat/build-engine.sh')
refs['originalConfiguredHelper']=d(SRC/'tests/node-compat/foundation-scheduler/combined-native-integration-candidate-v1/layer-policy.py')
refs['originalConfiguredPolicy']=d(SRC/'tests/node-compat/foundation-scheduler/combined-native-integration-candidate-v1/policy.json')
refs['artifactBasename']=refs['artifactBasename'].replace('combined355-v1','combined355-v2').replace('combined355v1','combined355v2')
refs['buildEnvironment']={k:v.replace('combined-native355-v1-build','combined-native355-v2-build').replace('combined355v1','combined355v2')for k,v in refs['buildEnvironment'].items()}
extras=[V,S/'independent-combined355-native-build-controller-source-review-v1',S/'independent-combined355-native-build-bootstrap-failure-review-v1',S/'independent-rustup-private-bootstrap-probe-review-v1']
refs['families'] += [d(p/'index.json')for p in extras]
write('references.json',refs)
files={}
def add(r):
    row={k:r[k]for k in ['path','sha256','bytes']}
    if row['path']in files:assert files[row['path']]==row
    files[row['path']]=row
# Reuse original finite protection scope and bind the failed phase/probe DATA.
for origin in [V/'source-inputs.json',S/'independent-combined355-native-build-bootstrap-failure-review-v1/input-hashes.json',S/'independent-rustup-private-bootstrap-probe-review-v1/input-hashes.json']:
    for r in load(origin)['files']:add(r)
for row in refs['families']:
    add(row);root=Path(row['path']).parent
    for r in load(row['path'])['files']:add(dict(path=str(root/r['path']),sha256=r['sha256'],bytes=r['bytes']))
for r in [refs['failedBuildResult'],refs['failedBuildObservation']]:add(r)
# All 755 failed-work regular files protected; never a cache source for this retry.
for inventory in refs['protectedTreeInventories']:
    add(inventory);v=load(inventory['path'])
    for r in v['files']:add(dict(path=str(Path(v['root'])/r['path']),sha256=r['sha256'],bytes=r['bytes']))
rows=sorted(files.values(),key=lambda r:r['path']);write('source-inputs.json',dict(schemaVersion=1,role='UNCHANGED_STAGED355_AND_ORIGINALS_PLUS_OLD_FAILED_WORK_AND_REAL_PROBE_PROTECTION',files=rows,modeRows=[dict(file=r,mode=stat.S_IMODE(Path(r['path']).stat().st_mode))for r in rows],originalContextsPreserved=True,operatingSystemEntireFilesystemSealed=False))
policy=dict(schemaVersion=1,mandatoryBeforeControllerSpawn=True,removePrefixes=['BASH_FUNC_'],removeExactNames=['BASH_ENV','ENV','SHELLOPTS','BASHOPTS','CDPATH','GLOBIGNORE'],preserveExactNames=['HOME','home','CODEX_HOME'],rootAuthorityMustBindPolicy=True,rootLauncherMustEnforcePolicy=True,actualChildMustContainNoRemovedEntries=True,recordRemovedVariableNamesOnly=True,recordEnvironmentValues=False,scope='Known inherited Bash function and startup controls; not an OS or universal environment sandbox')
root=load(V/'root-authority.template.json')
root.update(state='UNISSUED_COMBINED355_NORMAL_OFF_BUILD_RETRY_ROOT_AUTHORITY_V2',controllerIndex=None,controllerEntry=None,controllerSourceReview=None,workRoot=str(WORK),freezeRoot='/private/tmp/starling-node-compat/combined-native355-v2-freeze',buildOutputRoot='/private/tmp/starling-node-compat/combined-native355-v2-normal-off-build-root',externalOutputRoot='/private/tmp/starling-node-compat/combined-native355-v2-normal-off-build-external-root',rootObserverOutputRoot='/private/tmp/starling-node-compat/combined-native355-v2-build-root-observer',buildEnvironment=refs['buildEnvironment'],cachePlan=refs['cachePlan'],rootEnvironmentPolicy=policy,rootLauncherRequired=True,retryRecipe=refs['recipe'],retryPolicy=refs['policy'],retryHelper=refs['helper'],failedBuildReview=refs['failedBuildReview'],privateRustupProbeReview=refs['privateRustupProbeReview'],persistentPrivateRustupAutoSelfUpdateDisableRequired=True,oldWorkResumeAllowed=False)
write('root-authority.template.json',root)
write('config.template.json',dict(schemaVersion=1,state='COMBINED355_NORMAL_OFF_BUILD_CONFIG_V2',controllerIndex=None,sourceIndex=refs['integrationIndex'],rootAuthority=None))
write('future-source-review-contract.json',dict(schemaVersion=1,state='PROSPECTIVE_COMBINED355_BUILD_RETRY_SOURCE_REVIEW_CONTRACT_V2',requiredState='INDEPENDENT_COMBINED355_BUILD_CONTROLLER_SOURCE_REVIEW_PASSED_V2',requiredFixedValues=dict(schemaVersion=1,integrationSourceIndexSha256=refs['integrationIndex']['sha256'],actualStageReviewIndexSha256=refs['actualStageReview']['index']['sha256'],genericMonitorSourceIndexSha256=refs['monitorIndex']['sha256'],failedBuildReviewIndexSha256=refs['failedBuildReview']['index']['sha256'],privateRustupProbeReviewIndexSha256=refs['privateRustupProbeReview']['index']['sha256'],retryRecipeSha256=refs['recipe']['sha256'],requiredRootEnvironmentPolicy=policy,sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,hostActionsInvoked=False,nativeBuildActionsInvoked=False),requiredOwnIndexBinding='controllerSourceIndexSha256 must equal the final complete v2 source index SHA256',actualPeer=None,grantsAnyActionAuthority=False))
print(json.dumps(dict(state='SOURCE_PREPARATION_ONLY',declaredInputs=len(rows),completeFamilies=len(refs['families']),failedWorkProtected=len(load(refs['protectedTreeInventories'][0]['path'])['files']),probeReview=refs['privateRustupProbeReview'],recipeExecuted=False,helperImported=False)))
