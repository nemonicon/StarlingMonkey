"""Portable DATA checker. No oracle, JavaScript, compiler, component or host invocation."""
from pathlib import Path
from collections import Counter
import hashlib,json,re
HERE=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text())
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check():
    rows=read(HERE/'copies.json')['copies'];by={r['role']:r for r in rows};assert len(rows)==len(by)
    names=[]
    for r in rows:
        rel=Path(r['copied']['path']);assert not rel.is_absolute()and '..'not in rel.parts
        p=HERE/rel;assert p.is_file()and not p.is_symlink();assert p.stat().st_size==r['copied']['bytes']==r['original']['bytes'];assert digest(p)==r['copied']['sha256']==r['original']['sha256'];names.append(str(rel))
    assert len(names)==len(set(names))
    def path(role):return HERE/by[role]['copied']['path']
    def data(role):return read(path(role))
    def original(role):return by[role]['original']
    def linked(role,ref):assert original(role)==ref,(role,ref)
    def clean(t,code):
        assert t['rawExitCode']==code and t['timeout']is False and t['forcedCleanup']is False
        assert t['parentOwnedGroupGone']is True and t['allObservedOwnedGroupsGone']is True
        for k in ['signals','interruptedSignals','errors','remainingObservedPids']:assert t[k]==[]
    def terminal(role,code):
        t=data(role+'/terminal.json');clean(t,code)
        for k in ['stdout','stderr']:linked(role+'/'+k+'.log',t[k])
        return t
    def same_signature(r):
        if r['compiled']:return {k:r[k]for k in ['compiled','actualSource','actualFlags','samples']}
        return dict(compiled=False,**{k:r['error'][k]for k in ['valueType','isNull','name','code']})
    # The complete small source family is retained as an immutable versioned baseline.
    source_index=data('probe-source/index.json');source_files={r['path']:r for r in source_index['files']}
    assert set(source_files)|{'index.json'}=={k.removeprefix('probe-source/')for k in by if k.startswith('probe-source/')}
    for name,r in source_files.items():
        actual=original('probe-source/'+name);assert actual['sha256']==r['sha256']and actual['bytes']==r['bytes']
    contract=data('collector-source/case-contract.json')['cases'];assert len(contract)==12
    ids=[r['id']for r in contract];assert len(set(ids))==12
    plan=data('collector-source/plan.json');gap_ids=set(plan['expectedPropertyGapCases']);assert len(gap_ids)==7
    auth=data('root/http-authority.json');probe=data('probe/result.json')
    linked('collector-source/index.json',auth['sourceIndex']);linked('collector-source/plan.json',auth['plan'])
    linked('constructor-source/index.json',auth['constructionCallerIndex']);linked('construction/result.json',auth['constructionResult'])
    linked('construction/component-audit.json',auth['componentAudit']);linked('probe-source/index.json',probe['probeSourceIndex'])
    linked('node-monitor/stdout.log',auth['nodeOracleStdout']);linked('node-monitor/terminal.json',auth['nodeOracleTerminal'])
    assert probe['state']=='ISOLATED_REGEXP_PROBE_FAILED_OBSERVATION_PRESERVED_V1'
    assert probe['sourceIndex']==auth['sourceIndex']and probe['component']==auth['component']and probe['componentAudit']==auth['componentAudit']
    linked('root/http-authority.json',probe['rootAuthority']);assert probe['engine']==plan['engine']
    for k in ['allThreeCaptureAttemptsComplete','comparisonComplete','inputsPreserved']:assert probe[k]is True
    for k in ['observationsValid','nodeSelectedParity','applicationMounted','applicationImported','fullNextAcceptance','adoption']:assert probe[k]is False
    assert len(probe['errors'])==1 and probe['errors'][0]['name']=='AssertionError'and '3 !== 0'in probe['errors'][0]['message']
    assert path('probe/node-oracle.stdout.jsonl').read_bytes()==path('node-monitor/stdout.log').read_bytes()
    frames=[json.loads(s)for s in path('node-monitor/stdout.log').read_text().splitlines()];assert len(frames)==4
    identity=frames[0];assert identity['kind']=='node-oracle-identity'and identity['node']=='v22.14.0'and identity['v8'].startswith('12.4.')and identity['unicode']=='16.0'and identity['icu']=='76.1'and identity['guestExecuted']is False
    terminal('node-monitor',0);counts=Counter();expected_comparisons=[];kelvin=[]
    assert len(probe['responses'])==3
    for call in range(1,4):
        response=probe['responses'][call-1];assert response['call']==call and response['status']==200 and response['rawValueType']=='Uint8Array'and response['ordinalValidated']is True
        linked('probe/response-'+str(call)+'.body',response['body']);assert response['headers']['content-length']==str(response['body']['bytes'])
        payload=data('probe/response-'+str(call)+'.body');assert payload==response['typedPayload']
        frame=frames[call];assert frame['call']==call and frame['kind']=='string'and isinstance(frame['value'],str);node=json.loads(frame['value'])
        for value in [payload,node]:
            assert value['schemaVersion']==1 and value['suite']=='ISOLATED_UNICODE_PROPERTY_REGEXP_PROBE_V1'and value['call']==call
            assert [r['id']for r in value['records']]==ids
            for k in ['applicationImported','applicationRewritten','fullNextClaim']:assert value[k]is False
        assert payload['intlType']=='undefined'and node['intlType']=='object'
        for c,actual,expected in zip(contract,payload['records'],node['records']):
            for r in [actual,expected]:
                assert r['method']==c['method']and r['requestedSource']==c['source']and r['requestedFlags']==c['flags']and type(r['compiled'])is bool
                if r['compiled']:
                    assert [s['input']for s in r['samples']]==c['inputs']
                    for s in r['samples']:
                        assert type(s['matched'])is bool and s['matched']==(s['match']is not None)
                        assert s['match']is None or isinstance(s['match'],str)
                        assert s['index']is None or type(s['index'])is int
                else:
                    e=r['error'];assert e['valueType']=='object'and e['isNull']is False and e['name']=={'type':'string','value':'SyntaxError'}and e['message']['type']=='string'and e['code']=={'type':'undefined'}
            if same_signature(actual)==same_signature(expected):kind='matches-node-selected-semantics'
            elif c['id']in gap_ids and expected['compiled']and not actual['compiled']:kind='expected-noIntl-property-rejection'
            else:kind='unexpected-difference-requires-review'
            counts[kind]+=1;expected_comparisons.append(dict(call=call,id=c['id'],classification=kind,actual=actual,node=expected))
            if kind=='unexpected-difference-requires-review':
                assert c['id']=='unicode-ignorecase-control'and actual['compiled']and expected['compiled']
                differing=[(a,b)for a,b in zip(actual['samples'],expected['samples'])if a!=b];assert len(differing)==1
                a,b=differing[0];assert a=={'input':'K','matched':False,'match':None,'index':None}and b=={'input':'K','matched':True,'match':'K','index':0};kelvin.append(dict(call=call,guest=a,node=b))
    assert counts=={'matches-node-selected-semantics':12,'expected-noIntl-property-rejection':21,'unexpected-difference-requires-review':3}
    assert probe['comparisons']==expected_comparisons and probe['expectedPropertyDifferences']==21
    assert probe['unexpectedDifferences']==[dict(call=n,id='unicode-ignorecase-control')for n in range(1,4)]
    terminal('probe-monitor',1);po=data('probe-monitor/observation.json');assert po['rawExitCode']==1 and po['ownedGroupsClean']is True and po['protectedInputsPreserved']is True and po['observationsValid']is False
    ps=probe['server'];assert ps['exit']==dict(code=0,signal=None,error=None)and ps['forcedCleanup']is False and ps['shutdownRequested']is True and ps['sigintSent']is True
    for key in ['stdout','stderr']:linked('probe/wasmtime.'+key+'.log',ps[key])
    assert '--dir'not in ps['command']and ps['command'][ps['command'].index('--max-instance-reuse-count')+1]=='32'
    construction=data('construction/result.json');audit=data('construction/component-audit.json')
    assert construction['state']=='NEXT_NATIVE_COMPONENT_CONSTRUCTION_PASSED_UNREVIEWED_V2'and construction['passed']is True and construction['entryMode']=='regex-probe'and construction['finalProtection']['unchanged']is True
    assert construction['callerIndex']==auth['constructionCallerIndex']and construction['artifacts']['component']==probe['component']and audit['component']==probe['component']
    linked('probe-source/guest-entry.mjs',construction['artifacts']['inputEntry']);linked('probe-source/index.json',construction['artifacts']['inputSourceIndex'])
    assert audit['state']=='NEXT_NATIVE_COMPONENT_DATA_AUDIT_PASSED_V1'and audit['passed']is True and audit['entryMode']=='regex-probe'
    assert audit['engine']==plan['engine']and audit['nativeMetadata']==plan['nativeMetadata']and audit['allEmittedVersion']=='0.2.10'and audit['noExternalPreview1OrCustomImports']is True
    wit=path('construction/component-wit/stdout.log').read_text();world=wit.split('world root {',1)[1].split('\n}',1)[0]
    imports=re.findall(r'^\s*import ([^;]+);',world,re.M);exports=re.findall(r'^\s*export ([^;]+);',world,re.M)
    assert imports==audit['emittedImports']and set(imports)==set(plan['selectedInterfaces'])and len(imports)==13
    assert exports==audit['exports']==['wasi:http/incoming-handler@0.2.10']
    for command in construction['commands']:
        label=command['label'];t=terminal('construction/'+label,0);linked('construction/'+label+'/terminal.json',command['terminal']);assert command['rawExitCode']==0 and command['clean']is True
    assert '/* #undef JS_HAS_INTL_API */'in path('native-noIntl/js-config.h').read_text()
    assert '#define MOZ_ICU4X 1'in path('native-noIntl/js-confdefs.h').read_text()
    assert '--without-intl-api'in path('native-noIntl/spidermonkey.cmake').read_text()
    # The second actual full application remains an independent failed workload.
    nxt=data('next/result.json');client=data('next/client/result.json');assert nxt['state']=='NEXT_WASMTIME_DEPLOYMENT_FAILED_UNACCEPTED_V2'and nxt['passed']is False and client['passed']is False
    assert nxt['originalInputsPreserved']is True and nxt['readonlyAppPreserved']is True and nxt['adoption']is False
    linked('next/root-authority.json',nxt['rootAuthority']);linked('next/client/result.json',nxt['client']['result']);assert nxt['client']['exit']==dict(code=1,signal=None,error=None)
    terminal('next-monitor',1);ns=nxt['server'];assert ns['exit']==dict(code=0,signal=None,error=None)and ns['forcedCleanup']is False and ns['shutdownRequested']is True and ns['sigintSent']is True
    for owner in ['server','client']:
        for key in ['stdout','stderr']:linked('next/'+('wasmtime'if owner=='server'else'client')+'.'+key+'.log',nxt[owner][key])
    contract_requests=data('next/fixture-contract.json')['requests'];assert len(contract_requests)==23
    assert [h['id']for h in client['http']]==[h['id']for h in contract_requests]
    assert len(client['http'])==23 and client['transportErrors']==[] and len(client['errors'])==1
    for h in client['http']:
        assert h['status']==500 and h['passed']is False
        b=path('next/client/responses/'+h['id']+'.txt').read_bytes();assert len(b)==h['bodyBytes']and hashlib.sha256(b).hexdigest()==h['bodySha256']and h['headers']['content-length']==str(len(b))
    assert re.findall(r'name="(\$ACTION_ID_[^"]+)"',path('next/client/responses/server-action-form-ssr.txt').read_text())==[]
    assert all(k not in client for k in ['cacheInvalidation','streaming','browser'])
    assert '0 !== 1'in client['errors'][0]['message']and ':42:10'in client['errors'][0]['stack']
    assert not any(k.startswith('next/client/browser/')or k.startswith('next/client/stream')for k in by)
    log=path('next/wasmtime.stderr.log').read_text();assert 'invalid class property name in regular expression'in log and '/app/node_modules/next/dist/shared/lib/zod.js:30:36'in log and 'global is not defined'not in log
    assert 'next/dist/compiled/zod-validation-error'in path('next/app-source/zod.js').read_text()
    assert '\\p{ID_Start}'in path('next/app-source/zod-validation-error.js').read_text()and '\\p{ID_Continue}'in path('next/app-source/zod-validation-error.js').read_text()
    if (HERE/'index.json').exists():
        idx=read(HERE/'index.json');expected={r['path']for r in idx['files']};actual={p.relative_to(HERE).as_posix()for p in HERE.rglob('*')if p.is_file()};assert expected|{'index.json'}==actual
        assert not any(p.is_symlink()for p in HERE.rglob('*'))
        for r in idx['files']:
            p=HERE/r['path'];assert p.stat().st_size==r['bytes']and digest(p)==r['sha256']
    return dict(schemaVersion=1,state='FAILED_REGEXP_AND_NEXT_EVIDENCE_VALIDATED_V1',curationChecksPassed=True,underlyingProbePassed=False,underlyingFullNextPassed=False,rawCopies=len(rows),rawBytes=sum(r['original']['bytes']for r in rows),oracleIdentity=identity,httpProbeStatuses=[200]*3,probeOrdinals=[1,2,3],caseComparisons=dict(counts),kelvinDifferences=kelvin,probeRawExitCode=1,nextRawExitCode=1,nextBaseHttpAttempted=23,nextBaseHttpPassed=0,nextActionPostReached=False,nextStrictStreamingReached=False,nextBrowserReached=False,originalsRerun=False,fullNextAcceptance=False,adoption=False)
if __name__=='__main__':print(json.dumps(check(),indent=2,ensure_ascii=False))
