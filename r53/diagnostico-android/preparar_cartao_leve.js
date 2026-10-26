'use strict';
// Cartão em menos idas (26/10/2026): os trechos que mudaram no apps-script/EditorR53.gs, para trocar no EditorR53
// instalado (o de transporte do r53/editor_lazy.js) sem colar o arquivo inteiro. Cada trecho antigo aparece uma vez.
// node r53/diagnostico-android/preparar_cartao_leve.js  → confere os pares e imprime os hashes antes/depois
const fs=require('fs'),path=require('path'),crypto=require('crypto'),{execSync}=require('child_process');
const raiz=path.join(__dirname,'../..');
function pares(antes,depois){
 // Os pares saem do próprio diff: cada bloco trocado, com uma linha inteira de contexto de cada lado.
 const a=antes.split('\n'),b=depois.split('\n'),out=[];let i=0,j=0;
 while(i<a.length||j<b.length){
  if(a[i]===b[j]){i++;j++;continue;}
  let fi=i,fj=j,achou=false;
  for(let d=1;d<200&&!achou;d++)for(let x=0;x<=d&&!achou;x++){const y=d-x;if(a[i+x]!==undefined&&a[i+x]===b[j+y]&&a[i+x+1]===b[j+y+1]){fi=i+x;fj=j+y;achou=true;}}
  if(!achou)throw Error('diff sem fim');
  out.push([a.slice(i-1,fi+1).join('\n'),b.slice(j-1,fj+1).join('\n')]);i=fi;j=fj;
 }
 return out;
}
function aplicar(texto,ps){for(const p of ps){const n=texto.split(p[0]).length-1;if(n!==1)throw Error('Trecho encontrado '+n+' vez(es): '+p[0].slice(0,80));texto=texto.replace(p[0],()=>p[1]);}return texto;}
const sha=t=>crypto.createHash('sha256').update(t).digest('hex');
if(require.main===module){
 const {preparar}=require(path.join(raiz,'r53/editor_lazy.js'));
 const antes=execSync('git show 3e77909:apps-script/EditorR53.gs',{cwd:raiz,maxBuffer:1<<26}).toString('utf8'),depois=fs.readFileSync(path.join(raiz,'apps-script/EditorR53.gs'),'utf8');
 const ps=pares(antes,depois);if(aplicar(antes,ps)!==depois)throw Error('os pares não reproduzem o EditorR53.gs');
 const ta=preparar(antes).code,td=preparar(depois).code;if(aplicar(ta,ps)!==td)throw Error('os pares não reproduzem o de transporte');
 const saida=process.argv[2];if(saida)fs.writeFileSync(saida,JSON.stringify(ps));
 console.log(JSON.stringify({pares:ps.length,transporte_antes:sha(ta).slice(0,16),transporte_depois:sha(td),bytes_pares:JSON.stringify(ps).length}));
}
module.exports={pares,aplicar};
