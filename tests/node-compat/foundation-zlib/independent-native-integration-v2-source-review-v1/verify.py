"""Bounded source HOLD reader; standard-library hash/AST/data only."""
from pathlib import Path
import ast,difflib,hashlib,json,re,shlex,stat
HERE=Path(__file__).resolve().parent;FAMILY=HERE.parent;REPO=HERE.parents[3]
OWNER=FAMILY/'native-integration-candidate-v2';AMEND=FAMILY/'forced-include-amendment-v1'
OWNER_SHA='c65ed2c400b49e63d716ba92b05d0b5f0f56680f6a89d94a9b2c813faec0aba1'
AMEND_SHA='1d0c8626665c06247f4240be359704a2c10851489cb77e203f14ae511343c58c'
seen={}
def sha(b):return hashlib.sha256(b).hexdigest()
def read(path,h=None,size=None):
 p=Path(path);a=p.lstat();assert stat.S_ISREG(a.st_mode)and not p.is_symlink(),p
 value=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):value.update(b)
 z=p.lstat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns),p
 digest=value.hexdigest();assert h is None or digest==h,p;assert size is None or z.st_size==size,p
 name=str(p.resolve(strict=True));row={'path':name,'sha256':digest,'bytes':z.st_size};assert name not in seen or seen[name]==row,p;seen[name]=row
 return p.read_bytes()if z.st_size<8*1024*1024 else None
def doc(p,h=None):return json.loads(read(p,h))
def indexed(p,h,count=None):
 j=doc(p/'index.json',h)
 if count is not None:assert len(j['files'])==count
 names=set()
 for row in j['files']:
  n=row['path'];assert n not in names and not Path(n).is_absolute()and all(v not in('','.','..')for v in n.split('/'));names.add(n);read(p/n,row['sha256'],row['bytes'])
 return j
assert not(HERE/'results.json').exists()
indexed(OWNER,OWNER_SHA,77);indexed(AMEND,AMEND_SHA,11)
receipt=doc(OWNER/'source-receipt.json');assert receipt['recipeSha256']=='618b1ce7c882dd5dd8daaf978143c3f377ba3451fc933be35a365d2b0d8a99b0'
manifest=doc(OWNER/'input-freeze.json');assert len(manifest['inputs'])==2048 and manifest['relocatedActionsMustNotReinterpretThesePaths']is True
for row in manifest['inputs']:read(OWNER/row['path'],row['sha256'],row['bytes'])
for n,h in receipt['parentIndices'].items():indexed(OWNER/n,h)
old=FAMILY/'native-integration-candidate-v1';indexed(old,'3ff3a59d4fc1fafa32b2ba1e6ec5a1b8d7787f4e7eca1ee6855d7b38cc7c45db',72)
indexed(FAMILY/'independent-native-integration-source-review-v1','dafaff07578be6f62883ddf0815c023f4ba0e12b0c5b1e6ab5899d4f0edb474c')
proof=doc(AMEND/'derivation-proof.json');assert len(proof['files'])==6 and proof['parentIndexSha256']=='3ff3a59d4fc1fafa32b2ba1e6ec5a1b8d7787f4e7eca1ee6855d7b38cc7c45db'
for row in proof['files']:
 b=read(AMEND/'afterimages'/row['path'],row['afterSha256'],row['afterBytes']);assert b==read(OWNER/row['path'])
 if row['origin']is not None:read(REPO/row['origin'],row['beforeSha256'])
assert all(x['exitCode']==0 for x in proof['fullPatchForwardAndReverseChecks'])
derivation_count=0
for name in ['source-transformations.json','tool-transformations.json','model-transformations.json']:
 j=doc(OWNER/name)
 for row in j.get('records',j.get('files',[])):
  before=read(REPO/row['origin'],row['beforeSha256']).decode();after=read(OWNER/row['path'],row['afterSha256']).decode();value=before
  for e in row['edits']:
   assert value.count(e['old'])==e['count'];value=value.replace(e['old'],e['new'])
  assert value==after,row['path']
  for e in reversed(row['edits']):
   for at in reversed(e['afterOffsets']):assert value[at:at+len(e['new'])]==e['new'];value=value[:at]+e['old']+value[at+len(e['new']):]
  assert value==before;derivation_count+=1
policy=doc(OWNER/'policy.json',receipt['policySha256']);read(OWNER/'layer-policy.py',receipt['helperSha256']);read(OWNER/'source/tests/node-compat/build-engine.sh',receipt['recipeSha256'])
before=doc(FAMILY.parent/'foundation-classic-streams/trace-integration-candidate-v1/policy.json')['expectedNativeSourceManifest'];before={x['path']:x['sha256']for x in before}
native={x['path']:x['sha256']for x in policy['expectedNativeSourceManifest']};assert len(native)==350 and len(before)==342
adds=set(native)-set(before);changed={n for n in before if native[n]!=before[n]};assert len(adds)==8 and changed=={'builtins/node-compat/register.cpp','cmake/builtins.cmake'}and len(before)-len(changed)==340
for n,h in native.items():
 candidates=[OWNER/'source'/n,FAMILY/'integration-candidate-v1/source'/n,Path('/tmp/starling-node-compat/classic-trace-source-v1')/n,REPO/n]
 exact=[p for p in candidates if p.is_file()and not p.is_symlink()and hashlib.sha256(p.read_bytes()).hexdigest()==h];assert exact,n;read(exact[0],h)
for p in (OWNER/'source/builtins/node-compat/zlib').iterdir():
 if p.is_file():assert read(p)==read(FAMILY/'integration-candidate-v1/source/builtins/node-compat/zlib'/p.name),p
assert len([n for n in native if n.endswith('.cpp')and n.startswith(('runtime/','builtins/'))])==62
assert len(policy['privateTargetCpp'])==6
data=doc(OWNER/'evidence/actual-command-python.json');js=doc(OWNER/'evidence/actual-command-node.json')
for row in data['actualInputs']:read(row['path'],row['sha256'],row['bytes'])
commands=data['actualCommandRecords'];assert len(commands)==64 and js['count']==74
selected=data['selectedCompileInput'];assert selected['version']=='sm-selected-moz-z-compile-input-v1';root=selected['selectedDistribution'];required=selected['requiredForcedInclude']
assert required==selected['headers'][3]and required['path']==root+'/include/js-confdefs.h'and required['sha256']=='841e57a382d7d8219431dc26e1d1307af1649228503d21bcf2eac826fc99acd6'and required['bytes']==2283
for row in [selected['archive'],*selected['headers']]:read(row['path'],row['sha256'],row['bytes'])
def compile_tokens(words):
 assert words.count('-include')==1 and words[words.index('-include')+1]==required['path']
 assert all(w=='-include'or not w.startswith(('-include','-imacros','-Wp,','-Xpreprocessor','-Xclang'))for w in words)
 assert all(not w.startswith(('-DZ_PREFIX','-UZ_PREFIX'))for w in words)
for row in commands:
 assert shlex.split(row['command'])==row['tokens']and sha(row['command'].encode())==row['commandSha256'];compile_tokens(row['tokens'])
counts={k:sum(r['kind']==k for r in commands)for k in {r['kind']for r in commands}}
assert sorted(counts.values())==[1,2,61]
# Pure expected-shape check on the actual authenticated descriptor and the
# statically determined return binding. No owner function or subprocess runs.
codec=read(OWNER/'codec-evidence.py').decode();tree=ast.parse(codec);after=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='after')
assignments=[n for n in after.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='selected'for t in n.targets)]
assert len(assignments)==2 and [ast.unparse(n.value.func)for n in assignments]==['selected_compile_input','symbols']
returned=next(n.value for n in after.body if isinstance(n,ast.Return));fields={k.value:v for k,v in zip(returned.keys,returned.values)}
assert isinstance(fields['selectedCompileInput'],ast.Name)and fields['selectedCompileInput'].id=='selected'
symbols=next(ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='SYMBOLS'for t in n.targets))
assert len(symbols)==7
symbol_map={name:'static-symbol-result:'+name for name in symbols}
shape=lambda v:set(v)=={'version','selectedDistribution','archive','headers','requiredForcedInclude'}and v.get('version')=='sm-selected-moz-z-compile-input-v1'
assert shape(selected)and not shape(symbol_map)
shape_result={'schemaVersion':1,'state':'PURE_EXPECTED_DESCRIPTOR_SHAPE_MISMATCH_CONFIRMED',
 'actualAuthenticatedDescriptorKeys':list(selected),'returnedBindingAfterFinalAssignment':'symbols(child.stdout)',
 'returnedSymbolMapKeys':symbols,'expectedDescriptorShapeAccepted':True,'currentReturnBindingDescriptorShapeAccepted':False,
 'ownerFunctionOrToolsExecuted':False,'scope':'Static AST name-binding plus pure shape predicates; synthetic symbol values are markers, not archive/guest observations.'}
(HERE/'descriptor-shape-inspection.json').write_text(json.dumps(shape_result,indent=2)+'\n')
recipe=read(OWNER/'source/tests/node-compat/build-engine.sh').decode();helper=read(OWNER/'layer-policy.py').decode();admission=read(OWNER/'source/tests/node-compat/zlib-admission.mjs').decode();artifact=read(OWNER/'artifact-tools/artifact_common.py').decode()
assert recipe.index("metadata['zlibSelectedCodecInput']=codec.selected_compile_input(spidermonkey_dir)")<recipe.index('metadata = layer.decorate(')<recipe.index("metadata['zlibPolicy']['codecWitness']=codec.after(")
assert "selection_contract(selected)"in codec and "metadata['zlibSelectedCodecInput']==witness['selectedCompileInput']"in artifact
assert 'assert.deepEqual(witness.selectedCompileInput,metadata.zlibSelectedCodecInput)'in admission
assert 'validateCompileForcedInclude(tokens,metadata.zlibSelectedCodecInput)'in admission
assert 'codec.no_second_codec(words,selected)'in helper and 'codec.selection_contract(selected)'in helper
for name in ['bootstrap-pins.json','runtime-pins.json']:
 pins=doc(OWNER/name);assert len(pins['variants'])==4 and all(v is None for v in pins['variants'].values())
assert "Zlib350 operational admission CLOSED"in admission and "if(!hinted(metadata))return null"in admission
finding={'id':'Z350-M2','severity':'must-fix-before-stage-or-build','issue':'codec.after overwrites the authenticated selected compile-input descriptor with the seven-symbol definitions map and returns that map as selectedCompileInput.',
 'locations':[{'path':'codec-evidence.py','line':152,'role':'selected descriptor assigned'},{'path':'codec-evidence.py','line':166,'role':'selected overwritten by symbols result'},{'path':'codec-evidence.py','line':169,'role':'wrong binding returned as selectedCompileInput'},{'path':'codec-evidence.py','line':191,'role':'frozen witness expects descriptor'},{'path':'artifact-tools/artifact_common.py','line':279,'role':'descriptor equality required'},{'path':'source/tests/node-compat/zlib-admission.mjs','line':205,'role':'descriptor equality required'}],
 'effect':'After successful native/link/symbol collection, build/freezer/JS admission would reject the malformed witness; source guard/data tests do not exercise this final witness shape.',
 'requiredCorrection':'New immutable successor must keep selected compile-input descriptor and selected symbol definitions in separate bindings; selectedCompileInput must equal metadata.zlibSelectedCodecInput and archiveSymbolEvidence.selectedDefinitions must remain the seven-symbol map. Add a pure positive expected-witness-shape regression with no real native/tool calls.'}
for row in list(seen.values()):read(row['path'],row['sha256'],row['bytes'])
report={'schemaVersion':1,'state':'INDEPENDENT_ZLIB350_V2_SOURCE_REVIEW_HOLD_DESCRIPTOR_SYMBOL_SHADOW',
 'ownerIndexSha256':OWNER_SHA,'ownerFilesRehashed':77,'preparationInputsRehashed':2048,'mandatoryAmendmentIndexSha256':AMEND_SHA,'mandatoryAmendmentFiles':11,'mandatoryAfterimages':6,
 'recipeSha256':receipt['recipeSha256'],'policySha256':receipt['policySha256'],'helperSha256':receipt['helperSha256'],'derivationRecordsForwardAndReverse':derivation_count,
 'nativeSources':350,'parentNativeSources':342,'nativeAdds':8,'nativeParentChanges':2,'unchangedParentPaths':340,'nativePayloadMatchesConditional56a6':True,
 'expectedCompileCPP':{'on':62,'off':61},'privateTargetCPP':{'on':6,'off':5},'actualCommandDataRecords':counts,
 'selectedRequiredIncludeAuthenticated':required,'originalZ350M1SingletonCompileIncludeCorrectionPresent':True,'preDecorateDescriptorAuthenticationOrderingCorrect':True,
 'mandatoryFindings':[finding],'allOtherMechanismsApproved':False,'reviewScope':'Bounded critical source/data review and full index/preparation-byte authentication. Not final approval of every unexecuted linkage/stage/runtime path.',
 'futurePinsAllFourNull':True,'operationalAdmissionOpen':False,'runtimeBackendProof':{'verified':False,'version':None,'vernum':None},
 'ownerImportsOrActionMainsOrStageOrBuildOrCompilerOrNativeVerifierOrGuestOrHostOrTimingExecuted':False,'old3ffAndDafaffAndC65And1d0cModified':False,'runtimeAcceptanceClaim':False,'performanceClaim':False,
 'relatedInspection':'No additional concrete blocker found in recipe/decorate ordering, selected-include grammar, native/private compile scope, separate link/no-second-codec policy, closed operational selector or null bootstrap. This does not assert empirical link shape or runtime readiness.',
 'verifiedFiles':sorted(seen.values(),key=lambda r:r['path'])}
with(HERE/'results.json').open('x')as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps({'state':report['state'],'files':77,'inputs':2048,'mandatoryAfterimages':6,'paths':len(seen),'finding':'Z350-M2'}))
