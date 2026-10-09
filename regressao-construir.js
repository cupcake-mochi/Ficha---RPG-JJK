// Roda no node, sem Sheets: o construir() inteiro, do começo ao fim, num Sheets de mentira que é RIGOROSO.
//
// Por que existe (01/10/2026): o construir() ganhou a FICHA PESSOAL — nota de caixa, formato de número, cor de aviso,
// grupo de linhas, grupo de colunas dentro de outro, fórmula gravada em lote, trava por faixa — e nenhum validador
// executava esse caminho. Os outros testes rodam função a função; este roda o script como o editor do Apps Script roda.
//
// O que o Sheets de mentira cobra, porque o de verdade cobra:
//   - método que não existe no Apps Script estoura (a lista de nomes mora em REAIS, e não sai do código testado);
//   - faixa fora do tamanho da aba estoura;
//   - matriz de tamanho diferente da faixa estoura (setValues, setBackgrounds, setFormulas...);
//   - mesclar por cima de um pedaço de outra mesclagem estoura;
//   - pedir um grupo de linhas ou de colunas que não existe estoura.
// Depois do construir() ele confere o que ficou na planilha, e usa a planilha montada: escolhe o Caminho na FICHA,
// marca um grupo de treino e anota uma missão, passando pelo onEdit de verdade.
//
// node regressao-construir.js
'use strict';
const fs = require('fs'), path = require('path');
const RAIZ = __dirname;
const GS = fs.readFileSync(path.join(RAIZ, 'apps-script', 'Codigo.gs'), 'utf8');
// 06/10/2026: a INVOCAÇÕES e a DADOS_INVOC moram no Invocacoes.gs, que se junta ao ABAS quando carrega
const FICHA_SRC = fs.readFileSync(path.join(RAIZ, 'apps-script', 'Ficha.gs'), 'utf8') + '\n' + fs.readFileSync(path.join(RAIZ, 'apps-script', 'Invocacoes.gs'), 'utf8');
// 05/10/2026: o texto das habilidades mora num terceiro arquivo do projeto, e o Apps Script junta os .gs num escopo só
const HAB_SRC = fs.readFileSync(path.join(RAIZ, 'apps-script', 'Habilidades.gs'), 'utf8');
// O ABAS como o script o usa: o Ficha.gs escreve por extenso, quando carrega, as fileiras de cartas que são cópia
// (expandirCopias_). Lido como texto, ele viria só com a primeira fileira de cada tipo.
const ABAS = (() => { const c = {}; require('vm').createContext(c); require('vm').runInContext(FICHA_SRC, c); return JSON.parse(JSON.stringify(require('vm').runInContext('ABAS', c))); })();

let falhas = 0;
const ok = (nome, cond, det = '') => { console.log((cond ? '  ok    ' : '  FALHA ') + nome + (cond ? '' : '  <- ' + det)); if (!cond) falhas++; };

const { criaSheets, retrato, partes, letras, numero, CHAMADAS, zeraChamadas } = require('./medidas/sheets-de-mentira.js');

// ---------------------------------------------------------------------------------------------
console.log('O construir() DO COMEÇO AO FIM');
const S = criaSheets(FICHA_SRC, HAB_SRC + '\n' + GS);
let erro = null;
try { S.ctx.construir(); } catch (e) { erro = e; }
ok('o construir() roda inteiro, sem chamar nada que o Apps Script não tem e sem sair de nenhuma aba', !erro, erro ? erro.message : '');
if (erro) { console.log('\n>>> O construir() PAROU: ' + erro.message); process.exit(1); }
const { P } = S;
ok('as abas nascem na ordem do ABAS, e a planilha termina em português', P.abas.map((a) => a.nome).join('|') === ABAS.map((a) => a.nome).join('|') && P.locale === 'pt_BR',
   P.abas.map((a) => a.nome).join(', ') + ' · ' + P.locale);
ok('cada aba fica do tamanho que o gerador mediu', ABAS.every((s) => { const A = S.acha(s.nome); return A.maxR === s.rows && A.maxC === s.cols; }),
   ABAS.map((s) => { const A = S.acha(s.nome); return `${s.nome} ${A.maxR}x${A.maxC} (${s.rows}x${s.cols})`; }).join(' · '));
ok('as ocultas ficam ocultas, e só elas', ABAS.every((s) => S.acha(s.nome).oculta === !!s.oculta));
const formulasDoAbas = (s) => s.vals.filter((t) => typeof t[2] === 'string' && t[2][0] === '=');
// 07/10/2026: as linhas da lista do conjunto da INVOCAÇÕES saem do ABAS como referência à célula do texto, e o acabamento
// as troca pela ligação até a ficha, que cita a mesma célula. Só elas chegam diferentes, e só desse jeito.
const chegou = (s, t) => { const f = S.acha(s.nome).f.get(t[0] + ',' + t[1]);
  return f === t[2] || (s.nome === 'INVOCAÇÕES' && t[1] === 4 && /^=HYPERLINK\("#gid=\d+&range=[A-Z]+\d+",/.test(f || '') && f.endsWith(',' + t[2].slice(1) + ')')); };
ok('toda fórmula do ABAS chega à célula dela, igual (as linhas da lista de invocações, dentro da ligação)',
   ABAS.every((s) => formulasDoAbas(s).every((t) => chegou(s, t))),
   ABAS.map((s) => s.nome + ' ' + formulasDoAbas(s).filter((t) => !chegou(s, t)).length).join(' · '));
const totalF = ABAS.reduce((n, s) => n + formulasDoAbas(s).length, 0);
// 01/10/2026: o construir() estourou os seis minutos do Apps Script, e a montagem passou a ir menos vezes ao servidor.
// As fórmulas vão na mesma gravação dos valores, e por isso toda aba tem de existir antes de a primeira ser preenchida.
// 01/10/2026: os saltos da FICHA AMALDIÇOADA são a exceção. A ligação pede o número da aba, que só existe depois que ela
// nasce, e por isso o acabamento grava uma fórmula por salto.
const nSaltos = [...S.acha('FICHA AMALDIÇOADA').f.values()].filter((f) => f.startsWith('=HYPERLINK(')).length;
// 07/10/2026: e as doze linhas da lista do conjunto da INVOCAÇÕES, que levam cada uma até a ficha dela
const INV_ = S.acha('INVOCAÇÕES');
const ligacoes = [...INV_.f.entries()].filter(([, f]) => f.startsWith('=HYPERLINK('));
{
  // cada linha da lista leva ao número da lombada da ficha dela: uma ficha por linha, todas diferentes, na coluna da lombada
  const specI = ABAS.find((s) => s.nome === 'INVOCAÇÕES');
  const alvos = ligacoes.map(([k, f]) => /&range=([A-Z]+)(\d+)"/.exec(f)).filter(Boolean).map((m) => m[1] + m[2]);
  const numeros = alvos.map((a1) => { const m = /^([A-Z]+)(\d+)$/.exec(a1); let c = 0; for (const ch of m[1]) c = c * 26 + ch.charCodeAt(0) - 64; return INV_.v.get(m[2] + ',' + c); });
  ok('cada linha da lista de invocações leva ao número da ficha dela, de 1 a 12, e a ligação mostra o texto da linha',
     alvos.length === 12 && new Set(alvos).size === 12 && numeros.join(',') === '1,2,3,4,5,6,7,8,9,10,11,12'
     && ligacoes.every(([k, f]) => /,DADOS_INVOC!\$[A-Z]+\$\d+\)$/.test(f)) && !!specI, `alvos ${alvos.join(' ')} · números ${numeros.join(',')}`);
}
ok(`as ${totalF} fórmulas vão junto com os valores, numa gravação por aba: setFormula só nos ${nSaltos} saltos da FICHA AMALDIÇOADA e nas ${ligacoes.length} linhas da lista de invocações`, !CHAMADAS['Range.setFormulas'] && (CHAMADAS['Range.setFormula'] || 0) === nSaltos + ligacoes.length && nSaltos === 10 && ligacoes.length === 12,
   `${CHAMADAS['Range.setFormulas'] || 0} chamadas de setFormulas, ${CHAMADAS['Range.setFormula'] || 0} de setFormula`);
const reg = S.P.registros, ondeNo = (t) => reg.findIndex((l) => l.indexOf(t) >= 0);
ok('todas as abas nascem antes de a primeira ser preenchida, e cada etapa vai para o registro na hora, com o tempo dela',
   ondeNo('abas criadas') === 0 && ABAS.every((s, i) => ondeNo('· ' + s.nome + ' (') === i + 1) && ['menus', 'cor de estado', 'notas', 'caixa da paleta', 'travas de antes'].every((t) => ondeNo('· ' + t + ' (') > ABAS.length)
   && /^FICHA PRONTA em \d+s · .* · tempos: abas criadas /.test(reg[reg.length - 1]), reg.map((l) => l.slice(0, 40)).join(' | ').slice(0, 400));
ok('nenhuma fórmula é gravada antes de a aba que ela cita existir e ter o tamanho dela, nem com a planilha fora do inglês', !S.P.orfas.length,
   `${S.P.orfas.length}: ${S.P.orfas.slice(0, 3).join(' · ')}`);
const totalM = ABAS.reduce((n, s) => n + s.merges.length, 0), chM = (CHAMADAS['Range.merge'] || 0) + (CHAMADAS['Range.mergeAcross'] || 0) + (CHAMADAS['Range.mergeVertically'] || 0);
ok(`as ${totalM} mesclagens vão em lotes: menos de um terço em chamadas`, chM > 0 && chM < totalM / 3, `${chM} chamadas`);
ok('nenhuma etapa lê a planilha célula a célula: a mesclagem, a fórmula e o valor de uma célula são lidos de matriz',
   !CHAMADAS['Range.getFormula'] && (CHAMADAS['Range.isPartOfMerge'] || 0) <= ABAS.reduce((n, s) => n + (s.copias || []).reduce((m, k) => m + (k[5] ? k[5].length : 1), 0), 0) && (CHAMADAS['Range.getMergedRanges'] || 0) <= 5 && (CHAMADAS['Range.getValue'] || 0) <= 5 && !CHAMADAS['Spreadsheet.moveActiveSheet'],
   `getFormula ${CHAMADAS['Range.getFormula'] || 0}, isPartOfMerge ${CHAMADAS['Range.isPartOfMerge'] || 0}, getMergedRanges ${CHAMADAS['Range.getMergedRanges'] || 0}, getValue ${CHAMADAS['Range.getValue'] || 0}, moveActiveSheet ${CHAMADAS['Spreadsheet.moveActiveSheet'] || 0}`);
const PESO_DA_MONTAGEM = Object.assign({}, CHAMADAS);
// 01/10/2026: a DADOS_AM tem uma linha de conta por feitiço, com 75 fórmulas iguais a menos da linha. Só a primeira
// linha de cada retângulo vem no ABAS; o resto é a cópia dela para baixo, com as referências andando.
const { deslocaFormula } = require('./medidas/sheets-de-mentira.js');
const blocos = ABAS.flatMap((s) => (s.abaixo || []).map((b) => [s.nome, b]));
ok(`os ${blocos.length} retângulos preenchidos para baixo chegam até a última linha, com a referência de cada linha andando`,
   blocos.length > 0 && blocos.every(([nome, b]) => { const A = S.acha(nome); for (let c = b[1]; c <= b[3]; c++) { const base = A.f.get(b[0] + ',' + c);
     if (!base) return false; for (let r = b[0] + 1; r <= b[2]; r++) if (A.f.get(r + ',' + c) !== deslocaFormula(base, r - b[0], 0)) return false; } return true; })
   && blocos.some(([nome, b]) => { const A = S.acha(nome); return A.f.get(b[2] + ',' + b[1]) !== A.f.get(b[0] + ',' + b[1]); }));
ok('as fileiras de cartas da FICHA AMALDIÇOADA vêm por cópia de formato, e a montagem diz isso no registro', /FICHA AMALDIÇOADA: [^·]*fileiras copiadas/.test(P.registro || ''));
ok('toda mesclagem do ABAS existe na aba', ABAS.every((s) => s.merges.every((m) => S.acha(s.nome).merges.some((x) => x.join() === m.join()))));
// as mesclagens em lote não podem mesclar nada a mais: fora o que o ABAS pede, só a caixa de cada imagem e a da paleta
const aMais = ABAS.map((s) => { const pedidas = new Set(s.merges.map((m) => m.join()).concat(s.imgs.map((im) => [im[0], im[1], im[2], im[3]].join())));
  const daPaleta = Object.values(P.nomeados).filter((r) => r.getSheet().getName() === s.nome).map((r) => [r.getRow(), r.getColumn(), r.getLastRow(), r.getLastColumn()].join());
  return S.acha(s.nome).merges.map((m) => m.join()).filter((m) => !pedidas.has(m) && !daPaleta.includes(m)).map((m) => s.nome + ' ' + m); }).flat();
ok('nenhuma aba tem mesclagem que o ABAS não pede', !aMais.length, aMais.slice(0, 4).join(' · '));
ok('todo menu do ABAS vira validação na célula dele',
   ABAS.every((s) => (s.dv || []).every((d) => d[0].replace(/\$/g, '').split(' ').every((f) => { const p = partes(f); return S.acha(s.nome).dv.has(p.r + ',' + p.c); }))));
ok('toda caixa de seleção medida vira caixa', ABAS.every((s) => (s.caixas || []).every((c) => S.acha(s.nome).caixas.has(c[1] + ',' + c[0]) && S.acha(s.nome).caixas.has((c[1] + c[2] - 1) + ',' + c[0]))));
ok('a caixa da paleta nasce na CARTEIRA, com os três intervalos nomeados', ['PALETA_ESCOLHIDA', 'PALETA_ROTULO', 'PALETA_AVISO'].every((n) => P.nomeados[n]) && /paleta: criada em CARTEIRA!/.test(P.registro || ''),
   String(P.registro).slice(0, 200));
// 03/10/2026: a moldura saiu de dentro da caixa da foto, que nasce vazia (ver ficha-v01/moldura_foto.py), e a caixa da
// paleta, que se ancora na foto, não pode ir parar embaixo de outra imagem. O lugar é o que o Mizuki aprovou no Kaori.xlsx
// em 18/09/2026, o mesmo do regressao-paleta.js: o rótulo em C26:I26, o valor em C27:M28 e o aviso em C29:M29.
{ const letra = (c) => { let t = ''; while (c > 0) { const m = (c - 1) % 26; t = String.fromCharCode(65 + m) + t; c = Math.floor((c - 1) / 26); } return t; };
  const onde = (n) => { const r = P.nomeados[n]; return r ? letra(r.getColumn()) + r.getRow() + ':' + letra(r.getLastColumn()) + r.getLastRow() : '—'; };
  ok('a caixa da paleta nasce embaixo da foto, onde o Mizuki aprovou no Kaori.xlsx, com a caixa da foto vazia',
     onde('PALETA_ROTULO') === 'C26:I26' && onde('PALETA_ESCOLHIDA') === 'C27:M28' && onde('PALETA_AVISO') === 'C29:M29',
     ['PALETA_ROTULO', 'PALETA_ESCOLHIDA', 'PALETA_AVISO'].map(onde).join(' · ')); }
ok('o registro do construir() fala da ficha pessoal', /ficha pessoal: \d+ nota/.test(P.registro || ''), String(P.registro).slice(-200));

console.log('\nA FICHA PESSOAL, MONTADA');
const NOME = 'FICHA PESSOAL';
const spec = ABAS.find((a) => a.nome === NOME), A = S.acha(NOME);
ok(`as ${spec.notas.length} notas de caixa estão nas células delas`, spec.notas.every((n) => { const p = partes(n[0]); return A.notas.get(p.r + ',' + p.c) === n[1]; }));
ok('o formato de número chega à caixa dos ienes', spec.formatos.length >= 1 && spec.formatos.every((f) => { const p = partes(f[0]); return A.fmt.get(p.r + ',' + p.c) === f[1]; }));
ok(`as ${spec.condicional.length} regras de cor de aviso ficam na aba, cada uma na faixa dela`,
   A.cf.length === spec.condicional.length && A.cf.every((r, i) => r.contem === spec.condicional[i].contem && r.faixas.join() === spec.condicional[i].faixas.join()
   && (r.fundo || null) === (spec.condicional[i].fundo || null) && r.fonte === spec.condicional[i].fonte), JSON.stringify(A.cf).slice(0, 200));
const [gl] = spec.grupos.lin, [painel, ext] = spec.grupos.col;
const prof = (m, a, b) => { const s = new Set(); for (let i = a; i <= b; i++) s.add(m.get(i) || 0); return [...s].join(','); };
ok('o treino é um grupo de linhas aberto, com o botão em cima', prof(A.profL, gl[0], gl[1]) === '1' && !(A.profL.get(gl[0] - 1) || 0) && !(A.profL.get(gl[1] + 1) || 0)
   && A.fechL.length === 0 && A.posL === 'BEFORE', `profundidade ${prof(A.profL, gl[0], gl[1])}, fechados ${JSON.stringify(A.fechL)}`);
ok('o painel de XP é um grupo de colunas fechado, com o botão antes dele', prof(A.profC, painel[0], ext[0] - 1) === '1' && !(A.profC.get(painel[0] - 1) || 0)
   && A.fechC.some((g) => g[0] === painel[0] && g[1] === painel[1] && g[2] === 1) && A.posC === 'BEFORE', JSON.stringify(A.fechC));
ok('a extensão é um grupo dentro do painel, e também nasce fechada', prof(A.profC, ext[0], ext[1]) === '2' && A.fechC.some((g) => g[0] === ext[0] && g[1] === ext[1] && g[2] === 2), JSON.stringify(A.fechC));
ok('a extensão fecha antes do painel (de dentro para fora)', A.fechC.findIndex((g) => g[2] === 2) < A.fechC.findIndex((g) => g[2] === 1));
// 07/10/2026: as travas de aviso saíram da ficha. A conta em que alguém escreve por cima volta pelo onEdit (mais abaixo)
ok('nenhuma aba nasce com trava: a conta em que alguém escreve por cima volta sozinha', S.P.abas.every((a) => !a.prot.length) && ABAS.every((a) => !('protegidas' in a)),
   S.P.abas.filter((a) => a.prot.length).map((a) => `${a.nome}: ${a.prot.length}`).join(', '));
const F = S.acha('FICHA'), idx = S.ctx.indice();
ok('na FICHA, o XP e o EQUIPAMENTO são conta, e o EQUIPAMENTO não tem mais menu',
   [idx['xp'], idx['equipamento']].every((a1) => { const p = partes(a1); return F.f.has(p.r + ',' + p.c); })
   && !F.dv.has(partes(idx['equipamento']).r + ',' + partes(idx['equipamento']).c), `xp ${idx['xp']}, equipamento ${idx['equipamento']}`);
ok('o nível da FICHA continua digitável: valor solto', (() => { const p = partes(idx['nivel']); return !F.f.has(p.r + ',' + p.c); })());
const idxLivres = ['vida', 'energia', 'integridade'].map((k) => idx[k]);
// a nota de cada caixa da FICHA mora no título quando a célula de cima é texto digitado, e na própria caixa quando não é
const cabecaDe = (X, r, c) => { const m = X.merges.find((x) => r >= x[0] && r <= x[2] && c >= x[1] && c <= x[3]); return m ? [m[0], m[1]] : [r, c]; };
const notasCertas = ['defesa', 'iniciativa', 'maestria', 'nivel', 'xp', 'equipamento', 'caminho', 'trilha', 'pontos disponíveis'].map((k) => {
  const p = partes(idx[k]), [la, ca] = p.r === 1 ? [p.r, p.c] : cabecaDe(F, p.r - 1, p.c), acima = la + ',' + ca;
  const noTitulo = p.r > 1 && !F.f.has(acima) && typeof F.v.get(acima) === 'string' && F.v.get(acima).trim() !== '';
  return (noTitulo ? F.notas.has(acima) && !F.notas.has(p.r + ',' + p.c) : F.notas.has(p.r + ',' + p.c)) ? null : k;
}).filter(Boolean);
ok('as notas de regra da FICHA moram no título da caixa quando ele é texto, e na caixa quando não é', F.notas.size >= 35 && !notasCertas.length, `${F.notas.size} notas; fora do lugar: ${notasCertas}`);
const vivas = S.ctx.tabelaDaDados_(S.ss.getSheetByName('DADOS').getDataRange().getValues(), 'nota viva', ['texto da nota', 'caixa da nota']);
ok('as cinco notas que mudam com a ficha nascem escritas', vivas.length === 5 && vivas.every((n) => { const p = partes(n['caixa da nota']); return A.notas.has(p.r + ',' + p.c); }));

console.log('\nA PLANILHA MONTADA, EM USO (pelo onEdit de verdade)');
const ed = (aba, a1, value, oldValue) => ({ range: S.ss.getSheetByName(aba).getRange(a1), value, oldValue });
const t = S.ctx.caixasDeTreino_(S.ss.getSheetByName('DADOS').getDataRange().getValues());
const marcadas = () => t.armas.concat(t.grupos).filter((x) => { const p = partes(x.caixa); return A.le(p.r, p.c) === true; }).length;
let erroUso = null;
try {
  S.ss.getSheetByName('FICHA').getRange(idx['caminho']).setValue('Bastião');
  S.ctx.onEdit(ed('FICHA', idx['caminho'], 'Bastião', 'Escolha seu Caminho'));
} catch (e) { erroUso = e; }
ok('escolher Bastião na FICHA passa por todos os gatilhos dela sem erro e marca as 65 caixas de treino', !erroUso && marcadas() === 65, erroUso ? erroUso.message : marcadas() + ' marcadas');
try {
  S.ss.getSheetByName('FICHA').getRange(idx['caminho']).setValue('Emanador');
  S.ctx.onEdit(ed('FICHA', idx['caminho'], 'Emanador', 'Bastião'));
} catch (e) { erroUso = e; }
ok('trocar para Emanador deixa só Arma de Fogo e Balestra', !erroUso && marcadas() === 11, erroUso ? erroUso.message : marcadas() + ' marcadas');
const g = t.grupos.find((x) => x.categoria === 'Massa');
try { S.ss.getSheetByName(NOME).getRange(g.caixa).setValue(true); S.ctx.pessoalEditada_(ed(NOME, g.caixa, 'TRUE')); } catch (e) { erroUso = e; }
ok('marcar o grupo Massa na aba montada marca as cinco armas dele', !erroUso && marcadas() === 11 + 1 + t.armas.filter((x) => x.categoria === 'Massa').length, erroUso ? erroUso.message : marcadas() + ' marcadas');
const ip = S.ctx.indicePessoal_();
try {
  const px = partes(ip['xp total']); A.f.delete(px.r + ',' + px.c); A.v.set(px.r + ',' + px.c, 500);       // o LibreOffice é quem faz a soma; aqui o total é posto à mão
  const m3 = S.ctx.limitesA1_(ip['missões 3']);
  S.ctx.pessoalEditada_(ed(NOME, letras(m3.c1 + 1) + m3.l1, 'Longa'));
} catch (e) { erroUso = e; }
ok('anotar missão na extensão, com 500 de XP, sobe o nível da FICHA para o 4', !erroUso && F.le(partes(idx['nivel']).r, partes(idx['nivel']).c) === 4, erroUso ? erroUso.message : String(F.le(partes(idx['nivel']).r, partes(idx['nivel']).c)));
// 01/10/2026: o Mizuki digitou um número por cima do NO DOMÍNIO da FICHA AMALDIÇOADA, e a conta sumiu sem aviso.
{
  const AM = 'FICHA AMALDIÇOADA', X = S.acha(AM), spec = ABAS.find((s) => s.nome === AM);
  const rot = spec.vals.find((t) => t[2] === 'NO DOMÍNIO'), calc = [rot[0] + 1, rot[1]], chave = calc.join(',');
  const conta = X.f.get(chave), a1 = letras(calc[1]) + calc[0];
  const puras = spec.vals.filter((t) => typeof t[2] === 'string' && t[2][0] === '=' && t[0] >= 7);
  ok(`as ${puras.length} caixas calculadas da FICHA AMALDIÇOADA só apontam para uma célula: a conta mora na DADOS_AM`,
     puras.length > 700 && puras.every((t) => /^=(?:'[^']+'|[A-Z_]+)!\$?[A-Z]+\$?\d+$/.test(t[2])), puras.filter((t) => t[2].indexOf(',') >= 0).length + ' com vírgula');
  let erroAm = null;
  const antes = S.P.avisos.length;
  try { S.ss.getSheetByName(AM).getRange(a1).setValue(3); S.ctx.onEdit(ed(AM, a1, '3', '0')); } catch (e) { erroAm = e; }
  ok('digitar por cima de uma caixa calculada devolve a conta e avisa na tela', !erroAm && !!conta && X.f.get(chave) === conta && S.P.avisos.length === antes + 1,
     erroAm ? erroAm.message : `${X.f.get(chave)} · ${S.P.avisos.length - antes} aviso(s)`);
  try { S.ss.getSheetByName(AM).getRange(a1).clearContent(); S.ctx.onEdit(ed(AM, a1, undefined, '0')); } catch (e) { erroAm = e; }
  ok('apagar a caixa calculada também devolve a conta', !erroAm && X.f.get(chave) === conta, erroAm ? erroAm.message : String(X.f.get(chave)));
  // 05/10/2026, "Nome da técnica aparecer na ficha amaldiçoada" ("Espelha a CARTEIRA"): a caixa NOME DA TÉCNICA aponta para
  // o campo TÉCNICA DECLARADA da CARTEIRA; quem escreve por cima recebe a conta de volta, e o aviso diz onde se escreve. O
  // aviso da caixa calculada comum (o NO DOMÍNIO, acima) não fala da CARTEIRA.
  const rotT = spec.vals.find((t) => t[2] === 'NOME DA TÉCNICA'), lT = rotT ? [rotT[0] + 1, rotT[1]] : [0, 0];
  const aT = letras(lT[1]) + lT[0], chT = lT.join(','), contaT = X.f.get(chT), nT = S.P.avisos.length;
  try { S.ss.getSheetByName(AM).getRange(aT).setValue('Outra Técnica'); S.ctx.onEdit(ed(AM, aT, 'Outra Técnica')); } catch (e) { erroAm = e; }
  const avT = S.P.avisos[nT] || ['', ''], avComum = S.P.avisos[antes] || ['', ''];
  ok('escrever por cima do NOME DA TÉCNICA devolve a conta, e o aviso manda escrever na CARTEIRA (o da caixa comum não)',
     !erroAm && !!contaT && X.f.get(chT) === contaT && S.P.avisos.length === nT + 1 && avT[1].indexOf('CARTEIRA') >= 0
     && avComum[1].indexOf('CARTEIRA') < 0, erroAm ? erroAm.message : `${X.f.get(chT)} · ${avT[1]} · ${avComum[1]}`);
  // a caixa de escolher e a de escrever não são da conta: o onEdit não mexe nelas nem avisa
  const forma = spec.vals.find((t) => t[2] === 'Projétil'), nome = [forma[0] - 7, forma[1] + 1];
  const [aF, aN] = [letras(forma[1]) + forma[0], letras(nome[1]) + nome[0]], n0 = S.P.avisos.length;
  try {
    S.ss.getSheetByName(AM).getRange(aF).setValue('Toque'); S.ctx.onEdit(ed(AM, aF, 'Toque', 'Projétil'));
    S.ss.getSheetByName(AM).getRange(aN).setValue('Estalo'); S.ctx.onEdit(ed(AM, aN, 'Estalo'));
  } catch (e) { erroAm = e; }
  ok('escolher a Forma e escrever o nome do feitiço ficam como o jogador pôs, sem aviso',
     !erroAm && X.le(forma[0], forma[1]) === 'Toque' && X.le(nome[0], nome[1]) === 'Estalo' && S.P.avisos.length === n0,
     erroAm ? erroAm.message : `${X.le(forma[0], forma[1])} · ${X.le(nome[0], nome[1])} · ${S.P.avisos.length - n0} aviso(s)`);
  // 07/10/2026: a fórmula com conta (a linha de apoio do cabeçalho) também volta. Antes só a referência pura voltava
  const apoio = spec.vals.find((t) => typeof t[2] === 'string' && t[2][0] === '=' && t[2].indexOf('&') >= 0), aA = letras(apoio[1]) + apoio[0], n1 = S.P.avisos.length;
  try { S.ss.getSheetByName(AM).getRange(aA).setValue('x'); S.ctx.onEdit(ed(AM, aA, 'x')); } catch (e) { erroAm = e; }
  ok('a fórmula que não é referência pura também volta, com o aviso', !erroAm && !!apoio && X.f.get(apoio[0] + ',' + apoio[1]) === apoio[2] && S.P.avisos.length === n1 + 1,
     erroAm ? erroAm.message : `${X.f.get(apoio[0] + ',' + apoio[1])} · ${S.P.avisos.length - n1} aviso(s)`);
  // o salto em que alguém escreve por cima volta a ser a ligação, escrita na pontuação do português
  const salto = [...X.f.entries()].find(([, f]) => f.startsWith('=HYPERLINK(')), [sl, sc] = salto[0].split(',').map(Number), aS = letras(sc) + sl;
  try { S.ss.getSheetByName(AM).getRange(aS).setValue('x'); S.ctx.onEdit(ed(AM, aS, 'x')); } catch (e) { erroAm = e; }
  ok('o salto em que alguém escreve por cima volta a ser a ligação, com ponto e vírgula, porque a planilha está em português',
     !erroAm && /^=HYPERLINK\("#gid=\d+&range=[A-Z]+\d+";/.test(X.f.get(salto[0]) || '') && !S.P.orfas.length, erroAm ? erroAm.message : `${X.f.get(salto[0])} · ${S.P.orfas.slice(0, 2).join(' · ')}`);
}
{
  // 07/10/2026: toda caixa calculada volta, em toda aba ("Escrevi por cima da pericia e n corrigiu"). A fórmula de fábrica
  // está no ABAS como o construir() a grava, em inglês, e a planilha vive em português
  const F = S.ctx.formulaNoIdioma_;
  const casos = [['=IF(A1>0.25,"a,b",{1,2;3,4})', '=IF(A1>0,25;"a,b";{1\\2;3\\4})'], ["=SUM('FICHA, X'!A1,$B$2)*1.5+J26", "=SUM('FICHA, X'!A1;$B$2)*1,5+J26"],
                 ['=DADOS!$F$1&" · técnica, 1.5"', '=DADOS!$F$1&" · técnica, 1.5"'], ['=IF(N($J$26)=0,10,"x ""y, z"" 0.5")', '=IF(N($J$26)=0;10;"x ""y, z"" 0.5")']];
  ok('a fórmula de fábrica vira a do idioma da planilha: ponto e vírgula no argumento, vírgula no número, barra na matriz, e o que está entre aspas fica',
     casos.every(([en, pt]) => F(en, 'pt_BR') === pt && F(en, 'en_US') === en), casos.map(([en]) => F(en, 'pt_BR')).join('  '));
  let erroD = null;
  const tenta = (nomeAba, escolhe) => {
    const sp = ABAS.find((a) => a.nome === nomeAba), Y = S.acha(nomeAba), livres = S.ctx.livresDaAba_(sp);
    const t = sp.vals.find((v) => typeof v[2] === 'string' && v[2][0] === '=' && !livres[letras(v[1]) + v[0]] && escolhe(v, sp));
    const a1 = letras(t[1]) + t[0], n0 = S.P.avisos.length;
    try { S.ss.getSheetByName(nomeAba).getRange(a1).setValue('rew'); S.ctx.onEdit(ed(nomeAba, a1, 'rew')); } catch (e) { erroD = e; }
    return { t, a1, voltou: Y.f.get(t[0] + ',' + t[1]) === F(t[2], 'pt_BR'), avisos: S.P.avisos.length - n0, ficou: Y.f.get(t[0] + ',' + t[1]) || Y.le(t[0], t[1]) };
  };
  const comVirgula = (v) => v[2].replace(/"[^"]*"/g, '').includes(',');
  const naFicha = tenta('FICHA', (v, sp) => comVirgula(v) && !S.ctx.linhaSemTrava_('FICHA', v[0]));
  const naCarteira = tenta('CARTEIRA', comVirgula), naPessoal = tenta('FICHA PESSOAL', comVirgula);
  const emGrupo = tenta('FICHA PESSOAL', (v, sp) => comVirgula(v) && (sp.grupos.col.some((g) => v[1] >= g[0] && v[1] <= g[1]) || sp.grupos.lin.some((g) => v[0] >= g[0] && v[0] <= g[1])));
  ok('escrever por cima de uma conta da FICHA, da CARTEIRA ou da FICHA PESSOAL (em grupo ou não) devolve a conta, na pontuação do português, com um aviso cada',
     !erroD && [naFicha, naCarteira, naPessoal, emGrupo].every((x) => x.voltou && x.avisos === 1 && x.t[2] !== F(x.t[2], 'pt_BR')) && !S.P.orfas.length,
     erroD ? erroD.message : [naFicha, naCarteira, naPessoal, emGrupo].map((x) => `${x.a1}: ${String(x.ficou).slice(0, 50)} (${x.avisos})`).join(' · ') + ' · ' + S.P.orfas.slice(0, 2).join(' · '));
  // e não só uma de cada aba: TODA conta que não é livre volta. Era o que a trava cobria (toda fórmula, e mais nada)
  const todas = {};
  for (const nomeAba of ['FICHA', 'CARTEIRA', 'FICHA PESSOAL']) {
    const sp = ABAS.find((a) => a.nome === nomeAba), Y = S.acha(nomeAba), livres = S.ctx.livresDaAba_(sp), aba = S.ss.getSheetByName(nomeAba);
    const contas = sp.vals.filter((v) => typeof v[2] === 'string' && v[2][0] === '=' && !livres[letras(v[1]) + v[0]]);
    const naoVoltou = [];
    for (const v of contas) {
      const a1 = letras(v[1]) + v[0];
      try { aba.getRange(a1).setValue('rew'); S.ctx.onEdit(ed(nomeAba, a1, 'rew')); } catch (e) { erroD = e; }
      const f = Y.f.get(v[0] + ',' + v[1]) || '';
      // o salto e a ligação que o acabamento escreve por cima de uma referência voltam como a referência ou como a ligação
      if (f !== F(v[2], 'pt_BR') && !(f.startsWith('=HYPERLINK(') && f.endsWith(v[2].slice(1) + ')'))) naoVoltou.push(a1);
    }
    todas[nomeAba] = { contas: contas.length, livres: Object.keys(livres).length, naoVoltou };
  }
  ok(`toda conta que não é livre volta: as ${todas['FICHA'].contas} da FICHA, as ${todas['CARTEIRA'].contas} da CARTEIRA e as ${todas['FICHA PESSOAL'].contas} da FICHA PESSOAL, uma a uma`,
     !erroD && Object.values(todas).every((x) => x.contas > 5 && !x.naoVoltou.length) && todas['FICHA'].livres === 3 && !S.P.orfas.length,
     erroD ? erroD.message : Object.entries(todas).map(([k, x]) => `${k}: ${x.naoVoltou.slice(0, 5).join(',')}`).join(' · ') + ' · ' + S.P.orfas.slice(0, 2).join(' · '));
  // as caixas livres nascem com conta e são do jogador: a vida da FICHA, o Volume de um item, a vida atual da invocação
  const livre = (nomeAba, a1) => { const n0 = S.P.avisos.length; try { S.ss.getSheetByName(nomeAba).getRange(a1).setValue(7); S.ctx.onEdit(ed(nomeAba, a1, 7)); } catch (e) { erroD = e; }
    return S.ss.getSheetByName(nomeAba).getRange(a1).getValue() === 7 && S.P.avisos.length === n0; };
  const spP = ABAS.find((a) => a.nome === 'FICHA PESSOAL'), spI = ABAS.find((a) => a.nome === 'INVOCAÇÕES'), idxF = S.ctx.indice();
  // 08/10/2026 (B41): a Integridade atual da invocação é livre como a vida (duas caixas por ficha)
  ok('a vida da FICHA, o Volume de um item e a vida atual de uma invocação ficam como o jogador escreveu, sem aviso',
     !erroD && (spP.livres || []).length > 1 && (spI.livres || []).length === 24 && livre('FICHA', S.ctx.cel_(idxF, 'vida')) && livre('FICHA PESSOAL', spP.livres[1]) && livre('INVOCAÇÕES', spI.livres[4]),
     erroD ? erroD.message : `${(spP.livres || []).length} · ${(spI.livres || []).length}`);
  // se o Sheets não entender a fórmula na pontuação do português (a caixa mostra #ERROR!), ela vai como o construir() grava
  const G = S.acha('GLOSSÁRIO'), onde = 'A' + G.maxR, deVerdade = S.ctx.formulaNoIdioma_;
  let idiomas = [], erroE = null, foi = null;
  try {
    S.ss.getSheetByName('GLOSSÁRIO').getRange(onde).setValue('#ERROR!');
    S.ctx.formulaNoIdioma_ = () => "='GLOSSÁRIO'!$A$" + G.maxR;
    const trocaDeIdioma = S.ss.setSpreadsheetLocale;
    S.ss.getSheetByName('FICHA').getRange(naFicha.a1).setValue('rew');
    S.ctx.onEdit(ed('FICHA', naFicha.a1, 'rew'));
    foi = S.acha('FICHA').f.get(naFicha.t[0] + ',' + naFicha.t[1]);
  } catch (e) { erroE = e; }
  S.ctx.formulaNoIdioma_ = deVerdade;
  S.ss.getSheetByName('GLOSSÁRIO').getRange(onde).clearContent();
  ok('a conta que o Sheets não entende na pontuação do português é gravada em inglês, com a planilha em inglês por um instante, e volta ao português',
     !erroE && foi === naFicha.t[2] && S.P.locale === 'pt_BR' && !S.P.orfas.length, erroE ? erroE.message : `${foi} · ${S.P.locale} · ${S.P.orfas.slice(0, 2).join(' · ')}`);
  // a linha da lista de invocações em que alguém escreve por cima volta com a ligação até a ficha
  const IVx = S.acha('INVOCAÇÕES'), lig = [...IVx.f.entries()].find(([, f]) => f.startsWith('=HYPERLINK(')), [ll, lc] = lig[0].split(',').map(Number);
  try { S.ss.getSheetByName('INVOCAÇÕES').getRange(ll, lc).setValue('x'); S.ctx.onEdit(ed('INVOCAÇÕES', letras(lc) + ll, 'x')); } catch (e) { erroD = e; }
  ok('a linha da lista de invocações em que alguém escreve por cima volta com a ligação, com ponto e vírgula',
     !erroD && /^=HYPERLINK\("#gid=\d+&range=[A-Z]+\d+";/.test(IVx.f.get(lig[0]) || '') && !S.P.orfas.length, erroD ? erroD.message : `${IVx.f.get(lig[0])} · ${S.P.orfas.slice(0, 2).join(' · ')}`);
}
// 02/10/2026: o menu rápido da FICHA (a seção 8) só mostra o que está na FICHA AMALDIÇOADA. As caixas dele ficam fora
// da trava, e quem escreve por cima recebe a conta de volta, como na Ficha Amaldiçoada.
{
  const F2 = S.acha('FICHA'), spec = ABAS.find((s) => s.nome === 'FICHA');
  // a faixa sem trava de cada seção, achada pelo número dela na coluna D (desde 02/10/2026 a seção 7 também tem uma)
  const faixaDa = (n) => spec.sem_trava.find(([a]) => spec.vals.some((t) => t[0] === a && t[1] === 4 && String(t[2]) === String(n)));
  const [m0, m1] = faixaDa(8);
  const doMenu = spec.vals.filter((t) => t[0] >= m0 && t[0] <= m1 && typeof t[2] === 'string' && t[2][0] === '=');
  ok(`as ${doMenu.length} caixas do menu rápido só apontam para uma célula da DADOS_AM`,
     doMenu.length > 250 && doMenu.every((t) => /^=DADOS_AM!\$[A-Z]+\$\d+$/.test(t[2])), doMenu.filter((t) => !/^=DADOS_AM!\$[A-Z]+\$\d+$/.test(t[2])).slice(0, 3).map((t) => t[2]).join(' · '));
  // as fileiras que vieram por cópia de formato têm as mesclagens da primeira
  const faltam = spec.merges.filter((m) => m[0] >= m0 && m[2] <= m1 && !F2.merges.some((x) => x.join() === m.join()));
  ok(`as ${spec.merges.filter((m) => m[0] >= m0 && m[2] <= m1).length} mesclagens do menu estão na aba montada, as das fileiras copiadas também`,
     !faltam.length && (spec.copias || []).length >= 3, faltam.length + ' faltando: ' + faltam.slice(0, 3).map((m) => m.join(',')).join(' · '));
  const alvo = doMenu.find((t) => t[2].indexOf('$CA') < 0) || doMenu[0], a1 = letras(alvo[1]) + alvo[0], chave = alvo[0] + ',' + alvo[1];
  const conta = F2.f.get(chave), n2 = S.P.avisos.length;
  let erroM = null;
  try { S.ss.getSheetByName('FICHA').getRange(a1).setValue('Raio Negro'); S.ctx.onEdit(ed('FICHA', a1, 'Raio Negro')); } catch (e) { erroM = e; }
  ok('escrever por cima de uma caixa do menu rápido devolve a conta e avisa na tela', !erroM && !!conta && F2.f.get(chave) === conta && S.P.avisos.length === n2 + 1,
     erroM ? erroM.message : `${F2.f.get(chave)} · ${S.P.avisos.length - n2} aviso(s)`);
  // 02/10/2026, as Habilidades (seção 7): a etiqueta de nível e o título de cada bloco são conta na DADOS_AM, fora da trava;
  // o nome e o texto de cada carta são do jogador; e o que ele escrever numa carta acima do nível sai riscado
  const [h0, h1] = faixaDa(7);
  const daHab = spec.vals.filter((t) => t[0] >= h0 && t[0] <= h1 && typeof t[2] === 'string' && t[2][0] === '=');
  ok(`as ${daHab.length} contas das Habilidades (9 etiquetas de nível e 2 títulos) só apontam para uma célula da DADOS_AM`,
     daHab.length === 11 && daHab.every((t) => /^=DADOS_AM!\$[A-Z]+\$\d+$/.test(t[2])), daHab.map((t) => t[2]).slice(0, 3).join(' · '));
  const risca = F2.cf.filter((c) => c.riscado && /^=LEFT\(\$[A-Z]+\$\d+,4\)="Abre"$/.test(c.formula || ''));
  const etiquetas = daHab.filter((t) => risca.some((c) => c.formula.indexOf('$' + letras(t[1]) + '$' + t[0] + ',') >= 0));
  ok('a FICHA montada risca o nome e o texto das 9 cartas enquanto a etiqueta disser "Abre", e as outras regras dela continuam',
     risca.length === 9 && etiquetas.length === 9 && risca.every((c) => c.faixas.length === 2) && F2.cf.length > 9,
     `${risca.length} regra(s) de riscar, ${etiquetas.length} etiqueta(s), ${F2.cf.length} regra(s) na aba`);
  const et = daHab[0], aE = letras(et[1]) + et[0], kE = et[0] + ',' + et[1], contaE = F2.f.get(kE), n3 = S.P.avisos.length;
  try { S.ss.getSheetByName('FICHA').getRange(aE).setValue('Nível 30'); S.ctx.onEdit(ed('FICHA', aE, 'Nível 30')); } catch (e) { erroM = e; }
  ok('escrever por cima da etiqueta de nível devolve a conta e avisa na tela', !erroM && !!contaE && F2.f.get(kE) === contaE && S.P.avisos.length === n3 + 1,
     erroM ? erroM.message : `${F2.f.get(kE)} · ${S.P.avisos.length - n3} aviso(s)`);
}
// 05/10/2026, as cartas com o livro (B37): escolher o Caminho e a Trilha escreve o nome e o texto inteiro do livro em
// cada carta, e estica a caixa do texto; o que o jogador escrever numa carta fica, com o livro na nota, e a caixa estica
// junto. O esperado sai do Habilidades.gs, não daqui.
{
  const cH = {}; require('vm').createContext(cH);
  require('vm').runInContext(HAB_SRC + '; this.L = HABILIDADES_DO_LIVRO_; this.M = MEDIDA_DAS_CARTAS_;', cH);
  const LIVRO = cH.L, MED = cH.M, FA = S.acha('FICHA');
  const FI = S.ss.getSheetByName('FICHA'), DA = S.ss.getSheetByName('DADOS_AM').getDataRange().getValues(), h = DA[0];
  const cC = h.indexOf('habilidade: carta'), cN = h.indexOf('nível da carta'), cNm = h.indexOf('célula do nome'), cTx = h.indexOf('célula do texto');
  const cL = h.indexOf('célula do texto livre');
  const cartas = [], livres = [];
  for (let r = 1; r < DA.length && DA[r][cC] !== ''; r++) cartas.push({ fonte: String(DA[r][cC]).split(' ')[0], nivel: Number(DA[r][cN]), nome: DA[r][cNm], texto: DA[r][cTx] });
  for (let r = 1; r < DA.length && DA[r][cL] !== ''; r++) livres.push(DA[r][cL]);
  const linha = (fonte, dono, nivel) => LIVRO.find((l) => l.fonte === fonte && l.dono === dono && l.nivel === nivel);
  const lida = (c) => [FI.getRange(c.nome).getValue(), FI.getRange(c.texto).getValue(), FI.getRange(c.texto).getNote()];
  const doLivro = (l) => [l.nome, l.texto, ''];
  const lin = (a1) => Number(String(a1).replace(/^[A-Z]+/, ''));
  const alturas = (a1) => [...Array(MED.caixa)].map((_, k) => FA.alt.get(lin(a1) + k));
  const porLinha = (n) => Math.max(MED.minima, Math.ceil((n * MED.linha + MED.respiro) / MED.caixa));
  const esticada = (c, l) => alturas(c.texto).every((x) => x === porLinha(l.linhas));
  const escolhe = (k, v) => { const a = FI.getRange(idx[k]).getValue(); FI.getRange(idx[k]).setValue(v); S.ctx.onEdit(ed('FICHA', idx[k], v, a)); };
  const livroDa = (cam, tri, c) => c.fonte === 'Caminho' ? (linha('Caminho com a Trilha', tri, c.nivel) || linha('Caminho', cam, c.nivel)) : linha('Trilha', tri, c.nivel);
  let erroH = null;
  try { escolhe('caminho', 'Emanador'); escolhe('trilha', 'Ressonante'); } catch (e) { erroH = e; }
  ok(`escolher Emanador e Ressonante na FICHA escreve as ${cartas.length} cartas com o nome e o texto inteiro do livro, sem nota`,
     !erroH && cartas.length === 9 && cartas.every((c) => JSON.stringify(lida(c)) === JSON.stringify(doLivro(livroDa('Emanador', 'Ressonante', c)))),
     erroH ? erroH.message : JSON.stringify(lida(cartas[0])).slice(0, 120));
  const negritos = (a1) => { const x = partes(a1); return FA.ricos.get(x.r + ',' + x.c); };
  ok('o texto do livro vai como texto rico, com os subtítulos do livro em negrito ("deixar de forma legivel")',
     cartas.every((c) => JSON.stringify(negritos(c.texto)) === JSON.stringify(livroDa('Emanador', 'Ressonante', c).titulos))
     && cartas.some((c) => livroDa('Emanador', 'Ressonante', c).titulos.length > 0), JSON.stringify(cartas.map((c) => (negritos(c.texto) || []).length)));
  ok(`a caixa de cada carta estica para o texto: as ${MED.caixa} linhas dela com a altura que o livro pede`,
     cartas.every((c) => esticada(c, livroDa('Emanador', 'Ressonante', c))), JSON.stringify(cartas.map((c) => alturas(c.texto)[0])));
  const c7 = cartas.find((c) => c.fonte === 'Caminho' && c.nivel === 7);
  try { FI.getRange(c7.texto).setValue('O que eu anotei.'); S.ctx.onEdit(ed('FICHA', c7.texto, 'O que eu anotei.')); } catch (e) { erroH = e; }
  ok('o texto que o jogador escreve fica sem negrito', !erroH && negritos(c7.texto) === undefined, JSON.stringify(negritos(c7.texto)));
  ok('escrever numa carta encolhe a caixa para o texto novo e põe o livro na nota',
     !erroH && alturas(c7.texto).every((x) => x === MED.minima) && FI.getRange(c7.texto).getNote() === linha('Caminho', 'Emanador', 7).texto,
     erroH ? erroH.message : JSON.stringify(alturas(c7.texto)));
  try { escolhe('caminho', 'Incursor'); escolhe('trilha', 'Pugilista'); } catch (e) { erroH = e; }
  const j = linha('Caminho com a Trilha', 'Pugilista', 7);
  ok('o texto que o jogador escreveu fica quando o Caminho e a Trilha mudam, e o nome e a nota da carta seguem o livro',
     !erroH && !!j && JSON.stringify(lida(c7)) === JSON.stringify([j.nome, 'O que eu anotei.', j.texto]), erroH ? erroH.message : JSON.stringify(lida(c7)).slice(0, 160));
  ok('com Incursor e Pugilista, as outras cartas são as do livro, e a 7 do Caminho junta a Rajada Marcial',
     cartas.filter((c) => c !== c7).every((c) => JSON.stringify(lida(c)) === JSON.stringify(doLivro(livroDa('Incursor', 'Pugilista', c))) && esticada(c, livroDa('Incursor', 'Pugilista', c))));
  try { escolhe('caminho', 'Vanguarda'); escolhe('trilha', 'Batedor · Besta'); } catch (e) { erroH = e; }
  ok('a rota do Batedor se escolhe no menu de Trilha, e as cartas da Trilha são as da rota', !erroH && cartas.filter((c) => c.fonte === 'Trilha')
     .every((c) => JSON.stringify(lida(c)) === JSON.stringify(doLivro(linha('Trilha', 'Batedor · Besta', c.nivel)))), erroH ? erroH.message : '');
  const longo = LIVRO.reduce((a, l) => (l.linhas > a.linhas ? l : a)).texto;
  try { FI.getRange(livres[0]).setValue(longo); S.ctx.onEdit(ed('FICHA', livres[0], longo)); } catch (e) { erroH = e; }
  ok(`as ${livres.length} caixas livres (Anotações e Escolhas da Trilha) também esticam quando o jogador escreve`,
     !erroH && livres.length === 3 && alturas(livres[0]).every((x) => x > MED.minima), erroH ? erroH.message : JSON.stringify(alturas(livres[0])));
}
// 08/10/2026, do teste no Sheets: as caixas de texto fora das Habilidades também esticam. Nas de resistências e de
// imunidades "textos de aproximadamente 170 caracteres ficam cortados pela altura das caixas", o Legado do livro passa
// de 500 letras, e no pente-fino as cicatrizes cortaram com 189. O esperado é contado aqui, palavra por palavra, com a
// medida da Roboto 10 do Habilidades.gs. Cada texto do ABAS: [largura, células do texto, primeira linha, quantas, fixo].
{
  const cH = {}; require('vm').createContext(cH);
  require('vm').runInContext(HAB_SRC + '; this.M = MEDIDA_DAS_CARTAS_;', cH);
  const MED = cH.M, FA = S.acha('FICHA'), PE = S.acha('FICHA PESSOAL');
  const FI = S.ss.getSheetByName('FICHA'), FP = S.ss.getSheetByName('FICHA PESSOAL');
  const eF = (ABAS.find((a) => a.nome === 'FICHA').esticam || [])[0], eP = ABAS.find((a) => a.nome === 'FICHA PESSOAL').esticam || [];
  const larg = (t) => [...t].reduce((x, ch) => x + (MED.larguras[ch] === undefined ? MED.media : MED.larguras[ch]), 0);
  const linhas = (texto, px) => { let n = 0; texto.split('\n').forEach((par) => { n++; let l = null;
    par.split(' ').filter(Boolean).forEach((w) => { const x = larg(w); if (l === null) l = x; else if (l + MED.larguras[' '] + x <= px) l += MED.larguras[' '] + x; else { n++; l = x; } }); }); return n; };
  const somaDe = (h, c) => [...Array(c[3])].reduce((t, _, k) => t + h.get(c[2] + k), 0);
  // as alturas que o grupo pede: todas as linhas partem da comum, e cada caixa, na ordem, aumenta as dela até caber
  const pede = (x, textos) => { const h = new Map(); x.textos.forEach((c) => { for (let k = 0; k < c[3]; k++) h.set(c[2] + k, MED.minima); });
    x.textos.forEach((c, i) => { if (textos[i] === '') return; const falta = linhas(textos[i], c[0]) * MED.linha + MED.respiro - c[4] - somaDe(h, c);
      if (falta > 0) for (let k = 0; k < c[3]; k++) h.set(c[2] + k, h.get(c[2] + k) + Math.ceil(falta / c[3])); }); return h; };
  const bate = (A, x, textos) => [...pede(x, textos)].every(([l, px]) => A.alt.get(l) === px);
  // o que importa: a altura somada das linhas de cada caixa dá para todas as linhas do texto dela
  const cabe = (A, x, textos) => x.textos.every((c, i) => textos[i] === '' || somaDe(A.alt, c) + c[4] >= linhas(textos[i], c[0]) * MED.linha + MED.respiro);
  const comum = (A, x) => x.textos.every((c) => [...Array(c[3])].every((_, k) => A.alt.get(c[2] + k) === MED.minima));
  const mostra = (A, x) => JSON.stringify([...new Set(x.textos.flatMap((c) => [...Array(c[3])].map((_, k) => c[2] + k)))].map((l) => A.alt.get(l)));
  const escreve = (aba, nome, a1, v) => { aba.getRange(a1).setValue(v); S.ctx.onEdit(ed(nome, a1, v)); };
  const RES = 'Resistência a fogo, frio, eletricidade, veneno e dano cortante. Reduz o dano recebido enquanto a proteção estiver ativa, incluindo ataques repetidos e efeitos contínuos.';
  const IMU = 'Imune a medo, sono, paralisia e efeitos de veneno comuns. Esta imunidade permanece ativa durante o combate e não impede outros efeitos de controle descritos na ficha do personagem.';
  let erroE = null;
  ok('a FICHA declara a caixa de resistências e a de imunidades como caixas que esticam, pela linha de baixo delas',
     !!eF && eF.aba === 'FICHA' && eF.textos.length === 2 && eF.gatilhos.length === 2
     && eF.textos.every((c, i) => c[3] === 1 && c[4] === MED.minima && c[2] === eF.textos[0][2] && eF.gatilhos[i].split(':')[0] === c[1][0] && Number(c[1][0].replace(/^[A-Z]+/, '')) === c[2] - 1), JSON.stringify(eF));
  const [cRes, cImu] = eF.textos.map((c) => c[1][0]);
  try { escreve(FI, 'FICHA', cRes, RES); } catch (e) { erroE = e; }
  ok(`um texto de ${RES.length} letras nas resistências estica a caixa, e o texto inteiro cabe`,
     !erroE && bate(FA, eF, [RES, '']) && cabe(FA, eF, [RES, '']) && !comum(FA, eF), erroE ? erroE.message : mostra(FA, eF));
  try { escreve(FI, 'FICHA', cRes, ''); escreve(FI, 'FICHA', cImu, IMU); } catch (e) { erroE = e; }
  ok(`e um de ${IMU.length} letras só nas imunidades também: vale o texto de qualquer uma das duas`,
     !erroE && bate(FA, eF, ['', IMU]) && cabe(FA, eF, ['', IMU]) && !comum(FA, eF), erroE ? erroE.message : mostra(FA, eF));
  try { escreve(FI, 'FICHA', cRes, 'Fogo.'); } catch (e) { erroE = e; }
  ok('um texto curto numa caixa não encolhe a outra, que divide a linha com ela', !erroE && bate(FA, eF, ['Fogo.', IMU]) && cabe(FA, eF, ['Fogo.', IMU]), erroE ? erroE.message : mostra(FA, eF));
  try { escreve(FI, 'FICHA', cRes, ''); escreve(FI, 'FICHA', cImu, ''); } catch (e) { erroE = e; }
  ok('com as duas caixas vazias a linha volta à altura comum', !erroE && comum(FA, eF), erroE ? erroE.message : mostra(FA, eF));

  // os Legados: um texto do tamanho do mais comprido do livro (o de exceção "Inédito", 546 letras) e um curto
  const LONGO = 'Sua técnica não consta dos registros conhecidos. '.repeat(11).trim(), CURTO = 'Uma vez por dia, refaça um teste de perícia em que falhou.';
  const eEsp = eP.find((x) => x.aba === 'FICHA'), eTxt = eP.find((x) => x.aba === 'FICHA PESSOAL' && x.textos.length === 2), eDos = eP.find((x) => x.aba === 'FICHA PESSOAL' && x.textos.length > 2);
  ok('a FICHA PESSOAL declara as caixas dos Legados (a do texto, nela, e o espelho, na FICHA) e as seis do dossiê',
     eP.length === 3 && !!eEsp && !!eTxt && !!eDos && eEsp.textos.every((c) => c[1].length === 3 && c[3] === 2) && eTxt.textos.every((c) => c[1].length === 1)
     && eEsp.textos.every((c, i) => c[1][2] === eTxt.textos[i][1][0]) && eDos.textos.length === 6 && eDos.gatilhos.length === 6, JSON.stringify(eP).slice(0, 300));
  const [nm1, tp1, tx1] = eEsp.textos[0][1], tx2 = eEsp.textos[1][1][2];
  try { FP.getRange(nm1).setValue('Inédito'); FP.getRange(tp1).setValue('De exceção'); escreve(FP, 'FICHA PESSOAL', tx1, LONGO); } catch (e) { erroE = e; }
  const esp = ['Inédito · De exceção · ' + LONGO, ''];
  ok(`escrever um Legado de ${LONGO.length} letras estica a caixa dele na FICHA PESSOAL e o espelho da FICHA, e o texto inteiro cabe nos dois`,
     !erroE && LONGO.length >= 500 && bate(PE, eTxt, [LONGO, '']) && cabe(PE, eTxt, [LONGO, '']) && bate(FA, eEsp, esp) && cabe(FA, eEsp, esp) && !comum(PE, eTxt) && !comum(FA, eEsp),
     erroE ? erroE.message : `pessoal ${mostra(PE, eTxt)} · ficha ${mostra(FA, eEsp)}`);
  try { escreve(FP, 'FICHA PESSOAL', tx2, CURTO); } catch (e) { erroE = e; }
  ok('o segundo Legado, curto, não encolhe as caixas do primeiro', !erroE && bate(FA, eEsp, esp.slice(0, 1).concat(CURTO)) && cabe(FA, eEsp, [esp[0], CURTO]) && cabe(PE, eTxt, [LONGO, CURTO]),
     erroE ? erroE.message : `${mostra(FA, eEsp)} · ${mostra(PE, eTxt)}`);
  try { escreve(FP, 'FICHA PESSOAL', tx1, ''); FP.getRange(tp1).setValue(''); escreve(FP, 'FICHA PESSOAL', nm1, ''); escreve(FP, 'FICHA PESSOAL', tx2, ''); } catch (e) { erroE = e; }
  ok('apagar os Legados devolve as caixas à altura comum, nas duas abas', !erroE && comum(FA, eEsp) && comum(PE, eTxt), erroE ? erroE.message : `${mostra(FA, eEsp)} · ${mostra(PE, eTxt)}`);

  // o dossiê: as seis caixas num grupo só, porque dividem linhas (a personalidade com a história e os laços)
  const CIC = 'Uma cicatriz irregular atravessa o ombro esquerdo, resultado de um confronto antigo. Há pequenas marcas nas mãos e no rosto, que o personagem costuma esconder com luvas e com a gola do casaco.';
  const HIST = 'Cresceu numa oficina de bairro e aprendeu cedo a consertar o que os outros jogavam fora. '.repeat(24).trim(), PERS = 'Fala pouco, observa muito e não esquece um favor. '.repeat(16).trim();
  // cada caixa se acha pelo rótulo, que é a célula de cima dela
  const rotulo = (c) => { const x = partes(c[1][0]); return String(PE.le(x.r - 1, x.c)); };
  const noDossie = (r) => eDos.textos.findIndex((c) => rotulo(c) === r);
  const iCic = noDossie('CICATRIZES'), iHist = noDossie('HISTÓRIA'), iPers = noDossie('PERSONALIDADE');
  const divide = (a, b) => a[2] < b[2] + b[3] && b[2] < a[2] + a[3];
  const tD = eDos.textos.map(() => '');
  ok('as seis caixas do dossiê são as de texto livre, e a personalidade divide linhas com a história',
     iCic >= 0 && iHist >= 0 && iPers >= 0 && divide(eDos.textos[iPers], eDos.textos[iHist])
     && eDos.textos.map(rotulo).sort().join('|') === ['APARÊNCIA', 'CICATRIZES', 'HISTÓRIA', 'LAÇOS E ANOTAÇÕES', 'PERSONALIDADE', 'TRAÇO · UMA FRASE DA SUA HISTÓRIA'].sort().join('|'),
     JSON.stringify(eDos.textos.map(rotulo)));
  try { tD[iCic] = CIC; escreve(FP, 'FICHA PESSOAL', eDos.textos[iCic][1][0], CIC); } catch (e) { erroE = e; }
  ok(`as cicatrizes com ${CIC.length} letras esticam a caixa, e o texto inteiro cabe`, !erroE && bate(PE, eDos, tD) && cabe(PE, eDos, tD) && somaDe(PE.alt, eDos.textos[iCic]) > eDos.textos[iCic][3] * MED.minima,
     erroE ? erroE.message : mostra(PE, eDos));
  try { tD[iHist] = HIST; escreve(FP, 'FICHA PESSOAL', eDos.textos[iHist][1][0], HIST); tD[iPers] = PERS; escreve(FP, 'FICHA PESSOAL', eDos.textos[iPers][1][0], PERS); } catch (e) { erroE = e; }
  ok(`a história (${HIST.length} letras) e a personalidade (${PERS.length}), que dividem linhas, cabem as duas, e as cicatrizes continuam cabendo`,
     !erroE && bate(PE, eDos, tD) && cabe(PE, eDos, tD), erroE ? erroE.message : mostra(PE, eDos));
  try { [iCic, iHist, iPers].forEach((k) => escreve(FP, 'FICHA PESSOAL', eDos.textos[k][1][0], '')); } catch (e) { erroE = e; }
  ok('apagar os textos devolve o dossiê à altura comum', !erroE && comum(PE, eDos), erroE ? erroE.message : mostra(PE, eDos));
}
// 08/10/2026, do pente-fino no Sheets: "O link da segunda invocação chega ao cabeçalho, mas a ficha continua recolhida".
// A seleção que chega no número da ficha (onde o link cai) abre o grupo da fileira e o da coluna de fichas dela.
{
  const spI = ABAS.find((a) => a.nome === 'INVOCAÇÕES'), IV = S.ss.getSheetByName('INVOCAÇÕES'), abrir = spI.abrir || [];
  const fechado = (a) => [IV.getRowGroup(a[1], 1).isCollapsed(), IV.getColumnGroup(a[2], 1).isCollapsed()];
  const alvos = [...S.acha('INVOCAÇÕES').f.values()].filter((f) => f.startsWith('=HYPERLINK(')).map((f) => /&range=([A-Z]+\d+)"/.exec(f)[1]);
  let erroA = null, antes = null, depois = null, outra = null, fora = null;
  try {
    antes = fechado(abrir[7]);
    S.ctx.onSelectionChange({ range: IV.getRange('B3') }); fora = fechado(abrir[7]);
    S.ctx.onSelectionChange({ range: IV.getRange(abrir[7][0]) });
    depois = fechado(abrir[7]); outra = fechado(abrir[9]);
  } catch (e) { erroA = e; }
  ok('a INVOCAÇÕES declara, para as 12 fichas, a célula em que o link da lista cai e o que abrir',
     abrir.length === 12 && JSON.stringify(abrir.map((a) => a[0]).sort()) === JSON.stringify(alvos.slice().sort()), `${JSON.stringify(abrir.map((a) => a[0]))} · ${JSON.stringify(alvos)}`);
  ok('a seleção que chega na ficha 8, recolhida, abre a fileira e a coluna de fichas dela, e mais nenhuma; outra célula não abre nada',
     !erroA && JSON.stringify(antes) === '[true,true]' && JSON.stringify(fora) === '[true,true]' && JSON.stringify(depois) === '[false,false]' && outra[0] === true,
     erroA ? erroA.message : `${JSON.stringify(antes)} ${JSON.stringify(fora)} ${JSON.stringify(depois)} ${JSON.stringify(outra)}`);
  try { IV.getRowGroup(abrir[7][1], 1).collapse(); IV.getColumnGroup(abrir[7][2], 1).collapse(); } catch (e) { erroA = e; }
}
// 08/10/2026, do pente-fino: a vida ficou em 25 de 23 depois de trocar de Caminho, "sem aviso de excesso". A caixa do
// atual fica vermelha enquanto ele passar do máximo, nos três recursos, e essa regra vem antes das do atual baixo.
{
  const cf = S.acha('FICHA').cf, acima = cf.map((c, i) => [c, i]).filter(([c]) => /^=AND\(N\([A-Z]+\d+\)>0,N\([A-Z]+\d+\)>N\([A-Z]+\d+\)\)$/.test(c.formula || ''));
  const recursos = ['vida', 'energia', 'integridade'];
  ok('o atual acima do máximo fica vermelho, na vida, na energia e na integridade, e a regra vem antes das do atual baixo',
     acima.length === 3 && acima.every(([c, i], k) => c.fundo === '#C2334D' && c.faixas.join() === idx[recursos[k]].replace(/\$/g, '')
       && c.formula === `=AND(N(${idx[recursos[k] + '_max']})>0,N(${idx[recursos[k]]})>N(${idx[recursos[k] + '_max']}))`
       && /<=0\.25\)$/.test((cf[i + 1] || {}).formula || '')), JSON.stringify(acima.map(([c, i]) => [i, c.formula, c.faixas, c.fundo])).slice(0, 400));
}
// 08/10/2026 (B42): o Buff/Debuff dos máximos, da Proteção e da carga. O máximo soma a caixa na própria conta, e a caixa
// é número do jogador: o que ele digitar fica, sem aviso, e a nota diz para que serve.
{
  const FI = S.ss.getSheetByName('FICHA'), spF = ABAS.find((a) => a.nome === 'FICHA');
  const noAbas = (a1) => { const x = partes(a1); const t = spF.vals.find((v) => v[0] === x.r && v[1] === x.c); return t ? t[2] : undefined; };
  const fixa = (a1) => a1.replace(/^([A-Z]+)(\d+)$/, '$$$1$$$2');
  const pares = [['vida', 'vida_max'], ['energia', 'energia_max'], ['integridade', 'integridade_max'], ['proteção', 'proteção']];
  ok('a vida, a energia, a Integridade e a Proteção somam a caixa de Buff/Debuff delas, que nasce em 0 e não é conta',
     pares.every(([r, alvo]) => { const b = idx['buff de ' + r]; return !!b && noAbas(b) === 0 && String(noAbas(idx[alvo]) || '').indexOf('+IFERROR(VALUE(' + fixa(b) + '&""),0)') > 0; }),
     JSON.stringify(pares.map(([r, alvo]) => [r, idx['buff de ' + r], String(noAbas(idx[alvo]) || '').slice(-50)])));
  let erroB = null; const nB = S.P.avisos.length, bV = idx['buff de vida'], xB = partes(bV);
  try { FI.getRange(bV).setValue(5); S.ctx.onEdit(ed('FICHA', bV, 5)); } catch (e) { erroB = e; }
  ok('o que o jogador digita na caixa de Buff/Debuff da vida fica: não é devolvido, e não há aviso',
     !erroB && FI.getRange(bV).getValue() === 5 && !S.acha('FICHA').f.has(xB.r + ',' + xB.c) && S.P.avisos.length === nB,
     erroB ? erroB.message : `${FI.getRange(bV).getValue()} · ${S.P.avisos.length - nB} aviso(s)`);
  try { FI.getRange(bV).setValue(0); S.ctx.onEdit(ed('FICHA', bV, 0)); } catch (e) { erroB = e; }
  ok('as caixas de Buff/Debuff dos máximos e da Proteção têm nota no título',
     pares.every(([r]) => { const x = partes(idx['buff de ' + r]); return /Número negativo reduz/.test(FI.getRange(x.r - 1, x.c).getNote() || ''); })
     && /Lapidação/.test(FI.getRange(xB.r - 1, xB.c).getNote() || ''), JSON.stringify(pares.map(([r]) => { const x = partes(idx['buff de ' + r]); return (FI.getRange(x.r - 1, x.c).getNote() || '').slice(0, 30); })));
}
// 08/10/2026: os saltos são conferidos depois que a planilha volta ao português, e uma montagem não começa com outra
// rodando. Num teste no Sheets a ficha terminou em FICHA PRONTA com os 22 saltos em #ERROR!, depois de duas execuções juntas.
{
  const AM = 'FICHA AMALDIÇOADA', X = S.acha(AM), IVx = S.acha('INVOCAÇÕES');
  ok('o registro do construir() diz que os saltos foram conferidos depois do idioma, e que nenhum estava em erro',
     /saltos conferidos depois do idioma: nenhum em erro/.test(P.registros.join(' ')), P.registros.join(' ').slice(-300));
  const a1De = (k) => { const [l, c] = k.split(',').map(Number); return letras(c) + l; };
  const sAm = [...X.f.entries()].filter(([, f]) => f.startsWith('=HYPERLINK(')).map(([k]) => k), sIn = [...IVx.f.entries()].filter(([, f]) => f.startsWith('=HYPERLINK(')).map(([k]) => k);
  let erroC = null, dito = '', visto = '';
  try {
    sAm.forEach((k) => S.ss.getSheetByName(AM).getRange(a1De(k)).setValue('#ERROR!'));
    S.ss.getSheetByName('INVOCAÇÕES').getRange(a1De(sIn[0])).setValue('#ERROR!');
    S.ctx.verificar(); visto = S.P.registro;
    dito = S.ctx.conferirSaltos_(S.ss);
  } catch (e) { erroC = e; }
  ok('o verificar() acusa os saltos em erro, nas duas abas', !erroC && /FICHA AMALDIÇOADA: 10 salto\(s\) em erro/.test(visto) && /INVOCAÇÕES: 1 salto\(s\) em erro/.test(visto), erroC ? erroC.message : visto.slice(0, 300));
  ok('os saltos em #ERROR! são escritos de novo com ponto e vírgula, e o registro conta quantos eram',
     !erroC && sAm.length === 10 && /11 em erro, escritos de novo, e nenhum ficou em erro/.test(dito)
     && sAm.concat(sIn).every((k) => /^=HYPERLINK\("#gid=\d+&range=[A-Z]+\d+";/.test((sAm.indexOf(k) >= 0 ? X : IVx).f.get(k) || '')), erroC ? erroC.message : `${dito} · ${X.f.get(sAm[0])}`);
  let erroL = null; const soltas = S.P.travasSoltas || 0;
  S.P.montagemOcupada = true;
  try { S.ctx.acabar(); } catch (e) { erroL = e; }
  S.P.montagemOcupada = false;
  ok('com outra montagem rodando o acabar() para na hora, com o recado, e não mexe no idioma', !!erroL && /já tem uma montagem rodando/.test(erroL.message) && /acabar\(\)/.test(erroL.message) && S.P.locale === 'pt_BR',
     erroL ? erroL.message : 'rodou');
  const T = criaSheets(FICHA_SRC, HAB_SRC + '\n' + GS), abasAntes = T.P.abas.length;
  let erroK = null;
  T.P.montagemOcupada = true;
  try { T.ctx.construir(); } catch (e) { erroK = e; }
  ok('e o construir() também: não cria aba nenhuma nem troca o idioma', !!erroK && /já tem uma montagem rodando/.test(erroK.message) && /construir\(\)/.test(erroK.message)
     && T.P.abas.length === abasAntes && T.P.locale === 'en_US', erroK ? erroK.message : 'rodou');
  ok('a montagem que termina solta a trava', soltas >= 1, String(soltas));
}
{
  // 07/10/2026: a caixa de ± da vida de cada ficha de invocação, como a da FICHA. A vida máxima é uma conta, e o Sheets
  // de mentira não calcula: aqui ela vira número, na ficha 8 (a segunda da segunda coluna de fichas)
  const specI = ABAS.find((s) => s.nome === 'INVOCAÇÕES'), IV = S.ss.getSheetByName('INVOCAÇÕES');
  const red = specI.redutores || [];
  let erroR = null, passos = [];
  try {
    const [d, atual, temp, max] = red[7];
    const digita = (x) => { IV.getRange(d).setValue(x); S.ctx.onEdit(ed('INVOCAÇÕES', d, x)); passos.push([IV.getRange(atual).getValue(), IV.getRange(temp).getValue(), IV.getRange(d).getValue()].join('/')); };
    // a vida atual nasce apontando para a conta da DADOS_INVOC (a máxima, quando a ficha tem nome), que aqui vira número
    const m0 = /^=DADOS_INVOC!\$([A-Z]+)\$(\d+)$/.exec(IV.getRange(atual).getFormula());
    S.ss.getSheetByName('DADOS_INVOC').getRange(m0[1] + m0[2]).setValue(27);
    IV.getRange(max).setValue(27); IV.getRange(temp).setValue(4);
    digita(-9);     // a vida nasce cheia: 27, e a perda gasta os 4 de temporária primeiro
    digita(3);      // o ganho não devolve a temporária
    digita(50);     // e a vida não passa da máxima
    digita(-40);    // nem desce de zero
    // a vida atual apagada conta como cheia: a conta parte da máxima (na ficha 3)
    const [d3, atual3, , max3] = red[2];
    IV.getRange(max3).setValue(27); IV.getRange(atual3).clearContent();
    IV.getRange(d3).setValue(-5); S.ctx.onEdit(ed('INVOCAÇÕES', d3, -5));
    passos.push('em branco: ' + IV.getRange(atual3).getValue());
  } catch (e) { erroR = e; }
  ok('a caixa de ± de cada ficha de invocação aplica na vida atual e se limpa: a perda gasta a temporária primeiro, e a vida fica entre zero e a máxima',
     !erroR && red.length === 12 && new Set(red.map((x) => x[0])).size === 12 && passos.join(' ') === '22/0/ 25/0/ 27/0/ 0/0/ em branco: 22',
     erroR ? erroR.message : `${red.length} caixas · ${passos.join(' ')}`);
}
let erroSel = null;
try { S.ctx.onSelectionChange({ range: S.ss.getSheetByName(NOME).getRange('D10') }); S.ctx.onOpen({}); } catch (e) { erroSel = e; }
ok('clicar numa célula e abrir a planilha não estouram', !erroSel, erroSel ? erroSel.message : '');

console.log('\nO ACABAMENTO, SOZINHO');
// uma montagem limpa serve de referência; nela o acabar() roda de novo, e numa terceira o relógio corre
const R = criaSheets(FICHA_SRC, GS); R.ctx.construir();
const antes = JSON.stringify(retrato(R.P));
let erroAc = null;
try { R.ctx.acabar(); } catch (e) { erroAc = e; }
ok('rodar o acabar() numa ficha pronta não muda nada: mesmas notas, sem duplicar, e nenhuma trava', !erroAc && JSON.stringify(retrato(R.P)) === antes && R.P.locale === 'pt_BR'
   && /^ACABAMENTO PRONTO em /.test(R.P.registro), erroAc ? erroAc.message : R.P.registro.slice(0, 120));
// o relógio que corre: cada olhada no relógio adianta um minuto, e a montagem das abas passa do teto
let agora = 0;
class RelogioQueCorre { getTime() { agora += 60000; return agora; } }
const L = criaSheets(FICHA_SRC, GS, { Date: RelogioQueCorre });
// aqui a montagem das abas não para no meio (isso é o teste de baixo): o que se cobra é a vez passada ao acabar()
L.ctx.LIMITE_DA_EXECUCAO_ = Infinity;
let erroL = null;
try { L.ctx.construir(); } catch (e) { erroL = e; }
const semAcabamento = !L.acha('FICHA').prot.length && !L.acha('FICHA').notas.size && !L.P.nomeados['PALETA_ESCOLHIDA'];
ok('a montagem que passa do teto de tempo deixa as abas de pé, em português, e avisa que falta o acabar()',
   !erroL && semAcabamento && L.P.locale === 'pt_BR' && L.P.abas.map((a) => a.nome).join('|') === ABAS.map((a) => a.nome).join('|') && /FALTA O ACABAMENTO: rode a função acabar\(\)/.test(L.P.registro),
   erroL ? erroL.message : `${L.acha('FICHA').prot.length} travas · ${L.P.registro.slice(0, 120)}`);
try { L.ctx.acabar(); } catch (e) { erroL = e; }
ok('e o acabar() depois dela deixa a planilha igual à de uma montagem que não parou', !erroL && JSON.stringify(retrato(L.P)) === antes, erroL ? erroL.message : 'a planilha ficou diferente');
ok('o acabar() escreve a regra de cor com a planilha em inglês, como o construir()', !R.P.orfas.length && !L.P.orfas.length, R.P.orfas.concat(L.P.orfas).slice(0, 3).join(' · '));

console.log('\nA MONTAGEM QUE NÃO CABE NUMA EXECUÇÃO (07/10/2026, a INVOCAÇÕES com doze fichas)');
// o mesmo relógio que corre, agora com o limite de verdade: a montagem para antes de começar a aba que não cabe
agora = 0;
const C = criaSheets(FICHA_SRC, GS, { Date: RelogioQueCorre });
let erroC = null;
try { C.ctx.construir(); } catch (e) { erroC = e; }
const parada = () => (C.P.props.montagem_parada === undefined ? null : Number(C.P.props.montagem_parada));
const vazias = () => C.P.abas.filter((a) => !a.v.size).map((a) => a.nome);
const primeira = parada();
ok('a montagem que não cabe nos seis minutos para ANTES de começar uma aba, em português, guarda em que aba parou e pede o continuar()',
   !erroC && primeira > 0 && primeira < ABAS.length && C.P.locale === 'pt_BR' && /^A MONTAGEM PAROU ANTES DA ABA .* rode a função continuar\(\)/.test(C.P.registro)
   && C.P.registro.indexOf('ANTES DA ABA ' + ABAS[primeira].nome + ',') > 0 && C.P.abas.map((a) => a.nome).join('|') === ABAS.map((a) => a.nome).join('|')
   && vazias().join('|') === ABAS.slice(primeira).map((a) => a.nome).join('|'),
   erroC ? erroC.message : `parou em ${primeira} · vazias: ${vazias().join(', ')} · ${C.P.registro.slice(0, 120)}`);
let erroP = null;
try { C.ctx.acabar(); } catch (e) { erroP = e; }
ok('o acabar() não roda por cima de uma montagem parada: manda rodar o continuar()', !!erroP && /rode continuar\(\) antes do acabar\(\)/.test(erroP.message) && !C.acha('FICHA').prot.length,
   erroP ? erroP.message : 'não parou');
const paradas = [primeira];
let voltas = 0;
while (!erroC && parada() !== null && voltas < 30) {
  voltas++;
  try { C.ctx.continuar(); } catch (e) { erroC = e; }
  paradas.push(parada() === null ? ABAS.length : parada());
}
ok(`cada continuar() segue de onde o anterior parou e monta pelo menos uma aba: ${voltas} vez(es), paradas em ${paradas.join(', ')}`,
   !erroC && voltas >= 1 && paradas.every((p, i) => !i || p > paradas[i - 1]) && parada() === null && !vazias().length && C.P.locale === 'pt_BR',
   erroC ? erroC.message : `paradas em ${paradas.join(', ')} · vazias: ${vazias().join(', ')}`);
if (!erroC && /(FALTA O ACABAMENTO|FALTAM AS TRAVAS DO ACABAMENTO): rode a função acabar\(\)/.test(C.P.registro)) { try { C.ctx.acabar(); } catch (e) { erroC = e; } }
ok('e a planilha montada em várias execuções fica igual à de uma montagem que não parou', !erroC && JSON.stringify(retrato(C.P)) === antes, erroC ? erroC.message : 'a planilha ficou diferente');
let erroN = null;
try { C.ctx.continuar(); } catch (e) { erroN = e; }
ok('o continuar() sem montagem parada para com um recado, e não mexe em nada', !!erroN && /não há montagem parada/.test(erroN.message) && JSON.stringify(retrato(C.P)) === antes, erroN ? erroN.message : 'não parou');
// uma montagem do zero esquece a parada que houver, e esquece LOGO: se o Apps Script a cortar no meio, o continuar() não
// pode seguir de uma parada velha numa planilha que acabou de ser apagada
C.P.props.montagem_parada = '3';
const montarDeVerdade = C.ctx.montarAba_;
let cortada = null;
C.ctx.montarAba_ = () => { throw new Error('cortada no meio'); };
try { C.ctx.construir(); } catch (e) { cortada = e; }
C.ctx.montarAba_ = montarDeVerdade;
let erroV = null;
try { C.ctx.continuar(); } catch (e) { erroV = e; }
ok('a montagem cortada no meio não deixa valendo a parada de antes: o continuar() manda montar do começo',
   !!cortada && parada() === null && C.P.locale === 'pt_BR' && !!erroV && /não há montagem parada/.test(erroV.message), cortada ? `parada ${parada()} · ${erroV && erroV.message}` : 'a montagem não foi cortada');
try { C.ctx.LIMITE_DA_EXECUCAO_ = Infinity; C.ctx.TETO_DA_MONTAGEM_ = Infinity; C.ctx.TETO_DAS_TRAVAS_ = Infinity; C.ctx.construir(); } catch (e) { erroC = e; }
ok('o construir() começa do zero e esquece a montagem parada que houver', !erroC && parada() === null && JSON.stringify(retrato(C.P)) === antes && /^FICHA PRONTA em /.test(C.P.registro),
   erroC ? erroC.message : C.P.registro.slice(0, 100));

// 07/10/2026: a ficha montada antes disto tem as travas de aviso. O acabar() as tira, pela descrição que este script
// punha, e deixa a que o jogador ou o mestre criou por conta própria
let erroT = null, ficaram = null, registroT = '';
try {
  const FI_ = R.ss.getSheetByName('FICHA'), CA_ = R.ss.getSheetByName('CARTEIRA');
  FI_.getRange('D26').protect().setDescription('fórmula · FICHA!D26').setWarningOnly(true);
  FI_.getRange('J30:J31').protect().setDescription('fórmula · FICHA!J30:J31').setWarningOnly(true);
  CA_.getRange('C2').protect().setDescription('fórmula · CARTEIRA!C2').setWarningOnly(true);
  FI_.getRange('D40').protect().setDescription('do mestre: não mexer').setWarningOnly(true);
  R.ctx.acabar();
  registroT = R.P.registro;
  ficaram = R.P.abas.flatMap((a) => a.prot.map((p) => p.desc));
  R.acha('FICHA').prot.length = 0;
} catch (e) { erroT = e; }
ok('o acabar() tira as travas de fórmula de uma ficha montada antes (3) e deixa a que o mestre criou; a ficha fica igual à de uma montagem nova',
   !erroT && JSON.stringify(ficaram) === JSON.stringify(['do mestre: não mexer']) && /3 trava\(s\) de antes retirada\(s\)/.test(registroT) && JSON.stringify(retrato(R.P)) === antes,
   erroT ? erroT.message : `${JSON.stringify(ficaram)} · ${registroT.slice(0, 160)}`);

const semAba = criaSheets(FICHA_SRC, GS);
let erroS = null;
try { semAba.ctx.acabar(); } catch (e) { erroS = e; }
ok('o acabar() numa planilha sem a ficha para com um recado, e não mexe no idioma', !!erroS && /rode construir\(\) antes/.test(erroS.message) && semAba.P.locale === 'en_US', erroS ? erroS.message : 'não parou');

console.log('\nO PESO DO construir(), EM CHAMADAS');
const peso = ['Range.merge', 'Range.mergeAcross', 'Range.protect', 'Range.setValues', 'RangeList.setBorder', 'Range.setDataValidation', 'Range.setNote', 'Range.setNotes', 'Range.insertCheckboxes', 'Range.setTextRotation']
  .map((k) => k.split('.')[1] + ' ' + (PESO_DA_MONTAGEM[k] || 0)).join(' · ');
console.log('       ' + peso);

console.log('');
if (falhas) { console.log(`>>> ${falhas} FALHA(S) NO construir()`); process.exit(1); }
console.log('>>> O construir() MONTA A PLANILHA INTEIRA, E A PLANILHA MONTADA FUNCIONA');
