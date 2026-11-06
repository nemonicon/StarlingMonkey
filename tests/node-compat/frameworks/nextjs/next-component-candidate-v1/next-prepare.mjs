// Source fragment inlined in the raw ESM. No call occurs during INIT.
async function prepareServer() {
  const process=bootstrap();
  if(globalThis.process!==process)throw new Error('Native process identity mismatch');
  process.chdir('/app');
  const routing=readRoutingOrigin(process.env.STARLING_NEXT_ORIGIN);
  const required=JSON.parse(fs.readFileSync('/app/.next/required-server-files.json','utf8'));
  if(!required||typeof required.config!=='object'||!required.config||Array.isArray(required.config))
    throw new TypeError('Actual standalone Next config is required');
  process.env.NODE_ENV='production';
  process.env.NEXT_TELEMETRY_DISABLED='1';
  process.env.__NEXT_PRIVATE_STANDALONE_CONFIG=JSON.stringify(required.config);
  const require=Module.createRequire('/app/server.js');
  const versions={next:require('next/package.json').version,react:require('react/package.json').version,
    reactDom:require('react-dom/package.json').version};
  if(versions.next!=='16.4.5'||versions.react!=='19.3.1'||versions.reactDom!=='19.3.1')
    throw new Error('Pinned standalone dependency versions changed');
  // This configures real routing metadata. There is no socket/listener here;
  // the host owning this origin supplies standard incoming WASI HTTP resources.
  const next=require('next');
  const app=next({dir:'/app',dev:false,webpack:true,hostname:routing.hostname,port:routing.port});
  await app.prepare();
  const requestHandler=app.getRequestHandler();
  if(typeof requestHandler!=='function')throw new TypeError('Next request handler missing');
  const webHandler=createServerHandler(()=>requestHandler);
  return createWasiHttpHandler(webHandler,types,runFreshRequest);
}
