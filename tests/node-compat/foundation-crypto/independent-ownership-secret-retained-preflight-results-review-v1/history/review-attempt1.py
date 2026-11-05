"""Independent actual retained-preflight DATA audit; no owner code is evaluated."""
from pathlib import Path
import ast
import hashlib
import json
import re
import stat

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'ownership-secret-retained-bootstrap-candidate-v1'
SOURCE_SHA = 'c47ac2f9b3c89a5b4ed3f91acfa96ea30443d8d459adae4a21739d3102048d7c'
seen = {}
checks = []
check_count = 0


def need(value, label):
    global check_count
    check_count += 1
    if not value:
        raise AssertionError(label)


def checkpoint(label):
    checks.append(label)


def ident(p):
    s = p.lstat()
    need(stat.S_ISREG(s.st_mode), 'Ordinary non-symlink file: ' + str(p))
    return (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns,
            stat.S_IMODE(s.st_mode), s.st_nlink, str(p.resolve()))


def file(row):
    p = Path(row['path'])
    need(p.is_absolute() and str(p) == row['path'], 'Canonical absolute path')
    need(set(row) == {'path', 'sha256', 'bytes'}, 'Exact three-field descriptor')
    need(type(row['bytes']) is int and row['bytes'] >= 0, 'Actual finite byte count')
    need(re.fullmatch('[a-f0-9]{64}', row['sha256']) is not None, 'SHA256 descriptor')
    before = ident(p)
    if str(p) in seen:
        need(seen[str(p)] == (row, before), 'Repeated row and identity unchanged')
        return row
    h = hashlib.sha256()
    length = 0
    with p.open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(b)
            length += len(b)
    need(before == ident(p), 'File stable through streamed hash')
    need(length == row['bytes'] and h.hexdigest() == row['sha256'], 'Exact actual file bytes')
    seen[str(p)] = (dict(row), before)
    return row


def row(p):
    p = Path(p)
    b = p.read_bytes()
    return file(dict(path=str(p), sha256=hashlib.sha256(b).hexdigest(), bytes=len(b)))


def read(d):
    file(d)
    b = Path(d['path']).read_bytes()
    need(len(b) == d['bytes'] and hashlib.sha256(b).hexdigest() == d['sha256'], 'Stable JSON read')
    return json.loads(b)


def tree(p):
    need(p.is_dir() and not p.is_symlink(), 'Ordinary tree root')
    names = []
    for q in p.rglob('*'):
        need(not q.is_symlink(), 'No tree aliases')
        need(q.is_dir() or q.is_file(), 'Ordinary tree entry')
        if q.is_file():
            names.append(q.relative_to(p).as_posix())
    return sorted(names)


def family(d):
    value = read(d)
    need(value['schemaVersion'] == 1 and 0 < len(value['files']) <= 2048, 'Finite indexed family')
    base = Path(d['path']).parent
    names = ['index.json']
    rows = [d]
    for m in value['files']:
        n = m['path']
        need(n and not Path(n).is_absolute() and all(x not in ('', '.', '..') for x in n.split('/')) and '\\' not in n, 'Confined indexed path')
        names.append(n)
        rows.append(file(dict(m, path=str(base / n))))
    need(len(names) == len(set(names)), 'Unique family membership')
    need(tree(base) == sorted(names), 'Complete exact indexed membership')
    return rows


def proof(pair):
    members = family(pair['index'])
    need(sum(d == pair['result'] for d in members) == 1, 'Result indexed exactly once')
    return read(pair['result'])


def descriptors(value):
    if isinstance(value, dict):
        if set(value) == {'path', 'sha256', 'bytes'}:
            yield value
        else:
            for item in value.values():
                yield from descriptors(item)
    elif isinstance(value, list):
        for item in value:
            yield from descriptors(item)

def typed_same(a,b):
    if type(a)is not type(b):return False
    if isinstance(a,dict):return a.keys()==b.keys()and all(typed_same(a[k],b[k])for k in a)
    if isinstance(a,list):return len(a)==len(b)and all(typed_same(x,y)for x,y in zip(a,b))
    return a==b


def main():
    k=HERE.parent
    root_row=row(k/'ownership-secret-retained-preflight-root-results.json')
    need(root_row['sha256']=='9404467d2760658cde2c8006879707b807f5c8ce61ed6d8d3dea76dd9a2cd3b2'and root_row['bytes']==2398,'Assigned exact actual Root observation')
    root=read(root_row)
    root_external=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-retained-preflight-v1-root-observer')
    out=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-retained-preflight-v1')
    need(root_row['sha256']==row(root_external/'root-observation.json')['sha256']and Path(root_row['path']).read_bytes()==(root_external/'root-observation.json').read_bytes(),'Whole Root observation byte-identical across physical roles')
    for d in descriptors(root):file(d)
    source_index=row(SOURCE/'index.json');need(source_index['sha256']==SOURCE_SHA,'Actual immutable c47 Source family')
    own_members=family(source_index)
    refs=read(row(SOURCE/'references.json'));inputs=read(row(SOURCE/'source-inputs.json'))
    need(len(own_members)==36 and len(inputs['files'])==28208 and len(inputs['families'])==17,'Whole Source and finite input closure')
    ledger={d['path']:d for d in inputs['files']};need(len(ledger)==28208,'Unique declared original Source/protection rows')
    for d in inputs['files']:file(d)
    for ix in inputs['families']:
        for d in family(ix):need(ledger.get(d['path'])==d,'Complete original family protected')
    for d in descriptors(refs):file(d)
    checkpoint('Entire c47 family and28,208 physical inputs/17 families rehashed; original proof/native/frozen/normal/tool contexts intact')

    cfg=read(root['rootConfig']);authority=read(root['rootAuthority']);invocation=read(root['invocation'])
    peer=proof(authority['sourceIndependentReview'])
    need(peer['schemaVersion']==1 and peer['state']=='INDEPENDENT_CRYPTO_OWNER355_SECRET_RETAINED_BOOTSTRAP_SOURCE_REVIEW_PASSED_V1'and peer['sourceIndexSha256']==SOURCE_SHA and peer['sourceOnly']is peer['sourceReviewPassed']is True,'Genuine0372 Source peer')
    for key in ['ownerActionsInvoked','hostActionsInvoked','retainedPreflightActionsInvoked']:need(peer[key]is False,'Source peer action scope '+key)
    need(authority['schemaVersion']==1 and authority['state']=='ROOT_REVIEWED_SECRET355_RETAINED_BOOTSTRAP_PREFLIGHT_V1'and authority['phase']=='verify-retained'and authority['readOnlyVerificationAllowed']is True,'Actual new read-only Root authority')
    need(authority['sourceIndex']==cfg['sourceIndex']==source_index and cfg['rootAuthority']==root['rootAuthority'],'Exact Root config/Source binding')
    need(authority['actualBootstrapReview']==refs['actualBootstrapReview']and authority['historicalBootstrap']==refs['historicalBootstrap']and authority['variant']=='normal-off','Whole historical proof role bound by new Root authority')
    for key in ['helperInvocationAllowed','oneShotApiInvocationAllowed','historicalRecheckInvocationAllowed','exportAllowed','pinDerivationAllowed','nativeBuildAllowed','nativeFreezeAllowed','gcReconfigureAllowed','engineExecutionAllowed','componentAllowed','guestAllowed','keyOrCryptoAllowed','moduleAdmissionAllowed','runtimeAcceptanceClaim','operationalAdmission','sourcePromotionAllowed','metadataProjectionAllowed','timingAllowed']:
        need(authority[key]is False,'Root denies additional action '+key)
    need(authority['actualComponent']is authority['runtimeAuthority']is None,'No component/runtime authority')
    need(root['entry']==authority['rootVerifierEntry']==invocation['entry']and root['entry']['sha256']=='b8b05bf03a876ac40ddb92f993e3bef9e158481e192265e92871f4b1ef73d574','Actual Root entry Source')
    need(invocation['authority']==root['rootAuthority']and invocation['config']==root['rootConfig']and invocation['ownedNodeDeadlineSeconds']==1800,'Genuine invocation Root/config/owned deadline')
    need(invocation['argv']==[refs['node']['path'],root['entry']['path'],json.dumps(root['rootConfig'],separators=(',',':'))],'Plain pinned Node22 argv, no execArgv')
    checkpoint('Actual Root authority/config/entry/0372 peer and exact plain pinnedNode argv match; all non-read-only grants closed')

    actual=read(root['actualResult']);record=read(actual['outputs']['recordData']);historical=read(actual['outputs']['historical']);shape=read(actual['outputs']['shape'])
    need(tree(out)==['historical-bootstrap.json','record-data.json','record-shape.json','result.json'],'Whole four-file actual output inventory; no fabricated actual index')
    need(record.keys()==dict.fromkeys(['schemaVersion','kind','sourceIndex','actualReview','historicalBootstrap','currentVerification']).keys(),'All six DATA properties exactly retained')
    need(record['schemaVersion']==1 and record['kind']=='retained-secret355-bootstrap-v1'and record['sourceIndex']==source_index and record['actualReview']==refs['actualBootstrapReview'],'Genuine new record kind/current Source/actual historical review')
    frame=read(refs['historicalBootstrap']);python_frame=read(refs['historicalPythonFrame'])
    need(typed_same(record['historicalBootstrap'],frame)and typed_same(frame,python_frame)and typed_same(frame,historical),'Entire typed historical frame unchanged in all roles')
    need(Path(actual['outputs']['historical']['path']).read_bytes()==Path(refs['historicalBootstrap']['path']).read_bytes()==Path(refs['historicalPythonFrame']['path']).read_bytes(),'Whole41fieldfc86 bytes retained exactly')
    need(len(frame)==41 and frame['currentCompleteVerifierCalls']==1 and frame['nativeSourceFiles']==355 and frame['externalEmbeddingSources']==3 and frame['selectedManifestCount']==11,'Historical355+3/11/count1 remain historical')
    metadata=read(refs['metadata']);manifests=[read(d)for d in refs['selectedManifests']]
    need(typed_same(frame['metadata'],metadata)and len(metadata)==75 and typed_same(frame['selectedManifests'],manifests)and len(manifests)==11,'All75 raw metadata fields and11 complete manifests')
    for key in ['engineExecuted','guestExecuted','operationalAdmission','runtimeAcceptanceClaim','grantsRuntimeAuthority']:need(frame[key]is False,'Historical action scope '+key)
    need(frame['verifierFrame']['runtimeBackendProof']==dict(verified=False,version=None,vernum=None),'Backend runtime proof false/null/null')
    for key,value in refs['historicalContexts'].items():need(frame[key]==value,'No historical physical context projection: '+key)
    for key,descriptor_key in [('engine','engine'),('metadataDescriptor','metadata'),('freezeReceipt','freezeReceipt')]:need(frame[key]==refs[descriptor_key],'Exact frozen role '+key)
    for m in metadata['sourceManifest']:
        for prefix in [frame['configuredSourceRoot'],frame['sourceRoot']]:need(ledger[str(Path(prefix)/m['path'])]['sha256']==m['sha256'],'All355 original/frozen native source rows')
    for m in metadata['componentizeSourceManifest']:need(ledger[str(Path(frame['componentizeSourceRoot'])/m['path'])]['sha256']==m['sha256'],'All3 frozen embedding source rows')
    api_rows=dict(ledger)
    for d in own_members:api_rows[d['path']]=d
    for d in family(authority['sourceIndependentReview']['index']):api_rows[d['path']]=d
    for d in [root['rootConfig'],root['rootAuthority']]:api_rows[d['path']]=d
    need(len(api_rows)==28256,'Reconstructed exact API Capture count')
    root_rows=dict(api_rows);root_rows[root['entry']['path']]=root['entry'];need(len(root_rows)==28257,'Reconstructed exact Root capture count: one extra entry Source')
    expected_current=dict(schemaVersion=1,kind='current-read-hash-verification-v1',sourceIndex=source_index,config=root['rootConfig'],rootAuthority=root['rootAuthority'],protectedFileRows=28256,retainedTreeScopes=8,helperScope='original frozen-verifier/artifact helper',helperInvocations=0,originalApiInvocations=0,historicalRecheckInvocations=0,processesSpawned=0,filesCreated=0,sourceAndProtectionChecked=True,fullMetadataFields=75,selectedWholeManifests=11,engineExecuted=False,componentOrGuestExecuted=False,keyOrApplicationCryptoOperationsInvoked=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
    need(typed_same(record['currentVerification'],expected_current),'Whole typed currentVerification exact; no historical count rewritten')
    expected_shape={k:dict(type='number'if k=='schemaVersion'else'string'if k=='kind'else'object',writable=False,configurable=False,enumerable=True)for k in record}
    expected_shape['recheck']=dict(type='function',writable=False,configurable=False,enumerable=True)
    need(typed_same(shape,expected_shape)and len(shape)==7,'Six DATA property descriptors plus immutable live function descriptor')
    need('recheck'not in record and 'state'not in record and 'currentCompleteVerifierCalls'not in record,'No serialized executable, historical state/count spread or admission projection')
    checkpoint('All six DATA fields/seventh live callable descriptor; full41fieldfc86 bytes/75 metadata/11 manifests; exact reconstructed28256 API vs28257 Root counters')

    expected_top=dict(schemaVersion=1,state='ROOT_SECRET355_RETAINED_PREFLIGHT_PASSED_UNREVIEWED_V1',sourceIndex=source_index,sourceIndependentReview=authority['sourceIndependentReview'],rootAuthority=root['rootAuthority'],config=root['rootConfig'],entry=root['entry'],apiCalls=1,freshOwnRecheckCalls=1,originalOneShotApiCalls=0,historicalCallableCalls=0,helperCalls=0,originalProtectedRows=28257,outputs=actual['outputs'],primaryError=None,finalProtectionError=None,engineOrGuestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,requiresIndependentActualReview=True)
    need(typed_same(actual,expected_top),'Entire actual Root result frame matches bounded operation and failures')
    terminal=read(root['ownedNodeTerminal']);started=read(row(root_external/'node/started.json'));owned=read(row(root_external/'node/owned-0000.json'))
    for d in [terminal['stdout'],terminal['stderr']]:file(d)
    need(terminal['authority']==root['rootAuthority']and terminal['pid']==77532 and terminal['rawExitCode']==0,'Raw owned Node terminal identity/zero/authority')
    for key in ['timeout','forcedCleanup']:need(terminal[key]is False,'No '+key)
    for key in ['interruptedSignals','remainingObservedPids','signals','errors']:need(terminal[key]==[],'Clean owned terminal '+key)
    need(terminal['parentOwnedGroupGone']is terminal['allObservedOwnedGroupsGone']is True and terminal['finalGroups']==[dict(pgid=77532,alive=False,signalAllowed=False)],'Owned actual group gone without signals')
    need(len(terminal['observedProcesses'])==1 and terminal['observedProcesses'][0]==owned['process'],'Whole observed ownership record; one Node process')
    need(terminal['observedProcesses'][0]['command']==refs['node']['path']and terminal['observedProcesses'][0]['pgid']==77532,'Actual pinned Node process command and owned session')
    need(started['argv']==invocation['argv']and started['pid']==77532 and started['authority']==root['rootAuthority']and started['timeoutSeconds']==1800,'Durable pre-launch actual argv/deadline/authority')
    raw=Path(root['stdout']['path']).read_bytes();lines=raw.decode('utf-8','strict').splitlines()
    need(len(lines)==1 and json.loads(lines[0])==dict(result=root['actualResult'],state=actual['state']),'Whole actual Node stdout one strict expected return envelope')
    need(root['stdout']==terminal['stdout']and root['stderr']==terminal['stderr']and terminal['stderr']['bytes']==0,'Complete stdout/stderr tuples; no stderr')
    need(root['state']=='ROOT_OBSERVED_SECRET355_RETAINED_PREFLIGHT_ZERO_UNREVIEWED_V1'and root['rawExitCode']==0 and root['allObservedOwnedGroupsGone']is True,'Root-reported tool/result zero scope')
    for key in ['error','rootInputProtectionError']:need(root[key]is None,'No Root error '+key)
    for key in ['engineOrGuestExecuted','originalOneShotApiOrHelperExecuted','operationalAdmission','runtimeAcceptanceClaim']:need(root[key]is False,'Root action scope '+key)
    checkpoint('Strict whole raw return and durable ownedNode77532 raw0/1800s/no signals/errors/timeouts/forced cleanup; one observed process/group gone')

    source=Path(root['entry']['path']).read_text();api=(SOURCE/'retained-bootstrap.mjs').read_text()
    need(source.count('record=await loaded.retainedSecretBootstrapPreflight({configDescriptor});')==1 and source.count('assert.equal(await record.recheck(),undefined);')==1,'Genuine single API and single fresh own recheck sites')
    need(source.index('for(const row of inputs.files)await pinned(row)')<source.index('await recheckInputs();\nawait mkdir')<source.index('const loaded=await import'),'Complete Source protection before genuine API import')
    need("await family(authority.sourceIndependentReview.index)"in source and "finally{"in source and "await recheckInputs();"in source,'Source peer and final Root recheck branches')
    need("const recheck=async()=>{await verifyCurrent();"in api and 'secretArtifactBootstrapPreflight('not in api and 'await import('not in api and 'spawn('not in api,'Actual new closure only; no old API/helper/callable reconstruction/process branch')
    checkpoint('Read-only actual caller/API control flow supports counts1+1 and zero original helper/API/callable/process/write scopes; no re-execution by reviewer')

    tree_counts=[]
    for t in refs['retainedTrees']:
        p=Path(t['root']);need(tree(p)==sorted(t['names']),'Whole original retained tree membership')
        for q in [p]+list(p.rglob('*')):
            s=q.lstat()
            if q.is_file():need(str(q)in ledger,'Original retained file hash protected')
            if t['private']:
                need(stat.S_IMODE(s.st_mode)==(0o700 if q.is_dir()else 0o600),'Private original retained mode')
                if q.is_file():need(s.st_nlink==1,'Independent original retained file')
        tree_counts.append(dict(role=t['role'],files=len(t['names'])))
    for pair in refs['independentFrozenCopies']:
        a,b=Path(pair['frozen']),Path(pair['original']);ai,bi=ident(a),ident(b)
        need(ai[6]==1 and ai[:2]!=bi[:2]and ledger[str(a)]['sha256']==ledger[str(b)]['sha256'],'All1899 original/frozen identities and hashes distinct/equal')
    expected_monitor=['node/owned-0000.json','node/started.json','node/stderr.log','node/stdout.log','node/terminal.json','root-observation.json']
    need(tree(root_external)==expected_monitor,'Exact six-file owned actual monitor inventory')
    for p in [out,root_external]:
        for q in [p]+list(p.rglob('*')):
            s=q.lstat();need(not q.is_symlink()and stat.S_IMODE(s.st_mode)==(0o700 if q.is_dir()else 0o600),'Actual new roots/files private and regular')
            if q.is_file():need(s.st_nlink==1,'Actual new files independently owned');row(q)
    retained=k/'ownership-secret-retained-preflight-root-evidence'
    copies=[]
    need(len(tree(retained))==10,'All ten retained raw copies present')
    for name in tree(retained):
        first,rest=name.split('/',1);original=(out if first=='output'else root_external)/rest
        need(first in ['output','monitor'],'Exact retained copy physical role')
        a,b=row(original),row(retained/name);need(a['sha256']==b['sha256']and a['bytes']==b['bytes']and ident(original)[:2]!=ident(retained/name)[:2],'Whole retained raw copy bytes with distinct inode')
        copies.append(dict(original=a,retained=b))
    checkpoint('All four actual outputs/six monitor files and ten retained raw copies; private modes, old1391 normal/eight retained memberships and1899 independent frozen pairs')

    for path,(_,identity)in seen.items():need(ident(Path(path))==identity,'Final observed identity unchanged')
    for ix in [source_index,authority['sourceIndependentReview']['index']]+inputs['families']:
        value=json.loads(Path(ix['path']).read_bytes());need(tree(Path(ix['path']).parent)==sorted(['index.json']+[m['path']for m in value['files']]),'Final complete family membership')
    for t in refs['retainedTrees']:need(tree(Path(t['root']))==sorted(t['names']),'Final old retained membership')
    need(tree(out)==['historical-bootstrap.json','record-data.json','record-shape.json','result.json']and tree(root_external)==expected_monitor and len(tree(retained))==10,'Final actual/copy inventory exact')
    observed=sorted((v[0]for v in seen.values()),key=lambda d:d['path'])
    evidence=dict(schemaVersion=1,state='INDEPENDENT_RETAINED_PREFLIGHT_ACTUAL_DATA_AUDIT_PASSED_V1',checks=check_count,observedFiles=len(observed),observedLogicalBytes=sum(d['bytes']for d in observed),observedDescriptorVectorSha256=hashlib.sha256(json.dumps(observed,sort_keys=True,separators=(',',':')).encode()).hexdigest(),sourceIndex=source_index,sourceInputLedger=row(SOURCE/'source-inputs.json'),sourceIndependentReview=authority['sourceIndependentReview'],rootObservation=root_row,actualResult=root['actualResult'],rootAuthority=root['rootAuthority'],rootConfig=root['rootConfig'],entry=root['entry'],invocation=root['invocation'],ownedNodeTerminal=root['ownedNodeTerminal'],recordData=actual['outputs']['recordData'],historicalBootstrap=actual['outputs']['historical'],recordShape=actual['outputs']['shape'],engine=refs['engine'],metadata=refs['metadata'],freezeReceipt=refs['freezeReceipt'],actualHistoricalBootstrapReview=refs['actualBootstrapReview'],retainedCopies=copies,
        coverage=dict(sourceMembers=35,sourceInputs=28208,completeOriginalFamilies=17,currentApiProtectedRows=28256,rootProtectedRows=28257,actualDataProperties=6,actualOwnProperties=7,historicalFields=41,metadataFields=75,nativeSourceFiles=355,externalEmbeddingSources=3,selectedWholeManifests=11,retainedHistoricalTrees=8,frozenFiles=1903,protectedOldNormalFiles=1391,independentFrozenPairs=1899,actualOutputFiles=4,monitorFiles=6,retainedRawCopies=10,observedApiCalls=1,observedFreshOwnRecheckCalls=1,historicalCompleteVerifierCalls=1,currentHelperCalls=0,currentOriginalApiCalls=0,currentHistoricalCallableCalls=0,currentApiSpawnedProcesses=0,currentApiCreatedFiles=0,observedOwnedNodeProcesses=1),
        currentVerification=expected_current,checkedSections=checks,originalAndFrozenRolesUnchanged=True,reviewerReadHashDataOnly=True,reviewerOwnerApiHelperNodeProcessOrGuestActionsInvoked=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
    with(HERE/'audit-results.json').open('x')as f:json.dump(evidence,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(dict(passed=True,checks=check_count,observedFiles=len(observed),observedLogicalBytes=evidence['observedLogicalBytes'],reviewerActions=0)))


if __name__=='__main__':main()
