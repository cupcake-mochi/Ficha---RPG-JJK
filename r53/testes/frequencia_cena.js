'use strict';
// Frequência do R66 (12/11/2026): cinco habilidades passam de "uma vez por combate" para "uma vez por cena". O texto
// sai do manual.txt (R53) e o extrator aplica as oito frases de r53/textos_revisados.py (FREQUENCIA_POR_CENA).
// Ver r53/diagnostico-android/CORRECAO-FREQUENCIA-CENA-2026-11-12.md.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const zlib = require('node:zlib');
const { execFileSync } = require('node:child_process');

const python = fs.existsSync('.venv/bin/python') ? '.venv/bin/python' : 'python3';
const py = `
import json, sys, copy
sys.path.insert(0, 'ficha-v01'); sys.path.insert(0, '.')
import extrair_habilidades as x
from r53.textos_revisados import FREQUENCIA_POR_CENA as F
assert sum(len(v) for v in F.values()) == 8 and len(F) == 5
bruto = x.extrai()
novo = x.revisa_r66(copy.deepcopy(bruto))
assert not x.confere_no_manual(novo)
gravado = json.load(open(x.SAIDA, encoding='utf-8'))
assert json.dumps(gravado, sort_keys=True) == json.dumps(novo, sort_keys=True), 'arquivo fora do extrator'
mudou = [(g, d, n) for g in ('caminhos', 'trilhas', 'no_caminho') for d in bruto[g] for n in bruto[g][d] if bruto[g][d][n] != novo[g][d][n]]
assert sorted(mudou) == sorted(F), mudou
for (g, d, n), trocas in F.items():
    for antes, depois in trocas:
        assert antes in bruto[g][d][n]['texto'] and depois in novo[g][d][n]['texto']
        assert antes not in novo[g][d][n]['texto']
    assert bruto[g][d][n]['nome'] == novo[g][d][n]['nome'] and bruto[g][d][n]['titulos'] == novo[g][d][n]['titulos']
# a frase do R53 sumiu da carta: o extrator para, em vez de deixar a regra antiga
ruim = copy.deepcopy(bruto)
ruim['trilhas']['Assassino']['27']['texto'] = ruim['trilhas']['Assassino']['27']['texto'].replace('Uma vez por combate, ao', 'Uma vez por combate,  ao')
try:
    x.revisa_r66(ruim)
except SystemExit:
    pass
else:
    raise SystemExit('frase ausente aceita')
# um "por combate" novo em outra carta também para
ruim = copy.deepcopy(bruto)
ruim['caminhos']['Bastião']['2']['texto'] += ' Uma vez por combate.'
try:
    x.revisa_r66(ruim)
except SystemExit:
    pass
else:
    raise SystemExit('por combate aceito')
print('ok')
`;
assert.equal(execFileSync(python, ['-c', py], { encoding: 'utf8' }).trim(), 'ok');

// As duas cópias do texto no Apps Script: Habilidades.gs e a compactada do caminho leve (Caminho.gs).
const hab = fs.readFileSync('apps-script/Habilidades.gs', 'utf8');
const leve = zlib.gunzipSync(Buffer.from(fs.readFileSync('apps-script/Caminho.gs', 'utf8').match(/base64Decode\("([^"]+)"/)[1], 'base64')).toString();
for (const [nome, t] of [['Habilidades.gs', hab], ['Caminho.gs', leve]]) {
  assert.equal((t.match(/por combate|uso da habilidade no combate/g) || []).length, 0, nome + ' ainda tem a frequência antiga');
  for (const frase of ['Uma vez por cena · Participantes a até 18 m.', 'Marque o uso da habilidade na cena.',
    'Uma vez por cena · Turno de outra criatura', 'marque o uso da habilidade na cena.', 'O uso por cena pertence ao conjunto',
    'Uma vez por cena, pode ativar imediatamente', 'Uma vez por cena, ao utilizar Golpe Cirúrgico', 'Uma vez por cena · Fluidez e 12 PE.'])
    assert.ok(t.includes(frase), nome + ' sem: ' + frase);
}
console.log('Frequência do R66: cinco cartas e oito frases por cena, no JSON, no Habilidades.gs e no caminho leve; frase ausente ou por combate novo param o extrator.');

// O instalador das QAs: a mesma troca, nos dois lugares do Codigo.gs instalado; ida e volta exatas; trecho válido.
const inst = require('../diagnostico-android/instalar_frequencia_cena');
const caminhoDe = t => zlib.gunzipSync(Buffer.from(t.match(/base64Decode\("([^"]+)"/)[1], 'base64')).toString();
const leveVelho = caminhoDe(execFileSync('git', ['show', 'HEAD:apps-script/Caminho.gs'], { encoding: 'utf8', maxBuffer: 1 << 26 }));
if (leveVelho.includes('por combate')) {   // antes do commit do conserto; depois dele o HEAD já é o novo
  assert.equal(inst.aplicar(leveVelho, inst.trocas(), 'leve'), leve, 'O instalador não reproduz o caminho leve gerado');
}
assert.equal(inst.aplicar(inst.aplicar(leve, inst.trocas(true), 'leve'), inst.trocas(), 'leve'), leve, 'Ida e volta');
assert.throws(() => inst.aplicar(leve, inst.trocas(), 'leve'), /encontrada 0 vez/);
assert.throws(() => inst.aplicar(leve + leve, inst.trocas(true), 'leve'), /encontrada 2 vez/);
for (const r of [false, true]) new Function('return (async () => { ' + inst.trecho(r) + ' })');
console.log('Instalador da frequência: reproduz o gerado, desfaz, recusa frase ausente ou repetida.');
