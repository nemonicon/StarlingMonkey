"""Bounded local --version/read-only probes. Never configures, builds or installs."""
import hashlib,json,os,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
W=Path('/private/tmp/starling-node-compat/next-native-build-v5')
SDK=W/'extracted-wasi-sdk/wasi-sdk-30.0-arm64-macos'
HOST=Path('/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin')
RUST=W/'rustup-home/toolchains/1.88.0-aarch64-apple-darwin/bin'
COMMANDS=[
 ('host-clang',[str(HOST/'clang'),'--version']),
 ('host-clangxx',[str(HOST/'clang++'),'--version']),
 ('python312',['/opt/homebrew/Cellar/python@3.12/3.12.8/bin/python3.12','--version']),
 ('python39',['/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9','--version']),
 ('cmake',['/opt/homebrew/Cellar/cmake/4.3.3/bin/cmake','--version']),
 ('ninja',['/opt/homebrew/Cellar/ninja/1.13.2/bin/ninja','--version']),
 ('make',['/usr/bin/make','--version']),
 ('sdk-clang',[str(SDK/'bin/clang'),'--version']),
 ('sdk-clangxx',[str(SDK/'bin/clang++'),'--version']),
 ('sdk-ar',[str(SDK/'bin/llvm-ar'),'--version']),
 ('sdk-wasm-ld',[str(SDK/'bin/wasm-ld'),'--version']),
 ('rustc',[str(RUST/'rustc'),'--version','--verbose']),
 ('cargo',[str(RUST/'cargo'),'--version','--verbose']),
 ('rust-target-libdir',[str(RUST/'rustc'),'--print','target-libdir','--target','wasm32-wasip1']),
 ('cbindgen',[str(W/'tools/bin/cbindgen'),'--version']),
 ('macos-sdk-path',['/usr/bin/xcrun','--sdk','macosx','--show-sdk-path']),
 ('macos-sdk-version',['/usr/bin/xcrun','--sdk','macosx','--show-sdk-version']),
]
def row(p):
 p=Path(p);h=hashlib.sha256();size=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b);size+=len(b)
 s=p.stat();return dict(path=str(p),resolvedPath=str(p.resolve()),sha256=h.hexdigest(),bytes=size,mode=oct(s.st_mode&0o777),device=s.st_dev,inode=s.st_ino)
def main():
 assert len(sys.argv)==1
 out=HERE/'observations';assert not out.exists();out.mkdir(mode=0o700)
 env={k:os.environ[k]for k in ['HOME','USER','LOGNAME']if k in os.environ};env.update(PATH='/usr/bin:/bin',LC_ALL='C',LANG='C',PYTHONDONTWRITEBYTECODE='1')
 before={p:row(p)for _,argv in COMMANDS for p in argv[:1]};result=[]
 for name,argv in COMMANDS:
  started=time.monotonic();record=dict(label=name,argv=argv,timeoutSeconds=10,binaryBefore=before[argv[0]])
  try:
   r=subprocess.run(argv,cwd=HERE,env=env,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=10,check=False)
   (out/(name+'.stdout.log')).write_bytes(r.stdout);(out/(name+'.stderr.log')).write_bytes(r.stderr)
   record.update(rawExitCode=r.returncode,timeout=False,stdout=r.stdout.decode('utf-8',errors='replace'),stderr=r.stderr.decode('utf-8',errors='replace'))
  except subprocess.TimeoutExpired as e:
   (out/(name+'.stdout.log')).write_bytes(e.stdout or b'');(out/(name+'.stderr.log')).write_bytes(e.stderr or b'');record.update(rawExitCode=None,timeout=True)
  record['elapsedSeconds']=time.monotonic()-started;record['binaryAfter']=row(argv[0]);assert record['binaryBefore']==record['binaryAfter'];result.append(record)
 report=dict(schemaVersion=1,state='LOCAL_INTL_TOOL_PREFLIGHT_OBSERVED_V1',commands=result,allCommandsRawZero=all(r['rawExitCode']==0 and r['timeout']is False for r in result),sourceRootModified=False,configureExecuted=False,compilerSourceWorkloadExecuted=False,buildExecuted=False,installExecuted=False,rustupInvoked=False,globalHomesRepurposed=False)
 (out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'commands':len(result),'allCommandsRawZero':report['allCommandsRawZero'],'result':str(out/'result.json')}))
if __name__=='__main__':main()
