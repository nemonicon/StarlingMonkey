"""Independent existing-result decoder/hash reader; never invokes owner/guest/Node."""
from pathlib import Path
from collections import Counter
import hashlib,json,os,re,stat,zlib
HERE=Path(__file__).resolve().parent;FAMILY=HERE.parent
SOURCE=FAMILY/'component-validation-activated-v8';SOURCE_SHA='8af9a2137b93802ae2f09e30219ad416675a9b10fdac1cdbcc18e48e937a9e56'
OUTPUT=Path('/tmp/starling-node-compat/production-zlib-v4-normal-off-codec-validation-v2')
ROOT_SHA='7b9ea59d0a7a69c817229257c991745223d82e5be37d497967058df0393400b7'
COMPONENT_SHA='465776b53e91d8d744de1b72f334d39518967551a22df390d327210d4748e283'
seen={};identities={}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path,h=None,size=None,capture=True,force=False):
 path=Path(path);a=path.lstat();assert stat.S_ISREG(a.st_mode)and not path.is_symlink(),path
 path=path.resolve(strict=True);key=str(path);identity=(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns)
 if not capture and not force and key in seen:
  assert identities[key]==identity,path;row=seen[key];assert h is None or row['sha256']==h,path;assert size is None or row['bytes']==size,path;return row
 digest=hashlib.sha256();blocks=[]if capture else None
 with path.open('rb')as stream:
  for block in iter(lambda:stream.read(1024*1024),b''):
   digest.update(block)
   if capture:blocks.append(block)
 b=path.stat();assert identity==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns),path
 assert h is None or digest.hexdigest()==h,path;assert size is None or b.st_size==size,path
 row={'path':key,'sha256':digest.hexdigest(),'bytes':b.st_size};assert key not in seen or seen[key]==row,path;seen[key]=row;identities[key]=identity
 return b''.join(blocks)if capture else row
def doc(path,h=None):return json.loads(read(path,h))
def encoded(value):return(json.dumps(value,indent=2)+'\n').encode()
def indexed(root,digest,count=None):
 value=doc(root/'index.json',digest);assert count is None or len(value['files'])==count;names=set()
 for row in value['files']:
  name=row['path'];assert name not in names and not Path(name).is_absolute()and all(p not in('','.','..')for p in name.split('/'));names.add(name);read(root/name,row['sha256'],row['bytes'],False)
 return value
assert not(HERE/'results.json').exists()
root=doc(FAMILY/'normal-codec-validation-v2-root-results.json',ROOT_SHA);assert root['rawExitCode']==0 and root['validationFamilyIndexSha256']==SOURCE_SHA and len(root['references'])==10
for row in root['references']:read(row['path'],row['sha256'],row['bytes'],False)
outer=doc(root['references'][0]['path']);assert outer['rawExitCode']==0 and outer['argv'][2:]==[SOURCE_SHA,'normal-off']and read(root['references'][2]['path'])==b''
report=doc(OUTPUT/'results.json','0c466adcb737f228d7f01f32fd8c3e7d92c6a3dedc5ade77c3f516df85d8e8ac');completion=doc(OUTPUT/'completion.json','7e73191441fd91bb851364cd18f08d8b7e42ab076db480be88b232d8e5ba19ef')
assert report['state']=='ZLIB350_SIX_SYNC_COMPONENT_VALIDATION_PASSED'and report['variant']=='normal-off'and len(report['records'])==283
assert completion['reportSha256']==sha(read(OUTPUT/'results.json'))and len(completion['artifacts'])==1544
artifacts={}
for row in completion['artifacts']:
 path=Path(row['path']);assert path.is_relative_to(OUTPUT)and str(path)not in artifacts;artifacts[str(path)]=row;read(path,row['sha256'],row['bytes'],False)
actual_files=[];actual_links=[]
for directory,dirs,files in os.walk(OUTPUT,followlinks=False):
 for name in dirs+files:
  path=Path(directory)/name
  if path.is_symlink():actual_links.append(str(path))
  elif path.is_file():actual_files.append(str(path))
 dirs[:]=[name for name in dirs if not(Path(directory)/name).is_symlink()]
assert set(actual_files)==set(artifacts)|{str(OUTPUT/'completion.json')}and len(actual_files)==1545
assert completion['outputLinks']==root['outputLinks']and actual_links==[completion['outputLinks'][0]['path']]
for row in completion['outputLinks']:assert os.readlink(row['path'])==row['linkText']and str(Path(row['path']).resolve(strict=True))==row['resolvedTarget']
controls=doc(OUTPUT/'output-controls.json');assert controls['nodeModulesLink']==completion['outputLinks'][0];read(controls['packageJson']['path'],controls['packageJson']['sha256'])
indexed(SOURCE,SOURCE_SHA,21);node=doc(SOURCE/'node-results.json');contract=doc(SOURCE/'profile-contract.json');config=doc(SOURCE/'activation.json')
assert node['node']=='v22.14.0'and node['nodeExecutableSha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'and len(node['cases'])==61 and len(node['dataFiles'])==28
oracle={}
for row in node['dataFiles']:oracle[row['path']]=read(row['path'],row['sha256'],row['bytes'])
assert len(contract['exports'])==40 and len(node['inventory']['constants'])==107
fixture_text=read(SOURCE/'node-fixtures.mjs',node['fixtureSourceSha256']).decode();prefix='export const fixtures=Object.freeze(';assert fixture_text.startswith(prefix)and fixture_text.endswith(');\n');fixtures={key:bytes.fromhex(value)for key,value in json.loads(fixture_text[len(prefix):-3]).items()};assert len(fixtures)==28
MAX_INPUT=1048576;MAX_OUTPUT=16777216;formats=[('gzip','gzipSync','gunzipSync',31),('zlib','deflateSync','inflateSync',15),('raw','deflateRawSync','inflateRawSync',-15)]
cases=[]
def add(id,operation,kind,phase='ordinary',input=None,plain=None,code=None,deviation=None,options=None,view='u8'):
 cases.append({'id':id,'operation':operation,'kind':kind,'phase':phase,'input':input,'expectedPlain':plain,'profileCode':code,'deviation':deviation,'options':options,'view':view})
for fmt,enc,dec,wbits in formats:
 for label,plain,view in[('empty',{'kind':'zero','length':0},'u8'),('binary',{'kind':'seed','length':256,'seed':0x12345678},'buffer'),('offset',{'kind':'repeat','length':1024,'byte':65},'offset-u8')]:add(fmt+'-encode-'+label,enc,'encode',input=plain,plain=plain,view=view)
 for label,plain,view in[('empty',{'kind':'zero','length':0},'arraybuffer'),('binary',{'kind':'seed','length':256,'seed':0x12345678},'offset-dataview'),('repeat',{'kind':'repeat','length':4096,'byte':65},'offset-buffer')]:add(fmt+'-decode-'+label,dec,'decode',input={'kind':'fixture','id':fmt+'-'+label},plain=plain,view=view)
 add(fmt+'-encode-input-limit',enc,'encode','boundary',{'kind':'seed','length':MAX_INPUT,'seed':0xDEADBEEF},{'kind':'seed','length':MAX_INPUT,'seed':0xDEADBEEF},view='offset-u8')
 add(fmt+'-encode-limit-small',enc,'error',input={'kind':'repeat','length':256,'byte':65},code='ERR_BUFFER_TOO_LARGE',options={'maxOutputLength':1})
 add(fmt+'-encode-limit-valid',enc,'encode',input={'kind':'seed','length':256,'seed':17},plain={'kind':'seed','length':256,'seed':17},options={'maxOutputLength':1024})
 add(fmt+'-decode-limit-exact',dec,'decode',input={'kind':'fixture','id':fmt+'-repeat'},plain={'kind':'repeat','length':4096,'byte':65},options={'maxOutputLength':4096})
 add(fmt+'-decode-limit-under',dec,'error',input={'kind':'fixture','id':fmt+'-repeat'},code='ERR_BUFFER_TOO_LARGE',options={'maxOutputLength':4095})
 add(fmt+'-decode-output-cap',dec,'decode','large-output',{'kind':'fixture','id':fmt+'-output-cap'},{'kind':'repeat','length':MAX_OUTPUT,'byte':7},view='offset-u8')
 add(fmt+'-decode-output-over-cap',dec,'error','large-output',{'kind':'fixture','id':fmt+'-output-over-cap'},code='ERR_BUFFER_TOO_LARGE')
 for variant,code in[('invalid','Z_DATA_ERROR'),('truncated','Z_BUF_ERROR'),('multi','ERR_SM_ZLIB_TRAILING_DATA_UNSUPPORTED'),('trailing','ERR_SM_ZLIB_TRAILING_DATA_UNSUPPORTED')]:add(fmt+'-'+variant,dec,'error',input={'kind':'fixture','id':fmt+'-'+variant},code=code,deviation='strict-one-member-no-trailing'if variant in['multi','trailing']else'compare-actual-Node-code')
add('dictionary-refusal','inflateSync','error',input={'kind':'fixture','id':'zlib-dictionary'},code='ERR_SM_ZLIB_DICTIONARY_UNSUPPORTED',deviation='Node reports dictionary need; profile explicitly unavailable')
for operation in['gzipSync','inflateSync']:add(operation+'-input-over-cap',operation,'error','boundary',{'kind':'zero','length':MAX_INPUT+1},code='ERR_OUT_OF_RANGE',deviation='profile1MiB input cap precedes codec')
for value,label,code in[(0,'zero','ERR_OUT_OF_RANGE'),(-1,'negative','ERR_OUT_OF_RANGE'),(1.5,'fractional','ERR_OUT_OF_RANGE'),('1','string','ERR_INVALID_ARG_TYPE'),(MAX_OUTPUT+1,'over-profile-cap','ERR_OUT_OF_RANGE')]:add('option-'+label,'gzipSync','error',input={'kind':'repeat','length':16,'byte':1},code=code,options={'maxOutputLength':value})
add('unknown-option-level','gzipSync','error',input={'kind':'repeat','length':16,'byte':1},code='ERR_SM_NODE_UNSUPPORTED',options={'level':1},deviation='only maxOutputLength admitted')
add('ordinary-string-input-refusal','gzipSync','error',input={'kind':'string','value':'ordinary text'},code='ERR_SM_NODE_UNSUPPORTED',view='direct',deviation='Node accepts strings; profile byte-only')
assert len(cases)==61
for index,row in enumerate(cases):assert node['cases'][index]['index']==index and node['cases'][index]['id']==row['id']and node['cases'][index]['profileExpectedKind']==row['kind']and node['cases'][index]['profileExpectedCode']==row['profileCode']and node['cases'][index]['deviation']==row['deviation']
plain_cache={}
def plain(desc):
 key=json.dumps(desc,sort_keys=True)
 if key not in plain_cache:
  if desc['kind']=='string':value=desc['value'].encode()
  elif desc['kind']=='repeat':value=bytes([desc['byte']])*desc['length']
  elif desc['kind']=='zero':value=bytes(desc['length'])
  else:
   assert desc['kind']=='seed';value=bytearray(desc['length']);state=desc['seed']&0xffffffff
   for i in range(len(value)):
    state^=(state<<13)&0xffffffff;state^=state>>17;state^=(state<<5)&0xffffffff;state&=0xffffffff;value[i]=state>>24
   value=bytes(value)
  plain_cache[key]=value
 return plain_cache[key]
def decode(data,wbits,length):
 decoder=zlib.decompressobj(wbits);value=decoder.decompress(data,length+1);assert len(value)==length and decoder.eof and not decoder.unconsumed_tail and not decoder.unused_data;assert decoder.flush()==b'';return value
def wbits(operation):return next(bits for fmt,enc,dec,bits in formats if operation in[enc,dec])
absent={'own':False,'type':'undefined','value':None};native_codes={'ERR_BUFFER_TOO_LARGE','Z_DATA_ERROR','Z_BUF_ERROR','ERR_SM_ZLIB_DICTIONARY_UNSUPPORTED','ERR_SM_ZLIB_TRAILING_DATA_UNSUPPORTED'}
def error_contract(error,row):
 fields=error['fields']
 for key,wanted in{'code':row['profileCode'],'module':'node:zlib','profile':contract['profileVersion']}.items():assert fields[key]=={'own':True,'type':'string','value':wanted}
 if row['profileCode']in native_codes:
  assert fields['errno']['own']is True and fields['errno']['type']=='number'and type(fields['errno']['value'])is int and fields['operation']==absent
  return{'origin':'native-codec','errno':fields['errno']['value'],'operationAbsent':True}
 operation=row['operation']+(': option level'if row['id']=='unknown-option-level'else': string input'if row['id']=='ordinary-string-input-refusal'else'')
 assert fields['operation']=={'own':True,'type':'string','value':operation}and fields['errno']==absent;return{'origin':'facade','operation':operation,'errnoAbsent':True}
ordinary=[i for i,row in enumerate(cases)if row['phase']=='ordinary'];assert len(ordinary)==50
schedule=[('retained-0',list(range(61))),('retained-1',ordinary),('retained-2',ordinary),('fresh-Jco',list(range(61))),('fresh-Wasmtime',list(range(61)))]
expected_order=[];counter=0
for label,indices in schedule:
 if label=='fresh-Jco':counter=0
 for i in indices:
  if label=='fresh-Wasmtime':calls=1
  else:counter+=1;calls=counter
  expected_order.append((label,i,calls))
success_counts=Counter();case_values={};all_observations=[];compressed_different=set()
assert len(report['records'])==len(expected_order)
for record,(label,index,calls)in zip(report['records'],expected_order):
 row=cases[index];assert record['index']==index and record['id']==row['id']and record['label']==label and record['guestCalls']==record['expectedCalls']==calls
 value=doc(record['rawFile']['path'],record['rawFile']['sha256']);assert len(read(record['rawFile']['path']))==record['rawFile']['bytes'];assert value['calls']==calls and value['index']==index and value['id']==row['id']and value['inputImmutable']is True
 validated=Path(record['rawFile']['path']).with_name(Path(record['rawFile']['path']).name.replace('.raw.txt','.validated.json'));assert doc(validated)==record
 if label=='fresh-Wasmtime':
  terminal=doc(OUTPUT/f'processes/wasmtime-{index}.terminal.json');assert terminal['status']==0 and terminal['signal']is terminal['spawnError']is terminal['externalSignal']is None and terminal['errors']==terminal['signals']==[]
  assert terminal['closed']is terminal['ownedGroupGone']is terminal['terminalExitZeroObserved']is True and terminal['timedOut']is terminal['outputLimitExceeded']is False and terminal['timeoutMs']==600000
  assert terminal['args']==['run','--invoke',f'run({index})',str(OUTPUT/'zlib-validation.component.wasm')]
  for stream in['stdout','stderr']:read(terminal[stream]['path'],terminal[stream]['sha256'],terminal[stream]['bytes'],False)
  inner=json.loads(read(terminal['stdout']['path']).decode().strip());assert isinstance(inner,str)and json.loads(inner)==value and inner.encode()==read(record['rawFile']['path'])
  assert read(terminal['stderr']['path'])==b''
 if row['kind']=='error':
  assert value['outcome']=='error'and value['partialOutputPublished']is False and bytes.fromhex(value['recoveryHex'])==plain({'kind':'seed','length':256,'seed':0x12345678})
  computed={'outcome':'error','code':row['profileCode'],'errorContract':error_contract(value['error'],row),'node':node['cases'][index]['node'],'deviation':row['deviation']}
 else:
  assert value['outcome']=='ok'and value['isBuffer']is value['globalBuffer']is True and value['byteOffset']==0 and value['backingLength']==value['outputLength']<=MAX_OUTPUT
  result=bytes.fromhex(value['outputHex']);assert len(result)==value['outputLength']and len(value['outputHex'])==2*len(result);expected=plain(row['expectedPlain']);node_result=node['cases'][index]['node'];assert node_result['kind']=='ok';node_bytes=read(node_result['result']['path'],node_result['result']['sha256'],node_result['result']['bytes'])
  decoded=decode(result,wbits(row['operation']),len(expected))if row['kind']=='encode'else result
  node_plain=decode(node_bytes,wbits(row['operation']),len(expected))if row['kind']=='encode'else node_bytes
  assert decoded==node_plain==expected
  if row['kind']=='encode':
   if result!=node_bytes:compressed_different.add(index)
   if len(result)>MAX_INPUT:assert value['roundtrip']['kind']=='input-cap';error_contract(value['roundtrip']['error'],{'id':'roundtrip','operation':next(dec for fmt,enc,dec,bits in formats if enc==row['operation']),'profileCode':'ERR_OUT_OF_RANGE'})
   else:assert value['roundtrip']=={'kind':'decoded','bytes':len(expected)}
  else:assert value['roundtrip']is None
  computed={'outcome':'ok','compressedBytes':len(result)if row['kind']=='encode'else None,'decodedBytes':len(decoded),'fullBytesEqual':True,'outputSha256':sha(result),'decodedSha256':sha(decoded),'compressedByteIdentityRequired':False};success_counts[row['kind']]+=1
 assert record['semantic']==computed
 case_values.setdefault(index,[]).append((record,value));all_observations.append({'index':index,'label':label,'rawPath':record['rawFile']['path'],'outcome':value['outcome']})
assert success_counts=={'encode':69,'decode':69}and sum(1 for r in report['records']if r['semantic']['outcome']=='error')==145

# Preserve a per-case, per-observation ledger without normalizing the Node oracle.
difference_rows=[];all_error_rows=[]
for index,row in enumerate(cases):
 if row['kind']!='error':continue
 samples=case_values[index];first=samples[0][1];profile=first['error'];n=node['cases'][index]['node'];differences=[]
 if n['kind']!='error':differences.append('outcome')
 else:
  if profile['name']!=n['name']:differences.append('error.name')
  for key in['code','errno']:
   actual={k:v for k,v in profile['fields'][key].items()if k!='own'}
   if actual!=n[key]:differences.append('error.'+key)
 for record,value in samples:assert value['error']==profile
 ledger={'index':index,'id':row['id'],'profileExpectedCode':row['profileCode'],'sourceDeviationValuePreserved':row['deviation'],'nodeOutcomeAndErrorAsRecorded':n,'profileErrorAsObserved':profile,'comparisonDifferences':differences,'observationCount':len(samples),'citations':{'nodeOracle':{'path':str(SOURCE/'node-results.json'),'jsonPointer':f'/cases/{index}/node'},'sourceCorpus':{'path':str(SOURCE/'corpus.mjs'),'caseIndex':index,'caseId':row['id']},'guestRawObservations':[{'path':record['rawFile']['path'],'jsonPointer':'/error','label':record['label']}for record,value in samples]},'notCompared':['Node own-property flags/module/operation/profile were not recorded by oracle','message: absent from guest errorRecord']}
 all_error_rows.append(ledger)
 if differences:difference_rows.append(ledger)
assert len(difference_rows)==22 and sum('outcome'in row['comparisonDifferences']or'error.code'in row['comparisonDifferences']for row in difference_rows)==16
assert sum(row['comparisonDifferences']==['error.errno']for row in difference_rows)==6
assert sum(row['sourceDeviationValuePreserved']is None for row in difference_rows)==11
ledger={'schemaVersion':1,'state':'INDEPENDENT_ACTUAL_NODE_PROFILE_ERROR_DIFFERENCE_LEDGER','scope':'Bounded profile correctness; not61-case Node parity. Original oracle/corpus/results remain unchanged.','errorCases':31,'differentErrorCases':22,'outcomeOrCodeDifferentCases':16,'additionalErrnoOnlyDifferentCases':6,'nullDeviationDifferentCases':11,'comparisonFields':['outcome','error.name','code typed value','errno typed value'],'rows':difference_rows,'allErrorComparisons':all_error_rows,'successfulObservationsFullBytesComparedSeparately':138,'successfulEncoderIndicesWithDifferentCompressedBytes':sorted(compressed_different),'compressedByteIdentityRequired':False}
with(HERE/'node-profile-difference-ledger.json').open('x')as stream:json.dump(ledger,stream,indent=2);stream.write('\n')

# Decode every module/refusal/ownership return as well as all codec records.
def raw_observation(path):return doc(path)
def refusal_set(values):
 expected=[(name,mode)for name in contract['deferred']for mode in['call','new']]+[(name,'new-sync')for name in contract['sync']];assert len(values)==len(expected)==68
 for record,(name,mode)in zip(values,expected):
  assert record['name']==name and record['mode']==mode;fields=record['error']['fields']
  for key,wanted in{'code':'ERR_SM_NODE_UNSUPPORTED','module':'node:zlib','operation':'new '+name if mode=='new-sync'else name,'profile':contract['profileVersion']}.items():assert fields[key]=={'own':True,'type':'string','value':wanted}
  assert fields['errno']==absent
module_paths=[('module',0),('retained-module-0',61),('retained-module-1',111),('retained-module-2',161),('fresh-module',0),('fresh-module-after',61)]
for label,calls in module_paths:
 matches=list((OUTPUT/'calls').glob('*-'+label+'.raw.txt'));assert len(matches)==1;value=doc(matches[0]);assert value['calls']==calls and value['namespace']==value['aliasNamespace']==sorted(contract['exports'])
 for key in['aliasNamespaceCached','canonicalNamespaceCached','canonicalStaticNamespace','sameAliases','defaultNamed','cjsDefault','globalBuffer','sameConstantObjects','frozenDefault','frozenConstants','frozenCodes','constantPrototypeNull','codePrototypeNull']:assert value[key]is True
 for key in['thenType','defaultThenType','publicBackendInfoType','publicKernelType']:assert value[key]=='undefined'
 expected_constants=dict(node['inventory']['constants']);expected_constants['ZLIB_VERNUM']={'type':'number','value':4880};assert value['constants']==expected_constants and value['codes']==node['inventory']['codes']and value['publicVernum']==value['legacyVernum']=={'type':'number','value':4880}
 refusal_set(value['initializationRefusals']);snapshot=value['snapshot'];assert bytes.fromhex(snapshot['inputHex'])==bytes.fromhex(snapshot['plainHex'])==bytes([0,1,2,3,254,255]);assert decode(bytes.fromhex(snapshot['compressedHex']),31,6)==bytes.fromhex(snapshot['inputHex'])
 saved=OUTPUT/('module-observation.json'if label=='module'else label+'.json')
 if saved.exists():saved_value=doc(saved);assert saved_value['value']==value and Path(saved_value['rawFile']['path'])==matches[0]
refusals_file=list((OUTPUT/'calls').glob('*-refusals.raw.txt'));assert len(refusals_file)==1;refusals=doc(refusals_file[0]);refusal_set(refusals['records']);refusal_set(refusals['initializationRefusals'])
ownership_file=list((OUTPUT/'calls').glob('*-ownership.raw.txt'));assert len(ownership_file)==1;ownership=doc(ownership_file[0]);assert ownership['independentBacking']is ownership['globalBuffer']is True and ownership['inputSharedWithOutput']is False and ownership['inputByteOffset']==8 and ownership['inputByteLength']==256
assert decode(bytes.fromhex(ownership['firstHex']),15,256)==bytes((i*17+3)&255 for i in range(256))
assert len(list((OUTPUT/'calls').glob('*.raw.txt')))==291 and len(list((OUTPUT/'calls').glob('*.validated.json')))==283
module=doc(OUTPUT/'module-observation.json');assert module['runtimeBackendMetadataRemainsUnverified']is True and module['sourceCoupledBackendInference']['directPrivateBackendObserved']is False and module['sourceCoupledBackendInference']['inferenceOnly']is True
progress=sorted((OUTPUT/'progress').glob('*.json'));assert len(progress)==705;events=Counter()
for i,path in enumerate(progress,1):
 value=doc(path);assert path.stem==f'{i:05d}'and value['sequence']==i and value['partialObservationOnly']is value['requiresFinalCompletionAndExternalExitZero']is True and value['runtimeAcceptanceClaim']is False;events[value['event']]+=1
assert events=={'validation-started':1,'call-before':291,'call-returned':291,'wasmtime-before':61,'wasmtime-terminal':61}
initializers=[]
for name,statement in[('deferred-call','z.gzip(new Uint8Array(1));'),('deferred-new','new z.Gzip();'),('sync-new','new z.gzipSync(new Uint8Array(1));')]:
 assert read(OUTPUT/'initializers'/f'{name}.mjs').decode()=="import * as z from 'node:zlib';\n"+statement+"\nexport function run(){return '';}\n"
 value=doc(OUTPUT/'initializers'/f'{name}.result.json');assert value['rejected']is True and value['uncaughtErrorFieldsAcrossAbiObserved']is False and value['pairedCaughtInitFields']==68 and value['error']['name']=='Error';initializers.append({'name':name,'error':value['error'],'scope':'Generic uncaught initialization rejection paired with caught68-field/valid deployed controls; no unique ABI origin proof.'})

# Static component/core/glue and fresh type audit, never instantiation.
component=read(OUTPUT/'zlib-validation.component.wasm',COMPONENT_SHA,13793002);core=read(OUTPUT/'zlib_validation.core.wasm');assert component.find(core)==13
wit=read(HERE/'fresh-component.wit').decode();assert wit.rstrip()==read(OUTPUT/'emitted.wit').decode().rstrip()==report['emittedWit'].rstrip()and not re.search(r'\bimport\b',wit)
exports=re.findall(r'export\s+([\w-]+):\s*(func\([^;]+);',wit);assert len(exports)==5 and set(name for name,signature in exports)=={'run','module-contract','refusals','ownership','ordinary-gc'}
glue=read(OUTPUT/'zlib_validation.js').decode();assert "new URL('./zlib_validation.core.wasm', import.meta.url)"in glue and 'export { moduleContract, ordinaryGc, ownership, refusals, run,'in glue
assert report['interfaceAudit']['emittedImports']==[]and report['interfaceAudit']['componentSha256']==COMPONENT_SHA and report['componentSha256']==COMPONENT_SHA and report['engineSha256']==config['actual']['normal-off']['engineSha256']
assert root['runtimeBackendProof']=={'verified':False,'version':None,'vernum':None}and report['operationalAdmission']is False
audit=doc(HERE/'static-audit.json');read(audit['tool']['path'],audit['tool']['sha256'],audit['tool']['bytes'],False)
for row in list(seen.values()):read(row['path'],row['sha256'],row['bytes'],False,True)
r={'schemaVersion':1,'state':'INDEPENDENT_ZLIB350_NORMAL_CODEC_V2_BOUNDED_RESULTS_PASSED','rootReceiptSha256':ROOT_SHA,'rootReportedOuterExit':0,'pastRootTerminalObservedByThisReader':False,'completionArtifactsRehashed':1544,'completionAndAllPhysicalOutputFiles':1545,'outputLinksChecked':1,'actualSourceFamilyIndexSha256':SOURCE_SHA,'componentSha256':COMPONENT_SHA,'componentBytes':13793002,'freshStaticComponentImports':[],'freshStaticPublicScalarExports':5,'embeddedCoreExactByteOffset':13,'onePublicCoreAndGlueBound':True,'decodedCodecObservations':283,'labels':dict(Counter(record['label']for record in report['records'])),'fullSuccessfulByteObservations':138,'successfulEncoderCrossDecodedObservations':69,'successfulDecoderFullNodeByteComparisons':69,'profileErrorObservationsWithRecoveryAndNoPartialOutput':145,'freshWasmtimeFullNestedReturnsDecoded':61,'freshWasmtimeTerminalStreamsAndCleanOwnership':61,'allReturnedRawRecordsDecoded':291,'namespaceCheckpointObservations':6,'publicBindingCount':40,'typedConstantCount':107,'caughtRefusalSetsDecoded':8,'caughtRefusalRecordsDecoded':544,'uncaughtInitializerControls':initializers,'snapshotAndOwnershipFullBytesDecoded':True,'nodeOracleDataFilesRehashed':28,'sourceCoupledVernum':4880,'actualNodeOracleVernum':4865,'runtimeBackendProof':{'verified':False,'version':None,'vernum':None},'nodeParityClaim':False,'nodeProfileDifferenceLedger':'node-profile-difference-ledger.json','nodeProfileErrorCaseDifferences':22,'nodeProfileOutcomeOrCodeDifferences':16,'additionalErrnoOnlyDifferences':6,'nullDeviationDifferentCases':11,'compressedByteIdentityRequired':False,'sourceClosureFreshReaderRequired':True,'ordinaryGcResultClaimedByThisNormalReview':False,'ownershipScope':'Public application owners and Buffer identities only; no isolated VM roots, reset, request reuse or full Node support claim.','oldFixtureFailureReusedOrEdited':False,'operationalAdmission':False,'ownerHelpersPreflightsNodePackageNativeGuestOrHostActionsExecutedByReader':False,'staticWasmToolsOnly':True,'existingCompressedBytesDecodedByPythonStdlibOnly':True,'runtimeAcceptanceClaim':False,'performanceClaim':False,'verifiedFiles':sorted(seen.values(),key=lambda row:row['path'])}
with(HERE/'results.json').open('x')as stream:json.dump(r,stream,indent=2);stream.write('\n')
print(json.dumps({'state':r['state'],'artifacts':1544,'observations':283,'fullWT':61,'differences':22,'verifiedPaths':len(seen)}))
