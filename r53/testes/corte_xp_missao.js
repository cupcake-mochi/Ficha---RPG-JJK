'use strict';
// Corte do XP da missão abaixo de 25 (12/11/2026, regra da casa). Ver
// r53/diagnostico-android/CORRECAO-CORTE-XP-25-2026-11-12.md.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { execFileSync } = require('node:child_process');
const { ler, expandir } = require('./expansao_domada_modelo');
const P = require('../diagnostico-android/preparar_corte_xp_missao');
const delta = require('../diagnostico-android/corte_xp_missao_delta.json');
let checks = 0;
const ok = (c, m) => { assert.ok(c, m); checks++; };
const eq = (a, b, m) => { assert.deepEqual(a, b, m); checks++; };

// O catálogo é o dono do número.
const CAT = JSON.parse(fs.readFileSync('catalogo-projeto-m.json', 'utf8'));
eq(CAT.fora_do_livro.xp_minimo_da_missao, P.CORTE);

// 1. As três casas da fórmula: o gerador (Pessoal.gs), o json dos moldes e o Salarios.gs dizem a mesma coisa.
const abas = ler('apps-script');
const pessoal = expandir(abas.find(a => a.nome === 'FICHA PESSOAL'));
const moldes = JSON.parse(fs.readFileSync('salarios/missoes_moldes.json', 'utf8'));
eq(moldes.length, P.MOLDES);
for (const [r, c, f] of moldes) eq(pessoal.get(r + ':' + c), f, 'molde e gerador divergem em ' + r + ',' + c);
const sal = fs.readFileSync('apps-script/Salarios.gs', 'utf8');
eq(JSON.parse(/var SALARIO_MISSOES_MOLDES_=(\[[^\n]+\]);\n/.exec(sal)[1]), moldes, 'Salarios.gs e json divergem');
ok(!/MAX\(1,FLOOR/.test(sal) && !/MAX\(1,FLOOR/.test(fs.readFileSync('apps-script/Pessoal.gs', 'utf8')), 'sobrou o mínimo de 1');

// 2. A troca de texto: ida e volta exatas, recusa repetir e recusa contagem errada.
const antigo = P.preparar(sal, true);
eq(P.preparar(antigo), sal);
assert.throws(() => P.preparar(sal), /0 de 292 no formato antigo/); checks++;
assert.throws(() => P.preparar(antigo.replace('MAX(1,FLOOR(', 'MAX(2,FLOOR(')), /291 de 292/); checks++;

// 3. A regra, calculada pela própria fórmula do modelo contra as tabelas da DADOS.
const dados = expandir(abas.find(a => a.nome === 'DADOS'));
const tabela = (c1, l1, l2) => { const m = new Map(); for (let l = l1; l <= l2; l++) if (dados.get(l + ':' + c1) != null) m.set(dados.get(l + ':' + c1), dados.get(l + ':' + (c1 + 1))); return m; };
const TIPO = tabela(90, 5, 10), MULT = tabela(93, 5, 7), DESC = tabela(96, 5, 15);
eq([...DESC.keys()], ['3ª · 50%', '4ª · 25%', '5ª · 12,5%', '6ª · 6,25%', '7ª ou mais', 'Falha · metade',
  '3ª · 50% · falha', '4ª · 25% · falha', '5ª · 12,5% · falha', '6ª · 6,25% · falha'], 'o menu de 10 linhas');
eq([dados.get('15:96'), dados.get('15:97')], [undefined, undefined], 'a 11ª linha da faixa fica vazia');
const f = pessoal.get('15:53');
ok(f.includes('DADOS!$CR$5:$CS$15') && f.includes('FLOOR(ROUND(') && f.includes(',1)>=25,FLOOR('), 'a fórmula usa a faixa de sempre e o corte');
const xp = (tipo, adic, desc) => {
  const v = Math.round(TIPO.get(tipo) * (adic ? MULT.get(adic) : 1) * (desc ? DESC.get(desc) : 1) * 1e4) / 1e4;
  return Math.floor(v) >= P.CORTE ? Math.floor(v) : 0;          // o que a fórmula faz: IF(FLOOR(v,1)>=25,FLOOR(v,1),0)
};
eq(xp('Curta', '', '4ª · 25%'), 0, 'Curta na 4ª: 12,5 → 0');
eq(xp('Padrão', '', '4ª · 25%'), 25, 'Padrão na 4ª: exatamente 25 paga');
eq(xp('Final de arco', '2x', '7ª ou mais'), 0, '7ª ou mais dá 0, até no Final de arco 2x');
eq(xp('Final de arco', '2x', '6ª · 6,25%'), 37, 'a 6ª ainda paga na maior missão');
eq(xp('Final de arco', '2x', '6ª · 6,25% · falha'), 0, 'a 6ª com falha não chega a 25');
eq(xp('Longa', '', '3ª · 50% · falha'), 50, 'o exemplo do livro segue: 200 × ½ × ½ = 50');
eq(xp('Curta', '', ''), 50);

// 4. A camada: o plano bate com o modelo, a reversão é atômica e volta ao antes.
const n = a => delta.filter(d => d.aba === a && !d.addr).length;
eq([n('FICHA PESSOAL'), n('DADOS'), delta.filter(d => d.addr).length], [292, 4, 8]);
for (const d of delta) eq(P.explicar(d.aba, d.addr || d.r + ':' + d.c, d.antes), d.depois, 'fora do molde: ' + JSON.stringify(d).slice(0, 80));
const errado = structuredClone(abas);
errado.find(a => a.nome === 'DADOS').vals.find(v => v[0] === 9 && v[1] === 96)[2] = 'mexido';
const copia = JSON.stringify(errado);
assert.throws(() => P.reverterModelo(errado), /Corte do XP divergente/); checks++;
eq(JSON.stringify(errado), copia, 'reversão parcial');
P.reverterModelo(abas);
const volta = expandir(abas.find(a => a.nome === 'FICHA PESSOAL'));
for (const d of delta.filter(d => d.aba === 'FICHA PESSOAL' && !d.addr)) eq(volta.get(d.r + ':' + d.c), d.antes);
eq(expandir(abas.find(a => a.nome === 'DADOS')).get('15:96'), '7ª · 3,125% · falha');
eq(new Map(abas.find(a => a.nome === 'FICHA PESSOAL').notas).get('BA14').includes('a missão paga 1'), true);
assert.throws(() => P.reverterModelo(abas), /Corte do XP divergente/); checks++;

// 5. O menu do gerador Python, direto do catálogo.
const py = execFileSync(process.env.PYTHON || 'python3', ['-c', `
import sys, json; sys.path.insert(0, 'ficha-v01')
import ficha_pessoal as fp
R = fp.regras()
print(json.dumps([R['xp_minimo'], R['descontos']], ensure_ascii=False))`], { encoding: 'utf8' });
const [minimo, menu] = JSON.parse(py);
eq(minimo, 25); eq(menu.length, 10); eq(menu[4], ['7ª ou mais', 0]);

// 6. O trecho do console: parseia e troca os 292 moldes num editor de mentira.
const mk = r => new (Object.getPrototypeOf(async function () {}).constructor)('monaco', 'crypto', 'window', 'return ' + P.trecho(r));
mk(true); checks++;
let gravado = null; const win = {};
const instalado = '// cabeçalho\nfunction r53Modulo_(){}\n' + antigo + '\nfunction outra_(){}\n';
const modelo = { getValue: () => gravado === null ? instalado : gravado, setValue: v => { gravado = v; } };
const outro = { getValue: () => '// outro arquivo', setValue: () => { throw Error('não devia gravar'); } };
mk(false)({ editor: { getModels: () => [outro, modelo] } }, require('node:crypto').webcrypto, win).then(res => {
  ok(!String(res).startsWith('ERRO'), res);
  eq(gravado, '// cabeçalho\nfunction r53Modulo_(){}\n' + sal + '\nfunction outra_(){}\n');
  eq(win.__corteXpAntes, instalado);
  console.log(JSON.stringify({ checks, resultado: 'OK', escopo: 'corte do XP da missão abaixo de 25' }));
}).catch(e => { console.error(e); process.exit(1); });
