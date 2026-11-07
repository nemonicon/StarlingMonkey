"""Strict retained DATA only; no guest/Node/producer evaluation or network."""
import argparse,binascii,hashlib,json,re,stat,struct,zlib
from pathlib import Path
CASES=('small','large')

def need(value,message):
    if value is not True: raise ValueError(message)

def unique(pairs):
    result={}
    for k,v in pairs:
        need(k not in result,'Duplicate JSON key'); result[k]=v
    return result

def read(path,cap):
    path=Path(path); before=path.lstat()
    need(path.is_absolute() and path.resolve()==path and not any(p.is_symlink() for p in (path,*path.parents)),'Canonical input')
    need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_size<=cap,'Bounded independent input')
    raw=path.read_bytes(); after=path.lstat()
    need(all(getattr(before,k)==getattr(after,k) for k in ('st_dev','st_ino','st_mode','st_nlink','st_size','st_mtime_ns','st_ctime_ns')),'Read bookend')
    return raw

def document(path,cap=262144): return json.loads(read(path,cap),object_pairs_hook=unique)

def checked(ref,root,name,cap):
    need(type(ref) is dict and set(ref)=={'path','sha256','bytes'} and type(ref['bytes']) is int,'Descriptor schema')
    p=Path(ref['path']);need(p==root/name,'Confined declared role')
    b=read(p,cap);need(len(b)==ref['bytes'] and hashlib.sha256(b).hexdigest()==ref['sha256'],'Descriptor bytes')
    return b

def payload(case_id):
    if case_id=='small':return b'NEXT_GZIP_COMPOSITION_SMALL_V1\nplain finite response\n'
    need(case_id=='large','Fixed case');out=bytearray(2097152);n=0x6d2b79f5
    for at in range(len(out)):
        n=(n^(n<<13))&0xffffffff;n=(n^(n>>17))&0xffffffff;n=(n^(n<<5))&0xffffffff;out[at]=n>>24
    return bytes(out)

def http(wire):
    need(type(wire) is bytes and len(wire)<=4194304,'Wire bound')
    split=wire.find(b'\r\n\r\n');need(0<split<=16384,'HTTP header boundary')
    lines=wire[:split].split(b'\r\n');need(re.fullmatch(rb'HTTP/1\.[01] 200(?: [\x20-\x7e]*)?',lines[0]) is not None,'HTTP200')
    headers={}
    for line in lines[1:]:
        need(b':'in line and not line.startswith((b' ',b'\t')),'Ordinary HTTP header')
        key,value=line.split(b':',1);need(re.fullmatch(rb"[!#$%&'*+.^_`|~0-9A-Za-z-]+",key) is not None,'Header name')
        need(all(byte==9 or byte>=32 and byte!=127 for byte in value),'Raw HTTP field controls')
        name=key.decode('ascii').lower();need(name not in headers,'Unique selected response headers');headers[name]=value.strip(b' \t').decode('latin1')
    need(headers.get('content-encoding','').lower()=='gzip','One gzip encoding')
    body=wire[split+4:]
    if 'transfer-encoding'in headers:
        need(headers['transfer-encoding'].lower()=='chunked' and 'content-length'not in headers,'Single chunked framing')
        pos=0;chunks=[]
        for _ in range(4096):
            end=body.find(b'\r\n',pos);need(end>=pos and end-pos<=16,'Chunk header')
            token=body[pos:end];need(re.fullmatch(rb'[0-9a-fA-F]+',token) is not None,'Plain chunk length')
            size=int(token,16);pos=end+2
            if size==0:
                need(body[pos:]==b'\r\n','No undeclared trailers/extra message');return b''.join(chunks),headers
            need(pos+size+2<=len(body) and body[pos+size:pos+size+2]==b'\r\n','Complete chunk')
            chunks.append(body[pos:pos+size]);pos+=size+2
        raise ValueError('Chunk count bound')
    need('content-length'in headers and re.fullmatch('[0-9]+',headers['content-length']) is not None,'Explicit complete HTTP framing')
    need(len(body)==int(headers['content-length']),'Exact Content-Length/no tail');return body,headers

def gzip_member(encoded,expected):
    need(len(encoded)<=3145728 and len(encoded)>=18 and encoded[:3]==b'\x1f\x8b\x08','Gzip bound/header')
    d=zlib.decompressobj(31);plain=d.decompress(encoded,len(expected)+1)
    need(d.eof and not d.unused_data and not d.unconsumed_tail,'Exactly one complete gzip member/no tail')
    need(plain==expected and d.flush()==b'','Exact decoded fixture')
    crc,size=struct.unpack('<II',encoded[-8:]);need(crc==(binascii.crc32(expected)&0xffffffff) and size==(len(expected)&0xffffffff),'CRC32/ISIZE')
    return dict(encodedBytes=len(encoded),decodedBytes=len(plain),crc32=crc,isize=size,plainSha256=hashlib.sha256(plain).hexdigest(),completeSingleMember=True)

def events(raw):
    need(len(raw)<=8388608,'Guest log bound');result={k:[]for k in CASES};offset=0
    prefix=b'NEXT_GZIP_COMPOSITION_V1 '
    for number,line in enumerate(raw.splitlines(keepends=True),1):
        text=line.rstrip(b'\r\n')
        if text.startswith(prefix):
            value=json.loads(text[len(prefix):],object_pairs_hook=unique)
            need(value['suite']=='GZIP_COMPOSITION_PUBLIC_EVENTS_V1' and value['caseId']in result,'Marker role')
            result[value['caseId']].append(dict(line=number,byteOffset=offset,value=value))
        offset+=len(line)
    for case_id,rows in result.items():
        need(1<=len(rows)<=16,'Finite complete case log')
        need(all(type(r['value']['sequence'])is int for r in rows),'Strict event sequence numbers')
        need([r['value']['sequence']for r in rows]==list(range(1,len(rows)+1)),'Exact case event sequence')
        need(all(r['value']['error']is None for r in rows),'No public stream errors')
        for row in rows:
            value=row['value'];need(type(value['schemaVersion'])is int and value['schemaVersion']==1,'Marker version')
            for key in ('inputBytes','compressedBytes','dataChunks','inputWriteFalseCount','inputDrainCount','responseWriteFalseCount','responseDrainCount','pauseCount','resumeCount'):
                need(type(value[key])is int and 0<=value[key]<=8388608,'Strict every-row public counter')
            for key in ('gzipFinish','gzipEnd','resEndCalled','resFinish','resClose','gzipClose'):need(type(value[key])is bool,'Strict every-row public flag')
        labels=[r['value']['event']for r in rows]
        allowed={'start','first-input-drain','first-response-backpressure','first-response-drain','gzip-finish','gzip-end','response-end-call','response-finish','response-close','gzip-close'}
        need(labels[0]=='start' and set(labels)<=allowed,'Known public event roster/start')
        for label in ('start','gzip-finish','gzip-end','response-end-call','response-finish','response-close'):
            need(labels.count(label)==1,'Exactly one public event '+label)
        need(labels.index('gzip-end')<labels.index('response-end-call')<labels.index('response-finish')<labels.index('response-close'),'Public completion order')
        final=rows[-1]['value']
        need(all(final[k]is True for k in ('gzipFinish','gzipEnd','resEndCalled','resFinish','resClose')),'Normal public completion flags')
        for key in ('inputBytes','compressedBytes','dataChunks','inputWriteFalseCount','inputDrainCount','responseWriteFalseCount','responseDrainCount','pauseCount','resumeCount'):
            need(type(final[key])is int and 0<=final[key]<=8388608,'Strict bounded public counter')
    return result

def verify(capture_path,reference_path,guest_log):
    capture_path=Path(capture_path);reference_path=Path(reference_path)
    capture=document(capture_path);reference=document(reference_path);logs=events(read(guest_log,8388608))
    need(capture['suite']=='GZIP_COMPOSITION_RAW_WIRE_V1' and capture['semanticsInvoked']is False and capture['errors']==[],'Raw capture')
    need(re.fullmatch(r'http://127\.0\.0\.1:[1-9][0-9]{0,4}',capture['origin']) is not None,'Canonical recorded origin')
    port=int(capture['origin'].rsplit(':',1)[1]);need(0<port<=65535 and port!=80,'Canonical explicit port')
    need(reference['suite']=='INDEPENDENT_NODE_GZIP_COMPOSITION_REFERENCE_V1' and reference['node']=='v22.14.0' and reference['candidateCodeLoaded']is reference['httpOrServerInvoked']is False and reference['errors']==[] and reference['rawCaptureOnly']is True,'Independent Node reference')
    need([r['caseId']for r in capture['requests']]==list(CASES) and [r['caseId']for r in reference['cases']]==list(CASES),'Exact two-case order')
    checked_cases=[]
    for case_id,item,node in zip(CASES,capture['requests'],reference['cases']):
        expected=payload(case_id);need(item['method']=='GET' and item['path']=='/gzip-composition/'+case_id and item['url']==capture['origin']+item['path'],'Exact request role')
        need(item['error']is None and item['cleanupErrors']==[] and item['socketEndObserved']is item['socketCloseObserved']is True and item['socketHadError']is False,'Normal socket end and cleanup')
        need((item['initialReadDelayMs'],item['betweenReadDelayMs'],item['timeoutMs'])==(250,10,20000),'Declared ordinary delayed reader')
        wire=checked(item['wire'],capture_path.parent,case_id+'.http',4194304);need(item['receivedBytes']==len(wire),'Raw wire length')
        encoded,headers=http(wire);need(headers.get('x-gzip-composition-case')==case_id and headers.get('content-type','').split(';')[0]=='application/octet-stream','Response role')
        guest=gzip_member(encoded,expected)
        need(node['error']is None and 'finish'in node['events'] and 'end'in node['events'],'Node compressor completed')
        need(checked(node['plain'],reference_path.parent,case_id+'.plain',2097152)==expected,'Independent Node fixture')
        refgzip=checked(node['gzip'],reference_path.parent,case_id+'.gzip',3145728);node_decoded=gzip_member(refgzip,expected)
        need(node['encodedBytes']==len(refgzip),'Node encoded length')
        last=logs[case_id][-1]['value'];need(last['inputBytes']==len(expected) and last['compressedBytes']==len(encoded),'Public counters match wire')
        if case_id=='large':need(len(encoded)>65536 and len(refgzip)>65536,'Actual large gzip exceeds64KiB')
        checked_cases.append(dict(caseId=case_id,guest=guest,node=node_decoded,publicEventRecords=logs[case_id],wireVerified=True))
    large=logs['large'][-1]['value'];backpressure=all(large[k]>0 for k in ('responseWriteFalseCount','responseDrainCount','pauseCount','resumeCount'))
    return dict(schemaVersion=1,state='GZIP_COMPOSITION_RETAINED_DATA_CHECKED_V1',wireAndNormalCompletionVerified=True,
        publicResponseBackpressureObserved=backpressure,compositionProfilePassed=backpressure,
        cases=checked_cases,errors=[]if backpressure else ['Large response backpressure not observed; no backpressure-coverage claim'],
        privateWasiFinishCountProved=False,nativeResourceCountsProved=False,nextPostCauseProved=False,fullNextAccepted=False,adoption=False)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--capture',type=Path,required=True);p.add_argument('--node-reference',type=Path,required=True);p.add_argument('--guest-log',type=Path,required=True);a=p.parse_args()
    value=verify(a.capture,a.node_reference,a.guest_log);print(json.dumps(value));return 0 if value['compositionProfilePassed'] else 1
if __name__=='__main__':raise SystemExit(main())
