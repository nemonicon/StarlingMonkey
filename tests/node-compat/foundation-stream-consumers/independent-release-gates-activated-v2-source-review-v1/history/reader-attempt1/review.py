#!/usr/bin/env python3
"""Independent read-only/data reader. No owner module imports or actions."""
from pathlib import Path
import hashlib,json,os,stat,re
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
D=ROOT/'release-gates-activated-v2';B=ROOT/'release-gates-candidate-v1';A=ROOT/'release-gates-context-amendment-v1'
SHA='562e4236c8f99a34323c57c26f92749dba4aaf3e5dc1a509d33ababd97d79250'
BASE='a74dc603f7e42384892c9f4b69a2ba131a87a80daa38da19e91bbc2c099e5372'
AMEND='9080e48fbccaf74835bfb8c8ef54c91b8df54ff5eb6e4c2cdc1c83443ad79b70'
checks=[];hashed={};cache={}
def need(ok,label):
 if not ok:raise AssertionError(label)
 checks.append(label)
def read(p,expected=None,n=None,collect=True):
 p=Path(p);s=p.lstat();assert stat.S_ISREG(s.st_mode) and not p.is_symlink(),str(p)
 key=str(p);ident=(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
 if key in cache and cache[key][0]==ident and not collect:
  digest,size=cache[key][1:]
 else:
  h=hashlib.sha256();pieces=[];size=0
  with p.open('rb')as f:
   for raw in iter(lambda:f.read(1024*1024),b''):
    h.update(raw);size+=len(raw)
    if collect:pieces.append(raw)
  digest=h.hexdigest();a=p.lstat();assert ident==(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns),str(p)
  cache[key]=(ident,digest,size)
 if expected is not None:assert digest==expected,(str(p),digest,expected)
 if n is not None:assert size==n,(str(p),size,n)
 hashed[key]={'path':key,'sha256':digest,'bytes':size,'device':s.st_dev,'inode':s.st_ino}
 return b''.join(pieces)if collect else None
def js(p,sha=None):return json.loads(read(p,sha))
def h(raw):return hashlib.sha256(raw).hexdigest()
def safe(root,name):
 assert type(name)is str and name and not Path(name).is_absolute() and '\\'not in name and '\0'not in name and all(v not in('','.','..')for v in name.split('/'))
 p=root
 for part in name.split('/'):p/=part;assert not p.is_symlink(),str(p)
 return p
def indexed(p,sha):
 ix=js(p,sha);seen=set()
 for row in ix['files']:
  assert row['path']not in seen;seen.add(row['path']);read(safe(p.parent,row['path']),row['sha256'],row['bytes'],False)
 return ix
def descriptor(row):read(row['path'],row['sha256'],row['bytes'],False)
def paths(root):
 found=[]
 for at,dirs,files in os.walk(root,followlinks=False):
  for name in dirs:assert not(Path(at)/name).is_symlink()
  for name in files:
   p=Path(at)/name;assert p.is_file()and not p.is_symlink();found.append(str(p.relative_to(root)))
 return sorted(found)
def main():
 root_result=js(ROOT/'release-gates-context-v1-root-results.json','ba79b44f6af91ff5cf741240248ab8d452e41bbf2094a5fb4939e65b57836eb9')
 for k in['authority','generatedIndex','sourceReceipt','externalTerminal','externalStdout','externalStderr']:descriptor(root_result[k])
 ix=indexed(D/'index.json',SHA);base=indexed(B/'index.json',BASE);amend=indexed(A/'index.json',AMEND)
 need(len(ix['files'])==1727 and paths(D)==sorted([r['path']for r in ix['files']]+['index.json']),'exact1727 indexed/1728 actual ordinary files; no symlinks')
 need(root_result['externalPublisherExitCode']==0 and root_result['admissionPreflightCompilerNativeGuestHostOrTimingInvoked']is False,'Root publisher raw0 source-only scope')
 terminal=js(root_result['externalTerminal']['path']);need(terminal['rawExitCode']==0 and terminal['sourceCopyOnly']is True and terminal['genuineAdmissionPreflightNativeCompilerGuestHostOrTimingInvoked']is False,'external actual terminal raw0/source-only')
 need(terminal['argv'][1]==str(A/'publish.py') and terminal['argv'][-1]==str(D) and terminal['argv'][3]==AMEND,'exact executed publisher source/index/output argv')
 for k in['stdout','stderr']:descriptor(terminal[k])
 out=json.loads(read(terminal['stdout']['path']));need(out['indexSha256']==SHA and out['files']==1727 and out['inputs']==12569 and out['guestExecuted']is False,'actual stdout matches generated family')
 need(terminal['stderr']['bytes']==0,'external stderr empty')
 config_raw=read(D/'activation.json');config=json.loads(config_raw);seal_raw=read(D/'input-freeze.json');seal=json.loads(seal_raw);receipt=js(D/'source-receipt.json')
 need(receipt['configSha256']==h(config_raw)and receipt['inputFreezeSha256']==h(seal_raw)and receipt['consumedInputs']==12569,'receipt exact config/manifest digests/count')
 need(config['operationalAdmission']is False and config['runtimeActionAuthority']is None and config['guestExecuted']is False and config['nativeExecuted']is False,'generated source grants no runtime or operational action')
 need(config['proposalIndexSha256']==AMEND and config['parentProposalIndexSha256']==BASE and config['admissionSourceRoot']==config['nativeConfiguredSourceRoot']=='/private/tmp/starling-node-compat/consumers-source-v2','explicit configured admission checkout')
 need(config['runtimeSourceRoot']==config['nativeFrozenSourceRoot']=='/tmp/starling-node-compat/production-consumers-v1/native-freeze/source'and config['admissionSourceRoot']!=config['runtimeSourceRoot'],'frozen runtime root stays distinct')
 need(config['componentToolRoot']==str(D/'snapshot'),'packaging snapshot is neither configured nor frozen native root')
 review=js(D/'source-root-review.json',config['sourceReviewSha256']);need(review['state']=='ROOT_REVIEWED_CONSUMERS355_RELEASE_CONTEXT_AMENDMENT_V1'and review['proposalIndexSha256']==AMEND and review['parentProposalIndexSha256']==BASE,'exact Root context-source authority')
 need(review['sourceActivationApproved']is True and review['runtimeActionsApproved']is False and review['operationalAdmission']is False and review['sourcePromotionAllowed']is False,'source publication authority only')
 proof=review['independentSourceReview'];peer=indexed(Path(proof['index']['path']),proof['index']['sha256']);descriptor(proof['result']);need(any(str(Path(proof['index']['path']).parent/r['path'])==proof['result']['path']and r['sha256']==proof['result']['sha256']for r in peer['files']),'Root source-peer result indexed')
 for key,target in[('reviewedPins','reviewed-pins.json'),('nativeRootReview','root-review.json')]:descriptor(review[key]);need(read(D/target)==read(review[key]['path']),'Root authority byte-exact '+target)
 descriptor(review['priorFailure']);need(review['priorFailure']['sha256']=='bc1cd16985850ef243dc14295d75af655bed9eb6fe06e66bfb414d0565efbcf7','old actual preflight failure retained; not relabelled')
 # Reconstruct exactly the finite source publication and every copy source.
 payload=js(B/'payload-files.json')['files'];overrides={'native-preflight.template.mjs':A/'native-preflight.template.after.mjs','run-gates.mjs':A/'run-gates.after.mjs','selected-closure.json':A/'selected-closure.after.json'}
 for name in payload:
  origin=overrides.get(name,B/name);need(read(D/name)==read(origin),'exact published payload '+name);need((D/name).stat().st_ino!=origin.stat().st_ino,'independent copied inode '+name)
 need(read(D/'source-contexts.mjs')==read(A/'source-contexts.mjs'),'new helper exact amendment bytes')
 expected=set(payload)|{'source-contexts.mjs','reviewed-pins.json','root-review.json','source-root-review.json','activation.json','input-freeze.json','native-preflight.mjs','source-receipt.json','index.json'}
 need(set(paths(D))==expected,'actual family has only declared payload/bindings/boundaries')
 deriv=js(A/'derivations.json');before=read(B/'native-preflight.template.mjs').decode();after=before
 for edit in deriv['edits']:need(after.count(edit['before'])==1,'unique forward context edit '+edit['name']);after=after.replace(edit['before'],edit['after'],1)
 need(h(before.encode())==deriv['templateBeforeSha256']and h(after.encode())==deriv['templateAfterSha256']and after.encode()==read(D/'native-preflight.template.mjs'),'five exact template forward edits')
 reverse=after
 for edit in reversed(deriv['edits']):need(reverse.count(edit['after'])==1,'unique reverse context edit '+edit['name']);reverse=reverse.replace(edit['after'],edit['before'],1)
 need(reverse==before,'five exact reverse edits; no fixture/oracle/native code edit')
 runner_before=read(B/'run-gates.mjs');runner_after=read(D/'run-gates.mjs');need(runner_before.replace(b'production-consumers355-release-gates-v1/',b'production-consumers355-release-gates-v2/')==runner_after,'only fresh v2 runner output namespace edit')
 compiled=after.replace('@CONFIG_SHA@',h(config_raw)).replace('@INPUTS_SHA@',h(seal_raw)).encode();need(compiled==read(D/'native-preflight.mjs'),'compiled actual bridge equals exact template plus two actual primitive digests')
 need('@CONFIG_SHA@'not in compiled.decode()and'@INPUTS_SHA@'not in compiled.decode(),'no unresolved compiled template placeholders')
 # Reconstruct the union in ORIGINAL preparation contexts, not copied hints.
 inputs={}
 def add(path,sha,size,local=False):
  key=('L:'if local else'E:')+str(path);r={'path':str(path),'sha256':sha,'bytes':size,'local':local};assert key not in inputs or inputs[key]==r;inputs[key]=r
 prep=js(B/'source-inputs.preparation.json')
 for r in prep['files']:add(r['path'],r['sha256'],r['bytes'])
 for root,index,digest in[(B,base,BASE),(A,amend,AMEND)]:
  for r in index['files']:add(str(root/r['path']),r['sha256'],r['bytes'])
  add(str(root/'index.json'),digest,(root/'index.json').stat().st_size)
 for row in[root_result['authority'],review['reviewedPins'],review['nativeRootReview']]:add(row['path'],row['sha256'],row['bytes'])
 for name in sorted(expected-{'activation.json','input-freeze.json','native-preflight.mjs','source-receipt.json','index.json'}):
  p=D/name;raw=read(p);add(name,h(raw),len(raw),True)
 need(list(inputs.values())==seal['inputs']and len(inputs)==12569,'full12569 union exactly reconstructed; originalprep roles retained')
 seen=set()
 for r in seal['inputs']:
  p=safe(D,r['path'])if r['local']else Path(r['path']);need(str(p)not in seen,'unique actual union lexical source '+str(p));seen.add(str(p));read(p,r['sha256'],r['bytes'],False)
 need(seal['oldNestedPreparationRowsFollowed']is False and seal['originalPreparationRoot']==str(B)and seal['sourceAmendmentRoot']==str(A),'no nested historical manifest reinterpretation or original path redirect')
 need(paths(D/'snapshot')==seal['snapshotMembers']and len(seal['snapshotMembers'])==1677,'complete1677 snapshot membership')
 # Exact tool/link inventory data; no require.resolve or owner code execution.
 tools=js(D/'tool-context.json',seal['toolContextSha256']);need(len(tools['toolTrees'])==2 and len(tools['toolLinks'])==22 and len(tools['inputs'])==4892,'two tool trees/22links/4890 files plusNode+WT')
 for r in tools['inputs']:descriptor(r)
 for t in tools['toolTrees']:
  p=Path(t['path']);need(str(p.resolve())==t['realPath'],'tool real root '+str(p));rows=[]
  def walk(at):
   for q in sorted(at.iterdir()):
    s=q.lstat();kind='symlink'if q.is_symlink()else'directory'if q.is_dir()else'file'if q.is_file()else None;assert kind;rows.append({'path':str(q.relative_to(p)),'kind':kind})
    if kind=='directory':walk(q)
  walk(p);need(sorted(rows,key=lambda r:r['path'])==t['entries'],'exact full tool-tree kinds '+str(p))
 for row in tools['toolLinks']:
  p=Path(row['path']);need(p.is_symlink()and os.readlink(p)==row['linkText']and str(p.resolve())==row['resolvedTarget'],'tool exact link provenance '+str(p))
  if row['targetKind']=='file':read(row['resolvedTarget'],row['targetSha256'],row['targetBytes'],False)
 packages=js(D/'package-endpoints.json',seal['packageEndpointsSha256']);need([len(packages[k])for k in['packages','endpoints','packageData']]==[4,5,27],'four package manifests/five endpoints/27 data files')
 for rows in packages.values():
  for row in rows:descriptor(row)
 graph=js(D/'selected-closure.json',seal['selectedClosureSha256']);need(len(graph['localModulesAndData'])==103 and len(graph['localEdges'])==196,'actual103 local modules/data and196 explicit edges')
 for row in graph['localModulesAndData']:read(safe(D,row['path']),row['sha256'],row['bytes'],False)
 for row in graph['localEdges']:need(str((D/row['importer']).parent.joinpath(row['request']).resolve())==str((D/row['target']).resolve()),'finite physical source edge '+row['importer']+' '+row['request'])
 need(graph['compiledBoundaryModules']==['native-preflight.mjs']and graph['ownerModulesImported']is False,'compiled bridge separate; closure audit source-only')
 # All current actual355 native tuples stay unprojected; original caches unused.
 pins=js(D/'reviewed-pins.json',config['pinsSha256']);nr=js(D/'root-review.json',config['rootReviewSha256']);lineage=js(D/'lineage.json',config['lineageSha256'])
 need(pins['sourceFiles']==355 and pins['externalSources']==3 and pins['operationalAdmission']is False and nr['reviewedPinsSha256']==config['pinsSha256'],'actual355 native authority preserved')
 native=[]
 for label,pin in pins['variants'].items():
  need(label in['normal-off','normal-runtime','gc-off','disabled-off']and pin['reviewRequired']is False and pin['runtimeAcceptanceClaim']is False,'actual validation-only native tuple '+label)
  for k in['engineSha256','engineBytes','receiptSha256','freezeReceiptSha256']:need(pin[k]==nr['variants'][label][k],'Root native crossbinding '+label+'/'+k)
  read(pin['enginePath'],pin['engineSha256'],pin['engineBytes'],False);metadata_path=pin['enginePath']+'.build.json';metadata=js(Path(metadata_path),pin['receiptSha256']);freeze=js(Path(pin['freezeReceiptPath']),pin['freezeReceiptSha256'])
  need(len(metadata['sourceManifest'])==355 and metadata['sourceManifest']==lineage['native355']or metadata['sourceManifest']==[dict(row)for row in lineage['native355']],'native355 metadata vs exact lineage '+label)
  need(metadata.get('diagnosticOnly',False)is False and metadata.get('syntheticMetadataOnly',False)is False,'no diagnostic/synthetic metadata '+label)
  need(metadata['zlibPolicy']['runtimeBackendProof']=={'verified':False,'version':None,'vernum':None},'runtime backend metadata not fabricated '+label)
  for row in metadata['sourceManifest']:
   read(Path(config['admissionSourceRoot'])/row['path'],row['sha256'],None,False);read(Path(config['runtimeSourceRoot'])/row['path'],row['sha256'],None,False)
  for row in freeze['copies']:descriptor(row)
  native.append({'label':label,'engineSha256':pin['engineSha256'],'frozenCopies':len(freeze['copies']),'sources':355})
 toolpins=js(Path(config['bootstrapRoot'])/'artifact-tools/tool-pins.json','7ee0303e21e32da5b85bb7a6f2476a20f74a91c3cfef988274acc26f8fc5d9fe');need(len(toolpins['toolDependencies'])==767,'actual configured767 tool dependencies')
 for row in toolpins['toolDependencies']:read(Path(config['admissionSourceRoot'])/row['path'],row['sha256'],row['bytes'],False)
 # Static caller/callee reasoning: inspect real source without importing it.
 bridge=compiled.decode();admit=read(Path(config['bootstrapRoot'])/'artifact-tools/metadata-admission.mjs').decode();helper=read(D/'source-contexts.mjs').decode()
 need('admit(native.metadata,variant,roots.admissionSourceRoot)'in bridge and 'admit(frame.metadata,variant,roots.admissionSourceRoot)'in bridge,'initial and recheck genuine admission receive configured root')
 need('for(const row of tools.toolDependencies)await regularBelow(sourceRoot' in admit and 'sourceRoot,'in admit,'actual named admit requires full configured tool/native root')
 need('await regular(await safeLocal(roots.admissionSourceRoot,row.path),row.sha256)'in helper and 'await regular(await safeLocal(roots.runtimeSourceRoot,row.path),row.sha256)'in helper,'both native355 trees authenticated around real admit')
 need("assert.equal(runtimeSourceRoot,native.sourceRoot);assert.equal(runtimeSourceRoot,pin.sourceRoot)"in helper,'runtime sourceRoot remains frozen pin identity')
 need("assert(!Object.hasOwn(core,'sourceRoot')"in helper and "assert.equal(core.schema,1)"in helper,'actual no-path schema1 core hash contract, no fake root')
 need("for(const row of nativeIndex.files)await regular"in bridge and bridge.index('for(const row of nativeIndex.files)await regular')<bridge.index('const {consumersBootstrapPreflight}=await import'),'native index/source-tool verification before dynamic bootstrap')
 need('const seal=JSON.parse(await regular' in bridge and 'INPUTS_SHA' in bridge and '.replaceAll' in bridge,'immutable manifest/config compile digests checked and compiled source reconstructed')
 entry=read(D/'entry.mjs').decode();selected=read(D/'run-selected.mjs').decode();runner=read(D/'run-gates.mjs').decode();contracts=read(D/'contracts.mjs').decode()
 need(entry.index('for(const row of index.files)')<entry.index("await import('./run-gates.mjs')"),'supported entry hashes whole family before owned imports')
 need('assertRuntimeAuthority(authority' in selected and selected.index('assertRuntimeAuthority(authority')<selected.index('await import(pathToFileURL'),'selected mode uses fresh external authority before runner import')
 need('NODE_COMPAT_RELEASE_RESUME' in selected and 'noPriorPassReuse' in contracts,'no resume/oldpass reuse authority')
 # Root-defined stale planning DATA exception, narrowly inspect actual readers.
 erratum=js(ROOT/'release-gates-context-v1-planning-template-erratum.json','a6302b97a40e5b34e597cbb0913107dc5199f1f42d8efa99b72b976d47b8be3f');descriptor(erratum['affectedTemplate']);descriptor(erratum['actualExecutablePublisher'])
 planning=js(D/'future-actions.template.json');need(planning['sourcePublication']['requiredOutputBasename']=='release-gates-activated-v1'and planning['sourcePublication']['approved']is None,'stale unapproved planning label preserved exactly')
 for name,text in[('entry',entry),('publisher',read(A/'publish.py').decode()),('run-gates',runner),('run-selected',selected)]:need('requiredOutputBasename'not in text,'bounded executable reader does not interpret stale planning field: '+name)
 need("output.name=='release-gates-activated-v2'"in read(A/'publish.py').decode()and'production-consumers355-release-gates-v2/'in runner,'actual publisher and runner enforce v2 output namespace')
 need(config['runtimeActionAuthority']is None and receipt['priorPassReused']is False and receipt['guestExecuted']is False,'actual source publication is not release/preflight/runtime acceptance')
 # Final reread all unique bytes, preserving lexical aliases in the ledger.
 for row in list(hashed.values()):read(row['path'],row['sha256'],row['bytes'],False)
 return{'schemaVersion':1,'state':'INDEPENDENT_CONSUMERS355_RELEASE_GATES_ACTIVATED_V2_SOURCE_REVIEW_PASSED','verifiedPassed':True,'generatedIndexSha256':SHA,'proposalIndexSha256':AMEND,'parentProposalIndexSha256':BASE,'checks':len(checks),'indexedFiles':1727,'actualFiles':1728,'consumedUnionRows':12569,'uniqueLexicalPathsRehashed':len(hashed),'nativeVariants':native,'toolTrees':2,'toolLinks':22,'configuredToolDependencies':767,'snapshotFiles':1677,'localClosureModulesAndData':103,'localEdges':196,'externalSourcePublisherExitCode':0,'originalContextRolesPreserved':True,'configuredAdmissionAndFrozenRuntimeRootsSeparate':True,'caseOracleGuestAndNativeBytesChangedByContextFix':False,'fiveTemplateChangesExactForwardAndReverse':True,'compiledBridgeExact':True,'sourceOnly':True,'ownerHelpersOrPreflightsInvoked':False,'nodeOrGuestOrCompilerOrHostOrTimingInvoked':False,'genuineAdmissionOrRuntimePassClaim':False,'operationalAdmission':False,'runtimeAcceptanceClaim':False,'planningErratumScope':'The old requiredOutputBasename remains hashed unapproved DATA. It is not interpreted by entry/publisher/run-gates/run-selected. No claim that arbitrary future tools never consume it.'}
if __name__=='__main__':
 result=main();(HERE/'results.json').write_text(json.dumps(result,indent=2)+'\n');(HERE/'checks.json').write_text(json.dumps({'checks':checks},indent=2)+'\n');(HERE/'rehashed-files.json').write_text(json.dumps({'files':list(hashed.values())},indent=2)+'\n');print(json.dumps({k:result[k]for k in['state','checks','uniqueLexicalPathsRehashed','indexedFiles','consumedUnionRows']}))
