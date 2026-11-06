// Pure case DATA/construction. No formatter is invoked by importing this file.
export function positiveCases(){
  const rows=[
    ['next-demand',['value:%s:%d','ok',7]],['no-args',[]],['empty',['']],
    ['one-percent',['%%']],['one-directive',['%s']],['one-other-directive',['%j']],
    ['missing',['%s %d','ok']],['unknown',['%q',7]],['trailing',['tail%','x']],
    ['repeated-percent',['%%%%','x']],['percent-no-consume',['%%:%s:%d','ok',7]],
    ['percent-after-consumption',['%s %% %d','ok']],['extra',['%s','ok',7,true,null,undefined]],
    ['nonstring-first',[7,'x',false,null,undefined]],['null-first',[null,'x']],
    ['undefined-first',[undefined]],['negative-zero',[-0]],['nan',[NaN]],
    ['infinities',[Infinity,-Infinity]],['unicode',['λ:%s:%d','😀',7]],
    ['surrogate',['%s','\ud800']],['missing-other-directive',['%s %j','ok']],
  ];
  const operands=['', ' 7 ', '0x10', 'bad', true, false, null, undefined, 0, -0, NaN, Infinity, -Infinity, 1234567.1234567, -1234567.1234567, 1e21, 1.23e-7];
  for(let i=0;i<operands.length;i++){
    rows.push(['s-'+i,['%s',operands[i]]],['d-'+i,['%d',operands[i]]],['extra-'+i,['head',operands[i]]]);
  }
  for(const text of ['%q:%s:%d','%%%s','%s%%d','%d/%s/%%','%s%s%d','%x%%q']){
    rows.push(['grammar-'+text,[text]],['grammar-one-'+text,[text,'8']],['grammar-two-'+text,[text,'8',9]]);
  }
  return rows.map(([id,args])=>({id,args}));
}
export const settings=[
  {id:'plain',numericSeparator:false,colors:false},
  {id:'separators',numericSeparator:true,colors:false},
  {id:'colors',numericSeparator:false,colors:true},
  {id:'colors-separators',numericSeparator:true,colors:true},
];
export function typed(value){
  if(value===null)return{type:'null'};
  const type=typeof value;
  if(type==='number')return{type,value:Object.is(value,-0)?'-0':String(value)};
  if(type==='undefined')return{type};
  return{type,value};
}
