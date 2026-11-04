"""Seal source and pure-data evidence only. Never calls the activation main."""
from pathlib import Path
import ast,hashlib,json,sys
HERE=Path(__file__).resolve().parent
def sha(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
    path=HERE/name;path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb')as stream:stream.write(value if isinstance(value,bytes)else(json.dumps(value,indent=2)+'\n').encode())
def main():
    assert len(sys.argv)==2;test=Path(sys.argv[1]);assert not(HERE/'index.json').exists()
    for name,source in [('source-tests.json',test/'final-checks/results.json'),('source-tests-first25.json',test/'checks/results.json'),('source-tests.stdout.log',test/'final.stdout.log'),('source-tests.stderr.log',test/'final.stderr.log')]:put('evidence/'+name,source.read_bytes())
    report=json.loads((HERE/'evidence/source-tests.json').read_bytes());assert report['passed']==26 and report['actionMainOrGenuineVerifierOrPreflightOrGuestOrNativeOrTargetHostInvoked']is False
    syntax=[]
    for path in HERE.glob('*.py'):ast.parse(path.read_text());syntax.append({'path':path.name,'sha256':sha(path.read_bytes()),'kind':'Python AST'})
    put('evidence/syntax-results.json',{'checks':syntax,'actionMainInvoked':False})
    rows={}
    def add(path,digest=None,size=None):
        path=Path(path);assert path.is_file()and not path.is_symlink();path=path.resolve(strict=True);raw=path.read_bytes()
        assert digest is None or sha(raw)==digest,path;assert size is None or len(raw)==size,path
        row={'path':str(path),'sha256':sha(raw),'bytes':len(raw)};assert str(path)not in rows or rows[str(path)]==row;rows[str(path)]=row
    parents=[('measurement-correctness-candidate-v1','138a4e0bcfe22ef3b48375257a50958f595dcebb607fc9267a30080948d612da'),
      ('measurement-correctness-reporting-amendment-v1','0558b50589680f9e1b812c8a62210233a768385bfabeae2f07be47c2e1fe5350'),
      ('independent-measurement-correctness-source-review-v1','c6958e3efcc22ccd980e7900d3ff129318e1e32f48b915aec65389601283b2ac'),
      ('measurement-producer-candidate-v3','46c031d36c1691c3980c51d44102e1a7cc651ff4bf8b9470c9e746697eece8bc')]
    for name,digest in parents:
        root=HERE.parent/name;add(root/'index.json',digest)
        for row in json.loads((root/'index.json').read_bytes())['files']:add(root/row['path'],row['sha256'],row['bytes'])
        path=root/'input-freeze.json'
        if path.exists():
            for row in json.loads(path.read_bytes())['inputs']:add(root/row['path'],row['sha256'],row['bytes'])
    for name,digest in [('reviewed-diagnostic-v3-on-pins.json','2e9811a54b03733d7d4dde0b42f66831a9b97da2c2f26313f078443dc329165c'),('diagnostic-v3-on-root-review-receipt.json','9681578ea64c826f72baa1e1bff1533af276ff27d6dda52c5bf1dbe064697001')]:add(HERE.parent/'production-adoption-v1'/name,digest)
    for path in sorted(HERE.rglob('*')):
        if path.is_file():add(path)
    put('input-freeze.json',{'schemaVersion':1,'state':'SOURCE_PREPARATION_AUTHORITY_SCHEMA_AND_ANCESTRY_NOT_ACTUAL_ACTIVATION','inputs':sorted(rows.values(),key=lambda row:row['path']),
      'actualRootAuthorityOnlyReadAsJSON':True,'checkedInAuthorityTemplateRemainsNull':True,'activationMainInvoked':False})
    put('source-receipt.json',{'schemaVersion':1,'state':'SEALED_FINITE_ACTIVATION_PRODUCER_SOURCE_UNEXECUTED',
      'parentCorrectnessIndexSha256':'138a4e0bcfe22ef3b48375257a50958f595dcebb607fc9267a30080948d612da','mandatoryReportingIndexSha256':'0558b50589680f9e1b812c8a62210233a768385bfabeae2f07be47c2e1fe5350',
      'producerIndexSha256':'46c031d36c1691c3980c51d44102e1a7cc651ff4bf8b9470c9e746697eece8bc','recipeSha256':'d98d1129db0a55abe18c2b96e7fe314ab27d6bc9a2ef481abed3f07d996fbba6',
      'futureAuthorityTemplateNull':True,'actualEngineTupleEmbedded':False,'sourceAndNegativeChecks':26,'actualIssuedAuthoritySchemaCompatibleAsDataOnly':True,
      'inputSha256':sha((HERE/'input-freeze.json').read_bytes()),'preparationInputs':len(rows),'activationProducerImplemented':True,
      'genuineVerifierOrActivationOrGuestOrPackagerOrNativeOrTargetHostInvoked':False,'outputFamilyCreated':False,'runtimeAcceptanceClaim':False,'timingAllowed':False})
    files=[{'path':str(path.relative_to(HERE)),'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size}for path in sorted(HERE.rglob('*'))if path.is_file()]
    put('index.json',{'schemaVersion':1,'state':'SEALED_SOURCE_ONLY_FINITE_CORRECTNESS_ACTIVATOR_FUTURE_AUTHORITY_NULL','files':files,'runtimeAcceptanceClaim':False})
    print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'inputs':len(rows),'sourceChecks':26,'activationExecuted':False}))
if __name__=='__main__':main()
