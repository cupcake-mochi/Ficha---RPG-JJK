"""Compara exportações nativas da construção e da oficial, sem escrever no Google.

Os relatórios completos, inclusive diferenças de valores, ficam na pasta privada.
Não aprova automaticamente mudanças de fórmula, número, menu, nota ou estilo.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--referencia', type=Path, required=True)
    ap.add_argument('--oficial', type=Path, required=True)
    ap.add_argument('--saida', type=Path, required=True)
    a = ap.parse_args()
    spec = importlib.util.spec_from_file_location('fotos', Path(__file__).with_name('conferir-exportacoes.py'))
    fotos = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fotos)
    print('Lendo referência nativa', flush=True)
    wr, r = fotos.foto(a.referencia)
    print('Lendo alvo nativo', flush=True)
    wo, o = fotos.foto(a.oficial)
    assert set(r['abas']) == set(o['abas']), 'Conjunto de abas diferente'
    diff = fotos.diff(r, o)
    print('Comparando todos os estilos', flush=True)
    styles = fotos.diff_estilo(wr, wo)
    details = []
    for name in r['abas']:
        for key in ('F', 'V', 'N'):
            x, y = r['sheets'][name][key], o['sheets'][name][key]
            for coord in sorted(set(x) | set(y)):
                if x.get(coord) != y.get(coord):
                    details.append([name, key, coord, x.get(coord), y.get(coord)])
    result = {
        'sha256': {k: hashlib.sha256(p.read_bytes()).hexdigest()
                   for k, p in [('referencia', a.referencia), ('oficial', a.oficial)]},
        'resumo_referencia': fotos.resumo(r), 'resumo_oficial': fotos.resumo(o),
        'ordem_abas_igual': r['abas'] == o['abas'],
        'diferencas': diff, 'estilos': styles, 'detalhes': details,
        'aprovado': not diff and not styles and r['abas'] == o['abas'],
        'limites': 'XLSX exportado não contém IDs de abas, proteções, gatilhos nem todas as regras condicionais.'}
    a.saida.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'detalhes'}, ensure_ascii=False))
    if not result['aprovado']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
