'use strict';
// Um nível por missão (12/11/2026, livro R66). O comportamento está no missoes_integradas.js e a cadeia que reproduz o
// Salarios.gs nos testes do salário; aqui, o preparador e o trecho das QAs: ida e volta, recusa de repetir e de código
// divergente, e o trecho parseia.
const fs = require('node:fs'), assert = require('node:assert'), vm = require('node:vm');
const P = require('../diagnostico-android/preparar_trava_nivel_missao');
let checks = 0;
const eq = (a, b, m) => { assert.deepStrictEqual(a, b, m); checks++; };
const agora = fs.readFileSync('apps-script/Salarios.gs', 'utf8');
const volta = P.PARES.map(([a, b]) => [b, a]);
const antes = P.aplicar(agora, volta, 'reverter');
eq(P.preparar(antes), agora, 'o preparador leva o salário de antes ao de agora');
assert.throws(() => P.preparar(agora), /já presente/); checks++;
assert.throws(() => P.preparar(antes.replace('limiar);if(sobe!==null)', 'limiar) ;if(sobe!==null)')), /divergente/); checks++;
assert.throws(() => P.preparar(antes + antes), /2 vez/); checks++;
eq(antes.includes('salarioMissoesDaEdicao_'), false); eq(P.PARES.length, 2);
// Num Codigo instalado (o salário mais o resto), a troca é a mesma e não toca no resto.
const instalado = '// cabeçalho do Codigo\nfunction r53Modulo_(){}\n' + antes + '\nfunction outra_(){}\n';
eq(P.aplicar(instalado, P.PARES, 'instalado'), '// cabeçalho do Codigo\nfunction r53Modulo_(){}\n' + agora + '\nfunction outra_(){}\n');
// o trecho do console parseia nos dois sentidos e roda contra um editor de mentira
for (const r of [false, true]) {
  const f = new (Object.getPrototypeOf(async function () {}).constructor)('monaco', 'crypto', 'window', 'return ' + P.trecho(r));
  checks++;
  if (!r) {
    let gravado = null; const win = {};
    const modelo = { getValue: () => gravado === null ? instalado : gravado, setValue: v => { gravado = v; } };
    const outro = { getValue: () => '// outro arquivo', setValue: () => { throw Error('não devia gravar'); } };
    f({ editor: { getModels: () => [outro, modelo] } }, require('node:crypto').webcrypto, win).then(res => {
      assert(!String(res).startsWith('ERRO'), res); eq(gravado, P.aplicar(instalado, P.PARES, 'x')); eq(win.__travaNivelAntes, instalado);
      console.log(JSON.stringify({ checks, resultado: 'OK', escopo: 'preparador e trecho da trava de um nível por missão' }));
    }).catch(e => { console.error(e); process.exit(1); });
  }
}
