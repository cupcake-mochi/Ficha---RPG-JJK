"""Contagens locais pós-D; não acessa o Google nem recalcula a ficha.

Reutiliza a exportação fresca da retomada. Mede a mesma VM de A/B, em série;
não transforma esses tempos em latência do Apps Script ou do navegador.
"""
import argparse
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--modelo', type=Path, required=True)
    ap.add_argument('--saida', type=Path, required=True)
    a = ap.parse_args()
    a.saida.mkdir(parents=True, exist_ok=True)
    model = json.loads(a.modelo.read_text(encoding='utf-8'))
    cfg = next(s for s in model['layout']['abas'] if s['nome'] == 'CONFIGURAÇÃO')
    gs = sorted((ROOT / 'apps-script').glob('*.gs'))
    load = json.loads(subprocess.check_output(
        ['node', str(ROOT / 'capacidade-b47/medir-carregamento.js')], cwd=ROOT))
    # O adaptador exige o nome do campo, mas mede esticarCaixas_ para qualquer
    # grupo de texto válido. Usar um gatilho real da geometria atual.
    text_model = a.saida / 'perfil-texto-modelo.json'
    text_model.write_text(json.dumps({'layout': model['layout'], 'registros': [
        {'tipo': 'melhoria', 'n': 1, 'requisitos': cfg['esticam'][0]['gatilhos'][0]}
    ]}, ensure_ascii=False), encoding='utf-8')
    edit = json.loads(subprocess.check_output([
        'node', str(ROOT / 'capacidade-b47/medir-edicao.js'), str(text_model.resolve())
    ], cwd=ROOT))
    files = [{'nome': p.name, 'bytes': p.stat().st_size,
              'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in gs]
    result = {
        'tipo': 'contagem local e VM; sem latência Google',
        'git': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'modelo_sha256': hashlib.sha256(a.modelo.read_bytes()).hexdigest(),
        'python': sys.version.split()[0], 'gs_arquivos': len(gs),
        'gs_bytes': sum(p['bytes'] for p in files),
        'gs_maior': max(files, key=lambda p: p['bytes']), 'arquivos': files,
        'xlsx_local_bytes': (ROOT / 'ficha-v01/ficha-projeto-m-0.1.xlsx').stat().st_size,
        'configuracao': {
            'linhas_declaradas': cfg['linhas'], 'alturas_declaradas': len(cfg['linhas_alt']),
            'formulas_modelo': sum(isinstance(c[1], str) and c[1].startswith('=')
                                   for c in cfg['celulas']),
            'menus_modelo': len(cfg['menus']), 'notas_modelo': len(cfg['notas']),
            'grupos_texto': len(cfg['esticam'])},
        'vm_carregamento': load,
        'vm_carregamento_mediana_ms': statistics.median(s['ms'] for s in load['amostras']),
        'vm_texto': edit,
        'limites': ['Máquina Windows atual; histórico A/B medido em Linux.',
                   'Campos do modelo não equivalem à contagem de objetos XLSX exportados.',
                   'Nenhuma medição nova de geração integral ou construção nativa.']}
    (a.saida / 'perfil-local-reproduzivel.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items()
                      if k not in ('arquivos', 'vm_carregamento')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
