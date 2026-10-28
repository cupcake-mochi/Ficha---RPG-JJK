'use strict';
// Exporta somente contrato público. Sem SpreadsheetApp, rede ou dados de jogador.
const fs=require('fs'),path=require('path'),vm=require('vm'),crypto=require('crypto');
const root=path.resolve(__dirname,'../..');
const {separadores}=require('./gerar_contrato_pessoal');
const variantes=f=>[...new Set([f,separadores(f),f.replace(/'DADOS_SALARIOS'!/g,'DADOS_SALARIOS!'),separadores(f.replace(/'DADOS_SALARIOS'!/g,'DADOS_SALARIOS!'))])];
const fontes=['apps-script/Salarios.gs','apps-script/Ficha.gs','apps-script/Pessoal.gs','apps-script/Configuracao.gs','r53/inicializacao/financeiro.gs','r53/inicializacao/progressao.gs'];
function gerar(){
 const c={},hash=s=>crypto.createHash('sha256').update(s).digest('hex');vm.createContext(c);
 const hashes={};for(const f of fontes){const raw=fs.readFileSync(path.join(root,f),'utf8');hashes[f]=hash(raw);vm.runInContext(raw,c);}
 const abas=[...c.ABAS,...c.VALORES_CUSTOM_,...c.ABAS_DA_CONFIGURACAO];
 function valor(aba,r,col){for(let i=abas.length-1;i>=0;i--){if(abas[i].nome!==aba)continue;const x=abas[i].vals.find(x=>x[0]===r&&x[1]===col);if(x)return x[2];}throw Error('campo público ausente '+aba);}
 const formulas=c.r53NovaFinFormulas_(),ops=c.r53NovaFinOperacoes_({getSheetByName:n=>({getMaxRows:()=>5000})});
 const fin={operacoes:JSON.parse(JSON.stringify(ops)),guardas:c.R53_NOVA_FIN_.formulas.map(([aba,faixa],i)=>({aba,faixa,formulas:formulas[i].map(l=>l.map(f=>variantes(f)))}))};
 const curva=Array.from({length:29},(_,i)=>{const formula=valor('DADOS',i+5,44);if(formula!=='=DADOS_CONFIG!$Z$'+(i+3))throw Error('curva mudou; rever adaptador');return {linha:i+5,nivel:i+2,formula,fonte:'Z'+(i+3)};});
 const missao=Array.from({length:4},(_,g)=>{const f=c.r53NovaProgFormulaMissao_('{linha}',g);return {coluna:[53,59,65,71][g],formulas:variantes(f)};});
 for(let r=15;r<=87;r++)for(let g=0;g<4;g++){const formula=c.r53NovaProgFormulaMissao_(r,g);if(formula!==valor('FICHA PESSOAL',r,[53,59,65,71][g])||formula!==missao[g].formulas[0].replace(/\{linha\}/g,String(r)))throw Error('missão fora da fonte');}
 if(c.R53_NOVA_PROG_.regra!==valor('CONFIGURAÇÃO',46,7)||c.R53_NOVA_PROG_.xp!==valor('DADOS',47,104))throw Error('regra fora da fonte');
 const custos=Array.from({length:29},(_,i)=>({nivel:i+1,linha:i+65,livro:valor('CONFIGURAÇÃO',i+65,5),formulas:variantes(valor('CONFIGURAÇÃO',i+65,7))}));
 const prog={piso:{base:0,prefixo:"—",minimo:1,maximo:30},missoes_linhas:[15,87],custos,regra:[c.R53_NOVA_PROG_.regra,c.R53_NOVA_PROG_.regra.replace(/,/g,';')],xp:c.R53_NOVA_PROG_.xp,curva,missoes:missao,rotulos:[{aba:'CONFIGURAÇÃO',celula:'C46',valor:valor('CONFIGURAÇÃO',46,3)},{aba:'DADOS',celula:'CY47',valor:valor('DADOS',47,103)},{aba:'DADOS',celula:'CY54',valor:valor('DADOS',54,103)}]};
 return {protocolo:'carteira-contrato-rest-1',fontes:hashes,financeiro:fin,progressao:prog,criacaoDisponivel:false,conferenciaConjuntaConcluida:false,consistenciaTemporalVerificada:false,imagensAtuaisConferidas:false};
}
function texto(){return JSON.stringify(gerar(),null,2)+'\n';}
const destino=path.join(__dirname,'contrato_rest.json');
if(require.main===module){const out=texto();if(process.argv.includes('--conferir')){if(fs.readFileSync(destino,'utf8')!==out)throw Error('contrato REST desatualizado; revisar antes de regenerar');console.log('Contrato REST igual às fontes públicas; criação bloqueada.');}else fs.writeFileSync(destino,out);}
module.exports={gerar,texto};
