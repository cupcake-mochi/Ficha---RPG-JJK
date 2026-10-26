'use strict';
// Missões da FICHA PESSOAL com menos idas ao servidor (26/10/2026). Vai depois do preparar_missoes.js, sobre o
// Codigo.gs que já tem a integração das missões. Nunca publica nem toca em dados de personagens.
//  - por fórmula, uma edição fora da CONFIGURAÇÃO e da CARTEIRA não lê o estado (DADOS_SALARIOS!L2), que ninguém usa;
//  - os registros de missões saem numa ida só (A2:G aberta), sem getLastRow nem getMaxRows;
//  - o XP total e o nível vêm dos espelhos da DADOS (CY47:CZ48) na faixa que já se lia, sem duas leituras soltas.
// As trocas estão em missoes_enxutas.json, como pares [antes, depois]; cada "antes" aparece uma vez só.
const fs=require('fs'),path=require('path'),vm=require('vm');
const PARES=JSON.parse(fs.readFileSync(path.join(__dirname,'missoes_enxutas.json'),'utf8'));
function preparar(source){
 if(PARES.every(([,b])=>source.split(b).length===2))throw Error('Missões enxutas já presentes');
 let out=source;
 for(const [a,b] of PARES){if(out.split(a).length!==2)throw Error('Caminho das missões divergente: '+a.split('\n')[0].trim().slice(0,60));out=out.replace(a,()=>b);}
 new vm.Script(out);return out;
}
if(require.main===module){const [input,output]=process.argv.slice(2);fs.writeFileSync(output,preparar(fs.readFileSync(input,'utf8')));}
module.exports={preparar,PARES};
