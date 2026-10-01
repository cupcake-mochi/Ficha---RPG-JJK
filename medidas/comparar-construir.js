// Compara a planilha que DUAS versões do script montam, no Sheets de mentira: a de uma revisão do git e a que está na
// pasta. Serve para mexer no construir() (juntar chamadas, mudar a ordem das etapas) e provar que a planilha sai igual.
//
// Por que existe (01/10/2026): o construir() estourou os seis minutos do Apps Script, e a montagem foi reescrita para
// ir menos vezes ao servidor. O que se cobra é que só o caminho mudou, e não o que fica na planilha: valor, fórmula,
// formato, borda, mesclagem, nota, menu, caixa de seleção, grupo, altura, largura e as células travadas.
//
//   node medidas/comparar-construir.js            compara com o último commit (HEAD)
//   node medidas/comparar-construir.js c8c7ba2    compara com outra revisão
//
// As abas que a versão antiga tinha e a nova não tem são tiradas da antiga antes de montar, e o programa diz quais.
'use strict';
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
const RAIZ = path.dirname(__dirname);
const { criaSheets, retrato, CHAMADAS, zeraChamadas } = require('./sheets-de-mentira.js');

const rev = process.argv[2] || 'HEAD';
const doGit = (arq) => execFileSync('git', ['show', rev + ':' + arq], { cwd: RAIZ, maxBuffer: 1 << 28 }).toString('utf8');
const daPasta = (arq) => fs.readFileSync(path.join(RAIZ, arq), 'utf8');
// o ABAS como o script o usa, com as fileiras copiadas já escritas por extenso (expandirCopias_, no Ficha.gs)
const abasDe = (src) => { const c = {}; require('vm').createContext(c); require('vm').runInContext(src, c); return JSON.parse(JSON.stringify(require('vm').runInContext('ABAS', c))); };

const novo = { ficha: daPasta('apps-script/Ficha.gs'), codigo: daPasta('apps-script/Codigo.gs') };
const velho = { ficha: doGit('apps-script/Ficha.gs'), codigo: doGit('apps-script/Codigo.gs') };
const nomesNovos = abasDe(novo.ficha).map((a) => a.nome);
const sairam = abasDe(velho.ficha).map((a) => a.nome).filter((n) => !nomesNovos.includes(n));
// 01/10/2026: a aba que só existe na versão da pasta (a FICHA AMALDIÇOADA e a DADOS_AM, quando entraram) não tem montagem
// antiga para comparar. Ela fica de fora da comparação, e o que se cobra é que as outras não mudem por causa dela.
const nomesVelhos = abasDe(velho.ficha).map((a) => a.nome);
const entraram = nomesNovos.filter((n) => !nomesVelhos.includes(n));

let falhas = 0;
const ok = (nome, cond, det = '') => { console.log((cond ? '  ok    ' : '  FALHA ') + nome + (cond ? '' : '  <- ' + det)); if (!cond) falhas++; };

function monta(v, tirar) {
  zeraChamadas();
  const S = criaSheets(v.ficha, v.codigo);
  if (tirar.length) require('vm').runInContext('ABAS = ABAS.filter(function (a) { return ' + JSON.stringify(tirar) + '.indexOf(a.nome) < 0; });', S.ctx);
  S.ctx.construir();
  return { retrato: retrato(S.P), chamadas: Object.assign({}, CHAMADAS), registro: S.P.registro };
}

console.log(`A MONTAGEM DE ${rev} CONTRA A DA PASTA`);
if (sairam.length) console.log(`  (as abas ${sairam.join(', ')} existem em ${rev} e não existem mais: saem da montagem antiga antes de comparar)`);
// 1. o desenho: o ABAS das abas que ficam é o mesmo?
if (entraram.length) console.log(`  (as abas ${entraram.join(', ')} são novas na pasta e não existem em ${rev}: ficam fora da comparação)`);
const specVelho = abasDe(velho.ficha).filter((a) => !sairam.includes(a.nome)), specNovo = abasDe(novo.ficha).filter((a) => !entraram.includes(a.nome));
const mudou = specNovo.filter((a, i) => JSON.stringify(a) !== JSON.stringify(specVelho[i])).map((a) => a.nome);
ok(`o desenho das ${specNovo.length} abas que ficam (o ABAS) é o mesmo das duas versões`, specNovo.length === specVelho.length && !mudou.length, 'mudou: ' + mudou.join(', '));

// 2. a planilha montada
const A = monta(velho, sairam), B = monta(novo, []);
ok('as abas nascem na mesma ordem, e a planilha termina no mesmo idioma', A.retrato.ordem.join('|') === B.retrato.ordem.filter((n) => !entraram.includes(n)).join('|') && A.retrato.idioma === B.retrato.idioma,
   A.retrato.ordem.join(', ') + ' / ' + B.retrato.ordem.join(', '));
ok('os intervalos nomeados são os mesmos', JSON.stringify(A.retrato.nomeados) === JSON.stringify(B.retrato.nomeados), JSON.stringify(B.retrato.nomeados));
const PARTES = { tamanho: 'o tamanho', oculta: 'oculta ou à vista', grade: 'a grade', valores: 'os valores', formulas: 'as fórmulas', formato: 'o formato de cada célula', bordas: 'as bordas',
  mesclagens: 'as mesclagens', notas: 'as notas', menus: 'os menus suspensos', caixas: 'as caixas de seleção', numeros: 'o formato de número', cores_de_aviso: 'as regras de cor',
  grupos: 'os grupos que fecham', larguras: 'as larguras', alturas: 'as alturas', travadas: 'as células travadas' };
for (const nome of B.retrato.ordem) {
  const a = A.retrato.abas[nome], b = B.retrato.abas[nome], difs = [];
  if (entraram.includes(nome)) { console.log('  --    ' + nome + ': nova na pasta, sem montagem antiga para comparar'); continue; }
  if (!a) { ok(nome + ': existe nas duas montagens', false); continue; }
  for (const k of Object.keys(PARTES)) {
    const ja = JSON.stringify(a[k]), jb = JSON.stringify(b[k]);
    if (ja === jb) continue;
    // a primeira diferença, para quem for consertar
    let onde = '';
    if (a[k] && typeof a[k] === 'object' && !Array.isArray(a[k])) {
      const chave = [...new Set([...Object.keys(a[k]), ...Object.keys(b[k])])].find((x) => JSON.stringify(a[k][x]) !== JSON.stringify(b[k][x]));
      onde = ` (${chave}: ${JSON.stringify(a[k][chave])} -> ${JSON.stringify(b[k][chave])})`;
    }
    difs.push(PARTES[k] + onde);
  }
  const conta = `${Object.keys(b.valores).length} valores, ${Object.keys(b.formulas).length} fórmulas, ${Object.keys(b.formato).length} células com formato, ${Object.keys(b.bordas).length} lados de borda, ` +
    `${b.mesclagens.length} mesclagens, ${Object.keys(b.notas).length} notas, ${Object.keys(b.menus).length} células com menu, ${Object.keys(b.travadas).length} células travadas`;
  ok(`${nome}: igual nas duas montagens (${conta})`, !difs.length, difs.join(' · ').slice(0, 600));
}

// 3. o peso: quantas vezes cada montagem chama o Sheets
console.log('\nO PESO, EM CHAMADAS AO SHEETS');
const PESADAS = ['Range.merge', 'Range.mergeAcross', 'Range.mergeVertically', 'Range.setFormulas', 'Range.setFormula', 'Range.protect', 'Protection.setDescription', 'Protection.setWarningOnly', 'Range.setNote', 'Range.setNotes', 'Range.clearNote',
  'Range.getMergedRanges', 'Range.getFormula', 'Range.getValue', 'Range.isPartOfMerge', 'Range.setDataValidation', 'RangeList.setBorder', 'Range.insertCheckboxes', 'Spreadsheet.moveActiveSheet', 'Spreadsheet.setActiveSheet',
  'Sheet.getMaxColumns', 'Sheet.getMaxRows', 'Range.setValues', 'Range.setValue', 'Range.getValues', 'Range.getFormulas', 'Range.getNotes'];
const soma = (c) => Object.values(c).reduce((n, x) => n + x, 0);
console.log('  ' + 'chamada'.padEnd(30) + rev.slice(0, 10).padStart(10) + 'pasta'.padStart(10));
for (const k of PESADAS) if ((A.chamadas[k] || 0) !== (B.chamadas[k] || 0)) console.log('  ' + k.padEnd(30) + String(A.chamadas[k] || 0).padStart(10) + String(B.chamadas[k] || 0).padStart(10));
console.log('  ' + 'TODAS AS CHAMADAS'.padEnd(30) + String(soma(A.chamadas)).padStart(10) + String(soma(B.chamadas)).padStart(10));

console.log(falhas ? `\n>>> ${falhas} DIFERENÇA(S) ENTRE AS DUAS MONTAGENS` : '\n>>> AS DUAS MONTAGENS DEIXAM A MESMA PLANILHA');
process.exit(falhas ? 1 : 0);
