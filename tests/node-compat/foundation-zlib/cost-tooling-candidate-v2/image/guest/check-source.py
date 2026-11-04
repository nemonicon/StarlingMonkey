"""Finite read/hash/source checks only; never imports a JS/codec owner module."""
from pathlib import Path
import ast,hashlib,json,re,sys
HERE=Path(__file__).resolve().parent
PARENT=HERE.with_name('cost-comparison-candidate-v1')
PEER=HERE.with_name('independent-zlib-cost-comparison-source-review-v1')
checks=[]
def sha(value):return hashlib.sha256(value).hexdigest()
def check(name,condition=True):assert condition,name;checks.append(name)
def indexed(root,digest,count):
    raw=(root/'index.json').read_bytes();assert sha(raw)==digest
    index=json.loads(raw);assert len(index['files'])==count
    for row in index['files']:
        value=(root/row['path']).read_bytes();assert sha(value)==row['sha256']and len(value)==row['bytes']
    return index
def text(name):return(HERE/name).read_text()
parent=indexed(PARENT,'e29c596df3c809bab8fd3851b224a7ec4e84177d791c5d1f909072985f047ef8',83)
peer=indexed(PEER,'661f84883764fb33411a1d6052413a0755e2c115ca8d49395619e2e84b4dfe29',10)
check('83originalProposalAnd10IndependentReviewFilesUnchangedIndexedOnly')
for name,digest,size in [('cost-source-protocol-amendment-root-decision-v1.json','f96646cb3321aec452e9aef4d6b1798016400808cdd5a937d80f4e63f65109cf',3785),('cost-source-protocol-amendment-root-decision-v2.json','0025c7a1083d9291effe0cf51bbfef4e154353db75d433dae07f296d46d61cc6',5472)]:
    raw=(HERE.parent/name).read_bytes();assert sha(raw)==digest and len(raw)==size
decision=json.loads((HERE.parent/'cost-source-protocol-amendment-root-decision-v2.json').read_bytes())
check('exactRootV2SourceOnlyDecisionAndPreservedHistoricalV1',decision['abi']['totalExports']==7 and decision['codecLibraryOrOracleExecutionAllowed']is False)
copies=json.loads((HERE/'copied-parent-files.json').read_bytes())
for row in copies['files']:
    raw=Path(row['from']).read_bytes();assert raw==(HERE/row['to']).read_bytes()and sha(raw)==row['sha256']and len(raw)==row['bytes']
check('sixExactParentFixtureProviderControlProtocolLicenseCopies')
old=(PARENT/'proposed-public-abi.wit').read_text();new=text('public-abi.wit')
expected=old.replace('  export checkpoint: func() -> string;','  export checkpoint: func() -> string;\n  export stage: func(record: string) -> string;\n  export validate: func(record: string) -> string;')
check('exactTwoAdditiveOrdinaryScalarABIExportsOldFiveUnchanged',new==expected)
check('sevenESMFunctionExportsExact',re.findall(r'^export function (\w+)\(',text('guest.mjs'),re.M)==['identity','setup','stage','observe','batch','checkpoint','validate'])
runtime=text('runtime.mjs');observe=runtime[runtime.index(' function observe('):runtime.index(' function batch(')];batch=runtime[runtime.index(' function batch('):runtime.index(' function checkpoint(')];validate=runtime[runtime.index(' function validate('):]
check('observeDoesNotSetupOrStageImplicitly','needActive(caseId)'in observe and 'prepare('not in observe and 'setup('not in observe and 'stage('not in observe)
check('observeExactlyOneCapturedMethodCallAndFullBase64Output',observe.count('invoke(row)')==1 and 'base64:base64(output)'in observe)
check('validateSameSetupOptionalStageAdjacentObservePair',validate.count('setup(request.caseId)')==1 and validate.count('stage(wire(request.stageRecord))')==1 and validate.count('observe(request.caseId)')==2 and 'return wire('in validate)
check('stageNoCodecBeforeExactActiveDecoderAndInputCaps',runtime[runtime.index(' function stage('):runtime.index(' function invoke(')].count('invoke(')==0 and 'stageRecord(jsonRecord(record))'in runtime and 'stage exact active decoder ID'in runtime)
check('priorOutputClearedBeforeAnyBatchWork',batch.index('priorOutput=null')<batch.index('operationCount(') and 'priorOutput='not in batch[batch.index('const selected='):])
check('timedCodecFullOutputConsumptionNoPerByteRetainedTrace','consumeFNV1a(output)'in batch and 'aggregateStep('in batch and 'outputArraysRetained:false'in batch and '.push('not in batch)
check('allNamedFunctionEntriesAndExplicitCountersNoOuterGuess','publicFunctionEntries' in runtime and 'perExportEntries'in runtime and 'outerExportCalls'not in runtime and 'codecCalls++'in runtime)
check('wireAndStagingLimitsRemainExact','MAX_INPUT=1048576,MAX_OUTPUT=16777216,MAX_RAW=524288,MAX_WIRE=2097152'in text('contract.mjs') and 'cap before allocation'in text('contract.mjs'))
check('noNodeProviderOptionsOrFFDefaultsChanged',text('providers.mjs')==(PARENT/'providers.template.mjs').read_text() and 'Reflect.apply(selected[name],undefined,[input])'in text('providers.mjs'))
check('finiteBrowserAliasAndNativeImports','codec:fflate-browser'in text('fflate-provider.mjs') and "from 'node:zlib'"in text('native-provider.mjs') and 'jco:'not in text('native-provider.mjs')+text('fflate-provider.mjs'))
oracle=text('node-oracle.mjs')
check('oracleDoesNotImportCodecAndRequiresFutureInjectedAuthorityBindings',"from 'node:zlib'"not in oracle and "import('node:zlib')"not in oracle and "'rootActionAuthoritySha256'"in oracle and "'costToolingIndexSha256'"in oracle)
audit=oracle[oracle.index('async function auditNodeDecode('):oracle.index('export async function createNodeOracle(')]
check('NodeEncodedCapBeforeDecoderAndDurableRawBeforeChecks',oracle.index("name:'node-'+spec.id+'-'+format+'-first'")<oracle.index("'actual encoded input cap BEFORE decoder'") and audit.index('BEFORE decoder')<audit.index('const decodedValue=await retainedNodeCall') and audit.index('const decoded=await retainedNodeInfo')<audit.index('whole Node decoded raw bytes'))
check('externalNodeInfoOnlyNotNativeOptions',oracle.count('info:true,maxOutputLength:MAX_OUTPUT')==2 and 'info:true'not in text('providers.mjs'))
check('singleMemberActualRawPayloadConsumptionGate','deflatePayload(format,encoded)'in audit and 'payloadDecoded.sourceBytesConsumed===payload.length'in audit and 'bytesEqual(payloadDecoded.buffer,raw)'in audit)
transport=text('node-transport.mjs')
check('typedNodeReturnThrowAndInfoBeforeAssertions',transport.index("name+'-return-transport'")<transport.index('if(Buffer.isBuffer(value))') and transport.index("name+'-buffer-transport'")<transport.index("'Node info Buffer'") and transport.index("name+'-sourceBytesConsumed-transport'")<transport.index("'public Node consumed byte count'") and "name+'-throw'"in transport)
check('sourceRendererHashBeforeJSONAndNoCodec',text('render-node-inputs.mjs').index('sha(raw)===expectedOracleSha256')<text('render-node-inputs.mjs').index('JSON.parse(') and 'node:zlib'not in text('render-node-inputs.mjs'))
check('unconfiguredInputModuleNullAndNoPositiveActions','oracleInputs=null'in text('oracle-inputs.UNCONFIGURED.mjs') and json.loads((HERE/'future-authority.json').read_bytes())['actionsAllowed']is False)
guest_files=['guest.mjs','runtime.mjs','contract.mjs','cases.generated.mjs','fixtures.mjs','controls.mjs','owned-window.mjs','output-stability.mjs','providers.mjs','native-provider.mjs','fflate-provider.mjs']
edges=[]
for name in guest_files:
    source=text(name)
    for match in re.finditer(r"from\s*(['\"])([^'\"]+)\1",source):edges.append({'importer':name,'request':match[2]})
check('guestClosureNoHostInspectionOrTimers',all(not re.search(r"from\s*['\"]node:(?:fs|crypto|process|child_process)",text(name))for name in guest_files))
node_sources=[]
for name,needles in [('lib/zlib.js',['function zlibBufferSync(engine, buffer)','return { buffer, engine }','self.bytesWritten = inputRead']),('test/parallel/test-zlib-convenience-methods.js',['info: true','`${method[1]}Sync`'])]:
    path=HERE.parent/'source-freeze/node'/name;raw=path.read_bytes();source=raw.decode();assert all(needle in source for needle in needles)
    node_sources.append({'path':str(path),'sha256':sha(raw),'bytes':len(raw),'symbols':needles,'readOnlySourceNoNodeCodecExecuted':True})
check('actualPinnedNodeInfoAndConsumedInputAPIsFromLocalSource')
for path in HERE.glob('*.py'):ast.parse(path.read_bytes())
check('pythonASTOnly')
check('priorFullBaselineVerifiedAfterProviderBeforeMutation',observe.index('invoke(row)')<observe.index('requirePriorOutputUnchanged(priorOutput)')<observe.index('priorOutput.output[0]=saved^255'))
check('priorFullBaselineAlsoVerifiedAfterRestoration','finally{priorOutput.output[0]=saved;requirePriorOutputUnchanged(priorOutput);}'in observe)
check('priorOutputCapturedFromFullReturnedBaseline','captureUntimedOutput(caseId,output,result.output.base64)'in observe and 'previousFullBytesUnchanged'in observe)
parent_runtime=(HERE.with_name('cost-guest-oracle-candidate-v1')/'runtime.mjs').read_text()
check('timingBatchExactParentBytes',batch==parent_runtime[parent_runtime.index(' function batch('):parent_runtime.index(' function checkpoint(')])
held=HERE.with_name('cost-guest-oracle-candidate-v1')
indexed(held,'473c997933b5df6560896c58d8dd79cb426a81d0730d24892b93d3edaa75a046',58)
check('heldV1All58FilesUnchanged')
derivations=json.loads((HERE/'source-derivations.json').read_bytes())
for row in derivations['files']:
    before=(held/row['path']).read_bytes();after=(HERE/row['path']).read_bytes()
    assert sha(before)==row['beforeSha256']and sha(after)==row['afterSha256']
    forward=before.decode()
    for edit in row['edits']:
        assert forward.count(edit['old'])==edit['count'];forward=forward.replace(edit['old'],edit['new'],edit['count'])
    assert forward.encode()==after
    reverse=after.decode()
    for edit in reversed(row['edits']):
        assert reverse.count(edit['new'])==edit['count'];reverse=reverse.replace(edit['new'],edit['old'],edit['count'])
    assert reverse.encode()==before
check('twoExecutableAfterimagesEightExactForwardReverseEdits',len(derivations['files'])==2 and sum(len(row['edits'])for row in derivations['files'])==8)
for name in ['cases.generated.mjs','fixtures.mjs','controls.mjs','providers.mjs','native-provider.mjs','fflate-provider.mjs','contract.mjs','owned-window.mjs','node-oracle.mjs','node-transport.mjs','render-node-inputs.mjs','framing.mjs','guest.mjs','public-abi.wit','future-authority.json','raw-fixture-oracle.json','oracle-inputs.UNCONFIGURED.mjs']:
    assert (held/name).read_bytes()==(HERE/name).read_bytes()
check('seventeenCorpusProviderOracleABIAuthorityAndTransportFilesByteIdentical')
out=Path(sys.argv[1]);assert out.is_absolute()and not out.exists()
with out.open('x')as stream:json.dump({'schemaVersion':1,'state':'FINITE_CODEC_COST_SOURCE_CHECKED_NOT_EXECUTED','passed':len(checks),'checks':checks,'guestSourceFiles':guest_files,'guestImportEdges':edges,'nodeApiSourceEvidence':node_sources,'parentPreparationRowsFollowed':False,'codecOrFflateNodeZlibOracleBundleNativeGuestHostPilotOrTimingExecuted':False},stream,indent=2);stream.write('\n')
print(json.dumps({'sourceChecks':len(checks),'codecCalls':0,'parentPreparationsReinterpreted':False}))
