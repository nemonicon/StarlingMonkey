"""Supplemental static actual process/tool/header/link checks; no tool invocation."""
from pathlib import Path
import hashlib,json,os,re,shlex,tarfile
P=Path(__file__).resolve().parent;d=json.loads((P/'audit-data.json').read_bytes());seen={};checks=[]
def need(v,n):assert v,n;checks.append(n)
def read(p,h=None,size=None):
 p=Path(p);b=p.read_bytes();need(h is None or hashlib.sha256(b).hexdigest()==h,'exact witness hash');need(size is None or len(b)==size,'exact witness bytes');seen[str(p)]=dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b));return b
def data(r):return json.loads(read(r['path'],r['sha256'],r['bytes']))
m=data(d['metadata']);root=data(d['rootBuildObservation']);authority=data(d['rootBuildAuthority']);config=data(d['rootBuildConfig']);built=data(d['actualBuildResult']);source=Path(d['configuredSourceRoot']);work=Path(d['workRoot']);build=Path(m['cmakeCachePath']).parent
need(root['engine']==d['engine']and root['metadata']==d['metadata']and root['actualBuildResult']==d['actualBuildResult'],'Root direct actual output bindings')
counts={}
for desc,mode in[(d['externalParentTerminal'],'parent'),(d['controllerWorkerTerminal'],'worker')]:
 term=data(desc);base=Path(desc['path']).parent;started=json.loads(read(base/'started.json'));need(started['argv'][1:]==['-B','-I',authority['externalControllerEntry']['path'],mode,json.dumps(d['rootBuildConfig'],separators=(',',':'))],'real explicit mode/config invocation')
 need(started['pid']==term['pid']and started['timeoutSeconds']==7200 and started['authority']==d['rootBuildAuthority'],'real started/terminal authority and deadline')
 need(Path(started['argv'][0]).resolve()==Path('/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9').resolve(),'actual original Python context')
 counts[mode]=len(term['observedProcesses'])
output=Path(d['actualBuildResult']['path']).parent;need({p.name for p in output.iterdir()}=={'launch.json','build.log','result.json'},'genuine lifecycle output exact three files')
launch=json.loads(read(output/'launch.json'))
for key in launch:need(launch[key]==(None if key=='rawChildExitCode'else built[key]),'actual launch field preserved '+key)
w=m['zlibPolicy']['codecWitness'];selected=m['zlibSelectedCodecInput'];headers={'zlib.h':('8a5579af72ea4f427ff00a4150f0ccb3fc5c1e4379f726e101133b1ab9fc600c',96829),'zconf.h':('61c756bba04523c333be09e33830ab617b11401d23583569bb94af2057418e14',16600),'mozzconf.h':('c16f8894b2d303dd5bae94c4ed9f76ecd4c942ab7346d5c66c1cc7074d3351d9',5855),'js-confdefs.h':('841e57a382d7d8219431dc26e1d1307af1649228503d21bcf2eac826fc99acd6',2283)}
need({Path(r['path']).name:(r['sha256'],r['bytes'])for r in selected['headers']}==headers,'all four actual selected headers agree known SM contract')
for r in selected['headers']:read(r['path'],r['sha256'],r['bytes'])
db=json.loads(read(m['compileCommandsPath'],m['compileCommandsSha256']));native={r['path']:r['sha256']for r in m['sourceManifest']};classified=[];object_rows=[]
for r in db:
 words=shlex.split(r['command']);need(not any(v.startswith('@')or v in['&&',';','|']or '$('in v for v in words),'no unobserved compile response/shell stage')
 need(not any(v=='-DNODE_COMPAT_GC_STRESS'or v.startswith('-DNODE_COMPAT_GC_STRESS=')or v.startswith('-DNODE_COMPAT_OOM_TESTING')for v in words),'actual ordinary normal flags across all68 DB rows')
 p=Path(r['file']);name=p.relative_to(source).as_posix()if p.is_relative_to(source)else None
 if name:need(name in native,'every five extra configured source is still in full355 manifest');read(p,native[name]);kind='policy-builtins/runtime'if name.startswith(('builtins/','runtime/'))else'other-configured-source'
 else:need(p==build/'starling-raw.wasm/null.cpp','only generated null is outside actual configured source');read(p);kind='generated-null'
 classified.append(dict(file=r['file'],kind=kind));need(words.count('-o')==1,'one actual object output');obj=Path(words[words.index('-o')+1]);obj=obj if obj.is_absolute()else Path(r['directory'])/obj;raw=read(obj);need(raw[:8]==b'\x00asm\x01\x00\x00\x00'or raw[:4]in[b'BC\xc0\xde',b'\xde\xc0\x17\x0b'],'actual core-Wasm/LLVM object magic');object_rows.append(seen[str(obj)])
need({k:sum(r['kind']==k for r in classified)for k in['policy-builtins/runtime','other-configured-source','generated-null']}=={'policy-builtins/runtime':62,'other-configured-source':5,'generated-null':1},'actual68 DB exact62+5+1 split and no embedding DB row')
kernel=next(r['command']for r in db if r['file']==str(source/'builtins/node-compat/zlib/kernel.cpp'));words=shlex.split(kernel);includes=[];i=0
while i<len(words):
 v=words[i]
 if v in['-I','-isystem']:i+=1;includes.append(words[i])
 elif v.startswith('-I')and len(v)>2:includes.append(v[2:])
 elif v.startswith('-isystem')and len(v)>8:includes.append(v[8:])
 i+=1
need(w['actualHeaderSearchDirectories']==[includes],'actual kernel header-search witness')
candidates=[Path(p)/'zlib.h'for p in includes if(Path(p)/'zlib.h').is_file()];need(candidates[0]==Path(selected['selectedDistribution'])/'include/zlib.h','first actual codec header is selected SM header')
raw=read(w['postBuildLinkEvidence']['path'],w['postBuildLinkEvidence']['sha256']);line,=[v for v in raw.decode().splitlines()if'libspidermonkey.a'in v and' -c 'not in v];groups=[shlex.split(v)for v in line.split(' && ')];compiler,cd,optimizer=groups[1:];out=build/compiler[compiler.index('-o')+1]
expected=dict(rawCommand=line,expandedArguments=compiler,kind='compiler-cd-inplace-wasm-opt-v1',compilerArguments=compiler,compilerExpandedArguments=compiler,compilerOutputPath=str(out),postOptimizerArguments=optimizer,postOptimizerWorkingDirectory=cd[1],postOptimizerInputPath=str(out),postOptimizerOutputPath=str(out),sameWasmOutputProved=True)
need(w['postBuildLinkEvidence']['commands']==[expected]and w['postBuildLinkEvidence']['responseFiles']==[]and w['postBuildLinkEvidence']['beforeBuildCaptureExists']is False,'entire actual compound link witness reconstructed')
read(out,d['engine']['sha256'],d['engine']['bytes']);need(out.stat().st_ino!=Path(d['engine']['path']).stat().st_ino,'final link output/engine copy equal bytes and distinct inode')
need([v for v in compiler if v.startswith('-O')]==['-O3']and'-DNDEBUG'in compiler and[v for v in compiler if v.startswith('-flto')]==['-flto=thin'],'actual link ordinary thinLTO Release')
ba=next(r for r in m['downloadedArchives']if Path(r['path']).name=='binaryen-version_123-arm64-macos.tar.gz')
with tarfile.open(ba['path'])as tar:
 member=next(v for v in tar.getmembers()if v.name.endswith('/bin/wasm-opt'));blob=tar.extractfile(member).read();read(optimizer[0],hashlib.sha256(blob).hexdigest(),len(blob))
cache={}
for line in read(m['cmakeCachePath'],m['cmakeCacheSha256']).decode().splitlines():
 k,sep,v=line.partition(':')
 if sep and'='in v:cache[k]=v.partition('=')[2]
host_tools=[]
for key in['CMAKE_COMMAND','CMAKE_MAKE_PROGRAM']:
 p=Path(cache[key]);resolved=p.resolve();read(resolved);host_tools.append(dict(role=key,declaredPath=str(p),resolved=seen[str(resolved)],leafAlias=p.is_symlink(),linkText=os.readlink(p)if p.is_symlink()else None))
rust=m['generatedRustProject'];tokens=shlex.split(rust['actualCargoBuildCommands'][0])
for p in [Path(v)for v in tokens if v.endswith('/bin/cargo')]+[Path(v.split('=',1)[1])for v in tokens if v.startswith('CARGO_BUILD_RUSTC=')]:read(p.resolve());host_tools.append(dict(role='actual locked Rust command tool',declaredPath=str(p),resolved=seen[str(p.resolve())]))
read(source/'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm','988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0',53512)
for key in['configureRecipe','configdata']:r=m['openssl'][key];read(r['path'],r['sha256'],r.get('bytes'));need(seen[r['path']]['bytes']>0,'actual missing-metadata-size field concretely measured')
result=dict(schemaVersion=1,verifiedPassed=True,checks=len(checks),actualProcessRecords=counts,compileDatabaseClassification=classified,objectFiles=object_rows,allFourHeadersExact=True,firstSelectedHeaderActual=True,wholeCompoundLinkWitnessExact=True,finalPostOptimizerBytesEqualActualEngineCopy=True,binaryenToolMatchesArchive=True,hostToolReferences=host_tools,metadataOmittedSizesMeasured=True,standaloneCmakeOrCompilerTerminalObserved=False,ownerHelperCompilerNodeNinjaNmEngineGuestActionsInvoked=False,extraInputs=list(seen.values()))
with(P/'witness-review.json').open('x')as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(dict(witnessReviewPassed=True,checks=len(checks),processRecords=counts,extraInputs=len(seen),ownerActionsInvoked=False)))
