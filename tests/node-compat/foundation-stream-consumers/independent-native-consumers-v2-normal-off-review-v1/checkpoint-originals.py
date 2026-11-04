"""Independent pre-GC originals checkpoint. Read/hash/copy two text witnesses only."""
from pathlib import Path
import hashlib,json,stat
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
cache={}
def record(path,expected,size):
 path=Path(path);before=path.lstat();assert stat.S_ISREG(before.st_mode),str(path)
 key=(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)
 if key not in cache:
  h=hashlib.sha256()
  with path.open('rb') as f:
   for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
  cache[key]=h.hexdigest()
 after=path.lstat();assert key==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),str(path)
 assert cache[key]==expected and after.st_size==size,str(path)
 return {'path':str(path),'sha256':expected,'bytes':size,'observedStat':list(key),'readByThisReader':True}
def main():
 root_path=ROOT/'native-integration-v2-normal-off-root-results.json';raw=root_path.read_bytes();assert hashlib.sha256(raw).hexdigest()=='c44f4c544962e2a351df1df016239e54c61b21ec58a72770ccc2f791786c6627'
 root=json.loads(raw);d=root['originalInputClosure'];record(d['path'],d['sha256'],d['bytes']);closure=json.loads(Path(d['path']).read_bytes());assert len(closure['files'])==1162
 f=root['freezeReceipt'];record(f['path'],f['sha256'],f['bytes']);freeze=json.loads(Path(f['path']).read_bytes())
 observed=[record(r['path'],r['sha256'],r['bytes']) for r in closure['files']]
 assert len({r['path'] for r in observed})==1155
 mutable=[r for r in freeze['copies'] if Path(r['path']).name in ['normal-off-CMakeCache.txt','normal-off-compile_commands.json']];assert len(mutable)==2
 text=[]
 for row in mutable:
  record(row['original'],row['sha256'],row['bytes']);data=Path(row['original']).read_bytes();data.decode('utf-8')
  target=HERE/('pre-gc-original-'+Path(row['path']).name)
  with target.open('xb') as out:out.write(data)
  text.append({'original':row['original'],'frozen':row['path'],'independentWitness':str(target),'sha256':row['sha256'],'bytes':row['bytes']})
 result={'schemaVersion':1,'state':'INDEPENDENT_ALL1162_ORIGINAL_ENTRIES_CHECKED_BEFORE_GC','rootReceiptSha256':'c44f4c544962e2a351df1df016239e54c61b21ec58a72770ccc2f791786c6627','originalClosure':d,'freezeReceiptSha256':f['sha256'],'entries':1162,'distinctRecordedPaths':1155,'observed':observed,'mutableProjectConfigurationOnly':text,'allOriginalsMatchBeforeGC':True,'frozenCopiesMustRemainStrict':True,'GCStartDoesNotMeanFullNormalReviewCompleted':True,'ownerOrNativeActionsExecuted':False}
 with(HERE/'pre-gc-original-checkpoint.json').open('x') as out:json.dump(result,out,indent=2);out.write('\n')
 print(json.dumps({'state':result['state'],'entries':1162,'distinctPaths':1155,'checkpointSha256':hashlib.sha256((HERE/'pre-gc-original-checkpoint.json').read_bytes()).hexdigest(),'mutableOriginals':text}))
if __name__=='__main__':main()
