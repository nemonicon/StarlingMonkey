"""No-write test entry except temporary benign host-only files, auto-removed.
Calls the genuine actual checked/physical read guards, never bootstrap/run/load,
admit/helper/recheck or any native/cache/guest operation. JSON only on stdout.
"""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,os,sys,tempfile
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
pins=json.loads((P/'guard-test-inputs.json').read_bytes())
for r in pins['files']:
 b=Path(r['path']).read_bytes();assert len(b)==r['bytes']and hashlib.sha256(b).hexdigest()==r['sha256']
def imported(p,name):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
guard=imported(P/'revalidate.py','genuine_v2_inert_entry_read_guard')
assert guard.OWN==P and Path(guard.__file__).resolve()==P/'revalidate.py'
refs=json.loads((P/'references.json').read_bytes());assert guard.TMP_ALIAS_POLICY==refs['tmpAliasPolicy']
base=json.loads(Path(refs['baseSourceInputs']['path']).read_bytes());extra=json.loads(Path(refs['baseArtifactInputs']['path']).read_bytes());rows=[*base['files'],*extra['files']];assert len(rows)==21328
passed=0;mapped=[];negative=0
for r in rows:
 before=copy.deepcopy(r);actual=guard.checked(r);assert r==before
 assert actual==Path(r['path']).resolve(strict=True);passed+=1
 if r['path'].startswith('/tmp/'):mapped.append(dict(descriptor=r,physical=str(actual)))
assert [r['descriptor']['path']for r in mapped]==guard.TMP_ALIAS_POLICY['selectedDescriptorPaths']
def reject(fn):
 global negative
 try:fn()
 except(AssertionError,ValueError,FileNotFoundError):negative+=1;return
 raise AssertionError('negative accepted')
def row(p,aspath=None):
 b=p.read_bytes();return dict(path=aspath or str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
aliases=json.loads(Path(refs['baseReferenceAliases']['path']).read_bytes())['symlinks'];aliaschecks=0
for alias in aliases:
 link=Path(alias['path']);target=link.resolve(strict=True)
 if target.is_file():r=row(target,aspath=str(link))
 else:
  leaf=next(p for p in target.rglob('*')if p.is_file()and not p.is_symlink());r=row(leaf,aspath=str(link/leaf.relative_to(target)))
 reject(lambda:guard.checked(r));aliaschecks+=1
with tempfile.TemporaryDirectory(prefix='hashhmac357-read-guard-v2-',dir='/private/tmp')as name:
 root=Path(name);real=root/'real';real.mkdir();file=real/'fixture.txt';file.write_bytes(b'bounded guard fixture\n');r=row(file);assert guard.checked(r)==file
 leaf=root/'leaf';leaf.symlink_to(file);reject(lambda:guard.checked(row(file,aspath=str(leaf))))
 parent=root/'parent';parent.symlink_to(real,target_is_directory=True);reject(lambda:guard.checked(row(file,aspath=str(parent/'fixture.txt'))))
 # A matching real file under /tmp is refused unless one of the selected TWO.
 reject(lambda:guard.checked(row(file,aspath=str(file).replace('/private/tmp/','/tmp/',1))))
 for path in [str(file).replace('/private/tmp/','//private/tmp/',1),str(real/'..'/'real'/'fixture.txt')]:reject(lambda:guard.checked(dict(r,path=path)))
 reject(lambda:guard.checked(dict(r,sha256='0'*64)));reject(lambda:guard.checked(dict(r,bytes=r['bytes']+1)));reject(lambda:guard.checked(dict(r,bytes=True)))
for key,value in [('aliasPath','/var'),('linkText','/private/tmp'),('resolved','/private/other'),('selectedDescriptorPaths',guard.TMP_ALIAS_POLICY['selectedDescriptorPaths']+['/tmp/unselected']),('otherSymlinkAncestorsAllowed',True),('descriptorPathRewriting',True)]:
 policy=copy.deepcopy(guard.TMP_ALIAS_POLICY);policy[key]=value;reject(lambda:guard.physical(mapped[0]['descriptor']['path'],policy))
old=imported(Path(refs['parentAdapterIndex']['path']).parent/'revalidate.py','genuine_v1_inert_entry_read_guard');oldfail=0
for x in mapped:
 try:old.checked(x['descriptor'])
 except AssertionError:oldfail+=1
assert oldfail==2
print(json.dumps(dict(schemaVersion=1,passed=True,actualEntryOwnCorrect=True,genuineCheckedImplementationTested=True,recordedRows=passed,selectedTmpAliases=mapped,otherActualSymlinkPathsRefused=aliaschecks,negativeCases=negative,oldSelectedRowsRefused=oldfail,descriptorDataUnchanged=True,bootstrapRunOrRecheckCalled=False,helperOrAdmitImported=False,nativeCacheOrGuestActions=False)))
