"""All real helper callers plus synthetic caller failure-control-flow models."""
from pathlib import Path
import copy,hashlib,itertools,json,os,re
HERE=Path(__file__).resolve().parent;OLD=HERE.parent/'ownership-secret-failure-candidate-v1';checks=0
def need(ok,label):
    global checks
    checks+=1
    if not ok:raise AssertionError(label)
def row(p):p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def save(name,v):
    with(HERE/name).open('xb')as f:f.write((json.dumps(v,indent=2)+'\n').encode());f.flush();os.fsync(f.fileno())
d=json.loads((HERE/'derivations.json').read_bytes());need(len(d['newEdits'])==2 and d['composedReversibleEdits']==13,'two-site thin correction over eleven held edits')
for f in d['files']:
    a=Path(f['parentAfterimage']['path']).read_text();b=Path(f['after']['path']).read_text();need(row(f['parentAfterimage']['path'])==f['parentAfterimage']and row(f['after']['path'])==f['after'],'actual source bytes')
    for e in[e for e in d['newEdits']if e['file']==f['path']]:need(a.count(e['before'])==1,'exact new forward edit');a=a.replace(e['before'],e['after'])
    need(a==b,'whole afterimage derives exactly from parent')
    for e in reversed([e for e in d['newEdits']if e['file']==f['path']]):need(b.count(e['after'])==1,'exact reverse edit');b=b.replace(e['after'],e['before'])
    need(b==Path(f['parentAfterimage']['path']).read_text(),'whole new reversal byte exact')
algorithm=HERE/'afterimages/builtins/web/crypto/crypto-algorithm.cpp';text=algorithm.read_text();old=(OLD/'afterimages/builtins/web/crypto/crypto-algorithm.cpp').read_text()
need(text.count('EVP_PKEY_get_bn_param(')==old.count('EVP_PKEY_get_bn_param(')==1 and text.count('get_owned_bn_param(pkey.get(),')==old.count('get_owned_bn_param(pkey.get(),')==15,'all held immediate BIGNUM adoptions retained')
for name in ['crypto-key.cpp','crypto-raii.h']:need((HERE/'afterimages/builtins/web/crypto'/name).read_bytes()==(OLD/'afterimages/builtins/web/crypto'/name).read_bytes(),'point owner and allocator/header bytes unchanged')
calls=list(re.finditer(r'auto \[([a-z_]+), ([a-z_]+)\] = to_bytes_expand\(cx, ([^;]+)\);',text));need(len(calls)==17,'all seventeen actual helper calls enumerated')
groups=[('ECDSA sign',0,2),('EC private',2,5),('EC public',5,7),('RSA private basic',7,10),('RSA private CRT',10,15),('RSA public',15,17)];inventory=[]
for label,start,end in groups:
    subset=calls[start:end];owners=[m.group(1)for m in subset]
    for j,m in enumerate(subset):
        owner,length=m.group(1,2);after=m.end();guard=text.index('if (!'+owner,after)if label=='ECDSA sign'else text.index('if (!'+owners[0],subset[-1].end())
        guard_end=text.index('\n  }',guard)+4 if label=='ECDSA sign'else text.index('return nullptr;',guard)+len('return nullptr;')
        need('JS_ReportOutOfMemory(cx);'in text[guard:guard_end]and'return nullptr;'in text[guard:guard_end],'every caller guard reports existing OOM and returns null')
        need(guard<text.index(owner+'.get()',after),'owner check precedes first pointer consumption')
        length_use=re.search(r'\b'+re.escape(length)+r'\b',text[after:]);need(length_use is not None and guard<after+length_use.start(),'owner check precedes first returned-length consumption')
        if label=='ECDSA sign':
            next_boundary=calls[start+j+1].start()if j==0 else text.index('size_t result_size',after)
            need(guard_end<next_boundary,'immediate r/s guard before next helper/allocation/length')
        else:need(all('!'+name in text[guard:guard_end]for name in owners),'existing collective guard covers whole caller group')
        inventory.append(dict(group=label,owner=owner,length=length,callLine=text.count('\n',0,m.start())+1,guardLine=text.count('\n',0,guard)+1,checkedBeforeConsumption=True,immediateBeforeNextAllocation=label=='ECDSA sign'))
need(len(inventory)==17,'complete finite actual caller inventory, not just changed helper')
cases=[];counterexamples=0
# Synthetic allocator results and source-derived basic blocks. No native
# pointer, OpenSSL, OOM hook, compiler execution or guest is involved here.
for width in [32,48,66]:
    for r_ok,s_ok,result_ok,arraybuffer_ok in itertools.product([False,True],repeat=4):
        events=['convert-r'];owners=[];freed=[];reported=0;returned=None;out=None
        if r_ok:owners.append('r')
        else:reported=1;returned='nullptr'
        if returned is None:
            events.append('convert-s')
            if s_ok:owners.append('s')
            else:reported=1;returned='nullptr'
        if returned is None:
            events.extend(['use-lengths','allocate-result'])
            if not result_ok:reported=1;returned='nullptr'
            else:
                owners.append('result');events.extend(['copy-r','copy-s','create-ArrayBuffer'])
                if arraybuffer_ok:out=b'\x11'*width+b'\x22'*width;returned='ArrayBuffer';owners.remove('result')
                else:returned='nullptr'
        freed=list(reversed(owners))
        if not r_ok:
            need(events==['convert-r']and reported==1 and returned=='nullptr','r failure stops before s helper and every later operation')
        elif not s_ok:
            need(events==['convert-r','convert-s']and reported==1 and returned=='nullptr'and freed==['r'],'s failure stops before length/result/copy and retires r')
        elif not result_ok:need(events==['convert-r','convert-s','use-lengths','allocate-result']and reported==1 and returned=='nullptr','existing downstream result allocation failure unchanged')
        elif arraybuffer_ok:need(returned=='ArrayBuffer'and out==b'\x11'*width+b'\x22'*width and len(out)==2*width,'successful byte ordering/length remains original concatenation')
        else:need(returned=='nullptr'and events[-1]=='create-ArrayBuffer'and set(freed)=={'r','s','result'},'existing downstream ArrayBuffer failure retains cleanup')
        if not(r_ok and s_ok):
            need(not any(x in events for x in ['use-lengths','allocate-result','copy-r','copy-s','create-ArrayBuffer']),'no continuation after either conversion failure')
            if result_ok:counterexamples+=1 # held caller would continue to allocate/copy
        need(len(freed)==len(set(freed)),'synthetic local owners retire once')
        cases.append(dict(width=width,rConversionWouldSucceed=r_ok,sConversionWouldSucceed=s_ok,downstreamResultAllocationWouldSucceed=result_ok,arrayBufferWouldSucceed=arraybuffer_ok,actualSyntheticEvents=events,returned=returned,oomReports=reported,freedOwners=freed,actualNativeFaultInvoked=False))
need(len(cases)==48 and counterexamples==18,'full caller matrix includes r-only,s-only,both configured failures,success and downstream failures')
save('caller-inventory.json',dict(schemaVersion=1,totalHelperCalls=17,consumerGroups=6,checkedBeforeConsumption=17,changedEcdsaCalls=2,unchangedCollectivelyCheckedCalls=15,calls=inventory,limitations='Unchanged groups may allocate remaining helper buffers before their existing collective check; all returned owners are checked before pointer/length use.'))
save('source-check-results.json',dict(schemaVersion=1,state='SECRET_FAILURE_V2_CALLER_SOURCE_MODELS_PASSED',checks=checks,newReversibleEdits=2,composedReversibleEdits=13,callerCases=48,heldCallerContinuationCounterexamples=18,allActualHelperCallSites=17,sourceHelperCallsCheckedBeforeConsumption=17,cases=cases,inheritedBnPointAndAllocationGuardBytesRetained=True,actualNativeAllocationFaultOrOomInvoked=False,ownerHelperCryptoGuestGcOrRuntimeActionsInvoked=False,securityCompleteClaim=False))
print(json.dumps(dict(sourceAndCallerModelsPassed=True,checks=checks,callerCases=48,allHelperSites=17,newReversals=2,composedReversals=13,actualFaultOrRuntimeInvoked=False)))
