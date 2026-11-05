#!/usr/bin/env python3
"""SOURCE preparation: finite read/hash closure only; never package or publish."""
import json,hashlib,os,stat
from pathlib import Path
D=Path(__file__).resolve().parent;P=json.loads((D/'prerequisites.json').read_bytes());F=Path(P['paths']['familyRoot']);rows={};aliases={}
def need(v,m):
 if not v:raise AssertionError(m)
def h(path):
 out=hashlib.sha256()
 with Path(path).open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):out.update(b)
 return out.hexdigest()
def physical(path):
 path=str(path);need(path.startswith('/')and os.path.normpath(path)==path,'Absolute canonical spelling');expected='/private'+path if path.startswith('/tmp/')else path;need(str(Path(path).resolve(strict=True))==expected,'Only documented system/tmp alias');return expected

def add(path,sha=None,size=None,role='source'):
 declared=str(path);path=physical(declared);s=Path(path).lstat();need(stat.S_ISREG(s.st_mode)and not stat.S_ISLNK(s.st_mode),'Ordinary finite source');actual=h(path);need(sha is None or sha==actual,'Source hash drift '+declared);need(size is None or size==s.st_size,'Source byte drift '+declared)
 row=rows.get(path)
 if row:need(row['sha256']==actual and row['bytes']==s.st_size,'Conflicting physical identity')
 else:row={'path':path,'sha256':actual,'bytes':s.st_size,'declaredPaths':[],'roles':[]};rows[path]=row
 if declared not in row['declaredPaths']:row['declaredPaths'].append(declared)
 if role not in row['roles']:row['roles'].append(role)
 return row

ix=json.loads((F/'index.json').read_bytes());need(h(F/'index.json')==P['familyIndex']['sha256'],'Exact existing355 source family')
add(F/'index.json',P['familyIndex']['sha256'],P['familyIndex']['bytes'],'genuine355-original-family-index')
for r in ix['files']:add(F/r['path'],r['sha256'],r['bytes'],'genuine355-original-family-member')
seal=json.loads((F/'input-freeze.json').read_bytes())
for r in seal['inputs']:add(F/r['path']if r['local']else r['path'],r['sha256'],r['bytes'],'original-family-direct-consumed-input')
context=json.loads((F/'tool-context.json').read_bytes());need(len(context['toolTrees'])==2 and len(context['toolLinks'])==22 and len(context['inputs'])==4892,'Exact reviewed physical tool inventory')
for r in context['inputs']:add(r['path'],r['sha256'],r['bytes'],'complete-physical-Node-Jco-packager-toolchain')
for k in ['node','wasmTools']:add(P[k]['path'],P[k]['sha256'],P[k]['bytes'],k+'-public-tool')
for r in P.values():
 if isinstance(r,dict)and set(['path','sha256','bytes'])<=set(r):add(r['path'],r['sha256'],r['bytes'],'finite-provenance-reference')
# Native runtime tuple: all genuine frozen copies and the selected SDK reference.
pins=json.loads(Path(P['reviewedPins']['path']).read_bytes());pin=pins['variants']['normal-runtime'];need(pin['engineSha256']==P['normalRuntimeEngineSha256']and pin['sourceFiles']==355 and pin['reviewRequired']is False,'Exact genuine RuntimeOnly355')
for r in pin['frozenFiles']:add(r['path'],r['sha256'],r['bytes'],'selected-normal-runtime-frozen-copy')
add(pin['freezeReceiptPath'],pin['freezeReceiptSha256'],None,'selected-normal-runtime-freeze-receipt')
freeze=json.loads(Path(pin['freezeReceiptPath']).read_bytes())
for r in freeze['dependencyReferences']:add(r['path'],r['sha256'],r['bytes'],'selected-SDK-reference-not-copy')
for r in freeze['toolDependencyClosure']:add(Path(P['nativeConfiguredSourceRoot'])/r['path'],r['sha256'],r['bytes'],'actual-configured-native-tool767')
metadata=json.loads(Path(pin['enginePath']+'.build.json').read_bytes());need(len(metadata['sourceManifest'])==355,'Unprojected355 source manifest')
for r in metadata['sourceManifest']:
 for root in [P['nativeConfiguredSourceRoot'],P['nativeFrozenSourceRoot']]:add(Path(root)/r['path'],r['sha256'],None,'actual-configured-and-frozen-native355')
for k in ['baselineEntry','originalHandler','classicChecks','classicNodeOracle','worldSource']:add(P['paths'][k],None,None,'actual-HTTP-body-or-oracle-source')
# Exact package/adapter/WIT data physically reopened by the build code.
pack=Path(P['paths']['packagingRoot']);wit=pack/'host-apis/wasi-0.2.10/wit/deps';names=sorted(p.name for p in wit.iterdir());expected=sorted(['wasi-cli-0.2.10','wasi-clocks-0.2.10','wasi-filesystem-0.2.10','wasi-http-0.2.10','wasi-io-0.2.10','wasi-random-0.2.10','wasi-sockets-0.2.10']);need(names==expected,'Exact seven-package WIT directory')
live=[]
for name in names:
 folder=wit/name;need(not folder.is_symlink()and sorted(p.name for p in folder.iterdir())==['package.wit'],'Only ordinary package.wit');r=add(folder/'package.wit',None,None,'LIVE-WIT-copy-input');live.append({'name':'host-apis/wasi-0.2.10/wit/deps/'+name+'/package.wit',**{k:r[k]for k in ['path','sha256','bytes']}})
adapter=add(pack/'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm','988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0',53512,'LIVE-release-adapter');live.append({'name':'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm',**{k:adapter[k]for k in ['path','sha256','bytes']}})
result={'schemaVersion':1,'state':'FINITE_ORIGINAL_CONTEXT_355_HTTP_PHYSICAL_CLOSURE','files':list(rows.values()),'toolTrees':context['toolTrees'],'toolLinks':context['toolLinks'],'familySnapshotRoot':str(F/'snapshot'),'familySnapshotMembers':seal['snapshotMembers'],'packageEndpoints':str(F/'package-endpoints.json'),'liveInputs':live,'originalFamilyIndex':P['familyIndex'],'nativeConfiguredSourceRoot':P['nativeConfiguredSourceRoot'],'nativeFrozenSourceRoot':P['nativeFrozenSourceRoot'],'packagingRoot':P['paths']['packagingRoot'],'nestedPreparationManifestsNotReinterpreted':True,'fullActualFamilyConsumedRows':len(seal['inputs']),'actualToolRows':4892,'toolLinksCount':22,'selectedRuntimeFrozenCopies':len(pin['frozenFiles']),'nativeSourcesPerContext':355,'allActionsInvoked':False}
out=D/'closure.json';need(not out.exists(),'Fresh preparation data only');out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'state':result['state'],'files':len(rows),'logicalBytes':sum(r['bytes']for r in rows.values()),'liveInputs':len(live),'noActions':True}))
