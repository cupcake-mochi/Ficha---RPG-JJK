'use strict';
// Missões sem a leitura dos registros quando nada pode mudar (27/10/2026). Uma edição no painel de missões da FICHA
// PESSOAL lia a DADOS_SALARIOS!A2:G inteira (~2,5 s medidos numa cópia da Era) mesmo quando a caixa editada ficava sem
// missão antes e depois: o nome digitado com o tipo ainda vazio, o tipo apagado depois do nome, os modificadores.
// Agora essas edições só leem o painel. As trocas estão em missoes_sem_registros.json, como pares [antes, depois].
// O trecho para o console do editor troca só esses dois pedaços do Codigo instalado: confere antes o Codigo de hoje
// (f86423cf) e depois o Codigo igual ao gerado aqui; recusa sem gravar se algo não bater.
// Uso: node r53/diagnostico-android/preparar_missoes_sem_registros.js <projeto-leve.json> [saída do trecho]
const fs = require('fs'), path = require('path'), vm = require('vm'), crypto = require('crypto');
const sha = t => crypto.createHash('sha256').update(t, 'utf8').digest('hex');
const PARES = JSON.parse(fs.readFileSync(path.join(__dirname, 'missoes_sem_registros.json'), 'utf8'));
const CODIGO_ANTES = 'f86423cf';

function preparar(source) {
  if (PARES.every(([, b]) => source.split(b).length === 2)) throw Error('Missões sem registros já presentes');
  let out = source;
  for (const [a, b] of PARES) {
    if (out.split(a).length !== 2) throw Error('Caminho das missões divergente: ' + a.split('\n')[0].trim().slice(0, 60));
    out = out.replace(a, () => b);
  }
  new vm.Script(out); return out;
}
function gerar(projeto) {
  const codigo = require('./preparar_abertura_salario').gerar(projeto).codigoNovo;
  if (sha(codigo).slice(0, 8) !== CODIGO_ANTES) throw Error('o Codigo de hoje saiu ' + sha(codigo).slice(0, 8) + ', esperava ' + CODIGO_ANTES);
  const codigoNovo = preparar(codigo);
  return { pares: PARES, codigo, codigoNovo, esperado: { antes: sha(codigo), depois: sha(codigoNovo) } };
}
function trecho(g) {
  return 'await (async () => { try {\n' +
    'const pares = ' + JSON.stringify(g.pares) + ';\n' +
    'const sha = async t => [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(t)))].map(b => b.toString(16).padStart(2, "0")).join("");\n' +
    'const cod = monaco.editor.getModels().filter(m => m.getValue().indexOf("function r53Modulo_()") >= 0);\n' +
    'if (cod.length !== 1) throw new Error("Codigo encontrado " + cod.length + " vez(es)");\n' +
    'const v = cod[0].getValue();\n' +
    'if (await sha(v) !== ' + JSON.stringify(g.esperado.antes) + ') throw new Error("Codigo instalado diferente: " + (await sha(v)).slice(0, 8));\n' +
    'let novo = v;\n' +
    'for (const [a, b] of pares) { if (novo.split(a).length !== 2) throw new Error("trecho antigo fora do lugar"); novo = novo.replace(a, () => b); }\n' +
    'if (await sha(novo) !== ' + JSON.stringify(g.esperado.depois) + ') throw new Error("saiu diferente do node: " + (await sha(novo)).slice(0, 8));\n' +
    'cod[0].setValue(novo);\n' +
    'return {ok: true, antes: ' + JSON.stringify(g.esperado.antes.slice(0, 8)) + ', depois: (await sha(cod[0].getValue())).slice(0, 8)};\n' +
    '} catch (err) { return "ERRO: " + err.message; } })()';
}
if (require.main === module) {
  const [proj, saida] = process.argv.slice(2);
  if (!proj) throw Error('Uso: node r53/diagnostico-android/preparar_missoes_sem_registros.js <projeto-leve.json> [saída do trecho]');
  const g = gerar(JSON.parse(fs.readFileSync(proj, 'utf8')));
  if (saida) fs.writeFileSync(saida, trecho(g));
  console.log(JSON.stringify({ codigo_antes: g.esperado.antes.slice(0, 8), codigo_depois: g.esperado.depois, bytes_trecho: trecho(g).length }));
}
module.exports = { preparar, gerar, trecho, PARES };
