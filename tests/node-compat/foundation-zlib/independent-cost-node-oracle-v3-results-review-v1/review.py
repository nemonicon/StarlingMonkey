"""Read full retained bytes/JSON only. No codec, owner, Node or Wasm execution."""
from pathlib import Path
import base64,hashlib,json,os,re,stat
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
OUT=Path('/private/tmp/starling-node-compat/zlib-cost-node-oracle-v3');PUB=Path('/private/tmp/starling-node-compat/zlib-cost-source-v3');LOG=Path('/tmp/starling-node-compat/zlib-cost-node-oracle-v3-root')
checks=[];observed={};cache={}
def hashfile(p):
 p=Path(p);s=p.stat();key=(str(p.resolve()),s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
 if key not in cache:
  h=hashlib.sha256()
  with p.open('rb')as f:
   for b in iter(lambda:f.read(1048576),b''):h.update(b)
  t=p.stat();assert(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==(t.st_dev,t.st_ino,t.st_size,t.st_mtime_ns,t.st_ctime_ns);cache[key]=h.hexdigest()
 observed[str(p)]={'path':str(p),'sha256':cache[key],'bytes':s.st_size};return cache[key]
def verify(row,path=None):
 p=Path(path or row['path']);s=p.lstat();assert stat.S_ISREG(s.st_mode)and not stat.S_ISLNK(s.st_mode)
 assert s.st_size==row['bytes']and hashfile(p)==row['sha256'],p
 return p
def fnv(raw):
 v=2166136261
 for b in raw:v=((v^b)*16777619)&0xffffffff
 return v
def adler(raw):
 a=1;b=0
 for c in raw:a=(a+c)%65521;b=(b+a)%65521
 return(b<<16)|a
def crc(raw):
 value=0xffffffff
 for b in raw:
  value^=b
  for _ in range(8):value=(value>>1)^ (0xedb88320 if value&1 else 0)
 return value^0xffffffff
def b64(value):
 assert type(value)is str
 raw=base64.b64decode(value,validate=True);assert base64.b64encode(raw).decode()==value;return raw
capture_cache={}
def capture(row,expected=None):
 raw=b64(row['base64']);key=hashlib.sha256(raw).hexdigest()
 if key not in capture_cache:capture_cache[key]={'length':len(raw),'fnv':fnv(raw)}
 assert row['bytes']==len(raw)and row['sha256']==key and row['fnv1aU32']==capture_cache[key]['fnv']
 if expected is not None:assert raw==expected
 return raw
root_receipt=BASE/'cost-node-oracle-v3-root-results.json';assert hashfile(root_receipt)=='b67a7de1db3bfc3ae8383b493bd540fef92a3f8c18f459ccce121e252824f21b'
auth=BASE/'cost-node-oracle-v3-root-authority.json';assert hashfile(auth)=='31c57db9dcf36fd23d4b19cc09aaa90f2b329cd22eddeaa67020ebd35ca2b150'
config=BASE/'cost-node-oracle-v3-root-config.json';assert hashfile(config)=='90b3cab39e6e495083e7aef553071aa16ca0f9cfc860df3d579a4d3dbbd7add6'
root_authority=json.loads(auth.read_bytes());configuration=json.loads(config.read_bytes());assert root_authority['action']=='node-oracle'and root_authority['permittedArms']==['native-on']and root_authority['untimedNodeOracleAndRenderOnly']is True
assert root_authority['fflateCodecAllowed']is False and root_authority['componentOrGuestOrNativeBuildOrPilotOrTimingAllowed']is False
terminal=json.loads((LOG/'terminal.json').read_bytes());hashfile(LOG/'terminal.json');assert terminal['rawExitCode']==0 and terminal['pid']==21386 and terminal['timeout']is False
assert terminal['argv'][:2]==['/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',str(PUB/'control/node-oracle-action.mjs')]
arg=json.loads(terminal['argv'][2]);assert arg['path']==str(config)and arg['sha256']==hashfile(config)and arg['bytes']==config.stat().st_size
for name in ['stdout','stderr']:verify(terminal[name])
assert terminal['stdout']['sha256']=='db0318d8e81ee0e825c16dc68b118005f1f1c0f770cd125950189e26f6c78a3b'and terminal['stderr']['bytes']==0
stdout=json.loads((LOG/'stdout.log').read_bytes());verify(stdout['index'],OUT/'index.json');verify(stdout['completion'],OUT/'completion.json')
assert hashfile(OUT/'index.json')=='8a78bd0c9feb491f2e893f4c9e76906de759453c6e3b38e36dc2042c09e71d66'
index=json.loads((OUT/'index.json').read_bytes());completion=json.loads((OUT/'completion.json').read_bytes());records={r['path']:r for r in index['files']}
assert len(records)==194 and len(index['files'])==194
for name,row in records.items():
 p=verify(row,OUT/name);s=p.stat();assert stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1
files=set();dirs=set()
for directory,ds,fs in os.walk(OUT,followlinks=False):
 for name in ds+fs:
  p=Path(directory)/name;s=p.lstat();assert not stat.S_ISLNK(s.st_mode)
  if stat.S_ISDIR(s.st_mode):assert stat.S_IMODE(s.st_mode)==0o700;dirs.add(str(p.relative_to(OUT)))
  else:assert stat.S_ISREG(s.st_mode)and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==0o600;files.add(str(p.relative_to(OUT)))
assert len(files)==196 and files==set(records)|{'index.json','completion.json'}
assert stat.S_IMODE(OUT.stat().st_mode)==0o700
assert completion['state']=='NODE_ORACLE_RENDER_UNREVIEWED_EXTERNAL_EXIT_ZERO_REQUIRED'and completion['operationalAdmission']is False and completion['timingAllowed']is False
assert completion['index']==stdout['index']
for key in ['result','oracle','module']:verify(completion[key],OUT/completion[key]['path'])
checks.append('auth31cConfig90bExactNodeCommandRaw0And194Indexed196ActualFiles')
# Verify the actual immutable publication used, without loading its modules.
assert hashfile(PUB/'index.json')=='4621f7e72b4fb0555a5df630b1aedd4d2a04743b0db9188fc50099779f07387b'
publication=json.loads((PUB/'index.json').read_bytes())
for row in publication['files']:verify(row,PUB/row['path'])
for row in publication['links']:
 p=PUB/row['destination'];assert p.is_symlink()and os.readlink(p)==row['newLinkText']and p.resolve()==PUB/row['mappedTarget']
assert hashfile(Path(terminal['argv'][0]))=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
checks.append('all10187ActualSourcePublicationRowsAnd22LinksPlusActualNodeBinaryRehashedNoExecution')
result=json.loads((OUT/'results.json').read_bytes());oracle=json.loads((OUT/'node-oracle.json').read_bytes())
assert result['state']=='ZLIB_COST_NODE_ORACLE_AND_RENDER_CAPTURED_UNREVIEWED_V1'and oracle['state']=='NODE_22_CODEC_COST_ORACLE_CAPTURED_UNREVIEWED_V1'
expected_binding={'proposalIndexSha256':'e29c596df3c809bab8fd3851b224a7ec4e84177d791c5d1f909072985f047ef8','protocolDecisionSha256':'0025c7a1083d9291effe0cf51bbfef4e154353db75d433dae07f296d46d61cc6','nodeExecutableSha256':'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0','guestSourceIndexSha256':'ebe8fa901a3516358539c0458b09cad822308f9a3b0c76db33015ff378a8eae8','costToolingIndexSha256':'ff208e72d0b87933aa75cdeb7c1ae16f29aa6ae94c357318a9d6676af04b36b8','rootActionAuthoritySha256':hashfile(auth)}
assert result['sourceBinding']==oracle['sourceBinding']==expected_binding
assert result['publicationIndexSha256']==completion['sourcePublicationIndexSha256']==hashfile(PUB/'index.json')
assert oracle['node']=='v22.14.0'and oracle['nodeExecutableSha256']==expected_binding['nodeExecutableSha256']
assert oracle['providerLevel45EncoderOr135CrossDecodeProof']is False and oracle['ffOffProof']is False and oracle['guestOrTimingExecuted']is False
checks.append('exactSourceGuestProtocolAuthorityBindingsUnreviewedConstructionStatesAndNoCrossProviderClaim')
# Regenerate only deterministic byte fixtures, never a codec.
fixture_data={};specs=[('empty',0,False),('small-repeat',64,False),('small-prng',64,True),('large-repeat',524288,False),('large-prng',524288,True)]
for name,length,prng in specs:
 if prng:
  state=0x6d2b79f5;raw=bytearray(length)
  for i in range(length):
   state^=(state<<13)&0xffffffff;state^=state>>17;state^=(state<<5)&0xffffffff;state&=0xffffffff;raw[i]=state&255
  raw=bytes(raw)
 else:raw=(b'abc123'*((length+5)//6))[:length]
 fixture_data[name]=raw
assert len(oracle['rawFixtures'])==5
for row,(name,_,_)in zip(oracle['rawFixtures'],specs):assert row['id']==name;capture(row,fixture_data[name])
case_source=(PUB/'guest/cases.generated.mjs').read_text();cases=json.loads(case_source.split('Object.freeze(',1)[1].split('].map(Object.freeze)',1)[0]+']');assert len(cases)==30
for i,(row,case)in enumerate(zip(oracle['cases'],cases)):
 assert row=={'caseId':i,'caseName':case['id'],'fixture':case['fixture'],'format':case['format'],'direction':case['direction'],'logicalUncompressedBytes':case['logicalUncompressedBytesPerOperation'],'rawFixtureSha256':hashlib.sha256(fixture_data[case['fixture']]).hexdigest(),'providerSpecificGuestEncodingExpected':None}
checks.append('allFiveFullDeterministicRawFixturesAnd30ExactCaseAssociationsIndependentPureByteRegeneration')
raw_files=sorted((OUT/'raw').iterdir());assert len(raw_files)==190
for i,p in enumerate(raw_files,1):assert p.name.startswith(str(i).zfill(6)+'-')
raw_labels={p.name.split('-',1)[1]:p for p in raw_files};assert len(raw_labels)==190
expected_order=[];call_methods=[]
opaque={'type':'object','kind':'opaque','propertiesRead':False,'fullPrimitiveValueCaptured':False}
def raw(name,extension):
 label=name+extension;expected_order.append(label);p=raw_labels[label];return p.read_bytes()
def returned(name,method):
 value=json.loads(raw(name+'-return-transport','.json'));assert value=={'schemaVersion':1,'kind':'node-codec-call-returned','method':method,'value':opaque};call_methods.append(method)
def decoded(name,method,expected,consumed):
 returned(name,method);assert json.loads(raw(name+'-buffer-transport','.json'))==opaque
 value=raw(name+'-decoded','.bin');assert value==expected
 assert json.loads(raw(name+'-engine-transport','.json'))==opaque
 count=json.loads(raw(name+'-sourceBytesConsumed-transport','.json'));assert count=={'type':'number','kind':'finite','value':consumed,'fullPrimitiveValueCaptured':True}
 return value
assert len(oracle['encodedStreams'])==len(oracle['repeatedEncoderOutputs'])==len(oracle['decodedOwnStreams'])==15
summary=[];at=0
for fixture,_,_ in specs:
 expected=fixture_data[fixture];assert raw('raw-'+fixture,'.bin')==expected
 for format,encoder,decoder in [('zlib','deflateSync','inflateSync'),('gzip','gzipSync','gunzipSync'),('raw','deflateRawSync','inflateRawSync')]:
  stream=oracle['encodedStreams'][at];repeat=oracle['repeatedEncoderOutputs'][at];audit=oracle['decodedOwnStreams'][at];at+=1
  name='node-'+fixture+'-'+format;returned(name+'-first',encoder);first=raw(name+'-first-return-bytes','.bin');returned(name+'-repeat',encoder);second=raw(name+'-repeat-return-bytes','.bin');assert first==second
  assert 0<len(first)<=1048576 and stream['encodedBytes']==len(first)and b64(stream['encodedBase64'])==first
  assert stream['encodedSha256']==hashlib.sha256(first).hexdigest()and stream['encodedFNV1aU32']==fnv(first)
  case=next(c for c in cases if c['fixture']==fixture and c['format']==format and c['direction']=='decode')
  assert stream=={'schemaVersion':1,'kind':'codec-cost-stage-v1','caseId':case['index'],'fixture':fixture,'format':format,'provider':'node-22.14.0','streamId':'node-22.14.0.'+fixture+'.'+format,'encodedBytes':len(first),'encodedFNV1aU32':fnv(first),'encodedSha256':hashlib.sha256(first).hexdigest(),'encodedBase64':base64.b64encode(first).decode()}
  assert repeat['streamId']==stream['streamId']and repeat['fullByteEqual']is True;capture(repeat['first'],first);capture(repeat['second'],second)
  decoded(name,decoder,expected,len(first));assert audit['streamId']==stream['streamId']and audit['sourceBytesConsumed']==len(first)and audit['fullRawEqual']is True;capture(audit['output'],expected)
  if format=='zlib':
   assert len(first)>=8 and ((first[0]<<8)|first[1])%31==0 and first[0]&15==8 and first[0]>>4<=7 and first[1]&32==0
   checksum=int.from_bytes(first[-4:],'big');assert checksum==adler(expected);payload=first[2:-4]
   frame={'format':format,'header':list(first[:2]),'rawAdler32':checksum,'dictionary':False,'fullDeflateParsing':False}
  elif format=='gzip':
   assert len(first)>=20 and first[:4]==bytes([31,139,8,0])and int.from_bytes(first[4:8],'little')==0
   checksum=int.from_bytes(first[-8:-4],'little');size=int.from_bytes(first[-4:],'little');assert checksum==crc(expected)and size==len(expected);payload=first[10:-8]
   frame={'format':format,'header':list(first[:10]),'rawCRC32':checksum,'rawISize':size,'mtime':0,'memberCountBasis':'fixed header/trailer only; independent raw payload consumption audit required','fullDeflateParsing':False}
  else:payload=first;frame={'format':'raw','framing':'none','fullDeflateParsing':False}
  assert audit['framing']==frame
  if format!='raw':decoded(name+'-raw-payload','inflateRawSync',expected,len(payload))
  assert audit['rawPayload']=={'bytes':len(payload),'sourceBytesConsumed':len(payload),'fullRawEqual':True,'formatAudit':'actual Node inflateRawSync consumed exact strict-wrapper payload'}
  summary.append({'fixture':fixture,'format':format,'caseId':case['index'],'rawBytes':len(expected),'encodedBytes':len(first),'encodedSha256':stream['encodedSha256'],'rawFNV1aU32':fnv(expected),'repeatFullBytesEqual':True,'retainedWrappedConsumed':len(first),'retainedRawPayloadConsumed':len(payload)})
assert expected_order==list(raw_labels)and len(call_methods)==55
method_counts={name:call_methods.count(name)for name in sorted(set(call_methods))};assert method_counts=={'deflateRawSync':10,'deflateSync':10,'gunzipSync':5,'gzipSync':10,'inflateRawSync':15,'inflateSync':5}
checks.append('all190OrderedTypedRetentionFiles55Calls30Encodes25DecodesFullOutputsAndConsumedCounts')
checks.append('all15DeterministicStreamsFullBytesSHAFNVAndPureHeaderTrailerAdlerCRCChecksNoCodecRerun')
inputs={'schemaVersion':1,'kind':'codec-cost-node-inputs-v1','oracleSha256':hashfile(OUT/'node-oracle.json'),'records':oracle['encodedStreams']}
module='// Exact future Node input data; capture is UNREVIEWED until separate Root proof. No codec executes here.\nexport const oracleInputs='+json.dumps(inputs,separators=(',',':'),ensure_ascii=False)+';\n'
assert module.encode()==(OUT/'oracle-inputs.mjs').read_bytes()and len(module.encode())==2106468 and len(module.encode())<=33554432
assert result['nodeEncoderStreams']==15 and result['codecCases']==30 and result['rawRetentionFiles']==190 and result['operationalAdmission']is False and result['timingAllowed']is False
checks.append('renderedModuleIndependentlyReconstructedExactlyAsDataNoRendererOrModuleExecution')
# Final immutable publication/output digest checks; no prior helper is run.
assert hashfile(OUT/'node-oracle.json')=='bf1312f33bc4df030b16a0f52a8018b2cf50c7dcf4fbad31699fbd9217c9fcf5'
assert hashfile(OUT/'oracle-inputs.mjs')=='a8cf57eebe7f5edfaf92f98427fb4185b65c30e489b7e831879bdbee06eb08b4'
assert hashfile(PUB/'index.json')==configuration['publicationIndex']['sha256']
for name in ['index.json','completion.json']:hashfile(OUT/name)
# Recheck exact physical source membership and the explicit immutable350 data
# references selected by the already Root-reviewed pair, never old originals.
pub_files=set();pub_links=set();pub_dirs=set()
for directory,ds,fs in os.walk(PUB,followlinks=False):
 for name in ds+fs:
  f=Path(directory)/name;st=f.lstat();relative=str(f.relative_to(PUB))
  if stat.S_ISLNK(st.st_mode):pub_links.add(relative)
  elif stat.S_ISDIR(st.st_mode):assert stat.S_IMODE(st.st_mode)==0o700;pub_dirs.add(relative)
  else:assert stat.S_ISREG(st.st_mode)and st.st_nlink==1;pub_files.add(relative)
assert pub_files=={r['path']for r in publication['files']}|{'index.json','completion.json'}and len(pub_files)==10189
assert pub_links=={r['destination']for r in publication['links']}and pub_dirs==set(publication['directories'])
st=PUB.stat();assert {'device':st.st_dev,'inode':st.st_ino}==publication['rootIdentity']=={'device':16777234,'inode':169827073}
for row in publication['files']:assert stat.S_IMODE((PUB/row['path']).stat().st_mode)==row['mode']
pair_proof=root_authority['rootReviewedPair'];pair_index_path=verify(pair_proof['index']);pair_index=json.loads(pair_index_path.read_bytes())
for row in pair_index['files']:verify(row,pair_index_path.parent/row['path'])
pair=json.loads(verify(pair_proof['result']).read_bytes());assert pair['state']=='ROOT_REVIEWED_GENUINE_ZLIB350_COST_PAIR_V1'and pair['nativeInputs']==350 and pair['operationalAdmission']is False
native_rows=0
for name in ['nativeOn','nativeOff']:
 data=pair[name];verify(data['engine']);meta=json.loads(verify(data['metadata']).read_bytes());freeze=json.loads(verify(data['freezeReceipt']).read_bytes())
 assert len(meta['sourceManifest'])==350 and len(meta['componentizeSourceManifest'])==3 and len(freeze['copies'])==1024 and meta['zlibPolicy']['runtimeBackendProof']['verified']is False
 for row in freeze['copies']:verify(row);native_rows+=1
assert native_rows==2048
for row in pair['selectedSDKReferences']:verify(row)
checks.append('finalPhysicalPublicationMembershipIdentity2048Immutable350FrozenRowsAndSelectedSDKRefsStableNoOriginalCacheTraversal')
report={'schemaVersion':1,'state':'INDEPENDENT_COST_NODE_ORACLE_RENDER_VERIFIED_V1','verifiedPassed':True,'nodeVersion':'v22.14.0','nodeExecutableSha256':expected_binding['nodeExecutableSha256'],'toolingSourceIndexSha256':expected_binding['costToolingIndexSha256'],'guestSourceIndexSha256':expected_binding['guestSourceIndexSha256'],'sourcePublicationIndexSha256':hashfile(PUB/'index.json'),'rootActionAuthoritySha256':hashfile(auth),'rootConfigSha256':hashfile(config),'externalNodeActionExitCode':0,'outputIndexSha256':hashfile(OUT/'index.json'),'oracle':completion['oracle'],'module':completion['module'],'rawFixtures':5,'nodeEncoderStreams':15,'codecCases':30,'nodeCalls':55,'methodCounts':method_counts,'rawRetentionFiles':190,'indexedFiles':194,'actualFiles':196,'frozenNativeRowsRehashed':2048,'allFullRetainedEncoderAndDecoderBytesVerified':True,'pureFramingChecks':True,'independentCodecOrDeflateParsingExecuted':False,'consumptionEvidenceBasis':'All25 actual Node public bytesWritten typed returns and full raw decoder outputs retained; authenticated selected Node/source. Reader did not rerun a codec or parse general deflate bits.','opaqueObjectShapeEvidenceBasis':'Opaque carriers preserve actual type and no field inspection; Buffer/engine shape assertions are authenticated source/terminal evidence, while full output bytes are independently read.','renderReconstructedByteExact':True,'providerLevel45EncoderOr135CrossDecodeProof':False,'ffOffProof':False,'guestOrTimingExecuted':False,'operationalAdmission':False,'timingAllowed':False,'newRootRenderCapsuleReviewRequired':True,'sourceAcceptanceClaim':False,'checks':checks,'passedDataChecks':len(checks),'lexicalPathsObserved':len(observed),'physicalHashReads':len(cache),'ownerHelperPreflightNodeLibraryCodecBundleNativeGuestHostOrTimingInvokedByReader':False}
(HERE/'results.json').write_text(json.dumps(report,indent=2)+'\n');(HERE/'stream-summary.json').write_text(json.dumps({'schemaVersion':1,'streams':summary,'fullBytesLiveInExactActualOracleAnd190RetentionFiles':True},indent=2)+'\n');(HERE/'rehashed-files.json').write_text(json.dumps({'schemaVersion':1,'files':sorted(observed.values(),key=lambda r:r['path']),'streamBlockBytes':1048576},indent=2)+'\n')
print(json.dumps({'state':report['state'],'checks':len(checks),'streams':15,'nodeCalls':55,'retainedFiles':190,'paths':len(observed)}))
