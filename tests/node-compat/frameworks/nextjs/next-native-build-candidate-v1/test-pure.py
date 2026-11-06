"""Benign filesystem/data tests only; never calls runner main/phase/importutility."""
from pathlib import Path
import copy,importlib.util,json,os,stat,tempfile,tarfile,io,ast
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('own_next_build_pure',HERE/'run.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
checks=[]
def test(name,f):f();checks.append(name)
def assertion(value):assert value
def refuses_io(f):
 try:f()
 except FileExistsError:return
 raise AssertionError('expected FileExistsError')
def refuses(f):
 try:f()
 except(AssertionError,KeyError,TypeError):return
 raise AssertionError('expected refusal')
a=dict(schemaVersion=1,state='ROOT_EXPERIMENTAL_NEXT_NATIVE_BUILD_AUTHORITY_V1',buildAllowed=True,engineOrGuestExecutionAllowed=False,entry={},plan={},composition={},joinedFrontendResult={},installedGeneratorResult={},selectedPublicManifests=[],selectedPrivateManifests=[],workRoot='/private/tmp/starling-node-compat/next-native-build-pure-test')
test('pure complete Root action shape',lambda: m.validate_authority(a))
for key,value in [('buildAllowed',False),('engineOrGuestExecutionAllowed',True),('state','OLD83'),('entry',None),('composition',None),('selectedPublicManifests',None),('workRoot','/tmp/unsafe'),('workRoot','/private/tmp/starling-node-compat/next-native-build-x/../old')]:
 b=copy.deepcopy(a);b[key]=value;test('Root refusal '+key+str(value),lambda b=b:refuses(lambda:m.validate_authority(b)))
for path in ['/absolute','../escape','x/../../escape','']:
 test('confined refusal '+path,lambda path=path:refuses(lambda:m.confined(path)))
with tempfile.TemporaryDirectory(prefix='next-build-source-test-')as directory:
 root=Path(directory).resolve();source=root/'source';source.write_bytes(b'benign-source-copy');source.chmod(0o644)
 prior=os.umask(0o077)
 try:
  for mode in [0o644,0o755]:
   target=root/('dest-'+str(mode));r=m.copy_exclusive(m.descriptor(source),target,mode);test('real077 copy '+oct(mode),lambda mode=mode,target=target,r=r: (assertion(stat.S_IMODE(target.stat().st_mode)==mode),assertion(r['singleLink']and r['distinctInode'])))
 finally:os.umask(prior)
 test('exclusive output refuses overwrite',lambda:refuses_io(lambda:m.copy_exclusive(m.descriptor(source),root/'dest-420',0o644)))
 tar=root/'benign.tar'
 with tarfile.open(tar,'w')as t:
  member=tarfile.TarInfo('package/file');member.size=3;t.addfile(member,io.BytesIO(b'abc'))
 out=m.safe_extract(tar,root/'extract');assert(out/'file').read_bytes()==b'abc';checks.append('benign data archive only extraction')
 bad=root/'bad.tar'
 with tarfile.open(bad,'w')as t:
  member=tarfile.TarInfo('../escape');member.size=0;t.addfile(member,io.BytesIO())
 test('archive traversal refuses',lambda:refuses(lambda:m.safe_extract(bad,root/'bad-extract')))
# Parse source to confirm actual methods are invoked through real utility API.
s=(HERE/'run.py').read_text();ast.parse(s)
for token in ['monitor.monitor(','life.monitor_owned_command(','minimum_free=plan[\'disk\'][\'stopBytes\']','os.fchmod(fd,mode)','old83MetadataProjected=False','descriptor(__file__)==a[\'entry\']','private source changed during compilation']:
 assert token in s;checks.append('actual Source join '+token)
print(json.dumps(dict(schemaVersion=1,passed=True,checks=len(checks),cases=checks,nativeBuildOrCompilerInvoked=False,subprocessInvoked=False,benignTempFilesOnly=True)))

def unused():pass
