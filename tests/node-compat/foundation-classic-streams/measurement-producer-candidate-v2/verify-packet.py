"""Require a caller-approved index digest before interpreting its rows."""
from pathlib import Path
import hashlib,json,re,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def verify(expected,source_root=None):
    assert __debug__ and re.fullmatch('[0-9a-f]{64}',expected)
    raw=(HERE/'index.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==expected
    rows=json.loads(raw)['files'];seen=set()
    for row in rows:
        name=row['path'];assert type(name)is str and name not in seen;seen.add(name)
        assert not Path(name).is_absolute() and all(part not in ('','.','..')for part in name.split('/'))
        path=HERE
        for part in name.split('/'):path/=part;assert not path.is_symlink()
        assert path.is_file();data=path.read_bytes()
        assert hashlib.sha256(data).hexdigest()==row['sha256']and len(data)==row['bytes']
    seal=json.loads((HERE/'input-freeze.json').read_bytes());seen=set()
    for row in seal['inputs']:
        path=Path(row['path']);assert path.is_absolute()and str(path)not in seen;seen.add(str(path))
        assert path.is_file()and not path.is_symlink();data=path.read_bytes()
        assert hashlib.sha256(data).hexdigest()==row['sha256']and len(data)==row['bytes'],str(path)
    assert seal['preparationContext']['pathResolution']=='absolute-original-preparation-context-not-relocated'
    if source_root is not None:
        # The copied packet authenticates its own rows at the new location;
        # historical preparation rows remain explicit absolute provenance.
        # Actual mutable build inputs are independently checked in this root.
        from benchmark_common import require_source_root
        require_source_root(source_root)
    return len(rows)
if __name__=='__main__':assert len(sys.argv)==3;print(json.dumps({'sourceFilesVerified':verify(sys.argv[1],sys.argv[2]),'actionsInvoked':False}))
