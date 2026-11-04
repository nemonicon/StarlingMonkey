"""DATA ONLY: authenticate explicit historical descriptor-to-archive mappings.

Never opens originalPath, imports an owner helper or executes archived code.
The caller must supply the exact map SHA. Selected-row fixtures do not claim a
complete archive. Map creation/publication and Root acceptance are separate.
"""
import argparse,hashlib,json,os,stat
from pathlib import Path,PurePosixPath

class ContextError(ValueError):pass
def require(condition,message):
    if not condition:raise ContextError(message)
def exact(value,keys):require(type(value)is dict and set(value)==set(keys),'Unexpected record fields')
def text(value):
    require(type(value)is str and value and '\0'not in value,'Need nonempty text without NUL')
    return value
def sha_text(value):
    require(type(value)is str and len(value)==64 and all(c in'0123456789abcdef'for c in value),'Need SHA256')
    return value
def size_value(value):require(type(value)is int and value>=0,'Need nonnegative integer bytes');return value
def relative(value):
    text(value);parts=PurePosixPath(value)
    require('\\'not in value and not parts.is_absolute()and str(parts)==value and all(p not in('','..','.')for p in parts.parts),'Unsafe archive path')
    require(not(len(value)>1 and value[1]==':'),'Drive paths are not archive-relative')
    return parts.parts
def object_pairs(pairs):
    result={}
    for key,value in pairs:
        require(key not in result,'Duplicate JSON field');result[key]=value
    return result

class ArchiveContextReader:
    FORMATS={'input-freeze-v1':('inputs','path'),'v11-copied-evidence-v1':('copiedEvidence','original'),'sealed-files-v1':('files','path')}
    JSON_LIMIT=64*1024*1024
    def __init__(self,archive_root,map_path,expected_map_sha256):
        root=Path(archive_root)
        require(root.is_absolute()and str(root)==os.path.normpath(str(root))and root.resolve(strict=True)==root,'Need canonical absolute archive root')
        require(root.is_dir()and not root.is_symlink(),'Archive root must be an ordinary directory')
        self.fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);self.entries={};self.contexts={}
        try:self._load(map_path,sha_text(expected_map_sha256))
        except BaseException:self.close();raise
    def close(self):
        if self.fd is not None:os.close(self.fd);self.fd=None
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    def _read(self,path,expected=None,count=None,collect=False):
        parts=relative(path);directory=os.dup(self.fd);file_fd=None
        try:
            for part in parts[:-1]:
                next_fd=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=directory)
                os.close(directory);directory=next_fd
            file_fd=os.open(parts[-1],os.O_RDONLY|os.O_NOFOLLOW,dir_fd=directory)
            before=os.fstat(file_fd);require(stat.S_ISREG(before.st_mode),'Archive member is not regular')
            if count is not None:require(before.st_size==size_value(count),'Archive member size mismatch')
            if collect:require(before.st_size<=self.JSON_LIMIT,'JSON descriptor exceeds finite reader bound')
            digest=hashlib.sha256();chunks=[]
            while True:
                block=os.read(file_fd,1024*1024)
                if not block:break
                digest.update(block)
                if collect:chunks.append(block)
            after=os.fstat(file_fd)
            require((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'Archive member changed during read')
            actual=digest.hexdigest()
            if expected is not None:require(actual==sha_text(expected),'Archive member SHA mismatch')
            return(b''.join(chunks)if collect else None),actual,after.st_size
        finally:
            if file_fd is not None:os.close(file_fd)
            os.close(directory)
    def _json(self,path,expected,count=None):
        raw,_,_=self._read(path,expected,count,True)
        return json.loads(raw,object_pairs_hook=object_pairs)
    def _load(self,map_path,expected):
        mapping=self._json(map_path,expected)
        exact(mapping,['schemaVersion','state','contexts'])
        require(type(mapping['schemaVersion'])is int and mapping['schemaVersion']==1 and mapping['state']=='EXPLICIT_ARCHIVE_CONTEXT_MAP_V1','Unknown map schema/state')
        require(type(mapping['contexts'])is list and mapping['contexts'],'Need explicit contexts')
        for context in mapping['contexts']:
            exact(context,['contextId','format','coverage','manifest','rows'])
            identity=text(context['contextId']);require(identity not in self.contexts,'Duplicate context')
            require(context['format']in self.FORMATS and context['coverage']in('selected-rows','all-rows'),'Unknown context format/coverage')
            manifest=context['manifest'];exact(manifest,['originalPath','archivePath','sha256','bytes']);text(manifest['originalPath'])
            document=self._json(manifest['archivePath'],manifest['sha256'],manifest['bytes'])
            list_key,path_key=self.FORMATS[context['format']]
            records=document.get(list_key);require(type(records)is list,'Manifest lacks declared row list')
            require(type(context['rows'])is list and context['rows'],'Need explicit mapped rows')
            covered=set()
            for row in context['rows']:
                exact(row,['manifestRows','originalPath','expectedSha256','bytes','archivePath'])
                original=text(row['originalPath']);digest=sha_text(row['expectedSha256']);count=size_value(row['bytes']);relative(row['archivePath'])
                require(type(row['manifestRows'])is list and row['manifestRows'],'Need manifest row positions')
                for position in row['manifestRows']:
                    require(type(position)is int and 0<=position<len(records)and position not in covered,'Duplicate/out-of-range manifest row')
                    record=records[position];require(type(record)is dict,'Invalid original descriptor')
                    require(record.get(path_key)==original and record.get('sha256')==digest and type(record.get('bytes'))is int and record['bytes']==count,'Mapping differs from original descriptor')
                    covered.add(position)
                key=(identity,original,digest);require(key not in self.entries,'Ambiguous descriptor mapping')
                self.entries[key]=dict(row)
            if context['coverage']=='all-rows':require(covered==set(range(len(records))),'Incomplete all-rows context')
            self.contexts[identity]={'coverage':context['coverage'],'mappedManifestRows':len(covered),'manifestRows':len(records),'originalManifest':manifest['originalPath']}
    def verify(self,context_id,original_path,expected_sha256):
        key=(text(context_id),text(original_path),sha_text(expected_sha256))
        require(key in self.entries,'Unknown context/originalPath/expectedHash tuple')
        row=self.entries[key];_,digest,count=self._read(row['archivePath'],expected_sha256,row['bytes'])
        return{'contextId':context_id,'originalPath':original_path,'expectedSha256':digest,'bytes':count,'archivePath':row['archivePath'],'originalFilesystemOpened':False}
    def verify_all(self):
        return[self.verify(*key)for key in self.entries]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive-root',required=True);parser.add_argument('--map-path',required=True);parser.add_argument('--expected-map-sha256',required=True)
    parser.add_argument('--verify-all',action='store_true');parser.add_argument('--context');parser.add_argument('--original-path');parser.add_argument('--expected-sha256')
    args=parser.parse_args()
    require(args.verify_all!=(args.context is not None or args.original_path is not None or args.expected_sha256 is not None),'Choose verify-all or one exact tuple')
    with ArchiveContextReader(args.archive_root,args.map_path,args.expected_map_sha256)as reader:
        records=reader.verify_all()if args.verify_all else[reader.verify(args.context,args.original_path,args.expected_sha256)]
        print(json.dumps({'schemaVersion':1,'state':'MAPPED_ARCHIVE_DESCRIPTORS_BYTE_VERIFIED_ONLY','records':records,'contexts':reader.contexts,'originalFilesystemOpened':False,'programExecuted':False,'archiveAcceptance':False}))
if __name__=='__main__':main()
