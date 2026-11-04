"""Seal source/test data only; never calls driver or component tooling."""
from pathlib import Path
import ast,hashlib,json,subprocess,sys
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'measurement-correctness-candidate-v1'
NODE=Path('/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node')
def sha(data):return hashlib.sha256(data).hexdigest()
def put(name,value):
    with(HERE/name).open('xb')as stream:stream.write(value if isinstance(value,bytes)else(json.dumps(value,indent=2)+'\n').encode())
def main():
    assert len(sys.argv)==2;tests=Path(sys.argv[1]);put('test-results.json',(tests/'checks/results.json').read_bytes());put('test.stdout.log',(tests/'stdout.log').read_bytes());put('test.stderr.log',(tests/'stderr.log').read_bytes())
    assert json.loads((HERE/'test-results.json').read_bytes())['passed']==4
    syntax=[]
    for path in sorted(HERE.rglob('*.mjs')):
        result=subprocess.run([str(NODE),'--check',str(path)],capture_output=True,text=True);assert result.returncode==0,result.stderr;syntax.append({'path':str(path.relative_to(HERE)),'sha256':sha(path.read_bytes()),'exitCode':0})
    for path in HERE.glob('*.py'):ast.parse(path.read_text())
    put('syntax-results.json',{'javascript':syntax,'pythonAST':True,'guestOrWorkloadOrNativeOrPackagerExecuted':False})
    proof=json.loads((HERE/'transformation-proof.json').read_bytes());before=(PARENT/'component-driver.mjs').read_text();after=(HERE/'proposed/component-driver.mjs').read_text();reverse=after
    for edit in reversed(proof['edits']):assert reverse.count(edit['new'])==edit['count'];reverse=reverse.replace(edit['new'],edit['old'])
    assert reverse==before
    rows={}
    def add(path,digest=None):
        path=Path(path);assert path.is_file()and not path.is_symlink();path=path.resolve(strict=True);raw=path.read_bytes();assert digest is None or sha(raw)==digest,path
        row={'path':str(path),'sha256':sha(raw),'bytes':len(raw)};assert str(path)not in rows or rows[str(path)]==row;rows[str(path)]=row
    add(PARENT/'index.json','138a4e0bcfe22ef3b48375257a50958f595dcebb607fc9267a30080948d612da')
    for row in json.loads((PARENT/'index.json').read_bytes())['files']:add(PARENT/row['path'],row['sha256'])
    for path in sorted(HERE.rglob('*')):
        if path.is_file():add(path)
    put('input-freeze.json',{'schemaVersion':1,'state':'SOURCE_ONLY_MANDATORY_BOUNDED_REPORTING_AMENDMENT','inputs':sorted(rows.values(),key=lambda row:row['path'])})
    put('source-receipt.json',{'schemaVersion':1,'state':'SEALED_HOST_REPORTING_AMENDMENT_GUEST_UNEXECUTED','parentIndexSha256':'138a4e0bcfe22ef3b48375257a50958f595dcebb607fc9267a30080948d612da','driverSha256':sha(after.encode()),'helperSha256':sha((HERE/'bounded-comparison.mjs').read_bytes()),'reverseEdits':len(proof['edits']),'sourceTests':4,'workloadBoundaryOracleProviderSchedulerOrGuestBytesChanged':False,'fullCounterexamplePersistedBeforeCompactError':True,'runtimeAcceptanceClaim':False})
    files=[{'path':str(path.relative_to(HERE)),'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size}for path in sorted(HERE.rglob('*'))if path.is_file()]
    put('index.json',{'schemaVersion':1,'state':'SEALED_SOURCE_ONLY_BOUNDED_REPORTING_AMENDMENT_NO_GUEST','files':files,'runtimeAcceptanceClaim':False})
    print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'inputs':len(rows),'reverseEdits':len(proof['edits'])}))
if __name__=='__main__':main()
