"""Derive own stage stdlib primitives as Source only; never run a phase."""
import ast,hashlib,json
from pathlib import Path
OWN=Path(__file__).resolve().parent;ROOT=OWN.parents[3]
DONOR=ROOT/'tests/node-compat/foundation-scheduler/combined-native-stage-controller-candidate-v1/controller.py'
assert not (OWN/'index.json').exists()
text=DONOR.read_text();tree=ast.parse(text);wanted=['safe','checked','read','descriptor','family','indexed_result','absent','fsync_directory','durable','progress','git_environment','command','terminal_model']
blocks=[]
for name in wanted:
 node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name);block=ast.get_source_segment(text,node);blocks.append((name,block))
prefix='''"""Dormant genuine Hash/Hmac357 Source stage. No action on module import."""
from pathlib import Path
import hashlib,importlib.util,json,os,shutil,stat,subprocess,sys
if not __debug__:raise RuntimeError('Stage assertions must remain enabled')
REPO=Path('/Users/dan/dev/StarlingMonkey')
OWN=REPO/'tests/node-compat/foundation-crypto/node-crypto-hash-hmac-stage-candidate-v1'
SOURCE_FAMILY=REPO/'tests/node-compat/foundation-crypto/node-crypto-hash-hmac-native-integration-candidate-v1'
SOURCE_SHA='7c5a8468639f8bfab3b06f8a75e8cb74373747562b9826450397f90db2dc2429'
MONITOR_SHA='0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b'
DEST=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-source')
WORK=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-build')
FREEZE=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-freeze')
OUT=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-stage-external-root')
JOURNAL=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-stage.json')
BASE='54b3329b3ce818fd1f244e871e9c259b63667cda'
TIMEOUT=600
'''
actual=[]
for name,block in blocks:
 if name=='checked':
  block=block.replace("path=Path(row['path']);assert path.is_absolute()and '..'not in path.parts","path=Path(row['path']);assert path.is_absolute()and str(path)==row['path']and '..'not in path.parts and '\\\\'not in row['path']and '\\0'not in row['path']")
  block=block.replace("if str(path).startswith('/tmp/'):path=Path('/private'+str(path))","if str(path).startswith('/tmp/'):\n        assert Path('/tmp').is_symlink()and Path('/tmp').resolve()==Path('/private/tmp')\n        path=Path('/private'+str(path))")
 actual.append((name,block))
body=prefix+'\n\n'+'\n\n\n'.join(block for _,block in actual)+'\n\n\n'+(OWN/'stage-body.py.txt').read_text()
(OWN/'controller.py').write_text(body)
d=lambda p:dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
(OWN/'generic-derivation.json').write_text(json.dumps(dict(schemaVersion=1,donor=d(DONOR),definitions=[dict(name=name,beforeSha256=hashlib.sha256(before.encode()).hexdigest(),afterSha256=hashlib.sha256(block.encode()).hexdigest(),unchanged=before==block)for(name,before),(_,block)in zip(blocks,actual)],actualOwnModule=True,importedDonorModule=False,globalsRebound=False,newStageBody=d(OWN/'stage-body.py.txt')),indent=2)+'\n')
print(json.dumps(dict(state='SOURCE_ONLY_CONTROLLER_DERIVED',derivedActualPrimitives=len(blocks),byteIdenticalPrimitives=sum(a[1]==b[1]for a,b in zip(blocks,actual)),stageExecuted=False)))
