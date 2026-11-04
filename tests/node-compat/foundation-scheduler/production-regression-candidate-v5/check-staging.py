"""Read-only source/syntax checks for the four UNSEALED activation siblings.

Does not execute any JavaScript main, freeze generator, compiler, componentizer,
guest, host or real fixed-artifact preflight. Writes only FRESH_OUTPUT_JSON.
"""
from pathlib import Path
import ast
import hashlib
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
NODE = Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
PAIRS = [
    ('production-regression-candidate-v4', 'production-regression-candidate-v5'),
    ('production-followon-off-v2', 'production-followon-off-v3'),
    ('production-release-runner-v2', 'production-release-runner-v3'),
    ('production-followon-capability-v2', 'production-followon-capability-v3'),
]
sha = lambda data: hashlib.sha256(data).hexdigest()

def main():
    assert len(sys.argv) == 2, 'FRESH_OUTPUT_JSON'
    output = Path(sys.argv[1])
    assert not output.exists() and not output.is_symlink()
    old_files = []
    packets = []
    syntax = []
    diffs = []
    for old_name, new_name in PAIRS:
        old, new = BASE / old_name, BASE / new_name
        index_bytes = (old / 'index.json').read_bytes()
        old_index = json.loads(index_bytes)
        for row in old_index['files']:
            data = (old / row['path']).read_bytes()
            assert sha(data) == row['sha256'], (old_name, row['path'])
            old_files.append({'packet': old_name, 'path': row['path'], 'sha256': row['sha256']})
        assert json.loads((new / 'staging.json').read_bytes())['rootPinReviewIndexSha256'] == '656a88d8f0d38bcb2b9314a95f5463115c8b8f436722423e50e29939ff9e3934'
        if (new / 'pins.json').exists():
            expected = {'production-regression-candidate-v5': 'ed0d6f548ac354ce6ef0ab97c5162ece7091a4e22c81fdd3910665c0bbb21bea',
                        'production-followon-capability-v3': '26b16ba1404c76d04a3ae1a137d37d88a08cc87de4907d14eb3bc028759104f1'}[new_name]
            assert sha((new / 'pins.json').read_bytes()) == expected
        if (new / 'http-component-pins.json').exists():
            assert json.loads((new / 'http-component-pins.json').read_bytes())['component'] is None
        if (new / 'dependency-pins.json').exists():
            dependencies = json.loads((new / 'dependency-pins.json').read_bytes())
            if dependencies['state'] == 'UNCONFIGURED_SEALED_PARENT_INDICES_REQUIRED':
                assert dependencies['commonIndexSha256'] is None
                if 'offIndexSha256' in dependencies:
                    assert dependencies['offIndexSha256'] is None
            else:
                assert dependencies['state'] == 'REVIEWED_SEALED_PARENT_INDICES_V1'
                for key, parent in [('commonIndexSha256', 'production-regression-candidate-v5'),
                                    ('offIndexSha256', 'production-followon-off-v3')]:
                    if key in dependencies:
                        assert dependencies[key] == sha((BASE / parent / 'index.json').read_bytes())
        # Historical transformation records stay exact. Generated bodies first
        # reverse ONLY the declared sibling import/path changes.
        transformation = new / ('runner-transformations.json' if (new / 'runner-transformations.json').exists() else 'transformations.json')
        assert transformation.read_bytes() == (old / transformation.name).read_bytes()
        path_only_files = []
        for path in sorted(new.rglob('*')):
            if not path.is_file() or 'history' in path.relative_to(new).parts:
                continue
            relative = path.relative_to(new)
            old_path = old / relative
            if old_path.is_file():
                before, after = old_path.read_bytes(), path.read_bytes()
                if before != after:
                    restored = after
                    for old_dependency, new_dependency in reversed(PAIRS):
                        restored = restored.replace(new_dependency.encode(), old_dependency.encode())
                    if restored == before:
                        path_only_files.append(relative.as_posix())
                    diffs.append({'packet': new_name, 'path': relative.as_posix(),
                                  'predecessorSha256': sha(before), 'stagedSha256': sha(after),
                                  'siblingPathOnly': restored == before})
            if path.suffix == '.mjs':
                result = subprocess.run([str(NODE), '--check', str(path)], capture_output=True, text=True)
                assert result.returncode == 0, (path, result.stderr)
                syntax.append({'path': str(path), 'kind': 'node --check', 'executedMain': False})
            elif path.suffix == '.py':
                ast.parse(path.read_text(), filename=str(path))
                syntax.append({'path': str(path), 'kind': 'python ast.parse', 'executedModule': False})
        packets.append({'path': new_name, 'predecessorIndexSha256': sha(index_bytes),
                        'historicalTransformationRecordUnchanged': transformation.name,
                        'siblingPathOnlyFiles': path_only_files})
    report = {'schemaVersion': 1, 'state': 'REVIEWED_PINS_ACTIVATION_SOURCE_CHECKS_PASSED_RUNTIME_PENDING',
              'packets': packets, 'unchangedPredecessorFiles': old_files, 'changes': diffs,
              'syntaxChecks': syntax, 'reviewedPinsCreated': True,
              'actualFixedArtifactPreflightExecutedByThisCheck': False,
              'nativeBuildComponentizerGuestHostOrJavaScriptMainExecuted': False}
    with output.open('x') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'state': report['state'], 'predecessorFiles': len(old_files), 'syntaxChecks': len(syntax)}))

if __name__ == '__main__':
    main()
