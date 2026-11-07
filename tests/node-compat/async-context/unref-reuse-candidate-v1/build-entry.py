"""Pure Source assembly; no guest/module/engine import or execution."""
from pathlib import Path
import hashlib,json,sys
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
def row(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def render():
 adapter=REPO/'tests/node-compat/frameworks/nextjs/next-component-candidate-v3/adapter-descendant.mjs'
 lifecycle=REPO/'tests/node-compat/frameworks/nextjs/next-component-candidate-v2/lifecycle.mjs'
 assert row(adapter)['sha256']=='785e0eaee78beeae6b77e6ceaa1d1446c0a5992af3639bc566b6e3db3540e09e'
 assert row(lifecycle)['sha256']=='0f7a5e111a303d2afcf5842d1505d0743477a3be39ce85efe526bb0cf1df2627'
 wire=adapter.read_text();life=lifecycle.read_text().split('export function readRoutingOrigin',1)[0]
 assert wire.count('export function ')==1 and life.count('export function ')==1
 cases=(HERE/'cases.mjs').read_text()
 for old,new in [('export const ','const '),('export function ','function ')]:cases=cases.replace(old,new)
 text="""// Raw isolated ordinary-call unref control. INIT creates no ALS or timer.
import {bootstrap} from 'starling:node-startup';
import {runFreshRequest,runNeutralServer} from 'starling:node-http';
import {AsyncLocalStorage as UnrefAsyncLocalStorage} from 'node:async_hooks';
import {setTimeout as unrefTimeout,clearTimeout as unrefClearTimeout} from 'node:timers';
import * as types from 'wasi:http/types@0.2.10';
"""+wire.replace('export function ','function ')+'\n'+life.replace('export function ','function ')+'\n'+cases+'\n'+(HERE/'guest-tail.mjs').read_text()
 inputs=[row(p) for p in [adapter,lifecycle,HERE/'cases.mjs',HERE/'guest-tail.mjs',Path(__file__).resolve()]]
 return text,dict(schemaVersion=1,state='UNREF_REUSE_RAW_ENTRY_SOURCE_ASSEMBLY_V1',inputs=inputs,
  transforms=['whole adapter export removed','first lifecycle function only, export removed','shared cases export keywords removed','exact own guest tail appended'],
  noEntryEvaluated=True,noNativeOrGuestActions=True)
def main():
 text,proof=render();target=HERE/'guest-entry.mjs'
 if '--check' in sys.argv:assert target.read_text()==text
 else:
  assert not target.exists();target.write_text(text);proof['entry']=row(target)
  (HERE/'entry-derivation.json').write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(sourceOnly=True,entry=row(target),guestOrNativeExecuted=False)))
if __name__=='__main__':main()
