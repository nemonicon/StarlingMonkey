"""Source assembly and artificial stdlib DATA checks only; no Node/guest/HTTP."""
from pathlib import Path
import ast,hashlib,json,runpy,zlib
HERE=Path(__file__).resolve().parent
checker=runpy.run_path(str(HERE/'verify-data.py'),run_name='inert_data_functions')
assembly=runpy.run_path(str(HERE/'build-entry.py'),run_name='pure_source_assembly')
checks=[]
def check(value,label):
    assert value,label;checks.append(label)
def refuses(call,label):
    try:call()
    except (ValueError,zlib.error):checks.append(label);return
    raise AssertionError(label)
for name in ('build-entry.py','verify-data.py','test-source.py'):ast.parse((HERE/name).read_text());checks.append('AST '+name)
check(assembly['render']()==(HERE/'guest-gzip.mjs').read_text(),'Exact Source assembly')
refs=json.loads((HERE/'source-references.json').read_text());original=Path(refs['v5Entry']['path']).read_text();boundary='// Source fragment inlined in the raw ESM. No call occurs during INIT.\nasync function prepareServer() {'
prefix=(HERE/'guest-gzip.mjs').read_text().split('// Dormant definitions only.')[0]
check(prefix.replace("\nimport __gzipProbeZlib from 'node:zlib';",'')==original.split(boundary)[0],'Exact V5 prefix/adapter except one pure import')
plan=json.loads((HERE/'plan.json').read_text());check(plan['actionsAllowed']is False and plan['actualEngine']is plan['actualComponent']is plan['actualRuntime']is None,'Dormant actions/actuals')
check(plan['wasmtimeHostArguments']['requiredLiteralFlags']==['--no-logging-prefix'],'Explicit standard unprefixed logging contract')
check(plan['futureConstructor']['returnedFunctionCount']is None and len(plan['selectedInterfaces'])==13,'No returned-function-count projection')
small=checker['payload']('small');large=checker['payload']('large')
check(len(small)==53 and len(large)==2097152,'Exact independent byte fixture sizes')
check(large[:16].hex()=='40919c650f3def7cf90d9f3f9648e64f','Independent fixture first16')
# Host Python zlib creates artificial DATA fixtures only, not guest/Node execution.
gzip=zlib.compress(small,wbits=31)
check(checker['gzip_member'](gzip,small)['decodedBytes']==53,'Artificial single gzip positive')
headers=b'HTTP/1.1 200 OK\r\nContent-Encoding: gzip\r\nContent-Length: '+str(len(gzip)).encode()+b'\r\n\r\n'
check(checker['http'](headers+gzip)[0]==gzip,'Content-Length positive')
chunked=b'HTTP/1.1 200 OK\r\nContent-Encoding: gzip\r\nTransfer-Encoding: chunked\r\n\r\n'+hex(len(gzip))[2:].encode()+b'\r\n'+gzip+b'\r\n0\r\n\r\n'
check(checker['http'](chunked)[0]==gzip,'Chunked positive')
for name,bad in [('truncated',gzip[:-1]),('concat',gzip+gzip),('tail',gzip+b'x'),('CRC',gzip[:-8]+bytes([gzip[-8]^1])+gzip[-7:])]:refuses(lambda b=bad:checker['gzip_member'](b,small),'Gzip refuses '+name)
refuses(lambda:checker['gzip_member'](gzip,b'wrong'),'Gzip refuses changed plaintext')
for name,bad in [('tail',headers+gzip+b'x'),('truncated',headers+gzip[:-1]),('chunk tail',chunked+b'x'),('missing final',chunked[:-2]),('trailer',chunked[:-2]+b'X: y\r\n\r\n'),('dual framing',chunked.replace(b'Transfer-Encoding:',b'Content-Length: 1\r\nTransfer-Encoding:')),('duplicate',headers.replace(b'Content-Encoding: gzip',b'Content-Encoding: gzip\r\nContent-Encoding: gzip')),('raw LF field',headers.replace(b'Content-Encoding: gzip',b'Content-Encoding: \ngzip')),('raw CR field',headers.replace(b'Content-Encoding: gzip',b'Content-Encoding: \rgzip')),('raw DEL field',headers.replace(b'Content-Encoding: gzip',b'Content-Encoding: \x7fgzip'))]:refuses(lambda b=bad:checker['http'](b),'HTTP refuses '+name)
refuses(lambda:json.loads('{"x":1,"x":2}',object_pairs_hook=checker['unique']),'JSON duplicate refusal')
record=dict(schemaVersion=1,suite='GZIP_COMPOSITION_PUBLIC_EVENTS_V1',caseId='small',sequence=1,event='start',inputBytes=53,compressedBytes=len(gzip),dataChunks=1,inputWriteFalseCount=0,inputDrainCount=0,responseWriteFalseCount=0,responseDrainCount=0,pauseCount=0,resumeCount=0,gzipFinish=True,gzipEnd=True,resEndCalled=True,resFinish=True,resClose=True,gzipClose=True,error=None)
labels=['start','gzip-finish','gzip-end','response-end-call','response-finish','response-close'];rows=[]
for case in ('small','large'):
 for seq,label in enumerate(labels,1):rows.append(dict(record,caseId=case,sequence=seq,event=label))
def raw(values):return b''.join(b'NEXT_GZIP_COMPOSITION_V1 '+json.dumps(r).encode()+b'\n'for r in values)
check(len(checker['events'](raw(rows))['small'])==6,'Artificial public event order positive')
mutants=[('bool sequence',dict(rows[0],sequence=True),0),('bool counter',dict(rows[0],compressedBytes=True),0),('error',dict(rows[0],error={}),0),('missing close',dict(rows[5],event='unknown'),5)]
for name,item,pos in mutants:
 values=list(rows);values[pos]=item;refuses(lambda v=values:checker['events'](raw(v)),'Events refuse '+name)
print(json.dumps(dict(sourceOnly=True,nodeOrGuestOrHttpInvoked=False,checks=len(checks),passed=True,largePlainSha256=hashlib.sha256(large).hexdigest(),checksPassed=checks)))
