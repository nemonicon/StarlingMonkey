// Exact finite diagnostic categories from the sealed profile-bundler snapshot.
import assert from 'node:assert/strict';
export const diagnosticTemplates=Object.freeze({esm:'Node builtin is not admitted by this profile: ${source}',cjs:'CommonJS require is not admitted: ${specifier}'});
const kinds=Object.freeze({'default-esm':'esm','named-esm':'esm','namespace-esm':'esm','literal-cjs':'cjs'});
export function assertDisabledDenial(fixture,failure){
 assert(['node:stream/consumers','stream/consumers'].includes(fixture.id));assert(Object.hasOwn(kinds,fixture.kind));
 const category=kinds[fixture.kind],expected=diagnosticTemplates[category].replace(category==='cjs'?'${specifier}':'${source}',fixture.id);
 assert(failure&&typeof failure.message==='string','A bundler denial is required');
 // Rolldown may wrap/repeat a plugin diagnostic. Every admitted-builtin reason
 // present must be THIS exact category/specifier; arbitrary failures do not pass.
 const reasons=[...failure.message.matchAll(/(?:Node builtin is not admitted by this profile:|CommonJS require is not admitted:) [^\s"'`()]+/g)].map(match=>match[0]);
 assert(reasons.length>0&&reasons.every(reason=>reason===expected),'Unexpected disabled-import diagnostic');
 return{category,expectedReason:expected,actualReasons:reasons};
}
