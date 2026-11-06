import * as cryptoNode from 'node:crypto';
import * as cryptoBare from 'crypto';
import * as bufferNode from 'node:buffer';
import * as bufferBare from 'buffer';
import * as streamNode from 'node:stream';
import * as streamBare from 'stream';
export function run() {
  return JSON.stringify({schemaVersion:1,kind:'builtin-namespace-alias-identity-v1',
    namespaces:{crypto:cryptoBare===cryptoNode,buffer:bufferBare===bufferNode,stream:streamBare===streamNode},
    defaultObjects:{crypto:cryptoBare.default===cryptoNode.default,buffer:bufferBare.default===bufferNode.default,stream:streamBare.default===streamNode.default},
    namedFunctions:{createHash:cryptoBare.createHash===cryptoNode.createHash,createHmac:cryptoBare.createHmac===cryptoNode.createHmac,Buffer:bufferBare.Buffer===bufferNode.Buffer,Readable:streamBare.Readable===streamNode.Readable},
    constants:{cryptoSame:cryptoBare.constants===cryptoNode.constants,opensslVersionNumber:cryptoNode.constants.OPENSSL_VERSION_NUMBER},
    providerIdentityProved:false,cryptoOperationsInvoked:false,publicProfileAdmission:false});
}
