let { TextEncoder, TextDecoder } = contentGlobal;

let repCnt = 1;
let repTable = new Map();

let [$memory, $realloc, $dealloc] = $bindings;
delete globalThis.$bindings;



let dv = new DataView(new ArrayBuffer());
const dataView = mem => dv.buffer === mem.buffer ? dv : dv = new DataView(mem.buffer);
const TEXT_ENCODER_UTF8 = new TextEncoder();

function _utf8AllocateAndEncode(s, realloc, memory) {
  if (typeof s !== 'string') {
    throw new TypeError('expected a string, received [' + typeof s + ']');
  }
  if (s.length === 0) { return { ptr: 1, len: 0 }; }
  // Compute the exact allocation size up front. Some older preview1
  // adapters only support an initial allocation, not a subsequent shrink.
  let len = 0;
  let codepoints = 0;
  for (let i = 0; i < s.length; i++) {
    const ch = s.charCodeAt(i);
    codepoints++;
    if (ch < 0x80) { len += 1; }
    else if (ch < 0x800) { len += 2; }
    else if (ch >= 0xd800 && ch <= 0xdbff &&
    i + 1 < s.length &&
    (s.charCodeAt(i + 1) & 0xfc00) === 0xdc00) {
      len += 4;
      i++;
    } else { len += 3; }
  }
  const ptr = realloc(0, 0, 1, len);
  const { read, written } = TEXT_ENCODER_UTF8.encodeInto(
  s,
  new Uint8Array(memory.buffer, ptr, len),
  );
  if (read !== s.length || written !== len) {
    throw new Error('failed to encode whole string');
  }
  const res = { ptr, len, codepoints };
  return res;
}


const _debugLog = (...args) => {
  if (!globalThis?.process?.env?.JCO_DEBUG) { return; }
  console.debug(...args);
};

async function export_inspectResult(arg0) {
  _debugLog(' [Instruction::CallInterface] (sync, @ enter)');
  let ret;
  
  ret = await inspectResult();
  
  var encodeRes = _utf8AllocateAndEncode(ret, $realloc, $memory);
  var ptr0= encodeRes.ptr;
  var len0 = encodeRes.len;
  
  dataView($memory).setUint32(arg0 + 4, len0, true);
  dataView($memory).setUint32(arg0 + 0, ptr0, true);
  _debugLog('[Instruction::Return]', {
    funcName: 'inspect-result',
    paramCount: 0,
    async: false,
    postReturn: false
  });
  return;
}

async function export_run(arg0) {
  _debugLog(' [Instruction::CallInterface] (sync, @ enter)');
  let ret;
  
  ret = await apiRun();
  
  var encodeRes = _utf8AllocateAndEncode(ret, $realloc, $memory);
  var ptr0= encodeRes.ptr;
  var len0 = encodeRes.len;
  
  dataView($memory).setUint32(arg0 + 4, len0, true);
  dataView($memory).setUint32(arg0 + 0, ptr0, true);
  _debugLog('[Instruction::Return]', {
    funcName: 'run',
    paramCount: 0,
    async: false,
    postReturn: false
  });
  return;
}

class BindingsError extends Error {
  constructor (path, type, helpContext, help) {
    super(`"${__sourceName}" does not export a "${path}" ${type} as expected by the world.${
      help ? `\n  Try defining it${helpContext}:\n${help.split('\n').map(ln => `  ${ln}`).join('\n')}` : ''}`);
    }
  }
  function getInterfaceExport (mod, exportNameOrAlias, exportId) {
    if (typeof mod[exportId] === 'object')
    return mod[exportId];
    if (exportNameOrAlias && typeof mod[exportNameOrAlias] === 'object')
    return mod[exportNameOrAlias];
    if (!exportNameOrAlias)
    throw new BindingsError(exportId, 'interface', ' by its qualified interface name', `const obj = {};
    
    export { obj as '${exportId}' }
    `);
    else
    throw new BindingsError(exportNameOrAlias, 'interface', exportId && exportNameOrAlias ? ' by its alias' : ' by name', `export const ${exportNameOrAlias} = {};`);
  }
  function verifyInterfaceFn (fn, exportName, ifaceProp, interfaceExportAlias) {
    if (typeof fn !== 'function') {
      if (!interfaceExportAlias)
      throw new BindingsError(exportName, `${ifaceProp} function`, ' on the exported interface object', `const obj = {
        ${ifaceProp} () {
          
        }
      };
      
      export { obj as '${exportName}' }
      `);
      else
      throw new BindingsError(exportName, `${ifaceProp} function`, ` on the interface alias "${interfaceExportAlias}"`, `export const ${interfaceExportAlias} = {
        ${ifaceProp} () {
          
        }
      };`);
    }
  }
  function verifyInterfaceResource (fn, exportName, ifaceProp, interfaceExportAlias) {
    if (typeof fn !== 'function') {
      if (!interfaceExportAlias)
      throw new BindingsError(exportName, `${ifaceProp} resource`, ' on the exported interface object', `const obj = {
        ${ifaceProp} () {
          
        }
      };
      
      export { obj as '${exportName}' }
      `);
      else
      throw new BindingsError(exportName, `${ifaceProp} resource`, ` on the interface alias "${interfaceExportAlias}"`, `export const ${interfaceExportAlias} = {
        ${ifaceProp} () {
          
        }
      };`);
    }
  }
  
  let apiRun;
  
  let inspectResult;
  
  let __sourceName;
  function bindExports(sourceName) {
    __sourceName = sourceName;
    let __iface;
    __iface = getInterfaceExport($source_mod, 'api', null);
    apiRun = __iface.run;
    verifyInterfaceFn(apiRun, 'api', 'run', null);
    
    inspectResult = $source_mod.inspectResult;
    if (typeof inspectResult!== 'function')
    throw new BindingsError('inspectResult', 'function', '', `export function inspectResult() {};
    `);
    
  }
  