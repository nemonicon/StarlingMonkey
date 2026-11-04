"""Freeze actual completed benchmark artifacts only; main is never a unit test."""
import sys
sys.dont_write_bytecode=True
import importlib.util,json,subprocess
from pathlib import Path
from benchmark_common import *

def main():
    assert len(sys.argv)==5,'ENGINE LABEL EXACT_SOURCE_INDEX_SHA256 EXPLICIT_SOURCE_ROOT'
    engine_arg,label,index_sha,source_root=sys.argv[1:];assert label in LABELS
    spec=importlib.util.spec_from_file_location('benchmark_freeze_verified_packet',HERE/'verify-packet.py');verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier);verifier.verify(index_sha)
    require_source_root(source_root)
    original_engine=Path(engine_arg).absolute();metadata_path=Path(str(original_engine)+'.build.json')
    raw,metadata_sha=capture_regular(metadata_path);metadata=json.loads(raw)
    classify(metadata,label) # Must precede any original engine stat/read.
    dependencies=tool_dependencies(REPO);capture_addons();layer().validate_sources(REPO,metadata['sourceManifest'])
    cache_path=checked(metadata['cmakeCachePath'],metadata['cmakeCacheSha256']);db_path=checked(metadata['compileCommandsPath'],metadata['compileCommandsSha256'])
    ev=metadata['classicBenchmarkDiagnosticPolicy']['evidence'];assert ev['version']=='benchmark-before-after-command-config-v1'and ev['exactBytesUnchanged']is True
    pre=json.loads(checked(ev['beforeCapturePath'],ev['beforeCaptureSha256']).read_bytes())
    assert pre['files']==ev['before']and pre['collectionCommands']==ev['collectionCommands']
    evidence={}
    assert len(ev['before'])==len(ev['after'])==8
    for before,after in zip(ev['before'],ev['after']):
        assert before['name']==after['name']and before['sha256']==after['sha256']and before['bytes']==after['bytes']
        assert capture_regular(checked(before['path'],before['sha256']))[0]==capture_regular(checked(after['path'],after['sha256']))[0]
        evidence[after['name']]=Path(after['path']).read_bytes()
    assert ev['collectionCommands']=={'parent-targets.commands.txt':['ninja','-C',str(cache_path.parent),'-t','commands','builtin_componentize_embedding',CONTRACT['target']],
      'final-link.commands.txt':['ninja','-C',str(cache_path.parent),'-t','commands','starling-raw.wasm/starling-raw.wasm']}
    observations=validate_observations(metadata,label,cache_values(cache_path.read_bytes()),json.loads(db_path.read_bytes()),evidence['parent-targets.commands.txt'],evidence['builtins.incl'],evidence['final-link.commands.txt'])
    assert metadata['classicBenchmarkDiagnosticPolicy']['actualDiagnosticCompileCommands']==observations['diagnostic']
    assert metadata['classicBenchmarkDiagnosticPolicy']['actualEmbeddingCompileCommands']==observations['embedding']
    node='/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node'
    admission=subprocess.run([node,str(HERE/'metadata-admission.mjs'),str(metadata_path),label,str(REPO)],capture_output=True,check=True)
    assert json.loads(admission.stdout)['productionSelectorRefused']is True
    engine=checked(original_engine,metadata['engineSha256']);assert engine.stat().st_size==metadata['engineBytes']
    with engine.open('rb')as stream:assert stream.read(8)==b'\0asm\x01\0\0\0'
    rust=metadata['generatedRustProject'];openssl=metadata['openssl'];audit=openssl['completeSourceAudit']
    assert rust['cargoBuildLocked']is True and rust['manifestAndLockCheckedBeforeAndAfterBuild']is True
    assert audit['sourceFilesVerified']==4650 and audit['beforeAndAfterBuild']is True
    assert audit['sourceDirectory']==openssl['sourceDir']and audit['receiptSha256']==openssl['receiptSha256']
    before_audit=json.loads(checked(audit['beforeReportPath'],audit['beforeReportSha256']).read_bytes());assert before_audit['state']=='verified-complete-source'
    for key,value in before_audit.items():assert audit[key]==value
    assert rust['lockSha256']==sha(REPO/'runtime/crates/staticlib-template/Cargo.lock')
    assert checked(openssl['library']['path'],openssl['library']['sha256']).stat().st_size==openssl['library']['bytes']
    plan=[];planned={}
    def add(path,name,expected,shared=False):
        path=checked(path,expected);target=OUTPUT/name
        if target in planned:assert shared and planned[target]['shared']and planned[target]['sha256']==expected;return
        row={'original':path,'target':target,'sha256':expected,'shared':shared};planned[target]=row;plan.append(row)
    def generated(data,name):plan.append({'original':None,'data':data,'target':OUTPUT/name,'sha256':digest(data),'shared':False})
    add(engine,label+'.engine.wasm',metadata['engineSha256']);add(metadata_path,label+'.engine.wasm.build.json',metadata_sha)
    add(cache_path,label+'-CMakeCache.txt',metadata['cmakeCacheSha256']);add(db_path,label+'-compile_commands.json',metadata['compileCommandsSha256'])
    for name in ('parent-targets.commands.txt','final-link.commands.txt','builtins.incl'):generated(evidence[name],label+'-'+name)
    generated(admission.stdout,label+'-production-refusal.json')
    tool_witnesses=json.loads(evidence['tool-witnesses.json'])
    for index,row in enumerate(tool_witnesses):
        path=Path(row['path']);assert path.is_symlink()is row['symlink']
        if row['symlink']:assert __import__('os').readlink(path)==row['linkText']
        assert str(path.resolve(strict=True))==row['resolvedPath'];checked(Path(row['resolvedPath']),row['sha256'])
        if row['frozenCopyRequired']:add(row['resolvedPath'],label+'-tools/'+str(index)+'-'+Path(row['resolvedPath']).name,row['sha256'])
    for side in ('before','after'):
        for row in ev[side]:add(row['path'],label+'-witness/'+side+'/'+row['name'],row['sha256'])
    add(ev['beforeCapturePath'],label+'-witness/before-capture.json',ev['beforeCaptureSha256'])
    for row in manifest(metadata['sourceManifest'],342):add(REPO/row['path'],'source/'+row['path'],row['sha256'],True)
    for row in capture_addons():add(REPO/row['path'],'addon/'+row['path'],row['sha256'],True)
    home=Path(cache_values(cache_path.read_bytes())['CMAKE_HOME_DIRECTORY'])
    for row in validate_external_sources(metadata['componentizeSourceManifest'],home):add(home/row['path'],'componentize-source/'+row['path'],row['sha256'],True)
    add(adapter(),'tooling/wasi_snapshot_preview1.wasm',ADAPTER,True)
    dependency_rows=[('Cargo.toml',rust['manifestPath'],rust['manifestSha256']),('Cargo.lock',rust['lockPath'],rust['lockSha256']),
      ('openssl-before.json',audit['beforeReportPath'],audit['beforeReportSha256']),('openssl-receipt.txt',openssl['receiptPath'],openssl['receiptSha256']),
      ('openssl-configure.txt',openssl['configureRecipe']['path'],openssl['configureRecipe']['sha256']),('openssl-configdata.pm',openssl['configdata']['path'],openssl['configdata']['sha256']),
      ('libcrypto.a',openssl['library']['path'],openssl['library']['sha256'])]
    for name,path,expected in dependency_rows:add(path,label+'-'+name,expected)
    for row in dependencies:add(REPO/row['path'],'tooling/repository/'+row['path'],row['sha256'],True)
    for path in sorted((REPO/'builtins/node-compat').rglob('*')):
        if path.is_file()and path.name.startswith(('LICENSE','NOTICE')):add(path,'source/'+str(path.relative_to(REPO)),sha(path),True)
    license_path=Path(openssl['sourceDir'])/'LICENSE.txt';add(license_path,'licenses/openssl-LICENSE.txt',sha(license_path),True)
    index=checked(HERE/'index.json',index_sha);add(index,'producer/index.json',index_sha,True)
    for row in json.loads(index.read_bytes())['files']:add(HERE/row['path'],'producer/'+row['path'],row['sha256'],True)
    receipt_path=OUTPUT/(label+'-freeze-receipt.json')
    checked(metadata_path,metadata_sha);verifier.verify(index_sha);validate_plan(plan,receipt_path,OUTPUT)
    execute_plan(plan,OUTPUT)
    receipt={'schemaVersion':1,'state':'immutable-classic-trace-benchmark-diagnostic-engine-frozen','label':label,'recipeSha256':RECIPE,
      'engineSha256':metadata['engineSha256'],'engineBytes':metadata['engineBytes'],'metadataSha256':metadata_sha,
      'nativeInputsVerified':342,'addonInputsVerified':2,'totalDeclaredNativeAndBuildInputs':344,'externalEmbeddingInputsVerified':3,
      'actualNativeCommands':61,'actualStrictCommands':4,'actualPrivateCommands':5,'actualEmbeddingCommands':1,'actualDiagnosticCommands':1,
      'sourceIndexSha256':index_sha,'productionSelectorRefused':True,'diagnosticOnly':True,
      'sourceContractVersion':CONTRACT['sourceContractVersion'],'classicTraceSourcePolicy':CONTRACT['classicTraceSourcePolicy'],
      'semanticSourceProvenance':{
        'fixSourceIndexSha256':CONTRACT['classicTraceSourcePolicy']['fixSourceIndexSha256'],
        'correctedReceiptAnnotationBase':str(OUTPUT/'tooling/repository/tests/node-compat/foundation-classic-streams/trace-semantics-candidate-v1'),
        'primaryPinsPath':str(OUTPUT/'tooling/repository/tests/node-compat/foundation-classic-streams/trace-semantics-candidate-v1/primary-source-pins.json'),
        'primaryPinsSha256':next(row['sha256']for row in dependencies if row['path']=='tests/node-compat/foundation-classic-streams/trace-semantics-candidate-v1/primary-source-pins.json'),
        'nodeMitNoticePath':str(OUTPUT/'tooling/repository/tests/node-compat/foundation-classic-streams/trace-semantics-candidate-v1/LICENSE.node'),
        'nodeMitNoticeSha256':next(row['sha256']for row in dependencies if row['path']=='tests/node-compat/foundation-classic-streams/trace-semantics-candidate-v1/LICENSE.node')},
      'classicStreamsEnabled':metadata['classicStreamsEnabled'],'sourceRoot':str(OUTPUT/'source'),'addonRoot':str(OUTPUT/'addon'),
      'copies':[{'path':str(row['target']),'original':str(row['original'])if row['original']else None,'sha256':row['sha256'],'bytes':row['target'].stat().st_size,'shared':row['shared']}for row in plan],
      'toolWitnesses':tool_witnesses,'toolBinaryReferencesAreNotCopied':True,
      'toolingAdapter':{'path':str(OUTPUT/'tooling/wasi_snapshot_preview1.wasm'),'sha256':ADAPTER,'bytes':53512,'nativeInputCountUnchanged':True},
      'toolDependencyClosure':[{'path':str(OUTPUT/'tooling/repository'/row['path']),'sourcePath':row['path'],'sha256':row['sha256'],'bytes':row['bytes']}for row in dependencies],
      'licenses':[{'path':str(row['target']),'sha256':row['sha256']}for row in plan if row['target'].name.startswith(('LICENSE','NOTICE'))or row['target'].name=='openssl-LICENSE.txt'],
      'allInputsValidatedBeforeCopies':True,'allCopiesAndOriginalsRehashed':True,'reviewedPinsCreated':False,'guestExecuted':False,'runtimeAcceptanceClaim':False}
    with receipt_path.open('x')as stream:json.dump(receipt,stream,indent=2);stream.write('\n')
    print(json.dumps({'receiptPath':str(receipt_path),'sha256':sha(receipt_path),'runtimeAcceptanceClaim':False}))
if __name__=='__main__':main()
