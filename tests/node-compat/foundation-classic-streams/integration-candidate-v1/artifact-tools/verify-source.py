"""Read-only source-packet verification. Never calls artifact-action mains."""
import hashlib
import json
from pathlib import Path

def main():
    here=Path(__file__).resolve().parent
    checksum=lambda b:hashlib.sha256(b).hexdigest()
    receipt=json.loads((here/'source-receipt.json').read_bytes())
    inputs=(here/'input-freeze.json').read_bytes()
    assert checksum(inputs)==receipt['inputFreezeSha256']
    for row in json.loads(inputs)['inputs']:
        path=Path(row['observedPath']);assert path.is_file() and not path.is_symlink(),path
        data=path.read_bytes();assert checksum(data)==row['sha256'] and len(data)==row['bytes'],path
    index=json.loads((here/'index.json').read_bytes())
    for row in index['files']:
        path=here/row['path'];assert path.is_file() and not path.is_symlink(),path
        data=path.read_bytes();assert checksum(data)==row['sha256'] and len(data)==row['bytes'],path
    assert receipt['actualArtifactPins'] is None
    print(json.dumps({'state':'CLASSIC_ARTIFACT_SOURCE_PACKET_REHASHED','files':len(index['files']),
        'inputs':len(json.loads(inputs)['inputs']),'artifactActionMainsExecuted':False,'engineOrGuestExecuted':False}))

if __name__=='__main__':main()
