"""Independent pure model negatives against copied DATA; never mutate actual files."""
from pathlib import Path
import copy,json,hashlib
import artifact_model as M
HERE=Path(__file__).resolve().parent;F=Path(M.FREEZE)
mraw=(F/'gc-off.engine.wasm.build.json').read_bytes();fraw=(F/'gc-off-freeze-receipt.json').read_bytes();assert hashlib.sha256(mraw).hexdigest()=='90c3f45e439c116aaa526167b6fc26122a38c7da702984d53dd3e35fde5304c8';assert hashlib.sha256(fraw).hexdigest()=='7567f60f9212f28c8d5052de4e0e395373f5dd0ff08149f497677846591bf669'
m=json.loads(mraw);f=json.loads(fraw);policy=json.loads((Path(M.TOOLS).parent/'policy.json').read_bytes());cases=[]
for name,mutator in [('wrong gc variant',lambda x:x.update(gcStress=False)),('runtime entropy projection',lambda x:x.update(entropyPolicy='runtime-only')),('normal build path projection',lambda x:x.update(enginePath='/private/tmp/normal.wasm')),('lost native source',lambda x:x['sourceManifest'].pop()),('duplicate native source',lambda x:x['sourceManifest'].__setitem__(0,x['sourceManifest'][1])),('synthetic owner runtime proof',lambda x:x['cryptoKeyOwnershipPolicy'].update(runtimeValidation=True)),('promoted codec backend',lambda x:x['zlibPolicy'].update(runtimeBackendProof=dict(verified=True,version='fake',vernum=1)))]:
    changed=copy.deepcopy(m);mutator(changed)
    try:M.metadata(changed,policy)
    except(AssertionError,KeyError,TypeError):cases.append(dict(name=name,rejected=True))
    else:raise AssertionError('independent metadata model accepted '+name)
for name,key,value in [('failed receipt state','state','partial'),('wrong frozen label','label','normal-off'),('wrong native count','nativeInputsVerified',350),('invented backend proof','runtimeBackendProof',dict(verified=True,version='fake',vernum=1)),('projected original path','originalEngine','/tmp/wrong.wasm'),('engine executed','guestExecutedByHelper',True)]:
    changed=copy.deepcopy(f);changed[key]=value
    try:M.receipt(changed,m,hashlib.sha256(mraw).hexdigest(),m['engineSha256'],m['engineBytes'])
    except(AssertionError,KeyError,TypeError):cases.append(dict(name=name,rejected=True))
    else:raise AssertionError('independent receipt model accepted '+name)
with(HERE/'negative-data-results.json').open('x')as out:out.write(json.dumps(dict(schemaVersion=1,state='PURE_GC_ARTIFACT_DATA_NEGATIVES_PASSED',cases=cases,checks=M.CHECKS,actualFilesMutated=False,ownerActionsInvoked=False),indent=2)+'\n')
print(json.dumps(dict(negativeCases=len(cases),allRejected=True,ownerActionsInvoked=False)))
