'use strict';
// Deriva a aparência das mesmas fontes da ficha. Não leva fórmulas, entradas
// dos jogadores ou regras de jogo ao caminho simples de troca de paleta.
const fs=require('fs'),vm=require('vm'),path=require('path'),z=require('zlib'),crypto=require('crypto');
const root=path.resolve(__dirname,'..');
function gerar(){
 const source=fs.readFileSync(path.join(root,'apps-script/Codigo.gs'),'utf8');
 const ctx={};vm.createContext(ctx);
 // O arquivo anterior do próprio módulo é código sem efeitos na inicialização.
 vm.runInContext(require('../medidas/carregar-ficha.js').fontes(),ctx);
 const fields=['nome','rows','cols','padrao','fundo_base','estilos','fundos','bordas','imgs'];
 const tabs=ctx.ABAS.filter(s=>!s.oculta&&!s.paleta_fixa).map(s=>{
  const out=Object.fromEntries(fields.filter(k=>s[k]!==undefined).map(k=>[k,s[k]]));
  out.vals=(s.vals||[]).filter(t=>t.length>3).map(t=>[t[0],t[1],'',t[3]]);
  return out;
 });
 const artwork=Object.fromEntries(tabs.flatMap(s=>(s.imgs||[]).map(im=>[im[4],ctx.ARTE[im[4]]])));
 const start=source.indexOf('var PALETAS = ');
 if(start<0)throw Error('Fonte de paleta ausente');
 const code='var ABAS='+JSON.stringify(tabs)+';\nvar ARTE='+JSON.stringify(artwork)+';\n'+source.slice(start)+
 '\nfunction indicePessoal_(){return {"cor da barra cheia":"CZ51"};}\n'+
 '\nreturn {trocar:function(e){continuarPaleta_(e.r53Inicio_,e.oldValue,true,null,e.value);},continuar:function(e){continuarPaleta_(e.r53Inicio_,null,false,e.range);},tempos:verTemposDaPaleta,__abas:ABAS,__arte:ARTE};';
 new vm.Script('(function(){'+code+'})()');
 const hash=crypto.createHash('sha256').update(code).digest('hex');
 const payload=z.gzipSync(code,{mtime:0}).toString('base64');
 const output='// GERADO por r53/paleta_leve.js; somente aparência, sem fórmulas da ficha.\n'+
 'var R53_PALETA_LEVE_;\nfunction r53PaletaLeve_(){if(R53_PALETA_LEVE_)return R53_PALETA_LEVE_;'+
 'var code=Utilities.ungzip(Utilities.newBlob(Utilities.base64Decode('+JSON.stringify(payload)+'),"application/gzip")).getDataAsString("UTF-8");'+
 'var hash=Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256,code,Utilities.Charset.UTF_8).map(function(b){return ("0"+((b+256)%256).toString(16)).slice(-2);}).join("");'+
 'if(hash!=='+JSON.stringify(hash)+')throw Error("Paleta: pacote divergente");return R53_PALETA_LEVE_=(new Function(code))();}\n';
 new vm.Script(output);
 return {output,code,tabs,hash,bytes:Buffer.byteLength(code),transport:Buffer.byteLength(output)};
}
if(require.main===module){const data=gerar();fs.writeFileSync(path.join(root,'apps-script/PaletaAndroid.gs'),data.output);console.log(JSON.stringify({abas:data.tabs.length,bytes:data.bytes,transporte:data.transport,hash:data.hash}));}
module.exports={gerar};
