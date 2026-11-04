'use strict';
// O contrato vem dos fontes públicos; o oráculo da curva não usa o inicializador.
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {texto,gerar}=require('../inicializacao/gerar_contrato_rest');
const {preparado,seedProgressao}=require('./inicializacao_sequencia');
const {curvaInicial,custosLivro}=require('./curva_inicial');
let casos=0;function caso(n,fn){try{fn();casos++;}catch(e){e.message=n+': '+e.message;throw e;}}
function cenario(nivel=10,custos=custosLivro){const a=preparado({perfisReais:true});seedProgressao(a);a.put('CONFIGURAÇÃO','F46',nivel);a.put('CONFIGURAÇÃO','G46',nivel,a.ctx.R53_NOVA_PROG_.regra);const curva=curvaInicial(nivel,custos);for(let i=0;i<29;i++)a.put('DADOS','AR'+(i+5),curva[i],'=DADOS_CONFIG!$Z$'+(i+3));return a;}
caso('artefato gerado igual às fontes, sem execução nativa ou liberação',()=>{assert.equal(texto(),fs.readFileSync(path.resolve(__dirname,'../inicializacao/contrato_rest.json'),'utf8'));const c=gerar();assert.equal(Object.keys(c.fontes).length,6);assert.equal(c.protocolo,'carteira-contrato-rest-1');for(const k of ['criacaoDisponivel','conferenciaConjuntaConcluida','consistenciaTemporalVerificada','imagensAtuaisConferidas'])assert.equal(c[k],false);assert.equal(c.progressao.custos.length,29);assert.equal(c.progressao.missoes.length,4);assert.equal(c.financeiro.guardas.length,7);});
for(let nivel=1;nivel<=30;nivel++)caso('nível '+nivel+' com piso, prefixo e custo explícito 1→2',()=>{const a=cenario(nivel,[0,...custosLivro.slice(1)]);const d=a.ctx.r53NovaProgDados_(a.ss);assert.equal(d.nivel,nivel);assert.equal(d.base,0);assert.equal(a.writes.length,0);});
caso('curva nativa de nível 10 reproduzida e aceita',()=>{const valores=['—','—','—','—','—','—','—','—',0,700,1600,2500,3400,4500,5600,6700,8000,9300,10600,12100,13600,15100,16800,18500,20200,21900,23600,25300,27000];assert.deepEqual(curvaInicial(10),valores);const a=cenario();assert.equal(a.ctx.r53NovaProgDados_(a.ss).base,0);});
caso('custo 10→11 custom 2100 mantém base zero e futuro custom',()=>{const custos=custosLivro.slice();custos[9]=2100;assert.deepEqual(curvaInicial(10,custos).slice(8,11),[0,2100,3000]);const a=cenario(10,custos);assert.equal(a.ctx.r53NovaProgDados_(a.ss).base,0);});
caso('nível 1 sem custo 1→2 continua pendente, não inventa zero',()=>{const a=cenario(1);assert.throws(()=>a.ctx.r53NovaProgDados_(a.ss),/curva/);});
for(const v of [0,'-',null,'Pendente',false,''])caso('prefixo abaixo do piso não aceita outro valor '+String(v),()=>{const a=cenario();a.put('DADOS','AR5',v,'=DADOS_CONFIG!$Z$3');assert.throws(()=>a.ctx.r53NovaProgDados_(a.ss),/curva/);});
for(const v of [3700,'—',-1,'Pendente',false])caso('piso não aceita base herdada ou inválida '+String(v),()=>{const a=cenario();a.put('DADOS','AR13',v,'=DADOS_CONFIG!$Z$11');assert.throws(()=>a.ctx.r53NovaProgDados_(a.ss),/curva/);});
caso('queda futura e fórmulas adulteradas continuam recusadas',()=>{const a=cenario();a.put('DADOS','AR15',1,'=DADOS_CONFIG!$Z$13');assert.throws(()=>a.ctx.r53NovaProgDados_(a.ss),/curva/);const b=cenario();b.put('DADOS','AR5','—','=0');assert.throws(()=>b.ctx.r53NovaProgDados_(b.ss),/curva/);});
caso('diário de base anterior não é adotado nem reescrito depois da correção',()=>{
 const a=cenario();a.complete(a.preview());const dados=a.ctx.r53NovaProgDados_;
 a.ctx.r53NovaProgDados_=ss=>({...dados(ss),base:3700});const p=a.ctx.r53NovaFichaProgressaoPrevia(a.ss,a.context);
 for(let i=0;i<10;i++){if(a.ctx.r53NovaFichaProgressaoAplicar(a.ss,a.context,p.assinatura).concluido)break;}
 const raw=a.doc.get(a.ctx.R53_NOVA_PROG_.diario),w=a.writes.length;a.ctx.r53NovaProgDados_=dados;
 assert.throws(()=>a.ctx.r53NovaFichaProgressaoAplicar(a.ss,a.context,p.assinatura),/estrutura, fórmula ou configuração mudou/);
 assert.equal(a.writes.length,w);assert.equal(a.doc.get(a.ctx.R53_NOVA_PROG_.diario),raw);assert.equal(a.range('DADOS','CZ54').getValue(),3700);
});
console.log(`${casos} cenários offline de contrato REST/piso de XP aprovados; não é instalação ou execução nativa do inicializador.`);
