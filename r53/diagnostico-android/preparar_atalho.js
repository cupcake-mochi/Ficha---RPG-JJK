'use strict';
// Incremento estrito do atalho das células livres (26/10/2026): liga o r53/atalho_livre.gs no onEdit instalado.
// Antes do Caminho e do editor, a edição numa célula fora do mapa sai sem ler a planilha; a Trilha e o Caminho marcam
// as Famílias para a próxima sincronização, e o editor, quando sincroniza, desmarca. Não recompila nem troca catálogos.
// Uso: node r53/diagnostico-android/preparar_atalho.js <Codigo salvo> <saída>
const fs = require('fs'), path = require('path'), vm = require('vm');
const ANTES = 'if(r53EditarCaminho_(e))return r53ContinuarPaletaPendente_(e);if(typeof r53Editar_==="function" && r53Editar_(e))return r53ContinuarPaletaPendente_(e);if(e)e.r53EditorVerificado_=true;return r53Modulo_().onEdit(e);';
const DEPOIS = 'if(r53EdicaoLivre_(e))return r53ContinuarPaletaPendente_(e);r53LivreMarcar_(e);if(r53EditarCaminho_(e))return r53ContinuarPaletaPendente_(e);if(typeof r53Editar_==="function" && r53Editar_(e))return r53ContinuarPaletaPendente_(e);r53LivreConferido_(e);if(e)e.r53EditorVerificado_=true;return r53Modulo_().onEdit(e);';
const INICIO = '// GERADO por r53/atalho_livre.js;';
function preparar(src, atalho) {
  atalho = atalho || fs.readFileSync(path.join(__dirname, '..', 'atalho_livre.gs'), 'utf8');
  if (src.includes('function r53EdicaoLivre_')) {
    // Só troca o mapa de um atalho já instalado: o bloco gerado fica no fim e vai inteiro.
    const i = src.indexOf('\n' + INICIO);
    if (i < 0 || src.split(DEPOIS).length !== 2) throw Error('Atalho instalado divergente');
    const out = src.slice(0, i) + '\n' + atalho;
    new vm.Script(out); return out;
  }
  if (src.split(ANTES).length !== 2) throw Error('Atalho: onEdit divergente ou já alterado');
  const out = src.replace(ANTES, () => DEPOIS) + '\n' + atalho;
  new vm.Script(out);
  return out;
}
if (require.main === module) {
  const [a, b] = process.argv.slice(2);
  if (!a || !b) throw Error('Uso: <Codigo salvo> <saida>');
  fs.writeFileSync(b, preparar(fs.readFileSync(a, 'utf8')));
}
module.exports = { preparar, ANTES, DEPOIS };
