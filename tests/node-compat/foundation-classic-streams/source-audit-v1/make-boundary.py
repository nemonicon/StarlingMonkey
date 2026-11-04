#!/usr/bin/env python3
"""Finite proposed boundary from the actual pinned inventory; no runtime support claim."""
import json
from pathlib import Path
here = Path(__file__).resolve().parent
audit = json.loads((here/'source-audit.json').read_text())
assert audit['node'] == 'v22.14.0'
root = audit['modules']['node:stream']['exports']
assert len(root) == 24
consumers = audit['modules']['node:stream/consumers']['exports']
assert len(consumers) == 6
promises = audit['modules']['node:stream/promises']['exports']
assert len(promises) == 3
rows = []
for module, names in [('node:stream',root),('node:stream/promises',promises),('node:stream/consumers',consumers)]:
    for name in names:
        blob = module.endswith('/consumers') and name in ['blob','arrayBuffer','buffer']
        operators = module == 'node:stream' and name in ['compose','duplexPair']
        rows.append({'module':module,'export':name,'currentStatus':'unavailable','targetAvailability':'not-installed',
            'requiredCapability':[],
            'proposedStage':'Blob ownership/semantic gate' if blob else 'pure operators/pair gate' if operators else 'text/json consumer gate' if module.endswith('/consumers') else 'coherent classic-core/lifecycle gate',
            'proposedInitialStatus':'import-only' if blob else 'partial after independent validation',
            'strategy':'Finite explicit throwing call/new binding until Blob gate' if blob else 'Explicit default graph record' if name=='default' else 'Audited guest JavaScript state machine/facade with shared native dependencies',
            'validation':['exact Node22 finite export/default graph','real installed module aliases/static-CJS/uncached dynamic imports','ordinary supported-domain differential and explicit excluded operations','top-level componentization failure when unsupported'],
            'note':'Source-only proposal: no export in this row is installed by this packet; planned status is not verified support.'})
members = []
for name, record in audit['constructors'].items():
    for location in ['static','prototype']:
        for member in record['node'][location]:
            private = member['keyKind'] == 'nonregistry-reflection-only-symbol'
            members.append({'owner':name,'location':location,'inventory':member,
                'currentStatus':'unavailable','targetAvailability':'not-installed',
                'publicApiClaim':not private,'requiredCapability':[],
                'strategy':'Reflection-only observation; nonregistry symbol descriptions are not portable binding keys' if private else 'Node inventory requirement; executable target presence/behavior requires a future actual candidate',
                'validation':'Exact selected member/overload vectors; a bundled inherited member is unverified until independently exercised'})
legacy = [{'module':name,'bareAlias':name.removeprefix('node:'),'exports':record['exports'],
    'currentStatus':'unavailable','proposedStatus':'deferred','requiredCapability':[],
    'reason':'Deprecated Node JSStreamSocket depends on internal native stream_wrap/async_wrap/native-resource behavior; no portable replacement inferred' if name=='node:_stream_wrap' else 'Constructor default identity does not imply matching named ESM export inventory; admit later only with a separate explicit manifest'}
    for name,record in audit['modules'].items() if name.startswith('node:_stream_')]
result={'schemaVersion':1,'node':'v22.14.0','state':'SOURCE_ONLY_PROPOSAL',
    'currentModuleStatus':'node:stream, node:stream/promises and node:stream/consumers are not registered/admitted',
    'exportRows':rows,'nodeOwnMemberInventoryRows':members,'legacyModuleRows':legacy,
    'separateInstalledDependency':{'id':'node:stream/web','status':'partial selected m0.9 contract, not a classic substitute','inventory':audit['modules']['node:stream/web']['exports']},
    'relationships':['stream.default === stream.Stream','Stream.Stream === Stream','stream.promises === promises.default',
        'Initially default properties equal corresponding named bindings','pipeline/finished util.promisify.custom getters equal promises.pipeline/finished'],
    'interopProposal':'Six real IDs for three namespaces/bare aliases; strict factory/shared constructor graph. Static literal CommonJS lowering returns the default object/callable; no public runtime CommonJS loader or syncBuiltinESMExports.',
    'proposedGlobals':[],'selectedWasiInterfaces':[]}
(here/'proposed-api-boundary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'exportRows':len(rows),'nodeOwnMemberInventoryRows':len(members),'legacyModuleRows':len(legacy)}))
