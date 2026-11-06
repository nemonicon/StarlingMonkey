"""DATA-only compact comparison of the two already terminal Root attempts."""
from pathlib import Path
import base64
import hashlib
import json
import struct

HERE=Path(__file__).resolve().parent
NEXT=HERE.parents[1]
SOURCE=NEXT/'browser-phase-matched-host-candidate-v1'
def read(p):return json.loads(Path(p).read_text())
def row(p):
    p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def verify(r):assert row(r['path'])==r,r['path']
def family(ref):
    verify(ref);root=Path(ref['path']).parent;j=read(ref['path']);names=[r['path'] for r in j['files']]
    assert len(names)==len(set(names))
    assert set(names)|{'index.json'}=={x.relative_to(root).as_posix() for x in root.rglob('*') if x.is_file()}
    for r in j['files']:
        rel=Path(r['path']);assert not rel.is_absolute() and '..' not in rel.parts and not(root/rel).is_symlink()
        assert row(root/rel)==dict(r,path=str(root/rel))
def main():
    assert not (HERE/'index.json').exists(),'Do not rewrite a sealed review'
    plan=read(SOURCE/'plans.json');family(row(SOURCE/'index.json'))
    for r in plan['protectedInputs']:verify(r)
    for ref in plan['sourceFamilies']:family(ref)
    portable=[];summaries={}
    def copy(original,relative):
        assert not original.is_symlink();b=original.read_bytes();target=HERE/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
        assert row(original)['sha256']==row(target)['sha256'];portable.append(dict(original=row(original),retained=dict(row(target),path=relative)))
    for arm,pid in [('selected',55395),('stock',55394)]:
        p=Path(plan['arms'][arm]['outputRoot']);m=Path(plan['arms'][arm]['monitorOutputRoot']);authpath=HERE.parent/(arm+'-authority.json');auth=read(authpath)
        assert auth['state']=='ROOT_NEXT_BROWSER_PHASE_MATCHED_HOST_AUTHORIZED_V1' and auth['arm']==arm
        assert auth['sourceIndex']==row(SOURCE/'index.json') and auth['plans']==row(SOURCE/'plans.json')
        assert auth['localhostServerAllowed'] is auth['browserAllowed'] is True
        for k in ['compilerAllowed','nativeBuildAllowed','guestAllowed','engineAllowed','externalApplicationDeploymentAllowed']:assert auth[k] is False
        t=read(m/'terminal.json');o=read(m/'observation.json');r=read(p/'result.json');b=read(p/'browser/result.json')
        assert t['pid']==pid and t['rawExitCode']==0 and t['parentOwnedGroupGone'] and t['allObservedOwnedGroupsGone']
        assert not t['timeout'] and not t['forcedCleanup']
        for k in ['errors','signals','interruptedSignals','remainingObservedPids']:assert t[k]==[]
        assert t['authority']==row(authpath)
        for k in ['stdout','stderr']:verify(t[k])
        assert t['stderr']['bytes']==0
        assert o['state']=='ROOT_NEXT_BROWSER_PHASE_MATCHED_HOST_OBSERVATION_V1' and o['arm']==arm and o['rawExitCode']==0 and o['ownedGroupsClean'] and o['protectedInputsPreserved'] and o['hostExperimentPassed']
        assert o['terminal']==row(m/'terminal.json') and o['result']==row(p/'result.json')
        assert r['prepared'] and r['passed'] and r['errors']==r['transportErrors']==[] and not r['guestExecuted'] and not r['applicationModified']
        assert r['suite']==('FULL_NEXT_SELECTED_TOWEB_INSTRUMENTED_BROWSER_CONTROL_V1' if arm=='selected' else 'FULL_NEXT_STOCK_ORIGINAL_MODULE_BRIDGE_INSTRUMENTED_BROWSER_CONTROL_V1')
        assert r['installed']=={'next':'16.4.5','react':'19.3.1','react-dom':'19.3.1'}
        assert r['harness']==row(SOURCE/('run-'+arm+'.mjs')) and r['sourceServer']==row(Path(plan['standaloneSource'])/'server.js')
        verify(r['moduleSource']);verify(r['hostModuleProvider'])
        if arm=='selected':
            verify(r['toWebSource']);verify(r['httpFactory']);snap=r['moduleSnapshot'];metrics=snap['contextMetrics'];assert metrics['neutralEntries']==1 and metrics['prepareOwners']==[None] and metrics['freshEntries']==metrics['pairedClassChecks']>=24
            assert metrics['conversionOwners']==metrics['bridgeOwners']==list(range(1,metrics['freshEntries']+1))
            assert r['hostBufferUnchanged'] and snap['hostBufferUnchanged'] and snap['privateGlobalBufferSameAsSelected']
        else:verify(r['bridge'])
        assert r['moduleSnapshot']['candidateModuleIdentity']
        # Independent whole body/status/header/JSON/action replay from retained bytes.
        records={x['id']:x for x in r['http']};assert len(records)==len(r['http'])==24;bodies={}
        for x in r['http']:
            raw=(p/'responses'/(x['id']+'.txt')).read_bytes();assert len(raw)==x['bodyBytes'] and hashlib.sha256(raw).hexdigest()==x['bodySha256'];bodies[x['id']]=raw.decode('utf8')
        for item in read(NEXT/'fixture-contract.json')['requests']:
            x=records[item['id']];body=bodies[item['id']];assert x['passed'] and x['failures']==[] and x['status']==item['status']
            assert all(v in body for v in item.get('includes',[]))
            if 'location' in item:assert x['headers']['location']==item['location']
            if 'json' in item:
                actual=json.loads(body)
                for k,v in item['json'].items():assert actual[k]==v
            for k,v in item.get('responseHeaders',{}).items():assert x['headers'][k]==v
            for k,vs in item.get('responseHeaderIncludes',{}).items():assert all(v in x['headers'][k] for v in vs)
            if 'equalJsonTo' in item:assert body==bodies[item['equalJsonTo']]
        action=records['server-action-submit'];assert action['passed'] and action['status']==303 and action['headers']['location']=='/action-result?value=fixture-action'
        cache=r['cacheInvalidation'];assert cache['passed'] and cache['before']==json.loads(bodies['cache-first']) and cache['after']==json.loads(bodies['cache-after-revalidate']);assert [cache['before']['generation'],cache['after']['generation']]==[1,2]
        chunks=read(p/'stream-chunks.json');raw=b'';shell=ready=-1
        for i,x in enumerate(chunks):
            v=base64.b64decode(x['base64'],validate=True);assert len(v)==x['bytes'];raw+=v
            if shell<0 and b'NEXT_STREAM_SHELL' in raw:shell=i
            if ready<0 and b'NEXT_STREAM_READY' in raw:ready=i
        assert r['streaming']==dict(chunks=len(chunks),shellChunk=shell,readyChunk=ready,complete=True,incrementalDeliveryObserved=True) and ready>shell>=0
        raw.decode('utf8')
        assert r['browser']==b and r['browserExit']==dict(code=0,signal=None)
        assert b['suite']=='nextjs-instrumented-browser-phase-v1' and b['passed'] and b['functionalPassed'] and b['browserErrorFree'] and b['browserClosed']
        assert b['playwrightVersion']=='1.64.1' and b['browserVersion']=='156.0.8078.81'
        assert b['pageerrors']==b['consoleerrors']==b['failedrequests']==b['errors']==[]
        assert len(b['tests'])==2 and all(x['passed'] and not x['timedOut'] and x['error'] is None for x in b['tests'])
        for key in ['executable','playwrightPackage','playwrightEntry']:verify(b[key])
        for test in b['tests']:
            verify(test['screenshot']);v=Path(test['screenshot']['path']).read_bytes();assert v[:8]==b'\x89PNG\r\n\x1a\n' and all(struct.unpack('>II',v[16:24]))
        assert b['beforeCloseNetworkCompletionWait'] is False and b['responseFinishedDrainAfterCloseLimitMs']==2000
        # Exact event/identity and phase ordering, not a Chromium cause assertion.
        trace=b['trace'];assert len(trace)==90 and all(x['sequence']==i+1 for i,x in enumerate(trace));ns=[int(x['ns']) for x in trace];assert ns==sorted(ns)
        assert not any(x['event'] in ['requestfailed','response.finished-rejected','page-crash'] for x in trace)
        phases={};requests={}
        for x in trace:
            if x['event']=='phase':phases[(x['test'],x['phase'])]=x
            if 'requestId' in x:requests.setdefault((x['test'],x['requestId']),[]).append(x)
        assert len(requests)==len(b['responseFinishedObservations'])==14
        for (test,requestid),events in requests.items():
            byevent={x['event']:x for x in events};assert set(byevent)=={'request','response','requestfinished','response.finished'}
            assert len(events)==4 and byevent['request']['sequence']<byevent['response']['sequence']<byevent['requestfinished']['sequence']<byevent['response.finished']['sequence']
            assert byevent['response.finished']['error'] is None and byevent['response.finished']['sequence']<phases[(test,'context-close-start')]['sequence']
            assert len({(x['url'],x['method'],x['resourceType']) for x in events})==1
            observation=next(x for x in b['responseFinishedObservations'] if x['test']==test and x['requestId']==requestid);assert observation['error'] is None and observation['status']==byevent['response']['status'] and observation['phase']==byevent['response.finished']['phase']
        for test in ['client-counter','server-action']:
            assert phases[(test,'functional-complete')]['sequence']<phases[(test,'screenshot-start')]['sequence']<phases[(test,'screenshot-complete')]['sequence']<phases[(test,'context-close-start')]['sequence']<phases[(test,'context-close-end')]['sequence']<phases[(test,'response-finished-drain-after-close')]['sequence']<phases[(test,'test-terminal')]['sequence']
        actionevents=next(events for (test,_),events in requests.items() if test=='server-action' and events[0]['method']=='POST' and events[0]['url']==r['origin']+'/actions')
        assert all(x['phase']=='action-submit-and-navigation' for x in actionevents)
        response=next(x for x in actionevents if x['event']=='response');finish=next(x for x in actionevents if x['event']=='response.finished');assert response['status']==200
        navigation=next(x for x in trace if x['event']=='main-frame-navigated' and x['url']==r['origin']+'/action-result?value=browser-action')
        assert finish['sequence']<navigation['sequence']<phases[('server-action','functional-complete')]['sequence']
        actionPosts=b['actionPosts'];assert len(actionPosts)==1 and actionPosts[0]['url']==r['origin']+'/actions';post=base64.b64decode(actionPosts[0]['bodyBase64'],validate=True);assert len(post)==actionPosts[0]['bytes'] and b'browser-action' in post
        lines=(m/'stdout.log').read_text().splitlines();parsed=[];prefix=[]
        for line in lines:
            try:parsed.append(json.loads(line))
            except json.JSONDecodeError:prefix.append(line)
        assert len(parsed)==2 and len(prefix)==1 and 'Running next.config' in prefix[0]
        assert parsed[0]['passed'] and parsed[0]['browserErrorFree'] and parsed[0]['functionalPassed'] and parsed[1]['http']==parsed[1]['passedHttp']==24 and parsed[1]['errors']==parsed[1]['transportErrors']==[]
        for q in sorted(p.rglob('*')):
            if q.is_file() and 'application' not in q.relative_to(p).parts:copy(q,arm+'/actual/'+q.relative_to(p).as_posix())
        for q in sorted(m.rglob('*')):
            assert not q.is_symlink()
            if q.is_file():copy(q,arm+'/monitor/'+q.relative_to(m).as_posix())
        copy(authpath,arm+'/root-authority.json')
        summaries[arm]=dict(actualResult=row(p/'result.json'),browserResult=row(p/'browser/result.json'),terminal=row(m/'terminal.json'),observation=row(m/'observation.json'),authority=row(authpath),nodePid=pid,rawExitCode=0,ownedGroupsClean=True,httpPassed=24,browserPassed=2,cacheGeneration=[1,2],stream=dict(r['streaming'],wholeBytes=len(raw),wholeSha256=hashlib.sha256(raw).hexdigest()),browserRequestFailures=[],traceRows=len(trace),responseFinishedObserved=len(requests),allResponsesCompletedBeforeContextClose=True,actionTrace=dict(requestId=actionevents[0]['requestId'],events=actionevents,navigation=navigation,contextCloseStart=phases[('server-action','context-close-start')]),nativeOrGuestExecuted=False)
    # Both app/cache roots remain separate, with identical pinned source/config.
    assert plan['arms']['selected']['outputRoot']!=plan['arms']['stock']['outputRoot']
    for filename in ['server.js','.next/required-server-files.json']:
        expected=row(Path(plan['standaloneSource'])/filename)
        for arm in ['selected','stock']:assert row(Path(plan['arms'][arm]['outputRoot'])/'application'/filename)['sha256']==expected['sha256']
    comparison=dict(schemaVersion=1,state='ACTUAL_MATCHED_NEXT_BROWSER_PHASE_HOST_CONTROLS_PASSED_V1',sourceIndex=row(SOURCE/'index.json'),plans=row(SOURCE/'plans.json'),sourceAuthorRelationship='Reviewer authored instrumentation and derivative controls; independent Root executions inspected as DATA, not an independent Source approval',arms=summaries,abortedRequestReproduced=False,earlierFailedAttempt=row(NEXT/'native-profile-host-v2-root-results/independent-data-review-v1/index.json'),earlierFailureStillFailed=True,earlierAbortCauseEstablished=False,causalityLimit='One fresh matched attempt per arm; Node processing order and non-recurrence do not identify the earlier Chromium/network cause or estimate a failure rate. Both controls ran concurrently and instrumentation may affect scheduling. No performance comparison.',nextDecision='Preserve the failed original and both successful matched controls. Keep all failure gates and instrumentation, no cancellation filtering or pre-close wait. This supplies a passing layered selected host control; proceed through Root reviewed native build/runtime gates rather than require unrelated host API expansion. Actual full Next-on-Wasm remains unproved.',nativeOrGuestExecuted=False,fullNextOnWasmAccepted=False,adoptionAuthority=False)
    (HERE/'results.json').write_text(json.dumps(comparison,indent=2)+'\n');(HERE/'portable-files.json').write_text(json.dumps(dict(schemaVersion=1,files=portable,originalPathsUnmodified=True),indent=2)+'\n')
    for r in plan['protectedInputs']:verify(r)
    for ref in plan['sourceFamilies']:family(ref)
    family(row(SOURCE/'index.json'))
    for r in portable:verify(r['original']);assert row(HERE/r['retained']['path'])==dict(r['retained'],path=str(HERE/r['retained']['path']))
    files=[]
    for q in sorted(HERE.rglob('*')):
        assert not q.is_symlink()
        if q.is_file() and q!=HERE/'index.json':files.append(dict(row(q),path=q.relative_to(HERE).as_posix()))
    (HERE/'index.json').write_text(json.dumps(dict(schemaVersion=1,state='ACTUAL_MATCHED_NEXT_BROWSER_PHASE_COMPACT_DATA_REVIEW_V1',files=files),indent=2)+'\n')
    assert {x.relative_to(HERE).as_posix() for x in HERE.rglob('*') if x.is_file()}=={r['path'] for r in files}|{'index.json'}
    for r in files:assert row(HERE/r['path'])==dict(r,path=str(HERE/r['path']))
    print(json.dumps(dict(index=row(HERE/'index.json'),results=row(HERE/'results.json'),members=len(files),payloadBytes=sum(r['bytes'] for r in files)),indent=2))
if __name__=='__main__':main()
