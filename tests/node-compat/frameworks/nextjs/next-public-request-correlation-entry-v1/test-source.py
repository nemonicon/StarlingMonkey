"""Own Source/text/JSON/AST + independent public-metadata/bound models; never executes JS."""
from pathlib import Path
import ast
import hashlib
import json
import re
import stat

HERE=Path(__file__).resolve().parent
HEADER='x-next-public-request-correlation'
SAFE=9007199254740991


def row(path):
    before=path.lstat()
    assert path.resolve()==path and stat.S_ISREG(before.st_mode) and before.st_nlink==1
    raw=path.read_bytes();after=path.lstat()
    for name in ('st_dev','st_ino','st_mode','st_nlink','st_size','st_mtime_ns','st_ctime_ns'):
        assert getattr(before,name)==getattr(after,name)
    return dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))


def model_snapshot(count,value,shape=True):
    # Independent declared-record classification model, not JavaScript evaluation.
    count=min(2,count)
    if count==2:return dict(corrState='duplicate',corr=None,corrCount=2)
    if not shape:return dict(corrState='invalid',corr=None,corrCount=count)
    if count==0:return dict(corrState='missing' if value is None else 'invalid',corr=None,corrCount=0)
    valid=isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value) is not None
    return dict(corrState='valid' if valid else 'invalid',corr=value if valid else None,corrCount=1)


def model_classic(headers,raw):
    value=headers.get(HEADER) if isinstance(headers,dict) else None
    count=0;shape=isinstance(raw,list)
    if shape:
        shape=len(raw)%2==0
        for name in raw[::2]:
            if not isinstance(name,str):shape=False
            if isinstance(name,str) and len(name)==33 and name.lower()==HEADER:count=min(2,count+1)
    return model_snapshot(count,value,shape)


def main():
    checks=0
    def check(value):
        nonlocal checks
        assert value
        checks+=1
    read=lambda p:json.loads(p.read_bytes())
    plan,contract,derivation=map(lambda n:read(HERE/n),['plan.json','marker-contract.json','derivation.json'])
    base=Path(plan['baseEntry']['path']);before=base.read_text();after=(HERE/'guest-entry.mjs').read_text()
    for ref in [plan['baseSourceIndex'],plan['baseEntry'],plan['entry'],plan['markerContract'],plan['reviewedCorrelationProposal']]:check(row(Path(ref['path']))==ref)
    rendered=before
    for change in contract['entryReplacements']:
        check(rendered.count(change['before'])==1)
        rendered=rendered.replace(change['before'],change['after'],1)
    check(rendered==after and len(contract['entryReplacements'])==10)
    reversed_text=after
    for change in reversed(contract['entryReplacements']):
        check(reversed_text.count(change['after'])==1)
        reversed_text=reversed_text.replace(change['after'],change['before'],1)
    check(reversed_text==before)
    boundary='// Production-shaped guest adapter.'
    check(after.split(boundary)[0]==before.split(boundary)[0])
    for text in ['await ','.getReader(','.getWriter(','.blockingRead(','.blockingWriteAndFlush(',
                 'incoming.headers()','fieldResource.entries()','headers.append(name,text(value))',
                 'drop(fieldResource)','return handler.handle(incoming,outparam);','return requestHandler(req,res);']:
        check(after.count(text)==before.count(text))
    check('completionHolder' not in after and 'NEXT_GUEST_PROMISE_COMPLETION' not in after)
    check("res.once('error'" not in after and "res.on('error'" not in after)
    check(after.count("marker:'NEXT_GUEST_RESPONSE_COMPLETION_V2',version:2")==3)
    check('NEXT_GUEST_RESPONSE_COMPLETION_V1' not in after)
    check("guestCorrelationRequest(request,correlationCount)" in after)
    check("guestCorrelationClassic(req)" in after)
    check("request.headers.get('x-next-public-request-correlation')" in after)
    check("ownData(request,'headers'),raw=ownData(request,'rawHeaders')" in after)
    check("const name=ownData(raw,String(i));" in after)
    check("corrState:trace.corrState,corr:trace.corr,corrCount:trace.corrCount" in after)
    check(contract['marker']=='NEXT_GUEST_RESPONSE_COMPLETION_V2' and contract['version']==2)
    check(plan['entry']==row(HERE/'guest-entry.mjs') and plan['fixtureSelection']['entryMember']=='guest-entry.mjs')
    check(plan['fixtureSelection']['indexPublished'] is False and not (HERE/'index.json').exists())
    base_plan=read(Path(plan['baseSourceIndex']['path']).parent/'plan.json')
    for key in ['worldSourceIndex','witDirectory','worldName','witInputs','selectedInterfaces','componentExports','facadeReferences',
                'requiredEngine','requiredNativeMetadata','requiredFullNativeBuildReview','requiredCleanupSourceIndex',
                'requiredCompiledRequestResponse','requiredCompiledModuleLoader','requiredCurrentInteropRuntimeReview']:
        check(plan[key]==base_plan[key])
    check(plan['worldSourceIndex']['sha256']=='802595f5a32dd93fc95c63eb95c901352ecb8da180152735982c344d6b827f58')
    check(Path(plan['worldSourceIndex']['path']).parent==Path(plan['witDirectory']))
    check(len(plan['selectedInterfaces'])==len(set(plan['selectedInterfaces']))==13)
    check(plan['componentExports']==['wasi:http/incoming-handler@0.2.10'])
    for ref in plan['facadeReferences']+plan['witInputs']:
        check(row(Path(ref['path']))==ref)
    for key in ['requiredCompiledRequestResponse','requiredCompiledModuleLoader','requiredCleanupSourceIndex',
                'requiredFullNativeBuildReview','requiredCurrentInteropRuntimeReview','ancestorConstructionReviewForCurrentIntegration']:
        check(row(Path(plan[key]['path']))==plan[key])
    for key in ['actualEngine','actualNativeMetadata','actualRootAuthority','actualConstructor','actualComponent','actualImportFunctionCount',
                'actualRuntime','actualNonceManifest','actualConstructorReview','actualRuntimeActorIndex','actualRuntimeResult','actualCorrelationReview']:
        check(plan[key] is None)
    check(plan['publicRequestCorrelation']['headerName']==HEADER)
    check(plan['guestAddsOrChangesRequestHeaders'] is False and plan['futureBrowserHeaderDiagnosticInput'] is True)
    check(plan['futureManifestSchema']['nonceByTestKeys']==['client-counter','server-action'])
    check(plan['futureManifestSchema']['actualManifest'] is None)
    token='0123456789abcdef'*4
    cases=[(0,None,True,'missing',None,0),(0,token,True,'invalid',None,0),
        (1,token,True,'valid',token,1),(1,'A'*64,True,'invalid',None,1),
        (1,'a'*63,True,'invalid',None,1),(1,'a'*65,True,'invalid',None,1),
        (1,'a'*63+'\n',True,'invalid',None,1),(1,'a'*64+'\n',True,'invalid',None,1),
        (1,token+', '+token,True,'invalid',None,1),(1,' '+token,True,'invalid',None,1),
        (1,None,True,'invalid',None,1),(1,False,True,'invalid',None,1),
        (1,0,True,'invalid',None,1),(1,[],True,'invalid',None,1),
        (1,{},True,'invalid',None,1),(1,token,False,'invalid',None,1),
        (0,None,False,'invalid',None,0),(2,token,True,'duplicate',None,2),
        (2,None,False,'duplicate',None,2),(99,'untrusted',True,'duplicate',None,2)]
    modeled=[]
    for count,value,shape,state,corr,n in cases:
        observed=model_snapshot(count,value,shape)
        check(observed==dict(corrState=state,corr=corr,corrCount=n))
        check(observed['corr'] is None or re.fullmatch('[0-9a-f]{64}',observed['corr']) is not None)
        modeled.append(observed)
    classic_cases=[({},[],'missing',0),({HEADER:token},[HEADER,token],'valid',1),
        ({HEADER:token},[HEADER.upper(),token],'valid',1),
        ({HEADER:token},[HEADER,token,HEADER.upper(),token],'duplicate',2),
        ({HEADER:token+', '+token},[HEADER,token+', '+token],'invalid',1),
        ({},[HEADER,token],'invalid',1),({HEADER.upper():token},[HEADER,token],'invalid',1),
        ({HEADER:token},None,'invalid',0),({HEADER:token},[HEADER],'invalid',1),
        ({HEADER:token},[None,'x',HEADER,token],'invalid',1)]
    for headers,raw,state,count in classic_cases:
        observed=model_classic(headers,raw)
        check(observed['corrState']==state and observed['corrCount']==count)
    # Conservative independent schema envelope arithmetic; no JavaScript logger runs.
    maximum=0
    for method,path in [('GET','/actions'),('POST','/actions'),('GET','/action-result')]:
        for corr in modeled:
            for event,phase in [('output-child-dispose-returned','output-child-dispose'),('adapter-catch','outgoing-body-finish')]:
                frame=dict(marker=contract['marker'],version=2,sequence=255,lane='adapter',token=SAFE,method=method,path=path,
                    event=event,phase=phase,readBytes=SAFE,readChunks=SAFE,flags=7,**corr,caughtType='undefined')
                encoded=json.dumps(frame,separators=(',',':'),ensure_ascii=True).encode('ascii')+b'\n'
                maximum=max(maximum,len(encoded));check(len(encoded)<=512)
    for attempts in [0,1,254,255,256,257,1000]:check(min(attempts,255)+int(attempts>255)<=256)
    for name in ['test-source.py']:ast.parse((HERE/name).read_text());check(True)
    print(json.dumps(dict(state='PUBLIC_CORRELATION_SOURCE_AND_INDEPENDENT_MODEL_CHECKS_PASSED_V1',passed=True,
        checks=checks,classificationModelCases=len(cases),classicModelCases=len(classic_cases),artificialMaximumNormalFrameBytes=maximum,
        scope='Own Python Source/text/JSON/AST and independent declared classification/envelope models only; not JS/API/runtime behavior.',
        javaScriptNodeHelperGuardApiConstructorOrTargetExecuted=False,oldAnalyzerExecuted=False,
        nativeBinaryPayloadHashed=False,actualNewComponent=None,actualCorrelationObserved=False)))


if __name__=='__main__':
    main()
