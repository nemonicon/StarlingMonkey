// Pure retained browser/NetLog DATA gate. No browser, filesystem or network operations.
function need(value, message) { if (!value) throw new TypeError(message); }
const controls = /[\x00-\x08\x0a-\x1f\x7f]/;
function headerValue(value) {
  need(typeof value === 'string' && !controls.test(value), 'Raw header controls/type');
  return value.replace(/^[ \t]+|[ \t]+$/g, '').toLowerCase();
}
function objectValues(headers, name) {
  need(headers && typeof headers === 'object' && !Array.isArray(headers), 'Header object required');
  return Object.entries(headers).filter(([key]) => key.toLowerCase() === name).map(([,value]) => headerValue(value));
}
function lineValues(lines, name) {
  need(Array.isArray(lines) && lines.length <= 256, 'Finite NetLog header lines required');
  const values = [];
  for (const line of lines) {
    need(typeof line === 'string' && line.length <= 8192 && !controls.test(line), 'Raw NetLog header controls/type');
    const colon = line.indexOf(':');
    if (colon > 0 && line.slice(0, colon).toLowerCase() === name) values.push(headerValue(line.slice(colon + 1)));
  }
  return values;
}
const oneIdentity = values => values.length === 1 && values[0] === 'identity';

export function identityNegotiationGate({origin, actionPosts, responseHeaders, netlog}) {
  const parsed = new URL(origin);
  need(parsed.origin === origin && parsed.protocol === 'http:' && parsed.hostname === '127.0.0.1' && parsed.port,
       'Canonical leased loopback origin required');
  need(Array.isArray(actionPosts) && Array.isArray(responseHeaders), 'Retained browser arrays required');
  const target = origin + '/actions';
  const posts = actionPosts.filter(post => post.url === target);
  const responses = responseHeaders.filter(item => item.test === 'server-action' && item.method === 'POST' && item.url === target);
  const failures = [];
  if (posts.length !== 1) failures.push('Exactly one retained POST/actions required');
  if (responses.length !== 1) failures.push('Exactly one retained POST/actions response-header array required');
  const requestHeaders = posts.map(post => ({url:post.url, headers:post.headers,
    acceptEncodingValues:objectValues(post.headers, 'accept-encoding')}));
  const responseEncodings = responses.map(item => {
    need(Array.isArray(item.headers), 'Response headersArray required');
    return {test:item.test, requestId:item.requestId, url:item.url, method:item.method, status:item.status,
      contentEncoding:item.headers.filter(header => {
        need(header && typeof header.name === 'string' && typeof header.value === 'string' && !controls.test(header.value),
             'Raw response header fields required');
        return header.name.toLowerCase() === 'content-encoding';
      })};
  });
  const responseEncodingAbsent = responses.length === 1 && responseEncodings[0].contentEncoding.length === 0;
  if (!responseEncodingAbsent) failures.push('Content-Encoding must be absent on retained POST response');
  const playwrightRequestIdentity = requestHeaders.length === 1 && oneIdentity(requestHeaders[0].acceptEncodingValues);
  // Chromium's NetLog source namespace is used only inside this document. No CDP/PW ID or clock merge.
  const evidence = {observation:'unobserved', candidateCount:0, witnesses:[], identityObserved:false,
                    explicitContradiction:false, historyCompleteProved:false, wireBytesOrEofProved:false};
  if (netlog !== undefined) {
    need(netlog && typeof netlog.constants === 'object' && Array.isArray(netlog.events) && netlog.events.length <= 250000,
         'Bounded complete NetLog object required');
    const eventTypes = netlog.constants.logEventTypes, sourceTypes = netlog.constants.logSourceType;
    need(eventTypes && sourceTypes && Number.isSafeInteger(eventTypes.HTTP_TRANSACTION_SEND_REQUEST_HEADERS) &&
         Number.isSafeInteger(sourceTypes.URL_REQUEST), 'Pinned NetLog header/source constants required');
    const key = source => {
      need(source && Number.isSafeInteger(source.id) && Number.isSafeInteger(source.type), 'Typed NetLog source required');
      return source.type + ':' + source.id;
    };
    const candidates = new Set();
    for (const event of netlog.events) {
      if (event.source?.type === sourceTypes.URL_REQUEST && event.params?.url === target && event.params?.method === 'POST')
        candidates.add(key(event.source));
    }
    evidence.candidateCount = candidates.size;
    if (candidates.size > 1) failures.push('Ambiguous NetLog POST/actions source candidates');
    if (candidates.size === 1) for (let index = 0; index < netlog.events.length; index++) {
      const event = netlog.events[index];
      if (event.type !== eventTypes.HTTP_TRANSACTION_SEND_REQUEST_HEADERS || !candidates.has(key(event.source))) continue;
      need(evidence.witnesses.length < 8, 'Finite NetLog send-header witness bound');
      const params = event.params;
      need(params && params.line === 'POST /actions HTTP/1.1\r\n', 'Exact retained HTTP/1.1 POST request line required');
      const values = lineValues(params.headers, 'accept-encoding');
      const hosts = lineValues(params.headers, 'host');
      const identity = oneIdentity(values) && hosts.length === 1 && hosts[0] === parsed.host;
      evidence.witnesses.push({eventIndex:index, time:event.time, sourceId:event.source.id, sourceTypeId:event.source.type,
        line:params.line, headers:params.headers, acceptEncodingValues:values, hostValues:hosts, identity});
      if (!identity) evidence.explicitContradiction = true;
    }
    if (evidence.witnesses.length) {
      evidence.observation = 'explicit-send-request-headers';
      evidence.identityObserved = evidence.witnesses.every(item => item.identity);
    }
  }
  if (evidence.explicitContradiction) failures.push('Explicit NetLog send headers contradict identity origin/header');
  if (requestHeaders.some(item => item.acceptEncodingValues.length && !oneIdentity(item.acceptEncodingValues)))
    failures.push('Retained Playwright request header contradicts identity');
  const requestIdentityObserved = evidence.identityObserved;
  if (!requestIdentityObserved) failures.push('Explicit NetLog send-request identity header unobserved; browser configuration/metadata alone is insufficient');
  return {schemaVersion:1, state:'BROWSER_OUTER_IDENTITY_NEGOTIATION_GATE_V1',
    requestedContextExtraHTTPHeaders:{'Accept-Encoding':'identity'}, targetUrl:target,
    postCount:posts.length, responseHeaderCount:responses.length, requestHeaders, responseEncodings,
    playwrightRequestIdentity, netlog:evidence, requestIdentityObserved, responseEncodingAbsent,
    actualNetlogNegotiationVerified:requestIdentityObserved && responseEncodingAbsent && failures.length === 0,
    passed:failures.length === 0, failures, sourceScope:'Retained browser metadata and explicit NetLog header records; not raw HTTP wire bytes',
    innerSelfFetchEncodingProved:false, nativeAppendSelectedProved:false, privateStoreIdentityProved:false,
    uniqueCompressionCauseProved:false, fullNextAcceptance:false};
}
