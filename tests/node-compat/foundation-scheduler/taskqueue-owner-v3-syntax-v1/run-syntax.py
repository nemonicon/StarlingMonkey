#!/usr/bin/env python3
"""One approved diagnostic TU syntax check; never recompile the other four TUs."""
from pathlib import Path
import hashlib,json,subprocess
HERE=Path(__file__).resolve().parent
V3=HERE.parent/'taskqueue-owner-v3';V2=HERE.parent/'taskqueue-owner-v2'
BASE=HERE.parent/'taskqueue-owner-v2-syntax-v1/results.json'
ROOT=Path('/tmp/starling-node-compat/scheduler-taskqueue-v3-syntax-v1')
def pin(p):return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
def check_packet(root,digest):
 assert pin(root/'index.json')['sha256']==digest
 index=json.loads((root/'index.json').read_text())
 for item in index['files']:assert pin(root/item['path'])['sha256']==item['sha256']
 return index
v2=check_packet(V2,'7d46543bc27bac3f7a1ff20b91446043fd15203283af4455b6a8425fc06f0f4a')
v3=check_packet(V3,'4225a3145ffb9593efb24f90519b0e3c7f8d8637eae24e91ddd58d0fde4aa195')
assert pin(BASE)['sha256']=='8e634a9f65ad13b6710549b0ff02eaff576ae0365b310b6071e04a372229de62'
base=json.loads(BASE.read_text());assert base['allPassed'] and len(base['results'])==5
assert not ROOT.exists(),'Preserve prior results; choose a new versioned runner/root'
ROOT.mkdir()
source=ROOT/'test-extension.UNCOMPILED.cpp';source.write_bytes((V3/source.name).read_bytes())
prior=next(i for i in base['results'] if i['label']=='diagnostic')
args=list(prior['command']);assert args[-1]==prior['source']['path'];args[-1]=str(source)
assert '-fsyntax-only' in args and '-Werror' in args and '-DNDEBUG' in args
assert '-DNODE_COMPAT_INTERNAL_TICKS=1' in args
for item in base['stagedFiles']:assert pin(Path(item['path']))['sha256']==item['sha256']
result=subprocess.run(args,cwd=prior['cwd'],capture_output=True,text=True)
for name,value in [('stdout',result.stdout),('stderr',result.stderr)]:
 (ROOT/(name+'.log')).write_text(value);(HERE/(name+'.log')).write_text(value)
check_packet(V2,'7d46543bc27bac3f7a1ff20b91446043fd15203283af4455b6a8425fc06f0f4a')
check_packet(V3,'4225a3145ffb9593efb24f90519b0e3c7f8d8637eae24e91ddd58d0fde4aa195')
record={'schemaVersion':1,'status':'one-isolated-Release-SDK-diagnostic-syntax-check',
 'passed':result.returncode==0,'exitStatus':result.returncode,'v3Index':pin(V3/'index.json'),
 'v2Index':pin(V2/'index.json'),'priorFiveTuSyntax':pin(BASE),'source':pin(source),
 'command':args,'cwd':prior['cwd'],'compiler':base['compiler'],
 'unchangedStagedHeadersChecked':len(base['stagedFiles']),
 'stdout':pin(ROOT/'stdout.log'),'stderr':pin(ROOT/'stderr.log'),
 'v2AndV3PacketsByteIdentical':True,'unchangedOtherTusRecompiled':False,
 'engineBuilt':False,'guestExecuted':False,'debugFaultOrCrossRealmGuestProbe':False,
 'liveApplied':False,'resetSafeReuse':'OPEN'}
(ROOT/'results.json').write_text(json.dumps(record,indent=2)+'\n')
(HERE/'results.json').write_text(json.dumps(record,indent=2)+'\n')
assert record['passed'],result.stderr
print(json.dumps({'passed':True,'diagnosticsBytes':len(result.stdout)+len(result.stderr),'receiptSha256':pin(HERE/'results.json')['sha256']}))
