"""Future fresh local source stage. Default is read-only planning, not adoption.

Run only from the original reviewed proposal. Preparation references are never
reinterpreted from a relocated copy. No native/guest action is implemented here.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
CORRECTED=Path('/tmp/starling-node-compat/classic-trace-source-v1')
ALLOWED=Path('/tmp/starling-node-compat/zlib-source-v1')
REL=Path('tests/node-compat/foundation-zlib/native-integration-candidate-v1')
HEAD='54b3329b3ce818fd1f244e871e9c259b63667cda'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def checked(path,digest):
 path=Path(path);assert path.is_file()and not path.is_symlink()and sha(path)==digest,str(path)
 return path
def source_plan():
 """Exact native/tool inventory; callable by own isolated source-copy tests."""
 policy=json.loads((HERE/'policy.json').read_bytes());tools=json.loads((HERE/'artifact-tools/tool-pins.json').read_bytes())
 assert len(policy['expectedNativeSourceManifest'])==350
 plan={}
 for row in policy['expectedNativeSourceManifest']+tools['toolDependencies']:
  name=row['path'];assert not Path(name).is_absolute()and all(x not in('','.','..')for x in Path(name).parts)
  choices=[HERE/'source'/name]
  if Path(name).is_relative_to(REL):choices.append(HERE/Path(name).relative_to(REL))
  choices += [CORRECTED/name,REPO/name]
  candidates=[p for p in choices if p.is_file()and not p.is_symlink()and sha(p)==row['sha256']]
  assert candidates,'No exact reviewed source for '+name
  item={'path':name,'source':str(candidates[0]),'sha256':row['sha256'],'bytes':candidates[0].stat().st_size}
  assert name not in plan or plan[name]['sha256']==item['sha256']
  plan[name]=item
 return[plan[key]for key in sorted(plan)]

def verify_index(expected):
 checked(HERE/'index.json',expected);index=json.loads((HERE/'index.json').read_bytes())
 for row in index['files']:checked(HERE/row['path'],row['sha256']);assert(HERE/row['path']).stat().st_size==row['bytes']
 return index

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--index-sha256',required=True);parser.add_argument('--destination',type=Path,default=ALLOWED);parser.add_argument('--apply',action='store_true');args=parser.parse_args()
 assert HERE==Path('/Users/dan/dev/StarlingMonkey')/REL,'Original preparation context only; no relocated preparation seal interpretation'
 index=verify_index(args.index_sha256);plan=source_plan()
 destination=args.destination.absolute();assert destination==ALLOWED and not destination.exists()and not destination.is_symlink()
 staging=destination.with_name(destination.name+'.staging');assert not staging.exists()and not staging.is_symlink()
 assert subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip()==HEAD
 command=['git','-c','core.hooksPath=/dev/null','clone','--no-hardlinks',str(REPO),str(staging)]
 if not args.apply:
  print(json.dumps({'state':'SOURCE_STAGE_PLAN_ONLY','sourcePacketIndexSha256':args.index_sha256,'sourceRows':len(plan),'nativeSources':350,'gitCommandNotRun':command,'destination':str(destination),'nativeOrGuestExecuted':False}));return
 # A new task-owned checkout only. Accepted artifacts and active corrected
 # checkout are inputs, never mutation targets. Failed staging is retained.
 subprocess.run(command,check=True)
 assert subprocess.check_output(['git','-C',str(staging),'rev-parse','HEAD'],text=True).strip()==HEAD
 for row in plan:
  source=checked(row['source'],row['sha256']);target=staging/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
  assert not target.is_symlink()
  with source.open('rb')as src,target.open('wb')as out:shutil.copyfileobj(src,out,1024*1024)
  checked(target,row['sha256']);checked(source,row['sha256'])
 # Preserve the complete reviewed proposal and its original-context preparation
 # evidence as bytes. Runtime actions consume actual staged350/tool inventories.
 for row in index['files']+[{'path':'index.json','sha256':args.index_sha256}]:
  source=checked(HERE/row['path'],row['sha256']);target=staging/REL/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
  assert not target.is_symlink();target.write_bytes(source.read_bytes());checked(target,row['sha256'])
 verify_index(args.index_sha256)
 for row in plan:checked(staging/row['path'],row['sha256']);checked(row['source'],row['sha256'])
 assert not destination.exists()and not destination.is_symlink()
 record={'schemaVersion':1,'state':'REVIEWED_SOURCE_STAGE_CREATED_NO_NATIVE_OR_GUEST','proposalIndexSha256':args.index_sha256,'originalPreparationRoot':str(HERE),'destination':str(destination),'gitBase':HEAD,'actualSourceFiles':350,'copiedSourceAndToolRows':plan,'preparedReferencesRelocatedOrReinterpreted':False,'nativeOrGuestExecuted':False}
 (staging/'zlib-stage-receipt.json').write_text(json.dumps(record,indent=2)+'\n')
 staging.rename(destination);print(json.dumps({'state':record['state'],'sourceRoot':str(destination),'sourceRows':len(plan),'nativeOrGuestExecuted':False}))
if __name__=='__main__':main()
