'use strict';
// Um nível por missão (12/11/2026, livro R66: "no máximo um nível por missão concluída"). Dois pares [antes, depois] no
// código do salário (trava_nivel_missao_salario.json): o salarioNivelQueSobe_ ganha o teto, e o salarioMissaoDireta_
// passa o teto da edição (o nível atual mais as missões cujo nome ou tipo ela tocou, pelo salarioMissoesDaEdicao_).
// Vem depois do preparar_xp_atualizar.js na cadeia que reproduz o apps-script/Salarios.gs.
//
// Nas QAs o código do salário mora dentro do Codigo instalado (o arquivo que tem o salarioMissaoDireta_). O trecho para
// o console do editor acha esse arquivo, troca os dois pares (cada antigo exatamente uma vez), guarda o antes em
// window.__travaNivelAntes e grava. Salvar depois (Ctrl+S). O caminho de reserva do Codigo.gs (nivelPelaMissao_) e a
// ajuda da caixa do nível moram no módulo compactado e ficam para a próxima montagem: com o salário instalado, o
// caminho de reserva não roda.
//
//   node r53/diagnostico-android/preparar_trava_nivel_missao.js            > trecho.js   (aplica)
//   node r53/diagnostico-android/preparar_trava_nivel_missao.js --reverter > trecho.js   (desfaz)
const fs = require('fs'), path = require('path'), vm = require('vm');
const PARES = JSON.parse(fs.readFileSync(path.join(__dirname, 'trava_nivel_missao_salario.json'), 'utf8'));

/** Função pura, igual no node e no navegador: cada trecho antigo uma vez. */
function aplicar(texto, pares, onde) {
  for (const [velho, novo] of pares) {
    const n = texto.split(velho).length - 1;
    if (n !== 1) throw new Error(onde + ': trecho antigo encontrado ' + n + ' vez(es): ' + velho.trim().split('\n')[0].slice(0, 60));
    texto = texto.replace(velho, () => novo);
  }
  return texto;
}

/** O Salarios.gs (ou o Codigo instalado) com a trava; recusa se já tiver ou se o caminho das missões divergir. */
function preparar(source) {
  if (source.indexOf('function salarioMissoesDaEdicao_(') >= 0) throw Error('Trava de nível por missão já presente');
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
    'window.__travaNivelAntes = antes;\n' +
    'cod[0].setValue(novo);\n' +
    'return JSON.stringify({ antes: (await sha(antes)).slice(0, 12), depois: (await sha(cod[0].getValue())).slice(0, 12), trechos: pares.length });\n' +
    '} catch (err) { return "ERRO: " + err.message; } })()';
}

if (require.main === module) process.stdout.write(trecho(process.argv.includes('--reverter')) + '\n');
module.exports = { PARES, aplicar, preparar, trecho };
