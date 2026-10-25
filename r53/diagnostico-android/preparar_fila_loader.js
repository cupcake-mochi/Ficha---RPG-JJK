'use strict';
// Delta da fila (Sementes, barras no restaurador e guarda pós-lock da paleta)
// sobre o carregador instalado 6112c6cf…. Não regrava catálogos, não executa
// construir/continuar e não mexe em acionadores. Uso:
//   node r53/diagnostico-android/preparar_fila_loader.js <Codigo instalado> <saída>
const fs=require('fs'),vm=require('vm'),crypto=require('crypto'),zlib=require('zlib'),path=require('path');
const root=path.resolve(__dirname,'../..');
const sha=t=>crypto.createHash('sha256').update(t).digest('hex');
const git=(rev,p)=>require('child_process').execFileSync('git',['-C',root,'show',rev+':'+p],{encoding:'utf8',maxBuffer:1<<30});
const BASE='6112c6cf4ff34c88cea6c944b55aaf62a878e2310bb502b2ac5d2131f2d57e80';
const MODULO='2f153f659f714a7e5d16e483832f0bd4914bb93175f0527d97c7d20a03c2b110';
const MARCA='// FILA: Sementes, barras e paleta pós-lock';
const ENTRADA=/\[(\d+),(\d+),"((?:[^"\\]|\\.)*)",(\d+)\]/g;
function entradas(texto){const out={};for(const m of texto.matchAll(ENTRADA))(out[m[1]+','+m[2]]=out[m[1]+','+m[2]]||[]).push({t:m[0],i:m.index});return out;}
function unica(texto,trecho,rotulo){if(texto.split(trecho).length!==2)throw Error('Âncora não única: '+rotulo);}
function corpo(texto,nome){const s=texto.indexOf('function '+nome+'('),e=texto.indexOf('\n}\n',s);if(s<0||e<0)throw Error('Função ausente: '+nome);return texto.slice(s,e+2);}

// Pares [antes, depois] aplicados ao módulo já corrigido por r53CorrecaoAbertura_/Android_.
function patchesDoModulo(modulo){
 const A=git('fa54ab6','apps-script/Ficha.gs'),B=git('8523e57','apps-script/Ficha.gs');
 const ea=entradas(A),eb=entradas(B),patches=[];
 const so=(mapa,k,rot)=>{const v=(mapa[k]||[]).filter(x=>x.t.startsWith('['+k+',"='));if(v.length!==1)throw Error(rot+' '+k);return v[0].t;};
 // Barras: fórmula com guarda de zero, igual à já aplicada nas células.
 for(const r of [26,30,34]){const k=r+',19';patches.push([so(ea,k,'barra A'),so(eb,k,'barra B')]);}
 // CS2:CS4 passam a consultar CO2:CO5.
 for(const r of [2,3,4]){const k=r+',97';patches.push([so(ea,k,'CS A'),so(eb,k,'CS B')]);}
 // CO2:CO5 recebem as quatro Sementes; CS5 é nova. Insere após a entrada anterior em B.
 const lit=r=>{const v=(eb[r+',93']||[]).filter(x=>!x.t.startsWith('['+r+',93,"='));const nova=v.find(x=>!A.includes(x.t));if(!nova)throw Error('Semente ausente '+r);return nova;};
 for(const r of [2,3,4,5]){
  const nova=lit(r),antes=B.lastIndexOf('[',nova.i-2),ant=B.slice(antes,nova.i-1);
  if(!/^\[\d+,\d+,/.test(ant)||A.split(ant).length!==2)throw Error('Âncora anterior divergente '+r);
  let ins=nova.t;
  if(r===5){const cs=so(eb,'5,97','CS5');if(ea['5,97']&&ea['5,97'].some(x=>x.t===cs))throw Error('CS5 já existe');ins+=','+cs;}
  patches.push([ant+',',ant+','+ins+',']);
 }
 // J16 em lista estrita até CS5.
 patches.push(['["J16","DADOS_AM!$CS$2:$CS$4"]','["J16","DADOS_AM!$CS$2:$CS$5"]']);
 // Paleta pesada: mesmo corpo da fonte atual (progresso relido sob lock).
 const fonte=fs.readFileSync(path.join(root,'apps-script/Codigo.gs'),'utf8');
 patches.push([corpo(modulo,'continuarPaleta_'),corpo(fonte,'continuarPaleta_')]);
 patches.forEach(([a],i)=>unica(modulo,a,'módulo #'+i));
 return patches;
}

function lerModulo(codigo){
 const partes=[0,1,2,3,4].map(i=>{const m=new RegExp('R53_CODIGO_'+i+'_\\s*=\\s*"([^"]*)"').exec(codigo.arquivos);if(!m)throw Error('Bloco '+i);return m[1];});
 const texto=zlib.gunzipSync(Buffer.from(partes.join(''),'base64')).toString('utf8');
 if(sha(texto)!==MODULO)throw Error('Módulo divergente');
 const fn=(n)=>{const s=codigo.principal.indexOf('function '+n+'(');let e=codigo.principal.indexOf('\nfunction ',s+9);const v=codigo.principal.indexOf('\nvar ',s+9);if(v>0&&v<e)e=v;return codigo.principal.slice(s,e);};
 const [ab,an]=new Function(fn('r53CorrecaoAbertura_')+'\n'+fn('r53CorrecaoAndroid_')+';return [r53CorrecaoAbertura_,r53CorrecaoAndroid_];')();
 return an(ab(texto));
}

function preparar(principal,arquivosDoPacote){
 if(sha(principal)!==BASE)throw Error('Carregador instalado divergente do 6112c6cf…');
 if(principal.includes(MARCA))throw Error('Delta da fila já aplicado');
 const modulo=lerModulo({principal,arquivos:arquivosDoPacote});
 const patches=patchesDoModulo(modulo);
 let novoModulo=modulo;patches.forEach(([a,b])=>{novoModulo=novoModulo.replace(a,()=>b);});
 const anchor='R53_MODULO_=(new Function(r53CorrecaoAndroid_(r53CorrecaoAbertura_(code))))();';
 unica(principal,anchor,'carregador');
 const leve='// GERADO por r53/paleta_leve.js';
 unica(principal,leve,'paleta leve');
 const at=principal.indexOf(leve);
 const novaLeve=fs.readFileSync(path.join(root,'apps-script/PaletaAndroid.gs'),'utf8');
 if(!novaLeve.startsWith(leve)||!novaLeve.includes('5eb2be7e21292514156abffe0ccf6a8f84d3f957ed6e87c5c490b669d85713d7'))throw Error('Paleta leve da fonte divergente');
 const funcao=MARCA+'\nfunction r53CorrecaoFila_(code){var patches='+JSON.stringify(patches)+';patches.forEach(function(p){if(code.split(p[0]).length!==2)throw Error("Correção da fila: âncora divergente");code=code.replace(p[0],function(){return p[1];});});return code;}\n';
 let out=principal.slice(0,at).replace(anchor,'R53_MODULO_=(new Function(r53CorrecaoFila_(r53CorrecaoAndroid_(r53CorrecaoAbertura_(code)))))();')+funcao+novaLeve;
 new vm.Script(out);
 return {codigo:out,modulo:novoModulo,patches};
}
if(require.main===module){
 const [entrada,pacote,saida]=process.argv.slice(2);
 if(!entrada||!pacote||!saida)throw Error('Uso: <Codigo.gs instalado> <pasta com Ficha/Invocacoes/Analise/Configuracao/Origens .gs> <saída>');
 const arquivos=['Ficha','Invocacoes','Analise','Configuracao','Origens'].map(n=>fs.readFileSync(path.join(pacote,n+'.gs'),'utf8')).join('\n');
 const r=preparar(fs.readFileSync(entrada,'utf8'),arquivos);
 fs.writeFileSync(saida,r.codigo);fs.writeFileSync(saida+'.modulo.js',r.modulo);
 console.log(JSON.stringify({patches:r.patches.length,caracteres:r.codigo.length,sha256:sha(r.codigo),modulo_sha256:sha(r.modulo)}));
}
module.exports={preparar,BASE,MARCA};
