'use strict';
// Somente leitura local: valida o Codigo.gs capturado depois de recarregar.
const fs = require('fs'), vm = require('vm'), assert = require('assert');
const crypto = require('crypto');
const [beforePath, afterPath] = process.argv.slice(2);
if (!beforePath || !afterPath) throw Error('Informe capturas anterior e relida');
const before = fs.readFileSync(beforePath, 'utf8');
const after = fs.readFileSync(afterPath, 'utf8');
const marker = 'function concluirEnsaioPaletaC(){';
const index = before.indexOf(marker);
assert(index > 0 && before.indexOf(marker, index + 1) < 0);
assert.strictEqual(after, before.slice(0, index));
assert(!after.includes('concluirEnsaioPaletaC'));
let pending = false, menus = 0, appearance = 0;
const context = {PropertiesService: {getDocumentProperties: () => ({
  getProperty: () => pending ? 'tema' : null
})}};
vm.createContext(context);
vm.runInContext(after, context);
context.r53Modulo_ = () => { throw Error('Abertura carregou catálogos'); };
context.salarioAbrir_ = () => menus++;
context.r53Menu_ = () => menus++;
context.r53PaletaLeve_ = () => ({continuar: () => appearance++});
context.onOpen({});
assert.strictEqual(menus, 2); assert.strictEqual(appearance, 0);
pending = true; context.onOpen({});
assert.strictEqual(menus, 4); assert.strictEqual(appearance, 1);
console.log(JSON.stringify({resultado: 'OK', caracteres_antes: before.length,
  caracteres_depois: after.length, removidos: before.length - after.length,
  sha256_salvo: crypto.createHash('sha256').update(after).digest('hex'),
  abertura_sem_catalogos: true, retomada_pendente_preservada: true,
  limite: 'Captura do código nativo; teste de eventos em VM local, sem medir Android.'}));
