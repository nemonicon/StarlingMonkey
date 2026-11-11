"""Read the genuine current engine context without projecting older metadata."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
GUARD = REPO / 'tests/node-compat/frameworks/nextjs/next-native-export-diagnostic-next-root-results-v1/prepare-construction.py'
GUARD_SHA = '4bafbb2fd675bcee84746aea3988ae6eb597d64570d19cd3c8819aa158d2c5e4'


def main():
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('Use Python -I -B, without -O')
    if hashlib.sha256(GUARD.read_bytes()).hexdigest() != GUARD_SHA:
        raise RuntimeError('Original current-context reader changed')
    spec = importlib.util.spec_from_file_location('genuine_current_engine', GUARD)
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    context = guard.context()
    guard.protect(context)
    result = dict(schemaVersion=1, state='GENUINE_CURRENT_NATIVE_ENGINE_SELECTED_V1',
                  engine=guard.ENGINE, nativeMetadata=guard.NATIVE_METADATA,
                  genuineGuard=guard.row(GUARD), metadataKeys=sorted(context['metadata']),
                  buildEvidence=context['buildRefs'], sourceEvidence=context['sourceRefs'],
                  completeMetadataUsedWithoutProjection=True,
                  compilerPackageSelected=False, componentConstructed=False, guestExecuted=False,
                  productionProfilePromoted=False)
    guard.save(HERE / 'engine-selection.json', result)
    print(json.dumps(dict(engine=result['engine'], metadataKeys=len(result['metadataKeys']),
                         buildEvidence=len(result['buildEvidence']), sourceEvidence=len(result['sourceEvidence']),
                         selection=guard.row(HERE / 'engine-selection.json'))))


if __name__ == '__main__':
    main()
