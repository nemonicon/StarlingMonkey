"""Whole finite core DATA audit. No interpreter, encoder or guest invocation."""
from pathlib import Path
import hashlib,importlib.util
_spec=importlib.util.spec_from_file_location('next_adapter_core_data',Path(__file__).resolve().parent/'core_data.py')
core_data=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(core_data)

def audit(original,candidate):
    assert len(original)==53512 and hashlib.sha256(original).hexdigest()=='667907826ed62123beb0c1817969dcf32527a02b4bcbbbb10dc1dcafaba12ecc'
    old,new=core_data.decode(original),core_data.decode(candidate)
    assert len(old['imports'])==64 and len(old['functions'])==93
    removed={49,50,51,52,53,54,56}
    before=[x for x in old['imports']if x['kind']==0]
    after=[x for x in new['imports']if x['kind']==0]
    keep=[x for x in before if x['functionIndex']not in removed]
    targets=[x for x in before if x['functionIndex']in removed]
    assert len(after)==56 and len(targets)==7
    assert after==[dict(x,functionIndex=i)for i,x in enumerate(keep)]
    assert [x for x in old['imports']if x['kind']!=0]==[x for x in new['imports']if x['kind']!=0]
    mapping={x['functionIndex']:i for i,x in enumerate(keep+targets)}
    mapping.update({i:i for i in range(63,156)})
    assert len(mapping)==len(set(mapping.values()))==156
    assert old['types']==new['types'] and old['tables']==new['tables']and old['memories']==new['memories']
    assert new['functions']==[x['typeIndex']for x in targets]+old['functions']
    assert len(new['bodies'])==100
    terminal_none=([],[(32,[0]),(65,[0]),(58,[0,0]),(11,[])])
    trap=([],[(0,[]),(11,[])])
    assert new['bodies'][:7]==[terminal_none,trap,terminal_none,trap,terminal_none,trap,trap]
    def mapped(ops):return [(op,[mapping[a[0]]]if op in(16,18,210)else a)for op,a in ops]
    for i,(prior,actual)in enumerate(zip(old['bodies'],new['bodies'][7:]),63):
        locals_,ops=prior
        if i==142:
            assert len(ops)==245 and ops[10]==(16,[54]) and ops[32]==(16,[55])
            ops=ops[:10]+[(32,[2]),(65,[2]),(54,[2,8])]+ops[32:]
            assert len(ops)==226
        assert actual==(locals_,mapped(ops)),i
    assert [(v,m,mapped(e))for v,m,e in old['globals']]==new['globals']
    assert [dict(x,index=mapping[x['index']]if x['kind']==0 else x['index'])for x in old['exports']]==new['exports']
    old_custom=[(k,b)for k,b in old['custom']if k!='name'];new_custom=[(k,b)for k,b in new['custom']if k!='name']
    assert old_custom==new_custom
    metadata=[b for k,b in new_custom if k.startswith('component-type:')];assert len(metadata)==1
    clocks=[x for x in after if x['module'].startswith('wasi:clocks/')]
    poll=[x for x in after if x['module'].startswith('wasi:io/poll@')]
    stdio=[x for x in after if x['module'].startswith(('wasi:cli/stdout@','wasi:cli/stderr@'))]
    filesystem=[x for x in after if x['module'].startswith(('wasi:filesystem/types@','wasi:filesystem/preopens@'))]
    rng=[x for x in after if x['module'].startswith('wasi:random/random@')]
    assert len(clocks)==6 and len(poll)==2 and len(stdio)==2 and len(rng)==1
    assert len(filesystem)==len([x for x in before if x['module'].startswith(('wasi:filesystem/types@','wasi:filesystem/preopens@'))])
    assert not any(x['module'].startswith(('wasi:cli/stdin@','wasi:cli/terminal-','wasi:cli/exit@'))for x in after)
    return dict(schemaVersion=1,coreDataAuditPassed=True,functionImports=56,locals=100,totalFunctions=156,
      originalBodiesCompared=93,originalBodiesIdenticalWithMapping=92,constructorChangedOnly=True,
      newCanonicalNoneStubs=3,newDefensiveTrapStubs=4,typeCount=len(new['types']),exportCount=len(new['exports']),
      globalCount=len(new['globals']),allLocalsTypesPreserved=True,allFunctionReferencesMapped=True,
      originalConstructorInstructions=245,newConstructorInstructions=226,constructorPrefixSame=10,constructorTailSame=213,
      nonDebugCustomSectionsIdentical=True,metadataSha256=hashlib.sha256(metadata[0]).hexdigest(),metadataBytes=len(metadata[0]),
      functionMapping={str(k):v for k,v in sorted(mapping.items())},retainedClocks=clocks,retainedPoll=poll,
      retainedStdio=stdio,retainedFilesystem=filesystem,retainedSecureRandom=rng,
      remainingOriginalP2Versions=sorted(set(x['module']for x in after if x['module'].startswith('wasi:'))),
      finalSelected13ComponentVersionResourceClosureProved=False,adapterOrGuestExecuted=False)
