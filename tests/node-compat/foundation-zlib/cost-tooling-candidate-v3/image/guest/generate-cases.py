"""Pure source generator. Check exact parent data or write one fresh output."""
from pathlib import Path
import hashlib,json,sys
HERE=Path(__file__).resolve().parent
PARENT=HERE.with_name('cost-comparison-candidate-v1')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def main():
    raw=(PARENT/'index.json').read_bytes();assert sha(raw)=='e29c596df3c809bab8fd3851b224a7ec4e84177d791c5d1f909072985f047ef8'
    index=json.loads(raw)
    for row in index['files']:
        value=(PARENT/row['path']).read_bytes();assert sha(value)==row['sha256']and len(value)==row['bytes']
    protocol=json.loads((PARENT/'protocol.json').read_bytes());assert len(protocol['cases'])==30
    cases=[dict(index=i,**row)for i,row in enumerate(protocol['cases'])]
    source='// Generated data only from exact sealed e29 protocol; no codec executed.\nexport const cases=Object.freeze('+json.dumps(cases,separators=(',',':'))+'.map(Object.freeze));\n'
    if sys.argv[1:]==['--check']:
        assert(HERE/'cases.generated.mjs').read_text()==source;print(json.dumps({'cases':30,'sourceExact':True,'codecExecuted':False}));return
    assert len(sys.argv)==3 and sys.argv[1]=='--output','--check or --output ABSOLUTE_FRESH_FILE'
    path=Path(sys.argv[2]);assert path.is_absolute()and not path.exists()and not path.is_symlink()
    with path.open('x')as stream:stream.write(source)
    print(json.dumps({'sourceOnly':True,'output':str(path),'sha256':sha(source.encode()),'codecExecuted':False}))
if __name__=='__main__':main()
