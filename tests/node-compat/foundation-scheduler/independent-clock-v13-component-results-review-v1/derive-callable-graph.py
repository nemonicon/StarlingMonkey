"""Pure byte/type/link graph, never compiles or instantiates Wasm."""
from pathlib import Path
import base64,hashlib,json
P=Path(__file__).resolve().parent
g=json.loads((P/'binary-graph.json').read_bytes());js=json.loads((P/'ast.stdout.log').read_bytes())
component=Path(g['component']['path']).read_bytes();text=Path(js['source']['path']).read_text()
def sha(b):return hashlib.sha256(b).hexdigest()
class R:
 def __init__(self,b):self.b=b;self.p=0
 def byte(self):assert self.p<len(self.b);x=self.b[self.p];self.p+=1;return x
 def u(self):
  out=0
  for i in range(5):
   b=self.byte();out|=(b&127)<<(7*i)
   if b<128:return out
  raise AssertionError('u32 too long')
 def done(self):assert self.p==len(self.b)
def value(r):
 b=r.byte();assert b in [0x7f,0x7e,0x7d,0x7c,0x7b,0x70,0x6f];return{0x7f:'i32',0x7e:'i64',0x7d:'f32',0x7c:'f64',0x7b:'v128',0x70:'funcref',0x6f:'externref'}[b]
modules=[]
for i,m in enumerate(g['modules']):
 sec=m['componentSection'];b=component[sec['offset']:sec['offset']+sec['bytes']];assert sha(b)==m['moduleSha256'];types=[];locals=[]
 for s in m['sections']:
  r=R(b[s['offset']:s['offset']+s['bytes']])
  if s['id']==1:
   count=r.u();assert count<100000
   for _ in range(count):
    assert r.byte()==0x60;params=[value(r)for _ in range(r.u())];results=[value(r)for _ in range(r.u())];types.append(dict(params=params,results=results))
   r.done()
  elif s['id']==3:locals=[r.u()for _ in range(r.u())];r.done()
 imports=[x for x in m['imports']if x['kind']=='function'];fidx=[x['typeIndex']for x in imports]+locals
 imported=[dict(x,signature=types[x['typeIndex']])for x in imports]
 exported=[dict(x,signature=types[fidx[x['index']]])for x in m['exports']if x['kind']==0]
 modules.append(dict(index=i,sha256=m['moduleSha256'],bytes=len(b),functionTypeCount=len(types),functionImports=imported,functionExports=exported,startSectionPresent=any(x['id']==8 for x in m['sections'])))
physical=Path('/private/tmp/starling-node-compat/clock-v13-component-v1/transpiled/clock_v13.core.wasm').read_bytes();assert sha(physical)==modules[0]['sha256']
assert len(js['inlineModules'])==3
for i,v in enumerate(js['inlineModules'],1):
 encoded=json.loads(text[v['literalStart']:v['literalEnd']].replace("'",'"'))
 decoded=base64.b64decode(encoded+'='*((-len(encoded))%4),validate=True)
 assert sha(decoded)==v['sha256']==modules[i]['sha256']and len(decoded)==v['bytes']==modules[i]['bytes']
roots={r['name']:r for r in g['rootImports']};expected=['wasi:clocks/monotonic-clock@0.2.10','wasi:clocks/wall-clock@0.2.10','wasi:io/poll@0.2.10'];assert sorted(roots)==expected
assert roots[expected[0]]['functions']==['now','subscribe-instant','subscribe-duration']and roots[expected[1]]['functions']==['now']and roots[expected[2]]['functions']==['poll']
assert g['componentTypes'][1]['alias']=={'sort':[3],'kind':0,'instance':0,'name':'pollable'}
mono=roots[expected[0]]['typeDefinition']['declarations'];assert any(x=={'kind':'alias','alias':{'sort':[3],'kind':2,'outer':1,'index':1}}for x in mono)
assert g['componentTypes'][4]['alias']=={'sort':[3],'kind':0,'instance':0,'name':'pollable'}
drop=next(x for x in g['canonicalDefinitions']if x['kind']=='resource-drop');assert drop['typeIndex']==4
export=g['exports'];assert len(export)==1 and export[0]['name']=='run'and export[0]['sort']==[1]
f=g['componentFunctions'][export[0]['index']];assert f['kind']=='lift'and g['componentTypes'][f['typeIndex']]=={'kind':'function','params':[],'results':[-13]}
rootfunctions=[dict(interface=x['name'],functions=x['functions'],types=x['types'])for x in g['rootImports']]
assert not any(any(z in r['name']for z in ['preview1','@0.2.0','stderr','streams','error'])for r in g['rootImports'])
bridge=next(x for x in g['importBindings']if x['module']==0 and x['importModule']=='wasi_snapshot_preview1');assert bridge['importName']=='clock_time_get'and bridge['resolvedFunctionOrigin']['target']=={'kind':'core-module-export','module':1,'instance':9,'name':'clock_time_get'}
adapter=[x for x in g['importBindings']if x['module']==1 and x['importModule'].startswith('wasi:clocks/')]
assert len(adapter)==2
assert all(x['resolvedFunctionOrigin']['kind']=='root-function' or x['resolvedFunctionOrigin']['target']['kind']=='root-function'for x in adapter)
out=dict(schemaVersion=1,component=g['component'],rootInterfaces=expected,rootCallableFunctions=rootfunctions,pollableResourceSharedByPollAndMonotonicClock=True,pollableCanonicalDrop=True,publicAbi={'run':'() -> string'},embeddedModules=modules,physicalCoreWholeBytesEqualModule0=True,allThreeInlineCoreBytesEqualComponentModules=True,preview1ExternalComponentImport=False,internalPreview1ClockBridgePresent=True,internalAdapterClockLabelsVersion='0.2.0',externalClockInterfacesVersion='0.2.10',clockBridge=bridge,adapterClockBindings=adapter,allCanonicalCoreBindings=g['importBindings'],noExternalStderrStreamsError=True,callableNotMerelyTypeOnly=True,hostCallsActuallyObserved=False,componentOrEngineInstantiated=False)
(P/'callable-type-core-graph.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'rootInterfaces':expected,'callableFunctions':sum(len(x['functions'])for x in rootfunctions),'resourceDrop':True,'modules':len(modules),'physicalPlusInlineEquality':True,'externalPreview1':False,'internalPreview1Bridge':True,'targetExecuted':False}))
