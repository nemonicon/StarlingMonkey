"""Independent finite core-binary DATA comparison; no Wasm runtime/tool calls."""
import hashlib
class R:
    def __init__(self,b):self.b=b;self.p=0
    def byte(self):assert self.p<len(self.b);v=self.b[self.p];self.p+=1;return v
    def take(self,n):assert 0<=n<=len(self.b)-self.p;v=self.b[self.p:self.p+n];self.p+=n;return v
    def u(self):
        n=0
        for i in range(5):
            x=self.byte();n|=(x&127)<<(i*7)
            if x<128:assert n<=0xffffffff;return n
        raise AssertionError('u32 bound')
    def s(self,bits):
        n=0;shift=0
        while shift<bits+7:
            x=self.byte();n|=(x&127)<<shift;shift+=7
            if x<128:
                if x&64:n-=1<<shift
                assert -(1<<(bits-1))<=n<1<<(bits-1);return n
        raise AssertionError('signed bound')
    def name(self):return self.take(self.u()).decode('utf8')
    def end(self):assert self.p==len(self.b)
def sha(b):return hashlib.sha256(b).hexdigest()
def limits(r):
    flags=r.u();assert flags in(0,1);return [flags,r.u()]+([r.u()]if flags else[])
def expression(r,constant=False):
    out=[]
    while r.p<len(r.b):
        op=r.byte();a=[]
        if op in(2,3,4):a=[r.s(33)]
        elif op in(12,13,16,18,32,33,34,35,36,37,38,210,213,214):a=[r.u()]
        elif op==14:a=[r.u()];assert a[0]<65536;a.extend(r.u()for _ in range(a[0]+1))
        elif op in(17,19):a=[r.u(),r.u()]
        elif op==28:a=[r.u()];assert a[0]<16;a.extend(r.byte()for _ in range(a[0]))
        elif 40<=op<=62:a=[r.u(),r.u()]
        elif op in(63,64):a=[r.u()]
        elif op==65:a=[r.s(32)]
        elif op==66:a=[r.s(64)]
        elif op in(67,68):a=[r.take(4 if op==67 else 8)]
        elif op==208:a=[r.s(33)]
        elif op==252:
            sub=r.u();assert sub<=17;count=0 if sub<8 else(2 if sub in(8,10,12,14)else 1);a=[sub]+[r.u()for _ in range(count)]
        else:assert op in(0,1,5,11,15,26,27,209,211,212)or 69<=op<=196,hex(op)
        out.append((op,a))
        if constant and op==11:return out
    assert not constant;return out
def decode(data):
    assert data[:8]==b'\0asm\1\0\0\0'and len(data)<1024*1024
    r=R(data[8:]);sections=[];p={};custom=[]
    while r.p<len(r.b):
        kind=r.byte();payload=r.take(r.u());sections.append((kind,payload))
        if kind==0:
            t=R(payload);name=t.name();custom.append((name,t.take(len(t.b)-t.p)))
        else:assert kind not in p;p[kind]=payload
    assert set(p)<={1,2,3,4,5,6,7,10}
    types=[];t=R(p[1])
    for _ in range(t.u()):
        assert t.byte()==96;params=[t.byte()for _ in range(t.u())];results=[t.byte()for _ in range(t.u())];types.append((params,results))
    t.end();imports=[];fid=0;t=R(p[2])
    for _ in range(t.u()):
        x=dict(module=t.name(),name=t.name(),kind=t.byte())
        if x['kind']==0:x.update(typeIndex=t.u(),functionIndex=fid);fid+=1
        else:assert x['kind']==2;x['limits']=limits(t)
        imports.append(x)
    t.end();t=R(p[3]);functions=[t.u()for _ in range(t.u())];t.end()
    tables=[];memories=[]
    if 4 in p:
        t=R(p[4]);tables=[(t.byte(),limits(t))for _ in range(t.u())];t.end()
    if 5 in p:
        t=R(p[5]);memories=[limits(t)for _ in range(t.u())];t.end()
    globals=[]
    if 6 in p:
        t=R(p[6])
        for _ in range(t.u()):globals.append((t.byte(),t.byte(),expression(t,True)))
        t.end()
    t=R(p[7]);exports=[dict(name=t.name(),kind=t.byte(),index=t.u())for _ in range(t.u())];t.end()
    t=R(p[10]);bodies=[]
    for _ in range(t.u()):
        b=R(t.take(t.u()));local=[]
        for _ in range(b.u()):n=b.u();v=b.byte();assert len(local)+n<16384;local.extend([v]*n)
        bodies.append((local,expression(b)));b.end()
    t.end();assert len(bodies)==len(functions)
    return dict(types=types,imports=imports,functions=functions,tables=tables,memories=memories,globals=globals,exports=exports,bodies=bodies,sections=sections,custom=custom)
def compare(original,normal,pruned):
    o,n,p=map(decode,(original,normal,pruned))
    assert len(o['imports'])==64 and o['imports'][0]['kind']==2
    assert n['imports']==o['imports'][1:]+o['imports'][:1]
    assert [(k,b)for k,b in o['sections']if k!=2]==[(k,b)for k,b in n['sections']if k!=2]
    before=n['imports'][:-1];after=p['imports'][:-1]
    assert len(before)==63 and len(after)==49 and n['imports'][-1]==p['imports'][-1]
    retained={(x['module'],x['name'])for x in after};targets=[x for x in before if(x['module'],x['name'])not in retained];keep=[x for x in before if(x['module'],x['name'])in retained]
    assert len(targets)==14 and len(keep)==49
    assert after==[dict(x,functionIndex=i)for i,x in enumerate(keep)]
    assert all(x['module'].startswith(('wasi:io/streams@','wasi:io/error@','wasi:cli/stdin@','wasi:cli/stdout@','wasi:cli/stderr@'))for x in targets)
    mapping={x['functionIndex']:i for i,x in enumerate(keep+targets)};mapping.update({i:i for i in range(63,63+len(n['functions']))})
    assert len(mapping)==len(set(mapping.values()))==156
    assert n['types']==p['types']and n['tables']==p['tables']and n['memories']==p['memories']
    assert p['functions']==[x['typeIndex']for x in targets]+n['functions']
    assert p['bodies'][:14]==[([],[(0,[]),(11,[])])]*14
    def mapped(ops):return [(op,[mapping[a[0]]]if op in(16,18,210)else a)for op,a in ops]
    assert len(p['bodies'])==len(n['bodies'])+14
    for old,new in zip(n['bodies'],p['bodies'][14:]):assert old[0]==new[0]and mapped(old[1])==new[1]
    assert [(v,m,mapped(e))for v,m,e in n['globals']]==p['globals']
    assert [dict(x,index=mapping[x['index']]if x['kind']==0 else x['index'])for x in n['exports']]==p['exports']
    nc={k:b for k,b in n['custom']if k!='name'};pc={k:b for k,b in p['custom']if k!='name'}
    assert nc==pc and len(nc)==len(n['custom'])-1 and len(pc)==len(p['custom'])-1
    metadata=[b for k,b in pc.items()if k.startswith('component-type:')];assert len(metadata)==1
    clocks=[x for x in after if x['module'].startswith('wasi:clocks/')];poll=[x for x in after if x['module'].startswith('wasi:io/poll@')]
    assert len(clocks)==6 and len(poll)==2
    return dict(normalizationOnlyImportEntryOrder=True,typesCompared=len(n['types']),originalFunctionsCompared=len(n['functions']),convertedUnreachableStubs=14,totalFunctions=156,retainedFunctionImports=49,exportsCompared=len(p['exports']),globalsCompared=len(p['globals']),allOriginalInstructionsAndImmediatesCompared=True,originalInstructionCount=sum(len(b[1])for b in n['bodies']),functionReferenceMapping={str(k):v for k,v in mapping.items()},retainedClocks=clocks,retainedPoll=poll,convertedImports=targets,nonDebugCustomPayloadsIdentical=True,encodedMetadataSha256=sha(metadata[0]),encodedMetadataBytes=len(metadata[0]),metadataPayload=metadata[0])
