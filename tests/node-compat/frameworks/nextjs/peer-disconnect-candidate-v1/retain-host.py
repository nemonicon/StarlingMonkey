"""DATA-only lossless text retention. Does not rerun Node/monitor/guest."""
from pathlib import Path
import gzip,hashlib,io,json,tarfile
HERE=Path(__file__).resolve().parent
ROOTS=[Path('/private/tmp/starling-node-compat/peer-disconnect-v1-host-reference'),
 Path('/private/tmp/starling-node-compat/peer-disconnect-v1-final-source-grammar')]
def row_bytes(b):return dict(sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
if __name__=='__main__':
 assert not (HERE/'host-raw.tar.gz').exists()
 records=[];payload=io.BytesIO()
 with tarfile.open(fileobj=payload,mode='w')as archive:
  for ordinal,root in enumerate(ROOTS):
   for p in sorted(root.rglob('*')):
    assert not p.is_symlink()
    if p.is_dir():continue
    assert p.is_file()and p.stat().st_nlink==1
    b=p.read_bytes();b.decode('utf8');name=str(ordinal)+'/'+p.relative_to(root).as_posix()
    record=dict(path=str(p),archivePath=name,**row_bytes(b));records.append(record)
    info=tarfile.TarInfo(name);info.size=len(b);info.mode=0o600;info.mtime=0
    archive.addfile(info,io.BytesIO(b))
 with (HERE/'host-raw.tar.gz').open('xb')as f:
  with gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0)as g:g.write(payload.getvalue())
 (HERE/'host-evidence.json').write_text(json.dumps(dict(schemaVersion=1,records=records,
  expandedPayloadBytes=sum(r['bytes']for r in records),bundle=row_bytes((HERE/'host-raw.tar.gz').read_bytes()),
  sourceProtectionAtOriginalRun=True,firstGuestGrammarPreimages='preparation-history/first-grammar-preimages',
  laterChange='Only unexecuted guest adapter/entry success-log placement; finaltwo grammar0, no TCP rerun.'),indent=2)+'\n')
 print(json.dumps(dict(retainedRecords=len(records),expandedPayloadBytes=sum(r['bytes']for r in records))))
