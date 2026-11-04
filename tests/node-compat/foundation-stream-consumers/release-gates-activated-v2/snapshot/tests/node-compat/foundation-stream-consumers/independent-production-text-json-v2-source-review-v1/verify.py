"""Read-only independent successor reader. No proposal imports or action tools."""
from pathlib import Path
import ast
import hashlib
import json
import re

HERE=Path(__file__).resolve().parent
FAMILY=HERE.parent
NEW=FAMILY/'production-text-json-candidate-v2'
OLD=FAMILY/'production-text-json-candidate-v1'
HOLD=FAMILY/'independent-production-text-json-source-review-v1'
REPO=HERE.parents[3]
STAGE=Path('/tmp/starling-node-compat/zlib-source-v4')
NEW_SHA='eedeef581d961030b9aac3bf87c43e0f58cfe5516c5b04d997eb095c6df7ef7a'
OLD_SHA='d768d71244695d18914844c860f1053e0c09d67cf2b321bffedfeb2e911ebba1'
HOLD_SHA='b58cf2dc101686c63dce246e52702794ca08b76a8f68168b44162be6cfadc202'
HELPER_SHA='3df425d7fcfaf241b7c8d6f889bcefb8efde229af8df5e4c610e18a49b1bfd0c'
HELPER_REL='tests/node-compat/foundation-zlib/native-integration-candidate-v4/codec-evidence.py'
checks=[]
seen={}

def sha(value):return hashlib.sha256(value).hexdigest()
def raw(path):
    path=Path(path);before=path.lstat()
    assert path.is_file() and not path.is_symlink(),path
    value=path.read_bytes();after=path.lstat()
    assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),path
    row={'sha256':sha(value),'bytes':len(value),'realpath':str(path.resolve())}
    if str(path) in seen:assert seen[str(path)]==row,path
    else:seen[str(path)]=row
    return value
def obj(path):return json.loads(raw(path))
def check(label,condition):assert condition,label;checks.append(label)
def index(root,expected):
    value=raw(root/'index.json');assert sha(value)==expected
    result=json.loads(value);paths=set()
    for row in result['files']:
        assert row['path'] not in paths and not row['path'].startswith('/') and all(p not in ('','.','..') for p in row['path'].split('/'))
        paths.add(row['path']);value=raw(root/row['path'])
        assert sha(value)==row['sha256'] and len(value)==row['bytes']
    return result
def derive(value,edits):
    original=value
    for row in edits:
        if row.get('kind')=='append':value+=row['new']
        else:assert value.count(row['old'])==row['count'];value=value.replace(row['old'],row['new'])
    after=value
    for row in reversed(edits):
        if row.get('kind')=='append':assert value.endswith(row['new']);value=value[:-len(row['new'])]
        else:assert value.count(row['new'])==row['count'];value=value.replace(row['new'],row['old'])
    assert value==original
    return after

def main():
    new=index(NEW,NEW_SHA);old=index(OLD,OLD_SHA);hold=index(HOLD,HOLD_SHA)
    check('new39Old37Hold3IndexedBytes',len(new['files'])==39 and len(old['files'])==37 and len(hold['files'])==3)
    inputs=obj(NEW/'source-inputs.json');assert len(inputs['files'])==506
    paths=set()
    for row in inputs['files']:
        assert row['path'] not in paths;paths.add(row['path'])
        value=raw(row['path']);assert sha(value)==row['sha256'] and len(value)==row['bytes'] and str(Path(row['path']).resolve())==row['realpath']
    check('all506PreparationReferences',True)
    receipt=obj(NEW/'source-receipt.json')
    check('receiptExactAnchor',sha(raw(NEW/'source-receipt.json'))=='371750eeb421ceb56efd2c7a2979b5dd5fa43526569cc22383d39fba49c33e5e')
    proof=obj(NEW/'successor-derivations.json')
    check('parentAndHoldAuthority',proof['parentCandidateIndexSha256']==OLD_SHA and proof['parentHoldIndexSha256']==HOLD_SHA and receipt['v1Candidate']['sha256']==OLD_SHA and receipt['v1Hold']['sha256']==HOLD_SHA)
    before=raw(OLD/'proposed/tests/node-compat/build-engine.sh').decode()
    recipe=raw(NEW/'proposed/tests/node-compat/build-engine.sh').decode()
    check('recipeExactThreeTransformReverse',derive(before,proof['recipe']['edits'])==recipe and [r['count'] for r in proof['recipe']['edits']]==[3,3,2])
    check('recipeBeforeAfterPins',sha(before.encode())==proof['recipe']['beforeSha256'] and sha(recipe.encode())==proof['recipe']['afterSha256']==receipt['recipe']['sha256'])
    check('freshNamespaceAndChildPaths','consumers-v1' not in recipe and recipe.count('consumers-v2')==3 and 'production-text-json-candidate-v1' not in recipe and recipe.count('production-text-json-candidate-v2')==3)
    exact="codec_file=pathlib.Path(repo)/'"+HELPER_REL+"'"
    check('bothCorrectedPathsAndExactHashAssertions',recipe.count(exact)==2 and recipe.count("assert digest(codec_file)=='"+HELPER_SHA+"'")==2 and "codec_file=layer_file.parent/'codec-evidence.py'" not in recipe)
    helper_records=[]
    for root in [REPO,STAGE]:
        path=root/HELPER_REL;value=raw(path)
        assert sha(value)==HELPER_SHA and len(value)==16287
        helper_records.append({'path':str(path),**seen[str(path)]})
    check('physicalRepoAndStagedParentHelperBytes',True)
    check('oldAndNewChildMissingExplicitlyRetained',not (OLD/'codec-evidence.py').exists() and not (NEW/'codec-evidence.py').exists())
    blocks=[ast.parse(m.group(2)) for m in re.finditer(r"<<'([A-Z][A-Z0-9_]*)'\n(.*?)\n\1(?:\n|$)",recipe,re.S)]
    assignments=[node for tree in blocks for node in ast.walk(tree) if isinstance(node,ast.Assign) and any(isinstance(n,ast.Name) and n.id=='codec_file' for n in node.targets)]
    assert len(assignments)==2
    for node in assignments:
        expr=node.value;assert isinstance(expr,ast.BinOp) and isinstance(expr.op,ast.Div) and isinstance(expr.right,ast.Constant) and expr.right.value==HELPER_REL
        call=expr.left;assert isinstance(call,ast.Call) and isinstance(call.func,ast.Attribute) and isinstance(call.func.value,ast.Name) and call.func.value.id=='pathlib' and call.func.attr=='Path' and len(call.args)==1 and isinstance(call.args[0],ast.Name) and call.args[0].id=='repo'
    check('bothActualEmbeddedPythonAstPaths',len(blocks)==4)
    for name in ['policy.json','layer-policy.py','expected-native-source-manifest.json','native.UNAPPLIED.patch','native-derivations.json','build-only-selection.mjs']:
        assert raw(NEW/name)==raw(OLD/name)
    check('nativePolicyHelperManifestPatchAndBuildHookByteIdentical',True)
    native=obj(NEW/'native-derivations.json')
    native_paths=native['addedSources']+[r['path'] for r in native['changes']]
    assert len(native_paths)==7
    for path in native_paths:assert raw(NEW/'proposed'/path)==raw(OLD/'proposed'/path)
    check('allSevenNativeAfterimagesExact',True)
    policy=obj(NEW/'policy.json');parent_root=REPO/'tests/node-compat/foundation-zlib/native-integration-candidate-v4'
    parent=index(parent_root,policy['streamConsumersSourcePolicy']['parentIndexSha256'])
    parent_policy=obj(parent_root/'policy.json')
    before_sources={r['path']:r['sha256'] for r in parent_policy['expectedNativeSourceManifest']}
    after_sources={r['path']:r['sha256'] for r in policy['expectedNativeSourceManifest']}
    assert len(before_sources)==350 and len(after_sources)==355 and sum(after_sources[p]==before_sources[p] for p in before_sources)==348
    assert set(after_sources)-set(before_sources)==set(native['addedSources'])
    for path,digest in after_sources.items():
        source=NEW/'proposed'/path if path in native_paths else STAGE/path
        assert sha(raw(source))==digest
    check('actualProposed355Bytes348Unchanged2Replacements5Adds',True)
    check('noNewCppAndParent85Stable',not any(p.endswith('.cpp') for p in set(after_sources)-set(before_sources)) and len(parent['files'])==85)
    for row in obj(NEW/'host-derivations.json')['changes']:
        original=raw(row['source']).decode();after=raw(NEW/row['target']).decode()
        assert derive(original,row['edits'])==after and sha(after.encode())==row['afterSha256']
    check('allFourParent350HostForwardReverseProofs',True)
    pins=obj(NEW/'admission-pins.json');old_pins=obj(OLD/'admission-pins.json')
    expected_pins={**old_pins,'productionRecipeSha256':sha(recipe.encode())}
    check('pinsOnlyRecipeChangedAndFutureNull',pins==expected_pins and pins['reviewedFutureEnginePins'] is None)
    admission=raw(NEW/'proposed/tests/node-compat/stream-consumers-admission.mjs').decode()
    original_admission=raw(OLD/'proposed/tests/node-compat/stream-consumers-admission.mjs').decode()
    expected_admission=original_admission.replace(sha(raw(OLD/'admission-pins.json')),sha(raw(NEW/'admission-pins.json'))).replace(sha(before.encode()),sha(recipe.encode())).replace('production-text-json-candidate-v1','production-text-json-candidate-v2')
    check('admissionOnlyOwnPinRecipePathRebind',admission==expected_admission)
    check('moduleSelectorByteIdentical',raw(NEW/'proposed/tests/node-compat/module-selection.mjs')==raw(OLD/'proposed/tests/node-compat/module-selection.mjs'))
    check('operational350And355RemainClosed',"assert.fail('Consumers355 operational admission CLOSED:" in admission and "assert.fail('Zlib350 operational admission CLOSED:" in raw(STAGE/'tests/node-compat/zlib-admission.mjs').decode())
    check('noMetadataProjectionOrOld350SelectorAuthorization','const current=entries(metadata.sourceManifest);assert.equal(current.length,355);assert.deepEqual(current,entries(policy.expectedNativeSourceManifest));' in admission and 'metadata.sourceManifest=' not in admission and "metadata['sourceManifest']=" not in raw(NEW/'layer-policy.py').decode())
    checks_doc=obj(NEW/'checks.json');assert len(checks_doc['commands'])==11 and all(row['exitCode']==0 for row in checks_doc['commands'])
    stored=[]
    for row in checks_doc['commands']:
        if row['stdout'].startswith('{'):
            report=json.loads(row['stdout'])
            if 'passed' in report:stored.append(report['passed'])
    check('stored33Source21Denial18PhysicalChecksAuthenticated',stored==[33,18,21])
    path_test=raw(NEW/'test-codec-paths.py').decode()
    check('physicalPathTestDoesNotImportCollector','importlib' not in path_test and 'exec(' not in path_test and 'codecHelperImported' in path_test and 'for root in[REPO,BASE]' in path_test)
    for path in NEW.glob('*.py'):ast.parse(raw(path))
    check('pythonAstOnlyNoOwnerCodeExecution',True)
    check('templateAndFutureEvidenceBoundary',receipt['installed'] is False and receipt['futureEnginePins'] is None and receipt['operationalAdmission']=='CLOSED' and receipt['artifactFrameworkDeferred'] is True and receipt['historicalEvidenceIsRuntimeProofFor355'] is False and receipt['nativeSdkSyntaxBuildFactoryCodecBundlerGuestHostOrTimingExecuted'] is False)
    for path in list(seen):raw(path)
    check('allObservedInputsStableAfterRead',True)
    result={'schemaVersion':1,'state':'INDEPENDENT_STREAM_CONSUMERS355_V2_SOURCE_REVIEW_PASSED_V1','packetIndexSha256':NEW_SHA,'oldCandidateIndexSha256':OLD_SHA,'oldHoldIndexSha256':HOLD_SHA,
      'resolvedBlocker':'CONS355-M1','newPacketFilesVerified':39,'preparationInputsVerified':506,'nativeSourceBytesVerified':355,'nativePayloadChangesFromV1':0,'nativePrivateCppAdded':0,
      'checks':checks,'checksPassed':len(checks),'blockers':[],'actualHelperPaths':helper_records,
      'fixedRecipeAssignmentLines':[i for i,line in enumerate(recipe.splitlines(),1) if line==exact],
      'nativeCompilerOrConsumerRuntimeClaim':False,'operationalAdmission':'CLOSED','futureActualEnginePins':None,
      'limitations':['Source/path/data review only: no owner helper/test/factory, compiler/build, genuine native admission/preflight, bundler/componentizer, guest/host/timing action executed.',
      'Stored33/21/18 checks authenticated/read, not rerun. Independent Python only reads/hashes/AST/parses text.',
      '355 artifact/bootstrap framework, SDK syntax, actual compile/config/freeze proofs and registered runtime/component/HTTP acceptance remain pending.',
      'Unchanged metadata-v2 installed:false293 evidence supplies algorithm sources only, not355 proof. No Blob/raw Web async iteration/reset/reuse/full Node/performance claim.'],
      'readFileCount':len(seen),'readFiles':dict(sorted(seen.items()))}
    with (HERE/'results.json').open('x') as output:json.dump(result,output,indent=2);output.write('\n')
    print(json.dumps({k:result[k] for k in ['state','newPacketFilesVerified','preparationInputsVerified','nativeSourceBytesVerified','checksPassed','resolvedBlocker','blockers']}))

if __name__=='__main__':main()
