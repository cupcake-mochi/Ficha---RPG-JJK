# -*- coding: utf-8 -*-
"""Utilidades da revisão B47 (chat 2). Só lê o núcleo; saídas em nuvem-b47/saidas/revisao-b47/."""
import argparse
import gzip
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
SAIDAS = RAIZ / 'nuvem-b47' / 'saidas' / 'revisao-b47'
FIXTURE_V9 = AQUI / 'fixtures' / 'contrato-v9.json.gz'
PERFIS = json.loads((AQUI / 'casos' / 'perfis.json').read_text(encoding='utf-8'))

# Prefixos dos catálogos reduzidos em A. Tudo que não casa aqui deve sobreviver à redução.
RE_CATALOGO = re.compile(r'^(?:aviso\.)?custom\.(familia|melhoria|restricao|treino|pericia|oficio)\.(\d+)(?:\.|$)')


def sha():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=RAIZ, text=True).strip()


def arvore_limpa_do_nucleo():
    """Cache só vale se o núcleo não tiver alterações locais."""
    saida = subprocess.check_output(['git', 'status', '--porcelain', '--', '.', ':!revisao-b47'], cwd=RAIZ, text=True)
    return not saida.strip()


def python():
    venv = RAIZ / '.venv' / 'bin' / 'python'
    return str(venv) if venv.exists() else sys.executable


def perfil(nome):
    if nome not in PERFIS:
        sys.exit(f'perfil desconhecido: {nome}; opções: {", ".join(k for k in PERFIS if not k.startswith("_"))}')
    p = dict(PERFIS[nome])
    for cat, d in p['catalogos'].items():
        d.setdefault('chave', 'custom.' + cat + '.{n}.{campo}')
        d.setdefault('aviso', 'aviso.custom.' + cat + '.{n}')
    return p


def exportar(perfil_nome, tipo='analise', raiz=RAIZ):
    """Roda o gerador (real ou simulado) e devolve o caminho do JSON exportado.

    tipo: 'analise' (contrato, ~10 s) ou 'pecas' (layout inteiro, ~45 MB).
    """
    p = perfil(perfil_nome)
    SAIDAS.mkdir(parents=True, exist_ok=True)
    marca = sha()[:12] + ('' if arvore_limpa_do_nucleo() else '-sujo')
    destino = SAIDAS / f'{tipo}-{perfil_nome}-{marca}.json'
    if destino.exists() and not marca.endswith('-sujo'):
        return destino
    bandeira = '--exportar-analise' if tipo == 'analise' else '--exportar-pecas'
    cmd = [python(), str(AQUI / 'rodar_gerador.py'), str(raiz), json.dumps(p['trocas']), bandeira, str(destino)]
    r = subprocess.run(cmd, cwd=raiz, capture_output=True, text=True)
    if r.returncode != 0 or not destino.exists():
        sys.stderr.write(r.stdout[-3000:] + r.stderr[-3000:])
        raise SystemExit(f'gerador falhou para {perfil_nome}/{tipo}')
    return destino


def linhas_analise(caminho):
    dados = json.loads(Path(caminho).read_text(encoding='utf-8'))
    if 'linhas' in dados:
        return dados['linhas']
    aba = next(a for a in dados['layout']['abas'] if a['nome'] == 'ANALISE')
    return _linhas_da_aba(aba)


def _linhas_da_aba(aba):
    por_linha = {}
    for coord, valor, *_ in aba['celulas']:
        m = re.fullmatch(r'([A-D])(\d+)', coord)
        if m:
            por_linha.setdefault(int(m[2]), {})[m[1]] = valor
    out = []
    for r in sorted(por_linha):
        if r == 1:
            continue
        d = por_linha[r]
        out.append([d.get('A'), d.get('B'), d.get('C'), d.get('D')])
    return out


def aba_de(celula):
    """'CONFIGURAÇÃO'!B5 -> CONFIGURAÇÃO; =\"'X'!A1\" (literal publicado) também."""
    if not celula:
        return ''
    s = str(celula)
    m = re.search(r"'?([^'!]+?)'?!", s.replace('="', '').replace('""', '"'))
    return m.group(1) if m else ''


def carregar_v9():
    with gzip.open(FIXTURE_V9, 'rt', encoding='utf-8') as f:
        return json.load(f)


def ler_analise_modulo(caminho=None):
    spec = importlib.util.spec_from_file_location('ler_analise', caminho or (RAIZ / 'ler-analise.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class Placar:
    """Checagens 'bloqueante' derrubam o código de saída; 'risco' só é relatado."""

    def __init__(self, titulo):
        self.titulo, self.itens = titulo, []

    def check(self, nome, ok, detalhe='', nivel='bloqueante'):
        self.itens.append(dict(nome=nome, ok=bool(ok), detalhe=str(detalhe)[:600], nivel=nivel))
        marca = 'OK ' if ok else ('FALHA' if nivel == 'bloqueante' else 'RISCO')
        print(f'{marca:5} {nome}' + ('' if ok or not detalhe else f' — {str(detalhe)[:400]}'), flush=True)

    def fim(self, extra=None):
        falhas = [i for i in self.itens if not i['ok'] and i['nivel'] == 'bloqueante']
        riscos = [i for i in self.itens if not i['ok'] and i['nivel'] != 'bloqueante']
        SAIDAS.mkdir(parents=True, exist_ok=True)
        rel = dict(teste=self.titulo, sha=sha(), nucleo_limpo=arvore_limpa_do_nucleo(),
                   total=len(self.itens), falhas=len(falhas), riscos=len(riscos), itens=self.itens, **(extra or {}))
        nome = re.sub(r'[^a-z0-9]+', '-', self.titulo.lower()).strip('-')
        (SAIDAS / f'{nome}.json').write_text(json.dumps(rel, ensure_ascii=False, indent=1), encoding='utf-8')
        print(f'\n{self.titulo}: {len(self.itens)-len(falhas)-len(riscos)} ok · {len(falhas)} falha(s) bloqueante(s) · {len(riscos)} risco(s)')
        sys.exit(1 if falhas else 0)


def argumentos(descricao, padrao='base-v9'):
    ap = argparse.ArgumentParser(description=descricao)
    ap.add_argument('--perfil', default=padrao, help='perfil em casos/perfis.json')
    ap.add_argument('--analise', help='JSON já exportado (pula o gerador)')
    return ap


def hash_arquivo(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
