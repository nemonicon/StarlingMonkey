"""One-shot DATA-only curation. Never imports/runs an application or monitor."""
from pathlib import Path
import base64
import hashlib
import json
import struct

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parents[1]/'native-profile-host-v2'
ACTUAL=Path('/private/tmp/starling-node-compat/next-native-profile-host-v2')
MONITOR=ACTUAL.with_name(ACTUAL.name+'-monitor')
def read(p):return json.loads(Path(p).read_text())
def row(p):
    p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def verify(r):assert row(r['path'])==r,r['path']
def family(ref):
    verify(ref);root=Path(ref['path']).parent;index=read(ref['path']);names=[r['path'] for r in index['files']]
    assert len(names)==len(set(names))
    assert set(names)|{'index.json'}=={x.relative_to(root).as_posix() for x in root.rglob('*') if x.is_file()}
    for r in index['files']:
        p=Path(r['path']);assert not p.is_absolute() and '..' not in p.parts and not(root/p).is_symlink()
        assert row(root/p)==dict(r,path=str(root/p))
    return len(names)
def main():
    assert not (HERE/'index.json').exists(),'Never rewrite a sealed review'
    plan=read(SOURCE/'plan.json');authority=SOURCE.with_name('native-profile-host-v2-root-results')/'authority.json';auth=read(authority)
    assert auth['state']=='ROOT_NEXT_SELECTED_PROFILE_HOST_AUTHORIZED_V2'
    assert auth['sourceIndex']==row(SOURCE/'index.json') and auth['plan']==row(SOURCE/'plan.json')
    assert auth['localhostServerAllowed'] is auth['browserAllowed'] is True
    for k in ['compilerAllowed','nativeBuildAllowed','guestAllowed','engineAllowed','externalApplicationDeploymentAllowed']:assert auth[k] is False
    family(auth['sourceIndex'])
    for ref in plan['sourceFamilies']:family(ref)
    for ref in plan['protectedInputs']:verify(ref)
    t=read(MONITOR/'terminal.json');obs=read(MONITOR/'observation.json');result=read(ACTUAL/'result.json');browser=read(ACTUAL/'browser/result.json')
    assert t['pid']==47744 and t['rawExitCode']==1
    assert t['parentOwnedGroupGone'] and t['allObservedOwnedGroupsGone']
    assert not t['timeout'] and not t['forcedCleanup']
    for k in ['errors','signals','interruptedSignals','remainingObservedPids']:assert t[k]==[]
    assert t['authority']==row(authority)
    for k in ['stdout','stderr']:verify(t[k])
    assert t['stderr']['bytes']==0
    assert obs['state']=='ROOT_NEXT_SELECTED_PROFILE_HOST_OBSERVATION_V2' and obs['rawExitCode']==1 and obs['ownedGroupsClean'] and obs['protectedInputsPreserved']
    assert obs['terminal']==row(MONITOR/'terminal.json') and obs['result']==row(ACTUAL/'result.json') and obs['hostExperimentPassed'] is False
    assert result['suite']=='FULL_NEXT_SELECTED_HTTP_CLASSIC_TOWEB_IMPORTS_PRIVATE_VM_HOST_V2' and result['prepared'] and not result['passed']
    assert result['installed']=={'next':'16.4.5','react':'19.3.1','react-dom':'19.3.1'}
    assert result['guestExecuted'] is False and result['applicationModified'] is False
    assert result['errors']==result['transportErrors']==[] and result['browser']==browser
    for key in ['sourceServer','httpFactory','harness','moduleSource','hostModuleProvider','toWebSource']:verify(result[key])
    http={r['id']:r for r in result['http']};assert len(result['http'])==len(http)==24
    contract=read(SOURCE.parent/'fixture-contract.json');bodies={}
    for record in result['http']:
        raw=(ACTUAL/'responses'/str(record['id']+'.txt')).read_bytes();assert len(raw)==record['bodyBytes'] and hashlib.sha256(raw).hexdigest()==record['bodySha256'];bodies[record['id']]=raw.decode('utf8')
    for item in contract['requests']:
        r=http[item['id']];body=bodies[item['id']];assert r['status']==item['status'] and r['passed'] and r['failures']==[]
        assert all(s in body for s in item.get('includes',[]))
        if 'location' in item:assert r['headers']['location']==item['location']
        if 'json' in item:
            actual=json.loads(body)
            for k,v in item['json'].items():assert actual[k]==v,(item['id'],k)
        for k,v in item.get('responseHeaders',{}).items():assert r['headers'][k]==v
        for k,vs in item.get('responseHeaderIncludes',{}).items():assert all(v in r['headers'][k] for v in vs)
        if 'equalJsonTo' in item:assert body==bodies[item['equalJsonTo']]
    action=http['server-action-submit'];assert action['passed'] and action['status']==303 and action['headers']['location']=='/action-result?value=fixture-action'
    assert '$ACTION_ID_' in bodies['server-action-form-ssr'] and 'NEXT_ACTION_RESULT' in bodies['server-action-result-page']
    cache=result['cacheInvalidation'];assert cache['passed'] and cache['before']==json.loads(bodies['cache-first']) and cache['after']==json.loads(bodies['cache-after-revalidate']) and cache['before']['generation']==1 and cache['after']['generation']==2
    chunks=read(ACTUAL/'stream-chunks.json');raw=b'';shell=ready=-1
    for i,r in enumerate(chunks):
        b=base64.b64decode(r['base64'],validate=True);assert len(b)==r['bytes'];raw+=b
        if shell<0 and b'NEXT_STREAM_SHELL' in raw:shell=i
        if ready<0 and b'NEXT_STREAM_READY' in raw:ready=i
    raw.decode('utf8');assert len(chunks)==5 and shell==0 and ready==2
    assert result['streaming']==dict(chunks=5,shellChunk=0,readyChunk=2,complete=True,incrementalDeliveryObserved=True)
    assert browser['playwrightVersion']=='1.64.1' and browser['browserVersion']=='156.0.8078.81'
    assert len(browser['tests'])==2 and all(r['passed'] and not r['timedOut'] and r['error'] is None for r in browser['tests'])
    assert browser['functionalPassed'] is True and browser['browserErrorFree'] is False and browser['passed'] is False
    assert browser['pageerrors']==browser['consoleerrors']==browser['errors']==[]
    assert browser['browserClosed'] and browser['ephemeralContexts'] and not browser['userProfileUsed']
    for k in ['executable','playwrightPackage','playwrightEntry']:verify(browser[k])
    images=[]
    for test in browser['tests']:
        verify(test['screenshot']);b=Path(test['screenshot']['path']).read_bytes();assert b[:8]==b'\x89PNG\r\n\x1a\n';w,h=struct.unpack('>II',b[16:24]);assert w>0 and h>0;images.append(dict(id=test['id'],width=w,height=h,descriptor=test['screenshot']))
    failed=browser['failedrequests'];assert len(failed)==1
    assert failed[0]=={'test':'server-action','url':result['origin']+'/actions','method':'POST','resourceType':'fetch','failure':{'errorText':'net::ERR_ABORTED'}}
    actions=browser['actionPosts'];assert len(actions)==1 and actions[0]['url']==result['origin']+'/actions'
    post=base64.b64decode(actions[0]['bodyBase64'],validate=True);assert len(post)==actions[0]['bytes'] and b'browser-action' in post and actions[0]['headers']['next-action']
    actiontest=next(x for x in browser['tests'] if x['id']=='server-action');assert actiontest['observations']['url']==result['origin']+'/action-result?value=browser-action' and actiontest['observations']['value']=='browser-action'
    assert result['browserExit']==dict(code=1,signal=None)
    snap=result['moduleSnapshot'];metrics=snap['contextMetrics']
    assert metrics==dict(neutralEntries=1,freshEntries=40,prepareOwners=[None],conversionOwners=list(range(1,41)),bridgeOwners=list(range(1,41)),pairedClassChecks=40)
    for k in ['candidateModuleIdentity','hostBufferUnchanged','privateGlobalBufferSameAsSelected']:assert snap[k]
    assert result['hostBufferUnchanged'] and snap['cachedModules']==412 and len(snap['compiled'])==406
    lines=(MONITOR/'stdout.log').read_text().splitlines();prefix=[];records=[]
    for line in lines:
        try:records.append(json.loads(line))
        except json.JSONDecodeError:prefix.append(line)
    assert len(records)==2 and len(prefix)==1 and 'Running next.config' in prefix[0]
    assert records[0]['functionalPassed'] and not records[0]['passed'] and not records[0]['browserErrorFree']
    assert records[1]==dict(state='FULL_NEXT_SELECTED_PROFILE_HOST_FAILED',http=24,passedHttp=24,errors=[],transportErrors=[],guestExecuted=False)
    # Retain only finite complete experiment outputs, never the application tree.
    portable=[]
    def copy(original,relative):
        target=HERE/relative;target.parent.mkdir(parents=True,exist_ok=True);b=original.read_bytes();target.write_bytes(b);assert row(target)['sha256']==row(original)['sha256'];portable.append(dict(original=row(original),retained=dict(row(target),path=relative)))
    for q in sorted(ACTUAL.rglob('*')):
        if q.is_file() and 'application' not in q.relative_to(ACTUAL).parts:copy(q,'actual/'+q.relative_to(ACTUAL).as_posix())
    for q in sorted(MONITOR.rglob('*')):
        assert not q.is_symlink()
        if q.is_file():copy(q,'monitor/'+q.relative_to(MONITOR).as_posix())
    copy(authority,'root-authority.json')
    (HERE/'portable-files.json').write_text(json.dumps({'schemaVersion':1,'files':portable,'originalPathsUnmodified':True},indent=2)+'\n')
    summary={'schemaVersion':1,'state':'ACTUAL_NEXT_SELECTED_PROFILE_HOST_V2_DATA_VALIDATED_BROWSER_DIAGNOSTIC_UNRESOLVED','observationsValidated':True,'experimentPassed':False,'sourceAuthorRelationship':'Reviewer authored ToWeb and hostv2 Source; actual independent Root execution DATA evaluated without Source approval claim','sourceIndex':row(SOURCE/'index.json'),'plan':row(SOURCE/'plan.json'),'rootAuthority':row(authority),'actualResult':row(ACTUAL/'result.json'),'terminal':row(MONITOR/'terminal.json'),'rootObservation':row(MONITOR/'observation.json'),'rawExitCode':1,'ownedGroupsClean':True,'protectedInputsRehashed':len(plan['protectedInputs']),'sourceFamiliesAuthenticated':len(plan['sourceFamilies']),'httpPassed':24,'httpTotal':24,'cacheGeneration':[1,2],'strictStream':dict(result['streaming'],wholeBytes=len(raw),wholeSha256=hashlib.sha256(raw).hexdigest()),'browserFunctionalPassed':2,'browserTotal':2,'browserPageErrors':0,'browserConsoleErrors':0,'browserRequestFailures':failed,'browserScreenshots':images,'browserErrorFree':False,'exactFailureClassification':'Single observed /actions POST fetch net::ERR_ABORTED; functional action/navigation/result and all HTTP contracts pass. No request-response/phase/close timestamp trace retained; cause and whether navigation/context-close cancellation are not established. No missing-facade failure observed.','stdoutRoles':{'diagnosticPrefixLines':len(prefix),'JSONRecords':len(records),'allOriginalBytesRetained':True},'contextModelMetrics':metrics,'compiledModules':406,'cachedModules':412,'hostQualifications':result['hostOnlyQualifications'],'nativeOrGuestExecuted':False,'noRetryOrProfileModification':True,'fullNextOnWasmAccepted':False,'adoptionAuthority':False}
    (HERE/'results.json').write_text(json.dumps(summary,indent=2)+'\n')
    for ref in plan['protectedInputs']:verify(ref)
    for ref in plan['sourceFamilies']:family(ref)
    family(auth['sourceIndex'])
    for r in portable:verify(r['original']);assert row(HERE/r['retained']['path'])==dict(r['retained'],path=str(HERE/r['retained']['path']))
    files=[]
    for q in sorted(HERE.rglob('*')):
        assert not q.is_symlink()
        if q.is_file() and q!=HERE/'index.json':files.append(dict(row(q),path=q.relative_to(HERE).as_posix()))
    (HERE/'index.json').write_text(json.dumps({'schemaVersion':1,'state':'ACTUAL_NEXT_HOST_V2_COMPACT_DATA_REVIEW','files':files},indent=2)+'\n')
    assert {x.relative_to(HERE).as_posix() for x in HERE.rglob('*') if x.is_file()}=={r['path'] for r in files}|{'index.json'}
    for r in files:assert row(HERE/r['path'])==dict(r,path=str(HERE/r['path']))
    print(json.dumps({'index':row(HERE/'index.json'),'results':row(HERE/'results.json'),'members':len(files),'payloadBytes':sum(r['bytes'] for r in files)},indent=2))
if __name__=='__main__':main()
