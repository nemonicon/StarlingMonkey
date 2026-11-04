"""Independent read/hash/static construction review, no owner/helper execution."""
import hashlib,json,os,re,stat
from pathlib import Path
P=Path(__file__).resolve().parent;K=P.parent;C=K/'ownership-component-candidate-v1'
PIN='eb648e19274c055968557227221627e2ced5dd35a2c0fb17af941dbc9a8b5c30'
seen={};checks=[]
def need(v,m):
 if not v:raise AssertionError(m)
 checks.append(m)
def row(p,e=None):
 p=Path(p);s=p.lstat();need(stat.S_ISREG(s.st_mode),'Ordinary file '+str(p));h=hashlib.sha256()
 with p.open('rb')as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 d=dict(path=str(p),sha256=h.hexdigest(),bytes=s.st_size)
 if e:need(all(d[k]==e[k]for k in ('sha256','bytes')),'Exact file tuple '+str(p))
 seen[str(p)]=d;return d
def data(p):return json.loads(Path(p).read_bytes())
def write(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n')
def indexed(root,pin):
 need(row(root/'index.json')['sha256']==pin,'Exact indexed source/proof '+str(root));d=data(root/'index.json')
 for r in d['files']:row(root/r['path'],r)
 return d
def main():
 own=indexed(C,PIN);need(len(own['files'])==28,'28 final source files')
 inputs=data(C/'input-freeze.json');need(len(inputs['files'])==5059 and inputs['relocationIsNotActivation']is True and inputs['ownerActionsInvoked']is False,'5059 original source refs, no relocated action authority')
 for r in inputs['files']:row(r['path'],r)
 p=data(C/'prerequisites.json')
 for name in ['guestIndex','guest','wit','nativeSourceIndex','bootstrapEntry','reviewedNativePins','nativeRootReview','node']:row(p[name]['path'],p[name])
 for name in ['guestReview','nativeReview','publicationReview']:
  pair=p[name];ix=indexed(Path(pair['index']['path']).parent,pair['index']['sha256']);row(pair['result']['path'],pair['result']);need(sum(r['sha256']==pair['result']['sha256']and r['bytes']==pair['result']['bytes']and Path(pair['index']['path']).parent/r['path']==Path(pair['result']['path'])for r in ix['files'])==1,'Exactly indexed '+name+' result')
 indexed(Path(p['guestIndex']['path']).parent,p['guestIndex']['sha256']);indexed(Path(p['nativeSourceIndex']['path']).parent,p['nativeSourceIndex']['sha256'])
 native=data(p['nativeReview']['result']['path']);pins=data(p['reviewedNativePins']['path']);review=data(p['nativeRootReview']['path']);pin=pins['variants']['normal-off']
 need(native['engineSha256']==pin['engineSha256']==p['normalEngineSha256']=='36bd850895a11af8ffaefdb8296630222c4ad4652a0e58f45ce0ec23c1bebc05'and native['engineBytes']==pin['engineBytes']==10002820,'Actual new normal-only owner355 native tuple, not old350')
 need(pins['state']=='ROOT_REVIEWED_CRYPTO_OWNER355_VALIDATION_BOOTSTRAP_V2'and all(pins['variants'][n]is None for n in ['normal-runtime','gc-off','disabled-off']),'Only normal pin configured')
 need(review['reviewedPinsSha256']==p['reviewedNativePins']['sha256']and review['independentNativeReview']==p['nativeReview']and review['variants']['normal-off']['freezeReceiptSha256']==native['freezeReceiptSha256'],'Root native authority and actual independent proof crossbinding')
 need(native['sourceFiles']==355 and native['variant']=='normal-off'and native['ownerActionsInvoked']is False,'Expected actual proof fields present')
 mapping=data(C/'packaging-context.json');pub=Path(mapping['publicationRoot']);ixrow=mapping['publicationIndex'];row(ixrow['path'],ixrow);publication=data(ixrow['path'])
 need(ixrow['sha256']=='4621f7e72b4fb0555a5df630b1aedd4d2a04743b0db9188fc50099779f07387b'and mapping['originalZlibNativeFactsConsumed']is False and mapping['costActionStatesReused']is False,'Packaging source roles only, no old350 native/action projection')
 need(mapping['roleRoots']==['tools/toolchain','tools/packager','packaging']and len(mapping['files'])==4934 and mapping['toolFiles']==4890 and mapping['packagingFiles']==44,'Complete finite4934 package/tool role rows')
 published={r['path']:r for r in publication['files']};expected={r['path']:r for r in mapping['files']}
 need(len(expected)==4934 and set(expected)=={n for n in published if n.startswith(('tools/','packaging/'))},'Selected rows exactly equal all published tools/packaging members')
 for n,r in expected.items():
  need(all(r[k]==published[n][k]for k in ['sha256','bytes','mode']),'Role row actual published tuple '+n);q=pub/n;row(q,r);need(stat.S_IMODE(q.stat().st_mode)==r['mode']and q.stat().st_nlink==1,'Actual ordinary single-link mode '+n)
 s=pub.stat();need(s.st_dev==mapping['rootIdentity']['device']and s.st_ino==mapping['rootIdentity']['inode']and stat.S_IMODE(s.st_mode)==0o700,'Actual private publication identity')
 need(mapping['links']==publication['links']and len(mapping['links'])==22,'Exact22 mapped links from published source')
 linkmap={r['destination']:r for r in mapping['links']};files=set();links=set()
 def walk(base):
  for q in base.iterdir():
   n=q.relative_to(pub).as_posix()
   if q.is_symlink():
    need(n in linkmap and os.readlink(q)==linkmap[n]['newLinkText']and q.resolve()==pub/linkmap[n]['mappedTarget'],'Actual mapped link text/endpoint '+n);links.add(n)
   elif q.is_dir():need(stat.S_IMODE(q.stat().st_mode)==0o700,'Private package directory');walk(q)
   else:need(q.is_file()and n in expected,'No unindexed physical role member');files.add(n)
 for role in mapping['roleRoots']:need(not(pub/role).is_symlink(),'Ordinary role root');walk(pub/role)
 need(files==set(expected)and links==set(linkmap),'Exact physical role files/link membership')
 adapter=expected['packaging/host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm'];need(adapter['sha256']=='988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'and adapter['bytes']==53512,'Actual release53512 adapter')
 witrows=[n for n in expected if n.startswith('packaging/host-apis/wasi-0.2.10/wit/')];need(len(witrows)==7,'All7 existing standardWASI0.2.10 WIT files')
 mechanism=data(C/'mechanisms.json')
 for r in mechanism['copiedUnchanged']:
  need(row(r['origin'])['sha256']==r['sourceSha256']==r['afterSha256']==row(C/r['afterimage'])['sha256'],'Exact unchanged lifecycle/proof source '+r['afterimage'])
 ar=mechanism['authorityPrelude'];before=Path(ar['origin']).read_text();prelude=before[:before.index(ar['prefixEndsBefore'])].replace(ar['removedExactUnusedCostActionConstant'],'');need(prelude==(C/ar['afterimage']).read_text(),'Exact authority prelude, no oldcost action/native authority')
 parent=(C/'build.mjs').read_text();worker=(C/'build-worker.mjs').read_text();guard=(C/'guard.mjs').read_text();abi=(C/'abi.mjs').read_text();packaging=(C/'packaging.mjs').read_text();key=(C/'key-validation.mjs').read_text()
 need(guard.index('authorityModel(root,sourceSha)')<guard.index('await sourceIndex(ownIx)')<guard.index('await indexed(root.sourceIndependentReview')<guard.index('await loadPackaging(mapRow)')<guard.index('await import(pathToFileURL(p.bootstrapEntry.path))'),'Own/Root/indexedpeer/prerequisite/physical packaging before genuine bootstrap import')
 need("cryptoOwnerBootstrapPreflight({variant:'normal-off'"in guard and 'frame.metadata.sourceManifest.length===355'in guard and 'frame.configuredSourceRoot'in guard and 'sourceRoot:frame.sourceRoot'in guard,'Genuine new355 API and separate authentic contexts, no oldcost guard or invented sourceFiles field')
 need("await mkdir(join(output.root,'processes'),{mode:0o700})"in parent and parent.index("await mkdir(join(output.root,'processes')")<parent.index('await runOwnedCommand('),'Parent actually creates requiredprocesses0700 before owned lifecycle helper')
 need(parent.index('await componentPreflight(options)')<parent.index('await DurableOutput.create('),'No new outputs before full action preflight')
 need(worker.index('await sourceIndex(d.ownIndex)')<worker.index('await loadPackaging(d.mapRow)')<worker.index('await import(pathToFileURL(join(packaging.packagingRoot,\'tests/node-compat/toolchain.mjs\')))'),'Worker source/physical packaging before loader import')
 need('await recheck();await output.recheck();'in worker and 'await frame.recheck();await output.recheck();'in parent,'Pre/post success source/tool/artifact rechecks implemented')
 need('selected.componentize(source,options)'in worker and "worldName:'validation'"in abi and "selectedInterfaces:[]"in abi and "disableFeatures:['stdio','random','clocks','http','fetch-event']"in abi and "enableAot:false,env:{}"in abi,'Actual selected API/finite standard-WASI options; missing adapter handoff separately blocks')
 componentizer=(pub/'packaging/tests/node-compat/componentizer.mjs').read_text();toolchain=(pub/'packaging/tests/node-compat/toolchain.mjs').read_text()
 need('export async function loadToolchain()'in toolchain and 'parseAst' in toolchain and 'export async function loadComponentizer(toolchain' in componentizer and 'loaded.componentize(...publicArgs)'in componentizer and 'interfaceAudit' in componentizer,'Loader/selected componentize/options/audit API exists in actual pinned source')
 need(worker.index("output.write('crypto-owner.component.wasm'")<worker.index("result.interfaceAudit.emittedImports.length===0")and worker.index("output.write('emitted.wit'")<worker.index('parsePublicWit(emitted)')and worker.index("output.write('transpile-metadata.json'")<worker.index('checkTranspileMetadata(generated)'),'Actual component/WIT/transpile data retained before ABI/import assertions')
 need("NAMES=Object.freeze(['inspect','run','clear','validate'])"in abi and "run:1,clear:0,validate:0"in abi and 'Only terminal literal empty Jco helper'in abi and 'No default/star export'in abi and 'No ABI reassignment'in abi,'Finite4 scalar/dts/meta/JS-role policy, no generic extra-export allowance')
 need('await import(pathToFileURL(rows.glue.path)'not in worker and 'generatedModuleImported:false'in worker and 'ordinaryGuestExportsInvoked:false'in worker and 'keyOperationsInvoked:false'in worker,'Construction does not import generated guest or call key/ordinary exports')
 need("throw new Error('KEY_ACTION_SOURCE_SUCCESSOR_REQUIRED_AFTER_ACTUAL_COMPONENT_REVIEW')"in key,'Positive key-export action always unavailable pending separate successor')
 # Record the actual caller/options seam as source evidence; do not call it.
 dline=next(line for line in parent.splitlines()if 'const d={'in line);fields=re.findall(r'(?:[,{])([A-Za-z][A-Za-z0-9]*):',dline)
 need('adapter'not in fields and 'componentOptions(d,wit)'in worker and 'preview2Adapter:d.adapter.path'in abi and 'adapter,files:Object.freeze(rows)'in packaging,'Definite adapter caller/callee omission from actual descriptor')
 sourcefindings=[dict(id='CRYPTO-OWNER355-COMPONENT-ADAPTER-M1',state='CONSTRUCTION_SOURCE_HOLD',parentDescriptor=dict(path=str(C/'build.mjs'),line=17,fields=fields),workerCall=dict(path=str(C/'build-worker.mjs'),line=24,call='componentOptions(d,wit)'),callee=dict(path=str(C/'abi.mjs'),line=27,requires='d.adapter.path'),actualAuthenticatedAvailableValue='packaging.adapter from loadPackaging',sourceInference='The actual parent descriptor lacks adapter. The current callee would dereference undefined before selected.componentize, after selected loader imports.',actualConstructionAttemptObserved=False,requiredCorrection='Fresh immutable successor must explicitly pass the authentic loadPackaging().adapter into the real options caller, or capture/crosscheck a descriptor against it. Include a source/pure actual-descriptor-to-options seam regression, preserving28 old source bytes. Do not invent a path, default to npm adapter or change native metadata.'),dict(id='CRYPTO-OWNER355-FUTURE-KEY-TRANSPORT-LIMIT',state='OPEN_NONBLOCKING_CLOSED_FUTURE_KEY_ACTION_LIMIT',path=str(C/'key-validation.mjs'),line=6,scope='Unused future collector, no key action implemented.',detail='Nonfinite number envelopes remain nonfinite JSON values refused by plainJSON, and negative zero has no distinct envelope tag. Do not treat this as complete unexpected-primitive diagnostics or key-action readiness; source successor needed before actual key calls. No impact established on construction because key action is closed.')]
 future=data(C/'future-component-authority.template.json');futurekey=data(C/'future-key-authority.template.json')
 need(future['componentSourceIndexSha256']is None and future['sourceIndependentReview']is None and future['componentBuildAllowed']is False and future['componentInitializationAllowed']is False,'New construction action/sourcepeer remains null/refusing')
 need(futurekey['rootKeyExportsAllowed']is False and futurekey['actualComponentReview']is None and futurekey['actualLoadingProtocolReview']is None and futurekey['actualWasmtimeScalarProof']is None,'Key/root/loading/WT action gates remain closed')
 stored=data(C/'results.json');need(stored['pureChecks']==39 and stored['sourceDataChecks']==14901 and stored['parseChecks']==13 and stored['positiveBootstrapInvoked']is False and stored['componentizerInvoked']is False,'Stored owner39/14901/13 remain preparation evidence only')
 result=dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_COMPONENT_SOURCE_IDENTITY_VERIFIED_ADAPTER_HANDOFF_HOLD',componentSourceIndexSha256=PIN,sourceOnly=True,sourceIdentityAndClosureVerified=True,sourceReviewPassed=False,ownerActionsInvoked=False,requiredSourcePeerPassStateIssued=False,
  sourceFilesRehashed=28,originalInputRowsRehashed=5059,uniqueInputsRehashed=len(seen),physicalPackagingFilesVerified=4934,physicalToolFiles=4890,packagingFiles=44,physicalMappedLinksVerified=22,standardWasiWitFiles=7,releaseAdapterBytes=53512,
  normalNativeEngineSha256=p['normalEngineSha256'],normalNativeEngineBytes=10002820,nativeSourceFiles=355,nativeArtifactReviewIndexSha256=p['nativeReview']['index']['sha256'],nativePinDataSha256=p['reviewedNativePins']['sha256'],nativeRootReviewSha256=p['nativeRootReview']['sha256'],independentActualNativePinOrBootstrapReviewTransferred=False,
  otherConstructionMechanismsSourceConsistent=True,processLogDirectoryActuallyCreated=True,constructionBlockers=1,sourceFindings=sourcefindings,
  actualComponentConstructionOrInitializationExecutedByReviewer=False,actualGeneratedLoadingOrKeyOperationsApproved=False,
  futureComponentAuthority=None,futureKeyAuthority=None,operationalAdmission=False,runtimeAcceptanceClaim=False,
  limitations=['SOURCE identity/closure passes, but actual private descriptor to options handoff is blocked by M1.','No new actual4-scalar artifact/ESM/TLA/WT/key/async return proof is inferred.','Full physical packaging rows are packaging roles, never old350 native authority.','Fixed AST/ABI predicates are finite pinned-source checks, not general JavaScript semantic equivalence.','Closed future key collector is not complete primitive-transport or positive-key readiness.'])
 write('source-findings.json',sourcefindings);write('rehashed-inputs.json',[seen[k]for k in sorted(seen)]);write('static-checks.json',dict(passed=True,checks=len(checks),details=checks,ownerModulesOrTestsInvoked=False));write('results.json',result)
 print(json.dumps(dict(state=result['state'],inputs=len(seen),physicalFiles=len(files),links=len(links),blockers=1)))
if __name__=='__main__':main()
