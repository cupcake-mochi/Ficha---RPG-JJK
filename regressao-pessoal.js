// Roda no node, sem Sheets: o que o Codigo.gs faz pela FICHA PESSOAL.
//
// A aba nasce no gerador e calcula em fórmula; o regressao-ficha-pessoal.py confere essa parte com o LibreOffice.
// Aqui fica o que só o script faz, e que não dá para rodar fora do Google:
//   - a caixa de treino do grupo, que marca e desmarca o grupo inteiro, e a da arma, que acerta a do grupo;
//   - o treino que o Caminho dá quando ele é escolhido;
//   - a missão anotada, que sobe o nível, nunca desce e para no limiar do feito;
//   - o Volume do item, que volta a ser conta quando a caixa é apagada;
//   - as notas que mudam com a ficha.
// As contas moram em funções sem planilha em volta, e elas rodam contra o catálogo. O caminho inteiro (o onEdit, o
// índice da DADOS, as tabelas achadas pelo cabeçalho) roda num Sheets de mentira montado do ABAS do Ficha.gs.
//
// node regressao-pessoal.js
'use strict';
const fs = require('fs'), vm = require('vm'), path = require('path');
const RAIZ = __dirname;
const GS = fs.readFileSync(path.join(RAIZ, 'apps-script', 'Codigo.gs'), 'utf8');
const FICHA_SRC = fs.readFileSync(path.join(RAIZ, 'apps-script', 'Ficha.gs'), 'utf8');
const CAT = JSON.parse(fs.readFileSync(path.join(RAIZ, 'catalogo-projeto-m.json'), 'utf8'));

let falhas = 0;
const ok = (nome, cond, det = '') => { console.log((cond ? '  ok    ' : '  FALHA ') + nome + (cond ? '' : '  <- ' + det)); if (!cond) falhas++; };
const igual = (a, b) => JSON.stringify(a) === JSON.stringify(b);

// ---------------------------------------------------------------------------------------------
// o Sheets de mentira: uma grade de valores por aba, montada do ABAS, com as notas e as fórmulas
// ---------------------------------------------------------------------------------------------
// O ABAS como o script o usa: o Ficha.gs escreve por extenso, quando carrega, as fileiras de cartas que são cópia
// (expandirCopias_). Lido como texto, ele viria só com a primeira fileira de cada tipo.
const ABAS = (() => { const c = {}; require('vm').createContext(c); require('vm').runInContext(FICHA_SRC, c); return JSON.parse(JSON.stringify(require('vm').runInContext('ABAS', c))); })();
const NOME = 'FICHA PESSOAL';
const letras = (c) => { let s = ''; while (c > 0) { const m = (c - 1) % 26; s = String.fromCharCode(65 + m) + s; c = Math.floor((c - 1) / 26); } return s; };
const numero = (t) => [...t].reduce((n, ch) => n * 26 + ch.charCodeAt(0) - 64, 0);
const lc = (a1) => { const m = /^([A-Z]+)(\d+)$/.exec(a1.replace(/\$/g, '')); return [Number(m[2]), numero(m[1])]; };

function criaPlanilha() {
  const abas = {}, log = { leiturasDaDados: 0, chamadas: [] };
  for (const s of ABAS) {
    const v = [...Array(s.rows)].map(() => Array(s.cols).fill(''));
    const formulas = {};
    for (const t of s.vals) {
      if (typeof t[2] === 'string' && t[2].startsWith('=')) formulas[t[0] + ',' + t[1]] = t[2];
      else v[t[0] - 1][t[1] - 1] = t[2];
    }
    abas[s.nome] = { v, formulas, notas: {}, spec: s };
  }
  // a fórmula que o teste precisa ver calculada: o endereço em ADDRESS, e a referência direta a uma célula
  const resolve = (nomeAba, f) => {
    const end = [...f.matchAll(/ADDRESS\(ROW\((?:'[^']+'|[A-ZÇÃ_]+)!([A-Z]+\d+)\),COLUMN\([^)]*\),4\)/g)].map((m) => m[1]);
    if (end.length && f.replace(/\s/g, '').startsWith('=ADDRESS(')) return end.join(':');
    const ref = /^=(?:'([^']+)'|([A-ZÇÃ_]+))!\$?([A-Z]+)\$?(\d+)$/.exec(f);
    if (ref) return valor(ref[1] || ref[2], Number(ref[4]), numero(ref[3]));
    if (f === '=TRUE') return true;
    return f;
  };
  const valor = (nomeAba, r, c) => {
    const A = abas[nomeAba], f = A.formulas[r + ',' + c];
    return f === undefined ? A.v[r - 1][c - 1] : resolve(nomeAba, f);
  };
  const sheet = (nome) => {
    const A = abas[nome];
    if (!A) return null;
    const range = (r, c, nl = 1, nc = 1) => ({
      getRow: () => r, getColumn: () => c, getNumRows: () => nl, getNumColumns: () => nc,
      getA1Notation: () => letras(c) + r + (nl > 1 || nc > 1 ? ':' + letras(c + nc - 1) + (r + nl - 1) : ''),
      getSheet: () => sheet(nome),
      getValue: () => valor(nome, r, c),
      getValues: () => { if (nome === 'DADOS' && nl > 20 && nc > 20) log.leiturasDaDados++;
        return [...Array(nl)].map((_, i) => [...Array(nc)].map((__, j) => valor(nome, r + i, c + j))); },
      setValue: (x) => { delete A.formulas[r + ',' + c]; A.v[r - 1][c - 1] = x; log.chamadas.push(['setValue', nome, letras(c) + r, x]); },
      getNote: () => A.notas[r + ',' + c] || '',
      setNote: (t) => { A.notas[r + ',' + c] = t; log.chamadas.push(['setNote', nome, letras(c) + r]); },
      getFormulasR1C1: () => [...Array(nl)].map((_, i) => [...Array(nc)].map((__, j) => A.formulas[(r + i) + ',' + (c + j)] ? 'R1C1 da conta' : '')),
      setFormulaR1C1: (f) => { A.formulas[r + ',' + c] = '=a conta de volta'; log.chamadas.push(['setFormulaR1C1', nome, letras(c) + r, f]); },
    });
    const porA1 = (a1) => { const [a, b] = a1.split(':'); const [r1, c1] = lc(a); const [r2, c2] = b ? lc(b) : [r1, c1]; return range(r1, c1, r2 - r1 + 1, c2 - c1 + 1); };
    return {
      getName: () => nome, getLastRow: () => A.spec.rows,
      getRange: (r, c, nl, nc) => (typeof r === 'string' ? porA1(r) : range(r, c, nl, nc)),
      getDataRange: () => range(1, 1, A.spec.rows, A.spec.cols),
      getRangeList: (lista) => ({
        check: () => { lista.forEach((a1) => { const [r, c] = lc(a1); A.v[r - 1][c - 1] = true; }); log.chamadas.push(['check', nome, lista.length]); },
        uncheck: () => { lista.forEach((a1) => { const [r, c] = lc(a1); A.v[r - 1][c - 1] = false; }); log.chamadas.push(['uncheck', nome, lista.length]); },
      }),
    };
  };
  const ss = { getSheetByName: sheet };
  const ctx = {
    console: { log: () => {} }, Logger: { log: () => {} }, Date,
    SpreadsheetApp: { getActive: () => ss, flush: () => {} },
    PropertiesService: { getDocumentProperties: () => ({ getProperty: () => null, setProperty: () => {}, deleteProperty: () => {} }) },
    LockService: { getDocumentLock: () => ({ tryLock: () => true, releaseLock: () => {} }) },
  };
  vm.createContext(ctx); vm.runInContext(FICHA_SRC, ctx); vm.runInContext(GS, ctx);
  return { abas, log, ctx, ss, sheet, valor };
}

// ---------------------------------------------------------------------------------------------
// 1. as contas sem planilha, contra o catálogo
// ---------------------------------------------------------------------------------------------
console.log('AS CAIXAS DE TREINO, SEM PLANILHA');
const P0 = criaPlanilha();
const C = P0.ctx;
const eq = CAT.equipamento;
const armas = Object.entries(eq.armas).map(([n, a]) => ({ caixa: 'arma:' + n, categoria: a.categoria }));
const categorias = Object.values(eq.treino.listas).flat();
const grupos = categorias.map((c) => ({ caixa: 'grupo:' + c, categoria: c }));
const doGrupo = (c) => armas.filter((a) => a.categoria === c).map((a) => a.caixa);
const vazio = () => Object.fromEntries(armas.concat(grupos).map((x) => [x.caixa, false]));
const aplica = (m, muda) => Object.assign(m, muda);
ok(`o catálogo tem ${armas.length} armas em ${categorias.length} categorias, e toda arma tem a categoria numa lista de treino`,
   armas.length === 52 && categorias.length === 13 && armas.every((a) => categorias.includes(a.categoria)));
{
  let erros = [];
  for (const cat of categorias) {
    // marcar o grupo marca as armas dele, e só elas
    let m = vazio(); m['grupo:' + cat] = true;
    let muda = C.treinoDepoisDaCaixa_(armas, grupos, m, 'grupo:' + cat);
    if (!igual(Object.keys(muda).sort(), doGrupo(cat).sort()) || !Object.values(muda).every((v) => v === true)) erros.push('marcar ' + cat);
    aplica(m, muda);
    // desmarcar uma arma desmarca a caixa do grupo, e nenhuma outra arma
    const uma = doGrupo(cat)[0]; m[uma] = false;
    muda = C.treinoDepoisDaCaixa_(armas, grupos, m, uma);
    if (!igual(muda, { ['grupo:' + cat]: false })) erros.push('desmarcar uma arma de ' + cat);
    aplica(m, muda);
    // marcar de volta a última que faltava marca o grupo
    m[uma] = true;
    muda = C.treinoDepoisDaCaixa_(armas, grupos, m, uma);
    if (!igual(muda, { ['grupo:' + cat]: true })) erros.push('marcar a última de ' + cat);
    aplica(m, muda);
    // desmarcar o grupo desmarca as armas dele
    m['grupo:' + cat] = false;
    muda = C.treinoDepoisDaCaixa_(armas, grupos, m, 'grupo:' + cat);
    if (!igual(Object.keys(muda).sort(), doGrupo(cat).sort()) || !Object.values(muda).every((v) => v === false)) erros.push('desmarcar ' + cat);
    aplica(m, muda);
    if (Object.values(m).some((v) => v)) erros.push('sobrou marca depois de ' + cat);
  }
  ok('nas 13 categorias: o grupo marca e desmarca as armas dele, e a arma acerta a caixa do grupo', !erros.length, erros.join(' · '));
  // marcar uma arma com o resto do grupo vazio não marca o grupo
  const m = vazio(); const uma = doGrupo('Lâmina Longa')[0]; m[uma] = true;
  ok('uma arma marcada sozinha não marca o grupo', igual(C.treinoDepoisDaCaixa_(armas, grupos, m, uma), {}));
  ok('caixa que não é de treino não muda nada', igual(C.treinoDepoisDaCaixa_(armas, grupos, vazio(), 'Z99'), {}));
}

console.log('\nO TREINO QUE O CAMINHO DÁ');
{
  const caminhos = Object.keys(CAT.caminhos);
  const conj = eq.treino.conjurador_treina;
  // 04/10/2026: o livro reconstruído diz o treino de arma na tabela de Características de cada Caminho
  const linhas = fs.readFileSync(path.join(RAIZ, 'manual.txt'), 'utf8').split('\n');
  const armaDo = (cam) => {
    const i = linhas.findIndex((l) => l === '### ' + cam);
    const l = i < 0 ? null : linhas.slice(i, i + 40).find((x) => /^(Armas|Treino de arma|Armas treinadas) \| /.test(x));
    return l || '';
  };
  const todas = caminhos.filter((c) => /treze categorias|todas as categorias/i.test(armaDo(c)));
  const conta = (cam) => Object.values(C.treinoDoCaminho_(armas, grupos, cam, caminhos, todas, conj)).filter(Boolean).length;
  const doConj = armas.filter((a) => conj.includes(a.categoria)).length + conj.length;
  ok(`o livro dá todas as armas a ${todas.join(', ')}`, todas.length === 3 && todas.every((c) => CAT.caminhos[c].armas === 'todas'), String(todas));
  ok(`${todas.join(' e ')}: as ${armas.length + grupos.length} caixas marcadas`, todas.every((c) => conta(c) === armas.length + grupos.length));
  const outros = caminhos.filter((c) => !todas.includes(c));
  ok(`${outros.join(', ')}: só ${conj.join(' e ')}, ${doConj} caixas`, outros.length === 3 && outros.every((c) => conta(c) === doConj && /Arma(s)? de Fogo e Balestra/.test(armaDo(c))),
     outros.map((c) => c + ' ' + conta(c)).join(' · '));
  ok('sem Caminho escolhido, nenhuma caixa', conta('Escolha seu Caminho') === 0 && conta('') === 0);
}

console.log('\nA MISSÃO QUE SOBE O NÍVEL');
{
  // a curva do catálogo: o XP acumulado em que se chega a cada nível
  const tab = []; let ac = 0;
  Object.keys(CAT.progressao.tabela_impressa).map(Number).filter((n) => n >= 2).sort((a, b) => a - b).forEach((n) => {
    tab.push({ nivel: n, xp: ac });
    const custo = String(CAT.progressao.tabela_impressa[n].xp);
    if (custo !== '—') ac += Number(custo.replace('.', ''));
  });
  const LIM = CAT.progressao.limiar_do_feito.nivel;
  const xpDo = (n) => tab.find((t) => t.nivel === n).xp;
  const sobe = (xp, atual) => C.nivelQueSobe_(tab, xp, atual, LIM);
  ok(`a curva chega ao nível ${LIM} com ${xpDo(LIM)} e ao 30 com ${xpDo(30)}`, xpDo(3) === 200 && xpDo(LIM) === 14300 && xpDo(30) === 30700);
  let erros = [];
  for (let n = 2; n < LIM; n++) {
    if (sobe(xpDo(n + 1), n) !== n + 1) erros.push(`no XP do ${n + 1}, o ${n} não subiu`);
    if (sobe(xpDo(n + 1) - 12.5, n) !== null) erros.push(`12,5 antes do ${n + 1}, o ${n} subiu`);
  }
  ok(`do 2 ao ${LIM - 1}: sobe no XP exato do nível seguinte, e 12,5 antes ainda não`, !erros.length, erros.join(' · '));
  ok('o XP nunca desce o nível: nível 5 com 100 de XP fica no 5', sobe(100, 5) === null && sobe(0, 2) === null);
  ok('duas faixas de uma vez: nível 2 com o XP do 5 vai para o 5', sobe(xpDo(5), 2) === 5);
  ok(`o limiar do feito: no ${LIM} o XP não sobe mais, nem com o XP do 30`, sobe(xpDo(30), LIM) === null && sobe(xpDo(LIM + 1), LIM) === null);
  ok(`abaixo do limiar o XP para no ${LIM}`, sobe(xpDo(30), LIM - 1) === LIM && sobe(xpDo(25), 2) === LIM);
  ok(`quem já passou do limiar sobe pelo XP: ${LIM + 1} com o XP do ${LIM + 2}`, sobe(xpDo(LIM + 2), LIM + 1) === LIM + 2 && sobe(xpDo(30), 29) === 30);
  ok('XP que não é da curva não sobe ninguém', C.nivelQueSobe_([], 500, 2, LIM) === null);
}

console.log('\nAS FAIXAS');
{
  const r = (l, c, nl = 1, nc = 1) => ({ getRow: () => l, getColumn: () => c, getNumRows: () => nl, getNumColumns: () => nc });
  ok('limitesA1_ lê célula e faixa', igual(C.limitesA1_('D45:AT57'), { l1: 45, c1: 4, l2: 57, c2: 46 }) && igual(C.limitesA1_('$AW$10'), { l1: 10, c1: 49, l2: 10, c2: 49 })
     && C.limitesA1_('') === null);
  ok('tocaFaixa_: dentro, na borda, fora, e colagem que cruza', C.tocaFaixa_(r(45, 4), 'D45:AT57') && C.tocaFaixa_(r(57, 46), 'D45:AT57')
     && !C.tocaFaixa_(r(58, 4), 'D45:AT57') && !C.tocaFaixa_(r(45, 47), 'D45:AT57') && C.tocaFaixa_(r(40, 1, 10, 10), 'D45:AT57') && !C.tocaFaixa_(r(45, 4), undefined));
}

// ---------------------------------------------------------------------------------------------
// 2. o caminho inteiro, no Sheets de mentira
// ---------------------------------------------------------------------------------------------
console.log('\nO ÍNDICE E AS TABELAS QUE A ABA PUBLICA NA DADOS');
const P = criaPlanilha();
const ip = P.ctx.indicePessoal_();
const dadosDe = (Q) => Q.sheet('DADOS').getDataRange().getValues();
const editada = (Q, a1, value) => { const g = Q.sheet(NOME).getRange(a1); return { range: g, value }; };
{
  const esperados = ['principal', 'secundária', 'vestindo', 'grau', 'situação do traje', 'xp total', 'treino', 'missões 1', 'missões 2', 'missões 3', 'missões 4',
                     'equipáveis', 'itens', 'volume dos itens 1', 'volume dos itens 2', 'em uso', 'fileira'];
  ok(`o índice da FICHA PESSOAL tem os ${esperados.length} campos, cada um com endereço`,
     esperados.every((k) => /^[A-Z]+\d+(:[A-Z]+\d+)?$/.test(ip[k] || '')), esperados.filter((k) => !ip[k]).join(', '));
  const cab = P.sheet('DADOS').getRange(4, P.ctx.IDXP_COL_CAMPO).getValue();
  ok('o IDXP_COL_CAMPO do Codigo.gs aponta para a coluna do "campo pessoal"', cab === 'campo pessoal', String(cab));
  const t = P.ctx.caixasDeTreino_(dadosDe(P));
  ok(`a DADOS publica a caixa de treino das ${armas.length} armas e das ${categorias.length} categorias`,
     t.armas.length === 52 && t.grupos.length === 13 && t.armas.concat(t.grupos).every((x) => /^[A-Z]+\d+$/.test(x.caixa)),
     `${t.armas.length} armas, ${t.grupos.length} grupos`);
  ok('nenhuma caixa de treino se repete, e todas caem dentro da faixa do treino',
     new Set(t.armas.concat(t.grupos).map((x) => x.caixa)).size === 65
     && t.armas.concat(t.grupos).every((x) => { const [l, c] = lc(x.caixa); const f = P.ctx.limitesA1_(ip['treino']); return l >= f.l1 && l <= f.l2 && c >= f.c1 && c <= f.c2; }));
  ok('toda caixa de treino é caixa de seleção na aba (nasce FALSO)',
     t.armas.concat(t.grupos).every((x) => { const [l, c] = lc(x.caixa); return P.abas[NOME].v[l - 1][c - 1] === false; }));
  ok('a categoria de cada arma na DADOS é a do catálogo',
     t.armas.length === armas.length && Object.entries(eq.armas).every(([n, a]) => {
       const linha = P.ctx.tabelaDaDados_(dadosDe(P), 'equipável', ['categoria do equipável']).find((l) => l['equipável'] === n);
       return linha && linha['categoria do equipável'] === a.categoria; }));
  ok(`o conjurador treina ${eq.treino.conjurador_treina.join(' e ')}`, igual(t.conjurador.slice().sort(), eq.treino.conjurador_treina.slice().sort()), String(t.conjurador));
}

console.log('\nO onEdit NA FICHA PESSOAL');
{
  const Q = criaPlanilha();
  const t = Q.ctx.caixasDeTreino_(dadosDe(Q));
  const grupo = t.grupos.find((g) => g.categoria === 'Lâmina Curta');
  const dele = t.armas.filter((a) => a.categoria === 'Lâmina Curta').map((a) => a.caixa);
  const marca = (a1, v) => { const [l, c] = lc(a1); Q.abas[NOME].v[l - 1][c - 1] = v; };
  const lida = (a1) => { const [l, c] = lc(a1); return Q.abas[NOME].v[l - 1][c - 1]; };
  marca(grupo.caixa, true);
  Q.ctx.onEdit(editada(Q, grupo.caixa, 'TRUE'));
  ok(`marcar o grupo Lâmina Curta marca as ${dele.length} armas dele, numa chamada só`,
     dele.every((c) => lida(c) === true) && Q.log.chamadas.filter((c) => c[0] === 'check').length === 1
     && t.armas.filter((a) => a.categoria !== 'Lâmina Curta').every((a) => lida(a.caixa) === false), JSON.stringify(Q.log.chamadas));
  marca(dele[2], false);
  Q.ctx.onEdit(editada(Q, dele[2], 'FALSE'));
  ok('desmarcar uma arma desmarca a caixa do grupo e deixa as outras', lida(grupo.caixa) === false && dele.filter((c) => lida(c)).length === dele.length - 1);
  marca(dele[2], true);
  Q.ctx.onEdit(editada(Q, dele[2], 'TRUE'));
  ok('marcar a arma de volta marca o grupo', lida(grupo.caixa) === true);
  marca(grupo.caixa, false);
  Q.ctx.onEdit(editada(Q, grupo.caixa, 'FALSE'));
  ok('desmarcar o grupo desmarca todas as armas dele', dele.every((c) => lida(c) === false));
}
{
  const Q = criaPlanilha();
  const idx = Q.ctx.indiceDosDados_(dadosDe(Q));
  const nivel = () => Q.sheet('FICHA').getRange(idx['nivel']).getValue();
  const [lx, cx] = lc(ip['xp total']);
  const poeXp = (v) => { delete Q.abas[NOME].formulas[lx + ',' + cx]; Q.abas[NOME].v[lx - 1][cx - 1] = v; };
  const f1 = Q.ctx.limitesA1_(ip['missões 1']), f2 = Q.ctx.limitesA1_(ip['missões 2']);
  const missao = letras(f1.c1 + 1) + f1.l1, missao2 = letras(f2.c1 + 1) + (f2.l1 + 3);
  ok('a ficha nasce no nível 2', nivel() === 2, String(nivel()));
  poeXp(200); Q.ctx.onEdit(editada(Q, missao, 'Padrão'));
  ok('anotar missão até 200 de XP sobe a FICHA para o nível 3', nivel() === 3, String(nivel()));
  poeXp(100); Q.ctx.onEdit(editada(Q, missao, 'Curta'));
  ok('apagar a missão não desce o nível', nivel() === 3, String(nivel()));
  poeXp(20000); Q.ctx.onEdit(editada(Q, missao2, 'Final de arco'));
  ok('missão no segundo bloco também sobe, e o XP para no nível 20', nivel() === 20, String(nivel()));
  { const R = criaPlanilha(); const i2 = R.ctx.indiceDosDados_(dadosDe(R)); const f4 = R.ctx.limitesA1_(ip['missões 4']);
    const [l4, c4] = lc(ip['xp total']); delete R.abas[NOME].formulas[l4 + ',' + c4]; R.abas[NOME].v[l4 - 1][c4 - 1] = 500;
    R.ctx.onEdit(editada(R, letras(f4.c1 + 1) + (f4.l2), 'Longa'));
    ok('missão na última linha da quarta tabela, a da extensão, também sobe o nível', R.sheet('FICHA').getRange(i2['nivel']).getValue() === 4); }
  Q.sheet('FICHA').getRange(idx['nivel']).setValue(21);
  poeXp(17300); Q.ctx.onEdit(editada(Q, missao, 'Longa'));
  ok('depois do feito (nível 21 posto à mão) o XP volta a subir: 22', nivel() === 22, String(nivel()));
}
{
  const Q = criaPlanilha();
  const f = Q.ctx.limitesA1_(ip['volume dos itens 1']);
  const alvo = letras(f.c1) + (f.l1 + 2);
  const [l, c] = lc(alvo);
  delete Q.abas[NOME].formulas[l + ',' + c]; Q.abas[NOME].v[l - 1][c - 1] = 3;      // o jogador digitou o Volume por cima
  Q.ctx.onEdit(editada(Q, alvo, '3'));
  ok('Volume digitado por cima da conta fica como o jogador digitou', Q.abas[NOME].formulas[l + ',' + c] === undefined && Q.abas[NOME].v[l - 1][c - 1] === 3);
  Q.abas[NOME].v[l - 1][c - 1] = '';                                                 // e depois apagou
  Q.ctx.onEdit(editada(Q, alvo, undefined));
  ok('apagar o Volume do item traz a conta de volta, copiada da linha vizinha',
     Q.abas[NOME].formulas[l + ',' + c] !== undefined && Q.log.chamadas.filter((x) => x[0] === 'setFormulaR1C1').length === 1);
}
{
  const Q = criaPlanilha();
  const notas = Q.ctx.tabelaDaDados_(dadosDe(Q), 'nota viva', ['texto da nota', 'caixa da nota']);
  // 01/10/2026 (B30): duas notas a mais, a da arma de cada mão, na linha de detalhe embaixo da caixa de escolha
  ok('a DADOS publica as cinco notas que mudam, cada uma com a caixa dela', notas.length === 5 && notas.every((n) => /^[A-Z]+\d+$/.test(n['caixa da nota']))
     && new Set(notas.map((n) => n['caixa da nota'])).size === 5,
     JSON.stringify(notas.map((n) => [n['nota viva'], n['caixa da nota']])));
  const caixaDe = (k) => (notas.filter((n) => n['nota viva'] === k)[0] || {})['caixa da nota'];
  const [lp, cp] = lc(ip['principal']), [ls, cs] = lc(ip['secundária']);
  ok('a nota da arma de cada mão vai para a linha de detalhe, duas linhas abaixo da caixa em que se escolhe',
     caixaDe('arma da principal') === letras(cp) + (lp + 2) && caixaDe('arma da secundária') === letras(cs) + (ls + 2),
     `${caixaDe('arma da principal')} e ${caixaDe('arma da secundária')}, com as mãos em ${ip['principal']} e ${ip['secundária']}`);
  const daAba = ABAS.filter((s) => s.nome === NOME)[0].notas || [];
  const notaEm = (a1) => String((daAba.filter((n) => n[0] === a1)[0] || [])[1] || '');
  ok('a caixa de escolha de cada mão nasce com a nota que diz de onde vem o menu',
     /EQUIPÁVEIS GUARDADOS/.test(notaEm(ip['principal'])) && /EQUIPÁVEIS GUARDADOS/.test(notaEm(ip['secundária'])),
     `${notaEm(ip['principal']).slice(0, 60)} | ${notaEm(ip['secundária']).slice(0, 60)}`);
  const n1 = Q.ctx.configurarPessoal_(Q.ss);
  ok('o construir() grava as notas que nascem com texto, e uma segunda passada não grava de novo', /^[1-5] /.test(n1) && /^0 /.test(Q.ctx.configurarPessoal_(Q.ss)), n1);
  const antes = Q.log.leiturasDaDados;
  Q.ctx.onEdit(editada(Q, 'Q22', 'a história dela'));
  ok('digitar no dossiê não lê a DADOS inteira nem mexe em nada', Q.log.leiturasDaDados === antes && !Q.log.chamadas.slice(-1).some((x) => x[1] === NOME && x[0] !== 'setNote'));
  Q.ctx.onEdit(editada(Q, ip['principal'], 'Faca'));
  ok('trocar a arma da mão lê a DADOS uma vez e confere as notas', Q.log.leiturasDaDados === antes + 1);
}

console.log('\nO CAMINHO ESCOLHIDO NA FICHA');
{
  const Q = criaPlanilha();
  const idx = Q.ctx.indiceDosDados_(dadosDe(Q));
  const t = Q.ctx.caixasDeTreino_(dadosDe(Q));
  const marcadas = () => t.armas.concat(t.grupos).filter((x) => { const [l, c] = lc(x.caixa); return Q.abas[NOME].v[l - 1][c - 1] === true; }).length;
  const ficha = Q.sheet('FICHA');
  const escolhe = (cam) => Q.ctx.fichaMexeNaPessoal_({ range: ficha.getRange(idx['caminho']), value: cam }, idx);
  escolhe('Bastião');
  ok('Bastião: as 65 caixas de treino marcadas', marcadas() === 65, String(marcadas()));
  escolhe('Emanador');
  ok('trocar para Emanador deixa só Arma de Fogo e Balestra (9 armas e 2 grupos)', marcadas() === 11, String(marcadas()));
  escolhe('Vanguarda');
  ok('Vanguarda: as 65 de novo', marcadas() === 65, String(marcadas()));
  const antes = Q.log.chamadas.length;
  Q.ctx.fichaMexeNaPessoal_({ range: ficha.getRange('A1'), value: 'x' }, idx);
  ok('edição da FICHA que não é o Caminho nem a Força não encosta na FICHA PESSOAL', Q.log.chamadas.length === antes);
}

console.log('\nAS TRAVAS E A COR DE AVISO, NO ABAS');
{
  const spec = ABAS.find((a) => a.nome === NOME);
  const formulas = spec.vals.filter((t) => typeof t[2] === 'string' && t[2].startsWith('=') && t[0] > 7).map((t) => letras(t[1]) + t[0]);
  const cobre = (a1) => spec.protegidas.some((f) => { const g = C.limitesA1_(f); const [l, c] = lc(a1); return l >= g.l1 && l <= g.l2 && c >= g.c1 && c <= g.c2; });
  const livres = ['volume dos itens 1', 'volume dos itens 2'].map((k) => C.limitesA1_(ip[k]));
  const ehLivre = (a1) => { const [l, c] = lc(a1); return livres.some((g) => l >= g.l1 && l <= g.l2 && c >= g.c1 && c <= g.c2); };
  // 01/10/2026: o Sheets mostra o aviso da trava também para quem abre ou fecha um grupo com célula travada dentro
  // (o Mizuki o viu ao clicar no + do painel de XP). Fórmula em coluna ou linha de grupo fica sem trava.
  const emGrupo = (l, c) => spec.grupos.col.some((g) => c >= g[0] && c <= g[1]) || spec.grupos.lin.some((g) => l >= g[0] && l <= g[1]);
  const semTrava = (a1) => { const [l, c] = lc(a1); return ehLivre(a1) || emGrupo(l, c); };
  ok(`as ${formulas.filter((f) => !semTrava(f)).length} fórmulas da aba estão dentro de uma das ${spec.protegidas.length} faixas travadas, fora o Volume dos itens e o que mora em grupo`,
     formulas.every((f) => semTrava(f) ? !cobre(f) : cobre(f)), formulas.filter((f) => semTrava(f) ? cobre(f) : !cobre(f)).slice(0, 6).join(', '));
  ok('nenhuma faixa travada encosta em coluna ou linha de grupo: abrir e fechar o painel de XP e o treino não mostra o aviso da trava',
     spec.protegidas.every((f) => { const g = C.limitesA1_(f); return !spec.grupos.col.some((x) => g.c1 <= x[1] && g.c2 >= x[0]) && !spec.grupos.lin.some((x) => g.l1 <= x[1] && g.l2 >= x[0]); }),
     spec.protegidas.filter((f) => { const g = C.limitesA1_(f); return spec.grupos.col.some((x) => g.c1 <= x[1] && g.c2 >= x[0]) || spec.grupos.lin.some((x) => g.l1 <= x[1] && g.l2 >= x[0]); }).join(', '));
  const valorDe = (a1) => { const [l, c] = lc(a1); const t = spec.vals.find((x) => x[0] === l && x[1] === c); return t ? String(t[2]) : ''; };
  ok('cada regra de cor de aviso procura um texto que a fórmula da própria caixa escreve',
     spec.condicional.length >= 5 && spec.condicional.every((r) => r.faixas.every((a1) => valorDe(a1).includes(r.contem))),
     spec.condicional.filter((r) => !r.faixas.every((a1) => valorDe(a1).includes(r.contem))).map((r) => r.contem).join(', '));
  // 01/10/2026, achado do Mizuki: a linha é da planilha inteira, e uma linha de título mais alta engordava a linha
  // da lista de missões que caía nela. Do cabeçalho para baixo, toda linha tem a altura comum.
  const altas = Object.keys(spec.alturas).map(Number).filter((l) => l > 7);
  ok('do cabeçalho para baixo toda linha da aba tem a mesma altura (nenhuma linha gorda no meio de uma lista)', altas.length === 0, 'linhas ' + altas.join(', '));
  ok('a aba fecha o treino em grupo de linhas aberto e o painel em grupo de colunas fechado',
     spec.grupos && spec.grupos.lin.length === 1 && spec.grupos.lin[0][2] === false && spec.grupos.col[0][2] === true
     && spec.grupos.col[0][1] === spec.cols && spec.grupos.col[0][3] === 1);
  const [painel, ext] = spec.grupos.col;
  ok('a extensão é um segundo grupo de colunas, dentro do painel, fechado, e guarda as duas tabelas a mais',
     spec.grupos.col.length === 2 && ext[2] === true && ext[3] === 2 && ext[0] > painel[0] && ext[1] === painel[1]
     && [3, 4].every((n) => { const g = C.limitesA1_(ip['missões ' + n]); return g.c1 >= ext[0] && g.c2 <= ext[1]; })
     && [1, 2].every((n) => { const g = C.limitesA1_(ip['missões ' + n]); return g.c2 < ext[0]; }), JSON.stringify(spec.grupos.col));
  const tam = [1, 2, 3, 4].map((n) => { const g = C.limitesA1_(ip['missões ' + n]); return (g.l2 - g.l1 + 1) + 'x' + (g.c2 - g.c1 + 1); });
  ok('as quatro tabelas de missão têm o mesmo tamanho', new Set(tam).size === 1, tam.join(', '));
  const titulos = spec.merges.filter((m) => spec.vals.some((t) => t[0] === m[0] && t[1] === m[1] && t.length > 3 && spec.estilos[t[3]][0] === 'Oswald' && spec.estilos[t[3]][1] >= 12 && m[0] > 7));
  ok('todo título de seção ocupa duas linhas mescladas', titulos.length >= 8 && titulos.every((m) => m[2] - m[0] === 1), JSON.stringify(titulos.filter((m) => m[2] - m[0] !== 1)));
}

console.log('');
if (falhas) { console.log(`>>> ${falhas} FALHA(S) NO SCRIPT DA FICHA PESSOAL`); process.exit(1); }
console.log('>>> O SCRIPT DA FICHA PESSOAL FAZ O QUE FOI COMBINADO');
