"""Generate finite constants/declarations from the pinned local Node inventory."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
INVENTORY = HERE.parent/'inventory.node-v22.14.0.json'
def main():
    raw = INVENTORY.read_bytes()
    inventory = json.loads(raw)
    implemented = {'deflateSync','inflateSync','gzipSync','gunzipSync','deflateRawSync','inflateRawSync'}
    names = [row['name'] for row in inventory['exports'] if row['name'] != 'default']
    assert len(names) == 39
    deferred = [row['name'] for row in inventory['exports'] if row['type'] == 'function' and row['name'] not in implemented]
    assert len(deferred) == 31
    values = {kind: {name: row['value'] for name,row in inventory[kind].items()} for kind in ['constants','codes']}
    lines = ['// Generated from the pinned Node22 runtime inventory. No runtime host use.']
    for kind in ['constants','codes']:
        lines.append(f'export const {kind} = Object.freeze(Object.assign(Object.create(null), '+json.dumps(values[kind],separators=(',',':'))+'));')
    (HERE/'constant-data.generated.mjs').write_text('\n'.join(lines)+'\n')
    source = (HERE/'zlib-facade.template.mjs').read_text()
    declarations = '\n'.join(f"  function {name}() {{ unsupported('{name}'); }}" for name in deferred)
    bindings = '  const root = {'+', '.join(names)+'};\n'
    bindings += "  for (const key of Object.keys(constants)) if (!key.startsWith('BROTLI'))\n"
    bindings += "    Object.defineProperty(root, key, {value: constants[key], enumerable: false});\n"
    bindings += '  Object.freeze(root);\n  return Object.freeze({default: root, '+', '.join(names)+'});'
    assert source.count('// GENERATED_DECLARATIONS') == source.count('// GENERATED_BINDINGS') == 1
    source = source.replace('// GENERATED_DECLARATIONS', declarations.strip()).replace('// GENERATED_BINDINGS', bindings.strip())
    (HERE/'zlib-facade.generated.mjs').write_text(source)
    contract = {'schemaVersion':1,'state':'UNINSTALLED_FACADE_PROPOSAL_NO_PUBLIC_SUPPORT',
        'profileVersion':'sm-node-22.14.0-zlib-facade-template-v1','node':inventory['node'],
        'nodeRevision':inventory['nodeRevision'],'inventorySha256':hashlib.sha256(raw).hexdigest(),
        'moduleIds':['node:zlib','zlib'],'exports':[],'requiredWasiImports':[],
        'inputLimit':1048576,'outputLimit':16777216,'actualGuestTested':False}
    for row in inventory['exports']:
        name = row['name']
        status = 'partial-proposal' if name in implemented else 'import-only-data-proposal' if name in {'constants','codes','default'} else 'deferred-call-and-construct-refusal'
        contract['exports'].append({'name':name,'type':row['type'],'status':status})
    (HERE/'export-contract.proposal.json').write_text(json.dumps(contract,indent=2)+'\n')
    print(json.dumps({'namedBindings':len(names),'partialSyncProposals':len(implemented),'deferredCallables':len(deferred),'node':inventory['node'],'guestPerformed':False}))

if __name__ == '__main__':
    main()
