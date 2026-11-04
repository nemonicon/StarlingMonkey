"""Read-only packet/input verification; does not run artifact-tool mains."""
import hashlib
import json
from pathlib import Path
import sys

def main():
    here = Path(__file__).resolve().parent
    repo = here.parents[3]
    digest = lambda data: hashlib.sha256(data).hexdigest()
    receipt = json.loads((here/'source-receipt.json').read_bytes())
    inputs_data = (here/'input-freeze.json').read_bytes()
    assert digest(inputs_data) == receipt['inputFreezeSha256']
    inputs = json.loads(inputs_data)
    assert inputs['nativeSourceCount'] == 306
    assert len({row['path'] for row in inputs['files']}) == len(inputs['files'])
    for row in inputs['files']:
        path = Path(row['path'])
        path = path if path.is_absolute() else repo/path
        assert path.is_file() and not path.is_symlink(), path
        data = path.read_bytes()
        assert len(data) == row['bytes'] and digest(data) == row['sha256'], path
    index = json.loads((here/'index.json').read_bytes())
    for row in index['files']:
        path = here/row['path']
        assert path.is_file() and not path.is_symlink()
        data = path.read_bytes()
        assert len(data) == row['bytes'] and digest(data) == row['sha256'], path
    print(json.dumps({'state':'SOURCE_PACKET_AND_INPUTS_REHASHED','files':len(index['files']),
                      'inputs':len(inputs['files']),'nativeInputs':306,'artifactMainsExecuted':False,'nativeOrGuestExecuted':False}))

if __name__ == '__main__':
    main()
