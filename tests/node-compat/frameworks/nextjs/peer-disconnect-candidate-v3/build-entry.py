"""Pure text assembly for new diagnostic Source; no API/guest execution."""
from pathlib import Path
import hashlib,json,sys
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'peer-disconnect-candidate-v1'
LIFE=HERE.parent/'next-component-candidate-v2/lifecycle.mjs'
def row(p):
 b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def render():
 assert row(BASE/'index.json')['sha256']=='f3fc193b95e643e9ddd0fb0d503b8f629d27f8e92932fd822c53fb92c5164255'
 index=json.loads((BASE/'index.json').read_text());common=next(r for r in index['files']if r['path']=='diagnostic-common.mjs')
 assert row(BASE/'diagnostic-common.mjs')==dict(common,path=str(BASE/'diagnostic-common.mjs'))
 assert row(LIFE)['sha256']=='0f7a5e111a303d2afcf5842d1505d0743477a3be39ce85efe526bb0cf1df2627'
 parts=[BASE/'diagnostic-common.mjs',HERE/'policy.mjs',HERE/'diagnostic-handler.mjs',HERE/'adapter-diagnostic.mjs']
 text="""// Generated experimental observed-I/O adapter V2. No I/O/context capture at INIT.
import {bootstrap} from 'starling:node-startup';
import {runFreshRequest,runNeutralServer} from 'starling:node-http';
import {AsyncLocalStorage} from 'node:async_hooks';
import {setTimeout as peerTimeout,clearTimeout as peerClearTimeout} from 'node:timers';
import * as types from 'wasi:http/types@0.2.10';
"""
 for p in parts:
  source='\n'.join(line for line in p.read_text().splitlines()if not line.startswith('import '))+'\n'
  text+=source.replace('export function ','function ').replace('export const ','const ')+'\n'
 life=LIFE.read_text().split('export function readRoutingOrigin',1)[0];assert life.count('export function ')==1
 text+=life.replace('export function ','function ')+'\n'+(HERE/'guest-tail.mjs').read_text()
 return text,parts+[LIFE,HERE/'guest-tail.mjs',Path(__file__).resolve(),BASE/'index.json']
if __name__=='__main__':
 text,inputs=render();target=HERE/'guest-entry.mjs'
 if '--check'in sys.argv:assert target.read_text()==text
 else:
  assert not target.exists();target.write_text(text)
  (HERE/'entry-derivation.json').write_text(json.dumps(dict(schemaVersion=1,sourceOnly=True,inputs=[row(p)for p in inputs],entry=row(target),entryEvaluated=False),indent=2)+'\n')
 print(json.dumps(dict(entry=row(target),sourceOnly=True,entryEvaluated=False)))
