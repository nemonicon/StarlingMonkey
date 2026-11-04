"""Author-only source assembly; bytes/hash/copy, no owner code or action mains."""
import argparse,hashlib,json,stat
from pathlib import Path
HERE=Path(__file__).parent.resolve()
def need(v,m):
    if not v:raise AssertionError(m)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path,expected=None):
    p=Path(path);need(p.is_file()and not p.is_symlink(),'Ordinary source input');raw=p.read_bytes();need(expected is None or sha(raw)==expected,'Exact source SHA');return raw
def write(name,value):
    p=HERE/name
    with p.open('x')as f:json.dump(value,f,indent=2);f.write('\n')
def row(path,destination,role):
    p=Path(path).resolve();raw=read(p);return{'source':str(p),'destination':destination,'sha256':sha(raw),'bytes':len(raw),'mode':stat.S_IMODE(p.stat().st_mode),'role':role}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('guest_family');parser.add_argument('guest_index_sha');args=parser.parse_args()
    need(args.guest_family=='cost-guest-oracle-candidate-v2','Only corrected immutable guestv2')
    guest=HERE.parent/args.guest_family;ixraw=read(guest/'index.json',args.guest_index_sha);index=json.loads(ixraw)
    base=json.loads(read(HERE/'publication-plan.base.json'));objects=[];inputs=[]
    for r in base['objects']:
        copy=dict(r)
        if 'imagePath'in r:
            p=HERE/r['imagePath'];read(p,r['sha256']);copy.update(source=str(p.resolve()),mode=stat.S_IMODE(p.stat().st_mode),originalSourceReferenceOnly=r['source'])
        objects.append(copy)
    # Intake exact whole indexed guest source; no renderer/provider is imported.
    for r in index['files']:
        need(not Path(r['path']).is_absolute()and all(x not in('','.','..')for x in Path(r['path']).parts),'Finite guest member')
        source=guest/r['path'];raw=read(source,r['sha256']);need(len(raw)==r['bytes'],'Guest source size');p=HERE/'image/guest'/r['path'];p.parent.mkdir(parents=True,exist_ok=True)
        with p.open('xb')as f:f.write(raw)
        objects.append(row(p,'guest/'+r['path'],'immutable-corrected-guest-source'));inputs.append({'path':str(source.resolve()),'sha256':r['sha256'],'bytes':r['bytes']})
    guest_index=HERE/'image/guest/index.json'
    with guest_index.open('xb')as f:f.write(ixraw)
    objects.append(row(guest_index,'guest/index.json','immutable-guest-source-index'))
    inputs.append({'path':str((guest/'index.json').resolve()),'sha256':sha(ixraw),'bytes':len(ixraw)})
    controls=['authority.mjs','context.mjs','native.mjs','preflight.mjs','environment.mjs','bundle.mjs','durable.mjs','node-oracle-action.mjs','collector.mjs']
    for name in controls:objects.append(row(HERE/name,'control/'+name,'new-source-guard-or-action-body'))
    for name in['tool-trees.json','packaging-source-map.json']:
        objects.append(row(HERE/name,'metadata/'+name,'source-context-descriptor'))
    trees=json.loads(read(HERE/'tool-trees.json'))['trees']
    directories=sorted({t['publicationRoot']for t in trees}|{t['publicationRoot']+'/'+e['path']for t in trees for e in t['entries']if e['kind']=='directory'})
    context={key:base[key]for key in['packagingRoot','toolchainRoot','packagerRoot','fflateBrowser','existingNativeFacts','maxRenderedInputUtf8Bytes','maxBundleUtf8Bytes']}
    context.update(guestRoot='guest',controlRoot='control',guestSourceIndexSha256=args.guest_index_sha,sourceProtocolDecisionSha256=base['sourceProtocolDecisionSha256'],functionalPackagingModules=12,legacyNativeScalarHarnessRole='mechanism/reference-only; not invoked as cost runner')
    need(len({r['destination']for r in objects})==len(objects),'No publication collisions')
    plan={**base,'state':'FRESH_ZLIB350_COST_SOURCE_PUBLICATION_PLAN_NO_AUTHORITY','objects':objects,'toolTrees':trees,'emptyAndToolDirectories':directories,'context':context,'guestRoot':'guest','guestSourceIndexSha256':args.guest_index_sha,'logicalCopyBytesBeforeProofCapsules':sum(r['bytes']for r in objects),'contextClasses':{'configuredNativeRoot':'historical source identity DATA only, not executed','frozenNativeRoot':'actual genuine350 immutable refs, full actual Root pair review required','packagingRoot':'new physically copied packaging snapshot; old Root paths not followed','toolRoots':'complete physical files plus22 explicitly rebased links','guestRoot':'corrected sealed source; original NULL oracle input is never overwritten','oracleRenderRoot':'separate future reviewed immutable actual oracle/render artifact'},'operationalAdmission':False,'metadataProjection':False,'sourcePromotionAllowed':False,'actionsAllowed':False}
    write('publication-plan.json',plan);write('guest-intake.json',{'schemaVersion':1,'state':'CORRECTED_GUEST_SOURCE_BYTES_INTAKEN_ONLY','guestSourceFamily':args.guest_family,'indexSha256':args.guest_index_sha,'files':inputs,'unfixedParent473RetainedHistoricalNotAdmitted':True,'codecOrProviderOrOracleOrBundleInvoked':False})
    print(json.dumps({'sourceObjects':len(objects),'sourceLogicalBytes':plan['logicalCopyBytesBeforeProofCapsules'],'links':len(plan['links']),'guestSourceFiles':len(index['files']),'actions':False}))
if __name__=='__main__':main()
