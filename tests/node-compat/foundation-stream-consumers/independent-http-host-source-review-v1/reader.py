"""Independent read/hash/static host source review. No owner code imports."""
from pathlib import Path
import hashlib,json,ast,re,os
P=Path(__file__).resolve().parent;S=P.parent/'http-host-candidate-v1'
checks=0;seen={};physical={}
def need(ok,msg):
 global checks
 if not ok:raise AssertionError(msg)
 checks+=1
def ident(s):return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def row(p):
 p=Path(p);h=hashlib.sha256();size=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b);size+=len(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=size)
def verify(r,role):
 p=Path(r['path']);need(p.is_absolute()and p.is_file()and not p.is_symlink(),'ordinary absolute input')
 real=str(p.resolve());a=p.stat()
 if real not in physical:
  v=row(p);b=p.stat();need(ident(a)==ident(b),'stable streamed bytes');physical[real]=dict(sha256=v['sha256'],bytes=v['bytes'],identity=ident(b))
 else:need(ident(a)==physical[real]['identity'],'stable repeated physical bytes')
 need(physical[real]['sha256']==r['sha256']and physical[real]['bytes']==r['bytes'],'exact input '+str(p))
 if str(p)not in seen:seen[str(p)]={k:r[k]for k in ['path','sha256','bytes']};seen[str(p)]['roles']=set()
 seen[str(p)]['roles'].add(role)
 return r
def data(r,role='data'):verify(r,role);return json.loads(Path(r['path']).read_bytes())
def indexed(r,count=None):
 v=data(r,'index');need(v['schemaVersion']==1 and isinstance(v['files'],list),'finite source inventory')
 if count is not None:need(len(v['files'])==count,'exact source inventory count')
 rs=[];names=set()
 for x in v['files']:
  n=x['path'];need(n and not n.startswith('/')and '\\'not in n and all(t not in ['','.','..']for t in n.split('/'))and n not in names,'safe unique member');names.add(n)
  z=dict(path=str(Path(r['path']).parent/n),sha256=x['sha256'],bytes=x['bytes']);verify(z,'indexed-member');rs.append(z)
 need({str(p.relative_to(Path(r['path']).parent))for p in Path(r['path']).parent.rglob('*')if p.is_file()}==names|{'index.json'},'complete exact inventory membership')
 return rs
def descriptors(v):
 rs=[]
 def walk(x):
  if isinstance(x,dict):
   if isinstance(x.get('path'),str)and Path(x['path']).is_absolute()and isinstance(x.get('sha256'),str)and type(x.get('bytes'))is int:rs.append({k:x[k]for k in ['path','sha256','bytes']})
   for y in x.values():walk(y)
  elif isinstance(x,list):
   for y in x:walk(y)
 walk(v);return rs
def citation(n,text):
 p=S/n;s=p.read_text();need(text in s,'source citation');return dict(path=str(p),line=s[:s.index(text)].count('\n')+1,text=text)
def save(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
src=dict(path=str(S/'index.json'),sha256='4b7c36f2d50e2c3bee831d7c4681b62bea67fb667e5da10f227125e3dd860e70',bytes=6608)
rs=indexed(src,42);by={str(Path(r['path']).relative_to(S)):r for r in rs}
inputs=data(by['source-inputs.json'],'complete-source-inputs');need(len(inputs['files'])==12781 and inputs['delegatedFull355PhysicalFiles']==12667,'exact delegated source input counts')
for r in inputs['files']:verify(r,'complete12781-source-native-tool-context')
p=data(by['prerequisites.json'],'actual-source-prerequisites');deps=data(by['runtime-dependencies.json'],'runtime-import-data-seal');edges=data(by['module-edges.json'],'finite-module-graph');deriv=data(by['derivations.json'],'source-derivations')
need(len(deps['files'])==26 and len(edges['modules'])==26 and len(edges['edges'])==104,'finite runtime module/data graph')
for r in deps['files']:verify(r,'authenticated-runtime-import-or-data')
for r in edges['modules']:verify(r,'finite-static-module')
for r in descriptors(p):verify(r,'prerequisite-context-or-proof')
for x in deriv['exactCopies']:
 verify(x['origin'],'exact-copied-helper');need(Path(x['origin']['path']).read_bytes()==(S/x['afterimage']).read_bytes(),'helper unchanged '+x['afterimage'])
command=deriv['commandLifecycle'];verify(command['origin'],'genuine-owned-command-donor');original=Path(command['origin']['path']).read_text();actual=(S/command['afterimage']).read_text();f=original
for e in command['edits']:need(f.count(e['old'])==e['count']==1,'unique command forward edit');f=f.replace(e['old'],e['new'])
need(f==actual,'complete three-command edit afterimage');back=actual
for e in reversed(command['edits']):need(back.count(e['new'])==1,'unique command reverse edit');back=back.replace(e['new'],e['old'])
need(back==original,'complete command reverse exact')
std=deriv['standardSourceReader'];verify(std['origin'],'standard-reader-donor');st=Path(std['origin']['path']).read_text();own=(S/'source-auth.mjs').read_text();need(own.startswith(st[:std['prefixEnd']]+st[std['bodyStart']:std['bodyEnd']]),'exact standard-only source auth extraction')
# Reconstruct the literal static/dynamic module edges independently for this pinned syntax.
modulepaths={r['path']for r in edges['modules']};computed=[]
for r in edges['modules']:
 text=Path(r['path']).read_text()
 for kind,pattern in [('static',r"\b(?:import|export)\s+(?:[^;\n]*?\s+from\s*)?['\"]([^'\"]+)['\"]"),('literal-dynamic',r"\bimport\(\s*['\"]([^'\"]+)['\"]\s*\)")]:
  for spec in re.findall(pattern,text):
   edge=dict(from_=r['path'],specifier=spec,kind=kind);edge['from']=edge.pop('from_')
   if spec.startswith('.'):
    target=str((Path(r['path']).parent/spec).resolve());need(target in modulepaths,'all literal runtime helper modules in finite graph');edge['target']=target
   else:need(spec.startswith('node:'),'only standard bare modules in host graph')
   computed.append(edge)
actual_literal=[x for x in edges['edges']if x['kind']in ['static','literal-dynamic']]
need(sorted(map(lambda v:json.dumps(v,sort_keys=True),computed))==sorted(map(lambda v:json.dumps(v,sort_keys=True),actual_literal)),'complete finite literal graph edges')
# Bind the actual component proof and full unprojected metadata/native frame as data.
proof=p['availableComponentReviewData'];indexed(proof['index'],16);v=data(proof['result'],'actual-component-review');c=data(proof['contract'],'actual-component-contract')
need(v['state']=='INDEPENDENT_CONSUMERS355_HTTP_COMPONENT_REVIEW_PASSED_V1'and v['verifiedPassed']and v['sourceFiles']==355 and v['engineSha256']==p['engineSha256']and v['engineMetadataSha256']==p['engineMetadataSha256'],'exact actual355 RuntimeOnly component proof')
for k,w in c['requiredFixedValues'].items():need(v[k]==w,'whole component fixed field '+k)
for k,r in c['requiredExactDescriptors'].items():need(v[k]==r,'exact component descriptor '+k);verify(r,'actual-component-proof-artifact')
audit=data(v['componentAudit'],'full-unmodified-component-audit');metadata=data(v['metadata'],'full-actual-native-metadata');need(audit['fullActualNativeMetadata']==metadata and len(metadata['sourceManifest'])==355 and len(audit['actualSelectedManifests'])==11,'full actual355/native11 manifests retained')
need(v['selectedInterfaces']==v['emittedImports']==audit['allowedImports']==audit['emittedImports']and len(v['emittedImports'])==6 and v['emittedExports']==['wasi:http/incoming-handler@0.2.10']and v['clockTypeOnly']and v['callableClockImports']==v['coreClockImports']==[],'exact six/type-only clocks/sole handler')
# These large delegated source/proof files stay at their authenticated original contexts.
closure=data(p['constructionClosure'],'genuine-original355-physical-closure');need(len(closure['files'])==12667 and len(closure['toolTrees'])==2 and len(closure['toolLinks'])==22 and len(closure['liveInputs'])==8,'full source/tool/adapter context boundary')
for r in closure['files']:verify(r,'genuine-original355-closure-input')
for link in closure['toolLinks']:
 q=Path(link['path']);need(q.is_symlink()and os.readlink(q)==link['linkText']and str(q.resolve())==link['resolvedTarget'],'exact known physical tool link')
for r in closure['liveInputs']:verify(r,'all8-live-WIT-adapter')
# Static actual caller/callee ordering and closed phase models.
body=(S/'run-body.mjs').read_text();guard=(S/'guard.mjs').read_text();models=(S/'models.mjs').read_text();server=(S/'server.mjs').read_text();validation=(S/'validate.mjs').read_text();bootstrap=(S/'run.mjs').read_text()
need(bootstrap.index('captureHostSources(index)')<bootstrap.index("import('./run-body.mjs')"),'full own/dependency auth before body import')
need(guard.index('await indexFiles(descriptor(constructionRoot.publicationIndex))')<guard.index('await import(pathToFileURL(bridge))'),'actual publication before genuine preflight import')
need("httpPreflight({configDescriptor:rows.constructionConfig})"in guard and 'same(audit.fullActualNativeMetadata,frame.metadata)'in guard and 'same(audit.actualSelectedManifests,frame.selectedManifests)'in guard,'unchanged genuine config/frame full metadata comparison')
need("await mkdir(join(output.root,'processes'),{mode:0o700})"in body and body.index("await mkdir(join(output.root,'processes')")<body.index("await command('wasmtime-version'"),'genuine command processes directory before helper')
need("for(const k of ['HOME','home','CODEX_HOME'])"in models and 'processEnv={...ENV,...inheritedPaths,TMPDIR:'in body and 'const env={...ENV,...inheritedPaths,TMPDIR:'in body,'HOME/home/CODEX_HOME preserved in both contexts')
need("['serve','--addr','127.0.0.1:0',a.rows.component.path]"in body and "const base=['--user-config',userConfig,'-C',project]"in body and "'--meters','duration','dev'"in body,'actual accepted stock host CLI mechanisms')
need("for(let i=1;i<=3;i++)"in body and 'timeoutMs=600000'in server and 'Date.now()+60000'in body and 'Date.now()+120000'in body and 'AbortSignal.timeout(timeoutMs)'in body,'finite host/readiness/request scopes')
need("expectedCode:7"in body and "need(result.stdoutFile.bytes===0"in body and "'--connect-timeout','2','--max-time','3'"in body,'stopped curl7/no HTTP bytes')
need("pid>1&&pid!==self"in models and "shutdownSignals.length===1&&v.shutdownSignals[0]==='SIGINT'"in models and 'ownedGroupGone:!alive()'in server,'owned groups and graceful-only accepted')
need('const validators={combined:await import' in body and 'projectConsumerBody(raw.body,audit)'in validation and '...audit.baselineAndClassic,componentSha256:audit.componentSha256,selectedInterfaces:'in validation,'explicit ephemeral response/audit view preserves raw source objects')
need(body.count('await source.recheck()')>=5 and body.count('await a.recheck()')>=5 and "await adopt(output);await write('failure.json'"in body,'success/failure/final source-native-artifact audits')
for n in ['future-authority.template.json','future-component-phase.template.json','future-host-controller.template.json','future-config.template.json']:
 x=data(by[n],'closed-future-phase-template')
 for k,y in x.items():
  if k.endswith(('Allowed','Claim'))or k=='actionAllowed':need(y is False,'no future action grant '+k)
# Actual source defect: bytes/headers available before a failed read are not retained.
start=body.index('async function request(');end=body.index('async function stopProbe',start);request=body[start:end];catch=request[request.index('}catch(error)'):]
need(request.index("const r=await reader.read()")<request.index("await write(name+'-raw.json',metadata)"),'headers persisted only after whole stream completes')
need("partialBodyBytes:bytes,receivedHeaders:response!==undefined"in catch and "Buffer.concat(chunks)"not in catch and "response.headers"not in catch,'actual catch loses available chunks and header values')
finding=dict(id='HTTP-HOST-M1',disposition='HOLD',severity='mandatory-before-host-action',
 summary='A read/abort/network failure after response headers or partial chunks loses available status/header/body data, while the failure text claims complete available raw retention.',
 citations=[citation('run-body.mjs','async function request('),citation('run-body.mjs',"const raw=Buffer.concat(chunks);await output.write(name+'-body.bin',raw)"),citation('run-body.mjs',"}catch(error){const retry=readinessRetryAllowed"),citation('run-body.mjs',"partialRawRetained:true")],
 correction='Fresh immutable successor: durably retain actual status and public headers immediately after fetch; retain every available partial chunk on read/abort/network/reader failure before assertions. Record truthful complete/partial/capture-failure fields; do not claim a raw body exists when capture failed. Keep failed/partial responses unaccepted.',
 observedHostFailure=False,actualHostInvoked=False)
examples=[dict(case='headers then read rejects',availableStatus=503,availableHeaders=[['content-type','application/json']],availableBodyHex='',currentCatchRetains=['receivedHeaders:true','partialBodyBytes:0','error name/message'],lost=['actual status','actual header values']),dict(case='two chunks then timeout',availableStatus=200,availableHeaders=[['content-type','application/json']],availableBodyHex='7b226f6b223a',currentCatchRetains=['receivedHeaders:true','partialBodyBytes:6','error name/message'],lost=['actual status','actual header values','all6 received body bytes'])]
for n in ['check-source.py','seal-source.py']:ast.parse((S/n).read_text())
for real,r in physical.items():need(ident(Path(real).stat())==r['identity'],'all current inputs stable at final read')
save('findings.json',dict(schemaVersion=1,findings=[finding],staticCounterexamples=examples,counterexampleScope='Source/control-flow DATA only; no stream/network/helper executed.'))
save('rehashed-inputs.json',dict(schemaVersion=1,files=[dict(r,roles=sorted(r['roles']))for r in sorted(seen.values(),key=lambda r:r['path'])],physicalFilesHashed=len(physical),ownerActionsInvoked=False))
save('data-results.json',dict(schemaVersion=1,sourceIndex=src,sourceDataReviewComplete=True,sourceMembers=42,inputDescriptors=12781,runtimeDependencyFiles=26,moduleFiles=26,declaredModuleEdges=104,finiteLiteralEdgesIndependentlyReconstructed=len(computed),delegatedOriginalContextFiles=12667,toolTrees=2,toolLinks=22,liveWitAdapterFiles=8,exactStandardHelpers=4,exactCommandForwardReverseEdits=3,actualComponentReview=proof,component=v['component'],engine=v['engine'],metadata=v['metadata'],fullActualNativeMetadataAnd355SourceContextVerified=True,nativeSelectedManifests=11,emittedImports=v['emittedImports'],emittedExports=v['emittedExports'],clockTypeOnly=True,genuineUnchangedConstructionConfigBound=True,oldPureValidatorsOnlyThroughExplicitDataViews=True,homePathsPreserved=True,processesDirectoryCreatedBeforeCommandHelper=True,threeResponsesPerHostProposed=True,ownedGracefulShutdownAndStoppedCurl7ChecksPresent=True,finalAndFailureSourceAuditsPresent=True,pythonAstChecks=2,storedOwnerChecksAuthenticatedOnly=dict(sourceData=38812,pure=86,grammar=13,pythonAst=2),mandatorySourceFindings=1,sourceReviewPassed=False,sourceOnly=True,ownerActionsInvoked=False,uniqueDeclaredInputs=len(seen),physicalFilesHashed=len(physical),checks=checks))
print(json.dumps(dict(sourceDataReviewComplete=True,sourceBlockers=1,members=42,inputs=12781,physical=len(physical),checks=checks)))
