"""Read-only full-build guard tests; no runtime/monitor/constructor invocation."""
from pathlib import Path
import ast,copy,importlib.util,json
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
WORK=Path('/private/tmp/starling-node-compat/next-native-intl-build-portable825-sdk-restored-first')
spec=importlib.util.spec_from_file_location('actual_full_native_guard_tests',HERE/'run-full-native-requests.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
n=json.loads((WORK/'metadata.json').read_bytes())
a=dict(fullNativeBuildResult=m.row(WORK/'result.json'),fullNativeBuildObservation=m.row(Path(str(WORK)+'-root-monitor/observation.json')),fullNativeBuildReview=m.row(BASE/'next-native-portable-build-sdk-restored-root-v1/actual-build-review.json'),fullNativeBuildSourceIndex=m.row(BASE/'next-native-portable-build-preparation-v3/index.json'),fullBuildGeneratedNullSource=m.row(WORK/'build/starling-raw.wasm/null.cpp'),engine=n['engine'],nativeMetadata=m.row(WORK/'metadata.json'))
m.protect_full_build(a,n)
refused=[]
for name in ['incremental-kind','scalar-rows','missing-row','duplicate-row','scalar-embedding','missing-embedding','native-count','admission-version','boolean-admission-version','execution-claim','adoption-claim','logical-proof-false','foreign-source','missing-generated-source']:
    v=copy.deepcopy(n);root=copy.deepcopy(a)
    if name=='incremental-kind':v['metadataKind']='EXPERIMENTAL_NEXT_INTL_INCREMENTAL_NATIVE_BUILD_ACTUAL_V1'
    elif name=='scalar-rows':v['actualCompileRows']=80
    elif name=='missing-row':v['actualCompileRows'].pop()
    elif name=='duplicate-row':v['actualCompileRows'][-1]=v['actualCompileRows'][0]
    elif name=='scalar-embedding':v['actualSeparateEmbeddingCompileRows']=1
    elif name=='missing-embedding':v['actualSeparateEmbeddingCompileRows']=[]
    elif name=='native-count':v['nativePolicyInputCount']=434
    elif name=='admission-version':v['portableBuildAdmissionVersion']=2
    elif name=='boolean-admission-version':v['portableBuildAdmissionVersion']=True
    elif name=='execution-claim':v['engineExecuted']=True
    elif name=='adoption-claim':v['adoption']=True
    elif name=='logical-proof-false':v['logicalCargoAuditDescriptorFromVerifiedCapsule']=False
    elif name=='foreign-source':v['actualCompileRows'][0]['file']='/outside/source.cpp'
    else:root['fullBuildGeneratedNullSource']=root['fullNativeBuildReview']
    try:m.protect_full_build(root,v)
    except (AssertionError,TypeError,KeyError):refused.append(name)
    else:raise AssertionError('accepted invalid full-build DATA: '+name)
assert len(refused)==14
m.check_capacity(1073741824,1073741824)
for free,required in [(1073741823,1073741824),(True,1073741824),(1073741824,True)]:
    try:m.check_capacity(free,required)
    except AssertionError:pass
    else:raise AssertionError('accepted capacity-policy mutation')
for name in ['run-full-native-requests.py','test-full-native-guard.py']:ast.parse((HERE/name).read_text())
print(json.dumps(dict(passed=True,genuineFullBuildGuardPassed=True,generatedCMakeNullSourceExplicitlyBound=True,refused=refused,astFiles=2,runtimeOrConstructorOrMonitorInvoked=False,metadataOrSourceRewritten=False)))
