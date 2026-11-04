#!/usr/bin/env python3
"""Read/stat/hash/JSON only. Never imports source peers or admission helpers."""
from pathlib import Path
import hashlib,json,stat
HERE=Path(__file__).resolve().parent;S=HERE.parent;D=S/'release-gates-activated-v2';P=S/'independent-release-gates-activated-v2-source-review-v1';O=Path('/tmp/starling-node-compat/consumers355-release-gates-preflight-v2-root')
FAMILY='562e4236c8f99a34323c57c26f92749dba4aaf3e5dc1a509d33ababd97d79250';PEER='971243204b05ddcf54ac305d48236650f5d54cf1de4b040534011e3a602e6e48';rows={};checks=[]
def need(v,label):
 if not v:raise AssertionError(label)
 checks.append(label)
def read(path,expected=None,n=None,collect=True):
 p=Path(path);a=p.lstat();assert stat.S_ISREG(a.st_mode)and not p.is_symlink();h=hashlib.sha256();chunks=[];size=0
 with p.open('rb')as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):
   h.update(chunk);size+=len(chunk)
   if collect:chunks.append(chunk)
 b=p.lstat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns)
 assert expected is None or h.hexdigest()==expected,(str(p),h.hexdigest(),expected)
 assert n is None or size==n
 rows[str(p)]={'path':str(p),'sha256':h.hexdigest(),'bytes':size};return b''.join(chunks)if collect else None
def js(path,sha=None):return json.loads(read(path,sha))
def ix(path,sha):
 p=Path(path);v=js(p,sha);names=set()
 for r in v['files']:
  assert r['path']not in names and not Path(r['path']).is_absolute()and all(x not in('','.','..')for x in r['path'].split('/'));names.add(r['path']);read(p.parent/r['path'],r['sha256'],r['bytes'],False)
 return v
def main():
 root=js(S/'release-gates-preflight-v2-root-results.json','170251e33f9ed46763ab28375f091609c5b56fd22a8febfac8d0e9b29532cec7');need(root['readOnlyAdmissionHelpersInvoked']is True and root['ordinaryGuestExportsComponentizationNativeCompilerHostOrTimingInvoked']is False and root['runtimeActionAuthorityIssued']is False,'Root actual read-only helper execution and no runtime action scope')
 for row in[root['generatedIndex'],root['generatedSourceReview']['index'],root['generatedSourceReview']['result'],root['reviewedPins'],root['actualAggregateTerminal'],root['oldV1FailurePreserved']]:read(row['path'],row['sha256'],row['bytes'],False)
 for item in root['observed']:
  for key in['terminal','stdout','stderr']:
   row=item[key];read(row['path'],row['sha256'],row['bytes'],False)
 peer=ix(P/'index.json',PEER);need(len(peer['files'])==26,'current exact26-source-peer capsule')
 pr=js(P/'results.json');need(pr['verifiedPassed']is True and pr['generatedIndexSha256']==FAMILY and pr['sourceOnly']is True and pr['ownerHelpersOrPreflightsInvoked']is False,'prior source peer remains source-only; no action transfer')
 ledger=js(P/'rehashed-files.json')['files'];need(len(ledger)==12591,'prior source/native/tool ledger12591 lexical originals')
 for r in ledger:read(r['path'],r['sha256'],r['bytes'],False)
 family=ix(D/'index.json',FAMILY);need(len(family['files'])==1727,'current1727 generated family members unchanged')
 config=js(D/'activation.json');pins=js(D/'reviewed-pins.json',config['pinsSha256']);bridge=read(D/'native-preflight.mjs').decode();entry=read(D/'entry.mjs').decode()
 seal=read(D/'input-freeze.json');configRaw=read(D/'activation.json');template=read(D/'native-preflight.template.mjs').decode();compiled=template.replace('@CONFIG_SHA@',hashlib.sha256(configRaw).hexdigest()).replace('@INPUTS_SHA@',hashlib.sha256(seal).hexdigest());need(compiled==bridge,'actual entry bridge still bound to exact config/manifest digests')
 aggregate=js(O/'terminal.json');need(aggregate['state']=='THREE_READ_ONLY_PREFLIGHTS_RAW_ZERO'and aggregate['guestOrComponentExecuted']is False,'final external aggregate allthree raw0/no component or guest')
 modes=['normal-off','normal-runtime','gc-off'];need([r['variant']for r in aggregate['records']]==modes,'actual mode order/count exactlythree')
 actual=[]
 for item in aggregate['records']:
  label=item['variant'];terminal=js(O/label/'terminal.json');need(terminal==item,'final mode terminal exactly equals aggregate '+label)
  need(terminal['rawExitCode']==0 and terminal['timeout']is False and terminal['readOnly']is True and terminal['guestOrComponentExecuted']is False,'actual raw0/no-timeout/read-only '+label)
  need(terminal['argv']==['/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',str(D/'entry.mjs'),'preflight',label],'exact pinned Node entry/mode argv '+label)
  stdout=read(item['stdout']['path'],item['stdout']['sha256'],item['stdout']['bytes']);stderr=read(item['stderr']['path'],item['stderr']['sha256'],item['stderr']['bytes']);need(stderr==b'','actual stderr empty '+label)
  value=json.loads(stdout);expected={'state':'READ_ONLY_GENUINE355_PREFLIGHT_PASSED','variant':label,'engineSha256':pins['variants'][label]['engineSha256'],'sourceFiles':355,'operationalAdmission':False,'guestExecuted':False};need(json.dumps(value,sort_keys=True)==json.dumps(expected,sort_keys=True),'whole actual typed final JSON value matches exact reviewed355 tuple '+label);need(value==next(r['stdoutValue']for r in root['observed']if r['variant']==label),'Root aggregate preserves whole actual stdout '+label)
  need(item['stdout']['bytes']=={'normal-off':224,'normal-runtime':228,'gc-off':220}[label],'complete expected scalar stdout length '+label)
  pin=pins['variants'][label];read(pin['enginePath'],pin['engineSha256'],pin['engineBytes'],False);read(pin['enginePath']+'.build.json',pin['receiptSha256'],None,False);read(pin['freezeReceiptPath'],pin['freezeReceiptSha256'],None,False)
  actual.append({'variant':label,'pid':item['pid'],'rawExitCode':0,'stdout':item['stdout'],'stderr':item['stderr'],'value':value,'elapsedOperationalSeconds':item['elapsedSeconds'],'engineSha256':pin['engineSha256']})
 need("const {validationPreflight}=await import('./native-preflight.mjs')"in entry and 'await value.recheck()'in entry,'executed preflight mode awaits actual validation and its recheck before final JSON')
 need('admit(native.metadata,variant,roots.admissionSourceRoot)'in bridge and 'admit(frame.metadata,variant,roots.admissionSourceRoot)'in bridge,'successful corrected initial/recheck caller uses configured full native/tool root')
 need(config['runtimeSourceRoot']==config['nativeFrozenSourceRoot']and config['admissionSourceRoot']==config['nativeConfiguredSourceRoot']and config['runtimeSourceRoot']!=config['admissionSourceRoot'],'actual configured/frozen root roles remain distinct')
 old=js(S/'release-gates-preflight-v1-root-failure-v2.json','bc1cd16985850ef243dc14295d75af655bed9eb6fe06e66bfb414d0565efbcf7');need(old['readOnlyAdmissionHelpersExecuted']is True,'old v1 failed attempt immutable with helper-execution clarification')
 # Hash all captured text/result records after reading, no imported helper calls.
 for row in list(rows.values()):read(row['path'],row['sha256'],row['bytes'],False)
 return{'schemaVersion':1,'state':'INDEPENDENT_CONSUMERS355_RELEASE_PREFLIGHT_V2_RESULTS_VERIFIED_V1','verifiedPassed':True,'generatedSourceIndexSha256':FAMILY,'sourcePeerIndexSha256':PEER,'threeModePreflightPassed':True,'actualModes':actual,'sourceNativeToolClosureCurrent':True,'sourcePeerLedgerRows':len(ledger),'uniqueLexicalPathsRehashed':len(rows),'configuredAdmissionRoot':config['admissionSourceRoot'],'frozenRuntimeRoot':config['runtimeSourceRoot'],'rootReadOnlyAdmissionHelpersExecuted':True,'intermediateHelperResultsIndividuallyRetained':False,'intermediateHelperChecksSupportedByAuthenticatedControlFlowAndTerminal':True,'oldV1FailureRetainedNotRelabelled':True,'reviewerOwnerHelpersOrPreflightImported':False,'reviewerNodeGuestCompilerNativeHostOrTimingExecuted':False,'guestOrComponentExecutionProved':False,'operationalAdmission':False,'runtimeAcceptanceClaim':False,'scope':'Actual final read-only source/config/native admission plus recheck in three modes, not new runtime/Node-parity/capacity/performance proof','rootAggregateSha256':'170251e33f9ed46763ab28375f091609c5b56fd22a8febfac8d0e9b29532cec7'}
if __name__=='__main__':
 r=main();(HERE/'results.json').write_text(json.dumps(r,indent=2)+'\n');(HERE/'checks.json').write_text(json.dumps({'checks':checks},indent=2)+'\n');(HERE/'source-references.json').write_text(json.dumps({'files':list(rows.values())},indent=2)+'\n');print(json.dumps({k:r[k]for k in['state','verifiedPassed','threeModePreflightPassed','uniqueLexicalPathsRehashed']}))
