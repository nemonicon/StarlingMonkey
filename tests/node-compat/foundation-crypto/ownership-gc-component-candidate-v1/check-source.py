"""Source/data/AST only. No owner module or runtime/helper action is imported."""
from pathlib import Path
import ast,copy,hashlib,json,os,stat
O=Path(__file__).resolve().parent;K=O.parent;G=K/'ownership-gc-candidate-v2'
checks=[]
def check(name,value):assert value,name;checks.append(dict(name=name,passed=True))
def refuse(name,fn):
 try:fn()
 except (AssertionError,KeyError,ValueError,TypeError):check(name,True)
 else:raise AssertionError(name+' accepted')
def h(path):
 v=hashlib.sha256()
 with Path(path).open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):v.update(b)
 return v.hexdigest()
# Actual donor derivations, no normal source/root/pin projection.
proof=json.loads((O/'construction-derivations.json').read_bytes())
for row in proof['derived']:
 text=(O/row['file']).read_text()
 for delta in reversed(row['changes']):assert text.count(delta['after'])==1;text=text.replace(delta['after'],delta['before'])
 check('byte-exact reversal '+row['file'],text==Path(row['donor']['path']).read_text() and h(row['donor']['path'])==row['donor']['sha256'])
p=json.loads((O/'prerequisites.json').read_bytes());check('exact unchanged reviewed GC guest',h(p['guest']['path'])==p['guest']['sha256']=='08d5f7f49e253baef92fdcd668349c481554f8245c80a25432b882188bdd8c40')
check('unchanged real four-function WIT',h(p['wit']['path'])==p['wit']['sha256']=='18d499ca3c93ad6ad771087d4bbb36500a329e4acf323517b6a88a0241e4fa4d')
# Execute only pure collector functions/constant definitions extracted via Python AST.
collector=G/'collector.py';nodes=[]
for n in ast.parse(collector.read_bytes()).body:
 if isinstance(n,ast.FunctionDef)or isinstance(n,ast.Assign):nodes.append(n)
env={'json':json};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(collector),'exec'),env)
c=json.loads((O/'collector-contract.json').read_bytes());normal=json.loads(Path(c['acceptedNormalExpectedRecord']['path']).read_bytes());expected=json.loads(Path(c['completeExpected']['path']).read_bytes())
check('whole typed GC expected matches genuine collector',env['expected'](normal)==expected)
env['validate'](expected,expected);check('full collector positive DATA fixture',True)
check('exact scoped request deltas',[r['gcObservation']['publicGcPressureRequests']for r in expected['records']]==[4,4,8,0])
check('outer16 schema2 and native count unobserved',expected['schemaVersion']==2 and expected['gcObservation']['publicGcPressureRequests']==16 and expected['pressure']['actualNativeGcCountObserved']is False)
for label,mutator in [
 ('full tag mismatch',lambda x:x['records'][0]['result']['operations'].__setitem__('firstSignatureHex','0'*64)),
 ('run3 request truthfulness',lambda x:x['records'][3]['gcObservation'].__setitem__('publicGcPressureRequested',True)),
 ('partial missing run',lambda x:x['records'].pop()),
 ('counter mismatch',lambda x:x['records'][0]['counters'].__setitem__('runCalls',999)),
 ('pressure byte mismatch',lambda x:x['pressure']['records'][0].__setitem__('encodedHex','00'*64)),
 ('observed native count fabrication',lambda x:x['gcObservation'].__setitem__('actualNativeGcCountObserved',True)),
 ('unknown observation field',lambda x:x.__setitem__('extra',True)),
 ('typed bool changed to number',lambda x:x['gcObservation'].__setitem__('entropyRequested',0))]:
 value=copy.deepcopy(expected);mutator(value);refuse('typed collector rejects '+label,lambda v=value:env['validate'](v,expected))
# Existing module APIs and the concrete construction caller graph are source checks.
guard=(O/'guard.mjs').read_text();worker=(O/'build-worker.mjs').read_text();parent=(O/'build.mjs').read_text();bundle=(O/'bundle.mjs').read_text();artifact=(O/'artifact-guard.mjs').read_text();guest=Path(p['guest']['path']).read_text()
for name,value in [
 ('new GC bootstrap API called with genuine config',"cryptoOwnerGcBootstrapPreflight({configDescriptor:descriptor(root.gcBootstrapConfig)})"in guard),
 ('native and tooling contexts distinct',"bootstrapConfig.sourceIndex.path===p.nativeSourceIndex.path"in guard and "bootstrapConfig.toolingIndex.path===p.toolingIndex.path"in guard),
 ('configured and frozen roots explicit',"frame.nativeConfiguredSourceRoot===CONFIGURED"in guard and "frame.frozenSourceRoot===FROZEN+'/source'"in guard),
 ('normal pins not authority',"pins.state==='ROOT_REVIEWED_CRYPTO_OWNER355_ISOLATED_GC_BOOTSTRAP_V1'"in guard and "['normal-off','normal-runtime','disabled-off'].every(n=>pins.variants[n]===null)"in guard),
 ('actual bootstrap proof before API import',guard.index('bootstrapObservationModel(JSON.parse')<guard.index('await import(pathToFileURL(p.bootstrapEntry.path))')),
 ('independent actual bootstrap proof before API import',guard.index('const bootstrapPeer=await indexed')<guard.index('await import(pathToFileURL(p.bootstrapEntry.path))') and 'INDEPENDENT_CRYPTO_OWNER355_GC_BOOTSTRAP_REVIEW_PASSED_V1'in guard),
 ('full native artifact proof bound',"nativePeer.data.freezeReceiptSha256===p.freezeReceiptSha256"in guard and "nativePeer.data.sourceIndexSha256===p.nativeSourceIndex.sha256"in guard),
 ('only genuine native Buffer guest import',guest.count("import {Buffer} from 'node:buffer';")==1),
 ('GC observations removed stale broad boolean','gcOrEntropyRequested'not in guest and 'actualNativeGcCountObserved:false'in guest),
 ('no top-level pressure or key operations','const pressureRecords=[];let pressureRequests=0;'in guest and 'let rawKey=null,jwkKey=null'in guest),
 ('real whole-entry bundleProfile invocation','bundleProfile({rolldown:toolchain.rolldown,parseAst:toolchain.parseAst,input:code.path,builtinManifests:selectedManifests})'in bundle),
 ('no builtin replacement virtual injection','virtualModules'not in bundle and "JSON.stringify(value.imports)==='[\"node:buffer\"]'"in bundle),
 ('complete physical graph guarded','Unknown virtual helper refuses before componentization'in bundle and 'new Set(physical.map'in bundle),
 ('bounded bundle no clipping',"Buffer.byteLength(value.code,'utf8')<=32*1024*1024"in bundle),
 ('selected manifests file transmitted privately','selected-manifests.json'in parent and 'selectedManifests:descriptor({'in parent and 'await regular(d.selectedManifests)'in worker),
 ('bundle recorded before actual componentizer',worker.index("output.write('bundle-graph.json'")<worker.index('selected.componentize(source,options)')),
 ('selected package adapter passed actual options','componentOptions({engine:d.engine,adapter:packaging.adapter},wit)'in worker),
 ('zero actual imports audited','result.interfaceAudit.emittedImports.length===0'in worker),
 ('four-function actual ABI audit preserved','parsePublicWit(emitted)'in worker and 'checkTranspileMetadata(generated)'in worker and 'parsePublicDts(dts)'in worker and 'publicJSExports(toolchain.parseAst(glue' in worker),
 ('actual loader package file retained',"output.write('transpiled/package.json',Buffer.from('{\"type\":\"module\"}\\n'))"in worker),
 ('raw owned terminal persisted before assertions',parent.index('runOwnedCommand(')<parent.index('checkOwnedTerminal(status)')),
 ('process directory created before durable child',parent.index("mkdir(join(output.root,'processes')")<parent.index('runOwnedCommand(')),
 ('parent failure recheck before close','finally{try{await frame.recheck();}finally{await output.close();}}'in parent),
 ('worker failure recheck before close','finally{try{await recheck();}finally{await output.close();}}'in worker),
 ('future runtime remains refused','NEW_GC_RUNTIME_SOURCE_REVIEW_AND_ROOT_ACTION_REQUIRED'in artifact),
 ('new GC artifact tuple guard','INDEPENDENT_CRYPTO_OWNER355_GC_COMPONENT_ARTIFACT_REVIEW_PASSED_V1'in artifact and "value.engineSha256==='289df445"in artifact),
 ('no generated import by construction','await import(pathToFileURL(join(output'not in worker),
]:check(name,value)
# Check finite original source input contexts. No historical relative prep is followed.
v=json.loads((O/'input-freeze.json').read_bytes());seen=set();total=0
for row in v['files']:
 path=Path(row['path']);assert str(path)not in seen;seen.add(str(path));assert path.stat().st_size==row['bytes']and h(path)==row['sha256'],str(path);total+=row['bytes']
check('all original-context input hashes current',True)
root=Path(v['publicationRoot'])
for link in v['links']:
 path=root/link['destination'];check('exact tool link '+link['destination'],path.is_symlink()and os.readlink(path)==link['newLinkText']and path.resolve()==root/link['mappedTarget'])
# Data physical role inventory, including both trees and every22 mapped link.
rolemap=json.loads(Path(p['packagingMap']['path']).read_bytes());expected={r['path']:r for r in rolemap['files']};links={r['destination']:r for r in rolemap['links']};actualfiles=set();actuallinks=set()
for prefix in rolemap['roleRoots']:
 for path in (root/prefix).rglob('*'):
  rel=path.relative_to(root).as_posix()
  if path.is_symlink():assert rel in links;actuallinks.add(rel)
  elif path.is_file():
   row=expected[rel];assert stat.S_IMODE(path.stat().st_mode)==row['mode'];actualfiles.add(rel)
  elif path.is_dir():assert stat.S_IMODE(path.stat().st_mode)==0o700
check('complete physical package tool role membership',actualfiles==set(expected)and actuallinks==set(links))
result=dict(schemaVersion=1,state='SOURCE_DATA_GC_COMPONENT_CHECKS_PASSED_NO_ACTIONS_V1',checks=checks,count=len(checks),inputFiles=len(seen),inputBytes=total,toolLinks=len(links),physicalPackagingFiles=len(actualfiles),collectorWholeExpectedVerified=True,allOriginalHmacFieldsRetained=True,ownerModulesImported=False,collectorOnlyExtractedPureAst=True,bootstrapOrComponentizerInvoked=False,guestOrKeyOrGcExecuted=False)
(O/'source-check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(checks=len(checks),inputs=len(seen),toolLinks=len(links))))
