"""Read-only donor/recipe comparison. No Source materialization/tool/build."""
from pathlib import Path
import ast
import importlib.util
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


if __name__ == '__main__':
    old = module(HERE.parent/'next-native-portable-source-v1/materialize.py', 'original_portable_recipe_read_only')
    new = module(HERE/'materialize.py', 'boundary_portable_recipe_read_only')
    old_spec, before, old_inputs = old.selection(REPO)
    spec, after, inputs = new.selection(REPO)
    shape = lambda values: {(v['role'],v['path']): {k:v[k] for k in ['sha256','bytes','mode']} for v in values}
    a,b=shape(before),shape(after)
    assert set(a)==set(b) and len(a)==825
    assert [key for key in a if a[key]!=b[key]]==[('native-policy-source','runtime/script_loader.cpp')]
    assert len(spec['overlays'])==7 and spec['overlays'][:6]==old_spec['overlays'] and spec['additions']==old_spec['additions']
    assert sum(v['bytes'] for v in after)-sum(v['bytes'] for v in before)==2061
    assert spec['expectedBytes']==7532227 and new.fingerprint(after)==spec['roleContentSha256']=='cfbd75be70aeaa36006009fa6580b8f0f4bb789852e8d8201eefefd09d0a1550'
    base=json.loads((HERE.parent/'spidermonkey-intl-build-v1/cargo-root-results-v1/base-source-manifest.json').read_bytes())
    assert len(base['files'])==21
    for expected in base['files']:
        key=('native-policy-source',expected['path'])
        assert a[key]==b[key] and all(b[key][k]==expected[k] for k in ['sha256','bytes'])
    # Directly exercise the original no-output branch; no copier/write path.
    result=new.run(REPO)
    assert result['state']=='NEXT_PORTABLE_SOURCE_DONORS_CHECKED_V1' and result['outputRoot'] is None
    assert result['compilerOrGuestExecuted'] is result['generatedBuildMetadataProjected'] is False
    for path in HERE.glob('*.py'):ast.parse(path.read_text())
    print(json.dumps(dict(sourceOnly=True, selectedRows=825, changedPayloads=1, unchangedPayloads=824,
        native=435,support=387,embedding=3,unchangedRustBaseRows=21,logicalBytes=7532227,
        sourcePayloadFilesCopied=0,generatorsCargoCompilerEngineOrImportInvoked=False)))
