'use strict';
// 26/11/2026 (etapa 3 da versão rápida): o cartão de preencher do personagem, sem Google. Confere nas fontes geradas:
// o personagem fora da montagem R53; a conta leve dos 36 feitiços e das 3 Liberações (pontos, PE pela regra de
// conjuração, resolve, limite de Melhorias); as caixinhas Inescapável e Certeiro; os menus de ação e de alcance; e a
// Técnica Máxima completa (R67: dano, cura, PV temporários e SEM DANO, com a Forma e a base da função tiradas dos
// dados-base). Substitui os testes da montagem antiga, aposentados nesta etapa.
const assert = require('node:assert/strict');
const vm = require('node:vm');

const c = {};
vm.runInNewContext(require('../../medidas/carregar-ficha').fontes(), c);
const aba = n => c.ABAS.find(a => a.nome === n);
const FA = aba('FICHA AMALDIÇOADA'), AM = aba('DADOS_AM');
const col = s => [...s].reduce((n, ch) => n * 26 + ch.charCodeAt(0) - 64, 0);
const rc = a1 => { const m = /^([A-Z]+)(\d+)$/.exec(a1); return [+m[2], col(m[1])]; };
const valor = (a, a1) => { const [r, k] = rc(a1); const v = a.vals.find(x => x[0] === r && x[1] === k); return v ? v[2] : undefined; };
const cab = {};
for (const v of AM.vals) if (v[0] === 1 && v[2]) cab[v[2]] = v[1];
const am = (k, r) => { const v = AM.vals.find(x => x[0] === r && x[1] === cab[k]); return v ? String(v[2]) : ''; };
const naFicha = f => { const m = /'FICHA AMALDIÇOADA'!\$([A-Z]+)\$(\d+)/.exec(f); return m && m[1] + m[2]; };
const menus = new Map();
for (const [onde, f] of FA.dv) for (const parte of String(onde).split(' ')) menus.set(parte.split(':')[0], f);
const caixinha = a1 => { const [r, k] = rc(a1); return FA.caixas.some(([cc, rr, q]) => cc === k && rr <= r && r < rr + q); };
let n = 0;
const ok = (cond, msg) => { assert.ok(cond, msg); n++; };

// 1. o personagem saiu da montagem: no editor R53 só ficam as entidades
ok(Array.from(c.R53_EDITOR_.contextos, g => g.id).every(id => id.startsWith('entidade.')), 'sobrou cartão do personagem no editor R53');
ok(c.R53_EDITOR_.contextos.length === 204, 'o editor R53 devia ter as 204 entidades');

// 2. a conta leve: linha 2 a 37 são os feitiços, 38 a 40 as Liberações
for (let r = 2; r <= 40; r++) {
  ok(naFicha(am('nome', r)), 'o nome não lê o cartão, linha ' + r);
  ok(am('d', r).includes('MAX(0,'), 'os pontos, linha ' + r);
  ok(am('pe', r).includes('LET(estagio'), 'o PE não segue a regra de conjuração, linha ' + r);
  ok(am('resolve', r).includes('"Automático"') && am('resolve', r).includes('"TR para metade"'), 'o resolve, linha ' + r);
  ok(am('ampliar', r).includes('Melhorias: ') && am('ampliar', r).includes('Restrições: '), 'o limite, linha ' + r);
  ok(am('conta', r).includes(' pontos') && am('conta', r).includes('teto '), 'a conta escrita, linha ' + r);
  for (const k of ['lg', 'mr']) {
    const a1 = naFicha(am(k, r));
    ok(a1 && valor(FA, a1) === false && caixinha(a1), 'a caixinha ' + k + ' da linha ' + r + ' (' + a1 + ')');
  }
  const acao = naFicha(am('acao', r)), alcance = naFicha(am('alcance', r));
  ok(/^"Padrão,Bônus,Reação,Rodada inteira,/.test(menus.get(acao) || ''), 'o menu da ação em ' + acao);
  ok(menus.get(alcance) === "'DADOS_FORMAS'!$GH$2:$GH$7", 'o menu do alcance em ' + alcance);
  ok(am('alcance', r).includes('$GX' + r + ','), 'em branco, o alcance não cai no alcance base, linha ' + r);
}
// a Liberação começa em Rodada inteira; o feitiço, em Padrão
ok(valor(FA, naFicha(am('acao', 2))) === 'Padrão', 'a ação do feitiço 1');
ok(valor(FA, naFicha(am('acao', 38))) === 'Rodada inteira', 'a ação da Liberação 1');
ok(am('pe', 38).includes('4.5'), 'o PE da Liberação é 4,5 × Classe');

// 3. a Técnica Máxima completa
const calc = {};
for (const v of AM.vals) if (v[1] === cab['caixa calculada'] && v[0] > 1) {
  const f = AM.vals.find(x => x[0] === v[0] && x[1] === cab['o que a caixa mostra']);
  calc[v[2]] = f ? String(f[2]) : '';
}
const rotulos = {};
for (const v of FA.vals) if (['DANO', 'CURA', 'PV TEMP.', 'SEM DANO'].includes(v[2]) && v[0] > 300) rotulos[v[2]] = v;
ok(Object.keys(rotulos).length === 4, 'o cartão da Máxima sem as quatro funções');
for (const [rot, [r, k]] of Object.entries(rotulos)) {
  const letra = String.fromCharCode(64 + k), caixa = letra + (r + 1), mostra = letra + (r + 2);
  ok(valor(FA, caixa) === false && caixinha(caixa), 'a caixinha ' + rot + ' em ' + caixa);
  const f = calc[mostra] || '';
  ok(f.includes("'FICHA AMALDIÇOADA'!$" + letra + '$' + (r + 1)), rot + ': o valor não lê a caixinha (' + mostra + ')');
  if (rot !== 'SEM DANO') {
    ok(f.includes('CEILING(1.5*') && f.includes('="Área"'), rot + ': a Forma e a base não saem dos dados-base');
  }
}
ok((calc[String.fromCharCode(64 + rotulos.DANO[1]) + (rotulos.DANO[0] + 2)] || '').includes('Toca a Alma'), 'o dano não confere Toca a Alma');
ok((calc[String.fromCharCode(64 + rotulos['PV TEMP.'][1]) + (rotulos['PV TEMP.'][0] + 2)] || '').includes('3*MAX(0,'), 'o PV temporário é 3 por dado');
const montagem = Object.entries(calc).find(([, f]) => f.includes('marque uma função'));
ok(montagem, 'a montagem da Máxima não avisa quando falta ou sobra função');

console.log(JSON.stringify({resultado: 'OK', verificacoes: n}));
