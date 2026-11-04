"""Seal original-context source only. No codec/helper/action module is imported."""
from pathlib import Path
import hashlib,json,ast
HERE=Path(__file__).resolve().parent
PARENT=HERE.with_name('cost-comparison-candidate-v1')
PEER=HERE.with_name('independent-zlib-cost-comparison-source-review-v1')
def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb')as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def main():
    assert not(HERE/'index.json').exists()
    rows={}
    def add(path,role,expected=None,size=None):
        path=Path(path).absolute();assert path.is_file()and not path.is_symlink(),path
        row={'path':str(path),'realpath':str(path.resolve()),'sha256':digest(path),'bytes':path.stat().st_size}
        if expected is not None:assert row['sha256']==expected,path
        if size is not None:assert row['bytes']==size,path
        if str(path)in rows:
            assert all(rows[str(path)][k]==v for k,v in row.items())
            if role not in rows[str(path)]['roles']:rows[str(path)]['roles'].append(role)
        else:rows[str(path)]={**row,'roles':[role]}
    def indexed(root,sha,count,role):
        add(root/'index.json',role,sha);index=json.loads((root/'index.json').read_bytes());assert len(index['files'])==count
        for row in index['files']:add(root/row['path'],role,row['sha256'],row['bytes'])
    indexed(PARENT,'e29c596df3c809bab8fd3851b224a7ec4e84177d791c5d1f909072985f047ef8',83,'INDEXED_ONLY_ORIGINAL_SOURCE_NOT_PREPARATION_REINTERPRETATION')
    indexed(PEER,'661f84883764fb33411a1d6052413a0755e2c115ca8d49395619e2e84b4dfe29',10,'INDEXED_ONLY_ORIGINAL_SOURCE_REVIEW')
    add(HERE.parent/'cost-source-protocol-amendment-root-decision-v1.json','HISTORICAL_ROOT_SOURCE_ONLY_DECISION','f96646cb3321aec452e9aef4d6b1798016400808cdd5a937d80f4e63f65109cf',3785)
    add(HERE.parent/'cost-source-protocol-amendment-root-decision-v2.json','CURRENT_ROOT_SOURCE_ONLY_DECISION','0025c7a1083d9291effe0cf51bbfef4e154353db75d433dae07f296d46d61cc6',5472)
    ff=Path('/tmp/starling-node-compat/native-toolchain-lock/node_modules/fflate')
    add(ff/'esm/browser.js','PINNED_BROWSER_SOURCE_NOT_EXECUTED','b7ca4450b19559a1d50eb381adcee94b82449674be4cd17789d9beba7e6122a1',90922)
    add(ff/'package.json','PINNED_BROWSER_PACKAGE_DATA');assert json.loads((ff/'package.json').read_bytes())['version']=='0.8.3'
    add(ff/'LICENSE','PINNED_BROWSER_MIT_LICENSE');assert(ff/'LICENSE').read_bytes()==(HERE/'LICENSE.fflate').read_bytes()
    add('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node','PURE_PARSE_AND_FUTURE_ORACLE_BINARY','e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0')
    source=json.loads((HERE/'evidence/source-results.json').read_bytes())
    for row in source['nodeApiSourceEvidence']:add(row['path'],'PINNED_NODE_PUBLIC_API_SOURCE_NOT_EXECUTED',row['sha256'],row['bytes'])
    historical=HERE.parent/'cost-guest-draft-pure-root-results-v1.json'
    if historical.exists():add(historical,'HISTORICAL_ROOT_DRAFT99_NOT_FINAL_SOURCE_PROOF','1adcdb633b25ee1743e2295d305892d3d7b71951f7076d2b63b796e3df892084')
    for path in HERE.glob('*.py'):ast.parse(path.read_bytes())
    pure=json.loads((HERE/'evidence/pure-results.json').read_bytes());syntax=json.loads((HERE/'evidence/syntax-results.json').read_bytes())
    assert pure['forbiddenProviderCalls']==0 and pure['actualCodecOrFflateNodeZlibOracleBundleComponentGuestHostPilotOrTimingExecuted']is False
    assert source['codecOrFflateNodeZlibOracleBundleNativeGuestHostPilotOrTimingExecuted']is False and all(row['exitCode']==0 for row in syntax['commands'])
    for path in sorted(HERE.rglob('*')):
        if path.is_file()and '__pycache__'not in path.parts and path.name not in ['index.json','source-inputs.json','source-receipt.json']:add(path,'OWN_SOURCE_OR_EXPLICIT_PREPARATION_HISTORY')
    def put(name,value):
        with(HERE/name).open('x')as stream:json.dump(value,stream,indent=2);stream.write('\n')
    put('source-inputs.json',{'schemaVersion':1,'state':'ORIGINAL_CONTEXT_SOURCE_PREPARATION_REFERENCES_ONLY','originalPreparationRoot':str(HERE),'files':sorted(rows.values(),key=lambda row:row['path']),'parentPreparationManifestsFollowed':False,'completeNativeOrPackagingClosureClaim':False,'futureActionAuthority':None})
    put('source-receipt.json',{'schemaVersion':1,'state':'CODEC_COST_GUEST_ORACLE_SOURCE_SEALED_UNEXECUTED','parentProposalIndexSha256':'e29c596df3c809bab8fd3851b224a7ec4e84177d791c5d1f909072985f047ef8','parentReviewIndexSha256':'661f84883764fb33411a1d6052413a0755e2c115ca8d49395619e2e84b4dfe29','rootProtocolDecisionSha256':'0025c7a1083d9291effe0cf51bbfef4e154353db75d433dae07f296d46d61cc6','primaryCases':30,'rawFixtureCount':5,'proposedOrdinaryExports':7,'allProposedReturnTypes':'string','untimedUniqueEncoderOutputsRequired':45,'untimedUniqueCrossDecoderEdgesRequired':135,'additionalFfOffProofRequired':True,'actualEncodedOutputsOrOracle':None,'actualEmittedABI':None,'actualComponentTuples':None,'nativeOrEngineSourceChanged':False,'operationalAdmissionChanged':False,'actualCodecFflateNodeZlibOracleBundleNativeGuestHostPilotOrTimingExecuted':False,'pureChecks':pure['passed'],'pureProviderCalls':pure['forbiddenProviderCalls'],'sourceChecks':source['passed'],'nodeParseOnlyChecks':syntax['passed'],'sourcePreparationReferences':len(rows),'originalContextsPreserved':True,'rootDraft99ProofTransferred':False,'futureRootPositiveAuthority':None})
    files=[]
    for path in sorted(HERE.rglob('*')):
        if path.is_file()and '__pycache__'not in path.parts and path.name!='index.json':files.append({'path':str(path.relative_to(HERE)),'sha256':digest(path),'bytes':path.stat().st_size})
    put('index.json',{'schemaVersion':1,'state':'SEALED_UNEXECUTED_CODEC_COST_GUEST_ORACLE_SOURCE_V1','files':files,'sourcePreparationReferences':len(rows),'actualPositiveAuthority':None,'runtimeOrPerformanceClaim':False})
    print(json.dumps({'indexSha256':digest(HERE/'index.json'),'files':len(files),'sourceInputs':len(rows),'receiptSha256':digest(HERE/'source-receipt.json'),'pure':pure['passed'],'source':source['passed'],'syntax':syntax['passed'],'codecCalls':0}))
if __name__=='__main__':main()
