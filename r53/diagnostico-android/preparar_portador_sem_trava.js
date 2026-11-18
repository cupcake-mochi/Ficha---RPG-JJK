'use strict';
// Portador sem trava no salário (18/11/2026, pedido do Mizuki: "Sim, leva"). Numa cópia do Ciclo, editar o nome do
// portador (CARTEIRA O9:AH12) chegava aos 30 s. No modo fórmula (SALARIO_.formula) o nome não muda nada no salário, mas
// o salarioEditar_ travava e dava flush, e a chamada seguinte esperava o recálculo do nome (~4,3 s medidos). Agora o
// portador só entra nesse caminho fora do modo fórmula. Vem depois do preparar_xp_linha_congelada.js na cadeia que
// reproduz o apps-script/Salarios.gs. O par do EditorR53 (o Amparo, corte A) fica no próprio arquivo; teste dos dois
// em r53/testes/portador_rapido.js.
//
// Nas oficiais o código do salário mora dentro do Codigo instalado (o arquivo que tem o salarioMissaoDireta_). O
// trecho para o console do editor troca o par (o antigo exatamente uma vez), guarda o antes em
// window.__portadorSemTravaAntes e grava. Salvar depois (Ctrl+S).
//
//   node r53/diagnostico-android/preparar_portador_sem_trava.js            > trecho.js   (aplica)
//   node r53/diagnostico-android/preparar_portador_sem_trava.js --reverter > trecho.js   (desfaz)
const vm = require('vm');
const PARES = [[
  "  var nome=n==='CARTEIRA'&&salarioToca_(r,9,15,15,45);",
  "  // 18/11/2026: no modo fórmula o nome do portador não muda nada aqui; a trava e o flush só faziam a chamada seguinte\n" +
  "  // esperar o recálculo do nome (~4,3 s medidos numa cópia do Ciclo).\n" +
  "  var nome=!SALARIO_.formula&&n==='CARTEIRA'&&salarioToca_(r,9,15,15,45);"
]];

/** Função pura, igual no node e no navegador: cada trecho antigo uma vez, no fim de linha do próprio texto. */
function aplicar(texto, pares, onde) {
  const eol = texto.indexOf('\r\n') >= 0 ? '\r\n' : '\n';
  for (const [velho, novo] of pares) {
    const v = velho.split('\n').join(eol), n = texto.split(v).length - 1;
    if (n !== 1) throw new Error(onde + ': trecho antigo encontrado ' + n + ' vez(es): ' + velho.trim().split('\n')[0].slice(0, 60));
    texto = texto.replace(v, () => novo.split('\n').join(eol));
  }
  return texto;
}

/** O Salarios.gs (ou o Codigo instalado) com a troca; recusa se já tiver. */
function preparar(source) {
  if (source.indexOf('var nome=!SALARIO_.formula&&') >= 0) throw Error('portador sem trava já presente');
  const out = aplicar(source, PARES, 'Caminho do salário divergente');
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
    'window.__portadorSemTravaAntes = antes;\n' +
    'cod[0].setValue(novo);\n' +
    'return JSON.stringify({ antes: (await sha(antes)).slice(0, 12), depois: (await sha(cod[0].getValue())).slice(0, 12), trechos: pares.length });\n' +
    '} catch (err) { return "ERRO: " + err.message; } })()';
}

if (require.main === module) process.stdout.write(trecho(process.argv.includes('--reverter')) + '\n');
module.exports = { PARES, aplicar, preparar, trecho };
