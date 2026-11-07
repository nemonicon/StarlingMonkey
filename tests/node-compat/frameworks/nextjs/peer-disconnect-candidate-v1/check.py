"""Portable stdlib DATA checker. No JS, host, subprocess, API or target actions."""
from pathlib import Path
import base64,gzip,hashlib,io,json,tarfile
HERE=Path(__file__).resolve().parent
def digest(b):return dict(sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def frame(raw,partial=False):
 header,sep,encoded=raw.partition(b'\r\n\r\n');assert sep
 status=int(header.split(b' ')[1]);chunks=[]
 if b'transfer-encoding: chunked'in header.lower():
  offset=0
  while True:
   end=encoded.find(b'\r\n',offset)
   if end<0:assert partial;break
   length=int(encoded[offset:end].split(b';')[0],16);offset=end+2
   if not length:break
   if offset+length+2>len(encoded):assert partial;break
   assert encoded[offset+length:offset+length+2]==b'\r\n'
   chunks.append(encoded[offset:offset+length]);offset+=length+2
 else:chunks=[encoded]
 return status,header.decode('latin1'),b''.join(chunks)
def main():
 if (HERE/'index.json').exists():
  index=json.loads((HERE/'index.json').read_text());names={r['path']for r in index['files']}
  actual={p.relative_to(HERE).as_posix()for p in HERE.rglob('*')if p.is_file()and p!=HERE/'index.json'}
  assert actual==names
  for r in index['files']:assert digest((HERE/r['path']).read_bytes())=={k:r[k]for k in ['sha256','bytes']}
 evidence=json.loads((HERE/'host-evidence.json').read_text());bundle=(HERE/'host-raw.tar.gz').read_bytes()
 assert digest(bundle)==evidence['bundle'];records={r['archivePath']:r for r in evidence['records']};raw={}
 with tarfile.open(fileobj=io.BytesIO(gzip.decompress(bundle)),mode='r:')as archive:
  members=archive.getmembers();assert len(members)==len(records)
  for m in members:
   assert m.isfile()and m.name in records and m.name not in raw
   b=archive.extractfile(m).read();assert digest(b)=={k:records[m.name][k]for k in ['sha256','bytes']};b.decode('utf8');raw[m.name]=b
 assert set(raw)==set(records)
 host=json.loads((HERE/'host-check-results.json').read_text());assert host['passed']and host['sourceProtectionPassed']
 final=json.loads((HERE/'final-grammar-results.json').read_text());assert final['passed']and final['inputBookendsEqual']and final['noTcpOrGuestRerun']
 phases=[(p,'0/'+p['name'])for p in host['phases']]+[(p,'1/'+p['name'])for p in final['phases']]
 for p,prefix in phases:
  for key,file in [('terminal','terminal.json'),('stdout','stdout.log'),('stderr','stderr.log')]:
   assert digest(raw[prefix+'/'+file])=={k:p[key][k]for k in ['sha256','bytes']}
  terminal=json.loads(raw[prefix+'/terminal.json']);started=json.loads(raw[prefix+'/started.json'])
  assert terminal['rawExitCode']==0 and terminal['parentOwnedGroupGone']and terminal['allObservedOwnedGroupsGone']
  assert not terminal['timeout']and not terminal['forcedCleanup']
  assert all(terminal[k]==[]for k in ['errors','signals','interruptedSignals','remainingObservedPids'])
  assert started['argv']==p['argv']and started['timeoutSeconds']==p.get('seconds',30)
 data=json.loads(raw['0/node-localhost-reference/stdout.log']);events=data['nodeEvents']
 assert events==[json.loads(line)for line in raw['0/node-localhost-reference/stderr.log'].decode().splitlines()]
 assert [e['sequence']for e in events]==list(range(1,len(events)+1))
 assert data['hostReferenceCollectionPassed']and not data['forcedCleanup']and data['remainingSockets']==data['waiters']==0
 assert data['nodeVersion']=='v22.14.0'and data['pureCaptureChecks']==5
 assert data['wasiGuestPeerDisconnectCoverage']is False and data['nodeWasiTcpParityClaimed']is False
 assert data['requestSignalLinkedToPeer']is False and data['guestOrEngineOrCompilerExecuted']is False
 labels=['healthy-upload','healthy-output','partial-upload','inspect-after-upload','output-close','inspect-after-output']
 assert [c['label']for c in data['cases']]==labels
 cases={c['label']:c for c in data['cases']}
 for label,c in cases.items():
  b=base64.b64decode(c['rawBase64'],validate=True);assert len(b)==c['rawBytes']
  status,header,body=frame(b,label=='output-close');assert (status,header)==(c['status'],c['headers'])
  assert len(body)==c['decodedBodyBytes']and body==base64.b64decode(c['decodedBodyBase64'],validate=True)
 assert json.loads(base64.b64decode(cases['healthy-upload']['decodedBodyBase64']))['complete']is True
 body=base64.b64decode(cases['healthy-output']['decodedBodyBase64']);assert len(body)==32768
 for n in range(8):assert body[n*4096:(n+1)*4096]==bytes([65+n])*4096
 upload=[e for e in events if e['label']=='partial-upload'];out=[e for e in events if e['label']=='output-close']
 milestone=cases['partial-upload']['synchronizedMilestone'];assert milestone in upload and milestone['inputBytes']==1024
 assert milestone['phase']=='node-input-read-invocation-attempt'and milestone['hostReadEnteredOrBlockedProved']is False
 assert any(e['phase']=='node-input-read-failed'and e['error'].get('code')=='ECONNRESET'for e in upload)
 assert any(e['phase']=='handler-body-finally'and e['received']==1024 and e['signalAborted']is False for e in upload)
 failure=next(e for e in out if e['phase']=='node-output-write-failed')
 assert failure['error']['code']=='ERR_STREAM_DESTROYED'and cases['output-close']['firstBodyBeforeClose']is True
 assert cases['output-close']['decodedBodyBytes']>0
 for phase in ['producer-cancel-returned','node-response-reader-cancel-returned','node-adapter-finally-returned']:
  assert any(e['phase']==phase and e['sequence']>failure['sequence']for e in out)
 for label in ['inspect-after-upload','inspect-after-output']:
  c=cases[label];assert c['status']==200
  inspection=json.loads(base64.b64decode(c['decodedBodyBase64']))['inspection'];assert inspection['firstLabel']=='healthy-upload'
  assert inspection['lastOrdinal']==(4 if label=='inspect-after-upload'else 6)
 # Actual host backend and shared cases remain identical to the original phase inputs.
 ledger=json.loads((HERE/'source-inputs.json').read_text())
 for name in ['diagnostic-common.mjs','diagnostic-handler.mjs','node-control.mjs','run-host.py']:
  rows=[r for r in ledger['inputs']if r['path']==str(HERE/name)];assert len(rows)==1
  assert digest((HERE/name).read_bytes())=={k:rows[0][k]for k in ['sha256','bytes']}
 result=dict(schemaVersion=1,state='PEER_DISCONNECT_SOURCE_AND_NODE_REFERENCE_DATA_VERIFIED_V1',
  nodeReferencePassed=True,grammarCommands=len(phases)-1,nodeWorkloads=1,nodeEvents=len(events),
  healthyUploadBytes=8192,healthyOutputBytes=32768,partialUploadBytes=1024,
  nodeInputReadError='ECONNRESET',nodeLaterWriteError='ERR_STREAM_DESTROYED',
  nodeProducerAndReaderCancellationObserved=True,baselineRequestSignalAborted=False,
  inspectOrdinals=[4,6],sourceProtectionAtOriginalNodeRun=True,
  unexecutedGuestDiagnosticGrammarOnly=True,guestOrEngineOrComponentExecuted=False,
  wasiPeerDisconnectCoverage=False,nodeWasiTransportParityClaimed=False,
  nativeDisposalCountsOrStoreDeathProved=False,allPendingSourceOrRuntimeSlotsIssued=False)
 print(json.dumps(result,indent=2))
 return result
if __name__=='__main__':main()
