'use strict';

const fs = require('node:fs');
const path = require('node:path');
const {deslocaFormula} = require('../medidas/sheets-de-mentira');

const aba = 'DADOS_R53';
const colunas = [89, 94, 138, 180]; // CK, CP, EH, FX
// 26/11/2026 (etapa 3 da versão rápida): os cartões do personagem (linhas 2 a 46, e a 252 e a 253 da Prática) viraram de
// preencher e não têm mais montagem na DADOS_R53. Ficam as linhas das invocações
const pessoais = [...Array.from({length: 45}, (_, i) => i + 2), 252, 253];
// 26/11/2026 (etapa 4): as invocações também viraram de preencher. Não sobra linha com montagem na DADOS_R53
const linhas = [];

// 26/11/2026 (etapa 3): linhasAlvo deixa quem chama pular as linhas do personagem, que ficaram sem montagem
function formulas(pasta = path.join(__dirname, '../apps-script'), colunasAlvo = colunas, linhasAlvo = linhas) {
  // 26/11/2026 (etapa 4): sem linha com montagem, a DADOS_R53 saiu da ficha e o R53Dados.gs não é mais gerado
  if (!linhasAlvo.length) return [];
  const fontes = fs.readdirSync(pasta).filter(n => /^R53Dados\d+\.gs$/.test(n));
  const alvos = new Map();
  for (const nome of fontes) {
    const fonte = fs.readFileSync(path.join(pasta, nome), 'utf8');
    const dados = /var VALORES_R53_DADOS_\d+_ = (\[[\s\S]*?\n\]);/.exec(fonte);
    if (!dados) throw Error('Fragmento de DADOS_R53 inválido: ' + nome);
    for (const bloco of JSON.parse(dados[1])) {
      if (bloco.nome !== aba) throw Error('Aba de cálculo divergente: ' + nome);
      for (const [r, c, valor] of bloco.vals) {
        if (!linhas.includes(r) || !colunasAlvo.includes(c)) continue;
        const chave = r + ':' + c;
        if (alvos.has(chave) || typeof valor !== 'string' || !valor.startsWith('=')) {
          throw Error('Fórmula de montagem divergente: ' + chave);
        }
        alvos.set(chave, valor);
      }
    }
  }
  const fonte = fs.readFileSync(path.join(pasta, 'R53Dados.gs'), 'utf8');
  const spec = /^var ABAS_R53_DADOS_ = (\[.*\]);$/m.exec(fonte);
  const [{abaixo}] = JSON.parse(spec[1]);
  return linhasAlvo.flatMap(r => colunasAlvo.map(c => {
    const bloco = abaixo.find(([inicio, esq, fim, dir]) =>
      inicio < r && r <= fim && esq <= c && c <= dir);
    const origem = bloco && alvos.get(bloco[0] + ':' + c);
    const depois = alvos.get(r + ':' + c) ??
      (origem && deslocaFormula(origem, r - bloco[0], 0));
    if (!depois) throw Error('Fórmula de montagem ausente: ' + r + ':' + c);
    return {aba, r, c, depois};
  }));
}

module.exports = {aba, colunas, linhas, pessoais, formulas};
