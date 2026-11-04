#!/usr/bin/env python3
"""Independent read-only blocker proof; never imports owner validators."""
from pathlib import Path
import hashlib
import json
import shlex
import stat

HERE=Path(__file__).resolve().parent
FAMILY=HERE.parent
REPO=FAMILY.parents[2]
OWNER=FAMILY/'native-integration-candidate-v1'
CONDITIONAL=FAMILY/'integration-candidate-v1'
FREEZE=Path('/tmp/starling-node-compat/production-classic-trace-v1/native-freeze')
SDK=FAMILY/'sdk-syntax-v1'
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
def indexed(root,pin,count):
 checked(root/'index.json',pin);value=load(root/'index.json');assert len(value['files'])==count
 for row in value['files']:checked(root/row['path'],row['sha256'],row['bytes'])
 return value
indexed(OWNER,'3ff3a59d4fc1fafa32b2ba1e6ec5a1b8d7787f4e7eca1ee6855d7b38cc7c45db',72)
indexed(CONDITIONAL,'56a6ee5fecc921ce78e4c4402761c9fc790487eb6f2deeb6297c12cf3597fd2d',38)
indexed(SDK,'e7579d660126ab6688519f883ea76a3ac123b3e1f10368c7f1dd2b409f3b5682',12)
manifest=load(OWNER/'input-freeze.json');assert len(manifest['inputs'])==1940
for row in manifest['inputs']:
 path=Path(row['path']);path=path if path.is_absolute()else OWNER/path
 checked(path,row['sha256'],row['bytes'])
policy=load(OWNER/'policy.json');conditional=load(CONDITIONAL/'source-policy.proposal.json')
assert policy['expectedNativeSourceManifest']==conditional['proposedNativeSourceManifest']
assert len(policy['expectedNativeSourceManifest'])==350
for path in (OWNER/'source/builtins').rglob('*'):
 if path.is_file():assert path.read_bytes()==(CONDITIONAL/'source'/path.relative_to(OWNER/'source')).read_bytes()
assert(OWNER/'source/cmake/builtins.cmake').read_bytes()==(CONDITIONAL/'source/cmake/builtins.cmake').read_bytes()
checked(OWNER/'source/tests/node-compat/build-engine.sh','89c3580c967bf0290f500fc20dfbeadc363cabb5494ffeed1ff44b958cc0a814')
database_path=FREEZE/'normal-off-compile_commands.json'
checked(database_path,'05d3667f92647d7042160988d3cc20bf27a2bd04e478a7992e3c37baedf1e57f')
database=load(database_path);metadata=load(FREEZE/'normal-off.engine.wasm.build.json')
root='/private/tmp/starling-node-compat/classic-trace-source-v1/'
native=[row for row in database if row['file'].endswith('.cpp')and row['file'].startswith((root+'builtins/',root+'runtime/'))]
assert len(native)==61 and len(metadata['actualEmbeddingCompileCommands'])==1
expected_header='/tmp/starling-node-compat/classic-trace-v1-build/spidermonkey-dist-release/include/js-confdefs.h'
checked(expected_header,'841e57a382d7d8219431dc26e1d1307af1649228503d21bcf2eac826fc99acd6',2283)
observations=[]
def observation(kind,source,command,tokens=None):
 words=shlex.split(command)if tokens is None else tokens
 includes=[words[i+1]for i,word in enumerate(words[:-1])if word=='-include']
 assert includes==[expected_header]
 assert '-O3'in words and '-DNDEBUG'in words
 # These are the exact independently read predicates, evaluated as data here;
 # no owner module, source guard or compiler is imported/called.
 python_rejects=any(word.startswith(('-DZ_PREFIX','-UZ_PREFIX','-include','-imacros','-Wl,-lz'))or word in['-lz','-lzlib']for word in words)
 javascript_rejects=any(any(word.startswith(prefix)for prefix in['-DZ_PREFIX','-UZ_PREFIX','-include','-imacros','-Wl,-lz'])or word in['-lz','-lzlib']for word in words)
 codec_rejects=any(word in['-D','-U','-include','-imacros']or word.startswith(('-include','-imacros'))for word in words)
 assert python_rejects and javascript_rejects and codec_rejects
 observations.append({'kind':kind,'source':source,'commandSha256':hashlib.sha256(command.encode()).hexdigest(),'forcedInclude':includes,'headerSha256':'841e57a382d7d8219431dc26e1d1307af1649228503d21bcf2eac826fc99acd6','newPythonAndJsPredicateRejects':True,'codecNoSecondCodecPredicateRejects':True})
for row in native:observation('actual-frozen-native-compile-command',row['file'],row['command'])
observation('actual-frozen-external-embedding-command','embedding/embedding.cpp',metadata['actualEmbeddingCompileCommands'][0])
sdk_results=load(SDK/'results.json')
for row in sdk_results['commands']:
 assert row['rawExitCode']==0
 observation('actual-recorded-zlib-sdk-syntax-command',row['label'],shlex.join(row['command']),row['command'])
assert len(observations)==64
layer=(OWNER/'layer-policy.py').read_text();codec=(OWNER/'codec-evidence.py').read_text();js=(OWNER/'source/tests/node-compat/zlib-admission.mjs').read_text()
assert layer.count("assert not any(word.startswith(('-DZ_PREFIX','-UZ_PREFIX','-include','-imacros','-Wl,-lz'))") == 2
assert "assert word not in ['-D','-U','-include','-imacros']"in codec
assert "assert not word.startswith(('-include','-imacros'))"in codec
assert "['-DZ_PREFIX','-UZ_PREFIX','-include','-imacros','-Wl,-lz'].some(prefix=>word.startsWith(prefix))"in js
recipe=(OWNER/'source/tests/node-compat/build-engine.sh').read_text()
assert recipe.index('metadata = layer.decorate(')<recipe.index("metadata['zlibPolicy']['codecWitness']=codec.after(")
link_path=Path('/tmp/starling-node-compat/classic-benchmark-trace-v3-artifacts/native-freeze/benchmark-classic-on-final-link.commands.txt')
checked(link_path);link_commands=[line for line in link_path.read_text().splitlines()if'libspidermonkey.a'in line and' -c 'not in line]
assert len(link_commands)==1 and '-include'not in shlex.split(link_commands[0])
runtime=load(OWNER/'runtime-pins.json');bootstrap=load(OWNER/'bootstrap-pins.json')
for pins in[runtime,bootstrap]:assert set(pins['variants'])=={'normal-off','normal-runtime','gc-off','disabled-off'}and all(value is None for value in pins['variants'].values())
for row in list(seen.values()):checked(row['path'],row['sha256'],row['bytes'])
with(HERE/'actual-command-data.json').open('x')as stream:json.dump({'schemaVersion':1,'observations':observations,'ownerValidatorsOrCompilerInvoked':False},stream,indent=2);stream.write('\n')
report={'schemaVersion':1,'state':'INDEPENDENT_ZLIB350_SOURCE_REVIEW_HOLD_REQUIRED_SM_FORCE_INCLUDE_REJECTED','ownerIndexSha256':checked(OWNER/'index.json'),'ownerFilesRehashed':72,'preparationInputsRehashed':1940,'recipeSha256':checked(OWNER/'source/tests/node-compat/build-engine.sh'),'conditionalNativePayload350AndManifestUnchanged':True,'mandatoryFindings':[{'id':'Z350-M1','severity':'must-fix-before-stage-or-build','issue':'All three new command-guard implementations reject the pinned required SpiderMonkey js-confdefs.h forced include.','affectedLocations':[{'path':'layer-policy.py','lines':[98,113]},{'path':'codec-evidence.py','lines':[68,69]},{'path':'source/tests/node-compat/zlib-admission.mjs','lines':[166]}],'actualFrozenNativeCommandsRejected':61,'actualFrozenEmbeddingCommandsRejected':1,'actualRecordedSdkSyntaxCommandsRejected':2,'headerSha256':'841e57a382d7d8219431dc26e1d1307af1649228503d21bcf2eac826fc99acd6','logicEvaluation':'Independent pure predicate evaluation on actual command data; owner guards were not imported/called.','requiredCorrection':'New immutable coherent successor must allow exactly one separately authenticated selected-SMdist/include/js-confdefs.h operand in compile and embedding contexts, reject additional/unknown/joined/PCH/imacros/prefix forms, retain distinct actual link grammar, and add genuine frozen61+embedding and recordedSDK command regressions.','producerOrdering':'layer.decorate runs before codec.after assigns codecWitness; required header path/hash authority must be explicitly available before that producer check.','metadataProjectionPermitted':False}],'existingActualDiagnosticFinalLinkHasForcedInclude':False,'allOtherSourceMechanismsApproved':False,'reviewScope':'Critical source/data blocker and complete indexed/input-byte authentication. Remaining integration source approval is held pending coherent successor; no claim that this is the only possible future empirical issue.','futurePinsAllNull':True,'sourceOrNativeOrSealedPacketsModified':False,'ownerHelpersOrActionsOrCompilersOrGuestOrTimingExecuted':False,'runtimeAcceptanceClaim':False,'productionAdmissionOpen':False,'performanceClaim':False,'verifiedFiles':sorted(seen.values(),key=lambda row:row['path'])}
with(HERE/'results.json').open('x')as stream:json.dump(report,stream,indent=2);stream.write('\n')
print(json.dumps({'state':report['state'],'verifiedPaths':len(seen),'actualCommands':64,'mandatoryFindings':1,'actionsExecuted':False}))
