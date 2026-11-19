'use strict';
// Corte do XP da missão abaixo de 25 (12/11/2026, regra da casa, fora do livro; o Mizuki aprovou: "pode por"). O livro
// dá no mínimo 1 XP à missão positiva; a ficha passa a dar 0 quando o XP final (tipo, adicional, falha e desconto da
// semana, arredondado para baixo) fica abaixo de 25. Exatamente 25 paga. Cada missão se olha sozinha.
//
// A fórmula do TOTAL de cada missão (FICHA PESSOAL, BA, BG, BM e BS, linhas 15 a 87: 292 caixas) mora em três lugares:
//   - no gerador (ficha-v01/ficha_pessoal.py), que escreve o apps-script/Pessoal.gs;
//   - no salarios/missoes_moldes.json, que o preparar_missoes.js põe no SALARIO_MISSOES_MOLDES_ do Salarios.gs (o
//     salário regrava o molde quando alguém apaga a fórmula);
//   - no SALARIO_MISSOES_MOLDES_ do Codigo instalado nas fichas.
// Os moldes nascem no primeiro passo da cadeia (preparar_missoes.js lê o json), então a cadeia que reproduz o
// Salarios.gs não ganha passo: o json e o Salarios.gs mudam juntos, pela mesma troca daqui. Este arquivo é a troca
// (`trocar`) e o trecho para o console do editor das QAs, que troca os 292 moldes do Codigo instalado.
//
//   node r53/diagnostico-android/preparar_corte_xp_missao.js            > trecho.js   (aplica)
//   node r53/diagnostico-android/preparar_corte_xp_missao.js --reverter > trecho.js   (desfaz)
//   node r53/diagnostico-android/preparar_corte_xp_missao.js <gs-antes> <gs-depois>   (refaz o corte_xp_missao_delta.json)
const vm = require('vm');
const CORTE = 25, MOLDES = 292;

/** Troca, num texto, cada fórmula do total da missão. Função pura, igual no node e no navegador. Recusa se não achar
 *  exatamente `n` fórmulas no formato de origem ou se sobrar alguma no formato antigo. */
function trocar(texto, reverter, corte, n) {
  const antigo = /IF\((ROUND\(VLOOKUP\([^\n]+?,4\))>0,MAX\(1,FLOOR\(\1,1\)\),0\)/g;
  const novo = new RegExp('IF\\(FLOOR\\((ROUND\\(VLOOKUP\\([^\\n]+?,4\\)),1\\)>=' + corte + ',FLOOR\\(\\1,1\\),0\\)', 'g');
  const de = reverter ? novo : antigo, para = reverter ? antigo : novo;
  let achou = 0;
  const out = texto.replace(de, (s, v) => { achou++; return reverter ? 'IF(' + v + '>0,MAX(1,FLOOR(' + v + ',1)),0)' : 'IF(FLOOR(' + v + ',1)>=' + corte + ',FLOOR(' + v + ',1),0)'; });
  if (achou !== n) throw new Error('Moldes do XP da missão: ' + achou + ' de ' + n + ' no formato ' + (reverter ? 'novo' : 'antigo'));
  para.lastIndex = 0;
  if ((out.match(para) || []).length !== n) throw new Error('Moldes do XP da missão: a troca não fechou em ' + n);
  return out;
}

/** O Salarios.gs (ou o json dos moldes) com o corte. */
function preparar(source, reverter = false) {
  const out = trocar(source, reverter, CORTE, MOLDES);
  if (/function /.test(out)) new vm.Script(out); else JSON.parse(out);
  return out;
}

function trecho(reverter = false) {
  return 'await (async () => { try {\n' +
    'const trocar = ' + trocar.toString() + ';\n' +
    'const sha = async t => [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(t)))].map(b => b.toString(16).padStart(2, "0")).join("");\n' +
    'const cod = monaco.editor.getModels().filter(m => m.getValue().indexOf("var SALARIO_MISSOES_MOLDES_=") >= 0);\n' +
    'if (cod.length !== 1) throw new Error("SALARIO_MISSOES_MOLDES_ encontrado em " + cod.length + " arquivo(s)");\n' +
    'const antes = cod[0].getValue(), novo = trocar(antes, ' + reverter + ', ' + CORTE + ', ' + MOLDES + ');\n' +
    'window.__corteXpAntes = antes;\n' +
    'cod[0].setValue(novo);\n' +
    'return JSON.stringify({ antes: (await sha(antes)).slice(0, 12), depois: (await sha(cod[0].getValue())).slice(0, 12), moldes: ' + MOLDES + ' });\n' +
    '} catch (err) { return "ERRO: " + err.message; } })()';
}

// ---- O modelo da ficha (gerador ficha-v01/ficha_pessoal.py): a camada para os comparadores e a instalação nas QAs.
// Mudam 292 fórmulas do TOTAL na FICHA PESSOAL, o menu de desconto na DADOS (a 7ª vira "7ª ou mais", com fração 0; a
// "7ª · 3,125% · falha" sai e a CR15:CS15 fica vazia, para a faixa CR5:CS15 não mudar) e as 8 notas dos cabeçalhos
// DESCONTO e TOTAL, que citavam o mínimo de 1 XP.
const CAMINHO = __dirname + '/corte_xp_missao_delta.json';
const TOTAIS = [53, 59, 65, 71];                       // BA, BG, BM e BS
const DADOS = {                                        // DADOS!CR (96) e CS (97)
  '9:96': ['7ª · 3,125%', '7ª ou mais'], '9:97': [0.03125, 0],
  '15:96': ['7ª · 3,125% · falha', null], '15:97': [0.015625, null],
};
const NOTAS = {
  desconto: ['a quinta 12,5%, a sexta 6,25%, e cada uma depois paga metade da anterior. Missão que falhou e o mestre deu metade é Falha; se ela também foi da terceira em diante, escolha a posição com falha (a terceira longa que falhou paga 200 × ½ × ½ = 50). Em branco, paga cheio.',
             'a quinta 12,5% e a sexta 6,25%. Da sétima em diante, escolha 7ª ou mais: nenhuma missão chega a 25 XP ali, e pela regra da casa ela paga 0. Missão que falhou e o mestre deu metade é Falha; se ela também foi da terceira em diante, escolha a posição com falha (a terceira longa que falhou paga 200 × ½ × ½ = 50). Em branco, paga cheio.'],
  total: ['Quando a conta dá mais que zero e menos que 1, a missão paga 1.', 'Regra da casa: abaixo de 25, a missão paga 0 (25 paga).'],
};
const NOTAS_EM = { AZ14: 'desconto', BF14: 'desconto', BL14: 'desconto', BR14: 'desconto', BA14: 'total', BG14: 'total', BM14: 'total', BS14: 'total' };

/** Depois = antes com a troca; nada mais muda. Devolve undefined para o que não é desta camada. */
function explicar(aba, pos, antes) {
  if (aba === 'FICHA PESSOAL') {
    if (NOTAS_EM[pos]) { const [a, b] = NOTAS[NOTAS_EM[pos]]; return typeof antes === 'string' && antes.split(a).length === 2 ? antes.replace(a, () => b) : undefined; }
    const [r, c] = pos.split(':').map(Number);
    if (!TOTAIS.includes(c) || r < 15 || r > 87 || typeof antes !== 'string') return undefined;
    try { return trocar(antes, false, CORTE, 1); } catch (e) { return undefined; }
  }
  if (aba === 'DADOS' && DADOS[pos] && DADOS[pos][0] === antes) return DADOS[pos][1];
  return undefined;
}

function comparar(base, atual) {
  const { expandir } = require('../testes/expansao_domada_modelo');
  const assert = require('node:assert/strict');
  assert.deepEqual(atual.map(a => a.nome), base.map(a => a.nome), 'Abas divergentes');
  const delta = [];
  let posicoes = 0;
  for (const [i, a] of base.entries()) {
    const b = atual[i];
    const estrutura = ({ vals, abaixo, geracao, notas, ...resto }) => resto;
    assert.deepEqual(estrutura(b), estrutura(a), 'Estrutura ' + a.nome);
    const na = new Map(a.notas || []), nb = new Map(b.notas || []);
    for (const k of new Set([...na.keys(), ...nb.keys()])) {
      if (na.get(k) === nb.get(k)) continue;
      assert.equal(explicar(a.nome, k, na.get(k)), nb.get(k), 'Nota fora do molde: ' + a.nome + '!' + k);
      delta.push({ aba: a.nome, addr: k, antes: na.get(k), depois: nb.get(k) });
    }
    const o = expandir(a), d = expandir(b);
    for (const pos of new Set([...o.keys(), ...d.keys()])) {
      posicoes++;
      if (o.get(pos) === d.get(pos)) continue;
      assert.equal(explicar(a.nome, pos, o.get(pos)), d.has(pos) ? d.get(pos) : null, 'Mudança fora do molde: ' + a.nome + '!' + pos);
      const [r, c] = pos.split(':').map(Number);
      const e = { aba: a.nome, r, c, antes: o.get(pos), depois: d.has(pos) ? d.get(pos) : null };
      if (!d.has(pos)) e.estilo = a.vals.find(v => v[0] === r && v[1] === c)[3];
      delta.push(e);
    }
  }
  const n = aba => delta.filter(d => d.aba === aba && !d.addr).length;
  assert.deepEqual([n('FICHA PESSOAL'), n('DADOS'), delta.filter(d => d.addr).length], [MOLDES, 4, 8], 'Esperadas 292 fórmulas, 4 caixas do menu e 8 notas');
  return { delta, abas: base.length, posicoes };
}

// Comparadores históricos: devolve o modelo ao estado anterior. Atômico: confere tudo antes de gravar.
function reverterModelo(abas, delta = require(CAMINHO)) {
  const { expandir } = require('../testes/expansao_domada_modelo');
  const copias = {};
  for (const nome of new Set(delta.map(d => d.aba))) {
    const aba = abas.find(a => a.nome === nome);
    if (!aba) throw Error('Corte do XP: aba ' + nome + ' ausente');
    const antes = expandir(aba), notas = new Map(aba.notas || []);
    const meu = delta.filter(d => d.aba === nome);
    for (const d of meu) {
      const atual = d.addr ? notas.get(d.addr) : (antes.has(d.r + ':' + d.c) ? antes.get(d.r + ':' + d.c) : null);
      if (atual !== d.depois) throw Error('Corte do XP divergente: ' + nome + '!' + (d.addr || d.r + ',' + d.c));
    }
    const copia = structuredClone(aba);
    for (const d of meu) {
      if (d.addr) { const n = copia.notas.find(x => x[0] === d.addr); n[1] = d.antes; continue; }
      const v = copia.vals.find(v => v[0] === d.r && v[1] === d.c);
      if (v) v[2] = d.antes; else copia.vals.push([d.r, d.c, d.antes, d.estilo]);
    }
    copia.vals.sort((x, y) => x[0] - y[0] || x[1] - y[1]);
    const depois = expandir(copia), alvo = new Map(meu.filter(d => !d.addr).map(d => [d.r + ':' + d.c, d.antes]));
    for (const pos of new Set([...antes.keys(), ...depois.keys()])) {
      const esperado = alvo.has(pos) ? alvo.get(pos) : antes.get(pos);
      if (depois.get(pos) !== esperado) throw Error('Corte do XP: reversão fora do molde em ' + nome + '!' + pos);
    }
    copias[nome] = copia;
  }
  for (const [nome, copia] of Object.entries(copias)) { const aba = abas.find(a => a.nome === nome); aba.vals = copia.vals; if (copia.notas) aba.notas = copia.notas; }
  return abas;
}

if (require.main === module) {
  const [base, atual] = process.argv.slice(2);
  if (base && atual) {
    const { ler } = require('../testes/expansao_domada_modelo');
    const r = comparar(ler(base), ler(atual));
    require('fs').writeFileSync(CAMINHO, JSON.stringify(r.delta, null, 2) + '\n');
    console.log(JSON.stringify({ abas: r.abas, posicoes: r.posicoes, alteracoes: r.delta.length }));
  } else process.stdout.write(trecho(process.argv.includes('--reverter')) + '\n');
}
module.exports = { CORTE, MOLDES, trocar, preparar, trecho, explicar, comparar, reverterModelo, TOTAIS, DADOS, NOTAS_EM };
