"""Read five completed follow-on gates. Never executes a tool, guest or host."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import shlex
from binary_reader import sections, uint, string, core_imports

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
SOURCE=BASE/'production-regression-activated-v3'
RUNTIME=BASE/'production-runtime-activated-v3'
ADOPTION=BASE/'production-adoption-v1'
ROOT=Path('/tmp/starling-node-compat/production-classic-regression-v3')
NAMES=['allocator-gc','focused-off','focused-runtime','focused-gc','getter']
RANDOM=['wasi:random/random@0.2.10']
verified={}
def sha(data):return hashlib.sha256(data).hexdigest()
def checked(path,digest=None,size=None):
    path=Path(path);assert path.is_file()and not path.is_symlink(),path
    data=path.read_bytes();assert digest is None or sha(data)==digest,path
    assert size is None or len(data)==size,path
    verified[str(path)]={'path':str(path),'sha256':sha(data),'bytes':len(data)}
    return data
def doc(path,digest=None):return json.loads(checked(path,digest))
def indexed(path,digest):
    value=doc(path/'index.json',digest)
    for row in value['files']:checked(path/row['path'],row['sha256'],row['bytes'])
    return value
def manifest(path,digest):
    value=doc(path,digest)
    for row in value['inputs']:checked((path.parent/row['path']).resolve(),row['sha256'],row['bytes'])
    return value
def component_structure(data,expected):
    imports,exports,cores=[],[],[]
    for kind,part in sections(data,bytes.fromhex('0061736d0d000100')):
        if kind in [10,11]:
            count,pos=uint(part,0)
            for _ in range(count):
                assert part[pos]==0;name,pos=string(part,pos+1);tag=part[pos];pos+=1
                _,pos=uint(part,pos)
                if kind==10:assert tag==5;imports.append(name)
                else:assert tag==1 and part[pos]==0;pos+=1;exports.append(name)
            assert pos==len(part)
        elif kind==1:cores.append({'sha256':sha(part),'bytes':len(part),'imports':core_imports(part)})
    assert sorted(imports)==expected and exports==['run']
    wasi=sorted({row['module']for core in cores for row in core['imports']if row['module'].startswith('wasi:')})
    assert wasi==expected
    assert not any(row['module']=='wasi_snapshot_preview1'for core in cores for row in core['imports'])
    return{'imports':imports,'exports':exports,'embeddedCores':cores}
def walk(value):
    if isinstance(value,dict):
        if 'componentPath'in value:yield value
        for item in value.values():yield from walk(item)
    elif isinstance(value,list):
        for item in value:yield from walk(item)
def provenance(value):
    assert value['selection']=='patched-import-i32-clock-v2'
    checked(value['manifestPath'],value['manifestSha256'])
    root=Path(value['modulePath']).parent.parent
    for row in value['checkedFiles']:checked(root/row['path'],row['sha256'])
    checked(value['lock']['path'],value['lock']['sha256'])
def fatal(value,output):
    assert value['jcoChild']=={'status':0,'stdout':'EXPECTED_FATAL_DISCARD\n','stderr':''}
    assert value['wasmtime']['status']!=0 and value['wasmtime']['stdout']==''
    assert 'wasm trap' in value['wasmtime']['stderr']
    assert value['policy']=='Failure is terminal; both instances discarded, never reused'
    checked(value['wasmtime']['path'],value['wasmtime']['sha256'])
    child=checked(output/(value['name']+'-child.mjs')).decode()
    assert child.count('await run()')==1 and 'EXPECTED_FATAL_DISCARD'in child and 'UNEXPECTED_RETURN'in child
def main():
    assert not(HERE/'results.json').exists()
    index=indexed(SOURCE,'577dbad5759ef06f075763c2a793ae278fddc15df8f4f61edc9a7d2de51ecb51');assert len(index['files'])==82
    root_seal=manifest(SOURCE/'input-freeze.json','a9c41e39e811620a27d71cce21f084a17c7c0f785ae69dd6b9d2c29085e23a97');assert len(root_seal['inputs'])==2055
    cap_seal=manifest(SOURCE/'capability/input-freeze.json','24ade3ad845315b96190b3977c7f7e256faf1e16ba274f46b86445d1a944475a');assert len(cap_seal['inputs'])==2054
    runtime_index=indexed(RUNTIME,'7e9520e0859b939a8586e6d0cfa1fe376a3ace75a2624dd777d5825bbf91cf66')
    runtime_row=next(row for row in runtime_index['files']if row['path']=='input-freeze.json')
    runtime_seal=manifest(RUNTIME/'input-freeze.json',runtime_row['sha256'])
    for tree in runtime_seal['toolTrees']:
        root=Path(tree['path']);assert str(root.resolve())==tree['realPath']and not root.is_symlink();rows=[]
        def visit(path):
            for item in sorted(path.iterdir()):
                kind='symlink'if item.is_symlink()else'directory'if item.is_dir()else'file'if item.is_file()else None
                assert kind;rows.append({'path':str(item.relative_to(root)),'kind':kind})
                if kind=='directory':visit(item)
        visit(root);assert sorted(rows,key=lambda row:row['path'])==tree['entries']
    for row in runtime_seal['toolLinks']:
        path=Path(row['path']);assert path.is_symlink()and os.readlink(path)==row['linkText']and str(path.resolve())==row['resolvedTarget']
        if row['targetKind']=='file':checked(row['resolvedTarget'],row['targetSha256'],row['targetBytes'])
        else:assert Path(row['resolvedTarget']).is_dir()
    pins=doc(ADOPTION/'reviewed-runtime-pins-v1.json','c998dce40ff66a1764ad8c44f8a492b830d40bb6dce958aab711ecf3c5bcbf3e')
    for pin in pins['variants'].values():
        freeze=doc(pin['freezeReceiptPath'],pin['freezeReceiptSha256']);assert len(freeze['copies'])==405
        for row in freeze['copies']:checked(row['path'],row['sha256'],row['bytes'])
    oracle=doc(SOURCE/'capability/focused/node-results.json','34d1c9df3ff58ddf9740b96210cf0e12b8a3090a038cb2745028f24a3adfcdb7')
    summaries=[];all_components={}
    for name in NAMES:
        output=ROOT/name;collector=doc(ADOPTION/(name+'-v3-root-results.json'));assert collector['rawTerminalExitCodeObservedByRoot']==0
        for row in collector['artifacts']:checked(row['path'],row['sha256'],row['bytes'])
        for row in collector.get('links',[]):assert Path(row['path']).is_symlink()and os.readlink(row['path'])==row['target']
        if collector.get('collector'):checked(collector['collector']['path'],collector['collector']['sha256'],collector['collector']['bytes'])
        report=doc(output/'results.json');admission=report.get('preflight',report.get('productionTickAdmission'));variant=admission['variant'];pin=pins['variants'][variant]
        assert report['state']==collector['resultState']and report['engineSha256']==pin['engineSha256']==admission['engineSha256']
        assert admission['sourceFilesVerified']==342
        complete=doc(output/'production-admission-complete.json');assert complete['consumedInputsRecheckedAfterRun']
        for key in ['variant','engineSha256','sourceFilesVerified','recipeSha256','freezeReceiptSha256','inputClosure']:assert complete[key]==admission[key]
        if name!='allocator-gc':
            assert report['engineReceipt']==doc(pin['enginePath']+'.build.json',pin['receiptSha256'])
            assert isinstance(report['sourceFiles'],list)and len(report['sourceFiles'])==11
            for row in report['sourceFiles']:checked(row['path'],row['sha256']);checked(row['saved'],row['sha256'])
            checked(report['host']['path'],report['host']['sha256']);assert report['host']['version'].startswith('wasmtime 42.0.1 ')
        provenance(report.get('packaging',report.get('componentizerProvenance')))
        expected=RANDOM if variant=='normal-runtime'else[]
        fixtures={row['componentPath']:row for row in walk(report)}
        if name=='allocator-gc':
            path=next(row['path']for row in collector['artifacts']if row['path'].endswith('.component.wasm'))
            fixtures[path]={'componentPath':path,'componentSha256':report['componentSha256'],'componentBytes':report['componentBytes'],
              'sourceSha256':report['sourceSha256'],'interfaceAudit':report['interfaceAudit'],'emittedWit':report['emittedWit']}
        actual_components={row['path']for row in collector['artifacts']if row['path'].endswith('.component.wasm')}
        assert set(fixtures)==actual_components
        for path,fixture in fixtures.items():
            data=checked(path,fixture['componentSha256'],fixture['componentBytes']);structure=component_structure(data,expected)
            audit=fixture['interfaceAudit'];assert audit['state']=='verified-final-component'and audit['componentSha256']==sha(data)
            assert audit['emittedImports']==audit['selectedInterfaces']==expected and audit['unusedSelectedInterfaces']==[]
            if 'emittedImports'in fixture:assert fixture['emittedImports']==expected
            assert 'export run: func() -> string;'in fixture['emittedWit']
            source_path=output/'source.mjs'if name=='allocator-gc'else Path(path.removesuffix('.component.wasm')+'.source.mjs')
            checked(source_path,fixture['sourceSha256'])
            all_components[path]={'path':path,'sha256':sha(data),'bytes':len(data),'gate':name,**structure}
        summary={'gate':name,'state':report['state'],'variant':variant,'components':len(fixtures),'imports':expected,'recordedRawExitCode':0}
        if name in ['focused-off','focused-runtime']:
            assert report['publicNodeGroups']=={'public':16,'nested':4,'receivers':9,'total':29}
            assert len(report['initializers'])==8 and len(report['fatal'])==5
            for section in ['main','aliases','benign']:
                data=report[section];assert len(data['calls'])==3 and [v['calls']for v in data['calls']]==[1,2,3]
                assert data['freshWasmtime']['observed']==data['calls'][0]and data['freshWasmtime']['stderr']==''
                checked(data['freshWasmtime']['path'],data['freshWasmtime']['sha256'])
            for i,value in enumerate(report['main']['calls'],1):
                for key in ['publicCases','nestedOnceCases','receiverCases']:assert value[key]==oracle[key]
                assert value['namespace']['canonicalCached']and value['namespace']['aliasValues']and value['namespace']['then']=='undefined'
                assert value['commonJS']['same']and value['commonJS']['rejectedCall']==value['commonJS']['rejectedConstruction']=='ERR_SM_NODE_UNSUPPORTED'
                assert value['snapshot']=={'before':0 if i==1 else 1,'after':1,'signalThis':True,'currentTarget':True,'aborted':False}
                errors=value['profileErrors'];assert len(errors['errors'])==7 and errors['hooks']==errors['ambient']==0
                for error in errors['errors']:assert error['own']and error['module']=='node:events'and error['profile']=='sm-node-22.14.0-m0.10'
            for value in report['aliases']['calls']:
                for key in ['canonicalCached','bareCached','aliasValues','sameDefaults']:assert value[key]
                assert value['sharedDefault']==19 and value['namedSnapshot']==10 and value['then']=='undefined'
            for value in report['benign']['calls']:assert value['caught']==['ERR_SM_NODE_UNSUPPORTED']*2 and value['thenReads']==0
            for row in report['initializers']:
                checked(output/(row['name']+'.init.mjs'),row['sourceSha256']);assert 'Failed to initialize component'in row['message']
            for row in report['fatal']:fatal(row,output)
            symbol=report['targetSymbolIdentity'];assert symbol['node']['sameAsNodeRegistry']and not symbol['target']['sameAsNodeRegistry']
            summary.update({'publicGroups':29,'retainedCallsPerPositiveComponent':3,'freshWasmtimePerPositiveComponent':1,'initializerFailures':8,'fatalDiscardCases':5,'symbolRegistryParity':False})
        elif name=='focused-gc':
            clean=report['clean'];assert len(clean['calls'])==3 and clean['freshWasmtime']['observed']==clean['calls'][0]
            for i,value in enumerate(clean['calls'],1):
                assert value['calls']==i and value['completed']==8 and value['receiver']and value['contextRestored']
                assert value['nestedOnceCases']==oracle['nestedOnceCases']and value['snapshot']=={'before':0 if i==1 else 1,'after':1}
            row=report['initializer'];checked(output/(row['name']+'.init.mjs'),row['sourceSha256']);assert 'Failed to initialize component'in row['message']
            fatal(report['fatal'],output);assert '-DNODE_COMPAT_GC_STRESS=1'in shlex.split(report['actualKernelCommand'])
            summary.update({'retainedCalls':3,'freshWasmtime':1,'hexRoundtripsPerCall':8,'initializerFailures':1,'fatalDiscardCases':1,'isolatedGCRootClaim':False,'gcScope':'Combined-owner gate only; application/VM co-owners remain.'})
        elif name=='allocator-gc':
            for i,value in enumerate(report['calls'],1):assert value=={'calls':i,'roundtrips':8,'brands':5,'ownedLength':127,'viewOffset':3,'snapshotByte':4+i}
            assert len(report['calls'])==3 and report['wasmtime']['observed']==report['calls'][0]and report['wasmtime']['stderr']==''
            assert '-DNODE_COMPAT_GC_STRESS=1'in shlex.split(report['compileCommand'])
            assert report['fixedGCAdmission']['pins']==pin
            checked(output/'allocator-gc-summary.json');assert doc(output/'allocator-gc-summary.json')==report
            summary.update({'retainedCalls':3,'freshWasmtime':1,'hexRoundtripsPerCall':8,'isolatedGCRootClaim':False})
        else:
            assert report['observationCompleted']and report['nodeCompatibilityPassed']is False
            assert report['node']['observed']=={'ordinary':1,'protectedSignal':1,'alreadyAborted':0}
            assert report['jco']['freshInstance']and report['jco']['observed']==report['wasmtime']['observed']=={'ordinary':0,'protectedSignal':0,'alreadyAborted':0}
            checked(report['node']['executable'],report['node']['executableSha256']);checked(report['wasmtime']['path'],report['wasmtime']['sha256'])
            for row in report['observationSources']:checked(row['saved'],row['sha256'])
            summary.update({'nodeGetterReads':[1,1,0],'jcoAndWasmtimeGetterReads':[0,0,0],'nodeCompatibilityPassed':False,'getterReturnsUndefined':True})
        summaries.append(summary)
    for row in list(verified.values()):checked(row['path'],row['sha256'],row['bytes'])
    result={'schemaVersion':1,'state':'INDEPENDENT_FIVE_CLASSIC342_FOLLOWON_EVIDENCE_VERIFIED_WITH_KNOWN_COUNTEREXAMPLES',
      'verifiedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceIndexSha256':'577dbad5759ef06f075763c2a793ae278fddc15df8f4f61edc9a7d2de51ecb51',
      'sourceIndexedFiles':82,'sourceRootRows':2055,'sourceCapabilityRows':2054,'runtimeIndexSha256':'7e9520e0859b939a8586e6d0cfa1fe376a3ace75a2624dd777d5825bbf91cf66',
      'runtimeConsumedRows':len(runtime_seal['inputs']),'toolTrees':len(runtime_seal['toolTrees']),'toolLinks':len(runtime_seal['toolLinks']),
      'gates':summaries,'actualDerivedComponentCount':len(all_components),'components':list(all_components.values()),'verifiedFiles':list(verified.values()),
      'allGateCompletionSealsMatchActualNativePreflight':True,'sourceBeforeAfterFacts':'Root wrappers recorded preflight/completion after recheck; current complete source/tool/native inventories independently rehashed here.',
      'reviewerExecutedGuestNodeOracleBuildHostOrReplay':False,'runtimeCompatibilityComplete':False,
      'collectorHistory':'Root first unsaved collector attempt read fixture sourceFiles list as native count; corrected sourceFilesVerified342 evidence and collector bytes are preserved. No engine/product failure inferred.',
      'limitations':['This verifies existing raw0 observations, reports, code and bytes; it does not repeat runtime execution.',
        'Fatal child status0 means the fresh test child caught an expected trap and discarded the instance; Wasmtime nonzero is generic trap evidence, not hidden JavaScript cause identity or failed-instance reuse.',
        'Initializer failures have no emitted successful component; component count is derived from actual fixture/artifact rows, excluding rejected snapshots.',
        'Getter counters are .then getter READS returning undefined, not callable-then invocation counts; Node parity remains false. Symbol registry mismatch remains.',
        'Moving-GC gates retain combined application/VM owners; no isolated-root, OOM/DEBUG, reset, ALS or performance proof.',
        'HTTP gates and full current replay acceptance remain separate.']}
    with(HERE/'results.json').open('x')as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps({'state':result['state'],'components':len(all_components),'verifiedPaths':len(verified),'resultsSha256':sha((HERE/'results.json').read_bytes())}))
if __name__=='__main__':main()
