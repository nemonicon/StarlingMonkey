"""Finite own source seal after the separately retained source/data model result."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def descriptor(path, relative=False):
    data = path.read_bytes()
    return {'path': str(path.relative_to(HERE)) if relative else str(path),
            'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


for name in ('prepare.py', 'check-source.py', 'run-source-checks.py', 'seal-source.py'):
    ast.parse((HERE / name).read_text(), filename=name)
source_result = json.loads((HERE / 'source-results.json').read_text())
terminal = json.loads((HERE / 'evidence/final/terminal.json').read_text())
assert source_result['state'] == 'SOURCE_DATA_AND_EXTRACTED_MODELS_PASSED_V1'
assert terminal['rawExitCode'] == 0 and source_result['runtimeVerifiedSuccessor'] is False
for row in json.loads((HERE / 'input-freeze.json').read_text())['files']:
    assert descriptor(Path(row['path'])) == row
for row in json.loads((HERE / 'derivations.json').read_text())['records']:
    assert descriptor(Path(row['after']['path'])) == row['after']
for name in ('index.json', 'results.json', 'source-receipt.json'):
    assert not (HERE / name).exists(), 'new seal only; no edits to sealed source'
result = {'schemaVersion': 1, 'state': 'ZLIB_NODE_ERROR_SEMANTICS_SOURCE_CANDIDATE_PREPARED_V1',
          'sourceOnly': True, 'sourceChecksPassed': True, 'sourceChecks': source_result,
          'parentActualNativeSourceFiles': 350, 'changedAfterimages': 3, 'unchangedParentNativeFiles': 347,
          'fullRecordedDifferenceInventory': 22, 'targetedRowsPredictedOnly': 7,
          'remainingRecordedDifferences': 15, 'historicalConstantDifferenceSeparate': True,
          'backendRuntimeVersionObservedByThisCandidate': False,
          'nodeCodecCompilerHelpersNativeGuestOrRuntimeActionsInvoked': False,
          'sourcePeer': None, 'rootAuthority': None, 'nativeBuild': None,
          'runtimeValidation': None, 'deviationAcceptance': None,
          'operationalAdmission': False, 'adoption': False, 'performanceClaim': False}
(HERE / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
receipt = {'schemaVersion': 1, 'state': 'SOURCE_ONLY_FINITE_PREPARATION_RECEIPT_V1',
           'result': descriptor(HERE / 'results.json'),
           'sourceDataEvidence': descriptor(HERE / 'source-results.json'),
           'rawCheckerTerminal': descriptor(HERE / 'evidence/final/terminal.json'),
           'inputManifest': descriptor(HERE / 'input-freeze.json'),
           'derivations': descriptor(HERE / 'derivations.json'),
           'ownActions': 'Only own Python source/data/model preparation, checking and seal; no owner/codecs/runtime actions.',
           'historicalPacketsMutated': False}
(HERE / 'source-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
files = sorted(p for p in HERE.rglob('*') if p.is_file())
assert not any(p.is_symlink() for p in HERE.rglob('*'))
index = {'schemaVersion': 1, 'state': 'SEALED_UNAPPLIED_SOURCE_ONLY_ZLIB_NODE_ERROR_SEMANTICS_CANDIDATE_V1',
         'files': [descriptor(p, True) for p in files], 'sourceOnly': True,
         'sourcePeer': None, 'rootAuthority': None, 'nativeBuild': None,
         'runtimeValidation': None, 'adoption': False}
(HERE / 'index.json').write_text(json.dumps(index, indent=2) + '\n')
for row in index['files']:
    assert descriptor(HERE / row['path'], True) == row
print(json.dumps({'index': descriptor(HERE / 'index.json'), 'members': len(files),
                  'result': descriptor(HERE / 'results.json'), 'receipt': descriptor(HERE / 'source-receipt.json')}))
