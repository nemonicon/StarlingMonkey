// Public RSA vector copied from existing tests/integration/crypto/crypto.js, RFC7517 A.1.
const createPublicRsaJsonWebKeyData = () => ({
  alg: "RS256",
  e: "AQAB",
  ext: true,
  key_ops: ["verify"],
  kty: "RSA",
  n: "0vx7agoebGcQSuuPiLJXZptN9nndrQmbXEps2aiAFbWhM78LhWx4cbbfAAtVT86zwu1RK7aPFFxuhDR1L6tSoc_BJECPebWKRXjBZCiFV4n3oknjhMstn64tZ_2W-5JsGY4Hc5n9yBXArwl93lqt7_RN5w6Cf0h4QyQ5v-65YGjQR0_FDW2QvzqY368QQMicAtaSqzs8KJZgnYb9c7d0zgdAZHzu6qMQvRL5hajrn1n91CbOpbISD08qNLyrdkt-bFTWhAI4vMQFh6WeZu0fM4lFd2NcRwr3XPksINHaQ-G_xBniIqbw0Ls1jF44-csFCur-kEgU8awapJzKnqDKgw",
});

export async function rsaBridgeCheck(crypto) {
  const key = await crypto.subtle.importKey('jwk', createPublicRsaJsonWebKeyData(), {name:'RSASSA-PKCS1-v1_5',hash:'SHA-256'}, true, ['verify']);
  if (key.type !== 'public' || key.algorithm.modulusLength !== 2048) throw new Error('RSA import key metadata');
  return {type:key.type, algorithm:key.algorithm.name, modulusLength:key.algorithm.modulusLength, usages:[...key.usages]};
}
