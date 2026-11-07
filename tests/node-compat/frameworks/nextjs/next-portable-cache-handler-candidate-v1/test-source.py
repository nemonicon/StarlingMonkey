"""Read-only Source witness checks. Does not import/parse/execute JavaScript."""
from pathlib import Path
import ast
import hashlib
import json

HERE = Path(__file__).resolve().parent


def main():
    checks = 0

    def need(ok, message):
        nonlocal checks
        if ok is not True:
            raise AssertionError(message)
        checks += 1

    def descriptor(row):
        p = Path(row['path'])
        need(p.is_absolute() and p.resolve() == p and p.is_file(), 'canonical Source file')
        raw = p.read_bytes()
        need(len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], 'Source hash')
        return raw

    manifest = json.loads((HERE / 'manifest.json').read_bytes())
    refs = json.loads(descriptor(manifest['sourceReferences']))
    need(refs['state'] == 'OPTIONAL_CACHE_HANDLER_SOURCE_REFERENCES_UNEXECUTED_V1', 'Source-only scope')
    for row in refs['sources']:
        raw = descriptor(row)
        lines = raw.decode().splitlines()
        need(all(type(a) is int and type(b) is int and 1 <= a <= b <= len(lines)
                 for a, b in row['lineRanges']), 'finite actual Source ranges')
    handler = descriptor(manifest['handler']).decode()
    descriptor(manifest['testSource'])
    need(manifest['extension'] == 'cacheHandler' and manifest['exports'] == ['default CommonJS handler class'], 'genuine extension')
    policy = manifest['fetchPolicy']
    need(policy['maximumCooperativeFiles'] == 2 * (policy['slots'] + len(policy['declaredTags'])) == 140, 'finite fixed namespace')
    need(policy['maximumLogicalFileBytes'] == 2 * (policy['slots'] * policy['recordBytes'] + len(policy['declaredTags']) * policy['epochBytes']) == 8413184, 'logical cap arithmetic')
    need(policy['associationsPerHandler'] == 64 and len(set(policy['declaredTags'])) == 6, 'bounded association and tag profile')
    need(manifest['delegatedKinds'] == ['APP_PAGE', 'APP_ROUTE', 'PAGES'], 'declared route fallback')
    need(all(manifest[k] is None for k in ['actualSyntaxCheck', 'actualFakeTests', 'actualFilesystemTests',
             'actualInteropProbe', 'actualNextBuild', 'actualNodeScenario', 'actualGuestScenario']), 'no operational claims')
    need(all(manifest[k] is False for k in ['applicationChanged', 'nativeOrHostOrWorldChanged',
             'originalFailedCounterGateAccepted', 'productionReady']), 'existing gate remains unchanged')
    # These are finite Source inventory observations, not a JS parser, control
    # flow proof or behavior test. Native runtime checks and fake tests are NULL.
    need('module.exports = class PortableFetchCacheHandler' in handler, 'CommonJS class')
    need("require('next/dist/server/lib/incremental-cache/file-system-cache.js').default" in handler, 'real pinned delegate')
    need('maxMemoryCacheSize: 0' in handler and 'Delegate.memoryCache === undefined' in handler, 'zero option with no static-cache mutation')
    need("{ flag: 'wx' }" in handler and 'renameSync(pending, p)' in handler, 'existing publication APIs')
    need('unlinkSync' not in handler and 'flush:' not in handler and 'mode:' not in handler, 'no online reclamation or unsupported write options')
    need('setTimeout' not in handler and 'setInterval' not in handler and 'process.env' not in handler, 'no timers or invented runtime config')
    ast.parse(Path(__file__).read_text(), filename=str(Path(__file__)))
    print(json.dumps({'sourceOnly': True, 'sourceChecks': checks, 'javascriptParsedOrExecuted': False,
                      'cacheFilesystemUsed': False, 'nextImported': False, 'actorInvoked': False}))


if __name__ == '__main__':
    main()
