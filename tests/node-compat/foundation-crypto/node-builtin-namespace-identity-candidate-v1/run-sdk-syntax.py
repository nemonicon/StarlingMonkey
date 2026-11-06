"""Root-authorized ONE frontend-only command from actual9aec compiler row."""
from pathlib import Path
import hashlib,importlib.util,json,os,shlex,stat,sys
sys.dont_write_bytecode=True
OWN=Path(__file__).resolve().parent
REPO=OWN.parents[3]
SOURCE=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-source')
BUILD=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v3-build')
SDK=BUILD/'cache/wasi-sdk/85e6'
STAGE=Path('/private/tmp/starling-node-compat/node-builtin-namespace-identity-v1-sdk-syntax')
MONITOR=OWN.parent/'ownership-gc-build-controller-candidate-v1'
protected={}
def desc(p):
 p=Path(p);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024**2),b''):h.update(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size)
def guard(r):
 p=Path(r['path']);assert p.is_file()and not p.is_symlink();assert desc(p)==r,p
 s=p.stat();observed=dict(sha256=r['sha256'],bytes=r['bytes'],mode=stat.S_IMODE(s.st_mode),device=s.st_dev,inode=s.st_ino,links=s.st_nlink)
 if str(p)in protected:assert protected[str(p)]==observed
 else:protected[str(p)]=observed
def read(p):return json.loads(Path(p).read_bytes())
def write(p,data):
 p=Path(p);assert p.is_relative_to(STAGE);p.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
 with p.open('xb')as f:os.fchmod(f.fileno(),0o600);assert f.write(data)==len(data);f.flush();os.fsync(f.fileno())
def save(p,v):write(p,(json.dumps(v,indent=2)+'\n').encode())
def family(p,want):
 r=desc(p/'index.json');assert r['sha256']==want;guard(r);ix=read(r['path'])
 for x in ix['files']:guard(dict(x,path=str(p/x['path'])))
 return r
def stripped(command):
 words=shlex.split(command);driver=words.pop(0);args=[];removed=[];main=None;i=0
 while i<len(words):
  w=words[i]
  if w in ['-o','-MF','-MT','-MQ','-MJ','--serialize-diagnostics']:
   removed.append(words[i:i+2]);i+=2;continue
  if w=='-c':main=words[i+1];removed.append(words[i:i+2]);i+=2;continue
  if w in ['-MD','-MMD','-MP','-MG','-M','-MM']:removed.append([w]);i+=1;continue
  assert not any(w.startswith(x)and w!=x for x in ['-MF','-MT','-MQ','-MJ'])
  args.append(w);i+=1
 assert main and '--target=wasm32-wasi'in args and '-O3'in args and '-DNDEBUG'in args and '-fno-exceptions'in args
 assert not any(w.startswith(('-DDEBUG','-DNODE_COMPAT_OOM_TESTING','-DNODE_COMPAT_GC_STRESS'))for w in args)
 return driver,args,main,removed
def main():
 assert sys.argv[1:]==['--execute-authorized-one-syntax-check']and not STAGE.exists()
 guard(desc(Path(__file__).resolve()))
 deriv=read(OWN/'derivation.json');assert deriv['after']['sha256']=='b399c648323e44983345036bc01d679fb3e4618514fc4990e4c2ea7a2d984625';guard(deriv['before']);guard(deriv['liveBefore']);guard(deriv['after'])
 caller_index=family(OWN.parent/'node-crypto-hash-hmac-component-diagnostic-candidate-v2','48b15d2fd8618f6cd05a2404b2b3ace3ffd422d50889e9a30d34e3d6c5236f2f')
 refs=read(OWN.parent/'node-crypto-hash-hmac-component-diagnostic-candidate-v2/references.json')
 for k in ['nativeEngine','nativeMetadata','revalidationLedger']:guard(refs[k])
 assert refs['nativeEngine']['sha256']=='9aec9297122c33b60790fcf4e1ce909db0200a426c04de98074e39046aa0f16e'
 assert refs['nativeMetadata']['sha256']=='2b725c114a3c23e582f87213ec5de6af128416dc8f10e9a9f9d3f6cd5d0fbce6'
 metadata=read(refs['nativeMetadata']['path']);assert len(metadata)==83 and len(metadata['sourceManifest'])==357 and len(metadata['componentizeSourceManifest'])==3
 db=Path(metadata['compileCommandsPath']);guard(dict(path=str(db),sha256=metadata['compileCommandsSha256'],bytes=db.stat().st_size))
 rows=read(db);row=next(r for r in rows if r['file']==str(SOURCE/'runtime/script_loader.cpp'))
 driver,args,main_input,removed=stripped(row['command']);guard(desc(driver));wrapper=Path(driver).read_text()
 compiler=SDK/'bin/clang++';leaf=desc(compiler.resolve());assert leaf['sha256']=='1aca933cc48d7e137804231e0ced1624052fe489562ab496d63ad9a23998c7fe'and str(compiler)in wrapper and '"$@"'in wrapper
 guard(leaf);assert main_input==str(SOURCE/'runtime/script_loader.cpp')
 ledger=read(refs['revalidationLedger']['path'])['files'];sdk_rows=[r for r in ledger if r['path'].startswith(str(SDK)+'/')];sm_rows=[r for r in ledger if r['path'].startswith(str(BUILD/'spidermonkey-dist-release/include')+'/')]
 assert len(sdk_rows)==10114 and len(sm_rows)==352
 for r in sdk_rows+sm_rows:guard(r)
 for r in metadata['sourceManifest']:
  p=SOURCE/r['path'];guard(dict(path=str(p),sha256=r['sha256'],bytes=p.stat().st_size))
 for relative in ['deps/include/picosha2.h','deps/include/rust-encoding.h','deps/include/wizer.h','runtime/sequence.hpp']:guard(desc(SOURCE/relative))
 # Authenticate every actual staged regular non-Git file so no quoted include
 # outside the native357 list can silently become an unobserved input.
 source_files=[]
 for p in sorted(SOURCE.rglob('*')):
  if '.git'in p.relative_to(SOURCE).parts or p.is_symlink()or not p.is_file():continue
  r=desc(p);guard(r);source_files.append(str(p))
 embed_command=metadata['actualEmbeddingCompileCommands'][0];_,_,embed_input,_=stripped(embed_command);external_root=Path(embed_input).parents[1]
 for r in metadata['componentizeSourceManifest']:
  p=external_root/r['path'];guard(dict(path=str(p),sha256=r['sha256'],bytes=p.stat().st_size))
 ancestor=OWN.parent/'node-crypto-hash-hmac-artifact-revalidation-candidate-v1';ix=desc(ancestor/'index.json');assert ix['sha256']=='175e4061a92d982ad8cefbd77d2be3e8d4b88f9906df3d186923ba64397a918e';guard(ix)
 a=next(r for r in read(ix['path'])['files']if r['path']=='reference-aliases.json');alias_path=ancestor/a['path'];guard(dict(a,path=str(alias_path)))
 aliases=[r for r in read(alias_path)['symlinks']if r['path'].startswith(str(SDK)+'/')];assert len(aliases)==31
 for a in aliases:assert Path(a['path']).is_symlink()and os.readlink(a['path'])==a['linkText']and str(Path(a['path']).resolve())==a['resolved']
 monitor_index=family(MONITOR,'0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b')
 assert desc(MONITOR/'monitor.py')['sha256']=='86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
 STAGE.mkdir(mode=0o700);(STAGE/'tmp').mkdir(mode=0o700)
 private=STAGE/'native/runtime/script_loader.cpp';write(private,Path(deriv['after']['path']).read_bytes());assert private.stat().st_ino!=Path(deriv['after']['path']).stat().st_ino
 overlay=STAGE/'overlay.json';save(overlay,{'version':0,'case-sensitive':True,'use-external-names':False,'roots':[{'type':'file','name':main_input,'external-contents':str(private)}]})
 deps=STAGE/'script-loader.d';argv=[str(compiler),*args,'-ivfsoverlay',str(overlay),'-fsyntax-only','-MD','-MF',str(deps),'-MT','syntax-only-script-loader',str(private)]
 assert '-c'not in argv and '-o'not in argv and argv.count('-fsyntax-only')==1
 env=dict(PATH=str(SDK/'bin')+':/usr/bin:/bin',LC_ALL='C',LANG='C',TMPDIR=str(STAGE/'tmp'))
 for k in ['HOME','home','CODEX_HOME']:
  if k in os.environ:env[k]=os.environ[k]
 authority=dict(scope='Root-authorized one script_loader SDK frontend only',afterimage=deriv['after'],codegenLinkBuildEngineGuestCryptoAllowed=False)
 save(STAGE/'plan.json',dict(schemaVersion=1,authority=authority,driverSource=desc(Path(__file__).resolve()),actualCompileRow=row,actualMetadata=refs['nativeMetadata'],referencesAuthenticatedByCallerIndex=caller_index,compilerAlias=str(compiler),compilerLeaf=leaf,wrapperReadNotExecuted=desc(driver),removedOriginalOutputs=removed,argv=argv,cwd=str(STAGE),timeoutSeconds=60,overlay=desc(overlay),privateMainInput=desc(private),sdkRegularFiles=len(sdk_rows),spidermonkeyHeaders=len(sm_rows),configuredSourceRegularFiles=len(source_files),nativeSourceFiles=357,externalEmbeddingSources=3,sourceInventoryCountUnchanged=True,monitorIndex=monitor_index,environmentNames=sorted(env),onlySyntaxFrontendRequested=True))
 save(STAGE/'protection-before.json',dict(schemaVersion=1,files=protected,sdkAliases=aliases))
 spec=importlib.util.spec_from_file_location('genuine_builtin_alias_one_syntax_monitor',MONITOR/'monitor.py');monitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(monitor)
 out=STAGE/'command';out.mkdir(mode=0o700);terminal=None;protection=False
 try:terminal=monitor.monitor(argv,str(STAGE),env,out,60,authority)
 finally:
  for path,r in protected.items():
   p=Path(path);s=p.stat();actual=desc(p);assert actual['sha256']==r['sha256']and actual['bytes']==r['bytes']and(stat.S_IMODE(s.st_mode),s.st_dev,s.st_ino,s.st_nlink)==(r['mode'],r['device'],r['inode'],r['links']),path
  for a in aliases:assert os.readlink(a['path'])==a['linkText']and str(Path(a['path']).resolve())==a['resolved']
  assert sorted(str(p)for p in SOURCE.rglob('*')if '.git'not in p.relative_to(SOURCE).parts and not p.is_symlink()and p.is_file())==source_files
  protection=True;save(STAGE/'protection-final.json',dict(schemaVersion=1,unchangedFiles=len(protected),allHashesModesInodesLinksUnchanged=True,sdkAliasesUnchanged=31,configuredSourceMembershipUnchanged=True))
 assert terminal is not None
 clean=terminal['allObservedOwnedGroupsGone']and terminal['parentOwnedGroupGone']and not terminal['forcedCleanup']and not terminal['timeout']and not terminal['signals']and not terminal['errors']and not terminal['remainingObservedPids']
 result=dict(schemaVersion=1,state='BUILTIN_ALIAS_SINGLE_FRONTEND_SYNTAX_PASSED'if terminal['rawExitCode']==0 and clean and protection else'BUILTIN_ALIAS_FRONTEND_FAILURE_PRESERVED',rawExitCode=terminal['rawExitCode'],allOwnedGroupsGone=bool(clean),terminal=desc(out/'terminal.json'),stdout=desc(out/'stdout.log'),stderr=desc(out/'stderr.log'),actualPlan=desc(STAGE/'plan.json'),protectionBefore=desc(STAGE/'protection-before.json'),protectionFinal=desc(STAGE/'protection-final.json'),onlySyntaxFrontendRequested=True,nativeBuildLinkEngineGuestOrCryptoInvoked=False)
 save(STAGE/'result.json',result);print(json.dumps(result),flush=True)
 if terminal['rawExitCode']!=0 or not clean:sys.exit(1)
if __name__=='__main__':main()
