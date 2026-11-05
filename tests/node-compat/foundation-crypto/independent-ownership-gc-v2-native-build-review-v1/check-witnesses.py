"""Final static witness/process/Root binding checks. No owner helpers/tools."""
from pathlib import Path
import hashlib,json,re,shlex
P=Path(__file__).resolve().parent;spec=json.loads((P/'actual-evidence-inputs.json').read_bytes())
seen={}
def read(p,h=None,size=None):
 p=Path(p);b=p.read_bytes();assert h is None or hashlib.sha256(b).hexdigest()==h;assert size is None or len(b)==size;seen[str(p)]=dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b));return b
def data(r):return json.loads(read(r['path'],r['sha256'],r['bytes']))
m=data(spec['metadata']);root=data(spec['rootBuildObservation']);authority=data(spec['rootBuildAuthority']);config=data(spec['rootBuildConfig']);built=data(spec['actualBuildResult']);outer=data(spec['externalParentTerminal']);started=data(spec['externalParentStarted'])
assert spec['rootBuildObservation']['sha256']=='cdde20539a850a2679a91e7db2090d9dc0e1a881c8f17c19ff4664852123e931'and root['rootObservedToolRawExitCode']==0 and root['rootToolSessionId']==58915
for a,b in [('actualBuildResult','actualBuildResult'),('externalParentTerminal','externalParentTerminal'),('rootAuthority','rootBuildAuthority'),('config','rootBuildConfig'),('buildLog','buildLog'),('engine','engine'),('metadata','metadata')]:assert root[a]==spec[b]
assert authority['externalControllerIndex']==spec['controllerSourceIndex']and authority['externalControllerReview']==spec['controllerReview']and authority['independentSourceReview']==spec['sourceReview']and authority['independentStageReview']==spec['stageReview']
assert spec['rootBuildAuthority']['sha256']=='8c01977c8a653f2014c27911e32545d42cfdc5465d0ba25febb33b7ba656ae12'and spec['rootBuildConfig']['sha256']=='a9395c868071bf656de80d1a4a6f91825419fdcdc1a0fd60b68dd549fc70082c'
assert outer['pid']==root['pythonParentPid']==49070 and built['ownedGroupCleanup']['pgid']==root['innerBashPgid']==49081
assert started['pid']==outer['pid']and started['timeoutSeconds']==7200 and started['authority']==spec['rootBuildAuthority']and json.loads(started['argv'][2])==spec['rootBuildConfig']
assert started['argv'][1].endswith('/ownership-gc-native-candidate-v2/build.py')
external=Path(spec['externalParentTerminal']['path']).parent;observations=[];external_rows=[]
for p in sorted(external.iterdir()):
 assert p.is_file()and not p.is_symlink()and p.stat().st_nlink==1;read(p);external_rows.append(seen[str(p)])
 if p.name.startswith('owned-'):
  x=json.loads(p.read_bytes());assert x['sequence']==len(observations);observations.append(x)
assert [v['process']for v in observations]==outer['observedProcesses']
assert set(p.name for p in external.iterdir())=={'started.json','terminal.json','stdout.log','stderr.log'}|{f'owned-{i:04d}.json'for i in range(len(observations))}
assert {v['process']['pgid']for v in observations}<={v['pgid']for v in outer['finalGroups']}
assert outer['remainingObservedPids']==[]and all(v['alive']is False for v in outer['finalGroups'])and outer['signals']==outer['errors']==outer['interruptedSignals']==[]
w=m['zlibPolicy']['codecWitness'];selected=m['zlibSelectedCodecInput'];headers={'zlib.h':('8a5579af72ea4f427ff00a4150f0ccb3fc5c1e4379f726e101133b1ab9fc600c',96829),'zconf.h':('61c756bba04523c333be09e33830ab617b11401d23583569bb94af2057418e14',16600),'mozzconf.h':('c16f8894b2d303dd5bae94c4ed9f76ecd4c942ab7346d5c66c1cc7074d3351d9',5855),'js-confdefs.h':('841e57a382d7d8219431dc26e1d1307af1649228503d21bcf2eac826fc99acd6',2283)}
assert {Path(r['path']).name:(r['sha256'],r['bytes'])for r in selected['headers']}==headers
for r in selected['headers']:read(r['path'],r['sha256'],r['bytes'])
cache={}
for line in read(m['cmakeCachePath'],m['cmakeCacheSha256']).decode().splitlines():
 k,sep,tail=line.partition(':')
 if sep and '='in tail:cache[k]=tail.partition('=')[2]
build=Path(m['cmakeCachePath']).parent;work=Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-build');source=Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-source')
raw=read(w['postBuildLinkEvidence']['path'],w['postBuildLinkEvidence']['sha256']);lines=raw.decode().splitlines();line,=[v for v in lines if 'libspidermonkey.a'in v and ' -c 'not in v];groups=[shlex.split(v)for v in line.split(' && ')];compiler,cd,optimizer=groups[1:];out=build/compiler[compiler.index('-o')+1]
expected_link=dict(rawCommand=line,expandedArguments=compiler,kind='compiler-cd-inplace-wasm-opt-v1',compilerArguments=compiler,compilerExpandedArguments=compiler,compilerOutputPath=str(out),postOptimizerArguments=optimizer,postOptimizerWorkingDirectory=cd[1],postOptimizerInputPath=str(out),postOptimizerOutputPath=str(out),sameWasmOutputProved=True)
assert w['postBuildLinkEvidence']['commands']==[expected_link]and w['postBuildLinkEvidence']['responseFiles']==[]and w['postBuildLinkEvidence']['beforeBuildCaptureExists']is False
assert [v for v in compiler if v.startswith('-O')]==['-O3']and '-DNDEBUG'in compiler and [v for v in compiler if v.startswith('-flto')]==['-flto=thin']
assert not any('--threads'in v or '--thinlto-jobs'in v for v in compiler)
db=json.loads(read(m['compileCommandsPath'],m['compileCommandsSha256']));kernel=next(r['command']for r in db if r['file']==str(source/'builtins/node-compat/zlib/kernel.cpp'));words=shlex.split(kernel);includes=[];i=0
while i<len(words):
 v=words[i]
 if v in ['-I','-isystem']:i+=1;includes.append(words[i])
 elif v.startswith('-I')and len(v)>2:includes.append(v[2:])
 elif v.startswith('-isystem')and len(v)>8:includes.append(v[8:])
 i+=1
assert w['actualHeaderSearchDirectories']==[includes]
candidates=[Path(v)/'zlib.h'for v in includes if(Path(v)/'zlib.h').is_file()];assert candidates[0]==Path(selected['selectedDistribution'])/'include/zlib.h'
for r in db:
 if r['file'].startswith((str(source/'builtins')+'/',str(source/'runtime')+'/'))and r['file'].endswith('.cpp'):
  ws=shlex.split(r['command']);assert not any(v.startswith('@')or v in ['&&',';','|']or '$('in v for v in ws)
nm=w['archiveSymbolEvidence'];assert nm['command']==[nm['nm']['path'],'--defined-only','--extern-only','--format=posix','--print-file-name',selected['archive']['path']]
assert nm['nm']['sha256']=='0f0dfccb3778ec756b3bcbfe69574cdddfb2a6da2ae92c5bc1df1d1d6d3a591c'
nmo=next(r for r in w['witnessFiles']if Path(r['path']).name=='nm.stdout.txt');nmt=read(nmo['path'],nmo['sha256'],nmo['bytes']).decode()
for name in ['zlibVersion','deflateInit2_','deflate','deflateEnd','inflateInit2_','inflate','inflateEnd']:assert not any(re.search(r'(?:^|\s)(?:z_)?'+re.escape(name)+r'\s+[A-Za-z]\s',v)for v in nmt.splitlines())
nme=next(r for r in w['witnessFiles']if Path(r['path']).name=='nm.stderr.txt');assert read(nme['path'],nme['sha256'],nme['bytes']).decode()==str(selected['archive']['path'])+'[MmapFaultHandler.o]: no symbols\n'
ssl=m['openssl'];audit=ssl['completeSourceAudit'];assert audit['patchedSources']=={'crypto/uid.c':'86b53aecb1046e81dfbfe74d779704b408cbaa70abfb9a7d1cc98211bdc8ba08','crypto/rand/rand_lib.c':'e8c853b5d609b5b13f3a63ddcd88047a37fb75afa59e88d1950907c5a85bcd95'}
assert audit['receiptSha256']==ssl['receiptSha256']and Path(audit['sourceDirectory'])==Path(ssl['sourceDir'])
manifest=[dict(path=n,sha256=hashlib.sha256(p.read_bytes()).hexdigest())for p in sorted(Path(ssl['sourceDir']).rglob('*'))if p.is_file()for n in [str(p.relative_to(ssl['sourceDir']))]]
assert hashlib.sha256(json.dumps(sorted(manifest,key=lambda r:r['path']),separators=(',',':')).encode()).hexdigest()==audit['sourceManifestSha256']
read(ssl['receiptPath'],ssl['receiptSha256']);read(source/'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm','988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0',53512)
# Actual post-optimizer tool bytes are authenticated from the declared archive.
ba=next(r for r in m['downloadedArchives']if Path(r['path']).name=='binaryen-version_123-arm64-macos.tar.gz')
import tarfile
with tarfile.open(ba['path'])as tar:
 member=next(v for v in tar.getmembers()if v.name.endswith('/bin/wasm-opt'));b=tar.extractfile(member).read();read(optimizer[0],hashlib.sha256(b).hexdigest(),len(b))
log=read(spec['buildLog']['path'],spec['buildLog']['sha256'],spec['buildLog']['bytes']).decode();steps=[tuple(map(int,x))for x in re.findall(r'^\[(\d+)/(\d+)\]',log,re.M)];assert steps and steps[-1][0]==steps[-1][1]
value=dict(schemaVersion=1,verifiedPassed=True,rootObservation=spec['rootBuildObservation'],actualNewSourceControllerStageProofIdentitiesVerified=True,ownedOuterPid=49070,ownedInnerBashPgid=49081,completeRawRecordsBound=True,observedProcesses=len(observations),actualFinalGroups=outer['finalGroups'],noRemainingPidsOrForcedSignals=True,externalEvidenceInventory=external_rows,allFourSelectedHeadersMatchKnownPins=True,firstKernelHeaderActuallySelected=True,fullRawLinkMetadataExactlyReconstructed=True,noCompileResponseOrShellInjection=True,allSevenMozPrefixDefinitionsAndNmCommandVerified=True,allOpenSslPatchedManifestBytesRehashed=True,preview1AdapterStillExact=True,binaryenToolExactArchiveBytes=True,actualFinalNinjaStep=list(steps[-1]),standaloneCMakeRawTerminalIndependentlyObserved=False,ownerHelperNodeCompilerNmNinjaEngineCryptoGuestOrGcActionsInvoked=False,extraFileReads=list(seen.values()))
(P/'witness-review.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps(dict(witnessChecksPassed=True,observedProcesses=len(observations),finalNinjaStep=steps[-1],ownerActionsInvoked=False)))
