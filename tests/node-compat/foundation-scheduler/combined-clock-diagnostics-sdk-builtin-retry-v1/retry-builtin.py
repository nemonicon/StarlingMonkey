"""Explicit Root follow-up: only the previously unentered builtin frontend."""
from pathlib import Path
import hashlib,importlib.util,json,os,stat,sys
HERE=Path(__file__).resolve().parent
FIRST=Path('/private/tmp/starling-node-compat/combined-clock-diagnostics-v1-sdk-syntax')
OUT=Path('/private/tmp/starling-node-compat/combined-clock-diagnostics-v1-sdk-syntax-builtin-retry')
REPO=Path('/Users/dan/dev/StarlingMonkey')
MONITOR=REPO/'tests/node-compat/foundation-crypto/ownership-gc-build-controller-candidate-v1'
FROZEN=Path('/private/tmp/starling-node-compat/combined-native355-v2-freeze')
CONFIGURED=Path('/private/tmp/starling-node-compat/combined-native355-v1-source')
protected={}
def d(p):
 p=Path(p);h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return {'path':str(p),'sha256':h.hexdigest(),'bytes':p.stat().st_size}
def guard(row):
 p=Path(row['path']);assert p.is_file() and not p.is_symlink() and d(p)=={k:row[k] for k in ['path','sha256','bytes']}
 s=p.stat();protected[str(p)]={**row,'mode':stat.S_IMODE(s.st_mode),'device':s.st_dev,'inode':s.st_ino,'nlink':s.st_nlink}
def j(p):return json.loads(Path(p).read_text())
def put(p,v):
 with p.open('x') as f:os.chmod(p,0o600);json.dump(v,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def main():
 assert sys.argv[1:]==['--execute-only-authorized-builtin-retry'] and not OUT.exists()
 first_packet=HERE.parent/'combined-clock-diagnostics-sdk-syntax-v1'
 first_index=d(first_packet/'index.json');assert first_index['sha256']=='29815de8f625ebacea266ef5a98c253ab9644f35a958c70b8d8373935d5cd256';guard(first_index)
 for r in j(first_packet/'index.json')['files']:guard({'path':str(first_packet/r['path']),'sha256':r['sha256'],'bytes':r['bytes']})
 first_result=j(first_packet/'results.json')
 for key in ['actualResult','actualPlan','originalProtectionBefore','originalProtectionFinal']:guard(first_result[key])
 original=j(FIRST/'original-protection-before.json')['files']
 for path,r in original.items():
  guard({'path':path,'sha256':r['sha256'],'bytes':r['bytes']});s=Path(path).stat()
  assert (stat.S_IMODE(s.st_mode),s.st_dev,s.st_ino,s.st_nlink)==(r['mode'],r['device'],r['inode'],r['nlink'])
 plan=j(FIRST/'plan.json');aliases=plan['sdkAliases']
 for a in aliases:
  p=Path(a['path']);assert p.is_symlink() and os.readlink(p)==a['linkText'] and str(p.resolve())==a['resolved']
 guard(plan['privateOverlay'])
 for r in plan['copies']:guard(r['copy'])
 source_index=plan['authority']['sourceIndex'];guard(source_index);assert source_index['sha256']=='7aed33ec02b9024fb96ded8e77924a27ce7d54bf36102a5fd561a3e88f731e52'
 metadata=j(FROZEN/'normal-off.engine.wasm.build.json')
 for r in metadata['sourceManifest']:
  for root in [FROZEN/'source',CONFIGURED]:
   row=d(root/r['path']);assert row['sha256']==r['sha256'];guard(row)
 embedding_plan=next(r for r in plan['commands'] if r['id']=='embedding');embedding_root=Path(embedding_plan['argv'][-1]).parents[1]
 for r in metadata['componentizeSourceManifest']:
  for root in [FROZEN/'componentize-source',embedding_root]:
   row=d(root/r['path']);assert row['sha256']==r['sha256'];guard(row)
 for name,sha in [('normal-off.engine.wasm','355550f1d0bdc7455fd81ffbd739ac1453a56f3537b277eb644441d87434af3b'),('normal-off.engine.wasm.build.json','5f3be8851739635beaee6550ad03c7afed9e6eebb0607840ebd12e4a095354d3'),('normal-off-freeze-receipt.json','9ce681402425f2bc59134bec5b48c98ee20fe15d42abf7ecaa1df920e05fded4')]:
  row=d(FROZEN/name);assert row['sha256']==sha;guard(row)
 monitor_index=d(MONITOR/'index.json');assert monitor_index['sha256']=='0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b';guard(monitor_index)
 for r in j(MONITOR/'index.json')['files']:guard({'path':str(MONITOR/r['path']),'sha256':r['sha256'],'bytes':r['bytes']})
 assert d(MONITOR/'monitor.py')['sha256']=='86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'
 old=next(r for r in plan['commands'] if r['id']=='private-builtin');argv=old['argv'][:]
 virtual=argv[-1];mapped=next(r['external-contents'] for r in j(FIRST/'overlay.json')['roots'] if r['name']==virtual)
 assert Path(mapped).is_file();argv[-1]=mapped
 OUT.mkdir(mode=0o700);(OUT/'tmp').mkdir(mode=0o700);(OUT/'command').mkdir(mode=0o700)
 argv[argv.index('-MF')+1]=str(OUT/'headers.d')
 assert argv[:-1]!=old['argv'][:-1] and '-c' not in argv and '-o' not in argv and '-fsyntax-only' in argv
 # Only main input and private dependency sink differ; no Source, SDK, macro,
 # include, target, optimization, exception or VFS option changes.
 old_normal=old['argv'][:];new_normal=argv[:]
 for x in [old_normal,new_normal]:x[x.index('-MF')+1]='PRIVATE_DEPENDENCY_SINK';x[-1]='PRIVATE_CPP_MAIN_INPUT'
 assert old_normal==new_normal
 env={**plan['environment'],'TMPDIR':str(OUT/'tmp')}
 for k in ['HOME','home','CODEX_HOME']:
  if k in os.environ:env[k]=os.environ[k]
 authority={'scope':'Root-authorized ONLY builtin syntax retry after preserved Clang driver path refusal','sourceIndex':source_index,'parentFirstAttemptIndex':first_index,'fourPassedUnitsRerun':False,'nativeBuildLinkEngineGuestAllowed':False}
 put(OUT/'command.json',{'schemaVersion':1,'argv':argv,'cwd':str(OUT),'originalFailedCommand':old,'existingStagedMainInput':d(Path(mapped)),'sameVirtualOverlay':d(FIRST/'overlay.json'),'compilerLeaf':plan['compilerLeaf'],'argumentChangesOnlyMainInputAndPrivateDependencySink':True,'freshCwdAndTmpRoot':True,'authority':authority})
 put(OUT/'original-protection-before.json',{'schemaVersion':1,'files':protected,'originalFirstGuardRows':len(original),'sameSourceCopiesRehashed':len(plan['copies']),'additionalConfiguredAndFrozenParentProtection':True})
 spec=importlib.util.spec_from_file_location('genuine_retry_owned_monitor',MONITOR/'monitor.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 terminal=None
 try:terminal=module.monitor(argv,str(OUT),env,OUT/'command',60,authority)
 finally:
  for path,r in protected.items():
   p=Path(path);s=p.stat();assert d(p)['sha256']==r['sha256'] and s.st_size==r['bytes']
   assert (stat.S_IMODE(s.st_mode),s.st_dev,s.st_ino,s.st_nlink)==(r['mode'],r['device'],r['inode'],r['nlink'])
  for a in aliases:
   p=Path(a['path']);assert os.readlink(p)==a['linkText'] and str(p.resolve())==a['resolved']
  put(OUT/'original-protection-final.json',{'schemaVersion':1,'unchangedFiles':len(protected),'allHashesModesInodesLinksUnchanged':True,'unchangedSdkAliases':len(aliases)})
 assert terminal and terminal['allObservedOwnedGroupsGone'] and not terminal['forcedCleanup'] and not terminal['timeout'] and not terminal['signals'] and not terminal['errors']
 result={'schemaVersion':1,'state':'BUILTIN_FRONTEND_SYNTAX_PASSED' if terminal['rawExitCode']==0 else 'BUILTIN_FRONTEND_CPP_ERROR_PRESERVED','rawExitCode':terminal['rawExitCode'],'terminal':d(OUT/'command/terminal.json'),'sourceIndex':source_index,'otherFourUnitsRerun':False,'originalsUnchanged':True,'noObjectLinkBuildRuntimeClaim':True}
 put(OUT/'result.json',result);print(json.dumps(result),flush=True)
 if terminal['rawExitCode']!=0:sys.exit(1)
if __name__=='__main__':main()
