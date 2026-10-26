#!/usr/bin/env python3
"""Diagnóstico portátil e smoke sem rede, credenciais, geração ou escrita no Google."""
import argparse
import ast
import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--smoke', action='store_true', help='Executa catálogo, progressão e sintaxe Python/JS/GS')
    args = parser.parse_args()
    checks = []

    def check(name, ok, detail=''):
        checks.append({'teste': name, 'ok': bool(ok), 'detalhe': detail})
        print(('OK ' if ok else 'FALHA ') + name + (': ' + detail if detail else ''), flush=True)

    check('Python 3.10–3.12 (referência: 3.12)', (3, 10) <= sys.version_info[:2] <= (3, 12), sys.version.split()[0])
    for line in (ROOT/'requirements.txt').read_text().splitlines():
        if not line or line.startswith('#'):
            continue
        name, expected = line.split('==')
        try:
            actual = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            actual = 'ausente'
        check(name, actual == expected, actual + ' (esperado ' + expected + ')')
    node = shutil.which('node')
    node_version = subprocess.check_output([node, '--version'], text=True).strip() if node else 'ausente'
    check('Node >= 18 (ambiente de referência: 20)', bool(node) and int(node_version[1:].split('.')[0]) >= 18, node_version)

    required = ['ficha-v01/layout.json', 'manual.txt', 'manual-fonte.json',
                'catalogo-projeto-m.json', 'decisoes-ficha.json',
                'ficha-v01/progressao-base3a.json.gz', 'ESQUEMA-ANALISE.md',
                'repos/JJK---PDF---RPG-main/ficha/ficha-exemplo-kaori.docx']
    required += ['ficha-v01/'+s+'-do-livro.json' for s in ['equipamento', 'habilidades', 'invocacao', 'origens', 'tecnica']]
    for name in required:
        check('entrada ' + name, (ROOT/name).is_file())
    manifest = json.loads((ROOT/'nuvem-b47/referencias.json').read_text())
    for item in manifest['arquivos']:
        path = ROOT/item['arquivo']
        check('referência ' + item['arquivo'], path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256'])
    gs_files = sorted((ROOT/'apps-script').glob('*.gs'))
    check('arquivos Apps Script presentes', len(gs_files) >= 1, str(len(gs_files)))
    r53 = (ROOT/'apps-script/EditorR53.gs').is_file()
    if r53:
        # A R53 instala o pacote comprimido, não os 70 arquivos legíveis.
        # O controlador direto é o único módulo maior: orçamento explícito de
        # 1,2 MB, conferido na instalação nativa; partes de dados seguem <900 KB.
        packed = subprocess.run([sys.executable, str(ROOT/'r53/empacotar_script.py')],
                                cwd=ROOT, capture_output=True, text=True, timeout=60)
        check('empacotamento R53 a partir das fontes versionadas', packed.returncode == 0,
              packed.stderr.strip() or 'exit='+str(packed.returncode))
        if packed.returncode == 0:
            bundle = ROOT/'r53/saidas/pacote-script'
            published = json.loads((bundle/'manifesto.json').read_text())['arquivos']
            expected = {'Ficha.gs', 'Invocacoes.gs', 'Analise.gs', 'Configuracao.gs',
                        'Origens.gs', 'EditorR53.gs', 'Codigo.gs', 'Salarios.gs', 'PaletaAndroid.gs'}
            check('pacote R53 com salários e paleta leve', set(published) == expected, str(len(published)))
            for name in published:
                size = (bundle/name).stat().st_size
                limit = 1200000 if name == 'EditorR53.gs' else 900000
                check('teto publicado ' + name, size < limit, str(size)+' bytes; limite '+str(limit))
    else:
        for path in gs_files:
            check('teto ' + path.name, path.stat().st_size < 900000, str(path.stat().st_size) + ' bytes')

    # Fontes do repositório precisam funcionar com HOME vazio, sem fontes do PC.
    try:
        from PIL import ImageFont
        for name in ['Oswald.ttf', 'YujiSyuku.ttf']:
            font = ImageFont.truetype(str(ROOT/'arte/fontes'/name), 20)
            check('fonte ' + name, bool(font.getname()[0]), font.getname()[0])
    except Exception as error:
        check('carregamento das fontes', False, str(error))
    optional = {'LibreOffice Calc (contas locais)': bool(shutil.which('libreoffice') or shutil.which('soffice')),
                'Google Sheets/Apps Script': 'não sondado; exige conexão e conta no ambiente'}
    print('DEPENDÊNCIAS COMPLEMENTARES ' + json.dumps(optional, ensure_ascii=False), flush=True)

    if args.smoke and all(c['ok'] for c in checks):
        if r53:
            run = subprocess.run([node, str(ROOT/'r53/testes/pacote_runtime.js')],
                                 cwd=ROOT, capture_output=True, text=True, timeout=60)
            check('pacote R53 autossuficiente e íntegro', run.returncode == 0,
                  run.stderr.strip() or run.stdout.strip())
            run = subprocess.run([node, str(ROOT/'salarios/testes.js')],
                                 cwd=ROOT, capture_output=True, text=True, timeout=60)
            check('salários: períodos, participação e idempotência', run.returncode == 0,
                  run.stderr.strip() or run.stdout.strip())
            for name in ['salarios/testar_abertura.js', 'r53/testes/salario_lote.js',
                         'r53/testes/missoes_integradas.js', 'r53/testes/versao_publica.js',
                         'r53/testes/caminho_loader.js',
                         'r53/testes/caminho_leve.js',
                         'r53/testes/caminho_integrado.js', 'r53/testes/caminho_corrida.js',
                         'r53/testes/pacote_leve.js', 'r53/testes/pessoal_leve.js', 'r53/testes/atalho_livre.js', 'r53/testes/leituras_curtas.js',
                         'r53/testes/editor_lazy.js',
                         'conteudos-b47/comum/testar-notas-contextuais.js']:
                run = subprocess.run([node, str(ROOT/name)], cwd=ROOT, capture_output=True, text=True, timeout=300)
                check(name, run.returncode == 0, run.stderr.strip() or run.stdout.strip())
        # Git identifica as fontes, evitando percorrer dependências em .venv.
        files = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
        py_count = 0
        for name in filter(None, files):
            path = ROOT/name
            if name.endswith('.py'):
                try:
                    ast.parse(path.read_text(encoding='utf-8'), filename=name)
                    py_count += 1
                except (SyntaxError, OSError) as error:
                    check('sintaxe ' + name, False, str(error))
        check('fontes Python analisadas', py_count > 0, str(py_count))
        script = "const fs=require('fs'),vm=require('vm'),m=require('module');for(const p of process.argv.slice(1)){const s=fs.readFileSync(p,'utf8');new vm.Script(p.endsWith('.gs')?s:m.wrap(s),{filename:p});}"
        js = [str(ROOT/name) for name in filter(None, files) if name.endswith(('.js', '.gs'))]
        run = subprocess.run([node, '-e', script, *js], cwd=ROOT, capture_output=True, text=True, timeout=60)
        check('sintaxe JS/GS sem executar serviços', run.returncode == 0, run.stderr.strip() or str(len(js))+' arquivos')
        for name in ['conferir-catalogo.py', 'conferir-progressao.py', 'conferir-kaori.py']:
            run = subprocess.run([sys.executable, name], cwd=ROOT, text=True, capture_output=True, timeout=120)
            (ROOT/'nuvem-b47/saidas').mkdir(parents=True, exist_ok=True)
            (ROOT/'nuvem-b47/saidas'/f'{name}.log').write_text(run.stdout + run.stderr)
            check(name, run.returncode == 0, 'exit='+str(run.returncode))

    output = ROOT/'nuvem-b47/saidas'
    output.mkdir(parents=True, exist_ok=True)
    report = {'resultado': 'OK' if all(c['ok'] for c in checks) else 'FALHA',
              'escopo': 'smoke' if args.smoke else 'dependências e entradas',
              'testes': checks, 'complementares': optional,
              'aviso': 'Não é validação nativa, migração ou aprovação da redução.'}
    (output/'diagnostico.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    return 0 if report['resultado'] == 'OK' else 1


if __name__ == '__main__':
    sys.exit(main())
