"""Read five completed follow-on gates. Never executes a tool, guest or host."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import datetime
import hashlib
import json
import os
import shlex
import subprocess
from evidence_helpers import review_core_glue,raw_host_inventory
from binary_reader import sections, uint, string, core_imports

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
SOURCE=Path('/private/tmp/starling-node-compat/classic-trace-source-v1/tests/node-compat/foundation-classic-streams/production-trace-regression-activated-v1')
RUNTIME=BASE/'production-trace-runtime-activated-v1'
ADOPTION=BASE/'production-adoption-v1'
ROOT=Path('/tmp/starling-node-compat/production-classic-corrected-regression-v1')
NAMES=['allocator-gc','focused-off','focused-runtime','focused-gc','getter']
RANDOM=['wasi:random/random@0.2.10']
COLLECTORS={'allocator-gc': {'sha256': 'f4bf9970190c2dd1276d7186d2967d7cb0d98d11f89b57dcbb88581a45cb2314', 'session': 47113, 'artifacts': 11}, 'focused-off': {'sha256': 'f5238fba8c54275ffcb752c7549cbe215e8fd5691046a91a618fccfdf9743463', 'session': 87316, 'artifacts': 80}, 'focused-runtime': {'sha256': 'ed932f9884236faa025e8d28166ad8e73c235fc4e0064b20abf1793abdff48e3', 'session': 37883, 'artifacts': 81}, 'focused-gc': {'sha256': '070f9dc4d7911e01e3fb88919bffd149aa97ae231aadc97ebe41de04481be460', 'session': 23316, 'artifacts': 32}, 'getter': {'sha256': '16b919e21368fe90b1190307603884a336dee89aad6e55bd99513d8949750c88', 'session': 58626, 'artifacts': 27}}
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
        if 'componentPath'in value and 'interfaceAudit'in value:yield value
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
    assert not(HERE/'results.json').exists(), 'Preserve an existing review result; use a new sibling for another review'
    index=indexed(SOURCE,'a08aec2d8a28f6bb91251841b617be20820c23ab085e526d0dc107439b061c6e');assert len(index['files'])==83
    root_seal=manifest(SOURCE/'input-freeze.json','ab2a5a5822e8925cf50f363ecb024a29e31017d4fca581203ebbd3741759845f');assert len(root_seal['inputs'])==2293
    cap_seal=manifest(SOURCE/'capability/input-freeze.json','de0194d95d93b2b527f323a8e6d506d9c2e0fd9e899f1e0ae009f89633812b06');assert len(cap_seal['inputs'])==2292
    indexed(BASE/'independent-trace-replay-family-review-v1','85296020f2f792c01107e10d9602de5f586881c3cde3628e1c1b30226f6dbf1d')
    runtime_index=indexed(RUNTIME,'e1f87cd6a2fd09ff34055187bfb938c2b094c3fd333ef9f57b6a1eea4c175b78')
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
    pins=doc(ADOPTION/'reviewed-trace-runtime-pins-v1.json','182e8b724d94ebf73450c0ffcea81fb19b902028e2839bd2a9d1452ab7fab5eb')
    for pin in pins['variants'].values():
        freeze=doc(pin['freezeReceiptPath'],pin['freezeReceiptSha256']);assert len(freeze['copies'])==474
        for row in freeze['copies']:checked(row['path'],row['sha256'],row['bytes'])
    native=doc(BASE/'independent-corrected-replay-results-review-v1/native-results.json')
    assert native['state']=='CORRECTED_CLASSIC_CURRENT_SOURCE_NATIVE_REHASH_PASSED'
    for row in doc(BASE/'independent-corrected-replay-results-review-v1'/native['verifiedFiles']['path'],native['verifiedFiles']['sha256'])['files']:checked(row['path'],row['sha256'],row['bytes'])
    oracle=doc(SOURCE/'capability/focused/node-results.json','34d1c9df3ff58ddf9740b96210cf0e12b8a3090a038cb2745028f24a3adfcdb7')
    summaries=[];all_components={};reports={}
    imports_root=doc(ADOPTION/'corrected-followon-imports-root-results.json','283eb29186b0c7cb707e527859cf21c82d4043255b06c32ac4b082c3605ae970')
    tool=Path('/tmp/starling-node-compat/improved-build/cache/wasm-tools/1448/wasm-tools')
    checked(tool,'b332dd79057dafdcc8a36ca933d0d499acea506b56b1ea28e28fbb036c9e713d')
    for name in NAMES:
        output=ROOT/name;collector=doc(ADOPTION/('corrected-'+name+'-root-results.json'),COLLECTORS[name]['sha256']);assert collector['rawTerminalExitCodeObservedByRoot']==0
        assert collector['toolSession']==COLLECTORS[name]['session']
        assert len(collector['artifacts'])==COLLECTORS[name]['artifacts']
        for row in collector['artifacts']:checked(row['path'],row['sha256'],row['bytes'])
        for row in collector.get('links',[]):assert Path(row['path']).is_symlink()and os.readlink(row['path'])==row['target']
        if collector.get('collector'):checked(collector['collector']['path'],collector['collector']['sha256'],collector['collector']['bytes'])
        report=doc(output/'results.json');reports[name]=report;admission=report.get('preflight',report.get('productionTickAdmission'));variant=admission['variant'];pin=pins['variants'][variant]
        assert report['state']==collector['resultState']and report['engineSha256']==pin['engineSha256']==admission['engineSha256']
        assert admission['sourceFilesVerified']==342
        assert pin['sourceContractVersion']=='sm-classic-trace-source-v1'
        assert pin['classicTraceSourcePolicy']['unchangedNativePaths']==339 and pin['classicTraceSourcePolicy']['changedNativePaths']==3
        source_seal=root_seal if name=='allocator-gc' else cap_seal
        assert admission['inputClosure']=={'path':str(SOURCE/('input-freeze.json' if name=='allocator-gc' else 'capability/input-freeze.json')),'sha256':'ab2a5a5822e8925cf50f363ecb024a29e31017d4fca581203ebbd3741759845f' if name=='allocator-gc' else 'de0194d95d93b2b527f323a8e6d506d9c2e0fd9e899f1e0ae009f89633812b06','files':2293 if name=='allocator-gc' else 2292}
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
            argv=[str(tool),'component','wit',path]
            result=subprocess.run(argv,capture_output=True,timeout=55)
            assert result.returncode==0 and result.stderr==b''
            wit=result.stdout.decode();assert 'export run: func() -> string;'in wit
            emitted=[line.strip().split('import ',1)[1][:-1] for line in wit.splitlines() if line.strip().startswith('import ')]
            assert emitted==expected
            destination=HERE/'wit'/name/(Path(path).name+'.wit');destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(result.stdout)
            root_component=next(r for r in imports_root['components'] if Path(r['path']).resolve()==Path(path).resolve())
            assert root_component['sha256']==sha(data)
            all_components[path]={'path':path,'staticWit':{'argv':argv,'exitCode':0,'sha256':sha(result.stdout),'imports':emitted},'sha256':sha(data),'bytes':len(data),'gate':name,**structure}
        summary={'gate':name,'state':report['state'],'variant':variant,'components':len(fixtures),'imports':expected,'recordedRawExitCode':0}
        if name in ['focused-off','focused-runtime']:
            assert report['nodeOracleSha256']=='34d1c9df3ff58ddf9740b96210cf0e12b8a3090a038cb2745028f24a3adfcdb7'
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
            symbol=report['targetSymbolIdentity'];assert symbol['node']==oracle['targetSymbolInfo'];assert symbol['node']['sameAsNodeRegistry']and not symbol['target']['sameAsNodeRegistry']
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
            getter_source=checked(output/'observation-source/callback-return-cases.mjs').decode()
            assert getter_source.count('get then()')==3 and getter_source.count('return undefined;')==3
            summary.update({'nodeGetterReads':[1,1,0],'jcoAndWasmtimeGetterReads':[0,0,0],'nodeCompatibilityPassed':False,'getterReturnsUndefined':True,'nodeAndJcoRawStdoutAvailable':False,'wasmtimeRawStdoutIndependentlyDecoded':True})
        actual={str(x) for x in output.rglob('*') if x.is_file() and not x.is_symlink()}
        declared={r['path'] for r in collector['artifacts'] if Path(r['path']).is_relative_to(output)}
        assert actual==declared
        summary['exactOutputMembershipChecked']=True
        summary['rootArtifactRecordsRehashed']=len(collector['artifacts'])
        summary['rootToolSession']=collector['toolSession']
        summary['rawTerminalExitObservedByThisReader']=False
        summaries.append(summary)
    for row in list(verified.values()):checked(row['path'],row['sha256'],row['bytes'])
    result={'schemaVersion':1,'state':'INDEPENDENT_FIVE_CORRECTED_FOLLOWON_RESULTS_VERIFIED_WITH_KNOWN_COUNTEREXAMPLES',
      'verifiedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourceIndexSha256':'a08aec2d8a28f6bb91251841b617be20820c23ab085e526d0dc107439b061c6e',
      'sourceIndexedFiles':83,'sourceRootRows':2293,'sourceCapabilityRows':2292,'runtimeIndexSha256':'e1f87cd6a2fd09ff34055187bfb938c2b094c3fd333ef9f57b6a1eea4c175b78',
      'runtimeConsumedRows':len(runtime_seal['inputs']),'toolTrees':len(runtime_seal['toolTrees']),'toolLinks':len(runtime_seal['toolLinks']),
      'gates':summaries,'actualDerivedComponentCount':len(all_components),'components':list(all_components.values()),'verifiedFiles':list(verified.values()),
      'coreGlueReview':review_core_glue(ROOT,list(all_components.values())), 'rawHostEvidence':raw_host_inventory(reports),
      'rootImportReceipt':{'path':str(ADOPTION/'corrected-followon-imports-root-results.json'),'sha256':'283eb29186b0c7cb707e527859cf21c82d4043255b06c32ac4b082c3605ae970'},
      'componentCountsAreNotGlobalUniqueness':True,
      'allGateCompletionSealsMatchActualNativePreflight':True,'sourceBeforeAfterFacts':'Root wrappers recorded preflight/completion after recheck; current complete source/tool/native inventories independently rehashed here.',
      'reviewerExecutedGuestNodeOracleBuildHostOrReplay':False,'runtimeCompatibilityComplete':False,
      'collectorHistory':'Root first unsaved collector attempt read fixture sourceFiles list as native count; corrected sourceFilesVerified342 evidence and collector bytes are preserved. No engine/product failure inferred.',
      'limitations':['This verifies existing Root-observed raw0 observations, reports, code and bytes; it does not repeat runtime execution. Raw terminal outcomes were not independently observed by this reader.',
        'Raw Wasmtime stdout is independently decoded only where actually retained. Parsed-only records, including allocator GC, remain missing-raw evidence and are not reconstructed.',
        'Fatal child status0 means the fresh test child caught an expected trap and discarded the instance; Wasmtime nonzero is generic trap evidence, not hidden JavaScript cause identity or failed-instance reuse.',
        'Initializer failures have no emitted successful component; component count is derived from actual fixture/artifact rows, excluding rejected snapshots.',
        'Getter counters are .then getter READS returning undefined, not callable-then invocation counts; Node parity remains false. Symbol registry mismatch remains.',
        'Moving-GC gates retain combined application/VM owners; no isolated-root, OOM/DEBUG, reset, ALS or performance proof.',
        'HTTP, actual20 workload/14 boundary cases, timing and acceptance remain separate.']}
    with(HERE/'results.json').open('x')as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps({'state':result['state'],'components':len(all_components),'verifiedPaths':len(verified),'resultsSha256':sha((HERE/'results.json').read_bytes())}))
if __name__=='__main__':main()
