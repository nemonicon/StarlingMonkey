"""Create a fresh, explicit crypto construction caller; no owner APIs run."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
K = HERE.parent
PARENT = K / 'ownership-secret-component-candidate-v1'


def row(path):
    p = Path(path)
    assert p.is_file() and not p.is_symlink()
    b = p.read_bytes()
    return {'path': str(p), 'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b)}


def read(path):
    return json.loads(Path(path).read_bytes())


def write(name, data):
    p = HERE / name
    assert not p.exists(), 'Never overwrite a prepared or sealed source'
    p.write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')


def main():
    assert not (HERE / 'index.json').exists()
    parent_index = row(PARENT / 'index.json')
    assert parent_index['sha256'] == '4a2c1e2076c3215d094482abc6609481ca4e4c2d980cfa9daa158c44d02665f2'
    failure = K / 'independent-ownership-secret-component-failure-review-v1'
    failure_pair = {'index': row(failure / 'index.json'), 'result': row(failure / 'results.json')}
    assert failure_pair['index']['sha256'] == '6616a140cff1e1991d0a9043f965d705739353f25bd7c42cf3f600d58019a46a'
    contract = read(failure / 'result-contract.json')
    actual = read(failure_pair['result']['path'])
    for key, value in contract['requiredFixedValues'].items():
        assert actual[key] == value
    descriptor_fields = {'terminal': 'actualOwnedNodeTerminal', 'stdout': 'actualStdout', 'stderr': 'actualStderr',
                         'rootObservation': 'rootObservation', 'sourceIndex': 'sourceIndex'}
    assert set(descriptor_fields) == set(contract['requiredExactDescriptors'])
    for key, value in contract['requiredExactDescriptors'].items():
        assert actual[descriptor_fields[key]] == value
    refs = read(PARENT / 'references.json')
    refs.update(state='SOURCE_ONLY_SECRET355_COMPONENT_CONSTRUCTION_REFERENCES_V2', originalRoot=str(HERE),
                parentSourceIndex=parent_index, priorConstructionFailureReview=failure_pair,
                priorConstructionFailureContract=row(failure / 'result-contract.json'),
                requiredPackagingEnvironment=contract['requiredEnvironmentForAnySeparatelyAuthorizedSuccessor'],
                outputRoot='/private/tmp/starling-node-compat/crypto-owner355-secret-component-v2',
                externalRoot='/private/tmp/starling-node-compat/crypto-owner355-secret-component-v2-external-root')
    for name, key in [('guest.mjs', 'guest'), ('public-abi.wit', 'wit')]:
        (HERE / name).write_bytes((PARENT / name).read_bytes())
        refs[key] = row(HERE / name)
    before = (PARENT / 'build.mjs').read_text()
    after = before
    replacements = [
        (str(PARENT), str(HERE)),
        ('ROOT_REVIEWED_SECRET355_COMPONENT_CONSTRUCTION_V1', 'ROOT_REVIEWED_SECRET355_COMPONENT_CONSTRUCTION_V2'),
        ('SECRET355_COMPONENT_CONFIG_V1', 'SECRET355_COMPONENT_CONFIG_V2'),
        ('INDEPENDENT_CRYPTO_OWNER355_SECRET_COMPONENT_SOURCE_REVIEW_PASSED_V1', 'INDEPENDENT_CRYPTO_OWNER355_SECRET_COMPONENT_SOURCE_REVIEW_PASSED_V2'),
        ('SECRET_OWNER355_COMPONENT_CONSTRUCTED_UNREVIEWED_V1', 'SECRET_OWNER355_COMPONENT_CONSTRUCTED_UNREVIEWED_V2'),
        ('SECRET_OWNER355_COMPONENT_CONSTRUCTION_FAILED_V1', 'SECRET_OWNER355_COMPONENT_CONSTRUCTION_FAILED_V2'),
    ]
    for old, new in replacements:
        assert after.count(old) == 1, old
        after = after.replace(old, new)
    marker = 'export function constructionAuthority(root,own,refs){'
    helper = '''export function requiredPackagingEnvironment(environment,roles){
 const expected={NODE_COMPAT_TOOLCHAIN:roles.toolchainRoot,NODE_COMPAT_COMPONENTIZE_MODULE:join(roles.packagerRoot,'src/componentize.js')};
 for(const[key,value]of Object.entries(expected))need(environment?.[key]===value,'Required packaging environment: '+key);
 return Object.freeze(expected);
}
'''
    assert after.count(marker) == 1
    after = after.replace(marker, helper + marker)
    old = " need(root.actualComponentReview===null&&root.actualRuntimeAuthority===null,'No actual component/runtime adoption');captureDescriptor(root.retainedConfig);return true;"
    new = " need(same(root.requiredPackagingEnvironment,refs.requiredPackagingEnvironment),'Explicit packaging environment bound by Root');\n" + old
    assert after.count(old) == 1
    after = after.replace(old, new)
    old = ' const history=await validateActualPreflight(c,refs),retainedConfig=captureDescriptor(root.retainedConfig),ro=await c.read(retainedConfig);await c.file(ro.rootAuthority);'
    new = ''' const failure=await c.proof(refs.priorConstructionFailureReview),failureContract=await c.read(refs.priorConstructionFailureContract);
 for(const[key,value]of Object.entries(failureContract.requiredFixedValues))need(same(failure[key],value),'Exact prior construction failure: '+key);
 const failureDescriptorFields={terminal:'actualOwnedNodeTerminal',stdout:'actualStdout',stderr:'actualStderr',rootObservation:'rootObservation',sourceIndex:'sourceIndex'};
 need(same(Object.keys(failureDescriptorFields).sort(),Object.keys(failureContract.requiredExactDescriptors).sort()),'Complete failure descriptor roles');
 for(const[key,value]of Object.entries(failureContract.requiredExactDescriptors))need(same(failure[failureDescriptorFields[key]],value),'Exact prior failure descriptor: '+key);
 need(failureContract.grantsRetryOrRuntimeAuthority===false&&same(refs.requiredPackagingEnvironment,failureContract.requiredEnvironmentForAnySeparatelyAuthorizedSuccessor),'Failure evidence does not authorize this phase');
''' + old
    assert after.count(old) == 1
    after = after.replace(old, new)
    old = " await headroom(dirname(refs.outputRoot),2*1024*1024*1024);try{await lstat(refs.outputRoot);throw new Error('Fresh output root required');}catch(e){need(e.code==='ENOENT','Fresh output root required');}"
    new = " const packagingEnvironmentRecord=requiredPackagingEnvironment(process.env,refs.physicalRoles);need(same(packagingEnvironmentRecord,refs.requiredPackagingEnvironment),'Actual required packaging environment');\n" + old
    assert after.count(old) == 1
    after = after.replace(old, new)
    old = "  await out.write('retained-record-data.json',Object.fromEntries(Object.entries(record).filter(([k])=>k!=='recheck')),{json:true});"
    new = "  await out.write('required-packaging-environment.json',packagingEnvironmentRecord,{json:true});\n" + old
    assert after.count(old) == 1
    after = after.replace(old, new)
    (HERE / 'build.mjs').write_text(after)
    write('references.json', refs)
    ledger = read(PARENT / 'source-inputs.json')
    files = {x['path']: x for x in ledger['files']}
    families = {x['path']: x for x in ledger['families']}
    for p in [PARENT, K / 'independent-ownership-secret-component-source-review-v1', failure]:
        ix = row(p / 'index.json')
        families[ix['path']] = ix
        files[ix['path']] = ix
        for m in read(p / 'index.json')['files']:
            d = dict(m, path=str(p / m['path']))
            assert row(d['path']) == d
            files[d['path']] = d
    for d in contract['requiredExactDescriptors'].values():
        assert row(d['path']) == d
        files[d['path']] = d
    files[refs['priorConstructionFailureContract']['path']] = refs['priorConstructionFailureContract']
    write('source-inputs.json', dict(schemaVersion=1, files=sorted(files.values(), key=lambda x: x['path']),
                                  families=list(families.values()), completeDeclaredRuntimeIntake=True,
                                  allSourceAndProtectionBeforeFirstCustomImport=True, preparationOnly=True))
    for name in ['future-validation-workload.json', 'future-artifact-boundary.json']:
        (HERE / name).write_bytes((PARENT / name).read_bytes())
    authority = read(PARENT / 'future-root-authority.template.json')
    authority.update(outputRoot=refs['outputRoot'], externalRoot=refs['externalRoot'], requiredPackagingEnvironment=refs['requiredPackagingEnvironment'])
    write('future-root-authority.template.json', authority)
    write('future-config.template.json', dict(schemaVersion=1, state='SECRET355_COMPONENT_CONFIG_V2', sourceIndex=None, rootAuthority=None))
    write('future-source-review-contract.json', dict(schemaVersion=1, state='INDEPENDENT_CRYPTO_OWNER355_SECRET_COMPONENT_SOURCE_REVIEW_PASSED_V2',
                                                   componentSourceIndexSha256=None, sourceOnly=True, sourceReviewPassed=True,
                                                   ownerActionsInvoked=False, actualComponentProof=None))
    write('derivations.json', dict(schemaVersion=1, parent=parent_index, parentEntry=row(PARENT / 'build.mjs'), entry=row(HERE / 'build.mjs'),
                                  replacements=[dict(before=a, after=b) for a, b in replacements],
                                  changes=['New genuine source/config/authority/output contexts', 'Full prior failure DATA binding',
                                           'Root binds explicit packaging paths', 'Pure exact environment check before any custom import',
                                           'Record only two authenticated nonsecret packaging paths'],
                                  guestByteExact=refs['guest']['sha256'] == '26e48b2117eb232cb20c232f4c94b0bba1f359a9be0806629819e2caf9508c45',
                                  publicAbiByteExact=refs['wit']['sha256'] == '18d499ca3c93ad6ad771087d4bbb36500a329e4acf323517b6a88a0241e4fa4d',
                                  oldFilesModified=False, nativeFiles=355, embeddingFiles=3, manifests=11))
    print(json.dumps(dict(sourceOnly=True, files=len(files), families=len(families), ownerActions=0)))


if __name__ == '__main__':
    main()
