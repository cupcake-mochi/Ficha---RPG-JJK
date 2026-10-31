'use strict';
// Usa o leitor/executor reais e serviços simulados. Não avalia fórmulas do Google.
const assert = require('node:assert/strict'), fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const {ambiente} = require('./apoio_inicializacao');
const {curvaInicial,custosLivro} = require('./curva_inicial');
const raiz = path.resolve(__dirname, '../..');
const fonte = fs.readFileSync(path.join(raiz, 'r53/inicializacao/progressao.gs'), 'utf8');
const gerado = {}; vm.createContext(gerado);
vm.runInContext(fs.readFileSync(path.join(raiz, 'apps-script/Ficha.gs'), 'utf8'), gerado);
vm.runInContext(fs.readFileSync(path.join(raiz, 'apps-script/Pessoal.gs'), 'utf8'), gerado);
vm.runInContext(fs.readFileSync(path.join(raiz, 'apps-script/Configuracao.gs'), 'utf8'), gerado);
const dados = gerado.ABAS.find(a => a.nome === 'DADOS'), fp = gerado.VALORES_CUSTOM_.find(a => a.nome === 'FICHA PESSOAL');
const config = gerado.ABAS_DA_CONFIGURACAO.find(a => a.nome === 'CONFIGURAÇÃO');
const get = (s, r, c) => s.vals.find(v => v[0] === r && v[1] === c)[2];
let casos = 0;
function caso(nome, fn) { try { fn(); casos++; } catch (e) { e.message = nome + ': ' + e.message; throw e; } }
function preparado(op = {}) {
  const a = ambiente(); vm.runInContext(fonte, a.ctx);
  // Os valores de fábrica vêm de fonte gerada, não da função sob teste.
  const nivel = op.semOverride ? 2 : op.nivel ?? 10;
  // O cenário de nível 1 declara custo 1→2 zero: o livro deixa esse custo vazio.
  const custos = op.custos || [0,...custosLivro.slice(1)], curva = op.curva || curvaInicial(nivel,custos);
  a.put('CONFIGURAÇÃO', 'C46', get(config,46,3)); a.put('CONFIGURAÇÃO', 'E46', get(config,46,5));
  a.put('CONFIGURAÇÃO', 'F46', op.semOverride ? '' : nivel);
  a.put('CONFIGURAÇÃO', 'G46', op.semOverride ? 2 : nivel, get(config,46,7));
  a.put('DADOS', 'CY54', get(dados,54,103)); a.put('DADOS', 'CZ54', 987654);
  a.put('DADOS', 'CY47', get(dados,47,103)); a.put('DADOS', 'CZ47', 999999, get(dados,47,104));
  a.put('FICHA', 'AH11', 29);
  for (let i=0; i<29; i++) {
    a.put('DADOS', 'AQ'+(i+5), get(dados,i+5,43));
    a.put('DADOS', 'AR'+(i+5), curva[i], get(dados,i+5,44));
  }
  for (const x of fp.vals) if(x[0]>=15 && x[0]<=87 && [53,59,65,71].includes(x[1])) {
    const col={53:'BA',59:'BG',65:'BM',71:'BS'}[x[1]];a.put('FICHA PESSOAL',col+x[0],'',x[2]);
  }
  if (!op.semFinanceiro) a.complete(a.preview());
  a.writes.length=0;
  a.progPreview = () => a.ctx.r53NovaFichaProgressaoPrevia(a.ss,a.context);
  a.progApply = p => a.ctx.r53NovaFichaProgressaoAplicar(a.ss,a.context,p.assinatura);
  a.progComplete = p => { for(let i=0;i<10;i++){const r=a.progApply(p);if(r.concluido)return r;assert.equal(r.retomar,true);}throw Error('retomadas excedidas'); };
  return a;
}
function verificar(a,n,base) {
  assert.equal(a.range('FICHA','AH11').getValue(),n);assert.equal(a.range('DADOS','CZ54').getValue(),base);
  assert.equal(a.range('DADOS','CZ47').getFormulas()[0][0],get(dados,47,104));
  assert.equal(a.range('FICHA','AN11').getFormulas()[0][0],'=DADOS!$CZ$47');
  assert.equal(a.range('CONFIGURAÇÃO','AK51').getValue(),'habilidade custom da mesa');
  assert.equal(a.range('CONFIGURAÇÃO','G46').getFormulas()[0][0],get(config,46,7));
  for(const c of a.cells.values()){assert.equal(c.fmt,'tema');assert.equal(c.dv,'menu');}
  for(const [tipo,target] of a.writes) if(tipo!=='propriedade')assert(['FICHA!AH11','DADOS!CZ54'].includes(target),target);
  assert(!a.locked()); assert.equal(JSON.parse(a.doc.get(a.ctx.R53_NOVA_PROG_.diario)).concluido,true);
}
caso('contrato bate com as 292 fórmulas de missão e o XP gerados',()=>{
  const a=preparado();assert.equal(a.ctx.R53_NOVA_PROG_.xp,get(dados,47,104));assert.equal(a.ctx.R53_NOVA_PROG_.regra,get(config,46,7));
  let n=0;for(const x of fp.vals)if(x[0]>=15&&x[0]<=87&&[53,59,65,71].includes(x[1])){assert.equal(a.ctx.r53NovaProgFormulaMissao_(x[0],[53,59,65,71].indexOf(x[1])),x[2]);n++;}assert.equal(n,292);
});
for(let nivel=1;nivel<=30;nivel++)caso('início do nível '+nivel,()=>{
  const a=preparado({nivel});const p=a.progPreview();assert.equal(a.writes.length,0);
  const r=a.progComplete(p);assert.equal(r.criacaoDisponivel,false);assert(r.pendente.includes('marcos_e_recursos'));
  verificar(a,nivel,0);
  const writes=a.writes.length;a.progApply(p);assert.equal(a.writes.length,writes,'repetir sem gravar');
});
caso('campanha em branco usa o nível 2 do livro',()=>{const a=preparado({semOverride:true});a.progComplete(a.progPreview());verificar(a,2,0);});
caso('curva custom da campanha não é trocada pela do livro',()=>{const a=preparado({nivel:10,custos:[0,...custosLivro.slice(1)].map(x=>x*3)});a.progComplete(a.progPreview());verificar(a,10,0);assert.equal(a.range('DADOS','AR14').getValue(),2100);});
caso('curva de custo zero é válida',()=>{const a=preparado({nivel:30,custos:custosLivro.map(()=>0)});a.progComplete(a.progPreview());verificar(a,30,0);});
for(const nivel of [0,31,-1,2.5,'10',true,Infinity,NaN])caso('nível inválido '+String(nivel),()=>{const a=preparado();a.put('CONFIGURAÇÃO','F46',nivel);a.put('CONFIGURAÇÃO','G46',nivel,get(config,46,7));assert.throws(()=>a.progPreview(),/nível inicial inválido/);assert.equal(a.writes.length,0);});
for(const [s,addr,v,f]of [
 ['DADOS','CY54','outro',''],['DADOS','CZ47',0,'=0'],['FICHA','AN11',0,'=0'],
 ['CONFIGURAÇÃO','G46',10,'=10'],['DADOS','AR5',0,'=0'],['DADOS','AQ5',1,''],
 ['DADOS','AR6',-1,'=DADOS_CONFIG!$Z$4'],['DADOS','AR6','', '=DADOS_CONFIG!$Z$4'],
 ['CONFIGURAÇÃO','G46',9, get(config,46,7)],['DADOS','CZ54',5,'=5']
])caso('recusa contrato inválido '+s+'!'+addr,()=>{const a=preparado();a.put(s,addr,v,f);assert.throws(()=>a.progPreview());assert.equal(a.writes.length,0);});
caso('curva decrescente',()=>{const a=preparado();a.put('DADOS','AR15',1,'=DADOS_CONFIG!$Z$13');assert.throws(()=>a.progPreview(),/curva/);assert.equal(a.writes.length,0);});
caso('financeiro incompleto',()=>{const a=preparado({semFinanceiro:true});assert.throws(()=>a.progPreview(),/financeiro.*concluído/);assert.equal(a.writes.length,0);});
caso('financeiro de outra operação',()=>{const a=preparado();a.context.operacao='outra_operacao_00002';assert.throws(()=>a.progPreview(),/financeiro.*concluído/);assert.equal(a.writes.length,0);});
for(const x of [['AW15','missão','', ''],['BR87',5,'',''],['AX20','','','[Salário: antigo]'],['BA18',250,'',''],['BS87',0,'=0','']])
 caso('missão residual '+x[0],()=>{const a=preparado();a.put('FICHA PESSOAL',...x);assert.throws(()=>a.progPreview(),/missões|total de missão/);assert.equal(a.writes.length,0);});
caso('fórmulas de missão normalizadas para separador do Sheets',()=>{
 const a=preparado();for(const [k,c]of a.cells)if(k.startsWith('FICHA PESSOAL!')&&c.f.includes('VLOOKUP'))c.f=c.f.replace(/,/g,';');
 a.progComplete(a.progPreview());verificar(a,10,0);
});
caso('regra de nível com separador nativo pt-BR',()=>{
 const a=preparado();a.put('CONFIGURAÇÃO','G46',10,get(config,46,7).replace(/,/g,';'));
 a.progComplete(a.progPreview());assert.equal(a.range('FICHA','AH11').getValue(),10);
 assert.equal(a.range('DADOS','CZ54').getValue(),0);
 assert.equal(a.range('CONFIGURAÇÃO','G46').getFormulas()[0][0],get(config,46,7).replace(/,/g,';'));
});
caso('separador nativo não libera alteração na regra de nível',()=>{
 const a=preparado();a.put('CONFIGURAÇÃO','G46',10,get(config,46,7).replace(/,/g,';').replace('F46<=30','F46<=31'));
 assert.throws(()=>a.progPreview(),/regra de nível inicial/);assert.equal(a.writes.length,0);
});
caso('mudança de regra depois da prévia não escreve',()=>{const a=preparado(),p=a.progPreview();a.put('CONFIGURAÇÃO','F46',5);a.put('CONFIGURAÇÃO','G46',5,get(config,46,7));for(let i=0;i<29;i++)a.put('DADOS','AR'+(i+5),curvaInicial(5)[i],'=DADOS_CONFIG!$Z$'+(i+3));assert.throws(()=>a.progApply(p),/mudou após/);assert.equal(a.writes.length,0);});
caso('mudança da curva depois da prévia não escreve',()=>{const a=preparado(),p=a.progPreview();a.put('DADOS','AR14',901,'=DADOS_CONFIG!$Z$12');assert.throws(()=>a.progApply(p),/mudou após/);assert.equal(a.writes.length,0);});
caso('assinatura financeira não serve para iniciar progressão',()=>{const a=preparado();const j=JSON.parse(a.doc.get(a.ctx.R53_NOVA_FIN_.diario));assert.throws(()=>a.progApply(j),/mudou após/);assert.equal(a.writes.length,0);});
const total=preparado();total.progComplete(total.progPreview());
for(let i=1;i<=total.writes.length;i++)for(const fase of ['antes','depois'])caso('queda '+fase+' escrita '+i,()=>{
 const a=preparado(),p=a.progPreview();let n=0;a.hook(f=>{if(f===fase&&++n===i)throw Error('queda');});
 assert.throws(()=>a.progApply(p),/queda/);assert(!a.locked());a.hook(null);a.progComplete(p);verificar(a,10,0);
});
caso('edição durante pausa não é apagada',()=>{const a=preparado(),p=a.progPreview();a.hook((f,t)=>{if(f==='depois'&&t==='valor')throw Error('queda');});assert.throws(()=>a.progApply(p),/queda/);a.hook(null);a.put('DADOS','CZ54',-55);const n=a.writes.length;assert.throws(()=>a.progApply(p),/editados/);assert.equal(a.writes.length,n);assert.equal(a.range('DADOS','CZ54').getValue(),-55);});
caso('concluído não volta a zerar XP usado depois',()=>{const a=preparado(),p=a.progPreview();a.progComplete(p);a.put('DADOS','CZ54',4000);const n=a.writes.length;assert.throws(()=>a.progApply(p),/editados|já foi usada/);assert.equal(a.writes.length,n);});
caso('progressão não libera reexecutar financeiro com o nível anterior',()=>{
 const a=preparado();a.progComplete(a.progPreview());const n=a.writes.length;
 const j=JSON.parse(a.doc.get(a.ctx.R53_NOVA_FIN_.diario));
 assert.throws(()=>a.apply(j),/estrutura, fórmula ou configuração mudou/);assert.equal(a.writes.length,n);
 assert.equal(a.range('FICHA','AH11').getValue(),10);assert.equal(a.range('DADOS','CZ54').getValue(),0);
});
caso('missão inserida depois invalida a repetição',()=>{const a=preparado(),p=a.progPreview();a.progComplete(p);a.put('FICHA PESSOAL','AW15','nova missão');const n=a.writes.length;assert.throws(()=>a.progApply(p),/missões/);assert.equal(a.writes.length,n);});
caso('limite de passos e retomada entre nível e base',()=>{const a=preparado(),p=a.progPreview();a.ctx.R53_NOVA_PROG_.escritasPorExecucao=1;const r=a.progApply(p);assert.equal(r.concluido,false);assert.equal(r.retomar,true);assert.equal(a.range('DADOS','CZ54').getValue(),987654);a.progComplete(p);verificar(a,10,0);});
caso('dados e notas pessoais não aparecem no diário',()=>{const a=preparado(),p=a.progPreview();a.progComplete(p);const j=a.doc.get(a.ctx.R53_NOVA_PROG_.diario);assert(!j.includes('987654'));assert(!j.includes('habilidade custom'));assert(Buffer.byteLength(j)<9000);});
caso('marcas novas de XP congelado saem no financeiro e não reajustam a base',()=>{
 const a=preparado({semFinanceiro:true});
 for(const c of ['AW','BC','BI','BO'])a.put('FICHA PESSOAL',c+'15','missão antiga','','Nota antiga\n[XP congelado: 3750 · id-antigo]\n[Salário: id-antigo · 2026-10-27]');
 a.complete(a.preview());
 const notas=a.range('FICHA PESSOAL','AW15:BT87').getNotes();
 const base=a.range('DADOS','CZ54').getValue();
 assert.equal(a.ctx.salarioXpCongelado_(a.ss,{notas,caixas:{},xpCaixas:{}}),false);
 assert.equal(a.range('DADOS','CZ54').getValue(),base);
 a.writes.length=0;a.progComplete(a.progPreview());verificar(a,10,0);
});
caso('marca de XP congelado reinserida depois do financeiro impede progressão',()=>{
 const a=preparado();a.put('FICHA PESSOAL','AW87','','','[XP congelado: 3750 · id-antigo]');
 assert.throws(()=>a.progPreview(),/missões não estão limpas/);assert.equal(a.writes.length,0);
});
console.log(`${casos} cenários offline de nível inicial/base XP aprovados; sem inicialização geral ou aceite nativo.`);
