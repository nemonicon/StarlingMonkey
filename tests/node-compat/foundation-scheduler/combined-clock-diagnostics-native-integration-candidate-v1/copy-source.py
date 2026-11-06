"""Proposed exclusive Source/cache copy primitive; no action at import or CLI.
A future stage/controller must provide an already-owned private target parent,
authenticate sources/modes and bookend all original inputs. Not a stage API.
"""
from pathlib import Path
import hashlib
import os
import stat

def copy_file(source, target, expected_hash, expected_bytes, expected_mode):
    source,target=Path(source),Path(target)
    assert expected_mode in (0o644,0o755)
    assert source.is_file() and not source.is_symlink()
    assert target.parent.is_dir() and not target.parent.is_symlink()
    a=source.stat()
    fd=os.open(target,os.O_CREAT|os.O_EXCL|os.O_WRONLY,expected_mode)
    try:
        # umask077 is intentionally retained; never infer requested open mode.
        os.fchmod(fd,expected_mode)
        total=0;h=hashlib.sha256()
        with source.open('rb') as incoming:
            for chunk in iter(lambda:incoming.read(65536),b''):
                h.update(chunk);total+=len(chunk)
                at=0
                while at<len(chunk):
                    n=os.write(fd,chunk[at:]);assert n>0;at+=n
        assert total==expected_bytes and h.hexdigest()==expected_hash
        os.fsync(fd);b=os.fstat(fd)
        assert stat.S_IMODE(b.st_mode)==expected_mode and b.st_nlink==1 and b.st_size==expected_bytes
        assert hashlib.sha256(target.read_bytes()).hexdigest()==expected_hash
        assert (a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino)
        z=source.stat()
        assert (a.st_dev,a.st_ino,a.st_mode,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_mode,z.st_size,z.st_mtime_ns,z.st_ctime_ns)
        return dict(bytes=total,sha256=h.hexdigest(),mode=expected_mode,independentInode=True,links=1)
    finally:os.close(fd)
