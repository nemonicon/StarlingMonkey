"""Reproducible text-only V4 adapter-span replacement. No entry/API execution."""
from pathlib import Path
import hashlib,json,sys
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'next-component-entry-fixes-v4'
START='// Standard WASI HTTP resource ownership -> ordinary Web Request/Response.'
END='// Pure orchestration, inlined unchanged into each raw guest entry.'
def row(p):
 b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def digest(b):return dict(sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def render():
 assert row(BASE/'index.json')['sha256']=='34c350126b88e22ff71bf26822512315d4fa75101f60e878cb661991bc09dd8a'
 assert row(BASE/'guest-entry.mjs')['sha256']=='c43117a45a012c11ee9cf20e8a75e5ddf3caee8f6c0ed6cc1fc5bdb1f405e7a6'
 original=(BASE/'guest-entry.mjs').read_text();assert original.count(START)==original.count(END)==1
 start=original.index(START);end=original.index(END);assert start<end
 prefix,old,suffix=original[:start],original[start:end],original[end:]
 calls=['installNodeGlobalAlias(globalThis);','installClassicRequestBody(__nextReadable,globalThis);',
  'installAsyncResourceFacade(__nextAsyncHooks);','installCrossPrototypeBufferFrom(__nextBuffer);',
  'installReadStreamOptionsFacade(fs);','installSignalPipeTo(__nextAbortListener,globalThis,__nextWebStreams);']
 assert all(prefix.count(x)==1 for x in calls)
 adapter=(HERE/'adapter.mjs').read_text();assert adapter.count('export function ')==2
 replacement=adapter.replace('export function ','function ')+'\n'
 output=prefix+replacement+suffix
 assert output[:len(prefix)]==prefix and output[-len(suffix):]==suffix
 proof=dict(schemaVersion=5,sourceOnly=True,baseIndex=row(BASE/'index.json'),baseEntry=row(BASE/'guest-entry.mjs'),
  baseComposition=row(BASE/'composition.json'),adapter=row(HERE/'adapter.mjs'),assembler=row(Path(__file__).resolve()),
  exactAdapterSpan=dict(startByte=len(prefix.encode()),endByte=len((prefix+old).encode()),before=digest(old.encode()),after=digest(replacement.encode())),
  unchangedPrefix=digest(prefix.encode()),unchangedSuffix=digest(suffix.encode()),sixFacadeCalls=calls,
  transforms=['Replace exactly one authenticated adapter span; remove only two ownadapter export keywords.'],
  allSixFacadesAndAppPrepareAndNativeBoundariesPreserved=True,applicationRewritten=False,nativeSourceOrEngineChanged=False,
  rawEntryEvaluated=False,actualRootAuthority=None,actualComponent=None,actualRuntime=None)
 return output,proof
if __name__=='__main__':
 text,proof=render();target=HERE/'guest-entry.mjs'
 if '--check'in sys.argv:assert target.read_text()==text
 else:
  assert not target.exists();target.write_text(text);proof['entry']=row(target)
  (HERE/'composition.json').write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(sourceOnly=True,entry=row(target),rawEntryEvaluated=False)))
