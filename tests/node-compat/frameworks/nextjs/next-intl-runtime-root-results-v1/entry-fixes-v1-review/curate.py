#!/usr/bin/env python3
"""One-shot retained DATA collection. No subprocesses or executable imports."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import stat
import tarfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
TEMP = Path('/private/tmp/starling-node-compat')
PAIRS = [
    ('entry-v1', 'next-wasmtime-deployment-enginee7baa5a9-entry-fixes-v1',
     'next-entry-fixes-component-v1-real-next-enginee7baa5a9-entry-fixes-v1'),
    ('native-utf16-v2', 'next-wasmtime-deployment-engine4623640b-native-utf16-v2',
     'next-entry-fixes-component-v2-real-next-engine4623640b-native-utf16-v2'),
]


def descriptor(path, data=None):
    path = Path(path)
    if data is None:
        data = path.read_bytes()
    return {'path':str(path), 'sha256':hashlib.sha256(data).hexdigest(), 'bytes':len(data)}


def checked(row):
    path = Path(row['path'])
    assert path.is_absolute() and not path.is_symlink() and path.is_file(), row['path']
    data = path.read_bytes()
    assert descriptor(path,data) == {key:row[key] for key in ('path','sha256','bytes')}, row['path']
    return data


def main():
    assert not (HERE/'data.tar.gz').exists(), 'fresh curator output required'
    files, blobs, external, captures, families = [], {}, {}, {}, {}

    def add(name, path, expected=None):
        assert name not in blobs
        path = Path(path)
        data = checked(expected) if expected else checked(descriptor(path))
        row = descriptor(path,data)
        files.append({'path':name, 'original':row})
        blobs[name] = data
        captures.setdefault(str(path),row)
        return row

    def family(row):
        if row['path'] in families:
            assert families[row['path']] == row
            return
        index = json.loads(checked(row))
        base = Path(row['path']).parent
        names = [item['path'] for item in index['files']]
        assert len(names) == len(set(names))
        assert sorted(str(p.relative_to(base)) for p in base.rglob('*') if p.is_file()) == sorted(names+['index.json'])
        label = 'sources/'+base.name+'/'
        add(label+'index.json', row['path'], row)
        for item in index['files']:
            p = base/item['path']
            assert base in p.resolve().parents and not p.is_symlink()
            add(label+item['path'],p,{**item,'path':str(p)})
        families[row['path']] = row

    deploy_plan = json.loads((REPO/'wasmtime-deployment-candidate-v4/plan.json').read_bytes())
    app_inventory = json.loads(checked(deploy_plan['applicationInputs']))
    add('inputs/application-inputs.json', deploy_plan['applicationInputs']['path'], deploy_plan['applicationInputs'])
    add('inputs/fixture-contract.json', REPO/'fixture-contract.json')
    add('inputs/browser-check.mjs', REPO/'browser-phase-matched-host-candidate-v1/browser-check.mjs')
    pair_rows, app_checks = [], []
    for label, runtime_name, construct_name in PAIRS:
        runtime, constructor = TEMP/runtime_name, TEMP/construct_name
        result = json.loads((runtime/'result.json').read_bytes())
        construction = json.loads(checked(result['constructionResult']))
        assert constructor/'result.json' == Path(result['constructionResult']['path'])
        family(result['inputSourceIndex'])
        family(result['sourceIndex'])
        family(construction['callerIndex'])
        composition = json.loads((Path(result['inputSourceIndex']['path']).parent/'composition.json').read_bytes())
        for facade in composition['facades']:
            assert checked(facade['source']) == (Path(result['inputSourceIndex']['path']).parent/facade['copy']).read_bytes()
            source = Path(facade['source']['path'])
            name = 'inputs/facades/'+source.parent.name+'/'+source.name
            if name not in blobs:
                add(name,source,facade['source'])
        if 'inputs/parent-entry.mjs' not in blobs:
            add('inputs/parent-entry.mjs',composition['originalEntry']['path'],composition['originalEntry'])
        for kind, root in [('runtime',runtime), ('constructor',constructor)]:
            for path in sorted(root.rglob('*')):
                if not path.is_file():
                    continue
                relative = path.relative_to(root)
                if kind == 'runtime' and relative.parts[0] == 'app':
                    continue
                if path.suffix in ('.wasm','.a','.obj') or relative.as_posix() == 'api-return/native-metadata-input.json':
                    continue
                add(label+'/'+kind+'/'+relative.as_posix(),path)
            monitor = Path(str(root)+'-external-root')
            for path in sorted(monitor.rglob('*')):
                if path.is_file():
                    add(label+'/'+kind+'-monitor/'+path.relative_to(monitor).as_posix(),path)
            terminal = json.loads((monitor/'terminal.json').read_bytes())
            add(label+'/'+kind+'-authority.json',terminal['authority']['path'],terminal['authority'])
        for key in ('engine','nativeMetadata','component','adapter'):
            row = construction['artifacts'][key]
            checked(row)
            external[row['path']] = row
        for row in construction['artifacts']['engineBuildEvidence']:
            checked(row)
            external[row['path']] = row
        app = runtime/'app'
        expected = app_inventory['files']
        assert sorted(p.relative_to(app).as_posix() for p in app.rglob('*') if p.is_file()) == sorted(row['path'] for row in expected)
        for row in expected:
            original = Path(app_inventory['root'])/row['path']
            target = app/row['path']
            checked({**row,'path':str(original)})
            checked({**row,'path':str(target)})
            a,b = original.stat(),target.stat()
            assert stat.S_IMODE(b.st_mode) == 0o444 and b.st_nlink == 1 and (a.st_dev,a.st_ino) != (b.st_dev,b.st_ino)
        app_checks.append({'run':label,'files':len(expected),'bytes':sum(row['bytes'] for row in expected),'currentOriginalAndReadonlyCopyBytesMatch':True,'currentCopiedMode0444AndDistinctInodes':True})
        pair_rows.append({'id':label,'runtimeResult':descriptor(runtime/'result.json'),'constructionResult':result['constructionResult'],'component':result['component'],'componentAudit':result['componentAudit'],'inputEntry':result['inputEntry'],'inputSourceIndex':result['inputSourceIndex']})
    # A second read of every copied record and external artifact detects changes during collection.
    for row in list(captures.values())+list(external.values()):
        checked(row)
    with (HERE/'data.tar.gz').open('xb') as raw:
        with gzip.GzipFile(fileobj=raw,mode='wb',filename='',mtime=0) as compressed:
            with tarfile.open(fileobj=compressed,mode='w') as archive:
                for name,data in sorted(blobs.items()):
                    info=tarfile.TarInfo(name); info.size=len(data); info.mode=0o600; info.mtime=0
                    archive.addfile(info,io.BytesIO(data))
    capsule = {'schemaVersion':1,'archive':descriptor(HERE/'data.tar.gz'),'files':sorted(files,key=lambda row:row['path']),
               'runs':pair_rows,'sourceFamilies':list(families.values()),'externalArtifactDescriptors':list(external.values()),
               'currentApplicationReadbacks':app_checks,'copiedFilesRehashedBeforeFinal':len(captures),
               'appOrWasmOrSDKPayloadsCopied':False,'runtimeTargetsInvokedByCurator':False}
    (HERE/'capsule.json').write_text(json.dumps(capsule,indent=2)+'\n')
    print(json.dumps({'retainedFiles':len(files),'retainedBytes':sum(row['original']['bytes'] for row in files),'archive':capsule['archive'],'currentAppReadbacks':app_checks},sort_keys=True))


if __name__ == '__main__':
    main()
