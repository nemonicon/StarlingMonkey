"""Portable DATA validation; success is not strict cohort acceptance."""
from pathlib import Path
import base64
import codecs
import gzip
import hashlib
import json
from urllib.parse import urlsplit
HERE=Path(__file__).absolute().parent

def sha(data):return hashlib.sha256(data).hexdigest()

def clean(terminal, expected_raw_code=0):
    return (type(terminal['rawExitCode']) is int and terminal['rawExitCode'] == expected_raw_code
            and terminal['timeout'] is False and terminal['forcedCleanup'] is False
            and terminal['parentOwnedGroupGone'] is True
            and terminal['allObservedOwnedGroupsGone'] is True
            and all(terminal[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids'])
            and all(g['alive'] is False for g in terminal['finalGroups']))

def contract(record, body, expected, previous):
    text = body.decode('utf8')
    assert record['status'] == expected['status']
    assert all(x in text for x in expected.get('includes', []))
    if 'location' in expected:
        assert record['headers']['location'] == expected['location']
    if 'json' in expected:
        value = json.loads(text)
        assert all(value[k] == v for k, v in expected['json'].items())
    for key, value in expected.get('responseHeaders', {}).items():
        assert record['headers'][key] == value
    for key, values in expected.get('responseHeaderIncludes', {}).items():
        assert all(v in record['headers'][key] for v in values)
    if expected.get('equalJsonTo'):
        assert body == previous[expected['equalJsonTo']]


def main():
    index=json.loads((HERE/'index.json').read_text())
    assert {r['path'] for r in index['files']}=={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p.name!='index.json'}
    for r in index['files']:
        b=(HERE/r['path']).read_bytes();assert sha(b)==r['sha256'] and len(b)==r['bytes']
    manifest=json.loads((HERE/'evidence-index.json').read_text());z=(HERE/'evidence.json.gz').read_bytes()
    assert sha(z)==manifest['bundle']['sha256'] and len(z)==manifest['bundle']['bytes']
    expanded=gzip.decompress(z);assert len(expanded)==manifest['expandedBytes']<30*1024**2
    blobs={h:base64.b64decode(b,validate=True) for h,b in json.loads(expanded)['blobs'].items()}
    assert len(blobs)==manifest['uniqueBlobs'] and all(sha(b)==h for h,b in blobs.items())
    rows={r['path']:r for r in manifest['files']};assert len(rows)==manifest['payloads']==len(manifest['files'])
    assert sum(r['bytes'] for r in rows.values())==manifest['bytes']
    assert all(not n.startswith('/') and '..' not in Path(n).parts for n in rows)
    assert all(len(blobs[r['sha256']])==r['bytes'] for r in rows.values())
    def raw(n):return blobs[rows[n]['sha256']]
    def read(n):return json.loads(raw(n))
    def ref(r):
        names=[n for n,v in rows.items() if v['origin']==r['path']];assert names,r['path']
        for n in names:assert rows[n]['sha256']==r['sha256'] and rows[n]['bytes']==r['bytes']
        return raw(names[0])
    registry=read('root/cohort.json');assert sha(raw('root/cohort.json'))=='c185f2f86d84d22e00fa80459ffea310215e9f030edd406660ad8f7252760fd1'
    final=read('root/final-audit.json');review=json.loads((HERE/'review.json').read_text())
    expected_ids=['p1-stock','p1-native','p2-native','p2-stock','p3-stock','p3-native']
    assert [m['id'] for m in registry['members']]==expected_ids and len({m['runId'] for m in registry['members']})==6
    assert [m['memberId'] for m in final['members']]==expected_ids
    assert final['cohort']['sha256']==sha(raw('root/cohort.json'))
    assert final['plannedMembers']==final['completedMembers']==6
    assert final['lastMemberExplicitlyAudited'] is final['allSixSafetyAndProtectionAudited'] is True
    assert final['state']=='COHORT_COMPLETE_STRICT_GATE_FAILED_V1' and final['strictCohortGatePassed'] is False
    assert final['retries']==0 and final['failuresFiltered'] is False
    assert final['earlierV5AbortUnresolved'] is True and final['generalReliabilityOrCauseOrProductionPromotionClaimed'] is False
    assert ref(registry['launcher'])==raw('root/launch-member.py')
    assert ref(registry['prerequisiteReviewIndex'])==raw('prerequisite/index.json')
    assert registry['minimumFreeBytes']==1073741824
    # A separately sealed positive first pair remains a prerequisite, not two more cohort samples.
    assert review['prerequisiteFirstPairSeparateNotPooled'] is True
    for family in {n.split('/')[1] for n in rows if n.startswith('sources/')}:
        prefix='sources/'+family+'/';j=read(prefix+'index.json')
        assert {n.removeprefix(prefix) for n in rows if n.startswith(prefix)}=={'index.json'}|{r['path'] for r in j['files']}
        for r in j['files']:assert sha(raw(prefix+r['path']))==r['sha256'] and len(raw(prefix+r['path']))==r['bytes']
    spec=read('bindings/fixture-contract.json');requests={r['id']:r for r in spec['requests']};assert len(requests)==23
    pins=read('sources/browser-hydration-candidate-v3/asset-pins.json')['assets']
    totals={'http':0,'browserFunctions':0,'strict':0,'stock':0,'native':0};codes=[];failed=[];assets_by_member={};cdp_counts={}
    for ordinal,m in enumerate(registry['members']):
        mid=m['id'];arm=m['arm'];prefix='members/'+mid+'/';result=read(prefix+'actual/result.json')
        client=result if arm=='stock' else read(prefix+'actual/client/result.json')
        base=prefix+'actual/' if arm=='stock' else prefix+'actual/client/'
        authority=read(prefix+'authority.json');assert ref(m['authority'])==raw(prefix+'authority.json')
        observation=read(prefix+'monitor/observation.json');terminal=read(prefix+'monitor/terminal.json');started=read(prefix+'monitor/started.json')
        assert clean(terminal, 1 if mid=='p3-stock' else 0)
        assert type(terminal['rawExitCode']) is int and terminal['rawExitCode'] in (0,1)
        code=terminal['rawExitCode'];codes.append(code)
        assert code==observation['rawExitCode'] and started['authority']==terminal['authority']==m['authority']
        actor_root=Path(authority['sourceIndex']['path']).parent
        if arm=='stock':
            actor_plan=read('sources/browser-hydration-matched-host-candidate-v4/plans.json')
            child_argv=[actor_plan['node']['path'],str(actor_root/'run-stock.mjs'),m['outputRoot'],actor_plan['standaloneSource'],actor_plan['browserTools'],m['runId']]
        else:
            actor_plan=read('sources/wasmtime-deployment-candidate-v7/plan.json')
            child_argv=[actor_plan['node']['path'],str(actor_root/'deploy.mjs'),m['authority']['path']]
        assert started['argv']==child_argv and started['timeoutSeconds']==(300 if arm=='stock' else 600)
        assert started['pid']==terminal['pid'] and observation['protectedInputsPreserved'] is observation['ownedGroupsClean'] is True
        assert ref(observation['terminal'])==raw(prefix+'monitor/terminal.json')
        assert ref(terminal['stdout'])==raw(prefix+'monitor/stdout.log') and ref(terminal['stderr'])==raw(prefix+'monitor/stderr.log')
        assert ref(observation['result'])==raw(prefix+'actual/result.json')
        owned=[read(n) for n in rows if n.startswith(prefix+'monitor/owned-')]
        assert sorted(x['sequence'] for x in owned)==list(range(len(owned)))
        assert {json.dumps(x['process'],sort_keys=True) for x in owned}=={json.dumps(x,sort_keys=True) for x in terminal['observedProcesses']}
        admission=read(prefix+'launcher/admission.json');done=read(prefix+'launcher/cli-result.json')
        assert admission['member']==m and admission['cohort']==final['cohort'] and admission['launcher']==registry['launcher']
        assert admission['oneCommandOnly'] is True and admission['automaticNextOrRetry'] is False
        assert admission['freeBytesAtAdmission']>=admission['minimumFreeBytes']==registry['minimumFreeBytes']
        assert [x['id'] for x in admission['preceding']]==expected_ids[:ordinal]
        assert [x['rawExitCode'] for x in admission['preceding']]==codes[:-1]
        assert all(type(x['rawExitCode']) is int and x['functionalPassed'] is (x['rawExitCode']==0) and x['safeRecordedCompletion'] is True for x in admission['preceding'])
        assert admission['functionalFailuresNotPromoted'] is True
        for preceding_ref in admission['precedingRecords']:ref(preceding_ref)
        assert done['memberId']==mid and done['rawCliExitCode']==code and done['error'] is None
        assert done['registrySharedAndPriorRecordsPreserved'] is done['functionalPassNotInferred'] is True
        assert done['automaticNextOrRetry'] is False
        assert ref(done['stdout'])==raw(prefix+'launcher/cli.stdout.log') and ref(done['stderr'])==raw(prefix+'launcher/cli.stderr.log')
        assert result['passed'] is (code==0) and client['passed'] is (code==0)
        if arm=='stock':assert result['originalApplicationInputsPreserved'] is True and result['guestExecuted'] is False
        else:
            assert result['originalInputsPreserved'] is result['readonlyAppPreserved'] is True and result['errors']==[]
            assert result['server']['exit']==dict(code=0,signal=None,error=None) and result['server']['forcedCleanup'] is False
            assert result['server']['sigintSent'] is result['server']['shutdownRequested'] is True
            assert result['component']==authority['component'] and result['component']['sha256']=='1c3108d2fdce72a1bfa8cc64a0e6e0645acd71223b26b6dc11d037d4a95efe83'
            world=read(prefix+'world-guard.json');assert world['before']==world['after']
            assert world['unchanged'] is world['nativeInputsPreserved'] is True and world['authority']==m['authority']
            assert world['before']['members']==28 and world['before']['witFiles']==8
            assert world['before']['sourceIndex']==authority['worldSourceIndex']
        assert client['errors']==client['transportErrors']==[] and len(client['http'])==24 and all(r['passed'] for r in client['http'])
        assert [r['id'] for r in client['http']]==list(requests)+['server-action-submit']
        previous={}
        for r in client['http']:
            b=raw(base+'responses/'+r['id']+'.txt');assert sha(b)==r['bodySha256'] and len(b)==r['bodyBytes']
            if r['id'] in requests:contract(r,b,requests[r['id']],previous)
            else:assert r['status']==303 and r['headers']['location']=='/action-result?value=fixture-action'
            previous[r['id']]=b
        assert client['cacheInvalidation']['passed'] is True
        assert client['cacheInvalidation']['before']['generation']==1 and client['cacheInvalidation']['after']['generation']==2
        chunks=read(base+'stream-chunks.json');decoder=codecs.getincrementaldecoder('utf8')();text='';shell=ready=-1
        for i,c in enumerate(chunks):
            b=base64.b64decode(c['base64'],validate=True);assert len(b)==c['bytes'];text+=decoder.decode(b)
            if shell<0 and 'NEXT_STREAM_SHELL' in text:shell=i
            if ready<0 and 'NEXT_STREAM_READY' in text:ready=i
        text+=decoder.decode(b'',final=True);assert len(chunks)==5 and shell==0 and ready==2
        browser=client['browser'];assert browser==read(base+'browser/result.json')
        assert browser['functionalPassed'] is browser['browserClosed'] is True and browser['pageerrors']==browser['consoleerrors']==[]
        assert browser['perTestTimeoutMs']==20000 and browser['responseCaptureDrainBeforeCloseLimitMs']==500 and browser['responseFinishedDrainAfterCloseLimitMs']==2000
        assert len(browser['tests'])==2 and all(t['passed'] is True and t['timedOut'] is False and t['error'] is None for t in browser['tests'])
        assert all(t['captureDrainBeforeCloseComplete'] is True and t['cdpObserver']['stopped'] is False for t in browser['tests'])
        for t in browser['tests']:assert ref(t['screenshot']).startswith(b'\x89PNG\r\n\x1a\n')
        assert len(browser['assetBodies'])==9 and len(browser['bodyCaptures'])==10
        assetmap={}
        for asset in browser['assetBodies']:
            assert asset['sourceMatch'] is True and asset['status']==200
            assert ref(asset['decodedBody']) and sha(ref(asset['decodedBody']))==asset['decodedSha256']
            assetmap[(asset['test'],urlsplit(asset['url']).path)]=(asset['decodedSha256'],asset['decodedBytes'])
        assert all(assetmap[('client-counter',p['path'])]==(p['sha256'],p['bytes']) for p in pins);assets_by_member[mid]=assetmap
        post=next(x for x in browser['bodyCaptures'] if x['method']=='POST')
        events=browser['cdpEvents'];cdp_counts[mid]=len(events);assert all(x['identityProved'] is False for x in browser['cdpCorrelations'])
        assert len(events)==sum(t['cdpObserver']['events'] for t in browser['tests'])
        request=next(x for x in events if x['test']=='server-action' and x['event']=='Network.requestWillBeSent' and x['payload']['request']['method']=='POST')
        event_id=request['payload']['requestId'];transport=[x for x in events if x['test']=='server-action' and x['payload'].get('requestId')==event_id]
        errors=[x for x in transport if x['event']=='Network.loadingFailed'];finishes=[x for x in transport if x['event']=='Network.loadingFinished']
        assert sum(x['payload']['dataLength'] for x in transport if x['event']=='Network.dataReceived')==2963
        if mid=='p3-stock':
            assert code==1 and browser['passed'] is browser['browserErrorFree'] is False
            assert len(browser['failedrequests'])==1 and browser['failedrequests'][0]['requestId']==7
            assert browser['failedrequests'][0]['failure']['errorText']=='net::ERR_ABORTED'
            assert [x['stage'] for x in browser['errors']]==['server-action-response-body','server-action-response-finished','server-action-request-sizes']
            assert post['decodedBody'] is post['encodedSizes'] is None
            assert post['bodyCompletion']['kind']==post['sizesCompletion']['kind']=='requestfailed'
            assert len(errors)==1 and errors[0]['payload']['errorText']=='net::ERR_ABORTED' and errors[0]['payload']['canceled'] is True and finishes==[]
            close=next(x for x in browser['trace'] if x['test']=='server-action' and x['event']=='phase' and x['phase']=='context-close-start')
            failure=browser['failedrequests'][0];assert int(failure['ns'])<int(close['ns'])
            failed.append(mid)
        else:
            assert code==0 and browser['passed'] is browser['browserErrorFree'] is True
            assert browser['errors']==browser['failedrequests']==[] and errors==[] and len(finishes)==1
            assert post['bodyCompletion']['kind']==post['sizesCompletion']['kind']=='fulfilled' and len(ref(post['decodedBody']))==2963
        for capture in browser['bodyCaptures']:
            if capture['decodedBody'] is not None:assert len(ref(capture['decodedBody']))==capture['decodedBytes'] and sha(ref(capture['decodedBody']))==capture['decodedSha256']
        totals['http']+=24;totals['browserFunctions']+=2;totals['strict']+=int(code==0);totals[arm]+=int(code==0)
        fr=final['members'][ordinal];assert fr['memberId']==mid and fr['status']['rawExitCode']==code and fr['status']['functionalPassed'] is (code==0) and fr['status']['safeRecordedCompletion'] is True
        assert ref(fr['result'])==raw(prefix+'actual/result.json')
        for proof in fr['proofRecords']:ref(proof)
    assert codes==review['rawCodes']==[0,0,0,0,1,0] and failed==final['failedMembers']==review['failedMembers']==['p3-stock']
    assert totals==dict(http=144,browserFunctions=12,strict=5,stock=2,native=3)
    assert final['httpPassed']==final['httpTotal']==144 and final['browserFunctionalPassed']==final['browserFunctionalTotal']==12
    assert final['strictPassedRuns']==5 and final['strictFailedRuns']==1 and final['stockStrictPassed']==2 and final['nativeStrictPassed']==3
    assert review['dataValidationPassed'] is True and review['strictCohortGatePassed'] is False and review['curatorExecutedActorsOrRetry'] is False
    assert review['generalReliabilityOrCauseClaimed'] is review['adoption'] is False and review['earlierV5AbortUnresolved'] is True
    assert all(x==assets_by_member['p1-stock'] for x in assets_by_member.values())
    audit=json.loads((HERE/'current-copy-audit.json').read_text())['members']
    assert set(audit)=={'shared-source',*expected_ids}
    for mid,a in audit.items():
        assert a['listedFilesHashed']==2181 and a['listedBytes']==48714867 and a['listedBytesModesAndPhysicalPolicyMatched'] is True
        if a['arm']=='native':assert a['directoriesIncludingRoot']==427 and a['extraFiles']==[] and a['extraDirectories']==['.next/cache']
        elif a['arm']=='stock':assert a['directoriesIncludingRoot']==455 and len(a['extraFiles'])==37
        else:assert a['directoriesIncludingRoot']==426 and a['extraFiles']==[]
    originals=json.loads((HERE/'final-originals-check.json').read_text())
    assert originals['evidenceIndex']==dict(sha256=sha((HERE/'evidence-index.json').read_bytes()),bytes=(HERE/'evidence-index.json').stat().st_size)
    assert originals['logicalRowsRehashed']==580 and originals['uniqueOriginalFilesRehashed']==570
    assert originals['allCapturedOriginalBytesAndHashesUnchanged'] is originals['sourceFamilyMembershipRechecked'] is True
    assert originals['runtimeActorsOrRetriesExecuted'] is False and len(originals['sourceFamilies'])==6
    print(json.dumps(dict(dataValidated=True,plannedMembers=6,completedMembers=6,rawCodes=codes,
                         httpPassed=144,browserFunctionalPassed=12,strictPassedRuns=5,strictFailedRuns=1,
                         strictCohortGatePassed=False,failedMembers=failed,stockStrictPassed=2,nativeStrictPassed=3,
                         cdpEvents=cdp_counts,retainedPayloads=manifest['payloads'],privateOriginalsRequired=False,
                         actorOrRetryExecutedByReader=False,earlierAbortCauseUnresolved=True,adoption=False)))


if __name__=='__main__':main()
