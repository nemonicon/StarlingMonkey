# Exact original candidate body using actual explicit-root verifier.
def candidate(label, output, common):
    verify_frozen_variant=common.verify_frozen_variant
    RECIPE=common.RECIPE
    receipt_path, receipt, metadata, receipt_digest = verify_frozen_variant(label, output, return_receipt_digest=True)
    rows = [{'path': row['path'], 'sha256': row['sha256'], 'bytes': row['bytes']} for row in receipt['copies']]
    return {'state': 'unreviewed-crypto-owner355-freeze-pin-candidate',
        'variant': label, 'label': label, 'gcStress': metadata['gcStress'], 'entropyPolicy': metadata['entropyPolicy'],
        'classicStreamsEnabled': metadata['classicStreamsEnabled'],
        'sourceContractVersion': 'sm-webcrypto-key-owner-and-prototype-guard-source-v1', 'classicTraceSourcePolicy': metadata['classicTraceSourcePolicy'], 'cryptoKeyOwnershipPolicy':metadata['cryptoKeyOwnershipPolicy'],
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

