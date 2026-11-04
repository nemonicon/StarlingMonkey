"""Read-only current package/tree/link context from the proven zlib-v8 mechanism."""
from pathlib import Path
import hashlib,json,os
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
OLD=REPO/'tests/node-compat/foundation-zlib/component-validation-activated-v8'
def sha(value):return hashlib.sha256(value).hexdigest()
def main():
    old=json.loads((OLD/'input-freeze.json').read_bytes());roots=old['toolTrees'];assert len(roots)==2 and len(old['toolLinks'])==22
    def inside(path):
        actual=Path(path).resolve()
        return any(actual.is_relative_to(Path(row['realPath']))for row in roots)
    files=[]
    for row in old['inputs']:
        path=Path(row['path']);path=path if path.is_absolute()else OLD/path
        if not inside(path):continue
        assert path.is_file()and not path.is_symlink();value=path.read_bytes();assert sha(value)==row['sha256']and len(value)==row['bytes']
        files.append({'path':str(path),'sha256':sha(value),'bytes':len(value)})
    for row in roots:
        root=Path(row['path']);assert str(root.resolve())==row['realPath'];entries=[]
        for directory,names,leaves in os.walk(root,followlinks=False):
            for name in sorted(names+leaves):
                path=Path(directory)/name
                kind='symlink'if path.is_symlink()else'directory'if path.is_dir()else'file'if path.is_file()else None
                assert kind;entries.append({'path':str(path.relative_to(root)),'kind':kind})
        assert sorted(entries,key=lambda x:x['path'])==row['entries']
    for row in old['toolLinks']:
        path=Path(row['path']);assert path.is_symlink()and os.readlink(path)==row['linkText']and str(path.resolve())==row['resolvedTarget']and inside(path)
        if row['targetKind']=='file':value=path.resolve().read_bytes();assert sha(value)==row['targetSha256']and len(value)==row['targetBytes']
    invocation=old['invocation']
    for name in ['nodeRealPath','wasmtimeRealPath']:
        path=Path(invocation[name]);value=path.read_bytes();files.append({'path':str(path),'sha256':sha(value),'bytes':len(value)})
    context={'schemaVersion':1,'state':'PINNED_TWO_PUBLIC_TOOL_TREES_22_LINKS_NOT_COMPONENT_EXECUTION','toolTrees':roots,'toolLinks':old['toolLinks'],'invocation':invocation,'inputs':files,'oldCodecProofTransferred':False,'ownerModuleExecuted':False}
    with(HERE/'tool-context.json').open('x')as output:json.dump(context,output,indent=2);output.write('\n')
    paths=['cli','clocks','filesystem','http','io','random','sockets'];wit=[]
    for name in paths:
        path=REPO/f'host-apis/wasi-0.2.10/wit/deps/wasi-{name}-0.2.10/package.wit';value=path.read_bytes();wit.append({'path':str(path),'sha256':sha(value),'bytes':len(value)})
    adapter=REPO/'host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm';value=adapter.read_bytes();assert sha(value)=='988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'
    with(HERE/'live-inputs.json').open('x')as output:json.dump({'schemaVersion':1,'adapter':{'path':str(adapter),'sha256':sha(value),'bytes':len(value)},'wit':wit,'mustReopenBeforeAndAfterPackaging':True,'doesNotAuthorizeHTTPImports':True},output,indent=2);output.write('\n')
    print(json.dumps({'trees':2,'links':22,'toolInputRows':len(files),'liveWit':7,'ownerModuleExecuted':False}))
if __name__=='__main__':main()
