#!/usr/bin/env python3
"""Manifesto/pacote/conferência offline. Nunca acessa rede nem envia código."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
LIMITE = 900_000


def gravar(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def proteger_entradas(saida, entradas):
    for path in entradas:
        mesmo_arquivo = saida.exists() and path.exists() and saida.samefile(path)
        if saida.resolve() == path.resolve() or mesmo_arquivo:
            raise ValueError('A saída não pode sobrescrever uma entrada: ' + str(path))


def indice(files):
    result = {}
    for f in files:
        key = (f['name'], f['type'])
        if key in result or any(k[0] == key[0] for k in result):
            raise ValueError('Nome duplicado: ' + key[0])
        if f['type'] not in {'SERVER_JS', 'HTML', 'JSON'} or not isinstance(f['source'], str):
            raise ValueError('Tipo/source inválido')
        raw = f['source'].encode('utf-8')
        if f['type'] == 'SERVER_JS' and len(raw) >= LIMITE:
            raise ValueError('Teto de 900.000 bytes atingido: ' + f['name'])
        result[key] = {'nome': f['name'], 'tipo': f['type'], 'bytes': len(raw),
                       'sha256': hashlib.sha256(raw).hexdigest()}
    if not result:
        raise ValueError('Conjunto vazio')
    return result


def locais(directory):
    files = []
    for p in sorted(directory.glob('*.gs')):
        if p.is_symlink():
            raise ValueError('Link simbólico não permitido: ' + p.name)
        # read_bytes preserva CRLF: o hash mede exatamente o arquivo enviado.
        files.append({'name': p.stem, 'type': 'SERVER_JS', 'source': p.read_bytes().decode('utf-8')})
    indice(files)
    return files


def remoto(path, script_id):
    if not re.fullmatch(r'[A-Za-z0-9_-]+', script_id):
        raise ValueError('Script ID inválido')
    content = json.loads(path.read_text(encoding='utf-8'))
    if content.get('scriptId') != script_id:
        raise ValueError('Snapshot pertence a outro scriptId')
    indice(content['files'])
    manifests = [f for f in content['files'] if f['name'] == 'appsscript' and f['type'] == 'JSON']
    if len(manifests) != 1 or not isinstance(json.loads(manifests[0]['source']), dict):
        raise ValueError('Manifesto appsscript.json remoto ausente/inválido')
    return content['files']


def esperados(directory):
    """Complementos que a geração atual declarou no Ficha.gs (selo de geração), se houver."""
    ficha = directory/'Ficha.gs'
    if not ficha.is_file():
        return None
    m = re.search(r'^var COMPLEMENTOS_ESPERADOS_ = (\{.*\});$', ficha.read_text(encoding='utf-8'), re.M)
    return {k[:-3] for k in json.loads(m.group(1))} if m else None


def preparar(directory, snapshot, script_id, remover=()):
    local = locais(directory)
    old = remoto(snapshot, script_id)
    names = {f['name'] for f in local}
    declarados = esperados(directory)
    if declarados is not None:
        faltam=sorted(declarados-names)
        if faltam:raise ValueError('Complementos declarados ausentes localmente: '+', '.join(faltam))
        ficha=(directory/'Ficha.gs').read_text(encoding='utf-8')
        selo=re.search(r'^var GERACAO_ = "([0-9a-f]{16})";',ficha,re.M)
        if not selo:raise ValueError('Ficha.gs declara complementos sem selo de geração')
        for file in local:
            if file['name'] in ('Codigo','Habilidades','Ficha') or not file['source'].startswith('// GERADO POR'):continue
            stamps=re.findall(r'"geracao"\s*:\s*"([0-9a-f]{16})"',file['source'])
            if not stamps or any(stamp!=selo[1] for stamp in stamps):
                raise ValueError('Arquivo local de geração divergente: '+file['name'])
        # Complemento particionado que a geração atual não produziu é sobra da pasta.
        sobras = sorted(n for n in names if re.fullmatch(r'PecasAnalise\d+', n) and n not in declarados)
        if sobras:
            raise ValueError('Sobras locais de geração anterior: ' + ', '.join(sobras))
    extras = [f['name'] for f in old if f['type'] == 'SERVER_JS' and f['name'] not in names]
    pedidos = set(remover)
    if pedidos - set(extras):
        raise ValueError('--remover só aceita .gs remotos ausentes localmente: ' + ', '.join(sorted(pedidos - set(extras))))
    restantes = [n for n in extras if n not in pedidos]
    if restantes:
        raise ValueError('Revisar .gs remotos ausentes localmente antes de substituir: ' + ', '.join(restantes))
    if pedidos:
        # updateContent substitui o conjunto: omitir aqui é apagar no projeto. Fica registrado na saída.
        sys.stderr.write('Removidos do projeto por pedido explícito: ' + ', '.join(sorted(pedidos)) + '\n')
    # updateContent substitui o conjunto inteiro: preservar HTML e manifesto atual.
    files = local + [f for f in old if f['type'] != 'SERVER_JS']
    indice(files)
    return {'scriptId': script_id,
            'files': [{'name': f['name'], 'type': f['type'], 'source': f['source']} for f in files]}


def conferir(payload, snapshot, script_id):
    package = json.loads(payload.read_text(encoding='utf-8'))
    if package.get('scriptId') != script_id:
        raise ValueError('Pacote/snapshot esperado pertence a outro scriptId')
    expected = indice(package['files'])
    actual = indice(remoto(snapshot, script_id))
    differences = [list(k) for k in sorted(expected.keys() | actual.keys()) if expected.get(k) != actual.get(k)]
    return {'scriptId': script_id, 'igual': not differences, 'divergencias': differences,
            'arquivos': list(expected.values()), 'escopo': 'Conteúdo persistido; não prova execução, gatilhos ou Sheets.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='acao', required=True)
    for action in ('manifesto', 'preparar', 'conferir'):
        p = sub.add_parser(action)
        p.add_argument('--saida', type=Path, required=True)
        if action != 'conferir':
            p.add_argument('--fontes', type=Path, default=ROOT/'apps-script')
        if action == 'preparar':
            p.add_argument('--remover', action='append', default=[], metavar='NOME',
                           help='.gs remoto ausente localmente a apagar no envio (repetir por arquivo)')
        if action != 'manifesto':
            p.add_argument('--snapshot', type=Path, required=True)
            p.add_argument('--script-id', required=True)
        if action == 'conferir':
            p.add_argument('--pacote', type=Path, required=True)
    a = ap.parse_args()
    try:
        entradas = [p for p in (getattr(a, 'snapshot', None), getattr(a, 'pacote', None)) if p is not None]
        if hasattr(a, 'fontes'):
            entradas.extend(a.fontes.glob('*.gs'))
        proteger_entradas(a.saida, entradas)
        if a.acao == 'manifesto':
            rows = list(indice(locais(a.fontes)).values())
            value = {'limite_exclusivo_bytes': LIMITE, 'total_bytes': sum(r['bytes'] for r in rows),
                     'arquivos': [dict(r, arquivo=r['nome']+'.gs') for r in rows]}
        elif a.acao == 'preparar':
            value = preparar(a.fontes, a.snapshot, a.script_id, a.remover)
        else:
            value = conferir(a.pacote, a.snapshot, a.script_id)
        gravar(a.saida, value)
        return 1 if value.get('igual') is False else 0
    except (ValueError, KeyError, TypeError, OSError) as e:
        ap.exit(2, str(e) + '\n')


if __name__ == '__main__':
    raise SystemExit(main())
