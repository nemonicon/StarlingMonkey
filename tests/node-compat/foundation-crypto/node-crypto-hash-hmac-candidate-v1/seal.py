"""Seal this SOURCE proposal only. No action authority or native acceptance."""
from pathlib import Path
import ast, hashlib, json
OWN=Path(__file__).resolve().parent
def row(p, relative=False):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return {'path':str(p.relative_to(OWN)) if relative else str(p),'sha256':h.hexdigest(),'bytes':p.stat().st_size}
def dump(n,v): (OWN/n).write_text(json.dumps(v,indent=2)+'\n')
assert not (OWN/'index.json').exists(), 'Sealed packet is immutable; use a successor'
for p in OWN.rglob('*'):
    assert not p.is_symlink(), f'unexpected symlink {p}'
checks=json.loads((OWN/'source-checks.json').read_text())
assert checks['state']=='UNCOMPILED_SOURCE_AND_HOST_MOCK_CHECKS_PASSED'
inputs=json.loads((OWN/'source-inputs.json').read_text())
for r in inputs['files']:
    actual=row(Path(r['path']))
    assert all(actual[k]==r[k] for k in ['path','sha256','bytes']), r
for n in ['prepare-source.py','validate-source.py','seal.py']:
    ast.parse((OWN/n).read_text(),filename=n)
dump('preparation-history.json',{'schemaVersion':1,'allFailuresRetained':True,
 'sourceOnlyNetworkReads':'Five official tagged Node v22.14.0 text/license files; no execution',
 'attempts':[{'path':'evidence/derive-1','exitCode':0},{'path':'evidence/validation-driver-1','exitCode':1,
  'reason':'Reader required a literal JS_GetUint8ArrayData token; actual header generates it with Uint8 macro'},
 {'path':'evidence/validation-driver-2','exitCode':0},{'path':'evidence/derive-2','exitCode':0},
 {'path':'evidence/derive-3','exitCode':0},{'path':'evidence/validation-driver-3','exitCode':0},
 {'path':'evidence/derive-4','exitCode':0},{'path':'evidence/validation-driver-4','exitCode':0},
 {'path':'evidence/derive-5','exitCode':0},{'path':'evidence/validation-driver-5','exitCode':0}],
 'latestFacadeMockChecks':checks['facadeMockChecks'],'noTargetCryptoOrCompilerAction':True})
dump('results.json',{'schemaVersion':1,'state':'NODE_CRYPTO_SHA256_HASH_HMAC_SOURCE_PROPOSAL_SEALED_UNCOMPILED_V1',
 'sourceOnly':True,'independentSourceReview':None,'rootAuthority':None,
 'scope':['explicit Node22.14.0 namespace/stub policy','SHA256 factories/update/digest facade',
  'owned EVP native template','default copying baseline and guarded borrowing proposal','unapplied real registration/CMake afterimages'],
 'checks':{'finiteSourceAndDataChecks':checks['sourceChecks'],'facadeHostMockChecks':checks['facadeMockChecks'],
  'nativeLifetimePureModelCases':checks['nativeOwnerModelCases'],'nodeGrammarChecks':checks['grammarChecks'],
  'pythonAstChecks':3,'sourceInputsRechecked':len(inputs['files'])},
 'nativeCompiled':False,'nativeKernelExecuted':False,'actualHashOrHmacCalls':0,'nodeCryptoOracleExecuted':False,
 'engineActionsInvoked':False,'gcActionsInvoked':False,'componentActionsInvoked':False,
 'namespace':{'esmNamesIncludingDefault':68,'defaultOwnNames':71,'implementedCallableFactories':['createHash','createHmac'],
  'meaningfulNumericConstants':9,'constantsFullNodeSurface':False,
  'existingNativeValueAliases':['webcrypto','subtle'],'actualAliasRuntimeValidation':None,'fullNodeCryptoCompatibility':False},
 'ownership':{'nativeStateForegroundFinalized':True,'keyAlwaysCopiedBeforeProviderInit':True,
  'copyBaselineDefault':True,'borrowOptionDefault':False,'allSecretCopiesErasedClaim':False,'runtimeGcProof':False},
 'requiredFutureGates':['independent Source review','new actual source policy and full count/manifest lineage',
  'SDK frontend and native build','provider/allocator/entropy OFF and actual imports[] review',
  'actual key/digest Node oracle','retained/fresh guest/ownership/GC/error cases under new authority',
  'separate borrowing activation and performance experiment if requested'],
 'unresolved':['C++ template has never been compiled','integrated provider and NoGC behavior untested',
  'exact provider/allocation Node error codes not implemented','no real crypto/vector/GC/zeroization proof',
  'live-state snapshot unsupported','no filesystem/server or complete Next compatibility'],
 'runtimeAcceptanceClaim':False,'operationalAdmission':False,'adoptionAllowed':False})
dump('source-receipt.json',{'schemaVersion':1,'state':'UNCOMPILED_SOURCE_PRESERVATION_ONLY',
 'results':row(OWN/'results.json'),'sourceChecks':row(OWN/'source-checks.json'),
 'externalInputLedger':row(OWN/'source-inputs.json'),'integrationDerivation':row(OWN/'integration-derivation.json'),
 'priorNativeFilesMutated':False,'sealedPredecessorsMutated':False,'targetActionsInvoked':False,
 'authorityGranted':False,'note':'Only own root index.json is excluded from index membership; nested indices must be indexed.'})
payload=[row(p,True) for p in sorted(OWN.rglob('*')) if p.is_file() and p not in [OWN/'index.json',OWN/'member-ledger.json']]
dump('member-ledger.json',{'schemaVersion':1,'scope':'all payload files except this ledger and only the own root index', 'files':payload})
members=[row(p,True) for p in sorted(OWN.rglob('*')) if p.is_file() and p!=OWN/'index.json']
dump('index.json',{'schemaVersion':1,'state':'UNCOMPILED_SOURCE_PACKET_INDEX','files':members})
expected={r['path'] for r in members}|{'index.json'}
actual={str(p.relative_to(OWN)) for p in OWN.rglob('*') if p.is_file()}
assert actual==expected,(actual-expected,expected-actual)
for r in members:
    assert row(OWN/r['path'],True)==r
assert {r['path'] for r in payload}==actual-{'index.json','member-ledger.json'}
print(json.dumps({'state':'SEALED_UNCOMPILED_SOURCE_ONLY','index':row(OWN/'index.json'),'results':row(OWN/'results.json'),
 'receipt':row(OWN/'source-receipt.json'),'indexedMembers':len(members),'actualFiles':len(actual),'targetActionsInvoked':False}))
