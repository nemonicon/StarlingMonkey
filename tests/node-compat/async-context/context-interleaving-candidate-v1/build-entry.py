"""Pure Source assembly; never imports an entry or invokes an engine/toolchain."""
from pathlib import Path
import hashlib,json,sys
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
def row(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def render():
 facade=HERE.parent/'async-resource-candidate-v1/async-resource.mjs'
 assert row(facade)['sha256']=='e5f26f9efa28ee8b0daf713f86a9017b3c8caca48730fa9487b09214c54329cf'
 adapter=REPO/'tests/node-compat/frameworks/nextjs/next-component-candidate-v3/adapter-descendant.mjs'
 lifecycle=REPO/'tests/node-compat/frameworks/nextjs/next-component-candidate-v2/lifecycle.mjs'
 cases=(HERE/'cases.mjs').read_text();resource=facade.read_text();wire=adapter.read_text();life=lifecycle.read_text()
 assert resource.count('export function ')==1 and wire.count('export function ')==1
 life=life.split('export function readRoutingOrigin',1)[0];assert life.count('export function ')==1
 imports="""// Generated isolated context controls. INIT installs only the pure sealed facade.
import {bootstrap} from 'starling:node-startup';
import {runFreshRequest,runNeutralServer} from 'starling:node-http';
import contextAsyncHooks,{AsyncLocalStorage as ContextAsyncLocalStorage} from 'node:async_hooks';
import {setTimeout as contextTimeout,clearTimeout as contextClearTimeout,setImmediate as contextImmediate,clearImmediate as contextClearImmediate} from 'node:timers';
import {setTimeout as contextPromiseTimeout} from 'node:timers/promises';
import * as types from 'wasi:http/types@0.2.10';
"""
 body=imports+'const installContextResource=(()=>{\n'+resource.replace('export function ','function ')+'\nreturn installAsyncResourceFacade;})();\ninstallContextResource(contextAsyncHooks);\n'
 body+=wire.replace('export function ','function ')+'\n'+life.replace('export function ','function ')+'\n'
 for old,new in [('export const ','const '),('export async function ','async function '),('export function ','function ')]:cases=cases.replace(old,new)
 body+=cases+'\n'+(HERE/'guest-tail.mjs').read_text()
 inputs=[row(p) for p in [facade,adapter,lifecycle,HERE/'cases.mjs',HERE/'guest-tail.mjs',Path(__file__).resolve()]]
 return body,dict(schemaVersion=1,state='CONTEXT_INTERLEAVING_RAW_ENTRY_SOURCE_ASSEMBLY_V1',inputs=inputs,
  transforms=['exact sealed facade in closure; export removed','whole adapter export removed','first lifecycle function only, export removed','shared cases export keywords removed','exact own guest tail appended'],noEntryEvaluated=True,noNativeOrGuestActions=True)
def main():
 text,proof=render();target=HERE/'guest-entry.mjs'
 if '--check' in sys.argv:assert target.read_text()==text
 else:
  assert not target.exists();target.write_text(text)
  proof['entry']=row(target);(HERE/'entry-derivation.json').write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(sourceOnly=True,entry=row(target),guestOrNativeExecuted=False)))
if __name__=='__main__':main()
