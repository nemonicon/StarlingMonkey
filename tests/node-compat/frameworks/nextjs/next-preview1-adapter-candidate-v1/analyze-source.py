"""Authoring DATA/model writer only. No Wasm interpreter/encoder/tool invocation."""
from pathlib import Path
import hashlib,json,re,sys
HERE=Path(__file__).resolve().parent
assert sys.dont_write_bytecode
refs=json.loads((HERE/'references.json').read_text())
def checked(row):
    b=Path(row['path']).read_bytes()
    assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'];return b
assert (HERE/'core_data.py').read_bytes()==checked(refs['coreReaderDonor'])
import core_data
raw=checked(refs['normalizedInput']);d=core_data.decode(raw)
assert len(d['imports'])==64 and len(d['functions'])==93 and d['tables']==[(112,[1,1,1])]
old=d['bodies'][142-63][1]
def constructor_plan(ops):
    assert len(ops)==245 and ops[10]==(16,[54]) and ops[11]==(33,[4])
    assert ops[22]==(65,[1]) and ops[23]==(54,[2,8]) and ops[32]==(16,[55])
    return ops[:10]+[(32,[2]),(65,[2]),(54,[2,8])]+ops[32:]
new=constructor_plan(old)
assert len(new)==226 and old[:10]==new[:10] and old[32:]==new[13:]
assert sum(op==16 and a==[54] for _,ops in d['bodies'] for op,a in ops)==1
assert not any(op in (17,19,210) for _,ops in d['bodies'] for op,a in ops)
assert not any(op==16 and a==[54] for op,a in new)
# Actual adapter_open_badfd creates Descriptor discriminant2; actual drops only
# access owned stream handles for discriminant1. This is static instruction DATA,
# not an interpreter run or a reconstruction of missing primary Rust source.
bad=d['bodies'][63-63][1];drop=d['bodies'][113-63][1]
assert [(32,[1]),(65,[2]),(54,[2,16])] == bad[27:30]
assert [(32,[0]),(40,[2,0]),(65,[1]),(71,[])]==drop[1:5]
source=checked(refs['currentGeneratedBindings']).decode()
pattern=r'__attribute__\(\(__import_module__\("([^"]+)"\), __import_name__\("([^"]+)"\)\)\)\s*extern ([^;]+?) __wasm_import_\w+\(([^;]*?)\);'
current={}
def flat(t):
    t=t.strip()
    if '*'in t:return 127
    # Generated resource-drop declarations name their int32 parameter.
    t=re.sub(r'\s+[a-zA-Z_][a-zA-Z_0-9]*$','',t) if re.fullmatch(r'(?:u?int(?:32|64)_t|size_t|bool)\s+\w+',t) else t
    if t in ('int32_t','uint32_t','size_t','bool'):return 127
    if t in ('int64_t','uint64_t'):return 126
    if t=='void':return None
    raise ValueError('Unrecognized generated C primitive: '+t)
for module,name,result,args in re.findall(pattern,source,re.S):
    current[module,name]=([flat(x) for x in args.split(',')] if args and args!='void' else [],[] if result=='void' else [flat(result)])
removed={49,50,51,52,53,54,56};abi=[]
for x in d['imports']:
    if 'functionIndex' not in x or x['functionIndex'] in removed or x['module']=='__main_module__':continue
    compared=x['module'].split('@')[0]+'@0.2.10';typ=d['types'][x['typeIndex']]
    actual=current.get((compared,x['name']));assert actual==typ,(x,actual,typ)
    abi.append({'importIndex':x['functionIndex'],'originalModule':x['module'],'name':x['name'],
                'oldFlatType':typ,'newGeneratedCFlatType':actual,'comparedModuleOnly':compared,'same':True})
assert len(abi)==55
negatives=[]
for index,value in [(10,(16,[55])),(11,(33,[3])),(22,(65,[2])),(23,(54,[2,16])),(32,(16,[45]))]:
    copy=old.copy();copy[index]=value
    try:constructor_plan(copy)
    except AssertionError:negatives.append({'mutatedIndex':index,'refused':True})
    else:raise AssertionError('mutated constructor admitted')
try:constructor_plan(old+[old[-1]])
except AssertionError:negatives.append({'bodyLengthMutation':True,'refused':True})
else:raise AssertionError('wrong length admitted')
# Pure canonical option-none model: only tag0 is written; no terminal resource
# handle is returned. These bytes are synthetic and never invoke an adapter.
for payload in (b'ABCD',b'\xff'*4,b'\0'*4):
    memory=bytearray(b'\x01abc'+payload);memory[0]=0
    assert memory[0]==0 and memory[4:]==payload
plan={'schemaVersion':1,'sourceOnly':True,'normalizedInput':refs['normalizedInput'],
 'inputFunctionImports':63,'inputLocals':93,'inputTotalFunctions':156,'inputMemoryImports':1,
 'constructor':{'originalFunctionIndex':142,'type':d['types'][d['functions'][142-63]],
   'oldInstructionCount':245,'removedInstructionRangeHalfOpen':[10,32],
   'removedOps':old[10:32],'newOps':new[10:13],'newInstructionCount':226,
   'samePrefixInstructions':10,'sameTailInstructions':213,'actualBadfdTagEvidence':bad[27:30],
   'dropHandleGuardEvidence':drop[1:5],'privateRustLayoutSourceAvailable':False,
   'layoutEvidence':'Exact pinned binary constructor/open_badfd/drop data; no generic Rust layout inference'},
 'removedImports':[x for x in d['imports'] if x.get('functionIndex')in removed],
 'retainedImports':[x for x in d['imports'] if 'functionIndex'in x and x['functionIndex']not in removed],
 'plannedFunctionImports':56,'plannedLocals':100,'plannedTotalFunctions':156,
 'flatAbiComparedPublicImports':abi,'flatAbiMismatches':[],
 'primitiveAbiSource':'Actual generated0.2.10 C bindings in wasm32 ABI; version suffix compared only, NEVER rewritten',
 'fullCanonicalResourceEnumCompatibilityProved':False,'finalVersionMergeAnd13InterfaceGraphProved':False,
 'models':{'constructorPositive':1,'constructorNegatives':negatives,'canonicalNoneSyntheticPayloads':3},
 'actualAdapterTransformed':False,'actualRustToolExecuted':False,'adapterOrGuestExecuted':False}
(HERE/'data-analysis.json').write_text(json.dumps(plan,indent=2)+'\n')
print(json.dumps({'flatAbiCompared':55,'mismatches':0,'constructorPlan':True,'constructorNegativeCases':6,
 'syntheticNoneModels':3,'actualAdapterOrToolExecuted':False}))
