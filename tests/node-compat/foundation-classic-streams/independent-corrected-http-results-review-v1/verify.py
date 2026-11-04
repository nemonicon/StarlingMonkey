#!/usr/bin/env python3
"""Completed-output reader only: no host, guest, tool, preflight or owner imports."""
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from binary_reader import sections,uint,string,core_imports
from host_checks import equal,properties,response

HERE=Path(__file__).resolve().parent
FAMILY=HERE.parent
ADOPT=FAMILY/'production-adoption-v1'
ROOT=Path('/tmp/starling-node-compat/production-classic-corrected-http-v1/http')
OUT=ROOT/'http-joint'
SOURCE=Path('/private/tmp/starling-node-compat/classic-trace-source-v1/tests/node-compat/foundation-classic-streams/production-trace-http-activated-v1')
STAGED_TESTS=SOURCE.parents[1]
IMPORTS=sorted(['wasi:clocks/monotonic-clock@0.2.10','wasi:http/types@0.2.10','wasi:io/error@0.2.10','wasi:io/poll@0.2.10','wasi:io/streams@0.2.10','wasi:random/random@0.2.10'])
COMPONENT='24d76605a182ad21b0b0196570afd571737e549d2d89a1a4b30a542b4ab96efc'
seen={}
def checked(path,pin=None,size=None):
 path=Path(path);before=path.lstat();assert stat.S_ISREG(before.st_mode),str(path)
 digest=hashlib.sha256()
 with path.open('rb')as stream:
  for chunk in iter(lambda:stream.read(1024*1024),b''):digest.update(chunk)
 after=path.lstat();assert(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),str(path)
 value=digest.hexdigest()
 if pin is not None:assert value==pin,str(path)
 if size is not None:assert before.st_size==size,str(path)
 seen[str(path)]={'path':str(path),'sha256':value,'bytes':before.st_size};return value
def load(path):checked(path);return json.loads(Path(path).read_bytes())
def indexed(root,pin,count=None):
 checked(root/'index.json',pin);doc=load(root/'index.json')
 if count is not None:assert len(doc['files'])==count
 for row in doc['files']:checked(root/row['path'],row['sha256'],row['bytes'])
 return doc
root_path=ADOPT/'corrected-http-combined-root-results.json'
checked(root_path,'6c4eb6def019642d7953b5cbe8d60c862688aa2306f928aa21d062e9a7d5472a')
receipt=load(root_path)
assert receipt['rootToolSession']==60088
assert all(receipt[key]==0 for key in['wasmtimeWrapperRawExit','washWrapperRawExit','finalAuditRawExit'])
assert len(receipt['evidence'])==29
for row in receipt['evidence']:checked(row['path'],row['sha256'],row['bytes'])
checked(ADOPT/'collect-corrected-http-results.py')
pre=FAMILY/'independent-corrected-http-package-review-v1'
indexed(pre,'62dbb34be82a07fc290d0f56e6e21c614473ff18d9d2b941275bbda43cd0152b',7)
pre_result=load(pre/'results.json')
for row in pre_result['verifiedFiles']:checked(row['path'],row['sha256'],row['bytes'])
checked(ADOPT/'corrected-http-component-phase-root-review-v1.json','b7cfeb6b2f4edf508fb12a4ff9e70fe7e4ae3a2f93ef6e5d83119557d06500e7')
phase=load(ADOPT/'corrected-http-component-phase-root-review-v1.json')
assert phase['state']=='ROOT_REVIEWED_CLASSIC_TRACE_COMBINED_HTTP_COMPONENT_V1'
pin=phase['component'];assert pin['state']=='reviewed-classic-trace-combined-http-component'
assert pin['root']==str(ROOT)and pin['sourceEntryPath']==str(SOURCE/'capability/http-component.mjs')
for path_key,sha_key in[('componentPath','componentSha256'),('auditPath','auditSha256'),('bundlePath','applicationBundleSha256'),('inputsPath','inputsSha256')]:checked(pin[path_key],pin[sha_key])
assert pin['componentSha256']==COMPONENT and pin['componentBytes']==64058731
audit=load(OUT/'component-audit.json');final=load(ROOT/'combined-http-results.json')
checked(ROOT/'combined-http-results.json','8be9dbd1fbd8741411f5cba2f156246cc010c4f20f8acc6ce4d85ac51806b34e')
assert final['state']=='COMBINED_HTTP_BASELINE_AND_CLASSIC19_VALIDATED'
assert final['requiresIndependentBuildAndWrapperTerminalExitZero']is True
assert final['instanceReuseClaim']is False and final['requestIsolationClaim']is False
assert final['sourceEntryPath']==pin['sourceEntryPath']and final['component']['componentSha256']==COMPONENT
assert len(final['artifacts'])==18
for row in final['artifacts']:checked(row['path'],row['sha256'],row['bytes'])
manifest=load(SOURCE/'input-freeze.json');assert len(manifest['inputs'])==7496
equal(final['sourceFilesVerified'],manifest['inputs'])
for row in manifest['inputs']:checked((SOURCE/row['path']).resolve(),row['sha256'],row['bytes'])
runtime=Path(load(SOURCE/'source-binding.json')['runtimeRoot'])
runtime_manifest=load(runtime/'input-freeze.json')
for row in runtime_manifest['toolLinks']:
 path=Path(row['path']);assert path.is_symlink()and os.readlink(path)==row['linkText']and str(path.resolve())==row['resolvedTarget']
 if row['targetKind']=='file':checked(path.resolve(),row['targetSha256'],row['targetBytes'])
assert len(runtime_manifest['toolLinks'])==22
assert load(SOURCE/'capability/component-pins.json')['component']is None
assert audit['emittedImports']==audit['selectedInterfaces']==audit['allowedImports']==IMPORTS
assert audit['emittedExports']==['wasi:http/incoming-handler@0.2.10']
# Repeat only public-container parsing; no wasm tool or component instantiation.
imports=[];exports=[];nested=[]
for kind,part in sections(Path(pin['componentPath']).read_bytes(),bytes.fromhex('0061736d0d000100')):
 if kind==1:
  rows=core_imports(part);assert not any(r['module'].startswith('wasi:clocks/')or r['module']=='wasi_snapshot_preview1'for r in rows)
  nested.append({'sha256':hashlib.sha256(part).hexdigest(),'bytes':len(part),'importModules':sorted({r['module']for r in rows})})
 if kind not in[10,11]:continue
 count,pos=uint(part,0)
 for _ in range(count):
  assert part[pos]==0;name,pos=string(part,pos+1);assert part[pos]==5;_,pos=uint(part,pos+1)
  if kind==10:imports.append(name)
  else:assert part[pos]==0;pos+=1;exports.append(name)
 assert pos==len(part)
assert sorted(imports)==IMPORTS and exports==audit['emittedExports']and len(nested)==3
graph=load(OUT/'component-types.json');clock=[(i,v)for i,v in enumerate(graph['interfaces'])if v['name']=='monotonic-clock'];assert len(clock)==1
clock_id,clock_type=clock[0];assert clock_type['functions']=={}and list(clock_type['types'])==['duration']
assert graph['types'][clock_type['types']['duration']]['kind']=={'type':'u64'}
core_rows=core_imports((OUT/'native-profile-http.core.wasm').read_bytes());equal(core_rows,audit['packagingAudit']['coreImports'])
assert not any(row['module'].startswith('wasi:clocks/')or row['module']=='wasi_snapshot_preview1'for row in core_rows)

wt=load(OUT/'wasmtime-v1/wasmtime-results.json');wash=load(ROOT/'http-joint-wasmcloud-results.json')
assert wt['command']==[wt['command'][0],'serve','--addr','127.0.0.1:0',pin['componentPath']]
checked(wt['command'][0],'a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c')
assert wt['wasmtime'].startswith('wasmtime 42.0.1 ')and wt['componentSha256']==COMPONENT and wt['componentBytes']==64058731
checked(wash['host']['binaryPath'],'365d896eaed3894f1c551a1ed7351c2aae9dfa5548ce82041ead92e6253d1954')
properties(wash['host'],{'version':'2.11.0','embeddedWasmtimeVersion':'48.0.7','unmodifiedOfficialBinary':True})
assert wash['component']['path']==pin['componentPath']and wash['component']['sha256']==COMPONENT
checked(wash['component']['deployedPath'],COMPONENT,64058731)
equal(wash['componentAudit'],audit);equal(wash['hostInspection']['emittedImports'],IMPORTS);equal(wash['hostInspection']['emittedExports'],exports)
config=load(wash['configPath']);equal(config,wash['configuration'])
for key in['components','plugins','host_plugins','volumes']:equal(config['dev'][key],[])
equal(config['dev']['service'],False)
for key in['allowedHosts','allowedIpNameLookups','allowedHostLoopbackPorts']:
 equal(config['workload'][key],[]);equal(wash['effectiveConfiguration']['workload'][key],[])
user_path=wash['configInspectionCommand'][wash['configInspectionCommand'].index('--user-config')+1]
equal(load(user_path),{})
assert wash['command'][wash['command'].index('--user-config')+1]==user_path
for key in['customHostPlugins','sidecars','volumes','outgoingHostAllowlist','ipNameLookupAllowlist','hostLoopbackPortAllowlist']:equal(wash['isolation'][key],[])
for key in['globalInstallationModified','dockerUsed','natsUsed','publicListener']:equal(wash['isolation'][key],False)
equal(wash['isolation']['isolatedXdgDirectories'],True)

# Independent JSON-only translation of the sealed host assertion functions.
validator_sources=['foundations/assert-http-report.mjs','foundations/assert-stream-web-report.mjs','foundations/assert-protected-abort-report.mjs','entropy/assert-http-report.mjs','core-expectations.mjs']
for relative in validator_sources:checked(STAGED_TESTS/relative)
for name in['validate-combined.mjs','validate-hosts.mjs']:checked(SOURCE/'capability'/name)
oracle_path=STAGED_TESTS/'foundation-classic-streams/implementation-candidate-v1/node-final-acceptance-results.json'
checked(oracle_path,'88bd20781a396e6fd178d3b014a98495fec848eb28adb81c80e7dc838f4686ce')
classic_expected=load(oracle_path)['expected'];assert len(classic_expected)==19
events=load(STAGED_TESTS/'foundation-events/native-node-results.json')
ownership=load(STAGED_TESTS/'entropy/owned-input-node-results.json')['cases']
equal(audit['coreExpectations']['unsupportedStatic'],['copyBytesFrom','of','allocUnsafeSlow','compare','concat'])
assert audit['coreExpectations']['prototypeRefusals']==91
for relative,digest in audit['coreExpectations']['sourceHashes'].items():checked(Path(audit['engineSourceRoot'])/relative,digest)
observations=[];counters=[]
for name,host in[('wasmtime',wt),('wash',wash)]:
 assert host['process']['stopped']is True;equal(host['process']['exitStatus'],{'code':0,'signal':None})
 assert len(host['responses'])==3
 samples=[];counts=[]
 for row in host['responses']:
  equal(row['status'],200);tag=row['requestTag']if'requestTag'in row else row['request']
  data=response(row['body'],audit,tag,classic_expected,events,ownership)
  samples.append(data.pop('randomBytes'));counts.append(data['counter'])
  assert data['symbol']['sameAsNodeRegistry']is False
  observations.append({'host':name,'request':tag,'status':row['status'],**data})
 assert len(set(samples))==3
 counters.append(counts)
equal(counters,final['counters']);equal(counters,receipt['counters']);equal(counters,[[1,1,1],[1,1,1]])
assert len(observations)==6
for name in['production-admission-complete.json','wasmtime-v1/production-admission-complete.json']:
 complete=load(OUT/name);assert complete['sourceInputsRecheckedAfterRun']is True and complete['inputClosure']['sha256']==pin['sourceInputSha256']and complete['inputClosure']['files']==7496
wash_complete=load(ROOT/'wash/production-admission-complete.json');equal(wash_complete,complete)
for name in['wasmtime','wash','audit']:
 terminal=load(Path('/tmp/starling-node-compat/classic-corrected-http-'+name+'-v1.terminal.json'));assert terminal['returncode']==0
 assert Path('/tmp/starling-node-compat/classic-corrected-http-'+name+'-v1.stderr.log').stat().st_size==0
assert Path('/tmp/starling-node-compat/classic-corrected-http-wasmtime-v1.stdout.log').read_bytes()==(OUT/'wasmtime-v1/wasmtime-results.json').read_bytes()
audit_stdout=json.loads(Path('/tmp/starling-node-compat/classic-corrected-http-audit-v1.stdout.log').read_bytes());assert audit_stdout['state']==final['state']and audit_stdout['componentSha256']==COMPONENT
for row in list(seen.values()):checked(row['path'],row['sha256'],row['bytes'])
report={'schemaVersion':1,'state':'INDEPENDENT_ACTUAL_CORRECTED_COMBINED_HTTP_RESULTS_VERIFIED','rootReceiptSha256':checked(root_path),'finalReportSha256':checked(ROOT/'combined-http-results.json'),'componentSha256':COMPONENT,'componentBytes':64058731,'sourceEntryPath':pin['sourceEntryPath'],'sourceAndInputClosureRowsRehashed':7496,'artifactRecordsVerified':18,'rootEvidenceRecordsVerified':29,'responsesVerified':6,'requestsPerHost':3,'baselineSchema':5,'ordinaryClassicGroupsPerResponse':19,'protectedAbortGroupsPerResponse':29,'ordinaryGroupOccurrences':114,'protectedGroupOccurrences':174,'validationMethod':'Independent strict-type Python comparisons of persisted JSON, translated from sealed baseline/combined/entropy/streamweb/protected assertions; full Node oracle arrays, no owner JS imports or guest/host reruns.','observations':observations,'counters':counters,'instanceReuseClaim':False,'requestIsolationClaim':False,'publicComponentImports':sorted(imports),'publicComponentExports':exports,'clockDurationTypeOnlyU64':True,'embeddedCores':nested,'noCoreClockOrPreview1':True,'officialBinaryHashesVerified':True,'deployedWashCopyByteIdentical':True,'originalBuildAndEntryPathsPreserved':True,'emptyOutgoingAllowlistsPluginsSidecarsVolumesAndUserConfig':True,'reportedHostCleanup':{'bothStopped':True,'exitCode':0,'signal':None,'processEventsObservedByReviewer':False},'rootReportedRawWrapperAndAuditExits':[0,0,0],'postHostAdmissionRecordsVerified':3,'sourceNativeToolStaticPackagingProofRehashed':True,'earlierEnvironmentFailureAndUnknownTerminalPreserved':True,'ownerActionsHelpersOrPreflightOrNodeOrGuestOrHostOrNativeOrStaticToolsRerun':False,'runtimeAcceptanceClaim':False,'performanceClaim':False,'limitations':['Only fresh baseline schema5/protected29 plus ordinaryclassic19 on the same component across two stock hosts.','Counter1/1/1 is observation only, not instance reuse or request isolation.','Known fresh then-getter and Symbol gaps, combinedGC coowners, ALS/reset/cancellation and full Node/Streams remain out of scope.','No outgoingHTTP/customhost/callableclock, memory or performance claim.'],'verifiedFiles':sorted(seen.values(),key=lambda row:row['path'])}
with(HERE/'results.json').open('x')as stream:json.dump(report,stream,indent=2);stream.write('\n')
print(json.dumps({'state':report['state'],'verifiedPaths':len(seen),'responses':6,'ordinaryGroups':19,'protectedGroups':29,'counters':counters}))
