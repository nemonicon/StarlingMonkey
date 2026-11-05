"""Independent source/read/hash/data review. No owner module is imported."""
import ast,collections,hashlib,json,os,re,stat
from pathlib import Path
P=Path(__file__).resolve().parent;D=P.parent/'http-construction-candidate-v1'
SHA='dc98f4653eec1719e07d64ecfa8eb93ecfea1748bb3640521e0ac2a7e6aa5487'
seen={};checks=[]
def need(v,m):
 if not v:raise AssertionError(m)
 checks.append(m)
def row(p):
 p=Path(p);h=hashlib.sha256();n=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b);n+=len(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=n)
def verify(r,role):
 p=Path(r['path']);a=p.stat();need(p.is_file()and not p.is_symlink(),'ordinary leaf '+str(p));actual=row(p);b=p.stat()
 need(all(actual[k]==r[k]for k in ['path','sha256','bytes']),'exact bytes '+str(p));need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns),'stable read '+str(p))
 if str(p)in seen:need(all(seen[str(p)][k]==r[k]for k in ['path','sha256','bytes']),'consistent shared input');seen[str(p)]['roles'].add(role)
 else:seen[str(p)]={**actual,'roles':{role}}
 return actual
def data(r,role):verify(r,role);return json.loads(Path(r['path']).read_bytes())
def local(n):need(isinstance(n,str)and n and not n.startswith('/')and '\\'not in n and '\0'not in n and all(x not in ['', '.', '..']for x in n.split('/')),'finite local member');return n
def index(r,count=None):
 x=data(r,'index');need(x['schemaVersion']==1 and isinstance(x['files'],list),'finite indexed family')
 if count is not None:need(len(x['files'])==count,'exact indexed count '+str(count))
 names=set();rows=[]
 for v in x['files']:
  n=local(v['path']);need(n not in names,'unique indexed member');names.add(n);q=dict(path=str(Path(r['path']).parent/n),sha256=v['sha256'],bytes=v['bytes']);verify(q,'indexed-member');rows.append(q)
 return x,rows
def save(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
ownrow=row(D/'index.json');need(ownrow['sha256']==SHA and ownrow['bytes']==6151,'exact reviewed HTTP source')
ix,own=index(ownrow,39);need({str(p.relative_to(D))for p in D.rglob('*')if p.is_file()}=={r['path']for r in ix['files']}|{'index.json'},'exact own physical membership')
freeze=json.loads((D/'input-freeze.json').read_bytes());need(len(freeze['files'])==12789,'exact12789 prep rows')
for r in freeze['files']:verify(r,'original-preparation-reference')
c=json.loads((D/'closure.json').read_bytes());need(len(c['files'])==12667 and len({r['path']for r in c['files']})==12667,'exact canonical physical closure')
need(sum(r['bytes']for r in c['files'])==1441957178,'actual logical bytes')
for r in c['files']:
 verify(r,'runtime-physical-input')
 need(str(Path(r['path']).resolve())==r['path'],'canonical closure path')
 for spelling in r['declaredPaths']:need(str(Path(spelling).resolve())==r['path']and (spelling==r['path']or spelling.startswith('/tmp/')and '/private'+spelling==r['path']),'only explicit system/tmp aliases')
def inventory(root):
 result=[]
 def walk(at,prefix):
  for p in sorted(at.iterdir()):
   s=p.lstat();kind='symlink'if stat.S_ISLNK(s.st_mode)else'directory'if stat.S_ISDIR(s.st_mode)else'file'if stat.S_ISREG(s.st_mode)else None
   need(kind is not None,'ordinary tree entry');n=prefix+p.name;result.append(dict(path=n,kind=kind))
   if kind=='directory':walk(p,n+'/')
 walk(Path(root),'');return sorted(result,key=lambda r:r['path'])
need(len(c['toolTrees'])==2 and len(c['toolLinks'])==22 and c['actualToolRows']==4892,'complete two tool trees/4892 files22links')
for tree in c['toolTrees']:need(str(Path(tree['path']).resolve())==tree['realPath']and inventory(tree['path'])==tree['entries'],'exact physical tool membership')
for link in c['toolLinks']:
 p=Path(link['path']);need(p.is_symlink()and os.readlink(p)==link['linkText']and str(p.resolve())==link['resolvedTarget'],'exact declared npm link')
 need(any(link['resolvedTarget'].startswith(t['realPath']+'/')for t in c['toolTrees']),'link contained in declared tool tree')
snapshot=inventory(c['familySnapshotRoot']);need(all(r['kind']!='symlink'for r in snapshot)and sorted(r['path']for r in snapshot if r['kind']=='file')==c['familySnapshotMembers']and len(c['familySnapshotMembers'])==1678,'complete1678 source snapshot')
need(len(c['liveInputs'])==8,'LIVE8 exact count')
wit=[r for r in c['liveInputs']if '/wit/deps/'in r['name']];need(len(wit)==7,'seven live WIT files')
for r in c['liveInputs']:verify(r,'live8')
wr=Path(c['packagingRoot'])/'host-apis/wasi-0.2.10/wit/deps';need(sorted(p.name for p in wr.iterdir())==sorted(r['name'].split('/')[-2]for r in wit),'exact live WIT package names')
for p in wr.iterdir():need(p.is_dir()and not p.is_symlink()and sorted(x.name for x in p.iterdir())==['package.wit'],'only ordinary package.wit')
adapter=next(r for r in c['liveInputs']if '/preview1-adapter-release/'in r['name']);need(adapter['bytes']==53512 and adapter['sha256']=='988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0','repository release adapter exact')
p=json.loads((D/'prerequisites.json').read_bytes());family,frows=index(p['familyIndex'])
need(p['familySha256']==p['familyIndex']['sha256']=='a986e9b2fbdad5922f0ef9b9adba202912fa373ddb4a26b648495a1651e64916','genuine original a986 context')
pins=data(p['reviewedPins'],'four reviewed native pins');review=data(p['nativeRootReview'],'Root native review');pin=pins['variants']['normal-runtime']
need(p['reviewedPins']['sha256']=='93512520ba6f9ddaba096c09936f16f33462b371b5a9df4cf3315e9a43a5d67b'and p['nativeRootReview']['sha256']=='6359ca0b635bb252643f7082cc0df02d6c7fc83cdec5b4fc94e470c231470ce4','actual four-pin authority')
need(pin['engineSha256']==p['normalRuntimeEngineSha256']=='b227a8d2e6fb6b83da556d3520dceec82d5e1978801ba3c607bc9a31aa28ad60'and pin['reviewRequired']is False and pin['sourceFiles']==355,'genuine RuntimeOnly355 pin')
need(len(pin['frozenFiles'])==1164,'actual selected native1164 frozen copies')
for r in pin['frozenFiles']:verify(r,'actual-RuntimeOnly-frozen-copy')
meta_path=Path(pin['enginePath']+'.build.json');metadata=data(dict(path=str(meta_path),sha256=p['normalRuntimeMetadataSha256'],bytes=meta_path.stat().st_size),'genuine355-runtime-metadata')
need(len(metadata['sourceManifest'])==355 and metadata['entropyPolicy']=='runtime-only'and metadata['streamConsumersEnabled']is True and metadata['gcStress']is False,'complete native355 unprojected RuntimeOnly metadata')
for r in metadata['sourceManifest']:
 for root in [p['nativeConfiguredSourceRoot'],p['nativeFrozenSourceRoot']]:verify(dict(path=str(Path(root)/r['path']),sha256=r['sha256'],bytes=(Path(root)/r['path']).stat().st_size),'configured-and-frozen355')
bridge=Path(p['paths']['familyRoot'])/'native-preflight.mjs';text=bridge.read_text();need("validationPreflight({variant='normal-off'}={})"in text and "config.bootstrapRoot,'artifact-tools/bootstrap-preflight.mjs'"in text and 'sourceManifest.length,355'in text,'actual original named355 validation bridge')
need(str(bridge)in {r['path']for r in c['files']},'native bridge actual path in closure')
need(Path(p['baselineSource']['path']).read_bytes()==Path(p['actualAcceptedBaselineSource']['path']).read_bytes(),'actual accepted baseline bytes unchanged')
for copied in json.loads((D/'copied-mechanisms.json').read_bytes())['rows']:
 verify(copied['origin'],'unchanged mechanism/source origin');need((D/copied['afterimage']).read_bytes()==Path(copied['origin']['path']).read_bytes(),'copied mechanism byte exact '+copied['afterimage'])
deriv=json.loads((D/'virtual-data-derivation.json').read_bytes());verify(deriv['origin'],'old accepted fixture/oracle builder');raw=Path(deriv['origin']['path']).read_text().encode('utf-16-le');block=raw[deriv['originStartUtf16Offset']*2:deriv['originEndUtf16Offset']*2].decode('utf-16-le')
need(hashlib.sha256(block.encode()).hexdigest()==deriv['exactOriginalSemanticBlockSha256']and block in(D/'virtual-data.mjs').read_text(),'full old oracle-construction semantic block byte exact at true UTF16 offsets')
modules={n:(D/n).read_text()for n in ['admission.mjs','publish.py','run.mjs','worker.mjs','physical.mjs','composer.mjs','consumer-probes.mjs','virtual-data.mjs','type-audit.mjs','validate-response.mjs']}
g=modules['admission.mjs'];w=modules['worker.mjs'];pub=modules['publish.py'];run=modules['run.mjs'];physical=modules['physical.mjs']
need("publicationIndex.path===join(HERE,'index.json')"in g and "publication.outputRoot===HERE"in g and "descriptor(publication.proposalIndex)"in g,'actual published HERE distinct from original proposal context')
need(g.index('await verifyClosure(')<g.index('await import(pathToFileURL(bridge))')and "validationPreflight({variant:'normal-runtime'})"in g,'full closure authenticates original355 bridge before genuine import')
for token in ['native.admissionSourceRoot===p.nativeConfiguredSourceRoot','native.runtimeSourceRoot===p.nativeFrozenSourceRoot','native.componentToolRoot===p.paths.packagingRoot',"core.coreVersion==='sm-node-22.14.0-m0.11'","m.profileVersion==='sm-node-22.14.0-m0.14'"]:
 need(token in g,'actual full frame context/core/consumer clause '+token)
need('selectedManifestsForEngine('not in w and 'selectCoreExpectations('not in w and 'verifyProductionTicks('not in w,'no old selector/preflight bypass in active inner worker')
need('d.frame.selectedManifests'in w and 'd.frame.coreExpectations'in w and 'sourceManifest.length===355'in w,'whole actual355 frame passed to real bundler')
need("for(const k of ['NODE_COMPAT_RELEASE_SCOPE','NODE_COMPAT_RELEASE_SCOPE_OUTPUT','NODE_COMPAT_RELEASE_ACTION_AUTHORITY','NODE_COMPAT_RELEASE_ACTION_AUTHORITY_SHA256'])"in g,'old release action scope not an HTTP authority')
need('INDEPENDENT_CONSUMERS355_HTTP_CONSTRUCTION_SOURCE_REVIEW_PASSED_V1'in g and 'sourcePeer.data.httpSourceIndexSha256===sourceSha'in g and 'publishedPeer.data.runtimeActionsInvoked===false'in g,'separate source/publication/action peer contracts')
need(pub.index('authority_model(root,source_sha)')<pub.index('with PrivateRoot(OUTPUT)')and 'sourcePromotionAllowed'in pub and "out.discard_owned_success_marker('completion.json')"in pub,'guarded exclusive source-only publisher and failure marker removal')
need("'proposalIndex':{'path':str(HERE/'index.json')"in pub and "out.write('proposal-index.json',own_raw)"in pub,'original proposal pinned separately; no old preparation relocation')
payload=json.loads((D/'payload.json').read_bytes())['files'];need(len(payload)==18 and all(n in {r['path']for r in ix['files']}for n in payload)and not any(n in payload for n in ['publish.py','input-freeze.json','copy_primitives.py']),'finite18-file runtime payload no publisher/cache transplant')
need(run.index("mkdir(join(output.root,'processes')")<run.index('await runOwnedCommand(')and 'timeoutMs:a.workerTimeoutMs,maxOutputBytes:16*1024*1024'in run,'processes0700 before unchanged600s/full pipe owned lifecycle')
need('clean(status)'in run and 'await a.recheck();await output.recheck()'in run,'retained raw terminal gate and final parent audits')
need(w.index('await verifyClosure(')<w.index("await import(pathToFileURL(join(pack,'toolchain.mjs')))"),'worker whole source/tool check before genuine library imports')
need("createConsumersHTTPPlugin(paths)"in w and "treeshake:false"in w and "codeSplitting:false"in w and 'builtinManifests:d.frame.selectedManifests'in w,'real whole-entry Rolldown/native manifest bundling')
need(w.index("await output.write('http.bundle.mjs'")<w.index('Exact18 native/standard imports'),'whole bundle retained before graph acceptance')
need('Object.entries(virtual.virtualModules)'in w and 'virtualRows.push({id:name,...r})'in w,'all virtual source bytes recorded with actual IDs')
need("if(d.action==='bundle-source')"in w and 'd.actualBundle?.bundle'in w and 'componentizeSelectedHTTP('in w and 'componentNew(core,[],false)'in w,'bundle/build split and actual selected HTTP wrapping APIs')
need('before=await verifyLiveInputs(closure)'in w and 'after=await verifyLiveInputs(closure)'in w and 'wit/deps/'in w and "preview2Adapter:adapter.path"in w,'bounded7-WIT/adapter live8 guards before and after copies')
need('finalizeCore'not in w or 'componentizeSelectedHTTP'in w,'no direct alternate componentization seam')
need('WebAssembly.Module.imports(new WebAssembly.Module(core))'in w and "v.module==='wasi_snapshot_preview1'"in w,'no Preview1 core imports before final component wrapping')
need('auditClockDependency(p.wasmTools'in w and 'made.packagingAudit.coreImports'in w,'actual final core imports used in type-only clock audit')
need('child.stdout??Buffer.alloc(0)'in modules['type-audit.mjs']and modules['type-audit.mjs'].index("await output.write('wasm-tools-'")<modules['type-audit.mjs'].index('need(child.status===0'),'parser raw capture precedes status/JSON assertion')
need("Object.keys(clock.functions))==='[]'"in modules['type-audit.mjs']and "'{\"type\":\"u64\"}'"in modules['type-audit.mjs'],'finite duration-only nominal clock type required')
need("yield new Uint8Array([0xe2])"in modules['consumer-probes.mjs']and "yield new Uint8Array([0x82, 0xac])"in modules['consumer-probes.mjs']and "yield '{\"consumer\":'"in modules['consumer-probes.mjs'],'exact two supported per-request ordinary iterable fixtures')
need('request.body'not in modules['composer.mjs']and 'getReader'not in modules['composer.mjs'],'no wire-body/reader adapter')
need('originalCombinedValidator(view,audit.baselineAndClassic)'in modules['validate-response.mjs']and "base.classicCombinedHTTP?.ordinaryGroups===19"in modules['validate-response.mjs']and "base.foundationOracles?.protectedAbort?.counts?.total===29"in modules['validate-response.mjs'],'pure response-only view retains unchanged baseline29/classic19 validations')
expected=json.loads((D/'expected-interfaces.json').read_bytes());need(len(expected['oldBundleImports'])==17 and len(expected['expectedNewBundleImports'])==18 and set(expected['expectedNewBundleImports'])==set(expected['oldBundleImports'])|{'node:stream/consumers'},'exact17→18 residual bundle imports')
need(len(expected['outerImports'])==6 and expected['outerExports']==['wasi:http/incoming-handler@0.2.10']and all(n.endswith('@0.2.10')for n in expected['outerImports']),'expected six standard0.2.10 dependencies and sole HTTP export')
for n,key in [('future-source-publication.template.json','sourcePublicationAllowed'),('future-construction-action.template.json','actionAllowed')]:need(json.loads((D/n).read_bytes())[key]is False,'future action remains false '+key)
host_phase=json.loads((D/'future-host-phase.template.json').read_bytes())
need(host_phase['allHostActionsAllowed']is False and all(host_phase[k]is None for k in ['actualComponent','actualComponentAudit','independentComponentReview','rootComponentPhase','wasmtimeHTTPAuthority','washAuthority']),'future component/host authorities remain unissued')
for p0 in D.glob('*.py'):ast.parse(p0.read_text(),filename=str(p0))
save('rehashed-inputs.json',dict(schemaVersion=1,files=[dict(r,roles=sorted(r['roles']))for r in sorted(seen.values(),key=lambda r:r['path'])],ownerActionsInvoked=False))
save('source-boundaries.json',dict(schemaVersion=1,nativeBridge=str(bridge),nativeConfiguredSourceRoot=p['nativeConfiguredSourceRoot'],nativeFrozenSourceRoot=p['nativeFrozenSourceRoot'],packagingRoot=p['paths']['packagingRoot'],
 runtimeOnlyEngineSha256=p['normalRuntimeEngineSha256'],originalFamilyIndex=p['familyIndex'],payloadFiles=payload,liveInputs=c['liveInputs'],
 exactOldFixtureBlock=deriv,expectedInterfaces=expected,sourceOnly=True,noBodyAdapter=True))
save('results.json',dict(schemaVersion=1,state='INDEPENDENT_CONSUMERS355_HTTP_CONSTRUCTION_SOURCE_REVIEW_PASSED_V1',httpSourceIndexSha256=SHA,
 sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,sourceMembers=39,preparationRowsRehashed=12789,physicalClosureFiles=12667,physicalClosureLogicalBytes=1441957178,
 toolFiles=4892,toolTrees=2,toolLinks=22,snapshotFiles=1678,selectedNativeFrozenCopies=1164,nativeConfiguredSourceFiles=355,nativeFrozenSourceFiles=355,liveInputs=8,
 uniqueInputsRehashed=len(seen),publisherProposalAndPublishedContextsExplicit=True,actualGenuine355RuntimeOnlyBridgePreserved=True,noMetadataOrSourceProjection=True,
 unchangedProtectedGroups=29,unchangedClassicOrdinaryGroups=19,requestLocalConsumerFixtures=2,wholeOldFixtureOracleBlockByteExact=True,
 futureSourcePublication=None,futureBundle=None,futureComponent=None,futureHosts=None,wireBodyAdapter=False,
 actualPublisherPreflightHelperBundlerComponentGuestHostNativeActionsInvoked=False,reviewerReadHashSourcePythonAstOnly=True,
 operationalAdmission=False,runtimeAcceptanceClaim=False,timingAllowed=False,concreteBlockers=[],sourceChecks=len(checks),limitations=[
 'This is source approval only. Source copy, bundle, component, interface/typegraph and both-stock-host evidence do not yet exist for this new entry.',
 'The actual original355 bridge/native metadata/manifests remain genuine. No old342 metadata or selector acceptance was projected onto355.',
 'The source publisher and runtime actions require separate new Root authorities and independent actual publication/bundle/artifact reviews.',
 'Expected interfaces and nominal duration-only clock shape are future assertions, not a new binary observation.',
 'Two added consumer fixtures are ordinary request-local async iterables. They neither read wire request bodies nor provide a body reader/cancellation adapter.',
 'Response projection is a data-validation view only and preserves baseline/protected29/classic19 obligations.',
 'Source counters are not physical request/instance reuse/reset, GC/rooting/ownership, heap, performance, full streams/consumers/Node HTTP/crypto or roadmap acceptance.',
 'No owner helper/preflight/publisher/bundler/componentizer/Jco/parser CLI/guest/native/HTTP host/request action was invoked by the reviewer.']))
print(json.dumps(dict(sourceReviewPassed=True,sourceMembers=39,preparationRows=12789,closureFiles=12667,uniqueInputs=len(seen),checks=len(checks))))
