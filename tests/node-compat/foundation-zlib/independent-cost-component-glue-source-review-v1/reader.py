#!/usr/bin/env python3
"""Hash/reconstruct/inspect pinned source as data. No owner or parser imports."""
import difflib,hashlib,json,re,stat
from pathlib import Path
P=Path(__file__).resolve().parent
Z=P.parent
C=Z/'cost-component-glue-amendment-v1'
W=Z/'cost-component-wit-amendment-v1'
D=Z/'cost-component-candidate-v1'
T=Z/'cost-tooling-candidate-v3'
seen={}
def need(v,m):
 if not v:raise AssertionError(m)
def row(p,e=None):
 p=Path(p);s=p.lstat();need(stat.S_ISREG(s.st_mode),'regular final file '+str(p));h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 r=dict(path=str(p),sha256=h.hexdigest(),bytes=s.st_size)
 if e:need(all(r[k]==e[k] for k in ('bytes','sha256')),'exact tuple '+str(p))
 seen[str(p)]=r;return r
def data(p):return json.loads(Path(p).read_text())
def indexed(p,pin):
 need(row(p)['sha256']==pin,'pinned index '+str(p));d=data(p);names=set()
 for x in d['files']:
  n=x['path'];need(not Path(n).is_absolute() and all(v not in ('','.','..') for v in n.split('/')),'safe source member');need(n not in names,'unique source member');names.add(n);row(Path(p).parent/n,x)
 return d
def write(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n')
def main():
 own=indexed(C/'index.json','cf3110b3af503fecd2408781a4dcb53b21670b74cd94e3266c4f0b86f795d794')
 wit=indexed(W/'index.json','e7252156f464f3a73621c002d01b95fa309ebc8208934539687d54d885257caa')
 donor=indexed(D/'index.json','a2fa62b3ab63a6aca044aec9a83c1ff5a09edaa208eb615226a13845bf1522f9')
 tooling=indexed(T/'index.json','ff208e72d0b87933aa75cdeb7c1ae16f29aa6ae94c357318a9d6676af04b36b8')
 refs=data(C/'input-freeze.json')['files'];need(len(own['files'])==20 and len(refs)==91,'exact20/91')
 for x in refs:row(x['path'],x)
 fail=Z/'independent-cost-component-native-on-v2-failure-review-v1';indexed(fail/'index.json','45ded56295c41324f2bdaa8d63b4a8d46f8d2a6231807f53ce356e7a61f49cbe')
 oldfail=Z/'independent-cost-component-native-on-v1-failure-review-v1';need(row(oldfail/'index.json')['sha256']=='0075de18a03de7156a34277c7a86ea5519d148820f41ee25a1d108f700c610a7','original failure immutable')
 der=data(C/'derivations.json');der_names=[]
 for x in der['files']:
  old=''.join(difflib.restore(x['ndiff'],1)).encode();new=''.join(difflib.restore(x['ndiff'],2)).encode();need(old==(W/x['path']).read_bytes() and new==(C/x['path']).read_bytes(),'exact reversible '+x['path']);need(hashlib.sha256(old).hexdigest()==x['beforeSha256'] and hashlib.sha256(new).hexdigest()==x['afterSha256'],'derivation hashes');der_names.append(x['path'])
 need(set(der_names)=={'guard.mjs','build-worker.mjs','abi.mjs'},'only three semantic source afterimages')
 for n in ['build.mjs','authority.mjs','collector.mjs','proofs.mjs','durable.mjs','durable-host.mjs','public-abi.wit']:
  need((C/n).read_bytes()==(W/n).read_bytes(),'unchanged inherited mechanism '+n)
 need(row(C/'public-abi.wit')['sha256']=='84a5fb9b33dc1e9e7f77d490c3799a6a933d93cde2c0d4d63a6c438d40dd7c89','corrected WIT retained')

 guard=(C/'guard.mjs').read_text();worker=(C/'build-worker.mjs').read_text();build=(C/'build.mjs').read_text();abi=(C/'abi.mjs').read_text()
 need("value.componentWitSourceIndexSha256===COMPONENT_WIT_SHA&&value.generatedJsGluePolicy==='JCO7_SCALAR_FUNCTIONS_PLUS_EXACT_EMPTY_UTIL_V1'" in guard,'explicit corrected parent and finite policy in Root model')
 need("const own=await sourceIndex(join(HERE,'index.json'),componentSourceIndexSha256),witParent=await sourceIndex(join(HERE,'../cost-component-wit-amendment-v1/index.json'),COMPONENT_WIT_SHA),donor=await sourceIndex(join(HERE,'../cost-component-candidate-v1/index.json'),COMPONENT_BASE_SHA)" in guard,'four distinct source identities')
 need(guard.index('const own=await sourceIndex(')<guard.index("await import(pathToFileURL(join(baseRoot,'context.mjs')))"),'source authentication before inherited data-validator import')
 need('await own.recheck();await witParent.recheck();await donor.recheck();await base.recheck();await peer.recheck();' in guard,'complete four-source/peer recheck')
 need('zlib-cost-component-v3-' in guard and 'zlib-cost-component-v2-' not in guard,'fresh v3 output roots')
 need("readFile(join(HERE,'public-abi.wit'),'utf8')" in worker and "from './abi.mjs'" in worker,'new physical WIT/ABI context')
 need(worker.index("output.write('transpile-metadata.json'")<worker.index("output.write('transpiled/'+name")<worker.index('publicJSExports(toolchain.parseAst(')<worker.index('const declarationFunctions=parsePublicDts(')<worker.index("output.write('generated-js-public-exports.json'"),'raw artifacts retained before role/declaration assertions')
 need('names:publicJS.names,abiFunctionNames:publicJS.abiFunctionNames,glueHelpers:publicJS.glueHelpers' in worker and 'staticGeneratedJSPublicExportRoles:publicJS' in worker,'names and ABI/helper roles separately retained')
 need('generatedDeclarationFunctions:declarationFunctions' in worker and 'generatedModuleImported:false' in worker,'seven declaration functions separate/no generated import')

 # Audit the exact acceptance predicates as pinned source. These are source
 # witnesses, not a claim to execute the AST checker or prove arbitrary JS.
 checks={
  'sameNameSyncFunctionArity':"node?.type==='FunctionDeclaration'&&node.id?.name===name&&!node.async&&!node.generator&&Array.isArray(node.params)&&node.params.length===ARITY[name]&&node.params.every(p=>p.type==='Identifier')",
  'uniqueTopLevelBindings':"typeof name==='string'&&!allBindings.has(name)",
  'noDefaultOrStar':"node.type!=='ExportDefaultDeclaration'&&node.type!=='ExportAllDeclaration'",
  'noReexportOrAttributes':"!node.source&&!node.attributes?.length&&!node.assertions?.length",
  'noSpecifierAlias':"item.exported.name===item.local.name&&NAMES.includes(item.exported.name)",
  'singleConstHelper':"d.type==='VariableDeclaration'&&d.kind==='const'&&d.declarations?.length===1",
  'exactEmptyObject':"!helper&&item.id?.type==='Identifier'&&item.id.name==='_util'&&item.init?.type==='ObjectExpression'&&item.init.properties?.length===0",
  'terminalHelper':"node===ast.body.at(-1)",
  'sevenFunctionsEightNames':"functions.size===7&&exported.length===8&&new Set(exported).size===8&&NAMES.every(name=>exported.includes(name))&&helper",
  'noOtherUtilReference':"n.type==='Identifier'&&n.name==='_util'",
  'assignmentAndUpdateTargetChecks':"n.type==='AssignmentExpression'||n.type==='UpdateExpression'",
  'declarationCount':"parts.length===7",
  'declarationScalarTypes':"types.length===ARITY[m[1]]&&types.every(t=>t===(['stage','validate'].includes(m[1])?'string':'number'))",
 }
 for name,token in checks.items():need(token in abi,'finite predicate present '+name)
 need("export {NAMES,parsePublicWit,checkTranspileMetadata,checkOwnedTerminal,wasmArgumentFeasibility} from '../cost-component-candidate-v1/abi.mjs'" in abi,'old seven-function WIT/metadata/terminal checks reused exactly')
 need("{identity:0,setup:1,observe:1,batch:2,checkpoint:0,stage:1,validate:1}" in abi,'expected seven JS arities')
 need("role:'jco-generated-non-callable-helper'" in abi and 'notWitExport:true' in abi,'helper not labelled WIT function')
 need(not re.search(r'\b(?:eval|Function)\s*\(',abi) and not re.search(r'\bimport\s*\(',abi),'new pure checker does not evaluate/import generated code')
 # Finite static dependency graph; all local import forms in these sealed
 # files are literal, so this is not a general-purpose JavaScript parser.
 queue=[C/n for n in ['build.mjs','build-worker.mjs','guard.mjs','abi.mjs','authority.mjs','collector.mjs','proofs.mjs','durable.mjs','durable-host.mjs']];modules=set();edges=[]
 while queue:
  p=queue.pop(0).resolve()
  if p in modules:continue
  modules.add(p)
  for s in re.findall(r"(?:from\s+|import\s*)['\"]([^'\"]+)['\"]",p.read_text()):
   if s.startswith('node:'):continue
   need(s.startswith('.'),'only explicit local or Node static imports');q=(p.parent/s).resolve();need(q.parent in [C,D] and q.is_file(),'finite physical donor context');row(q);edges.append(dict(source=str(p),specifier=s,target=str(q)));queue.append(q)
 need({p.name for p in modules if p.parent==D}=={'authority.mjs','abi.mjs','collector.mjs','proofs.mjs','durable.mjs','durable-host.mjs'},'actual complete six donor modules')
 # Inherit the validated exact critical-list construction by byte identity,
 # replace only its own physical HERE; do not invent an executed descriptor.
 prior=data(Z/'independent-cost-component-wit-source-review-v1/prospective-critical-rows.json');critical=[]
 for x in prior:
  p=Path(x['path']);q=C/p.name if p.parent==W else p
  critical.append(row(q, x if q==p else None))
 need(len(critical)==78 and modules.issubset({Path(x['path']) for x in critical}),'all15 own/donor runtime modules covered in78 prospective tuples')
 need(len([x for x in critical if '/zlib-cost-source-v3/control/' in x['path']])==9,'all nine publication control modules')
 future=data(C/'future-authority.json');need(all(future[k] is None for k in ['ownSourceIndex','rootComponentAction','newComponent','newABI','correctness','timing']) and future['actionsAllowed'] is False,'closed NULL future authority')
 stored=data(C/'evidence/stdout.log');syntax=data(C/'evidence/syntax-results.json');need(stored['checks']==39 and stored['hostRolldownParserLibraryInvoked'] is True and stored['generatedGlueImported'] is False and stored['codecLibraryJcoTranspileComponentOrGuestInvoked'] is False,'stored parser-only library invocation scope')
 need(syntax['checks']==11 and all(x.get('nodeCheckExitCode')==0 or x.get('ASTParsed') is True for x in syntax['files']),'stored11 syntax checks')
 # The author used a pinned parser and actual captured source; verify those
 # exact inputs and negative-case categories, without invoking that parser.
 test=(C/'test-pure.mjs').read_text()
 for token in ['oldPublicJSExports(ast)','roles=publicJSExports(ast)','parsePublicDts(dts)','parsePublicWit(wit)','checkTranspileMetadata(metadata)','export const _util = {x: 1}','export const _util = {get x()','export const _util = {...other}','export const _util = {__proto__: null}','Object.create(null)','export let _util','_util.x = 1','consume(_util)','export default','export * from','export const then','batch as other','async function identity','function* identity','function setup(arg0,arg1)','setup = other','ALLOW_EXTRA_EXPORTS']:
  need(token in test,'meaningful stored source-data negative category '+token)
 outputs=['/private/tmp/starling-node-compat/zlib-cost-component-v3-'+a for a in ['native-on','fflate-on','fflate-off']];need(all(not Path(x).exists() for x in outputs),'fresh v3 roots absent at source review')
 result=dict(schemaVersion=1,state='INDEPENDENT_ZLIB_COST_COMPONENT_SOURCE_REVIEW_PASSED_V1',componentSourceIndexSha256=row(C/'index.json')['sha256'],componentWitSourceIndexSha256=row(W/'index.json')['sha256'],componentBaseSourceIndexSha256=row(D/'index.json')['sha256'],generatedJsGluePolicy='JCO7_SCALAR_FUNCTIONS_PLUS_EXACT_EMPTY_UTIL_V1',sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,sourceFilesRehashed=20,preparationRowsRehashed=91,correctedParentFilesRehashed=20,donorFilesRehashed=25,toolingSourceFilesRehashed=286,exactReversibleAfterimages=der_names,publicWitFunctionCount=7,jcoFunctionMetadataCount=7,declarationFunctionCount=7,allowedGeneratedJsNames=8,allowedAdditionalHelper='exact terminal const _util = empty ordinary-object literal; no other identifier references',ownDonorRuntimeModules=len(modules),prospectiveCriticalTuples=78,publicationControlModules=9,oldFailurePeer=row(fail/'index.json'),storedAuthorSourceParserChecks=39,storedAuthorSyntaxChecks=11,authorHostRolldownParserLibraryInvoked=True,reviewerInvokedParserTestsHelpersOrOwnerActions=False,finitePinnedSourceCheckerNotGeneralJavaScriptSemanticProof=True,futureOutputsAbsentAtReview=outputs,newComponentOrAbiApproved=False,ordinaryGuestExportsInvoked=False,operationalAdmission=False,timingAllowed=False,uniqueInputsRehashed=len(seen))
 write('source-predicate-witnesses.json',checks);write('source-import-edges.json',edges);write('prospective-critical-rows.json',critical);write('rehashed-inputs.json',[seen[k] for k in sorted(seen)]);write('results.json',result);print(json.dumps({'state':result['state'],'uniqueInputs':len(seen),'modules':len(modules),'critical':78}))
if __name__=='__main__':main()
