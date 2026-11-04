"""Seal finite original-context source evidence only; no action helper imports."""
from pathlib import Path
import ast,hashlib,json
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
def sha(value):return hashlib.sha256(value).hexdigest()
def describe(path):
    path=Path(path).absolute();before=path.stat();assert path.is_file()and not path.is_symlink(),path
    value=path.read_bytes();after=path.stat();assert(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)
    return{'path':str(path),'realpath':str(path.resolve()),'sha256':sha(value),'bytes':len(value)}
def put(name,value):
    with(HERE/name).open('x')as output:json.dump(value,output,indent=2);output.write('\n')
def main():
    assert not(HERE/'index.json').exists()
    refs={}
    def add(path,role,expected=None,size=None):
        row=describe(path)
        if expected is not None:assert row['sha256']==expected
        if size is not None:assert row['bytes']==size
        if row['path']in refs:assert all(refs[row['path']][k]==v for k,v in row.items());refs[row['path']]['roles'].append(role)
        else:refs[row['path']]={**row,'roles':[role]}
    for row in json.loads((HERE/'tool-origins.json').read_bytes())['files']:add(row['original'],'EXACT_FUTURE_STAGED_TOOL_SOURCE',row['sha256'],row['bytes'])
    source=HERE.parent/'production-text-json-candidate-v2';native=json.loads((HERE/'policy.json').read_bytes())['expectedNativeSourceManifest']
    derivation=json.loads((source/'native-derivations.json').read_bytes());new=set(derivation['addedSources']+[r['path']for r in derivation['changes']])
    for row in native:add(source/'proposed'/row['path']if row['path']in new else Path('/tmp/starling-node-compat/zlib-source-v4')/row['path'],'ACTUAL_NATIVE_SOURCE355',row['sha256'])
    for root,name,key,role in[(REPO/'tests/node-compat/foundation-zlib/native-integration-candidate-v4','input-freeze.json','inputs','PARENT350_PREPARATION_ORIGINAL_CONTEXT_ONLY'),(source,'source-inputs.json','files','CONSUMER_SOURCE_PREPARATION_ORIGINAL_CONTEXT_ONLY')]:
        add(root/'index.json',role);add(root/name,role)
        for row in json.loads((root/name).read_bytes())[key]:
            path=Path(row['path']);path=path if path.is_absolute()else root/path
            add(path,role,row['sha256'],row['bytes'])
    for root in[HERE.parent/'independent-production-text-json-v2-source-review-v1',HERE.parent/'sdk-registration-syntax-v1']:
        add(root/'index.json','INDEXED_ONLY_SOURCE_PEER_OR_SDK_CONTEXT')
        for row in json.loads((root/'index.json').read_bytes())['files']:add(root/row['path'],'INDEXED_ONLY_SOURCE_PEER_OR_SDK_CONTEXT',row['sha256'],row['bytes'])
    put('input-freeze.json',{'schemaVersion':1,'state':'ORIGINAL_PREPARATION_REFERENCES_NOT_RELOCATABLE_ACTION_CONTEXT','originalPreparationRoot':str(HERE),'inputs':sorted(refs.values(),key=lambda r:r['path']),'originalPrepRowsMustNeverBeReinterpretedInStagedActionHelpers':True,'nativeInputs':355,'toolRows':767,'componentHarnessClosureProvided':False,'actualFuturePins':None})
    tools=json.loads((HERE/'artifact-tools/tool-pins.json').read_bytes())
    evidence=json.loads((HERE/'evidence/source-tests.json').read_bytes())
    put('source-receipt.json',{'schemaVersion':1,'state':'UNAPPLIED_CONSUMERS355_NATIVE_ARTIFACT_FRAMEWORK_SOURCE_ONLY','parent350IndexSha256':'d384af814a95fa873afdca5bf31b61197463279b487064b6366ceaf6aad71172','consumerSourceIndexSha256':'eedeef581d961030b9aac3bf87c43e0f58cfe5516c5b04d997eb095c6df7ef7a','consumerSourceReviewSha256':'01f432678d2408d7645d35afea5abd73f192206c6dd3d4197f4ad7a83a0ad9d1','sdkSyntaxIndexSha256':'5d0f51bd3325fc3ec36743e10b5da55980a9f956469b7f76c902f5ab8c037117','recipeSha256':tools['recipeSha256'],'sourcePolicySha256':tools['sourcePolicySha256'],'sourceHelperSha256':tools['sourceHelperSha256'],'nativeInputs':355,'nativeCpp':62,'strictCpp':4,'privateNodeCpp':6,'embeddingCpp':1,'nativePayloadChangedFromReviewedConsumerSource':False,'toolRows':767,'toolPinsSha256':sha((HERE/'artifact-tools/tool-pins.json').read_bytes()),'preparationReferences':len(refs),'pureDataSourceChecks':evidence['passed'],'nodeSyntaxChecks':3,'initialLabels':['normal-off','gc-off','disabled-off'],'consumerOffKeepsZlibOn':True,'futureRuntimeOnlyPin':None,'futureAllPinsNull':True,'stagePublisherExecuted':False,'nativeBuildFreezerExporterVerifierBootstrapFactoryCodecBundlerGuestHostOrTimingExecuted':False,'historical350SdkAnd293EvidenceTransferredAs355RuntimeProof':False,'operationalAdmission':False,'componentHarnessClosureComplete':False})
    files=[]
    for path in sorted(HERE.rglob('*')):
        if path.is_file()and '__pycache__'not in path.parts and path.name!='index.json':
            row=describe(path);files.append({'path':str(path.relative_to(HERE)),'sha256':row['sha256'],'bytes':row['bytes']})
    put('index.json',{'schemaVersion':1,'state':'SOURCE_ONLY_CONSUMERS355_NATIVE_ARTIFACT_FRAMEWORK_SEALED','files':files,'sourceInputs':len(refs),'nativeSources':355,'toolDependencies':767,'reviewedActualEnginePins':None,'runtimeAcceptanceClaim':False})
    print(json.dumps({'files':len(files),'preparationInputs':len(refs),'indexSha256':sha((HERE/'index.json').read_bytes()),'sourceReceiptSha256':sha((HERE/'source-receipt.json').read_bytes())}))
if __name__=='__main__':main()
