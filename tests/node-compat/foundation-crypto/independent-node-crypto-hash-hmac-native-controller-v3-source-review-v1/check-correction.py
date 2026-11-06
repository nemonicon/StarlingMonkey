"""Read-only exact derivations and retained tiny filesystem regression DATA."""
from pathlib import Path
import ast,hashlib,json,stat
P=Path(__file__).resolve().parent;S=P.parent/'node-crypto-hash-hmac-native-controller-candidate-v3';count=0
def yes(x,m='correction'):
 global count
 count+=1;assert x,m
def row(p):p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def check(r):yes(row(r['path'])==r);return Path(r['path'])
d=json.loads((S/'derivations.json').read_bytes());yes(len(d['files'])==22 and d['nativeSourceFilesChanged']==0)
for f in d['files']:
 before=check(f['donor']).read_text();after=check(f['after']).read_text();yes(Path(f['after']['path'])==S/f['output']);a=[];b=[];left=0;right=0
 for e in f['edits']:
  x=e['beforeOffset'];y=e['afterOffset'];yes(x>=left and y>=right);yes(before[x:x+len(e['before'])]==e['before']);yes(after[y:y+len(e['after'])]==e['after']);a.extend([before[left:x],e['after']]);b.extend([after[right:y],e['before']]);left=x+len(e['before']);right=y+len(e['after'])
 a.append(before[left:]);b.append(after[right:]);yes(''.join(a)==after and ''.join(b)==before,'full forward/inverse '+f['output']);yes(f['byteIdentical']==(before==after))
yes(sum(len(f['edits'])for f in d['files'])==14)
refs=json.loads((S/'references.json').read_bytes());old=json.loads(Path(json.loads((S/'api-provenance.json').read_bytes())['producerOriginals']['policy.json']['path']).read_bytes());new=json.loads(check(refs['policy']).read_bytes());expected=json.loads(json.dumps(old));expected['contexts']['workRoot']=refs['workRoot'];expected['contexts']['freezeRoot']=refs['freezeRoot'];yes(new==expected,'policy only two context leaves; no native manifest/flag change')
for key in ['expectedNativeSourceManifest','expectedComponentizeSourceManifest','selectedModuleManifests','selectedManifestValues']:yes(new[key]==old[key],key)
recipe=check(refs['recipe']).read_text();helper=check(refs['helper']).read_text();yes('recipe_path' in recipe and str(S/'producer/build-engine.sh')in recipe);yes('[[ "$work_root" == "'+refs['workRoot']+'" ]]'in recipe);yes('consumers_layer_root="'+str(S/'producer')+'"'in recipe);yes(refs['helper']['sha256']in recipe);yes("HERE==Path('"+str(S/'producer')+"')"in helper and "REPO=Path('"+refs['configuredSourceRoot']+"')"in helper);yes(new==json.loads((S/'producer/policy.json').read_bytes())and refs['policy']['sha256']in helper)
body=ast.parse((S/'build_body.py').read_bytes());fn=next(x for x in body.body if isinstance(x,ast.FunctionDef)and x.name=='populate_cache');calls=[x for x in ast.walk(fn)if isinstance(x,ast.Call)and isinstance(x.func,ast.Attribute)];fchmod=[x for x in calls if x.func.attr=='fchmod'];yes(len(fchmod)==1 and isinstance(fchmod[0].args[0],ast.Name)and fchmod[0].args[0].id=='fd');yes(not any(x.func.attr=='chmod'for x in calls));text=(S/'build_body.py').read_text();yes('dst.flush();os.fchmod(fd,r[\'outputMode\']);os.fsync(fd)'in text,'held fd correction order')
benign=json.loads((S/'benign-copy-test-results.json').read_bytes());root=Path(benign['scratchRoot']);yes(benign['umaskDuringCopies']=='077'and benign['actualBenignFilesystemCopiesInvoked']and not benign['actualNativeCacheCopiesInvoked']);cases=benign['cases'];yes(len(cases)==5)
first=cases[0];p=check(first['partialFile']);yes(stat.S_IMODE(p.stat().st_mode)==first['actualMode']==0o600 and first['completedCopies']==0)
yes(not(root/'old-work/executable').exists());newcase=cases[1];yes(newcase['bothModesExact']and newcase['bothDistinctSingleLinks'])
for n,r in enumerate(newcase['copies'],1):
 a=check(r['source']);b=check(r['target']);yes(a.read_bytes()==b.read_bytes());yes(stat.S_IMODE(a.stat().st_mode)==r['sourceMode']and stat.S_IMODE(b.stat().st_mode)==r['outputMode']);yes(a.stat().st_ino!=b.stat().st_ino and b.stat().st_nlink==1);yes(json.loads((root/'new-output'/('cache-copy-'+str(n)+'.json')).read_bytes())==r)
yes((root/'receipt-failure-output/cache-copy-1.json').read_bytes()==b'KEEP_EXISTING_RECEIPT\n');yes(not(root/'receipt-failure-work/executable').exists());check(cases[2]['partialFile']);yes((root/'preexisting-work/keep').read_bytes()==b'KEEP\n'and not(root/'preexisting-work/readable').exists());partial=check(cases[4]['partialFile']);source=check(newcase['copies'][0]['source']);yes(0<len(partial.read_bytes())<len(source.read_bytes())and source.read_bytes().startswith(partial.read_bytes()))
allFiles=[];ids=set()
for p in sorted(root.rglob('*')):
 yes(not p.is_symlink())
 if p.is_file():
  st=p.stat();yes(st.st_nlink==1 and(st.st_dev,st.st_ino)not in ids);ids.add((st.st_dev,st.st_ino));allFiles.append(dict(file=row(p),mode=stat.S_IMODE(st.st_mode),inode=st.st_ino,device=st.st_dev,nlink=st.st_nlink))
 else:yes(p.is_dir()and stat.S_IMODE(p.stat().st_mode)==0o700)
yes(len(allFiles)==11)
failed=json.loads((S/'failed-v1-protection.json').read_bytes())
for t in failed['trees']:
 root=Path(t['root']);yes(stat.S_IMODE(root.stat().st_mode)==t['mode']);yes({str(p)for p in root.rglob('*')if p.is_file()}=={r['file']['path']for r in t['files']})
 for r in t['files']:p=check(r['file']);yes(stat.S_IMODE(p.stat().st_mode)==r['mode']and p.stat().st_nlink==r['nlink'])
for p in failed['absentRoots']:yes(not Path(p).exists())
value=dict(schemaVersion=1,passed=True,checks=count,exactForwardInverseFiles=22,editCapsules=14,nativeSourceChanges=0,policyChangesOnlyWorkAndFreeze=True,heldExclusiveFdFchmodBeforeFsyncVerified=True,actualBenignCases=5,retainedBenignFiles=allFiles,failedOldTreesPreserved=len(failed['trees']),benignEvidenceQualification='Authenticated retained test source/outcome and current tiny scratch bytes/modes/inodes, not new syscall trace or native cache/build execution',ownerOrProducerOrCacheActionsInvoked=False)
(P/'correction-review.json').write_text(json.dumps(value,indent=2)+'\n');print(json.dumps({k:value[k]for k in ['passed','checks','exactForwardInverseFiles','editCapsules','actualBenignCases','nativeSourceChanges']}))
