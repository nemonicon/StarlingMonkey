"""Actual descriptor/physical-context DATA, AST and source check. No action imports."""
from pathlib import Path
import ast,hashlib,json,os,stat,re
P=Path(__file__).resolve().parent;R=P.parents[3]
checks=0

def ck(v,m):
 global checks
 assert v,m;checks+=1

def load(p):return json.loads(Path(p).read_bytes())
def digest(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def d(p):return dict(path=str(p),sha256=digest(p),bytes=p.stat().st_size)
code=(P/'external.py').read_text();tree=ast.parse(code);functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
scope=dict(Path=Path,hashlib=hashlib,json=json,os=os,stat=stat)
exec(compile(ast.Module(body=[functions[n]for n in ['checked','read','family','package_context']],type_ignores=[]),'<extracted-read-hash-only>','exec'),scope)
refs=load(P/'references.json');inputs=load(P/'source-inputs.json');snap={}
for row in inputs['files']:
 p=scope['checked'](row);s=p.stat();snap[str(p)]=(row,(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,stat.S_IMODE(s.st_mode)));ck(True,'actual complete input hash')
for r in inputs['families']:scope['family'](r);ck(True,'complete source/proof original family')
scope['package_context'](refs);ck(True,'actual4889package files/21aliases/private root Source reader')
proof=load(refs['actualArtifactReview']['result']['path']);contract=load(refs['actualArtifactContract']['path']);ck(proof['artifacts']==contract['artifacts']==refs['artifacts']and proof['generatedFiles']==contract['generatedFiles']==refs['generatedFiles'],'whole actual artifact/generated tuples')
ck(proof['componentSha256']==refs['component']['sha256']=='5c002f8da675016fd7061d245074965413d6914e4f40eb2a32a8141c1f3b7460','actual immutable5c002 component')
ck(proof['nativeSourceFiles']==342 and proof['fullMetadataFields']==64 and proof['externalEmbeddingSources']==3 and proof['selectedManifestCount']==9,'genuine original342+3/64/9, no355 projection')
ck(proof['allThreeInlineCoreBytesEqual']is True and proof['physicalCoreWholeBytesEqual']is True and len(refs['inlineCoreModules'])==3,'entire actual four-core provenance')
metadata=load(refs['nativeMetadata']['path']);ck(len(metadata)==64 and len(metadata['sourceManifest'])==342 and len(metadata['componentizeSourceManifest'])==3 and len(metadata['selectedModuleManifests'])==9,'whole raw metadata shape')
ck(digest(refs['bundle']['path'])==refs['originalBundle']['sha256']=='8db23f2b6429cb4a6e7359d1371d65eacd6f278c892aba23a57195089c908d73'and refs['guest']['bytes']==772,'whole original ReactDOM bundle/guest')
report=load(refs['oracleEvidence']['report']['path']);case=next(r for r in report['cases']if r['id']=='react-dom-edge');command=next(r for r in report['commands']if r['name']=='node-react-dom-edge');ck(case['nodeControl']['value']==refs['oracleValue']and case['nodeControl']['status']=='passed'and json.loads(Path(command['stdout']['path']).read_bytes())==case['nodeControl'],'actual retained Node full raw JSON oracle')
for key,value in [('status',0),('signal',None),('spawnError',None),('timedOut',False),('closed',True),('ownedGroupGone',True),('outputLimitExceeded',False),('terminalExitZeroObserved',True),('errors',[]),('signals',[])]:ck(command[key]==value,'actual original Node control '+key)
# Assert the actual helper APIs/options from authenticated local sources, never import them.
jco=Path(refs['jcoApi']['path']).read_text();low=Path(refs['loaderPackageRoot'])/'node_modules/@bytecodealliance/jco-transpile/dist/transpile.js';lower=low.read_text()
ck('transpileComponent as transpile'in jco and 'transpileBytes(component, prepOpts(opts))'in(Path(refs['loaderPackageRoot'])/'node_modules/@bytecodealliance/jco/dist/cmd/transpile.js').read_text(),'genuine actual two-argument Jco byte API')
ck("'wasi:clocks/*': '@bytecodealliance/preview2-shim/clocks#*'"in lower and "'wasi:io/*': '@bytecodealliance/preview2-shim/io#*'"in lower and 'map: Object.entries(opts.map ?? {})'in lower,'actual #* mappings and option flow')
ck(refs['mappingOptions']==dict(name='clock_v13',wasiShim=False,map={'wasi:clocks/*':refs['shimClocksUrl']+'#*','wasi:io/*':refs['shimIoUrl']+'#*'}),'exact standard module maps without hidden capability adapter')
clocks=Path(refs['shimClocks']['path']).read_text();worker=Path(refs['loaderPackageRoot'])/'node_modules/@bytecodealliance/preview2-shim/dist/io/worker-io.js';sync=worker.parent.parent/'synckit/index.js'
ck('export const monotonicClock'in clocks and 'subscribeInstant(instant)'in clocks and 'subscribeDuration(duration)'in clocks and 'export const wallClock'in clocks,'actual standard clock exports')
ck('new Worker(new URL("./worker-thread.bundle.js"'in worker.read_text()and 'Atomics.wait(sharedBufferView, 0, 0, CALL_TIMEOUT)'in sync.read_text()and 'const CALL_TIMEOUT = undefined' in sync.read_text(),'real shim thread/unbounded in-process wait, external child deadline required')
entry=(P/'entry.mjs').read_text();body=(P/'body.mjs').read_text();models=(P/'models.mjs').read_text();wave=(P/'wave.mjs').read_text();donor=(R/'tests/node-compat/foundation-zlib/cost-wasmtime-transport-candidate-v1/scalar-transport.mjs').read_text()
start=donor.index('export function parseScalarStringOutput');end=donor.index('export function argvAccounting');ck(donor[start:end]in wave,'exact existing strict WAVE string reader')
for name,nextname in [('artifactModel','phaseModel'),('phaseModel','scalarRunArguments')]:
 a=models[models.index('export function '+name):models.index('export function '+nextname)]
 # entry follows phaseModel with nativeFrameModel; compare balanced exact function text only.
 a=a.rstrip();ck(a in entry,'same actual preimport authority predicate '+name)
ck(entry.index('for(const r of inputs.files)await c.file(r)')<entry.index('const {classicPreflight}=await import'),'full physical Source before genuine native custom import')
ck('await noExternalSearchRoots(refs.loaderPackageRoot)'in entry and 'await noExternalSearchRoots(f.refs.loaderPackageRoot)'in entry,'actual package dependency-resolution context before/final')
ck('finally{await f.recheck();}'in entry and 'finally{try{await c.recheck();}'in entry,'whole failed/complete admission/action bookends')
ck("await api.transpile(componentBytes,structuredClone(f.refs.mappingOptions))"in body and "await out.write('transpiled/'"in body,'genuine transpile into distinct fresh outputs; original glue untouched')
ck('All three inline core bytes unchanged'in models and 'Whole actual application engine core unchanged' in body,'all four actual core byte checks')
ck("const mapped=await reviewedMapped(f)"in body and "ROOT_REVIEWED_CLOCK_V13_MAPPED_OUTPUT_V1"in body and body.index('async function reviewedMapped')<body.index('await import(pathToFileURL(mapped.mapped'),'separate actual mapped-output proof before real app import')
ck("terminalModel(t)"in body and "args,write:"in body and "timeoutMs:f.root.ownedWorkerDeadlineMs"in body,'genuine external child deadline/raw collection')
ck("['run','--invoke','run()',f.refs.component.path]"in body and 'rawDurablyRetained:true' in body,'actual stock CLI WAVE invocation, raw-first parser')
ck("for(const scenario of ['retained','fresh'])"in body and "scenario==='retained'?3:1"in body and 'n<3' in body,'complete retained3/fresh1/threefreshWT schedule')
ck('new AggregateError([value,captureError]'in body and body.index("await write('raw/")<body.index('if(thrown)throw value'),'both original throw and raw writer failure preserved before checks')
ck('fullClockProfileAcceptance:false'in body and 'resourceDateSnapshotTimerTeardownSevenCaseGateComplete:false'in body,'no profile/teardown promotion from slice')
ck('monitor.monitor(argv,str(REPO),env,out,1200,root_row)'in code and 'finally:recheck()'in code and code.index('recheck();out=Path')<code.index('monitor=load_actual'),'genuine externally owned API/phase/source auth/finalfailure')
for name in ['entry.mjs','body.mjs','models.mjs','wave.mjs']:
 t=(P/name).read_text();ck('sys.modules'not in t and '.REPO='not in t and '.HERE='not in t and '.OUTPUT='not in t,'no old namespace/global/state rebinding')
for root in [refs['mappedOutputRoot'],refs['runtimeOutputRoot'],refs['mappedOutputRoot']+'-external-root',refs['runtimeOutputRoot']+'-external-root']:ck(not Path(root).exists()and not Path(root).is_symlink(),'dormant fresh output absent')
asts=[]
for p in P.glob('*.py'):ast.parse(p.read_text());asts.append(p.name);ck(True,'Python AST')
for path,(row,identity)in snap.items():
 p=Path(path);s=p.stat();ck(identity==(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,stat.S_IMODE(s.st_mode)),'final identity/mode');ck(digest(p)==row['sha256'],'final full input hash')
result=dict(schemaVersion=1,state='CLOCK_V13_REACTDOM_SOURCE_DATA_CHECKS_PASSED_V1',checks=checks,protectedFiles=len(inputs['files']),logicalBytes=sum(r['bytes']for r in inputs['files']),completeFamilies=len(inputs['families']),physicalPackageFiles=4889,physicalPackageAliases=21,pythonAsts=asts,actualJcoAndShimApisReadAsSourceOnly=True,actualComponentUsedAsData=refs['component'],nativePreflightOrJcoApiOrShimImported=False,generatedApplicationImported=False,componentOrGuestOrHostOrWasmtimeInvoked=False,fullClockProfileAcceptance=False)
(P/'source-check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
