"""Retained constructor/runtime DATA only; run after the actual runtime terminal."""
from pathlib import Path
import argparse,gzip,hashlib,io,json,tarfile
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[4]
FIXTURE=HERE.parents[1]/'context-interleaving-candidate-v1'
CONSTRUCTOR=Path('/private/tmp/starling-node-compat/context-interleaving-component-v1-context-interleaving-engine462-context-v1')
def digest(b):return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def row(p,b=None):
 p=Path(p);return dict(path=str(p),**digest(p.read_bytes() if b is None else b))
def checked(r):
 p=Path(r['path']);assert p.is_absolute() and p.is_file() and not p.is_symlink()
 b=p.read_bytes();assert row(p,b)=={k:r[k] for k in ['path','sha256','bytes']};return b
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--runtime',required=True);args=parser.parse_args()
 runtime=Path(args.runtime);assert runtime.is_absolute() and not (HERE/'data.tar.gz').exists()
 assert (runtime/'result.json').is_file() and Path(str(runtime)+'-external-root/terminal.json').is_file(), 'wait for genuine final runtime'
 data={};entries=[];originals={};external={};families={}
 def add(name,p,ref=None):
  p=Path(p);r=ref or row(p);b=checked(r)
  if str(p) in originals:
   old=originals[str(p)];assert old['original']==r and data[old['path']]==b;return old['path']
  assert name not in data and not name.startswith('/') and '..' not in Path(name).parts
  kind='gzip' if p.suffix=='.gz' else 'utf8'
  if kind=='utf8':b.decode('utf8')
  item=dict(path=name,original=r,kind=kind);entries.append(item);data[name]=b;originals[str(p)]=item;return name
 def family(ref):
  if ref['path'] in families:assert families[ref['path']]==ref;return
  index=json.loads(checked(ref));base=Path(ref['path']).parent;names=[r['path'] for r in index['files']]
  assert len(names)==len(set(names)) and {p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()}==set(names)|{'index.json'}
  add('sources/'+base.name+'/index.json',ref['path'],ref)
  for r in index['files']:
   p=base/r['path'];assert not p.is_symlink();add('sources/'+base.name+'/'+r['path'],p,{**r,'path':str(p)})
  families[ref['path']]=ref
 for label,root in [('constructor',CONSTRUCTOR),('runtime',runtime)]:
  for p in sorted(root.rglob('*')):
   assert not p.is_symlink()
   if not p.is_file():continue
   assert p.suffix not in ['.a','.o','.zip']
   if p.suffix=='.wasm':continue
   add(label+'/'+p.relative_to(root).as_posix(),p)
  monitor=Path(str(root)+'-external-root')
  for p in sorted(monitor.rglob('*')):
   assert not p.is_symlink()
   if p.is_file():add(label+'-outer/'+p.relative_to(monitor).as_posix(),p)
  terminal=json.loads((monitor/'terminal.json').read_text())
  add('authority/'+label+'.json',terminal['authority']['path'],terminal['authority'])
  started=json.loads((monitor/'started.json').read_text())
  for argument in started['argv']:
   p=Path(argument)
   if p.is_absolute() and p.is_file() and p.suffix in ['.py','.mjs']:add('root-callers/'+p.parent.name+'/'+p.name,p)
 construction=json.loads((CONSTRUCTOR/'result.json').read_text());ca=json.loads(checked(construction['rootAuthority']))
 fixturePlan=json.loads((FIXTURE/'plan.json').read_text());family(construction['artifacts']['inputSourceIndex']);family(construction['callerIndex'])
 fixtureInputs=json.loads((FIXTURE/'source-inputs.json').read_text())['inputs']
 for ref in fixtureInputs:checked(ref);external[ref['path']]=ref
 runtimeResult=json.loads((runtime/'result.json').read_text())
 # Runtime Source role is resolved from its genuine issued authority, never
 # inferred from a similarly named controller or guessed success output.
 rt=json.loads(Path(str(runtime)+'-external-root/terminal.json').read_text());ra=json.loads(checked(rt['authority']))
 if isinstance(ra.get('sourceIndex'),dict):family(ra['sourceIndex'])
 elif isinstance(ra.get('callerIndex'),dict):family(ra['callerIndex'])
 else:raise AssertionError('Runtime authority must declare its indexed Source role')
 world=fixturePlan['worldSourceIndex'];assert ca['worldSourceIndex']==world
 index=json.loads(checked(world));base=Path(world['path']).parent
 assert {p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()}=={r['path'] for r in index['files']}|{'index.json'}
 add('world/index.json',world['path'],world);worldRows=[]
 for r in index['files']:
  p=base/r['path'];ref={**r,'path':str(p)};checked(ref);assert p.stat().st_nlink==1;worldRows.append(ref)
  if p.suffix=='.wit':add('world/'+r['path'],p,ref)
 assert len([r for r in worldRows if r['path'].endswith('.wit')])==8
 # Exact Root launcher source establishes the historical world-guard contract.
 add('root-callers/launch-context-v1-construction.py',HERE.parent/'launch-context-v1-construction.py')
 history=HERE.parent/'preparation-history/unexecuted-context-collector-v1-authority.json'
 if history.exists():add('preparation-history/unexecuted-context-collector-v1-authority.json',history)
 for key in ['component','engine','adapter']:
  ref=construction['artifacts'][key];checked(ref);external[ref['path']]=ref
 for ref in construction['artifacts']['engineBuildEvidence']:
  checked(ref);external[ref['path']]=ref
 metadata=construction['artifacts']['nativeMetadata'];checked(metadata);external[metadata['path']]=metadata
 assert (CONSTRUCTOR/'api-return/native-metadata-input.json').read_bytes()==checked(metadata)
 parserModule=json.loads((CONSTRUCTOR/'api-return/tool-preopens-configured.json').read_text())['module'];checked(parserModule);external[parserModule['path']]=parserModule
 for label in ['constructor','runtime']:
  grant=json.loads(data['authority/'+label+'.json'])
  for value in grant.values():
   if isinstance(value,dict) and all(k in value for k in ['path','sha256','bytes']):
    checked(value);external[value['path']]=value
   for name in ['newSourceEvidence','engineBuildEvidence','nativeProtectedInputs']:
    for ref in grant.get(name,[]):checked(ref);external[ref['path']]=ref
 # Copy only the direct selected global/role records. Tool/SDK/history closures
 # remain external, and no old helper/admission/verifier is imported or invoked.
 for item in originals.values():checked(item['original'])
 for ref in list(external.values())+worldRows:checked(ref)
 with (HERE/'data.tar.gz').open('xb') as raw:
  with gzip.GzipFile(fileobj=raw,mode='wb',filename='',mtime=0) as compressed:
   with tarfile.open(fileobj=compressed,mode='w') as tar:
    for name,b in sorted(data.items()):
     member=tarfile.TarInfo(name);member.size=len(b);member.mode=0o600;member.mtime=0;tar.addfile(member,io.BytesIO(b))
 capsule=dict(schemaVersion=1,bundle=row(HERE/'data.tar.gz'),entries=sorted(entries,key=lambda r:r['path']),sourceFamilies=list(families.values()),worldSourceIndex=world,worldCurrentMembersRehashed=len(worldRows),selectedOriginalsRehashedBeforeFinal=len(originals),selectedFixtureInputsRehashedBeforeFinal=len(fixtureInputs),externalReferences=list(external.values()),
  actualConstructorResult=row(CONSTRUCTOR/'result.json'),actualRuntimeResult=row(runtime/'result.json'),originalRuntimeState=runtimeResult['state'],originalRuntimeObservationsValid=runtimeResult['observationsValid'],originalRuntimeNodePublicProjectionParity=runtimeResult.get('nodePublicProjectionParity'),newTargetAction=False,bigComponentSdkArchiveOrAppPayloadCopied=False,sourceAuthorRelationship='Reviewer authored the shared context cases and facade; actual DATA review is separate from Source certification.')
 (HERE/'capsule.json').write_text(json.dumps(capsule,indent=2)+'\n')
 print(json.dumps(dict(retainedFiles=len(entries),retainedBytes=sum(len(b) for b in data.values()),bundle=capsule['bundle'])))
if __name__=='__main__':main()
