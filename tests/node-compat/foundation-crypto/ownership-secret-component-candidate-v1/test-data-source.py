"""Pure DATA/schema and Source-coupled checks; no Node/JS/helper/tool execution."""
from pathlib import Path
import copy,hashlib,json,re
HERE=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_bytes())
refs=read(HERE/'references.json');checks=[]
def test(value,name):assert value,name;checks.append(name)
def refuses(fn,name):
    try:fn()
    except(AssertionError,KeyError,TypeError,ValueError):checks.append(name)
    else:raise AssertionError('Expected refusal: '+name)
data=read(refs['actualRetainedRecordData']['path']);h=data['historicalBootstrap'];code=(HERE/'build.mjs').read_text();body=(HERE/'caller-body.mjs').read_text()
def history_model(x):
    assert x==h and len(x)==41 and x['variant']=='normal-off'and x['nativeSourceFiles']==355 and x['externalEmbeddingSources']==3 and x['selectedManifestCount']==11
    m=x['metadata'];assert len(m)==75 and len(m['sourceManifest'])==355 and len(m['componentizeSourceManifest'])==3 and len(x['selectedManifests'])==11
    assert m['cryptoKeyOwnershipPolicy']['version']=='sm-webcrypto-key-owner-and-prototype-guard-source-v1'
    assert m['cryptoSecretFailureSourcePolicy']['version']=='sm-webcrypto-secret-failure-owner-source-v2'
    assert m['entropyPolicy']=='off'and m['gcStress']is False and m['oomTesting']is False
history_model(h);checks.append('Actual full historical355+3/11 frame accepted as DATA')
for name,change in [('nine manifests',lambda f:f['selectedManifests'].__delitem__(slice(9,None))),('ten manifests',lambda f:f['selectedManifests'].pop()),('native342',lambda f:f.__setitem__('nativeSourceFiles',342)),('old engine36bd',lambda f:f['engine'].__setitem__('sha256','36bd850895a11af8ffaefdb8296630222c4ad4652a0e58f45ce0ec23c1bebc05')),('missing guarded prototype',lambda f:f['metadata']['cryptoKeyOwnershipPolicy'].__setitem__('version','old-unsafe')),('missing secret layer',lambda f:f['metadata']['cryptoSecretFailureSourcePolicy'].__setitem__('version','old')),('GC projection',lambda f:f['metadata'].__setitem__('gcStress',True)),('entropy projection',lambda f:f['metadata'].__setitem__('entropyPolicy','runtime-only')),('metadata shortened',lambda f:f['metadata'].pop('limitations')),('historical counter relabeled',lambda f:f.__setitem__('currentCompleteVerifierCalls',0))]:
    f=copy.deepcopy(h);change(f);refuses(lambda:history_model(f),'Full-history refuses '+name)
schema=read(refs['manifestSchema']['path'])
def valid(value,s):
    if '$ref'in s:
        t=schema
        for name in s['$ref'][2:].split('/'):t=t[name.replace('~1','/').replace('~0','~')]
        valid(value,t)
    if 'const'in s:assert type(value)is type(s['const'])and value==s['const']
    if 'enum'in s:assert value in s['enum']
    types={'object':dict,'array':list,'string':str,'boolean':bool,'integer':int,'number':(int,float)}
    if 'type'in s:assert type(value)in(types[s['type']]if type(types[s['type']])is tuple else(types[s['type']],))
    if type(value)is str:
        assert len(value)>=s.get('minLength',0)
        if 'pattern'in s:assert re.search(s['pattern'],value)
    if type(value)in[int,float]:assert value>=s.get('minimum',float('-inf'))and value<=s.get('maximum',float('inf'))
    if type(value)is list:
        assert len(value)>=s.get('minItems',0)
        if s.get('uniqueItems'):assert len(value)==len(set(value))
        if 'items'in s:
            for item in value:valid(item,s['items'])
    if type(value)is dict:
        assert all(k in value for k in s.get('required',[]))
        for k,v in value.items():
            if 'propertyNames'in s:valid(k,s['propertyNames'])
            if k in s.get('properties',{}):valid(v,s['properties'][k])
            elif s.get('additionalProperties')is False:raise AssertionError('Unexpected property')
            elif type(s.get('additionalProperties'))is dict:valid(v,s['additionalProperties'])
def manifest_model(m):
    valid(m,schema);assert m['modules'];aliases=set()
    for canonical,v in m['modules'].items():
        assert 'default'in v['exports']and 'then'not in v['exports']
        for alias in v['aliases']:assert alias not in aliases;aliases.add(alias)
        for name in list(v.get('importOnlyExports',[]))+list(v.get('numericExports',{})):assert name!='default'and name in v['exports']
for m in h['selectedManifests']:manifest_model(m)
checks.append('All actual eleven manifests satisfy pure model of exact frozen schema/validator rules')
mapping={}
for m in h['selectedManifests']:
    for canonical,module in m['modules'].items():
        assert canonical not in mapping;mapping[canonical]=canonical
        for alias in module['aliases']:assert alias not in mapping;mapping[alias]=canonical
test('node:crypto'not in mapping and 'crypto'not in mapping,'Whole actual native map keeps public Nodecrypto unadmitted')
test('node:zlib'in mapping and 'node:stream/consumers'in mapping,'Actual11 includes both selected modules older enumeration omits')
for name,mutate in [('schema missing required',lambda m:m.pop('modules')),('undeclared extra schema field',lambda m:m.__setitem__('invented',True)),('then export',lambda m:next(iter(m['modules'].values()))['exports'].append('then'))]:
    m=copy.deepcopy(h['selectedManifests'][0]);mutate(m);refuses(lambda:manifest_model(m),'Manifest model refuses '+name)
deriv=read(HERE/'derivations.json')
for local,key in [('guest.mjs','guestDonor'),('public-abi.wit','witDonor')]:test((HERE/local).read_bytes()==Path(deriv[key]['path']).read_bytes(),'Exact unchanged '+local+' full source')
guest=(HERE/'guest.mjs').read_text();work=read(HERE/'future-validation-workload.json')
for marker in ['async function prototypeRefusals()','globalThis.CryptoKey.prototype','caseId<4','else result=await prototypeRefusals();','export async function validate()','for(let id=0;id<4;id++)']:
    test(marker in guest,'Full guarded guest retains '+marker)
test(work['case3MayBeOmitted']is False and len(work['ordinaryCases'])==4,'Future completion cannot omit prototype refusals')
test(work['normalSchedule']['expectedHarnessEntryCounters']['runCalls']==12 and work['normalSchedule']['freshValidateExpectedCounters']['runCalls']==4,'Full retained and fresh4-case workload preserved')
test("builtinMap(h.selectedManifests)"in code and 'builtinManifests:h.selectedManifests,virtualModules:{}'in code,'Real full11 builtinMap and explicit bundler API')
test('selectedManifestsForEngine('not in code and 'cryptoOwnerBootstrapPreflight('not in code and 'secretArtifactBootstrapPreflight('not in code,'No old selector/one-shot/native helper admission path')
test('await api.retainedSecretBootstrapPreflight({configDescriptor:f.retainedConfig})'in code and code.count('record=await api.retainedSecretBootstrapPreflight(')==1,'One genuine retained API action seam only')
test('await recheck();await record.recheck();'in code and 'try{if(record)await record.recheck();}catch'in code,'Before and final/failure fresh own rechecks')
test("const loaded"not in code and "await import(pathToFileURL(refs.retainedApi.path))"in code,'Actual original c47 module path, not copied operational API')
test('for(const r of inputs.files)await c.file(r)'in code and 'for(const ix of inputs.families)await c.family(ix)'in code,'Full Source ledger/families before custom imports')
test(code.index('const f=await authenticate(configDescriptor)')<code.index('await import(pathToFileURL(refs.retainedApi.path))')<code.index('await selected.componentize(bundle.code,options)'),'Actual caller auth/API/build order')
test('loadToolchain()'in code and 'loadComponentizer(toolchain)'in code and "patched-import-i32-clock-v2"in code,'Genuine published toolchain/loader APIs and selected version')
test('h.componentizeSourceRoot===refs.physicalRoles.frozenEmbeddingSourceRoot'in code,'Frozen native embedding role remains distinct from packager imports')
test("await out.write('selected-return-transport.json'"in code and "await out.write('transpile-return-transport.json'"in code,'Raw typed tool transports retained before assertions')
test('abi.parsePublicWit(emitted)'in code and 'abi.checkTranspileMetadata(generated)'in code and 'abi.publicJSExports('in code and 'abi.parsePublicDts(dts)'in code,'Actual full ordinary ABI/static generated-source audits retained')
test('generatedModuleImported:false'in code and 'ordinaryGuestExportsInvoked:false'in code and 'keyOperationsInvoked:false'in code,'Construction-only result flags distinct from guest INIT')
test('componentizationAttempted?null:false'in code,'Failed componentization cannot claim INIT did not happen')
test('finalErrors.push'in code and 'primaryError:primary,finalProtectionErrors:finalErrors'in code,'Primary and separate final protection errors retained')
test('const same=isDeepStrictEqual'in code and "rawKey','jwkKey','knownConstructor'"in code,'Typed whole frame comparison and null-key INIT guard')
root=read(HERE/'future-root-authority.template.json');cfg=read(HERE/'future-config.template.json');peer=read(HERE/'future-source-review-contract.json')
test(all(root[k]is None for k in ['state','phase','sourceIndex','entry','sourceIndependentReview','componentBuildAllowed','componentInitializationAllowed','retainedReadOnlyApiAllowed','retainedConfig','actualComponentReview','actualRuntimeAuthority']),'All new action/Root/peer/retainedConfig slotsNULL')
test(cfg['sourceIndex']is cfg['rootAuthority']is peer['componentSourceIndexSha256']is None,'No Source self-approval/config grant')
test(root['ordinaryGuestExportsAllowed']is root['keyOrCryptoOperationsAllowed']is root['generatedModuleImportAllowed']is root['operationalAdmission']is root['runtimeAcceptanceClaim']is False,'All non-construction action flags closed')
result=dict(schemaVersion=1,state='PURE_SECRET355_COMPONENT_DATA_AND_SOURCE_CHECKS_PASSED_V1',checks=len(checks),checkNames=checks,actualConstructorOrApiOrHelperOrToolExecuted=False,actualGuestInitialized=False,actualJavaScriptParsedOrEvaluated=False,modelsNotRuntimeEvidence=True)
(HERE/'pure-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(checks=len(checks),actions=0,jsGrammarChecked=False)))
