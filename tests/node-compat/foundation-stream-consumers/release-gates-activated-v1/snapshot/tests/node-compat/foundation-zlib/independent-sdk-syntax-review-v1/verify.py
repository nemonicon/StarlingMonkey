#!/usr/bin/env python3
"""Read-only syntax-evidence reader; no compiler, helper, or owner imports."""
from pathlib import Path
import collections
import hashlib
import json
import os
import re
import shlex
import stat

HERE=Path(__file__).resolve().parent
FAMILY=HERE.parent
PACKET=FAMILY/'sdk-syntax-v1'
PROPOSAL=FAMILY/'integration-candidate-v1'
FREEZE=Path('/tmp/starling-node-compat/production-classic-trace-v1/native-freeze')
STAGE=Path('/tmp/starling-node-compat/zlib-sdk-syntax-v1')
REPO=FAMILY.parents[2]
seen={}
def checked(path,expected=None,size=None):
 path=Path(path);before=path.lstat();assert stat.S_ISREG(before.st_mode),str(path)
 digest=hashlib.sha256()
 with path.open('rb')as stream:
  for chunk in iter(lambda:stream.read(1024*1024),b''):digest.update(chunk)
 after=path.lstat();assert(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),str(path)
 value=digest.hexdigest()
 if expected is not None:assert value==expected,str(path)
 if size is not None:assert before.st_size==size,str(path)
 seen[str(path)]={'path':str(path),'sha256':value,'bytes':before.st_size};return value
def load(path):checked(path);return json.loads(Path(path).read_bytes())
def indexed(root,pin,count):
 checked(root/'index.json',pin);value=load(root/'index.json');assert len(value['files'])==count
 for row in value['files']:checked(root/row['path'],row['sha256'],row['bytes'])
 return value
indexed(PACKET,'e7579d660126ab6688519f883ea76a3ac123b3e1f10368c7f1dd2b409f3b5682',12)
indexed(PROPOSAL,'56a6ee5fecc921ce78e4c4402761c9fc790487eb6f2deeb6297c12cf3597fd2d',38)
root=load(PACKET/'root-results.json');assert root['toolSession']==61573 and root['rawTerminalExitCode']==0
assert root['engineBuilt']is False and root['codecsLinked']is False and root['guestExecuted']is False
assert root['sourceFilesStaged']==350 and root['gcMacroConfigured']is False
policy=load(PROPOSAL/'source-policy.proposal.json');rows=policy['proposedNativeSourceManifest'];assert len(rows)==350
parent=load(FREEZE/'normal-off.engine.wasm.build.json');parent_rows={r['path']:r['sha256']for r in parent['sourceManifest']};assert len(parent_rows)==342
added=set(policy['addedSourcePaths']);assert len(added)==8
changed={r['path']:r for r in policy['changedParentSources']};assert len(changed)==2
for row in rows:
 relative=row['path'];checked(STAGE/'source'/relative,row['sha256'])
 if relative in added or relative in changed:checked(PROPOSAL/'source'/relative,row['sha256'])
 else:assert parent_rows[relative]==row['sha256'];checked(FREEZE/'source'/relative,row['sha256'])
for relative,row in changed.items():
 assert parent_rows[relative]==row['beforeSha256'];checked(FREEZE/'source'/relative,row['beforeSha256'])
assert {str(p.relative_to(STAGE/'source'))for p in(STAGE/'source').rglob('*')if p.is_file()}=={r['path']for r in rows}
database_path=FREEZE/'normal-off-compile_commands.json'
checked(database_path,'05d3667f92647d7042160988d3cc20bf27a2bd04e478a7992e3c37baedf1e57f')
assert parent['compileCommandsSha256']==root['parentCompileCommandsSha256']==checked(database_path)
database=load(database_path);result=load(PACKET/'results.json');assert len(result['commands'])==2
proto_source='/private/tmp/starling-node-compat/classic-trace-source-v1'
dep_union=set();commands=[];include_trace_lines=0
for label,relative,prototype in [('kernel','builtins/node-compat/zlib/kernel.cpp','builtins/node-compat/buffer.cpp'),('register','builtins/node-compat/register.cpp','builtins/node-compat/register.cpp')]:
 command=load(PACKET/(label+'-command.json'));record=next(r for r in result['commands']if r['label']==label)
 assert record==dict(command,rawExitCode=0)
 proto=[r for r in database if r['file']==command['prototypeFile']];assert len(proto)==1 and proto[0]['file']==proto_source+'/'+prototype
 tokens=shlex.split(proto[0]['command']);expected=[];i=0
 while i<len(tokens):
  if tokens[i]in['-c','-o']:i+=2
  else:expected.append(tokens[i].replace(proto_source,str(STAGE/'source')));i+=1
 expected+=['-DNODE_COMPAT_ZLIB=1','-fsyntax-only','-MD','-MF',str(STAGE/(label+'.d')),'-H',str(STAGE/'source'/relative)]
 assert command['command']==expected and command['cwd']==str(STAGE)
 assert '-c'not in expected and '-o'not in expected
 assert expected.count('-DNODE_COMPAT_ZLIB=1')==1
 assert all(not token.startswith(('-DNODE_COMPAT_GC_STRESS','-DDEBUG','-DOOM'))for token in expected)
 assert all(token in expected for token in ['--target=wasm32-wasi','-O3','-DNDEBUG','-flto=thin'])
 assert (PACKET/(label+'.stdout.log')).stat().st_size==0
 stderr=(PACKET/(label+'.stderr.log')).read_text().splitlines()
 assert stderr and all(re.fullmatch(r'\.+ .+',line)for line in stderr)
 include_trace_lines+=len(stderr)
 dependency=(PACKET/(label+'.d')).read_text().replace('\\\n','')
 target,body=dependency.split(':',1);assert target==label+'.o'
 paths=shlex.split(body);assert paths[0]==str(STAGE/'source'/relative)
 dep_union.update(paths)
 assert not(STAGE/(label+'.o')).exists() and not(STAGE/(label+'.obj')).exists()
 canonical_dependencies={str(Path(x).resolve())for x in paths}
 for line in stderr:assert str(Path(re.sub(r'^\.+ ','',line)).resolve())in canonical_dependencies
 for name in [label+'-command.json',label+'.stdout.log',label+'.stderr.log',label+'.d']:
  assert checked(STAGE/name)==checked(PACKET/name)
 commands.append(command)
dependencies=load(PACKET/'header-dependencies.json')['files'];assert len(dependencies)==1048
assert dep_union=={r['path']for r in dependencies}
extensions=collections.Counter(Path(r['path']).suffix for r in dependencies)
assert extensions=={'.h':982,'':64,'.cpp':2}
for row in dependencies:
 assert str(Path(row['path']).resolve())==row['resolvedPath']
 checked(row['resolvedPath'],row['sha256'],row['bytes'])
assert not[p for p in STAGE.iterdir()if p.is_file()and p.suffix in['.o','.obj','.a','.wasm']]

wrapper=Path(commands[0]['command'][0]);assert commands[1]['command'][0]==str(wrapper)
checked(wrapper)
wrapper_text=wrapper.read_text();tool=root['tool'];compiler=Path(tool['compilerPath'])
assert compiler.is_symlink() and os.readlink(compiler)==tool['compilerLinkText']=='clang'
assert str(compiler.resolve())==tool['compilerRealPath']
checked(compiler.resolve(),tool['compilerSha256'],tool['compilerBytes'])
assert 'PATH="'+proto_source+'/scripts:$PATH" '+str(compiler)+' "$@"' in wrapper_text
assert wrapper_text.count(str(compiler))==1
version_path=compiler.parent.parent/'VERSION';checked(version_path)
version=version_path.read_text();assert version.startswith('30.0\n')and'llvm-version: 21.1.4'in version
sm=Path('/tmp/starling-node-compat/classic-trace-v1-build/spidermonkey-dist-release')
header_pins={'zlib.h':'8a5579af72ea4f427ff00a4150f0ccb3fc5c1e4379f726e101133b1ab9fc600c','zconf.h':'61c756bba04523c333be09e33830ab617b11401d23583569bb94af2057418e14','mozzconf.h':'c16f8894b2d303dd5bae94c4ed9f76ecd4c942ab7346d5c66c1cc7074d3351d9','js-confdefs.h':'841e57a382d7d8219431dc26e1d1307af1649228503d21bcf2eac826fc99acd6'}
for name,pin in header_pins.items():checked(sm/'include'/name,pin)
assert '#  include "zconf.h"'in(sm/'include/zlib.h').read_text()or'#include "zconf.h"'in(sm/'include/zlib.h').read_text()
assert 'mozzconf.h'in(sm/'include/zconf.h').read_text()
archive=sm/'libspidermonkey.a';checked(archive,'298b85501657189dc66139242abf5aeb4e981b8db7c37cc5a69d1151ec40aacc',538170426)
nm=Path('/tmp/starling-node-compat/zlib-static-archive-audit-v1/nm.stdout.txt');checked(nm,'e7fbe2cea745ef1183e650c4eeef2847dc2e5361445a99600004f4c3f4983970')
symbols=['zlibVersion','deflateInit2_','deflate','deflateEnd','inflateInit2_','inflate','inflateEnd'];raw=nm.read_text()
counts={name:len(re.findall(r': MOZ_Z_'+re.escape(name)+r' T ',raw))for name in symbols};assert all(value==1 for value in counts.values())
assert not re.search(r': (?:z_)?(?:'+'|'.join(map(re.escape,symbols))+r') T ',raw)
prior=load(FAMILY/'independent-integration-source-review-v1/results.json')
live=[]
for row in prior['verifiedFiles']:
 if row['path'].startswith(str(REPO)+'/')and'/tests/'not in row['path']:
  checked(row['path'],row['sha256'],row['bytes']);live.append(row['path'])
for row in list(seen.values()):checked(row['path'],row['sha256'],row['bytes'])
report={'schemaVersion':1,'state':'INDEPENDENT_ZLIB_RELEASE_SDK_SYNTAX_EVIDENCE_VERIFIED_NO_COMPILER_RERUN','syntaxIndexSha256':checked(PACKET/'index.json'),'sourceIndexSha256':checked(PROPOSAL/'index.json'),'rawTerminalExitCodeRecorded':0,'translationUnits':[r['label']for r in commands],'commandsReconstructedExactlyFromFrozenCompileDatabase':True,'prototypeCompileDatabaseSha256':checked(database_path),'stageSourcesVerified':350,'parentSources':342,'addedPaths':8,'changedPaths':2,'dependencyRecords':1048,'translationUnitInputRecords':2,'otherHeaderDependencyRecords':1046,'dependencyExtensions':dict(extensions),'includeTraceLines':include_trace_lines,'allDependencyFilesRehashed':True,'actualSdkVersion':version,'compilerRealPath':tool['compilerRealPath'],'compilerSha256':tool['compilerSha256'],'wrapperForwardingChecked':True,'headers':header_pins,'selectedArchiveSha256':checked(archive),'staticMozDefinitions':counts,'newObjectOutputsObserved':False,'dependencyTargetNamesAreNotObjectOutputs':True,'inputBinarySourceAssetsExcludedFromOutputClaim':True,'liveSourceWitnessesRehashed':len(live),'compilerOrHelperOrGuestOrLinkRerun':False,'linkedNewBackend':False,'actualGuestVersionVerified':False,'gcOrRuntimeOrCostProof':False,'productionAdmissionOpen':False,'runtimeAcceptanceClaim':False,'limitations':['Root-recorded syntax exits and dependency output are authenticated; reviewer did not rerun compilation.','Static existing archive symbol definitions are not new-module linkage or runtime backend agreement.','No engine, guest, forced-GC, allocator-failure, or performance proof.'],'verifiedFiles':sorted(seen.values(),key=lambda row:row['path'])}
with(HERE/'results.json').open('x')as stream:json.dump(report,stream,indent=2);stream.write('\n')
print(json.dumps({'state':report['state'],'verifiedPaths':len(seen),'stageSources':350,'compilerDependencyFiles':1048,'cppInputs':2,'headers':1046,'compilerRerun':False}))
