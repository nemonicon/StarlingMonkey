"""Only explicitly authorized SDK frontend syntax checks; no owner helper imports."""
from pathlib import Path
import hashlib,json,os,shlex,subprocess,sys,tarfile
HERE=Path(__file__).resolve().parent;SOURCE=Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-source');FROZEN=Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-freeze');WORK=Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-build')
PRIVATE=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-failure-syntax-v1');INPUTS={}
def row(p):
    p=Path(p);assert p.is_file()and not p.is_symlink();a=p.stat();h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    b=p.stat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns);return dict(path=str(p),sha256=h.hexdigest(),bytes=b.st_size)
def verify(d):actual=row(d['path']);assert actual['sha256']==d['sha256']and actual['bytes']==d['bytes'];INPUTS[actual['path']]=actual;return Path(d['path'])
def read(p):d=row(p);verify(d);return json.loads(Path(p).read_bytes())
def write(p,b):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
def save(p,v):write(p,(json.dumps(v,indent=2)+'\n').encode())
freeze=read(HERE/'input-freeze.json')
for d in freeze['files']:verify(d)
m=read(FROZEN/'gc-off.engine.wasm.build.json');dbrow=row(m['compileCommandsPath']);assert dbrow['sha256']==m['compileCommandsSha256'];db=read(dbrow['path']);original_rows=[d for d in db if d['file']in [str(SOURCE/'builtins/web/crypto/crypto-key.cpp'),str(SOURCE/'builtins/web/crypto/crypto-algorithm.cpp')]];assert len(original_rows)==2
wrapper=Path(m['compileCommandsPath']).parent/'cxx-wrapper';wrapper_text=verify(row(wrapper)).read_text();sdk=WORK/'cache/wasi-sdk/85e6';assert str(sdk/'bin/clang++')+' "$@"'in wrapper_text
sdk_archive=next(d for d in m['downloadedArchives']if Path(d['path']).name=='wasi-sdk-30.0-arm64-macos.tar.gz');ar=row(sdk_archive['path']);assert ar['sha256']==sdk_archive['sha256'];verify(ar);aliases=[]
with tarfile.open(ar['path'])as tar:
    for name in ['VERSION','bin/clang++','bin/clang','bin/clang-21','bin/clang++.cfg','bin/clang.cfg']:
        member=tar.getmember('wasi-sdk-30.0-arm64-macos/'+name);p=sdk/name
        if member.issym():assert p.is_symlink()and os.readlink(p)==member.linkname;aliases.append(dict(path=str(p),linkText=member.linkname,resolvedTarget=str(p.resolve(strict=True))))
        else:
            blob=tar.extractfile(member).read();d=row(p);assert d['sha256']==hashlib.sha256(blob).hexdigest()and d['bytes']==len(blob);verify(d)
assert 'llvm-version: 21.1.4'in(sdk/'VERSION').read_text();compiler=sdk/'bin/clang++';assert compiler.resolve(strict=True)==sdk/'bin/clang-21'
resume=sys.argv[1:]==['--resume-recorded-first-syntax'];assert not sys.argv[1:]or resume
if resume:assert PRIVATE.is_dir()and not PRIVATE.is_symlink()and(PRIVATE/'tmp').is_dir()
else:assert not PRIVATE.exists()and not PRIVATE.is_symlink();PRIVATE.mkdir(mode=0o700);(PRIVATE/'tmp').mkdir(mode=0o700)
manifest={d['path']:d['sha256']for d in m['sourceManifest']};paths=set(manifest)
# Mirror every genuine355 input and every actual configured-source header in
# these compiler include roots. Four generated/header dependencies are outside
# the355 manifest and remain explicitly labelled actual observed inputs.
for prefix in ['include','runtime','builtins','deps/include','crates']:
    for p in(SOURCE/prefix).rglob('*'):
        if p.is_file()and not p.is_symlink()and p.suffix in ['.h','.hpp','.inc']:paths.add(p.relative_to(SOURCE).as_posix())
copies=[];vfs=[];mapped={}
for name in sorted(paths):
    original=row(SOURCE/name);verify(original)
    if name in manifest:assert original['sha256']==manifest[name]
    after=HERE/'afterimages'/name;chosen=after if after.exists()else SOURCE/name;chosen_row=row(chosen);verify(chosen_row);target=PRIVATE/'source'/name
    if resume:assert target.read_bytes()==chosen.read_bytes()
    else:write(target,chosen.read_bytes())
    assert row(target)['sha256']==chosen_row['sha256']and target.stat().st_ino!=chosen.stat().st_ino
    copies.append(dict(relativePath=name,original=original,syntaxBytes=row(target),afterimage=after.exists(),insideNative355Manifest=name in manifest));mapped[str(SOURCE/name)]=row(target);mapped[str(target)]=row(target)
    vfs.append(dict(type='file',name=str(SOURCE/name),**{'external-contents':str(target)}))
assert len(manifest)==355 and len(copies)==359 and sum(d['afterimage']for d in copies)==3
overlay=dict(version=0,**{'case-sensitive':True,'use-external-names':False},roots=vfs);overlay_path=PRIVATE/'overlay.json'
if resume:assert json.loads(overlay_path.read_bytes())==overlay
else:save(overlay_path,overlay)
records=[];dependencies={}
for original in original_rows:
    label=Path(original['file']).stem;words=shlex.split(original['command']);assert words[0]==str(wrapper)and words.count('-o')==words.count('-c')==1
    argv=[str(compiler)];removed=[];i=1
    while i<len(words):
        if words[i]in ['-o','-c']:removed.append(words[i:i+2]);i+=2
        else:argv.append(words[i]);i+=1
    evidence=HERE/'evidence'/label;reused=resume and evidence.exists()
    if not reused:evidence.mkdir(parents=True,exist_ok=False)
    dep_path=evidence/'headers.d'
    argv+=['-ivfsoverlay',str(overlay_path),'-fsyntax-only','-MD','-MF',str(dep_path),'-MT',label,original['file']]
    assert '-c'not in argv and '-o'not in argv and '-fsyntax-only'in argv and '--target=wasm32-wasi'in argv
    command=dict(originalCompileDbRow=original,originalCompileDb=dbrow,originalWrapper=row(wrapper),actualCompilerAlias=str(compiler),actualCompilerLeaf=row(compiler.resolve()),actualCommand=argv,cwd=str(PRIVATE),removedCompileOutputAndAction=removed,overlay=row(overlay_path),action='SDK30_LLVM21_FRONTEND_SYNTAX_ONLY_NO_OBJECT_LINK_OR_RUNTIME')
    if reused:
        assert read(evidence/'command.json')==command;terminal=read(evidence/'terminal.json');status=terminal['rawExitCode'];timed_out=terminal['timedOut'];stdout=verify(terminal['stdout']).read_bytes();stderr=verify(terminal['stderr']).read_bytes()
    else:
        save(evidence/'command.json',command);timed_out=False
        try:r=subprocess.run(argv,cwd=PRIVATE,env={'PATH':'/usr/bin:/bin','TMPDIR':str(PRIVATE/'tmp')},stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60);status=r.returncode;stdout=r.stdout;stderr=r.stderr
        except subprocess.TimeoutExpired as error:timed_out=True;status=None;stdout=error.stdout or b'';stderr=error.stderr or b''
        write(evidence/'stdout.log',stdout);write(evidence/'stderr.log',stderr);terminal=dict(schemaVersion=1,rawExitCode=status,timedOut=timed_out,timeoutSeconds=60,command=row(evidence/'command.json'),stdout=row(evidence/'stdout.log'),stderr=row(evidence/'stderr.log'),frontendSyntaxOnly=True,objectLinkOrEngineInvoked=False);save(evidence/'terminal.json',terminal)
    records.append(terminal);assert status==0 and timed_out is False and stdout==stderr==b'',(label,status,stderr.decode())
    dep_text=dep_path.read_text().replace('\\\n',' ');target,sep,rest=dep_text.partition(':');assert sep and target==label
    dep_names=shlex.split(rest)
    for logical in dep_names:
        p=Path(logical);assert p.is_absolute();canonical_logical=os.path.normpath(logical);physical=Path(mapped[canonical_logical]['path'])if canonical_logical in mapped else p.resolve(strict=True)
        if canonical_logical.startswith(str(SOURCE)+'/'):assert canonical_logical in mapped,'Unknown configured header outside complete overlay'
        assert str(physical).startswith((str(PRIVATE/'source')+'/',str(WORK/'spidermonkey-dist-release/include')+'/',str(sdk)+'/',m['openssl']['installDir']+'/include/')),'Unknown header/context'
        d=row(physical);verify(d);dependencies[logical]=dict(logicalPath=logical,canonicalLogicalPath=canonical_logical,physical=d,mappedOverlaySource=canonical_logical in mapped)
    terminal['dependencyFile']=row(dep_path)
for d in list(INPUTS.values()):verify(d)
for d in copies:assert row(d['syntaxBytes']['path'])==d['syntaxBytes']
expected_private_files={d['syntaxBytes']['path']for d in copies}|{str(overlay_path)}
assert {str(p)for p in PRIVATE.rglob('*')if p.is_file()}==expected_private_files,'No generated object/link output beyond original copied source inputs (which include a sealed adapter wasm DATA file)'
save(HERE/'syntax-overlay.json',dict(schemaVersion=1,privateRoot=str(PRIVATE),overlay=row(overlay_path),sourceCopies=copies,genuineNativeInputs=355,additionalObservedConfiguredHeaders=4,afterimages=3,sourceAndNormalFilesMutated=False))
save(HERE/'syntax-results.json',dict(schemaVersion=1,state='ACTUAL_PINNED_SDK_FRONTEND_SYNTAX_ONLY_PASSED_V1',compilerAlias=str(compiler),compilerLeaf=row(compiler.resolve()),sdkArchive=ar,sdkAliases=aliases,sdkVersionData=row(sdk/'VERSION'),originalCompileDb=dbrow,records=records,dependencyFiles=[dict(path=d['path'],sha256=d['sha256'],bytes=d['bytes'])for d in [row(HERE/'evidence'/Path(o['file']).stem/'headers.d')for o in original_rows]],dependencyCount=len(dependencies),checks=2,rawExitCodes=[0,0],stdoutBytes=0,stderrBytes=0,objectOrLinkOrEngineInvoked=False,ownerHelpersInvoked=False,actualGuestKeyGcOomFaultOrPrototypeActionsInvoked=False,syntaxOnlyNotSecurityOrRuntimeProof=True))
save(HERE/'header-dependencies.json',dict(schemaVersion=1,files=list(dependencies.values()),allFinalInputHashesStable=True,completeActualHeaderSetRetained=True))
save(HERE/'syntax-input-hashes.json',dict(schemaVersion=1,files=list(INPUTS.values()),allFinalInputHashesStable=True,syntaxOnly=True))
print(json.dumps(dict(frontendSyntaxOnlyPassed=True,checks=2,rawExitCodes=[0,0],dependencies=len(dependencies),nativeOverlayFiles=355,additionalHeaders=4,afterimages=3,ownerRuntimeActionsInvoked=False)))
