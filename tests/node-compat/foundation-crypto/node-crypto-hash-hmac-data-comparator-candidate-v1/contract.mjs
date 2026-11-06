// Pure fixed DATA. No action; all nested values are frozen.
const freeze=x=>{if(x&&typeof x==='object'){for(const v of Object.values(x))freeze(v);Object.freeze(x);}return x;};
export const CONTRACT = freeze({
  "schemaVersion": 1,
  "fixtureKind": "node-sha256-hash-hmac-ordinary-v1",
  "positiveIds": [
    "hash-empty",
    "hash-ascii-abc",
    "hash-unicode-eacute",
    "hash-unicode-surrogate",
    "hash-partition-abc",
    "hash-block-55",
    "hash-block-56",
    "hash-block-63",
    "hash-block-64",
    "hash-block-65",
    "hash-nonzero-window-copy",
    "hash-output-ownership",
    "hmac-rfc4231-1",
    "hmac-rfc4231-2",
    "hmac-rfc4231-6-long-key",
    "hmac-rfc4231-7-long-key-data",
    "hmac-empty",
    "hmac-key-window-snapshot",
    "terminal-hash",
    "terminal-hmac"
  ],
  "profileIds": [
    "unsupported-hash-constructor",
    "unsupported-hmac-constructor",
    "unsupported-sha1",
    "unsupported-options",
    "unsupported-input-encoding-hex",
    "unsupported-output-encoding-base64",
    "invalid-algorithm-type",
    "invalid-receiver"
  ],
  "aliases": {
    "namedDefaultHashSame": true,
    "namedDefaultHmacSame": true,
    "bareNamedHashSame": true,
    "bareNamedHmacSame": true,
    "bareDefaultObjectSame": true,
    "diffieHellmanAliasSame": true,
    "prngAliasSame": true,
    "rngAliasSame": true,
    "pseudoRandomBytesAliasSame": true,
    "defaultWebcryptoSame": true,
    "defaultSubtleSame": true,
    "webcryptoGlobalSame": true,
    "subtleSame": true
  },
  "profileErrors": {
    "unsupported-hash-constructor": "ERR_SM_NODE_UNSUPPORTED",
    "unsupported-hmac-constructor": "ERR_SM_NODE_UNSUPPORTED",
    "unsupported-sha1": "ERR_SM_NODE_UNSUPPORTED",
    "unsupported-options": "ERR_SM_NODE_UNSUPPORTED",
    "unsupported-input-encoding-hex": "ERR_SM_NODE_UNSUPPORTED",
    "unsupported-output-encoding-base64": "ERR_SM_NODE_UNSUPPORTED",
    "invalid-algorithm-type": "ERR_INVALID_ARG_TYPE",
    "invalid-receiver": "ERR_INVALID_THIS"
  },
  "namespaceNames": [
    "Certificate",
    "Cipher",
    "Cipheriv",
    "Decipher",
    "Decipheriv",
    "DiffieHellman",
    "DiffieHellmanGroup",
    "ECDH",
    "Hash",
    "Hmac",
    "KeyObject",
    "Sign",
    "Verify",
    "X509Certificate",
    "checkPrime",
    "checkPrimeSync",
    "constants",
    "createCipheriv",
    "createDecipheriv",
    "createDiffieHellman",
    "createDiffieHellmanGroup",
    "createECDH",
    "createHash",
    "createHmac",
    "createPrivateKey",
    "createPublicKey",
    "createSecretKey",
    "createSign",
    "createVerify",
    "default",
    "diffieHellman",
    "generateKey",
    "generateKeyPair",
    "generateKeyPairSync",
    "generateKeySync",
    "generatePrime",
    "generatePrimeSync",
    "getCipherInfo",
    "getCiphers",
    "getCurves",
    "getDiffieHellman",
    "getFips",
    "getHashes",
    "getRandomValues",
    "hash",
    "hkdf",
    "hkdfSync",
    "pbkdf2",
    "pbkdf2Sync",
    "privateDecrypt",
    "privateEncrypt",
    "publicDecrypt",
    "publicEncrypt",
    "randomBytes",
    "randomFill",
    "randomFillSync",
    "randomInt",
    "randomUUID",
    "scrypt",
    "scryptSync",
    "secureHeapUsed",
    "setEngine",
    "setFips",
    "sign",
    "subtle",
    "timingSafeEqual",
    "verify",
    "webcrypto"
  ],
  "defaultNames": [
    "Certificate",
    "Cipher",
    "Cipheriv",
    "Decipher",
    "Decipheriv",
    "DiffieHellman",
    "DiffieHellmanGroup",
    "ECDH",
    "Hash",
    "Hmac",
    "KeyObject",
    "Sign",
    "Verify",
    "X509Certificate",
    "checkPrime",
    "checkPrimeSync",
    "constants",
    "createCipheriv",
    "createDecipheriv",
    "createDiffieHellman",
    "createDiffieHellmanGroup",
    "createECDH",
    "createHash",
    "createHmac",
    "createPrivateKey",
    "createPublicKey",
    "createSecretKey",
    "createSign",
    "createVerify",
    "diffieHellman",
    "fips",
    "generateKey",
    "generateKeyPair",
    "generateKeyPairSync",
    "generateKeySync",
    "generatePrime",
    "generatePrimeSync",
    "getCipherInfo",
    "getCiphers",
    "getCurves",
    "getDiffieHellman",
    "getFips",
    "getHashes",
    "getRandomValues",
    "hash",
    "hkdf",
    "hkdfSync",
    "pbkdf2",
    "pbkdf2Sync",
    "privateDecrypt",
    "privateEncrypt",
    "prng",
    "pseudoRandomBytes",
    "publicDecrypt",
    "publicEncrypt",
    "randomBytes",
    "randomFill",
    "randomFillSync",
    "randomInt",
    "randomUUID",
    "rng",
    "scrypt",
    "scryptSync",
    "secureHeapUsed",
    "setEngine",
    "setFips",
    "sign",
    "subtle",
    "timingSafeEqual",
    "verify",
    "webcrypto"
  ],
  "nativeConstants": {
    "OPENSSL_VERSION_NUMBER": 805306640,
    "RSA_PKCS1_PADDING": 1,
    "RSA_NO_PADDING": 3,
    "RSA_PKCS1_OAEP_PADDING": 4,
    "RSA_X931_PADDING": 5,
    "RSA_PKCS1_PSS_PADDING": 6,
    "RSA_PSS_SALTLEN_DIGEST": -1,
    "RSA_PSS_SALTLEN_MAX_SIGN": -2,
    "RSA_PSS_SALTLEN_AUTO": -2
  },
  "constantNames": [
    "OPENSSL_VERSION_NUMBER",
    "RSA_PKCS1_PADDING",
    "RSA_NO_PADDING",
    "RSA_PKCS1_OAEP_PADDING",
    "RSA_X931_PADDING",
    "RSA_PKCS1_PSS_PADDING",
    "RSA_PSS_SALTLEN_DIGEST",
    "RSA_PSS_SALTLEN_MAX_SIGN",
    "RSA_PSS_SALTLEN_AUTO"
  ],
  "maximumRawUtf8Bytes": 262144,
  "guestCallOrdinals": [
    1,
    2,
    3,
    1,
    1,
    1,
    1
  ],
  "knownHashVectors": [
    {
      "id": "hash-empty",
      "message": "",
      "expectedHex": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    },
    {
      "id": "hash-ascii-abc",
      "message": "abc",
      "expectedHex": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    },
    {
      "id": "hash-unicode-eacute",
      "message": "\u00e9",
      "expectedHex": "4a99557e4033c3539de2eb65472017cad5f9557f7a0625a09f1c3f6e2ba69c4c"
    }
  ],
  "knownHmacVectors": [
    {
      "id": "hmac-rfc4231-1",
      "keyHex": "0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b",
      "message": "Hi There",
      "expectedHex": "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7"
    },
    {
      "id": "hmac-rfc4231-2",
      "keyUtf8": "Jefe",
      "message": "what do ya want for nothing?",
      "expectedHex": "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843"
    },
    {
      "id": "hmac-rfc4231-6-long-key",
      "keyHex": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "message": "Test Using Larger Than Block-Size Key - Hash Key First",
      "expectedHex": "60e431591ee0b67f0d8a26aacbf5b77f8e0bc6213728c5140546040f0ee37f54"
    },
    {
      "id": "hmac-rfc4231-7-long-key-data",
      "keyHex": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "message": "This is a test using a larger than block-size key and a larger than block-size data. The key needs to be hashed before being used by the HMAC algorithm.",
      "expectedHex": "9b09ffa71b942fcb27635fbcd5b0e944bfdc63644f0713938a7f51535c3a35e2"
    }
  ],
  "additionalOracleHex": {
    "unicodeSurrogate": "3599a031c169976f3cd1936b476c8ca43baa2847edd1798c37553e60305ea9a5",
    "emptyHmac": "b613679a0814d9ec772f95d778c35fc5ff1697c493715653c6c712144292c5ad"
  },
  "limitations": "Numeric guest-header constants are build-context expectations, not Node provider/runtime identity. Whole raw strings must be durably retained by caller before any comparator.",
  "valueFields": {
    "hash-empty": [
      "messageUtf8Hex",
      "expectedHex",
      "actual"
    ],
    "hash-ascii-abc": [
      "messageUtf8Hex",
      "expectedHex",
      "actual"
    ],
    "hash-unicode-eacute": [
      "messageUtf8Hex",
      "expectedHex",
      "actual"
    ],
    "hash-unicode-surrogate": [
      "messageUtf8Hex",
      "expectedUtf8Hex",
      "actual",
      "expectedDigest"
    ],
    "hash-partition-abc": [
      "expectedHex",
      "actual"
    ],
    "hash-block-55": [
      "messageHex",
      "whole",
      "partitioned"
    ],
    "hash-block-56": [
      "messageHex",
      "whole",
      "partitioned"
    ],
    "hash-block-63": [
      "messageHex",
      "whole",
      "partitioned"
    ],
    "hash-block-64": [
      "messageHex",
      "whole",
      "partitioned"
    ],
    "hash-block-65": [
      "messageHex",
      "whole",
      "partitioned"
    ],
    "hash-nonzero-window-copy": [
      "expectedMessageHex",
      "expectedHex",
      "sameReceiver",
      "actual",
      "afterCallerMutationHex",
      "sentinelsPreserved",
      "bufferWindow",
      "bufferInputIsBuffer",
      "bufferSameReceiver",
      "bufferAfterCallerMutationHex",
      "bufferSentinelsPreserved"
    ],
    "hash-output-ownership": [
      "first",
      "second",
      "priorStableAfterSecond",
      "secondStableAfterFirstMutation",
      "expectedFirstHex",
      "expectedSecondHex"
    ],
    "hmac-rfc4231-1": [
      "expectedHex",
      "keyHex",
      "keyUtf8",
      "actual"
    ],
    "hmac-rfc4231-2": [
      "expectedHex",
      "keyHex",
      "keyUtf8",
      "actual"
    ],
    "hmac-rfc4231-6-long-key": [
      "expectedHex",
      "keyHex",
      "keyUtf8",
      "actual"
    ],
    "hmac-rfc4231-7-long-key-data": [
      "expectedHex",
      "keyHex",
      "keyUtf8",
      "actual"
    ],
    "hmac-empty": [
      "actual",
      "expectedDigest"
    ],
    "hmac-key-window-snapshot": [
      "actual",
      "expectedHex",
      "callerUnchangedAfterCreate",
      "sentinelsPreserved",
      "callerAfterMutationHex"
    ],
    "terminal-hash": [
      "actual",
      "terminal",
      "expectedFinalizedErrorCode"
    ],
    "terminal-hmac": [
      "actual",
      "terminal",
      "expectedFirstHex",
      "expectedRepeatedHex",
      "expectedRepeatedBufferBytes",
      "expectedFinalizedErrorCode"
    ]
  }
});
