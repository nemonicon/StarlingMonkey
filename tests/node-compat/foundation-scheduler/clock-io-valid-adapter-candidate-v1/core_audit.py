"""Finite independent core Wasm DATA decoder/comparison; never executes Wasm."""
import hashlib

def need(v,m):
    if not v:raise ValueError(m)
class Reader:
    def __init__(self,b):self.b=b;self.p=0
    def byte(self):need(self.p<len(self.b),'bounded byte');x=self.b[self.p];self.p+=1;return x
    def take(self,n):need(0<=n<=len(self.b)-self.p,'bounded slice');x=self.b[self.p:self.p+n];self.p+=n;return x
    def u(self):
        n=0
        for shift in range(0,35,7):
            x=self.byte();n|=(x&127)<<shift
            if x<128:need(n<=0xffffffff,'u32 range');return n
        raise ValueError('u32 LEB bound')
    def s(self,bits=64):
        n=0;shift=0
        while shift<bits+7:
            x=self.byte();n|=(x&127)<<shift;shift+=7
            if x<128:
                if x&64:n|=-(1<<shift)
                need(-(1<<(bits-1))<=n<(1<<(bits-1)),'signed range');return n
        raise ValueError('signed LEB bound')
    def name(self):return self.take(self.u()).decode('utf8')
    def done(self):need(self.p==len(self.b),'complete payload')
def limits(r):
    flags=r.u();need(flags in[0,1],'finite unshared32 limits');out=[flags,r.u()]
    if flags:out.append(r.u())
    return out

def ops(r,stop_at_end=False):
    result=[]
    while r.p<len(r.b):
        op=r.byte();args=[]
        if op in[2,3,4]:args=[r.s(33)]
        elif op in[0x0c,0x0d,0x10,0x12,0x20,0x21,0x22,0x23,0x24,0x25,0x26,0xd2,0xd5,0xd6]:args=[r.u()]
        elif op==0x0e:
            n=r.u();need(n<=65536,'bounded branch table');args=[n]+[r.u()for _ in range(n+1)]
        elif op in[0x11,0x13]:args=[r.u(),r.u()]
        elif op==0x1c:
            n=r.u();need(n<=16,'finite select types');args=[n]+[r.byte()for _ in range(n)]
        elif 0x28<=op<=0x3e:args=[r.u(),r.u()]
        elif op in[0x3f,0x40]:args=[r.u()]
        elif op==0x41:args=[r.s(32)]
        elif op==0x42:args=[r.s(64)]
        elif op==0x43:args=[r.take(4).hex()]
        elif op==0x44:args=[r.take(8).hex()]
        elif op==0xd0:args=[r.s(33)]
        elif op==0xfc:
            sub=r.u();need(sub<=17,'finite bulk/saturating opcode set');count=0 if sub<=7 else(2 if sub in[8,10,12,14]else 1);args=[sub]+[r.u()for _ in range(count)]
        elif op in[0,1,5,0x0b,0x0f,0x1a,0x1b,0xd1,0xd3,0xd4]or 0x45<=op<=0xc4:pass
        else:raise ValueError('Unreviewed opcode '+hex(op))
        result.append([op,args])
        if stop_at_end and op==0x0b:return result
    need(not stop_at_end,'terminated constant expression');return result

def audit_debug_names(payload,total_functions,types,tables,memories,globals_count,function_types,bodies,imports):
    r=Reader(payload);subsections=[];seen=set()
    def names(t,bound):
        count=t.u();need(count<=65536,'bounded name map');keys=set()
        for _ in range(count):
            index=t.u();need(index not in keys and index<bound,'debug name index bound/unique');keys.add(index);t.name()
        return count
    imported_types=[x['typeIndex']for x in imports if x['kind']==0]
    all_types=imported_types+function_types
    while r.p<len(r.b):
        kind=r.byte();t=Reader(r.take(r.u()));need(kind not in seen and kind<=11,'finite unique reviewed debug-name subsection');seen.add(kind)
        if kind==0:t.name()
        elif kind in[1,4,5,6,7,8,9,11]:names(t,{1:total_functions,4:len(types),5:tables,6:memories,7:globals_count,8:0,9:0,11:0}[kind])
        elif kind in[2,3]:
            count=t.u();need(count<=total_functions,'finite indirect debug map');function_ids=set()
            for _ in range(count):
                index=t.u();need(index<total_functions and index not in function_ids,'debug function name reference');function_ids.add(index)
                if kind==2:
                    ty=all_types[index];bound=len(types[ty]['params'])+(len(bodies[index-len(imported_types)]['locals'])if index>=len(imported_types)else 0)
                else:bound=sum(op in[2,3,4]for op,args in bodies[index-len(imported_types)]['ops'])if index>=len(imported_types)else 0
                names(t,bound)
        elif kind==10:
            # No GC struct field types are in this pinned simple-func type cut.
            need(t.u()==0,'no struct field name references')
        t.done();subsections.append(kind)
    return subsections

def decode(data):
    need(len(data)<=1024*1024 and data[:8]==b'\0asm\1\0\0\0','bounded core module')
    r=Reader(data[8:]);sections=[];custom=[];payloads={}
    while r.p<len(r.b):
        kind=r.byte();payload=r.take(r.u());sections.append(dict(id=kind,bytes=len(payload),sha256=hashlib.sha256(payload).hexdigest()))
        if kind==0:
            c=Reader(payload);name=c.name();custom.append(dict(name=name,data=c.take(len(c.b)-c.p)))
        else:need(kind not in payloads and kind in[1,2,3,4,5,6,7,8,9,10,11,12],'unique reviewed core section');payloads[kind]=payload
    types=[]
    if 1 in payloads:
        t=Reader(payloads[1]);count=t.u();need(count<=4096,'finite types')
        for _ in range(count):
            need(t.byte()==0x60,'simple function types only');n=t.u();need(n<=128,'finite parameters');params=[t.byte()for _ in range(n)];n=t.u();need(n<=16,'finite results');results=[t.byte()for _ in range(n)];types.append(dict(params=params,results=results))
        t.done()
    imports=[];function_types=[];memories=[];tables=[];globals=[];exports=[];bodies=[]
    if 2 in payloads:
        t=Reader(payloads[2]);count=t.u();need(count<=256,'finite imports')
        for _ in range(count):
            x=dict(module=t.name(),name=t.name(),kind=t.byte())
            if x['kind']==0:x['typeIndex']=t.u();need(x['typeIndex']<len(types),'import type reference');x['functionIndex']=sum(z['kind']==0 for z in imports)
            elif x['kind']==2:x['limits']=limits(t)
            else:raise ValueError('Unreviewed import kind')
            imports.append(x)
        t.done()
    if 3 in payloads:
        t=Reader(payloads[3]);function_types=[t.u()for _ in range(t.u())];t.done();need(all(i<len(types)for i in function_types),'all defined type references')
    if 4 in payloads:
        t=Reader(payloads[4]);tables=[dict(elementType=t.byte(),limits=limits(t))for _ in range(t.u())];t.done()
    if 5 in payloads:
        t=Reader(payloads[5]);memories=[limits(t)for _ in range(t.u())];t.done()
    if 6 in payloads:
        t=Reader(payloads[6])
        for _ in range(t.u()):globals.append(dict(valueType=t.byte(),mutable=t.byte(),expr=ops(t,True)))
        t.done()
    if 7 in payloads:
        t=Reader(payloads[7]);exports=[dict(name=t.name(),kind=t.byte(),index=t.u())for _ in range(t.u())];t.done();need(len({x['name']for x in exports})==len(exports),'unique exports')
    if 10 in payloads:
        t=Reader(payloads[10])
        for _ in range(t.u()):
            body=Reader(t.take(t.u()));locals=[]
            for _ in range(body.u()):n=body.u();v=body.byte();need(len(locals)+n<=16384,'bounded expanded locals');locals.extend([v]*n)
            bodies.append(dict(locals=locals,ops=ops(body)));body.done()
        t.done();need(len(bodies)==len(function_types),'all code/type bodies paired')
    for k in[8,9,11,12]:need(k not in payloads,'pinned module has no start/elements/data/data-count')
    debug_subsections=[]
    for c in custom:
        if c['name']=='name':debug_subsections=audit_debug_names(c['data'],sum(x['kind']==0 for x in imports)+len(function_types),types,len(tables),sum(x['kind']==2 for x in imports)+len(memories),len(globals),function_types,bodies,imports)
    return dict(sections=sections,types=types,imports=imports,functionTypes=function_types,tables=tables,memories=memories,globals=globals,exports=exports,bodies=bodies,custom=custom,debugNameSubsectionsChecked=debug_subsections)

STREAMS={'[method]input-stream.blocking-read','[method]input-stream.skip','[method]input-stream.blocking-skip','[method]output-stream.blocking-write-and-flush','[method]output-stream.flush','[method]output-stream.write-zeroes','[method]output-stream.blocking-write-zeroes-and-flush','[method]output-stream.splice','[method]output-stream.blocking-splice','[resource-drop]input-stream','[resource-drop]output-stream','[method]input-stream.read','[method]input-stream.subscribe','[method]output-stream.check-write','[method]output-stream.write','[method]output-stream.blocking-flush','[method]output-stream.subscribe'}
ERRORS={'[method]error.to-debug-string','[resource-drop]error'}
def target(x):
    module=x['module'].split('@')[0];name=x['name']
    return x['kind']==0 and((module in['wasi:cli/stdin','wasi:cli/stdout','wasi:cli/stderr']and name in['get-stdin','get-stdout','get-stderr'])or(module=='wasi:io/streams'and name in STREAMS)or(module=='wasi:io/error'and name in ERRORS))
def mapped_ops(value,mapping):
    return [[op,[mapping[a[0]]]if op in[0x10,0x12,0xd2]else a]for op,a in value]
def component_type_payload(data):
    matches=[x['data']for x in decode(data)['custom']if x['name'].startswith('component-type:')]
    need(len(matches)==1 and matches[0][:8]==b'\0asm\x0d\0\x01\0','one encoded component-type metadata payload');return matches[0]

def audit_pair(normalized,pruned):
    need(len(normalized)==53512 and hashlib.sha256(normalized).hexdigest()=='667907826ed62123beb0c1817969dcf32527a02b4bcbbbb10dc1dcafaba12ecc','exact normalized input')
    result=compare_decoded(decode(normalized),decode(pruned))
    result['encodedWitComponentSha256']=hashlib.sha256(component_type_payload(pruned)).hexdigest()
    return result

def compare_decoded(a,b):
    af=[x for x in a['imports']if x['kind']==0];bf=[x for x in b['imports']if x['kind']==0]
    need(len(af)==63 and len(a['imports'])==64 and all(x['kind']==0 for x in a['imports'][:63])and a['imports'][-1]==dict(module='env',name='memory',kind=2,limits=[0,0]),'normalizer import IDs align with function IDs')
    targets=[x for x in af if target(x)];keep=[x for x in af if not target(x)];need(len(targets)==14 and len(keep)==49,'actual14 target imports')
    mapping={x['functionIndex']:i for i,x in enumerate(keep+targets)};mapping.update({i:i for i in range(63,63+len(a['functionTypes']))})
    expected=[dict(x,functionIndex=i)for i,x in enumerate(keep)]+[a['imports'][-1]]
    need(b['imports']==expected and len(bf)==49,'complete retained import identity/type signatures/order and env.memory')
    need(a['types']==b['types']and a['tables']==b['tables']and a['memories']==b['memories'],'all type/table/memory definitions preserved')
    need(b['functionTypes']==[x['typeIndex']for x in targets]+a['functionTypes'],'complete converted and original defined type vector')
    need(len(b['bodies'])==len(a['bodies'])+14,'all original bodies plus14stubs')
    for x in b['bodies'][:14]:need(x==dict(locals=[],ops=[[0,[]],[0x0b,[]]]),'exact unreachable/end stub body')
    for old,new in zip(a['bodies'],b['bodies'][14:]):need(old['locals']==new['locals']and mapped_ops(old['ops'],mapping)==new['ops'],'every original instruction/immediate preserved except declared function-ID remap')
    expected_globals=[dict(x,expr=mapped_ops(x['expr'],mapping))for x in a['globals']];need(b['globals']==expected_globals,'all globals and encoded constant references preserved')
    expected_exports=[dict(x,index=mapping[x['index']]if x['kind']==0 else x['index'])for x in a['exports']];need(b['exports']==expected_exports,'all exports and mapped function references preserved')
    ac={x['name']:x['data']for x in a['custom']if x['name']!='name'};bc={x['name']:x['data']for x in b['custom']if x['name']!='name'};need(len(ac)==len(a['custom'])-1 and len(bc)==len(b['custom'])-1 and ac==bc,'all non-debug custom bytes including encoded WIT aliases preserved')
    clocks=[x for x in keep if x['module'].startswith('wasi:clocks/')];poll=[x for x in keep if x['module'].startswith('wasi:io/poll@')];need(len(clocks)==6 and len(poll)==2,'six clocks and two poll imports preserved')
    return dict(schemaVersion=1,state='CLOCK_IO_PRUNED_CORE_STRUCTURAL_DATA_MATCH_V1',originalFunctionImports=63,retainedFunctionImports=49,convertedTargetImports=14,clocksPreserved=6,pollImportsPreserved=2,allTypesCompared=True,allExportsCompared=True,allOriginalFunctionInstructionsCompared=True,functionIndexMapping={str(k):v for k,v in mapping.items()},convertedImports=targets,nonDebugCustomSectionsByteIdentical=True,coreSemanticValidationByNodeRequired=True,metadataWitDecodeRequired=True,nameSectionIsDebugOnly=True,applicationComponentValidityClaim=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
