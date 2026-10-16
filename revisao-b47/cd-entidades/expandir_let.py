# -*- coding: utf-8 -*-
"""Expande LET(nome, valor, ..., resultado) por substituição, para recalcular no LibreOffice < 24.8.

Equivalente para fórmulas sem efeito colateral (planilha): cada nome vira `(expressão)`, de dentro para
fora. Nomes dentro de texto entre aspas não são tocados. Uso: `expande(formula)`.
"""
import re


def _args(s, i):
    """Argumentos de nível zero a partir de s[i] (logo depois do '('); devolve (args, índice do ')')."""
    args, nivel, ini, aspas = [], 0, i, False
    while i < len(s):
        ch = s[i]
        if ch == '"':
            aspas = not aspas
        elif not aspas:
            if ch in '({':
                nivel += 1
            elif ch in ')}':
                if nivel == 0:
                    args.append(s[ini:i])
                    return args, i
                nivel -= 1
            elif ch == ',' and nivel == 0:
                args.append(s[ini:i])
                ini = i + 1
        i += 1
    raise ValueError('parênteses desbalanceados')


def _troca(expr, nome, valor):
    partes = re.split(r'("[^"]*")', expr)
    padrao = re.compile(r"(?<![A-Za-z0-9_.!$'])" + re.escape(nome) + r"(?![A-Za-z0-9_(!])")
    return ''.join(p if p.startswith('"') else padrao.sub(lambda _: '(' + valor + ')', p) for p in partes)


def expande(f):
    while True:
        m = re.search(r'(?<![A-Z_.])(?:_xlfn\.)?LET\(', f)
        if not m:
            return f
        args, fim = _args(f, m.end())
        args = [a.strip() for a in args]
        pares, corpo = args[:-1], args[-1]
        valores = {}
        for k in range(0, len(pares), 2):
            nome, valor = pares[k].replace('_xlpm.', ''), pares[k + 1]
            for n, v in valores.items():
                valor = _troca(valor, n, v)
            valores[nome] = valor
        for n, v in valores.items():
            corpo = _troca(corpo, n, v)
        f = f[:m.start()] + '(' + corpo + ')' + f[fim + 1:]


if __name__ == '__main__':
    assert expande('=LET(x,2,y,x*3,y+x)') == '=(((2)*3)+(2))'
    assert expande('=LET(base,A1,IF(base="base",1,base))') == '=(IF((A1)="base",1,(A1)))'
    print('ok')
