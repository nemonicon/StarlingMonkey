"""Bounded source HOLD reader; standard-library hash/AST/data only."""
from pathlib import Path
import ast,difflib,hashlib,json,re,shlex,stat,sys
HERE=Path(__file__).resolve().parent;FAMILY=HERE.parent;REPO=HERE.parents[3]
OWNER=FAMILY/'native-integration-candidate-v3';AMEND=FAMILY/'descriptor-shadow-amendment-v1'
assert len(sys.argv)==2,'Caller-reviewed sealed v3 index SHA required'
OWNER_SHA=sys.argv[1];assert re.fullmatch('[0-9a-f]{64}',OWNER_SHA)
AMEND_SHA='c92e09b73f863dc9075b8d465b1804b8d8fd670dbff125f3188747c044190d37'
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
index=indexed(OWNER,OWNER_SHA,81);indexed(AMEND,AMEND_SHA,6)
receipt=doc(OWNER/'source-receipt.json');manifest=doc(OWNER/'input-freeze.json')
assert len(manifest['inputs'])==receipt['preparationInputs']==2146 and manifest['relocatedActionsMustNotReinterpretThesePaths']is True
for row in manifest['inputs']:read(OWNER/row['path'],row['sha256'],row['bytes'])
for name,h in receipt['parentIndices'].items():indexed(OWNER/name,h)
old=FAMILY/'native-integration-candidate-v2'
indexed(old,'c65ed2c400b49e63d716ba92b05d0b5f0f56680f6a89d94a9b2c813faec0aba1',77)
indexed(FAMILY/'independent-native-integration-v2-source-review-v1','89bc84d69c17b3959105ef1776c3275981b3bdace2aca7de64a355a1e6aabe1b',8)
indexed(FAMILY/'forced-include-amendment-v1','1d0c8626665c06247f4240be359704a2c10851489cb77e203f14ae511343c58c',11)
indexed(FAMILY/'native-integration-candidate-v1','3ff3a59d4fc1fafa32b2ba1e6ec5a1b8d7787f4e7eca1ee6855d7b38cc7c45db',72)
indexed(FAMILY/'independent-native-integration-source-review-v1','dafaff07578be6f62883ddf0815c023f4ba0e12b0c5b1e6ab5899d4f0edb474c')
proof=doc(AMEND/'derivation-proof.json');assert proof['parentIndexSha256']=='c65ed2c400b49e63d716ba92b05d0b5f0f56680f6a89d94a9b2c813faec0aba1'
before=read(old/'codec-evidence.py',proof['beforeSha256']).decode();after=read(AMEND/'codec-evidence.after.py',proof['afterSha256']).decode();value=before
for a,b in proof['exactTwoIdentifierEdits']:assert value.count(a)==1;value=value.replace(a,b)
assert len(proof['exactTwoIdentifierEdits'])==2 and value==after and read(OWNER/'codec-evidence.py')==after.encode()
for a,b in reversed(proof['exactTwoIdentifierEdits']):assert value.count(b)==1;value=value.replace(b,a)
assert value==before
assert ''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/codec-evidence.py',tofile='b/codec-evidence.py'))==read(AMEND/'descriptor-shadow.UNAPPLIED.patch').decode()
tree=ast.parse(after);function=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=='after')
bindings=[(x.targets[0].id,ast.unparse(x.value.func))for x in function.body if isinstance(x,ast.Assign)and isinstance(x.targets[0],ast.Name)and x.targets[0].id in ['selected','selected_symbols']]
assert bindings==[('selected','selected_compile_input'),('selected_symbols','symbols')]
returned=next(x.value for x in function.body if isinstance(x,ast.Return));fields={k.value:v for k,v in zip(returned.keys,returned.values)}
assert isinstance(fields['selectedCompileInput'],ast.Name)and fields['selectedCompileInput'].id=='selected'
symbol_fields={k.value:v for k,v in zip(fields['archiveSymbolEvidence'].keys,fields['archiveSymbolEvidence'].values)}
assert isinstance(symbol_fields['selectedDefinitions'],ast.Name)and symbol_fields['selectedDefinitions'].id=='selected_symbols'
mock=doc(AMEND/'after-contract-results.json');assert mock['count']==7 and mock['mockedReadersAndSubprocessOnly']is True and mock['nativeOrCompilerOrGuestOrActualArchiveOrCommandExecuted']is False
fixed=mock['actualFixedReturn'];held=mock['actualHeldReturn'];assert fixed['selectedCompileInput']['version']=='sm-selected-moz-z-compile-input-v1'and len(fixed['archiveSymbolEvidence']['selectedDefinitions'])==7
assert fixed['selectedCompileInput']!=fixed['archiveSymbolEvidence']['selectedDefinitions']
assert held['selectedCompileInput']==held['archiveSymbolEvidence']['selectedDefinitions']
assert read(OWNER/'test-after-contract.py')==read(AMEND/'test-after-contract.py')
derivations=[]
for name in ['source-transformations.json','tool-transformations.json','model-transformations.json']:
 data=doc(OWNER/name)
 for row in data.get('records',data.get('files',[])):
  before=read(REPO/row['origin'],row['beforeSha256']).decode();after_image=read(OWNER/row['path'],row['afterSha256']).decode();value=before
  for e in row['edits']:assert value.count(e['old'])==e['count'];value=value.replace(e['old'],e['new'])
  assert value==after_image,row['path']
  for e in reversed(row['edits']):
   for at in reversed(e['afterOffsets']):assert value[at:at+len(e['new'])]==e['new'];value=value[:at]+e['old']+value[at+len(e['new']):]
  assert value==before;derivations.append(row['path'])
policy=doc(OWNER/'policy.json',receipt['policySha256']);read(OWNER/'layer-policy.py',receipt['helperSha256']);read(OWNER/'source/tests/node-compat/build-engine.sh',receipt['recipeSha256'])
assert receipt['recipeSha256']=='b8b26474682c4236a6f1b02337f7b100a3a79adab5c95c2c7a96a0d0176b546e'
assert receipt['policySha256']=='16d80d546da62989153b9ecd3cc8006ed7b47eb23bbb9661873e8a770bb1c65a'
assert receipt['helperSha256']=='35e0f5b9d37f6912239c0744a796e16195991a642e546eef6fa2d84a5e163f0f'
old_policy=doc(old/'policy.json');assert policy['expectedNativeSourceManifest']==old_policy['expectedNativeSourceManifest']
old_policy['selectedCodecCompileContract']['codecEvidenceSha256']=proof['afterSha256'];assert policy==old_policy
native={row['path']:row['sha256']for row in policy['expectedNativeSourceManifest']};assert len(native)==350
for n,h in native.items():
 candidates=[OWNER/'source'/n,FAMILY/'integration-candidate-v1/source'/n,Path('/tmp/starling-node-compat/classic-trace-source-v1')/n,REPO/n]
 exact=[p for p in candidates if p.is_file()and not p.is_symlink()and hashlib.sha256(p.read_bytes()).hexdigest()==h];assert exact,n;read(exact[0],h)
for p in (OWNER/'source/builtins/node-compat/zlib').iterdir():
 if p.is_file():assert read(p)==read(FAMILY/'integration-candidate-v1/source/builtins/node-compat/zlib'/p.name),p
assert read(OWNER/'compile-input.mjs')==read(old/'compile-input.mjs')
assert read(OWNER/'artifact-tools/bootstrap-classifier.py')==read(old/'artifact-tools/bootstrap-classifier.py')and read(OWNER/'artifact-tools/bootstrap-preflight.mjs')==read(old/'artifact-tools/bootstrap-preflight.mjs')
assert len([p for p in native if p.endswith('.cpp')and p.startswith(('builtins/','runtime/'))])==62 and len(policy['privateTargetCpp'])==6
toolpins=doc(OWNER/'artifact-tools/tool-pins.json');assert toolpins['recipeSha256']==receipt['recipeSha256']and toolpins['sourcePolicySha256']==receipt['policySha256']and toolpins['sourceHelperSha256']==receipt['helperSha256']
tools=toolpins['toolDependencies'];assert len(tools)==receipt['toolDependencies']and len(tools)==len({r['path']for r in tools})
rel='tests/node-compat/foundation-zlib/native-integration-candidate-v3';stage_rows={}
for row in tools:
 n=row['path'];candidates=[OWNER/'source'/n]
 if Path(n).is_relative_to(Path(rel)):candidates.append(OWNER/Path(n).relative_to(Path(rel)))
 candidates += [Path('/tmp/starling-node-compat/classic-trace-source-v1')/n,REPO/n]
 exact=[p for p in candidates if p.is_file()and not p.is_symlink()and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']];assert exact,n;read(exact[0],row['sha256'],row['bytes']);stage_rows[n]=row['sha256']
for n,h in native.items():assert n not in stage_rows or stage_rows[n]==h;stage_rows[n]=h
data=doc(OWNER/'evidence/actual-command-python.json');js=doc(OWNER/'evidence/actual-command-node.json');assert len(data['actualCommandRecords'])==64 and js['count']==74
selected=data['selectedCompileInput'];required=selected['requiredForcedInclude'];assert selected['version']=='sm-selected-moz-z-compile-input-v1'and required==selected['headers'][3]and required['sha256']=='841e57a382d7d8219431dc26e1d1307af1649228503d21bcf2eac826fc99acd6'
for row in data['actualInputs']+[selected['archive'],*selected['headers']]:read(row['path'],row['sha256'],row['bytes'])
for row in data['actualCommandRecords']:
 words=shlex.split(row['command']);assert words==row['tokens']and sha(row['command'].encode())==row['commandSha256'];assert words.count('-include')==1 and words[words.index('-include')+1]==required['path']
 assert all(w=='-include'or not w.startswith(('-include','-imacros','-Wp,','-Xpreprocessor','-Xclang'))for w in words)
 assert all(not w.startswith(('-DZ_PREFIX','-UZ_PREFIX'))for w in words)
recipe=read(OWNER/'source/tests/node-compat/build-engine.sh').decode();admission=read(OWNER/'source/tests/node-compat/zlib-admission.mjs').decode();layer=read(OWNER/'layer-policy.py').decode();artifact=read(OWNER/'artifact-tools/artifact_common.py').decode();launcher=read(OWNER/'artifact-tools/build-one.py').decode();stage=read(OWNER/'stage-source.py').decode()
assert recipe.index("metadata['zlibSelectedCodecInput']=codec.selected_compile_input(spidermonkey_dir)")<recipe.index('metadata = layer.decorate(')<recipe.index("metadata['zlibPolicy']['codecWitness']=codec.after(")
assert proof['afterSha256']in recipe and proof['afterSha256']==policy['selectedCodecCompileContract']['codecEvidenceSha256']
assert 'codec.no_second_codec(words,selected)'in layer and 'validateCompileForcedInclude(tokens,metadata.zlibSelectedCodecInput)'in admission
assert "metadata['zlibSelectedCodecInput']==witness['selectedCompileInput']"in artifact and 'assert.deepEqual(witness.selectedCompileInput,metadata.zlibSelectedCodecInput)'in admission
assert 'Zlib350 operational admission CLOSED'in admission
assert 'production-zlib-v3/native-freeze'in artifact and 'zlib-v3-build'in launcher and 'production-zlib-v3/builds'in launcher
assert 'zlib-source-v3'in stage and 'native-integration-candidate-v3'in stage and 'originalPreparationRoot'in stage
assert 'gt 255'in recipe and 'REQUIRED_START_FREE = 2 * 1024 * 1024 * 1024'in launcher and 'MINIMUM_FREE = 800 * 1024 * 1024'in launcher
for name in ['bootstrap-pins.json','runtime-pins.json']:
 p=doc(OWNER/name);assert len(p['variants'])==4 and all(v is None for v in p['variants'].values())
assert receipt['runtimeBackendProof']=={'verified':False,'version':None,'vernum':None}and receipt['runtimeEnginePins']is receipt['validationBootstrapPins']is None
for row in list(seen.values()):read(row['path'],row['sha256'],row['bytes'])
result={'schemaVersion':1,'state':'INDEPENDENT_ZLIB350_V3_CORRECTED_SOURCE_SUCCESSOR_REVIEW_PASSED_NO_ACTIONS',
 'ownerIndexSha256':OWNER_SHA,'ownerFiles':len(index['files']),'preparationInputs':len(manifest['inputs']),'mandatoryDescriptorAmendmentIndexSha256':AMEND_SHA,'mandatoryAmendmentFiles':6,
 'exactCodecIdentifierChanges':2,'forwardReverseDerivationRecords':len(derivations),'derivedFiles':derivations,
 'descriptorShadowM2Resolved':True,'previousIncludeM1CorrectionRetained':True,'nativeSources':350,'nativePayloadAndApi40Unchanged':True,
 'expectedCompileCPP':{'on':62,'off':61},'privateTargetCPP':{'on':6,'off':5},'actualCommandDataRecords':64,
 'toolRows':len(tools),'nativeToolOverlap':350+len(tools)-len(stage_rows),'futureStageUniquePlanRows':len(stage_rows),
 'storedMockedAfterWitnessRegressionChecksAuthenticatedNotRerun':7,'preDecorateSelectedArchiveFourHeadersAuthenticated':True,
 'selectedRequiredInclude':required,'recipeSha256':receipt['recipeSha256'],'policySha256':receipt['policySha256'],'helperSha256':receipt['helperSha256'],
 'namespaces':{'source':'zlib-source-v3','build':'zlib-v3-build','artifacts':'production-zlib-v3'},
 'runtimeBackendProof':receipt['runtimeBackendProof'],'futurePinsAllFourNull':True,'operationalAdmissionOpen':False,
 'ownerImportsTestsActionsStageBuildCompilerNativeVerifierPreflightGuestHostOrTimingExecutedByReviewer':False,
 'runtimeAcceptanceClaim':False,'performanceClaim':False,'concreteSourceBlockers':[],
 'scope':'Scoped source successor review. Exact tiny semantic correction plus new source/recipe/tool closure; no existing engine admitted or native metadata projected.',
 'limitations':['Actual new link shape, archive extraction and linked runtime version remain unobserved future gates.','The7 mocked checks establish return/witness dataflow only, not real native/backend behavior.','No stage/build/freezer/bootstrap/guest/GC/cross-decode/host or cost result; future Root staging and independent review remain separate.'],
 'verifiedFiles':sorted(seen.values(),key=lambda r:r['path'])}
with(HERE/'results.json').open('x')as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'state':result['state'],'ownerFiles':len(index['files']),'inputs':len(manifest['inputs']),'paths':len(seen),'toolRows':len(tools),'stageUniquePaths':len(stage_rows)}))
