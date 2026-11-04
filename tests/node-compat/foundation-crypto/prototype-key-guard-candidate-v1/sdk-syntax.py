"""One isolated frontend-only source check; never runs keys/crypto/GC/guest.

Uses a new five-file VFS overlay. Does not configure/build/link/apply sources or
invoke owner helpers. The exclusive scratch directory prevents evidence reuse.
"""
from pathlib import Path
import hashlib,json,os,shlex,signal,subprocess,time
H=Path(__file__).resolve().parent;ROOT=H.parents[3];OWNER=H.parent/'key-owner-candidate-v1';STAGE=Path('/private/tmp/starling-node-compat/consumers-source-v2');WORK=Path('/tmp/starling-node-compat/crypto-prototype-key-guard-source-v1-sdk')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path,digest=None,size=None):
 p=Path(path);assert p.is_file();raw=p.read_bytes();assert digest is None or sha(raw)==digest,p;assert size is None or len(raw)==size,p;return raw
def put(path,value):
 with Path(path).open('x')as stream:json.dump(value,stream,indent=2);stream.write('\n')
def auth_parent():
 index=json.loads(read(OWNER/'index.json','216d0272025145f70c3a1e1c5e4f27cc3cc47ef6f97ae8131467e803db3c47d0'))
 for row in index['files']:read(OWNER/row['path'],row['sha256'],row['bytes'])
 for row in json.loads(read(OWNER/'source-inputs.json'))['files']:
  p=Path(row['path']);assert str(p.resolve())==row['realpath']and p.is_symlink()==row['isSymlink'];read(p,row['sha256'],row['bytes'])
auth_parent();composition=json.loads(read(H/'composition.json'));mapping={};roots=[]
for row in composition['afterimages']:
 actual=(H/row['afterimage']).resolve();read(actual,row['sha256'],row['bytes'])
 for base in [ROOT,STAGE]:
  logical=base/row['path'];mapping[str(logical.resolve())]=actual;roots.append({'type':'file','name':str(logical),'external-contents':str(actual)})
assert len(composition['afterimages'])==5 and len(roots)==10
overlay={'version':0,'case-sensitive':'true','use-external-names':False,'roots':roots}
evidence=H/'evidence';evidence.mkdir(exist_ok=True);overlay_path=evidence/'overlay.json';put(overlay_path,overlay)
database=Path('/tmp/starling-node-compat/production-consumers-v1/native-freeze/normal-off-compile_commands.json');database_bytes=read(database);commands=json.loads(database_bytes)
prototype=next(row for row in commands if row['file']==str(STAGE/'builtins/web/crypto/subtle-crypto.cpp'))
original=shlex.split(prototype['command']);assert original.count('-c')==original.count('-o')==1
argv=[];i=0
while i<len(original):
 if original[i]=='-c':i+=1;continue
 if original[i]=='-o':i+=2;continue
 argv.append(original[i]);i+=1
assert '-O3'in argv and'-DNDEBUG'in argv and'-fno-exceptions'in argv and'--target=wasm32-wasi'in argv
assert not any('NODE_COMPAT_GC_STRESS'in value or'OOM'in value or'DEBUG=1'in value for value in argv)
assert not WORK.exists();WORK.mkdir()
dependency=WORK/'subtle-crypto.d';argv.extend(['-ivfsoverlay',str(overlay_path.resolve()),'-fsyntax-only','-MD','-MF',str(dependency),'-H'])
wrapper=Path(argv[0]);wrapper_bytes=read(wrapper);compiler=json.loads(read(OWNER/'evidence/syntax-results.json'))['compiler'];read(compiler['path'],compiler['sha256'],compiler['bytes'])
command={'schemaVersion':1,'action':'SOURCE_ONLY_FRONTEND_SYNTAX','prototype':prototype,'prototypeCompileCommands':{'path':str(database),'sha256':sha(database_bytes),'bytes':len(database_bytes)},'command':argv,'cwd':prototype['directory'],'wrapper':{'path':str(wrapper),'sha256':sha(wrapper_bytes),'bytes':len(wrapper_bytes)},'compiler':compiler,'overlayPath':str(overlay_path.resolve()),'overlaySha256':sha(read(overlay_path)),'fiveSourceAfterimages':True,'nativeObjectsOrLinkRequested':False}
put(evidence/'sdk-command.json',command);auth_parent()
started=time.monotonic();timed_out=False
stdout_path=evidence/'sdk.stdout.log';stderr_path=evidence/'sdk.stderr.log'
with stdout_path.open('xb')as stdout,stderr_path.open('xb')as stderr:
 child=subprocess.Popen(argv,cwd=prototype['directory'],stdout=stdout,stderr=stderr,start_new_session=True)
 try:code=child.wait(timeout=90)
 except subprocess.TimeoutExpired:
  timed_out=True;os.killpg(child.pid,signal.SIGKILL);code=child.wait()
 stdout.flush();stderr.flush();os.fsync(stdout.fileno());os.fsync(stderr.fileno())
put(evidence/'sdk-terminal.json',{'schemaVersion':1,'state':'terminal','pid':child.pid,'returncode':code,'signal':-code if code<0 else None,'timeout':timed_out,'wallSeconds':time.monotonic()-started,'syntaxOnly':True,'objectOrLink':False,'keyCryptoGcOrGuestExecuted':False})
# Terminal evidence is retained before source/diagnostic assertions.
assert code==0 and not timed_out
text=read(dependency).decode();paths=shlex.split(text.replace('\\\n',' ').partition(':')[2]);rows=[]
for path in paths:
 logical=Path(path);physical=mapping.get(str(logical.resolve()),logical);raw=read(physical)
 rows.append({'logicalPath':path,'physicalPath':str(physical),'sha256':sha(raw),'bytes':len(raw),'vfsAfterimage':str(logical.resolve())in mapping})
assert len({row['logicalPath']for row in rows})==len(rows)
put(evidence/'dependencies.json',{'schemaVersion':1,'state':'ACTUAL_FRONTEND_DEPENDENCIES_HASHED_AFTER_ONLY','allHeadersPrehashed':False,'files':rows})
(evidence/'subtle-crypto.d').write_bytes(read(dependency))
auth_parent()
for row in composition['afterimages']:read(H/row['afterimage'],row['sha256'],row['bytes'])
diagnostics=read(stderr_path).decode();errors=sum(' error:'in line or' fatal error:'in line for line in diagnostics.splitlines());warnings=sum(' warning:'in line for line in diagnostics.splitlines());assert errors==warnings==0
put(evidence/'syntax-results.json',{'schemaVersion':1,'state':'ACTUAL_COMPOSED_147_RELEASE_FRONTEND_SYNTAX_PASSED_ONLY','exitCode':code,'warnings':warnings,'errors':errors,'logicalDependencies':len(rows),'fiveVfsAfterimages':True,'vfsMappingRows':10,'headersHashedAfterOnly':True,'sourceInputsRecheckedAfterFrontend':True,'nativeFullBuildLinkInstall':False,'keyCryptoGcGuestOrOldUnsafePrototypePathExecuted':False})
print(json.dumps({'state':'SOURCE_FRONTEND_ONLY_PASSED','exitCode':code,'dependencies':len(rows),'warnings':warnings,'keyCryptoGcOrGuestExecuted':False}))
