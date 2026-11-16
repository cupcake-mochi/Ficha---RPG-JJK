'use strict';
// Datas do salário sem hora (16/11/2026, achado do ChatGPT numa cópia descartável: "a cada fechamento, elas acumulam
// 9 horas, deslocando os próximos vencimentos"). O salarioCongelar_ grava o início e o fim do período no livro SALÁRIOS
// pelo salarioData_, que põe a data ao meio-dia UTC (09:00 em Brasília) para o dia não virar em outro fuso. A fórmula
// do "Início do 1º período pendente" (DADOS_SALARIOS!Q2) lia o último fim com MAX('SALÁRIOS'!C2:C), sem tirar a hora:
// o período seguinte começava às 09:00 e o fechamento dele gravava mais 9 h por cima. No terceiro fechamento o
// vencimento já andava um dia. Dois pares [antes, depois] em salario_datas_sem_hora.json:
//   1. a fórmula usa MAX(INT(ult);em): o período sempre começa num dia inteiro (é o conserto);
//   2. o salarioCongelar_ arredonda o dia antes de gravar (reforço: ficha com a fórmula antiga para de acumular).
// O salarioData_ continua igual: a hora dele protege o dia em planilha de outro fuso. Vem depois do
// preparar_xp_linha_congelada.js na cadeia que reproduz o apps-script/Salarios.gs.
//
// Planilha já montada: além do código, a célula DADOS_SALARIOS!Q2 precisa da fórmula nova (FORMULA_Q2, pela API).
//
//   node r53/diagnostico-android/preparar_salario_datas.js            > trecho.js   (aplica)
//   node r53/diagnostico-android/preparar_salario_datas.js --reverter > trecho.js   (desfaz)
const fs = require('fs'), path = require('path'), vm = require('vm');
const PARES = JSON.parse(fs.readFileSync(path.join(__dirname, 'salario_datas_sem_hora.json'), 'utf8'));
const FORMULA_Q2 = "=IF(ISNUMBER(N2);LET(ult;MAX('SALÁRIOS'!C2:C);em;INT(N2);IF(ult>0;MAX(INT(ult);em);em));\"\")";

/** Função pura, igual no node e no navegador: cada trecho antigo uma vez. */
function aplicar(texto, pares, onde) {
  for (const [velho, novo] of pares) {
    const n = texto.split(velho).length - 1;
    if (n !== 1) throw new Error(onde + ': trecho antigo encontrado ' + n + ' vez(es): ' + velho.trim().split('\n')[0].slice(0, 60));
    texto = texto.replace(velho, () => novo);
  }
  return texto;
}

/** O Salarios.gs (ou o Codigo instalado) com a troca; recusa se já tiver ou se o salário divergir. */
function preparar(source) {
  if (source.indexOf('MAX(INT(ult);em)') >= 0) throw Error('Datas sem hora já presentes');
  const out = aplicar(source, PARES, 'Salário divergente');
  new vm.Script(out); return out;
}

function trecho(reverter = false) {
  const pares = reverter ? PARES.map(([a, b]) => [b, a]) : PARES;
  return 'await (async () => { try {\n' +
    'const pares = ' + JSON.stringify(pares) + ';\n' +
    'const aplicar = ' + aplicar.toString() + ';\n' +
    'const sha = async t => [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(t)))].map(b => b.toString(16).padStart(2, "0")).join("");\n' +
    'const cod = monaco.editor.getModels().filter(m => m.getValue().indexOf("function salarioCongelar_(") >= 0);\n' +
    'if (cod.length !== 1) throw new Error("salarioCongelar_ encontrado em " + cod.length + " arquivo(s)");\n' +
    'const antes = cod[0].getValue(), novo = aplicar(antes, pares, "salário instalado");\n' +
    'window.__salarioDatasAntes = antes;\n' +
    'cod[0].setValue(novo);\n' +
    'return JSON.stringify({ antes: (await sha(antes)).slice(0, 12), depois: (await sha(cod[0].getValue())).slice(0, 12), trechos: pares.length });\n' +
    '} catch (err) { return "ERRO: " + err.message; } })()';
}

if (require.main === module) process.stdout.write(trecho(process.argv.includes('--reverter')) + '\n');
module.exports = { PARES, FORMULA_Q2, aplicar, preparar, trecho };
