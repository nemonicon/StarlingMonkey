"""Seal the bounded proposal and original-context references only; no action imports."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
def sha(value):return hashlib.sha256(value).hexdigest()
def describe(path):
    path=Path(path).absolute();assert path.is_file()and not path.is_symlink();value=path.read_bytes()
    return{'path':str(path),'realpath':str(path.resolve()),'sha256':sha(value),'bytes':len(value)}
def put(name,value):
    with(HERE/name).open('x')as out:json.dump(value,out,indent=2);out.write('\n')
def main():
    assert not(HERE/'index.json').exists();inputs={}
    def add(path,role,digest=None,size=None):
        row=describe(path)
        if digest:assert row['sha256']==digest
        if size is not None:assert row['bytes']==size
        if row['path']in inputs:assert all(inputs[row['path']][key]==value for key,value in row.items());inputs[row['path']]['roles'].append(role)
        else:inputs[row['path']]={**row,'roles':[role]}
    native=REPO/'tests/node-compat/foundation-stream-consumers/native-integration-candidate-v2'
    staged=Path('/private/tmp/starling-node-compat/consumers-source-v2/tests/node-compat/foundation-stream-consumers/native-integration-candidate-v2')
    for root,digest,role in[(native,'9edf31c16af401ac688a4ab9bfe2a01f0338739a6554fc12caa3b2f8ba03a378','ORIGINAL_PRODUCER_INDEXED_ONLY_NO_PREP_REINTERPRETATION'),(staged,'9edf31c16af401ac688a4ab9bfe2a01f0338739a6554fc12caa3b2f8ba03a378','STAGED_ACTUAL355_PRODUCER_INDEXED_ONLY'),(HERE.parent/'independent-native-integration-v2-source-review-v1','283008266ff55471723d1aff05bc66c5d48663346f1d4bc90752c4278f827811','INDEXED_ONLY_SOURCE_PEER')]:
        add(root/'index.json',role,digest)
        for row in json.loads((root/'index.json').read_bytes())['files']:add(root/row['path'],role,row['sha256'],row['bytes'])
    for row in json.loads((HERE/'packaging-origins.json').read_bytes())['files']:add(row['original'],'PACKAGING_SNAPSHOT_EXACT_ORIGIN',row['sha256'],row['bytes'])
    for row in json.loads((HERE/'tool-context.json').read_bytes())['inputs']:add(row['path'],'ACTUAL_TWO_TOOL_TREES_OR_INVOCATION_BINARY',row['sha256'],row['bytes'])
    closure=json.loads((HERE/'component-tool-closure.json').read_bytes())
    for row in closure['packages']+closure['endpoints']+closure['packageData']:add(row['path'],'ACTUAL_PACKAGE_ENDPOINT_PROVENANCE',row['sha256'],row['bytes'])
    live=json.loads((HERE/'live-inputs.json').read_bytes())
    for row in[live['adapter'],*live['wit']]:add(row['path'],'REOPENED_LIVE_ADAPTER_WIT',row['sha256'],row['bytes'])
    for name in['node-checks.mjs','node-results.json','prototype-node-results.json','metadata-v2/component-checks.mjs']:add(HERE.parent/name,'INPUT_ORACLE_ANCESTRY_ONLY_NOT293_RUNTIME_PROOF')
    old=REPO/'tests/node-compat/foundation-zlib/component-validation-activated-v8'
    for name in['durable-host.mjs','consumed.mjs','component-tools.mjs','run-validation.mjs','runtime-preflight.mjs','input-freeze.json']:add(old/name,'CORRECTED_TRANSPORT_OR_CONTEXT_REFERENCE_NOT350_RUNTIME_PROOF')
    # Payload/snapshot files are sealed both in this index and in the explicit
    # preparation list used by the later exclusive publisher.
    for path in sorted(HERE.rglob('*')):
        if path.is_file()and '__pycache__'not in path.parts and path.name not in['index.json','source-inputs.json','source-receipt.json']:add(path,'OWNED_SOURCE_PAYLOAD_OR_DATA')
    put('source-inputs.json',{'schemaVersion':1,'state':'SOURCE_PREPARATION_REFERENCES_NOT_ACTIVATED_RUNTIME_SEAL','originalPreparationRoot':str(HERE),'files':sorted(inputs.values(),key=lambda row:row['path']),'nativeConfiguredSourceRoot':'/private/tmp/starling-node-compat/consumers-source-v2','componentToolRoot':str(HERE/'packaging-tools'),'originalAncestorPreparationRowsReinterpreted':False,'futureActualAuthority':None})
    put('source-receipt.json',{'schemaVersion':1,'state':'UNACTIVATED_CONSUMERS355_COMPONENT_VALIDATION_SOURCE_CANDIDATE','nativeProducerIndexSha256':'9edf31c16af401ac688a4ab9bfe2a01f0338739a6554fc12caa3b2f8ba03a378','nativeSourceFiles':355,'profileVersion':'sm-node-22.14.0-m0.14','differentialGroups':18,'profileGroups':12,'additionalPublicGroups':8,'normalCaseRecordsPlanned':190,'caughtRefusalFields':6,'initializationFailuresPlanned':11,'consumerOffImportDenials':8,'consumerOffSmokeObservations':5,'combinedOwnerGcObservations':4,'publicRunParameterType':'u32','packagingModules':12,'selectedDataAndAdapter':8,'packages':4,'endpoints':5,'packageProvenanceFiles':27,'toolTrees':2,'toolLinks':22,'actualToolTreeFileRows':4890,'additionalInvocationBinaryRows':2,'sourceChecks':64,'closureChecks':13,'syntaxChecks':31,'newNodeHostOracleGroups':8,'actualFutureEngineTuples':None,'sourceActivationOrActualNativeBootstrapExecuted':False,'factoryCompilerComponentizerGuestTargetHostOrTimingExecuted':False,'oldRuntimeProofTransferred':False,'operationalAdmission':False,'HTTPBodyCancelOrReuseClaim':False,'sourceInputs':len(inputs)})
    files=[]
    for path in sorted(HERE.rglob('*')):
        if path.is_file()and '__pycache__'not in path.parts and path.name!='index.json':
            value=path.read_bytes();files.append({'path':str(path.relative_to(HERE)),'sha256':sha(value),'bytes':len(value)})
    put('index.json',{'schemaVersion':1,'state':'SOURCE_ONLY_CONSUMERS355_COMPONENT_VALIDATION_SEALED','files':files,'sourceInputs':len(inputs),'actualFutureEnginePins':None,'runtimeAcceptanceClaim':False})
    print(json.dumps({'files':len(files),'sourceInputs':len(inputs),'indexSha256':sha((HERE/'index.json').read_bytes()),'receiptSha256':sha((HERE/'source-receipt.json').read_bytes())}))
if __name__=='__main__':main()
