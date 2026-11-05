"""Full current355 source/compile producer; historical source is ancestry DATA."""
import copy
import hashlib
import importlib.util
import json
import pathlib
from pathlib import Path
import shlex
import sys
sys.dont_write_bytecode=True
if not __debug__:raise RuntimeError('Source policy checks require assertions')
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
POLICY_SHA256='@POLICY_SHA@'
AUTH_SHA256='@AUTH_SHA@'
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
assert digest(HERE/'policy.json')==POLICY_SHA256
POLICY=json.loads((HERE/'policy.json').read_bytes())

def authenticate_inputs():
    assert digest(HERE/'donor-inputs.json')==AUTH_SHA256
    rows=json.loads((HERE/'donor-inputs.json').read_bytes())['files']
    assert len(rows)==len({r['path']for r in rows})
    for r in rows:
        path=REPO
        for part in r['path'].split('/'):
            assert part and part not in('.','..');path/=part;assert not path.is_symlink(),path
        assert path.is_file()and path.stat().st_size==r['bytes']and digest(path)==r['sha256'],path
    return True
authenticate_inputs()
BASE_ROOT=REPO/'tests/node-compat/foundation-crypto/ownership-secret-integration-candidate-v1'
BASE=json.loads((BASE_ROOT/'policy.json').read_bytes())
ANCESTOR_ROOT=REPO/'tests/node-compat/foundation-scheduler/integration-candidate-v1'
ANCESTOR=json.loads((ANCESTOR_ROOT/'policy.json').read_bytes())
assert BASE['expectedNativeSourceManifest']==POLICY['combinedSourcePolicy']['parentExpectedNativeSourceManifest']
before={r['path']:r['sha256']for r in BASE['expectedNativeSourceManifest']}
after={r['path']:r['sha256']for r in POLICY['expectedNativeSourceManifest']}
assert len(before)==len(after)==355 and before.keys()==after.keys()
changes=POLICY['combinedSourcePolicy']['changes']
assert len(changes)==7 and sum(before[p]==after[p]for p in before)==348
for r in changes:assert before[r['path']]==r['beforeSha256']and after[r['path']]==r['afterSha256']
for key in ('cryptoKeyOwnershipSourcePolicy','cryptoSecretFailureSourcePolicy','streamConsumersSourcePolicy','zlibSourcePolicy'):
    assert POLICY[key]==BASE[key], 'Historical ancestry preserved; current source checked separately'
assert POLICY['parentExpectedNativeSourceManifest']==ANCESTOR['expectedNativeSourceManifest']

def expected(relative,base_expected):
    prior=ANCESTOR['sourceLayer'].get(relative)
    parent=base_expected
    if prior is not None:
        assert prior['beforeSha256']==base_expected
        parent=prior['afterSha256']
    entry=POLICY['sourceLayer'].get(relative)
    if entry is None:return parent
    assert entry['beforeSha256']==parent,'Actual306 source ancestry mismatch: '+relative
    return entry['afterSha256']
def resolved(mapping):return{path:expected(path,value)for path,value in mapping.items()}
def source_manifest(repo):
    authenticate_inputs();repo=Path(repo)
    assert repo.resolve()==Path(POLICY['contexts']['configuredSourceRoot'])
    rows=POLICY['expectedNativeSourceManifest']
    assert len(rows)==len({r['path']for r in rows})==355
    for r in rows:
        path=repo
        for part in r['path'].split('/'):
            assert part and part not in('.','..');path/=part;assert not path.is_symlink(),path
        assert path.is_file()and digest(path)==r['sha256'],'Unreviewed combined355 source: '+r['path']
    return copy.deepcopy(rows)
def validate_sources(repo,manifest=None):
    actual=source_manifest(repo)
    if manifest is not None:assert sorted(manifest,key=lambda r:r['path'])==actual and all(set(r)=={'path','sha256'}for r in manifest)
    return True
def load_codec():
    authenticate_inputs()
    path=REPO/'tests/node-compat/foundation-zlib/native-integration-candidate-v4/codec-evidence.py'
    assert digest(path)==POLICY['selectedCodecCompileContract']['codecEvidenceSha256']
    spec=importlib.util.spec_from_file_location('genuine_selected_codec_primitives',path)
    codec=importlib.util.module_from_spec(spec);spec.loader.exec_module(codec)
    return codec

# @GENERIC_FUNCTIONS@

# @COMPILE_FUNCTION@

# @DECORATE_FUNCTION@

if __name__=='__main__':
    assert len(sys.argv)==2
    validate_sources(sys.argv[1])
    print('Exact combined355 initial normal-OFF source policy verified; no compiler or guest ran')
