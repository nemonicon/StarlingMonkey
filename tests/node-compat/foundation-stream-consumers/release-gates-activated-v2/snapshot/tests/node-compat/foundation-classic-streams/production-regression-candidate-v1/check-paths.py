"""Read-only static comparison of import paths and resolvable directory bindings."""
from pathlib import Path
import json
import re
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[3]
PARENTS={'common':REPO/'tests/node-compat/foundation-scheduler/production-regression-candidate-v5',
 'off':REPO/'tests/node-compat/foundation-scheduler/production-followon-off-v3',
 'release':REPO/'tests/node-compat/foundation-scheduler/production-release-runner-v3',
 'capability':REPO/'tests/node-compat/foundation-scheduler/production-followon-capability-v3'}
def mapped(path):
    for name,parent in PARENTS.items():
        if path.is_relative_to(parent):return HERE/name/path.relative_to(parent)
    return path
def bindings(text,path):
    result={name:path.parent for name in re.findall(r'(?:const|let)\s+(\w+)\s*=\s*dirname\(fileURLToPath\(import\.meta\.url\)\)',text)}
    pattern=re.compile(r'''\b(\w+)\s*=\s*resolve\((dirname\(fileURLToPath\(import\.meta\.url\)\)|\w+),\s*['"]([^'"]+)['"]\)''')
    for _ in range(4):
        for name,base,relative in pattern.findall(text):
            root=path.parent if base.startswith('dirname(')else result.get(base)
            if root is not None:result[name]=(root/relative).resolve()
    return result
def main():
    document=json.loads((HERE/'derivations.json').read_bytes());compared=[];imports=[]
    for row in document['records']:
        old=REPO/row['sourcePath'];new=HERE/row['destinationPath'];a=bindings(old.read_text(),old);b=bindings(new.read_text(),new)
        for name in sorted(set(a)&set(b)):
            assert b[name]==mapped(a[name]),(row['destinationPath'],name,a[name],b[name])
            compared.append({'source':row['destinationPath'],'binding':name,'resolved':str(b[name])})
        for spec in re.findall(r'''(?:\bfrom\s*|\bimport\s*\()\s*['"]([^'"]+)['"]''',new.read_text()):
            if not spec.startswith('.'):continue
            target=(new.parent/spec).resolve();assert target.is_file(),(new,spec,target)
            imports.append({'source':row['destinationPath'],'specifier':spec,'resolved':str(target)})
    result={'state':'STATIC_REBASED_IMPORTS_AND_DIRECTORY_BINDINGS_PASSED','derivedSources':64,'directoryBindings':len(compared),'relativeImports':len(imports),'bindings':compared,
      'scope':'Only literal imports and simple dirname/resolve bindings checked statically; no source module, runner or guest executed.'}
    with(HERE/'path-check-results.json').open('x')as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps({key:result[key]for key in['state','derivedSources','directoryBindings','relativeImports']}))
if __name__=='__main__':main()
