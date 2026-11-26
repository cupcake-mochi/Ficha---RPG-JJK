'use strict';
// 26/11/2026 (etapa 4 da versão rápida): o cartão de preencher das invocações e a lista de perícias, sem Google. Confere
// nas fontes geradas: a montagem R53 vazia (nenhum cartão pesado); a conta leve dos 156 cartões (o nome livre, o peso de
// cada peça num menu com o preço tirado da tabela das invocações, as caixinhas Inescapável e Certeiro, a ação num menu, o
// dano e o alcance do jogador); a lista de perícias de cada uma das 12 fichas (a caixinha Treinada, o total, o contador e
// o Buff/Debuff do limite); e as contagens de especiais e do repertório lendo as caixas de nome.
const assert = require('node:assert/strict');
const vm = require('node:vm');

const c = {};
vm.runInNewContext(require('../../medidas/carregar-ficha').fontes(), c);
const aba = n => c.ABAS.find(a => a.nome === n);
const IV = aba('INVOCAÇÕES'), DI = aba('DADOS_INVOC');
const col = s => [...s].reduce((n, ch) => n * 26 + ch.charCodeAt(0) - 64, 0);
const letra = k => { let s = ''; for (; k > 0; k = Math.floor((k - 1) / 26)) s = String.fromCharCode(65 + (k - 1) % 26) + s; return s; };
const rc = a1 => { const m = /^([A-Z]+)(\d+)$/.exec(a1); return [+m[2], col(m[1])]; };
const valor = (a, a1) => { const [r, k] = rc(a1); const v = a.vals.find(x => x[0] === r && x[1] === k); return v ? v[2] : undefined; };
const desce = (f, d) => String(f).replace(/('[^']*'!|[A-Za-z_]+!)?(\$?)([A-Z]{1,3})(\$?)(\d+)\b/g,
  (m, a, sc, l, sr, n) => (a || '') + sc + l + sr + (sr ? n : String(+n + d)));
const formula = (a, r, k) => {
  const v = a.vals.find(x => x[0] === r && x[1] === k);
  if (v) return String(v[2]);
  const b = (a.abaixo || []).find(([r1, c1, r2, c2]) => r1 < r && r <= r2 && c1 <= k && k <= c2);
  const topo = b && a.vals.find(x => x[0] === b[0] && x[1] === k);
  return topo ? desce(topo[2], r - b[0]) : '';
};
// a tabela das cartas: os cabeçalhos repetem os de outras tabelas, então cada nome vale a partir da coluna dela
const cabDe = inicio => {
  const k0 = DI.vals.find(v => v[0] === 1 && v[2] === inicio)[1];
  const cab = {};
  for (const v of DI.vals.filter(v => v[0] === 1 && v[1] >= k0).sort((a, b) => a[1] - b[1])) if (!(v[2] in cab)) cab[v[2]] = v[1];
  return cab;
};
const CARTA = cabDe('conta de habilidade'), FICHA = cabDe('conta de ficha');
const carta = (k, r) => formula(DI, r, CARTA[k]);
const ficha = (k, r) => formula(DI, r, FICHA[k]);
const naAba = f => { const m = /'INVOCAÇÕES'!\$([A-Z]+)\$(\d+)/.exec(f); return m && m[1] + m[2]; };
const todasNaAba = f => [...String(f).matchAll(/'INVOCAÇÕES'!\$?([A-Z]+)\$?(\d+)/g)].map(m => m[1] + m[2]);
const menus = new Map();
for (const [onde, f] of IV.dv) for (const parte of String(onde).split(' ')) {
  const [ini, fim] = parte.split(':');
  if (!fim) { menus.set(ini, f); continue; }
  const [r1, c1] = rc(ini), [r2, c2] = rc(fim);
  for (let r = r1; r <= r2; r++) for (let k = c1; k <= c2; k++) menus.set(letra(k) + r, f);
}
const caixinha = a1 => { const [r, k] = rc(a1); return IV.caixas.some(([cc, rr, q]) => cc === k && rr <= r && r < rr + q); };
let n = 0;
const ok = (cond, msg) => { assert.ok(cond, msg); n++; };

// 1. a montagem R53 ficou vazia: nenhum cartão passa mais pelo editor
ok(Array.from(c.R53_EDITOR_.contextos).length === 0, 'sobrou cartão pesado no editor R53');

// 2. a conta leve dos 156 cartões
const PESOS = '"Leve,Média,Pesada,Leve · Livre,Média · Livre,Pesada · Livre"';
for (let r = 2; r <= 157; r++) {
  const nome = naAba(carta('nome', r));
  ok(nome, 'o nome não lê o cartão, linha ' + r);
  ok(!menus.has(nome), 'o nome tem menu, linha ' + r);
  for (let i = 1; i <= 4; i++) {
    const m = naAba(carta('m' + i, r));
    ok(m && !menus.has(m), 'a Melhoria ' + i + ' tem menu (o nome é livre), linha ' + r);
    const f = carta('k' + i, r), peso = naAba(f);
    ok(menus.get(peso) === PESOS, 'o menu de peso da Melhoria ' + i + ', linha ' + r + ' (' + peso + ')');
    ok(/="Pesada · Livre",INDEX\(\$[A-Z]+\$\d+:\$[A-Z]+\$\d+,MAX\(1,/.test(f), 'o preço da Melhoria ' + i + ' não sai da tabela, linha ' + r);
  }
  for (let i = 1; i <= 2; i++) {
    const f = carta('c' + i, r);
    ok(menus.get(naAba(f)) === '"Leve,Média"', 'o menu de peso da Restrição ' + i + ', linha ' + r);
    ok(f.includes('="Leve",CEILING(') && f.includes('="Média",'), 'a devolução da Restrição ' + i + ', linha ' + r);
  }
  for (const k of ['lg', 'mr']) {
    const a1 = naAba(carta(k, r));
    ok(a1 && valor(IV, a1) === false && caixinha(a1), 'a caixinha ' + k + ' da linha ' + r + ' (' + a1 + ')');
  }
  const acao = naAba(carta('acao', r));
  ok(/^"Atuação básica,Padrão,Bônus,Reação,/.test(menus.get(acao) || ''), 'o menu da ação em ' + acao);
  ok(['Atuação básica', 'Padrão'].includes(valor(IV, acao)), 'a ação começa preenchida em ' + acao);
  const dano = naAba(carta('dano', r)), alcance = naAba(carta('alcance', r));
  ok(dano && !menus.has(dano), 'o dano é do jogador, linha ' + r);
  ok(alcance && carta('alcance', r).includes(',$' + letra(CARTA.q1) + r + ','), 'em branco, o alcance cai no alcance base, linha ' + r);
  ok(carta('resolve', r).includes('"Automático"') && carta('resolve', r).includes('" · metade"'), 'as caixinhas mudam o resolve, linha ' + r);
  ok(!/(Melhoria|Restrição) não cadastrada/.test(carta('erros', r)), 'o nome da peça ainda é conferido no catálogo, linha ' + r);
  ok(carta('ampliar', r).includes('Melhorias: '), 'a linha do limite, linha ' + r);
}

// 3. a lista de perícias das 12 fichas
const N_PER = 23;
for (let r = 2; r <= 13; r++) {
  const marcadas = todasNaAba(ficha('tper', r));
  ok(marcadas.length === N_PER && new Set(marcadas).size === N_PER, 'o contador não lê as 23 caixinhas, ficha ' + (r - 1));
  for (const a1 of marcadas) ok(valor(IV, a1) === false && caixinha(a1), 'a caixinha Treinada em ' + a1);
  ok(ficha('nper', r).startsWith('=4+INT(') && ficha('nper', r).includes('+$' + letra(FICHA.per0) + r), 'o limite soma o Buff/Debuff, ficha ' + (r - 1));
  const bd = naAba(ficha('per0', r));
  ok(bd && valor(IV, bd) === 0, 'a caixa do Buff/Debuff do limite, ficha ' + (r - 1));
  ok(ficha('d_per', r).includes('PERÍCIAS TREINADAS · ') && ficha('d_per', r).includes('ACIMA DO LIMITE'), 'o título do contador, ficha ' + (r - 1));
  // o total de cada perícia: a caixa aponta para a tabela "mostra", e a conta lê a caixinha da mesma linha
  for (const a1 of marcadas) {
    const [rr, kk] = rc(a1), total = letra(kk + 1) + rr;
    const mostra = naAba(String(valor(IV, total))) ? null : /DADOS_INVOC!\$([A-Z]+)\$(\d+)/.exec(String(valor(IV, total)));
    ok(mostra, 'o total da perícia não aponta para a conta, em ' + total);
    const conta = formula(DI, +mostra[2], col(mostra[1]));
    ok(conta.includes("'INVOCAÇÕES'!$" + letra(kk) + '$' + rr + '=TRUE'), 'o total não lê a caixinha, em ' + total);
  }
}

// 4. as contagens de especiais (Expansão) e do repertório leem as caixas de nome
for (let r = 2; r <= 13; r++) {
  const ie = formula(DI, r, col('IE'));
  ok(!ie.includes('DADOS_R53') && todasNaAba(ie).length === 8, 'a contagem de especiais ainda lê a DADOS_R53, linha ' + r);
  const dc = formula(DI, r + 15, col('DC'));
  ok(!dc.includes('DADOS_R53') && todasNaAba(dc).length === 3, 'o repertório ainda lê a DADOS_R53, linha ' + (r + 15));
}

console.log(JSON.stringify({resultado: 'OK', verificacoes: n}));
