'use strict';
// O nível escrito na mão (27/10/2026): o trecho para o console do editor do Apps Script que troca só o bloco gerado do
// atalho no fim do Codigo (r53/atalho_livre.gs com R53_LIVRE_NIVEL_ e r53LivreNivel_). Módulo, EditorR53 e os outros
// arquivos ficam como estão. Confere antes o Codigo instalado (07a66b0a, o das caixas de ±) e o bloco do atalho de
// f484f49, e depois o Codigo igual ao gerado aqui; recusa sem gravar se algo não bater.
// A planilha muda à parte (DADOS!CY54:CZ54, a conta do XP total em DADOS!CZ47 e as três notas): ver PENDENCIAS.md.
// Uso: node r53/diagnostico-android/preparar_xp_nivel.js <projeto exportado antes dos cortes .json> [saída do trecho]
//      (o mesmo projeto-leve.json do preparar_caixas_delta.js, de onde sai o Codigo de hoje)
const fs = require('fs'), path = require('path'), crypto = require('crypto'), { execSync } = require('child_process');
const raiz = path.join(__dirname, '..', '..');
const { preparar: atalhoNoCodigo } = require('./preparar_atalho');
const caixas = require('./preparar_caixas_delta');
const sha = t => crypto.createHash('sha256').update(t, 'utf8').digest('hex');
const BASE = 'f484f49', CODIGO_ANTES = '07a66b0a';

function gerar(projetoAntesDosCortes) {
  const g = caixas.gerar(projetoAntesDosCortes);
  const atalhoVelho = execSync('git show ' + BASE + ':r53/atalho_livre.gs', { cwd: raiz, maxBuffer: 1 << 26 }).toString('utf8');
  // O atalho deste passo é o de ed4ff8c (o instalado com o nível escrito na mão); o do disco já tem os passos seguintes.
  const atalhoNovo = execSync('git show ed4ff8c:r53/atalho_livre.gs', { cwd: raiz, maxBuffer: 1 << 26 }).toString('utf8');
  if (atalhoNovo.indexOf('function r53LivreNivel_') < 0) throw Error('r53/atalho_livre.gs sem o acerto do nível');
  const codigo = atalhoNoCodigo(g.codigo, atalhoVelho);
  if (sha(codigo).slice(0, 8) !== CODIGO_ANTES) throw Error('o Codigo de hoje saiu ' + sha(codigo).slice(0, 8) + ', esperava ' + CODIGO_ANTES);
  const codigoNovo = atalhoNoCodigo(codigo, atalhoNovo);
  const esperado = { codigo_antes: sha(codigo), codigo: sha(codigoNovo), atalho_antes: sha(atalhoVelho), atalho: sha(atalhoNovo) };
  return { esperado, codigo, codigoNovo, trecho: caixas.trecho(atalhoNovo, esperado) };
}

if (require.main === module) {
  const [proj, saida] = process.argv.slice(2);
  if (!proj) throw Error('Uso: node r53/diagnostico-android/preparar_xp_nivel.js <projeto exportado .json> [saída do trecho]');
  const r = gerar(JSON.parse(fs.readFileSync(proj, 'utf8')));
  if (saida) fs.writeFileSync(saida, r.trecho);
  console.log(JSON.stringify(Object.assign({ bytes_trecho: r.trecho.length, sha_trecho: sha(r.trecho) }, r.esperado), null, 1));
}
module.exports = { gerar };
