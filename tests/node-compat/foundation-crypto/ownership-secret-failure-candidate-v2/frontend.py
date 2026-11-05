"""One permitted syntax-only check of the changed CPP; no owner wrapper/helper."""
from pathlib import Path
import hashlib,json,os,shlex,subprocess
HERE=Path(__file__).resolve().parent;OLD=HERE.parent/'ownership-secret-failure-candidate-v1';SOURCE=Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-source');WORK=Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-build');PRIVATE=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-failure-v2-syntax')
ROWS={}
def row(p):
    p=Path(p);assert p.is_file()and not p.is_symlink();a=p.stat();h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    b=p.stat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns);return dict(path=str(p),sha256=h.hexdigest(),bytes=b.st_size)
def verify(d):a=row(d['path']);assert a['sha256']==d['sha256']and a['bytes']==d['bytes'];ROWS[a['path']]=a;return Path(d['path'])
def read(p):d=row(p);verify(d);return json.loads(Path(p).read_bytes())
def write(p,b):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
def save(p,v):write(p,(json.dumps(v,indent=2)+'\n').encode())
old_index=row(OLD/'index.json');assert old_index['sha256']=='070f1c20247f4538622cf60fdc1613d44b113c10de0173250456c13d81db1958';index=read(old_index['path'])
for d in index['files']:verify(dict(d,path=str(OLD/d['path'])))
for d in read(OLD/'syntax-input-hashes.json')['files']:verify(d)
for d in read(OLD/'input-freeze.json')['files']:verify(d)
base_overlay=read(OLD/'syntax-overlay.json');old_syntax=read(OLD/'syntax-results.json');old_command=read(OLD/'evidence/crypto-algorithm/command.json');original=old_command['originalCompileDbRow'];compiler=Path(old_command['actualCompilerAlias']);verify(old_command['actualCompilerLeaf']);verify(old_command['originalCompileDb']);verify(old_command['originalWrapper']);assert compiler.resolve()==Path(old_command['actualCompilerLeaf']['path'])
for name in ['crypto-key.cpp','crypto-raii.h']:assert(HERE/'afterimages/builtins/web/crypto'/name).read_bytes()==(OLD/'afterimages/builtins/web/crypto'/name).read_bytes()
assert not PRIVATE.exists()and not PRIVATE.is_symlink();PRIVATE.mkdir(mode=0o700);(PRIVATE/'tmp').mkdir(mode=0o700)
copies=[];mapped={};vfs=[]
for d in base_overlay['sourceCopies']:
    verify(d['original']);name=d['relativePath'];after=HERE/'afterimages'/name;source=after if after.exists()else Path(d['original']['path']);verify(row(source));target=PRIVATE/'source'/name;write(target,source.read_bytes());assert row(target)['sha256']==row(source)['sha256']and target.stat().st_ino!=source.stat().st_ino
    copies.append(dict(relativePath=name,original=d['original'],syntaxBytes=row(target),afterimage=after.exists(),insideNative355Manifest=d['insideNative355Manifest']));mapped[str(SOURCE/name)]=target;vfs.append(dict(type='file',name=str(SOURCE/name),**{'external-contents':str(target)}))
assert len(copies)==359 and sum(d['afterimage']for d in copies)==3
overlay=PRIVATE/'overlay.json';save(overlay,dict(version=0,**{'case-sensitive':True,'use-external-names':False},roots=vfs))
words=shlex.split(original['command']);argv=[str(compiler)];removed=[];i=1
while i<len(words):
    if words[i]in['-o','-c']:removed.append(words[i:i+2]);i+=2
    else:argv.append(words[i]);i+=1
evidence=HERE/'evidence/crypto-algorithm';evidence.mkdir(parents=True,exist_ok=False);dep=evidence/'headers.d';argv+=['-ivfsoverlay',str(overlay),'-fsyntax-only','-MD','-MF',str(dep),'-MT','crypto-algorithm',original['file']]
assert '-c'not in argv and '-o'not in argv and '-fsyntax-only'in argv
save(evidence/'command.json',dict(originalCompileDbRow=original,originalCompileDb=old_command['originalCompileDb'],originalWrapper=old_command['originalWrapper'],actualCompilerAlias=str(compiler),actualCompilerLeaf=row(compiler.resolve()),actualCommand=argv,cwd=str(PRIVATE),removedCompileOutputAndAction=removed,overlay=row(overlay),action='SDK30_LLVM21_CHANGED_CPP_FRONTEND_SYNTAX_ONLY_NO_OBJECT_LINK_RUNTIME'))
timed_out=False
try:r=subprocess.run(argv,cwd=PRIVATE,env={'PATH':'/usr/bin:/bin','TMPDIR':str(PRIVATE/'tmp')},stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60);status=r.returncode;stdout=r.stdout;stderr=r.stderr
except subprocess.TimeoutExpired as e:timed_out=True;status=None;stdout=e.stdout or b'';stderr=e.stderr or b''
write(evidence/'stdout.log',stdout);write(evidence/'stderr.log',stderr);save(evidence/'terminal.json',dict(schemaVersion=1,rawExitCode=status,timedOut=timed_out,timeoutSeconds=60,command=row(evidence/'command.json'),stdout=row(evidence/'stdout.log'),stderr=row(evidence/'stderr.log'),frontendSyntaxOnly=True,objectLinkOrRuntimeInvoked=False));assert status==0 and not timed_out and stdout==stderr==b''
parts=dep.read_text().replace('\\\n',' ').partition(':');assert parts[0]=='crypto-algorithm';dependencies=[]
for logical in shlex.split(parts[2]):
    canonical=os.path.normpath(logical);p=mapped[canonical]if canonical in mapped else Path(logical).resolve(strict=True)
    if canonical.startswith(str(SOURCE)+'/'):assert canonical in mapped
    assert str(p).startswith((str(PRIVATE/'source')+'/',str(WORK/'spidermonkey-dist-release/include')+'/',str(WORK/'cache/wasi-sdk/85e6')+'/',str(WORK/'engine-abi-fixed-bigint-v1-keyowner-v2.OFF.p1.e1.d1.a1.q1.u1.w1.t1.c1.z1.s1/deps')+'/'))
    physical=row(p);verify(physical);dependencies.append(dict(logicalPath=logical,canonicalLogicalPath=canonical,physical=physical,mappedOverlaySource=canonical in mapped))
assert {str(p)for p in PRIVATE.rglob('*')if p.is_file()}=={d['syntaxBytes']['path']for d in copies}|{str(overlay)}
for d in list(ROWS.values()):verify(d)
for d in copies:verify(d['syntaxBytes'])
save(HERE/'syntax-overlay.json',dict(schemaVersion=1,privateRoot=str(PRIVATE),overlay=row(overlay),sourceCopies=copies,genuineNativeInputs=355,additionalObservedConfiguredHeaders=4,afterimages=3,productionOrNormalSourceMutated=False))
save(HERE/'header-dependencies.json',dict(schemaVersion=1,files=dependencies,allFinalHashesStable=True))
save(HERE/'syntax-input-hashes.json',dict(schemaVersion=1,files=list(ROWS.values()),allFinalHashesStable=True))
save(HERE/'syntax-results.json',dict(schemaVersion=1,state='CHANGED_CPP_SDK_FRONTEND_SYNTAX_ONLY_PASSED_V2',freshFrontendChecks=1,freshRawExitCodes=[0],freshStdoutBytes=0,freshStderrBytes=0,freshTerminal=row(evidence/'terminal.json'),freshDependencyFile=row(dep),freshDependencies=len(dependencies),originalCompileDb=old_command['originalCompileDb'],compilerLeaf=row(compiler.resolve()),inheritedSdkArchiveProof=row(OLD/'syntax-results.json'),unchangedKeySyntaxTerminal=row(OLD/'evidence/crypto-key/terminal.json'),unchangedKeyAndRaiiBytesVerified=True,newObjectOrLinkOrEngineOrFaultOrRuntimeActionsInvoked=False,compilerFrontendOnly=True))
print(json.dumps(dict(changedCppFrontendPassed=True,rawExitCodes=[0],dependencies=len(dependencies),objectLinkOrRuntimeInvoked=False)))
