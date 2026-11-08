'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {ler,expandir}=require('../testes/expansao_domada_modelo');
function gerar(pasta){
 const abas=ler(pasta),di=abas.find(a=>a.nome==='DADOS_INVOC'),iv=abas.find(a=>a.nome==='INVOCAÇÕES'),m=expandir(di);
 const valores=[],suporte=[],validacoes=[],notas=[];
 const aviso=r=>'IF(AND($FN'+r+'=0,$DH'+r+'=-1)," · REVISAR: nível obtido inválido; cálculo provisório no nível 1","")';
 for(let r=2;r<=13;r++){
  const antes=m.get(r+':112'),a=/^=N\((.+)\)$/.exec(antes);assert.ok(a);
  const cell=a[1],a1=cell.split('!')[1].replace(/\$/g,'');
  const vazio='OR(ISBLANK('+cell+'),AND(ISTEXT('+cell+'),'+cell+'=""))';
  const depois='=IFERROR(IF('+vazio+',0,IF(ISNUMBER('+cell+'),IF(AND('+cell+'=INT('+cell+'),'+cell+'>=1,'+cell+'<=30),'+cell+',-1),IF(ISTEXT('+cell+'),IF(REGEXMATCH('+cell+',"^([1-9]|[12][0-9]|30)$"),VALUE('+cell+'),-1),-1))),-1)';
  valores.push({aba:di.nome,r,c:112,antes,depois});
  for(const [c,marker]of [[215,' · nível '],[271,' · nv ']]){
   const antes=m.get(r+':'+c),anchor='&"'+marker+'"';assert.equal(antes.split(anchor).length,2);
   valores.push({aba:di.nome,r,c,antes,depois:antes.replace(anchor,'&'+aviso(r)+anchor)});
  }
  assert.ok(!iv.dv.some(d=>d[0].split(' ').includes(a1)));
  validacoes.push({aba:iv.nome,a1,antes:null,depois:{condition:{type:'ONE_OF_LIST',values:Array.from({length:30},(_,n)=>({userEnteredValue:String(n+1)}))},strict:true,showCustomUi:true}});
 }
 for(const d of valores)for(const c of [d.c-1,d.c+1]){
  const v=m.get(d.r+':'+c);if(v===undefined)continue;
  suporte.push({aba:di.nome,r:d.r,c,depois:v});
 }
 const acrescimos={
 K46:' Use um inteiro de 1 a 30. Texto contendo só os dígitos desse nível é interpretado como número. Entrada inválida fica preservada, exige revisão e usa cálculo provisório no nível 1.',
 O12:' Entrada inválida mostra REVISAR no título e na lista; as contas no nível 1 são provisórias, não aprovam a entidade.'
 };
 for(const [a1,texto]of Object.entries(acrescimos)){const antes=iv.notas.find(d=>d[0]===a1)?.[1];assert.equal(typeof antes,'string');notas.push({aba:iv.nome,a1,antes,depois:antes+texto});}
 return {valores,notas,validacoes,suporte};
}
if(require.main===module){const d=gerar(process.argv[2]);for(const [k,v]of Object.entries(d))fs.writeFileSync(path.join(__dirname,'nivel_obtido_'+k+'.json'),JSON.stringify(v,null,2)+'\n');console.log(Object.fromEntries(Object.entries(d).map(([k,v])=>[k,v.length])));}
module.exports={gerar};
