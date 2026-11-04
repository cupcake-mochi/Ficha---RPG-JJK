'use strict';
// Gera só o contrato público destes domínios; não monta planilha nem pacote.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../..'),ctx={};vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(root,'apps-script/Ficha.gs'),'utf8'),ctx);
const ficha=ctx.ABAS.find(a=>a.nome==='FICHA');
function pos(a){const m=/^([A-Z]+)(\d+)$/.exec(a);return [+m[2],[...m[1]].reduce((n,c)=>n*26+c.charCodeAt(0)-64,0)];}
function valor(a){const [r,c]=pos(a),x=ficha.vals.find(x=>x[0]===r&&x[1]===c);if(!x)throw Error('falta '+a);return x[2];}
function separadores(f){let dentro=false,out='';for(let i=0;i<f.length;i++){const c=f[i];if(c==='"'){if(dentro&&f[i+1]==='"'){out+='""';i++;continue;}dentro=!dentro;}out+=!dentro&&c===','?';':c;}if(dentro)throw Error('string aberta');return out;}
function aspasOpcionais(f){return f.replace(/"(?:[^"]|"")*"|[^"]+/g,t=>t[0]==='"'?t:t.replace(/'(FICHA|DADOS_PROGRESSAO)'!/g,'$1!'));}
const hash=f=>crypto.createHash('sha256').update(JSON.stringify(f)).digest('hex');
const escolhas=[['D11','D10'],['N11','N10'],['X11','X10'],...['D','L','T','AB','AJ'].map(c=>[c+'21',c+'18']),...['AK','AM','AO','AQ','AS'].map(c=>[c+'15',c+'16']),...['AO','AQ','AS'].map(c=>[c+'56',c+'55']),['Z67','Z66'],['AK67','AK66'],['AE70','AE69']];
const cena=[];for(const r of [26,30,34])for(const c of ['D','P','AF','AM'])cena.push([c+r,c+(r-1)]);
for(const [c,r]of [['L',59],['W',59],['AS',59],['L',63],['W',63],['AH',63],['AS',63],['W',67]])cena.push([c+r,c+(r-1)]);
cena.push(['D45','D44'],['O45','O44'],['F48','D47'],['H48','D47'],['J48','D47'],['O48','O47'],['J50','D50'],['Z48','Z47'],['AK48','AK47']);
function dominio(campos,formulas){const headers={};return {campos:campos.map(([a,h])=>{const v=valor(a),rot=valor(h);if(typeof rot!=='string'||rot.startsWith('='))throw Error('rótulo desconhecido '+h);headers[h]=rot;const nota=(ficha.notas||[]).find(x=>x[0]===a)?.[1]||'';if(typeof nota!=='string')throw Error('nota inválida');const formula=typeof v==='string'&&v.startsWith('=');if(formula&&!/^=J(26|30|34)$/.test(v))throw Error('fórmula-alvo desconhecida '+a);return {faixa:a,valor:formula?undefined:v,formula:formula?v:undefined,nota};}),cabecalhos:headers,formulas:formulas.map(a=>{const f=valor(a);if(typeof f!=='string'||!f.startsWith('='))throw Error('falta fórmula '+a);return {faixa:a,hashes:[...new Set([f,separadores(f),aspasOpcionais(f),aspasOpcionais(separadores(f))].map(hash))]};})};}
const contrato={versao:1,escolhas:dominio(escolhas,['D19','L19','T19','AB19','AJ19','Z15','AK14','AK56']),recursos:dominio(cena.slice(0,20),['J26','J30','J34','D37']),condicoes:dominio(cena.slice(20),['D49','O49','D41','O41','Z41','AK41'])};
const out='/** Contrato público gerado das fontes Ficha.gs. Não contém dados de jogador.\n * Gerar/conferir: node r53/inicializacao/gerar_contrato_pessoal.js [--conferir]\n */\nvar R53_NOVA_PESSOAL_CONTRATO_ = '+JSON.stringify(contrato,null,2)+';\n';
const target=path.join(__dirname,'contrato_pessoal.gs');
if(require.main===module){
if(process.argv.includes('--conferir')){if(fs.readFileSync(target,'utf8')!==out)throw Error('contrato pessoal desatualizado; revisar a mudança do produtor antes de regenerar');console.log('Contrato pessoal igual às fontes: '+escolhas.length+' escolhas / 20 recursos e bônus / 9 condições.');}
else fs.writeFileSync(target,out);
}
module.exports={separadores,aspasOpcionais};
