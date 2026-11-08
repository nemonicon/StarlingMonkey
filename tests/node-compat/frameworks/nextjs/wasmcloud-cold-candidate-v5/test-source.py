"""Read-only text/JSON/AST checks; never imports a target module or runs Node/wash."""
from pathlib import Path
import ast, hashlib, json

HERE = Path(__file__).resolve().parent
PARENT = HERE.with_name('wasmcloud-cold-candidate-v4')

def row(path):
    raw = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))

def main():
    count = 0
    def check(value):
        nonlocal count
        assert value
        count += 1
    read = lambda p: json.loads(p.read_text())
    derivation = read(HERE/'derivation.json')
    check(row(PARENT/'index.json') == derivation['parentSourceIndex'])
    for name in derivation['copiedExactly']:
        check((HERE/name).read_bytes() == (PARENT/name).read_bytes())
    old = (PARENT/'models.mjs').read_text()
    check((HERE/'models.mjs').read_text() == old.replace(
        "assert.equal(native.metadataKind,'EXPERIMENTAL_NEXT_INTL_INCREMENTAL_NATIVE_BUILD_ACTUAL_V1')",
        "assert.equal(native.metadataKind,'EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_ACTUAL_V1')"))
    old = (PARENT/'deploy.mjs').read_text()
    check((HERE/'deploy.mjs').read_text() == old.replace(
        'ownedDirectoriesIncludingRoot:426',
        'ownedDirectoriesIncludingRoot:plan.applicationSchema.ownedDirectoriesIncludingRoot'))
    plan, parent = read(HERE/'plan.json'), read(PARENT/'plan.json')
    changed = [k for k in plan if plan[k] != parent.get(k)]
    check(changed == derivation['changedPlanFields'])
    check(set(plan) == set(parent) | {'requiredExternalRootAdmission'})
    for k in ['node','monitor','selectedInterfaces','expectedExport','washSourceCommit','washVersion',
              'outerSeconds','configSeconds','listenerSeconds','requestMilliseconds','maxResponseBytes',
              'gracefulStopMilliseconds','applicationCopy','guestPaths','worldFamily','readinessPolicy']:
        check(plan[k] == parent[k])
    check(plan['expectedArtifacts']['wash'] == parent['expectedArtifacts']['wash'])
    check(plan['expectedMetadataKind'] == 'EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_ACTUAL_V1')
    check(plan['expectedApp'] == dict(files=2186,bytes=48755844,directories=427,directoryCountExcludesRoot=True,symlinks=0))
    check(plan['applicationSchema']['ownedDirectoriesIncludingRoot'] == 428)
    check(plan['applicationSchema']['additionalDirectories'] == [])
    check(plan['applicationInputs'] == derivation['newActualCohort']['applicationInventory'])
    expected = plan['expectedArtifacts']
    check(expected['component']['sha256'] == 'd990ecc139a2466ce70fe7f6eabdc1fa4b0f85c7535834545f75b3099471407f')
    check(expected['engine']['sha256'] == '476b1c1d7a5f8b37d2c40d17510a98dd45676994b894663d445ae2f519cc33f6')
    check(expected['nativeMetadata']['sha256'] == '22f1d4561b73ce58b194afd5614368d30b16fc90f8fc7d63fe5c413916711b48')
    check(expected['constructionResult']['sha256'] == 'c1bd0e4dd939b0688ec451a1f2d81ee11d8186414953121411d749104f0c6ef0')
    policy = plan['requiredExternalRootAdmission']
    check(policy['constructionReview'] == derivation['newActualCohort']['constructionReview'])
    check(policy['fullNativeBuildReview'] == derivation['newActualCohort']['fullBuildReview'])
    check(policy['actualRootAuthority'] is None and policy['currentGuardReceipt'] is None and policy['actualResults'] is None)
    for k,v in parent.items():
        if k.startswith('actual'):
            check(v is None and plan[k] is None)
    check(len(plan['selectedInterfaces']) == len(set(plan['selectedInterfaces'])) == 13)
    check(all(x.endswith('@0.2.10') for x in plan['selectedInterfaces']))
    check(plan['expectedExport'] == 'wasi:http/incoming-handler@0.2.10')
    check(not (HERE/'index.json').exists())
    ast.parse((HERE/'run-owned.py').read_text())
    check(True)
    for r in plan['protectedSourceReferences']:
        check(row(Path(r['path'])) == r)
    for r in read(HERE/'source-citations.json')['localReferences']:
        check(row(Path(r['file']['path'])) == r['file'])
    print(json.dumps(dict(sourceTextChecks=count,passed=True,targetModuleImported=False,
                         nodeExecuted=False,washExecuted=False,guardExecuted=False,actorExecuted=False,
                         currentBinaryPayloadHashVerified=False)))

if __name__ == '__main__':
    main()
