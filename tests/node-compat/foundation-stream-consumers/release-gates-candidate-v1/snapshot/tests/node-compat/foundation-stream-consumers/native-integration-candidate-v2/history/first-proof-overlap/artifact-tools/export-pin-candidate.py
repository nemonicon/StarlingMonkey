"""Export actual frozen hashes as UNREVIEWED data. Never activate a pin file."""
import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
from artifact_common import OUTPUT, LABELS, RECIPE, sha, verify_frozen_variant

def candidate(label, output=OUTPUT):
    receipt_path, receipt, metadata, receipt_digest = verify_frozen_variant(label, output, return_receipt_digest=True)
    rows = [{'path': row['path'], 'sha256': row['sha256'], 'bytes': row['bytes']} for row in receipt['copies']]
    return {'state': 'unreviewed-consumers355-production-freeze-pin-candidate',
        'variant': label, 'label': label, 'gcStress': metadata['gcStress'], 'entropyPolicy': metadata['entropyPolicy'],
        'classicStreamsEnabled': metadata['classicStreamsEnabled'],
        'sourceContractVersion': 'sm-stream-consumers-text-json-source-v1', 'classicTraceSourcePolicy': metadata['classicTraceSourcePolicy'],
        'zlibEnabled':metadata['zlibEnabled'],'zlibSourcePolicy':metadata['zlibSourcePolicy'],'runtimeBackendProof':{'verified':False,'version':None,'vernum':None},
        'streamConsumersEnabled':metadata['streamConsumersEnabled'],'streamConsumersSourcePolicy':metadata['streamConsumersSourcePolicy'],
        'sourceFiles': 355, 'recipeSha256': RECIPE, 'engineBytes': receipt['engineBytes'],
        'engineSha256': receipt['engineSha256'], 'receiptSha256': receipt['receiptSha256'],
        'cmakeCacheSha256': metadata['cmakeCacheSha256'], 'compileCommandsSha256': metadata['compileCommandsSha256'],
        'freezeReceiptSha256': receipt_digest, 'freezeRoot': str(output),
        'enginePath': str(output / (label + '.engine.wasm')), 'sourceRoot': str(output / 'source'),
        'componentizeSourceRoot': str(output / 'componentize-source'), 'cachePath': str(output / (label + '-CMakeCache.txt')),
        'commandsPath': str(output / (label + '-compile_commands.json')), 'recipePath': str(output / 'build-engine.sh'),
        'freezeReceiptPath': str(receipt_path), 'coreSources': receipt['coreSources'], 'frozenFiles': rows,
        'parentEmbeddingCommandPath': receipt['postBuildEmbeddingEvidence']['path'],
        'parentEmbeddingCommandSha256': receipt['postBuildEmbeddingEvidence']['sha256'],
        'reviewRequired': True, 'runtimeAcceptanceClaim': False}

def main():
    assert len(sys.argv) >= 3, 'FRESH_OUTPUT_JSON normal-off|normal-runtime|gc-off|disabled-off [more completed labels]'
    output = Path(sys.argv[1]).absolute()
    assert not output.exists() and not output.is_symlink(), 'Never overwrite pin data'
    labels = sys.argv[2:]
    assert len(labels) == len(set(labels)) and all(label in LABELS for label in labels)
    variants = {label: None for label in LABELS}
    for label in labels:
        variants[label] = candidate(label)
    document = {'schemaVersion': 1, 'state': 'UNREVIEWED_STREAM_CONSUMERS355_PRODUCTION_PIN_CANDIDATES_V1',
        'variants': variants, 'requiresIndependentReviewAndNewAdmissionRevision': True,
        'notAcceptedByReviewedClassicPinSelector': True, 'consumerPinsModified': False,
        'guestExecutedByExporter': False}
    with output.open('x') as stream:
        json.dump(document, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'output': str(output), 'state': document['state'], 'labels': labels, 'admitted': False}))

if __name__ == '__main__':
    main()
