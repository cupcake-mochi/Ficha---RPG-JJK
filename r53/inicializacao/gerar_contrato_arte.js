'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const root=path.resolve(__dirname,'../..'),g={};vm.createContext(g);vm.runInContext(require('../../medidas/carregar-ficha').fontes(),g);
const sheets=new Map(g.ABAS.map(s=>[s.nome,s])),iv=sheets.get('INVOCAÇÕES');
const campos=[{aba:'CARTEIRA',faixa:'C8',valor:'FOTO\n顔'},...iv.redutores.map(([_,a])=>{
 const m=/^([A-Z]+)(\d+)$/.exec(a),col=[...m[1]].reduce((n,c)=>n*26+c.charCodeAt(0)-64,0)-12;
 let letra='',n=col;while(n){n--;letra=String.fromCharCode(65+n%26)+letra;n=Math.floor(n/26);}
 return {aba:iv.nome,faixa:letra+(+m[2]+2),valor:'FOTO\n式神'};
}),{aba:'FICHA PESSOAL',faixa:'D10',formulaDestino:'=CARTEIRA!$C$8'}];
function coord(a){const m=/^([A-Z]+)(\d+)$/.exec(a);return [+m[2],[...m[1]].reduce((n,c)=>n*26+c.charCodeAt(0)-64,0)];}
if(campos.length!==14)throw Error('quantidade de fotos mudou');
for(const c of campos){const s=sheets.get(c.aba),[r,col]=coord(c.faixa),v=s.vals.find(x=>x[0]===r&&x[1]===col)?.[2];
 if(v!==(c.formulaDestino||c.valor))throw Error('foto/espelho de fábrica mudou '+c.aba+'!'+c.faixa);
 c.mesclas=s.merges.filter(m=>r>=m[0]&&r<=m[2]&&col>=m[1]&&col<=m[3]).map(m=>m.slice(0,4));
 if(c.mesclas.length!==1||c.mesclas[0][0]!==r||c.mesclas[0][1]!==col)throw Error('âncora da foto mudou');
 c.nota=new Map(s.notas).get(c.faixa)||'';
 c.guarda={faixa:c.aba==='CARTEIRA'?'O8':c.aba==='INVOCAÇÕES'?c.faixa.replace(/\d+$/,String(r-3)):'D30',valor:c.aba==='CARTEIRA'?'PORTADOR':c.aba==='INVOCAÇÕES'?'NOME':'PERSONALIDADE'};
 const [gr,gc]=coord(c.guarda.faixa);if(s.vals.find(x=>x[0]===gr&&x[1]===gc)?.[2]!==c.guarda.valor)throw Error('guarda mudou');
 if(s.imgs.some(x=>r>=x[0]&&r<=x[2]&&col>=x[1]&&col<=x[3]))throw Error('alvo coincide com arte do modelo');
}
function letras(n){let s='';while(n){n--;s=String.fromCharCode(65+n%26)+s;n=Math.floor(n/26);}return s;}
const contrato={versao:1,campos,limiteAbas:50,decoracoes:g.ABAS.flatMap(s=>(s.imgs||[]).map(im=>({aba:s.nome,faixa:letras(im[1])+im[0],arquivo:im[4]})))};
const text='/** Caixas de foto/espelho medidas no fonte público; sem imagens pessoais. */\nvar R53_NOVA_ARTE_CONTRATO_ = '+JSON.stringify(contrato,null,2)+';\n';
if(require.main===module){const file=path.join(__dirname,'contrato_arte.gs');if(process.argv.includes('--conferir')){if(fs.readFileSync(file,'utf8')!==text)throw Error('contrato de fotos desatualizado');console.log('Contrato de fotos igual às fontes.');}else fs.writeFileSync(file,text);}
module.exports={contrato};
