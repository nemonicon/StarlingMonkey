#!/usr/bin/env python3
"""Independent READ/HASH/DATA byte, Node retention and coverage subreview.

No project module, Node, Jco, CLI, parser helper, codec or guest is invoked.
Only ordinary files, JSON, base64 payloads and data checksums are examined.
"""
from pathlib import Path
import base64
import binascii
import hashlib
import json
import stat
from collections import Counter

HERE=Path(__file__).resolve().parent
Z=HERE.parent
R=Path('/private/tmp/starling-node-compat/zlib-cost-jco-correctness-v3')
ARMS=['native-on','fflate-on','fflate-off']
PROVIDERS=['node-22.14.0','native-on','fflate-on']
FORMATS=['zlib','gzip','raw']
FIXTURES=['empty','small-repeat','small-prng','large-repeat','large-prng']
LEDGER={}
FNVS={}
COUNTS=Counter()

def need(value,label):
    if not value:raise AssertionError(label)

def digest(value):return hashlib.sha256(value).hexdigest()

def read(path,expected=None):
    path=Path(path)
    need(path.is_absolute() and path.is_file() and not path.is_symlink(),'ordinary absolute byte-review input')
    before=path.stat();raw=path.read_bytes();after=path.stat()
    need((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'stable data read')
    row={'path':str(path),'sha256':digest(raw),'bytes':len(raw)}
    if expected:need(row['sha256']==expected['sha256'] and row['bytes']==expected['bytes'],'descriptor hash/size '+str(path))
    old=LEDGER.get(str(path));need(old is None or old==row,'consistent repeated tuple');LEDGER[str(path)]=row
    if str(path).startswith(str(R)+'/') and path.name!='index.json':
        member=path.relative_to(R).as_posix();need(member in INDEX and INDEX[member]['sha256']==row['sha256'] and INDEX[member]['bytes']==row['bytes'],'actual source indexed member '+member)
    return raw

def pairs(values):
    out={}
    for key,value in values:need(key not in out,'unique JSON key');out[key]=value
    return out

def data(path,expected=None):return json.loads(read(path,expected),object_pairs_hook=pairs)

def fnv(raw):
    key=(len(raw),digest(raw))
    if key not in FNVS:
        value=2166136261
        for byte in raw:value=((value^byte)*16777619)&0xffffffff
        FNVS[key]=value
    return FNVS[key]

def decode64(text):
    need(isinstance(text,str),'base64 string');raw=base64.b64decode(text,validate=True)
    need(base64.b64encode(raw).decode()==text,'canonical complete base64');return raw

def full(value,maxbytes=1048576):
    raw=decode64(value['base64']);need(len(raw)==value['bytes'] and len(raw)<=maxbytes,'whole encoded byte count/cap')
    if 'sha256' in value:need(digest(raw)==value['sha256'],'whole data SHA')
    if 'fnv1aU32' in value:need(fnv(raw)==value['fnv1aU32'],'whole data FNV')
    return raw

def stream_bytes(row):
    value=decode64(row['encodedBase64']);need(0<len(value)<=1048576 and len(value)==row['encodedBytes'] and digest(value)==row['encodedSha256'] and fnv(value)==row['encodedFNV1aU32'],'full stream size/SHA/FNV/base64')
    need(row['schemaVersion']==1 and row['kind']=='codec-cost-stage-v1' and row['streamId']==row['provider']+'.'+row['fixture']+'.'+row['format'],'full stage stream identity');return value

def fixture(name):
    size=0 if name=='empty' else 64 if name.startswith('small-') else 524288
    if name.endswith('repeat'):return (b'abc123'*((size+5)//6))[:size]
    if name=='empty':return b''
    out=bytearray(size);state=0x6d2b79f5
    for i in range(size):
        state^=(state<<13)&0xffffffff;state^=state>>17;state^=(state<<5)&0xffffffff;state&=0xffffffff;out[i]=state&255
    return bytes(out)

def raw_call(root,row,export):
    record=data(root/row['path'],row);need(record['schemaVersion']==1 and record['exportName']==export and record['partial'] is True,'retained raw call identity')
    returned=record['returned'];text=returned['value'];need(returned['type']=='string' and returned['fullPrimitiveCaptured'] is True and returned['codeUnits']==len(text.encode('utf-16-le'))//2,'full actual returned primitive')
    COUNTS['typedRawCallsDecoded']+=1
    return json.loads(text,object_pairs_hook=pairs)

def observation(value,row,arm,input_bytes,source,stage,encoded_reference=None):
    need(value['schemaVersion']==1 and value['kind']=='codec-cost-observation-v1' and value['caseId']==row['index'] and value['caseName']==row['id'] and value['operation']==row['operation'] and value['format']==row['format'] and value['direction']==row['direction'] and value['provider']==('native' if arm=='native-on' else 'fflate'),'full observation identity')
    need(value['logicalUncompressedBytes']==len(RAW[row['fixture']]) and value['inputSource']==source and value['stage']==stage,'actual observation source domain')
    expected_input={'byteOffset':8,'byteLength':len(input_bytes),'backingBytes':len(input_bytes)+16,'prefix':[165]*8,'suffix':[90]*8,'construction':'new ordinary ArrayBuffer; fixed/attached/unshared by construction','fnv1aU32':fnv(input_bytes),'fullInputUnchanged':True}
    need(value['input']==expected_input,'full expected input window/FNV/sentinels')
    output=full(value['output'],1048576 if row['direction']=='encode' else 524288)
    need(value['output']['isBuffer'] is True,'actual ordinary Buffer report')
    if row['direction']=='decode':need(output==RAW[row['fixture']],'whole actual guest decoded fixture equality');COUNTS['guestDecodedPayloadsCompared']+=1
    else:
        if encoded_reference is not None:need(output==encoded_reference,'whole within-provider encoded determinism')
        COUNTS['guestEncodedPayloadsCompared']+=1
    COUNTS['fullGuestOutputPayloadsCompared']+=1
    return output

def verify_case(root,record,kind,arm,cross_stream=None):
    row=CASES[record['caseId']]
    if cross_stream is None:
        input_bytes=RAW[row['fixture']] if row['direction']=='encode' else stream_bytes(NODE_BY_CASE[row['index']]);source='raw-fixture' if row['direction']=='encode' else 'node-oracle-input';stage=None
    else:
        need(row['direction']=='decode','crossdecode actual decode case');input_bytes=stream_bytes(cross_stream);source='staged-validation';stage={'caseId':row['index'],'streamId':cross_stream['streamId'],'provider':cross_stream['provider'],'fixture':cross_stream['fixture'],'format':cross_stream['format'],'parentDeclaredSha256':cross_stream['encodedSha256']}
    need(len(record['rawRows'])==4,'four retained case evidence rows')
    first=raw_call(root,record['rawRows'][0],'observe');second=raw_call(root,record['rawRows'][1],'observe');batch=raw_call(root,record['rawRows'][2],'batch');wrapped=raw_call(root,record['rawRows'][3],'validate')
    key=(arm,row['fixture'],row['format']);baseline=ENCODED.get(key)
    a=observation(first,row,arm,input_bytes,source,stage,baseline);b=observation(second,row,arm,input_bytes,source,stage,a);need(a==b,'full adjacent separate observation bytes equal')
    need(wrapped['kind']=='codec-cost-validation-v1' and wrapped['caseId']==row['index'] and wrapped['requestKind']==('primary' if cross_stream is None else 'crossdecode') and wrapped['withinOneOuterExport'] is True and wrapped['separateHostCallInterleavingProved'] is False and len(wrapped['observations'])==2,'bounded validate full pair shape')
    c=observation(wrapped['observations'][0],row,arm,input_bytes,source,stage,a);d=observation(wrapped['observations'][1],row,arm,input_bytes,source,stage,a);need(a==b==c==d,'separate and within-export complete pair equality')
    if row['direction']=='encode':
        need(cross_stream is None,'encoder in primary only')
        if baseline is None:ENCODED[key]=a
        else:need(a==baseline,'all retained/fresh rotations deterministic full encoding')
    aggregate=2166136261
    for value in [fnv(a),len(a),0]:aggregate=((aggregate^(value&0xffffffff))*16777619)&0xffffffff
    need(batch['schemaVersion']==1 and batch['kind']=='codec-cost-batch-v1' and batch['caseId']==row['index'] and batch['caseName']==row['id'] and batch['operations']==1 and batch['inputBytes']==len(input_bytes) and batch['totalOutputBytes']==len(a) and batch['lastOutputBytes']==len(a) and batch['lastOutputFNV1aU32']==fnv(a) and batch['aggregateFNV1aU32']==aggregate and batch['outputArraysRetained'] is False,'untimed N1 compact output agrees with whole output')
    need(record['withinExportPairCompared'] is True if cross_stream is None else record['adjacentFullPairChecked'] is True,'actual adjacent pair marker')
    COUNTS['guestCasesOrEdgesCompared']+=1

def frame(format,encoded,raw):
    if format=='zlib':
        need(len(encoded)>=8 and ((encoded[0]<<8)|encoded[1])%31==0 and encoded[0]&15==8 and encoded[0]>>4<=7 and encoded[1]&32==0,'strict zlib header/no dictionary')
        a=1;b=0
        for byte in raw:a=(a+byte)%65521;b=(b+a)%65521
        checksum=(b<<16)|a;need(int.from_bytes(encoded[-4:],'big')==checksum,'whole raw Adler trailer')
        expected={'format':'zlib','header':list(encoded[:2]),'rawAdler32':checksum,'dictionary':False,'fullDeflateParsing':False};payload=encoded[2:-4]
    elif format=='gzip':
        need(len(encoded)>=20 and encoded[:4]==b'\x1f\x8b\x08\0' and encoded[4:8]==b'\0'*4,'strict fixed gzip header')
        crc=binascii.crc32(raw)&0xffffffff;need(int.from_bytes(encoded[-8:-4],'little')==crc and int.from_bytes(encoded[-4:],'little')==len(raw),'whole raw CRC/ISIZE trailer')
        expected={'format':'gzip','header':list(encoded[:10]),'rawCRC32':crc,'rawISize':len(raw),'mtime':0,'memberCountBasis':'fixed header/trailer only; independent raw payload consumption audit required','fullDeflateParsing':False};payload=encoded[10:-8]
    else:
        need(format=='raw','finite format');expected={'format':'raw','framing':'none','fullDeflateParsing':False};payload=encoded
    return expected,payload

def verify_node(edge,prefix,index):
    stream=STREAMS[edge['streamId']];encoded=stream_bytes(stream);expected_raw=RAW[edge['fixture']]
    need(edge['schemaVersion']==1 and edge['decoder']=='node-22.14.0' and edge['freshActualDecode'] is True and edge['earlierNodeOwnDecodeReused'] is False and edge['timing'] is False,'fresh actual Node edge marker')
    name=prefix+'-'+str(index).zfill(2);complete=data(R/(name+'-complete.json'));need(complete==edge,'exact Node completed edge record')
    started=data(R/(name+'-started.json'));need(started['record']==stream and started['partial'] is True and started['freshDecodeRequired'] is True and started['earlierNodeOwnDecodeIsNotReused'] is True,'fresh current full Node input before call')
    whole=data(R/edge['whole']['path'],edge['whole']);need(whole['retained']==edge['retained'] and whole['partial'] is True,'exact Node retained metadata')
    observed=whole['observed'];need(observed['streamId']==stream['streamId'] and observed['provider']==stream['provider'] and observed['decoder']=='node-22.14.0','Node observed identity')
    need(full(observed['input'])==encoded and full(observed['output'],524288)==expected_raw and observed['fullRawEqual'] is True and observed['sourceBytesConsumed']==len(encoded),'whole actual Node input/output/full consumption')
    framing,payload=frame(stream['format'],encoded,expected_raw);need(observed['framing']==framing and observed['rawPayload']=={'bytes':len(payload),'sourceBytesConsumed':len(payload),'fullRawEqual':True,'formatAudit':'actual Node inflateRawSync consumed exact strict-wrapper payload'},'strict wrapper and raw payload consumption metadata')
    retained={row['path']:row for row in edge['retained']};need(len(retained)==(6 if stream['format']=='raw' else 11),'finite Node retention count')
    inputname=name+'-cross-input-'+stream['streamId']+'.bin';need(read(R/inputname,retained[inputname])==encoded,'plain U8 whole compressed input retained as binary');COUNTS['nodeUint8InputBinaryFiles']+=1
    outname=name+'-cross-output-'+stream['streamId'];methods=[('',{'zlib':'inflateSync','gzip':'gunzipSync','raw':'inflateRawSync'}[stream['format']],len(encoded))]
    if stream['format']!='raw':methods.append(('-raw-payload','inflateRawSync',len(payload)))
    for suffix,method,consumed in methods:
        base=outname+suffix;binname=base+'-decoded.bin';need(read(R/binname,retained[binname])==expected_raw,'whole Node info Buffer output retained as binary');COUNTS['nodeDecodedBufferBinaryFiles']+=1
        opaque={'type':'object','kind':'opaque','propertiesRead':False,'fullPrimitiveValueCaptured':False}
        need(data(R/(base+'-return-transport.json'),retained[base+'-return-transport.json'])=={'schemaVersion':1,'kind':'node-codec-call-returned','method':method,'value':opaque},'genuine Node opaque return transport remains honest')
        for field in ['buffer','engine']:need(data(R/(base+'-'+field+'-transport.json'),retained[base+'-'+field+'-transport.json'])==opaque,'explicit opaque Node object field transport')
        need(data(R/(base+'-sourceBytesConsumed-transport.json'),retained[base+'-sourceBytesConsumed-transport.json'])=={'type':'number','kind':'finite','value':consumed,'fullPrimitiveValueCaptured':True},'full primitive Node public consumed count')
        COUNTS['nodeTransportJsonFiles']+=4
    COUNTS['freshNodeEdgesCompared']+=1

INDEX={}
rawindex=(R/'index.json').read_bytes();need(digest(rawindex)=='e8da5ddba338e578fb8bdce83791c563465be440c1fe8a5c39f0ff9c4105aa7e','actual index pinned')
index=json.loads(rawindex);INDEX={row['path']:row for row in index['files']};need(len(INDEX)==len(index['files'])==11440,'unique complete actual index')
read(R/'index.json')
results=data(R/'results.json');need(digest((R/'results.json').read_bytes())=='ecd0ac44ecafc624471f6b2c64224facb0a087adf0a88adc30b11096cfe900d5','actual result pinned')
oracle=data(results['oracle']['path'],results['oracle']);need(results['oracle']['sha256']=='bf1312f33bc4df030b16a0f52a8018b2cf50c7dcf4fbad31699fbd9217c9fcf5','actual oracle pinned')
CASES=data(Z/'cost-jco-correctness-candidate-v2/cases.json');need(len(CASES)==30 and [x['index'] for x in CASES]==list(range(30)),'exact30 case table')
for actual,expected in zip(oracle['cases'],CASES):need(actual['caseId']==expected['index'] and actual['caseName']==expected['id'] and actual['fixture']==expected['fixture'] and actual['format']==expected['format'] and actual['direction']==expected['direction'],'original oracle/case association')
RAW={}
for row in oracle['rawFixtures']:
    value=full(row,524288);need(row['id'] in FIXTURES and value==fixture(row['id']),'complete pure deterministic trusted fixture');RAW[row['id']]=value
need(set(RAW)==set(FIXTURES),'all5 raw fixtures')
NODE_BY_CASE={row['caseId']:row for row in oracle['encodedStreams']};need(len(NODE_BY_CASE)==15,'all15 original Node input streams')
STREAMS={}
for row in oracle['encodedStreams']:stream_bytes(row);STREAMS[row['streamId']]=row
ENCODED={};primary=[];cross=[];origin_counts=Counter()
for origin in results['origins']:
    job=origin['job'];origin_counts[job['kind']]+=1;path=Path(origin['workerResults']['path']);worker=data(path,origin['workerResults']);need(worker['job']==job,'actual worker job association');observed=worker['observed'];root=path.parent
    if job['kind'] in ['retained-primary','fresh-primary']:
        arm=job['arm'];wanted=[(case_id,rotation) for rotation in range(3) for case_id in range(30)] if job['kind']=='retained-primary' else [(job['caseId'],0)]
        need([(x['caseId'],x['rotation']) for x in observed['records']]==wanted,'exact retained/fresh case rotation schedule')
        for record in observed['records']:
            verify_case(root,record,job['kind'],arm);primary.append({**record,'kind':job['kind']})
        expected_streams=[]
        for row in observed['streams']:
            value=stream_bytes(row);case=CASES[row['caseId']-1];need(case['direction']=='encode' and row['provider']==arm and row['caseId']==case['index']+1 and row['fixture']==case['fixture'] and row['format']==case['format'] and value==ENCODED[(arm,case['fixture'],case['format'])],'derived stream binds full actual encoded output')
            old=STREAMS.get(row['streamId']);need(old is None or old==row,'stable stream record across retained/fresh contexts');STREAMS[row['streamId']]=row;expected_streams.append(row['streamId'])
        need(len(expected_streams)==(15 if job['kind']=='retained-primary' else int(CASES[job['caseId']]['direction']=='encode')),'all actual encoder streams retained')
    else:
        need(job['kind'] in ['main-crossdecode','off-guest-crossdecode'],'finite worker kinds');stream=job['stream'];stream_bytes(stream);cross.append((origin,worker,observed))
need(origin_counts=={'retained-primary':3,'fresh-primary':90,'main-crossdecode':90,'off-guest-crossdecode':45},'exact228 worker job kinds')
need(len(STREAMS)==60,'all15 Node+45 actual guest encoder streams')
for origin,worker,record in cross:
    job=origin['job'];stream=job['stream'];need(STREAMS[stream['streamId']]==stream and record['streamId']==stream['streamId'] and record['provider']==stream['provider'] and record['decoder']==job['arm'] and record['caseId']==stream['caseId'],'actual crossdecode edge source stream/decoder binding')
    verify_case(Path(origin['workerResults']['path']).parent,record,job['kind'],job['arm'],stream)
for format in FORMATS:
    for name in FIXTURES:need(ENCODED[('fflate-off',name,format)]==ENCODED[('fflate-on',name,format)],'separate actual FF-OFF/FF-ON full encoded bytes equal')
need(len(primary)==360 and primary==results['primary'],'whole primary records collate exactly from actual workers')
expected_primary={(kind,arm,case_id,rotation) for kind in ['retained-primary','fresh-primary'] for arm in ARMS for rotation in (range(3) if kind=='retained-primary' else [0]) for case_id in range(30)}
actual_primary={(x['kind'],x['arm'],x['caseId'],x['rotation']) for x in results['primary']};need(len(actual_primary)==360 and actual_primary==expected_primary,'exact360 unique primary coverage')
stream_ids={provider+'.'+name+'.'+format for provider in PROVIDERS for name in FIXTURES for format in FORMATS}
main={(x['streamId'],x['decoder']) for x in results['mainEdges']};need(len(results['mainEdges'])==len(main)==135 and main=={(stream,decoder) for stream in stream_ids for decoder in PROVIDERS},'exact135 main matrix coverage')
offenc={(x['provider'],x['fixture'],x['format']) for x in results['offEncodings']};need(len(results['offEncodings'])==len(offenc)==15 and offenc=={('fflate-off',name,format) for name in FIXTURES for format in FORMATS},'exact15 separateFFOFF encodings')
offnode={(x['streamId'],x['decoder']) for x in results['offNodeEdges']};need(len(results['offNodeEdges'])==len(offnode)==15 and offnode=={('fflate-off.'+name+'.'+format,'node-22.14.0') for name in FIXTURES for format in FORMATS},'exact15 separateFFOFF Node matrix edges')
offguest={(x['streamId'],x['decoder']) for x in results['offGuestEdges']};need(len(results['offGuestEdges'])==len(offguest)==45 and offguest=={(stream,'fflate-off') for stream in stream_ids},'exact45 separateFFOFF guest matrix edges')
node_main=[x for x in results['mainEdges'] if x['decoder']=='node-22.14.0'];need(len(node_main)==45,'exact45 fresh primary Node edges')
for i,edge in enumerate(node_main):verify_node(edge,'node-main',i)
for i,edge in enumerate(results['offNodeEdges']):verify_node(edge,'node-off',i)
need(COUNTS['fullGuestOutputPayloadsCompared']==1980 and COUNTS['guestCasesOrEdgesCompared']==495 and COUNTS['freshNodeEdgesCompared']==60 and COUNTS['nodeUint8InputBinaryFiles']==60 and COUNTS['nodeDecodedBufferBinaryFiles']==100 and COUNTS['nodeTransportJsonFiles']==400,'complete finite byte retention totals')
sourcepaths=[Z/'cost-jco-correctness-candidate-v3/node-edges.mjs',Z/'cost-jco-correctness-candidate-v2/plan.mjs',Z/'cost-jco-correctness-candidate-v2/scenarios.mjs',Z/'cost-jco-correctness-candidate-v2/collector.mjs',Z/'cost-guest-oracle-candidate-v2/node-oracle.mjs',Z/'cost-guest-oracle-candidate-v2/node-transport.mjs']
for path in sourcepaths:read(path)
report={'schemaVersion':1,'state':'INDEPENDENT_FULL_CORRECTNESS_BYTE_NODE_RETENTION_AND_COVERAGE_SUBREVIEW_PASSED_V1','verifiedPassed':True,'reviewMode':'READ/HASH/DATA only; no codec or owner code execution','sourceResultSha256':digest((R/'results.json').read_bytes()),'sourceIndexSha256':digest(rawindex),'oracleSha256':results['oracle']['sha256'],'counts':dict(COUNTS),'jobKinds':dict(origin_counts),'rawFixturesReconstructedAndFullyCompared':5,'originalNodeStreamsRehashed':15,'actualGuestEncoderStreamsFullyCompared':45,'allEncoderStreamsIncludingNode':60,'primaryCoverage':360,'mainMatrixCoverage':135,'mainFreshNodeEdges':45,'mainFreshGuestEdges':90,'separateOffEncodings':15,'separateFreshOffNodeEdges':15,'separateFreshOffGuestEdges':45,'fullNodeBinaryFilesCompared':160,'nodeOpaqueObjectTransportRecordsNotRelabelledAsFullValues':True,'NodeU8InputsSnapshottedToWholeBinaryFiles':60,'wholeNodeInfoBufferOutputsSnapshottedToBinaryFiles':100,'zlibGzipHeadersAndRawFixtureTrailersIndependentlyCheckedAsData':True,'wrappedAndRawPayloadConsumedCountsMatched':True,'deflateBitstreamsDecodedByReviewer':False,'withinProviderEncodedDeterminismAcrossRetainedAndFreshContexts':True,'FFOffFFOnWholeEncodedEquality':True,'separateAndValidateGuestWholePairsEqual':True,'uniqueInputFilesRehashed':len(LEDGER),'sourceWitnessFiles':[LEDGER[str(x)] for x in sourcepaths],'reviewerOwnerWorkerNodeParserHelperCliCodecJcoGuestOrTimingExecuted':False,'runtimeAcceptanceClaim':False,'operationalAdmission':False,'sourcePromotionAllowed':False,'timingAllowed':False,'scope':'Complete finite bytes, data-checksum, source-stream and coverage relations. Actual process ownership, detailed counters, source closure and admission are separate parent checks. Existing original Node-own decodes are not substituted for the 60 fresh retained Node matrix edges.'}
with (HERE/'peer-bytes-inputs.json').open('x') as stream:json.dump({'schemaVersion':1,'files':list(LEDGER.values())},stream,indent=2);stream.write('\n')
with (HERE/'peer-bytes-review.json').open('x') as stream:json.dump(report,stream,indent=2);stream.write('\n')
print(json.dumps({'state':report['state'],'counts':dict(COUNTS),'uniqueFiles':len(LEDGER)}))
