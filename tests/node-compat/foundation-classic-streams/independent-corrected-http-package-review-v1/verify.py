#!/usr/bin/env python3
"""Read-only HTTP packaging evidence and public binary reader. No target calls."""
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import stat
from binary_reader import sections, uint, string, core_imports

HERE=Path(__file__).resolve().parent
FAMILY=HERE.parent
ADOPT=FAMILY/'production-adoption-v1'
OUTPUT=Path('/tmp/starling-node-compat/production-classic-corrected-http-v1/http/http-joint')
SOURCE=Path('/private/tmp/starling-node-compat/classic-trace-source-v1/tests/node-compat/foundation-classic-streams/production-trace-http-activated-v1')
NATIVE=Path('/tmp/starling-node-compat/production-classic-trace-v1/native-freeze')
IMPORTS=sorted(['wasi:clocks/monotonic-clock@0.2.10','wasi:http/types@0.2.10','wasi:io/error@0.2.10','wasi:io/poll@0.2.10','wasi:io/streams@0.2.10','wasi:random/random@0.2.10'])
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
 checked(root/'index.json',pin);document=load(root/'index.json')
 if count is not None:assert len(document['files'])==count
 for row in document['files']:checked(root/row['path'],row['sha256'],row['bytes'])
 return document
root_path=ADOPT/'corrected-http-package-root-results.json'
checked(root_path,'9d3c68d6425f2ff4a264957b7acbad737f8d2dd5aedd56650455bbb7abc5f1e5')
root=load(root_path);assert root['buildRawOuterExit']==0 and root['buildSession']==71459 and len(root['files'])==25
for row in root['files']:checked(row['path'],row['sha256'],row['bytes'])
checked(ADOPT/'collect-corrected-http-package.py')
audit=load(OUTPUT/'component-audit.json');packaging=load(OUTPUT/'packaging-audit.json');types=load(OUTPUT/'component-types.json');complete=load(OUTPUT/'production-admission-complete.json')
component=OUTPUT/'native-profile-http.component.wasm';core=OUTPUT/'native-profile-http.core.wasm'
checked(component,'24d76605a182ad21b0b0196570afd571737e549d2d89a1a4b30a542b4ab96efc',64058731)
checked(core,'2c7fa6166b50993b2c2aacbb43919e2c614ac5da8744d77cad03d13a75a2c0a7',64047200)
checked(OUTPUT/'http.bundle.mjs','c91a66bfa1be4460dc63e925164685a99f90610ecb95c1690554d026d240f7ed')
assert audit['componentSha256']==root['componentSha256']and audit['applicationBundleSha256']==root['applicationBundleSha256']
assert audit['httpEntry']==str(SOURCE/'capability/http-component.mjs')==root['sourceEntryPath']
assert audit['emittedImports']==audit['selectedInterfaces']==audit['allowedImports']==IMPORTS
assert audit['emittedExports']==['wasi:http/incoming-handler@0.2.10']
expected_builtins=['node:buffer','node:child_process','node:path','node:path/posix','node:path/win32','node:events','node:string_decoder','node:assert','node:assert/strict','node:querystring','node:util','node:util/types','node:sys','node:stream/web','wasi:http/types@0.2.10','node:stream','node:stream/promises']
assert audit['bundleImports']==expected_builtins and len(audit['bundledModules'])==53
assert len(audit['builtinManifests'])==9 and audit['applicationBundleExports']==['incomingHandler']
assert audit['classicCombinedHTTP']['ordinaryGroups']==19
assert audit['classicCombinedHTTP']['nodeOracleSha256']=='88bd20781a396e6fd178d3b014a98495fec848eb28adb81c80e7dc838f4686ce'
assert audit['protectedAbortFoundationsFixture']is True and audit['foundationsIntegrationFixture']is True
assert audit['clockDependency']['typeOnly']is True and audit['clockDependency']['types']==['duration']
assert audit['clockDependency']['durationRepresentation']=='u64'and audit['clockDependency']['callableImports']==audit['clockDependency']['coreClockImports']==[]

# Decode top-level public component imports/exports, and every embedded core.
imports=[];exports=[];embedded=[]
for kind,part in sections(component.read_bytes(),bytes.fromhex('0061736d0d000100')):
 if kind==1:embedded.append(part)
 if kind not in[10,11]:continue
 count,pos=uint(part,0)
 for _ in range(count):
  assert part[pos]==0;name,pos=string(part,pos+1);sort=part[pos];pos+=1
  assert sort==5;target,pos=uint(part,pos)
  if kind==10:imports.append(name)
  else:
   assert part[pos]==0;pos+=1;exports.append(name)
 assert pos==len(part)
assert sorted(imports)==IMPORTS and exports==audit['emittedExports']
actual_core_imports=core_imports(core.read_bytes())
assert actual_core_imports==packaging['coreImports']
actual_modules=sorted({row['module']for row in actual_core_imports})
assert actual_modules==sorted(audit['executableCoreInterfaces'])==packaging['coreImportModules']
assert actual_modules==[value for value in IMPORTS if not value.startswith('wasi:clocks/')]
assert all('wasi_snapshot_preview1'not in row['module']and not row['module'].startswith('wasi:clocks/')for row in actual_core_imports)
standard=lambda data:[(kind,hashlib.sha256(part).hexdigest())for kind,part in sections(data,bytes.fromhex('0061736d01000000'))if kind!=0]
matches=[data for data in embedded if standard(data)==standard(core.read_bytes())]
assert len(matches)==1 and len(embedded)==3
nested=[]
for data in embedded:
 imports_in_core=core_imports(data)
 assert all('wasi_snapshot_preview1'not in row['module']and not row['module'].startswith('wasi:clocks/')for row in imports_in_core)
 nested.append({'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'importModules':sorted({row['module']for row in imports_in_core})})
clock=[(i,value)for i,value in enumerate(types['interfaces'])if value['name']=='monotonic-clock'];assert len(clock)==1
clock_id,clock_type=clock[0];assert clock_type['functions']=={}and list(clock_type['types'])==['duration']
duration=types['types'][clock_type['types']['duration']]
assert duration=={'name':'duration','kind':{'type':'u64'},'owner':{'interface':clock_id}}
assert types['packages'][clock_type['package']]['name']=='wasi:clocks@0.2.10'
assert types['worlds'][0]['imports']['interface-3']=={'interface':{'id':clock_id}}
assert types['worlds'][0]['exports']=={'interface-6':{'interface':{'id':6}}}
expanded_wit=Path('/tmp/starling-node-compat/corrected-http-package-root-static-v1/emitted.wit').read_text()
assert sorted(re.findall(r'^\s*import\s+([^;\s]+);',expanded_wit,re.M))==IMPORTS
assert re.findall(r'^\s*export\s+([^;\s]+);',expanded_wit,re.M)==exports

indexed(SOURCE,'bb37128336a8b3044e4c632f77827c3e9e1f93dc56ec52f2099399791d3f985a',29)
checked(SOURCE/'input-freeze.json','55822794123728a11f6044ea0b15aec2ba70e674df8c0ce185283793b19e9da2')
manifest=load(SOURCE/'input-freeze.json');assert len(manifest['inputs'])==7496
for row in manifest['inputs']:checked((SOURCE/row['path']).resolve(),row['sha256'],row['bytes'])
template=(SOURCE/'capability/preflight.template.mjs').read_text()
assert template.replace('@INPUTS_SHA@',root['files'][18]['sha256'])==(SOURCE/'capability/preflight.mjs').read_text()
binding=load(SOURCE/'source-binding.json');runtime=Path(binding['runtimeRoot'])
indexed(runtime,'e1f87cd6a2fd09ff34055187bfb938c2b094c3fd333ef9f57b6a1eea4c175b78')
runtime_manifest=load(runtime/'input-freeze.json');assert len(runtime_manifest['toolTrees'])==2 and len(runtime_manifest['toolLinks'])==22
for row in runtime_manifest['toolLinks']:
 path=Path(row['path']);assert path.is_symlink()and os.readlink(path)==row['linkText']and str(path.resolve())==row['resolvedTarget']
 if row['targetKind']=='file':checked(path.resolve(),row['targetSha256'],row['targetBytes'])
runtime_pins=load(SOURCE/'runtime-pins.json');assert runtime_pins['state']=='REVIEWED_REAL_CLASSIC_TRACE_PRODUCTION_FREEZES_V1'
assert load(SOURCE/'capability/component-pins.json')['component']is None
pin=runtime_pins['variants']['normal-runtime'];assert pin['engineSha256']==audit['engineSha256']=='a2fbdfcd9ec928cdec9d35e548b90ca2617ff52ae819c68bd08ad0a8c3ceffa7'
checked(audit['engine'],pin['engineSha256'],pin['engineBytes']);checked(audit['engineMetadataPath'],pin['receiptSha256'])
metadata=load(audit['engineMetadataPath']);assert len(metadata['sourceManifest'])==342 and len(metadata['componentizeSourceManifest'])==3
assert metadata['classicStreamsEnabled']is True and metadata['internalTicksEnabled']is True and metadata['entropyPolicy']=='runtime-only'and metadata['gcStress']is False
assert metadata['diagnosticOnly']is False if 'diagnosticOnly'in metadata else True
assert 'zlibPolicy'not in metadata
freeze_path=NATIVE/'normal-runtime-freeze-receipt.json';checked(freeze_path,pin['freezeReceiptSha256']);freeze=load(freeze_path);assert len(freeze['copies'])==474
for row in freeze['copies']:checked(row['path'],row['sha256'],row['bytes'])
commands=load(NATIVE/'normal-runtime-compile_commands.json')
native=[row for row in commands if row['file'].endswith('.cpp')and row['file'].startswith(('/private/tmp/starling-node-compat/classic-trace-source-v1/builtins/','/private/tmp/starling-node-compat/classic-trace-source-v1/runtime/'))]
assert len(native)==61 and len(metadata['actualEmbeddingCompileCommands'])==1
for row in native:
 words=shlex.split(row['command']);assert all(flag in words for flag in['-O3','-DNDEBUG','-flto=thin','-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY=1'])
 assert not any(word.startswith(('-DNODE_COMPAT_GC_STRESS','-DDEBUG','-DNODE_COMPAT_ZLIB'))for word in words)
embedding=shlex.split(metadata['actualEmbeddingCompileCommands'][0]);assert '-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY=1'in embedding and '-flto=thin'not in embedding
assert complete['sourceInputsRecheckedAfterRun']is True and complete['runtimeAcceptanceClaim']is False
assert complete['inputClosure']==audit['currentProductionAdmission']['inputClosure']and complete['inputClosure']['files']==7496
assert audit['computedLiveInputChecks']['beforeCopy']==audit['computedLiveInputChecks']['afterCopy']
live=audit['computedLiveInputChecks']['beforeCopy'];assert live['files']==8 and live['witFiles']==7 and live['adapterFiles']==1
for row in live['inputs']:
 checked(Path('/private/tmp/starling-node-compat/classic-trace-source-v1')/row['name'],row['sha256'],row['bytes'])
 if row['name'].endswith('package.wit'):checked(OUTPUT/'wit/deps'/Path(row['name']).parent.name/'package.wit',row['sha256'],row['bytes'])
assert audit['preview1Adapter']['usedInFinalWrapping']is False and packaging['finalWrapping']['adapters']==[]
assert packaging['finalWrapping']['coreSha256']==checked(core)
provenance=audit['componentizerProvenance'];assert provenance['selection']=='patched-import-i32-clock-v2'and provenance['legacyEngineDiagnosticEnabled']is False and provenance['debugScalarOOMDiagnostic']is None
checked(provenance['manifestPath'],provenance['manifestSha256']);package=Path(provenance['modulePath']).parent.parent
for row in provenance['checkedFiles']:checked(package/row['path'],row['sha256'])
for row in provenance['checkedFiles']:assert row in packaging['checkedFiles']
for entry in[provenance['patch'],*provenance['additionalPatches'],provenance['lock']]:checked(entry['path'],entry['sha256'])
for tool,pin_sha in[('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node','e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'),('/tmp/starling-node-compat/native-build/cache/wasm-tools/1448/wasm-tools','b332dd79057dafdcc8a36ca933d0d499acea506b56b1ea28e28fbb036c9e713d')]:checked(tool,pin_sha)
terminal=load(Path('/tmp/starling-node-compat/classic-corrected-http-build-v2.terminal.json'));assert terminal['returncode']==0
assert Path('/tmp/starling-node-compat/classic-corrected-http-build-v2.stderr.log').stat().st_size==0
assert Path('/tmp/starling-node-compat/classic-corrected-http-build-v2.stdout.log').read_bytes()==(OUTPUT/'component-audit.json').read_bytes()
peer=FAMILY/'independent-workload-v2-results-review-v1';indexed(peer,'0f59a0dafdf9d0b426f90459ac0ac7ce4a9149b1aeeb568d314a7781dbc447e8',19)
workload_review=load(peer/'results.json');assert workload_review['individualReturnedObservations']==105 and workload_review['fullNodeWorkloadCases']==20 and workload_review['fullNodeBoundaryCases']==14
failed=load(ADOPT/'corrected-http-packaging-attempt1-root-env-failure.json')
assert failed['componentProduced']is False and failed['rawOuterTerminalStatus'].startswith('unavailable:')
for row in failed['files']:checked(row['path'],row['sha256'],row['bytes'])
for row in list(seen.values()):checked(row['path'],row['sha256'],row['bytes'])
report={'schemaVersion':1,'state':'INDEPENDENT_CORRECTED_HTTP_PACKAGING_PREHOST_STATIC_REVIEW_PASSED','rootReceiptSha256':checked(root_path),'rootReportedBuildSession':71459,'rootReportedBuildExitCode':0,'rootRawExitObservedByReader':False,'componentSha256':checked(component),'componentBytes':component.stat().st_size,'applicationBundleSha256':checked(OUTPUT/'http.bundle.mjs'),'sourceEntryPath':audit['httpEntry'],'publicComponentImportsDecoded':sorted(imports),'publicComponentExportsDecoded':exports,'rawCoreImportEntriesDecoded':len(actual_core_imports),'rawCoreImportModules':actual_modules,'noPreview1OrCallableClock':True,'typeOnlyClock':{'interface':'wasi:clocks/monotonic-clock@0.2.10','functions':{},'duration':'u64'},'embeddedCores':nested,'mainEmbeddedAndRawCoreStandardSectionsByteEquivalent':True,'applicationImports':audit['bundleImports'],'bundledModules':53,'sourceIndexSha256':checked(SOURCE/'index.json'),'sourceFiles':29,'inputClosureRowsRehashed':7496,'runtimeIndexSha256':checked(runtime/'index.json'),'nativeFrozenCopiesRehashed':474,'nativeSourceInputs':342,'nativeCommands':61,'separateEmbeddingCommands':1,'runtimeOnlyFlagsVerified':True,'toolLinksRechecked':22,'liveInputsRechecked':8,'nativeAndSourcePostBuildAdmissionComplete':True,'packagerSelection':provenance['selection'],'sameOriginalSourceEntryAndBuildPath':True,'localComponentPinStillNull':True,'prerequisiteWorkloadReview':{'indexSha256':checked(peer/'index.json'),'returnedRecords':105,'cases':20,'boundaries':14,'scope':'Prior separate diagnostic finite correctness proof; not this HTTP component runtime proof.'},'earlierEnvironmentFailurePreserved':True,'earlierOuterExitUnknownNotInvented':True,'hostRequestsExecutedByReader':False,'ownerImportsOrHelpersOrPreflightOrBundlesOrGuestOrNativeOrStaticToolReruns':False,'hostAcceptancePassed':False,'runtimeAcceptanceClaim':False,'performanceClaim':False,'scope':'Static packaging prerequisites clear for a separate Root-issued phase and future ordinary host validation. This is not pin promotion or target-host success.','limitations':['Baseline schema5/protected29 and ordinaryclassic19 source assertions are sealed; actual responses remain unobserved here.','Keep known then-getter/Symbol differences, combined GC ownership bounds, no request reuse/isolation inference from counters.','No complete Node/Streams, capability-function clock, timing or memory claim.'],'verifiedFiles':sorted(seen.values(),key=lambda row:row['path'])}
with(HERE/'results.json').open('x')as stream:json.dump(report,stream,indent=2);stream.write('\n')
print(json.dumps({'state':report['state'],'verifiedPaths':len(seen),'sourceRows':7496,'imports':imports,'hostExecuted':False}))
