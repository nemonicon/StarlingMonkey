"""Exact pure-source extraction only; never import helper or verifier modules."""
from pathlib import Path
import ast,hashlib,json
HERE=Path(__file__).resolve().parent
DONOR=HERE.parent/'ownership-secret-freezer-candidate-v1/artifact-tools/artifact_common.py'


def main():
    assert not(HERE/'index.json').exists()
    text=DONOR.read_text();tree=ast.parse(text);segments=[];derivations=[]
    donor=dict(path=str(DONOR),sha256=hashlib.sha256(DONOR.read_bytes()).hexdigest(),bytes=DONOR.stat().st_size)
    for name in['manifest','exact_release','compile_command','embedding_command']:
        node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==name);segment=ast.get_source_segment(text,node);segments.append(segment);derivations.append(dict(name=name,source=segment,exact=True))
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='classify');base=ast.get_source_segment(text,node);changed=base;edits=[]
    for before,after in [('SOURCE_POLICY','source_policy'),('==RECIPE','==recipe_sha256'),("label in LABELS","label in ('normal-off',)"),('def classify(metadata,label):','def validate_metadata(metadata,label,source_policy,recipe_sha256):')]:
        count=changed.count(before);assert count;changed=changed.replace(before,after);edits.append(dict(before=before,after=after,count=count))
    segments.append(changed)
    path=HERE/'verifier.py';body=path.read_text();start='# BEGIN SOURCE-DERIVED PURE PREDICATES';end='# END SOURCE-DERIVED PURE PREDICATES'
    assert body.count(start)==body.count(end)==1
    prefix=body[:body.index(start)+len(start)];suffix=body[body.index(end):]
    path.write_text(prefix+'\n'+'\n\n'.join(segments)+'\n'+suffix)
    (HERE/'derivations.json').write_text(json.dumps(dict(schemaVersion=1,donor=donor,exactPureFunctions=derivations,metadataPredicate=dict(donorFunction='classify',edits=edits,newFunction='validate_metadata'),oldCommonModuleImportedOrGlobalsRebound=False),indent=2)+'\n')
    print(json.dumps(dict(pureFunctionsExtracted=4,metadataPredicateEdits=len(edits),ownerModulesImported=False,actionsInvoked=False)))


if __name__=='__main__':main()
