from pathlib import Path
import hashlib,json,os,subprocess
R=Path('/Users/dan/dev/StarlingMonkey');S=R/'tests/node-compat/foundation-scheduler';P=S/'combined-clock-lifecycle-candidate-v2';OLD=S/'combined-clock-lifecycle-candidate-v1';O=S/'independent-combined355-clock-lifecycle-v2-source-review-v1';O.mkdir()
checks=0

def d(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def write(n,v):
 with (O/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def file(row):
 global checks
 assert d(row['path'])==row;checks+=1
ix=d(P/'index.json');assert ix['sha256']=='960a3b26af6c9b6fdd3e332e2d00e353feb683dfbe455855f3415ddc77f6291e'
value=json.loads((P/'index.json').read_bytes());names={'index.json'}
for row in value['files']:
 n=row['path'];assert n not in names and not Path(n).is_absolute() and '..' not in Path(n).parts;names.add(n);file(dict(row,path=str(P/n)))
assert not any(p.is_symlink() for p in P.rglob('*'));assert {p.relative_to(P).as_posix() for p in P.rglob('*') if p.is_file()}==names
refs=json.loads((P/'references.json').read_bytes());target=refs['nativeTarget']
for k in ['engine','metadata','freezeReceipt','nativeSourceIndex']:file(target[k])
for row in target['actualFrozenReview'].values():file(row)
m=json.loads(Path(target['metadata']['path']).read_bytes());assert len(m)==80 and len(m['sourceManifest'])==355 and len(m['componentizeSourceManifest'])==3 and len(m['selectedModuleManifests'])==11
assert m['engineSha256']=='355550f1d0bdc7455fd81ffbd739ac1453a56f3537b277eb644441d87434af3b' and m['entropyPolicy']=='off' and m['gcStress'] is m['oomTesting'] is False
for group,root in [('sourceManifest',refs['nativeSourceRoot']),('componentizeSourceManifest',refs['externalEmbeddingRoot'])]:
 for row in m[group]:
  b=(Path(root)/row['path']).read_bytes();assert hashlib.sha256(b).hexdigest()==row['sha256'];checks+=1
for row in m['selectedModuleManifests']:assert hashlib.sha256((Path(refs['nativeSourceRoot'])/row['path']).read_bytes()).hexdigest()==row['sha256'];checks+=1
for key in ['currentSource','externalEmbedding','mechanismAndHistoryReferences']:
 for row in refs[key]:file(row)
for row in refs['proposedCombinedBootstrapApi'].values():
 if isinstance(row,dict) and 'path'in row:file(row)
node=refs['nodeParserAndPureTests'];file(node)
for row in json.loads((P/'fixture-catalogue.json').read_bytes())['fixtures']:
 file(row['source']);file(row['wit']);assert Path(row['source']['path']).parent==P/'fixtures' and Path(row['wit']['path']).parent==P/'fixtures'
for p in (P/'fixtures').iterdir():assert p.read_bytes()==(OLD/'fixtures'/p.name).read_bytes();checks+=1
for name in ['schedules.json','requirements.json']:assert (P/name).read_bytes()==(OLD/name).read_bytes();checks+=1
requirements=json.loads((P/'requirements.json').read_bytes());assert len(requirements['gates'])==17 and all(r['actualResult'] is None for r in requirements['gates'])
commands=[]
for i,path in enumerate([*sorted((P/'fixtures').glob('*.mjs')),P/'collectors.mjs',P/'test-models.mjs']):
 args=[node['path'],'--check',str(path)];r=subprocess.run(args,capture_output=True,timeout=30);(O/('grammar-'+str(i)+'.stdout.log')).write_bytes(r.stdout);(O/('grammar-'+str(i)+'.stderr.log')).write_bytes(r.stderr);commands.append(dict(argv=args,rawExitCode=r.returncode));assert r.returncode==0
args=[node['path'],str(P/'test-models.mjs')];r=subprocess.run(args,capture_output=True,timeout=30);(O/'pure.stdout.json').write_bytes(r.stdout);(O/'pure.stderr.log').write_bytes(r.stderr);assert r.returncode==0;pure=json.loads(r.stdout);write('commands.json',dict(grammar=commands,pure=dict(argv=args,rawExitCode=r.returncode)))
print(json.dumps(dict(sourceIndex=ix,checkedFiles=checks,pure=pure,grammar=len(commands),reviewDirectory=str(O))),flush=True)
write('preliminary-checks.json',dict(schemaVersion=1,sourceIndex=ix,checkedFiles=checks,pure=pure,grammar=len(commands),sourceOnly=True,guestOrHelperOrClockWorkloadInvoked=False,notYetSealed=True))
