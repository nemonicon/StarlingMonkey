"""Read/hash/AST verification only. Pass the independently approved index hash.

An optional exact source checkout is checked directly against all342 new rows
and the92 consumed tooling rows. This never applies files or admits an engine.
"""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import os
import stat
HERE=Path(__file__).resolve().parent
def sha(data):return hashlib.sha256(data).hexdigest()
def regular(path,digest,size=None):
    path=Path(path);before=path.lstat();assert stat.S_ISREG(before.st_mode),str(path)
    data=path.read_bytes();after=path.lstat()
    assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)
    assert sha(data)==digest,str(path)
    assert size is None or len(data)==size,str(path)
    return data
def below(root,name):
    assert isinstance(name,str)and'\0'not in name and'\\'not in name and not Path(name).is_absolute()
    assert all(part not in ('','.','..')for part in name.split('/'))
    path=root
    assert root.is_dir()and not root.is_symlink()
    for part in name.split('/'):
        path/=part;assert not path.is_symlink(),str(path)
    return path
def verify_packet(expected_index,source_root=None):
    assert len(expected_index)==64 and all(value in '0123456789abcdef'for value in expected_index)
    index=json.loads(regular(HERE/'index.json',expected_index))
    assert index['state']=='SEALED_UNAPPLIED_CLASSIC_TRACE_SOURCE_INTEGRATION_ACTIONS_HELD'
    names=set()
    for row in index['files']:
        assert row['path']not in names;names.add(row['path'])
        regular(below(HERE,row['path']),row['sha256'],row['bytes']).decode('utf-8')
    actual={str(path.relative_to(HERE))for path in HERE.rglob('*')if path.is_file()}
    assert actual==names|{'index.json'}
    assert not any(path.is_symlink()for path in HERE.rglob('*'))
    receipt=json.loads((HERE/'source-receipt.json').read_bytes())
    inputs=json.loads(regular(HERE/'input-freeze.json',receipt['inputFreezeSha256']))
    paths=set()
    for row in inputs['inputs']:
        path=(HERE/row['path']).resolve(strict=True);assert path not in paths;paths.add(path)
        regular(path,row['sha256'],row['bytes'])
    contract=json.loads((HERE/'contract.json').read_bytes());policy=json.loads((HERE/'policy.json').read_bytes())
    regular(HERE/'policy.json',contract['sourcePolicySha256'])
    regular(HERE/'layer-policy.py',contract['sourceHelperSha256'])
    regular(HERE/'source/tests/node-compat/build-engine.sh',contract['productionRecipeSha256'])
    regular(HERE/'source/tests/node-compat/classic-streams-admission.mjs',contract['productionAdmissionSha256'])
    regular(HERE/'source/tests/node-compat/module-selection.mjs',contract['productionSelectorSha256'])
    regular(HERE/'admission-pins.json',contract['admissionPinsSha256'])
    regular(HERE/'artifact-tools/tool-pins.json',contract['toolPinsSha256'])
    assert contract['newEngineHashes']is None and contract['reviewedFutureEnginePins']is None
    assert contract['nativeBuildApproved']is contract['liveApplicationApproved']is False
    assert set(json.loads((HERE/'runtime-pins.json').read_bytes())['variants'].values())=={None}
    old=json.loads(regular(HERE/'ancestry/policy.json',contract['previousPolicySha256']))
    regular(HERE/'ancestry/layer-policy.py',contract['previousHelperSha256'])
    regular(HERE/'ancestry/build-engine.sh',contract['previousRecipeSha256'])
    a={row['path']:row['sha256']for row in old['expectedNativeSourceManifest']}
    b={row['path']:row['sha256']for row in policy['expectedNativeSourceManifest']}
    assert len(a)==len(b)==342 and set(a)==set(b)
    changed={name for name in a if a[name]!=b[name]};assert len(changed)==3
    assert sum(a[name]==b[name]for name in a)==339
    delta=policy['classicTraceSourcePolicy']['changes'];assert {row['path']for row in delta}==changed
    for row in delta:
        assert a[row['path']]==row['beforeSha256']and b[row['path']]==row['afterSha256']
        regular(HERE/'ancestry/native-before'/row['path'],row['beforeSha256'],row['beforeBytes'])
        regular(HERE/'source'/row['path'],row['afterSha256'],row['afterBytes'])
    expected_policy=json.loads(json.dumps(old))
    expected_policy['version']='sm-private-ticks-classic-streams-trace-source-v1'
    expected_policy['classicPolicyVersion']='sm-classic-streams-trace-install-v1'
    expected_policy['classicTraceSourcePolicy']=policy['classicTraceSourcePolicy']
    for row in delta:
        expected_policy['sourceLayer'][row['path']]['afterSha256']=row['afterSha256']
        next(item for item in expected_policy['expectedNativeSourceManifest']if item['path']==row['path'])['sha256']=row['afterSha256']
    assert expected_policy==policy,'No unrelated source policy change is allowed'
    trace=policy['classicTraceSourcePolicy']
    for field,target in [('previousPolicySha256','previousPolicySha256'),('previousHelperSha256','previousHelperSha256'),('previousRecipeSha256','previousRecipeSha256'),('fixSourceIndexSha256','fixSourceIndexSha256'),('independentFixSourceReviewIndexSha256','independentFixSourceReviewIndexSha256')]:assert trace[field]==contract[target]
    assert policy['strictPolicyVersion']==old['strictPolicyVersion']and policy['protectedPolicyVersion']==old['protectedPolicyVersion']
    assert policy['embedding']==old['embedding']and policy['nativePatchSha256']==old['nativePatchSha256']
    assert policy['profileVersion']==old['profileVersion']=='sm-node-22.14.0-m0.12'
    assert policy['classicManifestSha256']==old['classicManifestSha256']
    preimages=json.loads((HERE/'ancestry/preimages.json').read_bytes())
    originals={row['path']:row for row in preimages['files']}
    proofs=json.loads((HERE/'transformations.json').read_bytes())['files']
    for row in proofs:
        original=originals[row['origin']]
        text=regular(HERE/original['copy'],row['beforeSha256'],original['bytes']).decode()
        before=text
        for edit in row['edits']:
            assert text.count(edit['old'])==edit['count'];text=text.replace(edit['old'],edit['new'])
        assert text==(HERE/row['afterimage']).read_text()and sha(text.encode())==row['afterSha256']
        for edit in reversed(row['edits']):
            for at in reversed(edit['offsets']):
                assert text[at:at+len(edit['new'])]==edit['new'];text=text[:at]+edit['old']+text[at+len(edit['new']):]
        assert text==before
        regular(HERE/row['patch'],row['patchSha256'])
    parsed=[]
    for path in sorted(HERE.rglob('*.py')):
        ast.parse(path.read_text(),filename=str(path));parsed.append(str(path.relative_to(HERE)))
    if source_root is not None:
        source_root=Path(os.path.abspath(source_root));assert source_root.is_dir()and not source_root.is_symlink()
        for row in policy['expectedNativeSourceManifest']:regular(below(source_root,row['path']),row['sha256'])
        tools=json.loads((HERE/'artifact-tools/tool-pins.json').read_bytes())
        for row in tools['toolDependencies']:regular(below(source_root,row['path']),row['sha256'],row['bytes'])
        packet_root=source_root/'tests/node-compat/foundation-classic-streams/trace-integration-candidate-v1'
        regular(packet_root/'index.json',expected_index)
        for row in index['files']:regular(below(packet_root,row['path']),row['sha256'],row['bytes'])
    return {'schemaVersion':1,'state':'EXACT_TRACE_INTEGRATION_SOURCE_SEAL_AND_339_PLUS_3_ANCESTRY_VERIFIED_NOT_ENGINE_ADMISSION',
      'indexedFiles':len(names),'consumedInputs':len(paths),'derivationsForwardAndReverse':len(proofs),
      'nativeSourcePaths':342,'unchangedNativePaths':339,'changedNativePaths':3,'pythonFilesAstParsed':len(parsed),
      'exactSourceRootRehashed':str(source_root)if source_root is not None else None,
      'newArtifactPinsAllNull':True,'runtimeAcceptanceClaim':False,'engineBytesReadAsNewArtifacts':False,
      'importsProducerActionMainsConfigureCompilerGuestHostOrTimingExecuted':False}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--index-sha256',required=True);parser.add_argument('--source-root');args=parser.parse_args()
    print(json.dumps(verify_packet(args.index_sha256,args.source_root)))
if __name__=='__main__':main()
