'use strict';
// Portador sem o módulo (18/11/2026, pedido do Mizuki: "pode fazer a 1, 3, 4, 5 (todo ganho é bom, se afetar nada
// negativamente ta tudo bem)"). Corte C da edição do portador (CARTEIRA O9:AH12). Depois dos cortes A e B, o
// r53OnEditOriginal_ ainda carregava o módulo inteiro (~3,7 s) e rodava o onEdit dele (~4,2 s, quase tudo esperando o
// recálculo do nome). Para o portador, o onEdit do módulo só repetia o que a cadeia de fora já fez (restauradores,
// versão pública, salário, Caminho), não acha conta para devolver (O9 é texto no molde, sem fórmula) e continuava uma
// troca de paleta pendente. Agora o portador sai depois do r53LivreConferido_ com o r53ContinuarPaletaPendente_, como
// as outras saídas curtas da mesma função (cartões, salário, edição livre), que continua a paleta sem abrir o módulo.
// O onSelectionChange também continua a paleta a cada clique.
//
// Nas oficiais o r53OnEditOriginal_ mora no Codigo instalado (o arquivo que tem a função). O trecho para o console do
// editor troca o par (o antigo exatamente uma vez), guarda o antes em window.__portadorSemModuloAntes e grava. Salvar
// depois (Ctrl+S). Teste em r53/testes/portador_rapido.js.
//
//   node r53/diagnostico-android/preparar_portador_sem_modulo.js            > trecho.js   (aplica)
//   node r53/diagnostico-android/preparar_portador_sem_modulo.js --reverter > trecho.js   (desfaz)
const vm = require('vm');
const PORTADOR = 'e&&e.range&&e.range.getSheet().getName()==="CARTEIRA"&&e.range.getRow()>=9&&e.range.getLastRow()<=12' +
  '&&e.range.getColumn()>=15&&e.range.getLastColumn()<=34';
const PARES = [[
  'r53LivreConferido_(e);if(e)e.r53EditorVerificado_=true;return r53Modulo_().onEdit(e);',
  'r53LivreConferido_(e);if(' + PORTADOR + ')return r53ContinuarPaletaPendente_(e);' +
  'if(e)e.r53EditorVerificado_=true;return r53Modulo_().onEdit(e);'
]];

/** Função pura, igual no node e no navegador: cada trecho antigo uma vez. */
function aplicar(texto, pares, onde) {
  for (const [velho, novo] of pares) {
    const n = texto.split(velho).length - 1;
    if (n !== 1) throw new Error(onde + ': trecho antigo encontrado ' + n + ' vez(es): ' + velho.slice(0, 60));
    texto = texto.replace(velho, () => novo);
  }
  return texto;
}

/** O Codigo instalado com a troca; recusa se já tiver. */
function preparar(source) {
  if (source.indexOf(PARES[0][1]) >= 0) throw Error('portador sem módulo já presente');
  const out = aplicar(source, PARES, 'r53OnEditOriginal_ divergente');
  new vm.Script(out); return out;
}

function trecho(reverter = false) {
  const pares = reverter ? PARES.map(([a, b]) => [b, a]) : PARES;
  return 'await (async () => { try {\n' +
    'const pares = ' + JSON.stringify(pares) + ';\n' +
    'const aplicar = ' + aplicar.toString() + ';\n' +
    'const sha = async t => [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(t)))].map(b => b.toString(16).padStart(2, "0")).join("");\n' +
    'const cod = monaco.editor.getModels().filter(m => m.getValue().indexOf("function r53OnEditOriginal_(") >= 0);\n' +
    'if (cod.length !== 1) throw new Error("r53OnEditOriginal_ encontrado em " + cod.length + " arquivo(s)");\n' +
    'const antes = cod[0].getValue(), novo = aplicar(antes, pares, "Codigo instalado");\n' +
    'window.__portadorSemModuloAntes = antes;\n' +
    'cod[0].setValue(novo);\n' +
    'return JSON.stringify({ antes: (await sha(antes)).slice(0, 12), depois: (await sha(cod[0].getValue())).slice(0, 12), trechos: pares.length });\n' +
    '} catch (err) { return "ERRO: " + err.message; } })()';
}

if (require.main === module) process.stdout.write(trecho(process.argv.includes('--reverter')) + '\n');
module.exports = { PARES, PORTADOR, aplicar, preparar, trecho };
