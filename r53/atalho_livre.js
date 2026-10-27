'use strict';
// Atalho das células livres (26/10/2026). Uma edição numa célula em que o script não faz nada (texto livre, nome,
// descrição) ainda pagava a sincronização das Famílias (uma leitura, que espera o recálculo: ~4,5 s) e a abertura do
// módulo (~1,8 s) só para concluir que não havia o que fazer. Este gerador descobre, rodando o onEdit instalado contra
// a ficha oficial exportada, em quais células cada aba age, e grava o mapa no atalho_livre.gs: fora dele, a edição sai sem
// ler a planilha.
//
// O mapa junta: o que o módulo faz célula a célula (força bruta com três valores e espiando e.value/e.oldValue), os
// cartões do editor, as entradas do Amparo das Famílias (rastreadas pelas fórmulas da ficha até as células digitadas),
// o salário, o Caminho, a paleta e a versão pública. O atalho_livre.gs só vale para o módulo e o catálogo de onde o mapa
// saiu: com outro hash, ele se desliga sozinho.
//
// Uso: node r53/atalho_livre.js <projeto instalado .json> <ficha exportada .json> [saída .gs]
// A ficha exportada sai do r53/xlsx_para_json.py; nem ela nem o projeto vão para o Git (nuvem-b47/saidas/atalho/).
const fs = require('fs'), path = require('path'), vm = require('vm'), crypto = require('crypto');
const { criar } = require('./arnes_custo');

const ABAS = ['CARTEIRA', 'FICHA AMALDIÇOADA', 'INVOCAÇÕES', 'CONFIGURAÇÃO', 'FICHA', 'FICHA PESSOAL'];
// As quatro abas em que a edição fora dos cartões sincroniza as Famílias (r53Editar_).
const FAMILIAS = ['CARTEIRA', 'FICHA AMALDIÇOADA', 'INVOCAÇÕES', 'CONFIGURAÇÃO'];
// Áreas tratadas antes do módulo, copiadas de salarioEditar_, r53SalarioAreaPropria_, r53EditarCaminho_ e da paleta.
// [linha 1, coluna 1, linha 2, coluna 2]
const FIXAS = {
  'CONFIGURAÇÃO': [[35, 11, 76, 17]],
  'FICHA PESSOAL': [[15, 49, 87, 72], [11, 28, 11, 30], [86, 15, 87, 30], [10, 61, 12, 71], [71, 4, 83, 46]],
  'CARTEIRA': [[3, 46, 3, 46], [9, 15, 15, 45], [27, 3, 27, 3]],
  'FICHA': [[11, 4, 11, 22]],
};

function carregar(projeto, dump) {
  const files = projeto.files.filter(f => f.type !== 'JSON');
  const A = criar(dump, {});
  for (const f of files) vm.runInContext(f.source + '\n', A.ctx, { filename: f.name });
  const codigo = files.map(f => f.source).join('\n');
  const modulo = /hash!=='([0-9a-f]{64})'/.exec(files.find(f => f.name === 'Codigo').source);
  const catalogo = /if\(hash!=="([0-9a-f]{64})"\)throw Error\("Editor: catálogo divergente"\)/.exec(files.find(f => f.name === 'EditorR53').source);
  if (!modulo || !catalogo) throw Error('hash do módulo ou do catálogo não encontrado no projeto');
  return { A, codigo, hashModulo: modulo[1], hashCatalogo: catalogo[1] };
}

// Força bruta: a célula é de interesse se o módulo lê, grava, estoura, ou olha o valor da edição.
function interesse(A, aba, cartoes) {
  const ignorar = e => (e.t === 'P' && /paleta|lock/.test(e.k + (e.a || ''))) || (e.t === 'R' && e.k === 'nomeado') || e.t === 'L' || e.t === 'M';
  const sh = A.ss.getSheetByName(aba), out = [];
  for (let r = 1; r <= sh.rows; r++) for (let c = 1; c <= sh.cols; c++) {
    if (cartoes.some(a => r >= a[0] && r <= a[2] && c >= a[1] && c <= a[3])) continue;
    let ok = false;
    for (const v of ['x', 3, '']) {
      const range = sh.getRange(r, c), old = sh.cel(r, c).v, x = sh.cel(r, c, true);
      x.v = v; delete x.f; A.reset();
      let leu = false;
      const e = new Proxy({ range, source: A.ss, value: v === '' ? undefined : v, oldValue: old === '' ? undefined : old,
        r53EditorVerificado_: true, r53Inicio_: Date.now() }, { get(t, k) { if (k === 'value' || k === 'oldValue') leu = true; return t[k]; } });
      A.ctx.__e = e;
      try { vm.runInContext('r53Modulo_().onEdit(__e)', A.ctx); } catch (err) { ok = true; }
      if (leu || A.log.some(e => !ignorar(e))) ok = true;
      A.desfazer();
      if (ok) break;
    }
    if (ok) out.push([r, c, r, c]);
  }
  return out;
}

// As células digitadas de que o Amparo depende: das fórmulas da faixa do amparo para trás, até uma célula sem fórmula.
const numCol = t => [...t].reduce((n, x) => n * 26 + x.charCodeAt(0) - 64, 0);
function referencias(f, aba, dump) {
  f = f.replace(/"(?:[^"]|"")*"/g, '""');
  const re = /(?:'([^']+)'|\b([A-Z_][A-Z0-9_ÇÃÕÁÉÍÓÚÂÊÔ]*))!\$?([A-Z]{1,3})\$?(\d+)(?::\$?([A-Z]{1,3})\$?(\d+))?|(?<![A-Za-z_!'0-9])\$?([A-Z]{1,3})\$?(\d+)(?::\$?([A-Z]{1,3})\$?(\d+))?(?![(A-Za-z_0-9])/g;
  const out = [];
  for (const m of f.matchAll(re)) {
    let s, c1, r1, c2, r2;
    if (m[3]) { s = m[1] || m[2]; c1 = m[3]; r1 = m[4]; c2 = m[5] || c1; r2 = m[6] || r1; }
    else { s = aba; c1 = m[7]; r1 = m[8]; c2 = m[9] || c1; r2 = m[10] || r1; }
    if (!dump[s]) continue;
    out.push([s, +r1, numCol(c1), +r2, numCol(c2)]);
  }
  return out;
}
function entradasDoAmparo(dump, faixa) {
  const fila = [faixa], visto = new Set(), entradas = {};
  while (fila.length) {
    const [s, r1, c1, r2, c2] = fila.pop(), cells = dump[s].cells;
    const lista = (r2 - r1 + 1) * (c2 - c1 + 1) > 4000
      ? Object.keys(cells).filter(k => { const [r, c] = k.split(',').map(Number); return r >= r1 && r <= r2 && c >= c1 && c <= c2; })
      : [].concat(...Array.from({ length: r2 - r1 + 1 }, (_, i) => Array.from({ length: c2 - c1 + 1 }, (_, j) => (r1 + i) + ',' + (c1 + j))));
    for (const k of lista) {
      if (visto.has(s + '|' + k)) continue;
      visto.add(s + '|' + k);
      const v = cells[k];
      if (v && typeof v.f === 'string') {
        if (/INDIRECT\(|OFFSET\(/i.test(v.f)) throw Error('o Amparo passa por referência indireta em ' + s + '!' + k);
        referencias(v.f, s, dump).forEach(x => fila.push(x));
      } else {
        const [r, c] = k.split(',').map(Number);
        (entradas[s] = entradas[s] || []).push([r, c, r, c]);
      }
    }
  }
  return entradas;
}

// Células soltas viram retângulos: corridas na linha, depois corridas iguais em linhas seguidas.
function retangulos(lista) {
  const cel = new Set();
  lista.forEach(([r1, c1, r2, c2]) => { for (let r = r1; r <= r2; r++) for (let c = c1; c <= c2; c++) cel.add(r + ',' + c); });
  const linhas = new Map();
  [...cel].map(k => k.split(',').map(Number)).sort((a, b) => a[0] - b[0] || a[1] - b[1]).forEach(([r, c]) => {
    const l = linhas.get(r) || []; const u = l[l.length - 1];
    if (u && u[1] === c - 1) u[1] = c; else l.push([c, c]); linhas.set(r, l);
  });
  const abertos = new Map(), out = [];
  [...linhas.keys()].sort((a, b) => a - b).forEach(r => {
    const agora = new Map();
    linhas.get(r).forEach(([a, b]) => {
      const k = a + ':' + b, ant = abertos.get(k);
      if (ant && ant[2] === r - 1) { ant[2] = r; agora.set(k, ant); } else { const n = [r, a, r, b]; out.push(n); agora.set(k, n); }
    });
    abertos.clear(); agora.forEach((v, k) => abertos.set(k, v));
  });
  return out.sort((x, y) => x[0] - y[0] || x[1] - y[1]);
}

function gerar(projeto, dump) {
  const { A, hashModulo, hashCatalogo } = carregar(projeto, dump);
  vm.runInContext('r53Modulo_()', A.ctx);
  const E = vm.runInContext('r53ConfigEditor_()', A.ctx);
  const treino = vm.runInContext('typeof R53_TREINO_AREA_!=="undefined"?R53_TREINO_AREA_:null', A.ctx);
  if (JSON.stringify(treino) !== JSON.stringify(FIXAS['FICHA PESSOAL'][4])) throw Error('área de treino mudou: ' + JSON.stringify(treino));
  const publica = vm.runInContext('typeof R53_VERSAO_PUBLICA_!=="undefined"?R53_VERSAO_PUBLICA_:[]', A.ctx);
  const p = E.amparo, [a1] = [p.faixa.replace(/\$/g, '')];
  const m = /^([A-Z]+)(\d+):([A-Z]+)(\d+)$/.exec(a1);
  const amparo = entradasDoAmparo(dump, [p.aba, +m[2], numCol(m[1]), +m[4], numCol(m[3])]);
  const fora = Object.keys(amparo).filter(s => !ABAS.includes(s) && !dump[s].hidden);
  if (fora.length) throw Error('o Amparo depende de abas visíveis fora do mapa: ' + fora.join(', '));
  // As marcas do Caminho e da Trilha custom (DADOS_PROGRESSAO!K7:K8), que o módulo guarda nas propriedades: as células
  // digitadas de que elas dependem apagam a guardada (r53EdicaoLivre_), dentro ou fora do mapa.
  const marcas = entradasDoAmparo(dump, ['DADOS_PROGRESSAO', 7, 11, 8, 11]);
  const foraM = Object.keys(marcas).filter(s => !ABAS.includes(s) && !dump[s].hidden);
  if (foraM.length) throw Error('as marcas custom dependem de abas visíveis fora do mapa: ' + foraM.join(', '));
  const marcasVisiveis = {};
  Object.keys(marcas).filter(s => ABAS.includes(s)).forEach(s => { marcasVisiveis[s] = retangulos(marcas[s]); });
  const mapa = {}, contagem = {};
  for (const aba of ABAS) {
    const cartoes = E.contextos.filter(g => g.aba === aba).map(g => g.area_editor);
    const bruta = interesse(A, aba, cartoes);
    const tudo = [...bruta, ...cartoes, ...(FIXAS[aba] || []), ...(amparo[aba] || []),
      ...publica.filter(x => x.aba === aba).map(x => [x.linha, x.coluna, x.linha, x.coluna])];
    mapa[aba] = retangulos(tudo);
    contagem[aba] = { linhas: dump[aba].rows, colunas: dump[aba].cols, modulo: bruta.length, cartoes: cartoes.length,
      amparo: (amparo[aba] || []).length, retangulos: mapa[aba].length };
  }
  // A Trilha (FICHA) também muda o Amparo; o Caminho pode limpar a Trilha.
  const gatilhos = (amparo.FICHA || []).concat([[11, 4, 11, 4], [11, 14, 11, 14]]);
  return { mapa, contagem, hashModulo, hashCatalogo, gatilhos: retangulos(gatilhos), marcas: marcasVisiveis,
    output: fonte(mapa, hashModulo, hashCatalogo, retangulos(gatilhos), marcasVisiveis) };
}

function fonte(mapa, hashModulo, hashCatalogo, gatilhos, marcas) {
  const corpo = JSON.stringify(mapa);
  const sha = crypto.createHash('sha256').update(corpo).digest('hex');
  return `// GERADO por r53/atalho_livre.js; mapa ${sha.slice(0, 16)}. Não editar à mão.
// Fora destes retângulos o onEdit não lê a planilha: nem as Famílias nem o módulo têm o que fazer ali.
var R53_LIVRE_=${corpo};
var R53_LIVRE_FAMILIAS_=${JSON.stringify(FAMILIAS)};
var R53_LIVRE_GATILHOS_=${JSON.stringify(gatilhos)};
var R53_LIVRE_HASHES_=[${JSON.stringify(hashModulo)},${JSON.stringify(hashCatalogo)}];
var R53_LIVRE_PROP_='r53_amparo_sujo';
// Onde se mudam as marcas DADOS_PROGRESSAO!K7:K8 que o módulo guarda (marcasCustom_).
var R53_LIVRE_MARCAS_=${JSON.stringify(marcas || {})};
function r53LivreToca_(lista,r){var l1=r.getRow(),l2=r.getLastRow(),c1=r.getColumn(),c2=r.getLastColumn();
 for(var i=0;i<lista.length;i++){var a=lista[i];if(l1<=a[2]&&l2>=a[0]&&c1<=a[3]&&c2>=a[1])return true;}return false;}
// O mapa só vale para o módulo e o catálogo de onde saiu.
function r53LivreValido_(){
 if(typeof r53Modulo_!=='function'||typeof r53ConfigEditor_!=='function')return false;
 return String(r53Modulo_).indexOf(R53_LIVRE_HASHES_[0])>=0&&String(r53ConfigEditor_).indexOf(R53_LIVRE_HASHES_[1])>=0;
}
/** true: a edição caiu numa célula em que nada do script age; sai sem ler a planilha. */
function r53EdicaoLivre_(e){
 try{
  if(!e||!e.range)return false;var r=e.range,aba=r.getSheet().getName(),lista=R53_LIVRE_[aba],m=R53_LIVRE_MARCAS_[aba];
  // As marcas custom guardadas pelo módulo deixam de valer (marcasCustom_); apagar não lê a planilha.
  if(m&&r53LivreToca_(m,r))PropertiesService.getDocumentProperties().deleteProperty('r53_marcas_custom');
  if(!lista||r53LivreToca_(lista,r)||!r53LivreValido_())return false;
  // Trilha ou Caminho mudou desde a última sincronização: a próxima edição nas quatro abas sincroniza.
  if(R53_LIVRE_FAMILIAS_.indexOf(aba)>=0&&PropertiesService.getDocumentProperties().getProperty(R53_LIVRE_PROP_))return false;
  return true;
 }catch(err){console.log('atalho livre: '+err.message);return false;}
}
/** Antes do Caminho: Trilha e Caminho mudam o Amparo sem passar pelas quatro abas. */
function r53LivreMarcar_(e){
 try{if(e&&e.range&&e.range.getSheet().getName()==='FICHA'&&r53LivreToca_(R53_LIVRE_GATILHOS_,e.range))PropertiesService.getDocumentProperties().setProperty(R53_LIVRE_PROP_,'1');}
 catch(err){console.log('atalho livre: '+err.message);}
}
/** Depois do editor: fora dos cartões ele sincronizou as Famílias. */
function r53LivreConferido_(e){
 try{if(e&&e.range&&R53_LIVRE_FAMILIAS_.indexOf(e.range.getSheet().getName())>=0)PropertiesService.getDocumentProperties().deleteProperty(R53_LIVRE_PROP_);}
 catch(err){console.log('atalho livre: '+err.message);}
}
`;
}

if (require.main === module) {
  const [proj, dumpf, saida] = process.argv.slice(2);
  if (!proj || !dumpf) throw Error('Uso: node r53/atalho_livre.js <projeto .json> <ficha .json> [saída .gs]');
  const r = gerar(JSON.parse(fs.readFileSync(proj, 'utf8')), JSON.parse(fs.readFileSync(dumpf, 'utf8')));
  const alvo = saida || path.join(__dirname, 'atalho_livre.gs');
  fs.writeFileSync(alvo, r.output);
  console.log(JSON.stringify({ alvo, modulo: r.hashModulo.slice(0, 8), catalogo: r.hashCatalogo.slice(0, 8), contagem: r.contagem,
    sha: crypto.createHash('sha256').update(r.output).digest('hex') }, null, 1));
}
module.exports = { gerar, retangulos, entradasDoAmparo, referencias, FIXAS, ABAS, FAMILIAS };
