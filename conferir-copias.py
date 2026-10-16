#!/usr/bin/env python3
"""Confere a compactação sem perda e a expansão usada no Apps Script."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'ficha'))
import emitir_gs as gs


def numeros(obj):
    """JSON.stringify escreve 21 em vez de 21.0; ambos são o mesmo número."""
    if isinstance(obj, float) and obj.is_integer():
        return int(obj)
    if isinstance(obj, list):
        return [numeros(v) for v in obj]
    if isinstance(obj, dict):
        return {k: numeros(v) for k, v in obj.items()}
    return obj


def main():
    modelo = (ROOT/'ficha/modelo.gs.js').read_text()
    expansor = modelo[modelo.index('function expandirNotasCopiadas_('):modelo.index('ABAS.forEach(expandirCopias_);')]
    juntador = modelo[modelo.index('function juntarValores_(extras)'):modelo.index("if (typeof VALORES_DAS_ORIGENS_",modelo.index('function juntarValores_(extras)'))]
    # A nota diferente, inclusive vazia, deve ganhar da cópia do molde.
    fixture = dict(nome='notas', vals=[], fundos=[], merges=[], bordas=[],
                   copias=[[2, 4, [8, 14], None, None, None, True]], notas=[['B2', 'Base · ç\nsegunda linha'],
                   ['C4', 'Outra'], ['B8', 'Exceção'], ['C10', ''], ['A20', 'Fora']])
    simples = dict(nome='sem notas', vals=[], fundos=[], merges=[], bordas=[], copias=[[2, 4, [8]]])
    legado = dict(nome='ajuda só no primeiro cartão', vals=[], fundos=[], merges=[], bordas=[],
                  copias=[[2,4,[8,14]]], notas=[['B2','Ajuda do primeiro cartão']])
    abas = [fixture, simples, legado] + gs.abas_cruas()
    compactas, esperadas, resumo = [], [], []
    for aba in abas:
        inteira = gs.expandir(aba)
        compacta = gs.compactar(inteira)
        assert gs._forma_canonica(gs.expandir(compacta)) == gs._forma_canonica(inteira), aba['nome']
        compactas.append(compacta)
        esperadas.append(inteira)
        resumo.append(dict(aba=aba['nome'], notas=len(inteira.get('notas', [])),
                           notas_gravadas=len(compacta.get('notas', []))))
    fixture_n = dict(esperadas[0]['notas'])
    assert fixture_n['B8'] == 'Exceção' and fixture_n['C10'] == ''
    assert fixture_n['B14'] == fixture_n['B2'] and fixture_n['C16'] == 'Outra'
    assert 'notas' not in esperadas[1]
    assert esperadas[2]['notas'] == legado['notas']
    script = expansor + juntador + '''
var fs = require('fs');
var abas = JSON.parse(fs.readFileSync(0, 'utf8'));
// Metadados complementares precisam sobreviver aos dois sentidos da junção.
var ABAS = [{nome:'painel',vals:[],alturas:{'1':25},esticam:[]}];
var COMPLEMENTOS_FEITOS_ = new WeakMap();
var complemento=[{nome:'painel',vals:[],alturas:{'2':30},esticam:[['B2:G4',25]]}];
juntarValores_(complemento);
var uma=JSON.stringify(ABAS);
juntarValores_(complemento);
if (uma!==JSON.stringify(ABAS) || ABAS[0].alturas['2']!==30 || ABAS[0].esticam.length!==1) {
  throw Error('Alturas ou caixas expansíveis perdidas/repetidas');
}
// O molde e uma exceção podem morar em complementos que carregam depois.
[[0,1], [1,0]].forEach(function (ordem) {
  var s = { vals: [], fundos: [], merges: [], copias: [[2,4,[8,14],null,null,null,true]] };
  var extras = [[['B2','Base'], ['C4','Outra']], [['B8','Exceção'], ['C10','']]];
  expandirCopias_(s);
  ordem.forEach(function (i) { expandirNotasCopiadas_(s, extras[i]); });
  var n = Object.fromEntries(s.notas);
  if (n.B8 !== 'Exceção' || n.C10 !== '' || n.B14 !== 'Base' || n.C16 !== 'Outra') {
    throw Error('Nota perdida por ordem dos complementos: '+JSON.stringify(n));
  }
  var antes = JSON.stringify(s);
  ordem.forEach(function (i) { expandirNotasCopiadas_(s, extras[i]); });
  if (antes !== JSON.stringify(s)) throw Error('Complemento repetido mudou as notas');
});
abas.forEach(function (a) { expandirCopias_(a); });
var primeira = JSON.stringify(abas);
abas.forEach(function (a) { expandirCopias_(a); });
if (primeira !== JSON.stringify(abas)) throw Error('Expansão repetida mudou a aba');
abas.forEach(function (a) { delete a.copias_feitas; delete a.notas_copiadas_; });
process.stdout.write(JSON.stringify(abas));
'''
    run = subprocess.run(['node', '--max-old-space-size=1500', '-e', script],
                         input=json.dumps(compactas, ensure_ascii=False), text=True, capture_output=True, check=True)
    for esperada, real in zip(esperadas, json.loads(run.stdout)):
        assert gs._forma_canonica(numeros(real)) == gs._forma_canonica(numeros(esperada)), esperada['nome']+' Python/JS'
    print(json.dumps(dict(resultado='OK', abas=len(abas), detalhes=resumo), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
