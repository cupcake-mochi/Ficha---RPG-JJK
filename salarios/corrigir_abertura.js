'use strict';
// Atualização do carregador antigo: valida os bytes originais antes de aplicar
// substituições exatas de funções. Os cinco catálogos comprimidos ficam intactos.
const fs=require('fs'),path=require('path'),vm=require('vm');
const root=path.resolve(__dirname,'..');
const original=require('./abertura_r53_original.json').funcoes;
const atual=fs.readFileSync(path.join(root,'apps-script/Codigo.gs'),'utf8').replace(/\r\n/g,'\n');
function funcao(s,n){const start=s.indexOf('function '+n+'(');if(start<0)throw Error(n);const end=s.indexOf('\n}',start)+2;return s.slice(start,end);}
function preparar(before){
 before=before.replace(/\r\n/g,'\n');
 if(!before.includes("hash!=='2f153f659f714a7e5d16e483832f0bd4914bb93175f0527d97c7d20a03c2b110'"))throw Error('Pacote R53 divergente');
 if(before.includes('r53CorrecaoAbertura_'))throw Error('Correção já presente');
 // Atualiza também uma publicação salarial anterior, sem duplicar o módulo.
 const marker='/** Emissão e salários.';
 const at=before.indexOf(marker);if(at>=0)before=before.slice(0,at);
 const patches=['notasDosTipos_','configurarPaleta_','atualizarMenuDaPaleta_','onOpen'].map(n=>[original[n],funcao(atual,n)+(n==='onOpen'?'\n'+funcao(atual,'revisarAbertura'):'')]);
 patches.push(['"onOpen":onOpen,','"onOpen":onOpen,"revisarAbertura":revisarAbertura,']);
 patches.push(["var VERSAO_MENU_PALETA_ = '09/10/2026-descricoes-2-aviso';","var VERSAO_MENU_PALETA_ = '20/10/2026-abertura-sem-recalculo';"]);
 const apply='function r53CorrecaoAbertura_(code){var patches='+JSON.stringify(patches)+';patches.forEach(function(p){if(code.split(p[0]).length!==2)throw Error("Correção R53: âncora divergente");code=code.replace(p[0],p[1]);});return code;}\n';
 const anchor='R53_MODULO_=(new Function(code))();';
 if(before.split(anchor).length!==2)throw Error('Carregador divergente');
 before=before.replace(anchor,'R53_MODULO_=(new Function(r53CorrecaoAbertura_(code)))();');
 // onOpen corrigido dentro do módulo chama o salário uma única vez.
 before=before.replace('function onOpen(){if(typeof salarioAbrir_==="function")salarioAbrir_();','function onOpen(){');
 const out=before+'\n'+apply+'function revisarAbertura(){return r53Modulo_().revisarAbertura();}\n'+fs.readFileSync(path.join(root,'apps-script/Salarios.gs'),'utf8');new vm.Script(out);return out;
}
if(require.main===module){const input=process.argv[2],output=process.argv[3];if(!input||!output)throw Error('Informe entrada e saída');const out=preparar(fs.readFileSync(input,'utf8'));fs.writeFileSync(output,out);console.log(JSON.stringify({bytes:Buffer.byteLength(out),saida:output}));}
module.exports={preparar,funcao};
