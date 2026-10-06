# -*- coding: utf-8 -*-
"""Leitura do manual.txt por seção e por tabela.

Desde 04/10/2026 o manual.txt sai do LIVRO-COMPLETO.md do sistema (extrair-manual.py): os títulos
guardam o # do nível e as tabelas ficam uma fileira por linha, com " | " entre as colunas. Este
módulo só lê; quem decide o que conferir é cada validador.
"""
import os, re

RAIZ = os.path.dirname(os.path.abspath(__file__))
_CACHE = {}


def linhas(caminho=None):
    caminho = caminho or os.path.join(RAIZ, "manual.txt")
    if caminho not in _CACHE:
        _CACHE[caminho] = open(caminho, encoding="utf-8").read().splitlines()
    return _CACHE[caminho]


def texto(caminho=None):
    return "\n".join(linhas(caminho))


def nivel(l):
    m = re.match(r"^(#+) ", l)
    return len(m.group(1)) if m else 0


def titulos(titulo, caminho=None):
    """índices das linhas de título com esse texto, em qualquer nível"""
    return [i for i, l in enumerate(linhas(caminho)) if nivel(l) and l.lstrip("#").strip() == titulo]


def secao(titulo, n=0, caminho=None, dentro=None):
    """as linhas da n-ésima seção com esse título, até o próximo título do mesmo nível ou acima.
    dentro: restringe a busca às linhas de outra seção (lista devolvida por secao)."""
    L = linhas(caminho) if dentro is None else dentro
    achados = [i for i, l in enumerate(L) if nivel(l) and l.lstrip("#").strip() == titulo]
    if len(achados) <= n:
        return []
    i = achados[n]
    nv = nivel(L[i])
    fim = next((j for j in range(i + 1, len(L)) if nivel(L[j]) and nivel(L[j]) <= nv), len(L))
    return L[i:fim]


def tabelas(L):
    """todas as tabelas de um trecho: lista de (cabeçalho, fileiras), cada fileira uma lista de células"""
    out, atual = [], None
    for l in L:
        if " | " in l and not nivel(l):
            cel = [c.strip() for c in l.split(" | ")]
            if atual is None:
                atual = (cel, [])
                out.append(atual)
            else:
                atual[1].append(cel)
        else:
            atual = None
    return out


def tabela(L, primeira):
    """a primeira tabela do trecho cujo cabeçalho começa pela célula `primeira`"""
    for cab, fil in tabelas(L):
        if cab and cab[0] == primeira:
            return cab, fil
    return None, []


def sem_ponto(s):
    return s.strip().rstrip(".").strip()


def paragrafos(L, sem_exemplo=True, ate_subtitulo=False):
    """os parágrafos de prosa de um trecho: sem títulos, sem tabelas e sem os exemplos.
    ate_subtitulo: para no primeiro título depois da primeira linha (só o que vem logo abaixo do título)."""
    out = []
    for i, l in enumerate(L):
        if nivel(l):
            if ate_subtitulo and i > 0:
                break
            continue
        s = l.strip()
        if not s or " | " in s or s.startswith("- "):
            continue
        if sem_exemplo and re.match(r"^(Exemplo|Exemplo de registro)[.:]", s):
            continue
        out.append(s)
    return out


def frase(trecho, caminho=None):
    """o trecho tem de estar no manual, palavra por palavra (espaços normalizados)"""
    limpo = " ".join(texto(caminho).split())
    if " ".join(trecho.split()) not in limpo:
        raise SystemExit(f"o livro nao tem mais a frase: {trecho!r}")
    return trecho


def numero(s):
    """o primeiro número de uma célula, com vírgula decimal"""
    m = re.search(r"\d+(?:[.,]\d+)?", s.replace(".", "") if re.search(r"\d\.\d{3}", s) else s)
    if not m:
        return None
    v = m.group(0).replace(",", ".")
    return float(v) if "." in v else int(v)
