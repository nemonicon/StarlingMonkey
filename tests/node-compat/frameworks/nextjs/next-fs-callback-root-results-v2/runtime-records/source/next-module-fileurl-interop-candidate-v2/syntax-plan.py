"""Read-only derivation of an unissued single-TU frontend argv. Never execute it."""
from pathlib import Path
import hashlib
import json
import shlex
HERE = Path(__file__).resolve().parent

def derive(plan):
    argv = list(plan['originalArgv'])
    if shlex.split(plan['actualCompilerLine']) != argv:
        raise ValueError('actual compiler line')
    original_root = str(Path(plan['originalCompileRow']['file']).parents[1])
    new_root = str(Path(plan['proposedMaterializationRoot']) / 'source')
    if argv[-2:] != ['-c', plan['originalCompileRow']['file']]:
        raise ValueError('actual input')
    # Only flags present in this genuine invocation are admitted. Refuse a new
    # output-bearing spelling rather than guessing its arity or dropping it.
    removed = []; result = []; i = 0
    while i < len(argv):
        token = argv[i]
        if token in ['-o', '-MT', '-MF']:
            if i + 1 == len(argv): raise ValueError('missing output operand')
            removed.append(argv[i:i+2]); i += 2; continue
        if token == '-MD':
            removed.append([token]); i += 1; continue
        if token.startswith('-M') or token.startswith('-o'):
            raise ValueError('unknown output flag')
        if original_root in token:
            if token != original_root + '/runtime/script_loader.cpp' and not token.startswith('-I' + original_root + '/'):
                raise ValueError('unknown WORK source use')
            token = token.replace(original_root, new_root, 1)
        result.append(token); i += 1
    if removed != [['-MD'], ['-MT', plan['originalCompileRow']['output'].split('/build/',1)[1]], ['-MF', plan['originalCompileRow']['output'].split('/build/',1)[1] + '.d'], ['-o', plan['originalCompileRow']['output'].split('/build/',1)[1]]]:
        raise ValueError('exact genuine output arguments')
    result.insert(-2, '-fsyntax-only')
    if any(x.startswith('-M') or x == '-o' for x in result): raise ValueError('output flags remain')
    return {'argv': result, 'removedOutputArguments': removed,
            'cwd': plan['proposedCwd'], 'TMPDIR': plan['proposedTmpdir'],
            'actualRootAuthority': None, 'compilerExecuted': False}

def main():
    plan = json.loads((HERE/'syntax-only-plan.json').read_bytes())
    for role in ['failureEvidence','originalWrapper','ownerImplementation']:
        row = plan[role]; raw = Path(row['path']).read_bytes()
        if len(raw) != row['bytes'] or hashlib.sha256(raw).hexdigest() != row['sha256']:
            raise ValueError(role)
    value = derive(plan)
    print(json.dumps(value, indent=2))
if __name__ == '__main__': main()
