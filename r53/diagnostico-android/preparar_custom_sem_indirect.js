'use strict';
// DADOS_CUSTOM sem INDIRECT (15/11/2026, pente fino de desempenho pedido pelo Mizuki).
//
// As 225 fórmulas das listas dos cartões custom (linha 2, DF:JZ) e das conferências (JY/JZ das linhas 3–26) usavam
// INDIRECT(SWITCH(tipo,"Origem","'ABA'!$A$2:$A$9",...)): 525 INDIRECT voláteis, recalculados a cada edição em qualquer
// aba. Agora a faixa vem por CHOOSE(IFERROR(MATCH(tipo,{"Origem";...},0),9),faixa1,...,padrão), que só recalcula
// quando o tipo ou a faixa mudam (ficha-v01/custom.py, escolha_faixa). SWITCH com referência direta não serve: no
// Sheets ele não devolve faixa e a lista do menu some. Conferido na cópia descartável em dois estados do seletor
// ("Arma" e "Origem"), linha a linha: 0 diferenças.
//
//   node r53/diagnostico-android/preparar_custom_sem_indirect.js --fontes        reescreve apps-script/Custom.gs e Origens.gs
//   node r53/diagnostico-android/preparar_custom_sem_indirect.js <sheetId>        pedidos do batchUpdate (planilha montada)
//
// Na planilha montada: um único spreadsheets.batchUpdate com os dois findReplace (é atômico), limitado à DADOS_CUSTOM
// (sheetId da aba, não da planilha). A resposta tem de dizer 225 fórmulas e 4725 + 525 ocorrências; outro número
// é planilha fora do molde: desfazer pelo histórico de versões e investigar.
const fs = require('fs'), path = require('path');

// Onde o gerador grava essas fórmulas: as listas (DF:JX da linha 2) no Custom.gs e as conferências (JY/JZ) no Origens.gs.
const FONTES = ['Custom.gs', 'Origens.gs'];
const CHAVES = ['Origem', 'Marcante', 'Menor', 'Arma', 'Escudo', 'Uniforme', 'Item comum', 'Ferramenta amaldiçoada'];
const FAIXA = "'[A-Z_]+'!\\$[A-Z]+\\$[0-9]+:\\$[A-Z]+\\$[0-9]+";

/** Pura: argumentos de uma chamada sem parênteses internos, separados por vírgula fora de aspas. */
function argumentos(s) {
  const out = []; let cur = '', aspas = false;
  for (const ch of s) {
    if (ch === '"') aspas = !aspas;
    if (ch === ',' && !aspas) { out.push(cur); cur = ''; } else cur += ch;
  }
  out.push(cur); return out;
}

/** Pura (fórmula em inglês, como no Custom.gs): cada INDIRECT(SWITCH(...)) de faixas vira CHOOSE(MATCH). */
function converterIngles(f) {
  return f.replace(/INDIRECT\(SWITCH\(([^()]*)\)\)/g, (todo, dentro) => {
    const a = argumentos(dentro);
    if (a.length % 2 !== 0 || a.length < 4) throw new Error('SWITCH sem padrão: ' + todo.slice(0, 80));
    const sel = a[0], chaves = [], faixas = [];
    for (let i = 1; i < a.length - 1; i += 2) { chaves.push(a[i]); faixas.push(a[i + 1]); }
    faixas.push(a[a.length - 1]);
    const tira = v => { const m = new RegExp('^"(' + FAIXA + ')"$').exec(v); if (!m) throw new Error('Valor do SWITCH não é faixa: ' + v); return m[1]; };
    chaves.forEach(k => { if (!/^"[^"]*"$/.test(k)) throw new Error('Chave do SWITCH não é texto: ' + k); });
    return 'CHOOSE(IFERROR(MATCH(' + sel + ',{' + chaves.join(';') + '},0),' + (chaves.length + 1) + '),' + faixas.map(tira).join(',') + ')';
  });
}

/** Os dois findReplace da planilha montada (fórmulas como o Sheets pt_BR mostra: ";" e faixas sem aspas depois do 1º). */
function pedidos(sheetIdDadosCustom) {
  const campo = '([^;()"]+)', faixa = '([^;()"]+!\\$[^;()"]+)';
  const corpo = CHAVES.map((k, i) => '"' + k + '";' + (i ? campo : faixa)).join(';');
  const range = { sheetId: Number(sheetIdDadosCustom), startRowIndex: 1, endRowIndex: 26, startColumnIndex: 109, endColumnIndex: 286 };
  const grupos = CHAVES.map((_, i) => '$' + (i + 2)).join(';') + ';$' + (CHAVES.length + 2);
  return [
    { findReplace: { find: '"(' + FAIXA + ')"', replacement: '$1', range: range, matchCase: true, searchByRegex: true, includeFormulas: true } },
    { findReplace: { find: 'INDIRECT\\(SWITCH\\(' + campo + ';' + corpo + ';' + campo + '\\)\\)',
      replacement: 'CHOOSE(IFERROR(MATCH($1;{' + CHAVES.map(k => '"' + k + '"').join(';') + '};0);' + (CHAVES.length + 1) + ');' + grupos + ')',
      range: range, matchCase: true, searchByRegex: true, includeFormulas: true } }];
}

/** Pura: o que o Sheets faz com os pedidos, em JS (para os testes). "$10" é o décimo grupo, como no Sheets. */
function aplicarPedidos(formula, reqs) {
  return reqs.reduce((f, r) => {
    const fr = r.findReplace;
    return f.replace(new RegExp(fr.find, 'g'), (...m) => fr.replacement.replace(/\$(\d+)/g, (_, n) => m[Number(n)]));
  }, formula);
}

/** Pura: inglês → como o Sheets pt_BR mostra (vírgula vira ponto e vírgula fora de aspas). */
function paraPtBr(f) {
  let out = '', aspas = false;
  for (const ch of f) { if (ch === '"') aspas = !aspas; out += (!aspas && ch === ',') ? ';' : ch; }
  return out;
}

/** Reescreve as cadeias de texto do Custom.gs que têm INDIRECT; o resto do arquivo fica byte a byte. */
function reescreverCustomGs(texto) {
  let n = 0;
  const novo = texto.replace(/"(?:[^"\\]|\\.)*"/g, s => {
    if (s.indexOf('INDIRECT(') < 0) return s;
    const f = JSON.parse(s), g = converterIngles(f);
    if (g.indexOf('INDIRECT(') >= 0) throw new Error('Sobrou INDIRECT fora do molde: ' + g.slice(0, 120));
    n++; return JSON.stringify(g);
  });
  return { texto: novo, formulas: n };
}

if (require.main === module) {
  const arg = process.argv[2];
  if (arg === '--fontes') {
    for (const nome of FONTES) {
      const p = path.join(__dirname, '../../apps-script', nome), r = reescreverCustomGs(fs.readFileSync(p, 'utf8'));
      fs.writeFileSync(p, r.texto); console.log(nome + ': ' + r.formulas + ' cadeias convertidas');
    }
  } else if (/^\d+$/.test(arg || '')) process.stdout.write(JSON.stringify({ requests: pedidos(arg) }, null, 1) + '\n');
  else { console.error('uso: --fontes | <sheetId da DADOS_CUSTOM>'); process.exit(2); }
}
module.exports = { FONTES, CHAVES, argumentos, converterIngles, pedidos, aplicarPedidos, paraPtBr, reescreverCustomGs };
