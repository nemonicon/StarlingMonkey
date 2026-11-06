"""Root-authorized five SDK frontends only; preserve first attempt, never retry."""
from pathlib import Path
import hashlib, importlib.util, json, os, shlex, stat, sys

REPO=Path('/Users/dan/dev/StarlingMonkey')
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'combined-clock-diagnostics-candidate-v1'
STAGE=Path('/private/tmp/starling-node-compat/combined-clock-diagnostics-v1-sdk-syntax')
BUILD=Path('/private/tmp/starling-node-compat/combined-native355-v2-build')
CONFIGURED=Path('/private/tmp/starling-node-compat/combined-native355-v1-source')
FROZEN=Path('/private/tmp/starling-node-compat/combined-native355-v2-freeze')
PEER=HERE.parent/'independent-combined355-native-build-v2-results-review-v1'
MONITOR=REPO/'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1'
SDK=BUILD/'cache/wasi-sdk/85e6'
protected={}

def descriptor(p):
 p=Path(p);h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return {'path':str(p),'sha256':h.hexdigest(),'bytes':p.stat().st_size}
def verify(row,protect=True):
 p=Path(row['path']);assert p.is_absolute() and p.is_file() and not p.is_symlink(),p
 assert descriptor(p)=={k:row[k] for k in ['path','sha256','bytes']},p
 if protect:
  s=p.stat();protected[str(p)]={'mode':stat.S_IMODE(s.st_mode),'device':s.st_dev,'inode':s.st_ino,'nlink':s.st_nlink,'sha256':row['sha256'],'bytes':row['bytes']}
 return p
def read(row):return json.loads(verify(row).read_bytes())
def mkdir(p):
 p=Path(p);assert str(p).startswith(str(STAGE))
 missing=[];q=p
 while not q.exists():missing.append(q);q=q.parent
 for q in reversed(missing):q.mkdir(mode=0o700)
def write(p,raw):
 p=Path(p);mkdir(p.parent)
 with p.open('xb') as f:os.chmod(p,0o600);f.write(raw);f.flush();os.fsync(f.fileno())
def put(p,v):write(p,(json.dumps(v,indent=2)+'\n').encode())
def copy(row,destination):
 original=verify(row);write(destination,original.read_bytes());assert descriptor(destination)['sha256']==row['sha256']
 a,b=original.stat(),destination.stat();assert (a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino)
 return {'original':row,'copy':descriptor(destination),'distinctInode':True,'mode':stat.S_IMODE(b.st_mode)}
def family(directory,sha):
 row=descriptor(directory/'index.json');assert row['sha256']==sha
 index=read(row)
 for f in index['files']:verify({'path':str(directory/f['path']),'sha256':f['sha256'],'bytes':f['bytes']})
 return row
def clean_arguments(command):
 words=shlex.split(command);declared=words.pop(0);kept=[];removed=[];source=None;i=0
 with_value={'-o','-MF','-MT','-MQ','-MJ','--serialize-diagnostics'}
 singleton={'-MD','-MMD','-MP','-MG','-M','-MM','-fsyntax-only'}
 while i<len(words):
  w=words[i]
  if w in with_value:removed.append(words[i:i+2]);i+=2;continue
  if w=='-c':source=words[i+1];removed.append(words[i:i+2]);i+=2;continue
  if w in singleton:removed.append([w]);i+=1;continue
  assert not any(w.startswith(prefix) and w!=prefix for prefix in ['-MF','-MT','-MQ','-MJ']),w
  kept.append(w);i+=1
 assert source and '-o' not in kept and '-c' not in kept
 assert '--target=wasm32-wasi' in kept and '-DNDEBUG' in kept and '-O3' in kept and '-fno-exceptions' in kept
 assert not any(x.startswith(('-DDEBUG','-DNODE_COMPAT_GC_STRESS','-DNODE_COMPAT_OOM_TESTING')) for x in kept)
 return declared,kept,source,removed

def main():
 assert sys.argv[1:]==['--execute-authorized-five-frontends']
 assert not STAGE.exists(),'Preserve the first attempt; a retry requires a fresh Root authorization/namespace'
 source_index=family(SOURCE,'7aed33ec02b9024fb96ded8e77924a27ce7d54bf36102a5fd561a3e88f731e52')
 monitor_index=family(MONITOR,'0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b')
 monitor_row=descriptor(MONITOR/'monitor.py');assert monitor_row['sha256']=='86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
 metadata_row=descriptor(FROZEN/'normal-off.engine.wasm.build.json');assert metadata_row['sha256']=='5f3be8851739635beaee6550ad03c7afed9e6eebb0607840ebd12e4a095354d3'
 metadata=read(metadata_row);db_row=descriptor(metadata['compileCommandsPath']);assert db_row['sha256']==metadata['compileCommandsSha256'];db=read(db_row)
 ledger_row=descriptor(PEER/'input-hashes.json');assert ledger_row['sha256']=='c8e94c97cb6d2a9c8af42f4f41c46b1e3685672ad1542f4efffffbc76ff8e265';ledger=read(ledger_row)['files']
 sdk_rows=[r for r in ledger if r['path'].startswith(str(SDK)+'/')]
 sm_rows=[r for r in ledger if r['path'].startswith(str(BUILD/'spidermonkey-dist-release/include')+'/')]
 assert len(sdk_rows)==10114 and sm_rows
 for row in sdk_rows+sm_rows:verify(row)
 alias_row=descriptor(PEER/'reference-aliases.json');assert alias_row['sha256']=='c8738493e6a4c4e802dd74af364e564225d70a63685c249090e18f6133fcc9f0'
 aliases=[r for r in read(alias_row)['symlinks'] if r['path'].startswith(str(SDK)+'/')]
 for a in aliases:
  p=Path(a['path']);assert p.is_symlink() and os.readlink(p)==a['linkText'] and str(p.resolve())==a['resolved']
 compiler=SDK/'bin/clang++';leaf=compiler.resolve();compiler_row=descriptor(leaf)
 assert compiler_row['sha256']=='1aca933cc48d7e137804231e0ced1624052fe489562ab496d63ad9a23998c7fe'
 assert any(a['path']==str(compiler) for a in aliases);verify(compiler_row)
 base_timer=next(r for r in db if r['file']==str(CONFIGURED/'builtins/web/timers.cpp'))
 wrapper=Path(shlex.split(base_timer['command'])[0]);wrapper_row=descriptor(wrapper);verify(wrapper_row)
 assert str(compiler) in wrapper.read_text() and '"$@"' in wrapper.read_text()
 inventory=read(descriptor(SOURCE/'proposed-source-inventory.json'))
 mkdir(STAGE);mkdir(STAGE/'tmp');copies=[];roots=[]
 for r in inventory['native']:
  target=STAGE/'native'/r['path'];copies.append(copy(r['origin'],target))
  roots.append({'type':'file','name':str(CONFIGURED/r['path']),'external-contents':str(target)})
 assert len(copies)==357
 # These genuine configured headers are outside the355 Source inventory.
 configured=[]
 for relative in ['deps/include/picosha2.h','deps/include/rust-encoding.h','deps/include/wizer.h','runtime/sequence.hpp']:
  p=CONFIGURED/relative;row=descriptor(p);configured.append(row);target=STAGE/'native'/relative
  copies.append(copy(row,target));roots.append({'type':'file','name':str(p),'external-contents':str(target)})
 embedding_command=metadata['actualEmbeddingCompileCommands'];assert len(embedding_command)==1
 declared,args,embedding_source,removed=clean_arguments(embedding_command[0]);assert declared==str(compiler)
 embedding_root=Path(embedding_source).parents[1]
 for r in inventory['externalEmbedding']:
  target=STAGE/'external'/r['path'];copies.append(copy(r['origin'],target))
  roots.append({'type':'file','name':str(embedding_root/r['path']),'external-contents':str(target)})
 assert len(copies)==364 and len(roots)==364
 overlay=STAGE/'overlay.json';put(overlay,{'version':0,'case-sensitive':True,'use-external-names':False,'roots':roots})
 for directory in [STAGE,*[p for p in STAGE.rglob('*') if p.is_dir()]]:
  fd=os.open(directory,os.O_RDONLY);os.fsync(fd);os.close(fd)
 environment={'PATH':str(SDK/'bin')+':/usr/bin:/bin','LC_ALL':'C','LANG':'C','TMPDIR':str(STAGE/'tmp')}
 for k in ['HOME','home','CODEX_HOME']:
  if k in os.environ:environment[k]=os.environ[k]
 plans=[]
 selections=[('event-loop','runtime/event_loop.cpp'),('timers','builtins/web/timers.cpp'),('host-api','host-apis/wasi-0.2.0/host_api.cpp'),('private-builtin','builtins/diagnostics/clock-lifecycle.cpp'),('embedding',None)]
 for ident,relative in selections:
  if ident=='embedding':base=embedding_command[0];original_row=None
  else:
   suffix='builtins/web/timers.cpp' if ident=='private-builtin' else relative
   matches=[r for r in db if r['file']==str(CONFIGURED/suffix)];assert len(matches)==1;original_row=matches[0];base=original_row['command']
  driver,arguments,input_file,stripped=clean_arguments(base)
  assert driver in [str(wrapper),str(compiler)]
  if ident=='private-builtin':input_file=str(CONFIGURED/relative)
  deps=STAGE/'dependencies'/(ident+'.d');mkdir(deps.parent)
  argv=[str(compiler),*arguments,'-DNODE_COMPAT_LIFECYCLE_DIAGNOSTICS=1','-ivfsoverlay',str(overlay),'-fsyntax-only','-MD','-MF',str(deps),'-MT','syntax-only-'+ident,input_file]
  assert argv.count('-fsyntax-only')==1 and '-o' not in argv and '-c' not in argv
  plans.append({'id':ident,'originalCommand':base,'originalCompileDbRow':original_row,'newBuiltinIsProspectiveSyntaxCommandNotObservedDbRow':ident=='private-builtin','argv':argv,'cwd':str(STAGE),'strippedOriginalWritableArguments':stripped,'dependencyFile':str(deps),'timeoutSeconds':60})
 authority={'scope':'Root-authorized SDK syntax-only five frontends','sourceIndex':source_index,'monitorIndex':monitor_index,'nativeBuildOrLinkOrEngineOrGuestAllowed':False}
 put(STAGE/'plan.json',{'schemaVersion':1,'authority':authority,'compilerAlias':str(compiler),'compilerLeaf':compiler_row,'wrapperReadButNotExecuted':wrapper_row,'actualCompileDb':db_row,'actualMetadata':metadata_row,'reviewedInputLedger':ledger_row,'sdkRowsRehashed':len(sdk_rows),'smHeaderRowsRehashed':len(sm_rows),'configuredHeadersMeasuredNow':configured,'sdkAliases':aliases,'privateOverlay':descriptor(overlay),'copies':copies,'commands':plans,'environment':{k:v for k,v in environment.items() if k not in ['HOME','home','CODEX_HOME']},'preservedUserEnvironmentNames':[k for k in ['HOME','home','CODEX_HOME'] if k in environment]})
 put(STAGE/'original-protection-before.json',{'schemaVersion':1,'files':protected,'scope':'Current input files only; reused BUILD ledger remains external, no historical proof trees copied.'})
 # Inert stdlib-only import AFTER complete source/SDK/command authentication.
 spec=importlib.util.spec_from_file_location('authenticated_sdk_owned_monitor',MONITOR/'monitor.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 terminals=[]
 try:
  for plan in plans:
   out=STAGE/'commands'/plan['id'];mkdir(out)
   terminal=module.monitor(plan['argv'],plan['cwd'],environment,out,60,authority)
   terminals.append({'id':plan['id'],'terminal':descriptor(out/'terminal.json'),'rawExitCode':terminal['rawExitCode']})
   assert terminal['allObservedOwnedGroupsGone'] and not terminal['forcedCleanup'] and not terminal['signals'] and not terminal['timeout'] and not terminal['errors'] and not terminal['remainingObservedPids'],'Owned compiler cleanup failed; no further commands'
 finally:
  for path,before in protected.items():
   p=Path(path);s=p.stat();assert descriptor(p)['sha256']==before['sha256'] and s.st_size==before['bytes']
   assert (stat.S_IMODE(s.st_mode),s.st_dev,s.st_ino,s.st_nlink)==(before['mode'],before['device'],before['inode'],before['nlink']),path
  for a in aliases:
   p=Path(a['path']);assert os.readlink(p)==a['linkText'] and str(p.resolve())==a['resolved']
  put(STAGE/'original-protection-final.json',{'schemaVersion':1,'unchangedFiles':len(protected),'allHashesModesInodesLinksUnchanged':True,'sdkAliasesUnchanged':len(aliases),'noOriginalOutputFlagsUsed':True})
 put(STAGE/'result.json',{'schemaVersion':1,'state':'SDK_FRONTEND_SYNTAX_ONLY_ALL_PASSED' if len(terminals)==5 and all(t['rawExitCode']==0 for t in terminals) else 'SDK_FRONTEND_SYNTAX_FAILURE_PRESERVED','sourceIndex':source_index,'commands':terminals,'units':len(terminals),'compilerOnly':True,'noObjectOrLinkRequested':True,'originalsUnchanged':True,'nativeAbiLinkAdmissionRuntimeProved':False})
 print(json.dumps(json.loads((STAGE/'result.json').read_text())),flush=True)
 if len(terminals)!=5 or any(t['rawExitCode']!=0 for t in terminals):sys.exit(1)

if __name__=='__main__':main()
