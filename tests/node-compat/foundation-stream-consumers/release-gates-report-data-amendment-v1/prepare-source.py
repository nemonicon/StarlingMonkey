#!/usr/bin/env python3
"""Create owned source afterimages/data only. No owner imports or actions."""
from pathlib import Path
import hashlib,json,os,re
P=Path(__file__).resolve().parent
S=P.parent
B=S/'release-gates-candidate-v1'
C=S/'release-gates-context-amendment-v1'
F=S/'release-gates-activated-v2'
BPIN='a74dc603f7e42384892c9f4b69a2ba131a87a80daa38da19e91bbc2c099e5372'
CPIN='9080e48fbccaf74835bfb8c8ef54c91b8df54ff5eb6e4c2cdc1c83443ad79b70'
FPIN='562e4236c8f99a34323c57c26f92749dba4aaf3e5dc1a509d33ababd97d79250'
consumed={}
def h(b):return hashlib.sha256(b).hexdigest()
def read(p,sha=None):
 p=Path(p);assert p.is_file() and not p.is_symlink();b=p.read_bytes();assert sha is None or h(b)==sha;consumed[str(p)]=dict(path=str(p),sha256=h(b),bytes=len(b));return b
def js(p,sha=None):return json.loads(read(p,sha))
def out(n,b):
 p=P/n;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(b)
def obj(n,v):out(n,(json.dumps(v,indent=2)+'\n').encode())
def pinned(root,pin):
 d=js(root/'index.json',pin)
 for r in d['files']:
  b=read(root/r['path'],r['sha256']);assert len(b)==r['bytes']
 return d
base=pinned(B,BPIN);context=pinned(C,CPIN)
# The generated family is a historical witness; do not reuse its runtime pass.
family=js(F/'index.json',FPIN);fm={x['path']:x for x in family['files']}
classic='snapshot/tests/node-compat/foundation-classic-streams/production-trace-regression-activated-v1/'
util='snapshot/tests/node-compat/foundation-util/'
expected_source=js(F/(util+'native-component-results.json'),fm[util+'native-component-results.json']['sha256'])
expected=next(x['sha256'] for x in expected_source['sourceFiles'] if x['name']=='run-native-node.mjs')
origin=Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-util/native-source-freeze-v7/run-native-node.mjs')
producer=read(origin,expected);assert len(producer)==2251 and expected=='fe48fc8049fffbc7d60010f617369e498608db6e69cce05dbc4e06ed96a3c4ba'
out('data/run-native-node.mjs',producer)
node_oracle=read(F/(util+'native-node-results.json'),fm[util+'native-node-results.json']['sha256']);assert h(node_oracle)=='489cb9cf4fbe256201f70e385d4326ea32552d2f2a1f187211d9409e73838816'
receipt=js(S/'release-gates-release-off-v1-failure-root-results-v2.json','ce4c52bd15fcbfef91fa7b877fa77f2a911626d30a265f7157a97b038fe9a49d')
assert receipt['externalRawExitCode']==1 and receipt['utilComponentizationWasReached'] is True and receipt['overallReleasePassIssued'] is False

# Explicitly expand every late report-source list in the six optional runners,
# allocator and stream-web runners, and all required strict-stage assets.
matrix=[]
def required(caller,root,names,role):
 caller_row=fm[caller];read(F/caller,caller_row['sha256'])
 for name in names:
  rel=os.path.normpath(root+'/'+name);assert rel.startswith('snapshot/') and '/..' not in rel
  target=P/'data/run-native-node.mjs' if rel==util+'run-native-node.mjs' else F/rel
  raw=producer if rel==util+'run-native-node.mjs' else read(target,fm[rel]['sha256'])
  matrix.append(dict(caller=caller,callerSha256=caller_row['sha256'],path=rel,sha256=h(raw),bytes=len(raw),kind=role,executedByThisProposal=False))
required(classic+'release/runners/events.mjs','snapshot/tests/node-compat/foundation-events',['native-component.mjs','native-checks.mjs','native-require.cjs','checks.mjs','prototype-checks.mjs','run-native-component.mjs'],'LATE_REPORT_SOURCE_CAPTURE_DATA')
for kind in ['assert','querystring']:
 required(classic+'release/runners/'+kind+'.mjs','snapshot/tests/node-compat/foundation-'+kind,['native-component.mjs','native-require.cjs','run-native-component.mjs','checks.mjs'],'LATE_REPORT_SOURCE_CAPTURE_DATA')
required(classic+'release/runners/util.mjs',util.rstrip('/'),['run-native-component.mjs','run-native-node.mjs','native-component.mjs','native-dynamic.mjs','native-require.cjs','component-cases.mjs','prototype-scope.mjs'],'LATE_REPORT_SOURCE_CAPTURE_DATA')
required(classic+'common/runners/allocator.mjs','snapshot/tests/node-compat/foundation-alloc-unsafe/installed',['checks.mjs','component-v11.mjs','numeric-hooks-v11.mjs','static-require.cjs','run-component-v11.mjs'],'ALLOCATOR_REPORT_SOURCE_DATA')
sw='snapshot/tests/node-compat/foundation-stream-web/production-candidate'
sw_names=['native-component.mjs','native-checks.mjs','native-policies.mjs','native-require.cjs','native-aliases.mjs','native-preflight.mjs','native-preflight-contract.json','native-harness.mjs','run-native-component-v11.mjs','native-top-level-encoding.mjs']
sw_names+=['native-top-level-'+ctor+'-'+act+'.mjs' for ctor in ['compressionstream','decompressionstream'] for act in ['call','construct']]
sw_names+=['native-top-level-unknown-export-'+alias+'.mjs' for alias in ['canonical','bare']]
sw_names+=['../candidate/'+n for n in ['codec-cases.mjs','codec-node-results.json','guard-cases.mjs','byob-node-results.json','typed-view-cases.mjs','typed-view-node-results.json','controller-cases.mjs','controller-node-results.json']]
sw_names+=['../iteration/cases.mjs','../iteration/node-results.json','../iteration/intrinsics.mjs','../dataview/cases.mjs','../dataview/node-results.json','../dataview/policy.mjs','../profile.wit']
required(classic+'off/runners/stream-web.mjs',sw,sw_names,'STREAM_WEB_FINITE_EXPANDED_REPORT_SOURCE_DATA')
abort='snapshot/tests/node-compat/foundation-add-abort'
strict={'sync':['run-production-v11-sync.mjs','strict-event-v3.patch'],'runtime':['run-production-v11-runtime.mjs','componentize-strict-event-boundary-v2.patch','runtime-async-observation-results.json'],'late':['run-production-v11-late.mjs','componentize-strict-event-boundary-v2.patch'],'callbacks':['run-production-v11-callbacks.mjs','strict-event-v3.patch']}
for kind,names in strict.items():required(classic+'off/runners/'+kind+'.mjs',abort,names,'REMAINING_STRICT_STAGE_INPUT_OR_DIRECTORY_ANCHOR_NOT_EXECUTED')
focused=classic+'capability/focused'
required(focused+'/run-callback-return.mjs',focused,['callback-return-cases.mjs','callback-return-component.mjs','run-callback-return.mjs'],'FOLLOWON_REQUIRED_SOURCE_CAPTURE_DATA')
optional_capture=[]
for n in ['public-cases.mjs','run-node.mjs','node-results.json','component.mjs','require.cjs','profile.wit','preflight.mjs','harness.mjs','run-component.mjs','gc-component.mjs','run-gc.mjs']:
 rel=focused+'/'+n;optional_capture.append(dict(path=rel,present=rel in fm,sourcePolicy='Pinned harness explicitly catches ENOENT and continues for this optional capture list; no new requirement or silent successful input claim.'))
 if rel in fm:read(F/rel,fm[rel]['sha256'])
lineage=js(B/'lineage.json')
native355={x['path']:x['sha256'] for x in lineage['native355']}
oracle_maps=[]
for kind,names in [('assert',['assert.mjs','assert-strict.mjs','assert-factories.generated.h','export-manifest.assert.node-v22.14.0.json']),('querystring',['querystring.mjs','querystring-factories.generated.h','export-manifest.querystring.node-v22.14.0.json']),('util',None)]:
 rel='snapshot/tests/node-compat/foundation-'+kind+'/native-node-results.json';oracle=js(F/rel,fm[rel]['sha256']);keys=names if names is not None else [n for n in oracle['sources'] if n!='LICENSE.util']
 for n in keys:assert native355['builtins/node-compat/'+n]==oracle['sources'][n]
 oracle_maps.append(dict(kind=kind,oracle=rel,oracleSha256=h(read(F/rel)),keys=keys,readSemantics='Metadata sourceManifest hash lookup only, not join(here,name) file reads',licenseUtilExcluded=kind=='util',metadataProjection=False))
audit=dict(schemaVersion=1,state='FINITE_REQUIRED_REPORT_SOURCE_DATA_AND_STRICT_INPUT_CLOSURE',parentFamilyIndexSha256=FPIN,requiredReads=matrix,oracleBuiltinSourceMappings=oracle_maps,allocatorOracleChecks='common/runners/allocator.mjs checks source hash against oracle.sources[checks.mjs]; existing parent/installed source inputs remain exact',optionalCapturePolicy=optional_capture,newPhysicalSnapshotFiles=[util+'run-native-node.mjs'],producerDataReadOnly=True,oracleRegenerated=False,oldOracleSubstituted=False,strictStagesExecuted=False,allRuntimeReadSitesReviewedAsGeneralParser=False,scope='Finite exact caller/list expansions plus existing authenticated native/tool/historical contexts. Runtime outputs and dynamically generated guest sources are not source authority.')
obj('report-data-closure.json',audit)

origins=js(B/'snapshot-origins.json');assert not any(x['relativePath']=='tests/node-compat/foundation-util/run-native-node.mjs' for x in origins['files'])
origins['files'].append(dict(relativePath='tests/node-compat/foundation-util/run-native-node.mjs',originalPath=str(origin),canonicalOriginalPath=str(origin.resolve()),sha256=expected,bytes=len(producer),role='IMMUTABLE_V7_PRODUCER_SOURCE_READ_ONLY_DATA_NOT_EXECUTED',expectedSourceHashAuthority=dict(path=str(B/(util+'native-component-results.json')),sha256=h(read(B/(util+'native-component-results.json'))),jsonPointer='/sourceFiles/1'),currentOracleUnchangedSha256=h(node_oracle),notDirectlyBoundByCurrentOracleSources=True))
origins['files'].sort(key=lambda x:x['relativePath']);obj('snapshot-origins.after.json',origins)
run=read(C/'run-gates.after.mjs').decode();assert run.count('production-consumers355-release-gates-v2/')==1
run2=run.replace('production-consumers355-release-gates-v2/','production-consumers355-release-gates-v3/');out('run-gates.after.mjs',run2.encode())
graph=js(C/'selected-closure.after.json');newrow=dict(path=util+'run-native-node.mjs',sha256=expected,bytes=len(producer));assert not any(x['path']==newrow['path'] for x in graph['localModulesAndData'])
graph['localModulesAndData'].append(newrow)
known={x['path']:x for x in graph['localModulesAndData']}
edge_keys={(x['importer'],x['request'],x['target']) for x in graph['localEdges']}
for item in matrix:
 if item['path'] in known:assert all(known[item['path']][k]==item[k] for k in ['sha256','bytes'])
 else:
  entry={k:item[k] for k in ['path','sha256','bytes']};graph['localModulesAndData'].append(entry);known[item['path']]=entry
 request=os.path.relpath(item['path'],os.path.dirname(item['caller']))
 key=(item['caller'],request,item['path'])
 if key not in edge_keys:
  graph['localEdges'].append(dict(importer=item['caller'],request=request,target=item['path'],kind='FINITE_REQUIRED_REPORT_SOURCE_OR_STRICT_INPUT_DATA_NOT_IMPORTED_OR_EXECUTED'));edge_keys.add(key)
graph['localModulesAndData'].sort(key=lambda x:x['path'])
for x in graph['localModulesAndData']:
 if x['path']=='run-gates.mjs':x.update(sha256=h(run2.encode()),bytes=len(run2.encode()))
graph['requiredReportSourceData']=matrix
graph['state']='FINITE_PINNED_SELECTED_MODULE_DATA_PHYSICAL_CLOSURE_REPORT_SOURCE_M2_CORRECTED'
graph['scope']='Finite pinned import/data graph plus explicit dynamic report-source list expansion; not a general JavaScript parser or runtime success proof.'
obj('selected-closure.after.json',graph)

original=read(C/'publish.py').decode();text=original;edits=[]
def edit(old,new,label):
 global text
 assert text.count(old)==1,(label,text.count(old));text=text.replace(old,new);edits.append(dict(label=label,before=old,after=new))
edit("HERE=Path(__file__).parent.resolve();BASE=HERE.with_name('release-gates-candidate-v1');BASE_SHA='"+BPIN+"'", "HERE=Path(__file__).parent.resolve();BASE=HERE.with_name('release-gates-candidate-v1');BASE_SHA='"+BPIN+"';CONTEXT=HERE.with_name('release-gates-context-amendment-v1');CONTEXT_SHA='"+CPIN+"'",'distinct full immutable context parent')
edit("own=load(HERE/'index.json',args.index_sha256);base=load(BASE/'index.json',BASE_SHA)","own=load(HERE/'index.json',args.index_sha256);base=load(BASE/'index.json',BASE_SHA);context_parent=load(CONTEXT/'index.json',CONTEXT_SHA)",'authenticate all three source indices')
edit("for root,index in[(HERE,own),(BASE,base)]:","for root,index in[(HERE,own),(BASE,base),(CONTEXT,context_parent)]:",'full parent members recheck')
edit("for row in load(BASE/'source-inputs.preparation.json')['files']:checked(row['path'],row['sha256'],row['bytes'],False)","for row in load(BASE/'source-inputs.preparation.json')['files']:checked(row['path'],row['sha256'],row['bytes'],False)\n        for row in load(HERE/'source-inputs.json')['files']:checked(row['path'],row['sha256'],row['bytes'],False)",'new original-context data provenance checked before outputs')
edit("source_review['state']=='ROOT_REVIEWED_CONSUMERS355_RELEASE_CONTEXT_AMENDMENT_V1'and source_review['proposalIndexSha256']==args.index_sha256 and source_review['parentProposalIndexSha256']==BASE_SHA", "source_review['state']=='ROOT_REVIEWED_CONSUMERS355_RELEASE_REPORT_DATA_AMENDMENT_V1'and source_review['proposalIndexSha256']==args.index_sha256 and source_review['parentProposalIndexSha256']==BASE_SHA and source_review['contextAmendmentIndexSha256']==CONTEXT_SHA",'fresh exact source Root authority')
edit("output.name=='release-gates-activated-v2'","output.name=='release-gates-activated-v3'",'new immutable source output')
edit("payload=load(BASE/'payload-files.json')['files'];overrides={'native-preflight.template.mjs':HERE/'native-preflight.template.after.mjs','run-gates.mjs':HERE/'run-gates.after.mjs','selected-closure.json':HERE/'selected-closure.after.json'}", "payload=load(BASE/'payload-files.json')['files']+['"+util+"run-native-node.mjs','report-data-closure.json'];overrides={'native-preflight.template.mjs':CONTEXT/'native-preflight.template.after.mjs','run-gates.mjs':HERE/'run-gates.after.mjs','selected-closure.json':HERE/'selected-closure.after.json','snapshot-origins.json':HERE/'snapshot-origins.after.json','"+util+"run-native-node.mjs':HERE/'data/run-native-node.mjs','report-data-closure.json':HERE/'report-data-closure.json'}",'one physical read-only datum and exact union/graph/origin data')
edit("('source-contexts.mjs',HERE/'source-contexts.mjs')","('source-contexts.mjs',CONTEXT/'source-contexts.mjs')",'unchanged context helper from authenticated parent')
edit("'parentProposalIndexSha256':BASE_SHA,'sourceReviewSha256'", "'parentProposalIndexSha256':BASE_SHA,'contextAmendmentIndexSha256':CONTEXT_SHA,'reportDataClosureSha256':h(checked(HERE/'report-data-closure.json')),'sourceReviewSha256'",'explicit context/data contract provenance in config')
edit("for root,index,digest in[(BASE,base,BASE_SHA),(HERE,own,args.index_sha256)]:","for root,index,digest in[(BASE,base,BASE_SHA),(CONTEXT,context_parent,CONTEXT_SHA),(HERE,own,args.index_sha256)]:",'full source union retains all original roots')
edit("for r in load(BASE/'source-inputs.preparation.json')['files']:add(r['path'],r['sha256'],r['bytes'])", "for r in load(BASE/'source-inputs.preparation.json')['files']:add(r['path'],r['sha256'],r['bytes'])\n    for r in load(HERE/'source-inputs.json')['files']:add(r['path'],r['sha256'],r['bytes'])",'new finite original data rows in generated input freeze')
edit("'sourceAmendmentRoot':str(HERE),'inputs'", "'sourceAmendmentRoot':str(HERE),'contextAmendmentRoot':str(CONTEXT),'inputs'",'original contexts never rebased')
edit("checked(HERE/'native-preflight.template.after.mjs').decode()", "checked(CONTEXT/'native-preflight.template.after.mjs').decode()",'compile unchanged reviewed parent bridge at new publication')
edit("'sourceAmendmentContext':str(HERE),'admissionSourceRoot'", "'sourceAmendmentContext':str(HERE),'contextAmendmentRoot':str(CONTEXT),'reportDataClosureSha256':h(checked(HERE/'report-data-closure.json')),'admissionSourceRoot'",'source receipt context/data identity')
reverse=text
for e in reversed(edits):assert reverse.count(e['after'])==1;reverse=reverse.replace(e['after'],e['before'])
assert reverse==original
out('publish.py',text.encode())
obj('derivations.json',dict(schemaVersion=1,parentContextIndexSha256=CPIN,parentBaseIndexSha256=BPIN,publisherBeforeSha256=h(original.encode()),publisherAfterSha256=h(text.encode()),publisherEdits=edits,publisherReverseExact=True,runGateBeforeSha256=h(run.encode()),runGateAfterSha256=h(run2.encode()),runGateSingleNamespaceEdit=True,newSnapshotFiles=[newrow],guestRunnerOracleCaseNativeBytesChanged=False,ownerActionsInvoked=False))
obj('source-inputs.json',dict(schemaVersion=1,state='ORIGINAL_CONTEXT_SOURCE_PREPARATION_ROWS_NOT_REBASED',files=[consumed[k] for k in sorted(consumed)],parentRuntimePassesReused=False,parentNestedPreparationRowsFollowed=False))
print(json.dumps(dict(sourceOnly=True,publisherEdits=len(edits),requiredDataRows=len(matrix),newSnapshotFiles=1,originalInputs=len(consumed),ownerActionsInvoked=False)))
