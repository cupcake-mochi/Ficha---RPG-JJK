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
const FICHA_SRC = fs.readFileSync(path.join(RAIZ, 'apps-script', 'Ficha.gs'), 'utf8');
// O ABAS como o script o usa: o Ficha.gs escreve por extenso, quando carrega, as fileiras de cartas que são cópia
// (expandirCopias_). Lido como texto, ele viria só com a primeira fileira de cada tipo.
const ABAS = (() => { const c = {}; require('vm').createContext(c); require('vm').runInContext(FICHA_SRC, c); return JSON.parse(JSON.stringify(require('vm').runInContext('ABAS', c))); })();

let falhas = 0;
const ok = (nome, cond, det = '') => { console.log((cond ? '  ok    ' : '  FALHA ') + nome + (cond ? '' : '  <- ' + det)); if (!cond) falhas++; };

const { criaSheets, retrato, partes, letras, numero, CHAMADAS, zeraChamadas } = require('./medidas/sheets-de-mentira.js');

// ---------------------------------------------------------------------------------------------
console.log('O construir() DO COMEÇO AO FIM');
const S = criaSheets(FICHA_SRC, GS);
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
ok('toda fórmula do ABAS chega à célula dela, igual',
   ABAS.every((s) => formulasDoAbas(s).every((t) => S.acha(s.nome).f.get(t[0] + ',' + t[1]) === t[2])),
   ABAS.map((s) => s.nome + ' ' + formulasDoAbas(s).filter((t) => S.acha(s.nome).f.get(t[0] + ',' + t[1]) !== t[2]).length).join(' · '));
const totalF = ABAS.reduce((n, s) => n + formulasDoAbas(s).length, 0);
// 01/10/2026: o construir() estourou os seis minutos do Apps Script, e a montagem passou a ir menos vezes ao servidor.
// As fórmulas vão na mesma gravação dos valores, e por isso toda aba tem de existir antes de a primeira ser preenchida.
// 01/10/2026: os saltos da FICHA AMALDIÇOADA são a exceção. A ligação pede o número da aba, que só existe depois que ela
// nasce, e por isso o acabamento grava uma fórmula por salto.
const nSaltos = [...S.acha('FICHA AMALDIÇOADA').f.values()].filter((f) => f.startsWith('=HYPERLINK(')).length;
ok(`as ${totalF} fórmulas vão junto com os valores, numa gravação por aba: setFormula só nos ${nSaltos} saltos da FICHA AMALDIÇOADA`, !CHAMADAS['Range.setFormulas'] && (CHAMADAS['Range.setFormula'] || 0) === nSaltos && nSaltos === 10,
   `${CHAMADAS['Range.setFormulas'] || 0} chamadas de setFormulas, ${CHAMADAS['Range.setFormula'] || 0} de setFormula`);
const reg = S.P.registros, ondeNo = (t) => reg.findIndex((l) => l.indexOf(t) >= 0);
ok('todas as abas nascem antes de a primeira ser preenchida, e cada etapa vai para o registro na hora, com o tempo dela',
   ondeNo('abas criadas') === 0 && ABAS.every((s, i) => ondeNo('· ' + s.nome + ' (') === i + 1) && ['menus', 'cor de estado', 'notas', 'travas', 'caixa da paleta'].every((t) => ondeNo('· ' + t + ' (') > ABAS.length)
   && /^FICHA PRONTA em \d+s · .* · tempos: abas criadas /.test(reg[reg.length - 1]), reg.map((l) => l.slice(0, 40)).join(' | ').slice(0, 400));
ok('nenhuma fórmula é gravada antes de a aba que ela cita existir e ter o tamanho dela, nem com a planilha fora do inglês', !S.P.orfas.length,
   `${S.P.orfas.length}: ${S.P.orfas.slice(0, 3).join(' · ')}`);
const totalM = ABAS.reduce((n, s) => n + s.merges.length, 0), chM = (CHAMADAS['Range.merge'] || 0) + (CHAMADAS['Range.mergeAcross'] || 0) + (CHAMADAS['Range.mergeVertically'] || 0);
ok(`as ${totalM} mesclagens vão em lotes: menos de um terço em chamadas`, chM > 0 && chM < totalM / 3, `${chM} chamadas`);
ok('nenhuma etapa lê a planilha célula a célula: a mesclagem, a fórmula e o valor de uma célula são lidos de matriz',
   !CHAMADAS['Range.getFormula'] && (CHAMADAS['Range.isPartOfMerge'] || 0) <= ABAS.reduce((n, s) => n + (s.copias || []).length, 0) && (CHAMADAS['Range.getMergedRanges'] || 0) <= 5 && (CHAMADAS['Range.getValue'] || 0) <= 5 && !CHAMADAS['Spreadsheet.moveActiveSheet'],
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
ok(`as fórmulas da aba estão travadas em ${spec.protegidas.length} faixas, só com aviso`, A.prot.length === spec.protegidas.length && A.prot.every((p) => p.aviso && p.desc.indexOf('fórmula · ' + NOME + '!') === 0),
   `${A.prot.length} travas`);
const F = S.acha('FICHA'), idx = S.ctx.indice();
const travada = (a1) => F.prot.some((p) => p.a1 === a1 && p.aviso);
ok('na FICHA, o XP e o EQUIPAMENTO são fórmula travada com aviso, e o EQUIPAMENTO não tem mais menu',
   [idx['xp'], idx['equipamento']].every((a1) => { const p = partes(a1); return F.f.has(p.r + ',' + p.c) && travada(a1); })
   && !F.dv.has(partes(idx['equipamento']).r + ',' + partes(idx['equipamento']).c), `xp ${idx['xp']}, equipamento ${idx['equipamento']}`);
ok('o nível da FICHA continua digitável: valor solto, sem trava', (() => { const p = partes(idx['nivel']); return !F.f.has(p.r + ',' + p.c) && !travada(idx['nivel']); })());
// as travas por faixa cobrem as mesmas células que a trava por célula cobria: toda fórmula, e mais nada
const idxLivres = ['vida', 'energia', 'integridade'].map((k) => idx[k]);
const cobertura = (X) => { const m = new Map(); for (const p of X.prot) { const f = partes(p.a1); for (let i = f.r; i < f.r + f.nl; i++) for (let j = f.c; j < f.c + f.nc; j++) m.set(i + ',' + j, (m.get(i + ',' + j) || 0) + (p.aviso ? 1 : 100)); } return m; };
for (const nomeT of ['FICHA', 'CARTEIRA']) {
  const X = S.acha(nomeT), cob = cobertura(X), livres = nomeT === 'FICHA' ? idxLivres.map((a1) => { const p = partes(a1); return p.r + ',' + p.c; }) : [];
  const devem = [...X.f.keys()].filter((k) => !livres.includes(k));
  const faltam = devem.filter((k) => cob.get(k) !== 1), sobram = [...cob.keys()].filter((k) => !devem.includes(k));
  ok(`${nomeT}: as ${devem.length} fórmulas estão travadas com aviso, uma vez cada, em ${X.prot.length} faixas, e nenhuma célula sem fórmula está travada`,
     !faltam.length && !sobram.length && X.prot.length < devem.length && X.prot.every((p) => p.desc === 'fórmula · ' + nomeT + '!' + p.a1), `faltam ${faltam.slice(0, 4)}, sobram ${sobram.slice(0, 4)}, ${X.prot.length} travas`);
}
// a nota de cada caixa da FICHA mora no título quando a célula de cima é texto digitado, e na própria caixa quando não é
const cabecaDe = (X, r, c) => { const m = X.merges.find((x) => r >= x[0] && r <= x[2] && c >= x[1] && c <= x[3]); return m ? [m[0], m[1]] : [r, c]; };
const notasCertas = ['defesa', 'iniciativa', 'maestria', 'nivel', 'xp', 'equipamento', 'caminho', 'trilha', 'pontos disponíveis', 'feitiços disponíveis'].map((k) => {
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
let erroSel = null;
try { S.ctx.onSelectionChange({ range: S.ss.getSheetByName(NOME).getRange('D10') }); S.ctx.onOpen({}); } catch (e) { erroSel = e; }
ok('clicar numa célula e abrir a planilha não estouram', !erroSel, erroSel ? erroSel.message : '');

console.log('\nO ACABAMENTO, SOZINHO');
// uma montagem limpa serve de referência; nela o acabar() roda de novo, e numa terceira o relógio corre
const R = criaSheets(FICHA_SRC, GS); R.ctx.construir();
const antes = JSON.stringify(retrato(R.P));
let erroAc = null;
try { R.ctx.acabar(); } catch (e) { erroAc = e; }
ok('rodar o acabar() numa ficha pronta não muda nada: mesmas notas, mesmas travas, sem duplicar', !erroAc && JSON.stringify(retrato(R.P)) === antes && R.P.locale === 'pt_BR'
   && /^ACABAMENTO PRONTO em /.test(R.P.registro), erroAc ? erroAc.message : R.P.registro.slice(0, 120));
// o relógio que corre: cada olhada no relógio adianta um minuto, e a montagem das abas passa do teto
let agora = 0;
class RelogioQueCorre { getTime() { agora += 60000; return agora; } }
const L = criaSheets(FICHA_SRC, GS, { Date: RelogioQueCorre });
let erroL = null;
try { L.ctx.construir(); } catch (e) { erroL = e; }
const semAcabamento = !L.acha('FICHA').prot.length && !L.acha('FICHA').notas.size && !L.P.nomeados['PALETA_ESCOLHIDA'];
ok('a montagem que passa do teto de tempo deixa as abas de pé, em português, e avisa que falta o acabar()',
   !erroL && semAcabamento && L.P.locale === 'pt_BR' && L.P.abas.map((a) => a.nome).join('|') === ABAS.map((a) => a.nome).join('|') && /FALTA O ACABAMENTO: rode a função acabar\(\)/.test(L.P.registro),
   erroL ? erroL.message : `${L.acha('FICHA').prot.length} travas · ${L.P.registro.slice(0, 120)}`);
try { L.ctx.acabar(); } catch (e) { erroL = e; }
ok('e o acabar() depois dela deixa a planilha igual à de uma montagem que não parou', !erroL && JSON.stringify(retrato(L.P)) === antes, erroL ? erroL.message : 'a planilha ficou diferente');
ok('o acabar() escreve a regra de cor com a planilha em inglês, como o construir()', !R.P.orfas.length && !L.P.orfas.length, R.P.orfas.concat(L.P.orfas).slice(0, 3).join(' · '));
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
