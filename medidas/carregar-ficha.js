'use strict';
// A montagem completa precisa de todos os arquivos gerados, inclusive os de abas ocultas.
const fs = require('fs'), path = require('path');
const pasta = path.join(__dirname, '..', 'apps-script');
function arquivos() {
  return ['Ficha.gs', ...fs.readdirSync(pasta).filter(n => n.endsWith('.gs') &&
    !['Ficha.gs', 'Codigo.gs', 'Habilidades.gs'].includes(n)).sort()];
}
function fontes(ordem = arquivos()) {
  return ordem.map(n => fs.readFileSync(path.join(pasta, n), 'utf8')).join('\n');
}
module.exports = { arquivos, fontes };
