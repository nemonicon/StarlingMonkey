"""Pure DATA model. No filesystem reads, process launch, imports of owner code."""
from pathlib import PurePosixPath

CONFIGURED='/private/tmp/starling-node-compat/crypto-owner-source-v2'
NORMAL_WORK='/private/tmp/starling-node-compat/crypto-owner-v2-build'
NORMAL_FREEZE='/private/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze'
WORK='/private/tmp/starling-node-compat/crypto-owner355-gc-v1-build'
FREEZE='/private/tmp/starling-node-compat/crypto-owner355-gc-v1-freeze'
RAW='/private/tmp/starling-node-compat/crypto-owner355-gc-v1-build-root'

def canonical(p):
    if p.startswith('/tmp/'):p='/private'+p
    assert isinstance(p,str) and p.startswith('/') and '\\'not in p and '\0'not in p
    assert str(PurePosixPath(p))==p and all(x not in ('','.','..')for x in p.split('/')[1:])
    return p

def overlap(a,b):
    a,b=canonical(a),canonical(b)
    return a==b or a.startswith(b+'/') or b.startswith(a+'/')

def isolation(work,freeze,raw,protected):
    roots=[canonical(x)for x in [work,freeze,raw]]
    assert len(set(roots))==3
    for i,a in enumerate(roots):
        for b in roots[i+1:]:assert not overlap(a,b)
        for old in [CONFIGURED,NORMAL_WORK,NORMAL_FREEZE,*protected]:assert not overlap(a,old)
    return True

def build_plan(normal_environment,protected):
    isolation(WORK,FREEZE,RAW,protected)
    e=dict(normal_environment)
    assert e['NODE_COMPAT_GC_STRESS']=='0' and canonical(e['NODE_COMPAT_BUILD_ROOT'])==NORMAL_WORK
    assert e['NODE_COMPAT_BUILD_TYPE']=='Release' and e['NODE_COMPAT_OOM_TESTING']=='0' and e['NODE_COMPAT_ENTROPY_MODE']=='OFF'
    e.update(NODE_COMPAT_BUILD_ROOT=WORK,NODE_COMPAT_GC_STRESS='1',NODE_COMPAT_ARTIFACT_TAG='ko355gc1')
    return dict(schemaVersion=1,state='SOURCE_ONLY_ISOLATED_GC_NATIVE_BUILD_PLAN_NOT_AUTHORITY',command=['bash',CONFIGURED+'/tests/node-compat/build-engine.sh'],cwd=CONFIGURED,explicitSelectorEnvironment=e,workRoot=WORK,freezeRoot=FREEZE,externalControllerOutput=RAW,newOwnedController=None,requiresFreshAbsentDestinations=True,existingBuildOneGcOffMustNotBeCalled=True,recipeUnchanged=True,nativeSourceChanges=0,nativeSourceFiles=355,externalEmbeddingSources=3,buildAllowed=False,freezeAllowed=False,bootstrapAllowed=False,componentAllowed=False,guestAllowed=False,gcAllowed=False,keyOperationsAllowed=False,rootAuthority=None,reviewedGcPin=None,actualGcEngine=None,actualGcFreeze=None,actualGcReview=None,operationalAdmission=False,runtimeAcceptanceClaim=False,timingAllowed=False)
