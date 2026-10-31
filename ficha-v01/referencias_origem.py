"""Endereços declarados na coluna C da ANALISE, sem interpretar prosa.

Somente uma referência qualificada, ou uma lista delas, é transformada. Mantém
o formato literal/fórmula constante, aspas, cifrões e separadores originais.
Não tenta adivinhar endereços em textos, INDIRECT ou fórmulas calculadas.
"""
import re
from dataclasses import dataclass

_SHEET = r"(?:'(?:[^']|'')+'|[^\s'!:,;()+*/&=]+)"
_CELL = r"\$?[A-Z]{1,3}\$?[1-9][0-9]*"
_END = rf"(?:{_CELL}|\$?[A-Z]{{1,3}}|\$?[1-9][0-9]*)"
_REF = re.compile(rf"(?P<sheet>{_SHEET})!(?P<a>{_END})(?::(?:(?P<sheet2>{_SHEET})!)?(?P<b>{_END}))?")
_CONSTANT = re.compile(r'="((?:[^"]|"")*)"')


@dataclass(frozen=True)
class Referencia:
    aba: str
    endereco: str
    inicio: int
    fim: int
    prefixo: str
    prefixo2: str | None = None


def texto(valor):
    if not isinstance(valor, str):
        return None
    match = _CONSTANT.fullmatch(valor)
    if match:
        return match[1].replace('""', '"')
    return None if valor.startswith('=') else valor


def referencias(valor):
    """Retorna None para texto livre/expressão; lista vazia para origem vazia."""
    source = texto(valor)
    if source is None:
        return None
    result = []
    at = 0
    while at < len(source):
        if source[at].isspace():
            at += 1
            continue
        match = _REF.match(source, at)
        if not match or (match.end() < len(source) and not source[match.end()].isspace()):
            return None
        nome = lambda p: (p[1:-1] if p.startswith("'") else p).replace("''", "'")
        aba = nome(match['sheet'])
        if match['sheet2'] and nome(match['sheet2']) != aba:
            return None
        if not match['b'] and not re.fullmatch(_CELL, match['a']):
            return None
        endereco = match['a'] + (':' + match['b'] if match['b'] else '')
        result.append(Referencia(aba, endereco, at, match.end(), match['sheet'], match['sheet2']))
        at = match.end()
    return result


def mover(valor, traduzir):
    refs = referencias(valor)
    if not refs:
        return valor
    source = texto(valor)
    for ref in reversed(refs):
        destino = traduzir(ref.aba, ref.endereco)
        if destino == ref.endereco:
            continue
        # A notação com aba repetida conserva também o segundo prefixo.
        if ref.prefixo2:
            a, b = destino.split(':')
            destino = a + ':' + ref.prefixo2 + '!' + b
        source = source[:ref.inicio] + ref.prefixo + '!' + destino + source[ref.fim:]
    return '="' + source.replace('"', '""') + '"' if _CONSTANT.fullmatch(valor) else source
