#!/usr/bin/env python3
"""Read/hash/source checks only. Never invoke owner scripts, loaders or codecs."""
import hashlib,json,os,re,stat,sys
from pathlib import Path
D=Path(__file__).resolve().parent
checks=[]
def need(v,m):
 if not v: raise AssertionError(m)
 checks.append(m)
def read(p): return Path(p).read_bytes()
def sha(b): return hashlib.sha256(b).hexdigest()
p=json.loads(read(D/'prerequisites.json')); m=json.loads(read(D/'packaging-context.json'))
for name in ['guestIndex','guest','wit','nativeSourceIndex','bootstrapEntry','reviewedNativePins','nativeRootReview','node']:
 r=p[name];b=read(r['path']);need(len(b)==r['bytes'] and sha(b)==r['sha256'],'actual prerequisite '+name)
for n in ['guestReview','nativeReview','publicationReview']:
 proof=p[n];r=proof['index'];b=read(r['path']);need(sha(b)==r['sha256'] and len(b)==r['bytes'],'proof index '+n);ix=json.loads(b);found=0
 for v in ix['files']:
  path=Path(r['path']).parent/v['path'];data=read(path);need(sha(data)==v['sha256'] and len(data)==v['bytes'],n+' member '+v['path'])
  if str(path)==proof['result']['path']:need(v['sha256']==proof['result']['sha256'] and v['bytes']==proof['result']['bytes'],'exact proof result '+n);found+=1
 need(found==1,'proof result once '+n)
ix=json.loads(read(m['publicationIndex']['path']));need(sha(read(m['publicationIndex']['path']))==m['publicationIndex']['sha256'],'publication index hash')
rows={r['path']:r for r in ix['files']};need(len(m['files'])==4934 and sum(r['path'].startswith('tools/') for r in m['files'])==4890,'all physical tool/packaging roles')
for r in m['files']:
 need(all(r[k]==rows[r['path']][k] for k in ['path','sha256','bytes','mode']),'exact publication role '+r['path'])
 path=Path(m['publicationRoot'])/r['path'];s=path.lstat();need(stat.S_ISREG(s.st_mode) and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==r['mode'] and s.st_size==r['bytes'],'ordinary role '+r['path']);h=hashlib.sha256()
 with path.open('rb') as f:
  while True:
   block=f.read(1024*1024)
   if not block:break
   h.update(block)
 need(h.hexdigest()==r['sha256'],'physical role bytes '+r['path'])
need(m['links']==ix['links'] and len(m['links'])==22,'all mapped links')
for l in m['links']:
 path=Path(m['publicationRoot'])/l['destination'];need(path.is_symlink() and os.readlink(path)==l['newLinkText'] and path.resolve()==Path(m['publicationRoot'])/l['mappedTarget'],'exact known npm link '+l['destination'])
need(sum('/wasi-0.2.10/wit/' in r['path'] for r in m['files'])==7,'seven actual WIT files')
need(any(r['bytes']==53512 and r['sha256']=='988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0' for r in m['files']),'exact adapter')
pins=json.loads(read(p['reviewedNativePins']['path']));need(pins['variants']['normal-off']['engineSha256']==p['normalEngineSha256'] and all(pins['variants'][n] is None for n in ['normal-runtime','gc-off','disabled-off']),'actual normal-only native data')
need(pins['variants']['normal-off']['cryptoKeyOwnershipPolicy']['version']=='sm-webcrypto-key-owner-and-prototype-guard-source-v1','genuine guarded native lineage')
worker=(D/'build-worker.mjs').read_text();guard=(D/'guard.mjs').read_text();parent=(D/'build.mjs').read_text()
need('cryptoOwnerBootstrapPreflight({' in guard and 'costPreflight(' not in guard,'real crypto bootstrap API, no cost native projection')
need('sourceManifest.length===355' in guard,'actual metadata field')
need(parent.index("await mkdir(join(output.root,'processes')")<parent.index('await runOwnedCommand('),'owned processes directory before helper')
need('selected.componentize(source,options)' in worker and 'await import(pathToFileURL' in worker and 'generatedModuleImported:false' in worker,'concrete selected constructor, no generated-module import')
need('keyOperationsInvoked:false' in worker and "worldName:'validation'" in (D/'abi.mjs').read_text(),'construction key calls denied')
need('KEY_ACTION_SOURCE_SUCCESSOR_REQUIRED' in (D/'key-validation.mjs').read_text(),'positive key action closed')
print(json.dumps({'schemaVersion':1,'state':'SOURCE_DATA_CHECKS_PASSED','checks':len(checks),'genuineBootstrapInvoked':False,'componentizerInvoked':False,'keyOperationsInvoked':False,'ownerActionsInvoked':False}))
