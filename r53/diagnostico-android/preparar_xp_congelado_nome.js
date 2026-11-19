'use strict';
// XP congelado preso à mesma missão pelo nome (12/11/2026, pedido do Mizuki). Depois do XP digitado na FICHA!AN11, as
// missões que estavam no painel ficam congeladas ("[XP congelado: x · id]" na nota). Apagar o nome de uma delas e
// digitar de novo dava outro id, e o salarioXpCongelado_ descongelava: a missão contava outra vez. Agora, com outro id,
// o mesmo nome do registro dono da marca (DADOS_SALARIOS, mesma caixa) mantém o congelamento e passa a marca para o id
// novo; nome diferente conta inteira, como antes. Três pares [antes, depois] em xp_congelado_nome_salario.json: o
// comentário com o novo salarioMesmoNome_, o corpo do salarioXpCongelado_ e a chamada do caminho que lê os registros,
// que passa o `map`. Vem depois do preparar_trava_nivel_missao.js na cadeia que reproduz o apps-script/Salarios.gs.
//
// Nas QAs o código do salário mora dentro do Codigo instalado (o arquivo que tem o salarioMissaoDireta_). O trecho para
// o console do editor acha esse arquivo, troca os três pares (cada antigo exatamente uma vez), guarda o antes em
// window.__xpCongeladoNomeAntes e grava. Salvar depois (Ctrl+S).
//
//   node r53/diagnostico-android/preparar_xp_congelado_nome.js            > trecho.js   (aplica)
//   node r53/diagnostico-android/preparar_xp_congelado_nome.js --reverter > trecho.js   (desfaz)
const fs = require('fs'), path = require('path'), vm = require('vm');
const PARES = JSON.parse(fs.readFileSync(path.join(__dirname, 'xp_congelado_nome_salario.json'), 'utf8'));

/** Função pura, igual no node e no navegador: cada trecho antigo uma vez. */
function aplicar(texto, pares, onde) {
  for (const [velho, novo] of pares) {
    const n = texto.split(velho).length - 1;
    if (n !== 1) throw new Error(onde + ': trecho antigo encontrado ' + n + ' vez(es): ' + velho.trim().split('\n')[0].slice(0, 60));
    texto = texto.replace(velho, () => novo);
  }
  return texto;
}

/** O Salarios.gs (ou o Codigo instalado) com a troca; recusa se já tiver ou se o caminho das missões divergir. */
function preparar(source) {
  if (source.indexOf('function salarioMesmoNome_(') >= 0) throw Error('XP congelado pelo nome já presente');
  const out = aplicar(source, PARES, 'Caminho das missões divergente');
  new vm.Script(out); return out;
}

function trecho(reverter = false) {
  const pares = reverter ? PARES.map(([a, b]) => [b, a]) : PARES;
  return 'await (async () => { try {\n' +
    'const pares = ' + JSON.stringify(pares) + ';\n' +
    'const aplicar = ' + aplicar.toString() + ';\n' +
    'const sha = async t => [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(t)))].map(b => b.toString(16).padStart(2, "0")).join("");\n' +
    'const cod = monaco.editor.getModels().filter(m => m.getValue().indexOf("function salarioMissaoDireta_(") >= 0);\n' +
    'if (cod.length !== 1) throw new Error("salarioMissaoDireta_ encontrado em " + cod.length + " arquivo(s)");\n' +
    'const antes = cod[0].getValue(), novo = aplicar(antes, pares, "salário instalado");\n' +
    'window.__xpCongeladoNomeAntes = antes;\n' +
    'cod[0].setValue(novo);\n' +
    'return JSON.stringify({ antes: (await sha(antes)).slice(0, 12), depois: (await sha(cod[0].getValue())).slice(0, 12), trechos: pares.length });\n' +
    '} catch (err) { return "ERRO: " + err.message; } })()';
}

if (require.main === module) process.stdout.write(trecho(process.argv.includes('--reverter')) + '\n');
module.exports = { PARES, aplicar, preparar, trecho };
