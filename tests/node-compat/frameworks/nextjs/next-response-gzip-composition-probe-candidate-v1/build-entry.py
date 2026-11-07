"""Pure Source assembly. Default checks text; --write exclusively creates the entry."""
from pathlib import Path
import argparse,hashlib,json,os
HERE=Path(__file__).resolve().parent

def row(path):
    p=Path(path);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))

def checked(ref):
    p=Path(ref['path']);assert p.is_absolute() and p.resolve()==p and p.is_file() and not p.is_symlink() and p.stat().st_nlink==1
    assert row(p)==ref;return p.read_text()

def render():
    refs=json.loads((HERE/'source-references.json').read_text())
    raw=checked(refs['v5Entry']);index=json.loads(checked(refs['v5SourceIndex']))
    item=next(x for x in index['files']if x['path']=='guest-entry.mjs')
    assert dict(item,path=refs['v5Entry']['path'])==refs['v5Entry']
    boundary='// Source fragment inlined in the raw ESM. No call occurs during INIT.\nasync function prepareServer() {'
    assert raw.count(boundary)==1
    prefix=raw.split(boundary)[0]
    assert prefix.count('function createWasiHttpHandler(')==1 and prefix.count('function createNeutralReadyHandler(')==1
    assert prefix.count("import * as types from 'wasi:http/types@0.2.10';")==1
    prefix=prefix.replace("import * as types from 'wasi:http/types@0.2.10';", "import * as types from 'wasi:http/types@0.2.10';\nimport __gzipProbeZlib from 'node:zlib';")
    helper=(HERE/'handler.mjs').read_text()
    assert helper.count('export const ')==1 and helper.count('export function ')==2
    helper=helper.replace('export const ','const ').replace('export function ','function ')
    tail=(HERE/'guest-tail.mjs.in').read_text()
    return prefix+helper+'\n'+tail

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true');args=parser.parse_args()
    text=render();p=HERE/'guest-gzip.mjs'
    if args.write:
        fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o644)
        with os.fdopen(fd,'w')as f:f.write(text)
    else:assert p.read_text()==text
    print(json.dumps(dict(sourceAssemblyOnly=True,nodeOrGuestInvoked=False,entry=row(p))))
if __name__=='__main__':main()
