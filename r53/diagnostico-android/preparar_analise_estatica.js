'use strict';
// ANALISE estática (17/11/2026, fase 1 do plano da ANALISE estática; medição na seção 23 do ACHADOS de 16/11).
// O exportador mora no apps-script/AnaliseEstatica.gs, que entra no projeto como arquivo próprio (fora do módulo
// comprimido). Este preparador põe os dois ganchos no Codigo já instalado:
//   1. no onEdit, logo depois da guarda que marca o início, o analiseNaEdicao_ vê a edição antes de tudo
//      (a caixa da CARTEIRA AT4 e a marca de desatualizada);
//   2. no onOpen, o menu Bot com "Exportar para o bot".
// A guarda é a do onEdit de entrada, que roda os restauradores antes do salário (forma das oficiais em 17/11/2026:
// "function onEdit(e){if(e)e.r53Inicio_=Date.now();if(r53NivelRestaurar_(e))...return r53SalarioOnEdit_(e);}").
// Só quando o onEdit de entrada é o embrulho curto do preparar_salario_lote.js ("return r53SalarioOnEdit_(e)", sem
// guarda) o gancho vai no r53OnEditOriginal_. O onOpen tem duas formas: a do pacote (com typeof) e a das oficiais.
// Só mexe no texto do Codigo de entrada (fora do módulo comprimido): o hash do módulo e o atalho calado não mudam.
//
//   node r53/diagnostico-android/preparar_analise_estatica.js            > trecho.js   (aplica)
//   node r53/diagnostico-android/preparar_analise_estatica.js --reverter > trecho.js   (desfaz)
const vm = require('vm');

const GANCHO_EDIT = 'if(typeof analiseNaEdicao_==="function"&&analiseNaEdicao_(e))return;';
const GANCHO_MENU = 'if(typeof analiseMenu_==="function")analiseMenu_();';
const GUARDAS = ['function onEdit(e){if(e)e.r53Inicio_=Date.now();', 'function r53OnEditOriginal_(e){if(e)e.r53Inicio_=Date.now();'];
const ABERTURAS = ['function onOpen(e){if(typeof r53CuraMenu_==="function")r53CuraMenu_();', 'function onOpen(e){r53CuraMenu_();'];

/** Os pares [antes, depois] para um Codigo instalado. Função pura, igual no node e no navegador. */
function pares(texto) {
  const guarda = GUARDAS.find(g => texto.split(g).length - 1 === 1);
  if (!guarda) throw new Error('Guarda do onEdit não encontrada (ou repetida) no Codigo');
  const abertura = ABERTURAS.find(a => texto.split(a).length - 1 === 1);
  if (!abertura) throw new Error('Abertura do onOpen não encontrada (ou repetida) no Codigo');
  return [[guarda, guarda + GANCHO_EDIT], [abertura, abertura + GANCHO_MENU]];
}

function aplicar(texto, lista, onde) {
  for (const [velho, novo] of lista) {
    const n = texto.split(velho).length - 1;
    if (n !== 1) throw new Error(onde + ': trecho antigo encontrado ' + n + ' vez(es): ' + velho.trim().split('\n')[0].slice(0, 60));
    texto = texto.replace(velho, () => novo);
  }
  return texto;
}

/** O Codigo com os ganchos; recusa se já tiver. */
function preparar(source) {
  if (source.indexOf('analiseNaEdicao_') >= 0 || source.indexOf('analiseMenu_') >= 0) throw Error('Ganchos da ANALISE estática já presentes');
  const out = aplicar(source, pares(source), 'Codigo divergente');
  new vm.Script(out); return out;
}

/** O Codigo sem os ganchos (desfaz o preparar). */
function reverter(source) {
  const n = source.split(GANCHO_EDIT).length - 1, m = source.split(GANCHO_MENU).length - 1;
  if (n !== 1 || m !== 1) throw Error('Ganchos da ANALISE estática: ' + n + ' no onEdit e ' + m + ' no onOpen; esperado 1 e 1');
  const out = source.replace(GANCHO_EDIT, '').replace(GANCHO_MENU, '');
  new vm.Script(out); return out;
}

/** Trecho para o console do editor do Apps Script (Codigo aberto no Monaco), como os outros preparadores. */
function trecho(desfazer = false) {
  return 'await (async () => { try {\n' +
    'const GANCHO_EDIT = ' + JSON.stringify(GANCHO_EDIT) + ', GANCHO_MENU = ' + JSON.stringify(GANCHO_MENU) + ';\n' +
    'const GUARDAS = ' + JSON.stringify(GUARDAS) + ', ABERTURAS = ' + JSON.stringify(ABERTURAS) + ';\n' +
    'const pares = ' + pares.toString() + ';\n' +
    'const aplicar = ' + aplicar.toString() + ';\n' +
    'const sha = async t => [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(t)))].map(b => b.toString(16).padStart(2, "0")).join("");\n' +
    'const cod = monaco.editor.getModels().filter(m => GUARDAS.some(g => m.getValue().indexOf(g) >= 0));\n' +
    'if (cod.length !== 1) throw new Error("guarda do onEdit encontrada em " + cod.length + " arquivo(s)");\n' +
    'const antes = cod[0].getValue();\n' +
    (desfazer
      ? 'if (antes.split(GANCHO_EDIT).length !== 2 || antes.split(GANCHO_MENU).length !== 2) throw new Error("ganchos ausentes ou repetidos");\n' +
        'const novo = antes.replace(GANCHO_EDIT, "").replace(GANCHO_MENU, "");\n'
      : 'if (antes.indexOf("analiseNaEdicao_") >= 0) throw new Error("ganchos já presentes");\n' +
        'const novo = aplicar(antes, pares(antes), "Codigo instalado");\n') +
    'window.__analiseEstaticaAntes = antes;\n' +
    'cod[0].setValue(novo);\n' +
    'return JSON.stringify({ antes: (await sha(antes)).slice(0, 12), depois: (await sha(cod[0].getValue())).slice(0, 12) });\n' +
    '} catch (err) { return "ERRO: " + err.message; } })()';
}

if (require.main === module) process.stdout.write(trecho(process.argv.includes('--reverter')) + '\n');
module.exports = { GANCHO_EDIT, GANCHO_MENU, GUARDAS, ABERTURAS, pares, aplicar, preparar, reverter, trecho };
