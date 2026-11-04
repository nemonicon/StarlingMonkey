"""Compare saved fresh observations with immutable finite Node/reflection oracles."""
from pathlib import Path

def review(reports,metadata,document,regular,family,source,output):
    node_root=Path('/tmp/starling-node-compat/classic-trace-source-v1/tests/node-compat')
    native={r['path']:r['sha256'] for r in metadata['sourceManifest']}
    records=[]
    core=reports['core']
    for n,value in enumerate(core['calls'],1):
        assert value=={'coreVersion':'sm-node-22.14.0-m0.11','allocUnsafePolicy':'zeroed-no-pool-direct-u8-v1','allocUnsafePrimordialCalls':{'integerCalls':0,'finiteCalls':0,'truncatedLength':3},'calls':n,'snapshot':'native Buffer/brand/codecs survive','strings':381,'bytes':250,'seed':'0x57415349','unavailableMethods':91,'backingCases':['resizable-rejected','detached-rejected'],'nativeImports':['node:buffer','node:child_process'],'staticCommonJS':True,'globalBufferIdentity':True,'stubCalls':9,'stubConstructors':9}
    from evidence_helpers import cli_string
    assert cli_string(core['rawAliasFixture']['wasmtimeStdout'])=='native registry aliases, dynamic imports and per-specifier caching passed'
    records.append({'module':'core','strings':381,'bytes':250,'unavailableMethods':91,'stubCallsAndNew':9,'retainedCalls':2})
    stream=reports['stream-web'];manifest=document(Path('/tmp/starling-node-compat/production-classic-trace-v1/native-freeze/source/builtins/node-compat/export-manifest.stream-web.node-v22.14.0.json'))
    for n,value in enumerate(stream['calls'],1):
        assert value['calls']==n and value['names']==manifest['modules']['node:stream/web']['exports']
        for key,count in [('constructors',41),('codecs',250),('cancellations',4),('guards',24),('views',12),('controllers',6),('iterations',67),('data',26)]:assert value[key]==count
        assert value['passed'] and value['commonJS'] and value['snapshotResumption']
        assert value['fixtureRegistryUsed'] is value['applicationFactoryUsed'] is False
        assert value['policies']['ordinaryNativeBrandProof'] is False
    records.append({'module':'stream/web','finiteNamespaceCompared':True,'guardAndDataCounterexamplesPreserved':True})
    events=reports['optional/events'];oracle=document(node_root/'foundation-events/native-node-results.json','3c387dfda29f2e11ab8690c246911aabfbb634fe1038c36d8e805dd1c252c189')
    assert native['builtins/node-compat/events.mjs']==oracle['facadeSha256']
    regular(node_root/'foundation-events/native-checks.mjs',oracle['checksSha256'])
    for n,value in enumerate(events['calls'],1):
        assert value['calls']==n and value['snapshotTicks']==n+1 and value['namespaceIdentity']
        for k in ['cases','nativeCases','profile']:assert value[k]==oracle[k]
        assert value['commonJS']=={'same':True,'constructorAlias':True,'defaultProperty':'undefined','errorMonitorType':'symbol','rejectedCall':'ERR_SM_NODE_UNSUPPORTED','rejectedConstruction':'ERR_SM_NODE_UNSUPPORTED'}
    assert events['aliases']['names']==oracle['cases'][0]['result']['names']
    records.append({'module':'events','oracleCases':len(oracle['cases']),'nativeCases':len(oracle['nativeCases']),'reflectionAndProfileCompared':True})
    pinned={'assert':'cbb3bcb3f6bc9e97b12b1a61167483ac0f949de199ae6bd0172926419f4c01a3','querystring':'e59e05a7cb470970d9bcce230f359cf74bf62a00b094510a2df16d4ab3f901a4','util':'489cb9cf4fbe256201f70e385d4326ea32552d2f2a1f187211d9409e73838816'}
    for name,sha in pinned.items():
        report=reports['optional/'+name];oracle=document(node_root/('foundation-'+name)/'native-node-results.json',sha)
        assert oracle['node']=='v22.14.0'
        for filename,value in oracle['sources'].items():
            key='builtins/node-compat/'+filename
            if key in native:assert native[key]==value
            else:
                assert filename.startswith('LICENSE.')
                regular(node_root.parent.parent/'builtins/node-compat'/filename,value)
        ancestry=report['registrarOracleAncestry']
        assert ancestry['kind']==name and ancestry['oracleSha256']==sha
        assert ancestry['oracleRegistrarSha256']==oracle['registrarSha256']=='19eef9879c94e5232238f6df738d57057d384fa025849ee319fcf51eb06eda2b'
        assert ancestry['actualRegistrarSha256']==native['builtins/node-compat/register.cpp']=='2848f059fb5693aa37c54945bff685444c8431007ceaec59d3335d01f7aced4a'
        assert ancestry['oracleRewritten'] is ancestry['metadataProjected'] is ancestry['tickRegistrarChanged'] is False
        for row in report['sourceFiles']:regular(node_root/('foundation-'+name)/row['name'],row['sha256'])
        for n,value in enumerate(report['calls'],1):
            assert value['calls']==n and value.get('failure') is None
            if name=='util':
                variant=next(x for x in oracle['variants'] if x['features']==value['cases']['features'])
                assert value['cases']==variant and value['exports']==oracle['expectedExports']
                assert len(value['deferred'])==108 and all(x['code']=='ERR_SM_NODE_UNSUPPORTED' and x['profile']=='sm-node-22.14.0-m0.7' for x in value['deferred'])
                assert value['snapshotIdentity'] and value['noFacadeBundled']
                assert value['hardening']=={'unsupportedCode':'ERR_SM_NODE_UNSUPPORTED','invalidCode':'ERR_INVALID_ARG_TYPE','setterCalls':0,'depth':4}
            else:
                assert value['cases']==oracle['cases'] and value['profile']==oracle['sourceProfile']
                assert value['snapshotIdentity'] and value['namespaceIdentity']
                assert value['aliases']['thenType']=='undefined' and value['aliases']['sharedMutation']
                assert value['commonJS']['same'] and value['commonJS']['rejectedCall']==value['commonJS']['rejectedConstruction']=='ERR_SM_NODE_UNSUPPORTED'
                if name=='assert':assert value['snapshotCount']==n
                else:assert value['snapshotByte']==65+n and value['snapshotValues']==2+n
        records.append({'module':name,'oracleSha256':sha,'allSavedCasesAndProfilesCompared':True,'finiteReflectionCompared':True,'oracleRegistrarAncestryComparedWithoutProjection':True})
    decoder=reports['optional/string-decoder'];corpus=document(node_root/'foundation-string-decoder/component-corpus.json','1fdb198d1d07271fe123365856d5cbc1f43468496573b5452ca658b360258f09')
    for value in decoder['calls']:
        assert value['genericCases']==len(corpus['decoderCases'])==40 and value['sequences']==len(corpus['sequences'])==2982
        assert value['writes']==sum(len(x['chunks']) for x in corpus['sequences'])==8886
        assert value['mutationChecks']==2 and value['detachedInternalStateChecks']==5 and value['primordialReplacementCalls']==0
        assert value['nativeAliases']==2 and value['commonJS'] and value['identities'] and value['noGlobalPollution']
    for row in decoder['sourceManifest']:regular(node_root/'foundation-string-decoder'/row['path'],row['sha256'])
    records.append({'module':'string_decoder','corpusSequences':2982,'corpusWrites':8886,'genericCases':40,'preservedOrderingDeviations':2})
    return {'moduleChecks':records,'oracleExecutedByThisReader':False,'observationsAreFreshReportRecords':True,'oldReportsNotUsedAsCurrentPasses':True}
