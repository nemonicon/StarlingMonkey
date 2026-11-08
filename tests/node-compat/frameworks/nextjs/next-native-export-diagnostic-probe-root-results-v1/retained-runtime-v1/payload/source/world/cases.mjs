// Metadata only at INIT. Every RegExp/Function construction is inside collect.
export const cases=Object.freeze([
 {id:'ascii-identifier-control',method:'RegExp',source:'^[A-Za-z_$][A-Za-z0-9_$]*$',flags:'',inputs:['alpha','_x','$x','a1','1a','π','猫']},
 {id:'unicode-codepoint-control',method:'RegExp',source:'^\\u{03C0}+$',flags:'u',inputs:['π','ππ','Π','a']},
 {id:'astral-codepoint-control',method:'RegExp',source:'^\\u{1F600}$',flags:'u',inputs:['😀','a','']},
 {id:'id-start-property',method:'RegExp',source:'^[\\p{ID_Start}]$',flags:'u',inputs:['A','π','猫','1','_','$','😀']},
 {id:'id-continue-property',method:'RegExp',source:'^[\\p{ID_Continue}]$',flags:'u',inputs:['A','π','猫','1','_','\u0301','\u200c','\u200d']},
 {id:'actual-zod-dynamic',method:'RegExp',source:'[$_\\p{ID_Start}][$\\u200c\\u200d\\p{ID_Continue}]*',flags:'u',inputs:['alpha','π2','猫1','_x','$x','1a','a\u200c','😀']},
 {id:'actual-zod-literal-parser',method:'FunctionLiteral',source:'[$_\\p{ID_Start}][$\\u200c\\u200d\\p{ID_Continue}]*',flags:'u',literalBody:'return /[$_\\p{ID_Start}][$\\u200c\\u200d\\p{ID_Continue}]*/u;',inputs:['alpha','π2','猫1','_x','$x','1a','a\u200d','😀']},
 {id:'unicode-letter-property',method:'RegExp',source:'^\\p{Letter}+$',flags:'u',inputs:['Hello','π','猫','É','e\u0301','12','😀']},
 {id:'unicode-script-property',method:'RegExp',source:'^\\p{Script=Greek}+$',flags:'u',inputs:['αβ','Π','abc','猫']},
 {id:'zod-emoji-properties',method:'RegExp',source:'^(\\p{Extended_Pictographic}|\\p{Emoji_Component})+$',flags:'u',inputs:['😀','👨‍👩‍👧‍👦','1','#','A','猫']},
 {id:'unicode-ignorecase-control',method:'RegExp',source:'^k$',flags:'iu',inputs:['k','K','K','a']},
 {id:'invalid-property-negative',method:'RegExp',source:'[\\p{Not_A_Unicode_Property}]',flags:'u',inputs:['a']},
]);
function capturedError(value){
 const result={valueType:typeof value,isNull:value===null};
 if(value===null||!['object','function'].includes(typeof value)){result.primitive=value===undefined?'undefined':String(value);return result;}
 for(const key of ['name','message','code']){try{const v=value[key];result[key]=v===undefined?{type:'undefined'}:{type:typeof v,value:['string','number','boolean'].includes(typeof v)?v:null};}catch{result[key]={type:'read-threw'};}}
 return result;
}
export function collectRegExpProbe(call){
 const records=[];
 for(const item of cases){
  const record={id:item.id,method:item.method,requestedSource:item.source,requestedFlags:item.flags};
  try{
   const regex=item.method==='FunctionLiteral'?Function(item.literalBody)():new RegExp(item.source,item.flags);
   record.compiled=true;record.actualSource=regex.source;record.actualFlags=regex.flags;
   record.samples=item.inputs.map(input=>{const match=regex.exec(input);return{input,matched:match!==null,match:match===null?null:match[0],index:match===null?null:match.index};});
  }catch(error){record.compiled=false;record.error=capturedError(error);}
  records.push(record);
 }
 return{schemaVersion:1,suite:'ISOLATED_UNICODE_PROPERTY_REGEXP_PROBE_V1',call,intlType:typeof Intl,records,applicationImported:false,applicationRewritten:false,fullNextClaim:false};
}
