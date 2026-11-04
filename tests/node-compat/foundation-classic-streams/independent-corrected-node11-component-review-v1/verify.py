"""Read completed public component evidence only; never instantiate Wasm/JS."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
REPO=HERE.parents[3]
RUNTIME=BASE/'production-trace-runtime-activated-v1'
OUTPUT=Path('/tmp/starling-node-compat/production-classic-corrected-trace-v1')
ADOPTION=BASE/'production-adoption-v1'
checked={}
def sha(data):return hashlib.sha256(data).hexdigest()
def read(path,digest=None,size=None):
    path=Path(path);before=path.lstat();assert path.is_file()and not path.is_symlink(),path
    data=path.read_bytes();after=path.lstat()
    assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)
    assert digest is None or sha(data)==digest,path
    assert size is None or len(data)==size,path
    checked[str(path)]={'path':str(path),'sha256':sha(data),'bytes':len(data)}
    return data
def document(path,digest=None):return json.loads(read(path,digest))
def indexed(root,digest):
    rows=document(root/'index.json',digest)['files'];assert len(rows)==len({r['path']for r in rows})
    for row in rows:assert not Path(row['path']).is_absolute()and'..'not in Path(row['path']).parts;read(root/row['path'],row['sha256'],row['bytes'])
    return len(rows)
def put(name,value):
    with(HERE/name).open('xb')as stream:stream.write(value if isinstance(value,bytes)else(json.dumps(value,indent=2)+'\n').encode())
def main():
    root=document(ADOPTION/'corrected-node11-component-root-results.json','34dc3d0706df8b0480a177f3b29ec68a1e45d9a58a6ea44eacbd447a7e0440b4')
    assert root['rawTerminalExitCode']==0 and root['toolSession']==11859
    assert len(root['files'])==11 and root['nodeCompatibilityPassed']is True and root['differences']==[]
    for row in root['files']:read(row['path'],row['sha256'],row['bytes'])
    link=root['toolLink'];path=Path(link['path']);assert path.is_symlink()and os.readlink(path)==link['target']and path.resolve()==Path(link['target']).resolve()
    assert indexed(RUNTIME,'e1f87cd6a2fd09ff34055187bfb938c2b094c3fd333ef9f57b6a1eea4c175b78')==26
    assert indexed(BASE/'trace-runtime-activation-candidate-v1','693057a3f90e911e331d8e79f7242816e8f09b354fb78ba4c79f7c18f69649ab')==34
    indexed(BASE/'independent-trace-runtime-family-review-v1','d2ef84a640fb73dd343bbee3d0f44ca0e62b71005a06693faf74c88b79a139d1')
    seal=document(RUNTIME/'input-freeze.json');assert len(seal['inputs'])==6414 and len(seal['toolTrees'])==2 and len(seal['toolLinks'])==22
    for row in seal['inputs']:
        path=Path(os.path.abspath(RUNTIME/row['path']));read(path,row['sha256'],row['bytes'])
    for tree in seal['toolTrees']:
        boundary=Path(tree['path']);assert not boundary.is_symlink()and str(boundary.resolve())==tree['realPath'];members=[]
        def visit(folder):
            for child in sorted(folder.iterdir()):
                kind='symlink'if child.is_symlink()else'directory'if child.is_dir()else'file'if child.is_file()else None
                assert kind;members.append({'path':str(child.relative_to(boundary)),'kind':kind})
                if kind=='directory':visit(child)
        visit(boundary);assert sorted(members,key=lambda r:r['path'])==tree['entries']
    for row in seal['toolLinks']:
        path=Path(row['path']);assert path.is_symlink()and os.readlink(path)==row['linkText']and str(path.resolve())==row['resolvedTarget']
        if row['targetKind']=='file':read(row['resolvedTarget'],row['targetSha256'],row['targetBytes'])
    pins=document(ADOPTION/'reviewed-trace-runtime-pins-v1.json','182e8b724d94ebf73450c0ffcea81fb19b902028e2839bd2a9d1452ab7fab5eb')
    authority=document(ADOPTION/'trace-root-pin-review-receipt.json','ce88ac3495afdf97718a34f7bf2c2360613f95a91f5c193e556c87269b4a8be0')
    assert authority['runtimeAcceptanceClaim']is False
    freeze_counts={}
    for name,pin in pins['variants'].items():
        freeze=document(pin['freezeReceiptPath'],pin['freezeReceiptSha256']);assert len(freeze['copies'])==474
        assert freeze['nativeInputsVerified']==342 and freeze['externalEmbeddingInputsVerified']==3
        for row in freeze['copies']:read(row['path'],row['sha256'],row['bytes'])
        freeze_counts[name]=len(freeze['copies'])
    pin=pins['variants']['normal-off'];assert pin['engineSha256']==root['engineSha256']=='d54446dcd4071fe2c2b1db4984ead78d2fe61ceb0a0396822df8416a26921a92'
    metadata=document(pin['enginePath']+'.build.json',pin['receiptSha256'])
    assert metadata['gcStress']is False and metadata['entropyPolicy']=='off'and metadata['classicStreamsEnabled']is True
    assert metadata['oomTesting']is False and metadata['debuggerEnabled']is False
    assert len(metadata['sourceManifest'])==342 and len(metadata['componentizeSourceManifest'])==3
    stage=Path('/tmp/starling-node-compat/classic-trace-source-v1')
    for row in metadata['sourceManifest']:read(stage/row['path'],row['sha256']);read(Path(pin['sourceRoot'])/row['path'],row['sha256'])
    assert metadata['classicTraceSourcePolicy']['fixSourceIndexSha256']=='59c9233c5dd1c9f07c4da16a79abdb58abc9775b37c714f6af179e85f23f0631'
    assert read(stage/'builtins/node-compat/classic-streams/classic-core.generated.mjs', '5c0241a73f4cdffc61d7c962bd4d1a1d2015f8fbadef59a4631b7551f9a767b9')
    completion=document(OUTPUT/'completion.json','55c368aa4fac072e8de30c8fb17f22dbaf6efe2c7bbd143e702a2df7956b7135')
    assert completion['state']=='CLASSIC_GATE_OUTPUTS_COMPLETE_REQUIRES_EXTERNAL_EXIT_ZERO'
    assert completion['requiresIndependentTerminalExitCodeZero']is True and completion['terminalExitCodeObservedByThisHelper']is None
    assert completion['finalAdmissionRecheckCompletedBeforeReportPublication']is True
    assert len(completion['files'])==8 and completion['componentFiles']==['stream-trace.component.wasm']and completion['generatedWasmFiles']==['stream_trace.core.wasm']
    for row in completion['files']:assert not Path(row['path']).is_absolute()and'..'not in Path(row['path']).parts;read(OUTPUT/row['path'],row['sha256'],row['bytes'])
    report=document(OUTPUT/'results.json',completion['results']['sha256'])
    assert report['status']=='CORRECTED_REAL_COMPONENT_PUBLIC_STREAM_TRACE_NODE11_PASSED'and report['caseCount']==11
    assert report['engineSha256']==pin['engineSha256']and report['engineReceiptSha256']==pin['receiptSha256']and report['nativeSources']==342
    assert report['nodeCompatibilityPassed']is True and report['differences']==[] and report['hostModelEqualsActualGuest']is False
    assert report['interfaceAudit']['emittedImports']==report['interfaceAudit']['selectedInterfaces']==[]
    wit=read(OUTPUT/'emitted.wit').decode();assert wit==report['emittedWit']=='package root:component;\n\nworld root {\n  export run: func() -> string;\n}\n'
    reader_path=BASE/'independent-http-prehost-verification-v1/binary_reader.py'
    read(reader_path,'cb32f8a20904cf866b8cc9b6585f87b3461a597dca896270238c6d5b4c008fa8')
    spec=importlib.util.spec_from_file_location('public_component_sections_readonly',reader_path);reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
    component=read(report['componentPath'],root['componentSha256'],12948817)
    sections=list(reader.sections(component,bytes.fromhex('0061736d0d000100')))
    assert not[body for kind,body in sections if kind==10]
    assert [body.hex()for kind,body in sections if kind==7]==['0140000073']and[body.hex()for kind,body in sections if kind==11]==['01000372756e010000']
    cores=[body for kind,body in sections if kind==1];assert len(cores)==1 and cores[0]==read(OUTPUT/'stream_trace.core.wasm')
    imports=reader.core_imports(cores[0]);assert not any(r['module'].startswith('wasi:')or r['module']=='wasi_snapshot_preview1'for r in imports)
    glue=read(OUTPUT/'stream_trace.js').decode();assert 'stream_trace.core.wasm'in glue
    assert report['bundleImports']==['node:stream','node:buffer']and report['sourceModules']==[str(RUNTIME/'trace/cases.mjs'),str(RUNTIME/'trace/guest.mjs')]
    read(OUTPUT/'guest.bundle.mjs',report['bundleSha256'])
    oracle=document(RUNTIME/'trace/node-results.json',report['nodeOracleSha256']);assert oracle['groups']==11 and oracle['node']=='v22.14.0'and report['nodeObserved']==oracle['nodeObserved']
    retained=report['retained'];assert len(retained)==3 and[r['calls']for r in retained]==[1,2,3]
    assert report['freshJco']==retained[0]==report['wasmtime']['observed']
    assert report['wasmtime']['status']==0 and report['wasmtime']['stderr']==''
    assert report['wasmtime']['stdout'].isascii()and json.loads(json.loads(report['wasmtime']['stdout']))==retained[0]
    read(report['wasmtime']['path'],'a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c')
    for observed in retained+[report['freshJco'],report['wasmtime']['observed']]:
        assert observed['snapshot']=={'bytes':64,'checksum':151852933}and observed['observed']==oracle['nodeObserved']
        for row in observed['observed'][:8]:assert row['bytes']==64 and row['checksum']==151852933 and row['writeCalls']==row['callbackCalls']==1
        assert [r['encoding']for r in observed['observed'][8:]]==[{'type':'undefined'},{'type':'object','value':None},{'type':'string','value':'utf8'}]
        for row,callbacks in zip(observed['observed'][8:],[0,1,1]):assert row['samePayload']is True and row['valueId']==1 and row['payloadKeys']==['id']and row['hookCallbackCalls']==1 and row['userWriteCallbackCalls']==callbacks
    previous=document(ADOPTION/'stream-trace-component-v2-root-results.json','c81017aabca2b97e7367ed068b82a2160b470aa9aa1da1bc94f7acad96edbb37');assert previous['nodeCompatibilityPassed']is False
    # Preserve full report text, never engine/component bytes, in this review.
    put('component-results.json',read(OUTPUT/'results.json'));put('completion.json',read(OUTPUT/'completion.json'));put('root-results.json',read(ADOPTION/'corrected-node11-component-root-results.json'))
    result={'schemaVersion':1,'state':'INDEPENDENT_ACTUAL_CORRECTED_NODE11_COMPONENT_EVIDENCE_VERIFIED_NO_RERUN',
      'rawTerminalExitCodeObservedByRoot':0,'rootSession':11859,'componentSha256':root['componentSha256'],'componentBytes':len(component),'engineSha256':pin['engineSha256'],
      'runtimeFamilyIndexSha256':root['runtimeFamilyIndexSha256'],'runtimeConsumedInputsVerified':6414,'toolTreesVerified':2,'toolLinksVerified':22,'fourFreezeCopyCounts':freeze_counts,
      'nativeSourcesVerified':342,'externalEmbeddingSourcesVerified':3,'outerComponentImports':[],'coreImports':imports,'soleExport':'run: func() -> string',
      'nodeCases':11,'retainedJcoCalls':3,'freshJcoExact':True,'freshWasmtimeExact':True,'rawWasmtimeStringIndependentlyDecoded':True,'nodeCompatibilityPassed':True,'differences':[],
      'historicalOldModelStillDifferent':True,'historicalActualSixGapRootReceiptUnchanged':True,'completionFilesVerified':8,'rootFilesVerified':11,'resultAndBinaryCoreGlueHashesVerified':True,
      'sourceNativeAuthorityToolAdapterAndOutputSealsRehashed':True,'reviewerOnlyReadPublicBytesAndPureBinaryParser':True,
      'guestBuildPackagerNativeHostOrTimingRerun':False,'runtimeAcceptanceClaim':False,'performanceClaim':False,
      'limitations':['Exact eleven public cases only; full corrected classic/GC/regression/followon/HTTP and20/14 workload/boundary gates remain separate.','Ordinary OFF engine only: no GC-stress claim from this component.','Retained calls do not establish Engine.reset, request isolation, failed-instance reuse or ALS.','No throughput/RSS/size advantage or full Node Streams conformance claim.']}
    put('checked-inputs.json',{'schemaVersion':1,'files':sorted(checked.values(),key=lambda r:r['path'])});put('results.json',result)
    print(json.dumps({'state':result['state'],'checkedPaths':len(checked),'nodeCases':11,'componentImports':[]}))
if __name__=='__main__':main()
