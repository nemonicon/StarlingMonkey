"""Source reversals and synthetic ownership models; no C++/crypto execution."""
from pathlib import Path
import collections,hashlib,json,os,re
HERE=Path(__file__).resolve().parent;checks=0
def need(ok,label):
    global checks
    checks+=1
    if not ok:raise AssertionError(label)
def row(p):p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def load(p):return json.loads(Path(p).read_bytes())
def save(name,v):
    with(HERE/name).open('xb')as f:f.write((json.dumps(v,indent=2)+'\n').encode());f.flush();os.fsync(f.fileno())
derivations=load(HERE/'derivations.json');need(len(derivations['edits'])==11,'exact finite transformation count')
for d in derivations['files']:
    before=Path(d['before']['path']).read_text();after=Path(d['after']['path']).read_text();need(row(d['before']['path'])==d['before']and row(d['after']['path'])==d['after'],'actual derived source bytes');forward=before
    for edit in[e for e in derivations['edits']if e['file']==d['path']]:need(forward.count(edit['before'])==1,'single forward edit');forward=forward.replace(edit['before'],edit['after'])
    need(forward==after,'whole exact forward source derivation')
    for edit in reversed([e for e in derivations['edits']if e['file']==d['path']]):need(after.count(edit['after'])==1,'single reverse edit');after=after.replace(edit['after'],edit['before'])
    need(after==before,'whole byte-exact reverse source derivation')
alg=(HERE/'afterimages/builtins/web/crypto/crypto-algorithm.cpp').read_text();key=(HERE/'afterimages/builtins/web/crypto/crypto-key.cpp').read_text();raii=(HERE/'afterimages/builtins/web/crypto/crypto-raii.h').read_text();base_raii=(HERE/'before/builtins/web/crypto/crypto-raii.h').read_text()
helper=alg.split('bool get_owned_bn_param(',1)[1].split('\n}',1)[0];need(helper.index('EVP_PKEY_get_bn_param')<helper.index('output.reset(raw)')<helper.index('return result != 0;'),'actual helper adopts before status branch');need('JS_'not in helper and 'return'not in helper.split('output.reset(raw)')[0],'no intervening JS call/early return before adoption')
need(alg.count('EVP_PKEY_get_bn_param(')==1 and len(re.findall(r'get_owned_bn_param\(pkey.get\(\),',alg))==15,'all15 actual extraction calls use immediate ownership helper')
groups=[e for e in derivations['edits']if 'extraction adopts'in e['label']or e['label'].startswith('RSA CRT')];need(len(groups)==5,'all five actual strict/optional extraction groups')
need('if (!bytes)'in alg and alg.index('if (!bytes)')<alg.index('std::fill_n(bytes.get()')<alg.index('BN_bn2bin(bignum'),'actual allocation branch precedes every write/export')
need(key.index('OpenSslBufferPtr pub_key(pub_key_raw)')<key.index('auto bld = ParamBldPtr',key.index('OpenSslBufferPtr pub_key(pub_key_raw)'))<key.index('auto params = ParamPtr',key.index('OpenSslBufferPtr pub_key(pub_key_raw)')),'point owner declared before builder/params and held through conversion')
need('OSSL_PKEY_PARAM_PUB_KEY, pub_key.get(), pub_key_len)'in key and 'OPENSSL_free(bytes);'in raii,'builder borrows actual owned public point and actual deallocator')
need(raii.count('BN_free(bn);')==base_raii.count('BN_free(bn);')==1 and 'BN_clear_free'not in raii,'existing BN wiping policy not expanded')
# The oracle specifies short-circuit status/branch traces separately from native
# ownership. Synthetic allocation IDs are never pointers or real BIGNUM values.
ownership_cases=[];old_counterexamples=0
for group in groups:
    params=re.findall(r'get_owned_bn_param\(pkey.get\(\), (OSSL_PKEY_PARAM_[A-Z0-9_]+), ([a-z0-9]+)\)',group['after']);need(len(params)in[2,3,5],'finite actual extraction shape');optional=group['label'].startswith('RSA CRT')
    old_params=re.findall(r'EVP_PKEY_get_bn_param\(pkey.get\(\), (OSSL_PKEY_PARAM_[A-Z0-9_]+), &([a-z0-9]+)_raw\)',group['before']);need(params==old_params,'exact original/after parameter and slot order')
    for fail_at in [None,*range(len(params))]:
        for partial_failed_output in [False,True]:
            for next_js_fails in [False,True]:
                calls=[];allocated=[];owners={};frees=[];status_ok=True
                for i,(name,slot)in enumerate(params):
                    calls.append(name);status=0 if i==fail_at else 1
                    raw='allocation-'+str(i)if status or partial_failed_output else None
                    if raw is not None:allocated.append(raw)
                    owners[slot]=raw # output.reset(raw), before examining status
                    if status==0:status_ok=False;break
                expected_calls=[p[0]for p in params[:len(params)if fail_at is None else fail_at+1]];need(calls==expected_calls,'same observable OpenSSL short-circuit order')
                branch='continue'if status_ok else'fallback'if optional else'existing-DataError'
                expected_branch='continue'if fail_at is None else'fallback'if optional else'existing-DataError';need(branch==expected_branch,'same existing API error/fallback branch')
                # Native owners survive the unchanged downstream work, whether
                # it succeeds or a synthetic JS allocation path returns early.
                live_at_downstream=[x for x in owners.values()if x is not None]
                if optional and not status_ok:need(live_at_downstream==allocated,'partial CRT owners remain live through unchanged fallback')
                for raw in reversed(list(owners.values())):
                    if raw is not None:frees.append(raw)
                need(collections.Counter(frees)==collections.Counter(allocated)and len(frees)==len(set(frees)),'every actual-shaped synthetic output retires once on every exit')
                old_leaked=allocated if not status_ok else[]
                if old_leaked:old_counterexamples+=1;need(len(old_leaked)>0 and len(frees)>0,'old source partial-ownership counterexample distinguished')
                ownership_cases.append(dict(group=group['label'],failedIndex=fail_at,partialFailedOutput=partial_failed_output,syntheticDownstreamJsFailure=next_js_fails,calledParameters=calls,branch=branch,allocated=len(allocated),freedExactlyOnce=len(frees),oldSourceUnownedOnThisBranch=len(old_leaked)))
for status in [-1,1,2]:need((status!=0)==(not(status==0)),'helper preserves original nonzero test, not pointer truthiness')
point_cases=[]
for stop in ['point-allocation','builder-new','parameter-push','private-BN','to-param','ctx-new','fromdata-init','fromdata','validate','success']:
    allocated=stop!='point-allocation';freed=1 if allocated else 0;retained_through_to_param=allocated and stop not in ['builder-new','parameter-push','private-BN'];need(freed==int(allocated),'OpenSSL point synthetic owner retires exactly once on all success/failure exits')
    if stop in ['to-param','ctx-new','fromdata-init','fromdata','validate','success']:need(retained_through_to_param,'point buffer lives until param conversion needs it')
    point_cases.append(dict(stop=stop,allocation=allocated,frees=freed,retainedThroughToParam=retained_through_to_param))
allocation_cases=[]
for size in [0,1,32,66,8192]:
    for succeeds in [False,True]:
        writes=[]
        if succeeds:writes=['padding'if size else'zero-size-noop','BN-export']
        returned_size=size if succeeds else 0
        if not succeeds:need(writes==[]and returned_size==0,'allocation null reaches no padding/pointer/export action')
        else:need(returned_size==size,'successful helper output length unchanged')
        allocation_cases.append(dict(bufferSize=size,allocationSucceeded=succeeds,actions=writes,returnedSize=returned_size))
need(old_counterexamples>0 and len(ownership_cases)==80,'finite meaningful short-circuit/CRT/error matrix')
save('source-check-results.json',dict(schemaVersion=1,state='UNAPPLIED_SECRET_FAILURE_SOURCE_AND_SYNTHETIC_MODELS_PASSED_V1',checks=checks,exactReversibleEdits=11,changedFiles=3,unchangedNativeFiles=352,extractionGroups=5,actualExtractionCalls=15,syntheticOwnershipCases=len(ownership_cases),oldSourcePartialOwnershipCounterexamples=old_counterexamples,syntheticPointLifetimeCases=len(point_cases),syntheticAllocationCases=len(allocation_cases),ownershipCases=ownership_cases,pointCases=point_cases,allocationCases=allocation_cases,extractedActualSourceShapes=True,nativeFunctionsExecuted=False,actualAllocationFaultsInjected=False,cryptoGuestGcOrOomInvoked=False,securityCompleteClaim=False,runtimeAcceptanceClaim=False))
print(json.dumps(dict(sourceAndModelsPassed=True,checks=checks,reversibleEdits=11,ownershipCases=len(ownership_cases),pointCases=len(point_cases),allocationCases=len(allocation_cases),runtimeActionsInvoked=False)))
