"""Read/hash/AST audit of this finite source family. No action modules imported."""
from pathlib import Path
import ast,hashlib,json,os,re
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
checks=[]
def sha(value):return hashlib.sha256(value).hexdigest()
def check(name,condition=True):assert condition,name;checks.append(name)
def main():
    origins=json.loads((HERE/'packaging-origins.json').read_bytes())
    assert origins['localModules']==12 and origins['selectedDataAndAdapter']==8
    for row in origins['files']:
        copy=(HERE/row['path']).read_bytes();assert sha(copy)==row['sha256']and len(copy)==row['bytes'];assert Path(row['original']).read_bytes()==copy
    check('physical20SnapshotFilesAndOrigins')
    five={'builtins/node-compat/classic-streams/classic-core.generated.mjs','builtins/node-compat/classic-streams/transformation-receipt.json','builtins/node-compat/classic-streams/factories.generated.h','tests/node-compat/build-engine.sh','tests/node-compat/classic-streams-admission.mjs'}
    for row in origins['files']:assert Path(row['original'])not in [REPO/name for name in five]
    check('snapshotDoesNotReadLiveRootFive')
    closure=json.loads((HERE/'component-tool-closure.json').read_bytes());assert len(closure['files'])==20
    for row in closure['files']+closure['packages']+closure['endpoints']+closure['packageData']:
        value=Path(row['path']).read_bytes();assert sha(value)==row['sha256']and len(value)==row['bytes']
    check('actual4Packages5Endpoints27ProvenanceInputs',len(closure['packages'])==4 and len(closure['endpoints'])==5 and len(closure['packageData'])==27)
    check('twelveFiniteModulesAndTwelveInactiveLazyData',closure['scope']['localModules']==12 and len(closure['inactiveLazyReads'])==12 and all(row['usage']=='EXCLUDED_NOT_CALLED'for row in closure['inactiveLazyReads']))
    tools=json.loads((HERE/'tool-context.json').read_bytes());assert len(tools['toolTrees'])==2 and len(tools['toolLinks'])==22
    outside=[]
    for row in tools['inputs']:
        path=Path(row['path']);value=path.read_bytes();assert sha(value)==row['sha256']and len(value)==row['bytes']
        if not any(path.resolve().is_relative_to(Path(root['realPath']))for root in tools['toolTrees']):outside.append(str(path))
    check('actual4890TreeFilesPlusTwoInvocationBinaries',len(tools['inputs'])==4892 and len(outside)==2 and outside==[tools['invocation']['nodeRealPath'],tools['invocation']['wasmtimeRealPath']])
    native=REPO/'tests/node-compat/foundation-stream-consumers/native-integration-candidate-v2'
    for root,expected in[(native,'9edf31c16af401ac688a4ab9bfe2a01f0338739a6554fc12caa3b2f8ba03a378'),(HERE.parent/'independent-native-integration-v2-source-review-v1','283008266ff55471723d1aff05bc66c5d48663346f1d4bc90752c4278f827811')]:
        raw=(root/'index.json').read_bytes();assert sha(raw)==expected
        for row in json.loads(raw)['files']:assert sha((root/row['path']).read_bytes())==row['sha256']
    check('producer59AndSourcePeerIndexedOnly')
    for path in HERE.glob('*.py'):ast.parse(path.read_bytes())
    check('pythonAstOnly')
    main=(HERE/'component.mjs').read_text();profile=(HERE/'profiles.mjs').read_text()
    check('noPrivateFactoryBundledOrInvoked','createConsumersModule('not in main+profile and "from './prototype.mjs'"not in main+profile)
    check('settledSnapshotAndCombinedGcMarkers',all(value in main for value in['const snapshotText=await consumers.text','const snapshotJson=await consumers.json','vmTemporaryRootsIsolated:false','applicationStrongOwnerRetained:true']))
    config=json.loads((HERE/'future-authority.json').read_bytes());check('allAuthorityNullBeforeActions',all(value is None for value in config['variants'].values())and config['reviewedPinsPath']is None and config['rootReviewPath']is None)
    activation=(HERE/'activate.py').read_text();template=(HERE/'runtime-preflight.template.mjs').read_text()
    check('genuine355BootstrapNot350Projection','consumersBootstrapPreflight' in template and 'native.metadata.sourceManifest.length,355' in template and 'metadata.sourceManifest='not in template and 'selectedManifestsForEngine'not in template)
    check('configuredFrozenAndSnapshotContextsDistinct','nativeConfiguredSourceRoot' in template and 'componentToolRoot' in template and 'assert.notEqual(componentToolRoot,config.nativeConfiguredSourceRoot)'in template and "native['configuredSourceRoot']"in activation)
    check('exactPublicPayloadAndExclusiveFutureSourceOutput','component-validation-activated-v2'in activation and 'assert not DEST.exists()'in activation and "NATIVE_ORIGINAL"in activation and 'original==staged'in activation)
    result={'schemaVersion':1,'state':'FINITE_SOURCE_AND_PHYSICAL_PACKAGING_CLOSURE_CHECKED','passed':len(checks),'checks':checks,'packagingModules':12,'selectedDataAndAdapter':8,'toolTrees':2,'toolLinks':22,'treeFileRows':4890,'invocationBinaries':outside,'nativeAuthorityRole':'NONE until genuine futureRoot355 bootstrap','compilerFactoryVerifierBootstrapComponentizerGuestHostOrTimingExecuted':False}
    output=Path(os.environ['CONSUMERS_VALIDATION_CLOSURE_TEST_OUTPUT']);assert not output.exists();output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x')as target:json.dump(result,target,indent=2);target.write('\n')
    print(json.dumps({'passed':len(checks),'scope':'read-only source/physical data','guestExecuted':False}))
if __name__=='__main__':main()
