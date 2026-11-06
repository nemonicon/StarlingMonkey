"""Authorized tiny benign filesystem regression, never native cache/helper/build.
Uses exact old/new generic copy APIs with explicit private scratch arguments.
"""
from pathlib import Path
import hashlib,importlib.util,json,os,stat,sys
OWN=Path(__file__).resolve().parent;DONOR=OWN.with_name('node-crypto-hash-hmac-native-controller-candidate-v1');ROOT=Path('/private/tmp/starling-node-compat/hash-hmac-controller-v2-benign-copy-tests-20261106-01')
def load(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
# Authenticate the complete old sealed family before importing its inert generic code.
v=json.loads((DONOR/'index.json').read_bytes());assert hashlib.sha256((DONOR/'index.json').read_bytes()).hexdigest()=='9e5195b90e20708a8a398fa9013eba867e2f2e5e1d18c2f5b76ed5bbc3c01d3b'
for r in v['files']:
 b=(DONOR/r['path']).read_bytes();assert hashlib.sha256(b).hexdigest()==r['sha256']and len(b)==r['bytes']
old=load(DONOR/'build_body.py','authenticated_old_generic_copy_only');new=load(OWN/'build_body.py','new_generic_copy_only');io=load(OWN/'io_guard.py','new_generic_data_io_only')
assert not ROOT.exists()and not ROOT.is_symlink();ROOT.mkdir(mode=0o700);records=[];old_umask=os.umask(0o077)
def file(p,b,mode):
 fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 try:assert os.write(fd,b)==len(b);os.fchmod(fd,mode);os.fsync(fd)
 finally:os.close(fd)
 return io.row(p)
def fixture(name,data,mode):return dict(source=file(ROOT/(name+'.source'),data,mode),target=name,sourceMode=mode,outputMode=mode)
def event(name,fn,expected_failure=False):
 try:fn();assert not expected_failure;records.append(dict(name=name,status='PASSED'))
 except(AssertionError,FileExistsError)as e:
  if not expected_failure:raise
  records.append(dict(name=name,status='FAILED_AS_EXPECTED',errorType=type(e).__name__))
try:
 a=fixture('readable',b'BENIGN only: copy mode0644\n',0o644);b=fixture('executable',b'BENIGN DATA never executed: mode0755\n',0o755)
 for label,module,expected in [('old',old,True),('new',new,False)]:
  work=ROOT/(label+'-work');out=ROOT/(label+'-output');out.mkdir(mode=0o700);result=dict(cacheCopiesCompleted=[])
  event(label+'-populate-two-tiny-copies-under077',lambda module=module,work=work,out=out,result=result:module.populate_cache(dict(copies=[a,b]),result,work,out,io),expected)
  if expected:
   p=work/'readable';assert p.read_bytes()==b'BENIGN only: copy mode0644\n'and stat.S_IMODE(p.stat().st_mode)==0o600 and result['cacheCopiesCompleted']==[]and not(work/'executable').exists()
   records[-1].update(partialFile=io.row(p),actualMode=stat.S_IMODE(p.stat().st_mode),completedCopies=0)
  else:
   assert len(result['cacheCopiesCompleted'])==2
   for r in [a,b]:
    p=work/r['target'];s=p.stat();q=io.checked(r['source']).stat();assert io.row(p)['sha256']==r['source']['sha256']and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==r['outputMode']and(s.st_dev,s.st_ino)!=(q.st_dev,q.st_ino)
   records[-1].update(copies=result['cacheCopiesCompleted'],bothModesExact=True,bothDistinctSingleLinks=True)
 # Existing receipt prevents overwrite, but the completed tiny first data copy remains.
 work=ROOT/'receipt-failure-work';out=ROOT/'receipt-failure-output';out.mkdir(mode=0o700);marker=file(out/'cache-copy-1.json',b'KEEP_EXISTING_RECEIPT\n',0o600);result=dict(cacheCopiesCompleted=[])
 event('receipt-publication-collision-preserves-partial-copy',lambda:new.populate_cache(dict(copies=[a,b]),result,work,out,io),True)
 assert io.row(out/'cache-copy-1.json')==marker and len(result['cacheCopiesCompleted'])==1 and not(work/'executable').exists()and stat.S_IMODE((work/'readable').stat().st_mode)==0o644
 records[-1].update(completedTinyCopies=1,secondCopyAbsent=True,receiptUnchanged=True,partialFile=io.row(work/'readable'))
 # No existing work destination may be reused.
 work=ROOT/'preexisting-work';work.mkdir(mode=0o700);marker=file(work/'keep',b'KEEP\n',0o600);out=ROOT/'preexisting-output';out.mkdir(mode=0o700)
 event('existing-work-refused-without-overwrite',lambda:new.populate_cache(dict(copies=[a]),dict(cacheCopiesCompleted=[]),work,out,io),True);assert io.row(work/'keep')==marker and not(work/'readable').exists()
 # Actual stream write seam with a real partial file: no fake full-write success.
 class Short:
  def __init__(self,f):self.f=f
  def write(self,value):return self.f.write(value[:max(1,len(value)//2)])
 partial=ROOT/'short-write-target'
 with io.checked(a['source']).open('rb')as src,partial.open('xb')as dst:event('real-short-write-refused',lambda:new.stream_copy(src,Short(dst)),True)
 assert 0<partial.stat().st_size<a['source']['bytes'];records[-1]['partialFile']=io.row(partial)
 for r in [a,b]:assert io.checked(r['source']).stat().st_mode&0o777==r['sourceMode']
finally:os.umask(old_umask)
result=dict(schemaVersion=1,state='BENIGN_OWNED_COPY_MODE_REGRESSIONS_PASSED_V2',scratchRoot=str(ROOT),oldDonorIndexSha256='9e5195b90e20708a8a398fa9013eba867e2f2e5e1d18c2f5b76ed5bbc3c01d3b',umaskDuringCopies='077',cases=records,actualBenignFilesystemCopiesInvoked=True,actualNativeCacheCopiesInvoked=False,nativeHelperOrBuildInvoked=False,compilerInvoked=False,cryptoOrGuestExecuted=False,sourceDataNeverExecuted=True,sourceUmaskRestored=True)
(OWN/'benign-copy-test-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(state=result['state'],cases=len(records),oldFailedAsExpected=True,new644And755Passed=True,nativeActionsInvoked=False)))
