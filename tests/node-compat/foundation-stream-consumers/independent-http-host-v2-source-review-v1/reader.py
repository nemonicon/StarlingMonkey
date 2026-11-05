"""Independent finite source/caller/control-flow DATA review; no owner execution."""
from pathlib import Path
import ast,json,re,os
import review_io as I
HERE=Path(__file__).resolve().parent;S=HERE.parent;SOURCE=S/'http-host-candidate-v2';OLD=S/'http-host-candidate-v1';HOLD=S/'independent-http-host-source-review-v1'
SOURCE_SHA='9fc935f60bdfda0a0b4ee1a7552d05e0429dce7992957b05ba1dcc69380b0788'
def write(name,v):
    p=HERE/name
    with p.open('x')as f:json.dump(v,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def same(a,b):return json.dumps(a,sort_keys=True,separators=(',',':'))==json.dumps(b,sort_keys=True,separators=(',',':'))
def row(path):return I.descriptor(str(path))
def load(path):return I.read(row(path))
source_row=dict(path=str(SOURCE/'index.json'),sha256=SOURCE_SHA,bytes=4901)
source,source_members=I.indexed(source_row,'sealed HTTP host v2')
I.need(len(source_members)==31,'31 current source members')
old_row=dict(path=str(OLD/'index.json'),sha256='4b7c36f2d50e2c3bee831d7c4681b62bea67fb667e5da10f227125e3dd860e70',bytes=6608)
old,old_members=I.indexed(old_row,'immutable held HTTP host v1');I.need(len(old_members)==42,'all42 held source members')
hold_row=dict(path=str(HOLD/'index.json'),sha256='58ec38a3f2b5b3616c27e5f8b2e40a473d70546381597647d56a0bb66577c641',bytes=1624)
_,hold_members=I.indexed(hold_row,'immutable formal HTTP-HOST-M1 HOLD');I.need(len(hold_members)==10,'formal10 preserved')
correction=I.known(HOLD/'required-correction-contract.json','02dfd4eae68bb022e3f98bef46a113ee0824a6a1c8dea11a695e5e57f7ee9e03',2263)
I.need(correction['findingId']=='HTTP-HOST-M1'and correction['sourceOnly']is True and correction['grantsActionAuthority']is False,'bounded correction contract')
native_summary=I.known(HERE/'native-context/summary.json','b9d21eb5146b25628b3d01b360bc1c499f8e48252a35ef75e251ad1ad61eae37',4296)
native_ledger=I.known(HERE/'native-context/rehashed-inputs.json','513227c69fd095490bf149a3a98e5c499bca0e9a3a6a96026d8bea3e181c1c3d',17846354)
I.need(native_summary['blockers']==[]and native_ledger['ownerCodeExecuted']is False and native_ledger['allPhysicalFilesRehashedAtEnd']is True,'independent data subaudit scope')
for r in native_ledger['physicalFiles']:I.verify(r,'fresh parent verification of independent native physical ledger')
inputs=load(SOURCE/'source-inputs.json');I.need(len(inputs['files'])==12835,'all12835 source references')
for r in inputs['files']:I.verify(r,'current finite source input')
old_inputs=load(OLD/'source-inputs.json');I.need(len(old_inputs['files'])==12781,'original12781 contexts unchanged')
for r in old_inputs['files']:I.verify(r,'inherited original source input')
derivations=load(SOURCE/'source-derivations.json');I.need(len(derivations['files'])==5,'five thin afterimages');edit_count=0
for d in derivations['files']:
    origin=I.verify(d['origin'],'held original afterimage source').read_text();current=(SOURCE/d['afterimage']).read_text();generated=origin
    for e in d['edits']:
        I.need(generated.count(e['old'])==e['count']==1,'exact single forward edit');at=generated.index(e['old']);I.need(at==e['afterOffsetAtEdit'],'exact forward offset');generated=generated[:at]+e['new']+generated[at+len(e['old']):];edit_count+=1
    I.need(generated==current,'whole afterimage exactly derived')
    for e in reversed(d['edits']):
        at=e['afterOffsetAtEdit'];I.need(generated[at:at+len(e['new'])]==e['new'],'exact reverse offset');generated=generated[:at]+e['old']+generated[at+len(e['new']):]
    I.need(generated==origin,'whole reverse restores held bytes')
I.need(edit_count==26,'exact26 source transformations')
old_p=load(OLD/'prerequisites.json');p=load(SOURCE/'prerequisites.json');changed={k for k in set(old_p)|set(p)if not same(old_p.get(k),p.get(k))}
I.need(changed=={'hostSourceRoot','heldHostSourceIndex','sourceCheckpoint','inheritedPreparationInputFreeze','formalHold'},'only current context and explicit immutable source-history references change in prerequisites')
I.need(all(same(old_p[k],p[k])for k in old_p if k!='hostSourceRoot'),'all original prerequisite tuples/data unchanged')
I.need(same(p['heldHostSourceIndex'],old_row)and same(p['formalHold']['index'],hold_row),'new history binds held source and formal HOLD')
I.need(p['hostSourceRoot']==str(SOURCE),'genuine current source root')
I.verify_descriptors(p,'all unchanged actual host/component/native prerequisite descriptors')
deps=load(SOURCE/'runtime-dependencies.json');I.need(len(deps['files'])==34 and len({r['path']for r in deps['files']})==34,'finite34 runtime helper/DATA rows')
for r in deps['files']:I.verify(r,'actual runtime dependency')
graph=load(SOURCE/'module-edges.json');I.need(len(graph['modules'])==28 and len(graph['edges'])==108,'finite28 module/108 edge graph')
module_paths={r['path']for r in graph['modules']};expected_edges=[]
for r in graph['modules']:
    text=I.verify(r,'actual static module graph').read_text()
    for pattern,kind in [(r'\b(?:import|export)\s+(?:[^;\n]*?\bfrom\s*)?[\'\"]([^\'\"]+)[\'\"]','static'),(r'\bimport\s*\(\s*[\'\"]([^\'\"]+)[\'\"]\s*\)','literal-dynamic')]:
        for m in re.finditer(pattern,text):
            spec=m.group(1);edge=dict(source=r['path'],specifier=spec,kind=kind)
            if spec.startswith('.'):
                target=str((Path(r['path']).parent/spec).resolve());I.need(target in module_paths,'every literal local import resolves inside finite graph');edge['target']=target
                I.need(target.startswith(str(SOURCE)+'/')or target in {x['path']for x in deps['files']},'every external module bound before custom imports')
            else:I.need(spec.startswith('node:'),'only reviewed builtin or literal-local modules')
            expected_edges.append(edge)
declared=[dict(source=e['from'],**{k:v for k,v in e.items()if k!='from'})for e in graph['edges']]
key=lambda e:(e['source'],e['kind'],e['specifier'],e.get('target',''))
I.need(sorted(expected_edges,key=key)==sorted(declared,key=key),'independently reconstructed complete finite module graph')
I.need(sum(e['kind']=='literal-dynamic'for e in expected_edges)==1,'one literal dynamic body import')
auth=(SOURCE/'source-auth.mjs').read_text();run=(SOURCE/'run.mjs').read_text();body=(SOURCE/'run-body.mjs').read_text();guard=(SOURCE/'guard.mjs').read_text();capture=(SOURCE/'response-capture.mjs').read_text();test=(SOURCE/'test-capture.mjs').read_text();models=(SOURCE/'models.mjs').read_text()
for token in ["'4b7c36f2d50e2c3bee831d7c4681b62bea67fb667e5da10f227125e3dd860e70'",'inherited=await checkIndexedFamily(OLD_INDEX),family=await checkIndexedFamily(own)','await inherited.recheck();await family.recheck();await deps.recheck();','issued.add(capsule)','issued.has(capsule)']:
    I.need(token in auth,'complete private inherited/current/dependency source capsule '+token)
I.need(run.index('await captureHostSources(index)')<run.index("await import('./run-body.mjs')"),'source capsule before dynamic custom import')
I.need('finally{await source.recheck();}'in run,'public bootstrap final/failure source recheck')
I.need(body.index('assertHostSources(source,options.sourceIndex)')<body.index('await hostPreflight(options)')<body.index('await DurableOutput.create'),'private capsule before genuine preflight/output')
I.need('await source.recheck();await a.recheck();'in body and "postFailureSourceAuditPassed:audited"in body,'full source/native/artifact final and post-admission failure audits')
I.need(guard.index('await indexFiles(descriptor(constructionRoot.publicationIndex))')<guard.index('await import(pathToFileURL(bridge))'),'actual original publication authenticates before helper import')
I.need('same(audit.fullActualNativeMetadata,frame.metadata)&&same(audit.actualSelectedManifests,frame.selectedManifests)'in guard,'whole actual355 metadata/manifests no projection')
I.need('captureSetSummary(responseCaptures)'in body and 'partialRawRetained:true'not in body,'outer summary consumes real carriers, no blanket retention')
I.need(capture.index("await save('json',name+'-headers.json',metadata());headersSaved=true")<capture.index('reader=response.body?.getReader()')<capture.index('await reader.read()'),'durable headers before acquisition/read')
I.need(capture.index('const snapshot=Buffer.from(step.value);chunks.push(snapshot);bytes+=snapshot.length;')<capture.index("const row=await save('bytes',name+'-chunks/'"),'exact public U8 window snapshot before durable chunk/next read')
for token in ["name+'-body.partial.bin',Buffer.concat(chunks)",'writeFailures.push({stage:path,thrown:info(e)})','availableRawRetained:headersSaved&&bodyBytesRetained&&writeFailures.length===0','completeResponseRetained:receivedHeaders&&headersComplete&&streamEnded&&headersSaved&&bodyBytesRetained&&writeFailures.length===0',"failureRecordRetained=(await attempt('json',name+'-failure.json',receipt))!==null",'failed.rawCapture=summary()',"readinessRetryAllowed=retry&&writeFailures.length===0"]:I.need(token in capture,'truthful complete/partial/write-failure accounting '+token)
I.need("if(!headersSaved)"in capture and "-headers.partial.json"in capture,'partial metadata after pre-header/write error')
I.need("if(reader&&!streamEnded)"in capture and 'pending.catch(()=>{})'in capture,'best effort public reader cleanup, not guest wire proof')
for token in ['acquireError','readError','fetchError','failWrite','mutate','headersBeforeReader:true','midBodyReadAbortNetworkAndAcquisitionFailurePrefixesRetained:true','writerFailureFlagsAndOuterCarrierHonest:true','allFail','aggregateFail','recordFail','badText']:
    I.need(token in test,'genuine injected capture test source covers '+token)
for attempt in [1,2]:
    root=SOURCE/f'evidence/pure-attempt{attempt}';terminal=load(root/'terminal.json');stdout=(root/'stdout.log').read_bytes();lines=stdout.splitlines();I.need(terminal['rawExitCode']==0 and (root/'stderr.log').stat().st_size==0 and len(lines)==1,'retained genuine pure test clean exit')
    v=I.decode(lines[0]);I.need(v['checks']==[104,110][attempt-1] and v['actualFetchNetworkReaderIoServersPortsCurlPreflightGuestNativeCodecOrOtherActionsInvoked']is False,'stored historical104/final110 injected checks authenticated only, not rerun')
syntax=load(SOURCE/'evidence/syntax.json');I.need(len(syntax)==7 and all(v['rawExitCode']==0 and v['stderr']==''for v in syntax),'stored seven syntax checks authenticated only')
for path in SOURCE.glob('*.py'):ast.parse(path.read_text())
for name in ['future-authority.template.json','future-component-phase.template.json','future-host-controller.template.json','future-config.template.json']:
    value=load(SOURCE/name)
    for k in ['sourceIndependentReview','actualComponentReview','constructionConfig','componentPhase','hostController','sourceIndex','rootAction']:
        if k in value:I.need(value[k]is None,'future authority slot remains NULL '+k)
    for k in ['actionAllowed','hostRequestsAllowed','hostExecutionAllowed']:
        if k in value:I.need(value[k]is False,'future action remains false '+k)
I.need("consumers355-http-both-hosts-v2"in models and 'ROOT_REVIEWED_CONSUMERS355_HTTP_BOTH_HOSTS_V2'in models,'new exact action namespace, no old Root authority adoption')
component_review=I.read(p['availableComponentReviewData']['result']);component_contract=I.read(p['availableComponentReviewData']['contract'])
for k,v in component_contract['requiredFixedValues'].items():I.need(same(component_review[k],v),'unchanged actual artifact fixed value '+k)
I.need(component_review['hostActionAuthority']is None and component_review['hostRequestsInvoked']is False,'actual construction proof is not host authority')
I.full_construction_closure(I.read(p['constructionClosure']))
I.final_rehash()
write('rehashed-inputs.json',dict(schemaVersion=1,files=list(I.ROWS.values()),freshFinalRehash=True,ownerCodeImportedOrExecuted=False))
write('data-results.json',dict(schemaVersion=1,state='INDEPENDENT_HTTP_HOST_V2_SOURCE_DATA_REVIEW_COMPLETE',sourceIndex=source_row,heldSourceIndex=old_row,formalHoldIndex=hold_row,sourceMembers=31,heldMembers=42,formalHoldMembers=10,currentInputRows=12835,inheritedInputRows=12781,actualRuntimeDependencies=34,actualModules=28,actualEdges=108,exactAfterimages=5,exactForwardReverseEdits=26,independentlyReconstructedFiniteGraph=True,fullInitialFinalFailureSourceCapsulePresent=True,actual355NativeContextData=native_summary,actualArtifactReview=p['availableComponentReviewData'],storedOwnerEvidence=dict(pureChecksByRun=[104,110],finalPureChecks=110,pureRuns=2,syntaxChecks=7,rerunByReviewer=False),completePartialAndCaptureWriteFailureFlagsSourceChecked=True,allRootActionSlotsRemainNullOrFalse=True,uniquePhysicalFilesFreshlyRehashed=len(I.ROWS),checks=I.CHECKS,memberships=I.MEMBERSHIPS,reviewerReadHashDataAndPythonAstOnly=True,ownerCodeInvoked=False,concreteBlockers=[]))
print(json.dumps(dict(state='SOURCE_DATA_REVIEW_COMPLETE',sourceSha256=SOURCE_SHA,sourceMembers=31,oldMembers=42,holdMembers=10,uniquePhysicalFiles=len(I.ROWS),checks=I.CHECKS,modules=28,edges=108,exactEdits=26,ownerCodeInvoked=False)))
