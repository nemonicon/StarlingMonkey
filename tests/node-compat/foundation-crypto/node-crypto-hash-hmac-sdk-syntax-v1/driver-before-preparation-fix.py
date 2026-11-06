"""Root-authorized registrar/COPY/BORROW SDK frontends; no crypto execution."""
from pathlib import Path
import hashlib,importlib.util,json,os,shlex,stat,sys
REPO=Path('/Users/dan/dev/StarlingMonkey')
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'node-crypto-hash-hmac-candidate-v1'
PEER=HERE.parent/'independent-node-crypto-hash-hmac-source-review-v1'
S=REPO/'tests/node-compat/foundation-scheduler'
BUILD=Path('/private/tmp/starling-node-compat/combined-native355-v2-build')
CONFIGURED=Path('/private/tmp/starling-node-compat/combined-native355-v1-source')
FROZEN=Path('/private/tmp/starling-node-compat/combined-native355-v2-freeze')
STAGE=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-sdk-syntax')
SDK=BUILD/'cache/wasi-sdk/85e6'
MONITOR=HERE.parent/'ownership-gc-build-controller-candidate-v1'
protected={}
def d(p):
 p=Path(p);h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return {'path':str(p),'sha256':h.hexdigest(),'bytes':p.stat().st_size}
def guard(row):
 p=Path(row['path']);assert p.is_file() and not p.is_symlink(),p
 assert d(p)=={k:row[k] for k in ['path','sha256','bytes']},p
 s=p.stat();protected[str(p)]={'sha256':row['sha256'],'bytes':row['bytes'],'mode':stat.S_IMODE(s.st_mode),'device':s.st_dev,'inode':s.st_ino,'nlink':s.st_nlink}
def j(p):return json.loads(Path(p).read_text())
def mkdir(p):
 p=Path(p);assert str(p).startswith(str(STAGE));missing=[];q=p
 while not q.exists():missing.append(q);q=q.parent
 for q in reversed(missing):q.mkdir(mode=0o700)
def write(p,b):
 p=Path(p);mkdir(p.parent)
 with p.open('xb') as f:os.chmod(p,0o600);f.write(b);f.flush();os.fsync(f.fileno())
def put(p,v):write(p,(json.dumps(v,indent=2)+'\n').encode())
def family(root,sha):
 row=d(root/'index.json');assert row['sha256']==sha;guard(row)
 for r in j(root/'index.json')['files']:guard({'path':str(root/r['path']),'sha256':r['sha256'],'bytes':r['bytes']})
 return row
def clean(command):
 words=shlex.split(command);driver=words.pop(0);kept=[];removed=[];main=None;i=0
 while i<len(words):
  token=words[i]
  if token in ['-o','-MF','-MT','-MQ','-MJ','--serialize-diagnostics']:
   removed.append(words[i:i+2]);i+=2;continue
  if token=='-c':main=words[i+1];removed.append(words[i:i+2]);i+=2;continue
  if token in ['-MD','-MMD','-MP','-MG','-M','-MM']:
   removed.append([token]);i+=1;continue
  assert not any(token.startswith(x) and token!=x for x in ['-MF','-MT','-MQ','-MJ'])
  kept.append(token);i+=1
 assert main and '--target=wasm32-wasi' in kept and '-O3' in kept and '-DNDEBUG' in kept and '-fno-exceptions' in kept
 assert not any(t.startswith(('-DDEBUG','-DNODE_COMPAT_OOM_TESTING','-DNODE_COMPAT_GC_STRESS')) for t in kept)
 return driver,kept,main,removed
def copied(row,destination):
 guard(row);write(destination,Path(row['path']).read_bytes());a=Path(row['path']).stat();b=destination.stat()
 assert (a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino) and d(destination)['sha256']==row['sha256']
 return {'original':row,'copy':d(destination),'distinctInode':True,'mode':stat.S_IMODE(b.st_mode)}
def main():
 assert sys.argv[1:]==['--execute-authorized-three-syntax-checks'] and not STAGE.exists()
 source_index=family(SOURCE,'afdbefde3b591a9ecb396355d0e16138f902866b0a7d70652c870a2bfe0cd3dc')
 peer_index=family(PEER,'1c23afafe24742a66d3816305317bb60a0ff8a94e915eafc8cc3944c82a47690')
 peer=j(PEER/'results.json');assert peer['sourceReviewPassed'] is True and peer['sourceIndexSha256']==source_index['sha256']
 assert peer['state']=='INDEPENDENT_NODE_CRYPTO_SHA256_HASH_HMAC_SOURCE_REVIEW_PASSED_V1' and peer['sourceOnly'] is True
 for row in j(SOURCE/'source-inputs.json')['files']:guard(row)
 monitor_index=family(MONITOR,'0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b')
 assert d(MONITOR/'monitor.py')['sha256']=='86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
 metadata_row=d(FROZEN/'normal-off.engine.wasm.build.json');assert metadata_row['sha256']=='5f3be8851739635beaee6550ad03c7afed9e6eebb0607840ebd12e4a095354d3';guard(metadata_row);m=j(metadata_row['path'])
 assert len(m)==80 and len(m['sourceManifest'])==355 and m['entropyPolicy']=='off' and m['gcStress'] is False and m['debuggerEnabled'] is False
 db_row=d(m['compileCommandsPath']);assert db_row['sha256']==m['compileCommandsSha256'];guard(db_row);db=j(db_row['path'])
 reg=next(r for r in db if r['file']==str(CONFIGURED/'builtins/node-compat/register.cpp'))
 web=next(r for r in db if r['file']==str(CONFIGURED/'builtins/web/crypto/crypto-algorithm.cpp'))
 wrapper=Path(shlex.split(reg['command'])[0]);guard(d(wrapper))
 compiler=SDK/'bin/clang++';assert str(compiler) in wrapper.read_text() and '"$@"' in wrapper.read_text()
 compiler_leaf=d(compiler.resolve());assert compiler_leaf['sha256']=='1aca933cc48d7e137804231e0ced1624052fe489562ab496d63ad9a23998c7fe';guard(compiler_leaf)
 # Derive the guest OpenSSL include from the actual selected WebCrypto target.
 web_driver,web_args,_,_=clean(web['command']);ssl=[]
 for i,token in enumerate(web_args):
  if token=='-isystem' and '/deps/OpenSSL-' in web_args[i+1]:ssl+=['-isystem',web_args[i+1]]
 assert len(ssl)==2 and ssl[1].startswith(str(BUILD)) and Path(ssl[1]).is_dir()
 ledger_path=S/'independent-combined355-native-build-v2-results-review-v1/input-hashes.json';ledger_row=d(ledger_path);assert ledger_row['sha256']=='c8e94c97cb6d2a9c8af42f4f41c46b1e3685672ad1542f4efffffbc76ff8e265';guard(ledger_row);ledger=j(ledger_path)['files']
 sdk_rows=[r for r in ledger if r['path'].startswith(str(SDK)+'/')]
 sm_rows=[r for r in ledger if r['path'].startswith(str(BUILD/'spidermonkey-dist-release/include')+'/')]
 ssl_rows=[r for r in ledger if r['path'].startswith(ssl[1]+'/')]
 assert len(sdk_rows)==10114 and sm_rows and ssl_rows
 for r in sdk_rows+sm_rows+ssl_rows:guard(r)
 aliases_path=ledger_path.parent/'reference-aliases.json';row=d(aliases_path);assert row['sha256']=='c8738493e6a4c4e802dd74af364e564225d70a63685c249090e18f6133fcc9f0';guard(row)
 aliases=[r for r in j(aliases_path)['symlinks'] if r['path'].startswith(str(SDK)+'/')]
 assert len(aliases)==31
 for a in aliases:
  p=Path(a['path']);assert p.is_symlink() and os.readlink(p)==a['linkText'] and str(p.resolve())==a['resolved']
 # Protect the WHOLE existing frozen tree, not just active afterimage origins.
 inv_path=S/'independent-combined355-native-freeze-v2-results-review-v1/frozen-copy-inventory.json';row=d(inv_path);assert row['sha256']=='788e04ee5682c31678dc87e5cfd7da88ebf37f8b2a4cd5d7eec22383ec697ff2';guard(row);inv=j(inv_path)
 assert len(inv['files'])==2596
 for r in inv['files']:
  guard(r['copy']);p=Path(r['copy']['path']);assert str(p).startswith(str(FROZEN)+'/') and stat.S_IMODE(p.stat().st_mode)==r['mode'] and p.stat().st_nlink==1
 receipt=d(FROZEN/'normal-off-freeze-receipt.json');assert receipt['sha256']=='9ce681402425f2bc59134bec5b48c98ee20fe15d42abf7ecaa1df920e05fded4';guard(receipt)
 actual_frozen={str(p) for p in FROZEN.rglob('*') if p.is_file()};assert actual_frozen=={r['copy']['path'] for r in inv['files']}|{receipt['path']}
 for r in m['sourceManifest']:
  p=CONFIGURED/r['path'];row=d(p);assert row['sha256']==r['sha256'];guard(row)
 embedding_command=m['actualEmbeddingCompileCommands'][0];_,_,input_embedding,_=clean(embedding_command);embedding_root=Path(input_embedding).parents[1]
 for r in m['componentizeSourceManifest']:
  row=d(embedding_root/r['path']);assert row['sha256']==r['sha256'];guard(row)
 changes=j(SOURCE/'integration-derivation.json');overrides={}
 for r in changes['files']:
  guard(r['base']);guard(r['afterimage']);relative=str(Path(r['base']['path']).relative_to(CONFIGURED));overrides[relative]=r['afterimage']
 assert set(overrides)=={'cmake/builtins.cmake','builtins/node-compat/register.cpp'}
 mkdir(STAGE);mkdir(STAGE/'tmp');copies=[];roots=[];source_rows=[]
 for r in m['sourceManifest']:
  origin=overrides.get(r['path'],d(FROZEN/'source'/r['path']));target=STAGE/'native'/r['path'];copies.append(copied(origin,target));roots.append({'type':'file','name':str(CONFIGURED/r['path']),'external-contents':str(target)});source_rows.append(r['path'])
 new=changes['newFilesToPlaceOnlyInFutureFreshSource'];assert len(new)==2
 for name,relative in new.items():
  assert relative not in source_rows;target=STAGE/'native'/relative;copies.append(copied(d(SOURCE/name),target));roots.append({'type':'file','name':str(CONFIGURED/relative),'external-contents':str(target)});source_rows.append(relative)
 assert len(source_rows)==357
 for relative in ['deps/include/picosha2.h','deps/include/rust-encoding.h','deps/include/wizer.h','runtime/sequence.hpp']:
  target=STAGE/'native'/relative;copies.append(copied(d(CONFIGURED/relative),target));roots.append({'type':'file','name':str(CONFIGURED/relative),'external-contents':str(target)})
 for r in m['componentizeSourceManifest']:
  target=STAGE/'external'/r['path'];copies.append(copied(d(FROZEN/'componentize-source'/r['path']),target));roots.append({'type':'file','name':str(embedding_root/r['path']),'external-contents':str(target)})
 assert len(copies)==364
 overlay=STAGE/'overlay.json';put(overlay,{'version':0,'case-sensitive':True,'use-external-names':False,'roots':roots})
 driver,base,_,removed=clean(reg['command']);assert driver==str(wrapper)
 assert '-DNODE_COMPAT_CRYPTO_HASH_HMAC=1' not in base and not any('NODE_CRYPTO_AUDITED_BORROW' in x for x in base)
 base=base+ssl+['-DNODE_COMPAT_CRYPTO_HASH_HMAC=1','-ivfsoverlay',str(overlay),'-fsyntax-only']
 plans=[]
 for ident,relative,borrow in [('register','builtins/node-compat/register.cpp',False),('kernel-copy','builtins/node-compat/hash-hmac-kernel.cpp',False),('kernel-borrow','builtins/node-compat/hash-hmac-kernel.cpp',True)]:
  input_path=STAGE/'native'/relative;assert input_path.is_file()
  deps=STAGE/(ident+'.d');argv=[str(compiler),*base,*(['-DNODE_CRYPTO_AUDITED_BORROW=1'] if borrow else []),'-MD','-MF',str(deps),'-MT','syntax-only-'+ident,str(input_path)]
  assert '-c' not in argv and '-o' not in argv and argv.count('-fsyntax-only')==1
  plans.append({'id':ident,'argv':argv,'cwd':str(STAGE),'actualMainInput':d(input_path),'newKernelCommandProspectiveNotObservedCmakeRow':ident!='register','registrarAlsoAddsFutureTargetGuestOpenSSLInclude':True,'borrowMacro':1 if borrow else 'absent; source default0','dependencyFile':str(deps),'timeoutSeconds':60})
 env={'PATH':str(SDK/'bin')+':/usr/bin:/bin','LC_ALL':'C','LANG':'C','TMPDIR':str(STAGE/'tmp')}
 for k in ['HOME','home','CODEX_HOME']:
  if k in os.environ:env[k]=os.environ[k]
 authority={'scope':'Root-authorized three SDK syntax-only checks register/COPY/BORROW; no algorithm/provider/key/engine execution','sourceIndex':source_index,'sourcePeerIndex':peer_index,'nativeBuildLinkRuntimeAllowed':False}
 put(STAGE/'plan.json',{'schemaVersion':1,'authority':authority,'compilerAlias':str(compiler),'compilerLeaf':compiler_leaf,'originalWrapperReadNotExecuted':d(wrapper),'metadata':metadata_row,'compileDatabase':db_row,'baseRegistrarRow':reg,'actualWebCryptoRowForGuestOpenSSL':web,'guestOpenSSLIncludeArguments':ssl,'removedOriginalRegistrarOutputs':removed,'sdkFilesAuthenticated':len(sdk_rows),'smHeadersAuthenticated':len(sm_rows),'guestOpenSSLHeadersAuthenticated':len(ssl_rows),'sdkAliases':aliases,'sourceFiles':357,'externalEmbeddingSources':3,'configuredExtraHeaders':4,'copies':copies,'overlay':d(overlay),'commands':plans,'environment':{k:v for k,v in env.items() if k not in ['HOME','home','CODEX_HOME']},'preservedUserEnvironmentNames':[k for k in ['HOME','home','CODEX_HOME'] if k in env],'frozenMembershipFilesProtected':len(actual_frozen)})
 put(STAGE/'protection-before.json',{'schemaVersion':1,'files':protected,'allFrozenTreeFiles':2597,'allConfiguredNativeFiles':355,'allConfiguredEmbeddingFiles':3,'sdkAliases':31})
 for directory in [STAGE,*[p for p in STAGE.rglob('*') if p.is_dir()]]:
  fd=os.open(directory,os.O_RDONLY);os.fsync(fd);os.close(fd)
 spec=importlib.util.spec_from_file_location('genuine_hash_hmac_syntax_owned_monitor',MONITOR/'monitor.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 outcomes=[]
 try:
  for plan in plans:
   out=STAGE/'commands'/plan['id'];mkdir(out);t=module.monitor(plan['argv'],plan['cwd'],env,out,60,authority)
   outcomes.append({'id':plan['id'],'rawExitCode':t['rawExitCode'],'terminal':d(out/'terminal.json')})
   assert t['allObservedOwnedGroupsGone'] and not t['forcedCleanup'] and not t['timeout'] and not t['signals'] and not t['errors'] and not t['remainingObservedPids']
 finally:
  for path,r in protected.items():
   p=Path(path);s=p.stat();assert d(p)['sha256']==r['sha256'] and s.st_size==r['bytes'];assert (stat.S_IMODE(s.st_mode),s.st_dev,s.st_ino,s.st_nlink)==(r['mode'],r['device'],r['inode'],r['nlink']),path
  for a in aliases:
   p=Path(a['path']);assert os.readlink(p)==a['linkText'] and str(p.resolve())==a['resolved']
  assert {str(p) for p in FROZEN.rglob('*') if p.is_file()}==actual_frozen
  put(STAGE/'protection-final.json',{'schemaVersion':1,'unchangedFiles':len(protected),'allHashesModesInodesLinksUnchanged':True,'sdkAliasesUnchanged':31,'wholeFrozenMembershipUnchanged':True})
 result={'schemaVersion':1,'state':'HASH_HMAC_SDK_FRONTEND_SYNTAX_PASSED' if len(outcomes)==3 and all(r['rawExitCode']==0 for r in outcomes) else 'HASH_HMAC_SDK_FRONTEND_ERRORS_PRESERVED','sourceIndex':source_index,'sourcePeerIndex':peer_index,'outcomes':outcomes,'onlySyntaxFrontendRequested':True,'cryptoProviderKeyGuestOrEngineExecuted':False,'codegenOrLinkOrNativeBuildRequested':False,'snapshotGcZeroizationOrAdoptionSafetyProved':False}
 put(STAGE/'result.json',result);print(json.dumps(result),flush=True)
 if len(outcomes)!=3 or any(r['rawExitCode']!=0 for r in outcomes):sys.exit(1)
if __name__=='__main__':main()
