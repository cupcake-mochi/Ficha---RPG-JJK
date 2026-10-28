'use strict';
// Oráculo delimitado das fórmulas públicas de DADOS_CONFIG, sem usar o inicializador.
const fs=require('fs'),path=require('path'),vm=require('vm');
const c={};vm.createContext(c);for(const n of ['Ficha','Configuracao'])vm.runInContext(fs.readFileSync(path.resolve(__dirname,'../../apps-script/'+n+'.gs'),'utf8'),c);
const abas=[...c.ABAS,...c.ABAS_DA_CONFIGURACAO];
const config=abas.filter(a=>a.nome==='CONFIGURAÇÃO').at(-1),dados=abas.filter(a=>a.nome==='DADOS_CONFIG').at(-1);
function valor(s,r,col){return s.vals.find(x=>x[0]===r&&x[1]===col)?.[2]??'';}
const custosLivro=Array.from({length:30},(_,i)=>valor(config,i+65,5));
function curvaInicial(nivel,custos=custosLivro){
 if(valor(dados,2,26)!=='=IF(DADOS_CONFIG!$S$2=1,0,"—")')throw Error('base publicada mudou');
 let anterior=nivel===1?0:'—';const out=[];
 for(let n=2;n<=30;n++){
  const esperada='=IF('+n+'<DADOS_CONFIG!$S$2,"—",IF('+n+'=DADOS_CONFIG!$S$2,0,IF(OR(Z'+n+'="Pendente",W'+n+'=""),"Pendente",Z'+n+'+W'+n+')))';
  if(valor(dados,n+1,26)!==esperada)throw Error('fórmula publicada mudou');
  const custo=custos[n-2];
  anterior=n<nivel?'—':n===nivel?0:anterior==='Pendente'||custo===''?'Pendente':anterior+custo;
  out.push(anterior);
 }
 return out;
}
module.exports={curvaInicial,custosLivro};
