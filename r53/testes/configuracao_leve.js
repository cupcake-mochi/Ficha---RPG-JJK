'use strict';
// Etapa 5 da versão rápida (26/11/2026): a CONFIGURAÇÃO sem Melhorias, Restrições e Formas custom, e as entidades em
// lista simples. Confere no modelo gerado (apps-script/*.gs):
//  - as seções 06, 07 e 09 vazias (só o título e a nota), sem fórmula, menu ou caixinha;
//  - nenhuma fórmula ou menu, em aba nenhuma, lendo essas seções;
//  - o catálogo por dono (DADOS_MELHORIAS, colunas 40 a 63) fora, e as linhas custom de Formas em branco;
//  - as entidades em lista simples: sem BASE DO LIVRO, MESTRE VIU nem aviso; a DADOS_ENTIDADES lê só os campos que ficam;
//  - as chaves da ANALISE dessas seções no mesmo lugar, em branco.
// Uso: node r53/testes/configuracao_leve.js (da raiz do repositório).
const vm = require('vm'), fs = require('fs'), assert = require('assert');
let checks = 0;
function ok(v, m) { assert(v, m); checks++; }
// Os arrays vêm do contexto do vm (outro protótipo): compara pelo JSON.
const j = x => JSON.parse(JSON.stringify(x));
function eq(a, b, m) { assert.deepStrictEqual(j(a), j(b), m); checks++; }

const ctx = {};
vm.runInNewContext(require(process.cwd() + '/medidas/carregar-ficha').fontes(), ctx);
const abas = new Map(ctx.ABAS.map(a => [a.nome, a]));
const aba = n => { const a = abas.get(n); assert(a, 'aba ausente: ' + n); return a; };
const col = s => [...s].reduce((n, ch) => n * 26 + ch.charCodeAt(0) - 64, 0);
const formula = v => typeof v === 'string' && v.startsWith('=');
const cap = JSON.parse(fs.readFileSync('conteudos-b47/comum/contrato.json', 'utf8')).capacidades;

// Faixas de coluna da CONFIGURAÇÃO horizontal (17 colunas por seção; a 01 começa na 18).
const PASSO = 17, faixa = n => [18 + PASSO * (n - 1), 18 + PASSO * n - 1];
const SAIRAM = { 6: 'MELHORIAS', 7: 'RESTRIÇÕES', 9: 'FORMAS' }, ENTIDADES = { 12: 'TIPOS DE ENTIDADE', 13: 'TALENTOS DE ENTIDADE' };
const naFaixa = (c, n) => { const [a, b] = faixa(n); return c >= a && c <= b; };
const cfg = aba('CONFIGURAÇÃO');
const inicioDv = d => col(/^([A-Z]+)/.exec(d[0])[1]);

// 1. As seções que saíram: título + nota, nada mais.
for (const [n, nome] of Object.entries(SAIRAM)) {
  const vals = cfg.vals.filter(v => naFaixa(v[1], +n) && v[2] !== null && v[2] !== '');
  ok(vals.some(v => String(v[2]).includes(nome)), `seção ${n} sem o título ${nome}`);
  ok(vals.some(v => String(v[2]).startsWith('Saiu na versão rápida')), `seção ${n} sem a nota "Saiu na versão rápida"`);
  eq(vals.filter(v => formula(v[2])).map(v => v.slice(0, 2)), [], `seção ${n} ainda tem fórmula`);
  eq(vals.filter(v => typeof v[2] === 'boolean').map(v => v.slice(0, 2)), [], `seção ${n} ainda tem caixinha`);
  eq((cfg.dv || []).filter(d => naFaixa(inicioDv(d), +n)), [], `seção ${n} ainda tem menu`);
}

// 2. Ninguém lê as seções que saíram (fórmulas e menus de todas as abas).
const leituras = [];
for (const a of ctx.ABAS) {
  const textos = [...a.vals.filter(v => formula(v[2])).map(v => [v[0] + ',' + v[1], v[2]]), ...(a.dv || []).map(d => [d[0], String(d[1])])];
  for (const [onde, f] of textos)
    for (const m of f.matchAll(/'?CONFIGURAÇÃO'?!\$?([A-Z]{1,3})\$?\d+/g)) leituras.push([a.nome, onde, col(m[1])]);
}
for (const n of Object.keys(SAIRAM))
  eq(leituras.filter(x => naFaixa(x[2], +n)).map(x => x[0] + '!' + x[1]), [], `alguém ainda lê a seção ${n}`);

// 3. Abas de dados: o catálogo por dono saiu; nenhuma lê a CONFIGURAÇÃO.
const mel = aba('DADOS_MELHORIAS');
eq(mel.vals.filter(v => v[0] >= 2 && v[1] >= 40 && v[1] <= 63 && v[2] !== null && v[2] !== '').length, 0,
  'DADOS_MELHORIAS ainda tem o catálogo por dono (colunas 40 a 63)');
for (const n of ['DADOS_MELHORIAS', 'DADOS_RESTRICOES', 'DADOS_FORMAS'])
  eq(aba(n).vals.filter(v => formula(v[2]) && v[2].includes('CONFIGURA')).length, 0, n + ' ainda lê a CONFIGURAÇÃO');

// 4. Formas: os menus de Forma só trazem o livro (as linhas custom das tabelas-ponte ficam em branco).
const df = aba('DADOS_FORMAS'), cabeca = t => { const v = df.vals.find(x => x[0] === 1 && x[2] === t); assert(v, 'sem ' + t); return v[1]; };
const cNome = cabeca('nome');
const livro = df.vals.filter(v => v[1] === cNome && v[0] >= 2 && typeof v[2] === 'string' && v[2] !== '' && !formula(v[2])).length;
ok(livro >= 5, 'poucas Formas do livro na DADOS_FORMAS: ' + livro);
for (const t of ['formas_personagem.0', 'formas_entidade.0', 'menu_entidade_0.0']) {
  // A fórmula da 1ª linha desce pelo `abaixo` ([linha1, col1, linha2, col2]): ela tem de parar no fim do livro.
  const c = cabeca(t), linhas = df.vals.filter(v => v[1] === c && v[0] >= 2 && v[2] !== null && v[2] !== '').map(v => v[0]);
  const desce = (df.abaixo || []).filter(x => x[1] <= c && c <= x[3]).map(x => x[2]);
  eq(Math.max(...linhas, ...desce), livro + 1, `${t}: linha custom preenchida (o livro vai até a ${livro + 1})`);
  ok(linhas.includes(2), `${t}: a 1ª linha do livro não está lá`);
}

// 5. Entidades em lista simples.
for (const [n, nome] of Object.entries(ENTIDADES)) {
  const vals = cfg.vals.filter(v => naFaixa(v[1], +n) && v[2] !== null && v[2] !== '');
  ok(vals.some(v => String(v[2]).includes(nome)), `seção ${n} sem o título`);
  for (const sai of ['BASE DO LIVRO', 'MESTRE VIU', 'DEFINIÇÃO', 'REQUISITOS'])
    eq(vals.filter(v => v[2] === sai).length, 0, `seção ${n} ainda tem ${sai}`);
  eq(vals.filter(v => typeof v[2] === 'boolean').length, 0, `seção ${n} ainda tem caixinha`);
  eq(vals.filter(v => formula(v[2])).length, 0, `seção ${n} ainda tem fórmula (o aviso saiu)`);
}
const lidas = n => new Set(leituras.filter(x => x[0] === 'DADOS_ENTIDADES' && naFaixa(x[2], n)).map(x => x[0] + x[1]));
eq(lidas(12).size, cap.tipo_entidade * 5, 'DADOS_ENTIDADES lê mais (ou menos) que nome, vida, talismã, reserva e descrição');
eq(lidas(13).size, cap.talento_entidade * 3, 'DADOS_ENTIDADES lê mais (ou menos) que nome, categoria e efeito');
const fora = leituras.filter(x => (naFaixa(x[2], 12) || naFaixa(x[2], 13)) && !['DADOS_ENTIDADES', 'ANALISE'].includes(x[0]));
eq(fora.map(x => x[0] + '!' + x[1]), [], 'outra aba lê os cadastros de entidade');
const menus = n => (cfg.dv || []).filter(d => naFaixa(inicioDv(d), n)).length;
eq(menus(12), cap.tipo_entidade * 3, 'tipo de entidade: menus de vida, talismã e reserva');
eq(menus(13), cap.talento_entidade, 'talento de entidade: só o menu da categoria');

// 6. ANALISE: as chaves no mesmo lugar, em branco.
// As linhas das entidades moram num complemento à parte (CONTRATO_ENTIDADES_, no EntidadesAnalise.gs): junta todos.
const anVals = [...aba('ANALISE').vals];
for (const k of Object.getOwnPropertyNames(ctx)) {
  const x = ctx[k];
  if (x !== ctx.ABAS && Array.isArray(x)) for (const a of x) if (a && a.nome === 'ANALISE' && Array.isArray(a.vals)) anVals.push(...a.vals);
}
const an = { vals: anVals }, valor = new Map(an.vals.filter(v => v[1] === 2).map(v => [v[0], v[2]]));
const chaves = an.vals.filter(v => v[1] === 1 && typeof v[2] === 'string').map(v => [v[0], v[2]]);
const vazia = r => { const v = valor.get(r); return v === undefined || v === null || v === ''; };
const brancas = /^(custom\.(melhoria|restricao|forma)\.|aviso\.custom\.(melhoria|restricao|forma|tipo_entidade|talento_entidade)\.|custom\.tipo_entidade\.\d+\.(base|mestre_viu|definicao)$|custom\.talento_entidade\.\d+\.(base|mestre_viu|requisitos)$)/;
const alvo = chaves.filter(([, k]) => brancas.test(k));
ok(alvo.length > 500, 'poucas chaves das seções que saíram: ' + alvo.length);
eq(alvo.filter(([r]) => !vazia(r)).map(([, k]) => k), [], 'chave da ANALISE que devia estar em branco');
for (const k of ['custom.melhoria.30.nome', 'custom.restricao.30.nome', 'custom.forma.10.nome', 'aviso.custom.tipo_entidade.' + cap.tipo_entidade])
  ok(chaves.some(([, x]) => x === k), 'a chave sumiu (devia ficar, em branco): ' + k);
for (const k of ['custom.tipo_entidade.1.nome', 'custom.tipo_entidade.1.vida', 'custom.tipo_entidade.1.efeito',
  'custom.talento_entidade.1.nome', 'custom.talento_entidade.1.categoria', 'custom.talento_entidade.1.efeito']) {
  const r = chaves.find(([, x]) => x === k);
  ok(r && formula(valor.get(r[0])) && valor.get(r[0]).includes('CONFIGURA'), 'a chave que fica não lê a CONFIGURAÇÃO: ' + k);
}

console.log(`configuracao_leve: ${checks} conferências ok`);
