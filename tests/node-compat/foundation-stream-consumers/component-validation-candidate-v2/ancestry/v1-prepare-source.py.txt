"""Prepare public consumer fixtures and immutable packaging files only. No guest/actions."""
from pathlib import Path
import hashlib,json,re
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
FAMILY=HERE.parent
NATIVE=Path('/tmp/starling-node-compat/consumers-source-v2')
ZLIB=REPO/'tests/node-compat/foundation-zlib/component-validation-activated-v8'
def sha(value):return hashlib.sha256(value).hexdigest()
def put(name,value):
    path=HERE/name;path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x')as out:out.write(value if isinstance(value,str)else json.dumps(value,indent=2)+'\n')
def main():
    assert not(HERE/'packaging-tools').exists()
    for name in ['durable-host.mjs','consumed.mjs']:put(name,(ZLIB/name).read_text())
    node=json.loads((FAMILY/'node-results.json').read_bytes());text=(FAMILY/'node-checks.mjs').read_text()
    assert sha(text.encode())==node['sources']['node-checks.mjs']
    boundary='export async function blobChecks(consumers) {';assert text.count(boundary)==1;text=text[:text.index(boundary)]
    for old in["const BlobCtor = Blob;\n","const BufferCtor = globalThis.Buffer;\n",",new BlobCtor(['a'])"]:assert text.count(old)==1;text=text.replace(old,'')
    old='export async function textChecks(consumers) {';assert text.count(old)==1;text=text.replace(old,'export async function textChecks(consumers, selected = null) {')
    old='  async function check(name, run) { cases.push({name,result:await run()}); }';assert text.count(old)==1
    text=text.replace(old,'  let index=0; async function check(name, run) { const current=index++; if(selected===null||selected===current)cases.push({name,result:await run()}); }')
    assert not re.search(r'\bBlob\b|BlobCtor|BufferCtor|blobChecks',text)
    put('differential.mjs',text)
    cases=json.loads(json.dumps(node['text']));invalid=next(c for c in cases if c['name']=='invalid byte chunks reject with error type and code');assert len(invalid['result'])==6;invalid['result']=invalid['result'][:5]
    assert len(cases)==18
    put('node-oracle.json',{'schemaVersion':1,'node':'v22.14.0','sourceReportSha256':sha((FAMILY/'node-results.json').read_bytes()),'oldRuntimeProofTransferred':False,'cases':cases,'selection':{'groups':18,'invalidKindVectors':5,'excludedBlobVectors':1,'reason':'Do not construct native Blob; preserve all remaining Node input/oracle cases.'}})
    profiles=(FAMILY/'metadata-v2/component-checks.mjs').read_text()
    old="import { createConsumersModule, CONTRACT_VERSION, MAX_BYTE_INPUT, MAX_CHUNKS, MAX_OUTPUT_CODE_UNITS, MAX_STRING_INPUT_CODE_UNITS } from './create-module.mjs';"
    new="import { CONTRACT_VERSION, MAX_BYTE_INPUT, MAX_CHUNKS, MAX_OUTPUT_CODE_UNITS, MAX_STRING_INPUT_CODE_UNITS } from './profile-contract.mjs';"
    assert profiles.count(old)==1;profiles=profiles.replace(old,new)
    profiles=profiles.replace('export async function profileChecks(prototype){','export async function profileChecks(prototype, selected = null){')
    old='  const cases=[];async function group(name,run){cases.push({name,result:await run()});}'
    new='  const cases=[];let index=0;async function group(name,run){const current=index++;if(selected===null||selected===current)cases.push({name,result:await run()});}'
    assert profiles.count(old)==1;profiles=profiles.replace(old,new)
    old="    // Bundling can lower the isolated ESM namespace. Record its actual shape;\n    // this is not proof of a future registered native Module Namespace Object."
    assert profiles.count(old)==1;profiles=profiles.replace(old,"    // This fixture imports the actual registered native namespace; no facade is bundled.\n    check(Apply(Tag,prototype,[])==='[object Module]'&&GetProto(prototype)===null&&!Object.isExtensible(prototype),'registered namespace shape');")
    start="  await group('factory does not install globals or expose dependencies',()=>{"
    at=profiles.index(start);end=profiles.index('\n  return cases;',at)
    profiles=profiles[:at]+"  await group('registered public record exposes no factory or native dependencies',()=>{\n    equal(OwnKeys(prototype).sort(),['arrayBuffer','blob','buffer','default','json','text'],'finite registered public exports');\n    check(prototype.createConsumersModule===undefined&&prototype.TextDecoder===undefined&&prototype.kernel===undefined,'private factory/dependency absent');\n    return{finiteRegisteredBindings:true,privateFactoryType:'undefined',privateDecoderType:'undefined'};\n  });"+profiles[end:]
    assert 'createConsumersModule('not in profiles
    put('profiles.mjs',profiles)
    put('profile-contract.mjs',"export const CONTRACT_VERSION='sm-node-22.14.0-m0.14';\nexport const MAX_BYTE_INPUT=1048576,MAX_STRING_INPUT_CODE_UNITS=1048576,MAX_OUTPUT_CODE_UNITS=1048576,MAX_CHUNKS=4096;\n")
    put('consumer.cjs',"module.exports=require('stream/consumers');\n")
    native_js=['tests/node-compat/module-selection.mjs','tests/node-compat/classic-streams-admission.mjs','tests/node-compat/private-ticks-admission.mjs','tests/node-compat/zlib-admission.mjs','tests/node-compat/stream-consumers-admission.mjs','tests/node-compat/foundation-zlib/native-integration-candidate-v4/compile-input.mjs','builtins/node-compat/validate-manifest.mjs']
    root_js=['tests/node-compat/toolchain.mjs','tests/node-compat/componentizer.mjs','tests/node-compat/profile-bundler.mjs','tests/node-compat/foundations/native-scalar-harness.mjs','tests/node-compat/capability-policy.mjs']
    native_data=['builtins/node-compat/manifest.schema.json','builtins/node-compat/export-manifest.node-v22.14.0.json','tests/node-compat/legacy-stream-web-receipts.json']
    root_data=['tests/node-compat/wasi-0.2.10-interfaces.json','tests/node-compat/oom/componentize-clock-errno-v2.patch','tests/node-compat/abi-fix/componentize-import-i32-v1.patch','tests/node-compat/abi-fix/splicer-Cargo.v1.lock','host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm']
    origins=[]
    for root,paths,role in[(NATIVE,native_js,'STAGED355_STRUCTURAL_SELECTOR_NOT_OPERATIONAL_ADMISSION'),(REPO,root_js,'ROOT_GENERIC_LOADER_SNAPSHOT'),(NATIVE,native_data,'STAGED355_IMPORT_TIME_DATA'),(REPO,root_data,'ROOT_SELECTED_PATCH_CATALOGUE_ADAPTER_SNAPSHOT')]:
        for relative in paths:
            value=(root/relative).read_bytes();assert not(root/relative).is_symlink()
            target=HERE/'packaging-tools'/relative;target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb')as out:out.write(value)
            origins.append({'path':'packaging-tools/'+relative,'original':str(root/relative),'sha256':sha(value),'bytes':len(value),'role':role})
    assert len(native_js+root_js)==12 and len(native_data+root_data)==8
    put('packaging-origins.json',{'schemaVersion':1,'state':'FINITE_IMMUTABLE_PACKAGING_TOOLS_SNAPSHOT_NOT_NATIVE_AUTHORITY','localModules':12,'selectedDataAndAdapter':8,'files':origins,'componentToolRootRelative':'packaging-tools','liveAdapter':{'path':str(REPO/root_data[-1]),'sha256':sha((REPO/root_data[-1]).read_bytes()),'bytes':53512,'mustReopenBeforeAndAfterPackaging':True},'nativeTool767DoesNotCloseThisGraph':True})
    profiles_old=json.loads((FAMILY/'prototype-node-results.json').read_bytes())
    put('profile-oracle-ancestry.json',{'schemaVersion':1,'oldNodeOnlyProfileReportSha256':sha((FAMILY/'prototype-node-results.json').read_bytes()),'oldProfileGroups':profiles_old['profileGroups'],'oldRuntimeProofTransferred':False,'changedGroups':{'1':'Require actual registered Module Namespace, not lowered bundled factory shape','11':'Replace private factory construction with public installed finite-record/private-dependency absence'},'currentProfile':'sm-node-22.14.0-m0.14','oldProfiles':profiles_old['profiles']})
    put('fixture-derivations.json',{'schemaVersion':1,'differentialBeforeSha256':sha((FAMILY/'node-checks.mjs').read_bytes()),'differentialAfterSha256':sha(text.encode()),'differentialChanges':['Remove Blob-only function/captures/vector','Select a single original group per typed WIT run(index:u32) without changing that group body'],'profilesBeforeSha256':sha((FAMILY/'metadata-v2/component-checks.mjs').read_bytes()),'profilesAfterSha256':sha(profiles.encode()),'profilesChanges':['Replace private factory import with public contract constants','Add selection-only group dispatch','Require native registered namespace','Replace last private factory group with installed public namespace/dependency absence'],'initialPrototypeEngineSources':293,'runtimeProofTransferred':False})
    print(json.dumps({'sourceOnly':True,'differentialGroups':18,'profileGroups':12,'physicalPackagingModules':12,'physicalSelectedDataAndAdapter':8,'guestOrFactoryExecuted':False}))
if __name__=='__main__':main()
