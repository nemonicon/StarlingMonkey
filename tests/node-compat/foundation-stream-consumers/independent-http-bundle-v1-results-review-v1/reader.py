"""Actual whole-bundle read/hash/JSON review; no owner or guest execution."""
from pathlib import Path
import collections,hashlib,json,math,os,stat
P=Path(__file__).resolve().parent;S=P.parent/'http-construction-candidate-v1';OUT=Path('/private/tmp/starling-node-compat/consumers355-http-bundle-v1')
SOURCE='dc98f4653eec1719e07d64ecfa8eb93ecfea1748bb3640521e0ac2a7e6aa5487';PUB='37fe3e00e33b195a808362e4119c12fdea9fb36acaeefcaebd8d61601ec8b67e';ENGINE='b227a8d2e6fb6b83da556d3520dceec82d5e1978801ba3c607bc9a31aa28ad60'
seen={};phys={};checks=0
def need(v,m):
 global checks
 if not v:raise AssertionError(m)
 checks+=1
def ident(s):return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
def digest(p):
 h=hashlib.sha256();n=0
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b);n+=len(b)
 return h.hexdigest(),n
def row(p):h,n=digest(p);return dict(path=str(p),sha256=h,bytes=n)
def verify(r,role):
 p=Path(r['path']);need(p.is_file()and not p.is_symlink(),'ordinary input '+str(p));real=str(p.resolve());need(real==str(p)or str(p).startswith('/tmp/')and real=='/private'+str(p),'only declared system/tmp context')
 a=p.stat()
 if real not in phys:
  h,n=digest(p);b=p.stat();need(ident(a)==ident(b),'stable streamed read');phys[real]=dict(sha256=h,bytes=n,identity=ident(b))
 else:need(ident(a)==phys[real]['identity'],'repeated source input unchanged')
 need(phys[real]['sha256']==r['sha256']and phys[real]['bytes']==r['bytes'],'full exact input '+str(p))
 if str(p)not in seen:seen[str(p)]={k:r[k]for k in ['path','sha256','bytes']};seen[str(p)]['roles']=set()
 seen[str(p)]['roles'].add(role);return r
def data(r,role='data'):verify(r,role);return json.loads(Path(r['path']).read_bytes())
def local(n):need(isinstance(n,str)and n and not n.startswith('/')and '\\'not in n and '\0'not in n and all(x not in ['', '.', '..']for x in n.split('/')),'safe local name');return n
def index(r,count=None):
 x=data(r,'index');need(x['schemaVersion']==1 and isinstance(x['files'],list),'finite index')
 if count is not None:need(len(x['files'])==count,'exact finite count '+str(count))
 rows=[];names=set()
 for v in x['files']:
  n=local(v['path']);need(n not in names,'unique member');names.add(n);q=dict(path=str(Path(r['path']).parent/n),sha256=v['sha256'],bytes=v['bytes']);verify(q,'indexed-member');rows.append(q)
 return x,rows
def exact(a,b,label):
 # JSON numbers have a single JS Number domain; booleans remain distinct.
 if type(a)in [int,float]and type(b)in [int,float]:need(a==b,label+' number');return
 need(type(a)is type(b),label+' type')
 if isinstance(b,dict):
  need(set(a)==set(b),label+' keys')
  for k in b:exact(a[k],b[k],label+'.'+k)
 elif isinstance(b,list):
  need(len(a)==len(b),label+' length')
  for i,(x,y)in enumerate(zip(a,b)):exact(x,y,label+'['+str(i)+']')
 else:need(a==b,label+' value')
def save(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
rootrow=dict(path=str(P.parent/'http-bundle-v1-root-results.json'),sha256='f2d7f8e4699b3cecc5901bff4871f9316677353d4c0e04ea6127535292728615',bytes=6967)
root=data(rootrow,'Root-completed-bundle-result')
for k in ['sourceIndex','rootAction','config','externalTerminal','externalLaunch','started','externalStdout','externalStderr','index','result','completion','bundle','graph','rawBundleMetadata','privateActual355WorkerDescriptor','workerTerminal','engine','metadata']:verify(root[k],'Root-'+k)
need(root['sourceIndex']['sha256']==SOURCE and root['publicationIndexSha256']==PUB and root['engine']['sha256']==ENGINE,'exact source/publication/native tuple')
sx,srows=index(root['sourceIndex'],39)
for proof,count in [(root['sourceReview'],8),(root['publicationReview'],7)]:
 ix,rs=index(proof['index'],count);data(proof['result'],'prior-independent-proof')
 ledger=data(next(r for r in rs if r['path'].endswith('/rehashed-inputs.json')),'complete-prior-context-ledger')
 for r in ledger['files']:verify(r,'full-native-source-tool-publication-context')
action=data(root['rootAction'],'Root-bundle-only-authority');config=data(root['config'],'private-config')
need(action['state']=='ROOT_REVIEWED_CONSUMERS355_HTTP_CONSTRUCTION_V1'and action['action']=='bundle-source'and action['actionAllowed']is True and action['sourceIndexSha256']==SOURCE and action['engineSha256']==ENGINE,'new bundle-only authority')
for k in ['ordinaryGuestExportsAllowed','hostRequestsAllowed','wireBodyAdapterAllowed','metadataProjection','operationalAdmission','runtimeAcceptanceClaim']:need(action[k]is False,'no extra authority '+k)
need(config['sourceIndexSha256']==SOURCE and config['action']=='bundle-source'and config['rootAction']==root['rootAction'],'actual caller config binding')
terminal=data(root['externalTerminal'],'parent-raw-terminal');started=data(root['started'],'actual-started')
need(terminal['pid']==19432 and terminal['rawExitCode']==0 and terminal['timeout']is False and terminal['parentOwnedGroupGone']is True,'retained parent raw0/clean')
for k in ['stdout','stderr']:verify(terminal[k],'parent-'+k)
need(terminal['stderr']['bytes']==0 and terminal['argv'][1]=='/private/tmp/starling-node-compat/consumers355-http-source-v1/run.mjs'and json.loads(terminal['argv'][2])==root['config'],'actual published caller and full raw streams')
need(started['pid']==terminal['pid']and started['argv']==terminal['argv'],'external launch/terminal identity')
ix,rows=index(root['index'],19);by={str(Path(r['path']).relative_to(OUT)):r for r in rows}
need({str(p.relative_to(OUT))for p in OUT.rglob('*')if p.is_file()}==set(by)|{'index.json','completion.json'},'exact19-indexed21-actual output')
need(not any(p.is_symlink()for p in OUT.rglob('*'))and all(p.stat().st_nlink==1 for p in OUT.rglob('*')if p.is_file()),'ordinary single-link complete output')
result=data(root['result'],'parent-result');complete=data(root['completion'],'parent-completion')
for k,r in [('index',root['index']),('result',root['result'])]:need(complete[k]==dict(r,path=Path(r['path']).name),'parent completion '+k)
need(json.loads(Path(terminal['stdout']['path']).read_bytes())==dict(index=complete['index'],completion=dict(path='completion.json',sha256=root['completion']['sha256'],bytes=root['completion']['bytes'])),'whole parent stdout decoded')
wt=data(root['workerTerminal'],'owned-worker-terminal')
for k,v in dict(status=0,signal=None,spawnError=None,timedOut=False,externalSignal=None,outputLimitExceeded=False,closed=True,ownedGroupGone=True,terminalExitZeroObserved=True).items():need(wt[k]==v,'owned clean terminal '+k)
need(wt['errors']==[]and wt['signals']==[]and wt['pid']==19665 and wt['timeoutMs']==600000 and wt['maxOutputBytes']==16777216,'actual bounded full worker outcome')
for k in ['stdout','stderr']:verify(wt[k],'owned-worker-'+k)
need(wt['stderr']['bytes']==0 and wt['args'][0]=='/private/tmp/starling-node-compat/consumers355-http-source-v1/worker.mjs'and json.loads(wt['args'][1])==root['privateActual355WorkerDescriptor'],'actual own published worker/private descriptor')
wc=data(by['worker/completion.json'],'worker-completion');wi,wrows=index(by['worker/index.json'],11)
for k,r in [('index',by['worker/index.json']),('result',by['worker/results.json'])]:need(wc[k]==dict(r,path=Path(r['path']).name),'worker completion '+k)
need(json.loads(Path(wt['stdout']['path']).read_bytes())==dict(index=wc['index'],completion=dict(path='completion.json',sha256=by['worker/completion.json']['sha256'],bytes=by['worker/completion.json']['bytes'])),'whole worker stdout decoded')
d=data(root['privateActual355WorkerDescriptor'],'actual-private355-frame');frame=d['frame'];p=d['prerequisites'];metadata=data(root['metadata'],'actual-native-sidecar');pins=data(p['reviewedPins'],'genuine-four-native-pins')
exact(frame['metadata'],metadata,'whole unprojected captured355 metadata');exact(frame['pin'],pins['variants']['normal-runtime'],'whole actual pin')
need(len(metadata['sourceManifest'])==355 and metadata['entropyPolicy']=='runtime-only'and metadata['gcStress']is False and metadata['streamConsumersEnabled']is True,'genuine consumers355 RuntimeOnly selection')
need(frame['admissionSourceRoot']==p['nativeConfiguredSourceRoot']and frame['runtimeSourceRoot']==frame['sourceRoot']==p['nativeFrozenSourceRoot'],'captured configured/frozen context spellings')
manifests={r['path']:json.loads((Path(frame['sourceRoot'])/r['path']).read_bytes())for r in metadata['sourceManifest']if '/export-manifest' in r['path']}
need(len(manifests)==len(frame['selectedManifests'])==11,'all eleven native manifests')
for m in frame['selectedManifests']:need(sum(m==v for v in manifests.values())==1,'captured native manifest equals exact frozen source data')
need({json.dumps(m,sort_keys=True)for m in frame['selectedManifests']}=={json.dumps(m,sort_keys=True)for m in manifests.values()},'exact complete unique native manifest set')
core=frame['coreExpectations'];need(core['coreVersion']=='sm-node-22.14.0-m0.11','unchanged native core')
for name,sha in core['sourceHashes'].items():need(next(r['sha256']for r in metadata['sourceManifest']if r['path']==name)==sha,'actual core source pin')
g=data(root['graph'],'actual-whole-entry-graph');raw=data(root['rawBundleMetadata'],'actual-raw-bundle-metadata')
need(g['sourceIndexSha256']==SOURCE and g['publicationIndexSha256']==PUB and g['engineSha256']==ENGINE and g['metadataSha256']==root['metadata']['sha256']and g['bundle']==root['bundle'],'whole graph provenance tuple')
need(raw==dict(imports=g['imports'],exports=g['exports'],moduleIds=g['modules']),'raw emitted module metadata matches graph')
expected=json.loads((S/'expected-interfaces.json').read_bytes());need(g['imports']==root['bundleImports']==expected['expectedNewBundleImports']and g['exports']==['incomingHandler'],'actual eighteen residual imports and only handler export')
need(g['protectedGroups']==29 and g['classicOrdinaryGroups']==19 and g['consumerRequestFixtureGroups']==2 and g['wireRequestBodyRead']is False and g['componentizerInvoked']is False and g['hostRequestsInvoked']is False,'bundle scope preserves29/19/two local fixtures; no component/host action')
base=Path(p['paths']['baselineEntry']);need(row(base)['sha256']==g['baselineSha256']==p['baselineSource']['sha256']and base.read_bytes()==Path(p['actualAcceptedBaselineSource']['path']).read_bytes(),'entire accepted baseline source unchanged')
need(row(Path('/private/tmp/starling-node-compat/consumers355-http-source-v1/classic-ordinary.mjs'))['sha256']==g['classicOrdinarySha256']and row(Path(p['paths']['classicChecks']))['sha256']==g['classicChecksSha256'],'actual ordinary19/check source')
virtual={};json_text={}
for r in g['virtualModules']:
 rr=dict(path=str(OUT/'worker'/r['path']),sha256=r['sha256'],bytes=r['bytes']);verify(rr,'actual-virtual-source')
 text=Path(rr['path']).read_text();need(text.startswith('export default ')and text.endswith(';'),'whole finite JSON virtual module');payload=text[len('export default '):-1];virtual[r['id']]=json.loads(payload);json_text[r['id']]=payload
need(len(virtual)==6 and all('\0'+n in g['modules']for n in virtual),'six actual virtual source IDs/data map graph')
exact(virtual['node-compat:core-expectations'],{k:core[k]for k in ['schema','coreVersion','allocUnsafePolicy','unsupportedStatic','prototypeRefusals']},'whole actual guest core semantic expectations')
exact(virtual['node-compat:entropy-policy'],'runtime-only','native entropy virtual data')
# Independent deterministic Buffer-oracle DATA regeneration (no Buffer/guest).
state=0x57415349
def random():
 global state
 state=(state^(state<<13))&0xffffffff;state=(state^(state>>17))&0xffffffff;state=(state^(state<<5))&0xffffffff;return state
def canonical_string(s):return s.encode('utf-16-le','surrogatepass').decode('utf-16-le','surrogatepass')
strings=[];bytes_rows=[]
def string(s,encoding):
 s=canonical_string(s);units=s.encode('utf-16-le','surrogatepass');chars=[units[i]|units[i+1]<<8 for i in range(0,len(units),2)]
 if encoding.lower()=='hex':
  result=bytearray()
  for i in range(0,len(chars)-1,2):
   pair=''.join(chr(x)for x in chars[i:i+2])
   if any(x not in '0123456789abcdefABCDEF'for x in pair):break
   result.append(int(pair,16))
  b=bytes(result);text=b.hex();length=len(chars)//2
 else:b=units.decode('utf-16-le','replace').encode('utf8');text=b.decode('utf8');length=len(b)
 strings.append(dict(input=s,encoding=encoding,bytes=list(b),text=text,byteLength=length))
for s,e in [('hello','utf8'),('é😀','UTF-8'),('\ufeffBOM','utf8'),('\ud800','utf8'),('0001ff','hex'),('AbCd','HEX'),('a','hex'),('12x4','hex'),('12é4','hex'),('12\0a','hex'),('','hex')]:string(s,e)
for prefix in ['', '1','12','123','1234']:
 for invalid in ['x','\0','é','\u0100','\ud800','\udfff','😀','\uffff']:
  for middle in ['', 'a']:string(prefix+middle+invalid+'beef','hex')
alphabet='0123456789abcdefABCDEF'
for i in range(220):
 s=''.join(alphabet[random()%len(alphabet)]for _ in range(random()%257))
 if i&3==0:
  at=random()%(len(s)+1);s=s[:at]+['x','\0','\ud800','é'][random()%4]+s[at:]
 string(s,'HEX'if i&1 else'hex')
for i in range(70):string(''.join(chr(random()&0xffff)for _ in range(random()%80)),'utf8')
for i in range(250):
 value=[random()&255 for _ in range(i if i<8 else random()%513)];b=bytes(value);bytes_rows.append(dict(value=value,hex=b.hex(),text=b.decode('utf8','replace')))
exact(virtual['node-compat:oracle-vectors'],dict(seed='0x57415349',strings=strings,bytes=bytes_rows),'whole independent xorshift/UTF8/hex oracle data')
pack=Path(p['paths']['packagingRoot'])/'tests/node-compat'
def load(relative):return json.loads((pack/relative).read_bytes())
def manifest(name):return next(m for m in frame['selectedManifests']if name in m['modules'])
glob=load('foundation-path/glob-results.json');path_corpus=dict(lexical=load('foundation-path/lexical-vectors.json'),globs=load('foundation-path/glob-vectors.json'),denied=glob['denied'],acceptedAdversarial=glob['acceptedAdversarial'],exportNames=sorted(manifest('node:path')['modules']['node:path']['exports']))
exact(virtual['node-compat:path-oracles'],path_corpus,'whole path oracle data');decoder=load('foundation-string-decoder/component-corpus.json');exact(virtual['node-compat:string-decoder-oracles'],decoder,'whole decoder corpus')
stream_expected=dict(names=sorted(manifest('node:stream/web')['modules']['node:stream/web']['exports']))
for name,path in dict(codecs='candidate/codec-node-results.json',guards='candidate/byob-node-results.json',views='candidate/typed-view-node-results.json',controllers='candidate/controller-node-results.json',iteration='iteration/node-results.json',data='dataview/node-results.json').items():stream_expected[name]=load('foundation-stream-web/'+path)
exact(virtual['node-compat:stream-web-installed-oracles'],stream_expected,'whole installed stream-web oracle data')
fo=g['foundationOracles'];events=load('foundation-events/native-node-results.json');assertion=load('foundation-assert/native-node-results.json');query=load('foundation-querystring/native-node-results.json');util=load('foundation-util/native-node-results.json');abort=load('foundation-add-abort/production-native-m0.10/node-results.json')
need(fo['path']==dict(lexical=len(path_corpus['lexical']),globs=len(path_corpus['globs']),budgets=len(path_corpus['denied']),acceptedAdversarial=len(path_corpus['acceptedAdversarial']),corpusSha256=hashlib.sha256(json_text['node-compat:path-oracles'].encode()).hexdigest()),'actual path provenance counts/full JSON hash')
exact(fo['events'],dict(cases=len(events['cases']),nativeCases=len(events['nativeCases']),profile=events['profile'],facadeSha256=events['facadeSha256']),'events oracle summary')
exact(fo['assert'],dict(cases=assertion['cases'],profile=assertion['sourceProfile']),'all assertion oracle cases');exact(fo['querystring'],dict(cases=query['cases'],profile=query['sourceProfile']),'all querystring oracle cases');exact(fo['util'],dict(variants=util['variants'],expectedExports=util['expectedExports']),'all util oracle data')
need(fo['stringDecoder']==dict(sequences=len(decoder['sequences']),writes=sum(len(s['chunks'])for s in decoder['sequences']),genericCases=len(decoder['decoderCases']),preservedOrderingDeviations=len(decoder['deviations']),corpusSha256=hashlib.sha256(json_text['node-compat:string-decoder-oracles'].encode()).hexdigest()),'decoder provenance all counts/hash/deviations')
for k in ['publicCases','nestedOnceCases','receiverCases']:exact(fo['protectedAbort'][k],abort[k],'protected full oracle '+k)
exact(fo['protectedAbort']['counts'],dict(public=16,nested=4,receivers=9,total=29),'all protected29 groups');exact(fo['protectedAbort']['nodeSymbol'],abort['targetSymbolInfo'],'protected Node symbol data')
need(fo['protectedAbort']['admission']==frame['report']and fo['protectedAbort']['profileVersion']=='sm-node-22.14.0-m0.10','new genuine355 fixture-data report, not old action projection')
for name,sha in fo['protectedAbort']['sources'].items():need(row(pack/'foundation-add-abort/production-native-m0.10'/name)['sha256']==sha,'protected exact source '+name)
need(fo['streamWeb']['oracleCorpusSha256']==hashlib.sha256(json_text['node-compat:stream-web-installed-oracles'].encode()).hexdigest()and fo['streamWeb']['names']==stream_expected['names'],'full streamWeb virtual data hash/names')
need(fo['fixtureSha256']==g['baselineSha256']and fo['dynamicBareAliases']==['buffer','child_process','path','path/posix','path/win32','events','string_decoder','assert','assert/strict','querystring','util','util/types','sys','stream/web'],'all baseline/computed-bare alias provenance')
exact(fo['protectedAbort'],dict(counts=abort['passed'],publicCases=abort['publicCases'],nestedOnceCases=abort['nestedOnceCases'],receiverCases=abort['receiverCases'],nodeSymbol=abort['targetSymbolInfo'],names=sorted(manifest('node:events')['modules']['node:events']['exports']),profileVersion='sm-node-22.14.0-m0.10',oracleSha256=row(pack/'foundation-add-abort/production-native-m0.10/node-results.json')['sha256'],sources={n:row(pack/'foundation-add-abort/production-native-m0.10'/n)['sha256']for n in ['component.mjs','public-cases.mjs','require.cjs']},admission=frame['report'],scope='29 positive/handled groups only; fatal initialized/deployed fixtures remain in the separate focused runner'),'complete protected29 oracle provenance')
contract=load('foundation-stream-web/production-candidate/native-preflight-contract.json');source_pins=contract['nativeGuardSources']+[contract['decoderSource'],dict(path=contract['kernelPath'],sha256=contract['kernelSha256']),dict(path=contract['manifestPath'],sha256=contract['manifestSha256'])]
exact(fo['streamWeb']['nativeSourcePins'],source_pins,'all streamWeb source pins');need(all(next(r['sha256']for r in metadata['sourceManifest']if r['path']==pin['path'])==pin['sha256']for pin in source_pins),'virtual data binds actual installed355 streamWeb sources')
exact(fo['streamWeb'],dict(names=stream_expected['names'],profileVersion=manifest('node:stream/web')['profileVersion'],oracleCorpusSha256=hashlib.sha256(json_text['node-compat:stream-web-installed-oracles'].encode()).hexdigest(),nativeSourcePins=source_pins,limitations=['Fixed attached unshared BufferSources, bounded UTF-8 codecs and min1 BYOB only','Explicit deferred compression; known controller signal, error-code, proxy/layout and lifecycle gaps remain']),'complete streamWeb provenance including limits')
published=Path('/private/tmp/starling-node-compat/consumers355-http-source-v1')
composer='import {createIncomingHandler as original} from '+json.dumps(p['paths']['originalHandler'])+';\n'+'import {runClassic19} from '+json.dumps(str(published/'classic-ordinary.mjs'))+';\n'+'import {runConsumerHttpProbe} from '+json.dumps(str(published/'consumer-probes.mjs'))+';\n'+'''export function createIncomingHandler(runBaseline){return original(async()=>{
 const baseline=JSON.parse(await runBaseline());
 if(baseline.failure)return JSON.stringify({consumerCombinedSchema:1,joint:{combinedSchema:1,baseline,classic:null,failure:baseline.failure},consumers:null,failure:baseline.failure});
 const classic=await runClassic19();const consumers=await runConsumerHttpProbe();
 return JSON.stringify({consumerCombinedSchema:1,joint:{combinedSchema:1,baseline,classic},consumers});
 });}
'''
need(hashlib.sha256(composer.encode()).hexdigest()==g['composerSha256'],'full composer source independently reconstructed and hash bound')
(P/'derived-composer-data.mjs.txt').write_text(composer)
module_rows=[];categories=collections.Counter()
for name in g['modules']:
 if name.startswith('\0node-compat:'):need(name[1:]in virtual,'known actual JSON virtual ID');categories['jsonVirtual']+=1;module_rows.append(dict(id=name,kind='actual-retained-json-virtual'))
 elif name=='\0sm-consumers355-http-composer-v1':categories['composer']+=1;module_rows.append(dict(id=name,kind='pinned-finite-composer-source',source=str(Path(d['outputRoot']).parent.parent/'consumers355-http-source-v1/composer.mjs')))
 elif name.endswith('.cjs.native-profile.mjs'):
  original=Path(name[:-len('.native-profile.mjs')]);need(original.is_file(),'CJS synthetic identity has actual original source');verify(row(original),'actual-CJS-original');categories['literalCjs']+=1;module_rows.append(dict(id=name,kind='literal-CJS-lowering',original=row(original)))
 else:need(Path(name).is_file(),'all physical graph modules exist');verify(row(Path(name)),'actual-physical-module');categories['physical']+=1;module_rows.append(dict(id=name,kind='physical',source=row(Path(name))))
need(dict(categories)==dict(jsonVirtual=6,composer=1,literalCjs=9,physical=37),'complete53-module classified graph')
need(len(g['modules'])==len(set(g['modules']))==53,'unique actual whole-entry graph')
save('module-and-oracle-audit.json',dict(schemaVersion=1,moduleCategories=dict(categories),modules=module_rows,virtualModules=g['virtualModules'],allSixVirtualDataComparedCompletely=True,
 independentCoreVectorStrings=len(strings),independentCoreVectorByteRows=len(bytes_rows),foundationOracles=g['foundationOracles'],all29ProtectedCaseDataRetained=True,
 codeAndGraphAreDataNotImported=True,originalBundle=root['bundle'],originalGraph=root['graph']))
save('rehashed-inputs.json',dict(schemaVersion=1,files=[dict(r,roles=sorted(r['roles']))for r in sorted(seen.values(),key=lambda r:r['path'])],physicalFilesHashed=len(phys),ownerActionsInvoked=False))
save('data-results.json',dict(schemaVersion=1,dataReviewPassed=True,sourceIndexSha256=SOURCE,publicationIndexSha256=PUB,engineSha256=ENGINE,
 rootResult=rootrow,sourceIndex=root['sourceIndex'],sourceReview=root['sourceReview'],publicationReview=root['publicationReview'],rootAction=root['rootAction'],config=root['config'],
 actualIndex=root['index'],actualResult=root['result'],actualCompletion=root['completion'],externalParentTerminal=root['externalTerminal'],ownedWorkerTerminal=root['workerTerminal'],
 originalBundle=root['bundle'],originalGraph=root['graph'],nativeEngine=root['engine'],nativeMetadata=root['metadata'],privateActual355WorkerDescriptor=root['privateActual355WorkerDescriptor'],
 bundleRawExitCode=0,parentOwnedGroupGone=True,workerRawExitCode=0,workerOwnedGroupGone=True,actualIndexedFiles=19,actualRegularFiles=21,
 moduleCategories=dict(categories),actualGraphModules=53,fullActualSourceFiles=355,actualSelectedManifests=11,allSixVirtualDataComparedCompletely=True,
 independentCoreVectorStrings=len(strings),independentCoreVectorByteRows=len(bytes_rows),wholeEntryAndFixtureClosureVerified=True,
 componentizerInvoked=False,ordinaryGuestExportsInvoked=False,hostRequestsInvoked=False,wireBodyAdapter=False,operationalAdmission=False,runtimeAcceptanceClaim=False,
 reviewerReadHashJsonDataOnly=True,reviewerHelpersBundlerComponentGuestHostNativeActionsInvoked=False,uniqueDeclaredInputsVerified=len(seen),physicalFilesHashed=len(phys),checks=checks))
print(json.dumps(dict(dataReviewPassed=True,modules=53,categories=dict(categories),virtualData=6,coreStrings=len(strings),coreByteRows=len(bytes_rows),physicalFilesHashed=len(phys))))
