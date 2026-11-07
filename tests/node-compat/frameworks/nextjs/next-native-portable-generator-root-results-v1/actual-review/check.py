"""Portable DATA only; no generator/admission/tool/process imports or calls."""
from pathlib import Path
import base64
import gzip
import hashlib
import json
import stat
import sys
HERE=Path(__file__).resolve().parent
RESULT_SHA='f9e63c0455fb292e1c04ce2315f7680f58be3030c4df523c5b850eebee151b86'
def sha(b):return hashlib.sha256(b).hexdigest()
def row(path):
 p=Path(path);s=p.lstat();assert p.resolve()==p and stat.S_ISREG(s.st_mode)and s.st_nlink==1
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024**2),b''):h.update(b)
 t=p.lstat();assert(s.st_dev,s.st_ino,s.st_size,s.st_mode,s.st_mtime_ns,s.st_ctime_ns)==(t.st_dev,t.st_ino,t.st_size,t.st_mode,t.st_mtime_ns,t.st_ctime_ns)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=s.st_size)
def physical(p):
 s=Path(p).lstat();return dict(path=str(p),dev=s.st_dev,ino=s.st_ino,nlink=s.st_nlink,mode=stat.S_IMODE(s.st_mode),bytes=s.st_size,mtimeNs=s.st_mtime_ns,ctimeNs=s.st_ctime_ns)
def current(result,selection,families):
 root=Path(selection['sourceRoot']).parent;files={};dirs=[]
 for r in result['wholePortableBefore']:
  q=Path(r['path']);assert not q.is_symlink()and physical(q)==r;files[str(q.relative_to(root))]=row(q)
 for r in result['portableDirectoriesBefore']:
  q=Path(r['path']);s=q.lstat();assert q.resolve()==q and q.is_dir()and not q.is_symlink()
  assert dict(path=str(q),mode=stat.S_IMODE(s.st_mode),dev=s.st_dev,ino=s.st_ino,nlink=s.st_nlink,mtimeNs=s.st_mtime_ns,ctimeNs=s.st_ctime_ns)==r;dirs.append(str(q.relative_to(root)))
 nodes=list(root.rglob('*'));assert not any(q.is_symlink()for q in nodes)
 assert {str(q.relative_to(root))for q in nodes if q.is_file()}==set(files)|{'composition.json','source-materialization.json'}
 assert {'.'}|{str(q.relative_to(root))for q in nodes if q.is_dir()}==set(dirs)
 for record in result['toolInputsBefore']:
  q=Path(record['path']);s=q.lstat();assert physical(q)=={k:record[k]for k in ['path','dev','ino','nlink','mode','bytes','mtimeNs','ctimeNs']}
  assert row(q)=={k:record[k]for k in ['path','sha256','bytes']}
 for f in families:
  assert row(f['index']['path'])==f['index'];base=Path(f['index']['path']).parent;index=json.loads(base.joinpath('index.json').read_bytes())
  assert f['members']==[dict(x,path=str(base/x['path']))for x in index['files']]
  assert {str(q.relative_to(base))for q in base.rglob('*')if q.is_file()}=={'index.json'}|{x['path']for x in index['files']}
  for r in f['members']:assert row(r['path'])==r
 return dict(files=len(files),directories=len(dirs),toolRecords=len(result['toolInputsBefore']),families=len(families),rolePayloadBytes=sum(x['bytes']for x in files.values()),physicalBookendsMatched=True)
def clean(t):
 assert type(t['rawExitCode'])is int and t['rawExitCode']==0
 assert t['parentOwnedGroupGone']is t['allObservedOwnedGroupsGone']is True
 assert t['timeout']is t['forcedCleanup']is False
 assert all(t[k]==[]for k in ['signals','errors','interruptedSignals','remainingObservedPids'])
 assert all(x['alive']is False for x in t['finalGroups'])
def main():
 if(HERE/'index.json').exists():
  own=json.loads((HERE/'index.json').read_bytes());assert{r['path']for r in own['files']}|{'index.json'}=={str(p.relative_to(HERE))for p in HERE.rglob('*')if p.is_file()}
  for r in own['files']:
   b=(HERE/r['path']).read_bytes();assert sha(b)==r['sha256']and len(b)==r['bytes']
 cap=json.loads((HERE/'capsule.json').read_bytes());z=(HERE/'evidence.json.gz').read_bytes();assert sha(z)==cap['archive']['sha256']and len(z)==cap['archive']['bytes']
 expanded=gzip.decompress(z);assert len(expanded)==cap['expandedBytes']<16*1024**2
 blob=json.loads(expanded);rows={r['name']:r for r in cap['files']};assert set(blob)==set(rows)and len(rows)==cap['retainedFiles']
 data={n:base64.b64decode(v,validate=True)for n,v in blob.items()}
 for n,r in rows.items():assert sha(data[n])==r['original']['sha256']and len(data[n])==r['original']['bytes']
 def read(n):return json.loads(data[n])
 def get(ref):
  names=[n for n,r in rows.items()if r['original']['path']==ref['path']];assert names,ref['path']
  for n in names:assert rows[n]['original']==ref
  return data[names[0]]
 def doc(ref):return json.loads(get(ref))
 r=read('run/result.json');assert sha(data['run/result.json'])==RESULT_SHA
 assert r['state']=='ACTUAL_PORTABLE_NEXT_INSTALLED_GENERATORS_CHECKED_V1'and r['passed']is True
 a=doc(r['rootAuthority']);p=doc(r['plan']);idx=doc(r['sourceIndex']);selection=doc(a['portableSelection']);composition=doc(r['composition']);summary=doc(r['materializationSummary'])
 assert a['state']=='ROOT_PORTABLE_NEXT_GENERATORS_AUTHORIZED_V1'and a['unissued']is False
 assert a['generatorChecksAllowed']is a['nodeHostSourceOnly']is True
 assert all(a[k]is False for k in ['nativeBuildAllowed','compilerAllowed','cmakeAllowed','cargoAllowed','engineAllowed','guestAllowed','networkAllowed','copySourceAllowed'])
 assert a['sourceIndex']==r['sourceIndex']and a['plan']==r['plan']
 member=next(x for x in idx['files']if x['path']=='plan.json');assert r['plan']==dict(member,path=str(Path(r['sourceIndex']['path']).parent/'plan.json'))
 assert selection['composition']==r['composition']and selection['sourceMaterialization']==r['materializationSummary']
 assert r['composition']==summary['composition']==p['composition']and r['materializationSummary']==p['materializationSummary']
 assert r['roleContentSha256']==selection['roleContentSha256']==summary['roleContentSha256']==p['roleContentSha256']=='47755843d22d8e0e355ddc56e263e30aa997b4bd963fac50609639913c5c35df'
 assert selection['roleCounts']==summary['roleCounts']=={'native-policy-source':435,'build-support':387,'componentize-embedding':3}
 assert selection['sourceOnly']is True and selection['engineBuilt']is selection['guestExecuted']is selection['historicalMetadataProjected']is False
 assert summary['sourceOnly']is True and summary['compilerOrGuestExecuted']is summary['generatedBuildMetadataProjected']is False
 assert composition['engineBuilt']is composition['guestExecuted']is composition['legacyMetadataProjected']is False
 roles=selection['files'];assert len(roles)==825 and sum(x['bytes']for x in roles)==7530166
 fingerprints=[{k:x[k]for k in ['role','path','sha256','bytes','mode']}for x in roles];fingerprints.sort(key=lambda x:(x['role'],x['path']))
 assert sha(json.dumps(fingerprints,sort_keys=True,separators=(',',':')).encode())==r['roleContentSha256']
 assert composition['sourceRoot']==r['sourceRoot']==selection['sourceRoot']==p['sourceRoot']
 assert composition['nativeSourceFiles']==r['sourceFiles']==435
 native=[dict(path=str(Path(r['sourceRoot'])/x['path']),sha256=x['sha256'],bytes=x['bytes'])for x in roles if x['role']=='native-policy-source']
 assert r['sourceBefore']==r['sourceAfter']==native and len(native)==435
 assert r['wholePortableBefore']==r['wholePortableAfter']==selection['physicalRecords']and len(r['wholePortableBefore'])==825
 assert r['portableDirectoriesBefore']==r['portableDirectoriesAfter']==selection['directoryRecords']and len(r['portableDirectoriesBefore'])==171
 assert r['toolInputsBefore']==r['toolInputsAfter']==r['outerToolInputsBefore']==r['outerToolInputsAfter']
 assert all(r[k]is True for k in ['sourceBeforeAfterUnchanged','portableInputsPreserved','toolInputsPreserved','outerOwnedGroupsClean','outerInputsPreserved','outputCapSatisfied'])
 assert all(r[k]is None for k in ['primaryError','finalProtectionError','toolProtectionError','outerOwnerError'])
 assert r['nativeOrGuestExecuted']is False
 body=doc(r['bodyResult']);assert all(k in r and r[k]==v for k,v in body.items())
 command_paths=['generate-factories.mjs','generate-fs-factory.mjs','generate-startup-factory.mjs','generate-module-factory.mjs','generate-async-hooks-factory.mjs','generate-vm-data-factory.mjs','zlib/generate-factory.mjs','zlib/generate-stream-factory.mjs','next-http/generate-http-factory.mjs','next-imports/generate-imports-factory.mjs']
 assert len(r['commands'])==10 and r['node']==p['node']
 for i,(c,name)in enumerate(zip(r['commands'],command_paths)):
  expected=[r['node']['path'],str(Path(r['sourceRoot'])/'builtins/node-compat'/name)]
  if i==0:expected+=['--crypto-random']
  if i==6:expected+=['--repository',r['sourceRoot']]
  expected+=['--check'];assert c['argv']==expected and c['cwd']==r['sourceRoot']
  s=doc(c['started']);t=doc(c['terminal']);clean(t)
  assert s['argv']==expected and s['pid']==t['pid']and s['timeoutSeconds']==30 and s['authority']==t['authority']==r['rootAuthority']
  assert t['operationalElapsedSeconds']<=30 and c['rawExitCode']==0 and c['ownedGroupsClean']is True and c['monitorError']is None
  for k in ['stdout','stderr']:assert t[k]==c[k]and sha(get(c[k]))==c[k+'Sha256']and c[k]['bytes']<=1048576
  assert get(c['stderr'])==b'' and doc(dict(path=str(Path(c['terminal']['path']).parent/'record.json'),**{k:rows['run/command-'+str(i).zfill(2)+'/record.json']['original'][k]for k in ['sha256','bytes']}))==c
  events=[read(n)for n in rows if n.startswith('run/command-'+str(i).zfill(2)+'/owned-')]
  assert sorted(x['sequence']for x in events)==list(range(len(events)))and {json.dumps(x['process'],sort_keys=True)for x in events}=={json.dumps(x,sort_keys=True)for x in t['observedProcesses']}
 outer=doc(r['outerTerminal']);started=doc(r['outerStarted']);clean(outer)
 assert started['argv']==[p['python']['path'],'-I','-B',str(Path(r['sourceIndex']['path']).parent/'run.py'),'--worker-authority',r['rootAuthority']['path']]
 assert started['timeoutSeconds']==900 and started['pid']==outer['pid']and started['authority']==outer['authority']==r['rootAuthority']and outer['operationalElapsedSeconds']<=900
 assert outer['stdout']==r['outerStdout']and outer['stderr']==r['outerStderr']and get(r['outerStderr'])==b''
 outer_events=[read(n)for n in rows if n.startswith('outer/owned-')];assert sorted(x['sequence']for x in outer_events)==list(range(len(outer_events)))
 assert {json.dumps(x['process'],sort_keys=True)for x in outer_events}=={json.dumps(x,sort_keys=True)for x in outer['observedProcesses']}
 cli=[json.loads(x)for x in data['root/first-cli.stdout.log'].splitlines()];assert cli[-1]['result']==cap['runtimeResult']and cli[-1]['passed']is True and data['root/first-cli.stderr.log']==b''
 before_final=sum(x['original']['bytes']for n,x in rows.items()if n.startswith(('run/','outer/'))and n!='run/result.json')
 assert before_final==r['outputBytesBeforeFinalReceipt']==1017363
 assert before_final+len(data['run/result.json'])+128<=r['maxAcceptedOutputBytes']==8388608
 assert r['freeBytesAtAdmission']==426127360 and r['minimumFreeBytes']==p['minimumFreeBytes']==67108864
 assert r['continuousFreeFloorClaimed']is False and r['byteCapsArePostCaptureAdmissionNotContinuousLimits']is True
 for f in cap['families']:
  index=doc(f['index']);base=Path(f['index']['path']).parent;assert f['members']==[dict(x,path=str(base/x['path']))for x in index['files']]
 if '--current'in sys.argv:
  assert current(r,selection,cap['families'])==cap['currentBeforeFinal']
  for n,x in rows.items():assert row(x['original']['path'])==x['original']
 return dict(schemaVersion=1,state='INDEPENDENT_PORTABLE_GENERATOR_ACTUAL_DATA_REVIEW_PASSED_V1',dataValidated=True,actualResult=cap['runtimeResult'],commands=10,perCommandSeconds=30,outerSeconds=900,allRaw0Clean=True,sourceFiles=435,wholePortableFiles=825,portableDirectories=171,roleContentSha256=r['roleContentSha256'],physicalAndToolBookendsMatch=True,currentBeforeFinal=cap['currentBeforeFinal'],retainedFiles=len(rows),sourcePayloadsCopied=False,toolOrSdkPayloadsCopied=False,reviewerAuthoredPredecessorMaterializerAndRunner=True,reviewerPreviouslySourceReviewedProducer=True,generatorsRerunByReviewer=False,nativeBuildOrGuestOrAbiProved=False,cleanMachineBuildProved=False,adoption=False)
if __name__=='__main__':print(json.dumps(main(),indent=2))
