"""Inert text assembly; no entry evaluation, package API or guest operation."""
from pathlib import Path
import hashlib,json,sys
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[4]
def row(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def render():
 life=HERE.parent/'next-component-candidate-v2/lifecycle.mjs'
 assert row(life)['sha256']=='0f7a5e111a303d2afcf5842d1505d0743477a3be39ce85efe526bb0cf1df2627'
 parts=[HERE/'diagnostic-common.mjs',HERE/'diagnostic-handler.mjs',HERE/'adapter-diagnostic.mjs']
 text="""// Generated isolated diagnostic. No I/O/context capture at INIT.
import {bootstrap} from 'starling:node-startup';
import {runFreshRequest,runNeutralServer} from 'starling:node-http';
import {AsyncLocalStorage} from 'node:async_hooks';
import {setTimeout as peerTimeout,clearTimeout as peerClearTimeout} from 'node:timers';
import * as types from 'wasi:http/types@0.2.10';
"""
 for p in parts:
  source=p.read_text()
  source='\n'.join(line for line in source.splitlines() if not line.startswith('import '))+'\n'
  source=source.replace('export function ','function ').replace('export const ','const ')
  text+=source+'\n'
 source=life.read_text().split('export function readRoutingOrigin',1)[0]
 assert source.count('export function ')==1
 text+=source.replace('export function ','function ')+'\n'+(HERE/'guest-tail.mjs').read_text()
 return text,parts+[life,HERE/'guest-tail.mjs',Path(__file__).resolve()]
if __name__=='__main__':
 text,inputs=render();target=HERE/'guest-entry.mjs'
 if '--check' in sys.argv:assert target.read_text()==text
 else:
  assert not target.exists();target.write_text(text)
  (HERE/'entry-derivation.json').write_text(json.dumps(dict(schemaVersion=1,inputs=[row(p)for p in inputs],entry=row(target),sourceOnly=True,entryEvaluated=False),indent=2)+'\n')
 print(json.dumps(dict(sourceOnly=True,entry=row(target),entryEvaluated=False)))
