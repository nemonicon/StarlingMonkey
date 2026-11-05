"""Independent read/hash/AST review. Never imports or invokes owner tooling."""
from pathlib import Path
import ast,hashlib,json,stat

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'clock-io-valid-adapter-candidate-v1'
checks=0;seen={}
def check(v):
    global checks
    assert v;checks+=1
def row(path):
    path=Path(path);s=path.stat();check(path.is_file()and not path.is_symlink())
    h=hashlib.sha256()
    with path.open('rb')as stream:
        for b in iter(lambda:stream.read(4*1024*1024),b''):h.update(b)
    z=path.stat();identity=lambda x:(x.st_dev,x.st_ino,x.st_size,x.st_mtime_ns,x.st_ctime_ns,str(path.resolve()))
    check(identity(s)==identity(z));d=dict(path=str(path),sha256=h.hexdigest(),bytes=z.st_size)
    if str(path)in seen:check(seen[str(path)]==d)
    seen[str(path)]=d;return d
def verify(r):
    d=row(r['path']);check(d==r);return d
def load(path):return json.loads(Path(path).read_bytes())
def family(index):
    verify(index);root=Path(index['path']).parent;value=load(index['path']);names={'index.json'}
    for r in value['files']:
        check(not r['path'].startswith('/')and '..'not in Path(r['path']).parts and r['path']not in names)
        names.add(r['path']);verify(dict(path=str(root/r['path']),sha256=r['sha256'],bytes=r['bytes']))
    check({p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names)
    check(not any(p.is_symlink()for p in root.rglob('*')))

source_index=row(SOURCE/'index.json');check(source_index['sha256'].startswith('dc08495d'))
family(source_index)
refs=load(SOURCE/'references.json');inputs=load(SOURCE/'source-inputs.json')
check(len(inputs['files'])==24359 and len({r['path']for r in inputs['files']})==24359)
for r in inputs['files']:verify(r)
check(len(inputs['families'])==9)
for ix in inputs['families']:family(ix)
contract=load(refs['buildContract']['path']);proof=load(refs['buildReview']['result']['path'])
check(proof['state']==contract['requiredReviewState']=='INDEPENDENT_CLOCK_IO_TOOLS_BUILD_RESULTS_REVIEW_PASSED_V2')
for group in ['requiredFixedValues','requiredExactDescriptors','requiredPairs']:
    for k,v in contract[group].items():check(proof[k]==v)
check(proof['coverage']==contract['requiredCoverage']and proof['artifacts']==contract['artifacts'])
check(proof['artifacts'][0]==refs['hostPruner'])
check(proof['actualRootObservation']==refs['actualRootObservation']and proof['actualWorkerResult']==refs['actualWorkerResult'])
check(refs['hostPruner']['sha256']=='abb0fd2eac77e5f10f1fd2d9c3ec44e8df4908d5fe8bbccd3649d2a69b7cb0c3')
check(refs['sourceIndex']['sha256']=='55338bc0e5e0f47ed473ccd283ed1eae70183f081abb8f6a61e5c8001711945f')
check(refs['monitorIndex']['sha256']=='0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b')

controller=(SOURCE/'controller.py').read_text();tree=ast.parse(controller)
functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
for p in SOURCE.glob('*.py'):ast.parse(p.read_text());check(True)
def segment(text,name):
    t=ast.parse(text);n=next(n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name==name)
    return ast.get_source_segment(text,n)
derivation=load(SOURCE/'derivations.json');donor=Path(derivation['statelessPrimitiveDonor']['path']).read_text()
for d in derivation['exactPrimitiveSegments']:
    a=segment(controller,d['name']);b=segment(donor,d['name']);check(a==b and len(a.encode())==d['bytes']and hashlib.sha256(a.encode()).hexdigest()==d['sha256'])
check(len(derivation['exactPrimitiveSegments'])==7)
check('normalizer.write_normalized(refs[\'originalAdapter\'][\'path\'],str(normal))'in controller)
check(controller.count("'prune-clock-adapter-io'")==1 and "],300);terminals.append(row)"in controller)
check("folder,deadline,frame['rootRow']"in controller and "folder,600,frame['rootRow']"in controller)
check('closefd=False'in controller and 'finally:os.close(fd)'in controller and 'os.O_EXCL|os.O_NOFOLLOW'in controller)
check("finally:frame['c'].recheck()"in controller)
for k in ['outputRoot','externalRoot']:check(not Path(refs[k]).exists()and not Path(refs[k]).is_symlink())
node=(SOURCE/'validate-core.mjs').read_text()
check(node.count('WebAssembly.validate(')==2 and not any(s in node for s in ['WebAssembly.compile(','WebAssembly.instantiate(','new WebAssembly.Module(']))
future=load(SOURCE/'future-root-authority.template.json')
check(all(future[k]is None for k in ['state','sourceIndex','sourceIndependentReview','normalizationAllowed','singlePrunerCallAllowed','coreValidationAllowed','metadataWitDecodeAllowed']))
check(all(future[k]is False for k in ['adapterPromotionAllowed','defaultPackagerReplacementAllowed','componentAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','nativeBuildAllowed','runtimeAcceptanceClaim','operationalAdmission','timingAllowed']))
pure=load(SOURCE/'pure-results.json');check(pure['checks']==35)
for label in ['pure-source','js-syntax']:
    t=load(SOURCE/'evidence'/label/'terminal.json');check(t['rawExitCode']==0)
policy=load(SOURCE/'core-policy.json')
check(len(policy['imports'])==64 and len(policy['types'])==35 and policy['functionDefinitions']==93 and len(policy['exports'])==52)
targets=policy['targetImports'];check(len(targets)==14)
check(len(policy['retainedClockImports'])==6 and len(policy['retainedPollImports'])==2)
af=[x for x in policy['imports']if x['kind']==0];ids={x['functionIndex']for x in targets};keep=[x for x in af if x['functionIndex']not in ids]
check(len(af)==63 and len(keep)==49 and len(ids)==14)
mapping={x['functionIndex']:i for i,x in enumerate(keep+targets)}
mapping.update({i:i for i in range(63,63+93)})
check(len(mapping)==156 and set(mapping.values())==set(range(156)))
check(all(mapping[i]==i for i in range(63,156)))
check(not ids&{x['functionIndex']for x in policy['retainedClockImports']+policy['retainedPollImports']})
normalizer=Path(refs['normalizer']['path']).read_text();ntree=ast.parse(normalizer)
check(any(isinstance(n,ast.FunctionDef)and n.name=='write_normalized'and [a.arg for a in n.args.args]==['input_path','output_path']for n in ntree.body))
check('entries[1:] + entries[:1]'in normalizer and 'kinds == [2] + [0] * 63'in normalizer)
check('closefd=False'in normalizer and 'finally:\n        os.close(descriptor)'in normalizer)

# Bookend every declared row again; no transformed bytes or decoder result is
# manufactured by this independent reader.
for r in inputs['files']:verify(r)
family(source_index)
result=dict(schemaVersion=1,checks=checks,verifiedDeclaredInputRows=24359,logicalInputBytes=sum(r['bytes']for r in inputs['files']),completeSourceMembers=24,completeFixedFamilies=9,exactStatelessPrimitiveDerivations=7,sourceIndex=source_index,sourceInputManifest=row(SOURCE/'source-inputs.json'),mappingCardinality=156,originalDefinedFunctionIdsPreserved=93,plannedTargets=14,retainedFunctionImports=49,retainedClockImports=6,retainedPollImports=2,ownerChecksAuthenticatedNotRerun=35,normalizerInvoked=False,nativePrunerInvoked=False,nodeCoreValidatorInvoked=False,metadataDecoderInvoked=False,phaseInvoked=False,engineOrGuestInvoked=False)
(HERE/'checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
