// Carrega os .gs num contexto (como o Apps Script) em várias ordens e compara os vals de cada aba com a referência Python.
const fs = require('fs'), path = require('path'), vm = require('vm');
const [dir, refp] = process.argv.slice(2);
const ref = JSON.parse(fs.readFileSync(refp, 'utf8'));
const arqs = fs.readdirSync(dir).filter(f => f.endsWith('.gs') && f !== 'Codigo.gs' && f !== 'Habilidades.gs').sort();
const ordens = [arqs, arqs.slice().reverse(), arqs.slice(5).concat(arqs.slice(0, 5))];
let total = 0;
for (const ordem of ordens) {
  const c = {}; vm.createContext(c);
  for (const f of ordem) vm.runInContext(fs.readFileSync(path.join(dir, f), 'utf8'), c);
  const dif = {};
  for (const aba of c.ABAS) {
    const js = new Set(aba.vals.map(v => JSON.stringify(v))), py = new Set(ref[aba.nome] || []);
    const soPy = [...py].filter(x => !js.has(x)), soJs = [...js].filter(x => !py.has(x));
    if (soPy.length || soJs.length) dif[aba.nome] = { so_python: soPy.length, so_js: soJs.length, ex: soPy.slice(0, 2) };
  }
  total += Object.keys(dif).length;
  console.log('ordem', ordem[0], '→', Object.keys(dif).length ? JSON.stringify(dif) : 'JS = Python em todas as abas');
}
process.exit(total ? 1 : 0);
