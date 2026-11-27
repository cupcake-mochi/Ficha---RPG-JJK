'use strict';
// Etapa 6 da versão rápida (26/11/2026): o atalho das edições livres no pacote do repositório.
//
// As oficiais têm o atalho (r53/atalho_livre.gs, ligado pelo preparar_atalho.js): uma edição numa célula em que o script
// não faz nada sai sem ler a planilha, e o ± da FICHA roda sem abrir o módulo. O pacote que o empacotar_script.py monta
// não tinha nenhum dos dois. Este script gera o atalho para o módulo e o catálogo do pacote (o mapa só vale para eles:
// com outro hash, ele se desliga sozinho) e grava o AtalhoLivre.gs ao lado dos outros arquivos do pacote. O onEdit do
// pacote já chama o atalho só se ele existir (typeof), então o pacote sem este arquivo continua funcionando como antes.
//
// O r53/atalho_livre.gs (o das oficiais, desenho antigo da INVOCAÇÕES) não muda: ele vale para as oficiais até a etapa 8.
//
// Uso: node r53/atalho_pacote.js <ficha .json> [pasta do pacote]
//   A ficha .json sai do r53/xlsx_para_json.py rodado no ficha-v01/ficha-projeto-m-0.1.xlsx que o monta.py grava.
//   Esse .xlsx não tem os valores das fórmulas (o openpyxl não calcula): o mapa sai das fórmulas, das células digitadas
//   e do que o módulo faz em cada célula. Conferido em 26/11 na ficha oficial exportada: com e sem os valores, o mesmo
//   mapa (ver ANDAMENTO-OTIMIZACAO.md, etapa 6).
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const { gerar } = require('./atalho_livre');

const PACOTE = path.join(__dirname, 'saidas', 'pacote-script');
const NOME = 'AtalhoLivre.gs';

/** O pacote como o projeto do Apps Script o guarda: nome sem .gs, texto sem \r (o editor tira). */
function projeto(pasta) {
  const files = fs.readdirSync(pasta).filter(n => n.endsWith('.gs') && n !== NOME).sort()
    .map(n => ({ name: n.slice(0, -3), type: 'SERVER_JS', source: fs.readFileSync(path.join(pasta, n), 'utf8').replace(/\r\n/g, '\n') }));
  if (!files.some(f => f.name === 'Codigo') || !files.some(f => f.name === 'EditorR53')) throw Error('pacote sem Codigo ou EditorR53: ' + pasta);
  return { files };
}

/** O .xlsx do monta.py não traz todas as abas que o construir() cria: as que faltam vêm do modelo (apps-script/*.gs). */
function completar(dump) {
  const vm = require('vm'), ctx = {};
  vm.runInNewContext(require(path.join(__dirname, '..', 'medidas', 'carregar-ficha')).fontes(), ctx);
  const faltam = [];
  for (const a of ctx.ABAS) {
    if (dump[a.nome]) continue;
    if ((a.abaixo || []).length) throw Error('a aba ' + a.nome + ' falta na ficha e tem fórmulas que descem: exporte de novo');
    const cells = {};
    let rows = a.rows || 1, cols = a.cols || 1;
    for (const [r, c, v] of a.vals) {
      if (v === null || v === undefined || v === '') continue;
      cells[r + ',' + c] = typeof v === 'string' && v.startsWith('=') ? { f: v, v: '' } : { v };
      rows = Math.max(rows, r); cols = Math.max(cols, c);
    }
    dump[a.nome] = { rows, cols, hidden: !!a.oculta || /^(DADOS|R53|ANALISE)/.test(a.nome), cells };
    faltam.push(a.nome);
  }
  // A DADOS_R53_CATALOGO saiu na etapa 4 (26/11/2026), mas o EditorR53.gs ainda aponta o Amparo das Famílias para ela.
  // Sem a aba, o Amparo não tem entrada digitada nenhuma: ela entra vazia e oculta, só para o rastreio não cair.
  if (!dump.DADOS_R53_CATALOGO) { dump.DADOS_R53_CATALOGO = { rows: 1, cols: 1, hidden: true, cells: {} }; faltam.push('DADOS_R53_CATALOGO (vazia)'); }
  return faltam;
}

function gerarPacote(dump, pasta = PACOTE, faltam = completar(dump)) {
  const r = gerar(projeto(pasta), dump);
  r.completadas = faltam;
  // O arquivo gerado vai sem \r (o caminho_leve.js e os testes leem por texto).
  const alvo = path.join(pasta, NOME);
  fs.writeFileSync(alvo, r.output.replace(/\r\n/g, '\n'));
  // O manifesto lista os arquivos a subir para o editor: o atalho entra nele.
  const fm = path.join(pasta, 'manifesto.json');
  if (fs.existsSync(fm)) {
    const m = JSON.parse(fs.readFileSync(fm, 'utf8')), b = fs.readFileSync(alvo);
    m.arquivos[NOME] = { bytes: b.length, sha256: crypto.createHash('sha256').update(b).digest('hex') };
    m.atalho_livre = { modulo: r.hashModulo, catalogo: r.hashCatalogo, completadas: r.completadas };
    fs.writeFileSync(fm, JSON.stringify(m, null, 2) + '\n');
  }
  return r;
}

if (require.main === module) {
  const [dumpf, pasta] = process.argv.slice(2);
  if (!dumpf) throw Error('Uso: node r53/atalho_pacote.js <ficha .json> [pasta do pacote]');
  const dump = JSON.parse(fs.readFileSync(dumpf, 'utf8')), faltam = completar(dump);
  // A ficha completada fica fora do Git, para o r53/testes/atalho_pacote.js rodar a parte integrada. Grava antes do
  // gerar: a força bruta deixa marcas nas células que ela cria (as vazias ficam com o último valor tentado).
  const guardar = path.join(__dirname, '..', 'nuvem-b47', 'saidas', 'atalho');
  fs.mkdirSync(guardar, { recursive: true });
  fs.writeFileSync(path.join(guardar, 'pacote-ficha.json'), JSON.stringify(dump));
  const r = gerarPacote(dump, pasta || PACOTE, faltam);
  console.log(JSON.stringify({ alvo: path.join(pasta || PACOTE, NOME), modulo: r.hashModulo.slice(0, 8), catalogo: r.hashCatalogo.slice(0, 8),
    completadas: r.completadas, contagem: r.contagem, delta: Object.keys(r.delta), sha: crypto.createHash('sha256').update(r.output).digest('hex').slice(0, 16) }, null, 1));
}
module.exports = { projeto, completar, gerarPacote, NOME };
